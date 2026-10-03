# Upstream harvest round 4 — Round 2: the review pipeline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port items 7–12 of the 2026-10-02 survey (triage's third outcome, re-review dispositions, severity by effect and "Declined to judge", a plan's Review focus, four edge-case checks, standards discovery) and fix item 13 (a missing escalation heading) in this repository, the internal edition and the Copilot edition.

**Architecture:** Prose edits to agent, command, reference, rules and docs files, applied only through `wsub.py` (a whitespace-insensitive replace) from the edit files in Appendix B, so the text that lands is the text this plan carries. Shared rules live in `finding-triage` (triage, re-review) and `code-review` (grading, standards, edge cases); each caller changes only its triage sentence, its second-verdict sentence and its report line, citing the reference. The internal and Copilot editions take the same edit files through `gen.py`'s dialect substitution. Every edit file was dry-run against all three trees and the whole round was applied to throwaway copies before this plan was written: gates `EXIT=0` and `check.py` green in all three.

**Tech Stack:** Markdown prose executed by agents; git; bash; python3 (helpers, gates); node (mermaid gate).

**Spec:** `docs/superpowers/specs/2026-10-02-harvest-round-4-review-pipeline-design.md` (including § Amended during planning)

## Global Constraints

- **Never name the internal edition in this repository.** Check 19 rejects, anywhere in the work tree, the pattern `EDITION_FORBIDDEN_B64` decodes to in `scripts/check-docs.sh` — the internal edition's short name as a bare word, its repository names, and the organisation's name. Write "the internal edition" and `$IE`.
- **Prose is executed.** Every sentence added must be true of what the run does; a false one is a defect, not a typo.
- **Apply edits only with `wsub.py` from Appendix B's files.** A fix found later is a new edit block or a hand edit recorded as a `Ruling:` in the ledger, never an unrecorded change. `wsub.py` aborts with nothing written when a block's match count is wrong — that is a stop-and-look, never a reason to loosen the block.
- **Match the file's wrapping.** The edit files carry each file's own wrap: `finding-triage.md`, `escalation-rules.md`'s headings, `classification.md`, `code-review.md`, `risk-planner.md`, `review-fixer.md`, `doc-fixer.md` and the proposal commands' step 3 are hard-wrapped; everything else is one long line.
- **Copilot dialect.** In `$CE`, skills are named `implement:`, `document:` (never `/implement`), shared references are `~/.copilot/installed-plugins/ihudak-copilot-plugins/dev-workflows/skills/_shared/<name>.md`, and `${CLAUDE_PLUGIN_ROOT}` never appears. `gen.py` makes the substitutions; nothing else does.
- **Character limits.** Each `.github/instructions/*.md` in `$CE` stays under 20,000 characters (19,961 and 19,822 before; 19,894 and 19,786 after); this repository's `.claude/rules/docs-workflows.md` stays under 20,000 (19,965 before; 19,955 after). `check.py` asserts all of them.
- **Git discipline in this repository:** never `git checkout`/`switch` in `/workspace/ai-workflows` (work in `$AW`); run `git branch --show-current` immediately before every commit; never bare `git stash`; `.claude/rules/*` are tracked under an ignored directory, so stage them with `git add -f`.
- **Commit trailer:** `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.
- **Do not edit** `references/specification-format.md` (frozen).
- **Every `CHANGELOG.md` section is dated** (`2026-10-02`; re-date to the merge day if the merge slips) before it reaches `main` — check 18.
- **Zero known bugs:** every review finding — minors and nits included — is fixed before merge, and each edition is reviewed until a round returns zero findings.

## Review Focus

1. **A re-review that re-raises only a `BLOCKER` triage already dismissed** — the run must reach § On re-review's settle prompt, not stop. The old text stopped on the verdict word. Pinned by Task 3 Step 6's trace A.
2. **The same, with one new `MINOR` beside it** — still the settle prompt: the `MINOR` survives, is recorded and is not fixed. The old "partly emptied set" reading would have let the verdict stand and stop. Pinned by trace B.
3. **A fix that did not change the code at its finding** — the re-raised `BLOCKER` is carried as a survivor and the review stayed blocked: the run stops, as before. Pinned by trace C.
4. **An unverified `BLOCKER` as the only finding behind a first `BLOCK`** — no fixer is dispatched; the first-review settle prompt lists it with what would settle it. Pinned by Task 1 Step 5's read-through.
5. **The Copilot instruction files at the edge of their limit** — any edit there that grows them past 20,000 characters fails. Pinned by `check.py`'s limit checks (Task 9).

---

### Task 0: Variables, helpers, branches

**Files:**
- Create (scratch, never committed): `$S/{wsub.py,count.py,gen.py,check.py,apply.sh,gates.sh,release.py}`, `$S/edits/*`, `$S/cl/*`

**Interfaces:**
- Produces: `$AW`, `$IE`, `$CE`, `$S`, `$PLAN`; `wsub.py TARGET EDITFILE [--dry]` (exit 1, nothing written, on any count mismatch); `count.py ROOT TEXT [--no-changelog]`; `gen.py aw|ie|ce TEMPLATE` (dialect substitution, fails on a leftover `{{…}}`); `check.py aw|ie|ce ROOT` (prints each failing check as `FAIL …`, exit 0 only when all pass); `apply.sh ie|ce ROOT [--dry]` (every edit for one of the other editions, in order); `gates.sh aw|ie|ce ROOT` (the edition's CI chain); `release.py aw|ie|ce ROOT` (versions + changelog sections).

- [ ] **Step 1: Set the variables** (every later task assumes them)

```bash
AW=/workspace/.worktrees/ai-workflows-harvest-r4-review   # this repository's worktree, branch iv-gu/harvest-r4-review
IE=<the internal edition's checkout root under /workspace> # not written here: check 19
CE=/workspace/ihudak-copilot-plugins
S=/tmp/claude-502/-workspace-ai-workflows/d7e59186-271d-4a83-a94b-9e776fafee25/scratchpad/r5   # any scratch dir outside every repo
PLAN=$AW/docs/superpowers/plans/2026-10-02-harvest-round-4-review-pipeline.md
```

- [ ] **Step 2: Extract the helpers, edit files and changelog sections from this plan** (Appendices A–C)

```bash
mkdir -p "$S/edits" "$S/cl" "$S/gen" && python3 - "$PLAN" "$S" <<'EOF'
import os, re, sys
plan, S = sys.argv[1], sys.argv[2]
n = 0
for m in re.finditer(r'^#### `(scripts|edits|cl)/([^`]+)`\n\n`````[a-z]*\n(.*?)\n`````$', open(plan).read(), re.S | re.M):
    d = S if m.group(1) == 'scripts' else os.path.join(S, m.group(1))
    open(os.path.join(d, m.group(2)), 'w').write(m.group(3) + '\n'); n += 1
print(n, 'files')
EOF
chmod +x "$S"/*.sh "$S"/*.py
```
Expected: `68 files`.

- [ ] **Step 3: Dry-run every edit against every edition** — proves the trees have not moved since the plan was written

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4-review && test -z "$(git status --porcelain)" && echo CLEAN
"$S/apply.sh" ie "$IE" --dry | tail -1 && "$S/apply.sh" ce "$CE" --dry | tail -1
```
Expected: `CLEAN`, then `apply.sh ie: done` and `apply.sh ce: done` (every block `checked`, none `ABORT`). This edition's blocks are dry-run task by task below.

- [ ] **Step 4: RED — run the checks on all three unchanged trees**

```bash
python3 "$S/check.py" aw "$AW" | tail -1; python3 "$S/check.py" ie "$IE" | tail -1; python3 "$S/check.py" ce "$CE" | tail -1
```
Expected: `aw: 7/107 checks pass`, `ie: 5/83 checks pass`, `ce: 7/85 checks pass`. Every later task in this edition is measured by `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'`, which reads **100** here.

- [ ] **Step 5: Branch the other two editions** (their own checkouts; no shared-tree rule binds them)

```bash
for r in "$IE" "$CE"; do test -z "$(git -C "$r" status --porcelain)" && git -C "$r" switch -c iv-gu/harvest-r4-review && git -C "$r" branch --show-current; done
```
Expected: `iv-gu/harvest-r4-review` twice.

---

### Task 1: `workflows-core` — triage outcomes, re-review, escalation heading (this edition)

**Files:**
- Modify: `plugins/workflows-core/references/finding-triage.md` (§ The step, § When triage empties the survivor set, § The patch gate; new § On re-review; § Reporting; the no-fixer paragraph)
- Modify: `plugins/workflows-core/references/escalation-rules.md` (new heading above `— /document`; the `/document` and `/epics` entries)
- Modify: `plugins/workflows-core/references/model-routing/classification.md` (§6 item 4 and the disposition sentence)
- Modify: `plugins/workflows-core/agents/doc-fixer.md` (patch gate)

**Interfaces:**
- Produces: the outcomes **kept / unverified / dismissed**; `finding-triage` § On re-review, the noun **stayed blocked**, the term **settle prompts**, **carried**; the heading `Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline`. Tasks 3–5 cite these by exactly these names.

- [ ] **Step 1: RED** — `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'` → `100`.
- [ ] **Step 2: Generate this edition's triage edit and dry-run all five**

```bash
cd "$AW" && python3 "$S/gen.py" aw "$S/edits/triage-core.txt" > "$S/gen/aw-triage-core.txt" && for x in "plugins/workflows-core/references/finding-triage.md $S/gen/aw-triage-core.txt" "plugins/workflows-core/references/escalation-rules.md $S/edits/aw-escalation.txt" "plugins/workflows-core/references/model-routing/classification.md $S/edits/all-classification.txt" "plugins/workflows-core/agents/doc-fixer.md $S/edits/all-doc-fixer.txt"; do set -- $x; python3 "$S/wsub.py" "$1" "$2" --dry; done
```
Expected: `checked 6 block(s)`, `checked 3 block(s)`, `checked 2 block(s)`, `checked 1 block(s)`.

- [ ] **Step 3: Apply**

```bash
cd "$AW" && python3 "$S/wsub.py" plugins/workflows-core/references/finding-triage.md "$S/gen/aw-triage-core.txt" && python3 "$S/wsub.py" plugins/workflows-core/references/finding-triage.md "$S/edits/aw-triage.txt" && python3 "$S/wsub.py" plugins/workflows-core/references/escalation-rules.md "$S/edits/aw-escalation.txt" && python3 "$S/wsub.py" plugins/workflows-core/references/model-routing/classification.md "$S/edits/all-classification.txt" && python3 "$S/wsub.py" plugins/workflows-core/agents/doc-fixer.md "$S/edits/all-doc-fixer.txt"
```
Expected: five `applied N block(s)` lines (6, 1, 3, 2, 1).

- [ ] **Step 4: GREEN for this task** — `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'` → `85`.
- [ ] **Step 5: Read-through (Review Focus 4)** — read `finding-triage.md` end to end. Confirm, citing the sentence for each: an unverified `BLOCKER` is never handed to a fixer (§ The step, "Only survivors…"); with it the only finding behind a `BLOCK`, the survivor set is empty and § When triage empties the survivor set fires, its step 3 reporting the unverified finding with what would settle it; the patch gate's instruction-file clause and its reason; § On re-review's three rules and its settle prompt with no re-review arm; § Reporting's sum rule. Ledger one line per item.
- [ ] **Step 6: Commit**

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4-review && git add plugins/workflows-core/references/finding-triage.md plugins/workflows-core/references/escalation-rules.md plugins/workflows-core/references/model-routing/classification.md plugins/workflows-core/agents/doc-fixer.md && git commit -q -m "feat(workflows-core): triage's unverified outcome, § On re-review, the inline-fix escalation heading

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" && git log --oneline -1
```

---

### Task 2: `dev-workflows` agents — grading, standards, edge cases, Review focus (this edition)

**Files:**
- Modify: `plugins/dev-workflows/agents/code-review.md` (`## Review method` step 4; dimensions 3 and 4; `## Output`; `## Hard rules`)
- Modify: `plugins/dev-workflows/agents/risk-planner.md` (output template; `## Planning discipline`)
- Modify: `plugins/dev-workflows/agents/test-writer.md` (step 3)
- Modify: `plugins/dev-workflows/agents/review-fixer.md` (patch gate)

**Interfaces:**
- Consumes: the patch gate's instruction-file list (Task 1).
- Produces: `code-review`'s `### Declined to judge` output section; the plan section `### Review focus` (risk-planner) — Task 3 names both.

- [ ] **Step 1: RED** — `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'` → `85`.
- [ ] **Step 2: Dry-run, then apply**

```bash
cd "$AW" && for f in code-review risk-planner test-writer review-fixer; do python3 "$S/wsub.py" plugins/dev-workflows/agents/$f.md "$S/edits/all-$f.txt" --dry; done && for f in code-review risk-planner test-writer review-fixer; do python3 "$S/wsub.py" plugins/dev-workflows/agents/$f.md "$S/edits/all-$f.txt"; done
```
Expected: `checked 5`, `checked 2`, `checked 1`, `checked 1`, then the same four counts as `applied`.

- [ ] **Step 3: GREEN for this task** — `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'` → `69`.
- [ ] **Step 4: Read-through** — read `code-review.md` `## Review method` through `## Hard rules` once: the grading rule names exactly the dimensions that fix their own grade (3's floor, 9, 10, 11); the standards list in dimension 3 is the spec's D14 list; the four dimension-4 checks and the Review focus sentence; `### Declined to judge` sits between `### Findings` and `### Recommended next step`; the hard rule says the two short returns carry none. Ledger it.
- [ ] **Step 5: Commit**

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4-review && git add plugins/dev-workflows/agents/{code-review,risk-planner,test-writer,review-fixer}.md && git commit -q -m "feat(dev-workflows): code-review grades by effect, finds the repo's standards, checks four edge cases; plans carry a Review focus

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" && git log --oneline -1
```

---

### Task 3: The code commands — triage the re-review, stop only when the review stayed blocked (this edition)

**Files:**
- Modify: `plugins/dev-workflows/commands/implement.md` (Phase 2A item 9; Phase 3B step 7's BLOCK branch, triage sub-step and step 8; Phase 4's cleanup list; Phase 4.6's `"Every run"` paragraph and `clean_finish` row; the Phase 5 triage line and `### Next step`; the invariants)
- Modify: `plugins/dev-workflows/commands/vuln.md`, `plugins/dev-workflows/commands/upgrade.md` (triage sub-step, second-verdict line, every statement of that stop, the triage line)
- Modify: `plugins/dev-workflows/references/code-handoff.md` (§2.9)

**Interfaces:**
- Consumes: § On re-review, **stayed blocked**, **settle prompts** (Task 1); `### Declined to judge`, `### Review focus` (Task 2).

- [ ] **Step 1: RED** — `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'` → `69`.
- [ ] **Step 2: Dry-run**

```bash
cd "$AW" && python3 "$S/wsub.py" plugins/dev-workflows/commands/implement.md "$S/edits/aw-implement.txt" --dry && python3 "$S/wsub.py" plugins/dev-workflows/commands/vuln.md "$S/edits/aw-vuln.txt" --dry && python3 "$S/wsub.py" plugins/dev-workflows/commands/upgrade.md "$S/edits/aw-upgrade.txt" --dry && python3 "$S/wsub.py" plugins/dev-workflows/references/code-handoff.md "$S/edits/aw-code-handoff.txt" --dry
```
Expected: `checked 12`, `checked 5`, `checked 8`, `checked 1`.

- [ ] **Step 3: Apply** — the same four commands without `--dry`. Expected: `applied 12`, `applied 5`, `applied 8`, `applied 1`.
- [ ] **Step 4: GREEN for this task** — `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'` → `45`.
- [ ] **Step 5: Population sweep (refinement 8)** — `python3 "$S/count.py" "$AW" "second verdict still" --no-changelog` and `… "still-\`BLOCK\`"`, `… "review stayed \`BLOCK\`"`, `… "review still \`BLOCK\`"`, `… "is still \`BLOCK\` after its"`: every remaining hit is in a file Tasks 4–5 own (the docs pages) — none in `plugins/dev-workflows/commands/` or `references/`. Ledger the counts.
- [ ] **Step 6: Trace the three runs (Review Focus 1–3)** through `/implement` Phase 3B step 7 as edited, citing the sentence that decides each step, and ledger each trace as `Task 3: trace <A|B|C>: old → <outcome>; new → <outcome>`:
  - **A.** First review `BLOCK`: `BLOCKER` X (triage refutes it) and `MAJOR` Y (kept). The set is partly emptied, so the verdict stands and the BLOCK branch fixes Y and re-reviews. The re-review returns `BLOCK` re-raising X alone. Old: *"If the second verdict is still BLOCK, stop"* → **stop**. New: X matches its logged row, code unchanged → carried as dismissed; no `BLOCKER` survives → § On re-review point 3's **settle prompt**; *Proceed* → step 8.
  - **B.** As A, but the re-review also raises a new `MINOR` Z. Old → **stop**. New → Z is verified and survives, recorded and not fixed (point 1); X carried as dismissed; no `BLOCKER` survives → **settle prompt**.
  - **C.** First review `BLOCKER` W, kept; `review-fixer`'s edit leaves W's code as it was; the re-review raises W again. Old → **stop**. New → W matches its row and the code still reads as described → carried as a survivor → the review **stayed blocked** → **stop**, and Phase 4.6 commits with `clean_finish: false`.
- [ ] **Step 7: Commit**

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4-review && git add plugins/dev-workflows/commands/{implement,vuln,upgrade}.md plugins/dev-workflows/references/code-handoff.md && git commit -q -m "feat(dev-workflows): /implement, /vuln and /upgrade triage the re-review and stop only when the review stayed blocked

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" && git log --oneline -1
```

---

### Task 4: The product and docs triage callers (this edition)

**Files:**
- Modify: `plugins/docs-workflows/commands/document.md`, `plugins/product-workflows/commands/epics.md` (triage sub-step, second-verdict sentence, triage line)
- Modify: `plugins/product-workflows/commands/{prd-proposal,brd-proposal}.md` (Phase triage step 3, its report sentence, the final-report triage clause)
- Modify: `plugins/docs-workflows/commands/{docs-init,docs-brand,docs-audit}.md` (triage sentence, patch-gate restatement, `Findings:` report line)
- Modify: `plugins/docs-workflows/agents/docs-audit-reviewer.md`, `plugins/product-workflows/agents/proposal-reviewer.md`

**Interfaces:**
- Consumes: Task 1's names; the heading `… — commands that fix inline` (the proposals escalate per it).

- [ ] **Step 1: RED** — `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'` → `45`.
- [ ] **Step 2: Dry-run, then apply**

```bash
cd "$AW" && cat > "$S/gen/aw-task4.list" <<'EOF'
plugins/docs-workflows/commands/document.md edits/aw-document.txt
plugins/product-workflows/commands/epics.md edits/aw-epics.txt
plugins/product-workflows/commands/prd-proposal.md edits/aw-prd-proposal.txt
plugins/product-workflows/commands/brd-proposal.md edits/aw-brd-proposal.txt
plugins/docs-workflows/commands/docs-init.md edits/aw-docs-init.txt
plugins/docs-workflows/commands/docs-brand.md edits/aw-docs-brand.txt
plugins/docs-workflows/commands/docs-audit.md edits/aw-docs-audit.txt
plugins/docs-workflows/agents/docs-audit-reviewer.md edits/aw-agents-triage.txt
plugins/product-workflows/agents/proposal-reviewer.md edits/aw-proposal-reviewer.txt
EOF
while read f e; do python3 "$S/wsub.py" "$f" "$S/$e" --dry || break; done < "$S/gen/aw-task4.list"
```
Expected: nine `checked` lines (3, 3, 3, 3, 3, 3, 3, 1, 1) and no `ABORT`. Then apply: `while read f e; do python3 "$S/wsub.py" "$f" "$S/$e" || break; done < "$S/gen/aw-task4.list"` → the same nine as `applied`.

- [ ] **Step 3: GREEN for this task** — `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'` → `18`.
- [ ] **Step 4: Read-through** — in `/document` and `/epics` Phase 7 and the proposals' step 3, the second-verdict sentence names § On re-review, *Proceed*'s destination (Phase 8; "proceed"), and the escalation it keeps; in `/docs-init`, `/docs-brand` and `/docs-audit` nothing mentions a re-review (they run none). Ledger it.
- [ ] **Step 5: Commit**

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4-review && git add plugins/docs-workflows/commands/{document,docs-init,docs-brand,docs-audit}.md plugins/product-workflows/commands/{epics,prd-proposal,brd-proposal}.md plugins/docs-workflows/agents/docs-audit-reviewer.md plugins/product-workflows/agents/proposal-reviewer.md && git commit -q -m "feat: /document, /epics and the proposals triage the re-review; the docs commands report unverified findings

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" && git log --oneline -1
```

---

### Task 5: Item 13's callers, the rules files and the docs pages (this edition)

**Files:**
- Modify: `plugins/product-workflows/commands/{create-prd,update-prd,create-ard}.md`, `plugins/dev-workflows/commands/design.md` (the escalation pointer; `/create-prd`'s inline array)
- Modify: `plugins/product-workflows/docs/commands/{create-prd,update-prd}.md` (the choices' name)
- Modify: `.claude/rules/{workflows-core,dev-workflows,docs-workflows}.md`
- Modify: `plugins/dev-workflows/docs/commands/{implement,vuln,upgrade}.md`, `plugins/docs-workflows/docs/commands/{document,docs-audit,docs-init,docs-brand}.md`, `plugins/product-workflows/docs/commands/{epics,prd-proposal}.md`, `plugins/workflows-core/docs/reference/references.md`
- Untouched on purpose: `plugins/product-workflows/commands/specify.md` (spec § Amended during planning, 2)

- [ ] **Step 1: RED** — `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'` → `18`.
- [ ] **Step 2: Generate `/design`'s pointer edit, dry-run all, then apply**

```bash
cd "$AW" && python3 "$S/gen.py" aw "$S/edits/ed-design-pointer.tpl" > "$S/gen/aw-design-pointer.txt" && python3 "$S/gen.py" aw "$S/edits/ed-vuln-fixer.tpl" > "$S/gen/aw-vuln-fixer.txt" && cat > "$S/gen/aw-task5.list" <<'EOF'
plugins/product-workflows/commands/create-prd.md edits/aw-create-prd.txt
plugins/product-workflows/commands/update-prd.md edits/aw-bare-pointer.txt
plugins/product-workflows/commands/create-ard.md edits/aw-bare-pointer.txt
plugins/dev-workflows/commands/design.md gen/aw-design-pointer.txt
plugins/product-workflows/docs/commands/create-prd.md edits/aw-prd-docs.txt
plugins/product-workflows/docs/commands/update-prd.md edits/aw-prd-docs.txt
.claude/rules/workflows-core.md edits/aw-rules-wc.txt
.claude/rules/dev-workflows.md edits/aw-rules-dw.txt
.claude/rules/dev-workflows.md edits/aw-rules-fixer.txt
.claude/rules/docs-workflows.md edits/all-rules-docs.txt
.claude/rules/dev-workflows-tests.md edits/aw-rules-tests.txt
plugins/dev-workflows/agents/vuln-fixer.md gen/aw-vuln-fixer.txt
CLAUDE.md edits/aw-claude-md.txt
plugins/dev-workflows/docs/commands/implement.md edits/aw-doc-implement.txt
plugins/dev-workflows/docs/commands/vuln.md edits/aw-doc-vuln.txt
plugins/dev-workflows/docs/commands/upgrade.md edits/aw-doc-upgrade.txt
plugins/docs-workflows/docs/commands/document.md edits/aw-doc-document.txt
plugins/product-workflows/docs/commands/epics.md edits/aw-doc-epics.txt
plugins/docs-workflows/docs/commands/docs-audit.md edits/aw-doc-dismissal-is.txt
plugins/docs-workflows/docs/commands/docs-init.md edits/aw-doc-dismissal-init.txt
plugins/product-workflows/docs/commands/prd-proposal.md edits/aw-doc-dismissal-is.txt
plugins/workflows-core/docs/reference/references.md edits/aw-doc-wc-refs.txt
plugins/docs-workflows/references/docs-workflow/scaffold-tree.md edits/aw-scaffold-tree.txt
plugins/docs-workflows/docs/commands/docs-init.md edits/aw-doc-docs-init.txt
plugins/docs-workflows/docs/commands/docs-brand.md edits/aw-doc-docs-brand.txt
EOF
while read f e; do python3 "$S/wsub.py" "$f" "$S/$e" --dry || break; done < "$S/gen/aw-task5.list"
```
Expected: twenty-five `checked` lines and no `ABORT`. Then apply: `while read f e; do python3 "$S/wsub.py" "$f" "$S/$e" || break; done < "$S/gen/aw-task5.list"` → twenty-five `applied` lines.

- [ ] **Step 3: GREEN** — `python3 "$S/check.py" aw "$AW" | tail -1` → `aw: 107/107 checks pass`.
- [ ] **Step 4: The rules files' size and the claim-expiry sweep** — `python3 -c 'import sys;print(len(open(sys.argv[1]).read()))' .claude/rules/docs-workflows.md` → `19955`. Then sweep by subject across refinement 4's scope (`plugins/` with every `CHANGELOG.md`, `README.md`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/`): `grep -rn -i -E "dismiss|survivor|re-review|second verdict|still .BLOCK|Review verdict BLOCK|documented standard|Missed edge|Acceptance checks|patch gate" plugins README.md CLAUDE.md .claude/rules docs/maintainers --include=*.md | grep -v CHANGELOG`. Read each hit outside the files this round edited against the new rules; any that now states something false is fixed (a new edit block, ledgered as a `Ruling:`). Ledger the hit count and the disposition.
- [ ] **Step 5: Commit** (`.claude/rules` needs `-f`)

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4-review && git add CLAUDE.md plugins/docs-workflows/references/docs-workflow/scaffold-tree.md plugins/dev-workflows/agents/vuln-fixer.md plugins/product-workflows/commands/{create-prd,update-prd,create-ard}.md plugins/dev-workflows/commands/design.md plugins/product-workflows/docs/commands/{create-prd,update-prd,epics,prd-proposal}.md plugins/dev-workflows/docs/commands/{implement,vuln,upgrade}.md plugins/docs-workflows/docs/commands/{document,docs-audit,docs-init,docs-brand}.md plugins/workflows-core/docs/reference/references.md && git add -f .claude/rules/{workflows-core,dev-workflows,docs-workflows,dev-workflows-tests}.md && git commit -q -m "fix: commands that fix inline cite an escalation heading that exists; rules and docs describe the three outcomes and the re-review

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" && git log --oneline -1
```

---

### Task 6: Release this edition — versions, changelogs, gates

**Files:**
- Modify: `.claude-plugin/marketplace.json` (four `version` fields); `plugins/{workflows-core,dev-workflows,product-workflows,docs-workflows}/.claude-plugin/plugin.json`; the same four `CHANGELOG.md` (Appendix C)

- [ ] **Step 1: Bump and write the changelogs** — `python3 "$S/release.py" aw "$AW"`. Expected four lines, each name with its new version twice: `workflows-core 1.11.0 1.11.0`, `dev-workflows 4.6.0 4.6.0`, `product-workflows 3.12.0 3.12.0`, `docs-workflows 1.5.0 1.5.0` (marketplace order).
- [ ] **Step 2: Check each changelog entry against the diff it describes** — `git -C "$AW" diff origin/main...HEAD --stat` beside each `CHANGELOG.md` section; every claim names a change the diff makes.
- [ ] **Step 3: Gates** — `"$S/gates.sh" aw "$AW"; echo "EXIT=$?"` → `EXIT=0` (run with a timeout of at least 300 s). A failure is fixed and the chain re-run from the start.
- [ ] **Step 4: Commit**

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4-review && git add .claude-plugin/marketplace.json plugins/*/.claude-plugin/plugin.json plugins/{workflows-core,dev-workflows,product-workflows,docs-workflows}/CHANGELOG.md && git commit -q -m "release: workflows-core 1.11.0, dev-workflows 4.6.0, product-workflows 3.12.0, docs-workflows 1.5.0

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" && git log --oneline -1
```

---

### Task 7: Whole-branch review of this edition, to zero findings

- [ ] **Step 1: Dispatch a fresh reviewer** (Opus, its own scratch directory) with: the spec path (including § Amended during planning), the plan path, `git -C "$AW" diff origin/main...HEAD`, the ledger's `Ruling:` lines, and this brief — *"Review this branch against the spec. Prose here is executed literally by agents: report every false, ambiguous or self-contradicting sentence; every stale copy of a changed claim anywhere in `plugins/` (every `CHANGELOG.md` included), `README.md`, `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/`; every place a changed agent's or reference's caller or docs page now disagrees with it; every pointer whose target does not say what the pointer claims; and every edit whose wrapping or idiom differs from its file. Check each changelog entry against the diff. Report only real defects, with file:line, severity and the fix; do not re-raise a ruled item unless the ruling is false."*
- [ ] **Step 2: Triage each finding** at the location it names; fix every confirmed one, minors and nits included (an edit block or a ledgered hand edit); record any dismissal with a reason that disposes of that finding's own claim.
- [ ] **Step 3: Re-run** `check.py` (`107/107`) and the gate chain (`EXIT=0`); commit the wave as `fix: review round N — …`, branch verified first.
- [ ] **Step 4: Repeat** Steps 1–3 until a round returns zero findings. A fix that writes a new rule is re-read against the rule it closes first (the Round 1 lesson: every Important from round 2 on came from a rule written to close the previous round's finding).

---

### Task 8: Port to the internal edition

**Files (paths relative to `$IE`):** `plugins/dev-workflows/references/{finding-triage,escalation-rules,code-repo-handoff}.md`, `plugins/dev-workflows/references/model-routing/classification.md`, `plugins/dev-workflows/agents/{code-review,risk-planner,test-writer,review-fixer,doc-fixer,vuln-fixer}.md`, `plugins/dev-workflows/commands/{implement,vuln,upgrade,document,epics,create-vi,update-vi,create-ard,design}.md`, `.claude/rules/{dev-workflows-code,dev-workflows-docs}.md`, `plugins/dev-workflows/docs/commands/{implement,vuln,upgrade,document,epics,create-vi,update-vi}.md`, `plugins/dev-workflows/docs/reference/references.md`, `plugins/dev-workflows/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `plugins/dev-workflows/CHANGELOG.md`

- [ ] **Step 1: Carry this edition's review fixes over first.** Every fix Task 7 made to a shared or templated edit file (`triage-core.txt`, `all-*.txt`, `ed-*.tpl`, `aw-doc-*.txt`, `aw-rules-*.txt`, `aw-code-handoff.txt`) is already in `$S/edits`; a fix made by hand in `$AW` gets the matching edit block here, ledgered. Then `"$S/apply.sh" ie "$IE" --dry | tail -1` → `apply.sh ie: done`.
- [ ] **Step 2: RED** — `python3 "$S/check.py" ie "$IE" | tail -1` → `ie: 5/83 checks pass`.
- [ ] **Step 3: Apply** — `"$S/apply.sh" ie "$IE" | tail -1` → `apply.sh ie: done`.
- [ ] **Step 4: GREEN** — `python3 "$S/check.py" ie "$IE" | tail -1` → `ie: 83/83 checks pass`.
- [ ] **Step 5: Sweep** — as Task 5 Step 4, over `$IE`'s `plugins/`, `README.md`, `CLAUDE.md`, `.claude/rules/`; and `grep -rn '/specify\|specify\.md' "$IE/plugins/dev-workflows/references/escalation-rules.md"` names no `/specify` among the new heading's callers.
- [ ] **Step 6: Release** — `python3 "$S/release.py" ie "$IE"` → `dev-workflows 2.67.0 2.67.0`. Gates: `"$S/gates.sh" ie "$IE"; echo "EXIT=$?"` → `EXIT=0`.
- [ ] **Step 7: Commit** (branch verified; `git add -f` for `.claude/rules`)

```bash
cd "$IE" && test "$(git branch --show-current)" = iv-gu/harvest-r4-review && git add -A plugins .claude-plugin && git add -f .claude/rules/dev-workflows-code.md .claude/rules/dev-workflows-docs.md && git status --short && git commit -q -m "feat: upstream harvest round 4, Round 2 — the review pipeline (dev-workflows 2.67.0)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" && git log --oneline -1
```
Expected `git status --short` lists exactly the files in this task's **Files** line, all `M`.

- [ ] **Step 8: Review to zero** — as Task 7, against `git -C "$IE" diff main...HEAD`, with the brief's scope read as this edition's `plugins/`, `README.md`, `CLAUDE.md` and `.claude/rules/`, plus: *"Compare each changed passage with this repository's counterpart (`$AW`, the same branch); report any difference that is not dialect (the internal edition's command names, `${CLAUDE_PLUGIN_ROOT}` paths, Jira mode, VI)."*

---

### Task 9: Port to the Copilot edition

**Files (paths relative to `$CE`):** `dev-workflows/skills/_shared/{finding-triage,escalation-rules,code-repo-handoff,model-routing}.md`, `dev-workflows/agents/{code-review,risk-planner,test-writer,review-fixer,doc-fixer,vuln-fixer}.md`, `dev-workflows/skills/{implement,vuln,upgrade,document,epics,create-vi,update-vi,create-ard,design}/SKILL.md`, `.github/instructions/{dev-workflows-shared,dev-workflows-skill-map}.instructions.md`, `dev-workflows/docs/skills/{implement,vuln,upgrade,document,epics,create-vi,update-vi}.md`, `dev-workflows/docs/reference/references.md`, `dev-workflows/.plugin/plugin.json`, `.github/plugin/marketplace.json`, `dev-workflows/CHANGELOG.md`

- [ ] **Step 1: Carry the review fixes over** (as Task 8 Step 1, plus any Task 8 fixes), then `"$S/apply.sh" ce "$CE" --dry | tail -1` → `apply.sh ce: done`.
- [ ] **Step 2: RED** — `python3 "$S/check.py" ce "$CE" | tail -1` → `ce: 7/85 checks pass`.
- [ ] **Step 3: Apply** — `"$S/apply.sh" ce "$CE" | tail -1` → `apply.sh ce: done`. `ce-code-review.txt` runs after `all-code-review.txt` (it edits the text that one inserts); `apply.sh` keeps that order.
- [ ] **Step 4: GREEN** — `python3 "$S/check.py" ce "$CE" | tail -1` → `ce: 85/85 checks pass` — the two limit checks included (19,894 and 19,786 characters).
- [ ] **Step 5: Dialect sweep** — `grep -rn -E '/implement|/vuln|/upgrade|/document|/epics|CLAUDE_PLUGIN_ROOT|workflows-core:' $(git -C "$CE" diff --name-only | sed "s#^#$CE/#") | grep -v CHANGELOG` returns nothing a Copilot reader would act on wrongly (a `/document` inside a path is fine; a command name is not). Then the subject sweep, as Task 8 Step 5, over `dev-workflows/`, `README.md` and `.github/`.
- [ ] **Step 6: Release** — `python3 "$S/release.py" ce "$CE"` → `dev-workflows 2.36.0 2.36.0`. Gates: `"$S/gates.sh" ce "$CE"; echo "EXIT=$?"` → `EXIT=0`.
- [ ] **Step 7: Commit** — as Task 8 Step 7, with `git add -A dev-workflows .github` and message `(dev-workflows 2.36.0)`.
- [ ] **Step 8: Review to zero** — as Task 8 Step 8, against `git -C "$CE" diff main...HEAD`, the dialect being `implement:`-style names, `~/.copilot/…/_shared/` paths, the review tier, and the trailing `"Other… (describe)"` arm.

---

### Task 10: Harvest record, merge, push, clean up

- [ ] **Step 1: Merge and push the two other editions**

```bash
for r in "$IE" "$CE"; do
  test "$(git -C "$r" branch --show-current)" = iv-gu/harvest-r4-review || { echo "wrong branch in $r"; break; }
  git -C "$r" switch main && git -C "$r" merge --no-ff iv-gu/harvest-r4-review -m "Merge iv-gu/harvest-r4-review: upstream harvest round 4, Round 2 — the review pipeline" && git -C "$r" log --oneline -1
done
git -C "$IE" push origin main
for rem in $(git -C "$CE" remote); do git -C "$CE" push "$rem" main; done
for r in "$IE" "$CE"; do git -C "$r" branch -d iv-gu/harvest-r4-review; done
```
The internal edition's push prints a branch-protection bypass notice; confirm `git -C "$IE" rev-parse main origin/main` (equal) and, for the Copilot edition, `main` equal to every `<remote>/main`.

- [ ] **Step 2: Write the harvest record** in `$AW/docs/superpowers/harvest/NEXT.md` (never naming the internal edition):
  1. Retitle `## Harvest round 4 — surveyed 2026-10-02; Round 1 SHIPPED (2026-10-02)` to `## Harvest round 4 — surveyed 2026-10-02; Rounds 1–2 SHIPPED (2026-10-02)`.
  2. Insert directly above `**Backlog — surveyed, not yet built**` the block below, with the two merge shas Step 1 printed, `<R>` the number of review rounds Tasks 7–9 took, and the findings worth keeping from those rounds in the last list (each as one line: what was wrong, where, what it taught):

```markdown
**Round 2 — what shipped** (the review pipeline, items 7–12, plus item 13 found while reading). This repository: `workflows-core` 1.11.0, `dev-workflows` 4.6.0, `product-workflows` 3.12.0, `docs-workflows` 1.5.0 (merged with this entry). The internal edition: `dev-workflows` 2.67.0, merge `<sha>`. The Copilot edition: `dev-workflows` 2.36.0, merge `<sha>`. Spec + plan: `docs/superpowers/specs/2026-10-02-harvest-round-4-review-pipeline-design.md`, `docs/superpowers/plans/2026-10-02-harvest-round-4-review-pipeline.md`.
7. `finding-triage` dismissed a claim it "could not substantiate", so a serious-if-true `BLOCKER` vanished; a third outcome, `unverified`, records one that would be `MAJOR`+ if true with what would settle it, never reaches a fixer, and changes nothing the verdict gates. The patch gate never edits an instruction or contributor file the change did not edit; the triage line sums survived + unverified + dismissed (BMAD 3433612d, b0d27c3c).
8. The re-review was not triaged, and every caller stopped on the second verdict's word — on a `BLOCKER` triage had already refuted. § On re-review carries a logged row's outcome forward (`carried`), runs no fixer after a re-review, stops only when the review **stayed blocked**, and lets the user settle a `BLOCK` no surviving `BLOCKER` supports (BMAD 7c3e5827, 85d968fc).
9. `code-review` grades by effect where no dimension fixes the grade and lists what it declined to judge; triage raises a grade by effect, to `MAJOR` at most, and rules on each declined line (superpowers 5bf4e780 #2319).
10. Plans carry a Review focus — `risk-planner`'s `### Review focus`, `/implement` Phase 2A item 9 — which `test-writer` tests and `code-review` checks (superpowers 5bf4e780).
11. `code-review` dimension 4: implicit branches, handle lifetime, call against declaration, removed contracts (BMAD 44e0f806).
12. `code-review` finds the repository's documented standards before dimension 3 (BMAD 23f134e2; mattpocock code-review step 3).
13. Five commands escalated per a `Review verdict BLOCK` rule `escalation-rules` did not have, and `/design` cited the `/epics` one, whose "Defer" writes into a draft its handoff then refuses; the new heading `… — commands that fix inline` is theirs. `/specify` keeps the `/epics` rule on purpose.

**Found while planning — keep these:** the stop is reached two ways, so it has one name, *stayed blocked*; `/implement`'s first-review settle prompt's Keep-the-verdict and Cancel arms were stops after files were written that no early-stop list named, so neither committed the work; every edit file was dry-run against all three trees and the whole round applied to throwaway copies (gates and checks green) before the plan was written, which found four gaps the population sweep had missed.

**<R> whole-branch review rounds** — findings worth keeping:
- <one line per finding worth keeping>
```

  3. In the backlog, append ` — shipped in Round 2` to items 7–12.
  4. Under **Recorded divergences**, add: *BMAD's severity reset is not ported* (its reviewers lack the context ours carry); *BMAD's follow-up-review recommendation is not ported* (our re-review after a `BLOCK` fix cycle is automatic and capped); *`/specify` keeps the `/epics` escalation rule* (it defines its own "Defer" to mirror `/epics`).

- [ ] **Step 3: Commit, gate, merge, push** — commit the record (`docs(harvest): record round 4 — Round 2 shipped in three editions`), re-run `"$S/gates.sh" aw "$AW"` → `EXIT=0` and `check.py aw` → `107/107`, then from the main tree, which stands on `main`:

```bash
test "$(git -C /workspace/ai-workflows branch --show-current)" = main && test -z "$(git -C /workspace/ai-workflows status --porcelain)" && git -C /workspace/ai-workflows fetch -q origin && git -C /workspace/ai-workflows merge -q --ff-only origin/main && git -C /workspace/ai-workflows merge --no-ff iv-gu/harvest-r4-review -m "Merge iv-gu/harvest-r4-review: upstream harvest round 4, Round 2 — the review pipeline (workflows-core 1.11.0, dev-workflows 4.6.0, product-workflows 3.12.0, docs-workflows 1.5.0)" && git -C /workspace/ai-workflows push origin main
```

- [ ] **Step 4: Clean up** — `git -C /workspace/ai-workflows worktree remove "$AW" && git -C /workspace/ai-workflows branch -d iv-gu/harvest-r4-review`; confirm each repository: on `main`, clean, `main` equal to every remote's `main`, no `iv-gu/harvest-r4-review` branch locally or on a remote, one worktree.
- [ ] **Step 5: Installed copies** (the operator's step) — `claude plugin update workflows-core@shipwright`, `dev-workflows@shipwright`, `product-workflows@shipwright`, `docs-workflows@shipwright`, then restart; `copilot plugin update dev-workflows@ihudak-copilot-plugins`; the internal edition wherever it is installed.

---

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

#### `scripts/count.py`

`````python
#!/usr/bin/env python3
"""Wrap-insensitive count of a literal (or, with --regex, a pattern) in a repository's tracked
markdown, excluding docs/superpowers/ and, with --no-changelog, every CHANGELOG.md.

usage: count.py ROOT TEXT [--regex] [--no-changelog] [--ignore-case]
Prints one line per file with a hit, then TOTAL <n>.
"""
import re, subprocess, sys

root, needle = sys.argv[1], sys.argv[2]
flags = set(sys.argv[3:])
files = subprocess.run(['git', '-C', root, 'ls-files', '-z', '--', '*.md'],
                       capture_output=True, text=True, check=True).stdout.split('\0')
if '--regex' in flags:
    pat = re.compile(needle, re.I if '--ignore-case' in flags else 0)
else:
    pat = re.compile(r'\s+'.join(map(re.escape, needle.split())), re.I if '--ignore-case' in flags else 0)
total = 0
for f in filter(None, files):
    if f.startswith('docs/superpowers/'):
        continue
    if '--no-changelog' in flags and f.endswith('CHANGELOG.md'):
        continue
    n = len(pat.findall(open(f'{root}/{f}').read()))
    if n:
        print(f'{n:4d}  {f}')
        total += n
print(f'TOTAL {total}')
`````

#### `scripts/gen.py`

`````python
#!/usr/bin/env python3
"""gen.py EDITION TEMPLATE > OUT — substitute the {{...}} dialect placeholders for aw | ie | ce."""
import sys
ARR = ('"Provide manual fix notes (you\'ll be prompted)", "Defer to a follow-up issue (record in the final report)", '
       '"Override and accept the finding", "Cancel the whole run"')
V = {
    'aw': {'FT': 'workflows-core:finding-triage', 'IMPL': '/implement', 'DOCCMD': '/document', 'EPICSCMD': '/epics',
           'REVIEW': 'Opus review', 'SPECCMD': '/specify', 'VULNCMD': '/vuln'},
    'ie': {'FT': '${CLAUDE_PLUGIN_ROOT}/references/finding-triage.md', 'IMPL': '/implement', 'DOCCMD': '/document',
           'EPICSCMD': '/epics', 'CALLERS13': '`/create-vi`, `/update-vi`, `/create-ard` and `/design`', 'ARR13': ARR,
           'REVIEW': 'Opus review', 'SPECCMD': '/specify', 'VULNCMD': '/vuln'},
    'ce': {'FT': '~/.copilot/installed-plugins/ihudak-copilot-plugins/dev-workflows/skills/_shared/finding-triage.md',
           'IMPL': 'implement:', 'DOCCMD': 'document:', 'EPICSCMD': 'epics:',
           'CALLERS13': '`create-vi:`, `update-vi:`, `create-ard:` and `design:`', 'ARR13': ARR + ', "Other… (describe)"',
           'REVIEW': 'review-tier review', 'SPECCMD': 'specify:', 'VULNCMD': 'vuln:'},
}[sys.argv[1]]
t = open(sys.argv[2]).read()
for k, v in V.items():
    t = t.replace('{{' + k + '}}', v)
assert '{{' not in t, 'unsubstituted placeholder in ' + sys.argv[2]
sys.stdout.write(t)
`````

#### `scripts/check.py`

`````python
#!/usr/bin/env python3
"""check.py EDITION ROOT — Round 2's red/green checks. Exit 0 only when every check passes.

Counts are wrap-insensitive (whitespace runs collapse on both sides) over the file named, or with
'*' over every tracked *.md outside docs/superpowers/ with CHANGELOG.md excluded."""
import re, subprocess, sys
ed, root = sys.argv[1], sys.argv[2]
def text(f): return open(f'{root}/{f}').read()
def files():
    out = subprocess.run(['git', '-C', root, 'ls-files', '-z', '--', '*.md'], capture_output=True, text=True).stdout
    return [f for f in out.split('\0') if f and not f.startswith('docs/superpowers/') and not f.endswith('CHANGELOG.md')]
def count(f, s):
    pat = re.compile(r'\s+'.join(map(re.escape, s.split())))
    return sum(len(pat.findall(text(x))) for x in (files() if f == '*' else [f]))
P = {'aw': dict(ft='plugins/workflows-core/references/finding-triage.md', cr='plugins/dev-workflows/agents/code-review.md',
               rp='plugins/dev-workflows/agents/risk-planner.md', tw='plugins/dev-workflows/agents/test-writer.md',
               rf='plugins/dev-workflows/agents/review-fixer.md', df='plugins/workflows-core/agents/doc-fixer.md',
               er='plugins/workflows-core/references/escalation-rules.md', cl='plugins/workflows-core/references/model-routing/classification.md',
               ch='plugins/dev-workflows/references/code-handoff.md',
               impl='plugins/dev-workflows/commands/implement.md', vuln='plugins/dev-workflows/commands/vuln.md',
               upg='plugins/dev-workflows/commands/upgrade.md', doc='plugins/docs-workflows/commands/document.md',
               epics='plugins/product-workflows/commands/epics.md', design='plugins/dev-workflows/commands/design.md',
               spec='plugins/product-workflows/commands/specify.md',
               inline=['plugins/product-workflows/commands/create-prd.md', 'plugins/product-workflows/commands/update-prd.md',
                       'plugins/product-workflows/commands/create-ard.md', 'plugins/dev-workflows/commands/design.md',
                       'plugins/product-workflows/commands/prd-proposal.md', 'plugins/product-workflows/commands/brd-proposal.md'],
               props=['plugins/product-workflows/commands/prd-proposal.md', 'plugins/product-workflows/commands/brd-proposal.md'],
               dox=['plugins/docs-workflows/commands/docs-init.md', 'plugins/docs-workflows/commands/docs-brand.md', 'plugins/docs-workflows/commands/docs-audit.md'],
               rules=['.claude/rules/workflows-core.md', '.claude/rules/dev-workflows.md', '.claude/rules/docs-workflows.md'],
               pages=['plugins/dev-workflows/docs/commands/implement.md', 'plugins/dev-workflows/docs/commands/vuln.md',
                      'plugins/dev-workflows/docs/commands/upgrade.md', 'plugins/docs-workflows/docs/commands/document.md',
                      'plugins/product-workflows/docs/commands/epics.md', 'plugins/docs-workflows/docs/commands/docs-audit.md',
                      'plugins/docs-workflows/docs/commands/docs-init.md', 'plugins/product-workflows/docs/commands/prd-proposal.md',
                      'plugins/workflows-core/docs/reference/references.md'],
               limits=['.claude/rules/docs-workflows.md', '.claude/rules/workflows-core.md', '.claude/rules/dev-workflows.md']),
     'ie': dict(ft='plugins/dev-workflows/references/finding-triage.md', cr='plugins/dev-workflows/agents/code-review.md',
               rp='plugins/dev-workflows/agents/risk-planner.md', tw='plugins/dev-workflows/agents/test-writer.md',
               rf='plugins/dev-workflows/agents/review-fixer.md', df='plugins/dev-workflows/agents/doc-fixer.md',
               er='plugins/dev-workflows/references/escalation-rules.md', cl='plugins/dev-workflows/references/model-routing/classification.md',
               ch='plugins/dev-workflows/references/code-repo-handoff.md',
               impl='plugins/dev-workflows/commands/implement.md', vuln='plugins/dev-workflows/commands/vuln.md',
               upg='plugins/dev-workflows/commands/upgrade.md', doc='plugins/dev-workflows/commands/document.md',
               epics='plugins/dev-workflows/commands/epics.md', design='plugins/dev-workflows/commands/design.md',
               spec='plugins/dev-workflows/commands/specify.md',
               inline=[f'plugins/dev-workflows/commands/{c}.md' for c in ('create-vi', 'update-vi', 'create-ard', 'design')],
               props=[], dox=[], rules=['.claude/rules/dev-workflows-code.md', '.claude/rules/dev-workflows-docs.md'],
               pages=[f'plugins/dev-workflows/docs/commands/{c}.md' for c in ('implement', 'vuln', 'upgrade', 'document', 'epics')]
                     + ['plugins/dev-workflows/docs/reference/references.md'], limits=[]),
     'ce': dict(ft='dev-workflows/skills/_shared/finding-triage.md', cr='dev-workflows/agents/code-review.md',
               rp='dev-workflows/agents/risk-planner.md', tw='dev-workflows/agents/test-writer.md',
               rf='dev-workflows/agents/review-fixer.md', df='dev-workflows/agents/doc-fixer.md',
               er='dev-workflows/skills/_shared/escalation-rules.md', cl='dev-workflows/skills/_shared/model-routing.md',
               ch='dev-workflows/skills/_shared/code-repo-handoff.md',
               impl='dev-workflows/skills/implement/SKILL.md', vuln='dev-workflows/skills/vuln/SKILL.md',
               upg='dev-workflows/skills/upgrade/SKILL.md', doc='dev-workflows/skills/document/SKILL.md',
               epics='dev-workflows/skills/epics/SKILL.md', design='dev-workflows/skills/design/SKILL.md',
               spec='dev-workflows/skills/specify/SKILL.md',
               inline=[f'dev-workflows/skills/{c}/SKILL.md' for c in ('create-vi', 'update-vi', 'create-ard', 'design')],
               props=[], dox=[], rules=['.github/instructions/dev-workflows-shared.instructions.md', '.github/instructions/dev-workflows-skill-map.instructions.md'],
               pages=[f'dev-workflows/docs/skills/{c}.md' for c in ('implement', 'vuln', 'upgrade', 'document', 'epics')]
                     + ['dev-workflows/docs/reference/references.md'],
               limits=['.github/instructions/dev-workflows-shared.instructions.md', '.github/instructions/dev-workflows-skill-map.instructions.md'])}[ed]
C = []  # (file, string, op, n)
for s in ['could not substantiate', 'keep or dismiss', 'If the second verdict is still', 'second verdict still', 'still-`BLOCK`',
          'review is still `BLOCK`', 'verdict still `BLOCK` after its single allowed', 'returns BLOCK a second time',
          'the `Review verdict BLOCK` rule', 'a documented standard **overrides**', 'If review is still BLOCK',
          'if verdict is still BLOCK', 'review stayed `BLOCK`', 'review still `BLOCK`', 'kept or dismissed', 'its three steps']:
    C.append(('*', s, '==', 0))
for s in ['Mark unverified', '## On re-review', '**stayed blocked**', 'The instruction-file clause', '### Declined to judge',
          'Rule on what the reviewer set aside', 'settle prompts', 'carried']:
    C.append((P['ft'], s, '>=', 1))
for s in ['Grade by effect', 'Set nothing aside silently', 'Implicit branches', 'Handle lifetime', 'Call against declaration',
          'Removed contracts', 'CODING_STANDARDS.md', 'carries a Review focus section', 'NEVER set a behaviour aside silently']:
    C.append((P['cr'], s, '>=', 1))
C.append((P['cr'], '### Declined to judge', '>=', 3))
C.append((P['cr'], '.github/copilot-instructions.md' if ed == 'ce' else '.claude/rules/', '>=', 1))
C += [(P['rp'], '### Review focus', '>=', 2), (P['rp'], 'Name the review focus', '>=', 1), (P['tw'], '**Review focus**', '>=', 1),
      (P['rf'], 'CODING_STANDARDS.md', '>=', 1), (P['df'], 'CODING_STANDARDS.md', '>=', 1),
      (P['er'], '— commands that fix inline', '>=', 1), (P['er'], 'or when the review stayed blocked (`finding-triage.md`', '==', 2),
      (P['cl'], 'an unverified record', '>=', 1), (P['cl'], 'removed code whose contract', '>=', 1), (P['ch'], 'stayed blocked', '>=', 1),
      (P['impl'], '9. **Review focus**', '>=', 1), (P['impl'], 'Declined to judge', '>=', 1), (P['impl'], 'stayed blocked', '>=', 6),
      (P['impl'], 'settle prompt', '>=', 3 if ed == 'aw' else 2), (P['spec'], 'one fix cycle) — ' + ('epics:' if ed == 'ce' else '/epics'), '>=', 1),
      (P['design'], 'commands that fix inline', '>=', 1)]
for f in (P['impl'], P['vuln'], P['upg'], P['doc'], P['epics']):
    C += [(f, '§ On re-review', '>=', 1), (f, 'stayed blocked', '>=', 1), (f, 'U unverified', '>=', 1), (f, 'mark it unverified', '>=', 1)]
for f in P['inline']: C.append((f, 'commands that fix inline', '>=', 1))
for f in P['props']: C += [(f, '§ On re-review', '>=', 1), (f, 'stayed blocked', '>=', 1), (f, 'unverified', '>=', 2)]
for f in P['dox']: C += [(f, 'mark it unverified', '>=', 1), (f, 'U unverified', '>=', 1), (f, 'this run did not itself write', '>=', 1)]
for f in P['rules']: C.append((f, 'unverified', '>=', 1))
for f in P['pages']: C.append((f, 'unverified', '>=', 1))
bad = 0
for f, s, op, n in C:
    got = count(f, s)
    ok = got == n if op == '==' else got >= n
    if not ok:
        bad += 1; print(f'FAIL  {f}: "{s}" {op} {n}, got {got}')
for f in P['limits']:
    n = len(text(f))
    if n >= 20000: bad += 1; print(f'FAIL  {f}: {n} characters, limit 20,000')
print(f'{ed}: {len(C) + len(P["limits"]) - bad}/{len(C) + len(P["limits"])} checks pass')
sys.exit(1 if bad else 0)
`````

#### `scripts/apply.sh`

`````bash
#!/usr/bin/env bash
# apply.sh EDITION ROOT [--dry] — apply every Round 2 edit file to one edition, in order. Stops at the first mismatch.
set -euo pipefail
ed=$1; R=$2; dry=${3:-}; S=$(cd "$(dirname "$0")" && pwd); E=$S/edits; G=$S/gen; mkdir -p "$G"
w(){ python3 "$S/wsub.py" "$R/$1" "$2" $dry; }
g(){ python3 "$S/gen.py" "$ed" "$E/$1" > "$G/$ed-${1%.*}.txt"; echo "$G/$ed-${1%.*}.txt"; }
case $ed in
aw)
  w plugins/workflows-core/references/finding-triage.md "$(g triage-core.txt)"
  w plugins/workflows-core/references/finding-triage.md "$E/aw-triage.txt"
  w plugins/dev-workflows/agents/code-review.md "$E/all-code-review.txt"
  w plugins/dev-workflows/agents/risk-planner.md "$E/all-risk-planner.txt"
  w plugins/dev-workflows/agents/test-writer.md "$E/all-test-writer.txt"
  w plugins/dev-workflows/agents/review-fixer.md "$E/all-review-fixer.txt"
  w plugins/dev-workflows/agents/vuln-fixer.md "$(g ed-vuln-fixer.tpl)"
  w CLAUDE.md "$E/aw-claude-md.txt"
  w plugins/workflows-core/agents/doc-fixer.md "$E/all-doc-fixer.txt"
  w plugins/docs-workflows/agents/docs-audit-reviewer.md "$E/aw-agents-triage.txt"
  w plugins/product-workflows/agents/proposal-reviewer.md "$E/aw-proposal-reviewer.txt"
  w plugins/workflows-core/references/model-routing/classification.md "$E/all-classification.txt"
  w plugins/dev-workflows/commands/implement.md "$E/aw-implement.txt"
  w plugins/dev-workflows/commands/vuln.md "$E/aw-vuln.txt"
  w plugins/dev-workflows/commands/upgrade.md "$E/aw-upgrade.txt"
  w plugins/dev-workflows/references/code-handoff.md "$E/aw-code-handoff.txt"
  w plugins/docs-workflows/commands/document.md "$E/aw-document.txt"
  w plugins/product-workflows/commands/epics.md "$E/aw-epics.txt"
  w plugins/product-workflows/commands/prd-proposal.md "$E/aw-prd-proposal.txt"
  w plugins/product-workflows/commands/brd-proposal.md "$E/aw-brd-proposal.txt"
  for c in docs-init docs-brand docs-audit; do w plugins/docs-workflows/commands/$c.md "$E/aw-$c.txt"; done
  w plugins/workflows-core/references/escalation-rules.md "$E/aw-escalation.txt"
  w plugins/product-workflows/commands/create-prd.md "$E/aw-create-prd.txt"
  for c in update-prd create-ard; do w plugins/product-workflows/commands/$c.md "$E/aw-bare-pointer.txt"; done
  w plugins/dev-workflows/commands/design.md "$(g ed-design-pointer.tpl)"
  for c in create-prd update-prd; do w plugins/product-workflows/docs/commands/$c.md "$E/aw-prd-docs.txt"; done
  w .claude/rules/workflows-core.md "$E/aw-rules-wc.txt"
  w .claude/rules/dev-workflows.md "$E/aw-rules-dw.txt"
  w .claude/rules/dev-workflows.md "$E/aw-rules-fixer.txt"
  w .claude/rules/docs-workflows.md "$E/all-rules-docs.txt"
  w .claude/rules/dev-workflows-tests.md "$E/aw-rules-tests.txt"
  w plugins/dev-workflows/docs/commands/implement.md "$E/aw-doc-implement.txt"
  for c in vuln upgrade; do w plugins/dev-workflows/docs/commands/$c.md "$E/aw-doc-$c.txt"; done
  w plugins/docs-workflows/docs/commands/document.md "$E/aw-doc-document.txt"
  w plugins/product-workflows/docs/commands/epics.md "$E/aw-doc-epics.txt"
  for p in plugins/docs-workflows/docs/commands/docs-audit.md plugins/product-workflows/docs/commands/prd-proposal.md; do w $p "$E/aw-doc-dismissal-is.txt"; done; w plugins/docs-workflows/docs/commands/docs-init.md "$E/aw-doc-dismissal-init.txt"
  w plugins/docs-workflows/docs/commands/docs-audit.md "$E/aw-doc-docs-audit.txt"
  w plugins/docs-workflows/references/docs-workflow/scaffold-tree.md "$E/aw-scaffold-tree.txt"
  w plugins/docs-workflows/docs/commands/docs-init.md "$E/aw-doc-docs-init.txt"
  w plugins/docs-workflows/docs/commands/docs-brand.md "$E/aw-doc-docs-brand.txt"
  w plugins/workflows-core/docs/reference/references.md "$E/aw-doc-wc-refs.txt" ;;
ie|ce)
  if [ $ed = ie ]; then P=plugins/dev-workflows; FT=$P/references; CMD(){ echo $P/commands/$1.md; }; DOCP(){ echo $P/docs/commands/$1.md; }; REF=$P/docs/reference/references.md
  else P=dev-workflows; FT=$P/skills/_shared; CMD(){ echo $P/skills/$1/SKILL.md; }; DOCP(){ echo $P/docs/skills/$1.md; }; REF=$P/docs/reference/references.md; fi
  w $FT/finding-triage.md "$(g triage-core.txt)"
  w $P/agents/code-review.md "$E/all-code-review.txt"
  if [ $ed = ce ]; then  # ce-code-review.txt edits text all-code-review.txt inserts: a dry run checks it on a copy with that applied
    if [ -z "$dry" ]; then w $P/agents/code-review.md "$E/ce-code-review.txt"
    else t=$(mktemp); cp "$R/$P/agents/code-review.md" "$t"; python3 "$S/wsub.py" "$t" "$E/all-code-review.txt" >/dev/null && python3 "$S/wsub.py" "$t" "$E/ce-code-review.txt" --dry; rc=$?; rm -f "$t"; [ $rc = 0 ]; fi
  fi
  w $P/agents/risk-planner.md "$E/all-risk-planner.txt"
  w $P/agents/test-writer.md "$E/all-test-writer.txt"
  w $P/agents/review-fixer.md "$E/all-review-fixer.txt"
  w $P/agents/vuln-fixer.md "$(g ed-vuln-fixer.tpl)"
  w $P/agents/doc-fixer.md "$E/all-doc-fixer.txt"
  if [ $ed = ie ]; then w $FT/model-routing/classification.md "$E/all-classification.txt"; else w $FT/model-routing.md "$E/all-classification.txt"; fi
  for c in implement vuln upgrade document epics; do w $(CMD $c) "$(g ed-$c.tpl)"; done
  if [ $ed = ie ]; then w $FT/code-repo-handoff.md "$E/aw-code-handoff.txt"; else w $FT/code-repo-handoff.md "$E/ce-code-handoff.txt"; fi
  w $FT/escalation-rules.md "$(g ed-escalation.tpl)"
  w $(CMD create-vi) "$(g ed-create-vi.tpl)"
  for c in update-vi create-ard; do w $(CMD $c) "$(g ed-bare-pointer.tpl)"; done
  w $(CMD design) "$(g ed-design-pointer.tpl)"
  if [ $ed = ie ]; then
    w .claude/rules/dev-workflows-code.md "$E/aw-rules-wc.txt"; w .claude/rules/dev-workflows-code.md "$E/aw-rules-dw.txt"; w .claude/rules/dev-workflows-code.md "$E/ie-rules-fixer.txt"
    w .claude/rules/dev-workflows-docs.md "$E/all-rules-docs.txt"
    w $(DOCP implement) "$E/aw-doc-implement.txt"; w $(DOCP implement) "$E/ed-doc-failed-gate.txt"
    for c in vuln upgrade document epics; do w $(DOCP $c) "$E/aw-doc-$c.txt"; done
  else
    w .github/instructions/dev-workflows-shared.instructions.md "$E/ce-shared-instr.txt"
    w .github/instructions/dev-workflows-skill-map.instructions.md "$E/ce-skillmap.txt"
    for c in implement vuln upgrade document epics; do w $(DOCP $c) "$E/ce-doc-$c.txt"; done
  fi
  for c in create-vi update-vi; do w $(DOCP $c) "$E/ed-doc-vi-choices.txt"; done
  w $REF "$E/aw-doc-wc-refs.txt" ;;
esac
echo "apply.sh $ed: done"
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
"""release.py EDITION ROOT — bump Round 2's versions and insert its changelog sections ($S/cl/<ed>-<plugin>.md)."""
import json, os, re, sys
ed, root = sys.argv[1], sys.argv[2]
S = os.path.dirname(os.path.abspath(__file__))
R = {'aw': ('.claude-plugin/marketplace.json', {
         'workflows-core': ('1.10.0', '1.11.0', 'plugins/workflows-core/.claude-plugin/plugin.json', 'plugins/workflows-core/CHANGELOG.md'),
         'dev-workflows': ('4.5.0', '4.6.0', 'plugins/dev-workflows/.claude-plugin/plugin.json', 'plugins/dev-workflows/CHANGELOG.md'),
         'product-workflows': ('3.11.3', '3.12.0', 'plugins/product-workflows/.claude-plugin/plugin.json', 'plugins/product-workflows/CHANGELOG.md'),
         'docs-workflows': ('1.4.6', '1.5.0', 'plugins/docs-workflows/.claude-plugin/plugin.json', 'plugins/docs-workflows/CHANGELOG.md')}),
     'ie': ('.claude-plugin/marketplace.json', {
         'dev-workflows': ('2.66.0', '2.67.0', 'plugins/dev-workflows/.claude-plugin/plugin.json', 'plugins/dev-workflows/CHANGELOG.md')}),
     'ce': ('.github/plugin/marketplace.json', {
         'dev-workflows': ('2.35.0', '2.36.0', 'dev-workflows/.plugin/plugin.json', 'dev-workflows/CHANGELOG.md')})}[ed]
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
    open(f'{root}/{cl}', 'w').write(c[:i + 1] + sec + '\n\n' + c[i + 1:])
open(f'{root}/{market}', 'w').write(m)
for e in json.load(open(f'{root}/{market}'))['plugins']:
    if e['name'] in plugins: print(e['name'], e['version'], json.load(open(f"{root}/{plugins[e['name']][2]}"))['version'])
`````

## Appendix B — edit files

Extracted by Task 0 Step 2 into `$S/edits`. Each block is `<<<<<<< OLD <n>` (the text, matched whitespace-insensitively, `n` times), `=======`, the replacement, `>>>>>>> NEW`. Prefixes: `all-` every edition unchanged; `aw-` this edition; `ce-` the Copilot edition; `ed-*.tpl` the internal and Copilot editions through `gen.py`; `triage-core.txt` all three through `gen.py`; `ed-doc-*.txt` the internal and Copilot editions unchanged.

#### `edits/all-classification.txt`

`````text
<<<<<<< OLD 1
4. **Missed edge cases** — empty/null/zero/negative/very-large inputs, partial
   failures, concurrent access, time-zone / DST / locale, off-by-one, retries.
=======
4. **Missed edge cases** — empty/null/zero/negative/very-large inputs, partial
   failures, concurrent access, time-zone / DST / locale, off-by-one, retries;
   the unnamed members of a fixed value set the change special-cases, a
   re-check of something already held, a call that disagrees with its
   callee's declaration, and removed code whose contract nothing replaced.
>>>>>>> NEW
<<<<<<< OLD 1
each `CONCERN` — where a disposition is either a fix or a dismissal recorded with a
reason that disposes of that finding's own claim, per
=======
each `CONCERN` — where a disposition is a fix, a dismissal recorded with a reason
that disposes of that finding's own claim, or — for a finding triage could not
settle — an unverified record with what would settle it, per
>>>>>>> NEW
`````

#### `edits/all-code-review.txt`

`````text
<<<<<<< OLD 1
   - **Suggestion** - concrete, minimal fix
5. Derive a verdict:
=======
   - **Suggestion** - concrete, minimal fix

   **Grade by effect.** Where a dimension below fixes a finding's severity,
   that rule governs — dimension 3's judgment-call floor and dimensions 9,
   10 and 11. Everywhere else a finding's severity is what a reasonable
   person using this software meets if the change ships as it stands. The
   task, the plan and the spec say what the change must do, not every input
   it will meet: where they are silent on the input that triggers a finding,
   a reasonable user's expectation is the requirement, and the silence is not
   permission. A crash, lost data or a wrong result on an input nothing
   mentions is graded by that crash, that loss or that result.

   **Set nothing aside silently.** Every behaviour you considered and set
   aside as outside the task, the plan or the spec goes in
   `### Declined to judge`, one line each with the reason. The caller rules
   on each line.
5. Derive a verdict:
>>>>>>> NEW
<<<<<<< OLD 1
3. **Architectural consistency** - follows existing patterns, respects module
   boundaries, uses the right abstraction layer, avoids duplicate
   implementations. As a **floor** when the repo has no documented standard
   (a documented standard **overrides** this list), watch for the classic
   code smells — flag as judgment-call findings (`MINOR`/`NIT`, not hard
   violations): Mysterious Name, Duplicated Code, Feature Envy, Data Clumps,
   Primitive Obsession, Repeated Switches, Shotgun Surgery, Divergent Change,
   Speculative Generality, Message Chains, Middle Man, Refused Bequest.
=======
3. **Architectural consistency** - follows existing patterns, respects module
   boundaries, uses the right abstraction layer, avoids duplicate
   implementations, and honours the repository's **documented standards**.
   Find them before judging this dimension: `CLAUDE.md` and `AGENTS.md` at
   the project root and in every directory between it and a changed file;
   `CONTRIBUTING.md` at the root, in `.github/` or in `docs/`;
   `CODING_STANDARDS.md` at the root; and every file under `.claude/rules/`
   whose `paths:` frontmatter matches a changed file, or which has no
   `paths:`. Read each one that exists. A rule the repository's own lint,
   format or type-check configuration already enforces is that tool's to
   report, not this review's. As a **floor** where those files document no
   standard on a point (a standard documented in one of them **overrides**
   this list), watch for the classic code smells — flag as judgment-call
   findings (`MINOR`/`NIT`, not hard violations): Mysterious Name,
   Duplicated Code, Feature Envy, Data Clumps, Primitive Obsession,
   Repeated Switches, Shotgun Surgery, Divergent Change, Speculative
   Generality, Message Chains, Middle Man, Refused Bequest.
>>>>>>> NEW
<<<<<<< OLD 1
   caller of the same pattern), with no test catching the omission.
5. **Migration risks**
=======
   caller of the same pattern), with no test catching the omission. Then,
   mechanically:
   - **Implicit branches** — where the change special-cases some members of
     a fixed value set (enum values, status codes, sentinels, type tags,
     flags, value ranges), the members it does not name are branches too:
     say what each one meets.
   - **Handle lifetime** — where the changed code re-checks, re-fetches or
     re-validates something it already holds (a handle, an index, an id, a
     pointer), name the intervening call that can invalidate it, what that
     call does to it, and what the code skips when the re-check fails.
   - **Call against declaration** — at every call site the diff adds or
     changes, tests included, read the callee's declaration and check the
     call's argument count, order, types and defaults against it.
   - **Removed contracts** — for code the diff removes or replaces (not a
     pure rename or whitespace change), ask whether it carried a behaviour
     or a contract the change neither re-establishes nor intentionally
     retires. A regression, an orphaned reference or newly dead code is a
     finding.

   Where the **Plan** carries a Review focus section, check each of its
   lines deliberately, and report a finding for each input or failure mode
   the change does not handle the way its line expects.
5. **Migration risks**
>>>>>>> NEW
<<<<<<< OLD 1
- _or_ "no findings — every checkable claim verified"

### Recommended next step
=======
- _or_ "no findings — every checkable claim verified"

### Declined to judge
- [a behaviour you considered and set aside] - [why it is outside the task,
  the plan or the spec]
- _or_ "none — nothing set aside"

### Recommended next step
>>>>>>> NEW
<<<<<<< OLD 1
- NEVER skip a dimension silently - either report findings or say "N/A - reason".
=======
- NEVER skip a dimension silently - either report findings or say "N/A - reason".
- NEVER set a behaviour aside silently - it goes in `### Declined to judge`.
  The `### Re-classification` return and the `Diff: unreadable` return carry
  no such section; every full report does.
>>>>>>> NEW
`````

#### `edits/all-doc-fixer.txt`

`````text
<<<<<<< OLD 1
defer it as `DEFERRED — needs human decision` with that as the reason, rather than adding
     speculative content.
=======
defer it as `DEFERRED — needs human decision` with that as the reason, rather than adding
     speculative content. A fix that would edit an instruction file the gate names (`CLAUDE.md`,
     `AGENTS.md`, `.github/copilot-instructions.md`, a file under `.claude/rules/` or
     `.github/instructions/`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`) is deferred the same way unless
     the finding's own location is in that file — you are not handed the diff, and a finding located in
     such a file is one the review raised against that file's own text.
>>>>>>> NEW
`````

#### `edits/all-review-fixer.txt`

`````text
<<<<<<< OLD 1
public surface and **guard no state the finding did not demonstrate**. If the smallest correct fix
     would add such a guard, defer it as `DEFERRED — needs human decision` with that as the reason,
     rather than adding speculative defence.
=======
public surface, **guard no state the finding did not demonstrate**, and edit no instruction file the
     gate names (`CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, a file under
     `.claude/rules/` or `.github/instructions/`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`) unless the
     finding's own location is in that file — you are not handed the diff, and a finding located in
     such a file is one the review raised against that file's own text. If the smallest correct fix
     would add such a guard or make such an edit, defer it as `DEFERRED — needs human decision` with
     that as the reason: never add speculative defence, and never edit such a file to make a finding
     go away.
>>>>>>> NEW
`````

#### `edits/all-risk-planner.txt`

`````text
<<<<<<< OLD 1
### Acceptance checks
- [concrete observable conditions that prove success]
```
=======
### Acceptance checks
- [concrete observable conditions that prove success]

### Review focus
1. [an input class or failure mode the task implies and no step's tests
   exercise] - [the behaviour a reasonable user would expect]
2. ...
_or_ "none — checked"
```
>>>>>>> NEW
<<<<<<< OLD 1
  written the code — cut them back to the decisions. The other sections are
  not measured against the change.
=======
  written the code — cut them back to the decisions. The other sections are
  not measured against the change.
- **Name the review focus.** In `### Review focus`, list up to five input
  classes or failure modes the task implies and no step's tests exercise,
  most likely to bite a user first, each with the behaviour a reasonable
  user would expect. Draw them from the task, the spec where the brief
  carries one, and the code the steps touch: the spec says what the change
  must do, not every input it will meet, and its silence on one is not
  permission for that input to break the program. `code-review` checks
  each line, and where the command dispatches `test-writer` it writes a
  test for each or names in its `### Notes` why one cannot be written, so
  every line is acted on. `none — checked` means you looked and found
  none, never that you skipped the look.
>>>>>>> NEW
`````

#### `edits/all-rules-docs.txt`

`````text
<<<<<<< OLD 1
— each finding verified at the location it names, every dismissal recorded with a reason that disposes of that finding's own claim, survivors only,
=======
— each finding verified at the location it names; kept, marked unverified, or dismissed with a reason that disposes of its own claim; survivors only,
>>>>>>> NEW
`````

#### `edits/all-test-writer.txt`

`````text
<<<<<<< OLD 1
   - **Flag as `### Skipped (pre-existing untested code)`**: files that clearly pre-existed and remain untested — this agent never retrofits tests for unchanged code.
=======
   - **Flag as `### Skipped (pre-existing untested code)`**: files that clearly pre-existed and remain untested — this agent never retrofits tests for unchanged code.
   - **Review focus**: where the **Plan** carries a Review focus section, each line names an input class or failure mode this change must handle and the behaviour expected of it — map each line to the behaviour it covers and write the test that pins it, under step 5's rules. A line you cannot test in isolation goes in `### Notes` with the reason; never drop one silently.
>>>>>>> NEW
<<<<<<< OLD 1
Write against the conventions of the test files that command already runs, and where you can find none, write nothing and say so in `### Notes` rather than inventing a framework.
=======
Write against the conventions of the test files that command already runs, and where you can find none, write no test against that suite — name in `### Notes`, as untested, each behaviour step 3 finds in a changed file no other suite's tests live alongside — every one, where this is the baseline's only suite — rather than inventing a framework.
>>>>>>> NEW
`````

#### `edits/aw-agents-triage.txt`

`````text
<<<<<<< OLD 1
a second copy of its three steps in an agent body is the drift it exists to prevent.
=======
a second copy of its steps in an agent body is the drift it exists to prevent.
>>>>>>> NEW
`````

#### `edits/aw-bare-pointer.txt`

`````text
<<<<<<< OLD 1
the `Review verdict BLOCK` rule in `workflows-core:escalation-rules`
=======
the `Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline` rule in `workflows-core:escalation-rules`
>>>>>>> NEW
`````

#### `edits/aw-brd-proposal.txt`

`````text
<<<<<<< OLD 1
Verify each finding's claimed consequence at the location it names, keep or dismiss it, and record every dismissal with a reason that disposes of that finding's own claim. There is no silent-drop disposition. Fix the surviving BLOCKERs inline (the orchestrator edits both artifacts — there is no delegated writer) and re-review **once**; if still `BLOCK`, escalate per the `Review verdict BLOCK` rule in `Skill(skill: "workflows-core:reference", args: "escalation-rules")`. `PASS` / `PASS WITH RECOMMENDATIONS` → proceed. Cap: one fix cycle plus one re-review. Where triage empties the survivor set, do not dispatch a fix cycle with nothing to apply and do not silently promote the verdict — the user settles a verdict its own findings no longer support.
=======
Verify each finding's claimed consequence at the location it names; keep it, mark it unverified, or
   dismiss it; record every dismissal with a reason that disposes of that finding's own claim and every
   unverified finding with what would settle it; and raise a grade only by effect. There is no
   silent-drop disposition. Fix the surviving BLOCKERs inline (the orchestrator edits both artifacts —
   there is no delegated writer) and re-review **once**, triaging that re-review — and one you chose
   at the first settle prompt — under that reference's § On re-review. If the review **stayed
   blocked** — a BLOCKER survives that triage, or you keep the verdict at either settle prompt —
   escalate per the `Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline`
   rule in `Skill(skill: "workflows-core:reference", args: "escalation-rules")`; on § On re-review's
   **Proceed**, proceed as after a verdict that is not `BLOCK`. `PASS` / `PASS WITH RECOMMENDATIONS`
   → proceed. Cap: one fix cycle plus one re-review. Where triage empties the survivor set, do not
   dispatch a fix cycle with nothing to apply and do not silently promote the verdict — the user
   settles a verdict its own findings no longer support. At either of that reference's settle
   prompts, **Keep the verdict** means the review stayed blocked — on a kept verdict that is not
   `BLOCK`, which raised no BLOCKER, the run ends as Cancel does — and **Cancel** aborts the run.
>>>>>>> NEW
<<<<<<< OLD 1
Report findings reviewed, survivors, and every dismissal with its reason: a triage that reports only
survivors is indistinguishable from a reviewer that found less.
=======
Report the triage per `workflows-core:finding-triage` § Reporting — one line per review pass, naming
the counts, the survivors, the unverified findings, every dismissal with its reason and any settle
prompt's answer: a triage that reports only survivors is indistinguishable from a reviewer that found
less.
>>>>>>> NEW
<<<<<<< OLD 1
slices it affects; the pre-lint findings; the `proposal-reviewer` verdict with the triage line —
findings reviewed, survivors, and every dismissal with its reason — and every survivor whose location
was a slice document rather than the umbrella; resolved model routing (+ any Opus gate or
degradation, or
=======
slices it affects; the pre-lint findings; the `proposal-reviewer` verdict with the triage line per
`workflows-core:finding-triage` § Reporting — the counts, survivors, unverified findings, every
dismissal with its reason and any settle prompt's answer — and every survivor whose location was a
slice document rather than the umbrella; resolved model routing (+ any Opus gate or degradation, or
>>>>>>> NEW
`````

#### `edits/aw-claude-md.txt`

`````text
<<<<<<< OLD 1
`workflows-core:finding-triage` — the orchestrator's verify-and-dismiss step between a reviewer's findings and a fixer, and the patch gate
=======
`workflows-core:finding-triage` — the orchestrator's step between a reviewer's findings and a fixer (keep, mark unverified or dismiss), its re-review rules, and the patch gate
>>>>>>> NEW
`````

#### `edits/aw-code-handoff.txt`

`````text
<<<<<<< OLD 1
- an Opus review verdict still `BLOCK` after its single allowed fix cycle plus re-review;
=======
- an Opus review that stayed blocked — a `BLOCKER` survived its re-review's triage, or the user kept its verdict at a settle prompt (or, in `/vuln` and `/upgrade`, cancelled there);
>>>>>>> NEW
`````

#### `edits/aw-create-prd.txt`

`````text
<<<<<<< OLD 1
If still `BLOCK`, escalate per the `Review verdict BLOCK` rule in `workflows-core:escalation-rules` for each unresolved BLOCKER (`choices: ["Provide manual fix notes", "Defer to a follow-up issue", "Override and accept", "Cancel"]`).
=======
If still `BLOCK`, escalate per the `Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline` rule in `workflows-core:escalation-rules` for each unresolved BLOCKER individually (`choices: ["Provide manual fix notes (you'll be prompted)", "Defer to a follow-up issue (record in the final report)", "Override and accept the finding", "Cancel the whole run"]`).
>>>>>>> NEW
<<<<<<< OLD 1
Act on the verdict (mirrors `/specify`):
=======
Act on the verdict (mirrors `/specify`, save the escalation rule it cites):
>>>>>>> NEW
`````

#### `edits/aw-doc-dismissal-init.txt`

`````text
<<<<<<< OLD 1
every dismissal is recorded with a reason, and only survivors
=======
every dismissal and every unverified finding is recorded with a reason, and only survivors
>>>>>>> NEW
`````

#### `edits/aw-doc-dismissal-is.txt`

`````text
<<<<<<< OLD 1
every dismissal is recorded with a reason that disposes of that finding's own claim
=======
every dismissal is recorded with a reason that disposes of that finding's own claim and every unverified finding with what would settle it
>>>>>>> NEW
`````

#### `edits/aw-doc-docs-audit.txt`

`````text
<<<<<<< OLD 1
A BLOCKER that is neither fixed nor explicitly overridden stops the run.
=======
A BLOCKER that is neither fixed nor explicitly overridden stops the run. Where triage leaves no finding behind a verdict other than `PASS` standing (every one dismissed or unverified), you settle the verdict at a prompt instead: proceeding continues the run, keeping a `BLOCK` verdict takes that same stop, and keeping any other verdict or cancelling ends the run as a Cancel does.
>>>>>>> NEW
<<<<<<< OLD 1
- `DOCS_AUDIT_UNRESOLVED_BLOCKER` — a BLOCKER finding from `docs-audit-reviewer` was neither fixed nor accepted by you.
=======
- `DOCS_AUDIT_UNRESOLVED_BLOCKER` — a BLOCKER finding from `docs-audit-reviewer` was neither fixed nor accepted by you, or you kept a `BLOCK` verdict after triage left no finding behind it standing.
>>>>>>> NEW
`````

#### `edits/aw-doc-docs-brand.txt`

`````text
<<<<<<< OLD 1
- `DOCS_BRAND_UNRESOLVED_BLOCKER` — a BLOCKER finding from `docs-scaffold-reviewer` was neither fixed nor overridden.
=======
- `DOCS_BRAND_UNRESOLVED_BLOCKER` — a BLOCKER finding from `docs-scaffold-reviewer` was neither fixed nor overridden.
- A Cancel at the review gate, or keeping the review's verdict after triage left no finding behind it standing (every one dismissed or unverified), stops a standalone run there: the branding stays uncommitted on its branch, no pull request is drafted, and the cost entry is still recorded. Settle the findings, check each written path with `git check-ignore <path>` — leave any it prints unstaged, after removing every config reference to it — and commit by hand.
>>>>>>> NEW
<<<<<<< OLD 1
all but `DOCS_BRAND_UNRESOLVED_BLOCKER`, which belongs to the standalone review gate an `--inline` run skips
=======
all but `DOCS_BRAND_UNRESOLVED_BLOCKER` and a stop at the review gate, both of which belong to the standalone review gate an `--inline` run skips
>>>>>>> NEW
`````

#### `edits/aw-doc-docs-init.txt`

`````text
<<<<<<< OLD 1
- `DOCS_INIT_UNRESOLVED_BLOCKER` — a BLOCKER finding from `docs-scaffold-reviewer` was neither fixed nor explicitly overridden.
=======
- `DOCS_INIT_UNRESOLVED_BLOCKER` — a BLOCKER finding from `docs-scaffold-reviewer` was neither fixed nor explicitly overridden.
- A Cancel at the review gate, or keeping the review's verdict after triage left no finding behind it standing (every one dismissed or unverified), stops the run there: the scaffold stays uncommitted on its branch, no pull request is drafted, and the cost entry is still recorded. Settle the findings, check each written path with `git check-ignore <path>` — leave any it prints unstaged, after removing every config reference to it — and commit by hand — a re-run would refuse the scaffolded tree.
>>>>>>> NEW
`````

#### `edits/aw-doc-document.txt`

`````text
<<<<<<< OLD 1
each verified at the location it names, dismissals recorded with a reason — before `doc-fixer` ever sees them
=======
each verified at the location it names, dismissals and unverified findings recorded with a reason — before `doc-fixer` ever sees them
>>>>>>> NEW
`````

#### `edits/aw-doc-epics.txt`

`````text
<<<<<<< OLD 1
every dismissal recorded with a reason, survivors only handed to the fixer.
=======
every dismissal and every unverified finding recorded with a reason, survivors only handed to the fixer.
>>>>>>> NEW
<<<<<<< OLD 1
an unresolved BLOCKER after that cycle is escalated individually.
=======
the re-review is triaged too: a `BLOCKER` surviving that triage, or a verdict you keep, is escalated individually, and a second `BLOCK` that no surviving `BLOCKER` supports is yours to settle.
>>>>>>> NEW
`````

#### `edits/aw-doc-implement.txt`

`````text
<<<<<<< OLD 1
— each finding verified at the location it names, kept or dismissed, every dismissal recorded with a reason that disposes of that finding's own claim; `review-fixer` is handed **survivors only**, and dismissed findings never reach it.
=======
— each finding verified at the location it names and kept, marked unverified (recorded with what would settle it) or dismissed (with a reason that disposes of that finding's own claim); `review-fixer` is handed **survivors only**, and unverified and dismissed findings never reach it.
>>>>>>> NEW
<<<<<<< OLD 1
a `BLOCK` verdict gets one re-review after the fix cycle, and a still-`BLOCK` result stops the run rather than looping.
=======
a `BLOCK` verdict gets one re-review after the fix cycle; the re-review is triaged too, carrying forward what triage already ruled, and a review that stayed blocked — a `BLOCKER` surviving that triage, or a verdict you chose to keep — stops the run rather than looping; a second `BLOCK` that no surviving `BLOCKER` supports is yours to settle.
>>>>>>> NEW
<<<<<<< OLD 1
tests never run on risky work until the review returns a non-`BLOCK` verdict
=======
tests never run on risky work until the review returns a non-`BLOCK` verdict, or you settle a `BLOCK` that no surviving `BLOCKER` supports
>>>>>>> NEW
`````

#### `edits/aw-doc-upgrade.txt`

`````text
<<<<<<< OLD 1
— each finding verified at the location it names, kept or dismissed, every dismissal recorded with a reason;
=======
— each finding verified at the location it names and kept, marked unverified or dismissed, every unverified finding and every dismissal recorded with a reason;
>>>>>>> NEW
<<<<<<< OLD 1
a still-`BLOCK` result stops work on that component rather than looping.
=======
the re-review is triaged too, carrying forward what triage already ruled on that component, and a review that stayed blocked — a `BLOCKER` surviving that triage, or a verdict you chose to keep — stops work on that component rather than looping; a second `BLOCK` that no surviving `BLOCKER` supports is yours to settle, and a Cancel at that prompt also stops only that component while the run goes on.
>>>>>>> NEW
<<<<<<< OLD 1
tests never run on risky work until review returns a non-`BLOCK` verdict
=======
tests never run on risky work until review returns a non-`BLOCK` verdict, or you settle a `BLOCK` that no surviving `BLOCKER` supports
>>>>>>> NEW
`````

#### `edits/aw-doc-vuln.txt`

`````text
<<<<<<< OLD 1
— each finding verified at the location it names, kept or dismissed, every dismissal recorded with a reason;
=======
— each finding verified at the location it names and kept, marked unverified or dismissed, every unverified finding and every dismissal recorded with a reason;
>>>>>>> NEW
<<<<<<< OLD 1
a still-`BLOCK` result stops work on that CVE rather than looping.
=======
the re-review is triaged too, carrying forward what triage already ruled on that CVE, and a review that stayed blocked — a `BLOCKER` surviving that triage, or a verdict you chose to keep — stops work on that CVE rather than looping; a second `BLOCK` that no surviving `BLOCKER` supports is yours to settle, and a Cancel at that prompt also stops only that CVE while the run goes on.
>>>>>>> NEW
<<<<<<< OLD 1
a `### Review triage` section naming every finding reviewed and dismissed, with reasons,
=======
a `### Review triage` section, one line per review pass, counting every finding reviewed and naming each one dismissed or left unverified, with its reason,
>>>>>>> NEW
<<<<<<< OLD 1
tests never run on risky work until review returns a non-`BLOCK` verdict
=======
tests never run on risky work until review returns a non-`BLOCK` verdict, or you settle a `BLOCK` that no surviving `BLOCKER` supports
>>>>>>> NEW
`````

#### `edits/aw-doc-wc-refs.txt`

`````text
<<<<<<< OLD 1
verify each finding at the location it names, record every dismissal with a reason, and hand the fixer survivors only.
=======
verify each finding at the location it names; keep it, mark it unverified with what would settle it, or dismiss it with a reason; triage a re-review against the run's earlier rulings over the same artifact; and hand the fixer survivors only.
>>>>>>> NEW
`````

#### `edits/aw-docs-audit.txt`

`````text
<<<<<<< OLD 1
verify each finding's own claimed consequence at the location it names, keep or dismiss with a reason that disposes of that finding's own claim, carry **survivors only** forward, and carry every dismissal into the Phase 6 report
=======
verify each finding's own claimed consequence at the location it names; keep it, mark it unverified, or dismiss it — a dismissal with a reason that disposes of that finding's own claim, an unverified finding with what would settle it; raise a grade only by effect; carry **survivors only** forward, and carry every dismissal, every unverified finding and every raise into the Phase 6 report, per that reference's § Reporting
>>>>>>> NEW
<<<<<<< OLD 1
fix only a defect a finding actually demonstrated, never guard state it did not show.
=======
fix only a defect a finding actually demonstrated, never guard state it did not show, and never edit an instruction file the gate names that this run did not itself write.
>>>>>>> NEW
<<<<<<< OLD 1
Findings: <N reviewed, M survived triage, K applied, J deferred or overridden with reason | "N/A">
=======
Findings: <N reviewed — M survived triage, U unverified, X dismissed; K applied, J deferred or overridden with reason — every dismissal, unverified finding and raise, and any settle prompt's answer, listed per `workflows-core:finding-triage` § Reporting | "N/A">
>>>>>>> NEW
<<<<<<< OLD 1
Where triage empties the survivor set on a non-PASS verdict, follow that reference's own disposition: surface it and let the operator settle the verdict, never silently promote it to PASS.
=======
Where triage empties the survivor set on a non-PASS verdict, follow that reference's own disposition: surface it and let the operator settle the verdict with the prompt it gives a caller that runs no re-review, never silently promoting it to PASS. **Keep the verdict** there takes the `DOCS_AUDIT_UNRESOLVED_BLOCKER` stop below — or, on a kept verdict that is not `BLOCK`, which raised no BLOCKER, ends the run as Cancel does — and **Cancel** ends the run as a Cancel below does.
>>>>>>> NEW
<<<<<<< OLD 1
Run `git -C <top> check-ignore -v <top>/.dev-workflows/docs-backlog.yml`.
=======
Run `git -C <top> check-ignore -v <top>/.dev-workflows/docs-backlog.yml`; a line it prints whose pattern starts with `!` re-includes the path, and is no match.
>>>>>>> NEW
<<<<<<< OLD 1
Verdict: <PASS | PASS WITH RECOMMENDATIONS | BLOCK, resolved | "N/A — NO_SURFACES, nothing written to review">
=======
Verdict: <PASS | PASS WITH RECOMMENDATIONS | BLOCK, resolved | "N/A — NO_SURFACES, nothing written to review" | "<the verdict> — settled by the user at the settle prompt">
>>>>>>> NEW
<<<<<<< OLD 1
Review verdict: [PASS | PASS WITH RECOMMENDATIONS | BLOCK, resolved | N/A — never reached]
=======
Review verdict: [PASS | PASS WITH RECOMMENDATIONS | BLOCK, resolved | N/A — never reached | <the verdict> — settled by the user at the settle prompt]
>>>>>>> NEW
`````

#### `edits/aw-docs-brand.txt`

`````text
<<<<<<< OLD 1
for each finding, verify its claimed consequence at the location it names; keep or dismiss with a reason that disposes of that finding's own claim; carry survivors only into the next step, and every dismissal into the Phase 11 report.
=======
for each finding, verify its claimed consequence at the location it names; keep it, mark it unverified, or dismiss it — a dismissal with a reason that disposes of that finding's own claim, an unverified finding with what would settle it; raise a grade only by effect; carry survivors only into the next step, and every dismissal, every unverified finding and every raise into the Phase 11 report, per that reference's § Reporting.
>>>>>>> NEW
<<<<<<< OLD 1
fix only a defect a finding actually demonstrated, never guard state it did not show.
=======
fix only a defect a finding actually demonstrated, never guard state it did not show, and never edit an instruction file the gate names that this run did not itself write.
>>>>>>> NEW
<<<<<<< OLD 1
Findings: <N reviewed, M survived triage, K applied, J deferred or overridden with reason | "N/A">
=======
Findings: <N reviewed — M survived triage, U unverified, X dismissed; K applied, J deferred or overridden with reason — every dismissal, unverified finding and raise, and any settle prompt's answer, listed per `workflows-core:finding-triage` § Reporting | "N/A">
>>>>>>> NEW
<<<<<<< OLD 1
Where triage empties the survivor set entirely on a non-PASS verdict, follow the reference's own disposition — surface it and let the operator settle the verdict; never silently promote it to PASS.
=======
Where triage empties the survivor set on a non-PASS verdict, follow that reference's own disposition: surface it and let the operator settle the verdict with the prompt it gives a caller that runs no re-review, never silently promoting it to PASS. **Keep the verdict** and **Cancel** there both stop the run at this gate, by the route below.
>>>>>>> NEW
<<<<<<< OLD 1
the review verdict and every applied or dismissed finding (Phase 9),
=======
the review verdict and every applied, dismissed or unverified finding (Phase 9),
>>>>>>> NEW
<<<<<<< OLD 1
A **BLOCKER** left deferred (neither fixed nor overridden) stops the run before Phase 10:
=======
**A stop at this gate — Cancel at the settle prompt or this one, or Keep the verdict at the settle prompt — ends the run here**: skip Phase 10 and go straight to Phase 11's report, which names the stop — the review cancelled, or its verdict kept for a human decision. The branding Phase 8 applied stays on disk on its branch, uncommitted, and the emitter tail (Phases 12–14) still runs, so this run's cost and any feedback are still recorded.

A **BLOCKER** left deferred (neither fixed nor overridden) stops the run before Phase 10:
>>>>>>> NEW
<<<<<<< OLD 1
Verdict: <PASS | PASS WITH RECOMMENDATIONS | BLOCK, resolved | "N/A — cancelled at Phase 7, never reached">
=======
Verdict: <PASS | PASS WITH RECOMMENDATIONS | BLOCK, resolved | "N/A — cancelled at Phase 7, never reached" | "<the verdict> — stopped at the review gate: cancelled, or kept for a human decision" | "<the verdict> — settled by the user at the settle prompt">
>>>>>>> NEW
<<<<<<< OLD 1
<branch name — N commit(s), NOT pushed and NOT merged | "cancelled at Phase 7 — no branch created, nothing written or committed">
=======
<branch name — N commit(s), NOT pushed and NOT merged | "cancelled at Phase 7 — no branch created, nothing written or committed" | "<branch name> — stopped at the review gate: nothing committed, the written files left on it uncommitted">
>>>>>>> NEW
<<<<<<< OLD 1
(When Phase 7 was cancelled, this whole section reads instead: "none — no branch exists to open a pull request against.")
=======
(When Phase 7 was cancelled, this whole section reads instead: "none — no branch exists to open a pull request against." When the run stopped at the review gate, it reads: "none — nothing was committed to open a pull request from.")
>>>>>>> NEW
<<<<<<< OLD 1
guidance only, never auto-invoked. **When a branch and a drafted PR exist:**
=======
guidance only, never auto-invoked. **After a stop at the review gate:** name the findings left to settle and the branch holding the uncommitted branding; settle them there, check each written path with `git check-ignore <path>` — leave any path it prints unstaged, after removing every config reference to it (`scaffold-tree.md` §7 lists them) — and commit by hand — a re-run would find the tree dirty and offer to stash that work. **When a branch and a drafted PR exist:**
>>>>>>> NEW
<<<<<<< OLD 1
BLOCK, resolved | N/A — cancelled before Phase 9]
=======
BLOCK, resolved | N/A — cancelled before Phase 9 | <the verdict> — stopped at the review gate | <the verdict> — settled by the user at the settle prompt]
>>>>>>> NEW
<<<<<<< OLD 1
**A standalone run that cancelled at Phase 7 never reaches this phase either**
=======
**A standalone run that cancelled at Phase 7, or stopped at Phase 9's review gate, never reaches this phase either**
>>>>>>> NEW
<<<<<<< OLD 1
never reaches this phase either** — see Phase 7's cancel path, which jumps straight to Phase 11.
=======
never reaches this phase either** — see Phase 7's cancel path and Phase 9's review-gate stop, each of which goes straight to Phase 11.
>>>>>>> NEW
<<<<<<< OLD 1
Left uncommitted: <"none" | <path> —
=======
Left uncommitted: <"none" | "N/A — stopped at the review gate; Phase 10 never ran" | <path> —
>>>>>>> NEW
`````

#### `edits/aw-docs-init.txt`

`````text
<<<<<<< OLD 1
verify each finding's own claimed consequence at the location it names, keep or dismiss with a reason that disposes of that finding's own claim, carry **survivors only** forward, and carry every dismissal into the Phase 8.5 report
=======
verify each finding's own claimed consequence at the location it names; keep it, mark it unverified, or dismiss it — a dismissal with a reason that disposes of that finding's own claim, an unverified finding with what would settle it; raise a grade only by effect; carry **survivors only** forward, and carry every dismissal, every unverified finding and every raise into the Phase 8.5 report, per that reference's § Reporting
>>>>>>> NEW
<<<<<<< OLD 1
fix only a defect a finding actually demonstrated, never guard state it did not show.
=======
fix only a defect a finding actually demonstrated, never guard state it did not show, and never edit an instruction file the gate names that this run did not itself write.
>>>>>>> NEW
<<<<<<< OLD 1
Findings: <N reviewed, M survived triage, K applied, J deferred or overridden with reason | "N/A">
=======
Findings: <N reviewed — M survived triage, U unverified, X dismissed; K applied, J deferred or overridden with reason — every dismissal, unverified finding and raise, and any settle prompt's answer, listed per `workflows-core:finding-triage` § Reporting | "N/A">
>>>>>>> NEW
<<<<<<< OLD 1
Where triage empties the survivor set on a non-PASS verdict, follow that reference's own disposition: surface it and let the operator settle the verdict, never silently promote it to PASS.
=======
Where triage empties the survivor set on a non-PASS verdict, follow that reference's own disposition: surface it and let the operator settle the verdict with the prompt it gives a caller that runs no re-review, never silently promoting it to PASS. **Keep the verdict** and **Cancel** there both stop the run at this gate, by the route below.
>>>>>>> NEW
<<<<<<< OLD 1
the review verdict with every applied and every dismissed finding,
=======
the review verdict with every applied, every dismissed and every unverified finding,
>>>>>>> NEW
<<<<<<< OLD 1
A **BLOCKER** left deferred — neither fixed nor overridden — stops the run before Phase 8:
=======
**A stop at this gate — Cancel at the settle prompt or this one, or Keep the verdict at the settle prompt — ends the run here**: skip Phase 8 and go straight to Phase 8.5's report, which names the stop — the review cancelled, or its verdict kept for a human decision. The scaffold this run wrote stays on disk on its branch, uncommitted, and the emitter tail (Phases 9–11) still runs, so this run's cost and any feedback are still recorded.

A **BLOCKER** left deferred — neither fixed nor overridden — stops the run before Phase 8:
>>>>>>> NEW
<<<<<<< OLD 1
Verdict: <PASS | PASS WITH RECOMMENDATIONS | BLOCK, resolved | "N/A — cancelled at Phase 2.5, never reached">
=======
Verdict: <PASS | PASS WITH RECOMMENDATIONS | BLOCK, resolved | "N/A — cancelled at Phase 2.5, never reached" | "<the verdict> — stopped at the review gate: cancelled, or kept for a human decision" | "<the verdict> — settled by the user at the settle prompt">
>>>>>>> NEW
<<<<<<< OLD 1
<branch name — 1 commit, NOT pushed and NOT merged | "cancelled at Phase 2.5 — no branch created, nothing written or committed">
=======
<branch name — 1 commit, NOT pushed and NOT merged | "cancelled at Phase 2.5 — no branch created, nothing written or committed" | "<branch name> — stopped at the review gate: nothing committed, the written files left on it uncommitted">
>>>>>>> NEW
<<<<<<< OLD 1
(When Phase 2.5 was cancelled, this whole section reads instead: "none — no branch exists to open a pull request against.")
=======
(When Phase 2.5 was cancelled, this whole section reads instead: "none — no branch exists to open a pull request against." When the run stopped at the review gate, it reads: "none — nothing was committed to open a pull request from.")
>>>>>>> NEW
<<<<<<< OLD 1
guidance only, never auto-invoked. On a completed run:
=======
guidance only, never auto-invoked. After a stop at the review gate: name the findings left to settle and the branch holding the uncommitted scaffold; settle them there, check each written path with `git check-ignore <path>` — leave any path it prints unstaged, after removing every config reference to it (`scaffold-tree.md` §7 lists them) — and commit by hand — a re-run would refuse the tree, whose `mkdocs.yml`, `.vale.ini` and `docs-profile.yml` Phase 0 reads as an existing docs repository. On a completed run:
>>>>>>> NEW
<<<<<<< OLD 1
BLOCK, resolved | N/A — cancelled before Phase 7.5]
=======
BLOCK, resolved | N/A — cancelled before Phase 7.5 | <the verdict> — stopped at the review gate | <the verdict> — settled by the user at the settle prompt]
>>>>>>> NEW
<<<<<<< OLD 1
<no written path ignored | left uncommitted, ignored by a project line:
=======
<no written path ignored | ignore test not run — stopped at the review gate | left uncommitted, ignored by a project line:
>>>>>>> NEW
`````

#### `edits/aw-document.txt`

`````text
<<<<<<< OLD 1
**Triage sub-step** (before any fixer dispatch): invoke `Skill(skill: "workflows-core:reference", args: "finding-triage")` and follow it. For each finding, verify its claimed consequence at the location it names; keep or dismiss; record every dismissal with a reason that disposes of that finding's own claim. Hand the fixer **survivors only**, and carry the dismissal list into this run's report.
=======
**Triage sub-step** (before any fixer dispatch, and on every re-review): invoke `Skill(skill: "workflows-core:reference", args: "finding-triage")` and follow it. For each finding, verify its claimed consequence at the location it names; keep it, mark it unverified, or dismiss it; record every dismissal and every unverified finding with its reason; and raise a grade only by effect. Hand the fixer **survivors only**, and carry every disposition into this run's report. A re-review — the one the fix cycle allows, or one you chose at the first settle prompt — is triaged under that reference's § On re-review: it carries forward what this run already ruled — save, on a re-review you chose at the first settle prompt, the dismissed and unverified findings it re-verifies — and no survivor of it is handed to a fixer. At either of that reference's settle prompts, **Keep the verdict** means the review **stayed blocked** (below) — on a kept verdict that is not `BLOCK`, which raised no BLOCKER, the run ends as Cancel does — and **Cancel** aborts the run, as the escalation's own *Cancel the whole run* does.
>>>>>>> NEW
<<<<<<< OLD 1
If the second verdict is still BLOCK, escalate for each unresolved BLOCKER individually per the `Review verdict BLOCK (unresolved after one fix cycle) — /document` rule
=======
Triage the re-review under `workflows-core:finding-triage` § On re-review (the triage sub-step above); on that section's **Proceed**, continue to Phase 8 as after a verdict that is not BLOCK. If the review **stayed blocked** — a BLOCKER survives that triage, or you keep the verdict at either settle prompt — escalate for each unresolved BLOCKER individually per the `Review verdict BLOCK (unresolved after one fix cycle) — /document` rule
>>>>>>> NEW
<<<<<<< OLD 1
- **Review triage:** [N findings reviewed, M survived] — dismissals: [one line per dismissal, `finding — reason`; or "none"]
=======
- **Review triage:** [one line per review pass, per `workflows-core:finding-triage` § Reporting — N findings reviewed: M survived, U unverified, X dismissed (C carried, on a re-review)] — survivors: [on a re-review, `finding — severity` per survivor, or "none"; "N/A (first review)" otherwise] — dismissals: [`finding — reason`, or "none"] — unverified: [`finding — if-true severity — what would settle it`, or "none"] — raised: [`finding — from → to — effect`, or "none"] — settled: [the answer given at a settle prompt, or "not asked"]
>>>>>>> NEW
<<<<<<< OLD 1
which names this entry point alongside the second-BLOCK one.
=======
which names this entry point alongside a review that stayed blocked.
>>>>>>> NEW
<<<<<<< OLD 1
only, never the dismissed ones]
=======
only, never the dismissed or unverified ones]
>>>>>>> NEW
`````

#### `edits/aw-epics.txt`

`````text
<<<<<<< OLD 1
**Triage sub-step** (before any fixer dispatch): invoke `Skill(skill: "workflows-core:reference", args: "finding-triage")` and follow it. For each finding, verify its claimed consequence at the location it names; keep or dismiss; record every dismissal with a reason that disposes of that finding's own claim. Hand the fixer **survivors only**, and carry the dismissal list into this run's report.
=======
**Triage sub-step** (before any fixer dispatch, and on every re-review): invoke `Skill(skill: "workflows-core:reference", args: "finding-triage")` and follow it. For each finding, verify its claimed consequence at the location it names; keep it, mark it unverified, or dismiss it; record every dismissal and every unverified finding with its reason; and raise a grade only by effect. Hand the fixer **survivors only**, and carry every disposition into this run's report. A re-review — the one the fix cycle allows, or one you chose at the first settle prompt — is triaged under that reference's § On re-review: it carries forward what this run already ruled — save, on a re-review you chose at the first settle prompt, the dismissed and unverified findings it re-verifies — and no survivor of it is handed to a fixer. At either of that reference's settle prompts, **Keep the verdict** means the review **stayed blocked** (below) — on a kept verdict that is not `BLOCK`, which raised no BLOCKER, the run ends as Cancel does — and **Cancel** aborts the run, as the escalation's own *Cancel the whole run* does.
>>>>>>> NEW
<<<<<<< OLD 1
If still BLOCK, escalate per the `Review verdict BLOCK (unresolved after one fix cycle) — /epics` rule
=======
Triage the re-review under `workflows-core:finding-triage` § On re-review (the triage sub-step above); on that section's **Proceed**, continue to Phase 8 as after a verdict that is not BLOCK. If the review **stayed blocked** — a BLOCKER survives that triage, or you keep the verdict at either settle prompt — escalate per the `Review verdict BLOCK (unresolved after one fix cycle) — /epics` rule
>>>>>>> NEW
<<<<<<< OLD 1
- **Review triage:** [N findings reviewed, M survived] — dismissals: [one line per dismissal, `finding — reason`; or "none"]
=======
- **Review triage:** [one line per review pass, per `workflows-core:finding-triage` § Reporting — N findings reviewed: M survived, U unverified, X dismissed (C carried, on a re-review)] — survivors: [on a re-review, `finding — severity` per survivor, or "none"; "N/A (first review)" otherwise] — dismissals: [`finding — reason`, or "none"] — unverified: [`finding — if-true severity — what would settle it`, or "none"] — raised: [`finding — from → to — effect`, or "none"] — settled: [the answer given at a settle prompt, or "not asked"]
>>>>>>> NEW
<<<<<<< OLD 1
which names this entry point alongside the second-BLOCK one.
=======
which names this entry point alongside a review that stayed blocked.
>>>>>>> NEW
<<<<<<< OLD 1
only, never the dismissed ones]
=======
only, never the dismissed or unverified ones]
>>>>>>> NEW
`````

#### `edits/aw-escalation.txt`

`````text
<<<<<<< OLD 1
## Review verdict BLOCK (unresolved after one fix cycle) — /document
=======
## Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline

`choices: ["Provide manual fix notes (you'll be prompted)", "Defer to a follow-up issue (record in the final report)", "Override and accept the finding", "Cancel the whole run"]`

Used by the commands that fix their own reviewer's findings inline, with no delegated writer, and define no "Defer" of their own — `/create-prd`, `/update-prd`, `/create-ard`, `/design`, `/prd-proposal` and `/brd-proposal` — when the one re-review still returns `BLOCK`; for `/prd-proposal` and `/brd-proposal`, which triage their re-review, when the review stayed blocked (`finding-triage.md` § On re-review).
Escalate per unresolved BLOCKER individually. "Manual fix notes" → take free-text from the user and apply it inline in one bounded pass, with no further re-review. "Defer" → record the finding as deferred in the run's final report. "Override" → record it there with the user's rationale. "Cancel" aborts the run.

## Review verdict BLOCK (unresolved after one fix cycle) — /document
>>>>>>> NEW
<<<<<<< OLD 1
or when `doc-reviewer` returns BLOCK a second time.
=======
or when the review stayed blocked (`finding-triage.md` § On re-review).
>>>>>>> NEW
<<<<<<< OLD 1
or when `epic-reviewer` returns BLOCK a second time.
=======
or when the review stayed blocked (`finding-triage.md` § On re-review).
>>>>>>> NEW
<<<<<<< OLD 1
`## Refinement notes` section) in addition to the Phase 9 report.
=======
`## Refinement notes` section) in addition to the Phase 9 report.
`/specify` cites this entry on purpose and defines its own "Defer" to mirror it —
a `## Refinement notes` section in `specification.md`.
>>>>>>> NEW
`````

#### `edits/aw-implement.txt`

`````text
<<<<<<< OLD 1
8. **Out of scope** — explicitly list what is NOT being done
=======
8. **Out of scope** — explicitly list what is NOT being done
9. **Review focus** — up to five input classes or failure modes the task implies and no step's tests exercise, most likely to bite a user first, each with the behaviour a reasonable user would expect — or `none — checked`. `test-writer` writes a test for each line, or names in its `### Notes` why one cannot be written (Phase 3.5)
>>>>>>> NEW
<<<<<<< OLD 1
If the second verdict is still BLOCK, stop: surface the remaining blockers to the user, exactly as the `NEEDS HUMAN` stop above does.
=======
Triage the re-review under `workflows-core:finding-triage` § On re-review (the triage sub-step below). If the review **stayed blocked** — a `BLOCKER` survives that triage, or you keep the verdict at either settle prompt — stop: surface the remaining blockers to the user, exactly as the `NEEDS HUMAN` stop above does. On that prompt's **Proceed**, the verdict is settled as not BLOCK — continue to step 7.5.
>>>>>>> NEW
<<<<<<< OLD 1
Do not run tests until the verdict is not BLOCK.
   - **PASS WITH RECOMMENDATIONS**
=======
Do not run tests until the verdict is not BLOCK, or a settle prompt's **Proceed** has settled it so.
   - **PASS WITH RECOMMENDATIONS**
>>>>>>> NEW
<<<<<<< OLD 1
**Triage sub-step** (before any fixer dispatch): invoke `Skill(skill: "workflows-core:reference", args: "finding-triage")` and follow it. For each finding, verify its claimed consequence at the location it names; keep or dismiss; record every dismissal with a reason that disposes of that finding's own claim. Hand the fixer **survivors only**, and carry the dismissal list into this run's report.
=======
**Triage sub-step** (before any fixer dispatch, and on every re-review): invoke `Skill(skill: "workflows-core:reference", args: "finding-triage")` and follow it. For each finding, verify its claimed consequence at the location it names; keep it, mark it unverified, or dismiss it; record every dismissal and every unverified finding with its reason; raise a grade only by effect; and rule on each line of the review's `### Declined to judge`. Hand the fixer **survivors only**, and carry every disposition into this run's report. A re-review — the one the BLOCK branch allows, one you chose at the first settle prompt, and step 8's review of the Phase 3.5 delta — is triaged under that reference's § On re-review: it carries forward what this run already ruled — save, on a re-review you chose at the first settle prompt, the dismissed and unverified findings it re-verifies — and no survivor of it is handed to a fixer. At either of that reference's settle prompts, **Keep the verdict** means the review **stayed blocked** — the BLOCK branch's stop — **Cancel** stops the run through Phase 4.6, and **Proceed** continues to step 7.5 — or, after step 8's own delta review, to step 9.
>>>>>>> NEW
<<<<<<< OLD 1
so the re-review reads the post-Phase-3.5 diff). If the reviewer WAS down-classified, skip the re-review.
=======
so the re-review reads the post-Phase-3.5 diff). Triage it as a re-review (step 7's triage sub-step); if the review stayed blocked (`workflows-core:finding-triage` § On re-review), stop as step 7's BLOCK branch does after its re-review. If the reviewer WAS down-classified, skip the re-review.
>>>>>>> NEW
<<<<<<< OLD 1
`review-fixer` `NEEDS HUMAN` stop, a second verdict still `BLOCK`, or a Cancel — removes the files it
had made before it stops, in the same way, save a file the stop itself named as unreadable, which
stays for the operator to look at (that reference again).
=======
`review-fixer` `NEEDS HUMAN` stop, a review that stayed blocked, a settle prompt's **Keep the
verdict**, or a Cancel — removes the files it had made before it stops, in the same way, save a file
the stop itself named as unreadable, which stays for the operator to look at (that reference again).
>>>>>>> NEW
<<<<<<< OLD 1
the `review-fixer` `NEEDS HUMAN` stop, and a second verdict still `BLOCK`. **Each of those runs Phase 4.6
=======
the `review-fixer` `NEEDS HUMAN` stop, a review that stayed blocked (Phase 3B step 7, or step 8's review of the Phase 3.5 delta), and the **Keep the verdict** and **Cancel** arms of either of `workflows-core:finding-triage`'s settle prompts (Phase 3B steps 7 and 8). **Each of those runs Phase 4.6
>>>>>>> NEW
<<<<<<< OLD 1
when the Opus review is still `BLOCK` after its one fix cycle plus re-review
=======
when the review stayed blocked
>>>>>>> NEW
<<<<<<< OLD 1
**Six of the seven that paragraph enumerates, and the arithmetic is worth keeping because a reader who counts the list instead gets seven**: the seventh, *a second verdict still `BLOCK`*, is the next condition's own state word for word, so it was already being handed `false` and was never in the disagreement. `NEEDS HUMAN` is, because the run does **not** re-review there and that condition's *"plus re-review"* is then unmet.
=======
**Six of the seven that paragraph enumerated when this condition was added, and the arithmetic is worth keeping because a reader who counted the list then got seven**: the seventh — the stop after the one re-review, now *a review that stayed blocked* — was the next condition's own state, so it was already being handed `false` and was never in the disagreement. `NEEDS HUMAN` was, because the run does **not** re-review there, so its review never stays blocked. The settle prompts' **Keep the verdict** and **Cancel** arms joined that paragraph later, and reach `false` through this condition.
>>>>>>> NEW
<<<<<<< OLD 1
- **Review triage:** [N findings reviewed, M survived] — dismissals: [one line per dismissal, `finding — reason`; or "none"] — or "N/A (SIMPLE / MODERATE, no Opus review)"
=======
- **Review triage:** [one line per review pass, per `workflows-core:finding-triage` § Reporting — N findings reviewed: M survived, U unverified, X dismissed (C carried, on a re-review)] — survivors: [on a re-review, `finding — severity` per survivor, or "none"; "N/A (first review)" otherwise] — dismissals: [`finding — reason`, or "none"] — unverified: [`finding — if-true severity — what would settle it`, or "none"] — raised: [`finding — from → to — effect`, or "none"] — set aside by the reviewer: [`behaviour — ruling`, or "none"] — settled: [the answer given at a settle prompt, or "not asked"] — or "N/A (SIMPLE / MODERATE, no Opus review)"
>>>>>>> NEW
<<<<<<< OLD 1
If review is still BLOCK, resolve that first.]
=======
If the review stayed blocked, resolve that first.]
>>>>>>> NEW
<<<<<<< OLD 1
- AFTER one review-fixer pass + one re-review, if verdict is still BLOCK: stop and surface to user — do NOT loop
=======
- AFTER one review-fixer pass + one re-review, if the review stayed blocked (`workflows-core:finding-triage` § On re-review): stop and surface to user — do NOT loop
>>>>>>> NEW
<<<<<<< OLD 1
After the review gate clears (non-BLOCK verdict)
=======
After the review gate clears (a non-BLOCK verdict, or a settle prompt's **Proceed**)
>>>>>>> NEW
<<<<<<< OLD 1
before Opus review returns non-BLOCK"
=======
before Opus review returns non-BLOCK, or a settle prompt's Proceed settles it as one"
>>>>>>> NEW
<<<<<<< OLD 1
(do not wait for the BLOCK-still-BLOCK path)
=======
(do not wait for the review to stay blocked)
>>>>>>> NEW
<<<<<<< OLD 1
Dismissed findings NEVER enter that file;
=======
Dismissed and unverified findings NEVER enter that file;
>>>>>>> NEW
<<<<<<< OLD 1
returns a non-BLOCK verdict
=======
returns a non-BLOCK verdict, or a `workflows-core:finding-triage` settle prompt's **Proceed** settles it as one
>>>>>>> NEW
<<<<<<< OLD 1
**This stop offers no arms,
=======
**The stop for a review that stayed blocked offers no arms,
>>>>>>> NEW
<<<<<<< OLD 1
that question was put to the user before any file was edited. On `skip`,
=======
that question was put to the user before any file was edited. **Record in the Phase 5 `### Deferred items` section every behaviour — a Review focus line included — that the report's `### Notes` names as untested, with the reason it gives** (one it cannot test in isolation, or a `hinted` or `declared` command with no test of its own to follow): it is a test this run could not write. On `skip`,
>>>>>>> NEW
<<<<<<< OLD 1
asking for a baseline that can no longer be taken.
=======
asking for a baseline that can no longer be taken. As in Phase 3.5 step 2, record in the Phase 5 `### Deferred items` section every behaviour — a Review focus line included — that the report's `### Notes` names as untested, with the reason it gives.
>>>>>>> NEW
<<<<<<< OLD 1
Seven instructions in this file write test records here and the heading admits every one of them — they land in the six test bullets below, the two `CAVEAT: ` instructions (Pre-Phase 3.5's over its capture and Phase 3.5 step 5's over its verify) sharing one,
=======
Nine instructions in this file write test records here and the heading admits every one of them — they land in the seven test bullets below, the two `CAVEAT: ` instructions (Pre-Phase 3.5's over its capture and Phase 3.5 step 5's over its verify) sharing one and the two `test-writer` `### Notes` instructions (Phase 3.5 step 2's and Phase 3B step 4a's) sharing another,
>>>>>>> NEW
<<<<<<< OLD 1
- [each `CAVEAT: ` line the Pre-Phase 3.5 capture block
=======
- [each behaviour, a Review focus line included, that a `test-writer` report's `### Notes` named as untested — one it cannot test in isolation, or one a `hinted` or `declared` command gave it no test to follow for — with the reason it gave (Phase 3.5 step 2, Phase 3B step 4a); omit where none]
- [each `CAVEAT: ` line the Pre-Phase 3.5 capture block
>>>>>>> NEW
<<<<<<< OLD 1
- [MINOR / NIT review findings that were not applied; omit the line where there are none]
=======
- [review findings that were not applied — MINOR / NIT, and every survivor of a re-review, with its severity; omit the line where there are none]
>>>>>>> NEW
<<<<<<< OLD 1
and any deferred `MINOR`/`NIT` findings.
=======
and every review finding `### Deferred items` lists as not applied — deferred `MINOR`/`NIT` findings and every survivor of a re-review, each with its severity.
>>>>>>> NEW
`````

#### `edits/aw-prd-docs.txt`

`````text
<<<<<<< OLD 1
`workflows-core:escalation-rules`'s "Review verdict BLOCK" choices
=======
`workflows-core:escalation-rules`'s "Review verdict BLOCK … — commands that fix inline" choices
>>>>>>> NEW
`````

#### `edits/aw-prd-proposal.txt`

`````text
<<<<<<< OLD 1
Verify each finding's claimed consequence at the location it names, keep or dismiss it, and record every dismissal with a reason that disposes of that finding's own claim. There is no silent-drop disposition. Fix the surviving BLOCKERs inline (the orchestrator edits both artifacts — there is no delegated writer) and re-review **once**; if still `BLOCK`, escalate per the `Review verdict BLOCK` rule in `Skill(skill: "workflows-core:reference", args: "escalation-rules")`. `PASS` / `PASS WITH RECOMMENDATIONS` → proceed. Cap: one fix cycle plus one re-review. Where triage empties the survivor set, do not dispatch a fix cycle with nothing to apply and do not silently promote the verdict — the user settles a verdict its own findings no longer support.
=======
Verify each finding's claimed consequence at the location it names; keep it, mark it unverified, or
   dismiss it; record every dismissal with a reason that disposes of that finding's own claim and every
   unverified finding with what would settle it; and raise a grade only by effect. There is no
   silent-drop disposition. Fix the surviving BLOCKERs inline (the orchestrator edits both artifacts —
   there is no delegated writer) and re-review **once**, triaging that re-review — and one you chose
   at the first settle prompt — under that reference's § On re-review. If the review **stayed
   blocked** — a BLOCKER survives that triage, or you keep the verdict at either settle prompt —
   escalate per the `Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline`
   rule in `Skill(skill: "workflows-core:reference", args: "escalation-rules")`; on § On re-review's
   **Proceed**, proceed as after a verdict that is not `BLOCK`. `PASS` / `PASS WITH RECOMMENDATIONS`
   → proceed. Cap: one fix cycle plus one re-review. Where triage empties the survivor set, do not
   dispatch a fix cycle with nothing to apply and do not silently promote the verdict — the user
   settles a verdict its own findings no longer support. At either of that reference's settle
   prompts, **Keep the verdict** means the review stayed blocked — on a kept verdict that is not
   `BLOCK`, which raised no BLOCKER, the run ends as Cancel does — and **Cancel** aborts the run.
>>>>>>> NEW
<<<<<<< OLD 1
Report findings reviewed, survivors, and every dismissal with its reason: a triage that reports only
survivors is indistinguishable from a reviewer that found less.
=======
Report the triage per `workflows-core:finding-triage` § Reporting — one line per review pass, naming
the counts, the survivors, the unverified findings, every dismissal with its reason and any settle
prompt's answer: a triage that reports only survivors is indistinguishable from a reviewer that found
less.
>>>>>>> NEW
<<<<<<< OLD 1
the triage line — findings reviewed, survivors, and every dismissal with its reason; resolved model
routing (+ any Opus gate or degradation, or
=======
the triage line per `workflows-core:finding-triage` § Reporting — the counts, survivors, unverified
findings, every dismissal with its reason and any settle prompt's answer; resolved model routing (+ any Opus gate or degradation, or
>>>>>>> NEW
`````

#### `edits/aw-proposal-reviewer.txt`

`````text
<<<<<<< OLD 1
(keep or
  dismiss, each with a reason that disposes of that finding's own claim) before any survivor is
  fixed.
=======
(keep, mark
  unverified or dismiss, each with its reason) before any survivor is fixed.
>>>>>>> NEW
`````

#### `edits/aw-rules-dw.txt`

`````text
<<<<<<< OLD 1
each finding verified at the location it names, every dismissal recorded with a reason that disposes of that finding's own claim, and the fixer handed **survivors only**
=======
each finding verified at the location it names, every dismissal recorded with a reason that disposes of that finding's own claim, a finding triage cannot settle, and that would be MAJOR or BLOCKER if true, recorded as unverified with what would settle it, and the fixer handed **survivors only**
>>>>>>> NEW
`````

#### `edits/aw-rules-fixer.txt`

`````text
<<<<<<< OLD 1
- `review-fixer` handles BLOCKER findings; only one `review-fixer` cycle per review
=======
- `review-fixer` handles surviving BLOCKER and MAJOR findings; at most one `review-fixer` cycle per reviewed artifact, and none after its re-review (`workflows-core:finding-triage` § On re-review)
>>>>>>> NEW
`````

#### `edits/aw-rules-tests.txt`

`````text
<<<<<<< OLD 1
**Only the first clause is bounded, and by exactly one state** — Pre-Phase 3.5's skip on a `COMMAND_NOT_FOUND` capture, where `test-writer` returns its "not detected" report and writes nothing.
=======
**Only the first clause is bounded, and only by what `test-writer` could not write** — Pre-Phase 3.5's skip on a `COMMAND_NOT_FOUND` capture, where `test-writer` returns its "not detected" report and writes nothing, and every behaviour its `### Notes` names as untested: one it cannot test in isolation (its step 5), or each one, in a changed file no other suite's tests live alongside, where a `hinted` or `declared` command gives it no test to follow (its step 1). `/implement` names each of those in `### Deferred items`.
>>>>>>> NEW
<<<<<<< OLD 1
What the section is about is wider than that one exception, though:
=======
What the section is about is wider than those exceptions, though:
>>>>>>> NEW
<<<<<<< OLD 1
**no test written** (that same `COMMAND_NOT_FOUND` skip, the only member);
=======
**no test written** (that same `COMMAND_NOT_FOUND` skip, and every behaviour `test-writer`'s `### Notes` names as untested);
>>>>>>> NEW
<<<<<<< OLD 1
- **Pre-Phase 3.5's skip is where kind 1 and the first of kind 2's four members come from
=======
- **Pre-Phase 3.5's skip is where kind 1's first member and the first of kind 2's four members come from
>>>>>>> NEW
<<<<<<< OLD 1
**writes nothing** — the one kind with no test at all;
=======
**writes nothing**;
>>>>>>> NEW
<<<<<<< OLD 1
The first clause is not made unqualified: that would have to remove **both** escapes a user can choose — that option and Pre-Phase 3.5's *"Skip tests for this run"*;
=======
The first clause is not made unqualified: that would have to remove **both** escapes a user can choose — that option and Pre-Phase 3.5's *"Skip tests for this run"* — and would leave the clause unmeetable on whatever `test-writer` names as untested, which is the code's or the repository's answer rather than anybody's choice;
>>>>>>> NEW
`````

#### `edits/aw-rules-wc.txt`

`````text
<<<<<<< OLD 1
the three-step process (verify each finding's own claimed consequence at the location it names, keep or dismiss, record every dismissal with a reason that disposes of that finding's own claim — there is no silent-drop disposition), the patch gate (auto-fix only a defect that actually occurs, missing coverage for a specific case, or a broken gate/convention — never a state nothing reaches, and never a fix that guards state the finding did not demonstrate), the reporting contract (findings reviewed, survivors, and every dismissal with its reason — a triage that reports only survivors is indistinguishable from a reviewer that found less), and the disposition when triage empties the survivor set (never dispatch a fixer with nothing to apply, never run the unresolved-BLOCKER escalation on a refuted BLOCKER, and never silently promote a non-PASS verdict — the user settles a verdict its own findings no longer support).
=======
the step (verify each finding's own claimed consequence at the location it names; keep it, mark it unverified — verification could not settle it and it would be `MAJOR` or `BLOCKER` if true, so it is recorded at that grade with what would settle it and is never handed to a fixer — or dismiss it with a reason that disposes of that finding's own claim; raise a survivor's grade only by effect, to `MAJOR` at most; rule on each line of a `code-review` `### Declined to judge` list — there is no silent-drop disposition), the patch gate (auto-fix only a defect that actually occurs, missing coverage for a specific case, or a broken gate/convention — never a state nothing reaches, never a fix that guards state the finding did not demonstrate, and never one that edits a repository instruction or contributor file the change did not itself edit), the reporting contract (one line per review pass, where survived, unverified and dismissed sum to the findings reviewed and every dismissal and unverified finding is stated — a triage that reports only survivors is indistinguishable from a reviewer that found less), the disposition when triage empties the survivor set (never dispatch a fixer with nothing to apply, never run the unresolved-BLOCKER escalation on a BLOCKER that did not survive triage unless the user keeps the verdict, and never silently promote a non-PASS verdict — the user settles a verdict its own findings no longer support), and § On re-review (a re-review carries forward this run's earlier rulings over the same artifact — save that one the user chose at the first settle prompt re-verifies re-raised dismissed and unverified findings — no survivor of it is handed to a fixer, and the second-verdict stop acts on a review that **stayed blocked** — a BLOCKER surviving its triage, or a verdict the user keeps at a settle prompt — with the user settling a `BLOCK` no surviving BLOCKER supports).
>>>>>>> NEW
`````

#### `edits/aw-scaffold-tree.txt`

`````text
<<<<<<< OLD 1
Test each written path with `git -C <root> check-ignore -v <path>`. For each path that matches:
=======
Test each written path with `git -C <root> check-ignore -v <path>`; a line it prints whose pattern starts with `!` re-includes the path, and is no match. For each path that matches:
>>>>>>> NEW
`````

#### `edits/aw-triage.txt`

`````text
<<<<<<< OLD 1
`/prd-proposal` and `/brd-proposal` do re-review once after their inline fix, and that re-review can re-raise a finding triage dropped — but only a run that had a surviving BLOCKER to fix reaches it, so a dismissal there still has to carry its own reason.
=======
`/prd-proposal` and `/brd-proposal` do re-review once after their inline fix, and § On re-review carries a finding triage already dropped forward at its recorded outcome rather than deciding it again — so that re-review is no second chance for a dismissal, which still has to carry its own reason. `/docs-init`, a standalone `/docs-brand` and `/docs-audit`, which run no re-review, settle an emptied set with a prompt that has no re-review arm (§ When triage empties the survivor set).
>>>>>>> NEW
<<<<<<< OLD 1
**Keep the verdict** means the review stayed blocked: the caller takes its stop or escalation over the `BLOCKER`s the reviewer raised. Where the kept verdict is not `BLOCK`
=======
A caller that runs no re-review — `/docs-init`, a standalone `/docs-brand`, `/docs-audit` — asks
   without the re-review arm:
   ```
   choices: ["Proceed as if the verdict were PASS — every disposition is recorded (Recommended)", "Keep the verdict and stop for a human decision", "Cancel"]
   ```
   **Keep the verdict** means the review stayed blocked: the caller takes its stop or escalation over
   the `BLOCKER`s the reviewer raised. Where the kept verdict is not `BLOCK`
>>>>>>> NEW
`````

#### `edits/aw-upgrade.txt`

`````text
<<<<<<< OLD 1
**Triage sub-step** (before any fixer dispatch): invoke `Skill(skill: "workflows-core:reference", args: "finding-triage")` and follow it. For each finding, verify its claimed consequence at the location it names; keep or dismiss; record every dismissal with a reason that disposes of that finding's own claim. Hand the fixer **survivors only**, and carry the dismissal list into this run's report.
=======
**Triage sub-step** (before any fixer dispatch, and on every re-review): invoke `Skill(skill: "workflows-core:reference", args: "finding-triage")` and follow it. For each finding, verify its claimed consequence at the location it names; keep it, mark it unverified, or dismiss it; record every dismissal and every unverified finding with its reason; raise a grade only by effect; and rule on each line of the review's `### Declined to judge`. Hand the fixer **survivors only**, and carry every disposition into this run's report. A re-review — the one the fix cycle allows, or one you chose at the first settle prompt — is triaged under that reference's § On re-review: it carries forward what this run already ruled on this component — save, on a re-review you chose at the first settle prompt, the dismissed and unverified findings it re-verifies — and no survivor of it is handed to a fixer. At either of that reference's settle prompts, **Keep the verdict** means this component's review **stayed blocked** (below), and so does **Cancel**: this component stops, and the loop moves on to the next one.
>>>>>>> NEW
<<<<<<< OLD 1
- If the second verdict is still `BLOCK`, stop and escalate; do not continue to tests
=======
- Triage the re-review under `workflows-core:finding-triage` § On re-review (the triage sub-step above); on that section's **Proceed**, continue to step 5 as after a verdict that is not `BLOCK`. If a `BLOCKER` survives that triage, or you keep the verdict at either settle prompt, this component's review **stayed blocked**: stop and escalate; do not continue to tests
>>>>>>> NEW
<<<<<<< OLD 1
the `review-fixer` `NEEDS HUMAN` stop, a second verdict still `BLOCK`, and a `BLOCKED` return
=======
the `review-fixer` `NEEDS HUMAN` stop, a review that stayed blocked, and a `BLOCKED` return
>>>>>>> NEW
<<<<<<< OLD 1
or whose review stayed `BLOCK`, **is** committed
=======
or whose review stayed blocked, **is** committed
>>>>>>> NEW
<<<<<<< OLD 1
the `review-fixer` `NEEDS HUMAN` stop, a second
   verdict still `BLOCK`) keeps its files
=======
the `review-fixer` `NEEDS HUMAN` stop, a review
   that stayed blocked) keeps its files
>>>>>>> NEW
<<<<<<< OLD 1
Append a `### Review triage` section with one line per SIGNIFICANT/HIGH-RISK component that went through Opus review: - **Review triage:** [N findings reviewed, M survived] — dismissals: [one line per dismissal, `finding — reason`; or "none"]
=======
Append a `### Review triage` section with one line per review pass of each SIGNIFICANT/HIGH-RISK component that went through Opus review (`workflows-core:finding-triage` § Reporting): - **Review triage:** [N findings reviewed: M survived, U unverified, X dismissed (C carried, on a re-review)] — survivors: [on a re-review, `finding — severity` per survivor, or "none"; "N/A (first review)" otherwise] — dismissals: [`finding — reason`, or "none"] — unverified: [`finding — if-true severity — what would settle it`, or "none"] — raised: [`finding — from → to — effect`, or "none"] — set aside by the reviewer: [`behaviour — ruling`, or "none"] — settled: [the answer given at a settle prompt, or "not asked"]
>>>>>>> NEW
<<<<<<< OLD 1
or with a review still `BLOCK` — it is committed
=======
or with a review that stayed blocked — it is committed
>>>>>>> NEW
<<<<<<< OLD 1
or with a review still `BLOCK`, or with kept regressions
=======
or with a review that stayed blocked, or with kept regressions
>>>>>>> NEW
<<<<<<< OLD 1
returns a non-BLOCK verdict
=======
returns a non-BLOCK verdict, or a `workflows-core:finding-triage` settle prompt's **Proceed** settles it as one
>>>>>>> NEW
<<<<<<< OLD 1
its review verdict is non-`BLOCK` or the user chose to keep it,
=======
its review verdict is non-`BLOCK` or a settle prompt's **Proceed** settled it,
>>>>>>> NEW
<<<<<<< OLD 1
**"Stop and escalate" on a persisting `BLOCK` stops the component, not the run.**
=======
**"Stop and escalate" on a review that stayed blocked stops the component, not the run.**
>>>>>>> NEW
`````

#### `edits/aw-vuln.txt`

`````text
<<<<<<< OLD 1
**Triage sub-step** (before any fixer dispatch): invoke `Skill(skill: "workflows-core:reference", args: "finding-triage")` and follow it. For each finding, verify its claimed consequence at the location it names; keep or dismiss; record every dismissal with a reason that disposes of that finding's own claim. Hand the fixer **survivors only**, and carry the dismissal list into this run's report.
=======
**Triage sub-step** (before any fixer dispatch, and on every re-review): invoke `Skill(skill: "workflows-core:reference", args: "finding-triage")` and follow it. For each finding, verify its claimed consequence at the location it names; keep it, mark it unverified, or dismiss it; record every dismissal and every unverified finding with its reason; raise a grade only by effect; and rule on each line of the review's `### Declined to judge`. Hand the fixer **survivors only**, and carry every disposition into this run's report. A re-review — the one the fix cycle allows, or one you chose at the first settle prompt — is triaged under that reference's § On re-review: it carries forward what this run already ruled on this CVE — save, on a re-review you chose at the first settle prompt, the dismissed and unverified findings it re-verifies — and no survivor of it is handed to a fixer. At either of that reference's settle prompts, **Keep the verdict** means this CVE's review **stayed blocked** (below), and so does **Cancel**: this CVE stops, and the run moves on to the next one.
>>>>>>> NEW
<<<<<<< OLD 1
If the second verdict is still `BLOCK`, stop and escalate; do not continue to tests.
=======
Triage the re-review under `workflows-core:finding-triage` § On re-review (the triage sub-step above); on that section's **Proceed**, continue to step 4 as after a verdict that is not `BLOCK`. If a `BLOCKER` survives that triage, or you keep the verdict at either settle prompt, this CVE's review **stayed blocked**: stop and escalate; do not continue to tests.
>>>>>>> NEW
<<<<<<< OLD 1
when its review is still `BLOCK`,
=======
when its review stayed blocked,
>>>>>>> NEW
<<<<<<< OLD 1
the `review-fixer` `NEEDS HUMAN` stop, a
second verdict still `BLOCK`, each of which
=======
the `review-fixer` `NEEDS HUMAN` stop, a
review that stayed blocked, each of which
>>>>>>> NEW
<<<<<<< OLD 1
Append a `### Review triage` section with one line per CVE that went through Opus review: - **Review triage:** [N findings reviewed, M survived] — dismissals: [one line per dismissal, `finding — reason`; or "none"]
=======
Append a `### Review triage` section with one line per review pass of each CVE that went through Opus review (`workflows-core:finding-triage` § Reporting): - **Review triage:** [N findings reviewed: M survived, U unverified, X dismissed (C carried, on a re-review)] — survivors: [on a re-review, `finding — severity` per survivor, or "none"; "N/A (first review)" otherwise] — dismissals: [`finding — reason`, or "none"] — unverified: [`finding — if-true severity — what would settle it`, or "none"] — raised: [`finding — from → to — effect`, or "none"] — set aside by the reviewer: [`behaviour — ruling`, or "none"] — settled: [the answer given at a settle prompt, or "not asked"]
>>>>>>> NEW
<<<<<<< OLD 1
returns a non-BLOCK verdict
=======
returns a non-BLOCK verdict, or a `workflows-core:finding-triage` settle prompt's **Proceed** settles it as one
>>>>>>> NEW
<<<<<<< OLD 1
(`NEEDS HUMAN`, a persisting review `BLOCK`)
=======
(`NEEDS HUMAN`, a review that stayed blocked)
>>>>>>> NEW
<<<<<<< OLD 1
A CVE stopped at an unresolved review `BLOCK` or at `NEEDS HUMAN`
=======
A CVE stopped at a review that stayed blocked or at `NEEDS HUMAN`
>>>>>>> NEW
`````

#### `edits/ce-code-handoff.txt`

`````text
<<<<<<< OLD 1
- a review-tier review verdict still `BLOCK` after its single allowed fix cycle plus re-review;
=======
- a review-tier review that stayed blocked — a `BLOCKER` survived its re-review's triage, or the user kept its verdict at a settle prompt (or, in `vuln:` and `upgrade:`, cancelled there);
>>>>>>> NEW
`````

#### `edits/ce-code-review.txt`

`````text
<<<<<<< OLD 1
   `CODING_STANDARDS.md` at the root; and every file under `.claude/rules/`
   whose `paths:` frontmatter matches a changed file, or which has no
   `paths:`. Read each one that exists. A rule the repository's own lint,
   format or type-check configuration already enforces is that tool's to
   report, not this review's. As a **floor** where those files document no
   standard on a point (a standard documented in one of them **overrides**
=======
   `CODING_STANDARDS.md` at the root; `.github/copilot-instructions.md`;
   and every `.github/instructions/*.instructions.md` whose `applyTo:`
   frontmatter matches a changed file. Read each one that exists. A rule
   the repository's own lint, format or type-check configuration already
   enforces is that tool's to report, not this review's. As a **floor**
   where those files document no standard on a point (a standard
   documented in one of them **overrides**
>>>>>>> NEW
`````

#### `edits/ce-doc-document.txt`

`````text
<<<<<<< OLD 1
an unresolved BLOCKER after that cycle is escalated individually.
=======
the re-review is triaged too, and a `BLOCKER` surviving that triage is escalated individually.
>>>>>>> NEW
<<<<<<< OLD 1
before any `doc-fixer` dispatch.
=======
before any `doc-fixer` dispatch — each finding kept, marked unverified with what would settle it, or dismissed with a reason.
>>>>>>> NEW
`````

#### `edits/ce-doc-epics.txt`

`````text
<<<<<<< OLD 1
every dismissal recorded with a reason, survivors only handed to `doc-fixer`.
=======
every dismissal and every unverified finding recorded with a reason, survivors only handed to `doc-fixer`.
>>>>>>> NEW
<<<<<<< OLD 1
an unresolved BLOCKER after that cycle is escalated individually.
=======
the re-review is triaged too: a `BLOCKER` surviving that triage, or a verdict you keep, is escalated individually, and a second `BLOCK` that no surviving `BLOCKER` supports is yours to settle.
>>>>>>> NEW
`````

#### `edits/ce-doc-implement.txt`

`````text
<<<<<<< OLD 1
before any `review-fixer` dispatch — the fixer sees survivors only.
=======
before any `review-fixer` dispatch — each finding kept, marked unverified with what would settle it, or dismissed with a reason, and the fixer sees survivors only.
>>>>>>> NEW
<<<<<<< OLD 1
an unresolved BLOCKER after that cycle is escalated individually.
=======
the re-review is triaged too, carrying forward what triage already ruled, and a review that stayed blocked — a `BLOCKER` surviving that triage, or a verdict you chose to keep — stops the run rather than looping; a second `BLOCK` that no surviving `BLOCKER` supports is yours to settle.
>>>>>>> NEW
<<<<<<< OLD 1
a review still `BLOCK` after its one fix cycle,
=======
a review that stayed blocked after its one fix cycle,
>>>>>>> NEW
`````

#### `edits/ce-doc-upgrade.txt`

`````text
<<<<<<< OLD 1
kept or dismissed with a reason, and the fixer sees survivors only.
=======
kept, marked unverified or dismissed with a reason, and the fixer sees survivors only.
>>>>>>> NEW
<<<<<<< OLD 1
a still-`BLOCK` second verdict stops and escalates
=======
the re-review is triaged too, carrying forward what triage already ruled on that component, and a review that stayed blocked — a `BLOCKER` surviving that triage, or a verdict you chose to keep — stops and escalates (a second `BLOCK` that no surviving `BLOCKER` supports is yours to settle, and a Cancel at that prompt also stops only that component while the run goes on)
>>>>>>> NEW
<<<<<<< OLD 1
naming every finding reviewed and every dismissal's reason
=======
counting every finding reviewed and naming every dismissal's reason and every unverified finding's
>>>>>>> NEW
`````

#### `edits/ce-doc-vuln.txt`

`````text
<<<<<<< OLD 1
kept or dismissed with a reason, and the fixer sees survivors only.
=======
kept, marked unverified or dismissed with a reason, and the fixer sees survivors only.
>>>>>>> NEW
<<<<<<< OLD 1
a still-`BLOCK` second verdict stops and escalates
=======
the re-review is triaged too, carrying forward what triage already ruled on that CVE, and a review that stayed blocked — a `BLOCKER` surviving that triage, or a verdict you chose to keep — stops and escalates (a second `BLOCK` that no surviving `BLOCKER` supports is yours to settle, and a Cancel at that prompt also stops only that CVE while the run goes on)
>>>>>>> NEW
<<<<<<< OLD 1
naming every finding reviewed and every dismissal's reason
=======
counting every finding reviewed and naming every dismissal's reason and every unverified finding's
>>>>>>> NEW
`````

#### `edits/ce-shared-instr.txt`

`````text
<<<<<<< OLD 1
the three-step process (verify each finding's own claimed consequence at the location it names, keep or dismiss, record every dismissal with a reason that disposes of that finding's own claim — there is no silent-drop disposition), the patch gate (auto-fix only a defect that actually occurs, missing coverage for a specific case, or a broken gate/convention — never a state nothing reaches, and never a fix that guards state the finding did not demonstrate), the reporting contract (findings reviewed, survivors, and every dismissal with its reason — a triage that reports only survivors is indistinguishable from a reviewer that found less), and the disposition when triage empties the survivor set (never dispatch a fixer with nothing to apply, never run the unresolved-BLOCKER escalation on a refuted BLOCKER, and never silently promote a non-PASS verdict — the user settles a verdict its own findings no longer support).
=======
the step (verify each finding where it points; keep it, mark it unverified with what would settle it, or dismiss it with a reason that disposes of its own claim; raise a grade only by effect — no silent drop), the patch gate (auto-fix only a defect that actually occurs, missing coverage for a case, or a broken gate/convention — never a state nothing reaches, a guard the finding did not demonstrate, or an instruction file the change did not edit), the reporting contract (survived + unverified + dismissed = reviewed, every dismissal stated), the emptied-survivor-set disposition (no fixer with nothing to apply, no unresolved-BLOCKER escalation on a BLOCKER triage dropped, no silent promotion of a non-PASS verdict — the user settles it), and § On re-review (earlier rulings over the same artifact carry forward, bar a user-chosen re-review; the stop acts on a surviving BLOCKER or a kept verdict — the review **stayed blocked**).
>>>>>>> NEW
`````

#### `edits/ce-skillmap.txt`

`````text
<<<<<<< OLD 1
each finding verified at the location it names, every dismissal recorded with a reason that disposes of that finding's own claim, and the fixer handed **survivors only**
=======
each finding verified where it points, every dismissal and unverified finding recorded with its reason, and the fixer handed **survivors only**
>>>>>>> NEW
<<<<<<< OLD 1
— each finding verified at the location it names, every dismissal recorded with a reason that disposes of that finding's own claim, survivors only,
=======
— each finding verified where it points and kept, left unverified, or dismissed with a reason disposing of its own claim; survivors only,
>>>>>>> NEW
<<<<<<< OLD 1
- `review-fixer` handles BLOCKER findings; only one review-fixer cycle per review
=======
- `review-fixer` handles surviving BLOCKER and MAJOR findings; one review-fixer cycle per reviewed artifact, none after its re-review
>>>>>>> NEW
`````

#### `edits/ed-bare-pointer.tpl`

`````text
<<<<<<< OLD 1
the `Review verdict BLOCK` rule in
=======
the `Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline` rule in
>>>>>>> NEW
`````

#### `edits/ed-create-vi.tpl`

`````text
<<<<<<< OLD 1
If still `BLOCK`, escalate per the `Review verdict BLOCK` rule in
=======
If still `BLOCK`, escalate per the `Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline` rule in
>>>>>>> NEW
<<<<<<< OLD 1
for each unresolved BLOCKER (`choices: ["Provide manual fix notes", "Defer to a follow-up issue", "Override and accept", "Cancel"
=======
for each unresolved BLOCKER individually (`choices: ["Provide manual fix notes (you'll be prompted)", "Defer to a follow-up issue (record in the final report)", "Override and accept the finding", "Cancel the whole run"
>>>>>>> NEW
<<<<<<< OLD 1
Act on the verdict (mirrors `{{SPECCMD}}`):
=======
Act on the verdict (mirrors `{{SPECCMD}}`, save the escalation rule it cites):
>>>>>>> NEW
`````

#### `edits/ed-design-pointer.tpl`

`````text
<<<<<<< OLD 1
`Review verdict BLOCK (unresolved after one fix cycle) — {{EPICSCMD}}` rule in
=======
`Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline` rule in
>>>>>>> NEW
<<<<<<< OLD 1
**Act on the verdict** (mirrors `{{SPECCMD}}`):
=======
**Act on the verdict** (mirrors `{{SPECCMD}}`, save the escalation rule it cites):
>>>>>>> NEW
`````

#### `edits/ed-doc-failed-gate.txt`

`````text
<<<<<<< OLD 1
a review still `BLOCK` after its one fix cycle,
=======
a review that stayed blocked after its one fix cycle,
>>>>>>> NEW
`````

#### `edits/ed-doc-vi-choices.txt`

`````text
<<<<<<< OLD 1
's "Review verdict BLOCK" choices
=======
's "Review verdict BLOCK … — commands that fix inline" choices
>>>>>>> NEW
`````

#### `edits/ed-document.tpl`

`````text
<<<<<<< OLD 1
**Triage sub-step** (before any fixer dispatch):
=======
**Triage sub-step** (before any fixer dispatch, and on every re-review):
>>>>>>> NEW
<<<<<<< OLD 1
For each finding, verify its claimed consequence at the location it names; keep or dismiss; record every dismissal with a reason that disposes of that finding's own claim. Hand the fixer **survivors only**, and carry the dismissal list into this run's report.
=======
For each finding, verify its claimed consequence at the location it names; keep it, mark it unverified, or dismiss it; record every dismissal and every unverified finding with its reason; and raise a grade only by effect. Hand the fixer **survivors only**, and carry every disposition into this run's report. A re-review — the one the fix cycle allows, or one you chose at the first settle prompt — is triaged under that reference's § On re-review: it carries forward what this run already ruled — save, on a re-review you chose at the first settle prompt, the dismissed and unverified findings it re-verifies — and no survivor of it is handed to a fixer. At either of that reference's settle prompts, **Keep the verdict** means the review **stayed blocked** (below) — on a kept verdict that is not `BLOCK`, which raised no BLOCKER, the run ends as Cancel does — and **Cancel** aborts the run, as the escalation's own *Cancel the whole run* does.
>>>>>>> NEW
<<<<<<< OLD 1
If the second verdict is still BLOCK, escalate for each unresolved BLOCKER individually per the
=======
Triage the re-review under `{{FT}}` § On re-review (the triage sub-step above); on that section's **Proceed**, continue to Phase 8 as after a verdict that is not BLOCK. If the review **stayed blocked** — a BLOCKER survives that triage, or you keep the verdict at either settle prompt — escalate for each unresolved BLOCKER individually per the
>>>>>>> NEW
<<<<<<< OLD 1
- **Review triage:** [N findings reviewed, M survived] — dismissals: [one line per dismissal, `finding — reason`; or "none"]
=======
- **Review triage:** [one line per review pass, per `{{FT}}` § Reporting — N findings reviewed: M survived, U unverified, X dismissed (C carried, on a re-review)] — survivors: [on a re-review, `finding — severity` per survivor, or "none"; "N/A (first review)" otherwise] — dismissals: [`finding — reason`, or "none"] — unverified: [`finding — if-true severity — what would settle it`, or "none"] — raised: [`finding — from → to — effect`, or "none"] — settled: [the answer given at a settle prompt, or "not asked"]
>>>>>>> NEW
<<<<<<< OLD 1
which names this entry point alongside the second-BLOCK one.
=======
which names this entry point alongside a review that stayed blocked.
>>>>>>> NEW
<<<<<<< OLD 1
only, never the dismissed ones]
=======
only, never the dismissed or unverified ones]
>>>>>>> NEW
`````

#### `edits/ed-epics.tpl`

`````text
<<<<<<< OLD 1
**Triage sub-step** (before any fixer dispatch):
=======
**Triage sub-step** (before any fixer dispatch, and on every re-review):
>>>>>>> NEW
<<<<<<< OLD 1
For each finding, verify its claimed consequence at the location it names; keep or dismiss; record every dismissal with a reason that disposes of that finding's own claim. Hand the fixer **survivors only**, and carry the dismissal list into this run's report.
=======
For each finding, verify its claimed consequence at the location it names; keep it, mark it unverified, or dismiss it; record every dismissal and every unverified finding with its reason; and raise a grade only by effect. Hand the fixer **survivors only**, and carry every disposition into this run's report. A re-review — the one the fix cycle allows, or one you chose at the first settle prompt — is triaged under that reference's § On re-review: it carries forward what this run already ruled — save, on a re-review you chose at the first settle prompt, the dismissed and unverified findings it re-verifies — and no survivor of it is handed to a fixer. At either of that reference's settle prompts, **Keep the verdict** means the review **stayed blocked** (below) — on a kept verdict that is not `BLOCK`, which raised no BLOCKER, the run ends as Cancel does — and **Cancel** aborts the run, as the escalation's own *Cancel the whole run* does.
>>>>>>> NEW
<<<<<<< OLD 1
If still BLOCK, escalate per the
=======
Triage the re-review under `{{FT}}` § On re-review (the triage sub-step above); on that section's **Proceed**, continue to Phase 8 as after a verdict that is not BLOCK. If the review **stayed blocked** — a BLOCKER survives that triage, or you keep the verdict at either settle prompt — escalate per the
>>>>>>> NEW
<<<<<<< OLD 1
- **Review triage:** [N findings reviewed, M survived] — dismissals: [one line per dismissal, `finding — reason`; or "none"]
=======
- **Review triage:** [one line per review pass, per `{{FT}}` § Reporting — N findings reviewed: M survived, U unverified, X dismissed (C carried, on a re-review)] — survivors: [on a re-review, `finding — severity` per survivor, or "none"; "N/A (first review)" otherwise] — dismissals: [`finding — reason`, or "none"] — unverified: [`finding — if-true severity — what would settle it`, or "none"] — raised: [`finding — from → to — effect`, or "none"] — settled: [the answer given at a settle prompt, or "not asked"]
>>>>>>> NEW
<<<<<<< OLD 1
which names this entry point alongside the second-BLOCK one.
=======
which names this entry point alongside a review that stayed blocked.
>>>>>>> NEW
<<<<<<< OLD 1
only, never the dismissed ones]
=======
only, never the dismissed or unverified ones]
>>>>>>> NEW
`````

#### `edits/ed-escalation.tpl`

`````text
<<<<<<< OLD 1
## Review verdict BLOCK (unresolved after one fix cycle) — {{DOCCMD}}
=======
## Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline

`choices: [{{ARR13}}]`

Used by the commands that fix their own reviewer's findings inline, with no delegated writer, and define no "Defer" of their own — {{CALLERS13}} — when the one re-review still returns `BLOCK`.
Escalate per unresolved BLOCKER individually. "Manual fix notes" → take free-text from the user and apply it inline in one bounded pass, with no further re-review. "Defer" → record the finding as deferred in the run's final report. "Override" → record it there with the user's rationale. "Cancel" aborts the run.

## Review verdict BLOCK (unresolved after one fix cycle) — {{DOCCMD}}
>>>>>>> NEW
<<<<<<< OLD 1
or when `doc-reviewer` returns BLOCK a second time.
=======
or when the review stayed blocked (`finding-triage.md` § On re-review).
>>>>>>> NEW
<<<<<<< OLD 1
or when `epic-reviewer` returns BLOCK a second time.
=======
or when the review stayed blocked (`finding-triage.md` § On re-review).
>>>>>>> NEW
<<<<<<< OLD 1
`## Refinement notes` section) in addition to the Phase 9 report.
=======
`## Refinement notes` section) in addition to the Phase 9 report.
`{{SPECCMD}}` cites this entry on purpose and defines its own "Defer" to mirror it —
a `## Refinement notes` section in `specification.md`.
>>>>>>> NEW
`````

#### `edits/ed-implement.tpl`

`````text
<<<<<<< OLD 1
8. **Out of scope** — explicitly list what is NOT being done
=======
8. **Out of scope** — explicitly list what is NOT being done
9. **Review focus** — up to five input classes or failure modes the task implies and no step's tests exercise, most likely to bite a user first, each with the behaviour a reasonable user would expect — or `none — checked`. `test-writer` writes a test for each line, or names in its `### Notes` why one cannot be written (Phase 3.5)
>>>>>>> NEW
<<<<<<< OLD 1
If the second verdict is still BLOCK, stop: surface the remaining blockers to the user, exactly as the `NEEDS HUMAN` stop above does.
=======
Triage the re-review under `{{FT}}` § On re-review (the triage sub-step below). If the review **stayed blocked** — a `BLOCKER` survives that triage, or you keep the verdict at either settle prompt — stop: surface the remaining blockers to the user, exactly as the `NEEDS HUMAN` stop above does. On that prompt's **Proceed**, the verdict is settled as not BLOCK — continue to step 7.5.
>>>>>>> NEW
<<<<<<< OLD 1
Do not run tests until the verdict is not BLOCK.
   - **PASS WITH RECOMMENDATIONS**
=======
Do not run tests until the verdict is not BLOCK, or a settle prompt's **Proceed** has settled it so.
   - **PASS WITH RECOMMENDATIONS**
>>>>>>> NEW
<<<<<<< OLD 1
**Triage sub-step** (before any fixer dispatch):
=======
**Triage sub-step** (before any fixer dispatch, and on every re-review):
>>>>>>> NEW
<<<<<<< OLD 1
For each finding, verify its claimed consequence at the location it names; keep or dismiss; record every dismissal with a reason that disposes of that finding's own claim. Hand the fixer **survivors only**, and carry the dismissal list into this run's report.
=======
For each finding, verify its claimed consequence at the location it names; keep it, mark it unverified, or dismiss it; record every dismissal and every unverified finding with its reason; raise a grade only by effect; and rule on each line of the review's `### Declined to judge`. Hand the fixer **survivors only**, and carry every disposition into this run's report. A re-review — the one the BLOCK branch allows, one you chose at the first settle prompt, and step 8's review of the Phase 3.5 delta — is triaged under that reference's § On re-review: it carries forward what this run already ruled — save, on a re-review you chose at the first settle prompt, the dismissed and unverified findings it re-verifies — and no survivor of it is handed to a fixer. At either of that reference's settle prompts, **Keep the verdict** means the review **stayed blocked** — the BLOCK branch's stop — **Cancel** stops the run through Phase 4.6, and **Proceed** continues to step 7.5 — or, after step 8's own delta review, to step 9.
>>>>>>> NEW
<<<<<<< OLD 1
so the re-review reads the post-Phase-3.5 diff). If the reviewer WAS down-classified, skip the re-review.
=======
so the re-review reads the post-Phase-3.5 diff). Triage it as a re-review (step 7's triage sub-step); if the review stayed blocked (`{{FT}}` § On re-review), stop as step 7's BLOCK branch does after its re-review. If the reviewer WAS down-classified, skip the re-review.
>>>>>>> NEW
<<<<<<< OLD 1
the `review-fixer` `NEEDS HUMAN` stop, and a second verdict still `BLOCK`. **Each of those runs Phase 4.6
=======
the `review-fixer` `NEEDS HUMAN` stop, a review that stayed blocked (Phase 3B step 7, or step 8's review of the Phase 3.5 delta), and the **Keep the verdict** and **Cancel** arms of either of `{{FT}}`'s settle prompts (Phase 3B steps 7 and 8). **Each of those runs Phase 4.6
>>>>>>> NEW
<<<<<<< OLD 1
review is still `BLOCK` after its one fix cycle plus re-review,
=======
review stayed blocked after its one fix cycle plus re-review,
>>>>>>> NEW
<<<<<<< OLD 1
- **Review triage:** [N findings reviewed, M survived] — dismissals: [one line per dismissal, `finding — reason`; or "none"]
=======
- **Review triage:** [one line per review pass, per `{{FT}}` § Reporting — N findings reviewed: M survived, U unverified, X dismissed (C carried, on a re-review)] — survivors: [on a re-review, `finding — severity` per survivor, or "none"; "N/A (first review)" otherwise] — dismissals: [`finding — reason`, or "none"] — unverified: [`finding — if-true severity — what would settle it`, or "none"] — raised: [`finding — from → to — effect`, or "none"] — set aside by the reviewer: [`behaviour — ruling`, or "none"] — settled: [the answer given at a settle prompt, or "not asked"]
>>>>>>> NEW
<<<<<<< OLD 1
If review is still BLOCK, resolve that first.]
=======
If the review stayed blocked, resolve that first.]
>>>>>>> NEW
<<<<<<< OLD 1
- AFTER one review-fixer pass + one re-review, if verdict is still BLOCK: stop and surface to user — do NOT loop
=======
- AFTER one review-fixer pass + one re-review, if the review stayed blocked (`{{FT}}` § On re-review): stop and surface to user — do NOT loop
>>>>>>> NEW
<<<<<<< OLD 1
After the review gate clears (non-BLOCK verdict)
=======
After the review gate clears (a non-BLOCK verdict, or a settle prompt's **Proceed**)
>>>>>>> NEW
<<<<<<< OLD 1
before {{REVIEW}} returns non-BLOCK"
=======
before {{REVIEW}} returns non-BLOCK, or a settle prompt's Proceed settles it as one"
>>>>>>> NEW
<<<<<<< OLD 1
(do not wait for the BLOCK-still-BLOCK path)
=======
(do not wait for the review to stay blocked)
>>>>>>> NEW
<<<<<<< OLD 1
Dismissed findings NEVER enter that file;
=======
Dismissed and unverified findings NEVER enter that file;
>>>>>>> NEW
<<<<<<< OLD 1
returns a non-BLOCK verdict
=======
returns a non-BLOCK verdict, or a `{{FT}}` settle prompt's **Proceed** settles it as one
>>>>>>> NEW
<<<<<<< OLD 1
**This stop offers no arms,
=======
**The stop for a review that stayed blocked offers no arms,
>>>>>>> NEW
<<<<<<< OLD 1
that question was put to the user before any file was edited. On `skip`,
=======
that question was put to the user before any file was edited. **Record in the Phase 5 `### Deferred items` section every behaviour — a Review focus line included — that the report's `### Notes` names as untested, with the reason it gives** (one it cannot test in isolation, or a `hinted` or `declared` command with no test of its own to follow): it is a test this run could not write. On `skip`,
>>>>>>> NEW
<<<<<<< OLD 1
asking for a baseline that can no longer be taken.
=======
asking for a baseline that can no longer be taken. As in Phase 3.5 step 2, record in the Phase 5 `### Deferred items` section every behaviour — a Review focus line included — that the report's `### Notes` names as untested, with the reason it gives.
>>>>>>> NEW
<<<<<<< OLD 1
Seven instructions in this file write test records here and the heading admits every one of them — they land in the six test bullets below, the two `CAVEAT: ` instructions (Pre-Phase 3.5's over its capture and Phase 3.5 step 5's over its verify) sharing one,
=======
Nine instructions in this file write test records here and the heading admits every one of them — they land in the seven test bullets below, the two `CAVEAT: ` instructions (Pre-Phase 3.5's over its capture and Phase 3.5 step 5's over its verify) sharing one and the two `test-writer` `### Notes` instructions (Phase 3.5 step 2's and Phase 3B step 4a's) sharing another,
>>>>>>> NEW
<<<<<<< OLD 1
- [each `CAVEAT: ` line the Pre-Phase 3.5 capture block
=======
- [each behaviour, a Review focus line included, that a `test-writer` report's `### Notes` named as untested — one it cannot test in isolation, or one a `hinted` or `declared` command gave it no test to follow for — with the reason it gave (Phase 3.5 step 2, Phase 3B step 4a); omit where none]
- [each `CAVEAT: ` line the Pre-Phase 3.5 capture block
>>>>>>> NEW
<<<<<<< OLD 1
- [MINOR / NIT review findings that were not applied; omit the line where there are none]
=======
- [review findings that were not applied — MINOR / NIT, and every survivor of a re-review, with its severity; omit the line where there are none]
>>>>>>> NEW
<<<<<<< OLD 1
and any deferred `MINOR`/`NIT` findings.
=======
and every review finding `### Deferred items` lists as not applied — deferred `MINOR`/`NIT` findings and every survivor of a re-review, each with its severity.
>>>>>>> NEW
`````

#### `edits/ed-upgrade.tpl`

`````text
<<<<<<< OLD 1
**Triage sub-step** (before any fixer dispatch):
=======
**Triage sub-step** (before any fixer dispatch, and on every re-review):
>>>>>>> NEW
<<<<<<< OLD 1
For each finding, verify its claimed consequence at the location it names; keep or dismiss; record every dismissal with a reason that disposes of that finding's own claim. Hand the fixer **survivors only**, and carry the dismissal list into this run's report.
=======
For each finding, verify its claimed consequence at the location it names; keep it, mark it unverified, or dismiss it; record every dismissal and every unverified finding with its reason; raise a grade only by effect; and rule on each line of the review's `### Declined to judge`. Hand the fixer **survivors only**, and carry every disposition into this run's report. A re-review — the one the fix cycle allows, or one you chose at the first settle prompt — is triaged under that reference's § On re-review: it carries forward what this run already ruled on this component — save, on a re-review you chose at the first settle prompt, the dismissed and unverified findings it re-verifies — and no survivor of it is handed to a fixer. At either of that reference's settle prompts, **Keep the verdict** means this component's review **stayed blocked** (below), and so does **Cancel**: this component stops, and the loop moves on to the next one.
>>>>>>> NEW
<<<<<<< OLD 1
- If the second verdict is still `BLOCK`, stop and escalate; do not continue to tests
=======
- Triage the re-review under `{{FT}}` § On re-review (the triage sub-step above); on that section's **Proceed**, continue to step 5 as after a verdict that is not `BLOCK`. If a `BLOCKER` survives that triage, or you keep the verdict at either settle prompt, this component's review **stayed blocked**: stop and escalate; do not continue to tests
>>>>>>> NEW
<<<<<<< OLD 1
the `review-fixer` `NEEDS HUMAN` stop, and a second verdict still `BLOCK`. The last two
=======
the `review-fixer` `NEEDS HUMAN` stop, and a review that stayed blocked. The last two
>>>>>>> NEW
<<<<<<< OLD 1
or whose review stayed `BLOCK`, **is** committed
=======
or whose review stayed blocked, **is** committed
>>>>>>> NEW
<<<<<<< OLD 1
or with a review still `BLOCK` — it is committed
=======
or with a review that stayed blocked — it is committed
>>>>>>> NEW
<<<<<<< OLD 1
- **Review triage:** [N findings reviewed, M survived] — dismissals: [one line per dismissal, `finding — reason`; or "none"]
=======
- **Review triage:** [one line per review pass of each component, per `{{FT}}` § Reporting — N findings reviewed: M survived, U unverified, X dismissed (C carried, on a re-review)] — survivors: [on a re-review, `finding — severity` per survivor, or "none"; "N/A (first review)" otherwise] — dismissals: [`finding — reason`, or "none"] — unverified: [`finding — if-true severity — what would settle it`, or "none"] — raised: [`finding — from → to — effect`, or "none"] — set aside by the reviewer: [`behaviour — ruling`, or "none"] — settled: [the answer given at a settle prompt, or "not asked"]
>>>>>>> NEW
<<<<<<< OLD 1
or with a review still `BLOCK`, or with kept regressions
=======
or with a review that stayed blocked, or with kept regressions
>>>>>>> NEW
<<<<<<< OLD 1
returns a non-BLOCK verdict
=======
returns a non-BLOCK verdict, or a `{{FT}}` settle prompt's **Proceed** settles it as one
>>>>>>> NEW
<<<<<<< OLD 1
its review verdict is non-`BLOCK` or the user chose to keep it,
=======
its review verdict is non-`BLOCK` or a settle prompt's **Proceed** settled it,
>>>>>>> NEW
<<<<<<< OLD 1
**"Stop and escalate" on a persisting `BLOCK` stops the component, not the run.**
=======
**"Stop and escalate" on a review that stayed blocked stops the component, not the run.**
>>>>>>> NEW
`````

#### `edits/ed-vuln-fixer.tpl`

`````text
<<<<<<< OLD 1
orchestrator-side stop at an unresolved `BLOCK`. `{{VULNCMD}}` Step 3.9 has a branch to commit onto in
   every one of those cases precisely because this step ran first. Report the branch name in the
   output record.
=======
orchestrator-side stop on a review that stayed blocked. `{{VULNCMD}}` Step 3.9 has a branch to commit
   onto in every one of those cases precisely because this step ran first. Report the branch name in
   the output record.
>>>>>>> NEW
`````

#### `edits/ed-vuln.tpl`

`````text
<<<<<<< OLD 1
**Triage sub-step** (before any fixer dispatch):
=======
**Triage sub-step** (before any fixer dispatch, and on every re-review):
>>>>>>> NEW
<<<<<<< OLD 1
For each finding, verify its claimed consequence at the location it names; keep or dismiss; record every dismissal with a reason that disposes of that finding's own claim. Hand the fixer **survivors only**, and carry the dismissal list into this run's report.
=======
For each finding, verify its claimed consequence at the location it names; keep it, mark it unverified, or dismiss it; record every dismissal and every unverified finding with its reason; raise a grade only by effect; and rule on each line of the review's `### Declined to judge`. Hand the fixer **survivors only**, and carry every disposition into this run's report. A re-review — the one the fix cycle allows, or one you chose at the first settle prompt — is triaged under that reference's § On re-review: it carries forward what this run already ruled on this CVE — save, on a re-review you chose at the first settle prompt, the dismissed and unverified findings it re-verifies — and no survivor of it is handed to a fixer. At either of that reference's settle prompts, **Keep the verdict** means this CVE's review **stayed blocked** (below), and so does **Cancel**: this CVE stops, and the run moves on to the next one.
>>>>>>> NEW
<<<<<<< OLD 1
If the second verdict is still `BLOCK`, stop and escalate; do not continue to tests.
=======
Triage the re-review under `{{FT}}` § On re-review (the triage sub-step above); on that section's **Proceed**, continue to step 4 as after a verdict that is not `BLOCK`. If a `BLOCKER` survives that triage, or you keep the verdict at either settle prompt, this CVE's review **stayed blocked**: stop and escalate; do not continue to tests.
>>>>>>> NEW
<<<<<<< OLD 1
when its review is still `BLOCK`,
=======
when its review stayed blocked,
>>>>>>> NEW
<<<<<<< OLD 1
- **Review triage:** [N findings reviewed, M survived] — dismissals: [one line per dismissal, `finding — reason`; or "none"]
=======
- **Review triage:** [one line per review pass of each CVE, per `{{FT}}` § Reporting — N findings reviewed: M survived, U unverified, X dismissed (C carried, on a re-review)] — survivors: [on a re-review, `finding — severity` per survivor, or "none"; "N/A (first review)" otherwise] — dismissals: [`finding — reason`, or "none"] — unverified: [`finding — if-true severity — what would settle it`, or "none"] — raised: [`finding — from → to — effect`, or "none"] — set aside by the reviewer: [`behaviour — ruling`, or "none"] — settled: [the answer given at a settle prompt, or "not asked"]
>>>>>>> NEW
<<<<<<< OLD 1
returns a non-BLOCK verdict
=======
returns a non-BLOCK verdict, or a `{{FT}}` settle prompt's **Proceed** settles it as one
>>>>>>> NEW
<<<<<<< OLD 1
(`NEEDS HUMAN`, a persisting review `BLOCK`)
=======
(`NEEDS HUMAN`, a review that stayed blocked)
>>>>>>> NEW
<<<<<<< OLD 1
A CVE stopped at an unresolved review `BLOCK` or at `NEEDS HUMAN`
=======
A CVE stopped at a review that stayed blocked or at `NEEDS HUMAN`
>>>>>>> NEW
`````

#### `edits/ie-rules-fixer.txt`

`````text
<<<<<<< OLD 1
- `review-fixer` handles BLOCKER findings; only one `review-fixer` cycle per review
=======
- `review-fixer` handles surviving BLOCKER and MAJOR findings; at most one `review-fixer` cycle per reviewed artifact, and none after its re-review (`references/finding-triage.md` § On re-review)
>>>>>>> NEW
`````

#### `edits/triage-core.txt`

`````text
<<<<<<< OLD 1
2. **Keep or dismiss.** Keep a finding only where verification confirmed its consequence. Dismiss noise,
   claims the verification refuted, and claims it could not substantiate — no path to the claimed
   consequence at the named site is a valid disposal. Whatever the reason, **it must dispose of that
   finding's own claim**: a true fact about neighbouring code that leaves the claim standing is not a
   dismissal, and the finding stays kept.
3. **Record every dismissal with its reason.** Never drop a finding silently. There is no "reject and
   say nothing" disposition and none may be added.

Only survivors are handed to the fixer.
=======
2. **Keep, mark unverified, or dismiss** — one outcome per finding, from what verification established:
   - **Keep** a finding where verification confirmed its consequence. A kept finding is a **survivor**.
   - **Dismiss** noise, and a claim the verification refuted — no path to the claimed consequence at the
     named site is a refutation, checked, and a valid disposal. Whatever the reason, **it must dispose
     of that finding's own claim** — by refuting it, or, for an unverified finding the next bullet
     dismisses, by its grade if true: a true fact about neighbouring code that leaves the claim standing
     settles nothing, and the finding is kept where verification confirmed it and is otherwise one
     verification could not settle.
   - **Mark unverified** a finding verification could not settle — the diff and the code around it leave
     open whether its consequence occurs. Use this only where they leave the question open; where they
     are enough to decide, keep the finding or dismiss it. Its grade if true is the reviewer's, raised by
     effect as step 4 says. One whose grade if true is `MAJOR` or `BLOCKER` is recorded at that grade,
     marked `(unverified)`, with what would settle it — the file to read, the input to trace, the run
     that would show it. One whose grade if true is only `MINOR` or `NIT` is dismissed, with that grade
     and what would settle it as its reason. An unverified finding changes nothing the verdict gates;
     it reaches the user through § Reporting.
3. **Record every dismissal and every unverified finding with its reason.** Never drop a finding
   silently. There is no "reject and say nothing" disposition and none may be added.
4. **Raise a grade by effect, never lower one.** Where a survivor's grade reflects the spec's, the
   plan's or the task's silence on the input that triggers it, rather than what the people the change
   serves meet if it ships as it stands — users of the software, readers of the document — raise
   it, to `MAJOR` at most: a `BLOCKER` changes the verdict, and the verdict is not triage's to
   restate (§ When triage empties the survivor set). Step 2 grades an unverified finding by this rule
   too. Record every raise with its reason.
5. **Rule on what the reviewer set aside.** Where the review carries a `### Declined to judge` list
   (`code-review` returns one), rule on each line: it **stands** — record why — or it is a **defect**,
   recorded with its grade by effect and what shows it. A line ruled a defect is never handed to the
   fixer: no finding of the review carries it, and the verdict was taken without it.

**A reviewer with two grades** — one filing only `BLOCKER` and `RECOMMENDATION` — maps onto steps 2
and 4 with `RECOMMENDATION` below `MAJOR`: an unverified `RECOMMENDATION` is dismissed with its note,
and step 4 raises nothing, since the grade above it is `BLOCKER`.

Only survivors are handed to the fixer — never an unverified finding, never a dismissed one.
>>>>>>> NEW
<<<<<<< OLD 1
Triage disposes of findings; it does not restate the verdict. Where every finding behind a non-`PASS`
verdict is dismissed, the verdict is left standing on nothing — and because the **verdict**, not the
survivor set, is what gates every downstream branch, the run would otherwise dispatch a fixer with no
findings to apply, or escalate a `BLOCKER` triage has already refuted. The disposition, in order:
=======
Triage disposes of findings; it does not restate the verdict. Where no finding behind a non-`PASS`
verdict survives, every one of them dismissed or unverified, the verdict is left standing on nothing —
and because the **verdict**, not the survivor set, is what gates every downstream branch, the run would
otherwise dispatch a fixer with no findings to apply, or escalate a `BLOCKER` that did not survive
triage. The disposition, in order:
>>>>>>> NEW
<<<<<<< OLD 1
2. **Never run the unresolved-`BLOCKER` escalation on a refuted `BLOCKER`.** That escalation exists
   for a `BLOCKER` that survived a fix cycle, not for one that never survived triage.
3. **Surface it and let the user settle the verdict.** Report the verdict, the fact that nothing
   survived, and every dismissal with its reason, then ask:
   ```
   choices: ["Proceed as if the verdict were PASS — the dismissals are recorded (Recommended)", "Re-review, supplying the dismissal reasons", "Keep the verdict and stop for a human decision", "Cancel"]
   ```
   **Never** promote a non-`PASS` verdict to `PASS` silently. The orchestrator's authority under this
   reference is over *findings*; a verdict its own findings no longer support is the user's to settle.
=======
2. **Never run the unresolved-`BLOCKER` escalation on a `BLOCKER` that did not survive triage** —
   unless the user keeps the verdict at step 3's prompt. That escalation exists for a `BLOCKER` that
   survived a fix cycle, not for one that never survived triage; a user who keeps the verdict says the
   review stayed blocked (§ On re-review), at their own word.
3. **Surface it and let the user settle the verdict.** Report the verdict, the fact that nothing
   survived, every dismissal with its reason and every unverified finding with what would settle it,
   then ask:
   ```
   choices: ["Proceed as if the verdict were PASS — every disposition is recorded (Recommended)", "Re-review, supplying every disposition's reason", "Keep the verdict and stop for a human decision", "Cancel"]
   ```
   **Keep the verdict** means the review stayed blocked: the caller takes its stop or escalation over
   the `BLOCKER`s the reviewer raised. Where the kept verdict is not `BLOCK` the reviewer raised none,
   and a caller whose stop for a review that stayed blocked is an escalation ends the run instead — or,
   working unit by unit, the unit — as its own Cancel does. **Cancel** is the caller's own cancel.
   **Never** promote a non-`PASS` verdict to `PASS` silently. The orchestrator's authority under this
   reference is over *findings*; a verdict its own findings no longer support is the user's to settle.
>>>>>>> NEW
<<<<<<< OLD 1
A partly emptied set is not this case: where at least one finding survived, the verdict stands and the
command's normal branch runs on the survivors.
=======
A partly emptied set is not this case: where at least one finding survived, the verdict stands and the
command's normal branch runs on the survivors.

This section governs the first review. On a re-review, § On re-review settles the verdict instead —
there, no survivor is handed to a fixer, and its own prompt carries no re-review arm. The prompt
above, in either form, and § On re-review's are this reference's **settle prompts**.
>>>>>>> NEW
<<<<<<< OLD 1
smallest fix adds no public surface and **guards no state the finding did not demonstrate**. A survivor
failing any of those conditions is surfaced for a human decision instead of patched.

That last clause is the load-bearing one: a guard added for a state the finding never demonstrated is
the most common shape of a "fix" applied to a false positive, and it is invisible afterwards because it
looks like defensive coding.
=======
smallest fix adds no public surface, **guards no state the finding did not demonstrate**, and **edits no
file that tells agents or contributors how to work in the repository — `CLAUDE.md`, `AGENTS.md`,
`.github/copilot-instructions.md`, a file under `.claude/rules/` or `.github/instructions/`,
`CONTRIBUTING.md`, `CODING_STANDARDS.md` — that the change under review did not itself edit**. A
survivor failing any of those conditions is surfaced for a human decision instead of patched.

The guard clause is the load-bearing one: a guard added for a state the finding never demonstrated is
the most common shape of a "fix" applied to a false positive, and it is invisible afterwards because it
looks like defensive coding.

The instruction-file clause exists because `code-review` reads the repository's instruction and
contributor files as its documented standards: a finding that the change contradicts one of them is
the likeliest kind to reach the fixer, and editing the file to agree with the code makes such a
finding disappear without settling it. Where the change under review itself edited the file, a
finding on it is a finding on the change, and the clause does not apply. A fixer agent is not handed
the diff, so it applies the clause by the finding's location: it edits such a file only where the
finding's own location is in that file.

## On re-review

A **re-review** is any review a run dispatches over an artifact this run has already reviewed to a
verdict, whatever that verdict was: the one re-review a caller's cap allows, a re-review the user
chose at § When triage empties the survivor set, and `{{IMPL}}`'s review of its Phase 3.5 fix delta.
For a caller that works unit by unit, the artifact is the unit's own change, never the working tree's
cumulative diff. A `### Re-classification` return is no verdict: whether the review dispatched after
the user overrides one is a re-review turns only on whether an earlier review reached a verdict over
that artifact. A re-review's findings are triaged by § The step, with one check first and three
rules after.

**First, carry what this run already ruled.** A finding that names the same location as a row this
run already logged over that artifact — a code site or a document passage, whose line numbers may
have moved with the fix — and makes the same claim, where the text there still reads as the row
describes, keeps that row's outcome. It is marked **carried**, is not verified again, and is never
handed to a fixer again. A row whose fix changed the text there no longer matches: verify that
finding afresh. A carried survivor is a finding this run has not fixed — a fix that did not take, or
one no fixer was handed — and counts as a survivor below. **The one exception** is a re-review the
user chose at § When triage empties the survivor set, which exists to put every disposition's reason
to the reviewer: there, a re-raised dismissed or unverified finding is verified afresh against the
reviewer's answer.

**Then:**

1. **No survivor of a re-review is handed to a fixer** — each artifact gets at most one fix cycle, and
   only before its first re-review. Each survivor is recorded in the triage line at its own severity,
   and a second verdict that is not `BLOCK` gates nothing further.
2. **The caller's second-verdict stop or escalation acts on a `BLOCKER` surviving the re-review's
   triage — never on the verdict word.** A `BLOCKER` carried as dismissed or unverified is not one.
   A review **stayed blocked** where a `BLOCKER` survives its re-review's triage, or where the user
   keeps the verdict at either settle prompt — the name every caller that re-reviews gives this stop;
   a caller that works unit by unit may count a settle prompt's **Cancel** as one too, and says so.
3. **Where the second verdict is `BLOCK` and no `BLOCKER` survives**, the verdict is one its own
   findings no longer support. Never promote it silently: report the verdict, each carried row with
   its outcome and every new disposition, then ask:
   ```
   choices: ["Proceed — no BLOCKER survived triage, and every disposition is recorded (Recommended)", "Keep the verdict and stop for a human decision", "Cancel"]
   ```
   There is no re-review arm: this is the re-review the cap allows. **Proceed** continues as the
   caller does after a second verdict that is not `BLOCK`. **Keep the verdict** means the review
   stayed blocked: the caller takes its stop or escalation over the `BLOCKER`s the reviewer raised —
   at the user's word, not on triage's. **Cancel** is the caller's own cancel.
>>>>>>> NEW
<<<<<<< OLD 1
## Reporting

The orchestrator's run report names, for the triage step: how many findings were reviewed, how many
survived, and **every dismissal with its reason**. A triage that reports only survivors is
indistinguishable from a reviewer that found less.
=======
## Reporting

The orchestrator's run report carries one triage line per review pass, and the line names:

- how many findings were reviewed, and how many **survived**, are **unverified** and were
  **dismissed** — the three always sum to the findings reviewed, and a finding in none of them is a
  triage failure; on a re-review, also how many were **carried**;
- on a re-review, every survivor with its severity — none of them is handed to a fixer;
- **every dismissal with its reason** — a triage that reports only survivors is indistinguishable from
  a reviewer that found less;
- every unverified finding with its grade if true and what would settle it;
- every raise, with the grade it moved from and to and the effect that moved it;
- where the review carried a `### Declined to judge` list, each line with its ruling;
- where a settle prompt was asked, its answer, so a verdict the user settled is never left unmarked.
>>>>>>> NEW
`````

## Appendix C — changelog sections

Extracted by Task 0 Step 2 into `$S/cl`; `release.py` inserts each above its plugin's current top section.

#### `cl/aw-dev-workflows.md`

`````markdown
## [4.6.0] — 2026-10-03

**Update `workflows-core` to 1.11.0 with this release**: the review cycles below follow its `finding-triage` § On re-review, and `/design` cites its new `— commands that fix inline` escalation heading.

### Added
- **`code-review` grades by effect** where no dimension fixes the grade — what a reasonable person using the software meets if the change ships, the spec's silence on the triggering input being no permission — and returns `### Declined to judge`: every behaviour it set aside, with the reason, for the orchestrator to rule on. Prompted by superpowers 5bf4e780 (#2319).
- **`code-review` dimension 4 gains four checks**: the unnamed members of a fixed value set the change special-cases, a re-check of something already held (name the call that invalidates it), every changed call against its callee's declaration (tests included), and removed code whose contract nothing replaced. Prompted by BMAD 44e0f806 (edge-case hunter, deletion check).
- **`code-review` finds the repository's documented standards** before dimension 3 — `CLAUDE.md` and `AGENTS.md` at the root and on the path to each changed file, `CONTRIBUTING.md`, `CODING_STANDARDS.md`, and the `.claude/rules/` files whose `paths:` match a changed file or which have none — and leaves to the repository's lint, format and type-check configuration what they already enforce. "A documented standard overrides" had no rule for finding one. Prompted by BMAD 23f134e2 and mattpocock's code-review step 3.
- **A plan's Review focus** — up to five input classes or failure modes the task implies and no step's tests exercise, each with the behaviour a user would expect: `risk-planner` returns `### Review focus`, `/implement`'s Phase 2A plan carries it as item 9, `test-writer` writes a test for each line or names why it cannot, and `code-review` checks each one. Prompted by superpowers 5bf4e780 (writing-plans § Review Focus).

### Changed
- **`/implement`, `/vuln` and `/upgrade` triage the re-review** (`workflows-core:finding-triage` § On re-review) and stop only on a review that **stayed blocked**: a second `BLOCK` whose `BLOCKER`s did not survive triage now goes to the user to settle, where it used to stop the run. `/vuln` and `/upgrade` count a settle prompt's Cancel, like its Keep-the-verdict, as the unit's review having stayed blocked — the CVE or component stops and is committed, and the run moves on; the test-gate invariant of all three names a settle prompt's Proceed. `/implement` Phase 3B step 8's review of the Phase 3.5 delta is triaged and acted on the same way — it had no verdict handling. `/implement`'s early-stop lists now name both settle prompts' Keep-the-verdict and Cancel arms, so those stops commit the work with `clean_finish: false` like every other stop after the branch exists.
- **`/implement` records in `### Deferred items` each behaviour `test-writer` names as untested**, a Review focus line included — a test the run could not write, which no section used to name.
- **The triage report line** names unverified findings, raises, the reviewer's set-aside behaviours, any settle prompt's answer and every survivor of a re-review, which `/implement` also lists in `### Deferred items` and in its pull-request body; `review-fixer` applies the patch gate's instruction-file clause by the finding's location, since it is not handed the diff; `code-handoff` §2.9 names a review that stayed blocked.

### Fixed
- **`/design` escalated an unresolved BLOCKER per the `/epics` rule**, whose "Defer" appends a refinement note to the draft — which `/design`'s own handoff refuses while an item in it is open. It now cites `Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline`.
`````

#### `cl/aw-docs-workflows.md`

`````markdown
## [1.5.0] — 2026-10-03

**Update `workflows-core` to 1.11.0 with this release**: the commands below follow its `finding-triage` § On re-review and its patch gate's instruction-file clause.

### Changed
- **`/document` triages its re-review** (`workflows-core:finding-triage` § On re-review) and escalates only on a review that **stayed blocked** — a `BLOCKER` surviving that triage, or a verdict the user keeps at a settle prompt — ending the run as Cancel does on a kept verdict that is not `BLOCK`; its triage line names unverified findings, raises, any settle prompt's answer and every survivor of a re-review.
- **`/docs-init`, `/docs-brand` and `/docs-audit` report unverified findings, raises and any settle prompt's answer** beside survivors and dismissals, a verdict the user settled marked as such, settle an emptied survivor set with a prompt that has no re-review arm — `/docs-init` and `/docs-brand` stop at their review gate on its Keep-the-verdict or Cancel, the report saying which, and `/docs-audit` takes its unresolved-BLOCKER stop, or its Cancel route on a kept verdict that is not `BLOCK` — and `/docs-init` and `/docs-brand` list unverified findings in their pull-request drafts and say what a Cancel at the review gate leaves behind; their direct edits honour the patch gate's instruction-file clause; `docs-audit-reviewer` no longer counts the reference's steps.

### Fixed
- **`scaffold-tree.md` §7's and `/docs-audit`'s ignore test read every line `git check-ignore -v` prints as a match**, though it also prints a negated `!` pattern that re-includes the path; the scaffold left such a path unstaged and removed its config references, and `/docs-audit` reported its backlog as ignored. A `!` line is now no match.
`````

#### `cl/aw-product-workflows.md`

`````markdown
## [3.12.0] — 2026-10-03

**Update `workflows-core` to 1.11.0 with this release**: the commands below cite its new escalation heading and its `finding-triage` § On re-review.

### Changed
- **`/epics`, `/prd-proposal` and `/brd-proposal` triage their re-review** (`workflows-core:finding-triage` § On re-review) and escalate only on a review that **stayed blocked** — a `BLOCKER` surviving that triage, or a verdict the user keeps at a settle prompt — ending the run instead, as Cancel does, on a kept verdict that is not `BLOCK`; their triage reports unverified findings, raises, any settle prompt's answer and every survivor of a re-review, and `proposal-reviewer` describes the three outcomes.

### Fixed
- **`/create-prd`, `/update-prd`, `/create-ard`, `/prd-proposal` and `/brd-proposal` escalated per a `Review verdict BLOCK` rule `escalation-rules` did not have.** They now cite `Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline`, and `/create-prd`'s inline copy of its choices matches that heading word for word.
`````

#### `cl/aw-workflows-core.md`

`````markdown
## [1.11.0] — 2026-10-03

### Added
- **`finding-triage` gains a third outcome, `unverified`.** A finding the orchestrator can neither confirm nor refute — the diff and the code around it leave the question open — is no longer dismissed as unsubstantiated: one that would be `MAJOR` or `BLOCKER` if true is recorded at that grade, marked `(unverified)`, with what would settle it, and reaches the user in the triage line; one that would be only `MINOR` or `NIT` is dismissed with the same note. It is never handed to a fixer and changes nothing the verdict gates. Prompted by BMAD's `maybe-false` triage verdict (3433612d, b0d27c3c).
- **`finding-triage` § On re-review.** Every re-review is now triaged too — any review over an artifact the run has already reviewed to a verdict, `/implement`'s review of its Phase 3.5 delta included. A finding at the same location — a code site or a document passage — making the same claim as a row this run already logged over the same artifact (for `/vuln` and `/upgrade`, the CVE's or component's own change), where the text there still reads as that row describes, keeps the row's outcome (`carried`): it is not verified again — except on a re-review the user chose to put the dispositions' reasons to the reviewer — and never handed to a fixer again; no survivor of a re-review is handed to a fixer; and the caller's stop acts on a review that **stayed blocked** — a `BLOCKER` surviving that triage, or a verdict the user keeps at a settle prompt — never on the verdict word. A second `BLOCK` with no surviving `BLOCKER` is the user's to settle, at a prompt with no re-review arm, never promoted silently. Prompted by BMAD 7c3e5827 and 85d968fc.
- **Triage raises a grade by effect, to `MAJOR` at most, and never lowers one**, and rules on each line of a `code-review` `### Declined to judge` list — a line ruled a defect is recorded, never handed to a fixer. Prompted by superpowers 5bf4e780 (#2319).
- **`escalation-rules`: `Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline`** — the heading five commands already cited (see Fixed).

### Changed
- **The patch gate never edits an instruction or contributor file the change did not itself edit** — `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, a file under `.claude/rules/` or `.github/instructions/`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`: such a fix is surfaced for a human decision. `doc-fixer` applies the clause by the finding's location, since it is not handed the diff. `code-review` now reads `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `CODING_STANDARDS.md` and the `.claude/rules/` files that apply to the change as the repository's standards, which makes "edit the file to agree with the code" the likeliest wrong fix.
- **The triage line is one per review pass**, and survived + unverified + dismissed must sum to the findings reviewed. Where a settle prompt was asked, the line carries its answer, so a verdict the user settled is never left unmarked there; a re-review's line also names every survivor, none of which is handed to a fixer.
- **The first settle prompt** — the one an emptied survivor set raises — now says every disposition is recorded and puts every disposition's reason to a re-review, and a caller that runs no re-review asks it without that arm. A reviewer with two grades (`BLOCKER` and `RECOMMENDATION`) maps onto the unverified and raise rules with `RECOMMENDATION` below `MAJOR`.
- **`model-routing/classification` §6**: a disposition may be an unverified record, and item 4 names the four edge-case checks `code-review` dimension 4 gained.

### Fixed
- **Five commands escalated per a `Review verdict BLOCK` rule this reference did not have** (`/create-prd`, `/update-prd`, `/create-ard`, `/prd-proposal`, `/brd-proposal`) — only the `— /document` and `— /epics` variants existed — and `/design` cited the `— /epics` one, whose "Defer" appends a refinement note to the draft that `/design`'s own handoff then refuses. The new heading is the one all six cite (`product-workflows` 3.12.0, `dev-workflows` 4.6.0). `/specify` keeps the `— /epics` rule on purpose: it defines its own "Defer" to mirror it.
`````

#### `cl/ce-dev-workflows.md`

`````markdown
## [2.36.0] — 2026-10-03

### Added
- **`finding-triage` gains a third outcome, `unverified`.** A finding the orchestrator can neither confirm nor refute — the diff and the code around it leave the question open — is no longer dismissed as unsubstantiated: one that would be `MAJOR` or `BLOCKER` if true is recorded at that grade, marked `(unverified)`, with what would settle it, and reaches the user in the triage line; one that would be only `MINOR` or `NIT` is dismissed with the same note. It is never handed to a fixer and changes nothing the verdict gates. Prompted by BMAD's `maybe-false` triage verdict (3433612d, b0d27c3c).
- **`finding-triage` § On re-review.** Every re-review is now triaged too (any review over an artifact the run has already reviewed to a verdict, `implement:`'s review of its Phase 3.5 delta included): a finding at the same code site, making the same claim as a row this run already logged over the same artifact (for `vuln:` and `upgrade:`, the CVE's or component's own change), where the code still reads as that row describes, keeps the row's outcome (`carried`): it is not verified again — except on a re-review the user chose to put the dispositions' reasons to the reviewer — and never handed to a fixer again; no survivor of a re-review is handed to a fixer; and `implement:`, `vuln:`, `upgrade:`, `document:` and `epics:` stop or escalate only on a review that **stayed blocked** — a `BLOCKER` surviving that triage, or a verdict the user keeps at a settle prompt — never on the verdict word, and `document:` and `epics:` end the run as Cancel does on a kept verdict that is not `BLOCK`; a second `BLOCK` with no surviving `BLOCKER` goes to the user to settle, where it used to stop the run, and is never promoted silently. `implement:` Phase 3B step 8's review of the Phase 3.5 delta is triaged and acted on the same way — it had no verdict handling — and its early-stop list now names both settle prompts' Keep-the-verdict and Cancel arms; it also records in `### Deferred items` each behaviour `test-writer` names as untested. Prompted by BMAD 7c3e5827 and 85d968fc.
- **Severity by effect, and "Declined to judge."** `code-review` grades a finding no dimension fixes by what a reasonable person using the software meets if the change ships — the spec's silence on the triggering input is no permission — and returns `### Declined to judge`, every behaviour it set aside with the reason. Triage raises a grade by effect, to `MAJOR` at most, never lowers one, and rules on each set-aside line. Prompted by superpowers 5bf4e780 (#2319).
- **`code-review` dimension 4 gains four checks** — implicit branches of a fixed value set, handle lifetime, call against declaration (tests included), removed contracts — prompted by BMAD 44e0f806; and **finds the repository's documented standards** before dimension 3 — `CLAUDE.md` and `AGENTS.md` at the root and on the path to each changed file, `CONTRIBUTING.md`, `CODING_STANDARDS.md`, `.github/copilot-instructions.md`, and the `.github/instructions/*.instructions.md` files whose `applyTo:` matches — prompted by BMAD 23f134e2 and mattpocock's code-review step 3.
- **A plan's Review focus** — up to five input classes or failure modes the task implies and no step's tests exercise: `risk-planner` returns `### Review focus`, `implement:`'s Phase 2A plan carries it as item 9, `test-writer` writes a test for each line or names why it cannot, and `code-review` checks each one. Prompted by superpowers 5bf4e780.

### Changed
- **The patch gate never edits an instruction or contributor file the change did not itself edit** (`CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `.claude/rules/`, `.github/instructions/`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`); `review-fixer` and `doc-fixer`, which are not handed the diff, defer such an edit unless the finding's own location is in that file. The triage line is one per review pass, survived + unverified + dismissed must sum to the findings reviewed, and it carries any settle prompt's answer; a re-review's line names every survivor, which `implement:` also lists in `### Deferred items` and in its pull-request body.

### Fixed
- **`create-vi:`, `update-vi:` and `create-ard:` escalated per a `Review verdict BLOCK` rule `escalation-rules` did not have**, and `design:` cited the `epics:` variant, whose "Defer" appends a refinement note to the draft its own handoff then refuses. All four now cite the new heading `Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline`, and `create-vi:`'s inline choices match it word for word. `specify:` keeps the `epics:` rule on purpose: it defines its own "Defer" to mirror it.
`````

#### `cl/ie-dev-workflows.md`

`````markdown
## [2.67.0] — 2026-10-03

### Added
- **`finding-triage` gains a third outcome, `unverified`.** A finding the orchestrator can neither confirm nor refute — the diff and the code around it leave the question open — is no longer dismissed as unsubstantiated: one that would be `MAJOR` or `BLOCKER` if true is recorded at that grade, marked `(unverified)`, with what would settle it, and reaches the user in the triage line; one that would be only `MINOR` or `NIT` is dismissed with the same note. It is never handed to a fixer and changes nothing the verdict gates. Prompted by BMAD's `maybe-false` triage verdict (3433612d, b0d27c3c).
- **`finding-triage` § On re-review.** Every re-review is now triaged too (any review over an artifact the run has already reviewed to a verdict, `/implement`'s review of its Phase 3.5 delta included): a finding at the same code site, making the same claim as a row this run already logged over the same artifact (for `/vuln` and `/upgrade`, the CVE's or component's own change), where the code still reads as that row describes, keeps the row's outcome (`carried`): it is not verified again — except on a re-review the user chose to put the dispositions' reasons to the reviewer — and never handed to a fixer again; no survivor of a re-review is handed to a fixer; and `/implement`, `/vuln`, `/upgrade`, `/document` and `/epics` stop or escalate only on a review that **stayed blocked** — a `BLOCKER` surviving that triage, or a verdict the user keeps at a settle prompt — never on the verdict word, and `/document` and `/epics` end the run as Cancel does on a kept verdict that is not `BLOCK`; a second `BLOCK` with no surviving `BLOCKER` goes to the user to settle, where it used to stop the run, and is never promoted silently. `/implement` Phase 3B step 8's review of the Phase 3.5 delta is triaged and acted on the same way — it had no verdict handling — and its early-stop list now names both settle prompts' Keep-the-verdict and Cancel arms; it also records in `### Deferred items` each behaviour `test-writer` names as untested. Prompted by BMAD 7c3e5827 and 85d968fc.
- **Severity by effect, and "Declined to judge."** `code-review` grades a finding no dimension fixes by what a reasonable person using the software meets if the change ships — the spec's silence on the triggering input is no permission — and returns `### Declined to judge`, every behaviour it set aside with the reason. Triage raises a grade by effect, to `MAJOR` at most, never lowers one, and rules on each set-aside line. Prompted by superpowers 5bf4e780 (#2319).
- **`code-review` dimension 4 gains four checks** — implicit branches of a fixed value set, handle lifetime, call against declaration (tests included), removed contracts — prompted by BMAD 44e0f806; and **finds the repository's documented standards** before dimension 3 — `CLAUDE.md` and `AGENTS.md` at the root and on the path to each changed file, `CONTRIBUTING.md`, `CODING_STANDARDS.md`, and the `.claude/rules/` files whose `paths:` match a changed file or which have none — prompted by BMAD 23f134e2 and mattpocock's code-review step 3.
- **A plan's Review focus** — up to five input classes or failure modes the task implies and no step's tests exercise: `risk-planner` returns `### Review focus`, `/implement`'s Phase 2A plan carries it as item 9, `test-writer` writes a test for each line or names why it cannot, and `code-review` checks each one. Prompted by superpowers 5bf4e780.

### Changed
- **The patch gate never edits an instruction or contributor file the change did not itself edit** (`CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `.claude/rules/`, `.github/instructions/`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`); `review-fixer` and `doc-fixer`, which are not handed the diff, defer such an edit unless the finding's own location is in that file. The triage line is one per review pass, survived + unverified + dismissed must sum to the findings reviewed, and it carries any settle prompt's answer; a re-review's line names every survivor, which `/implement` also lists in `### Deferred items` and in its pull-request body.

### Fixed
- **`/create-vi`, `/update-vi` and `/create-ard` escalated per a `Review verdict BLOCK` rule `escalation-rules` did not have**, and `/design` cited the `/epics` variant, whose "Defer" appends a refinement note to the draft its own handoff then refuses. All four now cite the new heading `Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline`, and `/create-vi`'s inline choices match it word for word. `/specify` keeps the `/epics` rule on purpose: it defines its own "Defer" to mirror it.
`````

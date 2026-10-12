# Epic Sizing for One Agent Run — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/epics` sizes every Epic for one agent run — at most 5 acceptance criteria and 4 suggested stories, split along its stories within one component — and asks the PE only about misses.

**Architecture:** `/epics` owns the limit (`size_limit`) and hands it to `epic-writer` (which splits while drafting) and `epic-reviewer` (a new *Epic size* dimension). A new Phase 6 step 4 counts every drafted Epic and asks split / keep whole for any still over; a focus run re-splits only an Epic not yet specified, designed or implemented. All changes are prose executed literally by agents.

**Tech Stack:** Markdown command/agent prose; Python 3.11 string-assertion check script; the repo's CI gate chain (`scripts/validate-catalog.py`, `scripts/check-id-grammar.sh`, `scripts/check-docs.sh`, `scripts/mermaid/check-mermaid.mjs`).

**Spec:** `docs/superpowers/specs/2026-10-12-epic-sizing-design.md`

## Global Constraints

- The limit: at most **5** acceptance criteria and **4** suggested stories per Epic; over means more than 5 or more than 4; counted as top-level `- ` bullets directly under `## Acceptance criteria` and `## Suggested stories`, a guard criterion included (spec D1).
- Components first, size second: a split never crosses a component and never merges Epics (spec D0).
- `/epics` is the one place that states the numbers, as `size_limit: {criteria: 5, stories: 4}` (spec D2); the agents read them from their briefs.
- `kept_whole:` is written only from the operator's words — a D5 answer or a Phase 2 plan revision — never from the writer's judgement (spec D8).
- A focus run never splits an Epic whose folder holds `specification.md`, `design.md` or `implementation.md` (spec D7).
- No new `## Phase` heading: `docs/commands/epics.md` counts `/epics`' 23 `## Phase` headings and diagrams them; the count-and-ask is Phase 6 **step 4**.
- Every `choices:` array has 2–4 options and no "Other" option (CLAUDE.md hard constraint; check 12).
- Prose is executed literally: a false or ambiguous sentence is a defect (CLAUDE.md § Editing discipline).
- Release: product-workflows **3.32.0**, in `plugins/product-workflows/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` and `plugins/product-workflows/CHANGELOG.md`, dated `2026-10-12`.
- Verify the branch (`git branch --show-current` = `iv-gu/epic-sizing`) immediately before every commit.

## Review Focus

- An Epic exactly at the limit (5 criteria, 4 stories) — must NOT be split or flagged; only *more than* the limit is over. Pinned in Task 2 (the step-4 wording "exceeds") and Task 3 ("over either limit").
- A split whose slice is still over the limit — must be asked once more without *Split*, never re-split in a loop. Pinned in Task 2.
- A focus run on an Epic holding only `implementation.md` (no spec, no design) — must be not splittable. Pinned in Task 2 (all three files named).
- A full PRD run with an oversized Epic already on disk — listed in `### Sizing`, never re-drafted. Pinned in Task 2.
- An Epic producing an `[AD#N]` interface, split by size — exactly one slice keeps the `Produces` line. Pinned in Task 1.

---

### Task 0: The check script

**Files:**
- Create: `<scratchpad>/epic-sizing/check.py` (the session scratchpad — never the repo). Throughout this plan `<scratchpad>` is `/tmp/claude-1000/-home-ihudak-dev-ai-tools-ai-workflows/2878bf89-2294-4e3d-b53a-a35dc02ac6af/scratchpad` and `<root>` is `/home/ihudak/dev/ai-tools/ai-workflows`.

**Interfaces:**
- Produces: `python3 check.py <repo-root> [group]` — groups `writer`, `cmd`, `reviewer`, `docs`, `release`, `focus`; prints `<group>: N passed, M failed`; exit 0 only when all selected pass.

- [ ] **Step 1: Write the check script**

```python
#!/usr/bin/env python3
"""String assertions for Epic sizing. usage: check.py <root> [group]"""
import re, sys
root = sys.argv[1]; WANT = sys.argv[2] if len(sys.argv) > 2 else "all"
P = "plugins/product-workflows"
E, W, R = f"{P}/commands/epics.md", f"{P}/agents/epic-writer.md", f"{P}/agents/epic-reviewer.md"
D = f"{P}/docs/commands/epics.md"
def text(p): return re.sub(r"\s+", " ", open(f"{root}/{p}", encoding="utf-8").read())
RES = []
def has(g, p, s): RES.append((g, s in text(p), f"{p}: has {s!r}"))
def hasnt(g, p, s): RES.append((g, s not in text(p), f"{p}: lacks {s!r}"))
# writer (D0, D1, D3, D8)
hasnt("writer", W, "Prefer fewer, larger Epics")
has("writer", W, "- `size_limit` — `{criteria, stories}`")
has("writer", W, "**Components first, size second.**")
has("writer", W, "**An Epic is sized for one agent run**")
has("writer", W, "an `[AD#N]` interface keeps exactly one producing Epic")
has("writer", W, "**Never bundle** several independently testable behaviours")
has("writer", W, "never write `kept_whole` on your own judgement")
has("writer", W, "kept_whole: <only where the scope keeps this Epic whole over size_limit")
has("writer", W, "**A focus run that splits by size**")
# command (D2, D4, D5, D8)
hasnt("cmd", E, "prefer fewer, larger Epics")
has("cmd", E, "no Epic over 5 acceptance criteria or 4 suggested stories")
has("cmd", E, "`size_limit` (`{criteria: 5, stories: 4}` — this command's one statement of the limit")
has("cmd", E, "4. **Count every Epic against `size_limit`.**")
has("cmd", E, "where either count exceeds `size_limit`'s")
has("cmd", E, 'choices: ["Split it along its stories (Recommended)", "Keep it whole — give the reason", "Cancel"]')
has("cmd", E, 'choices: ["Keep it whole — give the reason", "Cancel"]')
has("cmd", E, "never re-dispatched for it a second time")
has("cmd", E, "> size_limit:")
has("cmd", E, "### Sizing")
has("cmd", E, "Existing Epics over the limit:")
has("cmd", E, "- ALWAYS size every Epic this run writes or refines against `size_limit`")
# focus run (D7)
has("focus", E, "holds `specification.md`, `design.md` or `implementation.md`")
has("focus", E, "the writer keeps the Epic's key and its first slice")
has("focus", E, "never re-drafted")
# reviewer (D6)
has("reviewer", R, "- **`size_limit`** (optional)")
has("reviewer", R, "| Epic size (conditional) |")
has("reviewer", R, "In `not_splittable` → report it, never a finding.")
has("reviewer", R, "bundles several independently testable behaviours")
# docs, rules, release (D10)
has("docs", D, "### Sizing")
has("docs", D, "Components first, size second")
has("docs", ".claude/rules/product-workflows.md", "writing (one target per Epic, each within `size_limit`")
has("release", f"{P}/.claude-plugin/plugin.json", '"version": "3.32.0"')
has("release", f"{P}/CHANGELOG.md", "## [3.32.0] — 2026-10-12")
rows = [r for r in RES if WANT in ("all", r[0])]
for g, ok, m in rows:
    if not ok: print("FAIL", g, m)
print(f"{WANT}: {sum(1 for r in rows if r[1])} passed, {sum(1 for r in rows if not r[1])} failed")
sys.exit(0 if all(r[1] for r in rows) else 1)
```

- [ ] **Step 2: Run it — every group must fail**

Run: `python3 <scratchpad>/epic-sizing/check.py /home/ihudak/dev/ai-tools/ai-workflows`
Expected: `all: 0 passed, 33 failed` (the two `hasnt` checks fail too, since "fewer, larger" is still present).

---

### Task 1: `epic-writer` — the size rule, `kept_whole`, the size split

**Files:**
- Modify: `plugins/product-workflows/agents/epic-writer.md` (Inputs list; Pre-flight step 2; the `epic.md` template frontmatter; *Refinement mode*'s `mode: both` paragraph)

**Interfaces:**
- Consumes: `size_limit` from the handoff (Task 2 puts it there).
- Produces: Epics within the limit; `kept_whole: "<reason>"` frontmatter only from `scope`; a size split on a focus run in `mode: both`.

- [ ] **Step 1: Confirm RED** — `python3 check.py <root> writer` → `writer: 0 passed, 9 failed`.

- [ ] **Step 2: Add the input.** Insert after the Inputs bullet that begins ``- `docs_grounding` —`` (one new line):

```markdown
- `size_limit` — `{criteria, stories}`: the most acceptance criteria and suggested stories one Epic may hold (`/epics` owns the numbers, Phase 6). Absent → no limit, as before.
```

- [ ] **Step 3: Rewrite the sizing rule.** Replace exactly these two lines of Pre-flight step 2:

```
2. **Sizing / sequencing.** Prefer fewer, larger Epics when the PRD direction is
   already validated; split only at a genuine risk or feedback-loop boundary.
```

with:

```markdown
2. **Sizing / sequencing.** **Components first, size second.** A capability that lands in two or more components is already one Epic per component (*Components and contracts* below), however small each is; size then applies to each Epic on its own and only ever splits further within one component — never merging Epics, never moving work across components. **An Epic is sized for one agent run**: where the handoff carries `size_limit`, no Epic holds more acceptance criteria than `size_limit.criteria` or more suggested stories than `size_limit.stories`, each counted as the top-level `- ` bullets directly under its `## Acceptance criteria` and `## Suggested stories`, a guard criterion included. Work for one component that would exceed it becomes several Epics on the **same** `target:`, cut along story boundaries: each carries its own stories, the criteria those stories satisfy, the requirements they cover and its own `## Independent Test`; each is titled by the user value it delivers, never "part 1"; an `[AD#N]` interface keeps exactly one producing Epic, and a consumer in the same component comes after it. **Never bundle** several independently testable behaviours into one criterion or one story to stay under the limit — that is not a way under it. **Keep an Epic whole only where `scope` says so** — a Phase 2 plan revision naming it, with the operator's reason: write it whole and put that reason, in the operator's words, in its `kept_whole:` frontmatter; never write `kept_whole` on your own judgement.
```

(The step's remaining lines — "Order the Epics so that none depends on a later one …" — stay as they are.)

- [ ] **Step 4: Add the frontmatter field.** In the `epic.md` template, replace:

```
target: <one component id from the handoff's `components` — omit this line where the handoff carries none>
---
```

with:

```
target: <one component id from the handoff's `components` — omit this line where the handoff carries none>
kept_whole: <only where the scope keeps this Epic whole over size_limit: the operator's reason, in their words, double-quoted — omit this line otherwise>
---
```

- [ ] **Step 5: Add the size split to refinement mode.** In the paragraph beginning `In \`mode: both\`, also draft net-new Epics`, replace:

```
that is the focus Epic's own scope landing outside its one target: one net-new Epic per other component, each targeting it.
```

with:

```
that is the focus Epic's own scope landing outside its one target: one net-new Epic per other component, each targeting it. **A focus run that splits by size** (`/epics` Phase 6 step 4) — the focus Epic over `size_limit` — is the same shape on one component: the focus Epic keeps its key and the first slice, the one the others depend on, and each other slice is one net-new Epic on the same `target:`, cut and ordered as *Sizing / sequencing* says, `_coverage.md` updated to match.
```

- [ ] **Step 6: Confirm GREEN** — `python3 check.py <root> writer` → `writer: 9 passed, 0 failed`.

- [ ] **Step 7: Commit**

```bash
test "$(git branch --show-current)" = iv-gu/epic-sizing
git add plugins/product-workflows/agents/epic-writer.md
git commit -m "feat(epics): epic-writer sizes each Epic for one agent run, components first" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: `/epics` — the limit, the count-and-ask, the focus re-split, the report

**Files:**
- Modify: `plugins/product-workflows/commands/epics.md` (Phase 2 sizing bullet; Phase 6 step 1 handoff list; Phase 6 new step 4; Phase 7 reviewer brief; Phase 9 report template; Invariants)

**Interfaces:**
- Consumes: Task 1's writer behaviour (size split in `mode: both`, `kept_whole` from `scope`).
- Produces: `size_limit` in the writer handoff and the reviewer brief (with `not_splittable`); the `### Sizing` report block.

- [ ] **Step 1: Confirm RED** — `python3 check.py <root> cmd` and `… focus` → all failing.

- [ ] **Step 2: Rewrite the Phase 2 bullet.** Replace:

```
- Proposed Epic sizing/sequencing — prefer fewer, larger Epics where the PRD direction is validated; split only at a genuine risk / feedback-loop boundary; order so that
```

with:

```
- Proposed Epic sizing/sequencing — one Epic per component, each sized for one agent run: no Epic over 5 acceptance criteria or 4 suggested stories (`size_limit`, Phase 6), work over it split along its stories into Epics on the same component, never across components; a *Revise* may name work to keep whole and why, which the writer records as that Epic's `kept_whole` reason; order so that
```

- [ ] **Step 3: Put the limit in the handoff.** In Phase 6 step 1, replace:

```
and `docs_grounding` (the Phase 3.6 digest, or omit when OFF/EMPTY). Record its absolute path.
```

with:

```
`docs_grounding` (the Phase 3.6 digest, or omit when OFF/EMPTY), and `size_limit` (`{criteria: 5, stories: 4}` — this command's one statement of the limit: the writer, step 4's count and the reviewer read it from here, and calibrating it is this one edit). Record its absolute path.
```

- [ ] **Step 4: Add step 4.** After the Phase 6 line `   Also record \`coverage_file\` (the \`_coverage.md\` path) and \`clarifications_needed[]\` for Phases 6.1 and 7.`, insert:

````markdown

4. **Count every Epic against `size_limit`.** For each Epic this run wrote or refined, count the top-level `- ` bullets directly under its `## Acceptance criteria` and under its `## Suggested stories` — a count, never a judgement. An Epic is **over the limit** where either count exceeds `size_limit`'s, and **settled** where its frontmatter carries `kept_whole`. For each Epic over the limit and not settled:
   - **On a focus run, where the focus Epic's folder holds `specification.md`, `design.md` or `implementation.md`**, that file describes the whole Epic, so no split is offered: record it for Phase 9's `### Sizing` as over the limit and not splittable, naming the file, and ask nothing.
   - **Otherwise ask:**
     ```
     choices: ["Split it along its stories (Recommended)", "Keep it whole — give the reason", "Cancel"]
     ```
     **Split** re-dispatches `epic-writer` once for that Epic as step 2 dispatches it, with `mode: both`, `refinement_targets` set to that Epic, `scope` in-scope to it alone and the handoff noting that the split is by size: the writer keeps the Epic's key and its first slice — the one the others depend on — writes each other slice as a net-new Epic on the same `target:`, keyed as Phase 0 mints a key (`<PRD-KEY>-NN`, the next unused two-digit segment under this PRD), and updates `_coverage.md`. Count the result again; a slice still over the limit is asked about once more, without *Split*, and is never re-dispatched for it a second time:
     ```
     choices: ["Keep it whole — give the reason", "Cancel"]
     ```
     **Keep it whole** asks for the reason in plain text and writes it, in the operator's words and double-quoted, as that Epic's `kept_whole:` frontmatter. **Cancel** stops the run with the drafts written so far left on disk and uncommitted — nothing is handed off — and the final report names every Epic left over the limit. A typed answer is acted on as the option it expresses; anything else is asked again.

   **On a run that is not a focus run, count every Epic already under the PRD too** (`existing_epics`) — each is never re-drafted — and record each over the limit and not settled for Phase 9's `### Sizing`: with `/product-workflows:epics <EPIC-KEY>` where its folder holds none of `specification.md`, `design.md` and `implementation.md`, or naming the one that rules a split out. Record every Epic's counts, every split (from which key, into which keys) and every `kept_whole` reason for the same block.
````

- [ ] **Step 5: Pass the limit to the reviewer.** In the Phase 7 brief, insert immediately before the line beginning `  > repository_modules:`:

```
  > size_limit:           [`size_limit` from Phase 6, and `not_splittable`: the keys of the Epics this run counted whose folder holds specification.md, design.md or implementation.md]
```

- [ ] **Step 6: Add the report block.** In the Phase 9 report template, insert immediately before the line `### Epic review verdict`:

```markdown
### Sizing
- Limit: <criteria> acceptance criteria, <stories> suggested stories per Epic (`size_limit`)
- [<EPIC-KEY>] — <n> criteria, <m> stories — _then, where it applies:_ split from [<EPIC-KEY>] | kept whole: "<reason>" | over the limit, not splittable: <file> describes the whole Epic
- ...
- Existing Epics over the limit: [<EPIC-KEY>] (<n> criteria, <m> stories) — `/product-workflows:epics <EPIC-KEY>` | not splittable: <file> — _full PRD runs only; omit where none_

```

- [ ] **Step 7: Add the invariant.** Insert as a new line immediately after the Invariants line that begins `- ALWAYS treat linked Epics flagged \`refinement_candidate: true\``:

```markdown
- ALWAYS size every Epic this run writes or refines against `size_limit` (Phase 6 step 4) — components first, size second: a split never crosses a component and never merges Epics; NEVER write `kept_whole` from anything but the operator's words; NEVER split an Epic whose folder holds `specification.md`, `design.md` or `implementation.md`.
```

- [ ] **Step 8: Confirm GREEN** — `python3 check.py <root> cmd` → `cmd: 12 passed, 0 failed`; `… focus` → `focus: 3 passed, 0 failed`.

- [ ] **Step 9: Commit**

```bash
test "$(git branch --show-current)" = iv-gu/epic-sizing
git add plugins/product-workflows/commands/epics.md
git commit -m "feat(epics): /epics owns size_limit, counts every Epic and asks about misses; focus runs re-split before spec/design" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: `epic-reviewer` — the *Epic size* dimension

**Files:**
- Modify: `plugins/product-workflows/agents/epic-reviewer.md` (Inputs list; Review dimensions table)

**Interfaces:**
- Consumes: `size_limit` and `not_splittable` from the Phase 7 brief (Task 2 step 5).

- [ ] **Step 1: Confirm RED** — `python3 check.py <root> reviewer` → `reviewer: 0 passed, 4 failed`.

- [ ] **Step 2: Add the input.** Insert immediately before the Inputs bullet that begins `- **\`claims_file\`** (optional)`:

```markdown
- **`size_limit`** (optional) — `{criteria, stories}`, and `not_splittable`: the Epics whose folder holds `specification.md`, `design.md` or `implementation.md`. When omitted, the *Epic size* dimension is skipped (no-regression).
```

- [ ] **Step 3: Add the dimension.** Insert immediately before the table row that begins `| Claims falsification |`:

```markdown
| Epic size (conditional) | Only when the brief carries `size_limit`. Count each Epic's top-level `- ` bullets directly under `## Acceptance criteria` and `## Suggested stories` (a guard criterion counts). Over either limit — more than it, never at it — with no `kept_whole:` frontmatter and not in `not_splittable` → MAJOR: split it along its stories into Epics on the same target, or record why it stays whole. With `kept_whole` → no finding; note the reason. In `not_splittable` → report it, never a finding. A criterion or story that bundles several independently testable behaviours → MAJOR, whatever the count. Absent → skip. |
```

- [ ] **Step 4: Confirm GREEN** — `python3 check.py <root> reviewer` → `reviewer: 4 passed, 0 failed`.

- [ ] **Step 5: Commit**

```bash
test "$(git branch --show-current)" = iv-gu/epic-sizing
git add plugins/product-workflows/agents/epic-reviewer.md
git commit -m "feat(epics): epic-reviewer checks Epic size" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Docs, rules map, claim sweep, release

**Files:**
- Modify: `plugins/product-workflows/docs/commands/epics.md` (new `### Sizing` subsection under `## How it runs`, after `### Multi-component PRDs`)
- Modify: `.claude/rules/product-workflows.md` (the `/epics` map line)
- Modify: `plugins/product-workflows/CHANGELOG.md`, `plugins/product-workflows/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

- [ ] **Step 1: Count the claim before** — wrap-insensitive count of `fewer, larger` across `plugins/` (CHANGELOGs included), `README.md`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/`. Expected before Tasks 1–2: 2; now (after them): 0. Record both.

- [ ] **Step 2: Confirm RED** — `python3 check.py <root> docs` and `… release` → failing.

- [ ] **Step 3: Add the docs section.** Insert immediately before the line `## What it needs` in `docs/commands/epics.md`:

```markdown
### Sizing

**Components first, size second.** Every Epic still targets one component — one repository, or one module of a repository where the PRD's component set lists it — so a PRD whose work lands in two components gives at least two Epics, however small each is. Each Epic is then sized for one agent run: **at most 5 acceptance criteria and 4 suggested stories**. Work for one component that would exceed that becomes several Epics on the same component, cut along their stories, ordered so none waits on a later one, and each titled by what it delivers.

The writer splits as it drafts. The run then counts every Epic and asks about any still over the limit — *Split it along its stories* (recommended) or *Keep it whole*, with your reason recorded in the Epic as `kept_whole` — and the reviewer flags an oversized Epic with no recorded reason. You can also name work to keep whole when revising the plan. Re-running `/epics <EPIC-KEY>` offers the split only while the Epic has no `specification.md`, `design.md` or `implementation.md`; after that it reports the Epic as oversized instead. A full PRD run lists any existing Epic over the limit in its report's `### Sizing` block, with the command to split it where that is still allowed. Smaller Epics mean more `/design`, `/implement` and `/conformance` runs, each with a smaller change, its own review and its own pull request.
```

- [ ] **Step 4: Update the rules map line.** In `.claude/rules/product-workflows.md`, replace `writing (one target per Epic)` with:

```
writing (one target per Epic, each within `size_limit` — split along its stories, never across components) → [count each Epic: over the limit → split, or keep whole with `kept_whole`]
```

- [ ] **Step 5: Release.** Bump product-workflows `3.31.1` → `3.32.0` in `plugins/product-workflows/.claude-plugin/plugin.json` and in its `.claude-plugin/marketplace.json` entry. Add above the top section of `plugins/product-workflows/CHANGELOG.md`:

```markdown
## [3.32.0] — 2026-10-12

### Changed
- **`/epics` sizes every Epic for one agent run.** Epics still split by component first — one repository, or one listed module, per Epic — and each is then held to at most 5 acceptance criteria and 4 suggested stories. Work for one component over that becomes several Epics on the same component, cut along their stories and ordered so none waits on a later one; the writer used to prefer "fewer, larger Epics", which left one Epic per component however big. The run counts every Epic and asks about any still over the limit — split (recommended) or keep whole, with your reason recorded as `kept_whole` — and `epic-reviewer` flags an oversized Epic with no recorded reason, and a criterion or story that bundles several behaviours, as MAJOR. `/epics <EPIC-KEY>` re-splits an Epic only before its specification, design or implementation exists. The final report gains a `### Sizing` block. `/specify`, `/design`, `/implement` and `/conformance` are unchanged: they take smaller Epics one at a time.
```

- [ ] **Step 6: Confirm GREEN** — `python3 check.py <root>` → `all: 33 passed, 0 failed`; the claim count from Step 1 is 0.

- [ ] **Step 7: Run the gate chain** (one `&&` chain, read its own exit):

```bash
export PATH="/home/ihudak/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin:$PATH"
python3 scripts/validate-catalog.py && ./scripts/check-id-grammar.sh --root . && ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root . && node scripts/mermaid/check-mermaid.mjs --root .; echo "EXIT=$?"
```

Expected: `EXIT=0`.

- [ ] **Step 8: Commit**

```bash
test "$(git branch --show-current)" = iv-gu/epic-sizing
git add plugins/product-workflows/docs/commands/epics.md .claude/rules/product-workflows.md plugins/product-workflows/CHANGELOG.md plugins/product-workflows/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "docs(epics): sizing section, rules map, product-workflows 3.32.0" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Whole-branch review

- [ ] **Step 1:** Dispatch an Opus reviewer over `git diff main...iv-gu/epic-sizing` with the spec, this plan's Review Focus verbatim, and the ledger's `Ruling:` lines.
- [ ] **Step 2:** Fix every finding above Minor test-first (a new failing assertion in `check.py`, then the fix), re-run the gate chain, commit, and re-review until no finding above Minor remains. Minors go to the ledger as deferred.
- [ ] **Step 3:** Merge to `main` and push only with the operator's explicit consent; then `claude plugin update product-workflows@shipwright` and a restart.

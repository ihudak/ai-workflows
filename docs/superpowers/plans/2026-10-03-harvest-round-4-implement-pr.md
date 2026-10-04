# Upstream harvest round 4 — Round 3: `/implement` looks before asking, and the code pull-request body — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port backlog items 13 (`/implement` looks before asking, and re-classifies upward after exploring and mid-implementation) and 15 (the code pull-request body: Summary, Evidence, Merge danger, Review, and the repository's own template) to this repository, the internal edition and the Copilot edition.

**Architecture:** Prose edits to one command, one agent, one reference, two callers and two docs pages per edition, applied only through `wsub.py` (a whitespace-insensitive replace) from the edit files in Appendix B, so the text that lands is the text this plan carries. Item 13 lives in `/implement` (Phases 1, 2A, 2B, 3A, 3B, 4/4.6, 5 and the invariants) and in `risk-planner`'s new `Work so far` input; item 15 lives in `code-handoff` §2.7, which owns the body's definition, and in the three callers' `body_facts`, which supply facts and restate no rule (`code-handoff` §4 obligation 4). The other two editions take the same edit files through `gen.py`'s dialect substitution, plus `ed-implement.txt`, which also fixes three defects found in their `/implement` while planning (spec § Amended during planning). Every edit file was dry-run against all three trees and the whole round applied to throwaway copies before this plan was written: gates `EXIT=0` and `check.py` green in all three.

**Tech Stack:** Markdown prose executed by agents; git; bash; python3 (helpers, gates); node (mermaid gate).

**Spec:** `docs/superpowers/specs/2026-10-03-harvest-round-4-implement-pr-design.md` (including § Amended during planning)

## Global Constraints

- **Never name the internal edition in this repository.** Check 19 rejects, anywhere in the work tree, the pattern `EDITION_FORBIDDEN_B64` decodes to in `scripts/check-docs.sh` — the internal edition's short name as a bare word, its repository names, and the organisation's name. Write "the internal edition" and `$IE`.
- **Prose is executed.** Every sentence added must be true of what the run does; a false one is a defect, not a typo.
- **Apply edits only with `wsub.py` from Appendix B's files.** A fix found later is a new edit block or a hand edit recorded as a `Ruling:` in the ledger, never an unrecorded change. `wsub.py` aborts with nothing written when a block's match count is wrong — that is a stop-and-look, never a reason to loosen the block.
- **Match the file's wrapping.** `/implement`'s Phase 4 handoff-file paragraph is hard-wrapped and its edit block keeps that wrap; every other passage this round edits is one long line.
- **Copilot dialect.** In `$CE`, skills are named `implement:`, `vuln:`, `upgrade:` (never `/implement`), shared references are `~/.copilot/installed-plugins/ihudak-copilot-plugins/dev-workflows/skills/_shared/<name>.md`, `${CLAUDE_PLUGIN_ROOT}` never appears, and a `choices` rule ends in `"Other… (describe)"`. `gen.py` makes the substitutions; nothing else does.
- **Character limits.** Each `.github/instructions/*.md` in `$CE` stays under 20,000 characters; this round does not touch them (19,998 and 19,846 before and after). `check.py` asserts both.
- **Git discipline in this repository:** never `git checkout`/`switch` in `/workspace/ai-workflows` (work in `$AW`); run `git branch --show-current` immediately before every commit; never bare `git stash`; stage `.claude/rules/*` with `git add -f` (none is edited this round).
- **Commit trailers:** `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>` and `Claude-Session: https://claude.ai/code/session_01Au7DfL9asXxZqvnrH2znsY`.
- **Do not edit** `references/specification-format.md` (frozen).
- **Every `CHANGELOG.md` section is dated** (`2026-10-03`; re-date to the merge day if the merge slips) before it reaches `main` — check 18.
- **Zero known bugs:** every review finding — minors and nits included — is fixed before merge, and each edition is reviewed until a round returns zero findings.

## Review Focus

1. **A `MODERATE` direct-mode run whose Phase 2A exploration lists six non-test files** — the class is raised before any file is written, `summary_file` carries the exploration to Phase 2B, and nothing explores twice. The old text planned and implemented it as `MODERATE`, with no review gate. Pinned by Task 1 Step 5's trace A.
2. **A `MODERATE` run that meets a migration in Phase 3A, and a user who cancels the re-plan** — the Cancel stops through Phase 4.6 with `clean_finish: false`, so the work is committed and any pull request is a draft carrying the banner. The old text shipped the run unreviewed. Pinned by trace B.
3. **A user who accepts `risk-planner`'s down-classification at the re-plan** — Phase 3A resumes on the plan already approved, Phase 2A's re-test does not run again, and a second §1.1 trigger is asked about, never re-planned. Pinned by trace C.
4. **A repository with `.github/pull_request_template.md` holding a checklist and a "How was this tested?" section** — the body is that template filled: Evidence in the testing section, a checkbox ticked only where the run can show it, Merge danger appended after the template, the banner first on a run that did not finish clean. Pinned by Task 2 Step 5's trace D.
5. **A repository whose `.github/PULL_REQUEST_TEMPLATE/` holds two templates** — none is applied, the four sections are written as on a repository with no template, and the body's last line names the directory. Pinned by trace E.

---

### Task 0: Variables, helpers, branches

**Files:**
- Create (scratch, never committed): `$S/{wsub.py,count.py,gen.py,check.py,apply.sh,gates.sh,release.py}`, `$S/edits/*`, `$S/cl/*`

**Interfaces:**
- Produces: `$AW`, `$IE`, `$CE`, `$S`, `$PLAN`; `wsub.py TARGET EDITFILE [--dry]` (exit 1, nothing written, on any count mismatch); `count.py ROOT TEXT [--no-changelog]`; `gen.py aw|ie|ce TEMPLATE` (dialect substitution, fails on a leftover `{{…}}`); `check.py aw|ie|ce ROOT` (prints each failing check as `FAIL …`, then `<ed>: N passed, M failed`; exit 0 only when all pass); `apply.sh aw|ie|ce ROOT [--dry]` (every edit for one edition, in order); `gates.sh aw|ie|ce ROOT` (the edition's CI chain); `release.py aw|ie|ce ROOT` (version + changelog section).

- [ ] **Step 1: Set the variables** (every later task assumes them)

```bash
AW=/workspace/.worktrees/ai-workflows-harvest-r4-impl-pr   # this repository's worktree, branch iv-gu/harvest-r4-impl-pr
IE=<the internal edition's checkout root under /workspace>  # not written here: check 19
CE=/workspace/ihudak-copilot-plugins
S=/tmp/claude-502/-workspace-ai-workflows/d7e59186-271d-4a83-a94b-9e776fafee25/scratchpad/r6   # any scratch dir outside every repo
PLAN=$AW/docs/superpowers/plans/2026-10-03-harvest-round-4-implement-pr.md
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
Expected: `22 files`.

- [ ] **Step 3: Dry-run every edit against every edition** — proves the trees have not moved since the plan was written

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4-impl-pr && test -z "$(git status --porcelain)" && echo CLEAN
for e in "aw $AW" "ie $IE" "ce $CE"; do set -- $e; "$S/apply.sh" $1 $2 --dry | grep -c '^checked'; done
```
Expected: `CLEAN`, then `9` three times (every block `checked`, none `ABORT`).

- [ ] **Step 4: RED — run the checks on all three unchanged trees**

```bash
python3 "$S/check.py" aw "$AW" | tail -1; python3 "$S/check.py" ie "$IE" | tail -1; python3 "$S/check.py" ce "$CE" | tail -1
```
Expected: `aw: 0 passed, 30 failed`, `ie: 0 passed, 34 failed`, `ce: 2 passed, 31 failed` (the two that pass are the Copilot length limits, which hold before and after). Every later task in this edition is measured by `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'`, which reads **30** here.

- [ ] **Step 5: Branch the other two editions** (their own checkouts; no shared-tree rule binds them)

```bash
for r in "$IE" "$CE"; do test -z "$(git -C "$r" status --porcelain)" && git -C "$r" switch -c iv-gu/harvest-r4-impl-pr && git -C "$r" branch --show-current; done
```
Expected: `iv-gu/harvest-r4-impl-pr` twice.

---

### Task 1: Item 13 — `/implement` looks before asking and re-classifies upward (this edition)

**Files:**
- Modify: `plugins/dev-workflows/commands/implement.md` (Phase 1; Phase 2A's exploration; Phase 2B's opening, exploration, brief and acceptance sentence; Phase 3A step 5; Phase 3B steps 4 and 6; Phase 3.5 step 3; Phase 4's handoff files; Phase 4.6's `"Every run"` and *Two Cancels* paragraphs; Phase 5's `### Classification`; the invariants)
- Modify: `plugins/dev-workflows/agents/risk-planner.md` (`## Inputs`; the mutation rule)
- Modify: `plugins/dev-workflows/docs/commands/implement.md` (the diagram and its key)

**Interfaces:**
- Produces: the rule **Look, then ask; never guess**; a **decision** (the evidence leaves it open and its answer changes what the user would notice in the result); `summary_file` written by Phase 2A; the announcements `Re-classified upward after exploration` and `Re-classified upward during implementation`; the **re-plan** (Phase 3A step 5), `partial_diff_file`, and `risk-planner`'s **`Work so far`** input. Task 2 does not consume them.

- [ ] **Step 1: RED** — `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'` → `30`.
- [ ] **Step 2: Generate this edition's templates and dry-run the four edits**

```bash
cd "$AW" && for t in impl risk-planner; do python3 "$S/gen.py" aw "$S/edits/$t.tpl" > "$S/gen/aw-$t.txt"; done && for x in "plugins/dev-workflows/commands/implement.md $S/gen/aw-impl.txt" "plugins/dev-workflows/commands/implement.md $S/edits/aw-implement.txt" "plugins/dev-workflows/agents/risk-planner.md $S/gen/aw-risk-planner.txt" "plugins/dev-workflows/docs/commands/implement.md $S/edits/awie-doc-implement.txt"; do set -- $x; python3 "$S/wsub.py" "$1" "$2" --dry; done
```
Expected: `checked 12 block(s)`, `checked 4 block(s)`, `checked 2 block(s)`, `checked 4 block(s)`.

- [ ] **Step 3: Apply** — the same four commands without `--dry`, in that order. Expected: `applied 12`, `applied 4`, `applied 2`, `applied 4`.
- [ ] **Step 4: GREEN for this task** — `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'` → `12` (the eleven item-15 checks and the changelog's).
- [ ] **Step 5: Trace the three runs (Review Focus 1–3)** through `/implement` as edited, citing the sentence that decides each step, and ledger each as `Task 1: trace <A|B|C>: old → <outcome>; new → <outcome>`:
  - **A** — direct mode, one repository, Phase 1.5 says `MODERATE`; Phase 2A's exploration lists six non-test files. Old: Phase 2A plan, Phase 3A, no review. New: Phase 2A's *Write the exploration down, then re-test the class* raises it to `SIGNIFICANT`, announces it, writes `summary_file`, and Phase 2B's exploration paragraph skips the subagent.
  - **B** — `MODERATE` run in Phase 3A meets a schema migration its plan did not name; the user picks **Cancel** at Phase 2B's plan approval. Old: step 5 asked a question at most; the run finished `MODERATE` and unreviewed. New: step 5's re-plan, then its Cancel → Phase 4.6's `"Every run"` list (the new member) → commit, `clean_finish: false` through the row's first condition, draft pull request with the banner.
  - **C** — as B, but `risk-planner` returns `### Re-classification` and the user accepts; a second trigger appears later. New: Phase 3A resumes on the approved plan (step 5's *Accept* clause); the second trigger is asked under step 5's **A decision** arm (*"A §1.1 trigger met after this run's one re-plan is asked here too"*), never re-planned.
- [ ] **Step 6: Read-through** — read Phase 4.6's `"Every run"` and *Two Cancels* paragraphs and the `clean_finish` row together: the three re-plan Cancels are members, reach `false` through the row's first condition, and the repro prompt's ordinary-path Cancel is still outside the set. Read Phase 2B from its first line with trace B's state in mind: its opening pointer sends the reader to Phase 3A step 5 before any arm.
- [ ] **Step 7: Commit**

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4-impl-pr && git add plugins/dev-workflows/commands/implement.md plugins/dev-workflows/agents/risk-planner.md plugins/dev-workflows/docs/commands/implement.md && git commit -q -F - <<'MSG' && git log --oneline -1
feat(dev-workflows): /implement looks before asking, and re-classifies upward after exploring and mid-implementation

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Au7DfL9asXxZqvnrH2znsY
MSG
```

---

### Task 2: Item 15 — the code pull-request body (this edition)

**Files:**
- Modify: `plugins/dev-workflows/references/code-handoff.md` (§2.7's body; §2.11's `body_facts` row)
- Modify: `plugins/dev-workflows/commands/implement.md` (Phase 4.6 `body_facts`)
- Modify: `plugins/dev-workflows/commands/vuln.md` (Step 3.9 `body_facts`)
- Modify: `plugins/dev-workflows/commands/upgrade.md` (step 7.5 `body_facts`)
- Modify: `plugins/dev-workflows/docs/reference/references.md` (the `code-handoff.md` entry)

**Interfaces:**
- Produces: §2.7's four sections `## Summary`, `## Evidence`, `## Merge danger`, `## Review`; the **door** (one-way / two-way; one-way where the run cannot tell) and the **blast radius**; the template ladder (three rungs). The callers' `body_facts` name "§2.7's four sections".

- [ ] **Step 1: RED** — `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'` → `12`.
- [ ] **Step 2: Generate, then dry-run the five edits**

```bash
cd "$AW" && for t in impl-body vuln upgrade; do python3 "$S/gen.py" aw "$S/edits/$t.tpl" > "$S/gen/aw-$t.txt"; done && for x in "plugins/dev-workflows/references/code-handoff.md $S/edits/all-code-handoff.txt" "plugins/dev-workflows/commands/implement.md $S/gen/aw-impl-body.txt" "plugins/dev-workflows/commands/vuln.md $S/gen/aw-vuln.txt" "plugins/dev-workflows/commands/upgrade.md $S/gen/aw-upgrade.txt" "plugins/dev-workflows/docs/reference/references.md $S/edits/aw-doc-references.txt"; do set -- $x; python3 "$S/wsub.py" "$1" "$2" --dry; done
```
Expected: `checked 2 block(s)`, then `checked 1 block(s)` four times.

- [ ] **Step 3: Apply** — the same five without `--dry`. Expected: `applied 2`, then `applied 1` four times.
- [ ] **Step 4: GREEN for this task** — `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'` → `1` (the changelog section, which Task 3 writes).
- [ ] **Step 5: Trace three runs (Review Focus 4–5, and the spec's `/vuln` walk-through)** through §2.7 as edited and ledger each as `Task 2: trace <D|E|F>: <body's shape, section by section>`:
  - **D** — `.github/pull_request_template.md` with `## Description`, `## How was this tested?` and a checklist (`- [ ] Tests added`, `- [ ] Docs updated`), on an `/implement` run that added tests and changed no docs, `clean_finish: false`. Expected: banner first; Summary in Description; Evidence in the testing section; `Tests added` ticked, `Docs updated` left unticked and kept; Merge danger and Review appended after the template, in that order.
  - **E** — `.github/PULL_REQUEST_TEMPLATE/` with `bug.md` and `feature.md`, no single-file template. Expected: rung 2 stops the ladder with no template; the four sections in order; the last line names `.github/PULL_REQUEST_TEMPLATE/`.
  - **F** — a `/vuln` run, `MODERATE`, on a repository with no template; one CVE fixed by a patch bump, tests green. Expected: no rung matches; Summary names the CVE, the version change and the manifest and lock files; Evidence pairs the installed version inside the vulnerable range with the applied one outside it, beside the test counts; Merge danger is two-way unless Step 3.9's facts show the new version changes something persisted or published, with the blast radius naming what in the repository uses the library; Review reads `N/A` for a review the CVE did not go through.
- [ ] **Step 6: Read-through** — §2.7 against §2.9 (the banner stays the first line, template or not) and §3.2 (the fallback names the same file); each caller's `body_facts` supplies facts for all four sections and restates no part of §2.7's door definition (§4 obligation 4).
- [ ] **Step 7: Commit**

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4-impl-pr && git add plugins/dev-workflows/references/code-handoff.md plugins/dev-workflows/commands/implement.md plugins/dev-workflows/commands/vuln.md plugins/dev-workflows/commands/upgrade.md plugins/dev-workflows/docs/reference/references.md && git commit -q -F - <<'MSG' && git log --oneline -1
feat(dev-workflows): the code pull-request body — Summary, Evidence, Merge danger, Review, and the repository's own template

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Au7DfL9asXxZqvnrH2znsY
MSG
```

---

### Task 3: Release this edition — version, changelog, gates

- [ ] **Step 1: Bump and write the changelog** — `python3 "$S/release.py" aw "$AW"`. Expected: `dev-workflows 4.7.0 4.7.0`.
- [ ] **Step 2: GREEN** — `python3 "$S/check.py" aw "$AW" | tail -1` → `aw: 30 passed, 0 failed`.
- [ ] **Step 3: Check the changelog entry against the diff it describes** — `git -C "$AW" diff origin/main...HEAD --stat` beside the new `CHANGELOG.md` section; every claim names a change the diff makes.
- [ ] **Step 4: Gates** — `"$S/gates.sh" aw "$AW"; echo "EXIT=$?"` → `EXIT=0` (timeout at least 300 s). A failure is fixed and the chain re-run from the start.
- [ ] **Step 5: Commit** — `.claude-plugin/marketplace.json`, `plugins/dev-workflows/.claude-plugin/plugin.json`, `plugins/dev-workflows/CHANGELOG.md`, message `chore(release): dev-workflows 4.7.0`, branch verified first.

---

### Task 4: Whole-branch review of this edition, to zero findings

- [ ] **Step 1: Dispatch a fresh reviewer** (Opus, general-purpose, in the background) with: the spec path (including § Amended during planning), the plan path, `git -C "$AW" diff origin/main...HEAD`, the ledger's `Ruling:` lines, and this brief — *"Review this branch as a whole. The prose is executed by agents in order, so a false or ambiguous sentence is a defect. Check every changed sentence against what the run does, every pointer (`this`, `it`, `above`, an ordinal, a section number) against what it now points at, each claim whose extent changed against every copy of it (changelog, docs page, rules summary), and the spec's decisions against the text. Report each finding with file:line, severity, and the failure it causes; list what you declined to judge."*
- [ ] **Step 2: Triage each finding** at the location it names; fix every confirmed one, minors and nits included (an edit block or a ledgered hand edit); record any dismissal with a reason that disposes of that finding's own claim.
- [ ] **Step 3: Re-read each fix where it lands** — the pronouns, the ordinals, a "which" after a list, a dropped noun, "among them" mixing classes — then re-run `check.py` (`aw: 30 passed, 0 failed`) and the gate chain (`EXIT=0`); commit the wave as `fix: review round N — …`, branch verified first.
- [ ] **Step 4: Repeat** Steps 1–3 until a round returns zero findings. Before writing a new rule to close a finding, look for a principle the authority already states.

---

### Task 5: Port to the internal edition

**Files:** `plugins/dev-workflows/{references/code-repo-handoff.md,commands/implement.md,commands/vuln.md,commands/upgrade.md,agents/risk-planner.md,docs/commands/implement.md,docs/reference/references.md}`, `plugins/dev-workflows/{.claude-plugin/plugin.json,CHANGELOG.md}`, `.claude-plugin/marketplace.json`.

- [ ] **Step 1: Carry this edition's review fixes over first.** Every fix Task 4 made through a shared or templated edit file (`all-*.txt`, `*.tpl`, `awie-*.txt`, `ed-*.txt`) is already in `$S/edits`; a fix made only through an `aw-*` file gets its counterpart in `ed-implement.txt` or `ed-doc-references.txt` where the passage exists there. Then `"$S/apply.sh" ie "$IE" --dry | grep -c '^checked'` → `9`.
- [ ] **Step 2: RED** — `python3 "$S/check.py" ie "$IE" | tail -1` → `ie: 0 passed, 34 failed`.
- [ ] **Step 3: Apply** — `"$S/apply.sh" ie "$IE" | grep -c '^applied'` → `9`.
- [ ] **Step 4: GREEN before the release** — `python3 "$S/check.py" ie "$IE" | tail -1` → `ie: 33 passed, 1 failed`, the one being the changelog section Step 6 writes.
- [ ] **Step 5: Sweep** — by subject, over `$IE`'s `plugins/`, `README.md`, `CLAUDE.md` and `.claude/rules/`: the retired strings of `check.py` and any copy of the Phase 4.6 list, the Phase 1 rule, the class's timing and the body's contents; each hit read in place.
- [ ] **Step 6: Release** — `python3 "$S/release.py" ie "$IE"` → `dev-workflows 2.68.0 2.68.0`; `check.py` → `ie: 34 passed, 0 failed`. Gates: `"$S/gates.sh" ie "$IE"; echo "EXIT=$?"` → `EXIT=0`.
- [ ] **Step 7: Commit** (branch verified) — `git -C "$IE" add -A plugins .claude-plugin && git -C "$IE" commit` with `feat(dev-workflows): /implement looks before asking and re-classifies upward; the code pull-request body (dev-workflows 2.68.0)` and the trailers. Expected `git status --short` beforehand lists exactly this task's **Files**, all `M`.
- [ ] **Step 8: Review to zero** — as Task 4, against `git -C "$IE" diff main...HEAD`, with the scope read as this edition's `plugins/`, `README.md`, `CLAUDE.md` and `.claude/rules/`, plus: *"Compare each changed passage with this repository's counterpart; a difference beyond dialect is a finding unless the spec records it."* Run in parallel with Task 6 Step 8. **After every wave that changes only the other two editions' files, rebuild this edition from `origin/main` with `apply.sh aw` + `release.py aw` in a scratch clone and confirm it is byte-identical to `$AW`** (`git -C <clone> diff --quiet "$AW"`-style comparison of each changed file), so a shared edit file never drifts from what this edition shipped:

```bash
B=$S/byte-aw; rm -rf "$B" && git clone -q --no-hardlinks /workspace/ai-workflows "$B" && "$S/apply.sh" aw "$B" >/dev/null && python3 "$S/release.py" aw "$B" >/dev/null && for f in $(git -C "$AW" diff --name-only origin/main...HEAD | grep -v '^docs/superpowers/'); do cmp -s "$AW/$f" "$B/$f" || echo "DIFF $f"; done; echo done
```
Expected: `done` alone. A `DIFF` line means an edit file changed under this edition: rebuild this edition's file from it, or restore the edit file, before the next review.

---

### Task 6: Port to the Copilot edition

**Files:** `dev-workflows/{skills/_shared/code-repo-handoff.md,skills/implement/SKILL.md,skills/vuln/SKILL.md,skills/upgrade/SKILL.md,agents/risk-planner.md,docs/skills/implement.md,docs/reference/references.md,.plugin/plugin.json,CHANGELOG.md}`, `.github/plugin/marketplace.json`.

- [ ] **Step 1: Carry the review fixes over** (as Task 5 Step 1, plus any Task 5 fixes), then `"$S/apply.sh" ce "$CE" --dry | grep -c '^checked'` → `9`.
- [ ] **Step 2: RED** — `python3 "$S/check.py" ce "$CE" | tail -1` → `ce: 2 passed, 31 failed`.
- [ ] **Step 3: Apply** — `"$S/apply.sh" ce "$CE" | grep -c '^applied'` → `9`.
- [ ] **Step 4: GREEN before the release** — `python3 "$S/check.py" ce "$CE" | tail -1` → `ce: 32 passed, 1 failed`, the one being the changelog section Step 6 writes.
- [ ] **Step 5: Dialect sweep** — `grep -n -E '/implement|/vuln|/upgrade|CLAUDE_PLUGIN_ROOT|workflows-core:|2–4 options' $(git -C "$CE" diff --name-only | grep -v CHANGELOG | sed "s#^#$CE/#")` returns nothing on a changed line a Copilot reader would act on wrongly.
- [ ] **Step 6: Release** — `python3 "$S/release.py" ce "$CE"` → `dev-workflows 2.37.0 2.37.0`; `check.py` → `ce: 33 passed, 0 failed`. Gates: `"$S/gates.sh" ce "$CE"; echo "EXIT=$?"` → `EXIT=0`.
- [ ] **Step 7: Commit** — as Task 5 Step 7, with `git add -A dev-workflows .github` and `(dev-workflows 2.37.0)`.
- [ ] **Step 8: Review to zero** — as Task 5 Step 8, against `git -C "$CE" diff main...HEAD`, the dialect being `implement:`-style names, `~/.copilot/…/_shared/` paths, the review tier, and the trailing `"Other… (describe)"` arm.

---

### Task 7: Harvest record, merge, push, clean up

- [ ] **Step 1: Merge and push the other two editions** — in each, from its own checkout: `git switch main && git merge --no-ff iv-gu/harvest-r4-impl-pr -m "Merge iv-gu/harvest-r4-impl-pr: upstream harvest round 4, Round 3 — /implement looks before asking; the code pull-request body (dev-workflows <version>)"`, push to every remote `git remote` lists (the internal edition's protected-branch bypass notice is expected), then `git branch -d iv-gu/harvest-r4-impl-pr`. Record each merge commit.
- [ ] **Step 2: Write the harvest record** in `$AW/docs/superpowers/harvest/NEXT.md` (never naming the internal edition): the § *Harvest round 4* heading reads *Rounds 1–3 SHIPPED*; a **Round 3** block with each edition's merge commit and version, items 13 and 15 as shipped, the three defects § Amended during planning found, and the review-round counts with the findings worth keeping; backlog items 13 and 15 marked `— shipped in Round 3`; two follow-up candidates added to the backlog — *look before asking* for the other commands that carry "Ask, don't guess", and the template rule for `phase-handoff` and `finish-and-handoff`'s bodies.
- [ ] **Step 3: Commit, gate, merge, push** — commit the record (`docs(harvest): record round 4 — Round 3 shipped in three editions`), re-run `"$S/gates.sh" aw "$AW"` → `EXIT=0` and `check.py aw` → `aw: 30 passed, 0 failed`; then from `/workspace/ai-workflows`, which stands on `main`: `git pull --ff-only && git merge --no-ff iv-gu/harvest-r4-impl-pr` (branch verified), push, and `gh run watch` the CI run to success.
- [ ] **Step 4: Clean up** — copy `$AW/.superpowers/sdd/<plan>/progress.md` out first; then `git -C /workspace/ai-workflows worktree remove "$AW" && git -C /workspace/ai-workflows branch -d iv-gu/harvest-r4-impl-pr`; confirm each repository: on `main`, clean, `main` equal to every remote's `main`, no `iv-gu/harvest-r4-impl-pr` branch left.
- [ ] **Step 5: Installed copies** (the operator's step) — `claude plugin update dev-workflows@shipwright`, then restart; `copilot plugin update dev-workflows@ihudak-copilot-plugins`; the internal edition wherever it is installed.

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
CE_SHARED = '~/.copilot/installed-plugins/ihudak-copilot-plugins/dev-workflows/skills/_shared/'
V = {
    'aw': {'IMPL': '/implement', 'FT': '`workflows-core:finding-triage`', 'QIMPL': '/dev-workflows:implement', 'REVIEW': 'Opus review',
           'CHOICES': '2–4 options; the harness supplies the free-text escape',
           'MR': '`workflows-core:model-routing/classification`',
           'REPODOCS': '`CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` and `README.md`',
           'CMR': '`${CLAUDE_PLUGIN_ROOT}/references/context-management.md`', 'READ': 'Read',
           'CH': '`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md`', 'OTHER': '', 'NOCOMMIT': ' (unless `--no-commit`)', 'NOCOMMITQ': ' (unless --no-commit)'},
    'ie': {'IMPL': '/implement', 'FT': '`${CLAUDE_PLUGIN_ROOT}/references/finding-triage.md`', 'QIMPL': '/dev-workflows:implement', 'REVIEW': 'Opus review',
           'CHOICES': '2–4 options; the harness supplies the free-text escape',
           'MR': '`${CLAUDE_PLUGIN_ROOT}/references/model-routing/classification.md`',
           'REPODOCS': '`CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` and `README.md`',
           'CMR': '`${CLAUDE_PLUGIN_ROOT}/references/context-management.md`', 'READ': 'Read',
           'CH': '`${CLAUDE_PLUGIN_ROOT}/references/code-repo-handoff.md`', 'OTHER': '', 'NOCOMMIT': '', 'NOCOMMITQ': ''},
    'ce': {'IMPL': 'implement:', 'FT': '`' + CE_SHARED + 'finding-triage.md`', 'QIMPL': 'implement:', 'REVIEW': 'review-tier review',
           'CHOICES': 'last: `"Other… (describe)"`',
           'MR': '`' + CE_SHARED + 'model-routing.md`',
           'REPODOCS': '`AGENTS.md`, `.github/copilot-instructions.md`, `CONTRIBUTING.md` and `README.md`',
           'CMR': '`' + CE_SHARED + 'context-management.md`', 'READ': 'view',
           'CH': '`' + CE_SHARED + 'code-repo-handoff.md`', 'OTHER': ', "Other… (describe)"', 'NOCOMMIT': '', 'NOCOMMITQ': ''},
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
"""check.py EDITION ROOT — Round 3 expectations: retired strings at 0, each new rule's name at its count,
counted wrap-insensitively (whitespace collapsed on both sides); the Copilot instruction files under 20,000 characters."""
import re, sys
ed, root = sys.argv[1], sys.argv[2]
P = {'aw': dict(IMPL='plugins/dev-workflows/commands/implement.md', CH='plugins/dev-workflows/references/code-handoff.md',
                RP='plugins/dev-workflows/agents/risk-planner.md', VULN='plugins/dev-workflows/commands/vuln.md',
                UPG='plugins/dev-workflows/commands/upgrade.md', DOC='plugins/dev-workflows/docs/commands/implement.md',
                REFS='plugins/dev-workflows/docs/reference/references.md', CL='plugins/dev-workflows/CHANGELOG.md',
                MRD='plugins/dev-workflows/docs/reference/model-routing.md'),
     'ie': dict(IMPL='plugins/dev-workflows/commands/implement.md', CH='plugins/dev-workflows/references/code-repo-handoff.md',
                RP='plugins/dev-workflows/agents/risk-planner.md', VULN='plugins/dev-workflows/commands/vuln.md',
                UPG='plugins/dev-workflows/commands/upgrade.md', DOC='plugins/dev-workflows/docs/commands/implement.md',
                REFS='plugins/dev-workflows/docs/reference/references.md', CL='plugins/dev-workflows/CHANGELOG.md',
                MRD='plugins/dev-workflows/docs/reference/model-routing.md'),
     'ce': dict(IMPL='dev-workflows/skills/implement/SKILL.md', CH='dev-workflows/skills/_shared/code-repo-handoff.md',
                RP='dev-workflows/agents/risk-planner.md', VULN='dev-workflows/skills/vuln/SKILL.md',
                UPG='dev-workflows/skills/upgrade/SKILL.md', DOC='dev-workflows/docs/skills/implement.md',
                REFS='dev-workflows/docs/reference/references.md', CL='dev-workflows/CHANGELOG.md',
                MRD='dev-workflows/docs/reference/model-routing.md')}[ed]
VER = {'aw': '4.7.0', 'ie': '2.68.0', 'ce': '2.37.0'}[ed]
col = lambda s: re.sub(r'\s+', ' ', s)
txt = {k: col(open(f'{root}/{v}').read()) for k, v in P.items()}
ok = bad = 0
def cnt(key, s, want):
    global ok, bad
    n = txt[key].count(col(s))
    if n == want: ok += 1
    else:
        bad += 1; print(f'FAIL {key} {P[key]}: {s[:70]!r} count {n}, want {want}')
# retired
for s in ["Ask, don't guess. This rule is absolute.", 'NEVER make assumptions that could have been asked',
          'If a **new ambiguity** emerges', 'If **nothing** is ambiguous']:
    cnt('IMPL', s, 0)
cnt('CH', 'It contains what the run produced', 0)
cnt('RP', 'approved any action', 0)
if ed in ('aw', 'ie'):
    cnt('DOC', '(set at classification)', 0); cnt('DOC', 'it is the classification Phase 1.5 already made', 0)
    cnt('DOC', '(as classified, or raised)', 1)
if ed == 'aw':
    cnt('IMPL', 'where Phase 2A never ran', 0)
else:
    for s in ['restore to pre-impl state" arm', 'the Cancel arms of the framework and repro prompts',
              'as discovered in Phase 2A exploration', 'once Phase 2B has read it and no later phase cites it']:
        cnt('IMPL', s, 0)
    cnt('IMPL', '**A stop before Pre-Phase 3 creates the branch is outside that set**', 1)
# new
for s, n in [('Look, then ask; never guess.', 1), ('Re-classified upward at planning', 1),
             ('Re-classified upward during implementation', 1), ('partial_diff_file', 4), ('Work so far', 3),
             ("§2.7's four sections", 1), ("when Phase 3A step 5's re-plan reached it", 1),
             ('**Write the exploration down**', 1), ('**Re-test the class against the plan**', 1),
             ('Settled by the run', 3), ('Stop here — the work so far is committed through Phase 4.6', 1),
             ("the **Stop** arm of that step's question on a trigger met after the re-plan", 1)]:
    cnt('IMPL', s, n)
cnt('RP', '**`Work so far`** (optional)', 1); cnt('RP', '**`Settled by the run`** (optional)', 1)
cnt('VULN', "§2.7's four sections", 1); cnt('VULN', "- Body: Step 3.9's `body_facts`", 1); cnt('UPG', "§2.7's four sections", 1)
for s, n in [('`## Merge danger`', 1), ('pull_request_template.md', 3), ('PULL_REQUEST_TEMPLATE/', 3),
             ('.gitlab/merge_request_templates/Default.md', 1), ("what §2.7 renders into the body file's four sections", 1),
             ('**The repository\'s own template wins.**', 1)]:
    cnt('CH', s, n)
cnt('DOC', 're-plan approved', 1)
cnt('MRD', 'that first meets, while implementing, a trigger its plan did not name', 1)
cnt('CH', 'paste it in place of any description the web UI prefills', 1)
cnt('REFS', 'a Merge danger call', 1)
cnt('CL', f'## [{VER}] — 2026-10-04', 1)
cnt('IMPL', 'change code only in the repository Pre-Phase 3 branched', 2); cnt('IMPL', '**No other code repository is written.**', 1)
cnt('IMPL', 'git add -N :/', 0); cnt('IMPL', 'git add -N --ignore-removal :/ && git -c diff.relative=false diff --no-ext-diff --no-color "$(git rev-parse -q --verify HEAD || git hash-object -t tree /dev/null)"', 8); cnt('IMPL', 'git add -N .', 0); cnt('IMPL', 'wrote into but never branched', 0); cnt('IMPL', '**A run that wrote into a repo it never branched.**', 0)
if ed == 'aw':
    _f = col(open(f'{root}/plugins/workflows-core/references/implementation-format.md').read())
    if 'a repository it edited and never branched' in _f: bad += 1; print('FAIL implementation-format still names an unbranched repository')
    else: ok += 1
    _c = col(open(f'{root}/plugins/workflows-core/CHANGELOG.md').read())
    if '## [1.11.1] — 2026-10-04' in _c: ok += 1
    else: bad += 1; print('FAIL workflows-core 1.11.1 changelog section')
if ed == 'ce':
    for f in ('dev-workflows-shared', 'dev-workflows-skill-map'):
        n = len(open(f'{root}/.github/instructions/{f}.instructions.md', encoding='utf-8').read())
        if n < 20000: ok += 1
        else: bad += 1; print(f'FAIL {f}: {n} characters')
print(f'{ed}: {ok} passed, {bad} failed'); sys.exit(1 if bad else 0)
`````

#### `scripts/apply.sh`

`````bash
#!/usr/bin/env bash
# apply.sh EDITION ROOT [--dry] — apply every Round 3 edit file to one edition, in order. Stops at the first mismatch.
set -euo pipefail
ed=$1; R=$2; dry=${3:-}; S=$(cd "$(dirname "$0")" && pwd); E=$S/edits; G=$S/gen; mkdir -p "$G"
w(){ python3 "$S/wsub.py" "$R/$1" "$2" $dry; }
g(){ python3 "$S/gen.py" "$ed" "$E/$1" > "$G/$ed-${1%.*}.txt"; echo "$G/$ed-${1%.*}.txt"; }
case $ed in
aw)
  w plugins/dev-workflows/references/code-handoff.md "$E/all-code-handoff.txt"
  w plugins/dev-workflows/references/code-handoff.md "$E/aw-ch-z.txt"
  w plugins/dev-workflows/commands/implement.md "$(g impl.tpl)"
  w plugins/dev-workflows/commands/implement.md "$(g impl-body.tpl)"
  w plugins/dev-workflows/commands/implement.md "$E/aw-implement.txt"
  w plugins/dev-workflows/commands/vuln.md "$(g vuln.tpl)"
  w plugins/dev-workflows/commands/upgrade.md "$(g upgrade.tpl)"
  w plugins/dev-workflows/commands/upgrade.md "$E/aw-upgrade-title.txt"
  w plugins/dev-workflows/agents/risk-planner.md "$(g risk-planner.tpl)"
  w plugins/dev-workflows/agents/test-writer.md "$(g test-writer.tpl)"
  w plugins/dev-workflows/agents/code-review.md "$(g code-review.tpl)"
  w plugins/dev-workflows/docs/commands/implement.md "$(g awie-doc-implement.tpl)"
  w plugins/dev-workflows/docs/commands/implement.md "$E/aw-doc-implement.txt"
  w plugins/dev-workflows/docs/reference/references.md "$E/aw-doc-references.txt"
  w plugins/dev-workflows/docs/reference/model-routing.md "$(g doc-model-routing.tpl)"
  w .claude/rules/dev-workflows.md "$E/all-rules-multisource.txt"
  w plugins/workflows-core/references/implementation-format.md "$E/aw-implformat.txt"
  w plugins/workflows-core/references/implementation-format.md "$E/aw-implformat1.txt"
  w plugins/workflows-core/docs/reference/references.md "$E/aw-wc-references.txt"
  w .claude/rules/dev-workflows.md "$E/all-rules-upgrademap.txt"
  w plugins/dev-workflows/docs/commands/upgrade.md "$E/aw-doc-upgrade.txt"
  w plugins/dev-workflows/commands/implement.md "$E/addN-7.txt"
  w plugins/dev-workflows/commands/vuln.md "$E/addN-2.txt"
  w plugins/dev-workflows/commands/upgrade.md "$E/addN-2.txt"
  w plugins/dev-workflows/agents/test-writer.md "$E/addN-1.txt"
  w plugins/dev-workflows/references/context-management.md "$E/addN-1.txt"
  w plugins/dev-workflows/docs/reference/follow-ups.md "$(g all-doc-followups.tpl)"
  w plugins/workflows-core/references/followup-emission.md "$(g all-followup-emission.tpl)"
  w plugins/workflows-core/references/followup-emission.md "$E/aw-ladder8.txt"
  w plugins/dev-workflows/commands/implement.md "$E/aw-ladder.txt"
  w plugins/dev-workflows/commands/ready.md "$E/aw-ladder.txt"
  w plugins/product-workflows/commands/epics.md "$E/aw-ladder.txt"
  w plugins/product-workflows/commands/brd-proposal.md "$E/aw-ladder.txt"
  w plugins/product-workflows/commands/prd-proposal.md "$E/aw-ladder.txt"
  w plugins/docs-workflows/commands/document.md "$E/aw-ladder.txt"
  w plugins/docs-workflows/commands/release-notes.md "$E/aw-ladder.txt"
  w plugins/dev-workflows/docs/reference/model-routing.md "$E/aw-doc-mr.txt"
  w plugins/dev-workflows/commands/vuln.md "$E/repopath-4.txt"
  w plugins/dev-workflows/commands/upgrade.md "$E/repopath-3.txt"
  w plugins/dev-workflows/commands/vuln.md "$E/all-vu-root.txt"
  w plugins/dev-workflows/commands/upgrade.md "$E/all-vu-root.txt"
  w plugins/dev-workflows/commands/vuln.md "$E/vuln-maint.txt"
  w plugins/dev-workflows/commands/upgrade.md "$E/upgrade-maint.txt"
  w .claude/rules/dev-workflows.md "$(g all-rules-reviewfixer.tpl)"
  w plugins/workflows-core/references/session-hygiene.md "$E/aw-hygiene.txt"
  w plugins/dev-workflows/commands/vuln.md "$E/vuln-span.txt"
  w plugins/workflows-core/references/model-routing/classification.md "$E/all-floor-classification.txt"
  w plugins/dev-workflows/docs/reference/model-routing.md "$E/all-floor-docs-mr.txt"
  w .claude/rules/dev-workflows.md "$E/awie-floor-rules.txt"
  w plugins/workflows-core/references/model-routing/classification.md "$E/aw-floor-nouns-cls.txt"
  w plugins/dev-workflows/docs/reference/model-routing.md "$E/aw-floor-nouns-mr.txt"
  w .claude/rules/dev-workflows.md "$E/aw-floor-nouns-rules.txt"
  w .claude/rules/dev-workflows.md "$E/aw-rules-handoff-node.txt"
  w plugins/dev-workflows/references/code-handoff.md "$(g all-ch-29.tpl)"
  w plugins/workflows-core/references/finding-triage.md "$E/all-triage-stayed.txt"
  w .claude/rules/workflows-core.md "$E/aw-rules-wc.txt"
  w plugins/product-workflows/docs/reference/model-routing.md "$E/aw-pw-mr.txt"
  w plugins/workflows-core/references/phase-handoff.md "$E/aw-ph-45.txt"
  w plugins/dev-workflows/commands/implement.md "$E/addN3-8.txt"
  w plugins/dev-workflows/commands/vuln.md "$E/addN3-2.txt"
  w plugins/dev-workflows/commands/upgrade.md "$E/addN3-2.txt"
  w plugins/dev-workflows/agents/test-writer.md "$E/addN3-1.txt"
  w plugins/dev-workflows/references/context-management.md "$E/addN3-1.txt"
  w plugins/product-workflows/commands/prd-ground.md "$E/aw-pg-comment.txt"
  w plugins/workflows-core/references/next-phase-offer.md "$E/aw-npo.txt"
  w plugins/workflows-core/references/next-phase-offer.md "$(g all-npo-rule5.tpl)"
  ;;
ie)
  w plugins/dev-workflows/references/code-repo-handoff.md "$E/all-code-handoff.txt"
  w plugins/dev-workflows/commands/implement.md "$(g impl.tpl)"
  w plugins/dev-workflows/commands/implement.md "$(g impl-body.tpl)"
  w plugins/dev-workflows/commands/implement.md "$E/ed-implement.txt"
  w plugins/dev-workflows/commands/vuln.md "$(g vuln.tpl)"
  w plugins/dev-workflows/commands/upgrade.md "$(g upgrade.tpl)"
  w plugins/dev-workflows/commands/upgrade.md "$E/ed-upgrade-title.txt"
  w plugins/dev-workflows/agents/risk-planner.md "$(g risk-planner.tpl)"
  w plugins/dev-workflows/agents/test-writer.md "$(g test-writer.tpl)"
  w plugins/dev-workflows/agents/code-review.md "$(g code-review.tpl)"
  w plugins/dev-workflows/docs/commands/implement.md "$(g awie-doc-implement.tpl)"
  w plugins/dev-workflows/docs/reference/references.md "$E/ed-doc-references.txt"
  w plugins/dev-workflows/docs/reference/model-routing.md "$(g doc-model-routing.tpl)"
  w .claude/rules/dev-workflows-code.md "$E/all-rules-multisource.txt"
  w .claude/rules/dev-workflows-map.md "$E/all-rules-upgrademap.txt"
  w plugins/dev-workflows/docs/commands/upgrade.md "$E/ed-doc-upgrade.txt"
  w plugins/dev-workflows/commands/implement.md "$E/addN-7.txt"
  w plugins/dev-workflows/commands/vuln.md "$E/addN-2.txt"
  w plugins/dev-workflows/commands/upgrade.md "$E/addN-2.txt"
  w plugins/dev-workflows/agents/test-writer.md "$E/addN-1.txt"
  w plugins/dev-workflows/references/context-management.md "$E/addN-1.txt"
  w plugins/dev-workflows/docs/reference/follow-ups.md "$(g all-doc-followups.tpl)"
  w plugins/dev-workflows/references/followup-emission.md "$(g all-followup-emission.tpl)"
  w plugins/dev-workflows/commands/vuln.md "$E/repopath-4.txt"
  w plugins/dev-workflows/commands/upgrade.md "$E/repopath-3.txt"
  w plugins/dev-workflows/commands/vuln.md "$E/all-vu-root.txt"
  w plugins/dev-workflows/commands/upgrade.md "$E/all-vu-root.txt"
  w plugins/dev-workflows/commands/vuln.md "$E/vuln-maint.txt"
  w plugins/dev-workflows/commands/upgrade.md "$E/upgrade-maint.txt"
  w .claude/rules/dev-workflows-code.md "$(g all-rules-reviewfixer.tpl)"
  w plugins/dev-workflows/commands/vuln.md "$E/vuln-span.txt"
  w plugins/dev-workflows/references/model-routing/classification.md "$E/all-floor-classification.txt"
  w plugins/dev-workflows/docs/reference/model-routing.md "$E/all-floor-docs-mr.txt"
  w .claude/rules/dev-workflows-code.md "$E/awie-floor-rules.txt"
  w plugins/dev-workflows/references/code-repo-handoff.md "$(g all-ch-29.tpl)"
  w plugins/dev-workflows/references/finding-triage.md "$E/all-triage-stayed.txt"
  w plugins/dev-workflows/commands/implement.md "$E/addN3-8.txt"
  w plugins/dev-workflows/commands/vuln.md "$E/addN3-2.txt"
  w plugins/dev-workflows/commands/upgrade.md "$E/addN3-2.txt"
  w plugins/dev-workflows/agents/test-writer.md "$E/addN3-1.txt"
  w plugins/dev-workflows/references/context-management.md "$E/addN3-1.txt"
  w plugins/dev-workflows/references/next-phase-offer.md "$E/ie-npo.txt"
  w plugins/dev-workflows/references/next-phase-offer.md "$(g all-npo-rule5.tpl)"
  ;;
ce)
  w dev-workflows/skills/_shared/code-repo-handoff.md "$E/all-code-handoff.txt"
  w dev-workflows/skills/implement/SKILL.md "$(g impl.tpl)"
  w dev-workflows/skills/implement/SKILL.md "$(g impl-body.tpl)"
  w dev-workflows/skills/implement/SKILL.md "$E/ed-implement.txt"
  w dev-workflows/skills/vuln/SKILL.md "$(g vuln.tpl)"
  w dev-workflows/skills/upgrade/SKILL.md "$(g upgrade.tpl)"
  w dev-workflows/skills/upgrade/SKILL.md "$E/ed-upgrade-title.txt"
  w dev-workflows/agents/risk-planner.md "$(g risk-planner.tpl)"
  w dev-workflows/agents/test-writer.md "$(g test-writer.tpl)"
  w dev-workflows/agents/code-review.md "$(g code-review.tpl)"
  w dev-workflows/docs/skills/implement.md "$E/ce-doc-implement.txt"
  w dev-workflows/docs/reference/references.md "$E/ed-doc-references.txt"
  w dev-workflows/docs/reference/model-routing.md "$(g doc-model-routing.tpl)"
  w .github/instructions/dev-workflows-skill-map.instructions.md "$E/all-rules-multisource.txt"
  w .github/instructions/dev-workflows-skill-map.instructions.md "$E/all-rules-upgrademap.txt"
  w dev-workflows/docs/skills/upgrade.md "$E/ed-doc-upgrade.txt"
  w dev-workflows/skills/implement/SKILL.md "$E/addN-7.txt"
  w dev-workflows/skills/vuln/SKILL.md "$E/addN-2.txt"
  w dev-workflows/skills/upgrade/SKILL.md "$E/addN-2.txt"
  w dev-workflows/agents/test-writer.md "$E/addN-1.txt"
  w dev-workflows/skills/_shared/context-management.md "$E/addN-1.txt"
  w dev-workflows/docs/reference/follow-ups.md "$(g all-doc-followups.tpl)"
  w dev-workflows/skills/_shared/followup-emission.md "$(g all-followup-emission.tpl)"
  w dev-workflows/skills/vuln/SKILL.md "$E/repopath-4.txt"
  w dev-workflows/skills/upgrade/SKILL.md "$E/repopath-3.txt"
  w dev-workflows/skills/vuln/SKILL.md "$E/all-vu-root.txt"
  w dev-workflows/skills/upgrade/SKILL.md "$E/all-vu-root.txt"
  w dev-workflows/skills/vuln/SKILL.md "$E/vuln-maint.txt"
  w dev-workflows/skills/upgrade/SKILL.md "$E/upgrade-maint.txt"
  w .github/instructions/dev-workflows-skill-map.instructions.md "$(g all-rules-reviewfixer.tpl)"
  w dev-workflows/skills/vuln/SKILL.md "$E/vuln-span.txt"
  w dev-workflows/skills/_shared/model-routing.md "$E/all-floor-classification.txt"
  w dev-workflows/docs/reference/model-routing.md "$E/all-floor-docs-mr.txt"
  w dev-workflows/skills/_shared/code-repo-handoff.md "$(g all-ch-29.tpl)"
  w dev-workflows/skills/_shared/finding-triage.md "$E/all-triage-stayed.txt"
  w dev-workflows/skills/implement/SKILL.md "$E/addN3-8.txt"
  w dev-workflows/skills/vuln/SKILL.md "$E/addN3-2.txt"
  w dev-workflows/skills/upgrade/SKILL.md "$E/addN3-2.txt"
  w dev-workflows/agents/test-writer.md "$E/addN3-1.txt"
  w dev-workflows/skills/_shared/context-management.md "$E/addN3-1.txt"
  w dev-workflows/skills/_shared/next-phase-offer.md "$E/ce-npo.txt"
  w dev-workflows/skills/_shared/next-phase-offer.md "$(g all-npo-rule5.tpl)"
  ;;
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
"""release.py EDITION ROOT — bump Round 3's versions and insert its changelog sections ($S/cl/<ed>-<plugin>.md)."""
import json, os, re, sys
ed, root = sys.argv[1], sys.argv[2]
S = os.path.dirname(os.path.abspath(__file__))
R = {'aw': ('.claude-plugin/marketplace.json', {
         'workflows-core': ('1.11.0', '1.11.1', 'plugins/workflows-core/.claude-plugin/plugin.json', 'plugins/workflows-core/CHANGELOG.md'),
         'dev-workflows': ('4.6.0', '4.7.0', 'plugins/dev-workflows/.claude-plugin/plugin.json', 'plugins/dev-workflows/CHANGELOG.md'),
         'product-workflows': ('3.12.0', '3.12.1', 'plugins/product-workflows/.claude-plugin/plugin.json', 'plugins/product-workflows/CHANGELOG.md'),
         'docs-workflows': ('1.5.0', '1.5.1', 'plugins/docs-workflows/.claude-plugin/plugin.json', 'plugins/docs-workflows/CHANGELOG.md')}),
     'ie': ('.claude-plugin/marketplace.json', {
         'dev-workflows': ('2.67.0', '2.68.0', 'plugins/dev-workflows/.claude-plugin/plugin.json', 'plugins/dev-workflows/CHANGELOG.md')}),
     'ce': ('.github/plugin/marketplace.json', {
         'dev-workflows': ('2.36.0', '2.37.0', 'dev-workflows/.plugin/plugin.json', 'dev-workflows/CHANGELOG.md')})}[ed]
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

Extracted by Task 0 Step 2 into `$S/edits`. Each block is `<<<<<<< OLD <n>` (the text, matched whitespace-insensitively, `n` times), `=======`, the replacement, `>>>>>>> NEW`. Prefixes: `all-` every edition unchanged; `aw-` this edition; `awie-` this edition and the internal edition; `ce-` the Copilot edition; `ed-` the internal and Copilot editions unchanged; `*.tpl` all three through `gen.py`.

#### `edits/addN-1.txt`

`````text
<<<<<<< OLD 1
git add -N .
=======
git add -N :/
>>>>>>> NEW
`````

#### `edits/addN-2.txt`

`````text
<<<<<<< OLD 2
git add -N .
=======
git add -N :/
>>>>>>> NEW
`````

#### `edits/addN-7.txt`

`````text
<<<<<<< OLD 7
git add -N .
=======
git add -N :/
>>>>>>> NEW
`````

#### `edits/addN3-1.txt`

`````text
<<<<<<< OLD 1
git add -N :/ && git diff
=======
git add -N --ignore-removal :/ && git -c diff.relative=false diff --no-ext-diff --no-color "$(git rev-parse -q --verify HEAD || git hash-object -t tree /dev/null)"
>>>>>>> NEW
`````

#### `edits/addN3-2.txt`

`````text
<<<<<<< OLD 2
git add -N :/ && git diff
=======
git add -N --ignore-removal :/ && git -c diff.relative=false diff --no-ext-diff --no-color "$(git rev-parse -q --verify HEAD || git hash-object -t tree /dev/null)"
>>>>>>> NEW
`````

#### `edits/addN3-8.txt`

`````text
<<<<<<< OLD 8
git add -N :/ && git diff
=======
git add -N --ignore-removal :/ && git -c diff.relative=false diff --no-ext-diff --no-color "$(git rev-parse -q --verify HEAD || git hash-object -t tree /dev/null)"
>>>>>>> NEW
`````

#### `edits/all-ch-29.tpl`

`````text
<<<<<<< OLD 1
cancelled there);
=======
cancelled there), or, in `{{IMPL}}`, a surviving `BLOCKER` whose fix lies in another code repository;
>>>>>>> NEW
`````

#### `edits/all-code-handoff.txt`

`````text
<<<<<<< OLD 1
Body: **written to a file** — `<body-path>`, a `command mktemp -t` path outside any repo tree — never passed inline, which would break on newlines and quoting. It contains what the run produced (`body_facts`), the files changed, the reviewer verdict where the caller has one, the test result, and, on a `clean_finish: false` run, §2.9's banner as its **first line**. The same file is what §3.2 names when `gh` is unavailable, so the user pastes the identical body — banner included — into the web UI.
=======
Body: **written to a file** — `<body-path>`, a `command mktemp -t` path outside any repo tree — never passed inline, which would break on newlines and quoting. The same file is what §3.2 names when `gh` is unavailable, so the user pastes the identical body — banner included — into the web UI.

**What the body holds.** Four sections, in this order, rendered from `body_facts`, with no preamble: on a `clean_finish: false` run §2.9's banner is the body's **first line**, and otherwise its first heading is — save where a template resolves (below), which keeps its own opening first, under the banner where there is one.

1. `## Summary` — what changed, one line per notable item, and the files changed: the paths the run's commits on this branch carry, read from git (`git -C "<repo>" show --no-show-signature --name-status -z --format= <sha>` per commit this run made), never an agent's own list. Where the branch also carries commits this run did not make — any that `origin/<base>..HEAD` lists besides its own, unpushed commits on a local `<base>` included — the Summary names them (`git -C "<repo>" log --no-show-signature --format='%h %s' origin/<base>..HEAD`, less this run's) as part of the pull request this run neither made nor reviewed, and Merge danger weighs them.
2. `## Evidence` — a **Before** and an **After**, each taken only from what the run observed: the caller's baseline against its verification, and on a bug fix the failing reproduction against the passing test. Where the run has no before or no after — tests the operator skipped, a verification that could not run — the section says which, and why. "Tests pass" alone is a claim, not a before and an after.
3. `## Merge danger` — the **door**, with one line of why, and the **blast radius**, with one line of what breaking would look like:
   - **Door: one-way** where the change includes a step that reverting its commit does not undo — a migration that drops or rewrites data, removing a public contract that consumers outside the repository use, writing persisted data in a new format, or anything that ships outward (sends, publishes, deletes); **two-way** otherwise. **Where the run cannot tell, one-way**, with the reason: the door is the run grading its own change, and the uncertain case is the one a reader should slow down on.
   - **Blast radius** — a short phrase naming what breaks if the change is wrong: an API's consumers, a data store, a screen, the build.
4. `## Review` — the run's classification; the reviewer verdict and triage summary where the caller has them, or, where no review ran, that none did and why; and every review finding the caller did not apply, with its severity.

**The repository's own template wins.** Resolve it against a fixed set of paths, never by searching for one: list the committed tree's candidates with `git -C "<repo>" ls-tree -r -z --full-tree --name-only HEAD | tr '\0' '\n' | grep -i -E '^(\.github/|docs/)?pull_request_template(\.md|/[^/]+\.md)$|^\.gitlab/merge_request_templates/default\.md$'` — `-z` because, without it, git quotes a name holding a non-ASCII byte and the anchor never matches it, and `--full-tree` so the listing is the whole tree wherever `<repo>` points; no output is no template — and stop at the first rung below that a listed path matches, comparing without regard to case —

1. `.github/pull_request_template.md`, then `pull_request_template.md` at the root, then `docs/pull_request_template.md`;
2. the first of `.github/PULL_REQUEST_TEMPLATE/`, `PULL_REQUEST_TEMPLATE/` and `docs/PULL_REQUEST_TEMPLATE/` that holds a `.md` file directly: where it holds exactly one, that file; where it holds several, none — a directory of templates names no default, so the body is written as above and its last line says the repository offers several templates, naming the directory;
3. `.gitlab/merge_request_templates/Default.md`.

Where a template resolves, read it with `git -C "<repo>" show HEAD:<path>`, `<path>` spelled exactly as the listing printed it (git looks a path up case-sensitively) — the committed file, never a working-tree copy that may hold somebody else's edit — and the body **is that template, filled**: its headings kept in their order, and each section answered from `body_facts`; a section the run has nothing for says so and why, and never keeps the template's placeholder text; a checkbox ticked only where the run can show what it claims, and never deleted; each of the four sections above placed in the template section that asks for it, and every one no template section asks for appended after the template, in the order above. A template with no headings is one section, answered in place. An HTML comment (`<!-- … -->`) in a template is its note to whoever fills it: follow it, then remove it with the placeholder text. The banner stays the first line. **The template wins because the body replaces it otherwise**: `gh pr create --body-file` replaces what the web UI would have prefilled, and §3.2 has the user paste the body in its place, so a body in this section's own shape would delete the template on either path.
>>>>>>> NEW
<<<<<<< OLD 1
| `body_facts` | what §2.7 renders into the body file |
=======
| `body_facts` | what §2.7 renders into the body file's four sections: what changed and the files changed; the before and the after the run observed; the facts its door and blast-radius calls rest on; and the review — the classification, the verdict and triage, and every finding not applied |
>>>>>>> NEW
<<<<<<< OLD 1
The body is at <body-path>.
=======
The body is at <body-path> — paste it in place of any description the web UI prefills.
>>>>>>> NEW
<<<<<<< OLD 1
| `repo` | absolute path of the code repository |
=======
| `repo` | absolute path of the code repository's top level — where the caller holds a path inside it, `git -C <path> rev-parse --show-toplevel` of that path: §2.2's porcelain paths are relative to the top level, and `git add` run from a subdirectory reads them against the wrong root |
>>>>>>> NEW
<<<<<<< OLD 1
Title: the commit subject of §2.3.
=======
Title: the commit subject of §2.3 — on a §2.12 terminal call, which makes no commit of its own, the caller's `title`, written the way §2.3 writes a subject.
>>>>>>> NEW
<<<<<<< OLD 1
| `title` | the commit subject and pull-request title |
=======
| `title` | the commit subject and pull-request title — on a §2.12 terminal call, which commits nothing, the pull-request title alone (§2.7) |
>>>>>>> NEW
<<<<<<< OLD 1
**A unit-level call emits no §3.1 line** (§3.1 allows one per *full* call), but it is not silent:
=======
**A unit-level commit that does not land ends the split**, whether a hook rejected it or git failed to stage or write it (§2.2, §2.3). Its changes stay behind uncommitted, and §2.3 forbids carrying on as though it landed, so the caller works no later unit — a later unit's §2.2 would fold the rejected changes into that unit's commit — and goes to its terminal call, which then stages and commits nothing: it runs §2.1, then, where the branch carries a commit this run's unit-level calls made, §2.4 onward for those commits, its §3.1 line carrying the *A unit commit rejected* append; the caller sets `clean_finish: false` (§2.9). Where the branch carries no such commit, its line is the *Commit rejected* row.

**A unit-level call emits no §3.1 line** (§3.1 allows one per *full* call), but it is not silent:
>>>>>>> NEW
<<<<<<< OLD 1
| Pre-existing dirty paths skipped |
=======
| A unit commit rejected (§2.12) | append `; <unit> NOT committed — rejected by <who> (<reason>); its changes are <where>.` |
| Pre-existing dirty paths skipped |
>>>>>>> NEW
<<<<<<< OLD 1
### 2.2 What gets staged

**The precondition.**
=======
### 2.2 What gets staged

**After a §2.12 unit-level commit that did not land, this step stages nothing** — its changes stay uncommitted — and the call goes straight on to §2.4 where the branch carries a commit this run's unit-level calls made, and otherwise ends on §3.1's *Commit rejected* row (§2.12).

**The precondition.**
>>>>>>> NEW
<<<<<<< OLD 1
and `<n> commit(s) on <branch>` for a terminal call whose own staging was empty but whose branch carries commits from unit-level calls.
=======
and `<n> commit(s) on <branch>` for a terminal call whose own commit set was empty, or skipped after a unit that did not land (§2.12), but whose branch carries commits from unit-level calls; `<who>` is `a <hook> hook`, or `git` where git itself failed to stage or write it (§2.2, §2.3); `<where>` is `staged` after an `add -A` whose commit did not land, and `in the working tree` where §2.2's `git add` failed or a carve-out-1 commit did not land; and `<unit>` is the unit's name on a §2.12 split, `the commit` otherwise.
>>>>>>> NEW
<<<<<<< OLD 1
and the terminal call's §3.1 line names the count of units that failed to commit.
=======
and the terminal call's §3.1 line names the unit that failed to commit where an earlier unit committed, and is otherwise the *Commit rejected* row (§2.12).
>>>>>>> NEW
<<<<<<< OLD 1
**The commit runs exactly as it would on a clean finish, and the push is still *offered* under §2.4's choice.**
=======
- a §2.12 unit-level commit that did not land — the pull request carries fewer units than the run was asked for, and that unit's changes sit uncommitted in the local repository, staged or in the working tree.

**The commit runs exactly as it would on a clean finish, and the push is still *offered* under §2.4's choice.**
>>>>>>> NEW
<<<<<<< OLD 1
A `pre-commit` / `commit-msg` hook can reject the commit; the changes then stay staged.
=======
A `pre-commit` / `commit-msg` hook can reject the commit; the changes then stay staged — or, under §2.2's carve-out 1, which stages nothing, in the working tree. A commit git itself fails to write (a signing failure, an unset author identity) leaves them the same way, and everything this paragraph and §2.12 say of a rejected commit holds for it, with git's error in place of the hook's output.
>>>>>>> NEW
<<<<<<< OLD 1
Record the failure and its hook output;
=======
Record the failure and the hook's output or git's error;
>>>>>>> NEW
<<<<<<< OLD 1
| Commit rejected by a hook | `Code repo: NOT committed — <n> unit(s) rejected by a <hook> hook (<reason>). The changes are staged.` |
=======
| Commit rejected | `Code repo: NOT committed — <unit> rejected by <who> (<reason>). The changes are <where>.` |
>>>>>>> NEW
<<<<<<< OLD 1
**Nothing staged.** Do **not** emit a line here
=======
**A `git add` git refuses** (a held `index.lock`, a full disk) is a unit that did not land too: what §2.3 and §2.12 say of a rejected commit holds for it, save that its changes are in the working tree, perhaps partly staged, rather than staged, as after an `add -A`.

**Nothing staged.** Do **not** emit a line here
>>>>>>> NEW
<<<<<<< OLD 1
Stage by enumeration instead: the current porcelain set **minus** the recorded paths. **A path that was already dirty and that this run also edited is staged**, because
=======
Commit by enumeration instead: the current porcelain set **minus** the recorded paths, taken whole — a rename or copy record (`R` or `C` in either column) carries two NUL-terminated paths, the new one then the original, and both belong to the set, as both do where the caller recorded `pre_existing_dirty`, so a rename the user had made is subtracted whole — and committed as pathspecs (§2.3's `-- <paths>` form), never staged into the index first: an index commit would also carry whatever else the index holds, somebody else's staged change included, and a per-path `git add` of a path already removed from the index (a `git rm`, or a `git mv`'s original) exits 128. Subtract path by path, never record by record, so a rename record pairing somebody else's new file with a path the run deleted keeps the run's deletion in the set. A ` D` record for a path `HEAD` does not hold (`git -C "<repo>" cat-file -e HEAD:<path>` fails) is an intent-to-add entry the run's captures left for a file the run created and removed again — no change: drop it with `git -C "<repo>" rm --cached -q -- ':(literal)<path>'` and leave it out of the set. A new file in the set is made known to git first, `git -C "<repo>" add -N -- ':(literal)<path>'`. `rm --cached`, `add -N` and §2.3's commit name each path with `:(literal)`, since a porcelain path can begin with `:`, which git otherwise reads as pathspec magic; never the global `--literal-pathspecs`, which every commit hook would inherit, its own globs then matching nothing. `cat-file` takes the path bare: `HEAD:<path>` is no pathspec. **A path that was already dirty and that this run also edited is committed**, because
>>>>>>> NEW
<<<<<<< OLD 1
    git -C "<repo>" commit -F <msg-path>
=======
git -C "<repo>" commit -F <msg-path>

Under §2.2's carve-out 1, run it as one commit, `git -C "<repo>" commit -F <msg-path> -- ':(literal)<path>' …`, with one `':(literal)<path>'` argument per enumerated path: git then commits those paths' work-tree state, read literally, and nothing else the index holds. Once it lands, run `git -C "<repo>" restore --staged -- ':(literal)<path>' …` over every committed path the new `HEAD` holds, so a `pre-commit` hook that fixed a file and re-staged it with a plain `git add` leaves no reverting copy in the index.
>>>>>>> NEW
<<<<<<< OLD 1
**Nothing staged.** Do **not** emit a line here — §3.1 allows exactly one per call, and this path continues.
=======
**Nothing to commit** — on the `add -A` path, the index holds nothing to commit after it (`git -C "<repo>" diff --cached --quiet` exits 0), a change the run staged itself with `git mv` or `git rm` included; under carve-out 1, the enumerated set is empty. Never run §2.3 with an empty `--` list: `git commit --` with no path commits whatever the index holds, somebody else's staged change included, or fails with `no changes added to commit`. Do **not** emit a line here — §3.1 allows exactly one per call, and this path continues.
>>>>>>> NEW
<<<<<<< OLD 1
the terminal call finds nothing left to stage, takes §2.2's `nothing staged` path,
=======
the terminal call finds nothing left to commit, takes §2.2's *nothing to commit* path,
>>>>>>> NEW
<<<<<<< OLD 1
it returns its outcome — commit sha, `nothing staged`, or a commit failure
=======
it returns its outcome — commit sha, `nothing to commit`, or a commit failure
>>>>>>> NEW
<<<<<<< OLD 1
§2.2 falls back to staging by enumeration exactly as the siblings do.
=======
§2.2 falls back to enumeration, as the siblings do, but commits the enumerated paths as pathspecs instead of staging them: an index commit would carry whatever else the index holds, and the dirty tree that sent the run there may include somebody else's staged change (§2.2 carve-out 1).
>>>>>>> NEW
<<<<<<< OLD 1
| `body_facts` | what §2.7 renders into the body file's four sections: what changed and the files changed;
=======
| `body_facts` | what §2.7 renders into the body file's four sections: what changed (the files changed being §2.7 item 1's, read from git);
>>>>>>> NEW
<<<<<<< OLD 1
a later unit's `add -A` would fold this unit's diff into that unit's commit under the wrong message
=======
a later unit's §2.2 would fold this unit's diff into that unit's commit under the wrong message
>>>>>>> NEW
`````

#### `edits/all-doc-followups.tpl`

`````text
<<<<<<< OLD 1
becomes a follow-up: a file or page owned by someone else
=======
becomes a follow-up: a change another code repository needs (`{{QIMPL}}` changes code only in the repository it branches), a file or page owned by someone else
>>>>>>> NEW
<<<<<<< OLD 1
a deferred review BLOCKER, a skipped test,
=======
a deferred review BLOCKER (save one whose fix lies in another code repository), a skipped test,
>>>>>>> NEW
<<<<<<< OLD 1
file path, gap id, or signal type
=======
file path, gap id, signal type, or other repository and unit
>>>>>>> NEW
`````

#### `edits/all-floor-classification.txt`

`````text
<<<<<<< OLD 1
was given more than one code repository, or any directory input (
=======
was given more than one distinct code repository (counted by top level, so an `@path` whose top level is already counted adds none), or any folder input (
>>>>>>> NEW
<<<<<<< OLD 1
- more than one code repository is referenced;
=======
- more than one distinct code repository is referenced (counted by top level);
>>>>>>> NEW
`````

#### `edits/all-floor-docs-mr.txt`

`````text
<<<<<<< OLD 1
Handing it more than one code repository, or any directory input (
=======
Handing it more than one distinct code repository (counted by top level, so an `@path` whose top level is already counted adds none), or any folder input (
>>>>>>> NEW
`````

#### `edits/all-followup-emission.tpl`

`````text
<<<<<<< OLD 1
requires a MANUAL human step:

- Files/pages owned by others
=======
requires a MANUAL human step:

- A change another code repository needs (`{{QIMPL}}` changes code only in the repository it branches, and records one for a run from there); its stable-key identity is the other repository — named by its `origin` remote URL with the scheme, host and `.git` dropped (`team-a/api`), by its absolute top-level path where it has no `origin`, and, for one the run was never given, by the name the plan gives it, marked `(not mounted)` — and the unit the task addresses, both named in its task line. The task's action is one run from that repository, which plans that unit's changes there itself; the changes the task lists are what this run saw, never the whole of that work.
- Files/pages owned by others
>>>>>>> NEW
<<<<<<< OLD 1
deferred review BLOCKERs, skipped tests,
=======
deferred review BLOCKERs (save one whose fix lies in another code repository, which the first bullet takes), skipped tests,
>>>>>>> NEW
<<<<<<< OLD 1
(file path | gap-id | signal-type)
=======
(file path | gap-id | signal-type | other repository + unit)
>>>>>>> NEW
`````

#### `edits/all-npo-rule5.tpl`

`````text
<<<<<<< OLD 1
a command operating at **Epic scope** offers TWO branches:
=======
a command operating at **Epic scope** offers TWO branches (and `{{QIMPL}}` names one more before them for each other code repository it recorded a change for: the run from that repository, addressed to the unit it implemented, the Epic itself where it was one):
>>>>>>> NEW
`````

#### `edits/all-rules-multisource.txt`

`````text
<<<<<<< OLD 1
A multi-source run that wrote into a repo it never branched names that repo and its dirty paths in the Phase 5 report rather than inventing a branch for it
=======
A multi-source run changes code only in the repository it branched; a change another code repository needs is a follow-up (Phase 6's, or named in the stop), never an uncommitted edit there
>>>>>>> NEW
`````

#### `edits/all-rules-reviewfixer.tpl`

`````text
<<<<<<< OLD 1
`review-fixer` handles surviving BLOCKER and MAJOR findings;
=======
`review-fixer` handles surviving BLOCKER and MAJOR findings (on `{{IMPL}}`, only those whose fix lies in the branched repository);
>>>>>>> NEW
`````

#### `edits/all-rules-upgrademap.txt`

`````text
<<<<<<< OLD 1
[finish-code-branch §2.2–§2.3: commit this component] ⟲
=======
[finish-code-branch §2.1–§2.3: commit this component] ⟲ (a commit that does not land ends the loop)
>>>>>>> NEW
`````

#### `edits/all-triage-stayed.txt`

`````text
<<<<<<< OLD 1
a caller that works unit by unit may count a settle prompt's **Cancel** as one too, and says so.
=======
a caller that works unit by unit may count a settle prompt's **Cancel** as one too, and says so; and a caller whose own rule keeps a first review's `BLOCKER` from the fixer, because its fix lies in another code repository, counts that `BLOCKER` as one, and says so.
>>>>>>> NEW
<<<<<<< OLD 1
A partly emptied set is not this case: where at least one finding survived, the verdict stands and the command's normal branch runs on the survivors.
=======
A partly emptied set is not this case: where at least one finding survived, the verdict stands and the command's normal branch runs on the survivors — save that a caller whose own rule keeps a first review's survivors from the fixer, because their fix lies in another code repository, treats a `BLOCK` as this case where none of those survivors is a `BLOCKER` and no `BLOCKER` or `MAJOR` is left for the fixer: it asks this section's first settle prompt, reporting every survivor — those kept from the fixer and any `MINOR` or `NIT` left — in place of *nothing survived*, and says so. A `BLOCKER` among the survivors kept from the fixer leaves the review blocked, as § On re-review rule 2 names that stop, and on a `PASS WITH RECOMMENDATIONS` with no `BLOCKER` or `MAJOR` left for the fixer the caller continues without one.
>>>>>>> NEW
`````

#### `edits/all-vu-root.txt`

`````text
<<<<<<< OLD 1
the diff (from `review_diff_file`),
=======
the diff (from `review_diff_file`), the project root (the repository's top level, `git rev-parse --show-toplevel`),
>>>>>>> NEW
<<<<<<< OLD 1
for the surviving `BLOCKER` and `MAJOR` findings
=======
for the surviving `BLOCKER` and `MAJOR` findings and the same project root
>>>>>>> NEW
<<<<<<< OLD 1
**Specify test command to use** → take free text, record it as `test_command_hint`,
=======
**Specify test command to use** → when asking, tell the user that a command matching a suite the capture detected runs in that suite's own directory and any other from the repository's top level (name it), so one meant for a subdirectory with no detected suite begins `cd <dir> &&` (`dev-workflows:test-baseliner` capture step 1, *Scope*); take free text and record it verbatim as `test_command_hint`,
>>>>>>> NEW
`````

#### `edits/aw-ch-z.txt`

`````text
<<<<<<< OLD 1
carve-out 1 would stage that path in its quoted form and `git add` would match no file
=======
carve-out 1 would commit that path in its quoted form and match no file
>>>>>>> NEW
`````

#### `edits/aw-doc-implement.txt`

`````text
<<<<<<< OLD 1
a read-only codebase-exploration subagent at Phase 2A, and at Phase 2B wherever Phase 1.7 did not run
=======
a read-only codebase-exploration subagent at Phase 2A (none where a down-classification you accepted at Phase 2B sent the run there, its exploration being already written) and at Phase 2B only where no exploration this run made (Phase 1.7's, Phase 2A's or an earlier pass of Phase 2B's own) has written the codebase summary
>>>>>>> NEW
<<<<<<< OLD 1
or any folder input (a PRD folder or a spec folder)
=======
or any folder input (a specs folder or a spec/design folder)
>>>>>>> NEW
`````

#### `edits/aw-doc-mr.txt`

`````text
<<<<<<< OLD 1
unless it spans multiple repos
=======
unless it is given more than one repository or any specs or spec/design folder, the multi-source floor
>>>>>>> NEW
`````

#### `edits/aw-doc-references.txt`

`````text
<<<<<<< OLD 1
only its pull request degrades, to a draft carrying a DO-NOT-MERGE banner. It is also the one git reference that stages at repository scope, and §1 says why that divergence from its two siblings is deliberate.
=======
only its pull request degrades, to a draft carrying a DO-NOT-MERGE banner. It is also the one git reference that stages at repository scope, and §1 says why that divergence from its two siblings is deliberate. The pull request's body holds a Summary, the before and the after the run observed as Evidence, a Merge danger call — a one-way or two-way door, and its blast radius — and the Review; where the repository carries one pull-request template at a path the reference lists, the body is that template, filled.
>>>>>>> NEW
`````

#### `edits/aw-doc-upgrade.txt`

`````text
<<<<<<< OLD 1
as soon as its gates settle (step 6.5)
=======
as soon as its gates settle (step 6.5; a commit that does not land, because a hook rejects it or git fails to stage or write it, ends the batch there, leaving that component's changes uncommitted, later components unrun and any pull request a draft)
>>>>>>> NEW
`````

#### `edits/aw-floor-nouns-cls.txt`

`````text
<<<<<<< OLD 1
(a saved file folder, or a spec/design folder)
=======
(a specs folder under `specifications/`, or a spec/design folder; an `@path` Phase 0 classifies as a code repository is never a folder input)
>>>>>>> NEW
<<<<<<< OLD 1
- a saved file folder is supplied;
=======
- a specs folder (under `specifications/`) is supplied;
>>>>>>> NEW
`````

#### `edits/aw-floor-nouns-mr.txt`

`````text
<<<<<<< OLD 1
(a saved file folder, or a spec/design folder)
=======
(a specs folder under `specifications/`, or a spec/design folder; an `@path` Phase 0 classifies as a code repository is never a folder input)
>>>>>>> NEW
`````

#### `edits/aw-floor-nouns-rules.txt`

`````text
<<<<<<< OLD 1
an exported-ticket folder or a spec folder
=======
a specs folder or a spec/design folder
>>>>>>> NEW
`````

#### `edits/aw-hygiene.txt`

`````text
<<<<<<< OLD 1
(mirror `followup-emission.md` §4 resolution)
=======
(mirror `followup-emission.md` §2 resolution)
>>>>>>> NEW
`````

#### `edits/aw-implement.txt`

`````text
<<<<<<< OLD 1
Phase 3B step 8 re-enters this step on the SIGNIFICANT / HIGH-RISK path, where Phase 2A never ran, and a Phase 2B `### Re-classification` the user accepts reaches Phase 3A with Phase 2A's own exploration deliberately not re-run.
=======
Phase 3B step 8 re-enters this step on the SIGNIFICANT / HIGH-RISK path, which a run reaches with or without Phase 2A's exploration, and a Phase 2B `### Re-classification` the user accepts reaches Phase 3A with Phase 2A's own exploration deliberately not re-run.
>>>>>>> NEW
<<<<<<< OLD 1
**First remove this run's handoff files.** Nothing from here on reads one — `summary_file`, `plan_file`,
every `test_diff_file` and `review_diff_file` this run wrote (a re-capture that overwrote a path leaves
one file, a fresh `mktemp` another), `review_file` and `claims_file`.
=======
**First remove this run's handoff files.** Nothing from here on reads one — `summary_file`,
`partial_diff_file` where Phase 3A step 5 wrote one, every `test_diff_file` and `review_diff_file` this
run wrote (a re-capture that overwrote a path leaves one file, a fresh `mktemp` another), `review_file`
and `claims_file` — save `plan_file`, which Phase 4.6's `body_facts` read and Phase 4.6 then
removes; under `--no-commit`, where nothing reads it, it goes now with the rest.
>>>>>>> NEW
<<<<<<< OLD 1
and the **Keep the verdict** and **Cancel** arms of either of `workflows-core:finding-triage`'s settle prompts (Phase 3B steps 7 and 8). **Each of those runs Phase 4.6 before it stops**,
=======
the **Keep the verdict** and **Cancel** arms of either of `workflows-core:finding-triage`'s settle prompts (Phase 3B steps 7 and 8), the **Cancel** arm of Phase 3B step 7's `### Re-classification` prompt, the **Cancel** arm of each of Phase 2B's three prompts — the re-classification prompt, the repro prompt and the plan-approval prompt — when Phase 3A step 5's re-plan reached it, and the **Stop** arm of that step's question on a trigger met after the re-plan. **Each of those runs Phase 4.6 before it stops**,
>>>>>>> NEW
<<<<<<< OLD 1
**Two Cancels are not in that set, and the test is the written file rather than the branch.** Phase 2B's repro prompt runs *before* Pre-Phase 3, so cancelling there leaves no branch and no written file. Pre-Phase 3.5's framework prompt runs *after* the branch and still before the first edit — its Cancel leaves a branch with nothing on it, and there is as little for this phase to commit as in the Phase 2B case.
=======
**Two Cancels are not in that set on the ordinary path, and the test is the written file rather than the branch.** Phase 2B's repro prompt runs *before* Pre-Phase 3, so cancelling there leaves no branch and no written file — save on Phase 3A step 5's re-plan, which reaches that prompt after files were written, so its Cancel there is in the set above. Pre-Phase 3.5's framework prompt runs *after* the branch and still before the first edit — its Cancel leaves a branch with nothing on it, and there is as little for this phase to commit as in the ordinary Phase 2B case.
>>>>>>> NEW
<<<<<<< OLD 1
phase — the two unreadable-`test_diff_file` stops, the unreadable-`review_diff_file` stop, the
`review-fixer` `NEEDS HUMAN` stop, a review that stayed blocked, a settle prompt's **Keep the
verdict**, or a Cancel — removes the files it had made before it stops, in the same way, save a file
the stop itself named as unreadable, which stays for the operator to look at (that reference again).
=======
phase — the two unreadable-`test_diff_file` stops, the unreadable-`review_diff_file` stop, the
`review-fixer` `NEEDS HUMAN` stop, a review that stayed blocked, a settle prompt's **Keep the
verdict**, Phase 3A step 5's **Stop** on a trigger met after the re-plan, or a Cancel — removes the
files it had made, `plan_file` included, as it stops — after Phase 4.6, where the stop runs it — in
the same way, save a file the stop itself named as unreadable, which stays for the operator to look
at (that reference again).
>>>>>>> NEW
<<<<<<< OLD 1
so the report still says where the work ended up.
=======
so the report still says where the work ended up. Where `plan_file` is still on disk — every run but an ordinary `--no-commit` one, whose Phase 4 removed it — remove it now (`command rm -f -- "<plan_file>"`): the run kept it for this phase's `body_facts`, which read it.
>>>>>>> NEW
<<<<<<< OLD 1
run against its §1, which says why the record lives with its unit: one entry per repository this
run touched, each naming `repo`, `branch`, `base`, `commit` and `pushed`.
=======
run against its §1, which says why the record lives with its unit: one entry, the code repository
this run branched, naming `repo`, `branch`, `base`, `commit` and `pushed`.
>>>>>>> NEW
<<<<<<< OLD 1
`/implement` scans repositories it may write to, which is exactly what no other
=======
`/implement` scans the repository it is about to branch and modify — the working directory's — which is exactly what no other
>>>>>>> NEW
<<<<<<< OLD 1
a code repo is an `/implement`-only scan target.
=======
a code repo is an `/implement`-only scan target (or, sharing the top level of one already classified here, a search hint, as the table says).
>>>>>>> NEW
<<<<<<< OLD 1
(`repo_count` = cwd + referenced repos)
=======
(`repo_count`, Phase 1.6)
>>>>>>> NEW
<<<<<<< OLD 1
read them from the repo's own build/lint configuration. **Do not cite Phase 2A here**
=======
read them from the repo's own build/lint configuration at its top level. Run each from the directory the exploration found it in, in a subshell so the session's own directory never moves: `(builtin cd "<top level>/<dir>" >/dev/null && <command>)`, `<top level>/<dir>` being the top level itself unless the exploration said otherwise. **Do not cite Phase 2A here**
>>>>>>> NEW
`````

#### `edits/aw-implformat.txt`

`````text
<<<<<<< OLD 1
`NOT committed` line, §3.1),
or, on a multi-source `/implement` run, a repository it edited and never branched, which that run
reports as uncommitted rather than committing. The convention still needs to be
=======
`NOT committed` line, §3.1). The convention still needs to be
>>>>>>> NEW
`````

#### `edits/aw-implformat1.txt`

`````text
<<<<<<< OLD 1
One `## <YYYY-MM-DD> — /implement` block per run, one entry per repository the run touched:
=======
One `## <YYYY-MM-DD> — /implement` block per run, with one entry: the code repository the run branched. A change another code repository needed is a later run from there, with a block of its own. A block appended before `dev-workflows` 4.7.0 may carry one entry per repository that run touched, and a reader takes every entry. For example:
>>>>>>> NEW
<<<<<<< OLD 1
  pushed:  true
- repo:    billing-api
  branch:  feat/ACME-77-01-order-intake
=======
  pushed:  true

## 2026-09-02 — /implement
- repo:    billing-api
  branch:  feat/ACME-77-01-order-intake
>>>>>>> NEW
<<<<<<< OLD 1
only partly** — a block naming two repositories where the earlier run resolved one and not the
=======
only partly** — a block appended before `dev-workflows` 4.7.0, when one run could record several repositories, naming two where the earlier run resolved one and not the
>>>>>>> NEW
`````

#### `edits/aw-ladder.txt`

`````text
<<<<<<< OLD 1
§4 ladder
=======
§2 ladder
>>>>>>> NEW
`````

#### `edits/aw-ladder8.txt`

`````text
<<<<<<< OLD 1
§4 (resolve target)
=======
§2 (resolve target)
>>>>>>> NEW
`````

#### `edits/aw-npo.txt`

`````text
<<<<<<< OLD 1
- `/dev-workflows:implement <EPIC>` → finish remaining Epics (breadth); once ALL Epics implemented →
=======
- `/dev-workflows:implement <EPIC>` → first, where it recorded a change another code repository needs, the run from that repository, addressed to the unit the run implemented (the Epic itself, where it was one); then finish remaining Epics (breadth); once ALL Epics implemented →
>>>>>>> NEW
`````

#### `edits/aw-pg-comment.txt`

`````text
<<<<<<< OLD 1
# the multi-source rule in model-routing/classification.md §1.1
=======
# the repository half of the multi-source rule (classification.md §1.1)
>>>>>>> NEW
`````

#### `edits/aw-ph-45.txt`

`````text
<<<<<<< OLD 1
`/implement`'s Phase 4.5 is a silent no-op where step 7.5 wrote no conformance note,
=======
`/implement`'s Phase 4.5 is a silent no-op where step 7.5 wrote no conformance note in `$SPECS_PATH`,
>>>>>>> NEW
`````

#### `edits/aw-pw-mr.txt`

`````text
<<<<<<< OLD 1
— the same multi-source rule the companion `dev-workflows` plugin's `/implement` applies, cited by name in `/prd-ground`'s own Phase 2.
=======
— the repository half of the multi-source rule the companion `dev-workflows` plugin's `/implement` applies, cited by name in `/prd-ground`'s own Phase 2.
>>>>>>> NEW
<<<<<<< OLD 1
what is never a floor is **the address**.
=======
what is never a floor in this plugin is **the address** (in `/implement` it is one, a resolved specs folder being a folder input).
>>>>>>> NEW
<<<<<<< OLD 1
A PRD, an Epic, or a BRD is always a single addressed item, and addressing one is not a multi-source trigger
=======
A PRD, an Epic, or a BRD is always a single addressed item, and in this plugin addressing one is not a multi-source trigger
>>>>>>> NEW
`````

#### `edits/aw-rules-handoff-node.txt`

`````text
<<<<<<< OLD 1
[handoff-to-main: escalated spec/design notes, when any]
=======
[handoff-to-main: escalated spec/design notes in the specs repo, when any]
>>>>>>> NEW
`````

#### `edits/aw-rules-wc.txt`

`````text
<<<<<<< OLD 1
a BLOCKER surviving its triage, or a verdict the user keeps at a settle prompt
=======
a BLOCKER surviving its triage, a verdict the user keeps at a settle prompt, a unit-by-unit caller's Cancel there, or a first review's BLOCKER a caller keeps from the fixer because its fix lies in another code repository
>>>>>>> NEW
`````

#### `edits/aw-upgrade-title.txt`

`````text
<<<<<<< OLD 1
`title` = `upgrade <component> to <version> [<key>]` for a single component, or `upgrade <first> and <N> more [<key>]` for a batch, dropping the suffix in a run with no key
=======
`title` = the commit subject step 6.5 wrote where it committed one component, or, where it committed several, `upgrade <first> and <N> more [<key>]` over those components alone, typed to the log's shape as step 6.5 types its subjects, dropping the suffix in a run with no key (where it committed no component, the call opens no pull request and needs no title)
>>>>>>> NEW
<<<<<<< OLD 1
Run `git status --porcelain`. If dirty,
=======
Run `git status --porcelain -z --untracked-files=all`. If dirty,
>>>>>>> NEW
`````

#### `edits/aw-wc-references.txt`

`````text
<<<<<<< OLD 1
one block per run, one entry per repository, holding refs and never a summary,
=======
one block per run, with one entry — the code repository the run branched — holding refs and never a summary,
>>>>>>> NEW
<<<<<<< OLD 1
the follow-up task and journal emitter
=======
the follow-up task and verbose-note emitter
>>>>>>> NEW
`````

#### `edits/awie-doc-implement.tpl`

`````text
<<<<<<< OLD 1
    BR --> G{"SIGNIFICANT · HIGH-RISK? (set at classification)"}
=======
    BR --> G{"SIGNIFICANT · HIGH-RISK? (as classified, or raised)"}
>>>>>>> NEW
<<<<<<< OLD 1
    TS --> MT["Post-impl maintenance (4 agents)"] --> RP["Final report"]
=======
    TS --> MT["Post-impl maintenance (4 agents)"] --> RP["Final report"]
    P1 -.->|"raised at planning, before approval"| P2
    IMA -.->|"a trigger the plan missed: re-plan"| P2
    P2 -.->|"re-plan approved"| IMB
>>>>>>> NEW
<<<<<<< OLD 1
the Phase 0.5 readiness pre-flight, clarification, and, only when the input is multi-source,
=======
the Phase 0.5 readiness pre-flight, clarification (which, on a keyed run, first resolves the applicable ARD, then looks in the inputs, the code, the repository's own docs, `git log` and the ARD's rules before it asks, and asks only what would change the result), and, only when the input is multi-source,
>>>>>>> NEW
<<<<<<< OLD 1
`G` is not a new decision: it is the classification Phase 1.5 already made, drawn where the two paths part.
=======
`G` is not a new decision: it is the class as it stands, drawn where the two paths part — Phase 1.5's, as the multi-source floor or a down-classification accepted at plan approval left it, or raised before any file is written when Phase 2A's plan shows a classification trigger (such as more than 3–5 non-test files, authentication, a schema or migration, or a public contract — the dotted `P1` → `P2` edge); after a down-classification you accepted at plan approval, only a trigger a later revision adds raises it. A run that meets such a trigger while implementing, one its approved plan did not state (one of the concrete triggers the [classification policy](../reference/model-routing.md) lists, not its catch-all of unclear requirements, large unknowns or otherwise high blast radius, whose unknowns are asked about instead), re-plans upward: `risk-planner` plans the rest with the diff so far, and once you approve, the run continues on the review path without re-branching or re-capturing the baseline (the dotted `IMA` → `P2` → `IMB` edges); cancelling that re-plan commits the work{{NOCOMMIT}}, and any pull request the run opens is a draft. That happens once per run: should you accept a down-classification at the re-plan, a later trigger is put to you instead — continue without the review, or stop, which commits the work as cancelling the re-plan does.
>>>>>>> NEW
<<<<<<< OLD 1
it compresses the whole run into its two real decision points instead of naming each phase.
=======
it compresses the whole run into its two real decision points — and the dotted edges a change of class takes — instead of naming each phase.
>>>>>>> NEW
<<<<<<< OLD 1
**An optional ARD** (Phase 1.8,
=======
**An optional ARD** (resolved at the start of Phase 1's clarification, which reads its rules; Phase 1.8,
>>>>>>> NEW
<<<<<<< OLD 1
and triggers the Phase 1.7 fan-out scan in place of the single Explore subagent.
=======
and triggers the Phase 1.7 fan-out scan in place of the single Explore subagent. Run it from inside the repository it is to change: it changes the repository it is run from, and started outside every git work tree it stops before planning, naming where to run it from. An `@path` at a repository's top level is read as a code repository, with a notice where it also holds `prompt.md` or `*-design.md` files (name those by file to read them), and the run stops there where nothing else describes the work. The run changes code only in the repository you run it from: every other code repository it is given is read-only context, and the changes one of them needs become one follow-up for that repository: a task Phase 6 files on a keyed run that finishes (a direct run lists it in its report), named in the stop message on one that stops after plan approval. Where the plan changes no file in this repository at all, the run asks, in place of plan approval, whether to revise the plan or stop with nothing written, naming the run each other repository needs.
>>>>>>> NEW
<<<<<<< OLD 1
`review-fixer` fixes `BLOCKER` and `MAJOR` findings;
=======
`review-fixer` fixes `BLOCKER` and `MAJOR` findings whose fix lies in this repository (one whose fix lies in another code repository is recorded as a follow-up instead, and a `BLOCKER` among them stops the run as a review that stayed blocked);
>>>>>>> NEW
<<<<<<< OLD 1
more than one code repo, or any directory input (
=======
more than one distinct code repo (counted by top level, so an `@path` whose top level is already counted adds none), or any folder input (
>>>>>>> NEW
<<<<<<< OLD 1
escalated as open-question notes written back onto the source `specification.md`/`design.md`
=======
escalated as open-question notes written back onto the source `specification.md`/`design.md` where it lies in the specs repository or this one, a spec anywhere else having its gap reported instead
>>>>>>> NEW
<<<<<<< OLD 1
classifies the task (typically `SIGNIFICANT` once a merged design is in scope)
=======
classifies the task (`SIGNIFICANT` by the multi-source floor, its resolved specs folder being a folder input)
>>>>>>> NEW
<<<<<<< OLD 1
(Phase 3B step 7.5) and, behind a consent choice, handed off onto the specs repo's main branch (Phase 4.5)
=======
(Phase 3B step 7.5), committed with the code where it lies in this repository (Phase 4.6), and, where it lies in the specs repository, handed off behind a consent choice onto its main branch (Phase 4.5) — on a run that finishes; one that stops after the review names any such note in its stop message, uncommitted in the specs repository
>>>>>>> NEW
<<<<<<< OLD 1
folded into it is Phase 4.5 (a silent no-op unless Phase 3B's review escalated spec/design conformance notes onto the source spec/design;
=======
folded into it is Phase 4.5 (a silent no-op unless Phase 3B's review escalated spec/design conformance notes onto a spec/design in the specs repository, a note written into this repository's own spec riding on the code commit instead;
>>>>>>> NEW
<<<<<<< OLD 1
— a silent no-op when nothing was escalated,
=======
— Phase 4.5 being a silent no-op when nothing was escalated into the specs repository,
>>>>>>> NEW
`````

#### `edits/awie-floor-rules.txt`

`````text
<<<<<<< OLD 1
(more than one repo, or any directory input —
=======
(more than one distinct repo, counted by top level, or any folder input —
>>>>>>> NEW
`````

#### `edits/ce-doc-implement.txt`

`````text
<<<<<<< OLD 1
    p35 --> p4["Phase 4 — Post-implementation maintenance (both branches)"]
=======
    p35 --> p4["Phase 4 — Post-implementation maintenance (both branches)"]
    p2a -.->|"raised at planning, before approval"| p2b
    p3a -.->|"a trigger the plan missed: re-plan"| p2b
    p2b -.->|"re-plan approved"| p3b
>>>>>>> NEW
<<<<<<< OLD 1
Planning gates too: `risk-planner` (Phase 2B, same strong-reasoning pin) is mandatory for SIGNIFICANT/HIGH-RISK work, and can itself return a `### Re-classification` down to SIMPLE/MODERATE — the user confirms before falling back to Phase 2A.
=======
Clarification (Phase 1) looks in the inputs, the code, the repository's own docs and `git log` before it asks, and asks only what would change the result. Planning gates too: `risk-planner` (Phase 2B, same strong-reasoning pin) is mandatory for SIGNIFICANT/HIGH-RISK work, and can itself return a `### Re-classification` down to SIMPLE/MODERATE — the user confirms before falling back to Phase 2A. The class also moves up: Phase 2A re-tests it against its own plan, before you approve it and after every revision — after a down-classification you accepted at plan approval, only on a trigger a later revision adds — and raises it, on to `risk-planner`, where the plan shows a classification trigger — more than 3–5 non-test files, authentication, a schema or migration, a public contract (the dotted `p2a` → `p2b` edge); and a SIMPLE/MODERATE run that meets such a trigger while implementing, one its approved plan did not state (one of the concrete triggers the [classification policy](../reference/model-routing.md) lists, not its catch-all of unclear requirements, large unknowns or otherwise high blast radius, whose unknowns are asked about instead), stops editing and re-plans with `risk-planner` from the diff so far, continuing on the review path once you approve, without re-branching or re-capturing the baseline (the dotted `p3a` → `p2b` → `p3b` edges); cancelling that re-plan commits the work, and any pull request the run opens is a draft. That happens once per run: should you accept a down-classification at the re-plan, a later trigger is put to you instead — continue without the review, or stop, which commits the work as cancelling the re-plan does.
>>>>>>> NEW
<<<<<<< OLD 1
**An optional ARD** (Phase 1.8,
=======
**An optional ARD** (resolved at the start of Phase 1's clarification, which reads its rules; Phase 1.8,
>>>>>>> NEW
<<<<<<< OLD 1
whose synthesized summary feeds `risk-planner` instead of the single Explore subagent.
=======
whose synthesized summary feeds `risk-planner` instead of the single Explore subagent. Run it from inside the repository it is to change: it changes the repository it is run from, and started outside every git work tree it stops before planning, naming where to run it from. An `@path` at a repository's top level is read as a code repository, with a notice where it also holds `prompt.md` or `*-design.md` files (name those by file to read them), and the run stops there where nothing else describes the work. The run changes code only in the repository you run it from: every other code repository it is given is read-only context, and the changes one of them needs become one follow-up for that repository: a task Phase 6 files on a keyed run that finishes (a direct run lists it in its report), named in the stop message on one that stops after plan approval. Where the plan changes no file in this repository at all, the run asks, in place of plan approval, whether to revise the plan or stop with nothing written, naming the run each other repository needs.
>>>>>>> NEW
<<<<<<< OLD 1
`BLOCK` invokes `review-fixer` for BLOCKER/MAJOR findings,
=======
`BLOCK` invokes `review-fixer` for BLOCKER/MAJOR findings whose fix lies in this repository (one whose fix lies in another code repository is recorded as a follow-up instead, and a `BLOCKER` among them stops the run as a review that stayed blocked),
>>>>>>> NEW
`````

#### `edits/ce-npo.txt`

`````text
<<<<<<< OLD 1
- `implement: <VI> <Epic>` → finish remaining Epics (breadth); once ALL Epics implemented →
=======
- `implement: <VI> <Epic>` → first, where it recorded a change another code repository needs, the run from that repository, addressed to the unit the run implemented (the Epic itself, where it was one); then finish remaining Epics (breadth); once ALL Epics implemented →
>>>>>>> NEW
`````

#### `edits/code-review.tpl`

`````text
<<<<<<< OLD 1
  user-approved equivalent).
- **Diff**
=======
  user-approved equivalent) — where the user approved `{{IMPL}}`'s mid-implementation re-plan, two
  plans under headings — the re-plan's Steps are the work remaining, every Review focus line in either plan
  applies, and the re-plan governs only where two items contradict.
- **Diff**
>>>>>>> NEW
<<<<<<< OLD 1
- **Project root** - absolute path so files can be opened.
=======
- **Project root** - absolute path so files can be opened.
- **Deferred to another code repository** (optional, from `{{IMPL}}`) — changes the run records as another code repository's work, never this diff's: each is an explicit deferral note, which dimension 10 honours where a spec is in scope. The deferred change's absence is never a defect of this diff; whether this diff is safe to merge and deploy before that change lands is still this review's to judge.
>>>>>>> NEW
`````

#### `edits/doc-model-routing.tpl`

`````text
<<<<<<< OLD 1
before implementation starts, then add a separate
=======
before implementation starts — or, for `{{IMPL}}`, mid-implementation, where a raise calls for it (below) — then add a separate
>>>>>>> NEW
<<<<<<< OLD 1
genuinely smaller than its input footprint suggests.
=======
genuinely smaller than its input footprint suggests.

`{{IMPL}}`'s class can also rise after Phase 1.5, before any file is written: Phase 2A re-tests it against the ordinary triggers once its plan names the steps and files the change touches, and again after every revision of that plan — after a down-classification you accepted at plan approval, only on a trigger a later revision adds, so the re-test never undoes your acceptance. A raise is overridable at plan approval exactly as the floor is. A run planned as `SIMPLE`/`MODERATE` that first meets, while implementing, a trigger its plan did not name (one of the classification policy's concrete triggers, such as a schema or migration, authentication, a public contract, concurrency or more than 3–5 non-test files; not its catch-all of unclear requirements, large unknowns or otherwise high blast radius, whose unknowns are asked about instead) is raised too and re-planned with `risk-planner` — and, should you accept a down-classification there, continues on its plan at the lower class.
>>>>>>> NEW
<<<<<<< OLD 1
## What floors a classification
=======
## What floors or raises a classification
>>>>>>> NEW
`````

#### `edits/ed-doc-references.txt`

`````text
<<<<<<< OLD 1
the push and the pull request sit behind one consent choice, asked once per run.
=======
the push and the pull request sit behind one consent choice, asked once per run. The pull request's body holds a Summary, the before and the after the run observed as Evidence, a Merge danger call — a one-way or two-way door, and its blast radius — and the Review; where the repository carries one pull-request template at a path the reference lists, the body is that template, filled.
>>>>>>> NEW
`````

#### `edits/ed-doc-upgrade.txt`

`````text
<<<<<<< OLD 1
as each component's gates settle (step 6.5)
=======
as each component's gates settle (step 6.5; a commit that does not land, because a hook rejects it or git fails to stage or write it, ends the batch there, leaving that component's changes uncommitted, later components unrun and any pull request a draft)
>>>>>>> NEW
`````

#### `edits/ed-implement.txt`

`````text
<<<<<<< OLD 1
Remove it with `command rm -f -- "<summary_file>"` once Phase 2B has read it and no later phase cites it.
=======
Phase 4.6 removes it with the run's other temp files, since Phase 3A step 5's re-plan may read it again after Phase 2B has.
>>>>>>> NEW
<<<<<<< OLD 1
3. **Run linters and builds.** Use the project's standard lint/build commands as discovered in Phase 2A exploration.
=======
3. **Run linters and builds.** Use the project's standard lint/build commands as discovered by whichever codebase exploration this run actually performed — Phase 2A's subagent, Phase 2B's Explore subagent, or the Phase 1.7 fan-out summary — and, where none of them named one, read them from the repo's own build/lint configuration at its top level: Phase 3B step 8 re-enters this step on runs where Phase 2A's exploration never ran. Run each from the directory the exploration found it in, in a subshell so the session's own directory never moves: `(builtin cd "<top level>/<dir>" >/dev/null && <command>)`, `<top level>/<dir>` being the top level itself unless the exploration said otherwise.
>>>>>>> NEW
<<<<<<< OLD 1
This command has exits that stop *after* Pre-Phase 3 created the branch and after files were written: the two unreadable-`test_diff_file` stops (Phase 3.5 step 2, Phase 3B step 4a), the Cancel arms of the framework and repro prompts and of both Phase 3.5 prompts (step 5's unverified-run prompt and step 6's regression prompt), the unreadable-`review_diff_file` stop (Phase 3B step 6), the `review-fixer` `NEEDS HUMAN` stop, a review that stayed blocked (Phase 3B step 7, or step 8's review of the Phase 3.5 delta), and the **Keep the verdict** and **Cancel** arms of either of
=======
This command has exits that stop *after* Pre-Phase 3 created the branch: the **Cancel** arm of Pre-Phase 3.5's framework prompt, before the first edit — this phase finds nothing to stage there, and still names any `stash_ref` — and, after files were written, the two unreadable-`test_diff_file` stops (Phase 3.5 step 2, Phase 3B step 4a), the **Cancel** arms of both Phase 3.5 prompts (step 5's unverified-run prompt and step 6's regression prompt), the unreadable-`review_diff_file` stop (Phase 3B step 6), the `review-fixer` `NEEDS HUMAN` stop, a review that stayed blocked (Phase 3B step 7, or step 8's review of the Phase 3.5 delta), the **Cancel** arm of Phase 3B step 7's `### Re-classification` prompt, the **Cancel** arm of each of Phase 2B's three prompts — the re-classification prompt, the repro prompt and the plan-approval prompt — when Phase 3A step 5's re-plan reached it, the **Stop** arm of that step's question on a trigger met after the re-plan, and the **Keep the verdict** and **Cancel** arms of either of
>>>>>>> NEW
<<<<<<< OLD 1
The one exit that does **not** reach Phase 4.6 is the "Abandon implementation and restore to pre-impl state" arm, whose entire purpose is to discard the work; say so explicitly when taking it.
=======
**A stop before Pre-Phase 3 creates the branch is outside that set** — a Cancel at Phase 2B's prompts on any path but Phase 3A step 5's re-plan among them — since there is no branch for this phase to commit onto.
>>>>>>> NEW
<<<<<<< OLD 1
`command rm -f -- "<summary_file>" "<plan_file>" "<test_diff_file>" "<review_diff_file>"` — for whichever of those the run actually created and no stop message above still cites.
=======
`command rm -f -- "<summary_file>" "<plan_file>" "<partial_diff_file>" "<test_diff_file>" "<review_diff_file>"` — for whichever of those the run actually created and no stop message above still cites. A run that stops before Pre-Phase 3 removes the `summary_file` it wrote as it stops.
>>>>>>> NEW
`````

#### `edits/ed-upgrade-title.txt`

`````text
<<<<<<< OLD 1
`title` = `<KEY> upgrade <component> to <version>` for a single component, or `<KEY> upgrade <first> and <N> more` for a batch (dropping the key in a run with none)
=======
`title` = the commit subject step 6.5 wrote where it committed one component, or, where it committed several, `<KEY> upgrade <first> and <N> more` over those components alone, typed to the log's shape as step 6.5 types its subjects (dropping the key in a run with none; where it committed no component, the call opens no pull request and needs no title)
>>>>>>> NEW
`````

#### `edits/ie-npo.txt`

`````text
<<<<<<< OLD 1
/dev-workflows:implement <VI> <Epic>` → finish remaining Epics (breadth); once ALL Epics implemented →
=======
/dev-workflows:implement <VI> <Epic>` → first, where it recorded a change another code repository needs, the run from that repository, addressed to the unit the run implemented (the Epic itself, where it was one); then finish remaining Epics (breadth); once ALL Epics implemented →
>>>>>>> NEW
`````

#### `edits/impl-body.tpl`

`````text
<<<<<<< OLD 1
- `body_facts` — what was implemented; the files changed; the {{REVIEW}} verdict and triage summary where Phase 3B produced one; the `test-baseliner` verify result against the Pre-Phase 3.5 baseline; and every review finding `### Deferred items` lists as not applied — deferred `MINOR`/`NIT` findings and every survivor of a re-review, each with its severity.
=======
- `body_facts` — what §2.7's four sections render: what was implemented and the files changed (§2.7 item 1 reads them from git, on an early stop as on a finished run); every change another code repository needs (the plan's Out of scope or Phase 3A/3B step 2), named in the Summary as a companion change (saying which of the two must land first where the plan or the diff shows it, and that the order is unknown where neither does) and weighed in Merge danger's blast radius; as the evidence, the Pre-Phase 3.5 baseline before and the `test-baseliner` verify result after; on a `task_shape: bug` run whose plan carries a red repro, also that repro's command and output before (where the repro was taken at a mid-implementation re-plan, noting that it ran on the partial edits) and the regression test's result in the verify run after; the facts §2.7's door and blast-radius calls rest on, as the plan and the diff show them; and the classification, with the {{REVIEW}} verdict and triage summary where Phase 3B produced one and every review finding the run did not apply, each with its severity — deferred `MINOR`/`NIT` findings, a `MAJOR` or `BLOCKER` `review-fixer` deferred, every survivor whose fix lies in another code repository (Phase 3B step 7's *Another code repository's findings*), every survivor of a review that stopped before any fixer ran, and every survivor of a re-review — and, where Phase 3A step 5's **Continue** let a §1.1 trigger ship without the {{REVIEW}}, that trigger and the paths that show it, as the reason no review ran.
>>>>>>> NEW
`````

#### `edits/impl.tpl`

`````text
<<<<<<< OLD 1
**Rule: Ask, don't guess. This rule is absolute.**

Before producing a plan, analyze the description for:
- Ambiguous scope or unclear boundaries
- Missing constraints (performance, security, backwards-compatibility)
- Multiple valid implementation approaches
- Undefined integration points or dependencies
- Missing acceptance criteria

If **any** ambiguity exists, ask the user. Rules:
=======
**Rule: Look, then ask; never guess.** The description is the starting intent, however brief — never ask the user to restate it.

On a keyed run, first run Phase 1.8's ARD resolution — stopping as Phase 1.8 says on an `unmerged` result — so the look below can read the ARD's rules; Phase 1.8 acts on what it found.

Before producing a plan, list the candidate ambiguities in the description:
- Ambiguous scope or unclear boundaries
- Missing constraints (performance, security, backwards-compatibility)
- Multiple valid implementation approaches
- Undefined integration points or dependencies
- Missing acceptance criteria

**Look before asking.** Try to settle each candidate from what this run can read: the inputs Phase 0 resolved, the code, the repository's own {{REPODOCS}}, and `git log` — and, on a keyed run, the ARD's rules resolved above. Look only as far as each candidate needs — this is not the run's codebase exploration (Phase 1.7, 2A or 2B), which still runs as before. Then sort each candidate:
- **Settled by the reading** — missing evidence, not a decision: ask nothing, and carry it into the plan with where it was found.
- **Left open, and its answer changes what the user would notice in the result** — behaviour, scope, an interface, compatibility, a constraint nobody wrote down: a **decision**. Ask it.
- **Left open, and the user would not notice the answer** — settle it yourself and list it in the plan's Assumptions.

What the run settles reaches the plan either way: Phase 2A writes it into its own plan, and on the Phase 2B path the `risk-planner` brief carries it on its `Settled by the run:` line.

Ask every decision. Rules:
>>>>>>> NEW
<<<<<<< OLD 1
If **nothing** is ambiguous, skip directly to Phase 1.5.
=======
If no candidate is left a decision, skip directly to Phase 1.5.
>>>>>>> NEW
<<<<<<< OLD 1
**Wait for the agent's response before proceeding. If the agent returns no relevant files or fails, proceed with the plan using your own file reads to gather context. Do not begin writing the plan until the file map is returned or you have gathered context yourself.**
=======
**Where this phase was entered from a `### Re-classification` the user accepted at Phase 2B, skip this block — `summary_file` is the context. Otherwise, wait for the agent's response before proceeding. If the agent returns no relevant files or fails, proceed with the plan using your own file reads to gather context. Do not begin writing the plan until the file map is returned or you have gathered context yourself.**

**Write the exploration down** — save where this phase was entered from a `### Re-classification` the user accepted at Phase 2B, where `summary_file` already holds it: write the returned file map — or, where you gathered context yourself, what those reads found — to a temp file (`command mktemp -t dw-impl-summary-XXXXXX`, never inside a repo tree) and record its absolute path as `summary_file`.
>>>>>>> NEW
<<<<<<< OLD 1
**Codebase exploration** — If Phase 1.7 ran (`fan_out = true`), use its **multi-source codebase summary** (already written to `summary_file` in Phase 1.7 step 4) as the codebase context and skip the single Explore subagent. Otherwise,
=======
**Phase 3A step 5's re-plan also runs this phase**, from the `risk-planner` dispatch on, and that step says where each arm below leads on it.

**Codebase exploration** — If Phase 1.7 ran (`fan_out = true`), use its **multi-source codebase summary** (already written to `summary_file` in Phase 1.7 step 4) as the codebase context and skip the single Explore subagent. If Phase 2A's re-test raised the class, `summary_file` already holds this run's exploration: use it the same way, and skip the subagent likewise. Otherwise,
>>>>>>> NEW
<<<<<<< OLD 1
  > Classification: [SIGNIFICANT | HIGH-RISK] — reason: [the criterion from Phase 1.5, or the multi-source floor from Phase 1.6 when fan_out]
=======
  > Classification: [SIGNIFICANT | HIGH-RISK] — reason: [the criterion from Phase 1.5, the multi-source floor from Phase 1.6 when fan_out, or the raise — Phase 2A's re-test or Phase 3A step 5 — with its trigger and path]
>>>>>>> NEW
<<<<<<< OLD 1
  > Current state: branch = [git branch], uncommitted = [git status --short summary]
=======
  > Settled by the run: [each fact Phase 1's reading settled, with where it was found, which the plan cites in its Approach; and each open question the run settled itself — in Phase 1, or at Phase 3A step 5 before a re-plan — with what was chosen, which the plan lists under `### Assumptions`; or "none"]
  > Current state: branch = [git branch], uncommitted = [git status --short summary]
  > Work so far: [on Phase 3A step 5's re-plan only — read the diff at the `partial_diff_file` path: this run's uncommitted edits, part of this change, save what the paths Pre-Phase 3 recorded as `pre_existing_dirty` already held, which is somebody else's work — name those paths here, or "none"; and read the plan the user approved before it at the `plan_file` path; omit the line otherwise]
>>>>>>> NEW
<<<<<<< OLD 1
Accepting here is the user exercising the **plan-approval override** of the multi-source SIGNIFICANT floor (Phase 1.6); that is the sanctioned way to leave the fan_out floor.
=======
Accepting here is the user exercising the **plan-approval override** — of the multi-source SIGNIFICANT floor (Phase 1.6), or of a raise; that is the sanctioned way to leave either, and Phase 2A's re-test then runs only on what a later **Revise** adds. Record the revised class and its reason in the `model_routing` block.
>>>>>>> NEW
<<<<<<< OLD 1
5. If a **new ambiguity** emerges mid-implementation: STOP, ask with choices ({{CHOICES}}), resume after answer
=======
5. If something **new** emerges mid-implementation, look before stopping, and sort it:
   - **A §1.1 trigger the approved plan did not state** — a fact its Steps and Files did not name: a schema change or migration, an authentication or authorization path, a public contract, concurrency, the non-test files changed passing §1.1's 3–5, or any other item on {{MR}} §1.1's list that names something the work touches — never §1.1's last item, *Unclear requirements, large unknowns, or otherwise high blast radius*, whose unknowns are a decision, below, and whose blast radius counts only through the concrete items above; nor *Multi-source input*, which is Phase 1.6's — → **re-plan upward**, once per run:
     1. Stop editing. Raise the class to SIGNIFICANT (HIGH-RISK under §1.1's multiplier), announce `Re-classified upward during implementation: <trigger> (<the path, or the paths, that show it>)`, and record the new class and that reason in the `model_routing` block, resolving its `planning_model` and `review_model` where the block left them out.
     2. Write the diff so far — `git add -N . && git diff` — to a temp file (`command mktemp -t dw-impl-partial-XXXXXX`, never inside a repo tree) and record its absolute path as `partial_diff_file`.
     3. Ask Phase 1.5's task-shape question where it is genuinely ambiguous whether this is a defect fix or new work. Then run Phase 2B from its `risk-planner` dispatch on, with the complete brief: `summary_file` as its codebase summary, this raise as its classification reason, its `Constraints:` line also carrying every answer given at this step's decision arm, its `Settled by the run:` line also carrying every open question this step's last arm settled, with what was chosen and where in the code it arose, and its `Work so far:` line naming `partial_diff_file`, the `pre_existing_dirty` paths and the `plan_file` the user approved before it. Its arms lead where they always do, save these: **Approve** writes into `plan_file` both plans, opening with the line *The re-plan governs only where the two contradict, and its Steps are the work remaining (the earlier plan's Steps record what the diff so far was made under); every other item in either plan still stands, both plans' Review focus lines included* — the one approved before it, under `## Plan before the re-plan — the diff so far was made under it`, and the new one, under `## Re-plan — the rest` — and continues at Phase 3B step 1, working through the re-plan's Steps; Pre-Phase 3 and Pre-Phase 3.5 are not run again, and the baseline still predates every edit. **Accept revised classification** records the revised class as Phase 2B's acceptance does and resumes Phase 3A where it stopped, on the plan already approved — the trigger the re-plan was raised on, and its §1.1 item, count from then on as ones the approved plan states, so neither trigger arm of this step fires on them again. Each **Cancel** — the re-classification prompt's, the repro prompt's and the plan-approval prompt's — stops through Phase 4.6, since files are written (its `"Every run"` list). Every re-dispatch on this path — **Override**, **Revise**, **Help construct a repro** — carries the complete brief, its `Work so far:` line included.
   - **A §1.1 trigger the approved plan did not state, met after this run's one re-plan** → announce `Classification trigger after the re-plan: <trigger> (<the path, or the paths, that show it>)`, then ask `choices: ["Continue at the current class — this change ships without the {{REVIEW}}", "Stop here — the work so far is committed through Phase 4.6{{NOCOMMITQ}}"{{OTHER}}]`. **Continue** records the trigger in the Phase 5 report's `### Assumptions & limitations` and counts it, and its §1.1 item, as ones the approved plan states, as the re-plan's **Accept revised classification** does, so this arm does not fire on them again; **Stop** is in Phase 4.6's `"Every run"` list.
   - **A decision** — Phase 1's test: nothing this run can read settles it, and its answer changes what the user would notice in the result → STOP, ask with choices ({{CHOICES}}), resume after answer.
   - **Anything else** → look it up and continue; an open question the user would not notice is settled by the run and recorded in the Phase 5 report's `### Assumptions & limitations`.
>>>>>>> NEW
<<<<<<< OLD 1
4. If a **new ambiguity** emerges mid-implementation: STOP, ask with choices ({{CHOICES}}), resume after answer
=======
4. If something **new** emerges mid-implementation, look before stopping: **a decision** — Phase 1's test: nothing this run can read settles it, and its answer changes what the user would notice in the result → STOP, ask with choices ({{CHOICES}}), resume after answer; **anything else** → look it up and continue — an open question the user would not notice is settled by the run and recorded in the Phase 5 report's `### Assumptions & limitations`.
>>>>>>> NEW
<<<<<<< OLD 1
     > Classification: [SIGNIFICANT | HIGH-RISK] — reason: [from Phase 1.5]
=======
     > Classification: [SIGNIFICANT | HIGH-RISK] — reason: [as the `model_routing` block records it — Phase 1.5's criterion, the multi-source floor, or a raise]
>>>>>>> NEW
<<<<<<< OLD 1
[SIMPLE | MODERATE | SIGNIFICANT | HIGH-RISK] — [reason]
=======
[SIMPLE | MODERATE | SIGNIFICANT | HIGH-RISK] — [reason]
[each change of class after Phase 1.5, one line each: `<from> → <to>`, where it happened — the multi-source floor, at planning, during implementation, or a down-classification the user accepted at plan approval or at review — and why: for a raise, the trigger and the path, or the paths, that show it, as its announcement named them; omit these lines where the class never changed]
>>>>>>> NEW
<<<<<<< OLD 1
- NEVER make assumptions that could have been asked — ask instead
=======
- NEVER assume what the evidence leaves open and the user would notice — look first, then ask (Phase 1); NEVER ask what the repository already answers
>>>>>>> NEW
<<<<<<< OLD 1
Either way, `summary_file` holds an absolute path before the planner is dispatched.
=======
In every case, `summary_file` holds an absolute path before the planner is dispatched.
>>>>>>> NEW
<<<<<<< OLD 1
3. **Approach** — chosen strategy and why
=======
3. **Approach** — chosen strategy and why, citing each fact Phase 1's reading settled, with where it was found
>>>>>>> NEW
<<<<<<< OLD 1
Then ask:
```
"Implementation plan ready. What would you like to do?"
=======
**Re-test the class against the plan** — before asking, and again after every **Revise**, save where this phase was entered from a `### Re-classification` the user accepted at Phase 2B: that acceptance is the plan-approval override, which a re-test would undo, so there it runs only after a **Revise**, and only on a trigger the revision added — one the plan before it did not state. Test the class as it stands — the `model_routing` block's — again against {{MR}} §1.1, reading the plan's Steps and Files to create/modify and what the exploration found those files do. Where a §1.1 trigger now applies — more than 3–5 non-test files, authentication or authorization, a schema or migration, a public contract, concurrency, or any other item on that list — do not ask: raise the class to SIGNIFICANT (HIGH-RISK under §1.1's multiplier), announce `Re-classified upward at planning: <trigger> (<the path, or the paths, that show it>)`, record the new class and that reason in the `model_routing` block — resolving its `planning_model` and `review_model` where the block left them out — and continue at Phase 2B with `summary_file` as its codebase summary and every answer given at this phase's **Revise** on the brief's `Constraints:` line, with no second exploration; ask Phase 1.5's task-shape question first where it is genuinely ambiguous whether this is a defect fix or new work.

Then ask:
```
"Implementation plan ready. What would you like to do?"
>>>>>>> NEW
<<<<<<< OLD 1
- **Revise** → ask what to change, update, re-show, re-ask
- **Cancel** → stop and summarize what was planned

---

## Phase 2B
=======
- **Revise** → ask what to change, update, re-test the class against the plan as above — continuing at Phase 2B where it raises the class — otherwise re-show and re-ask, through *A plan with no step in this repository* where the revision leaves no step here
- **Cancel** → stop and summarize what was planned

---

## Phase 2B
>>>>>>> NEW
<<<<<<< OLD 1
— the Phase 1.7 **multi-source codebase summary** when `fan_out = true`, otherwise the Explore summary —
=======
— whichever of Phase 1.7's **multi-source codebase summary**, Phase 2B's Explore output or Phase 2A's exploration this run wrote —
>>>>>>> NEW
<<<<<<< OLD 1
**Codebase exploration** — Before writing the plan, spawn an exploration subagent to map the relevant parts of the codebase:
=======
**Codebase exploration** — Before writing the plan, spawn an exploration subagent to map the relevant parts of the codebase — save where this phase was entered from a `### Re-classification` the user accepted at Phase 2B, where `summary_file` already holds the exploration and nothing is dispatched:
>>>>>>> NEW
<<<<<<< OLD 1
→ Use the returned file map as codebase context when writing the plan below.
=======
→ Use the returned file map — or, where this phase was entered from an accepted `### Re-classification`, `summary_file` — as codebase context when writing the plan below.
>>>>>>> NEW
<<<<<<< OLD 1
7. **Assumptions** — decisions made without user input (must be minimal)
=======
7. **Assumptions** — each open question the run settled itself because the user would not notice the answer (Phase 1's test) — in Phase 1 or while writing this plan — with what was chosen (must be minimal)
>>>>>>> NEW
<<<<<<< OLD 1
  > Constraints: [any from clarification, plus runtime/version/deadline known]
=======
  > Constraints: [any from clarification, every answer given at Phase 2A's **Revise** before a raise, plus runtime/version/deadline known — and always: this run changes code only in [the working directory's repository top level, `git rev-parse --show-toplevel`]; a change any other code repository needs goes under Out of scope; run every command from that top level]
>>>>>>> NEW
<<<<<<< OLD 1
If overridden, re-invoke code-review with an explicit note that the classification is intentional.
=======
If overridden, re-invoke code-review with an explicit note that the classification is intentional. If the user cancels, stop through Phase 4.6 — its `"Every run"` list.
>>>>>>> NEW
<<<<<<< OLD 1
9. Verify the outcome matches the approved plan and the review verdict.
=======
9. Verify the outcome matches the approved plan — on a run whose re-plan the user approved, both, as `plan_file`'s opening line reads them — and the review verdict.
>>>>>>> NEW
<<<<<<< OLD 1
names in its `### Notes` why one cannot be written (Phase 3.5)
=======
names in its `### Notes` why one cannot be written (Phase 3.5, or Phase 3B step 4a on a run whose re-plan the user approved)
>>>>>>> NEW
<<<<<<< OLD 1
- [review findings that were not applied — MINOR / NIT, and every survivor of a re-review, with its severity; omit the line where there are none]
=======
- [review findings that were not applied — MINOR / NIT, a MAJOR or BLOCKER `review-fixer` deferred, every survivor whose fix lies in another code repository (Phase 3B step 7's *Another code repository's findings*), and every survivor of a re-review, with its severity; omit the line where there are none]
>>>>>>> NEW
<<<<<<< OLD 1
 — i.e. NOT direct-prompt mode — resolve any ARD by
=======
 — i.e. NOT direct-prompt mode — the ARD is resolved (at the start of Phase 1, or here where Phase 1 did not) by
>>>>>>> NEW
<<<<<<< OLD 2
2. Make precise, surgical changes — do not modify unrelated code
=======
2. Make precise, surgical changes — do not modify unrelated code — and change code only in the repository Pre-Phase 3 branched: any other code repository, one this run was given included, is read-only context, and a change one needs goes into the Phase 5 report's `### Session learnings`, on that repository's one follow-up line for `{{QIMPL}}` run from there, addressed to the unit this run implemented (the Epic itself, where it was one; no key on a direct run), which Phase 6 collects; an early stop names it beside its §3.1 line instead (Phase 4.6)
>>>>>>> NEW
<<<<<<< OLD 1
8. **Out of scope** — explicitly list what is NOT being done
=======
8. **Out of scope** — explicitly list what is NOT being done, a change another code repository needs included (this run changes code only in the repository it branches)
>>>>>>> NEW
<<<<<<< OLD 1
**A run that wrote into a repo it never branched.** A multi-source run (Phase 1.7) may edit a repo other than the one Pre-Phase 3 branched. This step has no branch there to commit onto, so it does not invent one: list those repos and their dirty paths in the Phase 5 report under `### Branch`, explicitly flagged as uncommitted. Never leave them unmentioned — an unreported dirty repo is exactly the loss this phase exists to prevent.
=======
**No other code repository is written.** A multi-source run (Phase 1.7) may read several code repositories but changes code only in the one Pre-Phase 3 branched (Phase 3A and 3B step 2, and the invariants), so every code change it made is this phase's to commit; a change another code repository needs is a follow-up (Phase 6's, or named beside the stop's §3.1 line on an early stop), never an uncommitted edit there.
>>>>>>> NEW
<<<<<<< OLD 1
[the Phase 4.6 `Code repo:` outcome line, verbatim ({{CH}} §3.1)]
[any repo this run wrote into but never branched — path + dirty paths, flagged uncommitted; omit the line when there is none]
=======
[the Phase 4.6 `Code repo:` outcome line, verbatim ({{CH}} §3.1)]
>>>>>>> NEW
<<<<<<< OLD 1
- [top suggestions from impl-maintenance agent, or "no suggestions — routine session"]
=======
- [top suggestions from impl-maintenance agent, or "no suggestions — routine session"]
- [one line per other code repository a change is needed in (the plan's Out of scope or Phase 3A/3B step 2), naming each change — a follow-up for `{{QIMPL}}` run from that repository, addressed as Phase 3A/3B step 2 says; omit the line where there is none]
>>>>>>> NEW
<<<<<<< OLD 1
1. **Collect** the qualifying follow-ups: manual publish/config steps and
=======
1. **Collect** the qualifying follow-ups: one per other code repository a change is needed in (the plan's Out of scope or Phase 3A/3B step 2), listing each change this run found there, manual publish/config steps and
>>>>>>> NEW
<<<<<<< OLD 1
Report the §3.1 line with the stop, not in a Phase 5 report that will not be produced.
=======
Report the §3.1 line with the stop, not in a Phase 5 report that will not be produced, and name beside it everything Pre-Phase 3's opening sentence lists, since neither Phase 4.5, Phase 5 nor Phase 6 will run.
>>>>>>> NEW
<<<<<<< OLD 1
— guidance only, never auto-invoked.
=======
— guidance only, never auto-invoked. On a keyed run, where this run found a change another code repository needs (the plan's Out of scope or Phase 3A/3B step 2), name first a `{{QIMPL}}` run from that repository, addressed as Phase 3A/3B step 2 says, before any documentation step; a direct run, which omits this section, names that change in `### Session learnings` alone.
>>>>>>> NEW
<<<<<<< OLD 1
- NEVER skip Phase 1.5 classification — every run must state the level
=======
- NEVER skip Phase 1.5 classification — every run must state the level
- NEVER change code in a code repository other than the one Pre-Phase 3 branched — not in Phase 3A or 3B, not in Phase 3.5's fixes, not through `review-fixer`; a change another code repository needs is recorded as Phase 3A/3B step 2 says
>>>>>>> NEW
<<<<<<< OLD 1
> Diff: read it from the file at [the `review_diff_file` path from step 5]
=======
> Diff: read it from the file at [the `review_diff_file` path from step 5]
     > Deferred to another code repository: [each change another code repository needs (the plan's Out of scope or Phase 3A/3B step 2), as an explicit deferral note — omit where none]
>>>>>>> NEW
<<<<<<< OLD 1
**Review-fixer sub-step** (for BLOCK and PASS WITH RECOMMENDATIONS): first write the **triaged survivor list** from the sub-step above
=======
**Another code repository's findings** (after the triage sub-step, on every review and re-review): record each survivor whose fix lies in another code repository as Phase 3B step 2 says (the invariants), and hand it to no fixer; it is a finding the run did not apply. A `BLOCKER` among them is one this run cannot fix, whatever else survives: the review stayed blocked, so stop as the BLOCK bullet's stayed-blocked stop does, naming the repository each such fix lies in and every other survivor, which no fixer was handed, with no fixer dispatch and no re-review. On the first review, where at least one survivor was recorded so and no `BLOCKER` or `MAJOR` is left for the fixer, dispatch none: on PASS WITH RECOMMENDATIONS, continue to step 7.5; on BLOCK, ask {{FT}}'s first settle prompt (§ When triage empties the survivor set), reporting every survivor (those recorded for another code repository, and any `MINOR` or `NIT` left here) in place of its *nothing survived*, and act on its answer as the triage sub-step does.

   **Review-fixer sub-step** (for BLOCK and PASS WITH RECOMMENDATIONS): first write the **triaged survivor list** from the sub-step above, less the findings the paragraph above recorded for another code repository
>>>>>>> NEW
<<<<<<< OLD 1
Project root: [absolute path of the current working directory]
=======
Project root: [the repository's top level, `git rev-parse --show-toplevel` — every diff this run captures is relative to it]
>>>>>>> NEW
<<<<<<< OLD 5
Project root: [absolute path]
=======
Project root: [the repository's top level, `git rev-parse --show-toplevel` — every diff this run captures is relative to it]
>>>>>>> NEW
<<<<<<< OLD 1
repo_path: <absolute repo path>
=======
repo_path: <the repo's top level — `git -C <path> rev-parse --show-toplevel` of the path Phase 0 classified>
>>>>>>> NEW
<<<<<<< OLD 1
Given this implementation description: [paste the full implementation description from Phase 0 or Phase 1 here], find and return:
=======
Given this implementation description: [paste the full implementation description from Phase 0 or Phase 1 here], find in the repository at [its top level, `git rev-parse --show-toplevel`] (starting from [every `@path` the input named that shares its top level, and the working directory where it lies below the top level, each relative to that top level — omit where neither]) and return:
>>>>>>> NEW
<<<<<<< OLD 2
in the project root
=======
in the project root (the repository's top level, `git rev-parse --show-toplevel`)
>>>>>>> NEW
<<<<<<< OLD 1
- **Specify test command** → take free-text, record it as `test_command_hint`,
=======
- **Specify test command** → when asking, tell the user that a command matching a suite the capture detected runs in that suite's own directory and any other from the repository's top level (name it), so one meant for a subdirectory with no detected suite begins `cd <dir> &&` (`dev-workflows:test-baseliner` capture step 1, *Scope*); take free-text and record it verbatim as `test_command_hint`,
>>>>>>> NEW
<<<<<<< OLD 1
explicitly excludes those as in-scope work already carried by the current task.
=======
explicitly excludes those as in-scope work already carried by the current task. A finding whose fix lies in another code repository is the exception: the first clause above collects it.
>>>>>>> NEW
<<<<<<< OLD 1
(project-level, preferred for repo-specific knowledge)
=======
(project-level, at the repository's top level from `git rev-parse --show-toplevel`, preferred for repo-specific knowledge)
>>>>>>> NEW
<<<<<<< OLD 1
- `repo_count` = number of code repos (cwd + referenced git-repo dirs)
=======
- `repo_count` = number of distinct code repositories (cwd + referenced git-repo dirs), counted by top level (`git -C <path> rev-parse --show-toplevel`), so an `@path` whose top level is already counted adds none
>>>>>>> NEW
<<<<<<< OLD 1
For each code repo:
=======
For each distinct code repository (an `@path` sharing its top level adds that path to its scanner's `search_hints`, never a second scanner):
>>>>>>> NEW
<<<<<<< OLD 1
search_hints: <symbols/paths/keywords derived from the spec, if any>
=======
search_hints: <symbols/paths/keywords derived from the spec, plus every `@path` sharing this repository's top level and, for the working directory's repository, the working directory where it lies below the top level, each relative to that top level, if any>
>>>>>>> NEW
<<<<<<< OLD 1
uncommitted = [git status --short summary]
=======
uncommitted = [`git -C <top level> status --short --untracked-files=normal` summary]
>>>>>>> NEW
<<<<<<< OLD 1
on the ground that they are in-scope work already carried by this task — which holds only if they are written down here.
=======
on the ground that they are in-scope work already carried by this task — which holds only if they are written down here. The exception is a finding whose fix lies in another code repository, which Phase 6 collects as a Phase 3A/3B step 2 change.
>>>>>>> NEW
<<<<<<< OLD 1
| scan target in Phase 1.7 |
=======
| scan target in Phase 1.7 — or, where its top level (`git -C <path> rev-parse --show-toplevel`) is that of a code repository already classified here (the working directory's included), a search hint for that repository's scan and for Phase 2A/2B's exploration |

Test the rows top to bottom for each `@path` token: the first that matches classifies it, so a spec or specs folder below a repository's top level is that folder, never a code repo. The working directory, where `git rev-parse --is-inside-work-tree` succeeds there, and an `@path` that is its own work tree's top level (`git -C <path> rev-parse --show-prefix` succeeds and prints nothing), are always the Code repo row's whatever else they hold. A working directory outside every work tree stops the run: `{{IMPL}}` branches the repository it runs from, so run it from inside one. Where such a top level also matches the Spec folder row, print `<path> is a repository's top level and is read as a code repository — its prompt.md and *-design.md files are not read into the description; name them by file (@<path>/prompt.md) to read them`, and where nothing else gives the run a description, stop with that remedy.
>>>>>>> NEW
<<<<<<< OLD 1
WHEN `fan_out` is true (multi-repo or any directory input)
=======
WHEN `fan_out` is true (more than one distinct code repository, or a specs or spec/design folder)
>>>>>>> NEW
<<<<<<< OLD 1
run `git stash push -m "pre-impl stash"`
=======
run `git stash push -m "pre-impl stash" -- ':/' ':(top,exclude)<path>'`, one exclusion per `@path` input inside this repository, relative to its top level (tracked changes only, the run's own inputs left in place), and record every path it leaves dirty (`git status --porcelain -z --untracked-files=all` after it) as `pre_existing_dirty`, so {{CH}} §2.2's carve-out keeps them out of the commit unless this run edits one (they still appear in the diffs the agents read, as on **Proceed anyway**)
>>>>>>> NEW
<<<<<<< OLD 1
**If the return is a full plan** (ranking present, or the user chose to proceed without a repro)**:** present it to the user verbatim and ask:
=======
**If the return is a full plan** (ranking present, or the user chose to proceed without a repro)**:** present it to the user verbatim and ask:
>>>>>>> NEW
<<<<<<< OLD 1
Then ask:
```
"Implementation plan ready. What would you like to do?"
=======
**A plan with no step in this repository.** Where a plan written before any edit — this one as first written or after any **Revise**, or Phase 2B's full plan at its approval gate, never Phase 3A step 5's re-plan — changes no file in this repository (every change lying under Out of scope for another code repository, or none at all), there is nothing to implement here, and approving it would cut an empty branch. Present the plan and ask this in place of the approval question:

```
"This plan changes no file in this repository. What would you like to do?"
choices: ["Stop here, nothing written (Recommended)", "Revise plan"{{OTHER}}]
```

- **Stop** → name one follow-up per other code repository the plan puts a change in, if any — a `{{QIMPL}}` run from there, addressed as Phase 3A/3B step 2 says, listing its changes — and stop as **Cancel** does, nothing having been written.
- **Revise** → as the approval question's **Revise** does, in Phase 2A or Phase 2B, whichever wrote the plan.

Otherwise, ask:
```
"Implementation plan ready. What would you like to do?"
>>>>>>> NEW
<<<<<<< OLD 1
**If the return is a full plan whose `### Hypotheses (ranked)` section contains `Ranking withheld`:**
=======
**If the return is a full plan whose `### Hypotheses (ranked)` section contains `Ranking withheld`:**
>>>>>>> NEW
<<<<<<< OLD 1
Re-show, re-ask.
=======
Handle its return as above, every arm included.
>>>>>>> NEW
<<<<<<< OLD 1
**If the return is a full plan** (ranking present, or the user chose to proceed without a repro)**:** present it to the user verbatim and ask:
=======
**If the return is a full plan** (ranking present, or the user chose to proceed without a repro)**:** present it to the user verbatim and ask — or, where it has no step in this repository (never on Phase 3A step 5's re-plan), ask Phase 2A's *A plan with no step in this repository* question in its place:
>>>>>>> NEW
<<<<<<< OLD 1
## Pre-Phase 3 — Create feature branch
=======
## Pre-Phase 3 — Create feature branch

Every stop from here to the end of the run names, beside whatever else it reports, each change another code repository needs that the run has found (the plan's Out of scope or Phase 3A/3B step 2), one line per repository, and, once step 7.5 has run, every gap it reported without a note (a spec step 7.5 may not annotate) and every note it wrote into `$SPECS_PATH`, uncommitted there until handed off or removed.
>>>>>>> NEW
<<<<<<< OLD 1
never mutate existing `[Uxx]`/`[ACxx]`/`[TCxx]` IDs). Never silently drop them,
=======
never mutate existing `[Uxx]`/`[ACxx]`/`[TCxx]` IDs). Only a `specification.md` or `design.md` in `$SPECS_PATH`, or in this repository at a path git does not ignore (`git -C "<top level>" check-ignore -q -- <path>` exits 1), is annotated; one anywhere else — inside another code repository, which Phase 3A/3B step 2 keeps this run from writing, at an ignored path no commit would carry, or outside every repository — gets no note, the Phase 5 report's `### Spec/design conformance` section carrying the gap instead, or, on an early stop, the stop's own message (Pre-Phase 3). Never silently drop them,
>>>>>>> NEW
<<<<<<< OLD 1
and do not re-run exploration.
=======
and do not re-run exploration; every answer given at a **Revise** so far (Phase 2A's before a raise, or this gate's own) binds the plan the run continues on — the new Phase 2A plan honours it, and on Phase 3A step 5's re-plan, where the run resumes on its approved plan, Phase 3A follows it as a constraint.
>>>>>>> NEW
<<<<<<< OLD 1
then continue. Record the resulting stash as `stash_ref`
=======
then continue — or, where git refuses the stash, show its error and stop as **Cancel** does, nothing branched yet. Record the resulting stash as `stash_ref`, where git made one (`No local changes to save` makes none)
>>>>>>> NEW
<<<<<<< OLD 1
A **silent no-op** when step 7.5 (Phase 3B) wrote no `- [ ]` notes
=======
A **silent no-op** when step 7.5 (Phase 3B) wrote no `- [ ]` notes in `$SPECS_PATH` — a note it wrote in this repository rides on Phase 4.6's commit instead (and stays in the working tree under `--no-commit`)
>>>>>>> NEW
<<<<<<< OLD 1
`deliverable_paths` = the annotated file(s) themselves.
=======
`deliverable_paths` = the annotated file(s) in `$SPECS_PATH`.
>>>>>>> NEW
<<<<<<< OLD 1
escalate unresolved `missing`/`contradicts` as `- [ ]` notes on the spec/design
=======
escalate unresolved `missing`/`contradicts` as `- [ ]` notes on the spec/design where it lies in `$SPECS_PATH` or this repository, and, where it lies elsewhere, in the Phase 5 report or an early stop's message
>>>>>>> NEW
<<<<<<< OLD 1
re-dispatch `risk-planner` with it carried in the brief, and re-enter this branch on the new return.
=======
re-dispatch `risk-planner` with it carried in the brief, and handle the new return as above, every arm included.
>>>>>>> NEW
<<<<<<< OLD 1
stating the classification is intentional; do not down-classify again.
=======
stating the classification is intentional, and handle its return as above, every arm included — a `### Re-classification` it returns despite the constraint is the user's to settle again.
>>>>>>> NEW
<<<<<<< OLD 1
"Stash changes and continue (Recommended)", "Proceed anyway — pre-existing changes will appear in the diff and review outputs"
=======
"Stash tracked changes and continue (Recommended)", "Proceed anyway — pre-existing changes will appear in the diff and review outputs"
>>>>>>> NEW
<<<<<<< OLD 1
a. Run `git diff --stat` (or equivalent) and capture the list of changed files with line counts.
=======
a. Run `git add -N :/ && git diff --numstat -z` and capture the files this run has changed so far, each path whole and raw with its added and removed line counts, less every `pre_existing_dirty` path this run did not edit (both in `-z` form, as {{CH}} §2.2 compares them). Phase 4's own edits come after it, so the pull request's list is {{CH}} §2.7 item 1's, read from git, not this one.
>>>>>>> NEW
<<<<<<< OLD 1
Files changed (from git diff --stat):
<paste the git diff --stat output>
=======
Files changed so far (step a):
<step a's paths with their line counts, one per line>
>>>>>>> NEW
<<<<<<< OLD 1
### Files changed
- path/to/file.ext — [what changed]
=======
### Files changed
[the paths this run changed, Phase 4's edits included: those Phase 4.6's commits carry, read from git as {{CH}} §2.7 item 1 says, where it committed them; otherwise — a §2.1 gate failure, a `git add` git refused, a commit a hook or git rejected, `--no-commit` — the `git status --porcelain -z --untracked-files=all` set taken after Phase 4, less each ` D` record for a path `HEAD` does not hold (the intent-to-add entry {{CH}} §2.2 carve-out 1 drops), less every `pre_existing_dirty` path this run did not edit]
- path/to/file.ext — [what changed]
>>>>>>> NEW
<<<<<<< OLD 1
non-test files changed passing §1.1's 3–5
=======
non-test files this run changed (never a `pre_existing_dirty` path it did not edit) passing §1.1's 3–5
>>>>>>> NEW
<<<<<<< OLD 1
When step 7.5 did write one or more notes:
=======
When step 7.5 did write one or more notes in `$SPECS_PATH` — the set this phase reads throughout:
>>>>>>> NEW
<<<<<<< OLD 1
— this includes intent-to-add untracked new files so the diff is never empty for implementations that only create new files,
=======
— this includes intent-to-add untracked new files and, through `--ignore-removal` and the diff against `HEAD` (the empty tree before a first commit), every deletion, so the diff is never empty for implementations that only create or delete files,
>>>>>>> NEW
<<<<<<< OLD 1
the code-review dispatch (step 6) receives this path. Also capture `git diff --stat` for the summary (small — kept inline).
=======
the code-review dispatch (step 6) receives this path.
>>>>>>> NEW
<<<<<<< OLD 1
1. **Clean-tree check** — Run `git status --porcelain`. If the output is non-empty:
=======
1. **Clean-tree check** — Run `git status --porcelain -z --untracked-files=all`, which lists untracked files whatever the user's `status.showUntrackedFiles`. If the output is non-empty:
>>>>>>> NEW
<<<<<<< OLD 1
paste the `git status --short` output
=======
paste the `git status --short --untracked-files=normal` output, which shows untracked files whatever the user's `status.showUntrackedFiles` and an untracked directory as one line
>>>>>>> NEW
<<<<<<< OLD 1
Record which of `specification.md`/`design.md` actually received a note — the handoff step needs to know whether only one, or both, were annotated. The notes are written here and handed off later — see the escalation handoff after Phase 4.
=======
Record which of `specification.md`/`design.md` in `$SPECS_PATH` received a note — Phase 4.5 needs to know whether only one, or both, were annotated. A note in `$SPECS_PATH` is written here and handed off later (see the escalation handoff after Phase 4); a note in this repository rides on Phase 4.6's commit, or stays in the working tree under `--no-commit`.
>>>>>>> NEW
<<<<<<< OLD 1
the spec/design conformance notes from step 7.5 are handed off separately, also before this phase,
=======
the spec/design conformance notes step 7.5 wrote into `$SPECS_PATH` are handed off separately, also before this phase (one it wrote into this repository went with the implementation's commit, or stays in the working tree under `--no-commit`),
>>>>>>> NEW
`````

#### `edits/repopath-3.txt`

`````text
<<<<<<< OLD 3
[absolute repo path]
=======
[the repository's top level, `git rev-parse --show-toplevel`]
>>>>>>> NEW
<<<<<<< OLD 1
uncommitted = [git status --short summary]
=======
uncommitted = [`git -C <top level> status --short --untracked-files=normal` summary]
>>>>>>> NEW
`````

#### `edits/repopath-4.txt`

`````text
<<<<<<< OLD 4
[absolute repo path]
=======
[the repository's top level, `git rev-parse --show-toplevel`]
>>>>>>> NEW
<<<<<<< OLD 1
Note the repo path and,
=======
Note the repo path, its top level (`git rev-parse --show-toplevel`), and,
>>>>>>> NEW
`````

#### `edits/risk-planner.tpl`

`````text
<<<<<<< OLD 1
- **Current state** - git branch, uncommitted changes, test baseline if any.
=======
- **Current state** - git branch, uncommitted changes, test baseline if any.
- **`Settled by the run`** (optional) — from `{{IMPL}}`: what the run settled before this plan — each fact its reading found, with where it was found, and each open question it settled itself, in Phase 1 or, on a re-plan, while implementing. Plan from the first as facts, citing each in `### Approach` with where it was found; list the second under `### Assumptions`, so the user sees each one at plan approval.
- **`Work so far`** (optional) — from `{{IMPL}}`'s Phase 3A step 5 re-plan: the absolute path to a diff of the run's uncommitted edits so far, made under an earlier plan the user approved. `{{READ}}` the diff first. Those edits are part of this change and stay: plan the rest of the task from the tree as it stands — a step may revise what the diff wrote, and the plan never assumes a clean tree. Your Steps carry every step of the earlier plan the diff shows not done, since `{{IMPL}}` works through yours alone; the run changes code only in the repository the brief's `Constraints:` line names, so a change any other code repository needs goes under Out of scope. The `pre_existing_dirty` paths the line names are the exception to those edits being this change's: what they held before the run began is somebody else's uncommitted work, which the plan neither reverts nor counts as this change's — a step may still edit such a file where the task needs it, as the earlier plan could. The line also names that earlier plan's path: `{{READ}}` it too, keep its Out of scope and Assumptions unless the trigger forces a change, and name every change to them under `### Assumptions` — `{{IMPL}}` merges the two plans, yours governing only where the two contradict and your Steps being the work remaining — every other item in either still stands, both plans' Review focus lines included. On a read failure of either path, follow the **read-failure contract** in {{CMR}} — each is *context*: an unreadable diff degrades to absent, the edits staying in the working tree, where `Current state` still names them; an unreadable earlier plan degrades to absent alone — and name the unreadable path in the plan's `### Risks`. On a bug-shaped task those edits may already turn the repro green; that is the withheld ranking `task_shape` describes below, with what you tried.
>>>>>>> NEW
<<<<<<< OLD 1
a plan is produced **before** the user has approved any action, and running a mutating command there would act ahead of that approval.
=======
a plan is produced **before** the user has approved it, and running a mutating command there would act ahead of that approval.
>>>>>>> NEW
`````

#### `edits/test-writer.tpl`

`````text
<<<<<<< OLD 1
- **Plan** — the approved plan from Phase 2A (standard) or the risk-planner plan from Phase 2B (Opus)
=======
- **Plan** — the approved plan from Phase 2A (standard) or the risk-planner plan from Phase 2B (Opus) — or, where the user approved `{{IMPL}}`'s mid-implementation re-plan (its Phase 3A step 5), both, under two headings — the re-plan's Steps are the work remaining, every Review focus line in either plan applies, and the re-plan governs only where two items contradict
>>>>>>> NEW
`````

#### `edits/upgrade-maint.txt`

`````text
<<<<<<< OLD 1
key failures or workarounds, and the overall result.
=======
key failures or workarounds, the overall result, and the project root (the repository's top level, `git rev-parse --show-toplevel`).
>>>>>>> NEW
<<<<<<< OLD 1
Upgrade [component] from [current] to [target] in this repo.
=======
Upgrade [component] from [current] to [target] in the repository at [its top level, `git rev-parse --show-toplevel`].
>>>>>>> NEW
`````

#### `edits/upgrade.tpl`

`````text
<<<<<<< OLD 1
`body_facts` = the Upgrade Summary rows, each component's classification and review verdict, and the test result against the Phase 2 prep baseline;
=======
`body_facts` = what §2.7's four sections render, scoped as `title` is to the components step 6.5 committed (each other component named in the Summary as not committed or not run, with why): the Upgrade Summary rows and the files changed (§2.7 item 1, over the components it committed); as the evidence, each component's version before and after, and the test result against the Phase 2 prep baseline, naming each regression a component kept and each test a `NEW-FAILURE: ` note marks; the facts §2.7's door and blast-radius calls rest on — what in this repository depends on each component, as `git -C "<repo>" grep -l <package-or-import-name> -- ':/'` shows it (`:/`, so the search covers the whole tree), and whether its new version migrates or rewrites anything persisted, as its upgrade plan (its `files:` and `related:`) and the diff show it, or that none of them shows it, which §2.7 reads as one-way; and each component's classification, review verdict and triage summary, with every review finding not applied and its severity;
>>>>>>> NEW
<<<<<<< OLD 1
**"Stop and escalate" on a review that stayed blocked stops the component, not the run.**
=======
**A commit that does not land stops the run's loop, not only the component**, whether a hook rejected it or git failed to stage or write it ({{CH}} §2.12, §2.2, §2.3): record this component as not committed, with the hook's output or git's error, and every later component as not run, in step 7's table, then go to step 7.5, whose terminal call commits nothing in this component's place.

   **"Stop and escalate" on a review that stayed blocked stops the component, not the run.**
>>>>>>> NEW
<<<<<<< OLD 1
`clean_finish: false` when any component ended `BLOCKED` or `TESTS_NOT_RUN`, or with a review that stayed blocked, or with kept regressions,
=======
`clean_finish: false` when any component ended `BLOCKED` or `TESTS_NOT_RUN`, or with a review that stayed blocked, or with kept regressions, or with its step 6.5 commit not landed (§2.9),
>>>>>>> NEW
<<<<<<< OLD 1
Step 6.5 already committed every component, so §2.2 takes its `nothing staged` path and the call continues into §2.4's consent choice and §2.5–§2.6 — the branch carries commits to push (§2.12).
=======
§2.2 and §2.12 say what this terminal call stages and where it goes, after a step 6.5 commit that did not land included.
>>>>>>> NEW
<<<<<<< OLD 1
On **stash**, record the resulting stash as `stash_ref`
=======
On **stash**, run `git stash push -m "pre-upgrade stash"` (tracked changes only), record the resulting stash as `stash_ref` where git made one, and record every path it leaves dirty (`git status --porcelain -z --untracked-files=all` after it) as `pre_existing_dirty`; where git refuses the stash, show its error and stop as cancel does, nothing branched yet
>>>>>>> NEW
<<<<<<< OLD 1
stage per §2.2 honouring `pre_existing_dirty`, and commit per §2.3
=======
commit per §2.2 and §2.3, honouring `pre_existing_dirty`
>>>>>>> NEW
<<<<<<< OLD 1
so 6.5 finds nothing staged, makes no commit
=======
so 6.5 finds nothing to commit, makes no commit
>>>>>>> NEW
<<<<<<< OLD 1
If dirty, show the diff summary and ask
=======
If dirty, show `git status --short --untracked-files=normal` and ask
>>>>>>> NEW
<<<<<<< OLD 1
by that component's `add -A`.
=======
by that component's §2.2.
>>>>>>> NEW
`````

#### `edits/vuln-maint.txt`

`````text
<<<<<<< OLD 1
workarounds, and overall outcome.
=======
workarounds, overall outcome, and the project root (the repository's top level, `git rev-parse --show-toplevel`).
>>>>>>> NEW
`````

#### `edits/vuln-span.txt`

`````text
<<<<<<< OLD 1
`Project root: [the repository's top level, `git rev-parse --show-toplevel`]`
=======
``Project root: [the repository's top level, `git rev-parse --show-toplevel`]``
>>>>>>> NEW
`````

#### `edits/vuln.tpl`

`````text
<<<<<<< OLD 1
- `body_facts` — the CVE summary, the vulnerable range, the version change applied, the classification, the {{REVIEW}} verdict and triage where the CVE went through review, and the test counts before and after.
=======
- `body_facts` — what §2.7's four sections render: the CVE summary, the version change applied and the files changed; as the evidence, the installed version inside the vulnerable range before and the applied version outside it after, beside the test counts before and after, naming each regression kept at `keep-anyway` and each test a `NEW-FAILURE: ` note marks; the facts §2.7's door and blast-radius calls rest on — what in this repository uses the library, as `git -C "<repo>" grep -l <package-or-import-name> -- ':/'` shows it (`:/`, so the search covers the whole tree), and whether the new version changes anything it persists or publishes, as the research report, the fixer's `files_changed` and the diff show it, or that none of them shows it, which §2.7 reads as one-way; and the classification, with the {{REVIEW}} verdict and triage where the CVE went through review and every review finding not applied, with its severity.
>>>>>>> NEW
<<<<<<< OLD 1
- Body: CVE summary, vulnerable range, version change made, classification, review verdict and triage where the CVE went through review, and test results (pass count before vs. after)
=======
- Body: Step 3.9's `body_facts`, rendered as {{CH}} §2.7 says.
>>>>>>> NEW
<<<<<<< OLD 1
- `title` — `fix(deps): <library> upgrade to remediate <CVE-ID>`, with
=======
- `title` — the commit subject §2.3 writes from the "Commit message" template below, as §2.7 requires — by default `fix(deps): upgrade <library> to <version> to remediate <CVE-ID>`, with
>>>>>>> NEW
<<<<<<< OLD 1
- Title: `fix(deps): <library> upgrade to remediate <CVE-ID>` (append
=======
- Title: the commit subject — by default `fix(deps): upgrade <library> to <version> to remediate <CVE-ID>` (append
>>>>>>> NEW
<<<<<<< OLD 1
the CVE summary, the version change applied and the files changed;
=======
the CVE summary, the version change applied and the files changed (§2.7 item 1);
>>>>>>> NEW
`````

## Appendix C — changelog sections

Extracted by Task 0 Step 2 into `$S/cl`; `release.py` inserts each above its plugin's current top section.

#### `cl/aw-dev-workflows.md`

`````markdown
## [4.7.0] — 2026-10-04

**Update `workflows-core` to 1.11.1 with this release**: `/implement` Phase 4.7 writes the one-entry block its `implementation-format` §1 now defines, and Phase 6 files the follow-up kind its `followup-emission` §6 now names; its review and its Next step follow the new caller cases in `finding-triage` and `next-phase-offer`.

### Added
- **`/implement` re-classifies upward.** Phase 2A writes its exploration to `summary_file` and re-tests the class against `workflows-core:model-routing/classification` §1.1 on the plan it writes — its steps and files, where the file count and the areas a change touches are first knowable — before approval and after every revision — after a down-classification the user accepted at Phase 2B, only on a trigger a later revision adds — raising a run a trigger now applies to and continuing at Phase 2B without a second exploration. A `SIMPLE`/`MODERATE` run that meets, while implementing, a §1.1 trigger its approved plan did not state (one of §1.1's concrete triggers, not its catch-all of unclear requirements, large unknowns or otherwise high blast radius, whose unknowns it asks about) stops editing and re-plans once with `risk-planner`, which reads the diff so far through a new `Work so far` input; once the user approves, the run continues at Phase 3B under its review gate, without re-branching or re-capturing the baseline, with both plans in `plan_file` — the re-plan's Steps the work remaining, the re-plan governing only where the two contradict, both plans' Review focus lines applying — as `test-writer` and `code-review` now read it; cancelling the re-plan commits the work through Phase 4.6 with `clean_finish: false`. Where the user accepts a down-classification at that re-plan, a later trigger is put to them: continue without the Opus review — the pull-request body then says so — or stop with the work committed. Every change of class after Phase 1.5 is recorded in the Phase 5 report. Once planned, the class used to move only down, and such a run shipped with no review. Prompted by BMAD 124ea1af and 2c10d5ba.

### Changed
- **`/implement` looks before it asks.** Phase 1 tries to settle each candidate ambiguity from what the run can read — the inputs, the code, the repository's own `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` and `README.md`, and `git log` — and, on a keyed run, the applicable ARD, now resolved at the start of Phase 1 — and asks only a decision: a question the evidence leaves open and whose answer changes what the user would notice in the result. An open question the user would not notice is settled by the run and listed in the plan's Assumptions — on the Phase 2B path through the `risk-planner` brief's new `Settled by the run` line — and nothing that changes the result is assumed. The mid-implementation stop in Phase 3A and Phase 3B applies the same test, recording what it settles in the Phase 5 report. Prompted by BMAD 7e571784.
- **The code pull-request body** (`code-handoff` §2.7) holds four sections, with no preamble: a Summary; Evidence, a before and an after only as the run observed them; Merge danger, a one-way or two-way door — one-way where the run cannot tell — and the blast radius; and the Review, which names the classification and says so where no review ran. Where the repository carries one pull-request template at a path the reference lists, the body is that template, filled, its sections and checkboxes kept. §3.2's fallback now tells the user to paste the body in place of whatever the web UI prefills. The body's file list is read from git, and its Summary names any commit on the branch the run did not make. `/implement`, `/vuln` and `/upgrade` supply the facts. Prompted by mattpocock `pr`.
- **`/implement` changes code only in the repository it branches** — the one it runs from. Another code repository a multi-source run is given is read-only context; a change one needs is now planned as out of scope, named in the pull-request body as a companion change and in the report, given to `code-review` as a deferral, and recorded as a follow-up task, where it used to be edited there and left uncommitted, unreviewed and untested. Step 7.5 annotates a specification or design only in `$SPECS_PATH` (handed off at Phase 4.5) or at a path this repository does not ignore (committed with the code), reporting a gap in any other one instead; an early stop names every unnoted gap and every specs-repository note it leaves uncommitted. A review finding whose fix lies in another repository is recorded the same way and handed to no fixer; a `BLOCKER` among them leaves the review blocked. Phase 0's classification rows are now tested top to bottom, the working directory and any directory at a work tree's top level always reading as a code repository — a run started outside every work tree stops before planning, and a top level holding spec files is announced, the run stopping where nothing else describes the work — and an `@path` Phase 0 classifies as a code repository whose top level is the working directory's no longer counts as a second repository: it no longer floors the run at `SIGNIFICANT` or sends a second scan to the same repository, and it reaches that repository's scan and the exploration as a place to start. A plan with no step in this repository, as first written or after a revision, asks at its approval gate whether to revise it or stop with nothing written, naming the run each other repository needs; on a keyed run Phase 6 files one follow-up per other repository, and every stop after plan approval names them.
- **`risk-planner`'s no-mutation rule** says a plan comes before the user has approved *it*, not before any action — a re-plan follows a plan already approved.

### Fixed
- **`/implement` Phase 3B step 7's `### Re-classification` prompt offered a Cancel that no text defined**, and Phase 4.6's "Every run" list left it out, so a reviewed implementation could stop uncommitted on its branch. It now stops through Phase 4.6, like every other stop after files are written.
- **`/vuln`'s and `/upgrade`'s pull-request titles differed from their commit subjects**, which `code-handoff` §2.7 says a title is: `/vuln`'s is now the subject its commit template yields, version included, and `/upgrade`'s the subject of its one committed component or, where it committed several, a subject over those alone, typed the same way; §2.7 names the caller's title on a terminal call that commits nothing.
- **`/implement`'s `### Deferred items` and pull-request body dropped a `MAJOR` finding `review-fixer` deferred** on a `PASS WITH RECOMMENDATIONS` verdict, which gets no re-review; both now list every review finding the run did not apply.
- **`/upgrade` carried on after a component's commit did not land**, rejected by a hook, or not staged or written by git, so the next component's commit, or the terminal call, folded that component's uncommitted changes in under another subject. A commit that does not land now ends the loop (`code-handoff` §2.12): the terminal call commits nothing in its place, and where earlier components committed, its outcome line names the uncommitted component and any pull request is a draft. `/implement` and `/vuln` report a refused `git add`, or a commit git could not write, on §3.1's *Commit rejected* row, renamed from *Commit rejected by a hook*.
- **A run started from a subdirectory of the repository left new files outside that directory out of every diff it captured**: `git add -N .` marks only the working directory's untracked files. `/implement`'s, `/vuln`'s and `/upgrade`'s captures, and `test-writer`'s input, now use `git add -N --ignore-removal :/` and diff against `HEAD` (the empty tree before a first commit), which marks the whole work tree and shows every file the run deleted (plain `git add -N` staged a deletion out of the diff's sight, top-level runs included), ignoring the user's external-diff, colour and relative-path settings, and every root those commands pass, to an agent or to the test baseline, is the repository's top level — `/vuln`'s and `/upgrade`'s `code-review`, `review-fixer` and maintenance dispatches now pass one, as each agent asks — where the diffs' paths start. A run started in a monorepo's subdirectory therefore baselines and verifies every suite in the repository, and the directory it started in reaches the exploration and the scan as a place to start. Phase 3.5 step 3 runs the lint and build from the directory the exploration found them in, the top level unless it said otherwise, in a subshell, rather than wherever the session stood.
- **The *Stash* answer to `/implement`'s and `/upgrade`'s dirty-tree prompt left untracked files in the tree**, unrecorded, so the run's commit swept them in: the stash now takes tracked changes, leaving the run's own `@path` inputs in place, and every path it leaves is recorded as pre-existing, which keeps it out of the commit unless the run edits it; a stash git refuses stops the run before anything is branched.
- **`/implement`'s and `/upgrade`'s clean-tree test missed untracked files under `status.showUntrackedFiles=no`**, so the run took the `add -A` path and committed them: it now lists them, and shows them to the user (each untracked directory as one line), whatever the configuration.
- **On a dirty tree, `code-handoff` §2.2's carve-out committed the whole index**, somebody else's staged change included, and a deleted or moved path stopped its staging: it now commits the enumerated paths themselves, each read literally (`git commit -- ':(literal)<path>' …`), a rename's two paths included and never with an empty path list, and brings the index back in step with the commit afterwards.
- **`code-handoff`'s `repo` is the work tree's top level.** A caller holding a subdirectory of the repository staged §2.2's enumerated paths against the wrong root — porcelain paths are relative to the top level, and `git add` rejected them — so the commit carve-out for a dirty tree failed there; `repo` is now resolved with `git rev-parse --show-toplevel`.
- **`/implement` Phase 6 and `/ready` sent the follow-up write target to `followup-emission` §4**, which lists what no longer produces follow-ups; the ladder is §2.
`````

#### `cl/aw-docs-workflows.md`

`````markdown
## [1.5.1] — 2026-10-04

### Fixed
- **`/document` and `/release-notes` sent the follow-up write target to `followup-emission` §4**, which lists what no longer produces follow-ups; the ladder is §2.
`````

#### `cl/aw-product-workflows.md`

`````markdown
## [3.12.1] — 2026-10-04

### Fixed
- **`/epics`, `/prd-proposal` and `/brd-proposal` sent the follow-up write target to `followup-emission` §4**, which lists what no longer produces follow-ups; the ladder is §2.
- **The model-routing page called `/prd-ground`'s floor the same multi-source rule `/dev-workflows:implement` applies, and said the address is never a floor**: it is the rule's repository half, and in `/dev-workflows:implement` a resolved specs folder does floor the run.
- **`/prd-ground`'s classification comment called its floor the multi-source rule**: it is that rule's repository half, as the model-routing page now says.
`````

#### `cl/aw-workflows-core.md`

`````markdown
## [1.11.1] — 2026-10-04

**Update `dev-workflows` to 4.7.0 with this release**: `implementation-format` §1, §3 and §4, `followup-emission` §5 and §6, `finding-triage`'s partly-emptied rule and *stayed blocked*, `next-phase-offer`'s `/implement` row and rule 5, `phase-handoff`'s Phase 4.5 note, and `model-routing/classification` §1.1 and §8.1 describe its `/implement`, which changes code only in the repository it branches.

### Changed
- **`implementation-format` records one code repository per `/implement` run.** Its §1 example showed one run writing two repositories, and §3 named a repository a multi-source run edited and never branched as a way a run ends uncommitted; from `dev-workflows` 4.7.0, `/implement` changes code only in the repository it branches, and a second code repository is a later run with a block of its own; §4 names the blocks appended before 4.7.0 as the only ones a note can cover partly.
- **`followup-emission` §6 names a change another code repository needs** among the signals whose action lands outside the current change: `/dev-workflows:implement` records one as a follow-up rather than editing that repository. Its exclusion of deferred review `BLOCKER`s spares one whose fix lies in another code repository, and §5's stable key admits that identity: the other repository, named by its `origin` remote's path, and the unit the task addresses, whose one task is a run from that repository.

### Fixed
- **`model-routing/classification` §1.1's *Multi-source input* floored on any directory input**, so an `@path` to a plain directory inside the repository `/dev-workflows:implement` was started in raised the run to `SIGNIFICANT`; it now counts distinct repositories by top level and names folder inputs as Phase 0 of `/dev-workflows:implement` does, and so does §8.1's fan-out trigger, whose "saved file folder" is now a specs folder.
- **`finding-triage`'s *stayed blocked* now admits a caller's own member**: a first review's `BLOCKER` whose fix lies in another code repository, which `/dev-workflows:implement` keeps from the fixer.
- **The references page called `followup-emission` a journal emitter**; it emits follow-up tasks and verbose notes.
- **`followup-emission` §8's caller contract, and `session-hygiene`'s resume-pointer location, named `followup-emission` §4 for resolving the write target**, which lists what no longer produces follow-ups; the ladder is §2.
- **`phase-handoff`'s note on `/dev-workflows:implement`'s Phase 4.5** named every conformance note; only one in `$SPECS_PATH` reaches that phase.
- **`finding-triage`'s partly-emptied rule now admits a caller's own case**: a first-review `BLOCK` whose survivors a caller keeps from the fixer, because their fix lies in another code repository, none of them a `BLOCKER`, and that leaves no `BLOCKER` or `MAJOR` for it, asks the first settle prompt.
- **`next-phase-offer`'s routing graph and rule 5** name `/dev-workflows:implement`'s run from another repository, addressed to the unit it implemented (the Epic itself where it was one), before the remaining Epics, as the command's Next step does.
`````

#### `cl/ce-dev-workflows.md`

`````markdown
## [2.37.0] — 2026-10-04

### Added
- **`implement:` re-classifies upward.** Phase 2A writes its exploration to `summary_file` and re-tests the class against `model-routing.md` §1.1 on the plan it writes — its steps and files, where the file count and the areas a change touches are first knowable — before approval and after every revision — after a down-classification the user accepted at Phase 2B, only on a trigger a later revision adds — raising a run a trigger now applies to and continuing at Phase 2B without a second exploration. A `SIMPLE`/`MODERATE` run that meets, while implementing, a §1.1 trigger its approved plan did not state (one of §1.1's concrete triggers, not its catch-all of unclear requirements, large unknowns or otherwise high blast radius, whose unknowns it asks about) stops editing and re-plans once with `risk-planner`, which reads the diff so far through a new `Work so far` input; once the user approves, the run continues at Phase 3B under its review gate, without re-branching or re-capturing the baseline, with both plans in `plan_file` — the re-plan's Steps the work remaining, the re-plan governing only where the two contradict, both plans' Review focus lines applying — as `test-writer` and `code-review` now read it; cancelling the re-plan commits the work through Phase 4.6 with `clean_finish: false`. Where the user accepts a down-classification at that re-plan, a later trigger is put to them: continue without the review-tier review — the pull-request body then says so — or stop with the work committed. Every change of class after Phase 1.5 is recorded in the Phase 5 report. Once planned, the class used to move only down, and such a run shipped with no review. Prompted by BMAD 124ea1af and 2c10d5ba.

### Changed
- **`implement:` looks before it asks.** Phase 1 tries to settle each candidate ambiguity from what the run can read — the inputs, the code, the repository's own `AGENTS.md`, `.github/copilot-instructions.md`, `CONTRIBUTING.md` and `README.md`, and `git log` — and, on a keyed run, the applicable ARD, now resolved at the start of Phase 1 — and asks only a decision: a question the evidence leaves open and whose answer changes what the user would notice in the result. An open question the user would not notice is settled by the run and listed in the plan's Assumptions — on the Phase 2B path through the `risk-planner` brief's new `Settled by the run` line — and nothing that changes the result is assumed. The mid-implementation stop in Phase 3A and Phase 3B applies the same test, recording what it settles in the Phase 5 report. Prompted by BMAD 7e571784.
- **The code pull-request body** (`code-repo-handoff` §2.7) holds four sections, with no preamble: a Summary; Evidence, a before and an after only as the run observed them; Merge danger, a one-way or two-way door — one-way where the run cannot tell — and the blast radius; and the Review, which names the classification and says so where no review ran. Where the repository carries one pull-request template at a path the reference lists, the body is that template, filled, its sections and checkboxes kept. §3.2's fallback now tells the user to paste the body in place of whatever the web UI prefills. The body's file list is read from git, and its Summary names any commit on the branch the run did not make. `implement:`, `vuln:` and `upgrade:` supply the facts. Prompted by mattpocock `pr`.
- **`implement:` changes code only in the repository it branches** — the one it runs from. Another code repository a multi-source run is given is read-only context; a change one needs is now planned as out of scope, named in the pull-request body as a companion change and in the report, given to `code-review` as a deferral, and recorded as a follow-up task, where it used to be edited there and left uncommitted, unreviewed and untested. Step 7.5 annotates a specification or design only in `$SPECS_PATH` (handed off at Phase 4.5) or at a path this repository does not ignore (committed with the code), reporting a gap in any other one instead; an early stop names every unnoted gap and every specs-repository note it leaves uncommitted. A review finding whose fix lies in another repository is recorded the same way and handed to no fixer; a `BLOCKER` among them leaves the review blocked. Phase 0's classification rows are now tested top to bottom, the working directory and any directory at a work tree's top level always reading as a code repository — a run started outside every work tree stops before planning, and a top level holding spec files is announced, the run stopping where nothing else describes the work — and an `@path` Phase 0 classifies as a code repository whose top level is the working directory's no longer counts as a second repository: it no longer floors the run at `SIGNIFICANT` or sends a second scan to the same repository, and it reaches that repository's scan and the exploration as a place to start. A plan with no step in this repository, as first written or after a revision, asks at its approval gate whether to revise it or stop with nothing written, naming the run each other repository needs; on a keyed run Phase 6 files one follow-up per other repository, and every stop after plan approval names them.
- **`risk-planner`'s no-mutation rule** says a plan comes before the user has approved *it*, not before any action — a re-plan follows a plan already approved.

### Fixed
- **`implement:` Phase 3B step 7's `### Re-classification` prompt offered a Cancel that no text defined**, and Phase 4.6's "Every run" list left it out, so a reviewed implementation could stop uncommitted on its branch. It now stops through Phase 4.6, like every other stop after files are written.
- **`vuln:`'s and `upgrade:`'s pull-request titles differed from their commit subjects**, which `code-repo-handoff` §2.7 says a title is: `vuln:`'s is now the subject its commit template yields, version included, and `upgrade:`'s the subject of its one committed component or, where it committed several, a subject over those alone, typed the same way; §2.7 names the caller's title on a terminal call that commits nothing.
- **`implement:`'s `### Deferred items` and pull-request body dropped a `MAJOR` finding `review-fixer` deferred** on a `PASS WITH RECOMMENDATIONS` verdict, which gets no re-review; both now list every review finding the run did not apply.
- **`upgrade:` carried on after a component's commit did not land**, rejected by a hook, or not staged or written by git, so the next component's commit, or the terminal call, folded that component's uncommitted changes in under another subject. A commit that does not land now ends the loop (`code-repo-handoff` §2.12): the terminal call commits nothing in its place, and where earlier components committed, its outcome line names the uncommitted component and any pull request is a draft. `implement:` and `vuln:` report a refused `git add`, or a commit git could not write, on §3.1's *Commit rejected* row, renamed from *Commit rejected by a hook*.
- **A run started from a subdirectory of the repository left new files outside that directory out of every diff it captured**: `git add -N .` marks only the working directory's untracked files. `implement:`'s, `vuln:`'s and `upgrade:`'s captures, and `test-writer`'s input, now use `git add -N --ignore-removal :/` and diff against `HEAD` (the empty tree before a first commit), which marks the whole work tree and shows every file the run deleted (plain `git add -N` staged a deletion out of the diff's sight, top-level runs included), ignoring the user's external-diff, colour and relative-path settings, and every root those commands pass, to an agent or to the test baseline, is the repository's top level — `vuln:`'s and `upgrade:`'s `code-review`, `review-fixer` and maintenance dispatches now pass one, as each agent asks — where the diffs' paths start. A run started in a monorepo's subdirectory therefore baselines and verifies every suite in the repository, and the directory it started in reaches the exploration and the scan as a place to start. Phase 3.5 step 3 runs the lint and build from the directory the exploration found them in, the top level unless it said otherwise, in a subshell, rather than wherever the session stood.
- **The *Stash* answer to `implement:`'s and `upgrade:`'s dirty-tree prompt left untracked files in the tree**, unrecorded, so the run's commit swept them in: the stash now takes tracked changes, leaving the run's own `@path` inputs in place, and every path it leaves is recorded as pre-existing, which keeps it out of the commit unless the run edits it; a stash git refuses stops the run before anything is branched.
- **`implement:`'s and `upgrade:`'s clean-tree test missed untracked files under `status.showUntrackedFiles=no`**, so the run took the `add -A` path and committed them: it now lists them, and shows them to the user (each untracked directory as one line), whatever the configuration.
- **On a dirty tree, `code-repo-handoff` §2.2's carve-out committed the whole index**, somebody else's staged change included, and a deleted or moved path stopped its staging: it now commits the enumerated paths themselves, each read literally (`git commit -- ':(literal)<path>' …`), a rename's two paths included and never with an empty path list, and brings the index back in step with the commit afterwards.
- **`code-repo-handoff`'s `repo` is the work tree's top level.** A caller holding a subdirectory of the repository staged §2.2's enumerated paths against the wrong root — porcelain paths are relative to the top level, and `git add` rejected them — so the commit carve-out for a dirty tree failed there; `repo` is now resolved with `git rev-parse --show-toplevel`.
- **`implement:` Phase 4.6's "Every run" list named the Cancel arm of Phase 2B's repro prompt** as a stop after files were written, though that prompt runs before Pre-Phase 3 creates the branch; it is a member now only on Phase 3A step 5's re-plan, which reaches it after the edits. The list also named Pre-Phase 3.5's framework prompt among stops after files were written, though it comes before the first edit, and it named, as the one exit that does not reach Phase 4.6, an "Abandon implementation and restore to pre-impl state" arm Phase 3B no longer offers.
- **Phase 3.5 step 3 took its lint and build commands from Phase 2A's exploration**, which a run on the Phase 2B path never had — Phase 3B step 8 re-enters the step there. It now takes them from whichever exploration ran, or from the repository's own build and lint configuration.
`````

#### `cl/ie-dev-workflows.md`

`````markdown
## [2.68.0] — 2026-10-04

### Added
- **`/implement` re-classifies upward.** Phase 2A writes its exploration to `summary_file` and re-tests the class against `classification.md` §1.1 on the plan it writes — its steps and files, where the file count and the areas a change touches are first knowable — before approval and after every revision — after a down-classification the user accepted at Phase 2B, only on a trigger a later revision adds — raising a run a trigger now applies to and continuing at Phase 2B without a second exploration. A `SIMPLE`/`MODERATE` run that meets, while implementing, a §1.1 trigger its approved plan did not state (one of §1.1's concrete triggers, not its catch-all of unclear requirements, large unknowns or otherwise high blast radius, whose unknowns it asks about) stops editing and re-plans once with `risk-planner`, which reads the diff so far through a new `Work so far` input; once the user approves, the run continues at Phase 3B under its review gate, without re-branching or re-capturing the baseline, with both plans in `plan_file` — the re-plan's Steps the work remaining, the re-plan governing only where the two contradict, both plans' Review focus lines applying — as `test-writer` and `code-review` now read it; cancelling the re-plan commits the work through Phase 4.6 with `clean_finish: false`. Where the user accepts a down-classification at that re-plan, a later trigger is put to them: continue without the Opus review — the pull-request body then says so — or stop with the work committed. Every change of class after Phase 1.5 is recorded in the Phase 5 report. Once planned, the class used to move only down, and such a run shipped with no review. Prompted by BMAD 124ea1af and 2c10d5ba.

### Changed
- **`/implement` looks before it asks.** Phase 1 tries to settle each candidate ambiguity from what the run can read — the inputs, the code, the repository's own `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` and `README.md`, and `git log` — and, on a keyed run, the applicable ARD, now resolved at the start of Phase 1 — and asks only a decision: a question the evidence leaves open and whose answer changes what the user would notice in the result. An open question the user would not notice is settled by the run and listed in the plan's Assumptions — on the Phase 2B path through the `risk-planner` brief's new `Settled by the run` line — and nothing that changes the result is assumed. The mid-implementation stop in Phase 3A and Phase 3B applies the same test, recording what it settles in the Phase 5 report. Prompted by BMAD 7e571784.
- **The code pull-request body** (`code-repo-handoff` §2.7) holds four sections, with no preamble: a Summary; Evidence, a before and an after only as the run observed them; Merge danger, a one-way or two-way door — one-way where the run cannot tell — and the blast radius; and the Review, which names the classification and says so where no review ran. Where the repository carries one pull-request template at a path the reference lists, the body is that template, filled, its sections and checkboxes kept. §3.2's fallback now tells the user to paste the body in place of whatever the web UI prefills. The body's file list is read from git, and its Summary names any commit on the branch the run did not make. `/implement`, `/vuln` and `/upgrade` supply the facts. Prompted by mattpocock `pr`.
- **`/implement` changes code only in the repository it branches** — the one it runs from. Another code repository a multi-source run is given is read-only context; a change one needs is now planned as out of scope, named in the pull-request body as a companion change and in the report, given to `code-review` as a deferral, and recorded as a follow-up task, where it used to be edited there and left uncommitted, unreviewed and untested. Step 7.5 annotates a specification or design only in `$SPECS_PATH` (handed off at Phase 4.5) or at a path this repository does not ignore (committed with the code), reporting a gap in any other one instead; an early stop names every unnoted gap and every specs-repository note it leaves uncommitted. A review finding whose fix lies in another repository is recorded the same way and handed to no fixer; a `BLOCKER` among them leaves the review blocked. Phase 0's classification rows are now tested top to bottom, the working directory and any directory at a work tree's top level always reading as a code repository — a run started outside every work tree stops before planning, and a top level holding spec files is announced, the run stopping where nothing else describes the work — and an `@path` Phase 0 classifies as a code repository whose top level is the working directory's no longer counts as a second repository: it no longer floors the run at `SIGNIFICANT` or sends a second scan to the same repository, and it reaches that repository's scan and the exploration as a place to start. A plan with no step in this repository, as first written or after a revision, asks at its approval gate whether to revise it or stop with nothing written, naming the run each other repository needs; on a keyed run Phase 6 files one follow-up per other repository, and every stop after plan approval names them.
- **`risk-planner`'s no-mutation rule** says a plan comes before the user has approved *it*, not before any action — a re-plan follows a plan already approved.

### Fixed
- **`/implement` Phase 3B step 7's `### Re-classification` prompt offered a Cancel that no text defined**, and Phase 4.6's "Every run" list left it out, so a reviewed implementation could stop uncommitted on its branch. It now stops through Phase 4.6, like every other stop after files are written.
- **`/vuln`'s and `/upgrade`'s pull-request titles differed from their commit subjects**, which `code-repo-handoff` §2.7 says a title is: `/vuln`'s is now the subject its commit template yields, version included, and `/upgrade`'s the subject of its one committed component or, where it committed several, a subject over those alone, typed the same way; §2.7 names the caller's title on a terminal call that commits nothing.
- **`/implement`'s `### Deferred items` and pull-request body dropped a `MAJOR` finding `review-fixer` deferred** on a `PASS WITH RECOMMENDATIONS` verdict, which gets no re-review; both now list every review finding the run did not apply.
- **`/upgrade` carried on after a component's commit did not land**, rejected by a hook, or not staged or written by git, so the next component's commit, or the terminal call, folded that component's uncommitted changes in under another subject. A commit that does not land now ends the loop (`code-repo-handoff` §2.12): the terminal call commits nothing in its place, and where earlier components committed, its outcome line names the uncommitted component and any pull request is a draft. `/implement` and `/vuln` report a refused `git add`, or a commit git could not write, on §3.1's *Commit rejected* row, renamed from *Commit rejected by a hook*.
- **A run started from a subdirectory of the repository left new files outside that directory out of every diff it captured**: `git add -N .` marks only the working directory's untracked files. `/implement`'s, `/vuln`'s and `/upgrade`'s captures, and `test-writer`'s input, now use `git add -N --ignore-removal :/` and diff against `HEAD` (the empty tree before a first commit), which marks the whole work tree and shows every file the run deleted (plain `git add -N` staged a deletion out of the diff's sight, top-level runs included), ignoring the user's external-diff, colour and relative-path settings, and every root those commands pass, to an agent or to the test baseline, is the repository's top level — `/vuln`'s and `/upgrade`'s `code-review`, `review-fixer` and maintenance dispatches now pass one, as each agent asks — where the diffs' paths start. A run started in a monorepo's subdirectory therefore baselines and verifies every suite in the repository, and the directory it started in reaches the exploration and the scan as a place to start. Phase 3.5 step 3 runs the lint and build from the directory the exploration found them in, the top level unless it said otherwise, in a subshell, rather than wherever the session stood.
- **The *Stash* answer to `/implement`'s and `/upgrade`'s dirty-tree prompt left untracked files in the tree**, unrecorded, so the run's commit swept them in: the stash now takes tracked changes, leaving the run's own `@path` inputs in place, and every path it leaves is recorded as pre-existing, which keeps it out of the commit unless the run edits it; a stash git refuses stops the run before anything is branched.
- **`/implement`'s and `/upgrade`'s clean-tree test missed untracked files under `status.showUntrackedFiles=no`**, so the run took the `add -A` path and committed them: it now lists them, and shows them to the user (each untracked directory as one line), whatever the configuration.
- **On a dirty tree, `code-repo-handoff` §2.2's carve-out committed the whole index**, somebody else's staged change included, and a deleted or moved path stopped its staging: it now commits the enumerated paths themselves, each read literally (`git commit -- ':(literal)<path>' …`), a rename's two paths included and never with an empty path list, and brings the index back in step with the commit afterwards.
- **`code-repo-handoff`'s `repo` is the work tree's top level.** A caller holding a subdirectory of the repository staged §2.2's enumerated paths against the wrong root — porcelain paths are relative to the top level, and `git add` rejected them — so the commit carve-out for a dirty tree failed there; `repo` is now resolved with `git rev-parse --show-toplevel`.
- **`/implement` Phase 4.6's "Every run" list named the Cancel arm of Phase 2B's repro prompt** as a stop after files were written, though that prompt runs before Pre-Phase 3 creates the branch; it is a member now only on Phase 3A step 5's re-plan, which reaches it after the edits. The list also named Pre-Phase 3.5's framework prompt among stops after files were written, though it comes before the first edit, and it named, as the one exit that does not reach Phase 4.6, an "Abandon implementation and restore to pre-impl state" arm Phase 3B no longer offers.
- **Phase 3.5 step 3 took its lint and build commands from Phase 2A's exploration**, which a run on the Phase 2B path never had — Phase 3B step 8 re-enters the step there. It now takes them from whichever exploration ran, or from the repository's own build and lint configuration.
`````

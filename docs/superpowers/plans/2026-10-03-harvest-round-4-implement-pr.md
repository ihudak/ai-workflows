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
    'aw': {'IMPL': '/implement', 'REVIEW': 'Opus review',
           'CHOICES': '2–4 options; the harness supplies the free-text escape',
           'MR': '`workflows-core:model-routing/classification`',
           'REPODOCS': '`CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` and `README.md`',
           'CMR': '`${CLAUDE_PLUGIN_ROOT}/references/context-management.md`', 'READ': 'Read'},
    'ie': {'IMPL': '/implement', 'REVIEW': 'Opus review',
           'CHOICES': '2–4 options; the harness supplies the free-text escape',
           'MR': '`${CLAUDE_PLUGIN_ROOT}/references/model-routing/classification.md`',
           'REPODOCS': '`CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` and `README.md`',
           'CMR': '`${CLAUDE_PLUGIN_ROOT}/references/context-management.md`', 'READ': 'Read'},
    'ce': {'IMPL': 'implement:', 'REVIEW': 'review-tier review',
           'CHOICES': 'last: `"Other… (describe)"`',
           'MR': '`' + CE_SHARED + 'model-routing.md`',
           'REPODOCS': '`AGENTS.md`, `.github/copilot-instructions.md`, `CONTRIBUTING.md` and `README.md`',
           'CMR': '`' + CE_SHARED + 'context-management.md`', 'READ': 'view'},
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
                REFS='plugins/dev-workflows/docs/reference/references.md', CL='plugins/dev-workflows/CHANGELOG.md'),
     'ie': dict(IMPL='plugins/dev-workflows/commands/implement.md', CH='plugins/dev-workflows/references/code-repo-handoff.md',
                RP='plugins/dev-workflows/agents/risk-planner.md', VULN='plugins/dev-workflows/commands/vuln.md',
                UPG='plugins/dev-workflows/commands/upgrade.md', DOC='plugins/dev-workflows/docs/commands/implement.md',
                REFS='plugins/dev-workflows/docs/reference/references.md', CL='plugins/dev-workflows/CHANGELOG.md'),
     'ce': dict(IMPL='dev-workflows/skills/implement/SKILL.md', CH='dev-workflows/skills/_shared/code-repo-handoff.md',
                RP='dev-workflows/agents/risk-planner.md', VULN='dev-workflows/skills/vuln/SKILL.md',
                UPG='dev-workflows/skills/upgrade/SKILL.md', DOC='dev-workflows/docs/skills/implement.md',
                REFS='dev-workflows/docs/reference/references.md', CL='dev-workflows/CHANGELOG.md')}[ed]
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
for s, n in [('Look, then ask; never guess.', 1), ('Re-classified upward after exploration', 1),
             ('Re-classified upward during implementation', 1), ('partial_diff_file', 4), ('Work so far', 3),
             ("§2.7's four sections", 1), ("when Phase 3A step 5's re-plan reached it", 1),
             ('**Write the exploration down, then re-test the class.**', 1)]:
    cnt('IMPL', s, n)
cnt('RP', '**`Work so far`** (optional)', 1)
cnt('VULN', "§2.7's four sections", 1); cnt('UPG', "§2.7's four sections", 1)
for s, n in [('`## Merge danger`', 1), ('pull_request_template.md', 3), ('PULL_REQUEST_TEMPLATE/', 3),
             ('.gitlab/merge_request_templates/Default.md', 1), ("what §2.7 renders into the body file's four sections", 1),
             ('**The repository\'s own template wins.**', 1)]:
    cnt('CH', s, n)
cnt('DOC', 're-plan approved', 1)
cnt('REFS', 'a Merge danger call', 1)
cnt('CL', f'## [{VER}] — 2026-10-03', 1)
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
  w plugins/dev-workflows/commands/implement.md "$(g impl.tpl)"
  w plugins/dev-workflows/commands/implement.md "$(g impl-body.tpl)"
  w plugins/dev-workflows/commands/implement.md "$E/aw-implement.txt"
  w plugins/dev-workflows/commands/vuln.md "$(g vuln.tpl)"
  w plugins/dev-workflows/commands/upgrade.md "$(g upgrade.tpl)"
  w plugins/dev-workflows/agents/risk-planner.md "$(g risk-planner.tpl)"
  w plugins/dev-workflows/docs/commands/implement.md "$E/awie-doc-implement.txt"
  w plugins/dev-workflows/docs/reference/references.md "$E/aw-doc-references.txt"
  ;;
ie)
  w plugins/dev-workflows/references/code-repo-handoff.md "$E/all-code-handoff.txt"
  w plugins/dev-workflows/commands/implement.md "$(g impl.tpl)"
  w plugins/dev-workflows/commands/implement.md "$(g impl-body.tpl)"
  w plugins/dev-workflows/commands/implement.md "$E/ed-implement.txt"
  w plugins/dev-workflows/commands/vuln.md "$(g vuln.tpl)"
  w plugins/dev-workflows/commands/upgrade.md "$(g upgrade.tpl)"
  w plugins/dev-workflows/agents/risk-planner.md "$(g risk-planner.tpl)"
  w plugins/dev-workflows/docs/commands/implement.md "$E/awie-doc-implement.txt"
  w plugins/dev-workflows/docs/reference/references.md "$E/ed-doc-references.txt"
  ;;
ce)
  w dev-workflows/skills/_shared/code-repo-handoff.md "$E/all-code-handoff.txt"
  w dev-workflows/skills/implement/SKILL.md "$(g impl.tpl)"
  w dev-workflows/skills/implement/SKILL.md "$(g impl-body.tpl)"
  w dev-workflows/skills/implement/SKILL.md "$E/ed-implement.txt"
  w dev-workflows/skills/vuln/SKILL.md "$(g vuln.tpl)"
  w dev-workflows/skills/upgrade/SKILL.md "$(g upgrade.tpl)"
  w dev-workflows/agents/risk-planner.md "$(g risk-planner.tpl)"
  w dev-workflows/docs/skills/implement.md "$E/ce-doc-implement.txt"
  w dev-workflows/docs/reference/references.md "$E/ed-doc-references.txt"
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
         'dev-workflows': ('4.6.0', '4.7.0', 'plugins/dev-workflows/.claude-plugin/plugin.json', 'plugins/dev-workflows/CHANGELOG.md')}),
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

#### `edits/all-code-handoff.txt`

`````text
<<<<<<< OLD 1
Body: **written to a file** — `<body-path>`, a `command mktemp -t` path outside any repo tree — never passed inline, which would break on newlines and quoting. It contains what the run produced (`body_facts`), the files changed, the reviewer verdict where the caller has one, the test result, and, on a `clean_finish: false` run, §2.9's banner as its **first line**. The same file is what §3.2 names when `gh` is unavailable, so the user pastes the identical body — banner included — into the web UI.
=======
Body: **written to a file** — `<body-path>`, a `command mktemp -t` path outside any repo tree — never passed inline, which would break on newlines and quoting. The same file is what §3.2 names when `gh` is unavailable, so the user pastes the identical body — banner included — into the web UI.

**What the body holds.** No preamble: on a `clean_finish: false` run §2.9's banner is its **first line**, and otherwise its first heading is. Then four sections, in this order, rendered from `body_facts`:

1. `## Summary` — what changed, one line per notable item, and the files changed.
2. `## Evidence` — a **Before** and an **After**, each taken only from what the run observed: the caller's baseline against its verification, and on a bug fix the failing reproduction against the passing test. Where the run has no before or no after — tests the operator skipped, a verification that could not run — the section says which, and why. "Tests pass" alone is a claim, not a before and an after.
3. `## Merge danger` — the **door** and the **blast radius**, each with one line of why:
   - **Door: one-way** where the change includes a step that reverting its commit does not undo — a migration that drops or rewrites data, removing a public contract that consumers outside the repository use, writing persisted data in a new format, or anything that ships outward (sends, publishes, deletes); **two-way** otherwise. **Where the run cannot tell, one-way**, with the reason: the door is the run grading its own change, and the uncertain case is the one a reader should slow down on.
   - **Blast radius** — a short phrase naming what breaks if the change is wrong: an API's consumers, a data store, a screen, the build.
4. `## Review` — the reviewer verdict and triage summary where the caller has them, and every review finding the caller did not apply, with its severity.

**The repository's own template wins.** Resolve it against a fixed set of paths, never by searching for one: list the committed tree with `git -C "<repo>" ls-tree -r --name-only HEAD`, compare each path with the rungs below without regard to case, and stop at the first rung that matches —

1. `.github/pull_request_template.md`, then `pull_request_template.md` at the root, then `docs/pull_request_template.md`;
2. the first of `.github/PULL_REQUEST_TEMPLATE/`, `PULL_REQUEST_TEMPLATE/` and `docs/PULL_REQUEST_TEMPLATE/` that holds a `.md` file directly: where it holds exactly one, that file; where it holds several, none — a directory of templates names no default, so the body is written as above and its last line says the repository offers several templates, naming the directory;
3. `.gitlab/merge_request_templates/Default.md`.

Where a template resolves, the body **is that template, filled**: its headings kept in their order, and each section answered from `body_facts`; a section the run has nothing for says so and why, and never keeps the template's placeholder text; a checkbox ticked only where the run can show what it claims, and never deleted; each of the four sections above placed in the template section that asks for it, and every one no template section asks for appended after the template, in the order above. The banner stays the first line. **The template wins because the body replaces it otherwise**: `gh pr create --body-file` replaces what the web UI would have prefilled, so writing this section's own shape deletes the template on the `gh` path, and on §3.2's path the pasted body lands beside the prefilled template.
>>>>>>> NEW
<<<<<<< OLD 1
| `body_facts` | what §2.7 renders into the body file |
=======
| `body_facts` | what §2.7 renders into the body file's four sections: what changed and the files changed; the before and the after the run observed; the facts its door and blast-radius calls rest on; and the review |
>>>>>>> NEW
`````

#### `edits/aw-doc-references.txt`

`````text
<<<<<<< OLD 1
only its pull request degrades, to a draft carrying a DO-NOT-MERGE banner.
=======
only its pull request degrades, to a draft carrying a DO-NOT-MERGE banner. The pull request's body holds a Summary, the before and the after the run observed as Evidence, a Merge danger call — a one-way or two-way door, and its blast radius — and the Review; where the repository carries a pull-request template, the body is that template, filled.
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
**First remove this run's handoff files.** Nothing from here on reads one — `summary_file`, `plan_file`,
`partial_diff_file` where Phase 3A step 5 re-planned, every `test_diff_file` and `review_diff_file` this
run wrote (a re-capture that overwrote a path leaves one file, a fresh `mktemp` another), `review_file`
and `claims_file`.
>>>>>>> NEW
<<<<<<< OLD 1
and the **Keep the verdict** and **Cancel** arms of either of `workflows-core:finding-triage`'s settle prompts (Phase 3B steps 7 and 8). **Each of those runs Phase 4.6 before it stops**,
=======
the **Keep the verdict** and **Cancel** arms of either of `workflows-core:finding-triage`'s settle prompts (Phase 3B steps 7 and 8), and the **Cancel** arm of each of Phase 2B's three prompts — re-classification, withheld repro, plan approval — when Phase 3A step 5's re-plan reached it. **Each of those runs Phase 4.6 before it stops**,
>>>>>>> NEW
<<<<<<< OLD 1
**Two Cancels are not in that set, and the test is the written file rather than the branch.** Phase 2B's repro prompt runs *before* Pre-Phase 3, so cancelling there leaves no branch and no written file.
=======
**Two Cancels are not in that set, and the test is the written file rather than the branch.** Phase 2B's repro prompt runs *before* Pre-Phase 3, so cancelling there leaves no branch and no written file — save on Phase 3A step 5's re-plan, which reaches it after files were written and is in the set above for that reason.
>>>>>>> NEW
`````

#### `edits/awie-doc-implement.txt`

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
    P1 -.->|"raised after exploration"| P2
    IMA -.->|"a trigger the plan missed: re-plan"| P2
    P2 -.->|"re-plan approved"| IMB
>>>>>>> NEW
<<<<<<< OLD 1
the Phase 0.5 readiness pre-flight, clarification, and, only when the input is multi-source,
=======
the Phase 0.5 readiness pre-flight, clarification — which looks in the inputs, the code, the repository's own docs and `git log` before it asks, and asks only what would change the result — and, only when the input is multi-source,
>>>>>>> NEW
<<<<<<< OLD 1
`G` is not a new decision: it is the classification Phase 1.5 already made, drawn where the two paths part.
=======
`G` is not a new decision: it is the class as it stands, drawn where the two paths part — Phase 1.5's, or raised before any file is written when Phase 2A's exploration shows a classification trigger the description did not — more non-test files than expected, authentication, a schema or migration, a public contract (the dotted `P1` → `P2` edge). A run that meets such a trigger while implementing, one its approved plan did not state, re-plans upward: `risk-planner` plans the rest with the diff so far, and once you approve, the run continues on the review path without re-branching or re-capturing the baseline (the dotted `IMA` → `P2` → `IMB` edges); cancelling that re-plan commits the work, and any pull request the run opens is a draft.
>>>>>>> NEW
`````

#### `edits/ce-doc-implement.txt`

`````text
<<<<<<< OLD 1
    p35 --> p4["Phase 4 — Post-implementation maintenance (both branches)"]
=======
    p35 --> p4["Phase 4 — Post-implementation maintenance (both branches)"]
    p2a -.->|"raised after exploration"| p2b
    p3a -.->|"a trigger the plan missed: re-plan"| p2b
    p2b -.->|"re-plan approved"| p3b
>>>>>>> NEW
<<<<<<< OLD 1
Planning gates too: `risk-planner` (Phase 2B, same strong-reasoning pin) is mandatory for SIGNIFICANT/HIGH-RISK work, and can itself return a `### Re-classification` down to SIMPLE/MODERATE — the user confirms before falling back to Phase 2A.
=======
Clarification (Phase 1) looks in the inputs, the code, the repository's own docs and `git log` before it asks, and asks only what would change the result. Planning gates too: `risk-planner` (Phase 2B, same strong-reasoning pin) is mandatory for SIGNIFICANT/HIGH-RISK work, and can itself return a `### Re-classification` down to SIMPLE/MODERATE — the user confirms before falling back to Phase 2A. The class also moves up: Phase 2A re-tests it once its exploration returns, and raises it — on to `risk-planner` — where the exploration shows a classification trigger the description did not — more non-test files than expected, authentication, a schema or migration, a public contract (the dotted `p2a` → `p2b` edge); and a SIMPLE/MODERATE run that meets such a trigger while implementing, one its approved plan did not state, stops editing and re-plans with `risk-planner` from the diff so far, continuing on the review path once you approve, without re-branching or re-capturing the baseline (the dotted `p3a` → `p2b` → `p3b` edges); cancelling that re-plan commits the work, and any pull request the run opens is a draft.
>>>>>>> NEW
`````

#### `edits/ed-doc-references.txt`

`````text
<<<<<<< OLD 1
the push and the pull request sit behind one consent choice, asked once per run.
=======
the push and the pull request sit behind one consent choice, asked once per run. The pull request's body holds a Summary, the before and the after the run observed as Evidence, a Merge danger call — a one-way or two-way door, and its blast radius — and the Review; where the repository carries a pull-request template, the body is that template, filled.
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
3. **Run linters and builds.** Use the project's standard lint/build commands as discovered by whichever codebase exploration this run actually performed — Phase 2A's subagent, Phase 2B's Explore subagent, or the Phase 1.7 fan-out summary — and, where none of them named one, read them from the repo's own build/lint configuration: Phase 3B step 8 re-enters this step on runs where Phase 2A's exploration never ran.
>>>>>>> NEW
<<<<<<< OLD 1
This command has exits that stop *after* Pre-Phase 3 created the branch and after files were written: the two unreadable-`test_diff_file` stops (Phase 3.5 step 2, Phase 3B step 4a), the Cancel arms of the framework and repro prompts and of both Phase 3.5 prompts (step 5's unverified-run prompt and step 6's regression prompt), the unreadable-`review_diff_file` stop (Phase 3B step 6), the `review-fixer` `NEEDS HUMAN` stop, a review that stayed blocked (Phase 3B step 7, or step 8's review of the Phase 3.5 delta), and the **Keep the verdict** and **Cancel** arms of either of
=======
This command has exits that stop *after* Pre-Phase 3 created the branch: the **Cancel** arm of Pre-Phase 3.5's framework prompt, before the first edit — this phase finds nothing to stage there, and still names any `stash_ref` — and, after files were written, the two unreadable-`test_diff_file` stops (Phase 3.5 step 2, Phase 3B step 4a), the **Cancel** arms of both Phase 3.5 prompts (step 5's unverified-run prompt and step 6's regression prompt), the unreadable-`review_diff_file` stop (Phase 3B step 6), the `review-fixer` `NEEDS HUMAN` stop, a review that stayed blocked (Phase 3B step 7, or step 8's review of the Phase 3.5 delta), the **Cancel** arm of each of Phase 2B's three prompts — re-classification, withheld repro, plan approval — when Phase 3A step 5's re-plan reached it, and the **Keep the verdict** and **Cancel** arms of either of
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

#### `edits/impl-body.tpl`

`````text
<<<<<<< OLD 1
- `body_facts` — what was implemented; the files changed; the {{REVIEW}} verdict and triage summary where Phase 3B produced one; the `test-baseliner` verify result against the Pre-Phase 3.5 baseline; and every review finding `### Deferred items` lists as not applied — deferred `MINOR`/`NIT` findings and every survivor of a re-review, each with its severity.
=======
- `body_facts` — what §2.7's four sections render: what was implemented and the files changed; as the evidence, the Pre-Phase 3.5 baseline before and the `test-baseliner` verify result after — and, on a `task_shape: bug` run whose plan carries a red repro, that repro's command and output before and the regression test's result in the verify run after; the facts the door and blast-radius calls rest on, as the plan and the diff show them — a migration, a removed or changed public contract, a persisted format, anything sent or published; and the {{REVIEW}} verdict and triage summary where Phase 3B produced one, with every review finding `### Deferred items` lists as not applied — deferred `MINOR`/`NIT` findings and every survivor of a re-review, each with its severity.
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

Before producing a plan, list the candidate ambiguities in the description:
- Ambiguous scope or unclear boundaries
- Missing constraints (performance, security, backwards-compatibility)
- Multiple valid implementation approaches
- Undefined integration points or dependencies
- Missing acceptance criteria

**Look before asking.** Try to settle each candidate from what this run can read: the inputs Phase 0 resolved, the code, the repository's own {{REPODOCS}}, and `git log`. Look only as far as each candidate needs — this is not Phase 2A's or Phase 2B's exploration, which still runs. Then sort each candidate:
- **Settled by the reading** — missing evidence, not a decision: ask nothing, and carry it into the plan with where it was found.
- **Left open, and its answer changes what the user would notice in the result** — behaviour, scope, an interface, compatibility, a constraint nobody wrote down: a **decision**. Ask it.
- **Left open, and the user would not notice the answer** — settle it yourself and list it in the plan's Assumptions.

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
**Wait for the agent's response before proceeding. If the agent returns no relevant files or fails, proceed with the plan using your own file reads to gather context. Do not begin writing the plan until the file map is returned or you have gathered context yourself.**

**Write the exploration down, then re-test the class.** Write the returned file map — or, where you gathered context yourself, what those reads found — to a temp file (`command mktemp -t dw-impl-summary-XXXXXX`, never inside a repo tree) and record its absolute path as `summary_file`. Then test the Phase 1.5 class again against {{MR}} §1.1, reading the file map: the files the change will need to touch, and what they do. Where a §1.1 trigger now applies — more than 3–5 non-test files, authentication or authorization, a schema or migration, a public contract, concurrency, or any other item on that list — raise the class to SIGNIFICANT (HIGH-RISK under §1.1's multiplier), announce `Re-classified upward after exploration: <trigger> (<path>)`, record the new class and that reason in the `model_routing` block, and continue at Phase 2B with `summary_file` as its codebase summary — no second exploration. **Skip this paragraph where this phase was entered from a `### Re-classification` the user accepted at Phase 2B**: `summary_file` already holds the exploration, and that acceptance is the plan-approval override, which a re-test would undo.
>>>>>>> NEW
<<<<<<< OLD 1
**Codebase exploration** — If Phase 1.7 ran (`fan_out = true`), use its **multi-source codebase summary** (already written to `summary_file` in Phase 1.7 step 4) as the codebase context and skip the single Explore subagent. Otherwise,
=======
**Phase 3A step 5's re-plan also runs this phase**, from the `risk-planner` dispatch on, and that step says where each arm below leads on it.

**Codebase exploration** — If Phase 1.7 ran (`fan_out = true`), use its **multi-source codebase summary** (already written to `summary_file` in Phase 1.7 step 4) as the codebase context and skip the single Explore subagent. If Phase 2A's re-test raised the class, use the exploration it wrote to `summary_file` the same way, and skip the subagent likewise. Otherwise,
>>>>>>> NEW
<<<<<<< OLD 1
  > Classification: [SIGNIFICANT | HIGH-RISK] — reason: [the criterion from Phase 1.5, or the multi-source floor from Phase 1.6 when fan_out]
=======
  > Classification: [SIGNIFICANT | HIGH-RISK] — reason: [the criterion from Phase 1.5, the multi-source floor from Phase 1.6 when fan_out, or the raise — Phase 2A's re-test or Phase 3A step 5 — with its trigger and path]
>>>>>>> NEW
<<<<<<< OLD 1
  > Current state: branch = [git branch], uncommitted = [git status --short summary]
=======
  > Current state: branch = [git branch], uncommitted = [git status --short summary]
  > Work so far: [on Phase 3A step 5's re-plan only — read the diff at the `partial_diff_file` path: edits already on the branch, part of this change; omit the line otherwise]
>>>>>>> NEW
<<<<<<< OLD 1
Accepting here is the user exercising the **plan-approval override** of the multi-source SIGNIFICANT floor (Phase 1.6); that is the sanctioned way to leave the fan_out floor.
=======
Accepting here is the user exercising the **plan-approval override** — of the multi-source SIGNIFICANT floor (Phase 1.6), or of a raise; that is the sanctioned way to leave either, and Phase 2A's re-test does not run again.
>>>>>>> NEW
<<<<<<< OLD 1
5. If a **new ambiguity** emerges mid-implementation: STOP, ask with choices ({{CHOICES}}), resume after answer
=======
5. If something **new** emerges mid-implementation, look before stopping, and sort it:
   - **A §1.1 trigger the approved plan did not state** — a fact its Steps and Files did not name: a schema change or migration, an authentication or authorization path, a public contract, concurrency, the non-test files changed passing §1.1's 3–5, or any other item on {{MR}} §1.1's list → **re-plan upward**, once per run:
     1. Stop editing. Raise the class to SIGNIFICANT (HIGH-RISK under §1.1's multiplier), announce `Re-classified upward during implementation: <trigger> (<path>)`, and record the new class and that reason in the `model_routing` block.
     2. Write the diff so far — `git add -N . && git diff` — to a temp file (`command mktemp -t dw-impl-partial-XXXXXX`, never inside a repo tree) and record its absolute path as `partial_diff_file`.
     3. Run Phase 2B from its `risk-planner` dispatch on, with the complete brief: `summary_file` as its codebase summary, this raise as its classification reason, and its `Work so far:` line naming `partial_diff_file`. Its arms lead where they always do, save these: **Approve** writes the new plan over `plan_file` and continues at Phase 3B step 1 — Pre-Phase 3 and Pre-Phase 3.5 are not run again, and the baseline still predates every edit; **Accept revised classification** resumes Phase 3A where it stopped, on the plan already approved; and each **Cancel** — the re-classification prompt's, the withheld-repro prompt's and the plan-approval prompt's — stops through Phase 4.6, since files are written (its `"Every run"` list). Every re-dispatch on this path — **Override**, **Revise**, **Help construct a repro** — carries the complete brief, its `Work so far:` line included.
   - **A decision** — Phase 1's test: the repository cannot settle it, and its answer changes what the user would notice in the result → STOP, ask with choices ({{CHOICES}}), resume after answer. A §1.1 trigger met after this run's one re-plan is asked here too.
   - **Anything else** → look it up, and continue.
>>>>>>> NEW
<<<<<<< OLD 1
4. If a **new ambiguity** emerges mid-implementation: STOP, ask with choices ({{CHOICES}}), resume after answer
=======
4. If something **new** emerges mid-implementation, look before stopping: **a decision** — Phase 1's test: the repository cannot settle it, and its answer changes what the user would notice in the result → STOP, ask with choices ({{CHOICES}}), resume after answer; **anything else** → look it up, and continue.
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
[each raise, one line: `Raised from <class> after exploration` or `… during implementation`, then `— <trigger> (<path>)`; omit the line where the class was never raised]
>>>>>>> NEW
<<<<<<< OLD 1
- NEVER make assumptions that could have been asked — ask instead
=======
- NEVER assume what the evidence leaves open and the user would notice — look first, then ask (Phase 1); NEVER ask what the repository already answers
>>>>>>> NEW
`````

#### `edits/risk-planner.tpl`

`````text
<<<<<<< OLD 1
- **Current state** - git branch, uncommitted changes, test baseline if any.
=======
- **Current state** - git branch, uncommitted changes, test baseline if any.
- **`Work so far`** (optional) — from `{{IMPL}}`'s Phase 3A step 5 re-plan: the absolute path to a diff of edits already on the branch, made under an earlier plan the user approved. `{{READ}}` it first. Those edits are part of this change and stay: plan the rest of the task from the tree as it stands — a step may revise what the diff wrote, and the plan never assumes a clean tree. On a read failure, follow the **read-failure contract** in {{CMR}} — this input is *context*: degrade to absent — the edits stay on the branch, and `Current state` still names them — and name the unreadable path in the plan's `### Risks`. On a bug-shaped task those edits may already turn the repro green; that is the withheld ranking `task_shape` describes below, with what you tried.
>>>>>>> NEW
<<<<<<< OLD 1
a plan is produced **before** the user has approved any action, and running a mutating command there would act ahead of that approval.
=======
a plan is produced **before** the user has approved it, and running a mutating command there would act ahead of that approval.
>>>>>>> NEW
`````

#### `edits/upgrade.tpl`

`````text
<<<<<<< OLD 1
`body_facts` = the Upgrade Summary rows, each component's classification and review verdict, and the test result against the Phase 2 prep baseline;
=======
`body_facts` = what §2.7's four sections render: the Upgrade Summary rows and the files changed; as the evidence, each component's version before and after, and the test result against the Phase 2 prep baseline; the facts the door and blast-radius calls rest on — what in this repository depends on each component, and whether its new version migrates or rewrites anything persisted; and each component's classification and review verdict;
>>>>>>> NEW
`````

#### `edits/vuln.tpl`

`````text
<<<<<<< OLD 1
- `body_facts` — the CVE summary, the vulnerable range, the version change applied, the classification, the {{REVIEW}} verdict and triage where the CVE went through review, and the test counts before and after.
=======
- `body_facts` — what §2.7's four sections render: the CVE summary, the version change applied and the files changed; as the evidence, the installed version inside the vulnerable range before and the applied version outside it after, beside the test counts before and after; the facts the door and blast-radius calls rest on — what in this repository uses the library, and whether the new version changes anything it persists or publishes; and the classification, with the {{REVIEW}} verdict and triage where the CVE went through review.
>>>>>>> NEW
`````

## Appendix C — changelog sections

Extracted by Task 0 Step 2 into `$S/cl`; `release.py` inserts each above its plugin's current top section.

#### `cl/aw-dev-workflows.md`

`````markdown
## [4.7.0] — 2026-10-03

### Added
- **`/implement` looks before it asks.** Phase 1 tries to settle each candidate ambiguity from what the run can read — the inputs, the code, the repository's own `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` and `README.md`, and `git log` — and asks only a decision: a question the evidence leaves open and whose answer changes what the user would notice in the result. An open question the user would not notice is settled by the run and listed in the plan's Assumptions; nothing that changes the result is assumed. The mid-implementation stop in Phase 3A and Phase 3B applies the same test. Prompted by BMAD 7e571784.
- **`/implement` re-classifies upward.** Phase 2A writes its exploration to `summary_file` and re-tests the class against `workflows-core:model-routing/classification` §1.1 with the file map — where the file count and the areas a change touches are first knowable — raising a run a trigger now applies to and continuing at Phase 2B without a second exploration. A `SIMPLE`/`MODERATE` run that meets, while implementing, a §1.1 trigger its approved plan did not state stops editing and re-plans once with `risk-planner`, which reads the diff so far through a new `Work so far` input; once the user approves, the run continues at Phase 3B under its review gate, without re-branching or re-capturing the baseline, and a Cancel there commits the work through Phase 4.6 with `clean_finish: false`. The class used to move only down, and such a run shipped with no review. Prompted by BMAD 124ea1af and 2c10d5ba.
- **The code pull-request body** (`code-handoff` §2.7) holds four sections, with no preamble: a Summary; Evidence, a before and an after only as the run observed them; Merge danger, a one-way or two-way door — one-way where the run cannot tell — and the blast radius; and the Review. Where the repository carries a pull-request template, resolved against a fixed set of paths, the body is that template, filled, its sections and checkboxes kept. `/implement`, `/vuln` and `/upgrade` supply the facts. Prompted by mattpocock `pr`.
`````

#### `cl/ce-dev-workflows.md`

`````markdown
## [2.37.0] — 2026-10-03

### Added
- **`implement:` looks before it asks.** Phase 1 tries to settle each candidate ambiguity from what the run can read — the inputs, the code, the repository's own `AGENTS.md`, `.github/copilot-instructions.md`, `CONTRIBUTING.md` and `README.md`, and `git log` — and asks only a decision: a question the evidence leaves open and whose answer changes what the user would notice in the result. An open question the user would not notice is settled by the run and listed in the plan's Assumptions; nothing that changes the result is assumed. The mid-implementation stop in Phase 3A and Phase 3B applies the same test. Prompted by BMAD 7e571784.
- **`implement:` re-classifies upward.** Phase 2A writes its exploration to `summary_file` and re-tests the class against `model-routing.md` §1.1 with the file map — where the file count and the areas a change touches are first knowable — raising a run a trigger now applies to and continuing at Phase 2B without a second exploration. A `SIMPLE`/`MODERATE` run that meets, while implementing, a §1.1 trigger its approved plan did not state stops editing and re-plans once with `risk-planner`, which reads the diff so far through a new `Work so far` input; once the user approves, the run continues at Phase 3B under its review gate, without re-branching or re-capturing the baseline, and a Cancel there commits the work through Phase 4.6 with `clean_finish: false`. The class used to move only down, and such a run shipped with no review. Prompted by BMAD 124ea1af and 2c10d5ba.
- **The code pull-request body** (`code-repo-handoff` §2.7) holds four sections, with no preamble: a Summary; Evidence, a before and an after only as the run observed them; Merge danger, a one-way or two-way door — one-way where the run cannot tell — and the blast radius; and the Review. Where the repository carries a pull-request template, resolved against a fixed set of paths, the body is that template, filled, its sections and checkboxes kept. `implement:`, `vuln:` and `upgrade:` supply the facts. Prompted by mattpocock `pr`.

### Fixed
- **`implement:` Phase 4.6's "Every run" list named the Cancel arm of Phase 2B's repro prompt** as a stop after files were written, though that prompt runs before Pre-Phase 3 creates the branch; it is a member now only on Phase 3A step 5's re-plan, which reaches it after the edits. The list also named Pre-Phase 3.5's framework prompt among stops after files were written, though it comes before the first edit, and it named, as the one exit that does not reach Phase 4.6, an "Abandon implementation and restore to pre-impl state" arm Phase 3B no longer offers.
- **Phase 3.5 step 3 took its lint and build commands from Phase 2A's exploration**, which a run on the Phase 2B path never had — Phase 3B step 8 re-enters the step there. It now takes them from whichever exploration ran, or from the repository's own build and lint configuration.
`````

#### `cl/ie-dev-workflows.md`

`````markdown
## [2.68.0] — 2026-10-03

### Added
- **`/implement` looks before it asks.** Phase 1 tries to settle each candidate ambiguity from what the run can read — the inputs, the code, the repository's own `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` and `README.md`, and `git log` — and asks only a decision: a question the evidence leaves open and whose answer changes what the user would notice in the result. An open question the user would not notice is settled by the run and listed in the plan's Assumptions; nothing that changes the result is assumed. The mid-implementation stop in Phase 3A and Phase 3B applies the same test. Prompted by BMAD 7e571784.
- **`/implement` re-classifies upward.** Phase 2A writes its exploration to `summary_file` and re-tests the class against `classification.md` §1.1 with the file map — where the file count and the areas a change touches are first knowable — raising a run a trigger now applies to and continuing at Phase 2B without a second exploration. A `SIMPLE`/`MODERATE` run that meets, while implementing, a §1.1 trigger its approved plan did not state stops editing and re-plans once with `risk-planner`, which reads the diff so far through a new `Work so far` input; once the user approves, the run continues at Phase 3B under its review gate, without re-branching or re-capturing the baseline, and a Cancel there commits the work through Phase 4.6 with `clean_finish: false`. The class used to move only down, and such a run shipped with no review. Prompted by BMAD 124ea1af and 2c10d5ba.
- **The code pull-request body** (`code-repo-handoff` §2.7) holds four sections, with no preamble: a Summary; Evidence, a before and an after only as the run observed them; Merge danger, a one-way or two-way door — one-way where the run cannot tell — and the blast radius; and the Review. Where the repository carries a pull-request template, resolved against a fixed set of paths, the body is that template, filled, its sections and checkboxes kept. `/implement`, `/vuln` and `/upgrade` supply the facts. Prompted by mattpocock `pr`.

### Fixed
- **`/implement` Phase 4.6's "Every run" list named the Cancel arm of Phase 2B's repro prompt** as a stop after files were written, though that prompt runs before Pre-Phase 3 creates the branch; it is a member now only on Phase 3A step 5's re-plan, which reaches it after the edits. The list also named Pre-Phase 3.5's framework prompt among stops after files were written, though it comes before the first edit, and it named, as the one exit that does not reach Phase 4.6, an "Abandon implementation and restore to pre-impl state" arm Phase 3B no longer offers.
- **Phase 3.5 step 3 took its lint and build commands from Phase 2A's exploration**, which a run on the Phase 2B path never had — Phase 3B step 8 re-enters the step there. It now takes them from whichever exploration ran, or from the repository's own build and lint configuration.
`````

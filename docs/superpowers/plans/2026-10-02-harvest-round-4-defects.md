# Upstream harvest round 4 — Round 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the six defects the 2026-10-02 upstream survey found in text all three editions ship, in this repository, the internal edition and the Copilot edition.

**Architecture:** Prose edits to agent, command and reference files, applied through one whitespace-insensitive replace helper so a single edit file serves all three editions whatever their line wrapping. This edition first, then the internal edition, then the Copilot edition; each edition is gated, reviewed to zero findings, then merged. Item 1's git recipe is proven by a scratch-repository probe that fails on the current recipe and passes on the new one.

**Tech Stack:** Markdown prose run by agents; git; bash; python3 (helpers, gates); node (mermaid gate).

**Spec:** `docs/superpowers/specs/2026-10-02-harvest-round-4-defects-design.md`

## Global Constraints

- **Never name the internal edition in this repository.** Check 19 rejects, anywhere in the work tree, the pattern `EDITION_FORBIDDEN_B64` decodes to in `scripts/check-docs.sh` — the internal edition's short name as a bare word, its repository name, and the organisation's name. In this repository write "the internal edition" and `$IE`.
- **Prose is executed.** Every sentence added must be true of what the run does; a false one is a defect, not a typo.
- **Match the file's wrapping.** `code-review.md`, `risk-planner.md`, `implementation-format.md`, `handoff/diff-summarizer.md` and `grilling-technique.md`'s *Relationship* and *Autonomous* sections are hard-wrapped; the edit files below carry that wrapping. Every other touched passage is one long line.
- **Copilot dialect.** In `$CE`, skills are named `implement:`, `design:` (never `/implement`), shared references are `~/.copilot/installed-plugins/ihudak-copilot-plugins/dev-workflows/skills/_shared/<name>.md`, and `${CLAUDE_PLUGIN_ROOT}` never appears. None of the shared edit files below names a command or a path, so they apply to `$CE` unchanged.
- **Copilot instruction files stay under 20,000 characters** (`python3 -c 'import sys;print(len(open(sys.argv[1]).read()))' <file>`); `dev-workflows-shared.instructions.md` stands at 19,961.
- **Git discipline in this repository:** never `git checkout`/`switch` in `/workspace/ai-workflows` (work in `$AW`); run `git branch --show-current` immediately before every commit; never bare `git stash`.
- **Commit trailer:** `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.
- **Do not edit** `references/specification-format.md` (frozen).
- **Every `CHANGELOG.md` section is dated** (`2026-10-02`; re-date to the merge day if the merge slips) before it reaches `main` — check 18.
- **Zero known bugs:** every review finding — minors and nits included — is fixed before merge.

## Review Focus

1. **A branch merged into an intermediate branch before reaching the base** — `diff-summarizer` must read the branch's own files, not fall back and not return nothing. Pinned by the probe's `intermediate` case (Task 1).
2. **A re-run of `/implement` on an Epic whose every requirement an earlier run delivered** — dimension 10 must return every requirement `satisfied` (*already present*) and no `missing`. Pinned by Task 2 step 5's read-through.
3. **A grilling caller run with no human turn** — the confirmation gate must not block forever or self-confirm; the understanding is reported unconfirmed. Pinned by Task 4 step 4.
4. **`/idea` at its last bounded question** — the play-back must not consume a question slot. Pinned by Task 4 step 4.
5. **A merged PR whose forge-CLI range comes back empty, in the internal and Copilot editions** — the resolver must fall through to the local strategies, not report a summary of nothing. Pinned by Task 9 Step 5 and Task 10 Step 3.

---

### Task 0: Variables, helpers, branches

**Files:**
- Create (scratch, never committed): `$S/wsub.py`, `$S/count.py`, `$S/probe-landed.sh`, `$S/edits/*.txt`

**Interfaces:**
- Produces: `$AW`, `$IE`, `$CE`, `$S`; `wsub.py TARGET EDITFILE [--dry]` (exit 1 and no write on any count mismatch); `count.py ROOT TEXT [--regex] [--no-changelog] [--ignore-case]` (prints per-file hits and `TOTAL <n>`); `probe-landed.sh old|new` (exit 0 only when every case passes).

- [ ] **Step 1: Set the variables** (every later task assumes them)

```bash
AW=/workspace/.worktrees/ai-workflows-harvest-r4          # this repository's worktree, branch iv-gu/harvest-r4
IE=<the internal edition's checkout root under /workspace> # not written here: check 19
CE=/workspace/ihudak-copilot-plugins
S=/tmp/claude-502/-workspace-ai-workflows/d7e59186-271d-4a83-a94b-9e776fafee25/scratchpad/r4   # any scratch dir outside every repo
mkdir -p "$S/edits"
```

- [ ] **Step 2: Write `$S/wsub.py`**

```python
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
NEW is written verbatim. A count mismatch on any block aborts before anything is written.
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
    old, new = '\n'.join(b['old']), '\n'.join(b['new'])
    pat = re.compile(r'\s+'.join(map(re.escape, old.split())))
    found = len(pat.findall(text))
    if found != b['n']:
        sys.exit(f"ABORT {target}: expected {b['n']} match(es), found {found}, OLD begins {old[:80]!r}")
    text = pat.sub(lambda _m: new, text)
if not dry:
    open(target, 'w').write(text)
print(f"{'checked' if dry else 'applied'} {len(blocks)} block(s): {target}")
```

- [ ] **Step 3: Write `$S/count.py`**

```python
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
```

- [ ] **Step 4: Write `$S/probe-landed.sh`** — item 1's recipe, old and new, over seven histories

```bash
#!/usr/bin/env bash
# probe-landed.sh old|new — resolve seven histories with the recipe named; exit 1 on any FAIL.
set -u
W=$(mktemp -d); cd "$W" || exit 2
git init -q -b main r && cd r || exit 2
git config user.email p@p; git config user.name p
c(){ echo "$1" > "$1.txt"; git add -A; git commit -qm "$1"; }
resolve_old(){ git diff --name-only "$2...$1" | sort | tr '\n' ' '; }
resolve_new(){
  local bf=$1 bt=$2 landing range
  if git merge-base --is-ancestor "$bf" "$bt"; then
    landing=$(git rev-list --first-parent "$bf..$bt" | grep -Fx -f <(git rev-list --ancestry-path "$bf..$bt") | tail -1)
    if [ -n "$landing" ] && [ "$(git rev-list --parents -n1 "$landing" | wc -w)" -ge 3 ] \
       && ! git merge-base --is-ancestor "$bf" "$landing^1"; then
      range="$landing^1...$bf"
    else echo FALLBACK; return; fi
  else range="$bt...$bf"; fi
  if git diff --quiet "$range"; then echo FALLBACK; return; fi
  git diff --name-only "$range" | sort | tr '\n' ' '
}
fail=0
check(){ if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1: got [$2] want [$3]"; fail=1; fi; }
R=resolve_$1
c A
git switch -qc fa; c B; c C; FA=$(git rev-parse HEAD); git switch -q main; c D
check not-landed "$($R "$FA" main)" "B.txt C.txt "
git merge -q --no-ff fa -m Mfa; c E
check merge-commit "$($R "$FA" main)" "B.txt C.txt "
git switch -qc fb; c F; FB=$(git rev-parse HEAD); git switch -q main; git merge -q --ff-only fb; c G
check fast-forward "$($R "$FB" main)" "FALLBACK"
git switch -qc fc; c H; FC=$(git rev-parse HEAD); git switch -q main; git merge -q --squash fc; git commit -qm Sfc
check squash "$($R "$FC" main)" "H.txt "
git switch -qc int; git switch -qc fd; c I; FD=$(git rev-parse HEAD); git switch -q int; c J; git merge -q --no-ff fd -m Mfd
git switch -q main; c K; git merge -q --no-ff int -m Mint
check intermediate "$($R "$FD" main)" "I.txt "
git switch -qc fe; git commit -q --allow-empty -m empty; FE=$(git rev-parse HEAD); git switch -q main; c L
check empty-range "$($R "$FE" main)" "FALLBACK"
git switch -qc fg; c M; git merge -q --no-ff main -m Nbk; FG=$(git rev-parse HEAD); git switch -q main; git merge -q --ff-only fg
check backwards-ff "$($R "$FG" main)" "FALLBACK"
rm -rf "$W"; exit $fail
```

Run: `chmod +x $S/*.py $S/probe-landed.sh; $S/probe-landed.sh old 2>/dev/null; echo "EXIT=$?"; $S/probe-landed.sh new 2>/dev/null; echo "EXIT=$?"`
Expected: `old` prints 5 `FAIL` lines (merge-commit, fast-forward, intermediate, empty-range, backwards-ff) and `EXIT=1`; `new` prints 7 `PASS` and `EXIT=0`.

- [ ] **Step 5: Branch the other two editions** (both repositories are this session's alone)

```bash
for r in "$IE" "$CE"; do git -C "$r" fetch -q --all && git -C "$r" switch main && git -C "$r" pull -q --ff-only && git -C "$r" switch -c iv-gu/harvest-r4 && git -C "$r" status -sb | head -1; done
git -C "$AW" branch --show-current   # expect iv-gu/harvest-r4
```

- [ ] **Step 6: Record the before-counts** used by later tasks

```bash
for r in "$AW" "$IE" "$CE"; do python3 $S/count.py "$r" 'design tree' --ignore-case --no-changelog | tail -1; done
```
Expected: `TOTAL 8`, `TOTAL 11`, `TOTAL 11`.

---

### Task 1: `diff-summarizer` — landed refs and empty ranges (this edition)

**Files:**
- Modify: `$AW/plugins/docs-workflows/agents/diff-summarizer.md` (the *`refs` is the shape* paragraph, *Key-commit fallback* first sentence, `## Hard rules`)
- Modify: `$AW/plugins/docs-workflows/references/handoff/diff-summarizer.md:29-34`
- Modify: `$AW/plugins/workflows-core/references/implementation-format.md:90-92`

**Interfaces:**
- Consumes: `wsub.py`, `count.py`, `probe-landed.sh` (Task 0)
- Produces: edit files `$S/edits/E1a.txt`, `E1b.txt`, `E1c.txt` (this edition only)

- [ ] **Step 1: Confirm the failing recipe** — `$S/probe-landed.sh old; echo EXIT=$?` → 5 FAIL, `EXIT=1`. This is the three-dot range the agent states today.

- [ ] **Step 2: Write `$S/edits/E1a.txt`** (the agent)

````text
<<<<<<< OLD 1
with `branch_from` accepted as a commit sha when the branch is gone (`workflows-core:implementation-format` §1 records both for exactly that reason).
=======
with `branch_from` accepted as a commit sha when the branch is gone (`workflows-core:implementation-format` §1 records both for exactly that reason).

**A ref that has already landed has an empty three-dot range, so test for it before taking the diff.** Run `git -C "<repo_path>" merge-base --is-ancestor <branch_from> <branch_to>` first. Where it exits non-zero, `branch_from` has not landed on `branch_to`, and the three-dot diff above is the element's content. Where it exits 0, the work reached `branch_to` by a merge commit or a fast-forward, the range's merge base *is* `branch_from`, and `<branch_to>...<branch_from>` is empty by construction. Read the element from the merge that landed it instead:

1. **Find `landing`** — the oldest commit on `branch_to`'s first-parent line that descends from `branch_from`: the last commit `git -C "<repo_path>" rev-list --first-parent <branch_from>..<branch_to>` lists that `git -C "<repo_path>" rev-list --ancestry-path <branch_from>..<branch_to>` lists too. Take the two lists separately and intersect them: the two flags in one call follow first-parent edges only, and find nothing for a branch that reached `branch_to` through an intermediate branch's merge.
2. **Read the merge.** Where `landing` exists, `git -C "<repo_path>" rev-list --parents -n 1 <landing>` names two or more parents, and `git -C "<repo_path>" merge-base --is-ancestor <branch_from> <landing>^1` exits non-zero — `branch_from` arrived through one of the merge's later parents — the element's diff is `git -C "<repo_path>" diff <landing>^1...<branch_from>`, with `resolved_via: local_ref` and `base` the merge base of `<landing>^1` and `branch_from`. That is the branch's own work from its fork point, which is what the three-dot range read before the merge.
3. **Otherwise there is no merge to read** — no `landing`, a `landing` with one parent (a fast-forward), or a `branch_from` the merge's first parent already holds. The element goes to the **Key-commit fallback** below.

**An empty range is never a resolution.** Where the range an element resolved to changes no file (`git -C "<repo_path>" diff --quiet <range>` exits 0), do not report it `local_ref` with `files_changed: 0`. It goes to the Key-commit fallback, and where that finds nothing, to `unresolved_prs` with the range named in its `reason`. A summary of nothing tells the caller the work changed nothing, and `/document` and `/release-notes` would write from it.
>>>>>>> NEW
<<<<<<< OLD 1
Reached only where an element's own diff does not resolve — `branch_from` is neither a branch in the clone nor a commit in it, which is what a squash-merge leaves behind.
=======
Reached where an element's own diff does not resolve, in one of three ways: `branch_from` is neither a branch in the clone nor a commit in it, which is what a squash-merge leaves behind; it landed on `branch_to` with no merge commit to read it from (step 3 above); or the range it resolved to changes no file (above).
>>>>>>> NEW
<<<<<<< OLD 1
- NEVER fabricate diff content. If an element cannot be resolved, record it in `unresolved_prs`.
=======
- NEVER fabricate diff content. If an element cannot be resolved, record it in `unresolved_prs`.
- NEVER report an empty range as resolved. A `local_ref` element changes at least one file; one whose range changes none goes to the Key-commit fallback, then to `unresolved_prs`.
>>>>>>> NEW
````

- [ ] **Step 3: Write `$S/edits/E1b.txt`** (the handoff)

````text
<<<<<<< OLD 1
The diff is taken directly
(`git -C <repo_path> diff <branch_to>...<branch_from>`, `branch_from` accepted as a commit sha when
the branch is gone); where neither resolves, the agent's **Key-commit fallback** greps
`keys_hierarchy` when the caller supplied one.
=======
The diff is taken directly
(`git -C <repo_path> diff <branch_to>...<branch_from>`, `branch_from` accepted as a commit sha when
the branch is gone) — except where `branch_from` has already landed on `branch_to`, which empties
that range: the agent then reads the merge that landed it (`<landing>^1...<branch_from>`). Where
neither resolves, where a fast-forward left no merge to read, or where a range changes no file, the
agent's **Key-commit fallback** greps `keys_hierarchy` when the caller supplied one. An empty range
is never reported as resolved.
>>>>>>> NEW
````

- [ ] **Step 4: Write `$S/edits/E1c.txt`** (`implementation-format.md` §1)

````text
<<<<<<< OLD 1
**Branch for convenience, commit for durability.** A merged branch is deleted; the squashed commit
stays reachable from the base. `diff-summarizer` accepts either, and recording both is what makes the
file survive branch cleanup.
=======
**Branch for convenience, commit for durability.** A merged branch is usually deleted, so the record
names the commit as well. After a merge commit or a fast-forward that commit is reachable from the
base; after a squash-merge no branch reaches it once its own is deleted, and it survives only while a
clone still holds it — which is why `diff-summarizer` falls back to a key-commit search there.
`diff-summarizer` accepts either, and recording both is what makes the file survive branch cleanup;
how it reads a commit that has already landed on the base is that agent's own rule.
>>>>>>> NEW
````

- [ ] **Step 5: Apply** — dry first, then for real

```bash
cd "$AW"
for p in "plugins/docs-workflows/agents/diff-summarizer.md E1a" "plugins/docs-workflows/references/handoff/diff-summarizer.md E1b" "plugins/workflows-core/references/implementation-format.md E1c"; do set -- $p; python3 $S/wsub.py "$1" "$S/edits/$2.txt" --dry || break; done
for p in "plugins/docs-workflows/agents/diff-summarizer.md E1a" "plugins/docs-workflows/references/handoff/diff-summarizer.md E1b" "plugins/workflows-core/references/implementation-format.md E1c"; do set -- $p; python3 $S/wsub.py "$1" "$S/edits/$2.txt"; done
```
Expected: three `checked`, then three `applied` lines.

- [ ] **Step 6: Verify** — the recipe and the prose

```bash
$S/probe-landed.sh new 2>/dev/null; echo "EXIT=$?"                                       # 7 PASS, EXIT=0
python3 $S/count.py "$AW" 'An empty range is never a resolution' | tail -1               # TOTAL 1
python3 $S/count.py "$AW" '<landing>^1...<branch_from>' | tail -1                        # TOTAL 2 (agent, handoff; Task 7's changelog adds a third)
python3 $S/count.py "$AW" 'the squashed commit stays reachable from the base' | tail -1  # TOTAL 0
python3 $S/count.py "$AW" 'Reached only where an element' | tail -1                      # TOTAL 0
python3 $S/count.py "$AW" '--first-parent --ancestry-path' | tail -1                     # TOTAL 0
```
Then read the agent's `## Inputs` through `## Key-commit fallback` end to end: the new steps must agree with the Output block's `resolved_via` enum (`local_ref | key_commits | unresolved` — unchanged) and with `PARTIAL`'s definition in the handoff's status table (unchanged: a fallback-resolved element still makes the run `PARTIAL`).

- [ ] **Step 7: Sweep the claim subject** — how a ref becomes a range, and when the fallback is reached

```bash
python3 $S/count.py "$AW" '<branch_to>...<branch_from>' | tail -3
grep -rn -i "squash" "$AW"/plugins/docs-workflows/commands/{document,release-notes}.md "$AW"/plugins/docs-workflows/docs/commands/{document,release-notes}.md | grep -i -E "diff|ref|reach" 
```
Expected: the range appears only in the agent and its handoff (`ref:` template lines included); no caller or docs page states a range or a reachability claim. Any hit that does gets rewritten to match.

- [ ] **Step 8: Commit**

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4 && git add plugins/docs-workflows/agents/diff-summarizer.md plugins/docs-workflows/references/handoff/diff-summarizer.md plugins/workflows-core/references/implementation-format.md && git commit -q -m "fix(diff-summarizer): read a landed ref from its merge; an empty range is never resolved

A ref merged by a merge commit or a fast-forward is an ancestor of its base, so the
three-dot range was empty and the element reported OK with zero files.

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" && git log --oneline -1
```

---

### Task 2: Code review's spec coverage reads the code, and reports over-build (this edition)

**Files:**
- Modify: `$AW/plugins/dev-workflows/agents/code-review.md:138-148` (dimension 10) and its output template (`#### Spec/design conformance`)
- Modify: `$AW/plugins/dev-workflows/commands/implement.md` (step 7.5; Phase 5 `### Spec/design conformance` line)
- Modify: `$AW/.claude/rules/dev-workflows.md:22`

**Interfaces:**
- Consumes: `wsub.py`, `count.py`
- Produces: `$S/edits/E2a.txt` (code-review), `E2d.txt` (implement), `E2f.txt` (rules line) — reused verbatim by Tasks 9 and 11

- [ ] **Step 1: Confirm the defect** — `python3 $S/count.py "$AW" 'requirement against the diff and classify it' | tail -1` → `TOTAL 1`.

- [ ] **Step 2: Write `$S/edits/E2a.txt`**

````text
<<<<<<< OLD 1
    trace each `in_scope_ids` requirement against the diff and classify it:
    `satisfied` / `missing` / `partial` / `contradicts`. This checks
    design→**code** — it does NOT re-verify spec→design traceability (that is
    `design-reviewer`'s pre-code job). Severity:
=======
    classify each `in_scope_ids` requirement against **the code as it stands
    after this change**, not against the diff alone: `satisfied` / `missing` /
    `partial` / `contradicts`. Start from the diff; where the diff does not
    deliver a requirement, search the codebase before classifying it — a
    requirement an earlier run, or code predating the spec, already delivers
    is `satisfied`, counted as *already present*. A plan step's
    `implements [ID]` tag, an earlier implementation record and a ticked box
    are claims about coverage, not evidence of it: verify the behaviour in the
    code either way. Then report **`exceeds`**: behaviour this change adds that
    no in-scope requirement and no plan step asks for — judged on the diff
    only, since code that predates the change is not this change's
    over-build. This checks design→**code** — it does NOT re-verify
    spec→design traceability (that is `design-reviewer`'s pre-code job).
    Severity:
>>>>>>> NEW
<<<<<<< OLD 1
    - `partial` → `MINOR`.
=======
    - `partial` → `MINOR`.
    - `exceeds` → `MINOR`; `MAJOR` where it builds something the plan's or the
      design's `Out of scope` names. Report-only: no caller writes it onto the
      spec.
>>>>>>> NEW
<<<<<<< OLD 1
- Coverage: [N satisfied / M missing / P partial / C contradicts]
- [severity] `[ACxx]` - [missing | partial | contradicts] - [what the diff
  does vs. what the requirement demands]
=======
- Coverage: [N satisfied (K already present) / M missing / P partial / C contradicts / X exceeds]
- [severity] `[ACxx]` - [missing | partial | contradicts] - [what the code
  does vs. what the requirement demands]
- [severity] `path:line` - exceeds - [what the change adds that no in-scope
  requirement or plan step asks for]
>>>>>>> NEW
````

- [ ] **Step 3: Write `$S/edits/E2d.txt`** (`/implement`)

````text
<<<<<<< OLD 1
The notes are written here and handed off later — see the escalation handoff after Phase 4.
=======
The notes are written here and handed off later — see the escalation handoff after Phase 4. **`exceeds` findings are never written here**: they report what this change added beyond the spec, which the Phase 5 report carries and the review cycle acts on — not a gap in the spec.
>>>>>>> NEW
<<<<<<< OLD 1
list any missing/partial/contradicts — or "N/A";
=======
list any missing/partial/contradicts/exceeds, and the already-present count — or "N/A";
>>>>>>> NEW
````

- [ ] **Step 4: Write `$S/edits/E2f.txt`** (the rules/instructions copy — same length, so the Copilot file stays under its cap)

````text
<<<<<<< OLD 1
`[Uxx]`/`[ACxx]`/`[TCxx]` against the shipped diff.
=======
`[Uxx]`/`[ACxx]`/`[TCxx]` against the shipped code.
>>>>>>> NEW
````

- [ ] **Step 5: Apply, then verify**

```bash
cd "$AW"
python3 $S/wsub.py plugins/dev-workflows/agents/code-review.md $S/edits/E2a.txt
python3 $S/wsub.py plugins/dev-workflows/commands/implement.md $S/edits/E2d.txt
python3 $S/wsub.py .claude/rules/dev-workflows.md $S/edits/E2f.txt
python3 $S/count.py "$AW" 'against the diff and classify it' | tail -1        # TOTAL 0
python3 $S/count.py "$AW" 'the code as it stands after this change' | tail -1 # TOTAL 1
python3 $S/count.py "$AW" '`exceeds` findings are never written here' | tail -1  # TOTAL 1
python3 $S/count.py "$AW" 'against the shipped diff' | tail -1                 # TOTAL 0
```
Read-through (Review Focus 2): with an Epic whose `[AC01]`–`[AC05]` an earlier run delivered and a diff touching none of them, the edited dimension says to search the codebase, find each, and classify it `satisfied`, *already present* — zero `missing`, so step 7.5 writes nothing. Confirm by reading dimension 10 and step 7.5 together.

- [ ] **Step 6: Sweep** — what dimension 10 classifies against, and its class set

```bash
python3 $S/count.py "$AW" 'missing/partial/contradicts' | tail -4
python3 $S/count.py "$AW" '10th dimension' | tail -3
```
Expected: every hit either now names `exceeds` or describes only the escalated pair (`missing`/`contradicts` in step 7.5, Phase 4.5 and Hard rules, which stay as they are). Read `implement.md` Phase 4.5 and its Hard rules bullet on spec escalation: both escalate `missing`/`contradicts` only, which stays true.

- [ ] **Step 7: Commit**

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4 && git add plugins/dev-workflows/agents/code-review.md plugins/dev-workflows/commands/implement.md .claude/rules/dev-workflows.md && git commit -q -m "fix(code-review): spec coverage reads the code, not the diff alone; report exceeds

A requirement an earlier run delivered was classified missing (MAJOR), driving
review-fixer and a spurious spec note. Plan tags are claims, not evidence.

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" && git log --oneline -1
```

---

### Task 3: `risk-planner` — "Unambiguous, not complete" (this edition)

**Files:**
- Modify: `$AW/plugins/dev-workflows/agents/risk-planner.md:131-135`

**Interfaces:**
- Produces: `$S/edits/E3.txt` — reused verbatim by Tasks 9 and 11

- [ ] **Step 1: Confirm** — `python3 $S/count.py "$AW" 'without *how*' | tail -1` → `TOTAL 1`.

- [ ] **Step 2: Write `$S/edits/E3.txt`**

````text
<<<<<<< OLD 1
- **No placeholders.** Before returning, re-read the plan and replace any
  placeholder with concrete content: "TBD", "add proper error handling",
  "handle edge cases", "similar to step N", or any step that says *what*
  without *how*. A plan step that a fresh engineer could not act on is a plan
  failure.
=======
- **Unambiguous, not complete.** A step is done when the implementer can do
  exactly one reasonable thing from it; nothing more is asked of it. Each step
  names what makes it unambiguous: the file it touches; for anything new, its
  exact signature (name, parameters, return type); every value the spec or
  design pins, **quoted verbatim** — a maximum length, required vs nullable, an
  enum's values, a validation rule — never paraphrased or left to be looked
  up, because an implementer who does not find it invents its own; and, for a
  verification step, the command to run and the output that means it passed.
  Before returning, re-read the plan for both failures: a line that decides
  nothing ("TBD", "add proper error handling", "handle edge cases", "similar
  to step N", a type or function no step defines), and a step that writes out
  the body the implementer would write. **Proportion check:** a plan several
  times longer than the change it describes has written the code instead —
  cut it back to the decisions.
>>>>>>> NEW
````

- [ ] **Step 3: Apply and verify**

```bash
cd "$AW" && python3 $S/wsub.py plugins/dev-workflows/agents/risk-planner.md $S/edits/E3.txt
python3 $S/count.py "$AW" 'No placeholders' --no-changelog | tail -1   # TOTAL 0
python3 $S/count.py "$AW" 'Unambiguous, not complete' | tail -1        # TOTAL 1
```
Read the agent's `## Hard rules` beside it: `NEVER produce code patches` agrees (a signature and a quoted value are not a patch).

- [ ] **Step 4: Commit**

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4 && git add plugins/dev-workflows/agents/risk-planner.md && git commit -q -m "fix(risk-planner): replace the withdrawn 'what without how' rule

Upstream writing-plans removed it: it drove Opus plans to code size. A step is
unambiguous, not complete; spec-pinned values are quoted verbatim.

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" && git log --oneline -1
```

---

### Task 4: The grilling reference — confirmation gate and play-back (this edition)

**Files:**
- Modify: `$AW/plugins/workflows-core/references/grilling-technique.md` (Mechanics last bullet, `## Autonomous / background invocation`, `## Relationship …` *Read upstream* paragraph, `## Depth` *Relentless* bullet)

**Interfaces:**
- Produces: `$S/edits/E4.txt` (this edition only); the play-back bullet text, reused verbatim in `$S/edits/E5-ed.txt` (Task 9)

- [ ] **Step 1: Confirm** — `python3 $S/count.py "$AW" 'Reaching a shared understanding is the user' | tail -1` → `TOTAL 0` (the bare phrase "confirmation gate" already appears twice, on unrelated `/upgrade` and `/brd-reconcile` docs pages).

- [ ] **Step 2: Write `$S/edits/E4.txt`**

````text
<<<<<<< OLD 1
- Continue until you and the user reach a **shared understanding** for the current section, then write that section.
=======
- **The confirmation gate.** Reaching a shared understanding is the user's call to declare, not yours to infer from a quiet turn. The gate fires **wherever understanding is about to become an artifact or an irreversible step** — before writing a section, and again before a reviewer dispatch, a handoff, or a commit. It is therefore *not* a single end-of-interview event: a caller that writes its artifact section by section — its own interview-technique paragraph says it writes *each section* or *that stage's section* — closes the gate for each section as the interview settles it, over the part that is settled, and the frontier keeps turning afterwards. Confirming a section is not confirming the whole artifact.
- **At the gate, play the understanding back.** In a few lines, state what is settled for the part about to be written — the intended outcome, the constraints, what success looks like — marking what the user said and what you inferred, then ask the user to confirm or correct it. An inference the user has not confirmed is still an assumption, and it is the line most worth their reading. The play-back asks no decision, so it spends no slot of a bounded caller's cap and is not numbered against it.
>>>>>>> NEW
<<<<<<< OLD 1
Never grill yourself into a fabricated decision.
=======
Never grill yourself into a fabricated
decision. The confirmation gate cannot be self-satisfied either: with no human turn the understanding
is unconfirmed, and the caller reports it as such.
>>>>>>> NEW
<<<<<<< OLD 1
**Read upstream for ideas, not for parity — and three have already been taken.** Its *frontier*
framing, its rendered question format, and its rule that a fact is fetched rather than asked are all
in the Mechanics and Depth sections above, each marked where it landed. **Each was ported in part,
and the part left behind was left behind for the same reason every time**: the half that depends on
asking a whole round at once. Upstream's frontier is *asked* wholesale where ours supplies the next
question; its numbering counts a round where ours counts against a cap; its fetch-a-fact rule is
non-blocking because the rest of the round proceeds meanwhile. A future port should expect the same
split rather than assume an idea arrives whole. Port deliberately, record it here, and do not cite
upstream at runtime.
=======
**Read upstream for ideas, not for parity — and four have already been taken.** Its *frontier*
framing, its rendered question format, and its rule that a fact is fetched rather than asked are all
in the Mechanics and Depth sections above, each marked where it landed. **Each of those three was
ported in part, and the part left behind was left behind for the same reason every time**: the half
that depends on asking a whole round at once. Upstream's frontier is *asked* wholesale where ours
supplies the next question; its numbering counts a round where ours counts against a cap; its
fetch-a-fact rule is non-blocking because the rest of the round proceeds meanwhile. **The fourth, its
confirmation gate, was ported whole, because nothing in it depends on a round**: it closes the
Mechanics list, with a play-back of the understanding beside it adapted from superpowers'
brainstorming skill. A future port should expect the three's split wherever an idea leans on asking a
round at once, rather than assume an idea arrives whole. Port deliberately, record it here, and do
not cite upstream at runtime.
>>>>>>> NEW
<<<<<<< OLD 1
- **Relentless** — keep walking the tree until convergence, no cap.
=======
- **Relentless** — keep asking from the frontier until convergence, no cap.
>>>>>>> NEW
````

- [ ] **Step 3: Apply** — `cd "$AW" && python3 $S/wsub.py plugins/workflows-core/references/grilling-technique.md $S/edits/E4.txt`

- [ ] **Step 4: Verify** (Review Focus 3 and 4)

```bash
python3 $S/count.py "$AW" 'The confirmation gate cannot be self-satisfied' | tail -1   # TOTAL 1
python3 $S/count.py "$AW" 'spends no slot of a bounded caller' | tail -1                # TOTAL 1
python3 $S/count.py "$AW" 'keep walking the tree' | tail -1                             # TOTAL 0
python3 $S/count.py "$AW" 'Continue until you and the user reach' | tail -1             # TOTAL 0
```
Then read the whole file once: the *Relationship* table's first row (one question at a time) still holds — the gate asks no question; *Depth*'s bounded paragraph (`Q<n>/<cap>`) still holds — the play-back is not numbered.

- [ ] **Step 5: Commit**

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4 && git add plugins/workflows-core/references/grilling-technique.md && git commit -q -m "feat(grilling): the confirmation gate, with a play-back of the understanding

Shared understanding is the user's to declare. Ported from upstream grilling;
the play-back is adapted from superpowers' brainstorming.

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" && git log --oneline -1
```

---

### Task 5: Grilling callers and docs — "design tree" and the gate (this edition)

**Files:**
- Modify: `$AW/plugins/dev-workflows/commands/design.md:258`
- Modify: `$AW/plugins/product-workflows/commands/{create-prd.md:523,create-ard.md:562,specify.md:817,update-prd.md:123,idea.md:401,406,413-414}`
- Modify: `$AW/plugins/product-workflows/docs/reference/model-routing.md:23`
- Modify: `$AW/plugins/workflows-core/docs/reference/references.md:16`

**Interfaces:**
- Consumes: Task 4's gate (the callers now name it)

- [ ] **Step 1: Write the edit files**

`$S/edits/E5-design.txt`:
````text
<<<<<<< OLD 1
walk the design tree in dependency order, continue to shared understanding then write the section.
=======
ask from the frontier, and clear the confirmation gate before writing the section.
>>>>>>> NEW
````

`$S/edits/E5-each.txt` (applied to `create-prd.md` and to `create-ard.md`):
````text
<<<<<<< OLD 1
walk the design tree in dependency order, continue to shared understanding then write each section.
=======
ask from the frontier, and clear the confirmation gate before writing each section.
>>>>>>> NEW
````

`$S/edits/E5-specify.txt`:
````text
<<<<<<< OLD 1
walk the design tree in dependency order, continue to shared understanding then write that stage's section.
=======
ask from the frontier, and clear the confirmation gate before writing that stage's section.
>>>>>>> NEW
````

`$S/edits/E5-update-prd.txt`:
````text
<<<<<<< OLD 1
recommend each answer, fact-vs-decision split, dependency order.
=======
recommend each answer, fact-vs-decision split, ask from the frontier, and clear the confirmation gate before writing.
>>>>>>> NEW
````

`$S/edits/E5-idea.txt`:
````text
<<<<<<< OLD 1
walk the design tree in dependency order. **Depth: bounded by default (below); `--deep` = relentless.**
=======
ask from the frontier, and clear the confirmation gate before writing. **Depth: bounded by default (below); `--deep` = relentless.**
>>>>>>> NEW
<<<<<<< OLD 1
Seed the design tree with every `firm` entry of the Phase 2 `stated_scope` as an already-made decision
=======
Count every `firm` entry of the Phase 2 `stated_scope` among the settled decisions the frontier starts from
>>>>>>> NEW
<<<<<<< OLD 1
- **`--deep`:** relentless — keep walking the design tree one question at a time until you and the user
  reach shared understanding; the cap does not apply.
=======
- **`--deep`:** relentless — keep asking from the frontier, one question at a time, until the user
  confirms a shared understanding at the confirmation gate; the cap does not apply.
>>>>>>> NEW
````

`$S/edits/E5-mr-doc.txt`:
````text
<<<<<<< OLD 1
how relentlessly it walks the design tree rather than which agent gets dispatched
=======
how relentlessly it grills rather than which agent gets dispatched
>>>>>>> NEW
````

`$S/edits/E5-refs-doc.txt`:
````text
<<<<<<< OLD 1
and the file records where the two deliberately diverge.
=======
and the file records where the two deliberately diverge. Its confirmation gate — the user's to close, never the agent's — stands before every write and every outward step, and is where the agent plays its understanding back for correction.
>>>>>>> NEW
````

- [ ] **Step 2: Apply**

```bash
cd "$AW"
P=plugins/product-workflows
python3 $S/wsub.py plugins/dev-workflows/commands/design.md $S/edits/E5-design.txt
python3 $S/wsub.py $P/commands/create-prd.md $S/edits/E5-each.txt
python3 $S/wsub.py $P/commands/create-ard.md $S/edits/E5-each.txt
python3 $S/wsub.py $P/commands/specify.md $S/edits/E5-specify.txt
python3 $S/wsub.py $P/commands/update-prd.md $S/edits/E5-update-prd.txt
python3 $S/wsub.py $P/commands/idea.md $S/edits/E5-idea.txt
python3 $S/wsub.py $P/docs/reference/model-routing.md $S/edits/E5-mr-doc.txt
python3 $S/wsub.py plugins/workflows-core/docs/reference/references.md $S/edits/E5-refs-doc.txt
```

- [ ] **Step 3: Verify the counts** (before → after)

```bash
python3 $S/count.py "$AW" 'design tree' --ignore-case --no-changelog | tail -1        # 8 → TOTAL 0
python3 $S/count.py "$AW" 'continue to shared understanding' | tail -1                 # TOTAL 0
python3 $S/count.py "$AW" 'clear the confirmation gate before writing' | tail -1       # TOTAL 6
python3 $S/count.py "$AW" 'shared understanding' --no-changelog | tail -3              # grilling-technique.md (gate) and idea.md (--deep) only
```

- [ ] **Step 4: Sweep the subject** — when the grill may write

Read each grilling caller's interview paragraph (`grep -l grilling-technique plugins/*/commands/*.md`): `/brd-split`, `/prompt-grill-me`, `/prd-proposal` and `/brd-proposal` cite the reference and state no write moment of their own, so the reference's gate governs them — no edit. Read the docs pages that describe a grill (`plugins/product-workflows/docs/commands/idea.md`, `plugins/workflows-core/docs/commands/prompt-grill-me.md`, `plugins/product-workflows/docs/getting-started.md`): any sentence saying the grill writes as soon as it converges, or that the question cap counts every turn, gets rewritten; a sentence saying "up to ten questions" stays true (the play-back is not a question).

- [ ] **Step 5: Commit**

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4 && git add plugins/dev-workflows/commands/design.md plugins/product-workflows plugins/workflows-core/docs/reference/references.md && git commit -q -m "fix(grilling callers): ask from the frontier and clear the confirmation gate

'Walk the design tree' named a mechanic the reference had replaced and a term
that collides with design.md.

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" && git log --oneline -1
```

---

### Task 6: `test-baseliner` — the suite's own exit status (this edition)

**Files:**
- Modify: `$AW/plugins/dev-workflows/agents/test-baseliner.md:102` (capture step 2) and `:202` (verify step 3)

**Interfaces:**
- Produces: `$S/edits/E6.txt` — reused verbatim by Tasks 9 and 11

- [ ] **Step 1: Confirm** — `python3 $S/count.py "$AW" 'never from a pipe after it' | tail -1` → `TOTAL 0`.

- [ ] **Step 2: Write `$S/edits/E6.txt`**

````text
<<<<<<< OLD 1
Capture stdout and stderr combined **per suite**. **The project root is that directory only
=======
Capture stdout and stderr combined **per suite**, and read each suite's exit status from **its own command, never from a pipe after it**: a pipeline's exit status is its last command's, so a failing suite run through `| tail`, `| head`, `| grep` or `| tee` exits 0, and a suite recorded by its exit status alone (step 3's *Exit status is the result where the output yields no other*) is then recorded passing. Where the output is too long to read whole, redirect it to a temp file and take the status in the same call — `<command> > <file> 2>&1; echo "exit=$?"` — then read the file. **The project root is that directory only
>>>>>>> NEW
<<<<<<< OLD 1
and the same run order. Capture stdout and stderr combined per suite.
=======
and the same run order. Capture stdout and stderr combined per suite, and take each suite's exit status from its own command, never from a pipe after it — the capture mode's step 2 says why, and how to trim long output without losing the status.
>>>>>>> NEW
````

- [ ] **Step 3: Apply and verify**

```bash
cd "$AW" && python3 $S/wsub.py plugins/dev-workflows/agents/test-baseliner.md $S/edits/E6.txt
python3 $S/count.py "$AW" 'never from a pipe after it' | tail -1   # TOTAL 2
grep -n -i -E "exit status|pipe" plugins/dev-workflows/references/handoff/test-baseliner.md plugins/dev-workflows/docs/reference/test-suite-detection.md
```
Expected: the handoff and docs page state what a status-only suite records, never how a command is invoked — no edit. A statement of invocation there would be rewritten to match.

- [ ] **Step 4: Commit**

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4 && git add plugins/dev-workflows/agents/test-baseliner.md && git commit -q -m "fix(test-baseliner): read a suite's exit status from its own command

Through a pipe the filter's status is read, and a failing status-only suite
was recorded passing.

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" && git log --oneline -1
```

---

### Task 7: Release this edition — versions, changelogs, gates

**Files:**
- Modify: `$AW/.claude-plugin/marketplace.json` (four `version` fields), `$AW/plugins/{workflows-core,dev-workflows,product-workflows,docs-workflows}/.claude-plugin/plugin.json`
- Modify: the same four plugins' `CHANGELOG.md`

- [ ] **Step 1: Bump the versions** — `workflows-core` 1.9.1→1.10.0, `dev-workflows` 4.4.3→4.5.0, `product-workflows` 3.11.2→3.11.3, `docs-workflows` 1.4.5→1.4.6

```bash
cd "$AW" && python3 - <<'EOF'
import json, re
bumps = {'workflows-core': ('1.9.1', '1.10.0'), 'dev-workflows': ('4.4.3', '4.5.0'),
         'product-workflows': ('3.11.2', '3.11.3'), 'docs-workflows': ('1.4.5', '1.4.6')}
for name, (old, new) in bumps.items():
    p = f'plugins/{name}/.claude-plugin/plugin.json'
    s = open(p).read(); assert f'"version": "{old}"' in s, p
    open(p, 'w').write(s.replace(f'"version": "{old}"', f'"version": "{new}"', 1))
m = '.claude-plugin/marketplace.json'; s = open(m).read()
for name, (old, new) in bumps.items():
    pat = re.compile(r'("name":\s*"' + re.escape(name) + r'"[^}]*?"version":\s*")' + re.escape(old) + '"', re.S)
    s, n = pat.subn(lambda mm: mm.group(1) + new + '"', s); assert n == 1, (name, n)
open(m, 'w').write(s)
for e in json.load(open(m))['plugins']:
    if e['name'] in bumps: print(e['name'], e['version'])
EOF
```
Expected: the four names with their new versions.

- [ ] **Step 2: Write the changelog sections** — each inserted directly above the plugin's current top `## [` section

`plugins/workflows-core/CHANGELOG.md`:
```markdown
## [1.10.0] — 2026-10-02

### Added
- **`grilling-technique.md` gains the confirmation gate.** Reaching a shared understanding is the user's to declare, never the agent's to infer from a quiet turn: the gate fires wherever understanding is about to become an artifact or an irreversible step — before writing a section, and before a reviewer dispatch, a handoff or a commit — and a caller that writes section by section closes it per section. In autonomous or background invocation it cannot be self-satisfied, and the understanding is reported unconfirmed. Ported from upstream `grilling`; the July harvest had skipped it as "already a superset", which covered only the autonomous half. Previously the Mechanics ended *"Continue until you and the user reach a shared understanding … then write that section"*, which left the judgement with the agent.
- **At the gate, the agent plays its understanding back** — the intended outcome, the constraints and what success looks like, marking what the user said and what was inferred — and asks for confirmation or correction. The play-back asks no decision, so it spends no slot of a bounded caller's cap. Adapted from superpowers' brainstorming skill.

### Fixed
- **`implementation-format.md` §1 said a merged branch's recorded commit "stays reachable from the base"** for every merge style. After a squash-merge no branch reaches it once its own is deleted; the paragraph now says what is true per merge style, and that how a landed commit is read is `diff-summarizer`'s rule.
- **`grilling-technique.md`'s relentless depth said "keep walking the tree"**, a mechanic the file had replaced with asking from the frontier.
```

`plugins/dev-workflows/CHANGELOG.md`:
```markdown
## [4.5.0] — 2026-10-02

**Update `workflows-core` to 1.10.0 with this release**: `/design`'s interview paragraph now clears that version's confirmation gate.

### Added
- **`code-review`'s spec/design-conformance dimension reports `exceeds`** — behaviour the change adds that no in-scope requirement and no plan step asks for, judged on the diff only. `MINOR`, or `MAJOR` where it builds what the plan's or design's `Out of scope` names; report-only, never written onto the spec by `/implement` step 7.5. Upstream spec-kit's converge (#4621) flags code that "exceeds" the stated intent; this family's July adoption left that class out without recording why.

### Changed
- **`risk-planner`'s step rule is "Unambiguous, not complete"**, replacing *No placeholders*. A step names the file, the exact signature of anything new, every value the spec or design pins quoted verbatim, and for a verification step the command and the output that means it passed; the self-review checks both for lines that decide nothing and for steps that write the implementer's code, plus a proportion check. Upstream writing-plans withdrew the *"steps that say what without how"* wording this agent carried, measuring plans at a quarter of the time and a third of the tokens with no loss of planted-defect catches; the verbatim-constraint rule is from spec-kit's tasks template (#4430).

### Fixed
- **`code-review` dimension 10 classified requirements against the diff alone.** A keyed `/implement` run's in-scope IDs are the whole unit's, so a requirement an earlier run delivered — reachable through *"implement anyway"* on an Epic that holds a record — was `missing` (`MAJOR`), sending `review-fixer` after work that existed and writing a spurious `- [ ]` note onto the spec. It now classifies against the code as it stands after the change, searching the codebase before calling anything `missing`, and treats plan tags and earlier records as claims, not evidence.
- **`test-baseliner` could record a failing suite as passing.** Nothing forbade reading a suite's status through `| tail` or `| grep`, whose exit status is the filter's — and for a status-only suite that status is the whole result. Both modes now take the status from the suite's own command.
- **`/design` still said "walk the design tree"**, a term that collides with `design.md` and a mechanic `workflows-core`'s grilling reference had replaced; it now asks from the frontier and clears the confirmation gate before writing.
```

`plugins/product-workflows/CHANGELOG.md`:
```markdown
## [3.11.3] — 2026-10-02

**Update `workflows-core` to 1.10.0 with this release**: the grilling callers below now clear that version's confirmation gate.

### Fixed
- **`/idea`, `/create-prd`, `/create-ard`, `/specify` and `/update-prd` said "walk the design tree" or "dependency order"** — the first a term that collides with `design.md`, both a mechanic `workflows-core`'s grilling reference had replaced with asking from the frontier — and *"continue to shared understanding then write"*, which left the end of the interview to the agent. Each now asks from the frontier and clears the confirmation gate before writing. `/idea` seeds its source-stated scope as settled decisions the frontier starts from.
```

`plugins/docs-workflows/CHANGELOG.md`:
```markdown
## [1.4.6] — 2026-10-02

### Fixed
- **`diff-summarizer` returned an empty diff for work that had already been merged.** It took `<branch_to>...<branch_from>`; once the branch lands by a merge commit or a fast-forward it is an ancestor of the base, the range's merge base is the branch itself, and the element came back `OK` with zero files — so `/document` and `/release-notes`, which usually run after the merge, wrote without the code. The agent now tests whether the ref has landed and reads it from the merge that landed it (`<landing>^1...<branch_from>`); a fast-forward, which leaves no fork point to read, goes to the key-commit fallback; and a range that changes no file is never reported as resolved. Prompted by upstream superpowers' review-package fix for the same class (5bf4e780).
```

- [ ] **Step 3: Run the gate chain**

```bash
cd "$AW" && python3 scripts/validate-catalog.py --selftest && python3 scripts/validate-catalog.py && ./scripts/check-id-grammar.sh --selftest && ./scripts/check-id-grammar.sh --root . && ./scripts/check-docs.sh --selftest && ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root . && npm ci --prefix scripts/mermaid --ignore-scripts --no-audit --no-fund && node scripts/mermaid/check-mermaid.mjs --selftest && node scripts/mermaid/check-mermaid.mjs --root . && python3 "$(find plugins -type f -name session-cost.py)" --selftest; echo "EXIT=$?"
```
Expected: `EXIT=0`. A failure is fixed and the chain re-run from the start.

- [ ] **Step 4: Commit**

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4 && git add .claude-plugin/marketplace.json plugins/*/.claude-plugin/plugin.json plugins/{workflows-core,dev-workflows,product-workflows,docs-workflows}/CHANGELOG.md && git commit -q -m "release: workflows-core 1.10.0, dev-workflows 4.5.0, product-workflows 3.11.3, docs-workflows 1.4.6

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" && git log --oneline -1
```

---

### Task 8: Whole-branch review of this edition, to zero findings

- [ ] **Step 1: Dispatch a fresh reviewer** (Opus) with: the spec path, `git -C "$AW" diff origin/main...HEAD`, and this brief — *"Review this branch against the spec. Prose here is executed literally by agents: report every false, ambiguous or self-contradicting sentence, every stale copy of a changed claim anywhere in `plugins/`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/` and every `CHANGELOG.md`, every place a changed agent's caller or docs page now disagrees with it, and every edit whose wrapping or idiom differs from its file. Check each changelog entry against the diff it describes. Return findings with file:line, severity, and the fix."*
- [ ] **Step 2: Triage each finding** at the location it names; fix every confirmed one, minors and nits included; record any dismissal with a reason that disposes of that finding's own claim.
- [ ] **Step 3: Re-run the Task 7 gate chain** → `EXIT=0`; commit the fix wave (`fix: review round N — …`, branch verified first).
- [ ] **Step 4: Repeat** Steps 1–3 until a review returns zero findings.

---

### Task 9: Port to the internal edition

**Files (paths relative to `$IE`):**
- Modify: `plugins/dev-workflows/agents/diff-summarizer.md` (Local-git strategies, GitHub resolver step 3, *If all four strategies fail*, `## Hard rules`)
- Modify: `plugins/dev-workflows/agents/{code-review,risk-planner,test-baseliner}.md`, `plugins/dev-workflows/commands/implement.md`
- Modify: `plugins/dev-workflows/references/grilling-technique.md`, `plugins/dev-workflows/docs/reference/references.md`
- Modify: every file `count.py` lists for "design tree" (11 hits, 9 files)
- Modify: `.claude/rules/dev-workflows-code.md:27`

**Interfaces:**
- Consumes: `$S/edits/E2a.txt`, `E2d.txt`, `E2f.txt`, `E3.txt`, `E6.txt` (Tasks 2, 3, 6); Task 4's play-back bullet text
- Produces: `$S/edits/E1-ed.txt`, `E5-ed.txt`, `E5-ed-doc.txt` — reused verbatim by Task 10

- [ ] **Step 1: Write `$S/edits/E1-ed.txt`** (the forge-aware resolver)

````text
<<<<<<< OLD 1
Used for Bitbucket Server, Bitbucket Cloud, and GitHub when `gh` is unavailable.
=======
Used for Bitbucket Server, Bitbucket Cloud, and GitHub when `gh` is unavailable.

**Every local strategy's diff is `git -C "<repo_path>" diff <base>...<head>` — three dots.** Its merge base is the fork point whichever base a strategy names, so the target branch's own changes since the fork never enter the PR's diff — as a two-dot tree diff between a merge's two parents would carry them, reversed.

**A head that has already landed has an empty merge-base range, so test for it before deriving a base.** Once Strategy 1 or 2 has chosen a head, run `git -C "<repo_path>" merge-base --is-ancestor <head> <target_branch>`. Where it exits non-zero the PR has not landed, and the strategy's own base stands. Where it exits 0, `merge-base <target_branch> <head>` returns `head` itself and the range is empty; read the merge that landed it instead:

- **Find `landing`** — the oldest commit on `<target_branch>`'s first-parent line that descends from `head`: the last commit `git -C "<repo_path>" rev-list --first-parent <head>..<target_branch>` lists that `git -C "<repo_path>" rev-list --ancestry-path <head>..<target_branch>` lists too. Take the two lists separately and intersect them: the two flags in one call follow first-parent edges only, and find nothing for a PR that reached the target through an intermediate branch's merge.
- **Read the merge.** Where `landing` exists, `git -C "<repo_path>" rev-list --parents -n 1 <landing>` names two or more parents, and `git -C "<repo_path>" merge-base --is-ancestor <head> <landing>^1` exits non-zero — `head` arrived through one of the merge's later parents — base = `<landing>^1`, and the diff is `<landing>^1...<head>` under the strategy's own `resolved_via`.
- **Otherwise there is no merge to read** — no `landing`, a `landing` with one parent (a fast-forward), or a `head` the merge's first parent already holds. Fall through to Strategy 3.

**An empty range is never a resolution.** A strategy — the `gh` resolver included — whose range changes no file (`git -C "<repo_path>" diff --quiet <range>` exits 0) has not resolved the PR, and falls through to the next.
>>>>>>> NEW
<<<<<<< OLD 1
If present, use as head; derive base via `git -C "<repo_path>" merge-base <target_branch> <head>`.
=======
If present, use as head; derive base via `git -C "<repo_path>" merge-base <target_branch> <head>` — or, where the head has already landed, from the merge that landed it (above).
>>>>>>> NEW
<<<<<<< OLD 1
If **exactly one** branch matches → use as head.
=======
If **exactly one** branch matches → use as head, with its base derived as in Strategy 1, the landed-head rule above included.
>>>>>>> NEW
<<<<<<< OLD 1
3. **Produce diff.** `git -C "<repo_path>" diff <baseRefOid>..<headRefOid>`. Set `resolved_via: gh_cli`.
=======
3. **Produce diff.** `git -C "<repo_path>" diff <baseRefOid>...<headRefOid>` — three dots, so a base that moved after the fork contributes nothing to the PR's diff. Set `resolved_via: gh_cli`. Where that range changes no file it has not resolved the PR: drop to the local-git strategies, as for a missing `gh`.
>>>>>>> NEW
<<<<<<< OLD 1
If all four strategies fail: record the PR under `unresolved_prs` and continue.
=======
If all four strategies fail — an empty range counts as a failure — record the PR under `unresolved_prs` and continue.
>>>>>>> NEW
<<<<<<< OLD 1
- NEVER fabricate diff content. If a PR cannot be resolved by any strategy, record it in `unresolved_prs`.
=======
- NEVER fabricate diff content. If a PR cannot be resolved by any strategy, record it in `unresolved_prs`.
- NEVER report an empty range as resolved. A range that changes no file has not resolved its PR, on any path; fall through to the next strategy, and to `unresolved_prs` after the last.
>>>>>>> NEW
````

- [ ] **Step 2: Write `$S/edits/E5-ed.txt`** (the play-back, beside the gate the edition already has)

````text
<<<<<<< OLD 1
Confirming a section is not confirming the whole design.
=======
Confirming a section is not confirming the whole design.
- **At the gate, play the understanding back.** In a few lines, state what is settled for the part about to be written — the intended outcome, the constraints, what success looks like — marking what the user said and what you inferred, then ask the user to confirm or correct it. An inference the user has not confirmed is still an assumption, and it is the line most worth their reading. The play-back asks no decision, so it spends no slot of a bounded caller's cap and is not numbered against it.
>>>>>>> NEW
````

and `$S/edits/E5-ed-doc.txt`:
````text
<<<<<<< OLD 1
Both end at a confirmation gate the user closes, never the agent.
=======
Both end at a confirmation gate the user closes, never the agent, where the agent plays its understanding back for correction.
>>>>>>> NEW
````

- [ ] **Step 3: Apply items 1, 2, 3, 5 and 6**

```bash
cd "$IE" && D=plugins/dev-workflows
python3 $S/wsub.py $D/agents/diff-summarizer.md $S/edits/E1-ed.txt
python3 $S/wsub.py $D/agents/code-review.md $S/edits/E2a.txt
python3 $S/wsub.py $D/commands/implement.md $S/edits/E2d.txt
python3 $S/wsub.py .claude/rules/dev-workflows-code.md $S/edits/E2f.txt
python3 $S/wsub.py $D/agents/risk-planner.md $S/edits/E3.txt
python3 $S/wsub.py $D/agents/test-baseliner.md $S/edits/E6.txt
python3 $S/wsub.py $D/references/grilling-technique.md $S/edits/E5-ed.txt
python3 $S/wsub.py $D/docs/reference/references.md $S/edits/E5-ed-doc.txt
```

- [ ] **Step 4: Item 4 — rename "design tree" to "decision tree"** in every file the count lists, `CHANGELOG.md` excluded

```bash
cd "$IE" && python3 - <<'EOF'
import re, subprocess
files = [f for f in subprocess.run(['git', 'ls-files', '-z', '--', '*.md'], capture_output=True, text=True).stdout.split('\0') if f and not f.endswith('CHANGELOG.md')]
for f in files:
    s = open(f).read()
    t = re.sub(r'(?i)(design)(\s+)(tree)', lambda m: ('Decision' if m.group(1)[0] == 'D' else 'decision') + m.group(2) + m.group(3), s)
    if t != s: open(f, 'w').write(t); print('renamed in', f)
EOF
```

- [ ] **Step 5: Verify** (Review Focus 5 included)

```bash
python3 $S/count.py "$IE" 'design tree' --ignore-case --no-changelog | tail -1           # 11 → TOTAL 0
python3 $S/count.py "$IE" 'An empty range is never a resolution' | tail -1               # TOTAL 1
python3 $S/count.py "$IE" '<baseRefOid>..<headRefOid>' | tail -1                         # TOTAL 0
python3 $S/count.py "$IE" 'against the diff and classify it' | tail -1                   # TOTAL 0
python3 $S/count.py "$IE" 'without *how*' | tail -1                                      # TOTAL 0
python3 $S/count.py "$IE" 'never from a pipe after it' | tail -1                         # TOTAL 2
python3 $S/count.py "$IE" 'play the understanding back' | tail -1                        # TOTAL 1
python3 $S/count.py "$IE" 'against the shipped diff' | tail -1                           # TOTAL 0
```
Read the agent's resolver end to end: a merged PR whose `gh` range is empty now drops to the local strategies (GitHub resolver step 3), and Strategy 1/2 test for a landed head before using the merge base. The handoff file (`references/handoff/diff-summarizer.md`) states no strategy's range — confirm with `grep -n -E '\.\.\.?<|merge-base' plugins/dev-workflows/references/handoff/diff-summarizer.md` returning nothing — so it needs no edit.

- [ ] **Step 6: Sweep the remaining copies** — `grep -rn -i -E "strategy [123]|merge-base" plugins/dev-workflows/docs .claude/rules CLAUDE.md README.md`; any statement of a strategy's range is made to agree.

- [ ] **Step 7: Release** — `plugins/dev-workflows/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` 2.65.4→2.66.0; a `## [2.66.0] — 2026-10-02` section in `plugins/dev-workflows/CHANGELOG.md` carrying the dev-workflows 4.5.0 entries from Task 7 (with `/implement`, `/design` and the VI commands' names as this edition spells them), plus:

```markdown
- **`diff-summarizer` returned an empty diff for a merged PR on its local strategies.** Strategies 1 and 2 derived the base as `merge-base <target_branch> <head>`, which is `head` itself once the PR has merged — and the default filter takes merged PRs only. Both now test for a landed head and read the merge that landed it; a fast-forward falls through to Strategy 3; a range that changes no file, on any path, `gh` included, is never a resolution. Prompted by upstream superpowers' review-package fix for the same class (5bf4e780).
- **No local strategy stated its diff, and the `gh` path's was two-dot.** Strategy 3's *base = `<commit>^1`, head = `<commit>^2`*, read beside the `gh` path's explicit `<base>..<head>`, reads as a two-dot tree diff, which carries the target's own changes since the fork, reversed, as if the PR had made them. Every path now takes `<base>...<head>`.
- **The play-back** (as `workflows-core` 1.10.0 above, beside the confirmation gate this edition already had).
- **"design tree" is "decision tree" everywhere** — the reference had contradicted itself, *"Walk the decision tree"* in Mechanics against *"Map the design tree"* in Rhythm.
```

- [ ] **Step 8: Gates**

```bash
cd "$IE" && python3 scripts/validate-catalog.py --selftest && python3 scripts/validate-catalog.py && ./scripts/check-id-grammar.sh --selftest && ./scripts/check-id-grammar.sh --root . && ./scripts/check-docs.sh --selftest && ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root . && npm ci --prefix scripts/mermaid --ignore-scripts --no-audit --no-fund && node scripts/mermaid/check-mermaid.mjs --selftest && node scripts/mermaid/check-mermaid.mjs --root . && python3 plugins/dev-workflows/scripts/session-cost.py --selftest; echo "EXIT=$?"
```
Expected: `EXIT=0`.

- [ ] **Step 9: Commit, then review to zero** — commit on `iv-gu/harvest-r4` (branch verified), then Task 8's loop against this edition (`git -C "$IE" diff main...HEAD`), plus a parity read: each changed passage against this repository's, dialect differences aside.

---

### Task 10: Port to the Copilot edition

**Files (paths relative to `$CE`):** `dev-workflows/agents/{diff-summarizer,code-review,risk-planner,test-baseliner}.md`, `dev-workflows/skills/implement/SKILL.md`, `dev-workflows/skills/_shared/grilling-technique.md`, `dev-workflows/docs/reference/references.md`, every file the "design tree" count lists (11 hits, 9 files), `.github/instructions/dev-workflows-shared.instructions.md:25`, `dev-workflows/.plugin/plugin.json`, `.github/plugin/marketplace.json`, `dev-workflows/CHANGELOG.md`

**Interfaces:**
- Consumes: `$S/edits/E1-ed.txt`, `E2a.txt`, `E2d.txt`, `E2f.txt`, `E3.txt`, `E5-ed.txt`, `E5-ed-doc.txt`, `E6.txt` — none names a command or a path, so each applies unchanged

- [ ] **Step 1: Apply**

```bash
cd "$CE" && D=dev-workflows
python3 $S/wsub.py $D/agents/diff-summarizer.md $S/edits/E1-ed.txt
python3 $S/wsub.py $D/agents/code-review.md $S/edits/E2a.txt
python3 $S/wsub.py $D/skills/implement/SKILL.md $S/edits/E2d.txt
python3 $S/wsub.py .github/instructions/dev-workflows-shared.instructions.md $S/edits/E2f.txt
python3 $S/wsub.py $D/agents/risk-planner.md $S/edits/E3.txt
python3 $S/wsub.py $D/agents/test-baseliner.md $S/edits/E6.txt
python3 $S/wsub.py $D/skills/_shared/grilling-technique.md $S/edits/E5-ed.txt
python3 $S/wsub.py $D/docs/reference/references.md $S/edits/E5-ed-doc.txt
```

- [ ] **Step 2: Item 4** — the Task 9 Step 4 rename script, run with `cd "$CE"`.

- [ ] **Step 3: Verify** — Task 9 Step 5's eight counts with `$CE` (same expected totals: 0, 1, 0, 0, 0, 2, 1, 0), then the instruction files' size:

```bash
for f in "$CE"/.github/instructions/*.md; do python3 -c 'import sys;n=len(open(sys.argv[1]).read());print(n, sys.argv[1]);sys.exit(n>=20000)' "$f" || echo OVER; done
```
Expected: both under 20,000 (`dev-workflows-shared` unchanged at 19,961 — the edit is length-neutral). Then `grep -rn 'CLAUDE_PLUGIN_ROOT\|/implement\b' "$CE"/dev-workflows/agents/diff-summarizer.md` returns no line the edit added.

- [ ] **Step 4: Release** — `dev-workflows/.plugin/plugin.json` and `.github/plugin/marketplace.json` 2.34.4→2.35.0; a `## [2.35.0] — 2026-10-02` section in `dev-workflows/CHANGELOG.md` with Task 9 Step 7's entries in this edition's dialect (`implement:`, `design:`).

- [ ] **Step 5: Gates** — the Task 9 Step 8 chain from `cd "$CE"` minus the `session-cost.py` step (this edition ships none) → `EXIT=0`.

- [ ] **Step 6: Commit, then review to zero** — as Task 9 Step 9, against `git -C "$CE" diff main...HEAD`.

---

### Task 11: Harvest record, merge, push, clean up

- [ ] **Step 1: Merge and push the two other editions**

```bash
for r in "$IE" "$CE"; do
  test "$(git -C "$r" branch --show-current)" = iv-gu/harvest-r4 || { echo "wrong branch in $r"; break; }
  git -C "$r" switch main && git -C "$r" merge --no-ff iv-gu/harvest-r4 -m "Merge iv-gu/harvest-r4: upstream harvest round 4, Round 1 — six defects in shipped text" && git -C "$r" log --oneline -1
done
git -C "$IE" push origin main
for rem in $(git -C "$CE" remote); do git -C "$CE" push "$rem" main; done
for r in "$IE" "$CE"; do git -C "$r" branch -d iv-gu/harvest-r4; done
```
The internal edition's push prints a branch-protection bypass notice; confirm with `git -C "$IE" rev-parse main origin/main` (equal). For the Copilot edition, `git -C "$CE" rev-parse main` equals every `<remote>/main`.

- [ ] **Step 2: Write the harvest record** — append to `$AW/docs/superpowers/harvest/NEXT.md` after the last `## …` entry (never naming the internal edition):

```markdown
## Harvest round 4 — surveyed 2026-10-02; Round 1 SHIPPED (2026-10-02)
Survey of the four upstreams against the round-2 baseline: superpowers `b36e0829`..`8ca22dba` (v6.3.0 → v6.4.2), mattpocock/skills `5b15a47`..`d81f3a1` (v1.3, unreleased changesets), BMAD-METHOD `67d876f1`..`4f61d4e7` (v6.12.0 + Unreleased), spec-kit `27f50f7e`..`4a339209` (1.0.1 → 1.0.13). 21 portable items; the six that were **defects in text all three editions shipped** went first, as Round 1. Spec + plan: `docs/superpowers/specs/2026-10-02-harvest-round-4-defects-design.md` and `docs/superpowers/plans/2026-10-02-harvest-round-4-defects.md`.

**Round 1 — what shipped** (this repository: `workflows-core` 1.10.0, `dev-workflows` 4.5.0, `product-workflows` 3.11.3, `docs-workflows` 1.4.6; the internal edition `dev-workflows` 2.66.0, merge `<the sha Step 1 printed for $IE>`; the Copilot edition 2.35.0, merge `<the sha Step 1 printed for $CE>`):
1. `diff-summarizer` read a landed ref as an empty range and reported it resolved (superpowers 5bf4e780). Two findings while planning: `git rev-list --first-parent --ancestry-path` follows first-parent edges only (git 2.43), so `landing` intersects two lists; and the other two editions' local strategies and `gh` path were effectively two-dot, carrying the target's own changes since the fork, reversed — now three-dot on every path.
2. `code-review` dimension 10 judged the diff alone — a requirement an earlier run delivered came back `missing` (MAJOR); it now judges the code, treats plan tags as claims, and reports `exceeds` (spec-kit #4621).
3. `risk-planner` carried the "what without how" rule upstream writing-plans withdrew (#2333); now "Unambiguous, not complete", with spec-pinned values quoted verbatim (spec-kit #4430).
4. "design tree" survived the July rename in every caller; this repository now asks from the frontier, the other two say "decision tree" everywhere.
5. This repository's grill had no confirmation gate; it now has one, and all three play the understanding back at the gate (mattpocock grilling; superpowers #2258).
6. `test-baseliner` could read a filter's exit status through a pipe and record a failing status-only suite as passing (spec-kit #4604).

**Backlog — surveyed, not yet built** (items 7–21; each applies to all three editions unless noted):
7. Triage: "couldn't verify" is not "refuted" — defer a serious-if-true unsubstantiated finding with what would settle it; defer fixes to agent-instruction files; row count equals findings (BMAD 3433612d, b0d27c3c). M.
8. Re-review keeps prior triage dispositions; the second review is triaged (BMAD 7c3e5827, 85d968fc). M.
9. Effect-based severity where the spec is silent, and a reviewer's declined-to-judge list (superpowers 5bf4e780 #2319). S–M.
10. A plan "Review focus" section — implied inputs no test exercises — tested by `test-writer`, checked by `code-review` (superpowers 5bf4e780 #2319). M.
11. `code-review` edge-case checks: handle lifetime, call vs declaration (BMAD 44e0f806), implicit enum branch at code altitude, removed code whose contract nothing replaced. S.
12. `code-review` finds the repo's documented standards — CLAUDE.md, AGENTS.md, copilot-instructions, CONTRIBUTING, CODING_STANDARDS (BMAD 23f134e2; mattpocock code-review step 3). S.
13. `/implement` looks before asking, and can re-classify upward after exploring (BMAD 7e571784, 124ea1af, 2c10d5ba). M.
14. Design contracts: owning side, behavioural obligations, provider-side conformance (spec-kit aaa8fa92). S.
15. PR body: merge danger (one-way/two-way door, blast radius), before/after evidence, honour a repo's PR template (mattpocock `pr`). M.
16. `bug-diagnosis.md` drift: performance branch, one-variable probes, minimise the repro, no-loop fallback, name the confirmed hypothesis (mattpocock diagnosing-bugs). S–M.
17. `impl-maintenance`: sort each miss into "build a check" or "write a standard"; flag no-op instructions (mattpocock `retro`). S–M.
18. `/epics` dependency checks: needs and owners, collisions, one home per shared decision, touched-unit coverage (BMAD f033e70a, ba252f1b). S–M.
19. Acceptance-criteria wording tests: false before, true after; the rule, not an example; 3–8 (BMAD bmad-ticket). S; `specification-format.md` stays frozen.
20. Redact secrets, emails, hosts and home paths before `/prompt` and feedback capture write user text (superpowers diagnosing-superpowers redaction policy). S.
21. Low or deferred: a glossary input for `interface-designer` (mattpocock DESIGN-IT-TWICE); a transcript-based session-diagnosis command (superpowers diagnosing-superpowers) — L.

**Rejected again** (reasons unchanged): superpowers' native executing-plans / SDD ledger, verify-a-fix-by-test instead of re-review, nested mid-tier orchestrator; mattpocock `implement-spec`, `retro` as its own command, `pr`'s picture menu and Mermaid; BMAD's user-pinned review depth (bypasses the classification gate), finding floors scaled by diff size, the ticket store and walkthrough; spec-kit's extension and catalog machinery, `taskstoissues` (a tracker), the constitution sync report.

**Recorded divergences** — decisions, not gaps:
- **Grilling rhythm.** The internal and Copilot editions ask relentless callers' questions in rounds; this repository stays one question at a time, because `/brd-split`'s ledger walk forbids batching.
- **"design tree" vs "decision tree".** mattpocock renamed it "decision tree" (`3bb587f`) and then back (`a4b2009`); we keep "decision tree" for our own reason — "design tree" collides with `design.md`.
```

Fill the two merge shas from Step 1's output before committing — they are values Step 1 printed, not placeholders.

- [ ] **Step 3: Commit the record, re-run this edition's gates** (Task 7 Step 3 → `EXIT=0`), then merge this edition from the main tree, which stands on `main`:

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/harvest-r4 && git add docs/superpowers/harvest/NEXT.md && git commit -q -m "docs(harvest): record round 4 — Round 1 shipped, backlog 7–21

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
test "$(git -C /workspace/ai-workflows branch --show-current)" = main && test -z "$(git -C /workspace/ai-workflows status --porcelain)" && git -C /workspace/ai-workflows fetch -q origin && git -C /workspace/ai-workflows merge -q --ff-only origin/main && git -C /workspace/ai-workflows merge --no-ff iv-gu/harvest-r4 -m "Merge iv-gu/harvest-r4: upstream harvest round 4, Round 1 — six defects in shipped text (workflows-core 1.10.0, dev-workflows 4.5.0, product-workflows 3.11.3, docs-workflows 1.4.6)" && git -C /workspace/ai-workflows push origin main
```

- [ ] **Step 4: Clean up** — `git -C /workspace/ai-workflows worktree remove "$AW" && git -C /workspace/ai-workflows branch -d iv-gu/harvest-r4`; confirm each repository: on `main`, clean, `main` equal to every remote's `main`, no `iv-gu/harvest-r4` branch locally or on a remote, one worktree.

- [ ] **Step 5: Installed copies** (the operator's step) — `claude plugin update workflows-core@shipwright`, `dev-workflows@shipwright`, `product-workflows@shipwright`, `docs-workflows@shipwright`, then restart; `copilot plugin update dev-workflows@ihudak-copilot-plugins`; the internal edition wherever it is installed.

# Blind, batched grounding verification — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `/prd-ground` Phase 7's verification blind by construction and batched, so a finding's answer never reaches the agent re-deriving it, and dispatches scale with batches instead of findings (#73, #74).

**Architecture:** `grounding-verifier` gains two modes. Phase 7 cuts its unchanged verification set into batches per repository (`[CG#n]`) or frame set (`[DG#n]`), dispatches `mode: derive` with each finding's premise and source only, then `mode: compare` with the originals beside the blind result; compare returns today's per-finding fields, so every rule after the dispatch is untouched. An incomplete result is retried once; Phase 1 states the cost before repositories are chosen.

**Tech Stack:** Markdown prose executed literally by agents (commands, agents, references); repository gates in `scripts/` (Python, Bash, Node); `gh`; `claude -p --plugin-dir` for the live smoke run.

**Spec:** `docs/superpowers/specs/2026-10-01-verifier-blind-batched-design.md` — read it before Task 1.

## Global Constraints

- Every finding gets its own full, independent re-derivation on the Opus chain; nothing lowers a tier, samples, or lets one finding stand in for another (spec D1).
- A re-run re-verifies every finding on file, as today (spec D2).
- Batch cap: **25** findings, stated once, in Phase 7.
- Batch composition never depends on a finding's `verdict`, `evidence`, `control` or `cites`.
- The derive dispatch never carries `verdict`, `evidence`, `control` or `cites`, and no path under `$SPECS_PATH` other than `frame_set_dir`.
- Compare returns today's per-finding fields unchanged: `status`, `finding_id`, `outcome`, `own_verdict`, `own_evidence`, `own_control`, `control_outcome`, `commit`, `notes`.
- No agent continuation (no follow-up messages to a running agent).
- Command, agent and reference prose is executed literally: a false sentence is a defect. Never hard-wrap a paragraph you write (`workflows-core:prose-formatting`); match each file's existing wrapping where you edit inside a wrapped paragraph.
- Requirement ids in the bracketed form only (`[CG#n]`, `[BR#n]`) — `scripts/check-id-grammar.sh`.
- Read a file with the **Read tool** before editing it, so `.claude/rules/` files load (`CLAUDE.md` § Where the rest of the guidance lives).
- Every anchor phrase this plan quotes ("replace the paragraph that begins …") occurs exactly once, matched wrap-insensitively — verified when the plan was written. Several wrap across a line break in the source, so an Edit with the phrase as quoted will not match: run `python3 "$SCRATCH/count.py" "<phrase>"` (Task 0), open the `file:line` it prints, and copy the exact source text, line breaks included, into the Edit.
- `git branch --show-current` immediately before every commit; never `git checkout` in `/workspace/ai-workflows`; never bare `git stash`.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.
- Nothing is pushed until Task 9's review and fix wave are done and the user approves.

## Review Focus

1. **A return matched by position.** An agent may reorder or drop findings in a batch return. Phase 7 must match every returned entry to its finding by `finding_id`, never by position, and treat an unmatched finding as missing (Task 4, step 3 pins it).
2. **A compare return that rewrote the blind result.** If compare echoes an `own_verdict`/`own_evidence`/`own_control` that differs from the derive return, compare broke its never-revise rule. Phase 7 must read `own_*` from the derive return and treat a differing echo as an incomplete compare (Task 4, step 3).
3. **A class-4 `[DG#n]` batch spanning two repositories.** A frame-set batch can hold class-4 findings pinned to different repositories; each pair is integrity-checked, and a `COMMIT_MISMATCH` on any pair refuses the whole batch with the pair named (Task 3, Process step 1).
4. **The 25 cap at its boundary.** A repository's baseline `[CG#n]` counts toward its first batch; 25 findings are one batch and 26 are two (Task 4, step 3 states it; Task 8 checks the arithmetic in the cost line).
5. **`--no-code`.** Only `[DG#n]` are verified; a class-4 finding's repository pair comes from the on-file `[CG#n]` it cites, and no `[CG#n]` batch exists (Task 4, step 4).

---

### Task 0: Preconditions and baseline counts

**Files:** none modified.

- [ ] **Step 1: Confirm #70 has merged, then rebase.** The #70 fix (`iv-gu/specs-path-depth`) bumps product-workflows and workflows-core; this branch must sit on top of it.

```bash
cd /workspace/ai-workflows/.claude/worktrees/verifier-blind
git fetch -q origin
git log --oneline origin/main | grep -m1 -i 'specs-path-depth\|#70' || echo "STOP: #70 not on main yet"
git branch --show-current   # expect iv-gu/verifier-blind
git rebase origin/main
grep -h '"version"' plugins/product-workflows/.claude-plugin/plugin.json plugins/workflows-core/.claude-plugin/plugin.json
```

Expected: the #70 merge is found; rebase succeeds (only the spec and plan commits replay); versions read product-workflows `3.10.x`, workflows-core `1.8.x`. Record both — Task 8 bumps from them. If #70 is not on main, stop and tell the user.

- [ ] **Step 2: Save the counting script** to the session scratchpad (not the repo):

```bash
SCRATCH=/tmp/claude-502/-workspace-ai-workflows/d7e59186-271d-4a83-a94b-9e776fafee25/scratchpad
cat > "$SCRATCH/count.py" <<'EOF'
#!/usr/bin/env python3
"""Wrap-insensitive phrase count over CLAUDE.md refinement 4's scope.
Usage: count.py "<phrase>" ["<phrase>" ...]   (run from the repo root)"""
import pathlib, re, sys
roots = [pathlib.Path(p) for p in ("plugins", ".claude/rules", "docs/maintainers")]
files = [p for r in roots for p in r.rglob("*.md")] + [pathlib.Path(p) for p in ("README.md", "CLAUDE.md")]
def line_of(raw, flat_offset):
    """Map an offset in the whitespace-collapsed text back to a 1-based source line."""
    pos, line, prev_space = 0, 1, False
    for ch in raw:
        if pos >= flat_offset:
            return line
        if ch.isspace():
            if not prev_space:
                pos += 1
            prev_space = True
        else:
            pos += 1
            prev_space = False
        if ch == "\n":
            line += 1
    return line

for phrase in sys.argv[1:]:
    needle = re.sub(r"\s+", " ", phrase.strip())
    total = 0
    for f in sorted(set(files)):
        if not f.exists():
            continue
        raw = f.read_text(encoding="utf-8")
        flat = re.sub(r"\s+", " ", raw)
        for m in re.finditer(re.escape(needle), flat):
            print(f"  {f}:{line_of(raw, m.start())}")
            total += 1
    print(f"{total}\t{phrase}")
EOF
chmod +x "$SCRATCH/count.py"
```

Each hit prints as `file:line`; the totals are what Step 3 records.

- [ ] **Step 3: Record the before-counts** of every string this plan changes or retires:

```bash
python3 "$SCRATCH/count.py" \
  "One instance per finding" \
  "one per finding" \
  "one \`grounding-verifier\` dispatch per finding" \
  "exactly as the agent's own Inputs contract declares it" \
  "discard your search and restart it" \
  "DO NOT READ before Process step 2" \
  "Process step 2" \
  "provenance: own-run | inherited" \
  "§5 of its own instructions" \
  "without first reading \`evidence\`" | tee "$SCRATCH/counts-before.txt"
```

Expected: a non-zero total for most lines; keep the file. Task 7 re-runs the same command.

---

### Task 1: `grounding-format` §8 states the structural rule

**Files:**
- Modify: `plugins/workflows-core/references/grounding-format.md` (§8, from the line `**The verifier does not check citations.**`; §4.1's "Verification is unchanged" paragraph)

**Interfaces:**
- Produces: the authority sentence Tasks 3 and 4 cite — *"the step that re-derives is handed the premise and the source, and nothing of the finding's answer"*.

- [ ] **Step 1: Read** `plugins/workflows-core/references/grounding-format.md` with the Read tool (lines 380–420 and 781–882).

- [ ] **Step 2: Insert** a new paragraph immediately after the paragraph that begins `**The verifier does not check citations.**` and ends `returns one of four outcomes, each with its own evidence.`:

```markdown
**Independence is structural, not a discipline the verifier keeps.** The step that re-derives is handed the requirement premise and the source the finding rests on, and nothing of the finding's answer — not its `verdict`, its `evidence`, its `control`, or a class-4 `[DG#n]`'s `cites`. An agent cannot un-read text in its own context, so a re-derivation whose input carried the answer is anchored to it however carefully it was told not to look. Verification is therefore two steps, each its own dispatch: a blind re-derivation, which refuses an input carrying any of those fields, then a comparison, which is handed the original beside the blind result, runs the original's control, and decides the outcome without revising the blind result. `product-workflows:prd-ground`'s *Verify* phase dispatches both; `product-workflows:grounding-verifier` owns each step's inputs.
```

- [ ] **Step 3: Re-read §4.1's paragraph** beginning `**Verification is unchanged and is not an exception.**`. Replace its second sentence (`` `grounding-verifier` re-derives a baseline finding by re-running `baseline-integrity` against the commit it was handed, which its own Process step 1 already does for every finding that rests on code — so the re-derivation *is* that re-run, and the outcome it returns is a real outcome, not a courtesy. ``) with:

```markdown
`grounding-verifier` re-derives a baseline finding by re-running `baseline-integrity` against the commit it was handed, which its blind step does first for every batch that rests on code — so the re-derivation *is* that re-run, and the outcome its comparison returns is a real outcome, not a courtesy.
```

Leave the rest of that paragraph as it stands.

- [ ] **Step 4: Verify.**

```bash
grep -c 'Independence is structural, not a discipline' plugins/workflows-core/references/grounding-format.md   # expect 1
grep -c 'its own Process step 1 already does' plugins/workflows-core/references/grounding-format.md          # expect 0
./scripts/check-id-grammar.sh --root . ; echo "EXIT=$?"                                                       # expect EXIT=0
```

- [ ] **Step 5: Commit.**

```bash
git branch --show-current   # expect iv-gu/verifier-blind
git add plugins/workflows-core/references/grounding-format.md
git commit -m "grounding-format §8: verification is a blind re-derivation, then a comparison (#73)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: (folded into Task 4, step 1)

---

### Task 3: `grounding-verifier` — two modes

**Files:**
- Modify (full rewrite): `plugins/product-workflows/agents/grounding-verifier.md`

**Interfaces:**
- Consumes: Task 1's §8 paragraph (cited as `workflows-core:grounding-format` §8).
- Produces, for Task 4:
  - inputs `mode: derive | compare`; batch anchors `repo_path`, `frame_set_dir`, `inventory`; `findings[]`.
  - derive finding fields `id`, `claim`, `class`, `commit`, `repo_path` (class-4 only); compare adds `verdict`, `evidence`, `control`, `cites`, `cited`, `derived`.
  - derive return: batch `status` (`OK | INPUT_MISSING | INPUT_UNBLIND | REPO_MISSING | FRAME_SET_MISSING | NO_INDEX | STALE_INDEX | COMMIT_MISMATCH`), `commits[]`, `findings[]` of `{finding_id, status: OK | INPUT_MISSING, own_verdict, own_evidence, own_control, notes}`.
  - compare return: batch `status` (the derive set less `INPUT_UNBLIND`), `findings[]` of `{finding_id, status: OK | INPUT_MISSING | INCOMPLETE, outcome, own_verdict, own_evidence, own_control, control_outcome, commit, notes}`.

- [ ] **Step 1: Read** the current file with the Read tool.

- [ ] **Step 2: Replace the whole file** with the content below.

````markdown
---
name: grounding-verifier
description: Independently re-derives grounding findings in batches — [CG#n] from one pinned repository, [DG#n] from one exported frame set — in two dispatches its caller makes in order. In derive mode it is handed each finding's requirement premise and source and never the finding's answer, and refuses a dispatch that carries one; in compare mode it runs each original's positive control and returns agree / extend / contradict / unprovable against its own blind result, which it never revises. It does NOT check citations. A finding is not evidence until this agent has re-derived it. Read-only. Uses Claude Opus.
model: opus
tools: ["Read", "Glob", "Grep", "Bash", "Skill"]
---

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

**Two modes, one dispatch each, in this order.** Your caller dispatches you twice per batch. In `mode: derive` you re-derive every finding in the batch from its requirement premise and its source, and you are never handed the finding's answer — its `verdict`, `evidence`, `control` or, for a class-4 `[DG#n]`, `cites`. In `mode: compare` you are handed the originals beside your derive result and you settle the outcome. The split is the point. An agent that reads the citation first is checking a citation, and checking a citation only proves the cited line — or the cited `[CG#n]` — exists; it proves nothing about whether the claim is true. An agent cannot un-read text in its own context, so the derive step is blind because the answer was never sent, not because you were asked not to look (`workflows-core:grounding-format` §8).

Invoke `Skill(skill: "workflows-core:reference", args: "grounding-format")` and read it for the `[CG#n]`/`[DG#n]` finding record, the six verdicts, the horizons, and — in §8 — the four verification outcomes this agent returns. Follow that reference; do not restate it here. Invoke `Skill(skill: "workflows-core:reference", args: "read-only-repos")` and read it for the read-only posture toward a mounted repository when re-derivation requires reading one.

Independently re-derive a batch of `[CG#n]` or `[DG#n]` findings and, in compare mode, return an outcome for each from the closed set in `workflows-core:grounding-format` §8. The caller — `/prd-ground` Phase 7 — dispatches this agent as the gate every finding passes through before it is treated as evidence; on a different agent from whichever wrote the finding, per §8.

**Distinction from `code-grounder` and `design-grounder`.** Those agents produce a finding. This agent never produces a finding — it produces a verdict *on* a finding, arrived at by working the claim from scratch. It holds `Bash` for the same reason `code-grounder` does: to run `baseline-integrity` and re-pin the commit before re-deriving anything against it, never to check out or move the repository.

## Inputs

### Every dispatch

```yaml
mode:          derive | compare
repo_path:     <absolute path — every [CG#n] batch, the repository all of its findings are pinned
                against; omitted on a [DG#n] batch, where each class-4 finding carries its own>
frame_set_dir: <absolute path to the exported frame set — every [DG#n] batch; omitted on a [CG#n] batch>
inventory:     <every requirement row the caller claims, id and text — a BR#n on the BRD route, an
                AC#n/FR#n/US#n on the idea route — every [DG#n] batch. This is the same list
                design-grounder was handed; a [DG#n] is a reconciliation between the frame set and
                this inventory, and cannot be re-derived against only one side of it>
findings:      <the batch, in the shape the mode below gives>
```

### `mode: derive` — each entry of `findings`

```yaml
- id:        <CG#n> | <DG#n>
  claim:     <the requirement premise under test, id and text as the original finding recorded them>
  class:     <1-4, DG#n only — read up front, it names which reconciliation question to re-derive>
  commit:    <the commit the finding is pinned to — every CG#n and every class-4 DG#n>
  repo_path: <class-4 DG#n only — the repository the CG#n it cites is pinned against>
```

**Never present in a derive dispatch: `verdict`, `evidence`, `control`, `cites`, `cited`, `derived`.** If any entry carries one, return `status: INPUT_UNBLIND` for the batch, naming the field and the finding, and re-derive nothing. Do not "mitigate" a contaminated input by searching carefully anyway: the answer is already in your context, and a re-derivation that saw it is not independent.

### `mode: compare` — each entry of `findings`

```yaml
- id, claim, class, commit, repo_path:   <exactly as the derive dispatch gave them>
  verdict:  <the original finding's verdict>
  evidence: <the original finding's evidence>
  control:  <the original finding's positive control, where it carries one — absent on a finding that
             owes none; the closed-set rule in workflows-core:grounding-format §2.2 decides which, and
             this agent applies that rule itself rather than inferring owed-ness from the field being
             missing>
  cites:    <class-4 DG#n only — the CG#n it cites>
  cited:    <class-4 DG#n only — that CG#n's record as the caller holds it: verdict, evidence, control>
  derived:  <this finding's entry from your derive return, verbatim — own_verdict, own_evidence,
             own_control where returned, notes>
```

`claim` and `inventory` both carry an id already paired with its text by the caller — a `[BR#n]` on the BRD route, an `[AC#n]`/`[FR#n]`/`[US#n]` on the idea route. Resolve an id against the list you were handed; never parse one out of the text.

### Which inputs are required, and why it depends on the finding

A `[CG#n]` and a class-4 `[DG#n]` rest on code, and cannot be re-derived without a repository pinned to a commit. A `[DG#n]` of class 1, 2, or 3 rests on the design alone (`workflows-core:grounding-format` §6: those three are "settled entirely … from the frame set and the requirement text"), so there is no repository to pin and no commit to demand — demanding one would make every design-only finding permanently unverifiable, and a finding that can never carry an outcome can never become evidence (§8).

The row is chosen **per finding**, in both modes. On a `[CG#n]` batch `repo_path` is the batch's; on a class-4 `[DG#n]` it is the finding's own.

| Finding | Rests on | Required beyond `id` and `claim` |
|---|---|---|
| any `[CG#n]` | code | `repo_path` **and** `commit` |
| `[DG#n]`, `class: 4` | design **and** code | `frame_set_dir`, `inventory`, `repo_path`, **and** `commit` |
| `[DG#n]`, `class: 1`, `2`, or `3` | design only | `frame_set_dir` **and** `inventory` |

**`inventory` is required for every `[DG#n]`, and a class-1 finding is why.** A class-1 finding asserts *"this frame shows a field no requirement asks for"* — a **negative over the whole requirement set** — and `design-grounder` writes its `claim` as `none — frame-only: <field>`, naming the field and no requirement, because there is no requirement id to name. Handed the frames and that claim and nothing else, this agent cannot re-derive the assertion at all: it can see the field on the frame and has no set to establish the absence against. It correctly returns `NOT-PROVABLE` and says why, which is the contract working — but the finding is then permanently unverifiable, and a finding that can never carry an outcome can never become evidence (`workflows-core:grounding-format` §8). The dispatch was short an input, not the agent short a capability. It is required on classes 2, 3 and 4 as well rather than on class 1 alone: `design-grounder` already refuses to produce **any** `[DG#n]` without it, so a caller holding one necessarily holds the inventory, and a per-class conditional here is one more thing to get wrong in the direction this table exists to prevent. Where it is given on a `[CG#n]` batch it is honoured, never ignored.

**Refuse a finding whose row is short an input**, returning that finding's `status: INPUT_MISSING` naming exactly what was absent and which row was applied, and carry on with the rest of the batch. A batch anchor missing for the whole batch — `repo_path` on a `[CG#n]` batch, `frame_set_dir` or `inventory` on a `[DG#n]` batch — refuses the batch: `status: INPUT_MISSING` at batch level. `id` and `claim` are required on every finding, without exception.

**The row is chosen fail-closed, and that is what keeps a code finding from slipping through without a commit.** A finding takes the design-only row **only** when it is positively established to belong there: its `id` carries the `DG#` prefix **and** its `class` is present and reads exactly `1`, `2`, or `3`. Everything else takes a code row — every `[CG#n]`, every class-4 `[DG#n]`, and every `[DG#n]` whose `class` is absent, empty, unparseable, or outside `1`–`4`. So no field a caller can leave out ever moves a finding *out* of the code row: omitting `class` lands it in the strictest row, never the laxest, and the only way to reach the design-only row is to assert a design-only class explicitly. A caller that forgets `commit` on a `[CG#n]`, or on a `[DG#n]` whose class it failed to pass, is refused — never quietly verified against nothing.

**When a repository pair is supplied on a design-only finding**, use it: run Process step 1 against it as for any code finding, and refuse with `COMMIT_MISMATCH` if it does not check out. An input that is not required is still honoured when given; it is never silently ignored.

## Process

**Every command names the source it reads.** Your Bash tool starts every call in the session's directory — where `/prd-ground` stands, which need not be `repo_path` — and a `cd` does not persist between calls, so a bare `git` reads the session's repository, not the one the finding is pinned to. Write every command against the repository as `git -C "<repo_path>" …`, with an absolute path, or as a subshell `(builtin cd "<repo_path>" >/dev/null && …)` inside one Bash call — `builtin cd`, its output discarded, since your Bash tool's shell carries the user's shell functions and aliases, and a `cd` of theirs would otherwise run in its place and could print into what you read; give every `Grep` and `Glob` call `repo_path` or `frame_set_dir` as its `path`, since without one they search the session's directory too; and `Read` absolute paths.

**Under `$SPECS_PATH`, read nothing outside `frame_set_dir`, in either mode.** Frame sets live in a folder's `design/` directory, so `frame_set_dir` is itself under `$SPECS_PATH`; its sibling `grounding/`, where every finding on file lives, is never opened. In derive mode that file holds the answers you must not see; in compare mode the caller has already handed you everything the comparison needs.

1. **Establish the source, once per batch, before anything else** — in both modes, since the repository may move between your two dispatches.

   - **Each repository pair in the batch** — the batch's `repo_path` with its findings' `commit`, and every distinct `repo_path`/`commit` a class-4 `[DG#n]` carries, plus any pair given on a design-only finding: verify `repo_path` exists — batch `status: REPO_MISSING` if it does not — and re-run `baseline-integrity` (`workflows-core:grounding-format` §4) against the commit: `git -C "<repo_path>" rev-parse HEAD`, `git -C "<repo_path>" diff --ignore-cr-at-eol --stat`, `git -C "<repo_path>" status --porcelain`. On any mismatch, return batch `status: COMMIT_MISMATCH` naming the repository, the pinned commit and the resolved `HEAD`. A re-derivation against an unverified tree settles nothing. A `[CG#n]` batch whose findings name more than one `commit` is malformed: batch `status: INPUT_MISSING`, naming the commits.
   - **`frame_set_dir`** (every `[DG#n]` batch): verify it exists — batch `status: FRAME_SET_MISSING` if it does not — and that it holds an index file, the same requirement `design-grounder` refuses without. Without one there is no reliable mapping from a frame's filename to what it depicts, and a re-derivation over guessed frame identity is not a re-derivation; return batch `status: NO_INDEX` naming the directory searched. An index none of whose rows names a frame still in the directory is batch `status: STALE_INDEX`.

### `mode: derive`

2. **Refuse an input that carries the answer.** Before reading any finding's `claim`, check every entry for `verdict`, `evidence`, `control`, `cites`, `cited` or `derived`. Any present → batch `status: INPUT_UNBLIND`, naming the field and the finding; re-derive nothing.

3. **Re-derive each finding independently.** Start from its `claim` — the requirement premise — the same way `code-grounder` or `design-grounder` would starting cold: derive your own search terms, read the matching files or frames fully, and reach your own verdict from the closed set in `workflows-core:grounding-format` §3 — from the repository for a `[CG#n]`, and from `frame_set_dir`'s indexed frames and the requirement text for a `[DG#n]`, re-running that finding's own reconciliation question per §6. For a class-4 `[DG#n]`, "independently" covers both halves of the claim: whether the frame implies the capture (design-side, from the frame set) *and* whether the pinned code can perform it (code-side, from the repository) — re-derive the code question yourself; the `[CG#n]` it cites is not in your input and is not to be looked up.

   **Each finding stands on its own premise.** A fact you established for one finding in this batch — "this repository holds no persistence layer", say — may be cited for another only after you have checked that it bears on that finding's premise, and each finding's `own_evidence` must carry everything its verdict rests on: a reader of that one finding sees nothing else.

4. **Run a control for your own verdict wherever it owes one.** Decide owed-ness by `workflows-core:grounding-format` §2.2's closed-set rule. Where your re-derived verdict owes a control, run one and return it in `own_control`, on the same terms you would demand of a writer, in the `<method, and the case it was pointed at> — <path:line>` or `— no match` shape (§2.2). An outcome that asserts an absence with no control behind it is the defect this agent exists to catch, and it does not stop being one because a verifier wrote it. It is its own field rather than a line inside `own_evidence` because the caller writes it into the record when it rewrites the finding or writes its successor, and `own_evidence`'s shape requires a `path` a failed control has not got.

### `mode: compare`

5. **Compare.** For each finding, read `verdict`, `evidence`, `control` where it carries one, and — for a class-4 `[DG#n]` — `cites` and `cited`, and compare your blind result in `derived` against the original's, and against the cited `[CG#n]`'s.

   **Never revise the blind result.** `own_verdict`, `own_evidence` and `own_control` are returned exactly as `derived` gives them. You have now seen the original, so anything you re-derived here would not be independent. Disagreement with your own blind result goes in `notes`, never into its fields.

5a. **Settle the original's control, in two steps and in this order.**

   **First, decide whether this finding OWES one**, by `workflows-core:grounding-format` §2.2's closed-set rule and never by whether the field happens to be there. A control tests whether a **search** could have found the thing; where the question was a lookup in a set the caller handed in, there was no search to control for. So: a finding asserting no absence owes none, and neither does a `[DG#n]` of class 1 or 3 — both resolve against the `inventory` you were given — or of class 4, whose code half is the cited `[CG#n]`'s search and not its own. Everything else that asserts something is not there owes one. A finding that owes none is `control_outcome: not-owed` and this step is finished; **that is a correct finding, not a defect**, and treating a missing field as one without asking owed-ness first would contradict every class-1, class-3 and class-4 finding in the corpus.

   **Then, where it owes one, run it** — do not "confirm the cited line exists"; this agent checks nothing by looking at it. Run the control's own method against the case it names, and record in `notes` what it did:

   - **It reproduced** → `fired`. The search underlying the absence is shown capable of finding this kind of thing, so the absence means what it says.
   - **It did not reproduce** → `failed`. The search was never shown capable, so the absence rests on nothing. **This overturns the finding only where the finding's verdict rests on that absence.** A finding already reading `NOT-PROVABLE` and recording its own failed control did exactly what §2.2 tells a writer to do — you are reproducing its result, which is agreement — so return the outcome the comparison reaches and never `contradict` on this ground alone. Any other verdict resting on the absence **is** `contradict`, whatever your blind result turned up and even where it also found nothing: two searches sharing one blind spot is precisely the state a control exists to expose.
   - **It owes one and carries none** → `missing`, and `contradict`. A required field's absence is not something this agent may supply on the writer's behalf.

5b. **Check the blind result's own control.** Where `derived.own_verdict` owes a control by the same closed-set rule and `derived` carries no `own_control`, the blind result is incomplete: return that finding with `status: INCOMPLETE`, its `own_*` fields as `derived` gave them, and no `outcome`. Your caller re-derives it.

6. **Decide the outcome** from the closed set in `workflows-core:grounding-format` §8:
   - **`agree`** — your blind result reaches the same verdict.
   - **`extend`** — the claim holds at the same verdict, but your blind search surfaced evidence the original finding missed. Name, in `notes`, which `own_evidence` entries are the additions.
   - **`contradict`** — your blind result reaches a *different* verdict. **This is the outcome to return when the original finding is wrong — never soften a contradiction into an `extend`.** Filing `extend` over a finding whose verdict your blind search does not support is the exact failure mode this agent exists to prevent: it launders a wrong finding into evidence by dressing the correction up as an addition. If the two verdicts disagree, the outcome is `contradict`, full stop, regardless of how confident the original finding reads or how much of its evidence turned out to be real.
   - **`unprovable`** — your blind search could not settle the claim either way. This is independent of what the original finding concluded — report it even when the original was `CONFIRMED`.

## Output

### `mode: derive`

```yaml
mode:    derive
status:  OK | INPUT_MISSING | INPUT_UNBLIND | REPO_MISSING | FRAME_SET_MISSING | NO_INDEX | STALE_INDEX | COMMIT_MISMATCH
commits:                     # every repository pair Process step 1 checked — omitted on a design-only batch
  - repo_path: <absolute path>
    commit:    <the resolved commit this re-derivation was checked against>
findings:                    # one entry per finding in the batch, on status: OK only
  - finding_id:   <CG#n> | <DG#n>
    status:       OK | INPUT_MISSING
    own_verdict:  CONFIRMED | AMENDED | REWRITTEN | FALSE-FRIEND | NOT-PROVABLE | SUPERSEDED
    own_evidence:
      - path:  <relative to repo_path, or the frame path for a DG#n>
        lines: [<1-based line numbers>]   # omit only when the evidence is a whole-file read
        note:  <what this line or frame actually shows, and how it bears on the claim>
    own_control:  <required wherever own_verdict OWES a control by §2.2's closed-set rule, in §2.2's
                   shape; omitted otherwise>
    notes: |
      <optional — anything the caller should know>
```

### `mode: compare`

```yaml
mode:    compare
status:  OK | INPUT_MISSING | REPO_MISSING | FRAME_SET_MISSING | NO_INDEX | STALE_INDEX | COMMIT_MISMATCH
findings:                    # one entry per finding in the batch, on status: OK only
  - finding_id:  <CG#n> | <DG#n>
    status:      OK | INPUT_MISSING | INCOMPLETE
    outcome:     agree | extend | contradict | unprovable     # status: OK only
    own_verdict:  <exactly as derived gave it>
    own_evidence: <exactly as derived gave it>
    own_control:  <exactly as derived gave it, where it gave one>
    control_outcome: fired | failed | missing | not-owed     # status: OK only
      # Decide OWED-NESS FIRST, by §2.2's closed-set rule, and never from whether the field is present:
      #   `not-owed`  — this finding owes no control. Every finding asserting no absence, plus a [DG#n]
      #                 of class 1, 3 or 4 (1 and 3 resolve against the inventory the caller handed in,
      #                 which is a lookup and not a search; 4's code half belongs to the cited [CG#n]).
      #                 A `not-owed` finding with no control is correct and is NOT a defect.
      #   `fired`     — it owes one, carries one, and the control reproduced when THIS agent ran it.
      #   `failed`    — it owes one, carries one, and the control did not reproduce.
      #   `missing`   — it owes one and carries none. The writer skipped a required field.
      # `missing` forces `outcome: contradict`. `failed` forces it ONLY where the finding's verdict
      # RESTS on the absence — a finding already reading NOT-PROVABLE with its failed control recorded
      # said exactly the right thing (§2.2) and is agreed with, not overturned.
    commit: <the resolved commit this comparison's control ran against — omitted on a class-1/2/3 [DG#n]>
    notes: |
      <optional — where the blind search diverged from the original's approach, which own_evidence
      entries an extend adds, anything the caller should know before recording this outcome>
```

- Batch `status: OK` — every finding in the batch has an entry. `unprovable` is a legitimate outcome on a finding's `status: OK`, not a failure to complete the check.
- **`own_verdict` is returned on every outcome, `agree` included, and is a return field rather than a record field.** An outcome the caller cannot check against a verdict is one it has to take on trust, and removing that trust from the chain is this agent's whole purpose — the caller reconciles the two (`workflows-core:grounding-format` §8) and writes `verdict`, never both. A caller that transcribed `own_verdict` into the finding block would produce a record stating two verdicts at once, which `workflows-core:grounding-format` §2.1 forbids by naming the record's field set closed. **Report `agree` only where the blind verdict really is the same one** — an `agree` carrying a differing `own_verdict` contradicts itself, and the caller will normalise it to `contradict` rather than believe the label over the verdict.
- Finding `status: INPUT_MISSING` — a field required by this finding's row in the Inputs table was absent; that finding was not re-derived. Name the field and the row.
- Finding `status: INCOMPLETE` (compare only) — the blind verdict owes a control and `derived` carried none; no outcome. Your caller re-derives that finding once.
- Batch `status: INPUT_UNBLIND` (derive only) — an entry carried a field the derive step must never see; nothing was re-derived. Name the field and the finding.
- Batch `status: INPUT_MISSING` — a batch anchor was absent, or a `[CG#n]` batch named more than one commit; nothing was re-derived.
- Batch `status: REPO_MISSING` / `FRAME_SET_MISSING` — the path did not resolve to a directory; nothing was re-derived.
- Batch `status: NO_INDEX` — `frame_set_dir` held no index file; nothing was re-derived. The caller decides whether to export or name one — this agent never guesses at frame identity, exactly as `design-grounder` does not.
- Batch `status: STALE_INDEX` — an index was present but not one of its rows named a frame still in the directory; nothing was re-derived. Re-deriving a `[DG#n]` against an index whose frames are all gone would settle the claim against nothing while looking like a completed check, which is the one outcome worse than refusing. This is the same state `product-workflows:design-grounder` reports under the same name, met from the other side: that agent finds it while building the finding, this one while re-deriving it, and a frame set can go stale in between. **The caller's remedy differs from `NO_INDEX`'s and the difference matters** — here the index and its descriptions are intact and the *frames* are missing, so re-running `/workflows-core:frames` writes nothing (`workflows-core:grounding-format` §6.2 step 6 forbids it) and naming it would send the operator to a no-op. Name the missing frames instead.
- Batch `status: COMMIT_MISMATCH` — a repository's `HEAD` did not resolve to the commit its findings are pinned to; nothing was re-derived. The caller decides whether to re-pin and retry — this agent never moves the repository.

Every status other than `OK` is a *refusal*, not a verdict: the finding — or, at batch level, every finding in the batch — is left with no outcome, and `workflows-core:grounding-format` §8 keeps a finding without an outcome out of evidence entirely. The caller owns what happens next; this agent never invents an outcome to avoid returning one.

## Hard rules

- NEVER re-derive anything from a derive dispatch that carries a finding's `verdict`, `evidence`, `control`, `cites`, `cited` or `derived`. Refuse it with `INPUT_UNBLIND`. This is the one rule the entire agent exists to enforce, and it applies to a cited `[CG#n]` exactly as it applies to a `file:line`.
- NEVER read anything under `$SPECS_PATH` outside `frame_set_dir`.
- NEVER revise `own_verdict`, `own_evidence` or `own_control` in compare mode. Disagreement goes in `notes`.
- NEVER return `extend` when the blind verdict differs from the original's. That is `contradict`, argued with the blind evidence — not a softened `extend`.
- NEVER edit, create, or delete files under `repo_path`. NEVER commit, cherry-pick, reset, rebase, switch branches, or force. `Bash` is for `baseline-integrity` and read-only search only.
- NEVER accept a finding's `commit` without re-running `baseline-integrity` against it first, in each mode. A verification against an unverified tree is not a verification.
- NEVER re-derive a finding that rests on code without both a `repo_path` and its `commit`, and NEVER treat a missing or unreadable `class` as licence to skip them. The Inputs table's row selection is fail-closed for exactly this reason: only an explicitly asserted `class` of `1`, `2`, or `3` on a `DG#`-prefixed finding excuses a commit, and nothing a caller omits ever does.
- NEVER accept a `control` by reading it. Run it. A control this agent did not reproduce is a failed control.
- NEVER read a missing `control` as a defect before deciding whether the finding owed one. Owed-ness comes from `workflows-core:grounding-format` §2.2's closed-set rule, and three of the four `[DG#n]` classes owe none — a check that skipped that question would contradict every one of them.
- NEVER `contradict` a `NOT-PROVABLE` finding whose recorded control failed and fails again for you. It said exactly what §2.2 tells a writer to say, and your re-run reproduced its result. Overturning it would punish the one finding on the page that told the truth about its own search.
- NEVER leave `own_evidence` blank, including for a `NOT-PROVABLE` verdict. State what was searched and why it fell short, per `workflows-core:grounding-format` §2.
- NEVER let a confident original write-up substitute for your own search. Fluency is not evidence — and in derive mode there is no write-up to read.
````

- [ ] **Step 3: Verify the contract's key strings.**

```bash
F=plugins/product-workflows/agents/grounding-verifier.md
grep -c 'INPUT_UNBLIND' $F                      # expect ≥ 5
grep -c 'provenance' $F                         # expect 0
grep -c 'discard your search and restart' $F    # expect 0
grep -c 'DO NOT READ' $F                        # expect 0
grep -c 'Never revise the blind result' $F      # expect 1
grep -c 'every distinct .repo_path./.commit. a class-4' $F   # expect 1 (Review Focus 3)
grep -c '^model: opus$' $F                      # expect 1
python3 -c "import re,sys;d=open('$F').read().split('---')[1];m=re.search(r'description: (.*)',d);print(len(m.group(1)))"   # expect < 1024
```

- [ ] **Step 4: Commit.**

```bash
git branch --show-current   # expect iv-gu/verifier-blind
git add plugins/product-workflows/agents/grounding-verifier.md
git commit -m "grounding-verifier: a blind derive mode and a compare mode (#73)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: `/prd-ground` Phase 7 dispatches in batches, in two steps

**Files:**
- Modify: `plugins/product-workflows/commands/prd-ground.md` — Phase 7 (`## Phase 7 — Verify` to the `---` before `## Phase 8`), Phase 2's `review_model` comment line.

**Interfaces:**
- Consumes: Task 3's inputs and returns, exactly as listed in Task 3's Interfaces.
- Produces: the stop code `PRD_GROUND_VERIFY_UNBLIND`; the batch cap `25`; the tally fields Task 5 reports (batches, dispatches per step, retries).

- [ ] **Step 1: Read** Phase 7 with the Read tool (`## Phase 7 — Verify` through `## Phase 8`), then save the inventory of every place the command reads a verifier return field, status or `provenance` — Steps 2–8 must leave every return-field reader finding its field (compare returns them unchanged), and Step 5 rewrites every `provenance` reader:

```bash
grep -n -E 'own_verdict|own_evidence|own_control|control_outcome|INPUT_MISSING|REPO_MISSING|FRAME_SET_MISSING|NO_INDEX|STALE_INDEX|COMMIT_MISMATCH|provenance' \
  plugins/product-workflows/commands/prd-ground.md | cut -c1-140 > "$SCRATCH/phase7-readers.txt"
wc -l "$SCRATCH/phase7-readers.txt"
```

Re-run the same grep after Step 9 and read every line that moved.

- [ ] **Step 2: Replace the opening and the dispatch block** — from `Dispatch \`grounding-verifier\` over **every** finding this run holds` through the closing `> provenance: [own-run | inherited — see below]"` line — with:

```markdown
**The set.** Phase 7 verifies **every** finding this run holds — Phase 3's baseline `[CG#n]` findings, freshly-merged Phase 5 claim findings, the successors Phase 6 appended for a moved horizon, and **the on-file findings this run re-checks, which are exactly these**: every `[CG#n]` already on file that does not read `SUPERSEDED` and whose `commit` equals the recorded pin of a repository whose `HEAD` still matched it in Phase 3 — on a plain re-run and a `--rebaseline` pass alike, `provenance: inherited` (below), and none under `--no-code` (below) — **and never an on-file `[DG#n]`**, which no run of this command re-checks. A moved repository's on-file findings are not among them: a `--rebaseline` pass supersedes them in Phase 8.

**Batches.** Cut the set into batches before dispatching anything:

- A `[CG#n]` batches with the other `[CG#n]` pinned to the same repository. A `[DG#n]` batches with the other `[DG#n]` of the same frame set — the one Phase 5 recorded for it, or for a Phase 6 successor the frame set Phase 8's placement puts its superseded block in. A class-4 `[DG#n]` carries, beside its frame set, the repository and commit of the `[CG#n]` it cites, so one frame-set batch may hold several repository pairs.
- Within a group, put a repository's baseline `[CG#n]` first, then order the `[CG#n]` by the requirement id each one's `claim` names, and the `[DG#n]` by finding id. Cut each group into batches of at most **25** findings, the baseline counting toward its batch. **The cap is stated here and nowhere else.**
- **Nothing about a finding's answer decides its batch** — not its `verdict`, `evidence`, `control` or `cites`. A batch made of "the `NOT-PROVABLE` ones" would tell the blind step what the original concluded.

**Two dispatches per batch, in this order: `mode: derive`, then `mode: compare`** (`workflows-core:grounding-format` §8). At most four dispatches per Agent message — wait for a message's dispatches before sending the next — and a batch's compare dispatch may go in any message after its derive dispatch has returned. Both are pinned to the Opus chain (`review_model`, frontmatter-pinned, no override unless §10 enforces a model):

→ Agent (subagent_type: "product-workflows:grounding-verifier", model: `<review_model — §2 Opus chain, equal to grounding-verifier's frontmatter pin; under §10, run_flags.enforced_model>`):  # recorded in model_routing as review_model above, frontmatter-pinned, no override added unless §10 enforces a model
  > "mode: derive
  > repo_path:     [a [CG#n] batch: the repository all of its findings are pinned against; omit on a [DG#n] batch]
  > frame_set_dir: [a [DG#n] batch: its frame set; omit on a [CG#n] batch]
  > inventory:     [a [DG#n] batch: the Phase 0 step 8 claim list, id and text, exactly as design-grounder was handed it; omit on a [CG#n] batch]
  > findings:
  >   - id:        [CG#n or DG#n]
  >     claim:     [the requirement premise as the finding recorded it — a BR#n on route: brd, an AC#n/FR#n/US#n on route: idea]
  >     class:     [1-4 — DG#n only, omit for CG#n]
  >     commit:    [the finding's pinned commit — every CG#n and every class-4 DG#n; omit only for a class-1/2/3 DG#n]
  >     repo_path: [class-4 DG#n only — the repository the CG#n it cites is pinned against]"

**The derive dispatch carries the question and never the answer.** It names no finding's `verdict`, `evidence`, `control` or `cites`, and no path under `$SPECS_PATH` other than `frame_set_dir`. This replaces a contract that handed the verifier the whole record and relied on it not to read the answer until it had derived its own; four of eight dispatches in one live run reported, unprompted, that they could not honour that, since nothing in an agent's context can be un-read. The agent refuses a derive dispatch carrying any of those fields (`INPUT_UNBLIND`, below), so a slip here stops the run instead of passing as a verification.

→ Agent (subagent_type: "product-workflows:grounding-verifier", model: `<review_model — as the derive dispatch>`):
  > "mode: compare
  > repo_path, frame_set_dir, inventory: [exactly as this batch's derive dispatch]
  > findings:
  >   - id, claim, class, commit, repo_path: [exactly as this batch's derive dispatch]
  >     verdict:  [the finding's verdict]
  >     evidence: [the finding's evidence list]
  >     control:  [the finding's control, where it carries one — omit where it carries none; the agent decides owed-ness itself from grounding-format §2.2's closed-set rule and never from the field being absent]
  >     cites:    [class-4 DG#n only — the CG#n it cites]
  >     cited:    [class-4 DG#n only — that CG#n's record as this run holds it at dispatch: verdict, evidence, control]
  >     derived:  [this finding's entry from the derive return, verbatim]"
```

- [ ] **Step 3: Replace the paragraph** that begins `Supply the finding **exactly as the agent's own Inputs contract declares it**` and ends `never to withhold a field the contract lists.` with:

```markdown
**Match every returned entry to its finding by `finding_id`, never by position.** An agent may return a batch's entries in another order, or leave one out; a finding with no entry in a return is incomplete (*Retry once*, below).

**`own_verdict`, `own_evidence` and `own_control` are read from the derive return, never from the compare return.** Compare passes them through unchanged by its contract; where its echo differs from the derive return, compare revised a blind result it must not touch, and that finding's compare entry is incomplete (*Retry once*, below).
```

Keep the paragraph `**Which anchor fields go with which finding is that contract's own Inputs table, not this command's**` and its three bullets, changing only their leads to say both dispatches: `**Always pass \`class\` for a \`[DG#n]\`, in both dispatches.**`, `**Always pass \`frame_set_dir\` for a \`[DG#n]\` batch.**`, `**Always pass \`inventory\` for a \`[DG#n]\` batch**`. Leave their bodies as they are.

- [ ] **Step 4: Under `--no-code`, add one sentence** at the end of the paragraph that begins `**Under \`--no-code\`, "every finding this run holds" is the new \`[DG#n]\` set`:

```markdown
So no `[CG#n]` batch exists on such a run; a class-4 `[DG#n]`'s repository pair is the on-file `[CG#n]` it cites, and `cited` carries that on-file record.
```

- [ ] **Step 5: Rewrite the `provenance` paragraph's last two sentences.** In the paragraph beginning `**\`provenance\` is set per finding, by origin`, replace from `The agent's own Inputs contract and` to the paragraph's end with:

```markdown
`workflows-core:grounding-format` §8 defines an inherited finding as one from "another team's report **or an earlier run of this workflow**," and a finding surviving from before this invocation, unreproduced, is the second of those, regardless of how confident its write-up reads. **`provenance` is this phase's own bookkeeping, and it is never sent to the verifier**: it decides which `contradict` branch below writes — an in-place rewrite or a supersession — and the derive step, which never sees a finding's answer, searches an inherited finding exactly as hard as any other without being told which it is.
```

- [ ] **Step 6: Replace the status block** — from `**Act on \`status\` first — an \`outcome\` exists only on \`status: OK\`.**` through the end of its `REPO_MISSING / FRAME_SET_MISSING / NO_INDEX / STALE_INDEX` bullet — with:

```markdown
**Act on `status` first — an `outcome` exists only on a finding whose compare entry reads `status: OK`.** Each return carries a **batch** `status` and, on `OK`, a `status` per finding. Every value other than `OK` is a refusal, not a verdict: no outcome was produced, and a finding carrying no outcome is not evidence and blocks `/brd-split` for as long as it stays on file (`workflows-core:grounding-format` §8). So none of them may be shrugged off and none may be written.

**Batch statuses**, from either dispatch:

- **`OK`** — act on each finding's own `status`, below.
- **`COMMIT_MISMATCH`** — a repository moved between Phase 3's pin and this dispatch. Stop:
  `PRD_GROUND_VERIFY_COMMIT_MISMATCH: <the batch's finding ids> could not be verified — <repo> is at <resolved-HEAD>, not the pinned <commit>. Re-run '/product-workflows:prd-ground <KEY> --rebaseline' from a clean tree.`
  **Under `--no-code` the same message names the re-run without the mode** — `'/product-workflows:prd-ground <KEY> --rebaseline'`, no `--no-code` — since that mode refuses the flag the remedy requires, and the finding that failed here is pinned to a repository the design pass cannot re-pin on its own.
  The same repair as Phase 5's own `COMMIT_MISMATCH`: re-run from Phase 3, which re-pins and re-grounds. **`--rebaseline` is part of the remedy, not an optional extra**, and the message says so: where `grounding/baselines.md` recorded a pin for this repository when the run began, this run never replaced it — Phase 8 records a new pin, and this stop comes before it — and `HEAD` has moved off it, so the re-run stops with `PRD_GROUND_NEEDS_REBASELINE` unless the flag is given. "Re-run from a clean tree" on its own would send the operator straight into that second stop. Where no pin was recorded, the flag changes nothing and costs nothing.
- **`INPUT_UNBLIND`** (derive only) — this command handed the blind step a finding's answer. Stop, and fire `emit-block` per Phase 11's capture-at-block invariant — a dispatch this command controls getting the contract wrong is a plugin gap:
  `PRD_GROUND_VERIFY_UNBLIND: the derive dispatch for <the batch's finding ids> carried <field> on <finding-id> — the blind step must never be handed the answer it re-derives. No finding was written.`
- **`INPUT_MISSING`** — a batch anchor was absent. Stop, quoting the field the agent named, and fire `emit-block` as above (most often a `[DG#n]` batch sent without its `inventory` or its `frame_set_dir` — `inventory` first, because it is the newest requirement and the one whose omission made a class-1 finding permanently unverifiable).
- **`REPO_MISSING` / `FRAME_SET_MISSING` / `NO_INDEX` / `STALE_INDEX`** — the source this batch rests on is gone or unusable (a repository unmounted mid-run, a frame set removed or exported without an index since it was ground). Stop, naming the batch's findings and the path the agent reported — and the command that resolves it: on `NO_INDEX` that is `/workflows-core:frames <this run's KEY>`, then re-run this command. **On `STALE_INDEX` it is not** — the index is there and its descriptions are intact; the frames are gone. Re-running `/frames` on an empty directory writes nothing (`workflows-core:grounding-format` §6.2 step 6 forbids it), so naming it would send the operator to a no-op. Name the missing frames instead: restore them to the directory, then re-run this command — and `/frames` only if the set changed while they were away.

**Finding statuses:**

- **`OK`** (compare) — act on `outcome`, below.
- **`INPUT_MISSING`** — this command's dispatch was short a field that finding's row requires (most often a `[DG#n]` sent without its `class`). Stop, quoting the field and row the agent named, and fire `emit-block` as above.
- **`INCOMPLETE`** (compare), **no entry**, a **blank `own_evidence`**, or a compare echo that **differs** from the derive return — incomplete; *Retry once*, below.

**Retry once.** Re-dispatch every incomplete finding once, through the step that failed, as a batch of its own beside the rest of its group's anchors: a finding missing from a derive return, with a blank `own_evidence`, or marked `INCOMPLETE` gets a fresh derive dispatch and then a compare dispatch; a finding missing from a compare return, or whose compare echo differed, gets a fresh compare dispatch over its existing derive entry. **One retry per finding per run, never more.** A finding still incomplete after it falls to the rules that already govern an incomplete return: where its compare entry exists and reads `contradict`, the *incomplete return* branches under `contradict` below apply (an own-run finding stops the run with `PRD_GROUND_VERIFY_INCOMPLETE`; an on-file one writes nothing and is reported not verified by this run); where the compare entry reads `agree` or `extend` and only the blind verdict's own control is missing, it proceeds — the record keeps the original's control, which compare ran — and the Final report notes it; anything else stops the run with `PRD_GROUND_VERIFY_INCOMPLETE`, naming the finding and the step that failed twice.
```

Leave `**Nothing reaches Phase 8 unverified.**` and everything after it in Phase 7 as written, except Steps 7–8.

- [ ] **Step 7: Class-4 sweep re-dispatch.** Replace the paragraph beginning `**Every finding the sweep re-dispatches carries the \`frame_set_dir\` its own Phase 5 dispatch named**` with:

```markdown
**Every finding the sweep re-dispatches carries the `frame_set_dir` its own Phase 5 dispatch named** (Phase 5, *Record which frame set each `[DG#n]` came from*), so every one whose cited `[CG#n]` this phase rewrote can be re-derived rather than retired: batch them by frame set, at most 25 to a batch, and dispatch each batch through both steps again — `mode: derive`, then `mode: compare` with `cited` carrying the rewritten `[CG#n]` — with the same `model:` as the first dispatches (under §10, `run_flags.enforced_model`), and act on the returned outcomes as above — the own-run branch, since a held finding is not on file.
```

- [ ] **Step 8: Inherited-control paragraph.** In the paragraph beginning `**An inherited finding that owes a control and carries none is \`contradict\` like any other`, replace `and \`product-workflows:grounding-verifier\`'s own rules forbid searching one any less hard;` with `and the derive step, which never learns a finding's provenance, searches it exactly as hard as any other;`.

- [ ] **Step 9: Phase 2 comment.** In Phase 2's `review_model:` line, replace `grounding-verifier (Phase 7)` with `grounding-verifier (Phase 7, both steps)`.

- [ ] **Step 10: Verify.**

```bash
F=plugins/product-workflows/commands/prd-ground.md
grep -c 'exactly as the agent.s own Inputs contract declares it' $F     # expect 0
grep -c 'One instance per finding' $F                                    # expect 0
grep -c 'mode: derive' $F                                                # expect ≥ 2
grep -c 'PRD_GROUND_VERIFY_UNBLIND' $F                                   # expect 1
grep -c 'stated here and nowhere else' $F                                # expect 1
grep -c 'by .finding_id., never by position' $F                          # expect 1
grep -c 'One retry per finding per run' $F                               # expect 1
grep -c 'read from the derive return, never from the compare return' $F  # expect 1 (Review Focus 2)
grep -c 'the baseline counting toward its batch' $F                      # expect 1 (Review Focus 4)
grep -c 'no .\[CG#n\]. batch exists on such a run' $F                    # expect 1 (Review Focus 5)
grep -n -- '> provenance:' $F                                            # expect no output
./scripts/check-docs.sh --root . ; echo "EXIT=$?"                        # expect EXIT=0
```

- [ ] **Step 11: Commit.**

```bash
git branch --show-current   # expect iv-gu/verifier-blind
git add plugins/product-workflows/commands/prd-ground.md
git commit -m "prd-ground Phase 7: blind derive then compare, in batches of 25, retried once (#73, #74)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Phase 1 cost warning and the Final report tally

**Files:**
- Modify: `plugins/product-workflows/commands/prd-ground.md` — Phase 1 (before step 1), the Final report paragraph that begins `and model routing (+ any Opus degradation`.

**Interfaces:**
- Consumes: Task 4's cap (25) and retry rule.

- [ ] **Step 1: Read** Phase 1 and the Final report section with the Read tool.

- [ ] **Step 2: Insert a new step** in Phase 1, between step 0 and step 1, numbered `0a`:

```markdown
0a. **State the cost before asking for repositories**, on every run that grounds code (never under `--no-code`, which resolves no repository to ground). N is Phase 0 step 8's claim count; M is the number of `[CG#n]` already on file in `grounding/code-grounding.md` and not reading `SUPERSEDED` — 0 on a first run. M is the most Phase 7 re-verifies: a repository that has moved is re-ground under `--rebaseline` instead, and its findings are superseded rather than re-verified. Print, in place of the bracketed values:

    > This requirement set has N claims. Each repository you name is ground against all N, and every finding is verified on Opus in two steps, in batches of up to 25: K repositories → K×N findings and about K×⌈N/25⌉×2 verification dispatches. A re-run re-verifies every finding already on file for a repository that has not moved (up to M today).

    Print it with K left as the symbol — the operator has not named the repositories yet — and with N and M filled in. **It informs and gates nothing**: Phase 5 still sends every claim to every repository named, and nothing here narrows that. It is here because adding a repository multiplies both fan-outs by the full claim count, and the cost was otherwise visible only at Phase 7, after both had been paid for.
```

- [ ] **Step 3: Extend the Final report's verifier tally.** In the paragraph that contains `separately, and the verifier` / `tally (\`agree\` / \`extend\` / \`contradict\` / \`unprovable\`)`, insert after `tally (\`agree\` / \`extend\` / \`contradict\` / \`unprovable\`)` the text:

```markdown
 — with the number of batches, the number of `mode: derive` and `mode: compare` dispatches, and every retry by finding id and the step retried, or "no retries" —
```

and, after the clause that ends `which wrote nothing and leaves that finding **not verified by this run** — say so of it by id, beside the \`outcome\` an earlier run left on it (on an own-run finding the same return stops the run instead, with \`PRD_GROUND_VERIFY_INCOMPLETE\`) —`, insert:

```markdown
every `agree`/`extend` that proceeded after its retry with the blind verdict's own control still missing, by id —
```

- [ ] **Step 4: Verify.**

```bash
F=plugins/product-workflows/commands/prd-ground.md
grep -c 'State the cost before asking for repositories' $F   # expect 1
grep -c 'number of batches' $F                               # expect 1
./scripts/check-docs.sh --root . ; echo "EXIT=$?"            # expect EXIT=0
```

- [ ] **Step 5: Commit.**

```bash
git branch --show-current   # expect iv-gu/verifier-blind
git add plugins/product-workflows/commands/prd-ground.md
git commit -m "prd-ground: state the grounding and verification cost before repositories are chosen (#74)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Docs pages, the rules map line, and the rationale

**Files:**
- Modify: `plugins/product-workflows/docs/commands/prd-ground.md` (lines near 6, 145, the `**Phase 7 —` bullet, the `## When it is worth running` paragraph)
- Modify: `plugins/product-workflows/docs/reference/agents.md` (the `grounding-verifier` row)
- Modify: `.claude/rules/brd-route.md` (the `/prd-ground` map line; a new invariant bullet)
- Modify: `docs/maintainers/rationale.md` (new section `## verifier-blind-batched`)

- [ ] **Step 1: Read** each file with the Read tool.

- [ ] **Step 2: Command page, synopsis.** In `docs/commands/prd-ground.md` line ~6, replace `independently re-derives every live finding (\`grounding-verifier\`, Opus)` with `independently re-derives every live finding — blind, then compared, in batches (\`grounding-verifier\`, Opus)`.

- [ ] **Step 3: Command page, agents list.** Replace `\`grounding-verifier\` (Phase 7, one per finding, frontmatter-pinned to Opus` with `\`grounding-verifier\` (Phase 7, two dispatches per batch of up to 25 findings — a blind \`mode: derive\`, then \`mode: compare\` — frontmatter-pinned to Opus`.

- [ ] **Step 4: Command page, Phase 7 bullet.** In the bullet beginning `- **Phase 7 — \`grounding-verifier\` over every finding`, insert after its first sentence (ending `— except any already reading \`SUPERSEDED\`: a retired finding keeps the outcome it had, and re-deriving it could only bring it back to life beside its successor.`):

```markdown
  It runs in batches of up to 25 findings per repository or frame set, each in two dispatches: a blind re-derivation that is handed each finding's requirement and source and never its verdict, evidence, control or citation — and refuses a dispatch that carries one — then a comparison that runs the original's control and settles the outcome without changing the blind result. A finding whose result comes back incomplete is re-dispatched once.
```

- [ ] **Step 5: Command page, cost paragraph.** In `## When it is worth running (idea route)`, replace `(Phase 7, one \`grounding-verifier\` dispatch per finding, frontmatter-pinned — no override unless \`--enforce-model\` enforces one)` with `(Phase 7, batched — the run states the arithmetic before you name repositories — frontmatter-pinned, no override unless \`--enforce-model\` enforces one)`.

- [ ] **Step 6: Agents reference row.** Replace the `grounding-verifier` row's description cell with:

```markdown
Re-derives `[CG#n]`/`[DG#n]` findings in batches from their source — the pinned repo, or the frame set for a design-only one — first blind (`mode: derive`, never handed the finding's answer, and refusing a dispatch that carries it), then against the original (`mode: compare`); returns agree / extend / contradict / unprovable.
```

- [ ] **Step 7: Rules map line.** In `.claude/rules/brd-route.md`'s `/prd-ground` line, replace `[grounding-verifier@Opus: independent re-derivation, no outcome ⇒ not evidence;` with `[grounding-verifier@Opus, batched ≤25 per repository or frame set, two dispatches each — a blind derive handed no finding's answer, then a compare: independent re-derivation, no outcome ⇒ not evidence;`.

- [ ] **Step 8: Rules invariant.** Append to `.claude/rules/brd-route.md`'s `## Invariants` list:

```markdown
- **`/prd-ground`'s verification is blind by construction, batched, and never weakened per finding.** The derive dispatch carries a finding's premise and source and never its `verdict`, `evidence`, `control` or `cites` (`workflows-core:grounding-format` §8); a batch's composition never depends on a finding's answer; and every finding gets its own Opus re-derivation on every run — no cheaper tier, no sample, no repository-scope finding standing in for the ones under it, and no outcome carried forward from an earlier run. Read the rationale before proposing any of those as a saving. ([why](../../docs/maintainers/rationale.md#verifier-blind-batched))
```

- [ ] **Step 9: Rationale section.** Append to `docs/maintainers/rationale.md`:

```markdown
## verifier-blind-batched

**Blind by construction (#73).** Until 2026-10-01 `/prd-ground` Phase 7 handed `grounding-verifier` the whole finding — `evidence` and `cites` included — and relied on the agent's own rule not to read them before re-deriving. In one live run of eight dispatches, four reported unprompted that they could not comply: the evidence was already in their context. The anchoring risk is toward `agree` on exactly the failure that run found most often, an original citing something real but adjacent to the premise. A self-imposed discipline cannot remove text from a context window, so the answer is no longer sent: the derive dispatch carries the premise and the source, and the agent refuses one that carries more.

**Batched, not weakened (#74).** One Opus dispatch per finding made a 138-claim, two-repository run cost 278 verifier dispatches in about 70 sequential batches, 200 of them `NOT-PROVABLE` and 117 from a frontend answering backend claims. Batching by repository or frame set, at most 25 to a batch and two dispatches each, makes that run about 24 dispatches, and each derive batch explores its repository once instead of once per finding.

**Refused, with the reason:**

- *A cheaper tier, or a sample, for `NOT-PROVABLE` findings.* A wrong `NOT-PROVABLE` where the code actually contradicts the premise sends a question to `/brd-interview`'s operator without the fact that settles it. Every finding keeps its own Opus re-derivation.
- *One repository-scope finding ("this repository holds no persistence layer") standing in for the findings under it.* The findings under it would never be individually re-derived. Inside one derive batch the agent may cite a fact it established for one finding for another, after checking it bears on that premise — each finding's evidence still stands alone.
- *Carrying an outcome forward from an earlier run at the same pin.* It needs a stamp saying which verifier contract the outcome was reached under, something must bump that stamp whenever the agent, `grounding-format` or the model changes, and no gate would check it; a missed bump carries a stale outcome forward silently. Batching shrinks a re-run's cost by the same factor as a first run's, and on unchanged code a re-verification is the only way the first verifier's error surfaces.
- *One dispatch with the originals sealed in a file the agent opens after deriving.* Blind by instruction again.
- *The comparison done inline by Phase 7.* Running controls and judging agreement would move to the session's model, which need not be Opus, and every result would land in the orchestrator's context.
- *Continuing the same agent with the withheld fields.* Agent continuation is not available in every harness these commands run in.
- *Checkpoint and resume across a Phase 7 stop.* With batching a lost pass is about 24 dispatches; an incomplete result is retried once instead.
```

- [ ] **Step 10: Verify.**

```bash
grep -c 'verifier-blind-batched' .claude/rules/brd-route.md docs/maintainers/rationale.md   # expect 1 and 1
wc -c .claude/rules/brd-route.md                                                            # expect < 20000
python3 scripts/validate-catalog.py ; echo "EXIT=$?"                                        # expect EXIT=0
./scripts/check-docs.sh --root . ; echo "EXIT=$?"                                           # expect EXIT=0
```

- [ ] **Step 11: Commit.**

```bash
git branch --show-current   # expect iv-gu/verifier-blind
git add plugins/product-workflows/docs/commands/prd-ground.md plugins/product-workflows/docs/reference/agents.md .claude/rules/brd-route.md docs/maintainers/rationale.md
git commit -m "docs: prd-ground's verification is blind and batched; the rule and its rationale

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: Subject sweep and the after-counts

**Files:** whatever the sweep finds.

- [ ] **Step 1: Re-run Task 0's counts** and compare:

```bash
python3 "$SCRATCH/count.py" \
  "One instance per finding" \
  "one per finding" \
  "one \`grounding-verifier\` dispatch per finding" \
  "exactly as the agent's own Inputs contract declares it" \
  "discard your search and restart it" \
  "DO NOT READ before Process step 2" \
  "Process step 2" \
  "provenance: own-run | inherited" \
  "§5 of its own instructions" \
  "without first reading \`evidence\`" | tee "$SCRATCH/counts-after.txt"
diff "$SCRATCH/counts-before.txt" "$SCRATCH/counts-after.txt"
```

Expected after-counts outside `CHANGELOG.md`: 0 for every retired phrase. Every remaining hit must be in a `CHANGELOG.md` (history) or describe something other than the verifier (for `one per finding`, read each hit; `code-grounder` is "one per repository" and must not be touched). Fix any live stale hit and re-count.

- [ ] **Step 2: Sweep by subject.** Read every hit of these, in `plugins/`, `.claude/rules/`, `CLAUDE.md`, `docs/maintainers/`, `README.md`, and confirm each sentence is still true:

```bash
grep -rn -E 'grounding-verifier|verifier' plugins .claude/rules CLAUDE.md docs/maintainers README.md --include=*.md \
  | grep -v CHANGELOG | grep -v -E 'agents/grounding-verifier\.md|commands/prd-ground\.md'
```

Known hits that stay true (no edit): `design-grounder.md:~204` (fail-closed row selection), `figure-reader.md:22`, `idea-format.md:~278`, `read-only-repos.md:5`, `phase-handoff.md:~304` (`NO_INDEX`/`STALE_INDEX` — now batch-level, still returned), `frame-describer.md:19`, `commands/frames.md:22,334`, `docs/commands/frames.md:73`, `brd-split.md:442,1499`, `brd-interview.md:431,2324` (return fields, unchanged), `brd-package.md:511`, `docs/reference/model-routing.md:22` (pinned Opus, unchanged). Any sentence that states the verifier is dispatched per finding, reads `evidence` after a step, or receives `provenance` is stale: rewrite it to Tasks 3–4's behaviour.

- [ ] **Step 3: Exclusivity probe** (CLAUDE.md refinement 3) on the rewritten files: `only when`, `is the only`, `nothing else`, `and no other`, `only ever`, `the only`, `the sole`:

```bash
grep -n -E 'only when|is the only|nothing else|and no other|only ever|the only|the sole' \
  plugins/product-workflows/agents/grounding-verifier.md \
  plugins/workflows-core/references/grounding-format.md | sed -n '1,80p'
```

Read each hit in the new or edited text against Tasks 3–4; fix any that the two-mode design falsified.

- [ ] **Step 4: Commit** any fixes (skip if none).

```bash
git branch --show-current   # expect iv-gu/verifier-blind
git add -A plugins .claude/rules docs/maintainers
git commit -m "sweep: retire every per-finding and self-blinding statement of the verifier

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 8: Release — versions, CHANGELOGs, gates

**Files:**
- Modify: `plugins/product-workflows/.claude-plugin/plugin.json`, `plugins/workflows-core/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (the two entries' `version` only — do not reformat)
- Modify: `plugins/product-workflows/CHANGELOG.md`, `plugins/workflows-core/CHANGELOG.md`

- [ ] **Step 1: Bump minor versions** from the values Task 0 recorded: product-workflows `3.10.x` → `3.11.0`; workflows-core `1.8.x` → `1.9.0`. Edit `"version"` in each `plugin.json` and the matching entry in `.claude-plugin/marketplace.json` with the Edit tool (one string each).

- [ ] **Step 2: product-workflows CHANGELOG.** Insert above the newest section:

```markdown
## [3.11.0] — 2026-10-01

**Update `workflows-core` to 1.9.0 with this release**: §8 states the structural rule the verifier's new contract implements.

### Changed

- **`/prd-ground` verifies blind, in batches (#73, #74).** Phase 7 cuts its verification set into batches of up to 25 findings per repository or frame set and dispatches `grounding-verifier` twice per batch: `mode: derive`, handed each finding's requirement and source and never its verdict, evidence, control or citation, then `mode: compare`, handed the original beside the blind result. The old contract handed the verifier the whole finding and relied on it not to read the answer first; four of eight dispatches in one live run reported they could not. A 138-claim, two-repository run drops from 278 verifier dispatches to about 24, with every finding still re-derived on Opus and every finding on file still re-verified on a re-run.
- **`grounding-verifier` has two modes.** Derive refuses a dispatch carrying a finding's answer (`INPUT_UNBLIND`) and reads nothing under `$SPECS_PATH` outside the frame set; compare runs each original's control, never revises the blind result, and returns the same per-finding fields as before. The `provenance` input is gone: the blind step searches an inherited finding exactly as hard as any other without being told which it is.

### Added

- **Phase 1 states the cost before repositories are chosen** — the claim count, the per-repository multiplier, the batch arithmetic, and the findings on file a re-run re-verifies.
- **An incomplete verifier result is retried once**, through the step that failed, before the run stops (`PRD_GROUND_VERIFY_INCOMPLETE`). A derive dispatch this command built wrong stops with `PRD_GROUND_VERIFY_UNBLIND`.
```

- [ ] **Step 3: workflows-core CHANGELOG.** Insert above the newest section:

```markdown
## [1.9.0] — 2026-10-01

### Changed

- **`grounding-format` §8: independence is structural, not a discipline the verifier keeps (#73).** The step that re-derives is handed the requirement premise and the source, never the finding's verdict, evidence, control or citation; verification is a blind re-derivation followed by a comparison, each its own dispatch. §4.1 says the baseline re-derivation is the blind step's integrity re-run. `product-workflows` 3.11.0 implements it.
```

- [ ] **Step 4: Run the full gate chain.**

```bash
python3 scripts/validate-catalog.py --selftest && python3 scripts/validate-catalog.py \
 && ./scripts/check-id-grammar.sh --selftest && ./scripts/check-id-grammar.sh --root . \
 && ./scripts/check-docs.sh --selftest && ./scripts/check-docs.sh --root . \
 && npm ci --prefix scripts/mermaid --ignore-scripts --no-audit --no-fund \
 && node scripts/mermaid/check-mermaid.mjs --selftest && node scripts/mermaid/check-mermaid.mjs --root . \
 && python3 "$(find plugins -type f -name session-cost.py)" --selftest
echo "EXIT=$?"
```

Expected: `EXIT=0`. Fix any failure and re-run before committing.

- [ ] **Step 5: Commit.**

```bash
git branch --show-current   # expect iv-gu/verifier-blind
git add .claude-plugin/marketplace.json plugins/product-workflows/.claude-plugin/plugin.json plugins/workflows-core/.claude-plugin/plugin.json plugins/product-workflows/CHANGELOG.md plugins/workflows-core/CHANGELOG.md
git commit -m "release: product-workflows 3.11.0, workflows-core 1.9.0 — blind, batched verification

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 9: Live smoke run

**Files:** fixtures under the session scratchpad only; nothing in the repo.

- [ ] **Step 1: Confirm the worktree's plugins are the ones loaded.** A headless session loads them with `--plugin-dir`; the installed `@shipwright` copies must not shadow them.

```bash
WT=/workspace/ai-workflows/.claude/worktrees/verifier-blind
DISABLE='{"enabledPlugins":{"product-workflows@shipwright":false,"workflows-core@shipwright":false,"dev-workflows@shipwright":false,"docs-workflows@shipwright":false,"prose-style@shipwright":false}}'
claude -p --plugin-dir "$WT/plugins" --settings "$DISABLE" --max-budget-usd 1 \
  "Print the first sentence of the description of the product-workflows:grounding-verifier agent, verbatim, and nothing else."
```

Expected: the output contains `in batches` and `derive mode`. If it shows the old description, stop and report: the smoke run would test the installed version.

- [ ] **Step 2: Build the fixture** — a code repository and an idea-route specs repository, each with a bare `origin`, under the scratchpad:

```bash
FX=$SCRATCH/smoke && rm -rf "$FX" && mkdir -p "$FX"/{remotes,repos,specs}
git init -q --bare "$FX/remotes/tinyapp.git" && git init -q --bare "$FX/remotes/specs.git"
git init -q -b main "$FX/repos/tinyapp" && cd "$FX/repos/tinyapp"
mkdir -p app && cat > app/orders.py <<'EOF'
MAX_ITEMS = 50

def create_order(items):
    if len(items) > MAX_ITEMS:
        raise ValueError("too many items")
    return {"items": items, "status": "new"}
EOF
git add -A && git commit -qm init && git remote add origin "$FX/remotes/tinyapp.git" && git push -q -u origin main
git init -q -b main "$FX/specs" && cd "$FX/specs"
mkdir -p specifications/PRD-SMOKE-1-tiny-orders && cat > specifications/PRD-SMOKE-1-tiny-orders/prd.md <<'EOF'
---
kind: prd
key: PRD-SMOKE-1
title: Tiny orders
---
# Tiny orders

## Requirements

- [FR#1] An order rejects more than 50 items.
- [FR#2] A new order starts in status `new`.
- [FR#3] An order records the customer's email address.
- [FR#4] Orders are persisted to a database table.
EOF
git add -A && git commit -qm "PRD-SMOKE-1" && git remote add origin "$FX/remotes/specs.git" && git push -q -u origin main
```

Then read `/prd-ground`'s Phase 0 for the idea route (`commands/prd-ground.md`, route detection and step 8) and adjust the PRD file until Phase 0 accepts it — the minimum frontmatter and the requirement-row form are Phase 0's to say, not this plan's. Record each adjustment.

- [ ] **Step 3: First run.** Expected: `[FR#1]`/`[FR#2]` `CONFIRMED`, `[FR#3]`/`[FR#4]` `NOT-PROVABLE` or `REWRITTEN`, every finding with an outcome.

```bash
cd "$FX/specs"
SPECS_PATH="$FX/specs" REPOS_PATH="$FX/repos" claude -p --plugin-dir "$WT/plugins" --settings "$DISABLE" \
  --dangerously-skip-permissions --output-format stream-json --verbose --max-budget-usd 15 \
  "/product-workflows:prd-ground PRD-SMOKE-1 --skip-feedback --skip-costs --no-docs. When asked for repositories answer: tinyapp. Take the recommended option at every choice." \
  > "$FX/run1.jsonl"
python3 - "$FX/run1.jsonl" <<'EOF'
import json, sys
bad, modes = [], []
for line in open(sys.argv[1]):
    ev = json.loads(line)
    for block in (ev.get("message", {}) or {}).get("content", []) or []:
        if block.get("type") == "tool_use" and block.get("name") in ("Agent", "Task"):
            inp = block.get("input", {})
            if "grounding-verifier" in str(inp.get("subagent_type", "")):
                p = inp.get("prompt", "")
                mode = "derive" if "mode: derive" in p else "compare" if "mode: compare" in p else "?"
                modes.append(mode)
                if mode == "derive" and any(k in p for k in ("verdict:", "evidence:", "control:", "cites:")):
                    bad.append(p[:300])
print("verifier dispatches:", modes)
print("derive dispatches carrying an answer field:", len(bad))
for b in bad: print("---", b)
EOF
```

Expected: `verifier dispatches: ['derive', 'compare']` (one batch), and `0` derive dispatches carrying an answer field. Commit the specs repo state the run left if the run's own handoff did not.

- [ ] **Step 4: Plant a wrong on-file finding and re-run.** In `$FX/specs/specifications/PRD-SMOKE-1-tiny-orders/grounding/code-grounding.md`, change `[FR#2]`'s finding verdict from `CONFIRMED` to `REWRITTEN` and its evidence note to claim orders start as `pending`; commit it on `main` of the specs repo. Re-run Step 3's command into `run2.jsonl`.

Expected: that finding's on-file block reads `SUPERSEDED` with `prior_verdict: REWRITTEN`, and a successor carries `verdict: CONFIRMED`, `outcome: contradict`, and the note `supersedes [CG#n]`.

- [ ] **Step 5: `INPUT_UNBLIND`.** Dispatch the agent directly with a derive payload carrying `evidence`:

```bash
claude -p --plugin-dir "$WT/plugins" --settings "$DISABLE" --dangerously-skip-permissions --max-budget-usd 3 \
  "Dispatch the product-workflows:grounding-verifier agent with exactly this prompt and print its full return verbatim:
mode: derive
repo_path: $FX/repos/tinyapp
findings:
  - id: CG#99
    claim: '[FR#1] An order rejects more than 50 items.'
    commit: $(git -C "$FX/repos/tinyapp" rev-parse HEAD)
    evidence: [{path: app/orders.py, lines: [4], note: rejects over MAX_ITEMS}]"
```

Expected: `status: INPUT_UNBLIND` naming `evidence` and `CG#99`, and no `findings` re-derived.

- [ ] **Step 6: `INCOMPLETE`.** Dispatch compare with a `derived` entry whose absence verdict carries no `own_control`:

```bash
claude -p --plugin-dir "$WT/plugins" --settings "$DISABLE" --dangerously-skip-permissions --max-budget-usd 3 \
  "Dispatch the product-workflows:grounding-verifier agent with exactly this prompt and print its full return verbatim:
mode: compare
repo_path: $FX/repos/tinyapp
findings:
  - id: CG#98
    claim: '[FR#3] An order records the customer email address.'
    commit: $(git -C "$FX/repos/tinyapp" rev-parse HEAD)
    verdict: REWRITTEN
    evidence: [{path: app/orders.py, lines: [7], note: the order dict holds items and status only}]
    control: 'grep -rn status app/ pointed at the status field known present — app/orders.py:7'
    derived:
      own_verdict: REWRITTEN
      own_evidence: [{path: app/orders.py, lines: [7], note: no email field on the order}]"
```

Expected: finding `CG#98` with `status: INCOMPLETE` and no `outcome`, its `own_*` exactly as given. (Phase 7's retry of such a finding is verified by reading Task 4, step 6.)

- [ ] **Step 7: Record the results** in `docs/superpowers/verification/2026-10-01-verifier-blind-batched.md` — what each step ran, its expected and observed result, and every fixture adjustment Step 2 needed. This record is written **last**, after Task 10's fix wave (CLAUDE.md § Editing discipline); draft it in the scratchpad until then.

---

### Task 10: Independent review and fix wave

- [ ] **Step 1:** Dispatch a fresh reviewer (Opus, read-only) over `git diff origin/main..HEAD` with the spec, this plan, `CLAUDE.md` § Editing discipline and the loaded rules files as its brief; ask for a SHIP / FIX FIRST verdict and findings with file:line and a concrete scenario.
- [ ] **Step 2:** Triage each finding per `workflows-core:finding-triage` (verify its claimed consequence at the location it names; keep or dismiss with a reason). Fix every kept finding, minors included — nothing known is deferred past this wave. Re-run Task 7's counts and Task 8's gate chain.
- [ ] **Step 3:** Re-review the fix wave with a fresh reviewer; repeat Step 2 until SHIP.
- [ ] **Step 4:** Write the verification record (Task 9, Step 7) with the values observed on the final tree, and commit it.
- [ ] **Step 5:** Stop and ask the user to approve the merge and push. After the push: comment on and close #73 and #74, naming the commits.

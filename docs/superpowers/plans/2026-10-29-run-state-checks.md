# Run-state checks — Implementation Plan (to-fix D18, D24, D26)

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (native). Steps use checkbox (`- [ ]`) syntax.

**Goal:** a run stops before its work where its branch is behind `main` for its folder (D24), asks before its work where its handoff would reuse an open branch (D18), and writes nothing into an environment it did not start in (D26).

**Architecture:** two shared entry points — `phase-handoff` §6 `branch-check` (its own generated entry-point file, so no run reads the whole reference for it) and `session-hygiene` §7 `env-check` (a load-by-part part) — plus one sentence in each of the 24 commands that resolve a folder, and a gate that keeps a new command from skipping it. Prose executed by agents; one gate in `scripts/reference-parts.py`.

**Spec:** `docs/superpowers/specs/2026-10-29-run-state-checks-design.md` (approved 2026-10-29). Where a sentence below and the design disagree, the design wins and the plan is the defect.

## Global Constraints

- Every git call is `git -C "$SPECS_PATH" …`; the run merges, switches and resets nothing on its own account (`phase-handoff` §1 rule 4), save §1.2's *Switch* answer.
- `<default-ref>` is the ref `specs-repo-git` §3.2 resolves for the run's preflight.
- `env-check` and every emitter stay **prompt-free** (`specs-repo-git` §1 rule 7); a mismatch sets `specs_git: misrooted`, which every consumer already honours.
- Choice arrays: 2–4 options, no "Other", presented verbatim (`workflows-core:escalation-rules` §0).
- Versions are computed at build time against `main` (D30 may land first and take `workflows-core` 1.70.0 and `dev-workflows` 4.53.0); every touched plugin gets a minor bump, a dated CHANGELOG section and its `marketplace.json` entry; one coupling bullet (a command calling `branch-check` needs the `workflows-core` that ships it), keeping `.claude/rules/plugin-updates-coupling.md` under 20,000 characters.

## Decision recorded at planning (not in the design)

- **`env-check` lives in `session-hygiene` as part §7, not in `specs-repo-git`.** The design named `specs-repo-git`; `session-hygiene` loads by part — so the four emitters and `handoff-to-main` load a few lines, not a whole large reference — and already owns §6's environment record, whose pinned values §7 compares against. The `Environment:` line itself is printed by `specs-preflight` (`specs-repo-git` §3), as designed.

## Review Focus

1. **Main changed only session files under the root since the branch was cut** — no stop (§1.1 excludes `specs-repo-git` §2.1's bookkeeping shapes). Pinned in Task 1.
2. **B3 kept the run on another unit's branch through a shared PRD key** — the stop's remedy is *switch to the default branch*, never *merge into their branch*. Pinned in Task 1.
3. **`/ready` on a behind branch** — recorded as a finding in its report, never a stop. Pinned in Task 4.
4. **A conversation with no `Environment:` line** (a run started before this release, or one whose preflight did not run) — `env-check` passes. Pinned in Task 2.
5. **The branch the handoff would reuse exists only as `origin/<name>`** — §1.2 resolves it as §2.2 rule 3 does, remote-tracking refs included, and asks. Pinned in Task 1.

---

### Task 1: `phase-handoff` §6 `branch-check`, its entry-point file, and §4.1's *switch refused*

**Files:** `plugins/workflows-core/references/phase-handoff.md`; `plugins/workflows-core/skills/reference/SKILL.md` (the *These entry points read their own file* sentence); `plugins/workflows-core/skills/reference/entry-files.md` (a *The file for `phase-handoff branch-check` holds …* sentence); generated `plugins/workflows-core/reference-parts/phase-handoff/branch-check.md`.

**Interface:** `Skill(skill: "workflows-core:reference", args: "phase-handoff branch-check")`, inputs `folder` (resolved, relative to `$SPECS_PATH`) and optional `prefix`; outcomes `pass`, `stop <finding>`, and — §1.2 only — the two-option question. Declared as `entry branch-check holds=1,2.2,6` in the H1 declaration block, with `<!-- entry: branch-check -->` region markers around §6.

- [ ] **§6.1 Behind**, as the design's §1.1 states it: applies only where HEAD is a plugin branch; root = the top-level folder under `specifications/` holding `folder`; paths = `git -C "$SPECS_PATH" diff --name-only "$(git -C "$SPECS_PATH" merge-base HEAD "<default-ref>")" "<default-ref>" -- "./<root>/"` **less** every path `specs-repo-git` §2.1's bookkeeping shapes name; any left → stop naming up to ten and how many more. Remedy by row B's ownership test: own branch → row B′'s merge remedy text with its `lift`, misrooted and read-only forms (reuse the text, do not restate a variant); another unit's branch → `switch to <default> ('git -C "$SPECS_PATH" switch <default>'), then re-run`. Say once that `/ready` records the finding instead (Task 4 wires it) and that a run with several roots runs §6.1 per root.
- [ ] **§6.2 Reuse**, as the design's §1.2: only with `prefix`; resolve the branch §2.2 rule 3 would reuse, remote-tracking refs included; where it exists, is unmerged (`branch-merged`, `specs-repo-git` §3.5), is not HEAD, and changed a path under the root since its fork, ask `choices: ["Switch to <branch> and continue there (Recommended)", "Stop — merge or close <branch>'s pull request first"]`; *Switch* switches (git's own refusal stops naming its paths) then runs §6.1 against it.
- [ ] **§4.1 outcome *switch refused*** and §1 rule 4 gaining `switch --discard-changes` and `switch -f`, as the design's §1.3.
- [ ] Declare the entry file; add `phase-handoff branch-check` to SKILL.md's sentence and its *holds* sentence to `entry-files.md`; run `python3 scripts/reference-parts.py generate`, then `check-parts` and `check-citations` → PASS.
- [ ] **Verify the git commands in a throwaway repository** (under the scratchpad): (a) branch cut, then `main` gains `specifications/PRD-X-1-a/EPIC-X-1-02-b/epic.md` → §6.1's command lists it; (b) `main` gains only `specifications/PRD-X-1-a/dev-workflows/feedback/…` and `follow-ups.md` → nothing left after the bookkeeping exclusion (Review Focus 1); (c) HEAD `spec/X-1-01-a`, run key set holding `X-1` and `X-1-02` → ownership test says *another unit's* → switch remedy (Review Focus 2); (d) `origin/epics/X-1-…` only, unfetched as a local branch, changed `specifications/PRD-X-1-a/` → §6.2 finds it (Review Focus 5). Record each command and its output in the commit message.
- [ ] Commit.

### Task 2: `session-hygiene` §7 `env-check`, the preflight's `Environment:` line, and its callers

**Files:** `plugins/workflows-core/references/session-hygiene.md` (new part `env-check`, alias `"§7"`); `plugins/workflows-core/references/specs-repo-git.md` (§3's preflight prints the line before its first act); `plugins/workflows-core/references/phase-handoff.md` §2.1 (runs `env-check` first); `feedback-emission.md`, `followup-emission.md`, `cost-emission.md` and `session-hygiene`'s `resume-pointer` part (each runs `env-check` as its first step); generated parts.

**Interface:** the line `Environment: SPECS_PATH=<realpath> (origin <url, or none>), REPOS_PATH=<value, or unset>`; `Skill(skill: "workflows-core:reference", args: "session-hygiene env-check")` — prompt-free; compares the three live values with the last `Environment:` line the run printed; a difference sets `specs_git: misrooted` and prints `Environment changed: started in <old>, now <new> — this run writes nothing here; re-run in the container it started in.`; no line in the conversation → pass (Review Focus 4); a run §6 pinned compares against its pinned values.

- [ ] Write §7 and its part markers; the preflight sentence; the five callers' first-step sentences, each citing `session-hygiene env-check` the way they cite their other references.
- [ ] `python3 scripts/reference-parts.py generate`, `check-parts`, `check-citations` → PASS.
- [ ] Commit.

### Task 3: the gate — `reference-parts.py check-branch-check`

**Files:** `scripts/reference-parts.py` (subcommand and `--selftest` cases); `.github/workflows/validate-catalog.yml` (a step after `check-questions`); the scratchpad's `gates.sh` and `gates-nonode.sh` (the same step, so local runs match CI); `.claude/rules/gates-reference-parts.md` (what the check enforces and cannot see).

**Interface:** `python3 scripts/reference-parts.py check-branch-check` → `PASS -- N command(s) run branch-check` or one `FAIL <file>: <reason>` line per failure, exit 1. Rules: (1) every `plugins/*/commands/*.md` that names `resolve-address` executes `args: "phase-handoff branch-check"`; (2) every one of those that also executes `handoff-to-main` passes `prefix:` in that call, save the exempt set `EXEMPT_PREFIX = {"implement", "update-spec"}`, declared in the script with a one-line reason each.

- [ ] Selftest first: a command with `resolve-address` and no `branch-check` → FAIL; with both and a `handoff-to-main` but no `prefix:` → FAIL; the same named `implement.md` → PASS; with neither → not counted. Run `--selftest` → those cases FAIL before the subcommand exists.
- [ ] Implement; `--selftest` → PASS; `check-branch-check` on the tree now → FAIL listing all 24 commands (Task 4 fixes them).
- [ ] CI step, local gate scripts, rules entry. Commit.

### Task 4: one sentence in each of the 24 commands

**Files:** each command `grep -l resolve-address plugins/*/commands/*.md` lists (24 today; re-derive). The sentence, placed after both the preflight and the address resolution — whichever comes second — and before anything reads the resolved folder's contents:

> **Check the branch the run stands on.** Execute `branch-check` (`Skill(skill: "workflows-core:reference", args: "phase-handoff branch-check")`, §6) on the resolved folder[, with `prefix: <p>`]; a stop it makes ends the run here.

- [ ] **Prefixes**: `design`, `conformance`, `ready`, `idea`, `prd` (`/release-notes`, `/update-prd`, `/prd-proposal`, `/create-prd`), `brd` (`/brd-proposal`, `/brd-intake`, `/brd-interview`, `/brd-package`, `/brd-split`), `frames`, `spec` (`/specify`), `epics`, `ard`; `/prd-ground` passes the prefix of its route (`brd` on a slice, `prd` on the idea route). **No prefix**: `/vuln`, `/security-workflows:scan`, `/document` (no specs handoff), `/implement` and `/update-spec` (exempt by the design).
- [ ] **Placements that differ**: `/specify` on a PRD address runs §6.2 after its Step A pick, §6.1 at Phase 0; `/brd-reconcile` passes its first handoff's prefix only; `/vuln` and `/brd-reconcile` run it once per distinct root; **`/ready`** records a §6.1 stop as a finding beside the stopping rows its Phase 0 step 3 *Proceed anyway* already records (Review Focus 3), naming `phase-handoff` §3.7.
- [ ] `check-branch-check` → PASS; `check-citations`, `check-questions` → PASS. Commit.

### Task 5: sweep, docs, release, gates, review, PR

- [ ] **Claim sweep** (`.claude/rules/claim-sweep.md`, refinements 4–8): sentences saying a run on the default branch is always level; that `handoff-to-main`'s gate compares nothing with the run's start; D18's "git's advice" remedy; any description of what the preflight prints (it now prints a line every run) — `specs-repo-git` §3's *silent unless it acts* among them; `session-hygiene` §6's claim to be the only resume check. Count each changed phrase before and after.
- [ ] **Docs**: `plugins/workflows-core/docs/reference/references.md` (`phase-handoff`, `session-hygiene`, `specs-repo-git` lines), and each command docs page whose *Synopsis* or *How it runs* lists its Phase 0 steps.
- [ ] **Release** per Global Constraints; remove D18, D24 and D26 from `docs/superpowers/to-fix.md`.
- [ ] `bash <scratchpad>/gates-nonode.sh` from the worktree → `EXIT=0`. Commit.
- [ ] Independent Opus review of the branch, with this plan's Review Focus verbatim; fix; re-review the delta until clean; push; PR.

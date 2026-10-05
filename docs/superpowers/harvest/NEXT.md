# Harvest status pointer — dev-workflows upstream harvest

> **Removed from the tree 2026-09-23:** every design spec and plan this record cites under `docs/superpowers/specs/` or `docs/superpowers/plans/` (the one exception being `docs/superpowers/specs/2026-09-22-claude-md-split-design.md`, which stays). Each is still retrievable at its cited path with `git show 62e791e8:<path>`.

## COMPLETE & SHIPPED (2026-07-29)
The 8-item harvest (freebie + Tier 1 + Tier 2) is implemented, reviewed, and **merged to `main` + pushed**
in all three editions:
- `ihudak-claude-plugins` (canonical) — `main` at `b9cfd38`; dev-workflows **2.38.0**. Passed the opus
  whole-branch review (Ready-to-merge: YES; 4 Minors fixed in `dab042c`).
- the internal edition — `main` at `dd39786`; dev-workflows **2.38.0** (byte-identical copy of canonical).
- `ihudak-copilot-plugins` — `main` at `e4e3703`; dev-workflows **2.8.0** (hand-adapted conversion:
  `~/.copilot/…/skills/_shared/` paths, `implement:`/`design:` keywords).

What shipped: spec→code **converge** gate (code-review 10th dim + risk-planner ID-tags + /implement
wiring), `bug-diagnosis.md` discipline, test-writer falsifiability/mutation gate, review-fixer
plan-conflict, code-review Fowler floor, altitude-aware ambiguity taxonomy + "design tree"→"decision
tree" rename, deep-module/seam vocab, risk-planner no-placeholders, VI counter-metrics. Spec + plan:
`docs/superpowers/specs|plans/2026-07-29-dev-workflows-upstream-harvest*.md`. Do NOT redo any of this.

## Wave 3 — SHIPPED (2026-08-01; NIT follow-up 2026-08-02)
Five deferred nuggets + the cheap half of the Adjacent item shipped to all three editions. Current tips:
canonical `72bb7ae` (**2.39.1**), internal `5478b74` (**2.39.1**), Copilot `9fca4db` (**2.9.1**) — the `.1`
patch was a whole-branch-review NIT follow-up (`context-management.md` 4th-strategy summary consistency);
wave-3 base was 341b5df/557526b/fa25405 (2.39.0 / 2.9.0). Spec + plan:
`docs/superpowers/specs|plans/2026-08-01-dev-workflows-deferred-nuggets*.md`. What shipped: ADR
3-condition candidacy filter (`ard-format.md`), wide-refactor expand→migrate→contract exception
(`epics.md`), prototype-snippet exception (`design-format.md`), missing-adoption gap (`code-review.md`
dim 4), `resume.md` redaction reminder (`session-hygiene.md`), and the context "hand off by file, not
paste" 4th strategy (`context-management.md`, **reference-only**). Also **fixed** a pre-existing `/idea`
+ `/create-vi` YAML-frontmatter bug (a colon-space in the unquoted `description:` silently dropped all
frontmatter at runtime). Passed the Opus whole-branch review (READY; 3 minors fixed). Do NOT redo.

## Wave M (the `/implement` dispatch file-handoff) — SHIPPED (2026-08-02)
The deferred M item shipped to all three editions. Current tips: canonical `5d8f56c` (**2.39.2**),
internal `f2d0ac3` (**2.39.2**), Copilot `2de7eb2` (**2.9.2**). Spec + plan:
`docs/superpowers/specs|plans/2026-08-02-implement-dispatch-file-handoff*.md`. What shipped: extended
the existing `/document` + `/epics` `mktemp` handoff pattern to `/implement`'s four in-loop dispatches
(`risk-planner`, `test-writer`, `code-review`, `review-fixer`) plus the Phase 3.5 sibling — the
multi-source summary, approved plan, review diff, and code-review report are written to `mktemp` files
(outside every repo tree → no `git diff` pollution) and handed as absolute **paths**, not pasted
inline; each agent's `## Inputs` notes a field may arrive inline or as a path. Behavior-preserving
(Design A, surgical per-artifact). Passed the Opus whole-branch review (READY WITH MINORS; both fixed —
the re-review paths now refresh `review_diff_file`, and a review-fixer note period). Do NOT redo.

## Wave S (the `/vuln` + `/upgrade` dispatch file-handoff) — SHIPPED (2026-08-02)
The S follow-up shipped to all three editions. Current tips: canonical `04e51f4` (**2.39.3**),
internal `e1a7ab5` (**2.39.3**), Copilot `d7ad4b3` (**2.9.3**). Spec+plan (one doc):
`docs/superpowers/specs/2026-08-02-vuln-upgrade-dispatch-file-handoff-design.md`. What shipped: the
`/vuln` research report (→ `vuln-fixer`, `code-review`, resumes) and the `/upgrade` planner handoff
(→ `risk-planner`, `upgrade-executor`, resumes), plus each command's `code-review` `git diff`, are
written to `mktemp` files (outside every repo tree → no `git diff` pollution) and handed as absolute
**paths**; `vuln-fixer` + `upgrade-executor` `## Process` note a field may arrive inline or as a path.
Behavior-preserving. Passed the Opus whole-branch review (READY WITH MINORS; all fixed — the
`/upgrade` regression-resume `plan_file` gap + 2 NITs). Do NOT redo.

## Review-fix wave — SHIPPED (2026-08-02; committed + pushed)
An independent whole-branch review of the last 10 days across all three editions found 9 defects in
the shipped waves and fixed them: canonical/internal **2.39.4**, Copilot **2.9.4**. Two were functional:
(1) the `/vuln` + `/upgrade` post-`review-fixer` re-review re-used the *pre-fix* `review_diff_file`
(the `/implement` correction from the 2.39.2 follow-up was never carried into the 2.39.3 siblings), and
(2) `/implement`'s two `test-writer` dispatches embedded the `mktemp` + `git diff` capture **inside**
the agent-facing prompt unbracketed — `test-writer` has no `Bash`/`bash` tool, so it could not comply
(now an orchestrator step recorded as `test_diff_file`). The rest: dispatch brackets holding
instructions instead of values (`/vuln` ×2, `/upgrade` ×1), `/vuln`'s SIMPLE/MODERATE
regression-resume left on "verbatim", `context-management.md` missing the load-bearing
"`mktemp` outside every repo working tree" guard, both `handoff/` docs describing the report/plan as
inline-only, the `risk-planner` ID example in `[AC-3]` instead of `[AC03]` form, and — Copilot only —
two long-standing conversion gaps: the never-ported `phase: regression-resume` directive in
`vuln-fixer` + `upgrade-executor`, and 16 Claude tool names (`Read`/`Write`/`Glob`/`Grep`/`LS`) in
prose that edition never grants. Verified: `claude plugin validate` clean (both Claude repos),
canonical↔internal byte-identical outside the 5 expected files, handle counts match canonical↔Copilot.
Both this wave and the pre-existing-issue wave below were squashed into one commit per repo and
pushed: canonical `2d20bd2`, internal `4b78b34`, Copilot `2b54f94`.

## Pre-existing-issue wave — SHIPPED (2026-08-02; committed + pushed)
Same session, after the user asked for older defects too. Six more, all older than the reviewed window:
- **Dead `LS` tool entry** in every `allowed-tools` / `tools` list (50 dev-workflows files per Claude
  edition + the internal docs plugin's spec-planner + the `/ready` prose). Verified against the shipped Claude Code
  **v2.1.218** binary: zero occurrences of `"LS"`, and the legacy alias map is
  `{Task:"Agent", KillShell:"TaskStop", KillBash:"TaskStop", AgentOutputTool:"TaskOutput", …}` with no
  `LS` entry. Unmatched entries are dropped silently, so the lists worked — but a `tools` list whose
  entries *all* fail to match makes the Agent tool refuse to launch. **`Task` was kept** — still a live
  alias for `Agent`.
- **Stale `/impl:jira:docs` / `/impl:jira:epics` / `/impl` / `/impl:docs` command names** plus a
  non-existent "Phase 6.7", in the predecessor style plugin's `README.md` + its style-checker agent (all three
  editions) and the internal docs plugin's processing command. Corrected to `/document` (Jira mode)
  **Phase 6.4** and `/epics` **Phase 6.2**, with the mechanism restated accurately (`docs-style-checker`
  runs the primary linter *and* `prose-style-checker` internally, merging both finding sets).
- Copilot marketplace: `obsidian-llm-wiki` entry had no `homepage` (only entry missing it).
- Copilot manifests: "Thirty-one dispatched sub-agents" and a `README.md` tree saying "30 sub-agents"
  where there are 32.
- `plugins/acli/plugin.json` `"skills": ["./skills"]` removed — the default `skills/` scan is always
  performed and the `skills` field only *adds* to it, so the entry registered the directory twice and
  diverged from every sibling plugin.
- internal `dev-workflows/README.md` agent-table row order realigned to canonical (`idea-reader`).

Versions: dev-workflows **2.39.4** (canonical+internal) / **2.9.4** (Copilot); the predecessor style plugin **0.2.4** /
**0.3.3**; acli **0.1.1** (Claude); the internal docs plugin **0.1.1**. All `claude plugin validate` clean; all 12
marketplace↔plugin.json versions in sync; canonical↔internal dev-workflows byte-identical outside the 5
expected files. Committed and pushed together with the review-fix wave above (canonical `2d20bd2`,
internal `4b78b34`, Copilot `2b54f94`).

### RETRACTED finding — do not "fix" this
An earlier pass in this session flagged "18 unconverted `/slash-command` names" in the Copilot
`skills/_shared/docs-grounding.md`, `agents/docs-grounder.md`, and `skills/upgrade/README.md`, and by
extension the ~126 `/wiki-*` and ~20 of the predecessor style plugin's command names in the other Copilot plugins' READMEs. **That was
wrong.** Copilot CLI registers every user-invocable loaded skill as a slash command — verified in the
CLI 1.0.74 bundle: `getLoadedSkills().filter(n=>n.userInvocable && …).map(n=>({name:`/${…}`, isSkill:!0,
skill:n}))`. `/wiki-init`, the predecessor style plugin's PR-review command, and `/idea` are all valid invocations there. The dev-workflows
edition additionally documents a keyword form (`idea:`) via each skill's description; both work. Left
untouched deliberately.

**Copilot tool-name convention (verified against the shipped CLI, 1.0.74):** this edition declares the
CLI's own concrete tool names (`view`, `glob`, `grep`, `bash`, `create`, `edit`, `task`, `web_fetch`),
confirmed in the CLI bundle (`R_="view"`; `grepToolName??"grep"`, `globToolName??"glob"`,
`shellToolName??"bash"`; `["str_replace_editor","create","edit","insert","apply_patch"]`). GitHub's
`custom-agents-configuration` docs additionally define a portable *alias* layer
(`read`/`edit`/`search`/`execute`/`agent`/`web`/`todo`, case-insensitive, with `Read`/`Write`/`Grep`/
`Glob`/`Bash`/`Task` as compatible aliases). Both work on the CLI; the concrete names are kept for
consistency across all 32 agents. Switch to the alias layer only if this edition ever needs to run on
GitHub.com cloud agent or in an IDE as well.

**`acli` is intentionally opensource-only** (confirmed 2026-08-02): the internal edition uses the
PII-scrubbing variant built on an internal CLI proxy, which cannot ship in a public repo — so the
opensource marketplaces carry plain `acli` instead. The 1:1 ihudak→internal rule does **not** apply to this
plugin; do not "fix" the absence.

## Audit-residue + branch-naming wave — SHIPPED (2026-08-04; committed + pushed)
A full re-audit of every plan/design in `docs/superpowers` against the shipped plugins, plus a
three-edition port-parity sweep, found **zero functional gaps** — every plan, design, and recorded
deferral traces to a shipped artifact, all 12 marketplace↔plugin.json versions were in sync, and
`claude plugin validate` passed. Seven cosmetic residues were found and fixed:
- **Two dead `LS` tool names** the 2.39.4 sweep missed, in inline Agent-dispatch prose
  (`commands/document.md` Phase 10, `commands/implement.md` Phase 2A) — canonical + internal only; the
  Copilot edition already read `view/glob/grep`. → folded into dev-workflows **2.40.0**.
- **Copilot `skills/_shared/branch-naming.md` was documented but never wired.** The `$GIT_USER_INITIALS`
  prefix ladder had shipped since Copilot 1.6.0 and both `README.md` and the CHANGELOG described it as
  live policy, but no skill loaded it — every branch-creating workflow silently used its own inline
  `git branch -a` sniff, so the env var had no effect. **An earlier pass in this session deleted the
  file as dead; that was wrong** — the user relies on the feature. Instead it is now genuinely wired
  into all five branch-creating orchestrators in **all three editions**, and promoted to a first-class
  feature: new canonical/internal `references/branch-naming.md`, consumed by `/implement`, `/document`
  (both modes), `/docs-profile`, `/upgrade`, and `/vuln` (via `vuln-fixer`). Two latent defects in the
  policy fixed at the same time: §1.3 inference rejected **hyphenated** initials (`^[a-z0-9]+$` vs
  §4's `[a-z0-9-]`), so `iv-gu/…` branches were invisible to it; and §1.5's mandatory
  "no prefix detected" prompt was never implemented — now registered in `escalation-rules.md` as
  "Branch prefix undetected". `/docs-profile`'s ad-hoc `git config user.name` initials derivation was
  replaced by the shared ladder. `GIT_USER_INITIALS` is now documented in both repo-root READMEs.
  → dev-workflows **2.40.0** (canonical + internal) / **2.10.0** (Copilot) — MINOR, not PATCH.
- **The internal edition carried two stray plugin-embedded planning docs** (`plugins/dev-workflows/docs/{plans,specs}/
  2026-07-17-update-vi-*`) with no canonical counterpart. `git mv`-ed to the internal edition's repo-root
  `docs/superpowers/`, restoring strict plugin 1:1. Canonical's empty `plugins/dev-workflows/docs/`
  tree removed too.
- **28 design docs carried pre-implementation `Status:` headers** (`pending implementation`,
  `approved-for-planning`, `awaiting spec review`, …) though the features verifiably shipped. Each now
  reads `Shipped in dev-workflows v<X.Y.Z> — pre-implementation design snapshot, kept as authored`,
  with the version cross-checked against the CHANGELOG entry that introduced it (two, where no version
  could be pinned with evidence, say `Shipped` without one). Bodies untouched.
- **This file claimed the last two waves were uncommitted with pushes held** — they were committed and
  pushed on 2026-08-02; corrected above.
- **Copilot `wiki-tags-refresh` omitted its `[directory]` argument** from the invoke line (the body
  already scanned it) and had lost the `-print0` rationale note. → obsidian-llm-wiki **0.3.4**.
- **Dangling tracker pointer `dev-workflows-next-efforts`** (a memory that does not exist) in
  `2026-07-07-two-key-grammar-foundation-design.md` ×2 and `2026-07-07-design-command.md` ×1 →
  repointed at `docs/superpowers/harvest/NEXT.md`, which superseded it.

Verified: `claude plugin validate` clean (both Claude repos), all 12 marketplace↔plugin.json versions
in sync, canonical↔internal dev-workflows byte-identical outside the 5 expected files, zero `LS` outside
CHANGELOG history, and `branch-naming.md` reachable from all five branch-creating orchestrators in all
three editions (grep-proven, no orphan). Passed an independent whole-branch review over all three
diffs (READY TO MERGE; 10/10 hard invariants PASS, 2 NITs fixed — the `[a-z0-9-]` first-character
restriction is now stated in §1.5/§4 and `escalation-rules.md`, and §2's `implement`/`document`
doc-edit slug rule was aligned with the commands' own wording). **Merged to `main` + pushed.**

## Branch-naming repo-rule-first wave — SHIPPED (2026-08-04; committed + pushed)
The 2.40.0/2.10.0 branch-naming feature had the priority backwards. It made the `$GIT_USER_INITIALS`
ladder the **primary** mechanism, while only `/document` and `/docs-profile` ever read the target
repo's own documented convention — so `branch-naming.md`'s claim that a repo-documented pattern
"outranks this ladder" was **unenforceable** in `/implement`, `/upgrade`, and `/vuln`, which never read
those files. (Same class of defect as the orphaned Copilot file it replaced: policy documented, not
wired.) The user's intent: the repo's own `CONTRIBUTING.md` / `README.md` rule is the source of truth,
and initials fill an identity placeholder **only where the rule has one** — as the organisation's docs repo does
(`<your-name-or-initials>/<JIRA-ISSUE-KEY>-<short-branch-name>`, `CONTRIBUTING.md` §Branch name).

Inverted and closed in all three editions: every branch-creating orchestrator now reads the repo's
guidance files **first** (§1.1), classifies the documented pattern's segments (§1.2), and fills each
from its proper source — identity from the ladder (now §2), issue key from the run's resolved Jira key,
description from each command's own slug rule (§3). A pattern with **no** identity segment never gets
one (a `feat/<slug>` repo still yields `feat/add-oauth`, not `iv-gu/…`); identity inference ignores the
generic prefixes; and the §2.5 escalation drops its generic-fallback choice when an identity is being
filled. The ladder supplies the whole prefix only when a repo documents no convention at all (§1.4).
`/implement` prefixes a resolved Jira key to its slug when the chosen shape has no key segment.
Passed an independent whole-branch review (READY TO MERGE; 12/12 criteria PASS incl. an end-to-end walk
of the organisation's docs-repo case → `iv-gu/PRODUCT-17753-add-oauth`, and the no-identity case → `feat/…`;
1 NIT fixed — `DOCUMENTATION-GUIDELINES.md` added to canonical `/vuln` + `/upgrade` inline lists for
cross-edition parity). Versions: dev-workflows **2.41.0** (canonical + internal) / **2.11.0** (Copilot).

## Harvest round 2 — "verify what you assert" — SHIPPED (2026-08-21; merged 2026-08-22)
Second harvest from the same four upstreams (BMAD-METHOD, github/spec-kit, obra/superpowers,
mattpocock/skills), surveyed against the 2026-07-29 baseline. 383 upstream commits in the window; four
Tier-1 items adopted, all converging on one rule stated once and applied at three stations: **do not
act on, report, or accept a claim you have not verified against the thing it names.** Spec + plan:
`docs/superpowers/specs/2026-08-21-upstream-harvest-round-2-design.md` and
`docs/superpowers/plans/2026-08-21-upstream-harvest-round-2.md`.

What shipped on the branch (all three editions — canonical authored, internal ported, Copilot hand-adapted):
- **Item 1 — the read-failure contract** (`references/context-management.md`, new `## The read-failure
  contract` section). Every input a caller may hand over "inline or as an absolute file path" resolves
  into one of two tiers, fixed by the consuming agent where it takes that input, never at runtime:
  an unreadable **evidence** input is a hard stop that is **never** regenerated by other means (a resume
  that re-derives its own input is the failure the contract exists to prevent); an unreadable **context**
  input degrades to absent and the output records the degradation. Stated by six agents — `risk-planner`,
  `code-review`, `test-writer`, `review-fixer`, `vuln-fixer`, `upgrade-executor`. `status: BLOCKED` is
  consumed on the `/vuln` and `/upgrade` resume paths; `/implement` states `NEEDS HUMAN` at the call site.
- **Item 2 — orchestrator triage** (new `references/finding-triage.md`). Between an Opus reviewer's
  findings and a fixer's edits: verify each finding's own claimed consequence at the location it names,
  keep or dismiss, record every dismissal with a reason that disposes of that finding's own claim, hand
  the fixer survivors only. Run by the **orchestrator**, never the fixer — a dismissal must not sit at a
  weaker station than the Opus reviewer that produced the finding. Carries the patch gate (never a fix
  that guards state the finding did not demonstrate) and a reporting contract (a triage that reports only
  survivors is indistinguishable from a reviewer that found less). Wired into all five reviewer-fed paths
  — `/implement`, `/vuln`, `/upgrade`, `/document` (Jira mode), `/epics` — plus a `### Review triage`
  report section in each, and patch gates in `review-fixer` + `doc-fixer`. **Never** attaches to a
  style-checker-fed `doc-fixer` dispatch: a linter violation is not a claim about consequence.
- **Item 3 — claims falsification.** `code-review`, `doc-reviewer`, and `epic-reviewer` each gained an
  optional `claims_file` input and a final conditional dimension read **only after every other dimension
  is complete** — the deferral is what makes the falsification independent, and it is bought structurally
  (a path, read late) rather than by instruction. Dimension counts 10→11, 17→18, 18→19. Wired in five
  commands; in `/vuln` and `/upgrade` the fixer/executor output was **relocated** out of the inline
  review brief so it is named once, as `claims_file` — content left in both places would defeat the
  deferred read while appearing to implement it.
- **Item 4 — instruction-file maintenance** (new `references/instruction-file-maintenance.md`), cited by
  `impl-maintenance` and binding on hand edits: verify every command claim against the thing that runs
  it; a rewrite that narrows a rule is a deletion and is itemised separately; a pointer names an
  observable trigger, never one the agent must judge; two live contradictory instructions is a defect;
  retirement needs grounds, never "it looks derivable" and never "nothing has failed on it lately".

Also corrected en route (pre-existing drift, deliberately bounded — §10.3): the README agent table
claimed `code-review` had 8 dimensions (it already had 10) and `epic-reviewer` 9 (it already had 18).

**State as of this entry — read before assuming anything is done:**
- All 12 plan tasks are complete, and the final whole-branch review's fix wave (2 Critical, 2 Important,
  7 Minor) is applied in all three editions.
- **Ported.** All three editions are built on branch `iv-gu/upstream-harvest-round-2`: canonical
  (authored), internal (byte-identical to canonical outside the five identity files), Copilot (hand-adapted —
  never `cp`; and its `epic-reviewer` README row carries **no** dimension count, so do not import
  canonical's).
- **Versioned.** dev-workflows **2.54.0** (canonical + internal) / **2.24.0** (Copilot) — all six
  `plugin.json` / `marketplace.json` files carry it, and every edition's `CHANGELOG.md` has the entry.
- **Merged and pushed** in all three repos on 2026-08-22. Canonical `0f51443` and Copilot `8d2885f`
  merged directly; internal went through **PR #1** (`6db9e9c`) rather than a direct push, because
  the internal edition's repository requires PRs on `main` and the account's bypass privilege
  would have skipped the org's review gate on a shared internal repo. Prefer the PR route there again.
- **Two Criticals were found by the final whole-branch review, after every per-task review had passed.**
  Both lived in the *seam between two tasks*, which no single task's diff contained: the triage step's
  survivor list never reached the fixer (while the fixer had just been told it may not dismiss
  anything — this would have left the plugin **worse** than the branch point), and `review-fixer`'s
  `NEEDS HUMAN` stop was consumed only by `/implement`, not by its `/vuln` and `/upgrade` siblings —
  the 2.39.2→2.39.3 precedent repeating inside the round that adopted the rule against it. Cross-cutting
  review is not redundant with per-task review; it is the only thing that sees seams.
- **Twenty-two defects in the round's own plan were found and fixed during execution; none shipped.**
  Eleven were broken verification patterns — wrong inflection, wrong case, wrong file, wrong code-span
  shape, a working-tree comparison that passed vacuously, a check that halted on a healthy tree, and a
  `cp` that destroyed the very identity file its own task forbade copying. Two would have required
  damaging correct content to satisfy. The recurring root cause: **a verification pattern written
  against an imagined file reports on the imagined file.** Derive every expected value from the tree in
  front of you, and when a check disagrees with the tree, suspect the check first.

## Harvest round 3a — items 5 + 7 — SHIPPED, all three editions, merged (2026-08-22)
> Label corrected 2026-08-22: this round was written while it was still on a branch and canonical-only.
> It merged (`98b58e7`) and was ported — canonical/internal `2.55.0`, Copilot `2.25.0`.
Items 5 and 7 taken as one small bounded round; item 6 (design-it-twice) deliberately left for its own
architectural cycle, because it adds a parallel sub-agent fan-out to `/design` with its own gate, cost
story, and `design-reviewer` implications — bundling it with two additive hardening items would either
rush it or stall them.

**Item 7's second half is DROPPED, and this is the reason — do not re-derive it as a gap.** The
upstream rule says a reviewer must return findings as text and never route them through a
findings-reporting tool the host may offer. In these editions that rule can never fire: all eight
gating reviewers (`code-review`, `doc-reviewer`, `epic-reviewer`, `vi-reviewer`, `ard-reviewer`,
`spec-reviewer`, `design-reviewer`, `readiness-reviewer`) declare `tools: ["Read", "Glob", "Grep"]`, so
no such tool is in reach. Adding it would be a rule stated, counted, and never executed — the exact
class round 2 closed — and round 2's own patch gate forbids a fix that "guards no state the finding did
not demonstrate". If a reviewer's tool list is ever widened, revisit this.

**A rationale correction worth keeping.** The dispatch bound on the three `Task`-holding agents was
nearly justified as "review arrives from the caller, so a self-spawned reviewer duplicates that seat".
That is **false on half the paths**: `/document` direct mode runs no `doc-reviewer` at all
(`CLAUDE.md` — "deliberately lightweight"), and the SIMPLE / MODERATE paths of `/vuln` and `/upgrade`
run no `code-review`. The rule ships instead on **authority**: the caller owns the gate policy, the
absence of a reviewer on the light paths is a deliberate design choice, and a worker that spawns its
own reviewer silently overrides that choice while producing a verdict nobody consumes. True on every
path.

## Harvest round 3b — item 6 — SHIPPED, all three editions, merged (2026-08-22)
Canonical `b456ceb` and Copilot `0a79666` merged directly; internal went through **PR #3** (`0847555`),
the same route PR #1 took, because the internal edition's repository requires PRs on `main`.
Versions: canonical/internal `2.56.0`, Copilot `2.26.0`. The `interface-designer` agent, the
three-take Phase 5 fan-out in `/design` with `--design-twice` forcing it, `design-format.md`'s
unconditional `### Alternatives considered` and its four dependency categories, and `design-reviewer`'s
two new checks. Plan: `docs/superpowers/plans/2026-08-22-design-it-twice.md`; spec:
`docs/superpowers/specs/2026-08-22-design-it-twice-design.md`.

## Post-round review wave — 2.56.1 + 2.56.2 — SHIPPED & MERGED (2026-08-22)
A comprehensive review of rounds 2 → 3b along three axes — every agent's tool grants, every
producer→consumer data path, and the plan/design docs — found **four** live defects, all fixed and
merged in all three editions. **2.56.1** (canonical `882a200` / internal PR #4 `664ea98` / Copilot
`96607d3`) carried the first three; **2.56.2** (canonical `64b8dae` / internal PR #5 `566a7de` / Copilot
`73d4cb9`, Copilot **2.26.1**→**2.26.2**) carried the fourth, which this entry had briefly recorded as
"left as-is" before the bugs-first policy was applied to it.

- **`doc-fixer`'s `NEEDS HUMAN` stop had no consumer anywhere** (since 1.1.0). Its own hard rules say the
  caller "reads it to decide whether re-running the review is worth doing" and "must surface the deferred
  BLOCKERs to the user and stop the automated cycle" — and `grep -c 'Stop condition'` returned **0** in
  `/document`, `/epics`, and both Copilot skills. Three sites closed. `/epics`' style cycle deliberately
  gets none: `prose-style-checker` caps at `MAJOR`, so the flag cannot fire there — `doc-fixer.md` now
  records that reachability map so the absence is not later "fixed" into an unreachable guard.
  **2.54.0 fixed this exact class for `review-fixer`** across its three callers, then scoped the sweep to
  `review-fixer` and never asked whether the plugin's *other* fixer emitted the same flag. It did. Round 2
  also *added* a defer path to `doc-fixer` (the patch gate), raising the flag's firing rate against a
  consumer that was never there.
- **A `code-review` `BLOCK` from an unreadable diff was indistinguishable from a substantive one.** It now
  carries the literal first-line marker `Diff: unreadable at <path>`, mirroring `test-writer`'s, checked
  by all three code commands before triage. The plugin already handled the three sibling cases in these
  exact words — an orchestrator bug, not a user choice — for `test_diff_file`, `research_file`, and
  `plan_file`; `review_diff_file` was the fourth and the only one left out. `finding-triage.md` states the
  marker's exception, so the new rule does not contradict its own table.
- **`/design`'s `model_routing` `detection_model` comment read `# code-scanner`** while three agents route
  on that chain (`code-scanner`, `interface-designer`, `impl-maintenance`).

- **`api-guideline-reviewer` declared an unused `Bash` grant** (2.56.2). It reviews OpenAPI specs by
  reading them, names no executable, and `references/api-guidelines/` holds only markdown and a YAML
  template. Every other read-only reviewer declares `["Read", "Glob", "Grep"]`; every other `Bash` holder
  either uses it or bounds it explicitly. Its sibling `guideline-reviewer` keeps `Bash` — it really does
  run `references/guidelines/check_guidelines.py` — so the pair now diverges at the agent level for a
  real reason. Both commands' `allowed-tools` left unchanged: each is a thin dispatcher and the pair
  declares an identical set, so narrowing them would be speculative.

**What the review found clean.** No agent is instructed to do anything its tool grant forbids; every
`Bash` grant is bounded or used — `api-guideline-reviewer`'s was neither, and the unused grant was
dropped in **2.56.2** rather than carried (bugs-first). All counts re-derived rather than trusted: `code-review` 11, `doc-reviewer` 18,
`epic-reviewer` 19, nine Opus pins, thirty-four agents in twelve places across three editions.
`--design-twice` documented in all six required places in all three editions. Copilot dialect clean on
all four rules. One candidate finding was **withdrawn** on inspection — `/implement`'s PWR branch looked
like it never read `review-fixer`'s `NEEDS HUMAN`, but `implement.md:496` scopes the plan-conflict
handler to "BLOCK **and** PASS WITH RECOMMENDATIONS", and a deferred-BLOCKER `NEEDS HUMAN` cannot occur
on a PWR verdict. Reporting it would have been the unreachable-guard class this same review flagged.

**The class-sweep was then run, and found nothing further.** 2.56.1's lesson — when a fix is "wire up
X's unread signal", the axis is *every producer of that kind of signal*, not every caller of X — was
applied as a check: all 23 status enums and stop flags across the 34 agents enumerated, producers diffed
against consumers. Both `Stop condition flag` producers now have all five consumers. Eleven statuses
showed zero command-side branches; every one was chased and cleared. Most are `test-baseliner` statuses
the agent *reads* rather than emits. The genuine returns — `BUILD_FAILED`, `BASELINE_FAILED`, `REVERTED`,
`TEST_REGRESSION_KEPT`/`_REVERTED` — are **not** the dead-gate class: neither agent states a caller
obligation, each has already resolved the state before returning, and `references/handoff/*.md` declares
the full enum with per-status meanings feeding the results table. The four agents with no `## Output`
section are exactly those four, for exactly that reason. **Zero known open defects.**

**Verification discipline used:** every check was shown to return 0 on the pre-fix tree (`b456ceb`) and
non-zero after — nine checks, none vacuous. The three rounds' dominant defect was a verification pattern
written against an imagined file, so a check that cannot go red proves nothing.

## The 2026-08-21 survey — all three items now closed
> **Nothing in this section is live backlog any more.** Items 5 and 7a shipped in round 3a above; item 7b
> is dropped there with its reason; item 6 shipped in round 3b above. The three entries below are kept
> as originally written so the survey record stays intact — read them as history, not as work to pick up.
These three were surveyed on 2026-08-21 and **deliberately left out of round 2**, for one reason only:
round 2 was scoped to a single discipline — verify what you assert — and these three are a different
kind of change. They were **not** considered and rejected, they are **not** covered by anything round 2
shipped, and they are not on the "Rejected on merits" list below. A later round must not read their
absence as a verdict. Source: round-2 design §1.1 and §12.

- **Item 5 — `references/bug-diagnosis.md` has drifted from its mattpocock source.** Missing a
  `## Redact` section, and missing the completion criterion "name one command you have already run, and
  show its output".
- **Item 6 — "design it twice" for `/design`.** Three parallel sub-agents under different interface
  constraints, compared on depth / locality / seam placement; plus `DEEPENING.md`'s four dependency
  categories for `design-format.md`'s `## Seams`. **SHIPPED in round 3b** (canonical/internal `2.56.0`,
  Copilot `2.26.0`).
- **Item 7 — subagent-dispatch bounds** for the three agents that hold `Task` (`docs-style-checker`,
  `upgrade-executor`, `vuln-fixer`), and the Claude-only half: reviewers must return findings as text,
  never through a host findings-reporting tool.

### Recorded upstream divergences — decisions, not gaps (2026-08-21)
Both are deliberate. Do not "resync" either one without a fresh decision.
- **superpowers has reversed the plan-conflict rule** this plugin imported from it in July
  (`review-fixer`'s `DEFERRED — plan-conflict`), in favour of "rule and record". We keep our version:
  our commands run with a human present.
- **mattpocock's `grilling` has moved fully to round-by-round frontier batching.**
  `references/grilling-technique.md` continues to reject that for the authoring commands, which stay
  one-question-at-a-time.

**Rejected on merits (revisit only if asked):** CLI/template scaffolding, `constitution`, governance
presets, SDD ledger / 5-round fix-breaker, generic lens engine, git-push-blocking hook, PRD-coach
"never recommend an answer", batch-grill-me denser rounds. (See INDEX.md "Deliberately NOT adopting".)

## Harvest round 4 — surveyed 2026-10-02; Rounds 1–3 SHIPPED (2026-10-02 – 2026-10-04)
Survey of the four upstreams against the round-2 baseline: superpowers `b36e0829`..`8ca22dba` (v6.3.0 → v6.4.2), mattpocock/skills `5b15a47`..`d81f3a1` (v1.3, unreleased changesets), BMAD-METHOD `67d876f1`..`4f61d4e7` (v6.12.0 + Unreleased), spec-kit `27f50f7e`..`4a339209` (1.0.1 → 1.0.13). 21 portable items; the six that were **defects in text all three editions shipped** went first, as Round 1. Spec (with an "Amended during review" section per review round) + plan: `docs/superpowers/specs/2026-10-02-harvest-round-4-defects-design.md` and `docs/superpowers/plans/2026-10-02-harvest-round-4-defects.md`.

**Round 1 — what shipped.** This repository: `workflows-core` 1.10.0, `dev-workflows` 4.5.0, `product-workflows` 3.11.3, `docs-workflows` 1.4.6 (merged with this entry). The internal edition: `dev-workflows` 2.66.0, merge `f689511`. The Copilot edition: `dev-workflows` 2.35.0, merge `83f2bf3`.
1. `diff-summarizer` read a ref that had landed as an empty range and reported it resolved (superpowers 5bf4e780). It now reads the merge that landed it (`<landing>^1...<branch_from>`, `landing` found by intersecting `rev-list --first-parent` with `rev-list --ancestry-path` — the two flags in one call follow first-parent edges only on git 2.43), reads a fast-forwarded single commit as its own change, reads the base as `origin/<branch>` where the local branch is behind, treats a parentless commit and an empty single commit explicitly, and never reports an empty range resolved. `/document` and `/release-notes` state how a `refs[]` element is built, and `/release-notes` states it passes no keys. The other two editions' resolver also read two-dot on every path (now three-dot), and its Strategy 3 is one rule: the newest commit whose **subject** names the PR in a forge's own form, searched uncapped and printing sha/parents/subject only; its search by PR title is gone, since it read other PRs' merges as this one.
2. `code-review` dimension 10 judged the diff alone — a requirement an earlier run delivered came back `missing` (MAJOR); it now judges the code as it stands, treats plan tags as claims, and reports `exceeds` (spec-kit #4621), never escalated onto the spec.
3. `risk-planner` carried the "what without how" rule upstream writing-plans withdrew (#2333); now "Unambiguous, not complete", spec-pinned values quoted verbatim (spec-kit #4430), proportion check on `### Steps`.
4. "design tree" survived the July rename in every caller; this repository now asks from the frontier, the other two say "decision tree" everywhere.
5. This repository's grill had no confirmation gate; it now has one, and all three play the understanding back at it; with no human turn the gate does not hold the write.
6. `test-baseliner` could read a filter's exit status through a pipe and record a failing status-only suite passing (spec-kit #4604); long output now goes through a temp file outside the repository.

**Found while executing, beyond the six — keep these:**
- **`workflows-core:implementation-format` §4's commit scan takes `--no-merges`.** A merge commit's range is the whole branch it merged (or, merged the other way, the base's own work), which the scan reaches commit by commit; a forge writes a PR's `[<key>]` title into its merge commit, so without the flag nearly every merge landing came back as unrecorded work. The cost, stated in §4 and on `commit-convention.md`: work a merge commit's message carries alone is not found; the branch-name probe keeps merge commits. A first attempt (round 2) instead excluded scan commits that "re-land" recorded work; round 3 showed it hid work, counted unread commits as read and could not run as written — the simple rule replaced it.
- **The anchored key boundary stays**, and §4 now says what a digit-aware one would add (a squash commit naming the branch, as a forge may write) and why it is not taken here: it changes the one boundary every reader of the file shares.
- Two pre-existing resolver defects in the other two editions were fixed on the way: the `gh` path fell back to `gh pr checkout`, which switches the working tree, against its own "never run"; and the strategies' placeholders were never mapped to the inputs.

**Seven whole-branch review rounds**, one fresh Opus reviewer per edition per round, every finding fixed (minors and nits included): round 1 found 6 Important, round 2 two, rounds 3–4 a handful each — most in text the previous round's fix had just written — and round 7 returned zero findings in all three editions. **The lesson worth keeping:** every Important from round 2 on came from a *new rule* written to close the previous round's finding; where a fix needs a new mechanism, look first for a principle the authority already states (§4's double-report rule gave `--no-merges`; "a candidate qualifies by its subject" replaced three patches to Strategy 3).

**Round 2 — what shipped** (the review pipeline, items 7–12, plus item 13 found while reading). This repository: `workflows-core` 1.11.0, `dev-workflows` 4.6.0, `product-workflows` 3.12.0, `docs-workflows` 1.5.0 (merged with this entry). The internal edition: `dev-workflows` 2.67.0, merge `6412900`. The Copilot edition: `dev-workflows` 2.36.0, merge `911b4f4`. Spec (with "Amended during planning" and "Amended during review") + plan: `docs/superpowers/specs/2026-10-02-harvest-round-4-review-pipeline-design.md`, `docs/superpowers/plans/2026-10-02-harvest-round-4-review-pipeline.md`.
7. `finding-triage` dismissed a claim it "could not substantiate", so a serious-if-true `BLOCKER` vanished; a third outcome, `unverified`, records one that would be `MAJOR`+ if true with what would settle it, is never handed to a fixer, and changes nothing the verdict gates. The patch gate never edits an instruction or contributor file the change did not edit; the triage line is one per review pass and sums survived + unverified + dismissed (BMAD 3433612d, b0d27c3c).
8. The re-review was not triaged, and every caller stopped on the second verdict's word — even on a `BLOCKER` that had not survived triage. § On re-review carries a logged row's outcome forward over the same artifact (`carried`), hands no survivor of a re-review to a fixer, stops only when the review **stayed blocked**, and lets the user settle a `BLOCK` no surviving `BLOCKER` supports (BMAD 7c3e5827, 85d968fc).
9. `code-review` grades by effect where no dimension fixes the grade — a maintainer-facing finding by the worse of what its people meet and the failure its gap lets reach users (approved during review) — and lists what it declined to judge; triage raises a grade by effect, to `MAJOR` at most, and rules on each declined line (superpowers 5bf4e780 #2319).
10. Plans carry a Review focus — `risk-planner`'s `### Review focus`, `/implement` Phase 2A item 9 — which `test-writer` tests and `code-review` checks (superpowers 5bf4e780).
11. `code-review` dimension 4: implicit branches, handle lifetime, call against declaration, removed contracts (BMAD 44e0f806).
12. `code-review` finds the repository's documented standards before dimension 3, from the project root down to each changed file's own directory (BMAD 23f134e2; mattpocock code-review step 3).
13. Five commands escalated per a `Review verdict BLOCK` rule `escalation-rules` did not have, and `/design` cited the `/epics` one, whose "Defer" writes into a draft its handoff then refuses; the new heading `… — commands that fix inline` is theirs. `/specify` keeps the `/epics` rule on purpose.

**Found while planning — keep these:** the stop is reached two ways, so it has one name, *stayed blocked*; `/implement`'s first-review settle prompt's Keep-the-verdict and Cancel arms were stops after files were written that no early-stop list named, so neither committed the work; every edit file was dry-run against all three trees and the whole round applied to throwaway copies (gates and checks green) before the plan was written, which found four gaps the population sweep had missed.

**38 whole-branch review rounds** (25 here, 7 in the internal edition, 6 in the Copilot edition), one fresh Opus reviewer per round, every finding fixed, minors and nits included; no `MAJOR` after this repository's round 5. Findings worth keeping:
- **A narrowed claim survives in its summaries.** Round 7 narrowed the carry rule to rows logged over the same artifact; the old extent survived in a changelog, the rules summary, a docs page and the Copilot summary until round 15 — the changelogs and summaries are copies too, swept by subject.
- **From round 13 on, nearly every finding was in text the previous round's fix had written** — a dangling "its", an ordinal a new first condition shifted ("the third is …"), a list that lost its "directory" noun, a clause that pointed at the wrong half of a two-item list. Re-read each fix from where it lands before the next round, not only its own sentence.
- **"Grade by effect" read literally graded a missing test or a violated standard by what a user meets on ship day** — nothing. The user approved one sentence folding the maintainer-facing case into the general rule.
- **Edition-specific text by placeholder, never by a second edit file.** `gen.py` placeholders (`EITHERFORM`, `TWOGRADE`, `OTHER`, line breaks) carried the two ports' differences; each wave rebuilt this repository's files from `origin/main` and confirmed them byte-identical.
- **Measure a length-capped file before adopting a reviewer's wording.** The Copilot shared instructions stand at 19,998 of 20,000 characters; a suggested clause measured 20,013.
- **The port reviews found what this repository's could not:** the two other editions' `clean_finish` row returned `true` on most early stops its own "Every run" paragraph sends with `false`, a `§2.8` pointer that meant `§2.9`, and a Review-triage lead-in that said one line per unit beside a template that said one per review pass.
- **`git check-ignore -v` prints a negated `!` pattern that re-includes a path**; two readers took every printed line as a match, and the user-facing advice now uses the plain form.

**Round 3 — what shipped** (items 13 and 15, and what the user decided while it ran). This repository: `workflows-core` 1.11.1, `dev-workflows` 4.7.0, `product-workflows` 3.12.1, `docs-workflows` 1.5.1 (merged with this entry). The internal edition: `dev-workflows` 2.68.0, merge `0ea083b`. The Copilot edition: `dev-workflows` 2.37.0, merge `b063bf6`. Spec (with "Amended during planning" and "Amended during review") + plan: `docs/superpowers/specs/2026-10-03-harvest-round-4-implement-pr-design.md`, `docs/superpowers/plans/2026-10-03-harvest-round-4-implement-pr.md`.
13. `/implement` looks before it asks. Phase 1 tries to settle each candidate ambiguity from what the run can read, the applicable ARD first on a keyed run, and asks only a decision: a question the evidence leaves open and the user would notice. Phase 2A writes its exploration down and re-tests the class on the plan it writes; Phase 3A step 5 re-plans upward with `risk-planner` (`Settled by the run`, `Work so far`) when the work meets a §1.1 trigger the approved plan did not state (BMAD 7e571784, 124ea1af, 2c10d5ba).
15. The code pull-request body: Summary, Evidence (before and after, as observed), Merge danger (one-way or two-way door, blast radius), Review, and the repository's own template where it has one; the file list is read from git (mattpocock `pr`).

**The user's decisions during the round — keep these:**
- **One repository per run.** `/implement` changes code only in the repository it branches; a change another code repository needs is planned out of scope, named in the pull-request body as a companion change, and becomes a follow-up. A plan with no step in this repository asks *Stop here* or *Revise plan* at its approval gate.
- **The ARD in Phase 1**, and **a unit-level commit that does not land ends `code-handoff` §2.12's split** (a hook's rejection, or git's own failure).
- **Every root at the repository's top level**: the test baseline and every agent a command dispatches, a run started in a monorepo subdirectory included.
- **How the review ended.** After rounds 15–29 stopped converging, findings in five areas whose fixes kept opening neighbouring edge cases went to the backlog below rather than another fix wave (the Stash answer, Phase 0's classification order, follow-up keys, subdirectory roots, and from round 41 the commit-and-staging mechanics); after round 43 the two other editions got one review round each, whose findings were fixed without a re-review.

**43 whole-branch review rounds here, one in each other edition**, one fresh Opus reviewer per round. Round 14 returned zero findings on the round as designed; everything after it came from the user's decisions and the pre-existing behaviour they exposed. Findings worth keeping:
- **A narrowing reaches every phase it crosses.** "One repository per run" took fifteen rounds: the record, the report, the follow-up route, the review triage, the routing graph, the classification floor and Phase 0's classification each carried a copy of the old extent.
- **Prefer an existing exit to a new path.** A plan with no step in this repository went through an empty-diff exit, then an Approve that skipped phases, before the stop it now asks for; each new path reached phases whose text did not expect it.
- **Measure git before writing a git rule.** Three fixes were regressions the next round measured: `--no-relative` needs git 2.28, `git diff HEAD` fails before a first commit, and the global `--literal-pathspecs` is inherited by every commit hook.
- **Fixing pre-existing behaviour has a cost the branch pays.** Deletions hidden from review, a dirty-tree commit that swept in the user's staged change, and untracked files a Stash left behind were real and fixed; each fix opened a neighbouring edge case, which is why the user filed the areas rather than keep going.

**Backlog — surveyed, not yet built** (items 7–21; each applies to all three editions unless noted):
7. Triage: "couldn't verify" is not "refuted" — defer a serious-if-true unsubstantiated finding with what would settle it; defer fixes to agent-instruction files; row count equals findings (BMAD 3433612d, b0d27c3c). M. — shipped in Round 2
8. Re-review keeps prior triage dispositions; the second review is triaged (BMAD 7c3e5827, 85d968fc). M. — shipped in Round 2
9. Effect-based severity where the spec is silent, and a reviewer's declined-to-judge list (superpowers 5bf4e780 #2319). S–M. — shipped in Round 2
10. A plan "Review focus" section — implied inputs no test exercises — tested by `test-writer`, checked by `code-review` (superpowers 5bf4e780 #2319). M. — shipped in Round 2
11. `code-review` edge-case checks: handle lifetime, call vs declaration (BMAD 44e0f806), implicit enum branch at code altitude, removed code whose contract nothing replaced. S. — shipped in Round 2
12. `code-review` finds the repo's documented standards — CLAUDE.md, AGENTS.md, copilot-instructions, CONTRIBUTING, CODING_STANDARDS (BMAD 23f134e2; mattpocock code-review step 3). S. — shipped in Round 2
13. `/implement` looks before asking, and can re-classify upward after exploring (BMAD 7e571784, 124ea1af, 2c10d5ba). M. — shipped in Round 3
14. Design contracts: owning side, behavioural obligations, provider-side conformance (spec-kit aaa8fa92). S.
15. PR body: merge danger (one-way/two-way door, blast radius), before/after evidence, honour a repo's PR template (mattpocock `pr`). M. — shipped in Round 3
16. `bug-diagnosis.md` drift: performance branch, one-variable probes, minimise the repro, no-loop fallback, name the confirmed hypothesis (mattpocock diagnosing-bugs). S–M. — shipped 2026-10-05 (`dev-workflows` 4.11.0 here; 2.76.0 and 2.45.0 in the other two editions); the re-run of the unminimised scenario and the instrumentation-permission ask were dropped in review, as nothing carried them
17. `impl-maintenance`: sort each miss into "build a check" or "write a standard"; flag no-op instructions (mattpocock `retro`). S–M. — shipped 2026-10-05 (`workflows-core` 1.18.0 here; 2.76.0 and 2.45.0 in the other two editions); a no-op is flagged only where a key event shows it failed
18. `/epics` dependency checks: needs and owners, collisions, one home per shared decision, touched-unit coverage (BMAD f033e70a, ba252f1b). S–M. — shipped 2026-10-05 in part (`product-workflows` 3.18.0 here; 2.77.0 and 2.46.0 in the other two editions): needs are built or named, and a shared decision is stated alike, citing the ARD. Collisions and one owner for shared setup were dropped in review: they assume dependencies between new Epics, which *Epic independence* forbids outside its exceptions, and *Suggested stories* already catches overlapping work. Touched-unit coverage is *Single target*'s
19. Acceptance-criteria wording tests: false before, true after; the rule, not an example; 3–8 (BMAD bmad-ticket). S; `specification-format.md` stays frozen. — shipped 2026-10-05 (`workflows-core` 1.19.0, `product-workflows` 3.18.0 here; 2.77.0 and 2.46.0 in the other two editions) for Epics and PRD stories; an Epic past eight criteria consolidates, never splits for a count
20. Redact secrets, emails, hosts and home paths before `/prompt` and feedback capture write user text (superpowers diagnosing-superpowers redaction policy). S. — shipped 2026-10-05 (`workflows-core` 1.17.0 here; 2.75.0 and 2.44.0 in the other two editions): every feedback entry point redacts while rendering, `feedback-emission` §1.1; three review rounds, the third's fixes not re-reviewed
21. Low or deferred: a glossary input for `interface-designer` (mattpocock DESIGN-IT-TWICE); a transcript-based session-diagnosis command (superpowers diagnosing-superpowers) — L.

**Follow-ups from Round 3:**
- *Look before asking* for the other commands that carry "Ask, don't guess" (`/design`, `/specify`, `/epics`, `/document`, `/ready`, `/release-notes`, `/docs-profile`) — Round 3's non-goal.
- The repository-template rule for `phase-handoff` §2.7's and `finish-and-handoff`'s pull-request bodies — Round 3's non-goal.
- **Multi-repository features: one repository per Epic, the contract in the ARD — SHIPPED 2026-10-04 in all three editions.** This repository: `workflows-core` 1.12.0, `product-workflows` 3.13.0, `dev-workflows` 4.8.0, `docs-workflows` 1.5.3 (merged with this entry). The internal edition: `dev-workflows` 2.70.0, merge `de6f5bb`. The Copilot edition: `dev-workflows` 2.39.0, merge `4c7d87c`. Spec (with § Amended during planning and § Amended during review) and plan: `docs/superpowers/specs/2026-10-04-multi-component-epics-design.md`, `docs/superpowers/plans/2026-10-04-multi-component-epics.md`.
  - **What shipped.** The unit is a *component*: a repository, or a module inside one, proposed by `enumerate-components` from what the repository declares and confirmed by a person. A PRD is multi-component when it touches two or more code components. `/create-ard` writes the confirmed `components:` and, for a multi-component PRD, a `## Contracts` section (interface table, schema ownership, versioning, landing order). `/epics` gives every Epic one `target:`, splits a capability that spans components, writes each Epic's `## Contract`, and stops to recommend the ARD's contract and the PRD-level spec where they are missing. `/specify` and `/design` narrow to the target. `/ready` and `/implement` run `multi-component-prereqs`, a read-only check of the prerequisites, the target and the contract coverage. A new shared reference, `workflows-core:components`, owns the rules.
  - **Review.** Nine whole-branch rounds here, with Important findings per round of 6, 3, 1, 2, 2, 2, 2, 1 and 0. After round 4 the user chose to stop at the first round with no Important finding, and its Minor findings were fixed without a re-review. Each port then had one review round, fixed without a re-review. The two ports were written by port agents from this repository's reviewed text, starting from a net-diff generator and a token-level three-way merge, with each edition's structure adapted: Jira-imported Epics, the VI, and two-key addresses.
  - **Findings worth keeping.**
    - *A fix for an edge case adds behaviour, and that behaviour has edge cases of its own.* From round 4 on, every Important finding came from the previous round's fix: overrides, exemptions and splits. What converged was closing rules rather than opening paths — a closed definition, one flag read everywhere, an existing channel such as plan-approval *Revise* in place of a new one.
    - *Sweep each fix's subject before its commit.* Rounds 2–4 found mostly copies of the previous wave's fixes. Once each wave swept its subjects (CLAUDE.md refinements 6–8), those stopped.
    - *Shared checkouts move.* In all three repositories another session's branch was checked out while this round ran, so every merge went through a temporary worktree.
  - **Landed since.** The other session's `iv-gu/kb-ports-2` landed on 2026-10-05, renumbered above these versions (`workflows-core` 1.13.0, `product-workflows` 3.14.0, `dev-workflows` 4.9.0 here; 2.71.0 and 2.40.0 in the other two editions).
- **Commit staging — the filed specs-repo and commit-mechanics defects — SHIPPED 2026-10-05 in all three editions.** This repository: `dev-workflows` 4.9.1, `workflows-core` 1.13.1, `docs-workflows` 1.5.4 (merged with this entry). The internal edition: `dev-workflows` 2.71.1, merge `bd5119b`. The Copilot edition: `dev-workflows` 2.40.1, merge `a7c9f80`. No spec or plan: the filed entries were the brief, and a scratch ledger carried the rulings.
  - **What shipped.**
    - `commit-artifacts`, `handoff-to-main` and every docs-repository commit (`/docs-profile`, `/docs-init`, `/docs-brand`, `/document`'s Phase 6.3 commit and Phase 8.5 squash) commit by pathspec over the paths they staged that git still lists, then bring the index back in step after a `pre-commit` hook. `specs-repo-git` §4 step 4 states the form once. A commit git refuses has a *Commit failed* row.
    - `code-handoff` §2.2's **run set**: each path dirty before the run carries a content fingerprint (`git hash-object`, or a symlink's link text), and carve-out 1 commits the porcelain set less the unchanged recorded paths and the no-change records. A changed recorded file is committed whole and named; a deletion the user had staged stays out; a user's rename stays together and a copy does not; a path a commit carried is retired for later units and CVEs. `/implement` and `/vuln` read the same set.
    - The post-commit restore covers the paths that are both in the commit and out of step in the index, less what somebody else had staged before the commit.
    - Every diff capture runs `git add -N` against a temporary copy of the index, so no intent-to-add mark is left on the user's untracked files for a later `git commit -a` to take.
    - Free text reaches git and `gh` safely: commit messages through `-F` files, pull-request titles in single quotes.
    - `/implement`'s `title` is the subject §2.3 writes. In the other two editions, a Jira key that the subject's shape leaves out goes in the body as `Resolves <KEY>`.
    - The other editions' port drift: the `--no-commit` remnants, the Copilot edition's review-tier pin and its stale placement paragraph, and `review_file` and `claims_file` left behind (in the internal edition too).
  - **Review.** Two whole-branch rounds here, with 1 and then 0 Important findings; round 2's Minor and Nit findings were fixed without a re-review. Then one round per port, also fixed without a re-review. Each review widened the round into defects of the class it was fixing: the diff captures' intent-to-add marks, the docs-repository index commits, and the refused-commit outcomes.
  - **Findings worth keeping.**
    - *A rule that needs a mechanism needs one definition, cited.* "Which paths are the run's" had four copies, each judged by wording ("did not edit"). Round 1 named the run set once and pointed every reader at it; the port reviews found the one place the port had not followed.
    - *A replacement whose output contains its input must never run over its own output.* The capture rewrite wrapped the `--numstat` site twice, a bash syntax error at `/implement` Phase 4 that both port reviews caught. Every capture site is now checked with `bash -n`.
    - *Measure a git claim before writing it*, as before: a restore over a commit's whole list fails on one deleted path; a pathspec commit is refused during a merge; `hash-object` over several paths fails whole on one missing path; intent-to-add entries are invisible to `diff --cached`.
  - **Filed for the next round, and shipped in it** (below): `vuln-fixer`'s and `upgrade-executor`'s revert by an unspecified mechanism.
  - **Landed since.** The other session's `iv-gu/release-note-rules` landed above these versions (`docs-workflows` 1.6.0 here; `dev-workflows` 2.71.2 and 2.40.2 in the other two editions).
- **Reverts and stashes — the fixers' revert, the Stash answer and its early stops — SHIPPED 2026-10-05 in all three editions.** This repository: `dev-workflows` 4.9.2 (merged with this entry). The internal edition: `dev-workflows` 2.71.3, merge `6bd6508`. The Copilot edition: `dev-workflows` 2.40.3, merge `7035f61`. No spec or plan: the filed entries were the brief, and a scratch ledger carried the rulings.
  - **What shipped.**
    - `code-handoff.md` §6: `/vuln` and `/upgrade` snapshot the whole working tree — tracked and untracked files, through a temporary index — immediately before each CVE's or component's first dispatch and pass it as `pre_edit_tree`; `vuln-fixer` and `upgrade-executor` revert by running one bash script (§6.2) that removes what the unit created and restores the rest from the snapshot, never from `HEAD`; §6.3 says what the caller does with a revert (report the paths, re-take the fingerprints it touched, finish a failed revert unclean, run the revert itself when the agent could not). Both agents never stage.
    - `/implement`'s Stash excludes only the spec inputs the run reads — a Spec folder's `.md` files rather than the folder — literally, never a path of the Code repo row; a path in a submodule is outside the repository; `refs/stash` is read around the push.
    - Every exit after a stash names it: `/upgrade`'s early stops, and the `--no-commit` row (§3.1) here; `/implement`'s pre-branch stops in the other two editions, which lacked the sentence this edition had.
    - Every diff capture calls `command cp`.
  - **Review.** One whole-branch round here with 0 Important, 12 Minor and 14 Nit findings, fixed without a re-review; then one round per port (0 Important each), fixed without a re-review.
  - **Findings worth keeping.**
    - *A procedure an agent must run exactly is a script, not a template.* The prose revert pasted each path into a command line, where a `$` in a route file's name expands and a `'` breaks the pathspec. The script passes paths only through variables and NUL lists, and the doc's copy is checked byte for byte against the tested one in every edition.
    - *A revert's scope is the snapshot's scope.* Ignored files, submodule contents and skip-worktree paths are outside a tree snapshot, so the script leaves ignored files alone — a loosened `.gitignore` deletes nothing — and refuses the rest rather than reporting them restored.
    - *A port finds the source's holes too.* Porting the early-stop sentence showed the other two editions' `/upgrade` had no switch step, and the source's own "read before the push" sat after the push in every edition.
- **Phase 0's classification — the working directory first, the top-level notice for an `@path` only, `@.` classified like any token — SHIPPED 2026-10-05 in all three editions.** This repository: `dev-workflows` 4.9.3, `workflows-core` 1.14.1 (merged with this entry). The internal edition: `dev-workflows` 2.72.1, merge `9739d2d`. The Copilot edition: `dev-workflows` 2.41.1, merge `daf40d1`. No spec or plan: the filed entry was the brief, and a scratch ledger carried the rulings.
  - **What shipped.**
    - `/implement` classifies the working directory straight after its run flags — before address resolution (the Jira front-end in the other two editions), the specs-repo preflight and the Epic picker. Its work-tree test reads what `git rev-parse --is-inside-work-tree` prints, since inside a `.git` directory or a bare repository git exits 0 printing `false`, and a failure shows git's error, since a repository git refuses (its ownership check) is not one the user is outside.
    - The working directory is not a token: the top-level notice is printed only for an `@path` naming a repository's top level, and a token naming the working directory (`@.`) is classified by the rows, so below the top level a spec folder there is read as one.
    - Every check of the run's own inputs comes before the preflight, and before the Epic picker in the other two editions: a token naming nothing on disk or matching no row is named and asked about, an unreadable `@file` stops, a direct run with no description stops naming the forms one takes, and the design-doc guard, whose input is always a token, runs on both modes.
    - `workflows-core:specs-repo-git` §3 and §7, and `CLAUDE.md`, exempt by class: a run that stops before the preflight on a check of its own inputs needing no specs-repo state runs none — in the other two editions, a stop on the Jira input too.
  - **Review.** Two whole-branch rounds here, inside the three-round cap agreed before the round: round 1 had 1 Important finding (the older token stops left after the preflight), round 2 none, and its Minor and Nit findings were fixed without a re-review. Then one round per port, 0 Important each, fixed without a re-review.
  - **Findings worth keeping.**
    - *An exit status is not an answer.* `rev-parse --is-inside-work-tree` succeeds inside `.git` and inside a bare repository; the test is what it prints, as `/docs-init`, `/docs-brand` and `/docs-profile` already read it.
    - *Ordering one stop exposes its siblings.* Giving the new no-description stop an explicit "before the preflight" left the two older token stops behind it in reading order, placed only by "immediately"; every check of the same class moved with it.
    - *A port's second copy is the port's own exposure.* The other two editions restated the working-directory rule in their front-end paragraph, where one word ("itself") separated the directory from a token naming it; the fix dropped the copy rather than qualifying it.
- **Follow-up keys — one key per repository, its `<repo-slug>` — SHIPPED 2026-10-05 in all three editions.** This repository: `workflows-core` 1.15.1, `dev-workflows` 4.10.1 (merged with this entry). The internal edition: `dev-workflows` 2.73.1, merge `f2134e4`. The Copilot edition: `dev-workflows` 2.42.1, merge `7626458`. No spec or plan: the filed entry was the brief, and a scratch ledger carried the rulings. This was the last of the areas filed on 2026-10-04. It is numbered above the other session's untrusted-content guard, which landed first (`workflows-core` 1.15.0, `dev-workflows` 4.10.0 here; 2.73.0 and 2.42.0 in the other two editions).
  - **What shipped.**
    - `followup-emission` §6 names another code repository by its `<repo-slug>` (`components` §1, the last segment of its `origin` URL), so ssh, https, `user@`, scp and fork clones key alike; one the run was not given by its component's `<repo-slug>` from the run's known set (`components` §3) or its design's `Target span:` line, else by one name the run gives it, followed by `(not given)` outside the key; one with no `origin` by its path. It states where a name still splits keys and where two repositories share one.
    - The task line writes the repository once as ``repository `<name>` `` and the unit as the `/dev-workflows:implement` address it asks for, with a literal example, and §5 compares both exactly. `/implement` Phase 6 collects one follow-up per repository so named.
    - `components` lists `followup-emission` among its citers and routes a change to §1's derivation across every slug→clone map that restates it.
  - **Review.** Two whole-branch rounds here, inside the three-round cap agreed before the round: round 1 had 1 Important finding (the not-given source named artifacts that mostly do not name another repository, where the run's known set does), round 2 none, and its Minor and Nit findings were fixed without a re-review. Then one round per port, 1 Important each (the literal example line was carried over in this edition's line shape, where theirs carries a tracker link and a date), fixed without a re-review; their unit-address finding was applied here too.
  - **Findings worth keeping.**
    - *Pick the name the family already resolves against.* Rounds 28–30 alternated between a basename that collides and an owner path that cannot meet a not-given repository's name; the family's own `<repo-slug>` was the one form the known set, the clone maps and a fork's clone all share.
    - *An exact comparison retires every old form at once.* Making §5 compare one fixed form ended substring matches and, with them, every earlier line's chance to match; the CHANGELOG names each old form rather than the one remembered.
- **The filed items — eight defects the Phase 0 and follow-up keys rounds filed — SHIPPED 2026-10-05 in all three editions.** This repository: `workflows-core` 1.15.2, `dev-workflows` 4.10.2, `product-workflows` 3.16.1, `docs-workflows` 1.7.1 (merged with this entry). The internal edition: `dev-workflows` 2.73.2, merge `9aaecb7`. The Copilot edition: `dev-workflows` 2.42.2, merge `7e73df5`. No spec or plan: the filed entries were the brief, the user decided item 1 before the round, and a scratch ledger carried the rulings.
  - **What shipped.**
    - `/implement` run from inside the specs repository (`$SPECS_PATH` that repository's top level) stops a keyed run before the preflight; a direct run there runs on with a notice, and a specs tree inside a larger repository is left as it was (the user's decision).
    - Every keyed `/implement` run reads back the open follow-ups addressed to its repository and unit — working tree and default branch — and on an Epic targeted at another repository recommends a companion run, bounded to those changes through scan, plan, review, pull request and follow-ups; a `(not given)` task is asked about. `followup-emission`'s dedupe for that identity is change by change against open and ticked lines, and here `/implement` writes its follow-ups into the unit's folder under the unit's key.
    - `/create-prd` (here) and `/create-vi` (the other two) read their seed after `$SPECS_PATH` and the preflight, and only on *Overwrite* where the folder already holds one; `/design`'s address stops, `/ready`'s `--claimed` order and three preflight sentences (here only).
    - `components` §1's `<repo-slug>` takes any trailing `/` and an scp remote with no `/`, restated in every slug→clone map and agent check, with `/create-ard`'s and `/idea`'s "(slug)" and `implementation-format`'s `repo:` citing it, and its sweep recipe now lists every `get-url origin` read.
  - **Review.** Three whole-branch rounds here, the cap agreed before the round: round 1 had 1 Important finding (the companion run's bound lived in one sentence, not in the plan's inputs), round 2 had 2 (the scan template re-added the Epic's themes; the repository-and-unit dedupe lost a second change once the companion run implemented exactly the listed ones), round 3 none, and its Minor and Nit findings were fixed without a re-review. Then one round per port, fixed without a re-review: the internal edition's had 1 Important (its rules file carried round 2's dedupe wording, which round 3 had replaced), the Copilot edition's none; the findings that held here too were applied here.
  - **Findings worth keeping.**
    - *A bound stated once is not a bound.* The companion run's limit had to be carried into each input the plan is built from — scan themes, the brief, the review's spec — and into each collector of "another repository's need"; one sentence in Phase 1 was read past at every consumer.
    - *Narrowing what a reader does changes what its writer must record.* Once the companion run implemented exactly the listed changes, a dedupe that skipped by repository and unit lost work; the key had to grow to the change.
- **The specs commit's push scope — the one item the filed-items round filed — SHIPPED 2026-10-05 in all three editions.** This repository: `workflows-core` 1.16.1, `dev-workflows` 4.10.3, `product-workflows` 3.17.1, `docs-workflows` 1.7.2 (merged with this entry). The internal edition: `dev-workflows` 2.74.1, merge `48bb2ff`. The Copilot edition: `dev-workflows` 2.43.1, merge `cd7a101`. No spec or plan: the filed entry was the brief, the user approved the approach, and a scratch ledger carried the rulings.
  - **What shipped.** `specs-repo-git` §4 step 5 pushes only the default branch or a plugin branch, only where there is a remote to push to, and only while every commit the push would publish — measured against the branch's own remote ref, the remote's refs as a whole only for a branch with none — is a session-file commit (`push-scope`), the plugin's own commit included where a `pre-commit` hook put anything else into it. The push names its branch (`push -u <remote> <branch>`). §3.4's retry applies the same three conditions; §6 has three *not pushed* lines and a hook variant; G2's notice says its commit is not pushed. Every copy of the claim was aligned: `/implement`'s direct-run notice (with a `--no-commit` variant here), its Phase 4 note and terminal step, the 29 terminal-step paraphrases, docs pages, rules, the rationale (`#specs-push-scope`). The Copilot edition was affected too, through an earlier run's leftover session file.
  - **Review.** Three whole-branch rounds here, the cap: round 1 had 2 Important findings (`/create-prd`'s paraphrase missed; the first test counted commits on no ref of the remote at all, so a default branch fast-forwarded onto a pushed `prd/` branch would have pushed it), round 2 had 1 (the by-sha pass for this run's commits pushed what a broad hook swept in), round 3 had 2 (the by-path pass that replaced it missed a staged rename's original path; the report called a swept-in file uncommitted). The cap was reached without a clean round: the hook pass was removed rather than patched a third time, back to the rule round 2 confirmed, and those fixes were not re-reviewed. One port review each: the internal edition 1 Important (a `--no-commit` variant it has no flag for), the Copilot edition none. Another session's architecture-knowledge-base release landed meanwhile and was merged in (the `kb/` prefix; not material to the push rule).
  - **Findings worth keeping.**
    - *Measure a publish set against the branch's own remote ref.* "On no ref of the remote" passes commits that are published elsewhere but not on this branch, which is exactly a fast-forward of an unreviewed branch.
    - *An exemption for "our own" commits inherits whatever a hook puts into them.* By sha it pushes the user's swept-in work; by path it misses a rename's other half. A refused push that names the file is the cheaper failure.
- **The twelve findings the push-scope round filed — triaged 2026-10-05 against the reference text, with no reviewer; two fixed, ten closed.** The fix had one review (1 Important: the pull needed `--no-rebase`; 4 Minor), fixed without a re-review. The population for each was measured against the one specs repository in use: one `origin` remote and no push settings, pull requests landed as merge commits, and the plugin's session-file commits pushed straight to `main`.
  - **Fixed** (`workflows-core` 1.16.2 here, with the other two editions):
    - *B1 never pulls.* A checkout left on the default branch while a pull request merged on the remote, or a teammate pushed, committed on a stale base, and every push and retry after it was rejected as non-fast-forward. This is an ordinary setup: any run that leaves the checkout on the default branch, followed by any merge. §3.4 and `commit-artifacts` step 2 now fast-forward a default branch that is strictly behind (`--no-rebase`, so a `pull.rebase` setting cannot turn it into a rebase). A diverged one, including through a merge during a run, gets a line naming `pull --rebase --autostash` and the push.
    - *The refusal tail never tested G0.* This is rare: it needs a detached specs checkout and an address refusal. It was fixed anyway because it is the data-loss guard and costs one clause: §4 step 1 now tests the state itself on a run that ran no preflight.
  - **Closed**, each with its reason:
    - *§2.1's pattern matching a customer file under `brd/source/`.* This needs a BRD bundle holding a file named exactly like a session file, and that file goes to the same specs repository the BRD's own branch does.
    - *A fork layout and `pushRemote`/`pushDefault`.* No specs repository in use has a second remote or a push setting.
    - *A remote that renamed its default branch.* This happens once in a repository's life, and the stray branch it recreates is visible and deletable; nothing is lost.
    - *A protected default branch.* The repository in use accepts direct pushes to `main`. Reopen as a design question (where do session files go?) when one does not.
    - *A flush commit on a branch B4 leaves.* This needs a flush whose push fails in the same run, and the commit sits on a named plugin branch and goes out with it.
    - *A squash-merged plugin branch reading as unmerged.* The repository in use merges with merge commits. Reopen if a squash-merging team adopts the plugin.
    - *`branch-naming` §2.3 counting remote names.* This reaches only a code branch cut inside the specs repository itself, a rare `/implement` target; the preflight's handling of such a branch is non-destructive (`branch -d` only).
    - *G2's notice naming the starting branch on a direct `/implement` run.* The run must be in the same rare layout. The notice is advisory, and the commit lands safely on a named branch.
    - *The ALWAYS lines' "bounded … to plugin-created branches".* The phrase cites §2.2, which is exactly that bound; the commit and push rules sit in §3.3 G2 and §4 step 5, which the line does not restate. No run behaves differently.
    - *Phase 4.5's `handoff-to-main` on a direct `/implement` inside the specs repository.* It needs the same rare layout, it was never traced, and no run has reported it. Reopen on a report.
  - **Process note.** The twelve came from review briefs that asked each reviewer for out-of-scope findings "for filing". Briefs now ask only for defects in the change. An older problem is filed only when it reaches an ordinary setup, and the entry states that population.
**Rejected again** (reasons unchanged): superpowers' native executing-plans / SDD ledger, verify-a-fix-by-test instead of re-review, nested mid-tier orchestrator; mattpocock `implement-spec`, `retro` as its own command, `pr`'s picture menu and Mermaid; BMAD's user-pinned review depth (bypasses the classification gate), finding floors scaled by diff size, the ticket store and walkthrough; spec-kit's extension and catalog machinery, `taskstoissues` (a tracker), the constitution sync report.

**Recorded divergences** — decisions, not gaps:
- **BMAD's severity reset is not ported.** Its reviewers lack the context ours carry — Opus with the plan, the diff and the code — so reviewer grades stand, raised only by effect.
- **BMAD's follow-up-review recommendation is not ported.** Our re-review after a `BLOCK` fix cycle is already automatic and capped.
- **`/specify` keeps the `/epics` escalation rule.** It defines its own "Defer" to mirror `/epics`' Epic-refinement note.
- **Grilling rhythm.** The internal and Copilot editions ask relentless callers' questions in rounds; this repository stays one question at a time, because `/brd-split`'s ledger walk forbids batching.
- **"design tree" vs "decision tree".** mattpocock renamed it "decision tree" (`3bb587f`) and then back (`a4b2009`); we keep "decision tree" for our own reason — "design tree" collides with `design.md`.

## Standing constraints (still apply for any new work)
- Pushes are AUTHORISED (user, 2026-08-21) — merge to `main` and push in all three repos once the round
  is finished, not incrementally. Commit trailer names **the model that did the work**, not
  whatever a previous round used: `Co-Authored-By: Claude <model> (1M context) <noreply@anthropic.com>`.
  Waves through 2.41.0 used `Claude Opus 4.8 (1M context)`; harvest round 2 used
  `Claude Opus 5 (1M context)`.
- Do NOT edit `references/specification-format.md` (frozen snapshot).
- The internal edition's push bypasses a PR-required branch rule (user: "ok for now").

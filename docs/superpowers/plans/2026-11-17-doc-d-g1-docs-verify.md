# DOC-D-G1 sub-project 2 — `/docs-workflows:docs-verify` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Revision 2 (2026-11-18)** answers plan review 1 (`.superpowers/plan-review-1.md`: 0 Critical, 5 Important, 7 Minor) and the maintainer's answer to its QP3:

| Finding | Where it is settled |
|---|---|
| **QP3** (maintainer: *Export, no shell*) | R19 rewritten (the export), R-I11 rewritten, R29 (the reader's techniques), R30 (the cap); Task 2.1 (`backlog-lines.py export` and `claim-reader` with `Read`, `Grep`, `Glob`); Task 2.3 Phase 5; the design's dated note under S2-D5, added with this revision |
| **P1** free text on a shell line | Gone with Bash: R19, Task 2.1 |
| **P2** `/docs-write`-only sentences in the moved blocks | R1; Task 1.2 (Files, Step 4 part 6); Task 2.3 Phase 1 test 5, Phase 5 step 2, traces T-TAGREAD and T-ARDWT |
| **P3** the reader's return partly unclassed | R27; Task 2.3 Phase 5 step 6 |
| **P4** a record commit with nothing to commit | R28; Task 3.3 step 9 |
| **P5** `/docs-write`'s next step left stale | Task 2.4 (its text and counted string), Task 3.4 (Files, Step 1) |
| **m1** the re-point list | Task 1.2 Files and Step 2 |
| **m2** `CLAUDE.md` sizes | *Exact copy* |
| **m3** R8 against Q1 | R8 |
| **m4** recipe counts across the move | Task 1.2 Steps 1 and 6 |
| **m5** QP1, QP2 as the controller's | *Answers and rulings at plan review 1* |
| **m6** Task 2.3's load | Task 2.3 keeps the command, its page and the rows a gate fails without; every other registration moves to Task 2.4 |
| **m7** `walk-record`'s step number | Task 3.6 Step 3 |

**Revision 3 (2026-11-18)** answers plan review 2 (`.superpowers/plan-review-2.md`: 0 Critical, 2 Important, 5 Minor, all new; findings cited *N1*, *N2*, *n1*…*n5* here, the review's m1…m5). No question goes to the maintainer.

| Finding | Where it is settled |
|---|---|
| **N1** the search tools may not see the whole export | R31; Task 2.1 Step 5 (the build-time probe) and the reader's *Method* (canary first; a named path opened with Read); Task 2.3 Phase 5 steps 3, 4 and 6 (the root `.ignore`, the run-time canary, the reader's canary checked; `DOCS_VERIFY_EXPORT`); T-CANARY |
| **N2** `techniques` is shell text for a reader with no shell | R29; Task 2.1 (the translation rule in the reader's body; the recipes never run) and Step 7's trace of each §3 technique |
| **n1** skipped files read as "not found" | R32; Task 2.1 (the reader's `skipped`; an ignore file renamed, not skipped, so R32 does not fire on every repository holding a `.gitignore`), Task 2.3 Phase 5 step 8 and the report |
| **n2** three selftest cases | Task 2.1 Step 1: `export_no_filter_run`, `export_timeout`, `export_name_collision` (91 after batch 2) |
| **n3** a create failing for its name | Task 2.1 *The write* |
| **n4** `lines` against the cited file | R27; Task 2.3 Phase 5 step 6 |
| **n5** a dead session leaves the export | Task 2.3 Step 8 (the command page's *Failure modes*) |
| The reader's read-anywhere residual | R-I11; Task 2.7 Step 2 (batch 2's CHANGELOG) |

**Goal:** `/docs-workflows:docs-verify <unit-id>|--next [--prepare]` takes one `drafted` backlog unit to `verified` by its audience's method — an engineering page read in code, a user page walked — in one commit holding the resolved page, with a defined exit for every unit that cannot resolve.

**Architecture:**
- One new command with its own phases (S2-D1), dispatching `code-scanner`, `doc-writer`, `docs-style-checker`, `doc-fixer` and `doc-reviewer` as `/docs-write` does, plus two new agents: `claim-reader` (batch 2) and `walkthrough-composer` (batch 3).
- The parameter-free steps the two backlog runs share move out of `commands/docs-write.md` into a new `references/docs-iteration/backlog-run.md` (Q2), in batch 1, with `/docs-write`'s behaviour unchanged.
- `scripts/backlog-lines.py` stays the one line reader (S2-D10): `moved --own-moves` and three `edit` flags (batch 1), and five walkthrough verbs (batch 3). It also hosts `export` (batch 2): the one program that writes a clone's commit into a scratch directory for `claim-reader`, which holds no shell (QP3).
- Every difference an apply brief makes to `doc-writer` and `doc-reviewer` lives in `unit-brief.md` (S2-D7); `gate-ledger.md` gains §10 (S2-D12).
- `workflows-core` takes rows, counts, caller lines and the four GIT-G1 truth edits, all in batch 2, its one minor.

**Tech Stack:** markdown prose that agents execute; one Python 3 stdlib script with `--selftest`; generated reference parts (`python3 scripts/reference-parts.py generate`); the repository gates.

**Spec:** `docs/superpowers/specs/2026-11-17-doc-d-g1-sp2-docs-verify-design.md`, revision 3, approved 2026-11-17 (cited *S2-D1*…*S2-D15*, *Q1*…*Q4*, its abbreviations BF, EC, FH, ROUTE, DW, UB, GL, BL, AUD, WRT, REV, CS, SRC, ROR, MR, WCG, BKR, SRG, PH unchanged). The parent, `docs/superpowers/specs/2026-11-17-doc-d-g1-docs-iteration-design.md` revision 3, binds everything the sub-project design does not settle (*P-D1*…*P-D17*). A decision either design states is not repeated here. Model of shape: `docs/superpowers/plans/2026-11-17-doc-d-g1-docs-write.md`.

**The maintainer's answers on the design** (its Status line): Q1 an unresolvable unit stays `drafted`, tagged `claims-unresolved` in its three cases only, `explanation` pages verified by hand; Q2 the parameter-free shared steps extracted into `backlog-run.md` as batch 1; Q3 the fourth per-step option and a record commit for every walk that ends without its move; Q4 four batches, each released on its own. The four GIT-G1 edits are truth-only, under the 2026-11-17 standing OK.

**Answers and rulings at plan review 1** (2026-11-18; `.superpowers/plan-review-1.md`, findings *P1*…*P5*, *m1*…*m7*):
- **Maintainer — QP3, *Export, no shell*.** The command exports the commits `claim-reader` reads — today's whole tree, and the evidence paths at each recorded `ref` — into a scratch directory under `workflows-core:run-flags` §7, by one fixed program; `claim-reader` holds `tools: ["Read", "Grep", "Glob"]` and reads only under that directory. A departure from S2-D5's approved tools, which the maintainer approved; the design carries a dated note under S2-D5. R19, R27, R29, R30, Task 2.1.
- **Controller — QP1 is within Q2 once P2 is applied** (m5): `backlog-run.md` §6, §7 and §8 hold the read and the program only, and each consequence stays in its command (R1).
- **Controller — QP2** (m5): no new CI step; `.github/` is untouched; the pull requests of batches 2 and 3 name the two comments — *Self-test the backlog line reader* and *Self-test the tree snapshot* — as incomplete but true. `export`'s cases run in the existing *Self-test the backlog line reader* step, which is why the program lives in `backlog-lines.py` (R30): a script of its own would need a new step.
- **Controller — P4, P5 and the Minors** as the review says. **Task 2.3's load** (m6): split by what a gate fails without, the drafter's call (Task 2.3, Task 2.4).

No question is open.

**Execution:** subagent-driven, batch by batch. Opus implements every task. **[security-sensitive]** tasks are reviewed by Fable — Task 2.3 and Task 3.3 in two passes, Phases 0–5 and Phases 6–15; **[mechanical]** ones by Opus. Each batch ends with a whole-branch review by Fable against both designs and this plan, before its pull request.

**Batches** (S2-D15, Q4). Each is its own branch, pull request and release, cut from `origin/main` once the batch before it has merged, in its own worktree; versions are plan-time expectations, re-derived at landing (*Release*).

| Batch | Branch | Worktree | Release (plan time: main at `docs-workflows` 1.43.0, `workflows-core` 1.97.0) |
|---|---|---|---|
| 1 Groundwork | `feat/doc-d-g1-docs-verify` (this branch: the design and this plan land with it) | `/home/ihudak/dev/ai-tools/ai-workflows-wt/doc-d-g1-verify` | `docs-workflows` 1.44.0 |
| 2 Engineering units | `feat/doc-d-g1-verify-engineering` | `/home/ihudak/dev/ai-tools/ai-workflows-wt/doc-d-g1-verify-b2` | `docs-workflows` 1.45.0, `workflows-core` 1.98.0, patches of plugins whose pages only change |
| 3 User units in session | `feat/doc-d-g1-verify-user-walk` | `/home/ihudak/dev/ai-tools/ai-workflows-wt/doc-d-g1-verify-b3` | `docs-workflows` 1.46.0 |
| 4 `--prepare` | `feat/doc-d-g1-verify-prepare` | `/home/ihudak/dev/ai-tools/ai-workflows-wt/doc-d-g1-verify-b4` | `docs-workflows` 1.47.0 |

**Base:** `74d3e8d1e` (`origin/main`, sub-project 1 shipped as PR #210) plus the design commits, HEAD `2ca797de5`. Line numbers are finding aids at that base: **locate every site by its quoted phrase.**

**The GIT-G1 edits** — all four in batch 2, under the standing OK, each re-derived at batch 2's landing (*Exact copy*):

| # | Site | Task |
|---|---|---|
| G1 | WCG:26 — the `specs-repo-git` consumer counts | 2.5 |
| G2 | WCG:32 — the implementation-repository counts | 2.5 |
| G3 | SRG:310 — the bookkeeping-only class gains `/docs-verify` | 2.4 |
| G4 | PH:628 — `/docs-verify` refuses there as `/docs-write` does; `reference-parts/phase-handoff/require-on-main.md` regenerated | 2.4 |

G1 and G2 change WCG by +1 (19,986 → 19,987): G1 is −1 (`thirty-six`→`thirty-seven` +2 twice, `thirty-nine`→`forty` −6, `six of`→`seven of` +2, `eight`→`nine` −1), G2 +2.

---

## Global Constraints

### What is not ours

- **Never edited:** `plugins/workflows-core/scripts/specs-git.py` and its two modules, the `specs-git` skill, `run-key-set.md`, `.claude/rules/workflows-core-handoff.md`, `.github/` (the controller's QP2 ruling), `phase-handoff.md` but G4's clause, its `reference-parts/` but by `generate`, `specs-repo-git.md` but G3, `workflows-core-git.md` but G1 and G2.
- **Left as they stand, by the design's choice** (*The GIT-G1 edits*, *Left as they stand*): SRG:132 (kept true: `DOCS_VERIFY_NOT_A_REPOSITORY` takes no tail), SRG:314, SRG:752-762, PH:403, PH:439, PH:628's named readers, the `specs-git` skill. Also `.claude/rules/workflows-core-handoff.md:24`'s non-exclusive list of the drafts that follow the template rule, and QP2's two comments. Each pull request names them.
- **Any other GIT-G1 sentence a step finds false**: a plainly false sentence is given a truth-only edit under the standing OK and named in the pull request; anything that adds behaviour or a rule is reported to the controller as a question, never edited.
- **Untouched:** `commands/document.md`; `/docs-audit` and `docs-audit-reviewer` (BF §3 and §4 change in text only, S2-D14); `doc-location-finder` (not dispatched); the contracts of `code-scanner`, `docs-style-checker` and `doc-fixer` (their caller lines gain `/docs-verify`, P-D15's reading of "unchanged"); `/docs-init`, `/docs-brand`, `/docs-serve`, `/docs-profile`, `/release-notes`, the hooks; `schema_version` (stays 1).
- **Batches 1, 3 and 4 change no file under `plugins/workflows-core/`**, so that `workflows-core` takes one minor (Q4). A step that finds a `workflows-core` sentence its batch makes false reports it; it is not edited outside batch 2.

### Repository rules

- **Prose is executed.** Every sentence an agent reads is true in the release that ships it: a batch never names a later batch's behaviour (R6, R17). Every shell command in prose takes `-C '<top>'` (or `git -c safe.bareRepository=explicit -C '<clone>'`, or `git -C "$SPECS_PATH"`), quotes each value single-quoted with `'` written `'\''`, and ends options with `--`.
  - A pathspec built from data takes `':(literal)<path>'`; `check-ignore` takes `'./<path>'`, since it refuses pathspec magic.
  - A clone is admitted only by `test -e '<path>/.git'` first, and every git call in a clone runs with `-c safe.bareRepository=explicit`.
  - The profile's tool tokens are class-tested and single-quoted (TP-QUOTE); a repository's pull-request template is data (PR-TEMPLATE-COMMENT).
- **Data reaches an inline `python3 -I -c` program only as a single-quoted argument**, and a program in a list item sits in a fenced block, never an inline span.
- **No agent this sub-project adds runs a shell** (QP3): `claim-reader` holds `Read`, `Grep` and `Glob` and reads only under the export root it is handed; `walkthrough-composer` holds `Read`. Besides `code-scanner`'s own prep, which its contract bounds, every git call a run makes on a source repository is the orchestrator's or `backlog-lines.py`'s — a single-quoted command line built from class-tested values, or an argument list — never text an agent quoted.
- **A page-text phrase a program matches is pinned by a selftest in `backlog-lines.py`**, as `WHY_UNDO` and `EC_MARKER_PHRASE` are: the page-level marker phrase (both batches 1 and 2), the visibility marker (R5) and the slot comment (batch 3).
- **Resolve identifiers against a known set; never parse one out of free text.** A walkthrough id against the directory listing; a unit id against `units[].id`; a step number against `walk-check`'s `steps`; an answer's outcome against the closed set.
- **D4 holds: one prose copy.** A rule has one owner and others cite it. The phrases a gate or recipe reads stay literal in each command body (S2-D1's table): the core-references preamble (check 16), the load-by-part paragraph (`check-citations`), **Load the question rules.** (`check-questions`), `strip-run-flags`, the `workflows-core:model-routing` call, the `workflows-core:impl-maintenance` dispatch, `emit-cost` (check 8), `args: "specs-repo-git commit-artifacts` (WCG:26's recipe), `scan-refresh`. **No command body writes `resolve-address`** (`check-branch-check`).
- **`grep` here is ugrep; every count uses `command grep`.** A count is taken before and after each edit, wrap-insensitively, over refinement 4's scope (`.claude/rules/claim-sweep.md`).
- **Sizes**, by `LC_ALL=C.UTF-8 wc -m` (plan time): `CLAUDE.md` 35,840 (warn 36,000); `.claude/rules/docs-workflows.md` 18,775; `docs-workflows-backlog.md` 9,329; `docs-workflows-gates.md` 4,683; `workflows-core-git.md` 19,986; `workflows-core.md` 19,191; `workflows-core-model-routing.md` 5,575; `workflows-core-triage.md` 5,183; `docs-grounding.md` 11,982; `plugin-updates-coupling.md` 6,362; `workflows-core-read-only.md` 5,046. Rules files warn at 20,000. Every task that edits one measures it before and after.
- **User pages** (`plugins/*/docs/**`, READMEs): no `§`, no `S2-D<n>`/`D<n>`, no `<plugin>:<reference>` (check 25); a table cell at most 200 characters (check 6); a page naming a command links its page (check 28); a command page links `docs/workflow.md` (check 26). Every claim on a page is derived from the command or reference that runs it.
- **No dash-form requirement id; every executed regex uses `[0-9]`, never `\d`; no tracker, organisation or outside product named.**
- **Commits:** `git branch --show-current` immediately before each, expecting the batch's branch; never `git checkout`, never a bare `git stash`. Each message ends with the committing session's attribution lines.

### Gates

One chain, from the batch's worktree root; read the printed value:

```bash
set -o pipefail; python3 scripts/validate-catalog.py && ./scripts/check-id-grammar.sh --root . && ./scripts/check-id-grammar.sh --baseline && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && python3 scripts/reference-parts.py check-branch-check && ./scripts/check-docs.sh --root . && python3 plugins/workflows-core/scripts/lineage.py --selftest && python3 plugins/docs-workflows/scripts/backlog-lines.py --selftest && claude plugin validate .; echo "EXIT=$?"
```

Expected: `EXIT=0`; `validate-catalog` `0 error(s), 0 warning(s)`; `backlog-lines.py` `selftest: <n> passed` with the batch's count (57 at base; 75 after batch 1; 91 after batch 2, Task 2.1 adding 16; batch 3's count recorded at Task 3.1). `--baseline` runs alone, never with `--root .`. The mermaid gate needs `node`, which this machine lacks: CI runs it, and every edited label holding `[ ] ( ) { } |` or `#` is quoted. A task editing a load-by-part reference (`escalation-rules`, `finding-triage`, `next-phase-offer`, `session-hygiene`) or `phase-handoff.md` runs `python3 scripts/reference-parts.py generate` first and never hand-edits a generated file. `check-docs` takes about four minutes. `claude plugin validate` does not check agent frontmatter keys (R-I11), so it proves nothing about them.

**Tests for command prose are traced runs.** No harness executes a command's prose, so each fixture is a **scenario trace** in the task report: the input, each deciding sentence quoted as `file:line`, the outcome, and any step no sentence decides — a defect, fixed in that task. A trace that needs a git behaviour (a CRLF blob, a merge base) builds a throwaway repository under the session's scratchpad and quotes the commands and their output. Each batch adds one live check to `docs/superpowers/to-test-on-real-project.md`.

### Release (every batch)

Merge `origin/main` first, never rebase; take versions above main, the next free minor of each plugin the batch releases; the pull request that lands second takes the next free versions. Date each CHANGELOG section on landing day (UTC). Every plugin whose files change is released — a patch where only pages or prose change. One coupling bullet, only where an older side breaks something (batch 2 alone, *Exact copy*). The plugin `description` replaces words, never appends, under 900 characters, `plugin.json` equal to `marketplace.json`.

### The sweep (every batch)

By subject over refinement 4's scope — `plugins/` (every `CHANGELOG.md` included, where a hit is history and stays), the root `README.md`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/` — counted before and after each literal string changed (refinements 7, 8). Subjects (S2 *Files touched*): who moves a unit to `verified`; who composes walkthroughs and renders the checklist; who removes the page-level marker; which edges and `blocked_by` tokens have a writer; what stays manual on the route; which command dispatches each agent; which commands consume each shared reference; the counts. The exclusivity probe adds the design's phrases: "by that person alone", "Spec 2's", "a later release", "reserved", "no command", "by hand", "Two values are written", plus `the only`, `only writer`, `nothing in this increment`, `is planned`, `No such command`. The batch's close task checks every count.

### Shared names (every task uses these, exactly)

- **Classes**, `backlog-run.md` §3's (moved from DW:24-34, unchanged): `UNIT_ID`, `PAGE_PATH` with the page-path test, `ARTIFACT_PATH`, `OBJECT_ID`, the branch class, `rel-path`, `abs-path`, `tool`, `command`. New, `/docs-verify`'s own: **`STAMP_AT`** `^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$`; **`TOKEN`** the status class `^[a-z][a-z-]{0,31}$`; **`URL`** (S2-D4): starts `https://`, holds no whitespace, no character the class test's `X` names, none of `(`, `)`, `<`, `>`, `"`, `'`, a backtick; **an image extension** `png`, `jpg`, `jpeg`, `gif`, `webp`, `svg`, compared lowercased (R15).
- **`<top>`**, **`<base>`**, **`<default-ref>`**, `specs_git`, **`unfinished/`** as sub-project 1 defines them. **`<plugin root>`** is the value `${CLAUDE_PLUGIN_ROOT}` arrives as in the command's own body (R2).
- **The backlog-run reference** `${CLAUDE_PLUGIN_ROOT}/references/docs-iteration/backlog-run.md`, sections (R3): §1 *Parameters*, §2 *Untrusted input*, §3 *Classes and tests*, §4 *The base*, §5 *Sources*, §6 *The page-tag read*, §7 *The walkthrough's admission*, §8 *The ARD read*, §9 *Copies and the writing agents' reach*, §10 *The page-level marker programs* (§10.1 *read*, §10.2 *test*).
- **The parameters** each command names (§1): stop prefix `<RUN>` — `DOCS_WRITE`, `DOCS_VERIFY`; temp prefix `<run>` — `dw-docs-write`, `dv-docs-verify`; the scan phase — `/docs-write` Phase 4, `/docs-verify` Phase 5; the consent — `/docs-write` Phase 2, `/docs-verify` Phase 3; the reach set — "the unit's page and its placement targets", "the page alone".
- **The script** `${CLAUDE_PLUGIN_ROOT}/scripts/backlog-lines.py`: today's `check`, `moved`, `edit`, `--selftest`; batch 1 adds `moved … --own-moves` and `edit … [--from <status>] [--walkthrough <id>] [--block <token>]` (Task 1.1); batch 2 adds `export --repo <clone> --commit <oid> --out <dir> --manifest <file> [--whole] [--path <rel> …]` (Task 2.1); batch 3 adds `walk-check`, `walk-stamp`, `walk-record`, `walk-new`, `walk-append` (Task 3.1). The caller's rule is its docstring's.
- **The export root** `<export root>`: one `command mktemp -d -t dv-docs-verify-export-XXXXXX` directory per run (`workflows-core:run-flags` §7 sets where), holding each export (`c<k>` for clone `k` at today, `c<k>-r<j>` for its `j`th recorded `ref`), each export's manifest (`c<k>.files`, `c<k>-r<j>.files`: each written path beside its repository path, NUL-separated, relative to the export), the page's copy `page.md`, the reader's handoff `handoff.yml`, the command's `.ignore` (one line, `!*`) and the canary `canary/` (R31). Removed at Phase 12 with `command rm -rf -- '<export root>'`.
- **The walkthrough path** `<top>/.dev-workflows/walkthroughs/<id>.yml`; **the fixed id** of a composed file is the unit id (S2-D3).
- **`/docs-verify`'s phases** (S2-D1): 0 Resolve, 1 Select, 2 Resolve the evidence, 3 Consent, 4 Branch, 5 Walk or read, 6 Apply, 7 Style, 8 Build, 9 Review, 10 Commit, 11 Finish, 12 Report, 13 Session maintenance & feedback, 14 Follow-ups, 15 Session cost (then the resume pointer and `commit-artifacts`).
- **`/docs-verify`'s stop codes** (`DOCS_VERIFY_*`; wording the builder's, content as each task says): no tail — `UNKNOWN_FLAG`, `SELECTOR`, `NOT_A_REPOSITORY`; Phase 0 — `NOT_WRITEABLE`, `NO_PROFILE`, `PROFILE_COMMAND`, `PROFILE_IMAGES` (batch 3), `NO_BACKLOG`, `UNCOMMITTED`, `BACKLOG_UNREADABLE`, `BACKLOG_SHAPE`, `UNKNOWN_SCHEMA`, `DUPLICATE_ID`, `NO_MARKER`; Phase 1–2 — `NO_UNIT`, `STATUS`, `BLOCKED`, `RELEASE_UNIT`, `TYPE`, `PAGE`, `PAGE_TAGGED`, `NO_PAGE_MARKER` (R7), `USER_UNIT` (batch 2 only), `WALKTHROUGH` (batch 3), `WALKTHROUGH_SHAPE` (batch 3), `PREPARE_ENGINEERING` (batch 4), `EVIDENCE`, `ARTIFACT`, `NO_BASE`, `NO_CANDIDATE`; Phase 4 — `UNIT_CHANGED`, `PROFILE_CHANGED`; Phase 5 — `EXPORT` (an `export` that could not run, or a canary file the search tools missed, R31); later — `BACKLOG_EDIT`, `WALK_WRITE` (batch 3).
- **The three commits** (S2-D6), each by FH §6.3: subject `docs: <verb> <unit-id> (<type>, <audience>)`, `<verb>` one of `verify`, `record`, `prepare`; body `Unit: <unit-id>`, `Page: <page path>`, and, for a user unit, `Walkthrough: <id>` (R23).
- **The token** `claims-unresolved` (Q1, BF §4).
- **The apply brief** (S2-D7): a brief carrying `answers` as a top-level field of its own; `unit-brief.md` §2.1 (fields), §3.4 (`doc-writer`), §4.6 (`doc-reviewer`). Its new fields: `answers` `{backend, source, readings | steps, images}`; `coverage` (batch 3); `page_before`; `review_findings` (repair only); reviewer-only `fixer_reports`, with §4.1's `written_paths`, `style_check_report`, `gate_ledger`, `build_summary`, `claims_file`.
- **`answers`**: `backend` `engineering` (batch 2) or `user` (batch 3); `source` one line; engineering `readings: [{quote, line, outcome, observed?, source: {kind: code, repo, path, lines, commit} | {kind: artifact, path, commit}}]`; user `steps: [{n, outcome, observed?}]`; `images: [{slot, ref, shows}]` (batch 3; `[]` before). Only `confirmed` and `differs` reach a brief (the move test keeps the rest off it; R12).
- **The agents**: `docs-workflows:claim-reader` (Task 2.1; `tools: ["Read", "Grep", "Glob"]`), `docs-workflows:walkthrough-composer` (Task 3.2; `tools: ["Read"]`), each dispatched with an explicit `model:` on the §2 Opus chain, as DW:134 passes `doc-writer`'s; neither carries a `model:` key.

### Exact copy

Fenced blocks are the text to write, character for character; the fence is not part of it.

**The command's frontmatter `description`**, batch 2 (597 characters; the warning is at 600):
`Verifies one drafted documentation backlog unit, named by id or the next actionable one, by its audience's method: in this release, an engineering page's claims read by an Opus claim reader in the code at today's commit and in its ARD on the specs default branch. Applies the readings through doc-writer, removes the page's not-yet-verified marker, runs the style check, the build and an Opus review, and commits the page and the unit's move to verified in one commit on a branch. A unit whose claims do not resolve stays drafted, blocked and recorded. Offers one push; never opens a pull request.`

Batch 3 replaces it (597):
`Verifies one drafted documentation backlog unit, by id or the next actionable one, by its audience's method: a user page walked in this session from a walkthrough composed or extended to cover every claim, an engineering page read by an Opus claim reader in the code at today's commit. Applies the answers through doc-writer, removes the not-yet-verified marker, runs the style check, the build and an Opus review, and commits the page, its walk and the move to verified in one commit on a branch. A unit that cannot resolve stays drafted and recorded. Offers one push; never opens a pull request.`

Batch 4 replaces, in batch 3's text, `one drafted documentation backlog unit` with `one drafted backlog unit` and `a user page walked in this session from a walkthrough composed or extended to cover every claim` with `a user page walked here, or after --prepare outside the session, from a walkthrough covering every claim` (592).

**Signature:** batch 2 and 3 `/docs-verify <unit-id>|--next [--docs-repo <path>] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]`; batch 4 adds `[--prepare]` after the selector.

**The plugin `description`** (`plugin.json` and `marketplace.json` alike). Batch 2 replaces, in today's text: `a Material for MkDocs skeleton, public and internal builds, Vale, CI and a docs-profile.yml` → `a MkDocs skeleton, public and internal builds, Vale, CI and a profile`; `/docs-brand extracts a logo and colour pair from the product's code and applies them, WCAG contrast-checked.` → `/docs-brand applies a logo and colours taken from the product's code, contrast-checked.`; `/docs-write drafts a unit's page from its evidence and commits it on a branch, each behind an Opus review gate.` → `/docs-write drafts a unit's page from its evidence, and /docs-verify reads an engineering page's claims in the code, each committing on a branch behind an Opus review gate.`; `/docs-profile refreshes a docs repository's machine-readable profile;` → `/docs-profile refreshes the repository's profile;` (893 characters). Batch 3 replaces `/docs-verify reads an engineering page's claims in the code,` with `/docs-verify resolves its claims by a code read or a walk,` (891).

**Arrays** (each 2–4 options, no "Other"):
- Phase 3, the consent: `choices: ["Verify it (Recommended)", "Cancel"]`; under `--prepare` (batch 4): `choices: ["Prepare it (Recommended)", "Cancel"]`.
- Phase 5, the scans' escalations, reproduced as DW Phase 4 step 3 reproduces them and for its reason: *Dirty working tree* `choices: ["Stash changes and retry this repo", "Skip this repo", "Cancel"]`; *Refresh blocked* on a read by ref `choices: ["Skip this repo", "Cancel"]`.
- Phase 5, a claim on which a specs document and the code disagree (Q1, N4), one per claim: `choices: ["Document as the code reads (Recommended)", "Leave it undecided — the unit stays drafted"]`
- Phase 5, the readings (S2-D5): `choices: ["Apply these readings (Recommended)", "Cancel"]`
- Phase 5, each step of a user walk (P-D11, Q3): `choices: ["confirmed", "differs — I'll type what I saw", "blocked — I'll say why", "Stop — keep these answers for a later run"]`
- Phase 5, recorded answers that count (P-D11): `choices: ["Take these answers (Recommended)", "Walk it again here", "Cancel"]`
- Phase 5, an image slot (S2-D4): under `in-repo` `choices: ["I have it — I'll give the file", "Skip — the slot keeps its placeholder"]`; under `object-store` and `cdn` `choices: ["I have it — I'll give the URL", "Skip — the slot keeps its placeholder"]`
- Phase 5, the fitness question (P-D12), nothing recommended: `choices: ["They show nothing that must not be published", "Cancel — nothing is published, and the walk is recorded"]`
- Phase 7, violations left (as DW Phase 6): `choices: ["Proceed to review anyway — reviewer may still PASS", "Show remaining violations and let me fix manually", "Cancel"]`
- Phase 9, a review that stayed blocked (R9): engineering `choices: ["Provide manual fix notes (you'll be prompted)", "Defer — the unit does not move, and the report records the finding", "Override and accept the finding (you'll be prompted for the rationale)", "Cancel the whole run"]`; user `choices: ["Provide manual fix notes (you'll be prompted)", "Defer — the unit does not move, and the walk is recorded", "Override and accept the finding (you'll be prompted for the rationale)", "Cancel the whole run"]`. The command says it uses its own list, since `escalation-rules`' `/document` list's *Defer* names `/document`'s report.
- Cited, never reproduced: FH §6.2's adopt, name and clean-tree arrays; FH §3's push array (through §6.5); `finding-triage`'s settle prompts; `escalation-rules`' unspent re-review offer, *Repo missing (after resolution)*, *Refresh blocked* on any other repository, *Read-only mount — ref stale or diverged*; `gate-ledger` §5's conversion; `toolchain-preflight`'s missing-tool question.

**`unit-brief.md` §1**, batch 2 — the list becomes:

```text
**`doc-writer`**

- *Inputs*, its closing paragraph on discrepancy application included → §3.1, or §3.4 under an apply brief
- *Entry validation (BLOCKED, never guess)* → §3.2, or §3.4 under an apply brief
- *Write mechanics*, steps 2, 4, 5 and 7 → §3.3, or §3.4 under an apply brief

**`doc-reviewer`**

- *Inputs*, its closing refusal included → §4.1, or §4.6 under an apply brief
- *Review method*, step 2 → §4.2, or §4.6 under an apply brief
- *Review dimensions*, the rows Factual correctness, Completeness vs plan, Coverage, YAML frontmatter, Repo authoring guidance, Repo verification gates, Screenshots, Snippets and Verification-gate integrity → §4.3, or, for each row §4.6 gives, §4.6 under an apply brief
- *Review dimensions*, the row Source-code accuracy → §4.6, under an apply brief only
- *Hard rules*, the bullet opening "If the `doc-planner` checklist references a topic" → §4.4, or §4.6 under an apply brief
- *Output*, the three lines under `### Recommended next step` → §4.5, or §4.6 under an apply brief

**An apply brief** is a brief that carries `answers` as a top-level field of its own, besides `brief_kind: unit`: `/docs-workflows:docs-verify`'s (§2.1). Where `answers` is met only inside another field's value, the brief is no apply brief.
```

**`gate-ledger.md` §10**, batch 2, appended after §9:

```text
## 10. The `/docs-verify` gate registry

`/docs-workflows:docs-verify` adopts the ledger as §7 says, with §9's four gates. Its **Phase** column is `/docs-verify`'s own: 0 is its Resolve phase, 7 its Style phase, 8 its Build phase.

| Gate id | Phase | Precondition | Primary | Fallback |
|---|---|---|---|---|
| `toolchain_preflight` | 0 | as §9 | as §9 | none |
| `repo_checklist` | 7 | as §9 | `repo_verification_gates` applied to the page | none |
| `style_check` | 7 | as §9 | as §9 | `prose-style-checker` alone |
| `build_check` | 8 | as §9 | as §9 | none |

§9's paragraphs *One ledger per unit* and *`build_check` decides whether the unit moves*, and its last paragraph, hold here as written, `/docs-verify`'s phases in place of `/docs-write`'s: a run verifies one unit, so it keeps one ledger. The block goes to `doc-reviewer` under an apply brief, whose Verification-gate integrity row reads it against this section and §6 (`docs-iteration/unit-brief.md` §4.6).
```

**The selection refusal of a user unit**, batch 2 only (R17):
`DOCS_VERIFY_USER_UNIT: <id> is a user page, which this release does not walk — verify it by hand as the documentation route's step 6 says, or wait for the next docs-workflows release, which walks it here.`

**G1**, in `workflows-core-git.md:26`: `the thirty-six commands that write` → `the thirty-seven commands that write`; `the family's thirty-nine except` → `the family's forty except`; `returns the same thirty-six:` → `returns the same thirty-seven:`; ``six of `docs-workflows`'s eight`` → ``seven of `docs-workflows`'s nine``. Nothing else on the line.
**G2**, in `workflows-core-git.md:32`: `nineteen of the thirty-six callers` → `twenty of the thirty-seven callers`; `ten of the thirty-six also resolve` → `ten of the thirty-seven also resolve`; `Nineteen is all thirty-six minus the seventeen` → `Twenty is all thirty-seven minus the seventeen`. The "joined" sentence stands.
**G3**, in `specs-repo-git.md:310`: `` `/docs-audit`, `/docs-write`, the four logging commands `` → `` `/docs-audit`, `/docs-write`, `/docs-verify`, the four logging commands ``.
**G4**, in `phase-handoff.md:628`: `` save by `/docs-workflows:docs-write`, which refuses there the backlog unit that cites the file. `` → `` save by `/docs-workflows:docs-write` and `/docs-workflows:docs-verify`, each of which refuses there the backlog unit that cites the file. ``; then `python3 scripts/reference-parts.py generate`, which rewrites `reference-parts/phase-handoff/require-on-main.md`.

**`CLAUDE.md`**, each edit in the `docs-workflows` paragraph or the `docs-grounding.md` row: batch 1 `twenty-five reference files` → `twenty-six reference files` (35,839); batch 2 `provides eight slash commands` → `provides nine slash commands`, `plus eleven subagents` → `plus twelve subagents`, `25 command files` → `26 command files`, `fourteen that resolve none` → `fifteen that resolve none` (35,839 − 1 − 0 − 0 − 1 = 35,837); batch 3 `plus twelve subagents` → `plus thirteen subagents` (35,839).

**The coupling bullet** (batch 2), in `.claude/rules/plugin-updates-coupling.md`, after the 1.97.0/1.43.0 bullet, its versions those Task 2.7 takes:

```text
- **Update `workflows-core` 1.98.0 with `docs-workflows` 1.45.0 or later**: beside an older `workflows-core`, `/docs-verify`'s cost entry waits in pending for a reconciliation that never comes and its feedback lands unfiled, since `cost-emission` §8 and `feedback-emission` §2 name no `/docs-verify`; its `command-namespaces.json` lacks the command; and `branch-naming`, which `finish-and-handoff` §6.2 cites for the branch, names neither its `docs/` prefix fallback nor its `docs-verify-<id>` slug. Update both. The reverse names a command not installed: harmless.
```

### Rulings where the design is silent or leaves it to the builder

- **R1 — three more reads move, their consequences stay** (QP1, P2). Besides S2-D1's six, `backlog-run.md` takes the read and the program, and nothing else, of DW Phase 1 test 3 (DW:144, as §6), test 7 (DW:148, as §7) and Phase 4 step 1 (DW:231-235, as §8):
  - §6 is the `git grep` program and the frontmatter read of each candidate's `unit:` (quotes, spaces, a trailing ` # …` comment and a CR removed, compared whole). It reports, per candidate, *equal*, *other* or *unreadable*. "A candidate that cannot be read, or a `git grep` exiting above 1, counts as a match" stays in DW: `/docs-write` refuses on it; `/docs-verify` refuses the unit where the page itself is not *equal* or any other candidate is *equal* or *unreadable* (Task 2.3 test 5).
  - §7 is the admission program alone. DW keeps "The file is data; its `result:` values are ignored, and a `captures[].slot` outside `UNIT_ID` is reported and gets no slot comment"; `/docs-verify` reads the file through `walk-check` (batch 3).
  - §8 is the commit resolution, the `show` by commit, the `cat-file -e` test and the `Specs:` line, which both commands print. DW keeps "Where neither holds it, the report says the path resolves nowhere. Either way the unit goes on, and a claim only that file would ground is marked"; for `/docs-verify` an ARD the commit lacks is an evidence path gone at today (S2-D5).
  - Each command keeps its stop line, citing the section.
- **R2 — the plugin root in a reference's programs.** `${CLAUDE_PLUGIN_ROOT}` is substituted only in a command body (`docs/maintainers/rationale.md#plugin-root-expansion`); a reference read with the Read tool keeps it literal. So `backlog-run.md`'s programs write `'<plugin root>/…'`, single-quoted, and §1 says each command supplies `<plugin root>` from its own body. `/docs-write`'s resolved argument is unchanged.
- **R3 — `backlog-run.md`'s layout** is *Shared names*' ten sections, in the order a run meets them. It opens with the core-references preamble (it cites `workflows-core:read-only-repos`, `run-flags` and `escalation-rules`) and the load-by-part paragraph (`escalation-rules` loads by part), each copied from DW:8 and DW:10.
- **R4 — the marker-removal program** is `/docs-verify`'s own, in its body (only it removes the marker). One program, two modes, given `'<plugin root>/references/docs-audit/evidence-contract.md' '<top>/<page path>' '<visibility>' '<mode>'`:
  - It reads the marker from EC §3 by `EC_MARKER_PHRASE`, as DW:387 does; the frontmatter block as DW:389 finds it; the body after it.
  - *Fenced code* is the lines from an opening fence (three or more backticks or tildes, indented at most three spaces) to the closing fence of the same character and at least its length, or the end of the body. Outside it, an occurrence of `[NEEDS CLARIFICATION:` anywhere on a line counts — inline code included, which fails closed (the design's last risk: a page quoting the marker in inline code cannot be verified by command).
  - `remove`: exits 0 having deleted the marker line and the line after it where that line is blank, only where the first non-blank body line (after the visibility marker on an internal page) is the marker byte for byte and no other occurrence stands outside fenced code; writes through a temporary file in the page's directory renamed over it, keeping every other byte and the line endings; exits 1 writing nothing otherwise.
  - `check`: exits 0 where no occurrence stands outside fenced code, writing nothing; 1 otherwise.
  - The selftest pins the phrase in it: `backlog-run.md` holds two programs, `docs-verify.md` one, `docs-write.md` none.
- **R5 — the visibility marker pinned.** `<!-- docs-visibility: internal -->` is page text three programs match (§10.2's, and `/docs-verify`'s two). A new selftest case holds `visibility.md` §5's statement of it and each program's literal, byte for byte.
- **R6 — FH §6 in batch 1 names no later command.** Batch 1 generalises §6's wording so it reads the same for `/docs-write` and leaves each command to name its verb and its created and edited paths; batch 2 names `/docs-verify` and its paths; batch 3 adds images and the walkthrough; batch 4 the prepare commit.
- **R7 — two more selection tests.** S2-D2 test 5 also runs §10.2's test on the page (the marker present as its first body line): `DOCS_VERIFY_NO_PAGE_MARKER`, naming route step 6's by-hand move, so no Opus is spent on a page Phase 6 would refuse. And (batch 3) a walkthrough whose `walkthrough.unit` is not the unit id is refused, named or found at the fixed-id path alike: a walk of another unit's page verifies nothing here.
- **R8 — an unread repository.** *Skip this repo* at a scan escalation or at *Repo missing*, an export over R30's cap or past its timeout, and an evidence path the export reports `skipped` each leave that repository, or that path, unread. The reader is handed no export of it; each claim resting only on it is `not read`, outside Q1's three cases: the move test fails, no token is written, an engineering run commits nothing, and the report names the repository and why. A token for an environment the run could not reach would block the unit everywhere once merged. **Where a run has both an unread repository and a Q1 case** (an `unresolvable` claim, an evidence path gone, a `specs-vs-code` claim left undecided), **R8 wins** (m3): no token, nothing committed, the report listing both, since the reading is incomplete and a later run with the repository may resolve what this one could not.
- **R9 — *Defer*'s wording by backend** (*Exact copy*): an engineering run records no walk.
- **R10 — Phase 10 re-tests.** The frontmatter program (S2-D8 step 2) and R4's `check` run again immediately before the backlog's copy, since a fixer or notes can follow the last review; either failing ends the unit.
- **R11 — the walkthrough in the verify commit.** It is among the commit's paths wherever `git -C '<top>' status --porcelain -z -- ':(literal).dev-workflows/walkthroughs/<id>.yml'` prints anything at Phase 10 — changed by this run, or uncommitted answers taken behind the question — so the commit's tree holds the results either way (S2-D6, *P-D8, read soundly*).
- **R12 — a `specs-vs-code` claim answered *Document as the code reads*** reaches the brief as a `differs` reading whose `observed` is the code's phrasing; `doc-writer` rewrites to it, which changes nothing where the page already says it. The decision is recorded in the report and §6.6's draft, as SRC §7.4 records one.
- **R13 — the page's blob** (S2-D9) is computed in `/docs-verify`'s body, named once as *The page's blob* — `git -C '<top>' hash-object --path='<page path>' -- './<page path>'`, held to `OBJECT_ID` — and used at Phase 1, Phase 4's re-check, the stamp's write (`walk-stamp --blob`) and the stamp's test (compared with `walk-check`'s printed `stamp.blob`). The script never hashes the page.
- **R14 — the walk verbs' exits** are 0, 2 and 3, with no 4: a composed walkthrough is untracked, so no `git diff` can hold the write. Each verb instead checks, before it writes, that every line it does not write is byte-equal and in order, writes through a temporary file renamed over the walkthrough, and reads the result back. A walk verb exiting 2 stops the run (`DOCS_VERIFY_WALK_WRITE`, the script's one line quoted), **makes no record commit** — the file's state is unknown — and the report names the file.
- **R15 — images.** An absent `images` block asks no slot question; each slot is reported unfilled. A present one out of class stops at Phase 0 (`DOCS_VERIFY_PROFILE_IMAGES`, naming the field). The image extensions are *Shared names*'.
- **R16 — MR §9.2's synthesis row names `claim-reader`** (batch 2), so its *Reader* row (§2.1 Sonnet) is never read to cover it. `walkthrough-composer` is a planner by that row's own words, and is not named in batch 2's `workflows-core` release.
- **R17 — batch 2's user-unit refusal** names "the next docs-workflows release", never a version (*Exact copy*); batch 3 deletes it, a claim-expiry hit its sweep counts.
- **R18 — `edit --block`'s refusals** are `blocked` (a value neither empty nor `[]`, a block sequence included) and `no-blocked-by` (no `blocked_by:` line); its token takes the status class less the reserved words.
- **R19 — the export, and a reader with no shell** (QP3, P1). The orchestrator writes each commit `claim-reader` reads into `<export root>` with `backlog-lines.py export` (Task 2.1): per clone, today's whole tree (`--whole`, every code evidence path of that clone as a `--path` whose state it reports); per distinct recorded `ref` of a clone other than today, the evidence paths recorded at it (`--path` alone). Every value it hands the program is class-tested first and single-quoted: the clone's resolved path (`abs-path`, both parts of the clone test, admitted), the commit (`OBJECT_ID`), each path (`rel-path`), `--out` and `--manifest` under `<export root>`. The reader gets the export directories, the page's copy and the handoff, all under `<export root>`. Its tool list holds that it writes nothing and runs nothing, so no page text and no file name from a repository ever reaches a shell line; its prompt holds that it reads under `<export root>` alone, and it holds no tool that could carry anything elsewhere. A commit the clone lacks is reported by the program (`commit-absent`), so the read at that `ref` is `not read`.
- **R20 — the walkthrough's line shape** (EC §4's new paragraph, Task 3.1) is BF §1's line rules, cap 1 MiB, plus the structure Task 3.1 states.
- **R21 — `--prepare` before batch 4** is an unknown flag (`DOCS_VERIFY_UNKNOWN_FLAG`): no page or line mentions it until batch 4.
- **R22 — an engineering Q1 exit** commits the backlog alone (`record`), after which Phase 11 offers the push and §6.6 prints the draft; nothing on the page changes.
- **R23 — the commit bodies** carry `Walkthrough: <id>` for a user unit; no other value read from the backlog enters a message.
- **R24 — the composer's return, held by the orchestrator** before anything shows or writes it: `status` `DONE`; every `action` one of the five verbs; every string one line (no character `walk-record` refuses) and at most 500 characters; `target` a string or a mapping, `expect` a mapping with `kind`, their keys `^[a-z_][a-z0-9_]{0,31}$`; at most 200 steps in the file once appended; `role` one of the unit's `roles` (compose); every coverage entry's steps naming a step that exists or is appended. A return that fails is an agent failure: the run ends, nothing written.
- **R25 — a `missing` unit's refusal in a `<unit-id>` run** names `moved`'s refs only where `<base>` resolves; otherwise it says no unmerged branch was read. A `moved` that does not answer leaves the refusal saying the branches could not be read; the refusal stands either way.
- **R26 — two rules sentences outside GIT-G1** become incomplete with `/docs-verify` and are swept in batch 2: `workflows-core-read-only.md:24` ("The ten commands that … name `prep.read_only`"; the docs-repository commands that cite §3 for the default branch) and `docs-workflows.md:73` ("which `/docs-audit` and `/docs-write` take"). Sub-project 1's R26 established the first file is not GIT-G1.
- **R27 — the reader's sources, held to a known set** (P3). Before a reading's `source` reaches the readings question, the brief or an `evidence:` entry: a code source's `file` must lie under the today export of one of the clones handed over, `<export root>/c<k>/`, and its remainder must be a written path that export's manifest lists, whole — a known set, tested by a program given `'<manifest>' '<remainder>'`, which prints the repository path paired with it — and that repository path, which passes `rel-path`, is the `path`, and the clone's `repo` and `today` fill the rest. An artifact source's `path` must pass `ARTIFACT_PATH` and equal one of the artifacts handed over. `lines` must match `^[0-9]{1,7}-[0-9]{1,7}$` with the first at least 1 and not above the second, and the second not above the cited file's line count in the export (n4: a program given `'<export root>/c<k>/<path>'` prints the count; an artifact's against `text_today`'s); `commit` must be the clone's today or the artifact's `today_ref`. A return with any source failing is unusable: the run ends, nothing written.
- **R28 — a record commit with nothing to record** (P4). Before §6.3, where `git -C '<top>' status --porcelain -z -- ':(literal).dev-workflows/walkthroughs/<id>.yml' ':(literal).dev-workflows/docs-backlog.yml'` prints nothing — answers taken from a commit, then a later end — no commit is made, §6.3 is not run, and the report says the walk is already committed and names the commit `git log -1` gives for the walkthrough. The same test guards the engineering record commit, which a token always changes.
- **R29 — the reader's techniques, handed over.** `claim-reader` holds no `Skill` tool, so it cannot load a `workflows-core` reference, and it cites none (check 16 holds that both ways). The orchestrator, which holds `Skill`, loads `workflows-core:source-truth` and writes into the handoff, as top-level literal blocks no value read from data can supply (UB:33's reasoning for `brief_kind`): `techniques`, §3 (SRC:126-222) as it reads, and `outcomes`, §4.2 step 4's mapping (SRC:250-261). The agent's body names those two fields as the plugin reference text its caller hands it, to follow; every other field is data. One prose copy stands: the reference; the handoff holds a copy for one dispatch. **§3's recipes are shell, and the reader has none** (N2), so its body carries the translation once (Task 2.1, *Running the techniques*): each recipe runs as Grep and Glob over the clone's export directory alone; two recipes are never run — §3.0's `grep -rn … <spec_dir>`, since the ARD's text is in the handoff and no other specs document is the reader's (BKR invariant 5), and §3.7's third, `grep -rn "<command-head>" <docs_repo_path>`, since the docs repository is not the reader's to read.
- **R30 — the export's caps, and where the program lives.** A file above **1 MiB (1,048,576 bytes)** is skipped and counted `large`; an export above **50,000 files or 512 MiB (536,870,912 bytes)** of the files it would write is refused before anything is written (`over-cap`); `cat-file --batch` runs within **300 seconds** (`timeout`). Each refusal makes that repository `not read` (R8). The reason, measured at plan time over the code repositories on the maintainer's machine (`git ls-tree -r -l HEAD`): the largest holds 5,825 tracked files and 95 MiB in the files at or under 1 MiB; nine of them hold 10 files above 1 MiB in about 18,000, every one generated, minified or data. 1 MiB is the cap the script already sets on a backlog read from a ref (`REF_CAP`) and on a walkthrough, and source a page's claim rests on sits far under it; 50,000 files and 512 MiB are over eight and five times the largest measured, so a large application repository is read, and a monorepo above them is not read by command, which the consent and the report say. The program lives in `backlog-lines.py` because the existing *Self-test the backlog line reader* step then runs its cases; a script of its own would need a new CI step, a GIT-G1 edit the controller ruled out (QP2).
- **R31 — what the search tools see** (N1). The reader finds files with Grep and Glob, whose defaults may skip a dot-directory and honour an ignore file — inside the export or in any parent of `<export root>`. A file it cannot see reads as "not found", which is `unresolvable` and would write the token. Four measures:
  - **No ignore file is written under its own name**: `export` writes a file whose base name is `.gitignore`, `.ignore` or `.rgignore` as that name plus `.exported`, the manifest pairing it with its repository path, so its content stays readable and no rule inside an export applies — and, since nothing is skipped for it, a claim resting on one is never `not read` on that account (R32).
  - **Parent ignore files are neutralised**: before the first export the command writes `<export root>/.ignore`, one line `!*`, which an ignore-honouring search reads as closer to every exported path than any parent rule, and so as the rule that wins — and which, for a search built on the common ignore library, also lifts its hidden-file filter. It is the command's file, never a repository's.
  - **A build-time probe** (Task 2.1 Step 5) settles, in a live session, what the harness's Grep and Glob find under such a root. Where either misses a dot-directory or a parent-ignored file with the root `.ignore` in place, the task stops and reports to the controller, proposing the fallback named there; nothing ships around a failed probe.
  - **A run-time canary** (Task 2.3 Phase 5 step 4) carries the guarantee on every run: the command plants `<export root>/canary/.hidden/canary-hidden.txt` (under a dot-directory) and `<export root>/canary/node_modules/canary-ignored.log` (a path ordinary ignore rules match: `node_modules/`, `*.log`), each holding one line, a token the run made; its own Grep for the token and Glob for `**/canary-*`, each over `<export root>/canary` — whose ancestors, and so whose ignore rules and hidden-file handling, are those of every export beside it — must each list exactly those two files, and the reader's first act repeats both searches and returns what it found (the handoff, which also holds the token, lies outside that directory). Any miss is a stop, `DOCS_VERIFY_EXPORT`, before any claim is graded:
    `DOCS_VERIFY_EXPORT: the search tools did not find <each canary file missed> under the export root — a hidden directory or an ignore rule there would hide files from the claim reader, so no claim was graded and nothing was written.`
- **R32 — a skipped file is never "not found"** (n1). Each today export's `skipped` counts go to the reader (per clone) and to the report. Where any today export of the run skipped a file — a link, a submodule, another mode, a name, a large file — every claim the reader grades `unresolvable` with `why.kind: not-found` is `not read` (R8): no token, nothing committed, the report printing the clone's counts beside the claim. A claim not found in a repository the export took whole stays Q1's.
- **R-I11 — the plan-time frontmatter check** (S2-D5, design I11), and why it led to QP3. Agent frontmatter cannot deny an agent anything but whole tools:
  - `claude plugin validate .` (2.1.323), run on a scratch plugin, passed an agent with `tools: Read, Bash(git grep *), …`, one with `disallowedTools: Write, Edit`, and one with an unknown key `frobnicate` alike — it does not check agent frontmatter keys, so its pass is no evidence.
  - The harness's own subagent documentation (its *sub-agents* page): `tools` takes tool names, with a specifier form only for an MCP-server glob and `Agent(type)`, the latter ignored in a subagent; `disallowedTools` exists, but an entry with a specifier such as `Bash(git push *)` removes the whole tool; `hooks`, `mcpServers` and `permissionMode` are ignored for plugin subagents.
  - The family's 56 `tools:` lines (`command grep -h '^tools:' plugins/*/agents/*.md`) hold no specifier and no agent has `disallowedTools` — the design's assumption, re-counted.
  - A plugin-wide `PreToolUse` hook could filter Bash, but it would run on every Bash call of every session with the plugin enabled and block — against `CLAUDE.md`'s "Hook scripts must exit 0". Not taken.
  - **So a Bash-holding reader could be held read-only by its prompt alone.** The maintainer's QP3 answer takes Bash away instead (R19): `claim-reader`'s frontmatter is `tools: ["Read", "Grep", "Glob"]`, its read-only rule is held by that list, and the residual the design named — the one `code-scanner` still carries (CS:139-142) — is gone for this agent. The residual left is narrower, and is named in batch 2's CHANGELOG (Task 2.7): Read, Grep and Glob can reach any path the session can, and only its prompt confines the reader to `<export root>`; it writes, runs and sends nothing, its `source` is held to the manifest (R27) and its `outcome` and `line` to classes, and its one free-text output, `observed`, reaches the page only after the readings question has shown every `differs` phrasing to the operator, then the reviewer and the pull request. That is the exposure `doc-writer` and `walkthrough-composer` carry. What search hides from it is R31's.

## Review Focus

Inputs a reasonable operator will meet that no gate exercises, most likely first. Each has its test in the owning task.

| # | Input | Expected | Test |
|---|---|---|---|
| RF1 | `--next` while another `/docs-write` draft branch is still open, cut before the candidate was drafted | The candidate is chosen; only a branch that itself moved the unit passes it over | 1.1 `own_moves_open_draft_branch`; 2.3 T-C1 |
| RF2 | A how-to page with one "why" sentence, or an `explanation` page | Q1's exit before any write: token, record commit, each claim and why, route step 6 named | 3.3 T-U3 |
| RF3 | Observed text holding `"`, `\`, a bidi control, Markdown or HTML | One escaped line in the file; applied as words; the reviewer blocks markup it brought in | 3.1 `walk_record_escapes`, `walk_record_markup_is_text`; 3.3 T-U9 |
| RF4 | The session dies, or the operator stops, mid-walk | Every answer already in the file; the next run takes them behind the question and walks the rest | 3.3 T-U4, T-U5 |
| RF5 | A page with CRLF endings committed before `* text=auto`, or `core.autocrlf` changed between a prepare and the take | Equal blobs where settings are the same; otherwise the answers do not count, "line-ending or filter settings changed", fail closed | 3.3 T-U8; 4.1 T-P2 |
| RF6 | The docs repository is also a source repository (a `site/` beside the code) | Read by ref with settings of its own; the run's branch never moves | 2.3 T-E8 |
| RF7 | A hand-written walkthrough in a layout the reader does not take — a block scalar note, a `- action:` step opener | A stop naming the line and the reason, before any consent | 3.1 `walk_block_scalar_out`, `walk_step_opener_out`; 3.3 T-U16 |
| RF8 | A drafted page someone already verified by hand (marker removed, unit still `drafted`) | Refused at selection, naming the by-hand move, no Opus spent | 2.3 T-NOMARK |
| RF9 | A large source repository — a monorepo, or one carrying a generated bundle or a symlinked directory | Under R30's caps it is read, the bundle and the link skipped and counted; over them it is `not read`, named in the report, no token | 2.1 `export_over_cap`, `export_large_file_skipped`, `export_links_not_followed`; 2.3 T-CAP |
| RF10 | A claim grounded in `.github/workflows/`, `.env.example` or a `node_modules/` path, in a session whose scratchpad sits under an ignore file | Found by the reader's Grep and Glob; where the tools cannot see such a file, the run stops before grading, `DOCS_VERIFY_EXPORT`, and never writes the token | 2.1 Step 5's probe; 2.3 T-CANARY |

---

# Batch 1 — groundwork (`feat/doc-d-g1-docs-verify`)

`/docs-write`'s behaviour is unchanged. *Usable:* the same `/docs-write`, and the script flags the later batches call.

### Task 1.1: The line reader's new flags [security-sensitive]

**Files:**
- Modify `plugins/docs-workflows/scripts/backlog-lines.py`: the docstring (usage lines, `moved`'s and `edit`'s paragraphs, the refusal words, the arguments' classes), `SINGLE_FLAGS`, `_args`, `cmd_moved`, `_ref_blob`, `cmd_edit`, the selftest.
- Modify `.claude/rules/docs-workflows-backlog.md` invariant 1: one sentence — the new flags are tested with the script, and `/docs-write` passes none of them (S2-D14).

**Interfaces** (Tasks 2.3 and 3.3 call these exactly; without a new flag every output is byte-identical to today's):
- **`moved --repo <top> --base <name> --id <id> [--id <id> …] [--own-moves]`**. `--own-moves` is a bare flag, refused given twice or as `--own-moves=…` (exit 2, `WHY_USAGE`). With it, a kept ref moves a unit only where the unit's status there differs from the working status **and** from its status at the ref's merge base with the base (`git merge-base <base_oid> <oid>`, already computed in `_ref_blob`):
  - the merge base's backlog is read by object id within today's limits — a file mode, a blob, at most 1 MiB, in shape, each `--id` at most once with a status in `^[a-z][a-z-]{0,31}$` — and anything else makes the ref `unreadable`;
  - no backlog at the merge base, or the unit absent there, counts as a status that differs;
  - a ref sharing no merge base counts as today;
  - the JSON keys and their meanings are unchanged.
- **`edit --repo <top> --id <id> --status <s> [--page-path <rel>] [--from <status>] [--walkthrough <id>] [--block <token>]`**, each new flag at most once:
  - `--from` (status class less the reserved words, else exit 2 `--from is outside the status class`): exit 3 `{"refused": "status-differs", "line": <status line>, "reason": null}`, file untouched, where the entry's `status:` text is not it. Tested after `id-absent`/`id-twice`, before anything is computed.
  - `--walkthrough` (`UNIT_ID`, else exit 2): no `walkthrough:` line in the entry → exit 3 `no-walkthrough` (the entry's first line); `null`, `~` or an empty value with no child → set to the id; equal to the id as `_scalar_text` reads it → unchanged; anything else, a child block included → exit 3 `walkthrough-set` (its line).
  - `--block` (R18; else exit 2): no `blocked_by:` line → exit 3 `no-blocked-by`; an empty value with no child, or flow `[]` → set to `[<token>]`; anything else → exit 3 `blocked`.
  - The read-back check (`after = read_shape(new_data)`) also holds each new key's value to what was asked; the hunk check holds the up-to-four changed lines inside the entry as today; an edit that changes nothing exits 0 with `changed: []`, writing nothing (`edit_noop`'s rule).
- `/docs-verify`'s record commit calls `edit --id '<id>' --from drafted --status drafted [--walkthrough '<id>'] [--block claims-unresolved]`; its verify commit `edit --id '<id>' --from drafted --status verified [--walkthrough '<id>']`.

- [ ] **Step 1: Before counts.** `python3 plugins/docs-workflows/scripts/backlog-lines.py --selftest` → `selftest: 57 passed`. Run each of today's `moved` and `edit` cases' fixtures once and keep their stdout bytes (for Step 4's identity check).
- [ ] **Step 2: The failing cases**, added to `CASES` before the two pinning cases, each name then its assertion. A fixture `MINI_W` is `MINI` with `    walkthrough: null` after `page_path:`.
  - `own_moves_open_draft_branch` (C1): `main` has `U-001` `drafted`, `U-002` `missing`; `docs/w-u-002` cut when `U-001` was `missing` moved `U-002` to `drafted`; `docs/v-u-003` moved `U-003` `drafted`→`verified`. `moved --id U-001 --id U-003` without the flag → both moved; with it → `{"U-003": ["docs/v-u-003"]}` only.
  - `own_moves_real_move`: a branch moved `U-001` `drafted`→`verified` → moved, flag or not.
  - `own_moves_no_merge_base`: an orphan branch whose backlog differs → moved, as without the flag.
  - `own_moves_merge_base_unreadable`: the merge base's backlog out of shape, then over 1 MiB → the ref in `unreadable` each time, `read` counting it.
  - `own_moves_unchanged_without_flag`: one repository, `moved` without the flag → stdout byte-equal to a literal expected JSON written in the case.
  - `own_moves_bad_args`: `--own-moves` twice, `--own-moves=yes` → exit 2 `WHY_USAGE` each, nothing read.
  - `edit_from_refused`: `U-001` `missing`, `--from drafted --status verified` → exit 3 `status-differs`, its line 6, file byte-equal, mtime kept.
  - `edit_from_ok`: `DRAFTED`, `--from drafted --status verified` → `changed: [6]`.
  - `edit_walkthrough_unset`: `MINI_W` with `null`, `~` and an empty value, each `--walkthrough U-001` → set, every other byte equal, CRLF kept on a CRLF copy.
  - `edit_walkthrough_other`: `walkthrough: W-9` → exit 3 `walkthrough-set`. `edit_walkthrough_same`: `walkthrough: "U-001"` → that line unchanged.
  - `edit_no_walkthrough_key`: `MINI`, `--walkthrough U-001` → exit 3 `no-walkthrough`.
  - `edit_block_sets`: `blocked_by: []` → `blocked_by: [claims-unresolved]`; an empty value → `blocked_by: [claims-unresolved]`.
  - `edit_block_refused`: `blocked_by: [env-down]`, and a block sequence under `blocked_by:` → exit 3 `blocked` each. `edit_no_blocked_by_key` → exit 3 `no-blocked-by`.
  - `edit_record_noop`: `DRAFTED`, `--from drafted --status drafted` → exit 0, `changed: []`, bytes and mtime kept.
  - `edit_new_flags_bad_args`: `--from 'Drafted!'`, `--from null`, `--walkthrough '../x'`, `--block 'a b'`, `--block true`, `--from` twice, `--block=x` → exit 2 each, nothing read or written (`_IO`).
  - `visibility_marker_pinned` (R5): `references/docs-workflow/visibility.md` §5 holds `<!-- docs-visibility: internal -->` on a line of its own once; `docs-write.md` holds `"<!-- docs-visibility: internal -->"` (the Python literal) once. Task 1.2 moves that program and turns this case to `backlog-run.md`.

  Run the selftest. Expected: FAIL naming `own_moves_open_draft_branch`.
- [ ] **Step 3: Implement** to the interfaces. Thread `own_moves` from `_args` into `cmd_moved`, and have `_ref_blob` return the merge base's entry beside the blob when asked; `REASONS` is unchanged.
- [ ] **Step 4: Run.** Expected `selftest: 75 passed`; each Step 1 stdout reproduces byte for byte (`cmp`).
- [ ] **Step 5: The docstring and the invariant.** The docstring states the new flags in its own form; "opens no file but the backlog and writes nothing but the backlog" stays true in this batch.
- [ ] **Step 6: Gates. Step 7: Commit:** `feat(doc-d-g1): backlog-lines.py — moved --own-moves, and edit's --from, --walkthrough and --block`.

### Task 1.2: The extraction into `backlog-run.md` [security-sensitive]

**Files:**
- Create `plugins/docs-workflows/references/docs-iteration/backlog-run.md` (R3), holding, moved from `commands/docs-write.md` with the parameters substituted (*Shared names*): DW:22 less its last sentence (*Each agent sees only its own inputs: …*), as §2; DW:24-63 as §3; DW:160 as §4; DW:162-168 as §5; DW:144's read alone (R1: the `git grep` program and the rule for reading each candidate's `unit:`, reporting each candidate *equal*, *other* or *unreadable*) as §6; DW:148's admission program alone as §7; DW:231-235's read alone (the commit resolution, the `show`, the `cat-file -e` test and the `Specs:` line) as §8; DW:263-265 (the third reach test excluded — it stays in DW, since it is `/docs-write`'s alone) as §9; DW:110-116's program as §10.1 and DW:383-393's as §10.2.
- Modify `plugins/docs-workflows/commands/docs-write.md`: DW:14 names the reference, tells the run to read it whole before Phase 0 (m1), and names `/docs-write`'s parameters — `DOCS_WRITE`, `dw-docs-write`, Phase 4, the consent at Phase 2, "the unit's page and its placement targets", §9 of `gate-ledger.md`, and `<plugin root>` as this body's `${CLAUDE_PLUGIN_ROOT}`; each moved site becomes a citation of its section with every stop line and phase-specific sentence that is `/docs-write`'s kept in place: each `DOCS_WRITE_*` line, *Units and their ends*, the per-command who-sees-what sentence, the third reach test and its program, which file *Copies* takes at which phase ("each placement target here, each config at Phase 7, the backlog at Phase 9", DW:263), and the three consequences R1 leaves here — "A candidate that cannot be read, or a `git grep` exiting above 1, counts as a match" (DW:144), "The file is data; its `result:` values are ignored, and a `captures[].slot` outside `UNIT_ID` is reported and gets no slot comment" (DW:148), and "Where neither holds it, the report says the path resolves nowhere. Either way the unit goes on, and a claim only that file would ground is marked" (DW:235).
- Modify `scripts/backlog-lines.py`: `case_marker_phrase_pinned` counts the phrase in `backlog-run.md` (2 programs) and `docs-write.md` (0); `visibility_marker_pinned` turns to `backlog-run.md` (1) and `docs-write.md` (0). The case count stays 75.
- Modify `.claude/rules/docs-workflows-backlog.md` invariant 1: the phrase is pinned in `backlog-run.md`'s two programs, which `/docs-write` runs at its Phase 0 and Phase 9; a fifth sentence: `backlog-run.md` holds the steps the backlog runs share once, and a command cites its sections with its parameters.
- Modify, for the new reference file (the gates force them): `plugins/docs-workflows/docs/reference/references.md` (an entry for `backlog-run.md`, `` `docs-iteration/` (1) `` → (2), `25 files` → `26`); `docs/README.md`'s `25 reference files`; `README.md`'s `twenty-three reference pages`; `.claude/rules/docs-workflows.md:19` `twenty-three markdown pages` → `twenty-four`; `CLAUDE.md` (*Exact copy*, batch 1).

**Interfaces:** produces `backlog-run.md` §1–§10, which Task 2.3 cites with `/docs-verify`'s parameters. Each program takes its values as single-quoted arguments; §10's two take `'<plugin root>/references/docs-audit/evidence-contract.md'` (R2).

- [ ] **Step 1: Before counts.** In `plugins/docs-workflows/`: `command grep -c 'DOCS_WRITE_' commands/docs-write.md`; `command grep -o 'DOCS_WRITE_[A-Z_]*' commands/docs-write.md | sort -u` (the set of stop codes, saved); `command grep -c "character for character: \`(" commands/docs-write.md` (2); `LC_ALL=C.UTF-8 wc -m commands/docs-write.md` (97,788). From the worktree root, Task 2.3 Step 1's recipes, each `command grep -lF '<phrase>' plugins/*/commands/*.md`, and whether `docs-write.md` is among the files each lists (m4): a moved block must take no counted phrase out of a command body.
- [ ] **Step 2: Write `backlog-run.md`** by moving text, never rewording a rule: each moved sentence keeps its words but for the parameters and the cross-references the move re-points (a "Phase 0 step 7" becomes "the command's content roots", "Phase 4's *Repo missing*" "the scan phase's", "the consent (Phase 2)" "the consent", "Phases 0, 2 and 7" "the phases its command names", "Phase 0 step 9's `DOCS_WRITE_BACKLOG_UNREADABLE`" (DW:63) "the command's `<RUN>_BACKLOG_UNREADABLE`", "each placement target here, each config at Phase 7, the backlog at Phase 9" (DW:263) "each file its command names, before its first edit of it for the unit", "(Phase 4 step 3)" (DW:168) "(the scan phase's handling of a return)", `"${CLAUDE_PLUGIN_ROOT}/…"` `'<plugin root>/…'`). Every other phase number in the moved text is a defect: `command grep -nE 'Phase [0-9]' references/docs-iteration/backlog-run.md` prints nothing. §1 states the parameters and that each command names them once, and that this file restates no step a command's own phases hold.
- [ ] **Step 3: Rewrite DW's sites as citations**, in DW's order; DW keeps its run order and every phase heading.
- [ ] **Step 4: The extraction trace** — the proof that `/docs-write` is unchanged. In the task report:
  1. **Parameter rendering.** Substitute `/docs-write`'s parameters into §2–§10 (`sed`, into the scratchpad) and diff against the removed text (`git show HEAD:plugins/docs-workflows/commands/docs-write.md`). Expected: the only differences are the re-pointed cross-references listed in Step 2 and whitespace from re-flowing; list each.
  2. **Programs, byte for byte.** Each of the six programs (the class test, the containment test, §6's read, §7's admission, §10.1, §10.2) appears in `backlog-run.md` equal to DW's but for `${CLAUDE_PLUGIN_ROOT}` → `<plugin root>` and the quoting R2 sets (`command grep -cF` per program body).
  3. **Stop codes.** The Step 1 set of `DOCS_WRITE_*` codes equals the set DW plus `backlog-run.md` rendered with `DOCS_WRITE` print.
  4. **Sub-project 1's fixtures re-run** against the new text, each quoting its deciding lines now (`backlog-run.md:<n>` and `docs-write.md:<n>`) and reaching the same outcome and stop code: T-N, T-B1, T-HOOK, T-DEC, T-ARTQ, T-CLONE, T-WALK, T-R4, T-NOPY, T-SNAP, T-PROF, T-NONASCII.
  5. **The loader.** No `workflows-core:` reference loses a citation `check-docs` check 16 or `check-citations` counts; `check-questions` still reports 38.
  6. **Both commands' consequences** (P2). `command grep -cF` on each of the three consequence sentences the Files list quotes: 1 in `docs-write.md`, 0 in `backlog-run.md`. Then, for each of §6, §7 and §8, a two-column table: what `/docs-write` does with the section's result (quoting `docs-write.md:<n>`), and what `/docs-verify` will do with it (quoting R1 and Task 2.3, which Task 2.3's traces T-TAGREAD, T-ARDWT and T-U14 then quote from the command) — so the section reads true for both, and neither command's consequence is in it.
- [ ] **Step 5: The selftest's pins** follow; `selftest: 75 passed`.
- [ ] **Step 6: After counts**; Step 1's recipes print the same counts with `docs-write.md` still among each list it was in; sizes of `docs-write.md`, `backlog-run.md`, `docs-workflows.md`, `CLAUDE.md`.
- [ ] **Step 7: Gates. Step 8: Commit:** `refactor(doc-d-g1): the backlog runs' shared steps move to references/docs-iteration/backlog-run.md; /docs-write unchanged`.

### Task 1.3: FH §6, generalised [security-sensitive]

**Files:** `plugins/docs-workflows/references/finish-and-handoff.md` §6 (R6).

**Interfaces:** produces §6's per-command hooks Task 2.3 fills: the commit verb, the created and edited paths, and which commit §6.5 counts.

- [ ] **Step 1: The edits**, each reading as before for `/docs-write`:
  - §6's opening (FH:151): a backlog run's command says which of its phases runs each subsection and names what this section leaves to it — its commit verb, and the paths it hands §6.3 and §6.4. No other command is named.
  - §6.3's opening: "once the page carries its `unit:` line" → "once its command's writes for the unit are made". Step 1's path list and §6.4's opening and step 4 list `/docs-write`'s paths as that command's.
  - §6.3 step 3: the subject is `docs: <verb> <unit-id> (<type>, <audience>)`, the verb the command's — `draft` for `/docs-write`; the `commit_convention` rule and the body unchanged.
  - §6.5: "only where this run committed a unit" → "made a commit"; `<k>`'s sentence counts every commit the run made.
  - §6.1, §6.2 and §6.6 keep their text.
- [ ] **Step 2: Trace** `/docs-write`'s T-N, T-HOOK and T-B1 through §6: each sentence reads to the same act.
- [ ] **Step 3: Gates. Step 4: Commit:** `docs(doc-d-g1): finish-and-handoff §6 names each backlog run's verb and paths`.

### Task 1.4: Sweep and release, batch 1 [mechanical]

**Files:** whatever the sweep finds false; `plugins/docs-workflows/.claude-plugin/plugin.json`, `CHANGELOG.md`, `.claude-plugin/marketplace.json`; `docs/superpowers/to-fix.md`, `docs/superpowers/reviews/2026-10-26-feature-gaps-review.md`.

- [ ] **Step 1: The sweep** (*Global Constraints*), subjects *which commands consume each shared reference* and *the counts*; known sites: EC:7 (its `/docs-write` clause reads §3's marker through `backlog-run.md` §10), BKR:25, `.claude/rules/docs-workflows.md:13`'s split-out list where it names the backlog runs' rules.
- [ ] **Step 2: Merge and versions** (*Release*): `docs-workflows` next free minor (plan time 1.44.0); no other plugin changes; no coupling bullet. The CHANGELOG names `backlog-run.md`, the flags, the pins, and "no behaviour of `/docs-write` changes".
- [ ] **Step 3: `to-fix.md`** under *From DOC-D-G1*: **DW-EDIT-FROM** (S2 *to-fix*, recorded only) and **BASE-MOVED-STALE** (S2 *to-fix*, review 2 §2). **Feature-gaps**: DOC-D-G1's heading (:285) and row (:48) gain sub-project 2's design path and this release.
- [ ] **Step 4: Gates; measure; Step 5: Commit:** `release(doc-d-g1): docs-workflows <X> — the backlog runs' shared steps, and the line reader's new flags`.

### Task 1.5: Close, batch 1 [security-sensitive]

- [ ] **Step 1: Consistency.** `command grep -c "character for character: \`(" plugins/docs-workflows/references/docs-iteration/backlog-run.md plugins/docs-workflows/commands/docs-write.md` → 2 and 0. Every selftest case name in Task 1.1 runs.
- [ ] **Step 2: No regression.** Task 1.2 Step 4's trace re-run against the final tree; every hunk of `git diff origin/main...HEAD -- plugins/docs-workflows/commands plugins/docs-workflows/references` listed with the condition under which it acts; one that changes what `/docs-write` does is a defect.
- [ ] **Step 3: GIT-G1 audit.** `git diff origin/main...HEAD --stat` shows nothing under a GIT-G1 file or `plugins/workflows-core/`.
- [ ] **Step 4: The sweep's counts**, each equal to its intended value; the probe once more.
- [ ] **Step 5: The full CI list**: every `run:` step of `.github/workflows/validate-catalog.yml`, in order, the mermaid gate where `node` exists.
- [ ] **Step 6: The PR text**, for the controller: what moved and the proof; the flags; the controller's QP1 and QP2 rulings; the maintainer's QP3 answer and the design's dated note under S2-D5, which this pull request carries; the versions; the attribution lines the session gives for pull requests. The verification record is written now, after the last fix wave.

---

# Batch 2 — engineering units (`feat/doc-d-g1-verify-engineering`)

*Usable:* an engineering page reaches `verified`; a unit that cannot resolve leaves by Q1's exit. A user unit is refused, naming the next release.

### Task 2.1: The export, and `claim-reader` [security-sensitive]

**Files:**
- Modify `plugins/docs-workflows/scripts/backlog-lines.py`: the `export` verb (R19, R30), its constants `EXPORT_FILE_CAP = 1048576`, `EXPORT_FILES_CAP = 50000`, `EXPORT_BYTES_CAP = 536870912`, `EXPORT_TIMEOUT = 300`, the docstring (a usage line; a paragraph in its form; its opening line names "the export of a source repository's commit for `/docs-verify`'s claim reader"; "opens no file but the backlog and writes nothing but the backlog" becomes "opens no file but the backlog, and writes nothing but the backlog and, for `export`, the files under `--out` and the file `--manifest` names"), the selftest.
- Modify `.claude/rules/docs-workflows-backlog.md` invariant 1: one sentence — `export` lives in the script so the existing CI step runs its cases (R30); it is the one program that reads a source repository for `claim-reader`, never through a shell.
- Create `plugins/docs-workflows/agents/claim-reader.md`.
- Modify `plugins/docs-workflows/docs/reference/agents.md` (a row; its count `eleven` → `twelve`), `docs/README.md`'s agent count, `README.md`'s `Eleven agents`.

**Interfaces** (Task 2.3 calls the verb and dispatches the agent exactly):
- **`export --repo <clone> --commit <oid> --out <dir> --manifest <file> [--whole] [--path <rel> …]`** — at least one of `--whole` and `--path`; every flag but `--path` at most once; no `--flag=value`.
  - **Arguments**, tested before anything is read or run (exit 2 with a fixed line otherwise): `--repo` `abs-path` and a directory; `--commit` `OBJECT_ID`; `--out` and `--manifest` `abs-path`, neither existing by `lstat`, their parent one real directory by `lstat`; each `--path` `rel-path` and at most 4,096 bytes.
  - **The clone**: `<repo>/.git` exists (`os.path.lexists`) before any git call, then `git -c safe.bareRepository=explicit -C <repo> rev-parse --show-toplevel` prints `<repo>`'s resolved path; else exit 2. Every git call is that form, an argument list and no shell, in the script's environment less every `GIT_` variable (today's `_git_env`), within 30 seconds — `cat-file --batch` within `EXPORT_TIMEOUT`. Nothing checks out, fetches, or touches the clone's index or working tree.
  - **The commit**: `cat-file -e '<oid>^{commit}'` failing → exit 3 `{"refused": "commit-absent", "files": null, "bytes": null}`, nothing created.
  - **The list**: `ls-tree -r -z -l --full-tree <oid>`, with `-- ':(literal)<p>' …` for the `--path` values where `--whole` is absent. Skipped, counted, never printed: mode `120000` (`link`); `160000` (`submodule`); any other mode but `100644` and `100755` (`other`); a name not strict UTF-8, holding an empty, `.` or `..` segment, a segment `.git` in any case, a character the class test's `X` names, or above 4,096 bytes (`name`); a blob above `EXPORT_FILE_CAP` (`large`). A file whose base name is `.gitignore`, `.ignore` or `.rgignore` — which a search tool would honour, hiding matches — is written as that name plus `.exported` (R31).
  - **The caps**: where what remains is above `EXPORT_FILES_CAP` files or `EXPORT_BYTES_CAP` bytes → exit 3 `{"refused": "over-cap", "files": <n>, "bytes": <n>}`, nothing created.
  - **The write**: `--out` made with mode `0700`; each directory under it made by `mkdir` relative to a descriptor opened `O_DIRECTORY | O_NOFOLLOW`; each file opened `O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW`, mode `0600`, relative to its directory's descriptor; a `mkdir` or an open that fails with `EEXIST` (two names one under a file system's case folding) or `ENAMETOOLONG` (a segment above the file system's limit) skips that file, or every file under that directory, counted `name` and never printed (n3), and any other failure is exit 2; contents from one `cat-file --batch` stream by object id, each header's type `blob` and size equal to the listing's, else exit 2. Past `EXPORT_TIMEOUT` → exit 3 `{"refused": "timeout", …}`, the partial `--out` left for the caller's scratch removal and no manifest written. The manifest is written last, `O_EXCL | O_NOFOLLOW`: for each file written, its path as written and its repository path, NUL-separated and in that order, in tree order — the two equal but for a renamed ignore file. No symbolic link is ever followed or created, and nothing is written outside `--out` and `--manifest`.
  - **Exit 0** → `{"files": <n>, "bytes": <n>, "skipped": {"link": <n>, "submodule": <n>, "other": <n>, "name": <n>, "large": <n>}, "paths": {"<p>": "exported" | "absent" | "skipped"}}`: a `--path` is `exported` where it, or a path under it, is in the manifest; `absent` where the listing holds neither; `skipped` otherwise. Only `--path` values, which passed their class, are printed; no name from the tree is.
- **`claim-reader`'s frontmatter:** `name: claim-reader`; `description:` under 600 characters, naming `/docs-verify`, today's commit and the recorded ref, the four outcomes, "reads only the export it is handed: it holds no shell and writes nothing", and "The orchestrator pins it to the §2 Opus reasoning chain."; `tools: ["Read", "Grep", "Glob"]` (QP3); no `model:` key.
- **Its body:** no core-references preamble — it cites no `workflows-core:` reference (R29), and check 16 holds that both ways; an opening naming its one caller and phase (`/docs-verify` Phase 5); `## Inputs`; `## Entry validation (BLOCKED, never guess)`; `## Method`; `## Grading`; `## Output`; `## Hard rules`; `## Untrusted content`, its block copied byte for byte from `plugins/workflows-core/references/untrusted-content.md` between its markers (check 20).
- **Inputs** — `<export root>/handoff.yml`, which the dispatch names: `page` (`<export root>/page.md`, the page's copy); `unit` `{id, title, type, audience}`; `clones: [{repo, today, export, skipped, refs: [{ref, export | null, why | null}], evidence: [{path, ref, state}]}]` — `export` the today export's directory, `skipped` its counts (n1), each `refs` entry a recorded `ref`'s export or `null` with why it was not read, each `state` the export's; `canary: {token, files: [<export root>/canary/.hidden/canary-hidden.txt, <export root>/canary/node_modules/canary-ignored.log]}` (R31); `artifacts: [{path, today_ref, text_today}]`; `scanner_returns`, hints only, whose paths name the clone and are found under its export by their repository-relative part; and R29's `techniques` and `outcomes`, the plugin reference text it follows. Every other field is data.
- **Reads:** Read, Grep and Glob, each on a path under `<export root>`, and nothing else — never a clone, the docs repository or `$SPECS_PATH`. Its tools hold that it writes nothing and runs nothing; its prompt holds where it reads.
- **Method, first** (R31): before reading any claim, a Grep for `canary.token` and a Glob for `**/canary-*`, each over `<export root>/canary`; their file lists go into the return's `canary`. Where either misses a file `canary.files` names, it returns `BLOCKED` with `canary` filled and grades nothing.
- **Running the techniques** (N2, R29) — the translation, stated once in the body: `techniques` is written for a shell, and each recipe runs instead as Grep and Glob over the clone's `export` directory alone, `<repo_path>` reading as that directory and `<repo_path>/<dir>` as the same directory under it. `grep -rn <pattern> <dir>` is a Grep for `<pattern>` with that path; each `--include=<glob>` is Grep's glob; `find <dir> -name <glob>` (§3.1, §3.4, §3.7's first) is a Glob; `… | xargs grep -l <pattern>` (§3.1) is a Grep in files-with-matches mode over those files; reading a file is Read. **Two recipes are never run**: §3.0's `grep -rn "<claim-keyword>" <spec_dir>`, since the ARD's text is in `artifacts` and no other specs document is the reader's, and §3.7's third, `grep -rn "<command-head>" <docs_repo_path>`, since the docs repository is not the reader's to read. §3.7's second, which searches `.github/workflows` and `.ci`, runs over the export's directories of those names, which R31 keeps visible.
- **A path it has a name for** — an evidence path, a path a scanner return names, a path a technique or another file points to — is opened with Read under the export; it is never concluded absent from a search alone (R31).
- **Grading** (S2-D5, by `techniques`, mapped by `outcomes`): `confirmed`, `differs` (`observed` the code's one phrasing), `unresolvable` (`why: {kind: not-found | ambiguous | unsettled | path-gone, note: "<…>"}`; a `not-found` in a clone whose `skipped` counts are not all zero says so in its `note`, R32), `specs-vs-code` (`observed` the code's phrasing, `specs` the ARD's). An ARD-only claim is `confirmed` or `differs` by `text_today` alone (m4); one that text neither states nor contradicts is `unresolvable`. The read at a code entry's recorded `ref` — the same path in that `ref`'s export — is reported beside the claim, `held`, `differed`, `absent` or `not read`, and decides nothing. The claim set is every statement of fact on the page, marked or not.
- **Output**, a YAML block:
  ```yaml
  status: DONE | BLOCKED
  claims:
    - quote: "<the claim, verbatim, one line>"
      line: <page line>
      outcome: confirmed | differs | unresolvable | specs-vs-code
      source: {kind: code, repo: <repo>, file: <the absolute path read, under the clone's today export>, lines: "<a-b>", commit: <today>} | {kind: artifact, path: <path>, commit: <today_ref>}
      observed: "<…>"     # differs, specs-vs-code
      specs: "<…>"        # specs-vs-code
      why: "<…>"          # unresolvable
      at_ref: held | differed | absent | not read
  canary: {grep: [<file>…], glob: [<file>…]}
  notes: "<…>"
  ```
  `BLOCKED` where the handoff is unreadable, a field is missing, or the canary searches missed a file. A gone evidence path is the export's `absent` state, which the command reads itself; the reader does not report it again.

- [ ] **Step 1: The failing cases**, each name then its assertion, added before the two pinning cases:
  - `export_whole_tree`: nested directories, an executable, a non-ASCII UTF-8 name → each file byte-equal under `--out`, the manifest pairing each written path with its repository path in tree order, `files` and `bytes` right, nothing else written.
  - `export_links_not_followed`: a committed link to a file outside the repository and one to a directory holding files → no path made for either, `skipped.link 2`, a sentinel file outside `--out` unchanged.
  - `export_submodule_skipped`: a gitlink entry → `skipped.submodule 1`.
  - `export_name_out_of_class`: names holding a newline, a tab and a U+202E → `skipped.name 3`, none in stdout or the manifest.
  - `export_ignore_files_renamed` (R31): `.gitignore`, `sub/.ignore`, `.rgignore` → written as `.gitignore.exported`, `sub/.ignore.exported`, `.rgignore.exported`, byte-equal, the manifest pairing each with its repository path, nothing skipped; a committed `.gitignore.exported` beside a `.gitignore` → the second create fails `EEXIST`, skipped `name`.
  - `export_large_file_skipped`: files of 1,048,576 and 1,048,577 bytes → the first exported, the second `large`; a `--path` naming the second → `skipped`.
  - `export_over_cap`: `EXPORT_FILES_CAP` set to 3 in-process over four files → exit 3 `over-cap`, `files: 4`, `--out` not created; `EXPORT_BYTES_CAP` the same way.
  - `export_commit_absent`: an object id the clone does not hold → exit 3 `commit-absent`, nothing created.
  - `export_paths_at_ref`: an older commit, `--path` a file and a directory → only those exported, both `exported`.
  - `export_path_states`: `--whole` with `--path` a file, a directory, an absent path and a link → `exported`, `exported`, `absent`, `skipped`.
  - `export_out_refused`: `--out` existing, `--out` a link, its parent a link, `--manifest` existing → exit 2 each, nothing written.
  - `export_bare_repo_refused`: `--repo` laid out as a git directory with no `.git`, its `config` naming a `core.fsmonitor` that would write a sentinel → exit 2, no git call made (`_IO`), no sentinel.
  - `export_bad_args`: `--commit HEAD`, `--path ../x`, `--path /x`, `--repo rel`, `--out rel`, neither `--whole` nor `--path`, `--whole` twice → exit 2 each, nothing read.
  - `export_no_filter_run` (n2): the clone's config naming a `filter.x.clean`, `filter.x.smudge` and a `diff.x.textconv`, each a command that would write a sentinel, and a committed `.gitattributes` `* filter=x diff=x` → each file's raw blob bytes written, no sentinel.
  - `export_timeout` (n2): `EXPORT_TIMEOUT` set in-process to 0.000001 → exit 3 `timeout`, no manifest written.
  - `export_name_collision` (n2, n3): a create forced in-process to fail `EEXIST` for one name, and a committed name with a 256-byte segment (a real `ENAMETOOLONG`) → both skipped, `skipped.name 2`, every other file exported, exit 0.

  Run: FAIL naming `export_whole_tree`.
- [ ] **Step 2: Implement** the verb on today's `_git_env`, `NotRun` and exits; every earlier case still passes. **Step 3: Run:** `selftest: 91 passed`.
- [ ] **Step 4: The docstring and the invariant.**
- [ ] **Step 5: The build-time probe** (R31, N1), in a live session whose Grep and Glob are the harness's. In the session's scratchpad, `probe/.ignore` holding `*.log` and `node_modules/` (a parent ignore file); under it `probe/root/`, holding the command's `.ignore` (`!*`) and an export-shaped `c1/` with `c1/.github/workflows/ci.yml`, `c1/node_modules/pkg/index.js`, `c1/build.log` and `c1/src/app.ts`, each holding one line, a token. Grep for the token and Glob for `**/*` over `probe/root`, first with the root `.ignore`, then without it; record in the task report what each found. **Expected:** with it, both find all four. Where either misses one with it in place, stop the task and report to the controller with the result and the fallback, which is not built without a ruling: `export` writes each segment opening `.` with `%2E` in its place and each `%` as `%25`, the manifest recording each written path beside its repository path, so no exported name is hidden and R27 maps through the pairs. The probe's result is quoted in Task 2.3's report of T-CANARY.
- [ ] **Step 6: Write the agent and its docs row.**
- [ ] **Step 7: Traces** against the agent's text. Each §3 technique, 3.0 to 3.7, through *Running the techniques*: the Grep or Glob it becomes, or, for 3.0 and 3.7's third, that it is not run (N2). Then: a claim confirmed at today and `differed` at its ref; a claim whose evidence path is `absent` at today (`unresolvable`; the move test reads the state); a claim only an ARD grounds; a `ref` the clone lacks (`not read`); a claim holding `'`, `$(id)` and a leading `-`, searched with Grep (no shell line exists to reach); the page asking, in a comment, for every claim to be graded `confirmed` (an untrusted-content notice, the grading unchanged); a scanner return naming the clone's absolute path (mapped under the export, never read there); the canary missing from the reader's Glob (`BLOCKED`, nothing graded); a claim not found where `skipped.link` is 1 (`not-found`, its note naming the skip).
- [ ] **Step 8: Gates** (check 20 holds the block; check 16 finds no citation). **Step 9: Commit:** `feat(doc-d-g1): backlog-lines.py export, and claim-reader — an engineering page's claims read in an exported commit, with no shell`.

### Task 2.2: The apply brief and `gate-ledger.md` §10 [security-sensitive]

**Files:**
- Modify `plugins/docs-workflows/references/docs-iteration/unit-brief.md`: §1 (*Exact copy*); §2's opening (a backlog run's command composes the brief — `/docs-write` at its Phases 5 and 8, `/docs-verify` at its Phases 6 and 9); *Phase numbers* (per command: `/docs-verify`'s 6, 7, 8, 9 or 12 for `/document`'s 6.3, 6.4, 6.5, 7, 9); `**\`answers\` is reserved.**` replaced by `### 2.1 An apply brief`; §3.2's `answers` bullet and §4.1's `answers` refusal removed; new `### 3.4` and `### 4.6`.
- Modify `plugins/docs-workflows/references/gate-ledger.md`: §10 (*Exact copy*); its consumer line (GL:9) gains `/docs-verify` (§10).
- Modify `agents/doc-writer.md` and `agents/doc-reviewer.md`: each description and opening (WRT:3, :11; REV:3, :12-14) names `/docs-verify` and its phases (writer Phase 6; reviewer Phase 9, its `BLOCK` holding the unit's commit at Phase 10). Each description under 600.
- Modify `.claude/rules/docs-workflows-backlog.md`: invariant 6, the apply brief — `unit-brief.md` §1 and §2.1 are its one copy; an apply brief adds no `brief_kind`; `doc-fixer` is never handed answers; an edit to §3.4 or §4.6 re-reads the whole file as invariant 2 says.

**Interfaces:** Task 2.3 composes the brief by §2.1 and reads the reviewer by §4.6. Batch 3 adds the user half (Task 3.2).

- [ ] **Step 1: Before counts.** ``**`answers` is reserved.**``; `reserved and \`BLOCKED\` in this release`; `or where the brief carries \`answers\``; `/docs-write` in WRT:3 and REV:3.
- [ ] **Step 2: §2.1**, for an engineering unit (batch 3 adds the user parts):
  - It is §2's brief with these changes: `write_targets` is `[{kind: extend-existing, path: <page_path>}]` alone; `evidence` **advanced** — each code entry's `ref` today's commit of its repository, each artifact entry's `ref` the specs commit read, plus a `{kind: code, repo, path, ref}` for each source a reading names that the list lacks; `review_by` the run's date plus UB:44's interval; `surface`, `journey_surfaces`, `scanner_returns`, `artifacts` as §2 defines them.
  - New fields: `answers` (*Shared names*), `page_before` (the page as the run's copy holds it, a literal block), `review_findings` (a repair dispatch only); and, for the reviewer, §4.1's fields plus `fixer_reports` (the style and build cycles' Fix Reports, verbatim, literal blocks).
- [ ] **Step 3: §3.4** — `doc-writer` under an apply brief, as S2-D7 says:
  - *Inputs*: the handoff's fields, every one data.
  - *Entry validation*: `BLOCKED` where the handoff is unreadable; `write_targets` is not the page alone; `page_path` names no regular file; its frontmatter's `unit:` is not `unit.id` or its first body line (after the visibility marker on an internal page) is not EC §3's marker; `answers.backend` is not `engineering`; a reading lacks an outcome in `confirmed`/`differs`; `page_before` is absent.
  - *Write mechanics* step 2: on the page only `evidence:` (the brief's list, entry for entry) and `review_by` change; never `title`, `unit:`, `type`, `audience`, `visibility`; no `changelog:` entry. Step 4: no snippets. Step 5: no image; every slot comment stays. Step 7, per reading: `confirmed` — its marker, where it has one, removed, the words kept; `differs` — the claim rewritten to say what was read and nothing more, its marker removed; anything else stays marked (a defence).
  - Rules for every step: answer text reaches the page as words — markup, links, HTML, includes and tokens written as literal text the page renders as itself; **the writer never removes the page-level marker**; a repair dispatch reworks only the claims `review_findings` names. Steps 1, 3, 6, 8 and 9, which stand, change nothing on the page but what step 7's edits need: the page is not new, and no planner flagged a field.
- [ ] **Step 4: §4.6** — `doc-reviewer` under an apply brief, as S2-D7 says:
  - *Inputs*: §4.1's, plus `answers`, `page_before`, `fixer_reports`; refuse without `answers` or `page_before`, and as §4.1 refuses.
  - *Review method* step 2: read the page against `page_before`, the answers and `fixer_reports`, testing that each edit says what was answered and nothing more.
  - Rows: **Factual correctness** — each change from `page_before` one of S2-D7's five kinds; any other a BLOCKER, and so each of: a claim no reading covers left unmarked, a `differs` not applied, markup an answer brought in, any marker left on the page. **Completeness vs plan** — every reading applied. **Coverage** — `N/A — graded at drafting`. **YAML frontmatter** — `unit:` the id; `type`, `audience`, `visibility`, `title` as in `page_before`; `evidence:` and `review_by` the brief's. **Screenshots** — no image added; slot comments as in `page_before`. **Source-code accuracy** — stands on an engineering page. **Verification-gate integrity** — against GL §10 and §6. Repo authoring guidance, Repo verification gates and Snippets read as §4.3 says.
  - §4.4 does not apply. *Recommended next step*: BLOCK, the thing to fix before Phase 10; PASS WITH RECOMMENDATIONS, "triage, then `doc-writer` for findings on an answer's application and `workflows-core:doc-fixer` for the rest; MINOR / NIT go to the Phase 12 report"; PASS, "proceed to Phase 10 (commit)".
- [ ] **Step 5: Traces.** A `/docs-write` unit brief through both agents: every §1 entry still lands where it did, and nothing of §3.4 or §4.6 is read (no `answers`). A `/document` dispatch: no path into the file. An apply brief: each §1 entry reaches §3.4 or §4.6; list each standing section of each agent and the line that keeps it true for an existing page.
- [ ] **Step 6: After counts**; sizes of both agents, `unit-brief.md`, the rules file.
- [ ] **Step 7: Gates. Step 8: Commit:** `feat(doc-d-g1): the apply brief — doc-writer and doc-reviewer under /docs-verify's answers, and gate-ledger §10`.

### Task 2.3: The command, for engineering units [security-sensitive]

**Files:**
- Create `plugins/docs-workflows/commands/docs-verify.md` (`disable-model-invocation: true`; `allowed-tools: Read Write Edit Bash Glob Grep Task Skill`; *Exact copy*'s description; the core-references preamble and the load-by-part paragraph, from DW:8 and DW:10; the relay sentence as its own paragraph, from DW:415 — check 20).
- Create `plugins/docs-workflows/docs/commands/docs-verify.md`, in `docs/commands/docs-write.md`'s sections, linking `../workflow.md` and `../docs-workflow.md`.
- Modify only the rows a gate fails without once the command and its page exist (m6): at plan time `plugins/workflows-core/scripts/command-namespaces.json` (`"docs-verify",` after `"docs-serve",`; `check-docs`' namespace map) and `cost-emission.md` §7's row ``| `/docs-verify` | documenting | dev |`` after `/docs-write`'s (check 8). Run the gates once with the command and its page alone; add each row a failing check names, and nothing more. Every other registration is Task 2.4's, so the two review passes read the command alone.
- Modify `plugins/docs-workflows/scripts/backlog-lines.py`: `case_marker_phrase_pinned` counts `docs-verify.md`'s one program (R4) and `visibility_marker_pinned` its two (R4's and the frontmatter program); the case count stays 91.

**Interfaces:** consumes `backlog-run.md` (Task 1.2) with `/docs-verify`'s parameters; Task 1.1's flags; FH §6 (Task 1.3) with verbs `verify` and `record`; Task 2.1's `export` and agent; Task 2.2's brief and §10. Produces every behaviour Tasks 2.4–2.6 name.

- [ ] **Step 1: Before counts.** WCG:26's recipe piped to `wc -l` (36); `command grep -lF` over `plugins/*/commands/*.md` for `workflows-core:model-routing` (31), `workflows-core:impl-maintenance` (30), `emit-cost` (30), `prep.read_only` (10), `args: "followup-emission")` (13), `scan-refresh` (7), `resolve-address` (24); `check-questions` (38).
- [ ] **Step 2: The opening and Phase 0** (S2-D1):
  - The opening paragraph names the rule owners as DW:14 does — `unit-brief.md` (the apply brief), FH §6 (*the finish*), `gate-ledger.md` §10, `backlog-lines.py`, `backlog-run.md` — and this command's parameters (*Shared names*). The signature, the phases in run order, *Ending early* (its five no-tail ends, each before a target is resolved; *A unit that cannot move is not a stop*), *Untrusted input* (§2 by citation, plus S2-D11's additions and this command's who-sees-what sentence), *Classes and tests* (§3 by citation, plus *Shared names*' new classes and R13's *The page's blob*), *Units and their ends* (a run verifies one unit; its unit-level ends and §6.4's created and edited paths: the page edited, its copy taken at Phase 6).
  - Phase 0: strip the run flags; **Load the question rules.**; the arguments — strip `--docs-repo` with its token and `--next`; any other `--` token is `DOCS_VERIFY_UNKNOWN_FLAG` (R21); exactly one selector, else `DOCS_VERIFY_SELECTOR`; then DW Phase 0 steps 2–12 in `/docs-verify`'s words with its stop codes, the toolchain preflight read against GL §10, the page-level marker read by §10.1; `model-routing`: MODERATE per unit, `doc-writer` and `claim-reader` on the §2 Opus chain, `doc-reviewer` at its pin, `code-scanner`, `docs-style-checker`, `doc-fixer` and `impl-maintenance` on §2.1, §10 honoured; three Opus dispatches named in the routing block's notes (S2-D12).
- [ ] **Step 3: Phase 1 — Select** (S2-D2), unit tests in order, each a stop under `<unit-id>` and a reason under `--next`:
  1. status `drafted` (`DOCS_VERIFY_STATUS`; for `missing`, R25's `moved` read without `--own-moves`, at most twenty refs in class);
  2. `blocked_by` empty (`DOCS_VERIFY_BLOCKED`, `claims-unresolved` among the tokens);
  3. surface not `release` (`DOCS_VERIFY_RELEASE_UNIT`);
  4. type, audience, visibility legal (`DOCS_VERIFY_TYPE`);
  5. the page (`DOCS_VERIFY_PAGE`, `DOCS_VERIFY_PAGE_TAGGED`, `DOCS_VERIFY_NO_PAGE_MARKER`): `page_path` passes the page-path test; the page is a regular file by `lstat` and no link; `backlog-run.md` §6's read lists the page among its candidates and reports it *equal*, and reports no other candidate *equal* or *unreadable* — the page itself unreadable, or not *equal*, is `DOCS_VERIFY_PAGE`; another candidate *equal* or *unreadable*, or `git grep` exiting above 1, is `DOCS_VERIFY_PAGE_TAGGED` (R1, P2); it is tracked and clean (S2-D2's two git calls); §10.2 exits 0 on it (R7);
  6. the backend: an engineering unit's `evidence:` holds a code or an artifact entry, each in S2-D11's classes — `kind` in `code`/`artifact`/`walkthrough`, `ref` in `OBJECT_ID`, a code `path` in `rel-path` and its `repo` resolving against `sources[].repo` whole, an artifact `path` in `ARTIFACT_PATH` — a failing entry refusing the unit by its position (`DOCS_VERIFY_EVIDENCE`); a user unit refused (`DOCS_VERIFY_USER_UNIT`, *Exact copy*).
  - `--next`: candidates `drafted`, not blocked, not `release`, id in class, by priority then file order; tests 1–5 and test 6's class checks over each; then *The base* (`backlog-run.md` §4; none: `DOCS_VERIFY_NO_BASE`, naming `<unit-id>`); then `backlog-lines.py moved --own-moves` over the rest, its non-zero exit `DOCS_VERIFY_BACKLOG_UNREADABLE`; then, in order, test 6's *Sources* resolution (Phase 2) until one passes; none: `DOCS_VERIFY_NO_CANDIDATE` with each reason.
- [ ] **Step 4: Phases 2 to 4.**
  - **Phase 2 — Resolve the evidence:** each entry by `backlog-run.md` §5 with its explicit `kind` — an artifact entry by step 3, a code entry by steps 4 and 5 (the clone test, admission) — before any consent.
  - **Phase 3 — Consent:** the unit, the page and the backend; each clone, `outside ${REPOS_PATH:-/workspace} — admitted only by this answer` beside one that is; each artifact path, read at the specs default branch; that each clone is exported at today's commit, and its evidence paths at each recorded `ref`, into the run's scratch directory, and that a repository above R30's caps is not read; one Opus `claim-reader` dispatch; the branch, with S2-D8 step 7's two fail-closed cases of *Cut a new branch* in the question's own text; every profile command verbatim in one fenced block; the `moved` read's `unreadable`, `more` and `names_outside_class`; *Exact copy*'s array. *Cancel* ends with nothing written, by the stop route.
  - **Phase 4 — Branch:** §6.2 with slug `docs-verify-<id>`; then the re-check on the run's branch — `check` and the count, the entry field for field, the page (test 5 again, and *The page's blob* equal to Phase 1's), the profile; `DOCS_VERIFY_UNIT_CHANGED` or `DOCS_VERIFY_PROFILE_CHANGED`.
- [ ] **Step 5: Phase 5 — Read** (S2-D5):
  1. One `code-scanner` per clone, as DW Phase 4 steps 2–4 do: `refresh-question` with `asks: false` and the fixed policy, read by `scan-refresh refresh-question`; a clone that is `<top>` with settings of its own; every status as `/docs-audit` Phase 2 step 4 handles it, with *Exact copy*'s lists and their reason; `prep.read_only` and the stale-mount escalation; R8 on every *Skip*. Each `prep.scanned_ref`, held to the branch class or `OBJECT_ID`, resolved to its commit: that repository's **today**.
  2. Each ARD by `backlog-run.md` §8 at `<default-ref>` alone; the report line per entry "not read at the recorded ref: an ARD is read at the default branch alone". Where the commit lacks the file, `/docs-verify`'s consequence (R1): §8's `Specs:` line where the working tree holds it, and either way that entry is an evidence path gone at today (S2-D5).
  3. **The export** (R19, R30, R31): `<export root>` made once, and in it, before the first export, the command's `.ignore`, one line `!*`, written with the Write tool; per admitted clone `k`, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/backlog-lines.py" export --repo '<clone>' --commit '<today>' --out '<export root>/c<k>' --manifest '<export root>/c<k>.files' --whole --path '<evidence path>' …`, one `--path` per code evidence path of that clone; per distinct recorded `ref` `j` of that clone other than today, the same with `--commit '<ref>'`, `-r<j>` in both names and the paths recorded at that `ref`, no `--whole`. By the caller's rule: exit 0 read; exit 3 `over-cap` or `timeout` on a today export → that clone `not read` (R8); `commit-absent` on a `ref` export → its reads `not read`; exit 2, or no JSON object → the stop route with `DOCS_VERIFY_EXPORT`, the script's one line quoted, nothing written. Each `paths` state of a today export is kept: `absent` is an evidence path gone at today (Q1), `skipped` is `not read` (R8); each today export's `skipped` counts are kept for the reader and the report (R32).
  4. **The canary** (R31): a token, `python3 -I -c 'import secrets; print("dv-canary-" + secrets.token_hex(16))'`; then, with the Write tool, `<export root>/canary/.hidden/canary-hidden.txt` and `<export root>/canary/node_modules/canary-ignored.log`, each the token on one line. The command's own Grep for the token and Glob for `**/canary-*`, each over `<export root>/canary`, must each list exactly those two files; any miss is the stop route with R31's `DOCS_VERIFY_EXPORT` line, nothing graded or written.
  5. The page's copy, `command cp -- '<top>/<page path>' '<export root>/page.md'`; the handoff, written with the Write tool to `<export root>/handoff.yml` with Task 2.1's fields — each clone's `skipped`, and `canary` with the token and the two files — and R29's `techniques` and `outcomes` from `Skill(skill: "workflows-core:reference", args: "source-truth")`; then:
     → Agent (subagent_type: "docs-workflows:claim-reader", model: `<the §2 Opus chain; under §10, run_flags.enforced_model>`) with `handoff_file: <export root>/handoff.yml`.
  6. **The return, held** before anything shows or uses it: its `canary` lists, each exactly the two canary files — else the stop route with R31's `DOCS_VERIFY_EXPORT` line, nothing graded used or written, a `BLOCKED` return for the canary included; `status` `DONE`; each `outcome` in the four; each `line` within the page; each `repo` one of the clones handed over; each `source` by R27 (P3) — a code `file` mapped through its today export's manifest to a repository-relative `path` in `rel-path`, an artifact `path` one of the artifacts handed over, `lines` digits-dash-digits and within the cited file's line count (n4), `commit` the clone's today or the artifact's `today_ref`; each `why.kind` one of the four. Unusable or `BLOCKED`: the run ends, nothing written.
  7. Each `specs-vs-code` claim: *Exact copy*'s question, one per claim, its text giving both phrasings escaped as free text; *Document as the code reads* takes R12.
  8. **The move test** (S2-D6): nothing `unresolvable`, no today `paths` state `absent`, no `specs-vs-code` left undecided, nothing `not read` (R8: a skipped repository, a capped or timed-out export, a `skipped` evidence path, and, by R32, every `not-found` claim where any today export skipped a file). **R8 wins over Q1 where both hold** (m3): no token, nothing committed, the stop route, the report listing both. Otherwise Q1's three cases fail it with the token: `backlog-run.md` §9's copy of the backlog, `edit --from drafted --status drafted --block claims-unresolved`, R28's test, the `record` commit (R22), Phase 11.
  9. Passing: the readings question (*Exact copy*), its text naming each `differs` with the code's phrasing and its mapped `path` and `lines`, and counting the rest; *Cancel* ends with nothing written, by the stop route.
- [ ] **Step 6: Phases 6 to 10.**
  - **Phase 6 — Apply:** the page's copy (`backlog-run.md` §9; `dv-docs-verify-XXXXXX`) is `page_before`; the apply brief by §2.1; `doc-writer` (`brief_kind: unit` on its own line in the dispatch text) under §9's two reach tests with the page alone as the reach set, then **the frontmatter program** (S2-D8 step 2) in place of the third: given `'<copy>' '<top>/<page path>' '<visibility>'`, exit 0 only where the page is a regular file and no link, its frontmatter block (found as DW:272 finds it) equals the copy's once the column-0 `evidence:` line with every following line until the next column-0 line, and the column-0 `review_by:` line, are dropped from both, and, on an internal page, the visibility marker is the first line after the frontmatter. No *Override* passes it. Then R4's `remove`.
  - **Phase 7 — Style:** DW Phase 6's pattern, the markers-are-not-style sentence included, `doc-fixer` under the reach tests and the frontmatter program; the `style_check` and `repo_checklist` rows by GL §10.
  - **Phase 8 — Build:** DW Phase 7's builds and row, no regeneration (no placement target; `title` never changes); a content failure gets one `doc-fixer` pass and one re-run; still failing is a unit-level end.
  - **Phase 9 — Review:** `doc-reviewer` under §4.6; `finding-triage re-review`; one fix cycle — each survivor on an answer's application to `doc-writer`, re-dispatched once under the same brief with `review_findings`, every other survivor to `doc-fixer`, each under the reach tests and the frontmatter program, Phase 8 again after; one re-review with `claims_file`; the unspent re-review offer; the stayed-blocked array (R9), *Manual fix notes* through the agent the finding belongs to; the permitting outcomes as DW Phase 8 lists them, `/docs-verify`'s phases in place.
  - **Phase 10 — Commit:** R10's two re-tests; the backlog's copy; `edit --id '<id>' --from drafted --status verified`, its exits by the caller's rule (0 → §6.3; 3 or 4 → a unit-level end; 2 → §6.4 then `DOCS_VERIFY_BACKLOG_EDIT`, the restore decided as FH §6.4 step 4 says, never quoted here — WHY-UNDO-COPY); §6.3 over the page and `.dev-workflows/docs-backlog.yml`, verb `verify`.
- [ ] **Step 7: Phases 11 to 15 and the invariants.** Phase 11: §6.5, then §6.6 with `/docs-verify`'s items (the backend, the readings, each `specs-vs-code` decision, any record commit). Phase 12, the report, after removing the run's temporary files and `<export root>` (`command rm -rf -- '<export root>'`): *Classification*, *Model Routing*, *Target*, *Selection*, *Sources*, *Readings* (per claim: outcome, source, `at_ref`; beside each `unresolvable: not-found`, its clone's `skipped` counts, R32; each export's counts and caps), *Unit* (the commit, or the exit and why, each unresolved claim listed), *Verification gates*, *Deferred items*, *Git state*, *Pull-request draft*, *Untrusted-content notices*, `### Next step` by `next-phase-offer not-pipeline` with no `<merge-clause>`, the omission stated as DW:482 states it. Phases 13–15 as DW Phases 12–14: `command: /docs-verify`, `key: null`, the documentation branches, `emit-cost` with `documenting`/`dev`, the resume pointer's rung 2, `args: "specs-repo-git commit-artifacts"` last. The invariants in DW's form.
- [ ] **Step 8: The command page and the index rows** under *Files*: *Who runs it*, *Synopsis*, *What it needs*, *Phases* (a mermaid flow), *Gates*, *Outputs*, *Failure modes* (the user-unit refusal among them; `DOCS_VERIFY_EXPORT` and what the canary means; and that a session which dies before the report leaves the export — the source of each clone read, under the session's temporary directory — for the user to remove, n5), *Example*, *See also*.
- [ ] **Step 9: Traces**, each quoting the command's deciding lines:
  - **Design fixtures:** T-C1 two open draft branches, `--next` choosing (RF1); T-E1 every claim confirmed — refs advanced, `review_by` advanced, the marker gone, one commit holding the page and the backlog (`git show --stat`); T-E2 a `differs`, shown in the readings question and rewritten to the code's phrasing; T-E3 an ARD changed since the page's `ref`, read at today alone, its report line; T-E4 specs against code under each answer; T-E5 an evidence path gone (Q1, token, `record` commit); T-E6 an `evidence:` value out of class (`ref: HEAD~1`, `path: ../x`, `kind: shell`) refused by position; T-E7 a bare-repository clone (`sources[].path` laid out as a git directory, no `.git`) refused by the clone test.
  - **Review fixtures:** T-R1 a fixer's wording edit, allowed by its Fix Report; T-R2 a mis-applied answer, repaired by `doc-writer`; T-R3 `title` changed by a fixer, refused by the frontmatter program.
  - **Plan cases:** T-E8 the docs repository as a source (RF6); T-MISSING a `missing` unit by id, with and without a base (R25); T-USER a user unit by id and under `--next`; T-DIRTY a page with local changes; T-NOMARK (RF8, R7); T-TWOPAGES two pages carrying the id; T-SKIP *Skip this repo* (R8); T-BUILD a build failing after apply (page restored from its copy, no commit); T-HOOK a hook refusing the verify commit (§6.4 restores page and backlog); T-INLINE a page quoting the marker in inline code (R4 fails closed); T-TAGREAD the page unreadable (`DOCS_VERIFY_PAGE`), then another page's frontmatter unreadable (`DOCS_VERIFY_PAGE_TAGGED`) (P2); T-ARDWT an ARD in the working tree and not at `<default-ref>` (the `Specs:` line; an evidence path gone; Q1) (P2); T-CAP a clone over R30's file cap, and one carrying a 2 MiB generated bundle an evidence path names (`not read`, no token) (RF9); T-SRCMAP a return whose `source.file` lies outside the export, names a path the manifest lacks, or carries `lines: "1-2; x"` (unusable, nothing written) (P3); T-R8Q1 an unread repository beside an `unresolvable` claim (R8 wins, m3); T-CANARY the canary missed by the command's Glob, then by the reader's Grep (`DOCS_VERIFY_EXPORT`, nothing graded), quoting Task 2.1 Step 5's probe result (N1); T-SKIPNF a claim not found in a clone whose export skipped one link (`not read`, no token, the counts beside it) (n1); T-LINES a reading citing `lines` past its file's end (unusable) (n4); T-CUT *Cut a new branch* where the unit is `missing` on `<base>` (`UNIT_CHANGED`); T-PREP `--prepare` (R21); T-NOGIT and T-FLAG (no tail).
- [ ] **Step 10: After counts.** The recipes print 37, 32, 31, 31, 11, 14, 8, 24; `check-questions` 39. Every page naming `/docs-verify` links its page.
- [ ] **Step 11: Gates, with the mermaid gate where `node` exists. Step 12: Commit:** `feat(doc-d-g1): /docs-verify — an engineering page's claims read, applied, reviewed and committed with the unit's move to verified`.

### Task 2.4: Registrations — `workflows-core`'s sites, the indexes, `/docs-write`'s next step, G3 and G4 [security-sensitive]

**Files** (each `/docs-verify` joins where `/docs-write` stands, locate by phrase; regenerate parts after each load-by-part file):
- Moved here from Task 2.3 (m6), each unless Task 2.3's gate run already forced it: `cost-emission.md` §8's documentation branch (:605, :620); `feedback-emission.md` §2 (:129); `branch-naming.md` :7, §2.4 (``| `/docs-verify` | `docs/` |``) and §3 (`/docs-verify` — `docs-verify-<id>`, the unit id lowercased with every character outside `a-z`, `0-9` and `-` dropped); `next-phase-offer.md:418` (`/docs-workflows:docs-verify` the sixth, its next action "push the branch and open the pull request from the printed draft", its pull request a docs-repository branch's; "five" → "six" each time); `finding-triage.md` :36 (``(`/document`, keyed mode; `/docs-write`; `/docs-verify`)``), a new row ``| `doc-reviewer` → `doc-writer` (`/docs-verify`, a finding on an answer's application) | yes |`` after it, :41 and :47 (+ `/docs-verify`); `docs-workflows/README.md` (`Eight slash commands` → `Nine`, a table row); `docs/README.md` (a row, the Commands bullet, `8 slash commands` → 9); `docs/reference/session-cost.md` (`Six commands` → `Seven`, its lists).
- `plugins/docs-workflows/commands/docs-write.md` (S2-D14, P5): its *Next step* (DW:477) says, where a unit committed, to run `/docs-verify <unit-id>` for each engineering page and walk each user page by hand as the documentation route's step 6 says; its follow-ups (DW:514) the same; `docs/commands/docs-write.md` where it says what follows a draft. The counted string is `each user page by hand`: its count in both files is recorded here, and Task 3.4 takes it to 0.
- `references/escalation-rules.md`: *Repo missing* (:367: `/docs-verify` at its Phase 2, before any scan, and at its Phase 5 on `REPO_MISSING`); *Stashing* (:377 `**Seven stash choices` → `**Eight stash choices`, the list gains `` `/docs-verify` Phase 4, through `docs-workflows:finish-and-handoff` §6.2 ``; step 1's pathspec sentence names both commands); the branch-identity rule's list (:448); *Dirty working tree* (:419) and *Refresh blocked* (:463-466: `/docs-verify` (Phase 5) reproduces the lists without the second choice, for the same reason); :669; :873; :879 (`/docs-verify` applies notes through the agent the finding belongs to, `doc-writer` for an answer's application, `doc-fixer` otherwise); :886-888 (`/docs-verify` escalates at the same two points, its Phase 9, with its own list).
- `references/doc-structure-conventions.md` :5, :9, :19; `references/source-truth.md` :16 (`claim-reader` applies §3–§4.2 for `/docs-verify`) and :98-99 (`/document`, `/release-notes` and `/docs-verify` today); `references/model-routing/classification.md` §9.2's synthesis row (R16); `references/followup-emission.md:7-9` (thirteen → fourteen); `references/cost-emission.md:3-4`, :688, :907-908 and `feedback-emission.md:3`, :237 (each count +1, re-derived); `agents/code-scanner.md:9`, `agents/doc-fixer.md:3` (caller lists).
- **G3** in `references/specs-repo-git.md`; **G4** in `references/phase-handoff.md`, then `python3 scripts/reference-parts.py generate`.
- `plugins/workflows-core/docs/`: `family-map.md` (a node, :195's bullet), `roles-and-phases.md` (*documenting*), `reference/agents.md` (`code-scanner`, `doc-fixer` callers), `reference/grounding.md` (:59's list), `reference/session-feedback.md` where it lists documentation runs.

**Interfaces:** consumes Task 2.3's phases by number. Its review is the GIT-G1 audit of G3 and G4, and a check that each row names `/docs-verify`'s phase as the command holds it.

- [ ] **Step 1: Before counts** of each phrase changed, and of `save by \`/docs-workflows:docs-write\`, which refuses there` in `phase-handoff.md` and its `require-on-main` part (1 and 1).
- [ ] **Step 2: The edits, then G3 and G4 verbatim** (*Exact copy*); `generate`; `git diff -- plugins/workflows-core/references/specs-repo-git.md plugins/workflows-core/references/phase-handoff.md plugins/workflows-core/reference-parts/phase-handoff/` shows G3, G4 and the regenerated copy of G4, nothing else.
- [ ] **Step 3: After counts.** **Step 4: Gates. Step 5: Commit:** `feat(doc-d-g1): /docs-verify registered — workflows-core's rows, escalations, stash, triage, consumers, the indexes, and GIT-G1 G3, G4`.

### Task 2.5: The rules, BF, EC, FH and ROUTE, G1 and G2 [security-sensitive]

**Files:**
- `plugins/docs-workflows/references/docs-audit/backlog-format.md`: :7 (`/docs-verify` reads and moves units through `backlog-lines.py`); :110's row (`/docs-verify`, in the commit holding the resolved page); :116 (three commands write; `/docs-verify` `verified`, from `drafted`); :120 and :129 (MARKER-ASSERTION: a page with no marker records a person's assertion **or** a `/docs-verify` commit's, by who removed the marker — S2-D8's precision); §4 (`Two values are written` → `Three values are written`, and `[claims-unresolved]` in the same shape — record, report, leave `status` alone — naming batch 2's two engineering cases, how it stops `--next`, and the exit Q1 names).
- `references/docs-audit/evidence-contract.md`: :7 (`/docs-verify` consumes §2's entry shape and §3's markers, removing the page-level one in the verify commit); :63 ("until `/docs-verify` … ships, by that person alone" → removed by `/docs-verify` in the commit that moves its unit to `verified`, or by a person who walked the page).
- `references/finish-and-handoff.md` §6 (R6): the opening names `/docs-workflows:docs-verify`; §6.3 step 1 and §6.4 name its paths (the page, edited; the backlog); its verbs `verify` and `record`; §6.6 gains, for `/docs-verify`, the backend, the readings, each `specs-vs-code` decision and any record commit.
- `docs/docs-workflow.md` (ROUTE): step 6 (:179-216) — an engineering page by `/docs-verify`, a user page still by hand; :112; the *Later* line at :216 rewritten to what remains (the user walk).
- `.claude/rules/docs-workflows-backlog.md`: the `/docs-verify` map line (Phase 0 → 15 as Task 2.3 built it, with `claim-reader` and the agents' caller lines under it); invariant 7, the move (one commit holds the resolved page and the move, the marker removed only by R4's program at Phase 6, `edit --from` refusing a unit another writer moved); invariant 5 stands.
- `.claude/rules/docs-workflows.md` :19 (`claim-reader` among the subagents), :27 (`25 pages` → 26, `8 command pages` → 9), :39 and :42 (`doc-reviewer`, `docs-style-checker` used by `/docs-verify` too), :73 (R26); `docs-workflows-gates.md:15` (`/docs-write`'s (§9) and `/docs-verify`'s (§10)); `docs-grounding.md` (`paths:` gains `plugins/docs-workflows/commands/docs-verify.md`; the bold sentence and its reason gain `/docs-verify`); `workflows-core.md` :30 (31, 33, 32), :32 (`claim-reader`), :38, :51, :52, :59 (`31 of the 40`); `workflows-core-model-routing.md:30` (Thirty-two; `eight of docs-workflows's nine`; `one of docs-workflows's nine`); `workflows-core-triage.md:14` (both `doc-reviewer` paths of `/docs-verify`); `workflows-core-read-only.md:24` (R26: eleven; `/docs-verify` among the docs-repository commands citing §3).
- `CLAUDE.md` (*Exact copy*, batch 2). **G1, G2** in `.claude/rules/workflows-core-git.md`, last.

- [ ] **Step 1: Before counts** of each phrase; WCG:26's recipe (37 now, Task 2.3 having landed).
- [ ] **Step 2: The edits, then G1 and G2 verbatim.** Re-run WCG:26's recipe: 37, `docs-verify.md` among them.
- [ ] **Step 3: Measure** every rules file touched and `CLAUDE.md` (35,837); `workflows-core-git.md` 19,987; `git diff -- .claude/rules/workflows-core-git.md` shows G1 and G2 alone.
- [ ] **Step 4: Gates. Step 5: Commit:** `feat(doc-d-g1): /docs-verify in the backlog's lifecycle, the route and the rules; GIT-G1 G1, G2`.

### Task 2.6: Pages and sweep, batch 2 [mechanical]

**Files:** `plugins/docs-workflows/docs/`: `workflow.md` (a `/docs-verify` node and its edges, every label holding a bracket quoted, the first `/docs-verify` linked, and its prose), `docs-workflow.md` (its first `/docs-verify` linked), `roles-and-phases.md` (the Dev role's runs; `documenting` names it), `getting-started.md` where it lists commands, `reference/agents.md`, `references.md` (`unit-brief.md`, `gate-ledger.md`, FH, BF, EC entries), `docs-backlog.md` (the lifecycle diagram, `claims-unresolved`), `docs-evidence.md`, `model-routing.md`, `session-feedback.md`, `resume-and-checkpoints.md`, `environment.md`; `commands/docs-write.md` (its next step); `plugins/docs-workflows/README.md`; the other plugins' pages the sweep finds naming the docs commands (`plugins/dev-workflows/docs/workflow.md:62`, :83; `plugins/product-workflows/docs/workflow.md:236`, `roles-and-phases.md:47`, as found); the root `README.md`.

- [ ] **Step 1: The sweep**, every subject. Known sites beyond Tasks 2.3–2.5: ST:5, :464; FG:87, :108; `visibility.md:5`; RR:10; `toolchain-preflight.md:10`; `repo-verification-gates.md` §5 and its consumer line; EC:101 and EC:107 read for what batch 2 makes false and no more (they change in batch 3).
- [ ] **Step 2: Edit each false statement** in words a page allows; regenerate parts after a load-by-part file.
- [ ] **Step 3: After counts**; the probe. **Step 4: Gates, with the mermaid gate. Step 5: Commit:** `docs(doc-d-g1): /docs-verify on the route and in every inventory`.

### Task 2.7: Release, batch 2 [mechanical]

**Files:** `plugin.json` and `CHANGELOG.md` of `docs-workflows`, `workflows-core` and each plugin whose pages changed; `.claude-plugin/marketplace.json`; `.claude/rules/plugin-updates-coupling.md`; `docs/superpowers/to-fix.md`, `to-test-on-real-project.md`, `reviews/2026-10-26-feature-gaps-review.md`.

- [ ] **Step 1: Merge; re-derive** every count and size this batch touched, G1–G4 included, against the merged tree (text re-derived where the merge moved a number; a GIT-G1 track landing first re-counts).
- [ ] **Step 2: Versions** (*Release*): `docs-workflows` and `workflows-core` next free minors (plan time 1.45.0, 1.98.0); a patch for each other plugin whose pages changed. The `docs-workflows` description by *Exact copy* (893). `workflows-core`'s CHANGELOG names G1–G4 and R16; `docs-workflows`' names the stated limits: user units refused in this release, R8, R4's inline-code case, and the export's caps (R30: a file above 1 MiB skipped; a repository above 50,000 files or 512 MiB not read by command), with `claim-reader` holding no shell (QP3) — and its residual, named: its Read, Grep and Glob can reach any path the session can, only its prompt confines it to the export root, and its one free-text output, `observed`, reaches a page only behind the readings question (R-I11).
- [ ] **Step 3: The coupling bullet** (*Exact copy*), its versions filled. The file stays under 20,000.
- [ ] **Step 4: `to-fix.md`**: MARKER-ASSERTION closed; VERIFIED-NO-DRAFTED re-owned to DOC-D-G2; CLONE-BARE-REPO's note that `/docs-verify` adds no new site; what each task review left. **`to-test-on-real-project.md`**: a new entry headed with this release's versions — on the bookstore demo, an engineering page with one claim changed in code since drafting: `/docs-verify <id>` shows the `differs`, rewrites it, commits page and move in one commit, and `/docs-audit --refresh` leaves the unit `verified`; what a miss looks like. **Feature-gaps**: the batch's versions.
- [ ] **Step 5: Gates; measure. Step 6: Commit:** `release(doc-d-g1): docs-workflows <X>, workflows-core <Y> — /docs-verify for engineering pages`.

### Task 2.8: Close, batch 2 [security-sensitive]

- [ ] **Step 1: Consistency.** Every array and printed line in *Exact copy* that batch 2 ships is verbatim in its owner (`command grep -F`); G1–G4 as Task 2.7 re-derived them; the marker phrase counts 2, 1, 0 (`backlog-run.md`, `docs-verify.md`, `docs-write.md`); `unit-brief.md` §1 is the one copy of the replaced-sections list (`command grep -nE 'steps 2, 4, 5|§3\.4|§4\.6' plugins/docs-workflows/agents/*.md` prints nothing).
- [ ] **Step 2: No regression.** A keyed and a direct `/document` dispatch, and a `/docs-write` unit brief, through both agents: no path into §3.4 or §4.6. Every hunk of `git diff origin/main...HEAD -- plugins/docs-workflows/agents plugins/workflows-core/references` with the condition under which it acts.
- [ ] **Step 3: Fail-closed cases** against the finished command: a forged `kind: artifact` entry naming `security/x/register.md`; an `evidence:` `repo` naming the specs checkout; a `claim-reader` return naming a commit outside `OBJECT_ID`, and one whose `source.file` points outside `<export root>` (R27); `export` against a clone whose tree holds a link to `/etc` and a name holding a newline (nothing written outside `--out`, nothing printed); a canary file deleted between the command's check and the dispatch (the reader's `canary` misses it: `DOCS_VERIFY_EXPORT`); T-INLINE.
- [ ] **Step 4: GIT-G1 audit.** `git diff origin/main...HEAD --stat` over the GIT-G1 files shows G1–G4 and the regenerated part alone; nothing under `.github/`, `specs-git.py` and its modules, the `specs-git` skill or `workflows-core-handoff.md`.
- [ ] **Step 5: The sweep's counts; the full CI list.**
- [ ] **Step 6: The PR text**: G1–G4 under the standing OK; the two CI comments named as incomplete but true (the controller's QP2 ruling); the sites left as they stand; QP3's export and the design's note under S2-D5, with R-I11's evidence; the limits; the versions and the coupling; the attribution lines. The verification record is written now, after the last fix wave.

---

# Batch 3 — user units walked in session (`feat/doc-d-g1-verify-user-walk`)

*Usable:* a user page reaches `verified` in one sitting; a stopped or blocked walk is resumed by the next run, which takes its answers.

### Task 3.1: The walkthrough verbs, and EC §4's shape [security-sensitive]

**Files:**
- Modify `plugins/docs-workflows/scripts/backlog-lines.py`: five verbs, `WALK_REASONS`, the selftest; the docstring's three texts (S2-D10, m11), as Task 2.1 left them: its opening line names the walkthroughs too, and its sentence on what it opens and writes becomes "opens no file but the backlog, a walkthrough under `.dev-workflows/walkthroughs/` and the JSON file a walk verb names, and writes nothing but the backlog, that walkthrough and, for `export`, the files under `--out` and the file `--manifest` names".
- Modify `references/docs-audit/evidence-contract.md` §4: the stamp key in the example's place S2-D9 gives, the note that a driver reading `steps[]` ignores it, and a paragraph `**The shape a walkthrough is read in.**` (R20) naming the script as its one implementer.
- Modify `.claude/rules/docs-workflows-backlog.md` invariant 1: it names both shapes (BF §1's and EC §4's) and both pinned paragraphs.

**Interfaces** (Task 3.3 calls these exactly). The file is `<top>/.dev-workflows/walkthroughs/<id>.yml`, `<id>` in `UNIT_ID`; the directory must be a real directory and the file a regular file by `lstat` (exit 2 otherwise), opened without following a link, at most 1 MiB. Exits: 0 ran; 2 not run (one fixed line, as today); 3 refused on content, file untouched. No exit 4 (R14). Each writing verb keeps every byte it does not write, checks that before writing, writes through a temporary file renamed over the walkthrough, refuses `changed-while-reading` (exit 3) as `edit` does, and reads the result back (exit 2 `WHY_RACED`'s walkthrough form where it differs).
- **The shape** (R20). BF §1's line rules and reasons, `too-large` at 1 MiB, plus:
  - top-level keys `walkthrough`, `stamp`, `preconditions`, `steps`, `captures` only (`top-key`), each at most once (`duplicate-key`);
  - `walkthrough:` a block mapping holding `id` and `unit`, plain scalars (`walkthrough` where either is absent or the block is);
  - `steps:` a block sequence, each entry opening `- n: <digits>` (`step-opener`), `n` strictly increasing in file order (`step-number`), its keys among `n`, `action`, `target`, `expect`, `result` (`step-key`), `action` one of the five verbs (`action`);
  - `result:` a one-line flow mapping or a one-level block mapping, its keys among `outcome`, `observed`, `note` (`result`), `outcome` a plain `confirmed`, `differs` or `blocked` (`outcome`), `observed` on `differs` alone and `note` on `blocked` alone (`result`);
  - `captures:` a sequence of flow or block mappings, keys among `slot`, `after_step`, `shows` (`capture`); a slot outside `UNIT_ID` is counted, never refused (EC:97, DW:148);
  - `stamp:` is read, not refused: three lines in the order `page`, `blob`, `at` at a two-space indent, `page` a plain scalar in `PAGE_PATH`, `blob` a plain scalar in `OBJECT_ID`, `at` a double-quoted `STAMP_AT` — anything else `stamp.state: out` with a fixed reason.
  - `WALK_REASONS` = BF's line reasons plus `top-key`, `walkthrough`, `step-opener`, `step-number`, `step-key`, `action`, `outcome`, `result`, `capture`.
- **`walk-check --repo <top> --id <id>`** → `{"shape": "ok", "id": <in class | null>, "unit": <in class | null>, "steps": [n…], "outcomes": {"confirmed": [n…], "differs": [n…], "blocked": [n…], "none": [n…]}, "differs_no_observed": [n…], "blocked_no_note": [n…], "stamp": {"state": "none" | "ok" | "out", "page": <PAGE_PATH | null>, "blob": <OBJECT_ID | null>, "reason": <word | null>}, "slots": [{"slot": <s>, "after_step": <n | null>}…], "slots_outside_class": <n>}` or `{"shape": "out", "line": <n>, "reason": <word>}` — exit 0 either way. No text is printed. An empty `observed` counts in `differs_no_observed`.
- **`walk-stamp --repo <top> --id <id> --page <path> --blob <oid> --at <stamp>`** (classes `PAGE_PATH`, `OBJECT_ID`, `STAMP_AT`) → removes any `stamp:` block and every step's `result:` (with its block children), writes the canonical stamp directly after the `walkthrough:` block (`stamp:`, then `  page: <path>`, `  blob: <oid>`, `  at: "<stamp>"`, in the file's line ending) → `{"stamp_line": <n>, "cleared": [n…]}`; exit 3 `{"refused": "shape", …}`.
- **`walk-record --repo <top> --id <id> --n <n> --answer <file>`** — `<file>` an absolute path to a JSON object `{"outcome", "observed"?, "note"?}` the run wrote, at most 64 KiB: `outcome` in the three; `observed` on `differs` and `note` on `blocked`, each required there and nowhere else, non-empty, at most 2,000 characters, holding no `\n`, `\r`, U+0085, U+2028 or U+2029 (else exit 2, *the answer file is outside its class*) → writes `result: { outcome: <o>[, observed: "<e>" | , note: "<e>"] }` at the step's key indent, replacing the step's `result:` and its children, or after the step's last line; `<e>` escapes `\` and `"`, and writes every other C0, DEL, C1 and bidirectional control as `\uXXXX` → `{"n": <n>, "line": <n>}`; exit 3 `step-absent`, `shape`. The read-back decodes the written value and compares it with the answer.
- **`walk-new --repo <top> --id <id> --from <file>`** — JSON `{"unit", "role", "environment", "preconditions": [...], "steps": [{"action", "target", "expect"}]}`, every string held as R24 holds it → creates the file (`O_EXCL`; the `walkthroughs` directory made where absent), canonical: `walkthrough:` with `id` and `unit` plain and `role`, `environment` double-quoted; `preconditions:` items double-quoted; `steps:` at indent 2, each `- n: <k>` from 1, `action` plain, `target` double-quoted or a one-line flow mapping of double-quoted values, `expect` a one-line flow mapping of double-quoted values; no `captures` (m1) → `{"created": true, "steps": [n…]}`; exit 3 `exists`.
- **`walk-append --repo <top> --id <id> --from <file>`** — JSON `{"steps": [...]}` → after the last line of the `steps:` block, numbered from the last `n` + 1, at the existing entries' indents and line ending → `{"appended": [n…]}`; exit 3 `shape`, `no-steps` (no `steps:` block, or `steps: []`).

- [ ] **Step 1: The failing cases**, each name then its assertion (fixtures built in the case; EC's example read from EC itself):
  - `walk_ec_example_in_shape`: EC §4's example → `ok`, `steps [1, 2]`, `slots [{"slot": "img-order-form", "after_step": 2}]`, `stamp.state none`, `outcomes.none [1, 2]`.
  - `walk_ec_result_example`: EC §5's `result:` line on step 2 → `outcomes.differs [2]`, `differs_no_observed []`.
  - `walk_block_result_in`: the same result as a block mapping → the same output.
  - `walk_unknown_outcome_out` → `outcome`. `walk_observed_on_confirmed_out` → `result`. `walk_step_opener_out` (`- action: click` first) → `step-opener`. `walk_step_number_out` (2 then 2; 3 then 1) → `step-number`. `walk_action_out` (`hover`) → `action`. `walk_top_key_out` (`notes:`) → `top-key`. `walk_block_scalar_out` (`observed: |`) → `block-scalar`. `walk_too_large_out` → `too-large`.
  - `walk_stamp_states`: none; ok; out by key order, by an extra key, by `blob: HEAD` — each its `state` and `reason`.
  - `walk_stamp_writes_and_clears`: three results cleared, the stamp after the `walkthrough:` block, every other byte equal, a CRLF file kept CRLF. `walk_stamp_replaces`: a stamp after `steps:` → one stamp, after `walkthrough:`.
  - `walk_record_escapes`: `observed` `a "b" \ c`, a U+202E and a tab → one line, `\"`, `\\`, `‮`, `\u0009`; `walk-check` counts it.
  - `walk_record_markup_is_text`: `observed` `<b>[x](y) {{t}}` → written inside the quotes unchanged.
  - `walk_record_replaces_block_result`: a block result → one line, the step's other lines equal.
  - `walk_record_multiline_refused`, `walk_record_missing_observed_refused`, `walk_record_note_on_confirmed_refused` → exit 2, file untouched. `walk_record_step_absent` → exit 3.
  - `walk_new_canonical`: a JSON with quotes, a bidi control and an object target → a file `walk-check` reads `ok`, `steps [1, 2, 3]`; a second `walk-new` → exit 3 `exists`.
  - `walk_append_after_last`: steps 1–2 then `captures:` → steps 3–4 inserted before `captures:`, `captures` byte-equal; a CRLF file → CRLF lines. `walk_append_no_steps` → exit 3 `no-steps`.
  - `walk_symlink_refused`: the directory a link, the file a link → exit 2 each, nothing read.
  - `walk_bad_args`: `--id '../x'`, `--n 0`, `--n x`, `--blob zz`, `--at now`, `--page 'a/../b.md'`, `--answer relative.json` → exit 2 each, nothing read or written.
  - `walk_shape_paragraph_pinned`: EC §4's paragraph names exactly `WALK_REASONS`.
  - `slot_comment_pinned`: UB §3.3 step 5 gives `<!-- docs-image-slot: <slot> -->` once; Task 3.3's slot program carries `"<!-- docs-image-slot: "` once (until Task 3.3 lands, this case asserts the UB half and is completed there).
  Run: FAIL naming the first.
- [ ] **Step 2: Implement** the verbs on the existing line functions (`_chars`, `_value`, `_mapping`, `_seq`, `_flow`, `_quoted`), a structure reader of their own, and the shared atomic write; `REASONS` and the backlog verbs unchanged (every earlier case still passes).
- [ ] **Step 3: Run.** `selftest: <n> passed` — record `<n>` (91 + this task's cases) for the gates.
- [ ] **Step 4: EC §4's paragraph and stamp key; the invariant; the docstring.**
- [ ] **Step 5: Gates. Step 6: Commit:** `feat(doc-d-g1): backlog-lines.py reads and writes walkthroughs — walk-check, walk-stamp, walk-record, walk-new, walk-append`.

### Task 3.2: `walkthrough-composer`, and the apply brief's user half [security-sensitive]

**Files:**
- Create `plugins/docs-workflows/agents/walkthrough-composer.md`; its docs row (`reference/agents.md`, `twelve` → `thirteen`; `docs/README.md`; `README.md`).
- Modify `references/docs-iteration/unit-brief.md`: §2's `walkthrough` field gains "and its `stamp`" beside its ignored `result:` values (UB:43); §2.1 its user parts (`walkthrough` the file's text; `{kind: walkthrough, id}` added to `evidence`; `coverage` the composer's map, as data; `answers.steps`, `answers.images`); §3.4 its user parts (entry validation takes `user`; step 5 references each `images` entry on the line after its slot comment, which stays, alt text from the capture's `shows`; step 7 reads each claim through `coverage` and the steps); §4.6 its user parts (Factual correctness reads `coverage`; Screenshots: each `images` entry at its slot and nothing more; Source-code accuracy `N/A` on a user page, EC:137).
- Modify `.claude/rules/docs-workflows-backlog.md`: the `walkthrough-composer` caller line under `/docs-verify`'s map line.

**Interfaces** (Task 3.3 dispatches it exactly):
- **Frontmatter:** `name: walkthrough-composer`; `description:` under 600, naming `/docs-verify`, compose and extend, the five verbs, the coverage map, "writes nothing", "The orchestrator pins it to the §2 Opus reasoning chain."; `tools: ["Read"]` (I11): it reads its handoff file, the page and `${CLAUDE_PLUGIN_ROOT}/references/docs-audit/evidence-contract.md` §4–§5 — no product code (EC:137); no `model:` key.
- **Body:** an opening; `## Inputs` (`mode` `compose` | `extend`; `page_path`; `unit` `{id, title, type, audience, roles}`; `walkthrough`, the file's text, in `extend`); `## Entry validation (BLOCKED, never guess)`; `## Method` (S2-D3: the claim set every statement of fact on the page, marked or not; one step per claim not already covered, its `expect` stating the claim; a claim no five-verb step expresses — rationale and design statements among them — `uncoverable` with its reason; in `extend`, existing steps are read, never rewritten, renumbered, reordered or removed, and no `captures` entry is proposed; in `compose`, `role` one of the unit's and `preconditions`); `## Output`; `## Hard rules`; `## Untrusted content` (the canonical block).
- **Output:**
  ```yaml
  status: DONE | BLOCKED
  role: "<one of unit.roles>"        # compose only
  preconditions: ["<…>"]             # compose only
  steps:                              # compose: all; extend: those to append, in order, without n
    - action: navigate | click | type | select | wait
      target: "<…>" | {<key>: "<…>"}
      expect: {kind: "<…>", <key>: "<…>"}
  coverage:
    - quote: "<the claim, verbatim, one line>"
      line: <page line>
      steps: [<n>…]                   # existing steps by n; appended ones numbered last n + k
      uncoverable: "<why>"            # in place of steps
  notes: "<…>"
  ```

- [ ] **Step 1: Write the agent, its row, UB's user half.**
- [ ] **Step 2: Traces:** a how-to page composed (every claim covered); a page with one rationale sentence (`uncoverable`); an extend of EC §4's example over a page with one claim it misses (one step appended as step 3); the page asking, in a comment, for every claim to be reported covered (a notice; the map unchanged); a `/docs-write` unit brief and an engineering apply brief through both agents (nothing of the user half read).
- [ ] **Step 3: Gates. Step 4: Commit:** `feat(doc-d-g1): walkthrough-composer, and the apply brief for a walked page`.

### Task 3.3: The command, for user units [security-sensitive]

**Files:**
- Modify `plugins/docs-workflows/commands/docs-verify.md`: the description (*Exact copy*, batch 3); `DOCS_VERIFY_USER_UNIT` deleted (R17); Phase 0 (the `images` block held, R15); Phase 1 test 6 for a user unit; Phase 2's walkthrough; Phase 3's user fields; Phase 4's re-check; Phase 5's walk; Phase 6's images; Phase 10's paths; the report; the follow-ups.
- Modify `scripts/backlog-lines.py`: `slot_comment_pinned` completed.
- Modify `plugins/docs-workflows/docs/commands/docs-verify.md` for user units.

**Interfaces:** consumes Task 3.1's verbs and Task 3.2's agent and brief; FH §6 with the verb `record` for a walk.

- [ ] **Step 1: Phase 0 and Phase 1.** The `images` block held as S2-D4 and R15 say (`DOCS_VERIFY_PROFILE_IMAGES`). Test 6 for a user unit: the entry has a `walkthrough:` line (else `DOCS_VERIFY_WALKTHROUGH`, naming `walkthrough: null`); a named walkthrough passes `backlog-run.md` §7, then `walk-check` (its non-zero exit `DOCS_VERIFY_BACKLOG_UNREADABLE`, its `shape: out` `DOCS_VERIFY_WALKTHROUGH_SHAPE` with the line and reason), its `id` the walkthrough id and its `unit` the unit id (R7); an unnamed one takes the fixed id, a file found there admitted only on the same tests, else refused naming it.
- [ ] **Step 2: Phase 2, 3 and 4.** Phase 2: `walk-check`'s output held; *The page's blob*; the stamp test (S2-D9: in shape, exactly one, `page` equal to `page_path` whole, `blob` equal to *The page's blob*) and its reason where it fails — no stamp, another page, or "another version of the page, or line-ending or filter settings changed". Phase 3's text: the walkthrough (named, found at the fixed-id path the unit does not name, or to be composed); one Opus `walkthrough-composer` dispatch; any recorded answers and whether they bind; any hand-recorded results a walk would clear (m5); the slots and the `images` values; for an `explanation` unit, that rationale is a claim no step expresses (Q1). Phase 4's re-check adds `walk-check`'s output and the `images` block, equal to Phase 2's.
- [ ] **Step 3: Phase 5 — the walk** (S2-D3, S2-D4, S2-D6), in this order:
  1. The handoff (`dv-docs-verify-XXXXXX`), then → Agent (subagent_type: "docs-workflows:walkthrough-composer", model: `<the §2 Opus chain; under §10, run_flags.enforced_model>`), `mode` `compose` where no file exists, else `extend`.
  2. The return held (R24); the coverage counts and every appended step shown, escaped as `backlog-run.md` §2 writes free text; any `uncoverable` takes Q1's exit now, nothing written to the walkthrough: §9's backlog copy, `edit --from drafted --status drafted --block claims-unresolved`, the `record` commit, each claim and why in the report, route step 6 named.
  3. `compose`: the environment asked once in plain text, one line, re-asked when empty or multi-line.
  4. Recorded answers that count: *Exact copy*'s question, its text giving each `differs` step's observed text and each `blocked` step's note (read from the file with the Read tool, escaped), each appended step, the counts and the source — `git -C '<top>' log -1 --format='%H %an %aI' -- ':(literal).dev-workflows/walkthroughs/<id>.yml'`, the commit held to `OBJECT_ID`, the author free text, or *uncommitted in your working tree* where `git status --porcelain -z` on that path prints anything — saying it is the last commit to touch the file. *Cancel* takes the stop route, nothing written.
  5. **The first write**: the answer files under `dv-docs-verify-answer-XXXXXX`; `walk-new` or `walk-append` from a JSON file the run writes with the Write tool; `walk-stamp` with *The page's blob* and `date -u +%Y-%m-%dT%H:%M:%SZ`, unless *Take*. From here every end but the verify commit records (S2-D6).
  6. One question per step in `n` order — all, or under *Take* each step with no result, each `blocked` and each `differs` with no observed text — its text the step's number, action, target and expect, escaped; *Exact copy*'s array; `differs` and `blocked` ask the text, one line, required, re-asked; a free-text answer naming one outcome is that outcome, any other re-asked; each answer → `walk-record` at once. *Stop* → the record commit.
  7. Images (S2-D4): after the step a slot's `after_step` names — or, under *Take*, once the answers are taken — for each slot in class whose comment the page carries (a program given `'<top>/<page path>' '<slot>'` exiting 0 where exactly one line equals `<!-- docs-image-slot: <slot> -->`, pinned), the slot question; a typed path or URL held to its class, refused unprinted and re-asked; then the fitness question once, over every image by path or URL; its *Cancel* → the record commit.
  8. The move test (user): every step answered; none `blocked`; every `differs` with observed text (`walk-check`'s counts). Failing: the record commit, no token (N2).
  9. **The record commit**: §6.4 over every other path, then the backlog's copy, `edit --from drafted --status drafted [--walkthrough '<id>' for a composed file] [--block claims-unresolved for Q1's case]`, R28's test — where neither the walkthrough nor the backlog differs from `HEAD`, as after *Take* of committed answers and a later end, no commit is made and the report says the walk is already committed, naming the commit — else §6.3 over the walkthrough and the backlog, verb `record`. A record commit a hook refuses leaves the walkthrough dirty and the report says so. A `walk-*` exit 2 makes none (R14).
- [ ] **Step 4: Phase 6 and Phase 10 for a user unit.** Images placed first, as S2-D4's *Placement* says, each copy or creation an edited or created path; the brief's `answers.steps`, `answers.images`, `coverage`, `walkthrough`; then as batch 2. Phase 10's paths add each image and the walkthrough (R11); `edit … --walkthrough '<id>'` for a composed file; the body's `Walkthrough:` line.
- [ ] **Step 5: The report and follow-ups**: the walk (answers, their source, appended steps, slots filled and unfilled, images), the record commit and why, "run /docs-verify <id> to finish the walk" as a follow-up.
- [ ] **Step 6: Traces** (two review passes):
  - **Design fixtures:** T-U1 a composed walk to `verified` (the file, the stamp, the results, the page and the move in one commit); T-U2 a hand-written walkthrough extended (steps appended after the last `n`, `captures` byte-equal); T-U3 an `explanation` page, Q1's exit and token (RF2); T-U4 a blocked step's record commit with no token, then the next run's *Take* walking that step (RF4); T-U5 *Stop*, then a resume; T-U6 a build failing after apply — page restored, images moved under `unfinished/`, the walk recorded.
  - **Outside answers:** T-U7 uncommitted answers through *Proceed anyway*, and *Stash*, which Phase 4's re-check stops; T-U8 a CRLF page under `text=auto` (RF5: a scratch repository; `hash-object` equal at stamp and test, unequal to `rev-parse 'HEAD:./<path>'`), then `core.autocrlf` changed between runs (the answers void).
  - **Text and images:** T-U9 a `differs` holding markup (RF3); T-U10 an internal unit's image under `<content root>/internal/assets/<id>/`; T-U11 `images.root` outside the repository (a Phase 0 stop).
  - **Plan cases:** T-U12 a stamp naming another page; T-U13 a page edited after a stopped walk; T-U14 a named walkthrough of another unit (R7); T-U15 a fixed-id file of another unit; T-U16 an out-of-shape walkthrough (RF7); T-U17 the fitness *Cancel*; T-U18 *Take* with appended steps; T-U19 a refused record commit (dirty walkthrough named; the next run's §6.2 asks); T-U20 *Take* of answers already committed, then a build failing after apply (R28: no record commit, the walk named as committed) (P4).
- [ ] **Step 7: Gates** (selftest count recorded). **Step 8: Commit:** `feat(doc-d-g1): /docs-verify walks a user page — the composer, the walk, recorded answers, images and the record commit`.

### Task 3.4: Rules, references, pages and sweep, batch 3 [mechanical]

**Files:** `plugins/docs-workflows/commands/docs-write.md` (its *Next step* and follow-ups: run `/docs-verify <unit-id>` on each page drafted, whatever its audience) and `plugins/docs-workflows/docs/commands/docs-write.md` (the same, where Task 2.4 wrote it) (P5); EC:101 (who composes: `/docs-verify`, and `/docs-capture` when it ships) and EC:107 (`/docs-verify` asks each step in session; by hand otherwise), EC §5's first and third rules (S2-D9: `/docs-verify` takes results only behind a stamp naming the page as it stands; `/docs-capture`'s results carry no stamp and never count) and its second (a person verifying by hand records results with no stamp); BF §4's `claims-unresolved` gains the user case; FH §6 (§6.4 names images and says the walkthrough is never in its lists; §6.6 the source, the counts and the images); ROUTE step 6 (a user page walked by `/docs-verify`; by hand remains for an `explanation` page and any Q1 exit), :112 and the *Later* line; `.claude/rules/docs-workflows-backlog.md` (the map line's walk), `.claude/rules/docs-workflows.md:19` (`walkthrough-composer`); `CLAUDE.md` (*Exact copy*, batch 3); the pages naming the user route (`docs-workflow.md`, `workflow.md`, `reference/docs-evidence.md`, `docs-backlog.md`, `agents.md`, `references.md`).

- [ ] **Step 1: The sweep**, every subject, the probe; R17's line counted gone (0), and Task 2.4's string `each user page by hand` counted before and after over the scope, 0 after (P5). **Step 2: Edits; after counts. Step 3: Gates, with the mermaid gate. Step 4: Commit:** `docs(doc-d-g1): the walked page on the route, the contract and the rules`.

### Task 3.5: Release, batch 3 [mechanical]

- [ ] **Step 1: Merge; re-derive.** **Step 2: Versions:** `docs-workflows` next free minor (plan time 1.46.0); the description by *Exact copy*; no coupling bullet (the batch-2 bullet covers "1.45.0 or later"). The CHANGELOG names the stated limits: a page holding any rationale sentence takes Q1's exit; a walk's answers void when line-ending or filter settings change.
- [ ] **Step 3: `to-fix.md`**: **UNWALKABLE-CLAIMS** (Q1's recommendation); what each review left. **`to-test-on-real-project.md`**: a composed walk to `verified` on the bookstore demo, and a stop then resume. **Feature-gaps**: the versions.
- [ ] **Step 4: Gates. Step 5: Commit:** `release(doc-d-g1): docs-workflows <X> — /docs-verify walks user pages`.

### Task 3.6: Close, batch 3 [security-sensitive]

- [ ] **Step 1: Consistency**: the arrays; `WALK_REASONS` and EC §4's paragraph reason for reason; the three pins (marker phrase, visibility marker, slot comment); EC §4's example still `ok` under `walk-check`.
- [ ] **Step 2: No regression**: `/docs-write`'s T-WALK, T-N and a unit naming a stamped walkthrough (its `stamp` ignored as data, UB:43); an engineering T-E1 re-run.
- [ ] **Step 3: Fail-closed**: a walkthrough a link; a `walk-record` call whose `--n` names no step in `walk-check`'s `steps` (exit 3 `step-absent`, the file untouched — and the command never makes one, since it resolves each `n` against that set first) (m7); an observed text with an embedded newline via the free-text escape (re-asked, never written).
- [ ] **Step 4: GIT-G1 audit** (nothing under a GIT-G1 file or `plugins/workflows-core/`). **Step 5: Counts; the full CI list. Step 6: The PR text**, the two CI comments named as incomplete but true (the controller's QP2 ruling); the verification record written last.

---

# Batch 4 — `--prepare` (`feat/doc-d-g1-verify-prepare`)

*Usable:* the asynchronous walk; its answers are taken by batch 3's question.

### Task 4.1: `--prepare` [security-sensitive]

**Files:** `plugins/docs-workflows/commands/docs-verify.md` (signature, Phase 0's argument, Phase 1 test 6, Phase 3's array and text, Phase 5's prepare path, the report, the description by *Exact copy*); `references/docs-audit/evidence-contract.md` §5 (recording results by hand for a later run: the `result:` line form EC:117-125 shows, in the stamped file, then `/docs-verify <unit-id>`; the stamp left as it stands); `docs/commands/docs-verify.md`.

**Interfaces:** consumes Task 3.1's `walk-new`, `walk-append`, `walk-stamp`; Task 3.2's composer; FH §6 with the verb `prepare`.

- [ ] **Step 1: The flag.** Phase 0 strips `--prepare`, a bare flag, given at most once (R21 retired). Phase 1 test 6 refuses an engineering unit (`DOCS_VERIFY_PREPARE_ENGINEERING`). Phase 3's array is *Exact copy*'s prepare array; its text names the results the stamp will clear (m5).
- [ ] **Step 2: Phase 5 under `--prepare`** (S2-D4): the composer as in a walk, Q1's exit on `uncoverable`; `walk-new` or `walk-append`; `walk-stamp`, clearing every result; the `prepare` commit — §6.3 over the walkthrough and the backlog after `edit --from drafted --status drafted [--walkthrough '<id>']`; the checklist printed: the stamp, the preconditions, each step with its `expect`, each slot, every free text escaped, and the instruction to record results as EC §5 says and run `/docs-verify <unit-id>`; then Phase 11, the report and the tail.
- [ ] **Step 3: Traces:** T-P1 `--prepare`, then another author's answers committed, then `/docs-verify <id>` taking them behind the question that names the commit and its author; T-P2 the page rewritten after the prepare (answers void; restamp) and `core.autocrlf` changed (RF5); T-P3 `--prepare` on an engineering unit; T-P4 `--prepare` over hand-recorded results (named in the consent, cleared); T-P5 `--prepare` meeting an `uncoverable` claim (Q1's exit, no prepare commit); T-P6 `--prepare` twice (the second restamps).
- [ ] **Step 4: Gates. Step 5: Commit:** `feat(doc-d-g1): /docs-verify --prepare — a stamped walkthrough committed for a walk outside the session`.

### Task 4.2: Pages and sweep, batch 4 [mechanical]

**Files:** ROUTE step 6 (the asynchronous walk), FH §6.6 (any prepare commit), `.claude/rules/docs-workflows-backlog.md`'s map line, the pages naming `/docs-verify`'s signature.

- [ ] **Step 1: The sweep**; R21's absence claims counted gone. **Step 2: Edits; after counts. Step 3: Gates, with the mermaid gate. Step 4: Commit:** `docs(doc-d-g1): --prepare on the route and the pages`.

### Task 4.3: Release, batch 4 [mechanical]

- [ ] **Step 1: Merge; re-derive. Step 2: Versions:** `docs-workflows` next free minor (plan time 1.47.0); no coupling bullet. **Step 3: `to-test-on-real-project.md`**: a `--prepare` round trip with another author's answers. **`to-fix.md`**: what the reviews left. **Feature-gaps**: sub-project 2 complete, its four releases. **Step 4: Gates. Step 5: Commit:** `release(doc-d-g1): docs-workflows <X> — /docs-verify --prepare`.

### Task 4.4: Close, batch 4 [security-sensitive]

- [ ] **Step 1: Consistency**: every array, printed line and description in *Exact copy* verbatim in its owner across the whole sub-project.
- [ ] **Step 2: No regression**: T-U1 and T-E1 re-run; `/docs-write`'s T-N.
- [ ] **Step 3: GIT-G1 audit; the sweep's counts; the full CI list.**
- [ ] **Step 4: The design's notes.** Append under S2-D10 and S2-D9 a dated note giving the shape and the stamp test as built (R13, R14, R20), without rewriting the approved text.
- [ ] **Step 5: The PR text**; the verification record written last. The whole-branch review is the controller's: Fable against both designs and this plan.

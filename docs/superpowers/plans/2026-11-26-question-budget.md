# Question Budget Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every question the BRD route puts to a person earns its place: at most a budget of questions per sitting, duplicates merged, every answer applied to the whole question registry at once, strategic questions first when the registry is large, and the same rules in the customer's package prompt.

**Architecture:** One rulebook reference and two agents in `workflows-core` (a planner and an applier); one deterministic bookkeeping script in `product-workflows` (`question-registry.py`) that holds a run's registry, records what became of every question, cascades reopens and computes the account; `/brd-intake`, `/brd-interview`, `/brd-package` (via the customer-review schema) and `/brd-reconcile` call them. Delivered in four increments, each a release.

**Tech Stack:** Markdown prose programs (commands, agents, references) executed by Claude Code; Python 3 standard library for the script; the repository's gate chain (`.github/workflows/validate-catalog.yml`).

**Spec:** `docs/superpowers/specs/2026-11-26-question-budget-design.md` (approved 2026-11-26). Read it before any task; decisions are cited as D1–D16.

## Global Constraints

- Public repository: no customer, product, person or host name from the engagement anywhere — code, fixtures, docs, commit messages. Fixtures are synthetic and built at run time inside the selftest.
- Default budget **25** questions per sitting; `--budget <N>` accepts an integer **5 to 50**; anything else stops with `<CMD>_BAD_BUDGET: --budget takes a whole number from 5 to 50`.
- Strategic stop rule: offer the detailed walk (Recommended) once the open questions for a person are at most **2 × budget**; recommend another strategic sitting while above that and fewer than **3** strategic sittings have run; after 3, offer both and recommend the detailed walk.
- Grounding is untouched: no edit to `/prd-ground`, `code-grounder`, `design-grounder`, `grounding-verifier`, or `grounding-format`.
- Tag rules unchanged: `[G]` never asked; `[V]` never to the customer; a `[C]` becomes a `[CD#n]` only at `/brd-reconcile` on operator confirmation.
- The field for coverage is `covers`; the applied-from field is `applied_from`; never reuse `settles`.
- Every `choices:` array has 2–4 options and is presented verbatim; every command that asks a question loads `escalation-rules core` first (gated by `reference-parts.py check-questions`).
- A file outside `workflows-core` that cites `workflows-core:question-budget` carries the *Core references* preamble (check 16).
- Every new agent ends with the canonical `## Untrusted content` block copied byte for byte from `plugins/workflows-core/references/untrusted-content.md` between its `<!-- untrusted-content:begin -->` and `end` markers (check 20).
- Every number written into `CLAUDE.md`, `.claude/rules/` or a docs page is re-derived with the command beside it.
- Python: standard library only; atomic writes (temporary file beside the target, then replace); no output names a path; exit 0 ran, 2 unreadable/invalid state, 3 caller's input refused, 4 account does not close.
- **The gate chain** (run from the repo root, read the printed value): `python3 scripts/validate-catalog.py && ./scripts/check-id-grammar.sh --root . && ./scripts/check-id-grammar.sh --baseline && ./scripts/check-docs.sh --root . && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && python3 scripts/reference-parts.py check-branch-check && node scripts/mermaid/check-mermaid.mjs --root .; echo "EXIT=$?"` — expected `EXIT=0`. (`npm ci --prefix scripts/mermaid --ignore-scripts --no-audit --no-fund` once per worktree.)
- Verify `git branch --show-current` immediately before every commit. Work on `feat/question-budget`, cut from `design/question-budget`, in a worktree (`superpowers:using-git-worktrees`).

## Review Focus

1. **A re-run over a round written before this ships** (no registry, no `questions` account line): the registry is built from the round records as they stand, no existing entry is rewritten, and the account's baseline is appended once — pinned by Task 8's live check and the selftest `init_from_existing_states`.
2. **A held `[C]` whose bundle exists but cannot be read**: it is treated as carried and never rewritten, narrowed, re-tagged or closed — pinned by Task 10's step and the selftest `carried_refuses_all_but_proposed`.
3. **An operator who answers every question in free text**: each answer is read as the option it expresses and no dialog is put twice — pinned by Task 5's and Task 9's grep steps and a live check.
4. **A compaction or session stop mid-sitting**: the run resumes at the next unanswered question with every given answer kept and every applier result reused — pinned by the run-folder steps in Tasks 5 and 8 and a live check.
5. **An applied answer whose source decision, in a sibling slice, is superseded at `/brd-reconcile`**: the applied answer is reopened in this slice at its next interview — pinned by the selftest `reopen_cascades_cross_brd` and Task 16's step.

---

## Increment 1 — the rulebook, the registry, the agents, the intake walk

### Task 1: `question-registry.py`

**Files:**
- Create: `plugins/product-workflows/scripts/question-registry.py`
- Modify: `.github/workflows/validate-catalog.yml` (a step after *Self-test the ledger evidence writer*)

**Interfaces:**
- Produces (CLI; the registry file path is always `--registry <path>`):
  - `init` — stdin `{"budget": int, "questions": [Q, ...]}`; creates the registry; refuses an existing file (exit 3).
  - `add` — stdin `{"questions": [Q, ...]}`; appends (strategic questions, later rounds).
  - `merge --into <qid> --from <qid>[,<qid>...] --reason <text>`
  - `drop --qid <qid> --reason <text>`
  - `record --sitting <n>` — stdin one event `E`.
  - `reopen (--qid <qid> | --follows <decision-id>)` — `--follows` reopens every question whose `applied_from` is that id, transitively through the decisions those questions recorded; prints the reopened qids.
  - `next [--limit N]` — prints the open, non-carried qids in plan order: open strategic first, then by `rank`, then by qid; default limit = budget.
  - `sitting-list --sitting <n>` — prints markdown: `### Applied from <decision-id>` groups (one line per question: qid, derived answer, reason), then `### Merged`, `### Dropped`, `### Confirmed in a table`.
  - `account` — prints JSON `{"<tag>": {"generated", "retagged_in", "merged", "dropped", "auto", "applied", "table", "answered", "deferred", "open", "retagged_out"}, "closes": bool}`; exit 4 where any tag's `generated + retagged_in ≠ merged + dropped + auto + applied + table + answered + deferred + open + retagged_out`.
  - `--selftest`.
- `Q` = `{"qid": str matching ^[A-Za-z0-9/._-]+$ (interview "<round>/<position>", intake "cand/<n>"), "tag": "V"|"C"|"DEF", "text": str, "rows": ["[BR#n]"], "findings": ["[CG#n]"|"[DG#n]"], "strategic": bool, "covers": [qid], "carried": bool, "rank": int, "recommendation": str|null, "confidence": "high"|"medium"|"low"|null}`; a question in the file also carries `state` (`open`|`merged`|`dropped`|`auto`|`applied`|`table`|`answered`|`deferred`), `into`, `reason`, `decision`, `applied_from`, `proposed`, `sitting`.
- `E` = `{"qid", "event": "answered"|"applied"|"table"|"deferred"|"auto"|"narrowed"|"proposed"|"retagged", "decision"?, "applied_from"?, "answer"?, "reason"?, "text"?, "tag"?}`.
- Refusals (exit 3, nothing written): unknown qid; a state-changing event on a question not `open`; any event but `proposed` on a `carried` question; `answered`/`applied`/`table` on tag `C`; `applied` without `applied_from` and `decision`; `answered`/`table` without `decision`; `auto` on a tag other than `DEF`; `deferred` on tag `DEF` with a decision other than `sent-on-unreviewed`; `retagged` without `tag` and `reason`, or to the same tag; a merge across tags, into a question not `open`, or of a carried question. A decision id is `[VD#n]`, `[CD#n]`, or `<KEY>/[VD#n]` with `<KEY>` matching `^[A-Z][A-Z0-9_]*(-\d+)+$`; for tag `DEF` it is one of `confirmed`, `confirmed-narrowed`, `not-logged`, `noted-in-inventory`, `sent-on-unreviewed`.

- [ ] **Step 1: Write the failing selftest cases** in `selftest()` (fixtures built in a temporary directory), each asserting exit code and the registry or output after the call:
  - `init_and_account_closes` — 5 open questions: `account` → `generated 5, open 5`, `closes: true`, exit 0.
  - `init_refuses_existing_registry` — exit 3, file unchanged.
  - `merge_records_and_counts`; `merge_across_tags_refused` (exit 3).
  - `applied_requires_from_and_decision`; `applied_on_C_refused`; `auto_only_for_DEF`.
  - `carried_refuses_all_but_proposed` — every event but `proposed` exits 3; `proposed` sets `proposed`, state stays `open`.
  - `reopen_cascades_transitively` — q1 answered `[VD#1]`; q2 applied from `[VD#1]` as `[VD#2]`; q3 applied from `[VD#2]` as `[VD#3]`; `reopen --follows [VD#1]` prints q2 and q3, both `open`; q1 stays `answered`.
  - `reopen_cascades_cross_brd` — `applied_from: "PRD-X-02/[VD#4]"` reopens on `--follows PRD-X-02/[VD#4]`.
  - `retag_moves_counts` — a `C` retagged to `V`: `C.retagged_out 1`, `V.retagged_in 1`, `closes: true`.
  - `next_orders_and_skips` — open strategic first, then rank, skips closed and carried, honours `--limit` and the default budget.
  - `sitting_list_groups_by_source` — two questions applied from `[VD#1]` appear under one `### Applied from [VD#1]` heading; merges and drops appear in their sections.
  - `account_detects_gap` — a hand-corrupted state value → exit 2; a registry edited to drop a question's state accounting → exit 4.
  - `init_from_existing_states` — `init` accepts `Q` objects carrying a `state` already terminal (a round written earlier), counts them in the account, and refuses events on them.
  - `atomic_write_leaves_no_temp` — no stray file beside the registry after a refused and after a successful write.

- [ ] **Step 2: Run and see it fail**

Run: `python3 plugins/product-workflows/scripts/question-registry.py --selftest`
Expected: non-zero exit (subcommands not implemented).

- [ ] **Step 3: Implement the subcommands** in the file's own style (`ledger-evidence.py` is the model: module docstring stating the contract and exit codes, `argparse` subparsers, `Refused`/`InputRefused` exceptions mapped to exits 2/3).

- [ ] **Step 4: Run and see it pass**

Run: `python3 plugins/product-workflows/scripts/question-registry.py --selftest`
Expected: exit 0, every case named as passed.

- [ ] **Step 5: Add the CI step** — name `Self-test the question registry`, a comment saying which commands call it and that a silent miscount would let a question vanish from the account, `run: python3 plugins/product-workflows/scripts/question-registry.py --selftest`.

- [ ] **Step 6: Commit** — `feat(question-budget): question-registry.py — the registry, the account and the reopen cascade`.

### Task 2: The rulebook `workflows-core:question-budget`

**Files:**
- Create: `plugins/workflows-core/references/question-budget.md`
- Modify: `plugins/workflows-core/docs/reference/references.md` (an entry; the file count, re-derived with `find plugins/workflows-core/references -type f | wc -l`), `.claude/rules/workflows-core.md` (the reference count; an Authorities paragraph), `CLAUDE.md` § Shared authorities (one line → `workflows-core.md`)

**Interfaces:**
- Produces sections other tasks cite by number: §1 Terms · §2 The value test (D2) · §3 The budget (default, range, flag text) · §4 The question shape (D5, the fixed copy below) · §5 Merging (D4) · §6 Ranking (cites `workflows-core:grilling-technique`'s Impact × Uncertainty; adds coverage count first) · §7 Strategic sittings (D6, the stop rule from Global Constraints) · §8 Applying forward (D7: after each answer; one-line derivation or narrow; never a carried `[C]`; a `[C]` becomes a proposal or a re-tag) · §9 The tail table (D8) · §10 The end-of-sitting list (grouped by source; merges, drops; one question) · §11 The account (D16, the identity from Task 1) · §12 The registry (names `question-registry.py`, its subcommands, and that the registry file lives in the caller's run folder as `question-registry.json`) · §13 The customer block.
- §4 fixed copy: the recommended option is labelled `<label> (Recommended — <why>)`, resolved per showing; selecting it records `<why>` as the argumentation; "why" is asked only for a choice with no stated reason and no free text; every claim a question makes about a `[BR#n]`, a finding or the code is checked against its source before the question is written; a typed answer is read as the option it expresses, with one clarifying question only where it maps to none, and the same dialog is never put twice.
- §13 is plain text between `<!-- question-budget:customer:begin -->` and `<!-- question-budget:customer:end -->`, written for an agent with nothing installed: strategic questions first; at most 25 questions a sitting, offering to stop and continue; apply each answer to every question it settles and mark it in the decision log as applied, naming the answer it follows; show the applied answers at the end of each sitting grouped by the answer they follow; put proposals as tables; for requirement traceability propose `confirmed` where the package's reading matches the customer's own source text and ask only about mismatches. No slash command, agent, skill, plugin path or tool name.

- [ ] **Step 1: Write the check that fails** — `grep -c 'question-budget:customer:begin' plugins/workflows-core/references/question-budget.md` → expected `1` (fails: no file).
- [ ] **Step 2: Write the reference** with the sections above; it carries no entry point; it is read whole.
- [ ] **Step 3: Check the customer block is plugin-free** — extract the lines between the markers to a temporary file and run `python3 plugins/product-workflows/scripts/bundle-scan.py tokens <file>`; expected: no hit, exit 0.
- [ ] **Step 4: Add the docs entry, the rules paragraph and the `CLAUDE.md` line;** re-derive the counts.
- [ ] **Step 5: Run the gate chain** — expected `EXIT=0`.
- [ ] **Step 6: Commit** — `feat(question-budget): workflows-core:question-budget, the rulebook`.

### Task 3: The agents `question-planner` and `answer-applier`

**Files:**
- Create: `plugins/workflows-core/agents/question-planner.md`, `plugins/workflows-core/agents/answer-applier.md`
- Modify: `plugins/workflows-core/docs/reference/agents.md` (two rows; "eleven" → the count from `ls plugins/workflows-core/agents | wc -l`), `.claude/rules/workflows-core.md` (agent list, count, caller lines `question-planner (workflows-core) (used by /brd-intake, /brd-interview)`, `answer-applier (workflows-core) (used by /brd-interview)`)

**Interfaces:**
- Both: frontmatter `tools: ["Read", "Glob", "Grep", "Write"]`, no `model:` pin; callers dispatch them on the Opus chain (`workflows-core:model-routing/classification` §2), as `architecture-grounder` is, recorded in `agents.md` as "per routing (dispatch-pinned to the Opus chain)". Each takes `input_path` (a JSON file) and `result_path`, writes its whole result to `result_path` and nothing else, and replies with one line: `RESULT <result_path> <counts>`.
- `question-planner` input: `{"mode": "merge"|"plan"|"strategic"|"intake", "budget": int, "questions": [Q], "decisions": [{"id", "statement", "chosen", "argumentation"}], "findings": [{"id", "verdict", "evidence"}]}`. Output: `{"merges": [{"into", "from": [qid], "reason"}], "drops": [{"qid", "reason"}], "strategic": [{"text", "why", "covers": [qid], "options": [str], "recommended": str, "reason": str, "tag": "V"|"C"}], "groups": [{"text", "covers": [qid], "reason"}], "plan": {"ask": [qid], "table": [{"qid", "answer", "reason"}], "wait": [qid]}, "code_defects": [{"qid", "behaviour": "[CG#n]", "intent_basis": str, "statement", "intent"}]}`; a field the mode does not produce is `[]`. Mode `merge` produces `merges` and `drops`; `plan` produces `plan` and `code_defects`; `strategic` produces `strategic` and `plan`; `intake` produces `groups` and `plan`.
- `answer-applier` input: `{"answer": {"qid", "decision", "statement", "chosen", "argumentation"}, "candidates": [Q], "decisions": [...]}`. Output: `{"results": [{"qid", "verdict": "determined"|"narrowed"|"untouched"|"proposal"|"retag", "answer"?, "reason", "text"?}]}` — `determined` only with a one-line derivation; `proposal` and `retag` only for tag `C`; never `determined` for tag `C`; never anything but `untouched` for a carried question.
- `code_defects` entries only where `intent_basis` cites a test, comment, document, design or another code path already present in the input's findings or documentation (D13) — never the BRD.

- [ ] **Step 1: Write the failing check** — `./scripts/check-docs.sh --root .` after creating only the agent files: expected FAIL `agent 'question-planner' has no row in reference/agents.md`.
- [ ] **Step 2: Write both agents** — sections `## Inputs`, `## Process`, `## Output`, `## Hard rules` (the one-write rule, read only what the input names, never close on a guess, the tag rules above), then the canonical `## Untrusted content` block.
- [ ] **Step 3: Add the docs rows and rules lines;** re-derive counts.
- [ ] **Step 4: Run the gate chain** — expected `EXIT=0`.
- [ ] **Step 5: Commit** — `feat(question-budget): question-planner and answer-applier agents`.

### Task 4: `brd-reader`'s candidates and the split rule

**Files:**
- Modify: `plugins/product-workflows/agents/brd-reader.md`, `plugins/product-workflows/references/brd-format.md` (§2, §2.1, §3), `plugins/product-workflows/docs/reference/` page(s) that describe the inventory or defect classes (find with `grep -l 'split is one defect\|brd-inventory' plugins/product-workflows/docs -r`)

**Interfaces:**
- `brd-reader` gains input `result_path` and tool `Write` (its one permitted write); replies `RESULT <result_path> rows=<n> candidates=<n>`.
- Each `defect_candidates` entry gains `confidence: high|medium|low` and, by class: `readings: [str, str, ...]` (ambiguity, at least two), `clash: str` (conflict), `missing_measure: str` (untestable), `prescribes: str` (scope-leak). A new top-level `splits: [{row: "[BR#n]", split_from: str}]` replaces the `duplicate` candidates a split used to raise.
- `brd-format` §2.1: the inventory may end with `## Inventory notes`, lines `- [BR#n] — split from <item>` and `- [BR#n] — restates [BR#m]`; §2's *The split is one defect* is replaced by the split note; a log already on file keeps its split entries.

- [ ] **Step 1: Count the claims before editing** — `grep -c 'split is one defect' -r plugins/` and every phrasing of the split rule found by `grep -rn -i 'split' plugins/product-workflows/references/brd-format.md`; record the numbers.
- [ ] **Step 2: Edit `brd-reader` and `brd-format`.**
- [ ] **Step 3: Check every reader of the inventory tolerates the notes section** — `grep -l 'brd-inventory' plugins/*/commands/*.md plugins/*/agents/*.md plugins/*/scripts/*.py`; for each, confirm it reads the table only (or add that sentence); list the files checked in the commit message.
- [ ] **Step 4: Recount** — the split-rule phrase count is 0 outside `CHANGELOG.md`.
- [ ] **Step 5: Run the gate chain** — `EXIT=0`.
- [ ] **Step 6: Commit** — `feat(question-budget): brd-reader returns readings and confidence; a split is an inventory note`.

### Task 5: The `/brd-intake` defect walk

**Files:**
- Modify: `plugins/product-workflows/commands/brd-intake.md` (Phase 0 flags, Phase 3 dispatch, Phase 4, Phase 5, Final report), `plugins/product-workflows/docs/commands/brd-intake.md`

**Interfaces:**
- Consumes: Task 1 (`init`, `record`, `next`, `account` with tag `DEF`), Task 2 (§3, §4, §6, §9, §11), Task 3 (`question-planner` mode `intake`), Task 4 (candidate fields, `splits`), `workflows-core:run-folder` (`open-run`, `run-dispatch` for `brd-reader` and the planner, `run-gate` for each answer, `close-run`).
- Fixed copy (D12, user's wording):
  - Walk intro: "These questions check the wording of the BRD. A problem you confirm becomes a question to the customer later; one you mark clear is dropped. Each question shows what I saw and the answer I recommend."
  - First line of each question: `This is about the wording of requirement [BR#n] in the BRD.`
  - `choices: ["Ask the customer about this", "Ask the customer, about a narrower point (you'll be prompted)", "The wording is clear — nothing to ask", "Cancel"]`, the recommended one carrying `(Recommended — <why>)` per showing. Descriptions: "Logged as an open [DEF#n]; the interview later asks the customer, built from this reason." / "Logged with a reason you narrow first; the customer's question is built from it." / "Not logged; nothing goes to the customer about this wording." / "End the run here, before any defect is logged."
  - The one list question for unsourced and restatements: `choices: ["All fine as listed (Recommended)", "Let me name the ones to look at"]`.
  - After the budget: `choices: ["Continue with the next sitting now (Recommended)", "Stop here and continue later", "Send the rest on as open defects, unreviewed"]`.

- [ ] **Step 1: Count the claims to retire** — `grep -c 'No option carries `(Recommended)`' plugins/product-workflows/commands/brd-intake.md` (expect 1) and the word-for-word descriptions block; record.
- [ ] **Step 2: Phase 0** — parse `--budget` (Global Constraints range and stop text); open the run folder.
- [ ] **Step 3: Phase 3** — dispatch `brd-reader` with `result_path` through `run-dispatch`; read the result file.
- [ ] **Step 4: Phase 4** — rewrite: print the intro; record `splits` as notes (no question); auto-record `unsourced` (`auto`, decision `confirmed`); put restatement `duplicate` candidates in the one list question (`table` with `noted-in-inventory`, or walked where named); dispatch the planner (mode `intake`) to group the rest; ask at most the budget in §4's shape, by `next`; table the confident beyond the budget; offer the next sitting with the three-way choice; persist every answer with `run-gate` and `record`; typed answers per §4; keep the existing on-file matching rules unchanged.
- [ ] **Step 5: Phase 5** — write `## Inventory notes`; write `[DEF#n]` only for `confirmed`, `confirmed-narrowed` and `sent-on-unreviewed` (the last recorded as `deferred` in the registry and marked `not reviewed at intake` in its reason).
- [ ] **Step 6: Final report** — the intake account from `account`; exit 4 reported as a defect of the run.
- [ ] **Step 7: Recount** — the Step 1 phrase count is 0; `grep -c 'This is about the wording of requirement' plugins/product-workflows/commands/brd-intake.md` ≥ 1; `grep -n 'read as the option it expresses' plugins/product-workflows/commands/brd-intake.md` ≥ 1 line in Phase 4 (Review Focus 3).
- [ ] **Step 8: Docs page** — synopsis (`--budget`), Phase 4 described from the command.
- [ ] **Step 9: Run the gate chain** — `EXIT=0`.
- [ ] **Step 10: Commit** — `feat(question-budget): /brd-intake asks at most a budget of plain-language wording questions`.

### Task 6: Release increment 1

**Files:**
- Modify: `plugins/workflows-core/.claude-plugin/plugin.json`, `plugins/product-workflows/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, both `CHANGELOG.md`, `.claude/rules/plugin-updates-coupling.md`, `.claude/rules/brd-route.md` (`/brd-intake` map line; `brd-reader` caller line unchanged), `docs/superpowers/to-test-on-real-project.md`, `docs/superpowers/to-fix.md` (delete nothing; this increment closes no LB item)

- [ ] **Step 1: Versions** — next minor of each at release time (at writing: `workflows-core` 1.101.0, `product-workflows` 3.89.0), in both `plugin.json` and `marketplace.json`.
- [ ] **Step 2: CHANGELOG sections**, dated, each opening with **What changes for you.**; coupling bullet: `product-workflows` 3.89.0 needs `workflows-core` 1.101.0 (it cites `question-budget` and dispatches `question-planner`); an older `workflows-core` beside it fails at the loader.
- [ ] **Step 3: Claim sweep** (`.claude/rules/claim-sweep.md`) over `plugins/`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/` for every statement of the retired walk behaviour; count before and after.
- [ ] **Step 4: Live checks** in `to-test-on-real-project.md`: a free-text answer in the walk; a stop mid-walk and a resume; a BRD whose candidates exceed two sittings.
- [ ] **Step 5: Run the gate chain and every selftest step of `validate-catalog.yml`** — `EXIT=0`.
- [ ] **Step 6: Commit** — `release(question-budget-1): workflows-core 1.101.0, product-workflows 3.89.0`.

---

## Increment 2 — the interview: one question per row, the registry, applying forward, bulk paths, the code-defect question

### Task 7: One question per row across repositories (D14)

**Files:**
- Modify: `plugins/product-workflows/commands/brd-interview.md` (Phase 3, *Round 1 is generated from the grounding*, the `NOT-PROVABLE` bullet; Phase 10's `unsourced` close test), `plugins/product-workflows/references/interview-tagging.md` §3, `plugins/product-workflows/docs/commands/brd-interview.md`

**Interfaces:**
- Fixed rule text: "A row raises a question for an unsettled claim only where no repository in the run settles it; a repository settles it where its verified finding carries a verdict other than `NOT-PROVABLE` and a verifier outcome other than `unprovable`."

- [ ] **Step 1: Count the statements of the per-finding rule** — every sentence saying a `NOT-PROVABLE` finding raises a question, across `plugins/` and the docs pages; record.
- [ ] **Step 2: Edit** the three places to the fixed rule text.
- [ ] **Step 3: Recount** — each old statement rewritten; count as intended.
- [ ] **Step 4: Run the gate chain** — `EXIT=0`.
- [ ] **Step 5: Commit** — `feat(question-budget): /brd-interview raises one question per row, not per repository`.

### Task 8: The registry, merging and applying forward in `/brd-interview`

**Files:**
- Modify: `plugins/product-workflows/commands/brd-interview.md` (Phase 0, Phase 2, Phase 4, Phase 6, Phase 7, Phase 9, Final report), `plugins/product-workflows/references/decision-register-format.md` (§1 fields, §4 reopening, §9 worked example), `plugins/product-workflows/references/interview-tagging.md` §5 (state vocabulary), `plugins/product-workflows/docs/commands/brd-interview.md`

**Interfaces:**
- Consumes: Task 1 (all subcommands), Task 2 (§5, §8, §10, §11, §12), Task 3 (planner mode `merge`; applier), `workflows-core:run-folder`.
- `decision-register-format` §1 gains `taken: asked | applied | table` (omitted reads as `asked`, so every register on file stays valid) and `applied_from: <decision-id>` (only where `taken: applied`; cross-BRD form allowed). §4: reopening, superseding or withdrawing a decision reopens every decision whose `applied_from` names it, transitively.
- Round-record state lines: `- **State:** applied — [VD#n], from <decision-id>`, `- **State:** merged into <round>/<position>`, `- **State:** dropped — <reason>`, `- **State:** confirmed in a table — [VD#n]`. Account line, once per run's last write: `questions [V]: generated N + retagged in N = merged N + dropped N + applied N + table N + answered N + deferred N + open N + retagged out N` and the same for `[C]`.
- Registry scope (D7 *Reach*): every open question on file in the slice, every round; a held `[C]` is `carried` where its round and position appear in any `bundle-*/` on file, or where a bundle exists that cannot be read.
- *What is on file*: this slice's register, its sibling slices' under the same parent, and each `depends-on:` BRD's.

- [ ] **Step 1: Phase 0/2** — open the run folder; `init` the registry from the round records as they stand (terminal states carried in), mark carried `[C]`s; `--budget` parsed.
- [ ] **Step 2: Phase 4** — after tagging, the planner in mode `merge`; record merges and drops; the end-of-sitting list later shows them.
- [ ] **Step 3: Phases 6 and 7** — after each answer: record it; settle the answer's `covers` mechanically; dispatch the applier over the remaining open questions; record each `determined` as `applied` (a `[VD#n]` written with `taken: applied` and `applied_from`), each `narrowed` as `narrowed`; never ask a closed question (`next`).
- [ ] **Step 4: End of each sitting** — print `sitting-list`; one question `choices: ["All correct (Recommended)", "Let me name the ones to reopen"]`; `reopen` what is named and every decision that follows it.
- [ ] **Step 5: Phase 9** — the state lines and the account line above; per-sitting writes append state lines and register blocks, the account and `Status:` lines once at the run's last write; exit 4 from `account` reported as a defect of the run.
- [ ] **Step 6: The register and tagging references** — §1 fields, §4 cascade, §9 example; §5 vocabulary.
- [ ] **Step 7: Live checks** in `to-test-on-real-project.md`: a re-run over a round written before this release (Review Focus 1); a stop mid-sitting and a resume (Review Focus 4).
- [ ] **Step 8: Run the gate chain** — `EXIT=0`.
- [ ] **Step 9: Commit** — `feat(question-budget): /brd-interview keeps a question registry and applies every answer to it`.

### Task 9: The question shape, the table and the bulk paths in Phase 6

**Files:**
- Modify: `plugins/product-workflows/commands/brd-interview.md` (Phase 6), `plugins/product-workflows/docs/commands/brd-interview.md`

**Interfaces:**
- Consumes: Task 2 §3, §4, §9; Task 8's registry.
- Each detailed sitting opens with the planner in mode `plan` over the open registry; Phase 6 then asks at most the budget per sitting, by `next`, in §4's shape; the argumentation is the recommended option's stated reason where that option is chosen; the separate "why" prompt fires only per §4.
- A deferral may name the held `[C]`s it waits on, appended as `- **Blocked-on:** <round>/<position>, …`; Phase 2 surfaces a deferred `[V]` whose blocking `[C]`s now carry a `[CD#n]`, with that customer answer as its recommendation (D7).
- Tail table: one `choices: ["Accept all as recommended (Recommended)", "Let me name the exceptions"]` over the planner's `plan.table`; each accepted row recorded `table` (`taken: table`).
- At the budget: `choices: ["Continue with the next sitting now (Recommended)", "Stop here and continue later", "Defer the rest, with one reason (you'll be prompted)"]`; the third records `deferred` per question with the shared reason.

- [ ] **Step 1: Count the retired claims** — `grep -c 'exactly one at a time, never batched' plugins/product-workflows/commands/brd-interview.md` and its statements in the docs page; record.
- [ ] **Step 2: Edit Phase 6** — keep one question per `AskUserQuestion` for every asked question; the table and the end-of-sitting list are the two sanctioned multi-item prompts, named as such beside the one-at-a-time rule.
- [ ] **Step 3: Recount** — no sentence left saying nothing is ever batched without naming the two exceptions.
- [ ] **Step 4: Typed-answer check** — `grep -n 'read as the option it expresses' plugins/product-workflows/commands/brd-interview.md` ≥ 1 line in Phase 6 (Review Focus 3).
- [ ] **Step 5: Run the gate chain** — `EXIT=0`.
- [ ] **Step 6: Commit** — `feat(question-budget): /brd-interview Phase 6 — budget, plain-language shape, table, defer the rest`.

### Task 10: Held `[C]` questions: proposals, re-tags, carried entries

**Files:**
- Modify: `plugins/product-workflows/commands/brd-interview.md` (Phase 7), `plugins/product-workflows/references/interview-tagging.md` §3, `plugins/product-workflows/references/decision-register-format.md` (the held entry's lines), `plugins/product-workflows/docs/commands/brd-interview.md`

**Interfaces:**
- Consumes: Task 3 applier verdicts `proposal`, `retag`; Task 1 `proposed`, `retagged`.
- Held entry lines in the round record and `interview/customer-questions.md`: `- **Proposed answer:** <text> — follows <decision-id>`; a re-tag appended as `- **Re-tagged:** [C] → [V] — <reason>`, after which the question is decided or applied as a `[V]`.
- A carried `[C]` is never edited; an applier `proposal` for it is recorded with `proposed` only and shown in the next package beside the entry.

- [ ] **Step 1: Phase 7** — record `proposal` and `retag` verdicts; append the lines; leave carried entries untouched (Review Focus 2).
- [ ] **Step 2: Sweep** — the statements that only `/brd-reconcile` closes a round holding a `[C]` (in `brd-package.md`, `interview-tagging.md`, `brd-interview.md`): rewrite each to name the re-tag path; count before and after.
- [ ] **Step 3: Run the gate chain** — `EXIT=0`.
- [ ] **Step 4: Commit** — `feat(question-budget): a delivery-team answer turns a held [C] into a proposal or corrects its tag`.

### Task 11: The code-defect question (D13)

**Files:**
- Modify: `plugins/product-workflows/commands/brd-interview.md` (Phase 6, *Then, on exactly one condition, offer to record a code defect*), `plugins/product-workflows/references/code-defect-log-format.md` (§2 table's trigger note), `plugins/product-workflows/docs/commands/brd-interview.md`

**Interfaces:**
- Consumes: Task 3 planner `code_defects`.
- Fixed copy: opening sentence "A code defect here means existing code that fails what it was itself meant to do — a bug that exists today, independent of this BRD."; `choices: ["No — not a code defect", "Yes — record a code defect (you'll be prompted)"]`, the recommendation per showing; descriptions: "Nothing is recorded." / "Records a [CDF#n] that goes to the customer in the package with a scope decision, and is priced by the effort proposal."

- [ ] **Step 1: Count** the statements of the old trigger (`REWRITTEN`, `AMENDED` or `FALSE-FRIEND` as the offer's condition) across `plugins/` and docs; record.
- [ ] **Step 2: Replace the offer** with the planner-raised question; keep *the operator may raise one at any point* and the reviewer residue check.
- [ ] **Step 3: Recount** — the old trigger stated nowhere as the offer's condition.
- [ ] **Step 4: Run the gate chain** — `EXIT=0`.
- [ ] **Step 5: Commit** — `feat(question-budget): the code-defect question only with an intent basis`.

### Task 12: Release increment 2

- [ ] **Step 1:** `product-workflows` next minor (at writing 3.90.0) in `plugin.json` and `marketplace.json`; dated `CHANGELOG.md` section; coupling bullet if it needs a newer `workflows-core` than 1.101.0.
- [ ] **Step 2:** `.claude/rules/brd-route.md` `/brd-interview` map line (registry, planner, applier, end-of-sitting list); `.claude/rules/workflows-core.md` caller lines.
- [ ] **Step 3:** Claim sweep over refinement 4's scope; count before and after.
- [ ] **Step 4:** Gate chain and every selftest — `EXIT=0`.
- [ ] **Step 5: Commit** — `release(question-budget-2): product-workflows 3.90.0`.

---

## Increment 3 — strategic sittings

### Task 13: The strategic mode of `/brd-interview` (D6)

**Files:**
- Modify: `plugins/product-workflows/commands/brd-interview.md` (after Phase 4: a new phase *Plan the sittings*), `plugins/product-workflows/references/interview-tagging.md` §5, `plugins/product-workflows/docs/commands/brd-interview.md`, `plugins/product-workflows/docs/brd-workflow.md` (prose; the diagram only if a step it draws changes)

**Interfaces:**
- Consumes: Task 3 planner mode `strategic`; Task 1 `add` (strategic questions, `strategic: true`, `covers`), `next`; Global Constraints stop rule.
- Scale statement before the first sitting: `Questions for a person after merging: <N> ([V] <n>, [C] <n>). Plan: strategic sittings first, then the detailed walk. Expected agent dispatches: <planner 1 per sitting + applier 1 per answer>.`
- Strategic `[V]`s are asked in the interview; strategic `[C]`s are written as entries of the current round (round and position like any held `[C]`) with `- **Why we ask:**`, `- **Covers:** <round>/<position>, …` and `- **Proposed answer:**`.
- After each strategic sitting: applier sweep, re-plan, the stop-rule choice `choices: ["Another strategic sitting (Recommended)", "Go to the detailed questions"]` with the recommendation set by the rule.

- [ ] **Step 1: Write the phase** — trigger (open questions for a person > budget), scale statement, planner dispatch, strategic entries, stop rule, the registry kept whole (D6).
- [ ] **Step 2: Rounds** — state in `interview-tagging` §5 that a strategic sitting is a sitting of the current round and how its entries are numbered.
- [ ] **Step 3: Live check** in `to-test-on-real-project.md`: a synthetic slice of several hundred questions reaches the detailed walk after at most three strategic sittings with at most 2 × budget questions left (goal 9).
- [ ] **Step 4: Run the gate chain** — `EXIT=0`.
- [ ] **Step 5: Commit** — `feat(question-budget): strategic sittings over the kept registry`.

### Task 14: Release increment 3

- [ ] **Step 1:** `product-workflows` next minor (at writing 3.91.0); dated CHANGELOG; map line; claim sweep; gate chain and selftests `EXIT=0`.
- [ ] **Step 2: Commit** — `release(question-budget-3): product-workflows 3.91.0`.

---

## Increment 4 — the customer side

### Task 15: The package prompt (D11)

**Files:**
- Modify: `plugins/product-workflows/references/customer-review-schema.md` (§1 note on the inlined block; §4 sections 4 and 7; §5 rules), `plugins/product-workflows/commands/brd-package.md` (*Render the prompt*: inline `workflows-core:question-budget` §13 verbatim; render strategic `[C]`s and proposals first, tables for proposals), `plugins/product-workflows/references/bundle-packaging.md` (only if the allow-list or §1.2 needs a line), `plugins/product-workflows/docs/commands/brd-package.md`

**Interfaces:**
- Consumes: Task 2 §13; Task 10 held-entry lines; Task 13 strategic entries.
- Review section 7 rows gain `applied from <round>/<position>` where the customer's agent applied an answer; section 4 states the pre-fill rule from §13.

- [ ] **Step 1:** Edit `brd-package` to load `workflows-core:question-budget` (Core references preamble present) and inline §13 between its markers.
- [ ] **Step 2:** Edit the schema sections and rules.
- [ ] **Step 3: Plugin-free check** — write a temporary fixture holding the inlined §13 block, one strategic `[C]` entry and one proposal entry as the prompt renders them, and run `python3 plugins/product-workflows/scripts/bundle-scan.py tokens <fixture>` — expected: no hit, exit 0.
- [ ] **Step 4: Run the gate chain** — `EXIT=0`.
- [ ] **Step 5: Commit** — `feat(question-budget): the customer's prompt carries the question rules`.

### Task 16: `/brd-reconcile` reads applied answers

**Files:**
- Modify: `plugins/product-workflows/commands/brd-reconcile.md` (confirm candidates; freeze; propagation sweep), `plugins/product-workflows/agents/customer-review-reader.md` (section 7 `applied from`), `plugins/product-workflows/docs/commands/brd-reconcile.md`

**Interfaces:**
- A section-7 row marked `applied from <round>/<position>` is confirmed in a group with the answer it follows: `choices: ["Confirm the answer and every answer applied from it (Recommended)", "Let me name the ones to correct"]`; each confirmed becomes a `[CD#n]` with `taken: applied` and `applied_from` the `[CD#n]` of the answer it follows.
- The propagation sweep follows `applied_from` as it follows `conditional_on`, across BRDs; a superseded or withdrawn source reopens its applied decisions in their own slices (Review Focus 5).

- [ ] **Step 1:** `customer-review-reader` returns the `applied from` marker per row.
- [ ] **Step 2:** `brd-reconcile` group confirmation and freeze.
- [ ] **Step 3:** The propagation sweep; a live check entry for a sibling-slice supersession reopening an applied answer.
- [ ] **Step 4: Run the gate chain** — `EXIT=0`.
- [ ] **Step 5: Commit** — `feat(question-budget): /brd-reconcile confirms applied answers by group and cascades their source`.

### Task 17: Release increment 4 and the measurement

- [ ] **Step 1:** `product-workflows` next minor (at writing 3.92.0); dated CHANGELOG; coupling bullet if needed; map lines for `/brd-package` and `/brd-reconcile`; claim sweep.
- [ ] **Step 2: Measure goal 9** on a synthetic slice shaped like the engagement (several hundred rows, findings across several repositories with most rows absent from most, repeated questions in other words, questions an earlier answer settles): intake ≤ budget + one table; interview ≤ 3 strategic sittings before ≤ 2 × budget remain; record the numbers in `docs/superpowers/verification/2026-11-question-budget.md`, written last. The real engagement may be measured locally and never committed.
- [ ] **Step 3:** Gate chain and every selftest — `EXIT=0`.
- [ ] **Step 4: Commit** — `release(question-budget-4): product-workflows 3.92.0; verification record`.

# D32 Document Lineage (part 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every `specification.md`, `epic.md` and `design.md` records the exact upstream bytes it was built from, and `/specify`, `/epics`, `/design` and `/update-spec` walk that record up the chain and ask when an upstream's items moved.

**Architecture:** One script, `plugins/workflows-core/scripts/lineage.py`, does every git read, frontmatter write and comparison; its kind table is `lineage-kinds.json` beside it. A new shared reference, `workflows-core:document-lineage`, owns the record format, the moved rule, the table (by citing the JSON) and the `upstream-check` entry point; the four commands call the script through it.

**Tech Stack:** Python 3 standard library only (as every family script); git CLI; markdown command/reference prose.

**Spec:** `docs/superpowers/specs/2026-11-03-d32-document-lineage-design.md`

## Global Constraints

- Work in worktree `$S/wt-d32`, branch `feat/d32-document-lineage`; `git branch --show-current` before every commit; commit trailer as in the repo's session rules.
- A moved upstream **asks, never hard-stops**; only a script failure stops (`<COMMAND>_LINEAGE_FAILED`).
- Record keys: `upstreams:` entries `{path, blob, version}`; `accepted:` entries `{path, blob}`; `path` relative to `$SPECS_PATH`; `blob` = `git hash-object` (no `-w`) of the bytes the run read; `version` null where the kind has none.
- Question text, verbatim: `choices: ["Stop — revise <highest stale document> first with <reviser> (Recommended)", "Proceed — record that I accepted these upstreams"]`, preceded by a **Load the question rules.** step if the command lacks one (`check-questions` gates it).
- Display identity: `Version` where the kind carries one (`specification.md`, `design.md`), else the 7-char blob id. Item keys are full ID paths where IDs restart (`[U02]/[AC01]/[TC03]`).
- Covered kinds this part: `specification.md`, `epic.md`, `design.md`. Upstream-only: `prd.md`, ARD (`ard.md`, `ard-<area>.md`), `code-grounding.md`, `design-grounding.md`, `decisions.md`, `idea.md`. An upstream-only document never asks for a missing record.
- `/specify` and `/update-spec` stop writing `inputs_at`; `/update-spec` still reads it as a fallback.
- Size limits: `CLAUDE.md` < 36,000 chars (now 35,336); each `.claude/rules/*.md` < 20,000 (`dev-workflows.md` 20,173 and `plugin-updates-coupling.md` 20,061 are **already over** — net-shrink any edit there; the coupling overflow moves to `plugin-updates-coupling-history.md`, whose boundary statement appears in four places and moves with it).
- After editing a reference that loads by part or has entry files: `python3 scripts/reference-parts.py generate`, then `check-parts` and `check-citations`.
- No tracker, organisation or client name anywhere; bracketed `[PREFIX#N]` ID grammar only.

## Review Focus

1. **A note-only change to `specification.md`** (an `## Engineering review` section, a `- [ ]` → `- [x]` tick, an `Engineering proposal (/design):` line) must not count as moved — selftest `test_notes_only_not_moved` (Task 1).
2. **A superseded/withdrawn marker added to an item** must show as `withdrawn`/`changed`, and items nested under it must not each be reported as changed — selftest `test_marker_reports_once` (Task 1).
3. **A recorded blob absent from the clone** (working-tree bytes never committed) must report `unavailable`, not crash — selftest `test_blob_unavailable` (Task 2).
4. **A document whose frontmatter has unknown keys** (a key of the user's own) must keep them byte-for-byte through `stamp` and `accept` — selftest `test_stamp_preserves_unknown_keys` (Task 2).
5. **An upstream present in the record but deleted from `<default-ref>`** reports `absent`, never `moved` and never a crash — selftest `test_upstream_absent` (Task 2).

---

### Task 1: The kind table and the item comparison

**Files:**
- Create: `plugins/workflows-core/scripts/lineage-kinds.json`
- Create: `plugins/workflows-core/scripts/lineage.py` (comparison core + `--selftest` harness)

**Interfaces:**
- Produces: `kind_of(path: str, text: str) -> str | None` (row name, by basename; ARD by `ard.md`/`ard-*.md`); `items(kind: str, text: str) -> dict[str, str]` (item key → normalised live content; a not-live item maps to the sentinel `"<withdrawn>"` and its nested items are omitted); `compare(kind, old_text, new_text) -> {"added": [...], "changed": [...], "withdrawn": [...]}` (sorted keys; all empty = not moved); `version_of(kind, text) -> str | None`.
- JSON row shape: `{"match": ["specification.md"], "covered": true, "reviser": "/product-workflows:update-spec <KEY>", "version": "header" | null, "items": [{"level": 1, "start": "<regex with one capture group = id>"} ...], "notes": ["<regex of a heading opening an excluded section>", ...], "ignore_lines": ["<regex>", ...]}`. A row with `"items": []` uses the no-ID rule (whole text outside notes, normalised, compared as one item `"<text>"`).

- [ ] **Step 1: Write the failing selftests** in `lineage.py`'s `selftest()` (inline fixture strings, `assert`):
  - `test_spec_items_keyed_by_path`: a spec with `### [U01]`, two `#### [AC01]`s under different stories → keys include `[U01]/[AC01]` and `[U02]/[AC01]`.
  - `test_notes_only_not_moved`: add `## Engineering review` section, tick a `- [ ]`, add an `Engineering proposal (/design): …` line → `compare` all empty.
  - `test_ac_text_change`: edit one EARS sentence → `changed == ["[U01]/[AC01]"]`.
  - `test_marker_reports_once`: append ` — Withdrawn 2026-11-03: gone` to `### [U02]` → `withdrawn == ["[U02]"]`, no `[U02]/...` keys anywhere.
  - `test_prd_items`: `### [US#2]:` heading and `- [AC#4] …` bullet under `**For [US#2] — …**` → keys `[US#2]`, `[AC#4]` (PRD ids are globally numbered, `prd-format.md:144-145`).
  - `test_no_id_kind`: a row with `"items": []` → any text change outside notes is `changed == ["<text>"]`; whitespace-only change → empty.
  - `test_version_of`: spec header `- **Version**: 3` → `"3"`; `prd.md` → `None`.
- [ ] **Step 2: Run** `python3 plugins/workflows-core/scripts/lineage.py --selftest` — Expected: FAIL (functions undefined).
- [ ] **Step 3: Write `lineage-kinds.json`** with one row per kind in the Global Constraints' two lists. Spec row: items `### \[(U\d+)\]`, `#### \[(AC\d+)\]`, `\*\*\[(TC\d+)\]` at levels 1–3; notes `^## Engineering review`, `^#{4,5} Open questions`; ignore_lines `^\s*- \[[ x]\]`, `Engineering proposal \(/design\):`; version from the header's `**Version**:` line. PRD, ARD, grounding, `decisions.md` rows: measure each id's defining form from its format reference (`prd-format.md`, `ard-format.md`, `workflows-core` `grounding-format.md`, `decision-register-format.md`) and write one level-1 pattern per id prefix. `epic.md` and `design.md`: measure from `agents/epic-writer.md` § write template and `dev-workflows/references/design-format.md`; where no item ids exist, `"items": []`. Record each measurement (file:line) in a `"_source"` field per row.
- [ ] **Step 4: Implement** `kind_of`, `items`, `compare`, `version_of`. Normalisation: drop frontmatter, drop notes sections and ignore_lines, collapse whitespace. Not-live = the item's own start line carries ` — Superseded by ` or ` — Withdrawn `.
- [ ] **Step 5: Run** the selftest — Expected: `selftest: N passed` and exit 0.
- [ ] **Step 6: Commit** `feat: lineage.py item comparison and kind table (D32)`.

### Task 2: Git subcommands, the walk, and the gate step

**Files:**
- Modify: `plugins/workflows-core/scripts/lineage.py`
- Modify: `.github/workflows/validate-catalog.yml` (a `Self-test the document lineage script` step after the `bounded.py` one, with a two-line comment naming its silent failure modes)
- Modify: `$S/gates-nonode.sh` (same step; scratch only)

**Interfaces:**
- Consumes: Task 1's functions.
- Produces (CLI; every subcommand prints JSON on stdout, exit 0 on success, 2 on usage error, 1 on any other failure with a one-line stderr reason):
  - `capture --specs DIR --ref REF [--from-ref PATH]... [--from-disk PATH]... --out FILE` → `[{path, blob, version}]`.
  - `stamp --specs DIR --ref REF --doc FILE --capture FILE` → writes `upstreams:` (replacing any earlier one) and carries forward each existing `accepted` entry whose blob equals that path's current blob at REF; prints `{"stamped": FILE, "carried": [...], "dropped": [...]}`.
  - `check --specs DIR --ref REF [--output FILE] DOC...` → walks from each DOC (relative path) up recorded `upstreams:` through covered kinds; returns `{"stale": [{downstream, upstream, recorded: {blob, version}, current: {blob, version}, added, changed, withdrawn, unavailable}], "missing": [{doc, blob}], "absent": [{downstream, upstream}], "accepted": [...], "highest": {downstream, reviser} | null}`; links accepted in `--output`'s `accepted:` (same path and current blob) go to `accepted`, not `stale`/`missing`. `highest` = the stale or missing link nearest the top of the walk.
  - `accept --doc FILE --check FILE` → appends `{path: upstream, blob: current}` for each stale link and `{path: doc, blob}` for each missing record, de-duplicated.
  - `--selftest`.

- [ ] **Step 1: Write the failing selftests** (each builds a throwaway repo under `tempfile.TemporaryDirectory()` with `git init -b main`, commits fixtures, runs the subcommands in-process):
  - `test_capture_ref_and_disk`: a committed `prd.md` and an uncommitted `code-grounding.md` → blobs equal `git rev-parse main:prd.md` and `git hash-object` of the disk bytes.
  - `test_walk_full_chain`: design → spec → prd; change a `[US#n]` in prd and commit → one stale link `spec ← prd`, `highest.downstream == spec`, reviser `/product-workflows:update-spec`.
  - `test_notes_commit_not_stale`: commit an `## Engineering review` into spec → design's check reports nothing stale.
  - `test_missing_record`: spec without `upstreams:` → `missing == [{doc: spec, …}]`; a `prd.md` without one → not listed.
  - `test_accept_suppresses_then_reasks`: accept into a design → re-check with `--output design` is clean; move prd again → stale again.
  - `test_blob_unavailable`, `test_stamp_preserves_unknown_keys`, `test_upstream_absent` (Review Focus 3–5).
  - `test_stamp_carry_forward`: an `accepted` entry still current is carried; a moved one is dropped.
- [ ] **Step 2: Run** the selftest — Expected: FAIL on the first new test.
- [ ] **Step 3: Implement** the subcommands. Frontmatter writes touch only the `upstreams:`/`accepted:` blocks (emit them as block YAML in the shape the spec shows; no YAML library — the family scripts use none); every other byte of the file is unchanged. Recorded copies via `git cat-file -p <blob>`, a non-zero exit → `unavailable: true`.
- [ ] **Step 4: Run** the selftest — Expected: all pass, exit 0.
- [ ] **Step 5: Add the CI step**, then run `python3 scripts/validate-catalog.py` — Expected: exit 0.
- [ ] **Step 6: Commit** `feat: lineage.py capture, stamp, check, accept (D32)`.

### Task 3: The shared reference and its docs

**Files:**
- Create: `plugins/workflows-core/references/document-lineage.md`
- Modify: `plugins/workflows-core/docs/reference/references.md` (new bullet; counts 38→39 files, 34→35 top-level, 36→37 named, re-derived with `find`)
- Modify: the `workflows-core` docs page that lists scripts, if one does (find it with `grep -rln "session-branch.py" plugins/workflows-core/docs`)
- Modify: `CLAUDE.md` § Shared authorities (one bullet: `workflows-core:document-lineage` — the lineage record, the moved rule, the kind table and `upstream-check` → `workflows-core.md`); `.claude/rules/workflows-core.md` (its full paragraph; keep under 20,000)

**Interfaces:**
- Produces: entry point `upstream-check`, invoked `Skill(skill: "workflows-core:reference", args: "document-lineage upstream-check")`, with caller inputs `docs` (paths the run reads, relative to `$SPECS_PATH`), `output` (the consumer's existing output document, or none), `command` (for the error token); returns the `check` JSON and the operator's answer (`stop` | `proceed`). Entry point `record`, invoked the same way with `args: "document-lineage record"`, covering `capture` at read time and `stamp` at write time. `<COMMAND>_LINEAGE_FAILED: <stderr line>` on a non-zero exit.

- [ ] **Step 1: Write the failing check**: `grep -c "document-lineage" CLAUDE.md` → Expected `0` now; `./scripts/check-docs.sh --root .` will fail once the reference exists without its docs bullet (run it after Step 2 to see it fail).
- [ ] **Step 2: Write the reference**: §1 the record (spec § The record, including ruling 1's blob rule); §2 the moved rule (spec § When an upstream counts as moved, items 1–5); §3 missing record and the coverage boundary; §4 the kind table — cite `scripts/lineage-kinds.json` as the authority and render it as the spec's table; §5 `record` entry point (call `capture` when the run reads its inputs, `stamp` after it writes each output, with `--from-disk` for an input read from the working tree); §6 `upstream-check` entry point: run `check`; nothing stale or missing → silent, one `Lineage: current` report line; otherwise print one block per stale link (`<upstream> <id> → <id>: changed …; new …; withdrawn …`, or `recorded copy unavailable`), one line per missing record, then the Global Constraints' question; *Stop* → the command stops with `<COMMAND>_UPSTREAM_STALE: …` naming the reviser; *Proceed* → remember the check file and, after each output is stamped, run `accept` on it (spec ruling 4); §7 the report line (`Lineage: current | <n> stale, accepted | stopped`). Script path as `specs-repo-git` gives `session-branch.py`'s.
- [ ] **Step 3: Docs and authorities bullets** as listed under Files.
- [ ] **Step 4: Run** `./scripts/check-docs.sh --root . > $S/g-t3.log 2>&1; echo EXIT=$?` (about 15 minutes, background) and `python3 scripts/validate-catalog.py` — Expected: `EXIT=0`, no size warning for `CLAUDE.md` or `workflows-core.md`.
- [ ] **Step 5: Commit** `feat: workflows-core:document-lineage reference (D32)`.

### Task 4: `/specify` records and checks

**Files:**
- Modify: `plugins/product-workflows/commands/specify.md` (:505-512 the `inputs_at` capture → `record` capture over the same inputs; Phase 5's frontmatter write → `stamp`; after the Epic's `require-on-main` (:384) → `upstream-check` from `epic.md`, `output` = the existing `specification.md` if any; Final report line :1240 `inputs_at` → `Lineage:`)
- Modify: `plugins/product-workflows/references/specification-format.md` (§ Frontmatter: `upstreams:`/`accepted:` replace `inputs_at`, which stays documented as a legacy field read by `/update-spec`)
- Modify: `plugins/product-workflows/agents/spec-reviewer.md:31` (validate `upstreams:` entries' shape; `inputs_at` only where present on a legacy file)
- Modify: `plugins/product-workflows/docs/commands/specify.md:93`

**Interfaces:**
- Consumes: Task 3's `record` and `upstream-check`.

- [ ] **Step 1: Failing check**: `grep -c "inputs_at" plugins/product-workflows/commands/specify.md` → record the count (expected non-zero) and `grep -c "document-lineage" …specify.md` → `0`.
- [ ] **Step 2: Edit** per Files. The input set recorded is exactly what :508-511 lists (PRD, ARDs, `epic.md`, grounding from disk, register); an `epic.md` `require-on-main` returned `absent` is captured `--from-disk`. Error tokens `SPECIFY_LINEAGE_FAILED`, `SPECIFY_UPSTREAM_STALE`.
- [ ] **Step 3: Run** `python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && ./scripts/check-id-grammar.sh --root .` — Expected: all exit 0; `grep -c "inputs_at" …commands/specify.md` → `0`.
- [ ] **Step 4: Commit** `feat: /specify records and checks lineage (D32)`.

### Task 5: `/epics` and `epic-writer`

**Files:**
- Modify: `plugins/product-workflows/commands/epics.md` (capture `prd.md` and the PRD-level `specification.md` where :441's gate passes; `upstream-check` from that `specification.md` after :441, `output` = the focus Epic's `epic.md` on a re-refine, else none; `stamp` each `epic.md` the run writes before the Phase 7.5 handoff; `accept` into each on *Proceed*; Final report `Lineage:` line)
- Modify: `plugins/product-workflows/agents/epic-writer.md` (refine mode keeps every frontmatter key it did not write — `upstreams:`, `accepted:` and unknown keys — as it keeps `kept_whole:`)
- Modify: `plugins/product-workflows/docs/commands/epics.md`

- [ ] **Step 1: Failing check**: `grep -c "document-lineage" plugins/product-workflows/commands/epics.md` → `0`.
- [ ] **Step 2: Edit** per Files; tokens `EPICS_LINEAGE_FAILED`, `EPICS_UPSTREAM_STALE`.
- [ ] **Step 3: Run** Task 4 Step 3's gate chain — Expected: exit 0.
- [ ] **Step 4: Commit** `feat: /epics records and checks lineage (D32)`.

### Task 6: `/design` and `design-format`

**Files:**
- Modify: `plugins/dev-workflows/commands/design.md` (capture at the inputs' reads: `specification.md`, `epic.md` where per-Epic, the ARDs it reads; `upstream-check` from `specification.md` right after step 3's gate (:103), `output` = the existing `design.md`; `stamp` `design.md` in Phase 7 (:510) **after** the `specification.md` amendment is written — the record names the spec's blob as read, and the amendment is notes, which the moved rule ignores; Final report `Lineage:` line)
- Modify: `plugins/dev-workflows/references/design-format.md` (frontmatter keeps `upstreams:`/`accepted:` and unknown keys across a rewrite)
- Modify: `plugins/dev-workflows/docs/commands/design.md`

- [ ] **Step 1: Failing check**: `grep -c "document-lineage" plugins/dev-workflows/commands/design.md` → `0`.
- [ ] **Step 2: Edit** per Files; tokens `DESIGN_LINEAGE_FAILED`, `DESIGN_UPSTREAM_STALE`.
- [ ] **Step 3: Run** Task 4 Step 3's gate chain — Expected: exit 0.
- [ ] **Step 4: Commit** `feat: /design records and checks lineage (D32)`.

### Task 7: `/update-spec` reads the record

**Files:**
- Modify: `plugins/product-workflows/commands/update-spec.md` (:57 baseline: the record first, `inputs_at` fallback, else null; :78 upstream diff `git diff <recorded blob> <default-ref>:<path>` per recorded upstream; the downstream report finds documents whose `upstreams:` lists this spec — `grep -l` over `upstreams:` blocks under the PRD folder — and keeps today's grep for unrecorded ones, naming them unrecorded; `upstream-check` over the base's covered upstreams only (`epic.md` on an Epic-level spec), never the base's own links; capture/stamp the revised spec; :106 and :151 stop writing `inputs_at`; :187 report)
- Modify: `plugins/product-workflows/docs/commands/update-spec.md` (:41, :63, :83, :93)

- [ ] **Step 1: Failing check**: `grep -c "document-lineage" plugins/product-workflows/commands/update-spec.md` → `0`.
- [ ] **Step 2: Edit** per Files; tokens `UPDATE_SPEC_LINEAGE_FAILED`, `UPDATE_SPEC_UPSTREAM_STALE`.
- [ ] **Step 3: Run** Task 4 Step 3's gate chain — Expected: exit 0; every remaining `inputs_at` in `update-spec.md` is in a fallback sentence (read each).
- [ ] **Step 4: Commit** `feat: /update-spec reads the lineage record (D32)`.

### Task 8: Release, sweep, gates

**Files:**
- Modify: `plugins/{workflows-core,product-workflows,dev-workflows}/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (minor bumps from `main`'s current versions), each plugin's `CHANGELOG.md` (dated 2026-11-03)
- Modify: `.claude/rules/plugin-updates-coupling.md` (new bullet: product-workflows and dev-workflows at these versions need workflows-core at this version — they cite `document-lineage`; move the oldest bullet(s) to `plugin-updates-coupling-history.md` so the file ends under 20,000, and update the boundary in all four places — find them with `$S/sweep.py +"1.58.0"`)
- Modify: `.claude/rules/product-workflows.md`, `.claude/rules/dev-workflows.md` (map lines; `dev-workflows.md` must end smaller than 20,173 or under 20,000)
- Modify: `docs/superpowers/to-fix.md` (D32: part 1 done in these versions; parts left: the three follow-ups)

- [ ] **Step 1: Claim sweep** (`.claude/rules/claim-sweep.md`): count before/after with `$S/sweep.py` for `inputs_at`, `cannot tell what moved upstream`, `null baseline`, and the subject "downstream report … grep"; disposition every hit's paragraph.
- [ ] **Step 2: Bumps, changelogs, coupling, rules, to-fix** per Files.
- [ ] **Step 3: Run the full gates** in the background: `bash $S/gates-nonode.sh > $S/g-d32.log 2>&1; echo "EXIT=$?" >> $S/g-d32.log` — Expected: `EXIT=0`; no size warning.
- [ ] **Step 4: Commit** `release: D32 part 1 — document lineage (workflows-core X, product-workflows Y, dev-workflows Z)`.

# `/brd-package` set-resolution scanner — Implementation Plan (to-fix D21, part 2 of 2)

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (native). Steps use checkbox (`- [ ]`) syntax.

**Goal:** `scripts/bundle-scan.py sets` runs `bundle-packaging.md` §7 (Phase 8 rule 9) over the assembled bundle and the delivery note, so no run writes its own set-resolution check again. This closes D21.

**Architecture:** a third subcommand of the scanner beside `tokens` and `citations` (product-workflows 3.61.0, part 1), sharing their table parser, their record reader (`_blocks`) and their JSON output. Like those two, it **finds and never rules**: every relation it runs is reported with both sides, and rule 9 turns each hit into its stop. Python standard library only, with `--selftest` held by CI.

**Spec:** `plugins/product-workflows/references/bundle-packaging.md` §7.1–§7.2 is the authority. The decisions below add **render forms** to Phase 6, Phase 7 and Phase 8 rule 6, so the restatements §7 compares can be found without parsing prose. They also add **one narrowing** to §7.1 (*members open an item*), with its measurement. Where a sentence below and §7 disagree, §7 wins and the plan is the defect.

## Global Constraints

- Standard library only. `--selftest` builds its fixtures at run time, and CI runs it (`.github/workflows/validate-catalog.yml`, the `bundle-scan.py` step).
- **Resolve, never parse:**
  - Every file is found by its exact bundled name, built from `--key` and `--date` (`<KEY>-customer-review-prompt-<YYYYMMDD>.md`, `<KEY>-decisions.md`, `<KEY>-code-defect-log.md`, `<KEY>-baselines.md`) or passed in (`--manifest`, `--note`).
  - Each filter is read off the records' own fields (§7.1, *Resolve the filter against the records' own fields*).
  - A `conditional_on` key is matched against `--unreviewed-prereq`, the set Phase 2 settled. It is never judged from prose.
- Every source is parsed by its owner's layout, through part 1's `_blocks` (`decision-register-format.md` §1.1: fields at block indentation; a block scalar's lines are its value).
- Exit codes are as for `tokens`: 0 means it ran (with hits or without); 2 means an input could not be read or a fixed render form is missing. Output is one compact JSON line.
- Membership, never a count (§7, *A count comparison is not the check*). Both sides empty passes. A filtered source that is empty while the restatement is not is `unreadable`, never `mismatch` (§7.1's last paragraph).
- Every narrowing §7.1 records is pinned by a fixture: id ranges, field-resolved filters, the extension either way, the manifest not listing itself, images out of scope, prefix pins, a date that is not a pin, and the same commit recorded twice. A reader who widens one back reintroduces a false positive somebody already paid for.

## Decisions the maintainer is asked to make before Task 1

1. **How relation 1 finds each enumeration in the rendered prompt.** A whole part is the wrong unit, and that is measured:
   - part 7 legitimately names a withdrawn record on a held `[C]` entry's `Re-puts:` line (Phase 6, *Only a held entry is rendered*);
   - part 9 carries the reviewer's own words, which may cite any id;
   - in one older register, 7 of 13 `[VD#n]` records name a sibling `[VD#n]` in their own text.

   So a whole-part comparison reports inventions against correct packages.

   *Recommendation:* Phase 6 renders each of relation 1's enumerations under a **fixed sub-heading** inside its part. Each record is an **item that opens with its id**: a list item, a table row's first cell, or a heading. The script takes as members only the ids that open an item, expanding a range in that position. An id inside an item's text is a mention, not a member. A sub-heading that is missing stops the run (exit 2). The six sub-headings are listed in Task 2.

   *Alternative:* compare every unqualified id of the prefix anywhere in the part, which the measurements above show fires.

2. **How relation 2 reads the manifest's document list.**
   *Recommendation:* rule 6 pins the list as the table under `## Documents`, one row per document, its first cell the bundled filename in backticks. The real manifest already takes this form. The script compares that column, extension tolerated, with the working directory's `.md` files minus the manifest.
   *Alternative:* every backticked key-prefixed name anywhere in the manifest. That fires on the names it gives as context not carried (Phase 8 rule 5).
3. **How relation 3 pairs a repository with its commit.**
   *Recommendation:* Phase 7 pins the note's pin wording, one clause per repository: ``the `<repo>` repository at commit `<commit>` ``. The real note already uses it, wrapped across a line. The script pairs each repository with its own baseline commits, so it catches a swapped pair and a repository the baselines lack.
   *Alternative:* membership only — every baseline repository named, every commit word a prefix of some baseline commit. That is blind to a swap and to an extra repository, both of which would be recorded in §7.2.
4. **Part 8 and a conditional `[AS#n]`.** Phase 6 names part 8's positions "by its `[VD#n]`". `decision-register-format.md` §7 lets an `[AS#n]` carry `conditional_on`, and every measured part 8 that had one listed it.
   *Recommendation:* relation 1 follows the command as written, comparing `[VD#n]` only. Widening part 8 is a content change outside D21, recorded as a new to-fix item. An open `[AS#n]` is already in parts 7 and 9 either way.
   *Alternative:* widen part 8 to every live record carrying `conditional_on`, with the relation following it.

**Calls made in this plan, for the maintainer to check:**
- A conditional position counts only while its `status` is `open`, `decided` or `reopened`. A superseded or withdrawn record is no longer a position the package takes.
- A range is two ids of one prefix joined by `–` or `-`, with optional backticks and spaces. Only those two forms are measured.
- A part heading is `## <N>` followed by `.`, `·` or `:`. The script requires parts 1 to 11, each exactly once and in order.
- An abbreviation that prefixes two different commits is reported under `ambiguous` and stops with a new `BRD_PACKAGE_SET_AMBIGUOUS`. It is not folded into `MISMATCH`, whose wording ("not in the source") would be false of it.

## Review Focus

1. **A record's own text names a sibling id of the same prefix** (measured, 7 of 13). It is a mention, never a member. Pinned in Task 2.
2. **A held `[C]` entry's `Re-puts:` names a withdrawn `[AS#n]` in part 7**, outside the *Open assumptions* sub-heading. No hit. Pinned in Task 2.
3. **A `status:` line inside an `argumentation: |` scalar** is not the record's status. Pinned in Task 2.
4. **A pin clause wrapped across a line break**, as the real note's is. The clause is matched on whitespace-collapsed text. Pinned in Task 4.
5. **The note's `bundle-20261012/` path and a bare `20261012` date are no pin.** A 7-digit all-digit abbreviation that prefixes a baseline commit is one. Pinned in Task 4.

---

### Task 1: the subcommand, its inputs and the prompt's parts

**Files:** Modify `plugins/product-workflows/scripts/bundle-scan.py`.

**Interface:** `bundle-scan.py sets <bundle-dir> --key KEY --date YYYYMMDD --manifest NAME --note PATH [--unreviewed-prereq KEY]…`
- It produces `sets(bundle, key, date, manifest, note, unreviewed=()) -> dict` and `prompt_parts(text) -> {int: (start_line, end_line)}`.
- The output is `{"relations": [...], "mismatch": [...], "unreadable": [...], "ambiguous": [...]}`.
- Each relation entry carries `relation` (1–3), `where` (the part and sub-heading, `manifest`, or `delivery note`), `source`, `filter`, `named`, `held`, `missing` and `extra`. Those are the fields `BRD_PACKAGE_SET_MISMATCH` and `BRD_PACKAGE_SET_UNREADABLE` print.

- [ ] Tests (selftest):
  - `## 1. Setup` … `## 11. …` locate eleven parts, and so do `## 1 · Setup` headings.
  - A prompt missing `## 8` or repeating `## 7` raises `Refused`.
  - A schema heading `### 10.3` stays inside part 10.
  - An absent `<KEY>-customer-review-prompt-<DATE>.md` raises `Refused` naming it.
- [ ] Implement, then commit.

### Task 2: relation 1 — enumerations against their filtered records

**Interface:** `members(lines, prefix) -> [id]` (item openers, ranges expanded) and `regions(lines, parts) -> {title: (part, start, end)}`.

The six regions and their filters, each read from this key's own partition:

| Part | Sub-heading (exact title, optional number before it) | Prefix | Source | Filter (record fields) |
|---|---|---|---|---|
| 6 | `Code defects we will repair` | `CDF` | `<KEY>-code-defect-log.md` | `disposition: in-scope` |
| 7 | `Open assumptions` | `AS` | `<KEY>-decisions.md` | `status: open` |
| 8 | `Positions that could still move` | `VD` | `<KEY>-decisions.md` | `conditional_on: <K>/<id>` with `<K>` in `--unreviewed-prereq`, and `status` open, decided or reopened |
| 8 | `Code defects whose scope is unsettled` | `CDF` | `<KEY>-code-defect-log.md` | `disposition: conditional` |
| 9 | `Open assumptions` | `AS` | `<KEY>-decisions.md` | `status: open` |
| 11 | `Code defects we will not repair` | `CDF` | `<KEY>-code-defect-log.md` | `disposition: out-of-scope` |

- A region runs from its sub-heading to the next heading of the same or a higher level, or to the end of the part.
- An item is a line opening with `-`, `*`, `+`, `<n>.`, `|` or `#`. Its opener is the first id on that line with only markup before it (`*`, `_`, `` ` ``, spaces, the list marker).
- An absent source file is an empty corpus (§6.1's rule for `code-defect-log.md`).

- [ ] Tests:
  - Matching sets pass, and so do both sides empty (a `None: …` body).
  - An omission and an invention each give `mismatch`, with the ids in `missing` and `extra`.
  - `- **[AS#1]**–**[AS#4]**: …` names four (range).
  - Inside `- [VD#7] — … as [VD#11] decided`, `[VD#11]` is a mention (Review Focus 1).
  - A `- **Re-puts:** [AS#3]` line under `### 7.1` is no hit (Review Focus 2).
  - An indented `  status: open` inside `argumentation: |` on a `decided` record leaves it out of the open set (Review Focus 3).
  - A `[VD#n]` `conditional_on` a reviewed prerequisite is not in part 8's set; a superseded conditional one is not either.
  - A region naming `[CDF#2]` over an absent log is `unreadable`.
  - A missing `Open assumptions` sub-heading in part 9 raises `Refused`.
- [ ] Implement, then commit.

### Task 3: relation 2 — the manifest against the bundle's listing

- **A review document is every `.md` file but the manifest.** Rule 9 runs over the working directory this run assembled, so §7.1's never-sent marker cannot be in it.
- Members are the first cells of the table under `## Documents` (Decision 2), with `.md` stripped. An entry with an image extension (`png`, `jpg`, `jpeg`, `gif`, `svg`, `webp`) is skipped. The other side is every `.md` file in the bundle directory except `--manifest`, with `.md` stripped.

- [ ] Tests:
  - The real manifest's shape passes.
  - `` `K-1-decisions` `` and `` `K-1-decisions.md` `` both match `K-1-decisions.md`.
  - The manifest's absence from its own table is no hit.
  - An `.svg` row is no hit.
  - A bundle file with no row is `missing`; a row with no file is `extra`.
  - A manifest with no `## Documents` table raises `Refused`.
- [ ] Implement, then commit.

### Task 4: relation 3 — the delivery note's pins against the baselines

- Baselines are read as (`repo`, `commit`) pairs from `<KEY>-baselines.md`'s entries.
- The note is read on whitespace-collapsed text for ``the `<repo>` repository at commit `<commit>` `` clauses (Decision 3).
- A commit word, anywhere in the note, is a 7–40-hex run standing as a word. It is not one inside a filename or path. It is not one that reads as a valid `YYYYMMDD` date while prefixing no baseline commit.

- [ ] Tests:
  - The real note's wrapped clause passes (Review Focus 4).
  - An abbreviation passes where it prefixes the repository's commit, including a commit recorded under two dated runs.
  - It is `ambiguous` where it prefixes two different commits.
  - A swapped pair is a `mismatch`, and so is a repository named in the note that the baselines lack, or the reverse.
  - `bundle-20261012/` and `20261012` are no pin; `1234567` that prefixes a baseline commit is one (Review Focus 5).
  - A note naming a commit over an absent baselines file is `unreadable`.
- [ ] Implement, then commit.

### Task 5: wire it into `/brd-package`, the reference, the docs and the release

**Files:**
- `commands/brd-package.md`:
  - Phase 6: Decision 1's six sub-headings and the item form, beside the parts that render them; part 9's open assumptions move under their sub-heading.
  - Phase 7: Decision 3's pin clause.
  - Phase 8 rule 6: Decision 2's table.
  - Rule 9: run `bundle-scan.py sets` with its arguments, each from what the run holds. Read `mismatch`, `unreadable` and `ambiguous` as the three stops, and add `BRD_PACKAGE_SET_AMBIGUOUS` to the list of stops that remove the working directory. Any non-zero exit stops the run, naming stderr.
  - The Final report counts the relations run.
- `references/bundle-packaging.md`:
  - §7.1: *members open an item*, with its measurement; the regions found by Phase 6's sub-headings; the pin clause.
  - §7.2: what stays blind, including an id named only in an item's prose.
- Also: `docs/commands/brd-package.md`, the CI step's comment, and `.claude/rules/brd-route.md`'s map line.
- Release: `CHANGELOG.md` (minor bump, 3.62.0), `plugin.json` and `marketplace.json`.
- `docs/superpowers/to-fix.md`: D21 closed, and Decision 4's item added where it was taken.

- [ ] Run the scanner over the real `PRD-BOOK-2-01` bundle and its note:
  - Unedited, it refuses (exit 2), because that prompt predates Decision 1's sub-headings. That is the designed behaviour, and the run records it.
  - On a copy whose prompt gains only the five missing sub-headings (each with its `None` body), expect relation 1 with every set empty, relation 2 at 11 documents, relation 3 at one repository, and nothing reported.
  - Then mutate that copy (drop a manifest row, change one pin character) and expect both reported.
- [ ] Claim sweep (`.claude/rules/claim-sweep.md`): sweep the phrases that say rule 9 runs without a script, by phrase, across refinement 4's scope.
- [ ] Full gate chain → `EXIT=0`; independent Opus review until clean; PR.

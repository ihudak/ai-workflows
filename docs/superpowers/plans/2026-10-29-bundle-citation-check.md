# `/brd-package` citation-resolution scanner — Implementation Plan (to-fix D21, part 1 of 2)

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (native). Steps use checkbox (`- [ ]`) syntax.

**Goal:** `scripts/bundle-scan.py citations` runs `bundle-packaging.md` §6 — Phase 8 rule 8 — over an assembled bundle, so no run writes its own citation check again. Part 2 (a later plan) scripts §7's set resolution, rule 9.

**Architecture:** a second subcommand of the scanner `/brd-package` already ships (`tokens`, product-workflows 3.54.0), sharing its table parser, its span placement and its JSON output. It **finds and never rules**, as `tokens` does: every hit is reported with the span its position places it in, and the run still rules on customer content (§6.3) the way it rules on `tokens`' hits. Python standard library only, `--selftest` held by CI.

**Spec:** `plugins/product-workflows/references/bundle-packaging.md` §6.1–§6.4 is the authority; this plan adds no rule, it implements that section. Where a sentence below and §6 disagree, §6 wins and the plan is the defect.

## Global Constraints

- Standard library only; `--selftest` builds its fixtures at run time; CI runs it (`.github/workflows/validate-catalog.yml`, beside `tokens`' step).
- Never resolve a key by parsing a filename: the partition keys come in as arguments, resolved by the run from the key set it holds (§6.1, `CLAUDE.md` § Editing discipline *Resolve an identifier against a known set*).
- Every corpus is **parsed by its owner's layout**, never by a fixed column or a fixed run of spaces (§6.1, `workflows-core:grounding-format` §2.1): table files split by `brd-format.md` §2.3's delimiting-`|` rule (the `tokens` parser), record files by `id:` keys tolerant of padding.
- Exit codes as `tokens`: 0 ran (with hits or without), 2 an input could not be read. Output one compact JSON line.
- Prose is executed: `brd-package.md` Phase 8 rule 8 and the docs page change only to say *run the scanner and read its output by these fields*; the rule text of §6 stays where it is.

## Decisions the maintainer is asked to make before Task 1

1. **The structured-field discharges (§6.2's table) — where the script gets them.** §6.2 says the fields are "derived from the authorities that own them, never maintained as a list here", yet a script needs to know them. *Recommendation:* the script carries one entry per field, and its selftest **reads §6.2's table and fails where the table names a field the script does not know** — so a field an authority adds stops CI until the script learns it, and never passes silently.
2. **§1.1's working filenames (relation 3's shape 2) — where the script gets them.** §6.2 says they are "derived from §1.1's own table each time this relation runs, never copied into a second list". *Recommendation:* the script **parses §1.1's table at run time** from `${PLUGIN_ROOT}/references/bundle-packaging.md` — every backticked working `.md` path the section names, in its table and its prose (the exclusions sit in its prose), `references/` and `commands/` paths aside, placeholders resolved as relation 3 says — and stops (exit 2) where the table cannot be read, rather than falling back to a copy.

## Review Focus

1. **A corpus file with padded or unusual `id:` spacing** — the 140-false-absences case §6.1 cites; pinned in Task 2.
2. **A prerequisite package copied in under flattened names** — §6.1's vacuity guard must fire, not pass; pinned in Task 3.
3. **`[SR#n]`, placeholders and qualified cross-package references** — none may be reported dead; pinned in Task 4.
4. **A `docs/api.md:12` in grounding evidence, and a customer's own `notes.md` link** — relation 3 must stay off both; pinned in Task 6.
5. **A class-4 `[DG#n]` whose claim names two requirements** — reported as ambiguous, never resolved by a guess; pinned in Task 5.

---

### Task 1: the subcommand, its inputs and the partitions (§6.1)

**Files:** Modify `plugins/product-workflows/scripts/bundle-scan.py`.

**Interface:** `bundle-scan.py citations <bundle-dir> --key <THIS-KEY> [--prereq-key <KEY>]… [--copied-key <KEY>]… [--date <YYYYMMDD>] [--captured <bundled name>]… [--captured-path <path>]… [--source-basename <name>]…`
- `--key` this run's key; `--prereq-key` every prerequisite Phase 2 carried; `--copied-key` those whose package rule 5 copied in (the vacuity guard's set, §6.1 *The guard reads Phase 2's own carry*); `--date` the run's `<YYYYMMDD>`; `--source-basename` each captured markdown file's basename (relation 3's placeholders).
- Output `{"partitions": {...}, "dead": [...], "mismatch": [...], "ambiguous": [...], "unreadable": [...], "customer": [...], "discharged": N}`.

- [ ] Test (selftest): a bundle of `K-1-*.md` and `P-2-*.md` partitions by `--key K-1 --prereq-key P-2`; a document named by no key is reported dead as unkeyed; `--copied-key P-2` with no `P-2-` document is dead (vacuity guard); `--prereq-key P-3` without `--copied-key` is no hit.
- [ ] Implement partitioning by **resolving** each filename's leading `<KEY>-` against the given key set, the longest matching key winning at a segment boundary.
- [ ] Commit.

### Task 2: the corpus parsers (§6.1's table)

**Interface:** `corpus(partition) -> {class: set(ids)}` and `unreadable(partition) -> [(file, class)]`.
- `[BR#n]` from `<KEY>-brd-inventory.md`'s `id` column; `[DEF#n]` from `<KEY>-brd-defect-log.md`'s `id` column; `[CG#n]`/`[DG#n]` from `<KEY>-code-grounding.md` / `<KEY>-design-grounding.md` blocks' `id:`; `[VD#n]`/`[CD#n]`/`[AS#n]` from `<KEY>-decisions.md` records' `id:`; `[CDF#n]` from `<KEY>-code-defect-log.md` (absent file = empty corpus).
- **Record-shaped content** = a table row of the owner's header shape, or a line opening a record with an `id:` key; such content parsing to zero ids of its class → `unreadable` (`BRD_PACKAGE_CORPUS_UNREADABLE`); none at all → empty corpus, no hit.

- [ ] Tests: padded `- id:       [CG#1]` and unpadded `- id: [CG#12]` both parse; a header-only `decisions.md` is empty, not unreadable; a `code-grounding.md` with blocks whose `id:` lines are all malformed is unreadable; an absent `code-defect-log.md` is empty.
- [ ] Implement; commit.

### Task 3: relation 1 — identifier references (§6.2)

- Every `[PREFIX#n]` (a number, not the placeholder `n`) in a document resolves in its own partition's corpus for its class, unless carried in the qualified prose form `<KEY> [X#n]` with another BRD's key (discharged) — its own key is resolved like an unqualified id.
- The structured fields (Decision 1) are read, not refused: a value carrying another BRD's key is discharged, its own key resolved, a bare `prerequisite` reported (never resolved), a bare `resolved-by:` reported as §6.2 says.
- `[SR#n]` is exempt entirely (§6.3).
- A hit inside a span `tokens` places as customer content (`captured-file`, `inventory-text`/`ledger-text` on a prose row, `anchor`, `locator`, `locator-tail`) goes to `customer`, for the operator's ruling; every other is `dead`.

- [ ] Tests: `[CG#7]` resolves in `K-1` and is dead in `P-2` where only `K-1` holds it; `P-2 [CG#7]` in a `K-1` document is discharged; `K-1 [CG#99]` is dead; `[SR#3]` and `[BR#n]` are no hit; `conditional_on: P-2/[CD#2]` discharged, `resolved-by: K-1/[CD#9]` dead where `K-1` holds no `[CD#9]`; a `[BR#4]` in a customer's captured file goes to `customer`.
- [ ] The Decision-1 selftest: the script's field set equals §6.2's table's.
- [ ] Implement; commit.

### Task 4: relation 2 — class-4 design findings (§6.2)

- For every `[DG#n]` with `class: 4`, its `cites` resolves in the same partition, and the cited `[CG#n]`'s `claim` **names** the same requirement id the citing claim names (anywhere in the claim, not only first). A claim naming two or more requirement ids → `ambiguous`, never a pick.

- [ ] Tests: a matching pair passes; a mismatch reports both claims; a dead `cites` is `dead`; a two-id claim is `ambiguous`.
- [ ] Implement; commit.

### Task 5: relation 3 — bare filenames (§6.2)

- A bare `<name>.md` token with no `/` is tested only where it carries a key-prefix the key set resolves, or matches a §1.1 working filename (Decision 2), placeholders resolved by `--date` and `--source-basename`; it must name a file in the bundle.
- Off the relation: a `<file>:<line>` in a grounding finding's `evidence`; a manifest map line's quoted target; a captured file's own links (§6.3 rule 3); customer spans.

- [ ] Tests: `K-1-decisions.md` present passes, absent is dead; `self-review-20261029.md` (excluded by §1.1) is dead; `docs/api.md:12` and `README.md:12` in evidence are no hit; a manifest line quoting `notes.md` is no hit.
- [ ] Implement; commit.

### Task 6: wire it into `/brd-package`, docs, release

**Files:** `commands/brd-package.md` Phase 8 rule 8 (run `bundle-scan.py citations` with the arguments Task 1 names; read `dead`, `mismatch`, `ambiguous`, `unreadable` as the three stops and `customer` as §6.3's ruling; any non-zero exit stops the run); `docs/commands/brd-package.md`; the CI step's comment; `CHANGELOG.md` (minor bump), `plugin.json` + `marketplace.json`; `docs/superpowers/to-fix.md` D21 narrowed to part 2 (§7).

- [ ] Run the scanner over the real `PRD-BOOK-2-01` bundle and record what it reports beside what that run's hand-written check reported.
- [ ] Full gate chain → `EXIT=0`; independent Opus review until clean; PR.

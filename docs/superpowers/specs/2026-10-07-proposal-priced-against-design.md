# Proposal currency by content — design

**Status:** approved 2026-10-07. **Plugin:** `product-workflows` (this repository only — no sibling edition carries the proposal commands).

## Problem

Whether a slice's `proposal.md` is current is decided today (3.26.1) by **time**: the proposal's last commit time — or its modification time where it is uncommitted — against those of the slice's `prd.md`, `decisions.md` and `grounding/`. Time is a proxy, and it fails in three ways:

1. **It records no version.** An input edited locally is newer only than its own last commit, so a proposal committed later by someone else reads as current against it; a squash merge, a rebase or the preflight's flush can carry a proposal and the change it never priced in one commit, which 3.26.1 can only report as *undecidable* and hand to the operator.
2. **It watches three inputs of the many the pricing reads.** `/prd-proposal` also reads `ard.md` and `specification.md` (they set the readiness tier), `interview/round-<N>.md` (whether the register is settled, and the open customer questions), `code-defect-log.md` and `self-review-<YYYYMMDD>.md` (the defect package), each `EPIC-*/epic.md` (they seed the middle work packages) and the shared proposal profile (productivity, team, calendar). A proposal priced at tier 2 still reads as current after `ard.md` lands, and `/brd-proposal` rolls the stale tier into the umbrella, whose tier is the minimum of its slices'.
3. **A shallow clone or a tie decides nothing**, and the walk falls back to asking.

## Decision

`/prd-proposal` records **which version of each input it priced** — the git blob id of each file's content — in the proposal itself, and `/brd-proposal` does the same for the umbrella (§5a). Currency compares those ids with the inputs on disk. The 3.26.1 time rule stays, unchanged, for a slice proposal written before this release.

## 1. The input set

Defined **once**, in a new `references/proposal-format.md` §15, and enumerated from there by the writer and by both readers. Paths are relative to the slice folder unless marked:

| Input | Why the pricing reads it |
|---|---|
| `prd.md` — or, where none exists, the `<KEY>_<slug>.md` PRD addressing's legacy fallback accepts | the requirement set the packages cluster |
| `decisions.md` | tier 2's settled-register half; frozen decisions are driver evidence |
| `ard.md` | tier 3 |
| `specification.md` | tier 4; the authored test-case count sizes QA |
| `code-defect-log.md` | defect source 1 |
| every `.md` file under `grounding/`, recursively, no name (file or directory) beginning with `.` — a symlink counts as what it points at (amended 3.27.1: a skipped symlink left an edit through it unseen, and an editor's backup file read as an input) | tier 2's verified-grounding half; driver evidence; defect source 2 |
| every `interview/round-<N>.md`, and `interview/customer-questions.md` | the register's settledness; the open-items sweep's unanswered customer questions |
| every `self-review-<YYYYMMDD>.md` | defect source 3 |
| `epic.md` in every immediate `EPIC-*` subfolder | seeds the middle work packages |
| `$SPECS_PATH/.dev-workflows/proposal-profile.yml` | productivity basis, roles, calendar, engagement model |
| the `--baseline` file, where one was given | section 22's reconciliation (amended 3.27.1; its line flagged `baseline` — folder-relative inside the folder, `$SPECS_PATH/` elsewhere under the root, `<outside>` beyond it; compared where held, else listed `unverifiable`) |

**Not inputs:** `proposal.md` and `proposal-brief.md` (the output, and the stability anchor a re-run reads), `revisions/`, `brd-link.md` and `coverage-ledger.md` (read only to word a refusal).

**An absent input has no line.** Its later appearance is therefore an *added* input — `ard.md` landing after pricing makes the proposal stale, which is the point.

## 1a. The script

**The record is computed, written and compared by one bundled script**, `plugins/product-workflows/scripts/proposal-record.py` — Python standard library only, the pattern `promotion-signals.py` and `architecture-harvest.py` already set in this plugin, with a `--selftest` run in CI. Enumeration, hashing, sorting, parsing and comparison are the parts an agent re-deriving them from prose gets subtly wrong (a glob, a sort order, a 40-character id transcribed), so the commands run the script and never compute an id themselves:

```
proposal-record.py record --specs <SPECS_PATH> --folder <folder> [--baseline <file>] [--brd-key <KEY> [--excluded <slice-dir>,…]]
proposal-record.py stamp  --proposal <proposal.md> --record <file> [--excluded <slice-dir>,…]
proposal-record.py check  --specs <SPECS_PATH> --proposal <proposal.md> [--brd-key <KEY>]
proposal-record.py --selftest
```

`record` prints the record block for the inputs on disk now (a slice's, or with `--brd-key` an umbrella's); the command saves it to a temp file (`command mktemp`, never inside a repository). `stamp` writes that block as the last thing in `proposal.md`, replacing any record already there and removing any other record block — a damaged one's stray opening line included, since an unclosed comment hides everything after it — preserving every other byte, and reports whether it changed anything; on an umbrella, `--excluded` sets which slices the record marks excluded. `check` parses the record a `proposal.md` ends with and compares it with the inputs on disk, printing JSON — `basis: content` with `current` and the `changed`, `added` and `removed` paths, or `basis: none` with `reason: no-record` or `reason: unreadable` and what failed; an umbrella's adds the `included` and `excluded` slices, `stale_slices` (an included slice whose own record reads stale, which also makes `current` false) and `unrecorded_slices`. Exit 0 whenever it ran; 2 when it could not (a missing folder, git absent, a bad argument, any file-system or encoding failure), with the cause on stderr — and callers treat any non-zero exit as could-not-run.

## 2. The record

The last thing in `proposal.md` is one HTML comment:

```
<!-- priced-against
$SPECS_PATH/.dev-workflows/proposal-profile.yml 77b2…
decisions.md 5c1e…
grounding/code-grounding.md 0a7d…
prd.md 9f3c…
-->
```

- **One line per input present when pricing began**: the path as §1 writes it, one space, and the id `git -C "$SPECS_PATH" hash-object -- <path relative to $SPECS_PATH>` prints in full — 40 lowercase hex characters, or 64 in a repository using SHA-256 objects. Lines are sorted by path in byte order (`LC_ALL=C`), so two runs over the same inputs write the same record.
- **`hash-object` is the right tool, not a checksum**: it works whether or not `$SPECS_PATH` is a git repository, the path is never written to the object store, and inside a repository it applies the clean filters git would apply on commit — so a CRLF checkout on one machine and an LF checkout on another hash to the same id.
- **Paths are folder-relative** so a slice folder moved with `git mv` keeps its record valid; the profile, which lives outside every folder, is written with its literal `$SPECS_PATH/` prefix.
- **An HTML comment** because `proposal.md` is a document a vendor sends a customer: the record is invisible wherever the markdown renders, travels with the proposal through archiving (`revisions/` keeps each revision's record), is committed with it, and passes `/brd-proposal`'s `require-on-main` gate with it. A sidecar file was rejected: a third artifact to archive, hand off and gate, which can be committed without the proposal it describes.
- **The record is machine data, not a section.** It is not one of §4's twenty-three, carries no prose, and is not reviewed for content.

## 3. When the ids are taken

**Once, at the end of Phase 2** — after the profile is settled (it may be written there) and before Phase 3 reads the folder to grade it: `record` into a temp file. **Phase 7 stamps that file's block** into the `proposal.md` it writes and then runs `check` on it: where any input moved during the run, the record still holds the **Phase 2** ids — the versions pricing began from — so the proposal reads as stale at once and a re-run is recommended, and the final report names each input `check` lists. A record of the Phase 7 ids would claim the run priced content it may only partly have seen.

## 4. The check — `/brd-proposal` Phases 2 and 3

Per slice holding a `proposal.md`, Phase 2 records one of four bases:

- **`content`** — the proposal ends with a well-formed record: enumerate §1's input set now, take each present input's id, and compare with the record. An input whose id differs is *changed*, one present now and not in the record *added*, one in the record and absent now *removed*. Any of the three → **stale**; none → **current**. The working-tree content counts, committed or not: a re-run prices what is on disk.
- **`commit`**, **`file`**, **`undecidable`** — the proposal carries **no record** (it predates this release): 3.26.1's time rule, unchanged, over its original three inputs.
- **A record that does not parse** — not the last thing in the file (only whitespace may follow it), a line that is not `<path> <id>` (or, in an umbrella record, `<slice>/brd-link.md <id> excluded` — §5a), an id that is not 40 or 64 lowercase hex characters, a duplicate path — is treated as no record: the time rule decides, and the walk's picture says the record is unreadable.

Phase 3's five rows keep their recommendations; only the third row's test and the picture change:

| Slice state | Recommendation |
|---|---|
| … the two no-`proposal.md` rows, unchanged … | |
| `proposal.md` present and **stale** — on basis `content`, an input changed, added or removed; with no record, older than `prd.md`, `decisions.md` or `grounding/` | **Re-run it.** |
| `proposal.md` present, no record, and its time cannot be ordered (basis `undecidable`) | unchanged — reachable only on the time fallback now |
| `proposal.md` present and current | **Include.** |

The picture names the basis per slice as today, and on basis `content` names each input that differs (`ard.md added`, `prd.md changed`, `grounding/code-grounding.md removed`). On a time basis it adds that the proposal carries no record and that re-pricing it once moves the slice to the content basis.

## 5. `/prd-proposal`'s next-step offer

Its sibling option asks the same question of each sibling — *does it hold a current proposal?* — and now answers it with §4's test, so the offer and the walk never disagree: basis `content` where the sibling's proposal carries a record, the time rule where it does not, `undecidable` still counting as *not current* there.

**That reads a sibling's record, and nothing else of its proposal** — no figure, no section. The census every surface states (the one command reading another folder's proposal *as a proposal* is `/brd-proposal`; every other targeted read is an own-folder one; `/brd-reconcile` reads one only as prose) gains one clause beside the `/brd-reconcile` one: **one read is of the record alone** — `/prd-proposal`'s next-step offer reads a sibling's `priced-against` record to decide whether to offer pricing it, and nothing else of it. Every surface that states the census carries the clause, and `/prd-proposal`'s sentence *"It never opens a sibling's proposal"* is replaced.

## 5a. The umbrella's record, and the check that tells you it needs a re-run

**The umbrella `proposal.md` carries a record too**, in §2's form, over its own input set — also defined in proposal-format §15, paths relative to the BRD folder:

| Input | Why |
|---|---|
| `<slice>/brd-link.md` for every slice Phase 2 enumerates | a slice carved or removed since |
| `<slice>/proposal.md` for every slice holding one, included or excluded | a slice re-priced since, or one excluded then and priced since |
| `coverage-ledger.md` (the root ledger) | the coverage statement |
| the container's own `code-defect-log.md`, `grounding/` files and `self-review-*.md` | the defect sweep `/brd-proposal` Phase 6 runs at container level |
| an excluded slice holding no `proposal.md`: its own §1 input set, under `<slice>/` | an excluded slice becoming estimable — nothing else in the record would show it |
| `$SPECS_PATH/.dev-workflows/proposal-profile.yml` | team shape and calendar: peak concurrency and the schedule |

**Which slices the umbrella included is part of the record**: an excluded slice's `brd-link.md` line carries a third field, `excluded` — `PRD-1234-03/brd-link.md <id> excluded`. That word is the only third field the grammar admits, and only on a `brd-link.md` line of an umbrella record; a slice record never carries one.

**The umbrella is stale** when its record differs from disk (§4's *changed*, *added*, *removed*, over this input set), **or** when any slice it included is not current by that slice's own test (§4 — stale, or `undecidable` on the time fallback). The second clause carries staleness upward: a slice whose `ard.md` landed needs re-pricing, and so does the umbrella above it — which is why no slice's `prd.md` is in the umbrella's set.

**Where you learn it: `/brd-proposal <BRD-KEY>`, at the end of Phase 2** — after the slices are enumerated and their bases recorded, and before the walk, the profile, the gate or any pricing. Where an umbrella `proposal.md` is on disk, the run prints whether it is current and, where it is not, every reason (`PRD-1234-02/proposal.md changed`, `PRD-1234-05 added`, `PRD-1234-03 excluded then, priced since`, `PRD-1234-04 stale: ard.md added`, `proposal-profile.yml changed`). Then:

- **Current** → it asks, with the recommendation printed beside the array:
  `choices: ["Stop — the umbrella is current (Recommended)", "Re-price it anyway"]`.
  **Stop** ends the run there: no artifact written, no stop id (an operator's finished decision), the Phase 13 emitter tail run on the way out, and the final report saying the umbrella is current against its record. **Re-price it anyway** continues into the walk. `--redo` and `--profile` skip the question — each already asks for a re-price — and the run continues.
- **Stale, or carrying no record** (an umbrella written before this release, or one whose record does not parse) → the reasons are printed, or *"no record — re-price once to enable this check"*, and the run continues into the walk with no question.

**A slice Phase 6 step 1 excludes later** (its figures could not be read) is marked by Phase 8's `stamp --excluded`, which sets the marks without re-taking any id. **The umbrella's ids are taken once, at the end of Phase 5** — after the walk has settled which slices are excluded and the profile is settled, and before Phase 6 reads the slices' figures to roll them up, so the record names the versions the roll-up actually read; Phase 8 stamps the block and runs `check`, and where any input moved mid-run the record keeps the Phase 5 id and the final report names it.

**After pricing a slice**, `/prd-proposal`'s closing offer already carries *"Roll it into the programme umbrella"*; it is left as it is, and reads no umbrella record — which would add a read the census does not need.

## 6. Checks on the record

- **`/prd-proposal` Phase 9's and `/brd-proposal` Phase 10's pre-lint** check the record by re-running `stamp` with the run's own temp file: a record that is present and byte-identical to the block the run recorded is left alone, and anything else — missing, altered, no longer last — is a finding, inline-fixed by that same `stamp` from the ids the run took, never from a fresh hash. **The triage's inline edits re-stamp too**: after the last edit to `proposal.md`, `stamp` runs once more, so no edit can carry a damaged record into the handoff.
- **`proposal-reviewer`** is told the trailing comment is machine data: it is not a section, is not counted against §4's set, and is not a finding.

## 7. Out of scope

- **`/update-prd`** keeps reporting downstream artifacts by date (3.26.1): it lists what an update *may* invalidate, which is not a currency test.
- **No migration.** A slice proposal without a record keeps the time rule until it is next re-priced; an umbrella without one gets no early check until it is.

## 8. Verification

`proposal-record.py --selftest` builds scratch git repositories at run time and proves, among its cases:

1. A file held with CRLF under `core.autocrlf=true` (a Windows checkout) and the same file held with LF (a Linux checkout) hash to one id inside a repository; outside one, `record` still runs and gives the raw content's id.
2. An absent input yields no line; an input added after recording is reported *added*; a deleted one *removed*; an edited one *changed*; an untouched set compares equal whether committed, staged or neither.
3. A folder moved with `git mv` compares equal.
4. A record that is not last, or has a malformed line, falls back to the time rule.
5. The umbrella's check: a re-priced included slice, a new slice, an excluded slice priced since, an excluded unpriced slice whose inputs moved, a stale included slice (through `stale_slices`), a changed container defect source, a changed profile — each reported stale with its reason; an untouched set reported current; an `excluded` field on any line but a `brd-link.md` one refused as malformed.

Then the repository's gates — `scripts/check-docs.sh`, `scripts/validate-catalog.py`, `scripts/check-id-grammar.sh`, the mermaid gate — and one Opus whole-branch review, its findings all fixed in the same round.

## Release

The next free `product-workflows` minor above 3.26.1 (3.27.0 unless taken at merge), CHANGELOG dated at merge; `docs/commands/prd-proposal.md`, `docs/commands/brd-proposal.md`, `docs/reference/proposal-format.md` and `.claude/rules/product-workflows.md` updated where they state the currency test, the census, or `/brd-proposal`'s flow (which gains the early check).

## Amendment — 3.27.1

Four follow-ups from the 3.27.0 review's set-aside cases, each a fix: **a symlink counts as the file or directory it points at** (the pricing reads through it; a dangling link is no input; a directory reached twice is walked once); **only `.md` files under `grounding/` are inputs**, so an editor's backup or autosave never is; **`--baseline` is an input** — under `$SPECS_PATH` by its `$SPECS_PATH/` path, inside the folder by its folder-relative path, elsewhere under the root by its `$SPECS_PATH/` path, outside it as `<outside>` with its id and without its path — each on a line flagged `baseline`, compared wherever this machine holds it and otherwise listed under `unverifiable`, never counted; never the folder's own `proposal.md` or `proposal-brief.md`; section 22 names an outside one by file name alone; and **`/brd-proposal`'s Stop answer says where the umbrella stands in git**, from three of `require-on-main`'s read-only primitives (phase-handoff §3.2) — never the gate, which prompts and can switch branches. A sorted walk records the same path on every machine, and a link up to the folder or above it is not followed.

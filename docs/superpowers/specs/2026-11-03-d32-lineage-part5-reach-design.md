# D32 — Document lineage, part 5: the altitude filter's reach, and part 4's minors

Date: 2026-11-03. To-fix entry: **D32**, follow-ups (4) and (5). Builds on parts 1–4 (`2026-11-03-d32-document-lineage-design.md`, `…-part2-prd-ard-design.md`, `…-part3-brd-design.md`, `…-part4-docs-design.md`), whose decisions bind here unchanged: the record format, the moved rule, the full walk, the per-link altitude filter, the never-ask callers.

## Intent

A grounding file changes on every `/prd-ground` run even when nothing a downstream document was built from has changed, and the lineage check reads that churn as a move. Two causes, found by part 3's review:

- **The repository-pin finding.** Every run that grounds code mints a fresh baseline `[CG#n]` per repository — "`<repo>` is pinned at a verified, unmodified commit", `altitude: implementation` — and supersedes the last (`workflows-core:grounding-format` §4.1). An added item and a changed item, at implementation altitude: every specification that recorded the grounding, and the decision register (whose link to the grounding compares everything), read as behind it after any re-run. Nothing downstream draws from a baseline finding — §4.1 rule 3 says so — so the noise buys nothing.
- **Text outside every finding.** `lineage.py` puts it in per-section buckets with no altitude, so it counts for every downstream. Three sections hold it: `## Derivation matrix` (implementation facts `/specify` reads), `## Documentation divergences` (where the product docs contradict a verified finding; never evidence) and `## Frame sets covered` (a census of `design/` for `/brd-split`'s gate).

The goal: an unchanged `/prd-ground` re-run reads as no move for any downstream, and a real change still reaches exactly the documents at its altitude.

Part 4's review also left six minors (D32 (5)); the maintainer folded them into this release, so D32 closes with it.

## Decisions (the maintainer's)

1. **A baseline finding never counts.** It is left out of the comparison entirely, for every downstream. It is identified by the grounding folder's own pin record, `grounding/baselines.md` — each entry's `finding:` id — never by its `claim` text (CLAUDE.md, *resolve an identifier against a known set*; §4.1 resolves supersession the same way). If the code moved, the claim findings re-checked at the new commit change too, and those count.
2. **Each section counts at its own altitude.** `## Derivation matrix` is implementation altitude (`grounding-format` §7: "always implementation-altitude"): a specification and the register see a change in it, an ARD does not. `## Documentation divergences` and `## Frame sets covered` are notes: a change there counts for no downstream, the register included.
3. **Part 4's six minors are fixed in this release** (below).
4. **A finding is compared by what it asserts, never by its verification bookkeeping.** Every `/prd-ground` run re-verifies each finding and writes that run's `outcome` onto it, and a `notes` entry on some outcomes (`grounding-format` §2.1's closed field set: §2's fields plus `outcome` and `notes`). A change in those two fields alone — `agree` flipping to `extend`, a note recording an inconclusive re-derivation — is not a move; the claim, verdict, evidence, altitude, horizon, commit and the rest are. A contradiction still counts: it retires the finding (`SUPERSEDED`) and appends its successor, both item changes.

## The six minors (D32 (5))

1. **Acceptances read from disk only.** `lineage.py check` reads each `--accepted-from` (and `--output`) document from the working tree, while `/document`, `/release-notes` and `/ready` 2a say "in the working tree or on `<default-ref>`". The script reads a document missing from disk at `<default-ref>` instead.
2. **A missing ref reported as absent.** With no `<default-ref>` in `$SPECS_PATH`, or a `$SPECS_PATH` that is no repository, every document comes back `absent` and the run reports *not on `<default-ref>`*. The script refuses instead: a non-zero exit naming the ref it could not resolve, which every caller already handles (an asking caller stops with `_LINEAGE_FAILED`, a never-ask caller prints a ⚠ line).
3. **The ⚠ template drops new keys.** `/document`, `/release-notes` and `/ready` 2a write `<changed keys>`; a requirement the PRD gained is in the JSON's `added`, so a literal fill prints none in exactly the headline case. Each quotes §6 step 3's own form, `changed <keys>; new <keys>; withdrawn <keys>`.
4. **"Those two" in §6 step 6.** Names `/document` and `/release-notes` instead.
5. **A link above the units repeated per unit.** A stale `prd.md ← decisions.md` comes back from every Epic's check. A never-ask caller lists, and counts, each (downstream, upstream) pair once.
6. **No report line for a script failure.** §7 gains `Lineage: not checked — lineage.py failed: <first stderr line>` for a never-ask caller, whose run did reach `upstream-check`.

## Goals

- `/prd-ground` re-run with nothing changed → no stale link from the grounding for the register, any ARD or any specification, whatever outcome each finding's re-verification wrote.
- A changed claim finding still reaches the downstreams at its altitude, and a changed derivation matrix still reaches every specification and the register.

## Non-goals

- No change to what a baseline finding is, how it is verified, or `baselines.md`'s layout.
- No change to the register's own altitude handling or to any downstream's altitude.

## The builder's calls (mine; the builder may revisit with a ledgered ruling)

- **The derivation matrix becomes one replaced section.** `/prd-ground` Phase 8 appends its rows on every run that writes one, under no fixed heading, so a re-run that derives the same rows would add them again and read as a move at implementation altitude — decision 1's goal fails without this. It writes them under one `## Derivation matrix` heading, **replacing any section of that name** rather than appending a second, as it already does `## Frame sets covered`; `grounding-format` §7 names the heading. The builder confirms the current layout first and reports a real file whose earlier matrix rows a replacement would drop (rows a later run did not derive again), rather than deciding it away. *Revised by the final review:* a literal replacement could delete a finding written after the table and would reword an unchanged matrix, so `/prd-ground` keeps the section — its heading, lead-in and table, never a `- id:` block — and reconciles it row by row, leaving a row derived again unchanged byte for byte; and a run's dated section in `design-grounding.md` is dropped as the two notes sections are.
- **How the script learns the rules.** Kind-table data, not code paths: the `grounding` row gains a per-section altitude for `Derivation matrix`, a list of sections whose own text is dropped (`Documentation divergences`, `Frame sets covered`), the two bookkeeping fields to ignore with their continuation lines (`outcome`, `notes`), and a way to name the baseline set — the builder chooses the field names. **Not the existing `notes` mechanism** for the two sections: it skips every line until the next heading, and `/prd-ground` appends a later run's findings after `## Documentation divergences` with no heading between, so it would hide them (the builder check reproduced it). A dropped section's text is left out, but an item-start line inside it still opens a finding, exactly as one inside any other section does.
- **The dropped sections' own layout is out of scope.** `## Documentation divergences` is appended on every run with documentation grounding on, so a file can carry several; with its text dropped that no longer touches lineage. A new to-fix entry records it for `/prd-ground`.
- **A never-ask caller's per-pair count** (minor 5): a (downstream, upstream) pair stale in any unit is listed once, as stale; it is shown *accepted in this unit* only where every unit that met it accepted it, since acceptance is per unit.
- **A `baselines.md` entry with no `finding:` id** (the legacy layout) excludes nothing: its repository's next re-pin reads as a move once, after which every baseline id is on record.
- **The not-checked lines** (minors 2 and 6): an unresolvable ref now comes back as a script failure, reported `Lineage: not checked — lineage.py failed: <first stderr line>`; `Lineage: not checked — <doc…> not on <default-ref>` stays for a valid ref whose documents are missing from it. The baseline ids are read from `grounding/baselines.md` beside the grounding file, at `<default-ref>` — append-only, so its current copy names every baseline id the recorded copy can hold. A `baselines.md` missing or unreadable excludes nothing: today's behaviour, the safe side.
- **A grounding file's per-run date headings** (`design-grounding.md`'s run headings) already add nothing — an empty section bucket is dropped — and stay as they are; the builder confirms with a test.
- **The minors' fixes are in the script where the defect is the script's** (1, 2) and in prose where it is the prose's (3–6).
- **A reviser's own diff of the grounding follows the same two rules.** `/product-workflows:update-spec` Phase 2 lists the grounding's implementation records changed since its base; a re-pin, a dropped section and a change in a finding's `outcome` or `notes` alone are left out of that list too, so the change list a revision is grilled on matches what the check reported. The builder sweeps for any other prose diff of a grounding file.

## Tests (for the plan)

`lineage.py --selftest` gains, at least: an unchanged re-run (a fresh baseline `[CG#n]` added, the old one `SUPERSEDED`, `baselines.md` naming both) → no link for an `implementation` downstream nor for the register; a changed claim finding beside it → reported; a changed `## Derivation matrix` → stale for `implementation` and unfiltered, not for `architecture`; a changed `## Documentation divergences` or `## Frame sets covered` → no link anywhere; a `[CG#n]` appended after `## Documentation divergences` with no heading between → reported; a changed `outcome:` or `notes:` (one line, and a multi-line `notes`) on an otherwise unchanged finding → no link; `baselines.md` absent → today's behaviour; `--accepted-from` present only on the ref → honoured; an unresolvable `--ref` → non-zero exit.

## Release

workflows-core minor (`lineage.py`, `lineage-kinds.json`, `document-lineage` §2/§6/§7, `grounding-format` §4.1/§7); product-workflows patch (`/prd-ground` Phase 8's matrix section); docs-workflows and dev-workflows patches (the ⚠ templates, the per-pair count); a coupling bullet; docs pages where they describe what counts; `docs/superpowers/to-fix.md` — D32 closed, and a new entry for `## Documentation divergences` piling up across runs. A claim sweep (refinements 3, 7, 8) for every sentence saying text outside a record counts at every altitude, that an unchanged re-run reads as a move, or that the derivation matrix is appended.

# D50 — `/ready` orders work within a day: a UTC instant on the records it compares

**Date:** 2026-11-12. **Status:** design, revised after two Fable design reviews (2026-11-12), for approval. **Fixes:** D50 in `docs/superpowers/to-fix.md` (delete the entry when this lands), and the same limit in `workflows-core:source-truth` §7.8 rule 1.

## 1. The problem

`/dev-workflows:ready` decides whether work was implemented after the PRD's conformance record (Phase 1 step 2b, condition 6), and after each release-preparation draft (step 2c), by comparing bare `YYYY-MM-DD` dates, each in its writer's own zone:

| Record | Its date today | Writer | `/ready` reads it in |
|---|---|---|---|
| `/implement`'s block | `## <YYYY-MM-DD> — /implement` (`workflows-core:implementation-format` §1) | `/implement` Phase 4.7, the only writer | step 2b condition 6, step 2c |
| PRD conformance record | `- **Run:** … — <YYYY-MM-DD>` (`dev-workflows:conformance-format` §2) | `/conformance` Phase 5 | step 2b condition 6 |
| Dev-stage release note | scope comment's first line, `<!-- release-note scope: <KEY> <YYYY-MM-DD>` (`docs-workflows:release-note-types` §1) | `/release-notes` Phase 8 step 1 | step 2c |
| `pr-draft.md` | its last commit's committer date, `git log -1 --format=%cs` | git (`/document` writes the file) | step 2c |

Two failures follow, both stated in `ready.md` as known limits:
- **Same day.** Work implemented later on the same day is missed.
- **Zones.** Writers in different zones can be a day apart either way.

`source-truth` §7.8 rule 1 ("the Epic's record carries a later `Run:` date than the PRD folder's") compares two `Run:` dates with the same limits.

## 2. Goals, non-goals, anti-goals

- **Goal.** Where every record in a comparison was written after this change, they are ordered by instant, in UTC, so neither failure occurs. One residual limit is stated, not hidden: the writers' clocks. Each instant comes from its own machine's clock, so a clock skewed by minutes can misorder work done minutes apart.
- **Goal.** Records written before this change read exactly as they do today, limits included. Nothing is migrated.
- **Non-goal: the session-hygiene resume-pointer rules.** They date a record by its heading day, then `git blame`. Using the instant there is a separate improvement, recorded as a follow-up.
- **Non-goal: `implementation-format` §4's date fallback.** It applies only to notes with no `read:` lines. Those lines date from `docs-workflows` 1.2.2 (`implementation-format.md:384`), so it does not meet a note written since.
- **Anti-goal: changing the `## <YYYY-MM-DD> — /implement` heading.** `lineage.py:507` (`_IMPL_BLOCK`) would stop matching, so `accept` would error. So would every prose presence test, "holds at least one `## <YYYY-MM-DD> — /implement` block". (`session-branch.py:141` already accepts a `T…Z` suffix, but an offset form would break it too.) The heading, the `Run:` line and the scope comment's first line all stay exactly as they are.

## 3. The design — decided

### 3.1 The instant

**Format.** Every new value is exactly `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`, a UTC instant. Cost entries and the specs-git state record already use this format.

**Writing it.** It is written by pasting the output of `date -u +%Y-%m-%dT%H:%M:%SZ` verbatim. That command is POSIX, and identical with GNU and BSD `date`.

**An invalid value.** A value that does not match the pattern — hand-typed, offset form, truncated — is **no instant**. The pair it is in falls back to dates (§3.3). It never makes a record unreadable.

**Comparing.** Each value is first tested against the pattern above. Two instants that pass are compared mechanically, `[ "$a" \> "$b" ]` in the shell: fixed-width `Z` instants order as text, and no agent compares them by eye.

### 3.2 Where each instant is written, and what it means

**Which moment each record takes.** Each record takes the instant that keeps a mistake harmless.
- **A block takes the moment it is written**, so it is never earlier than the work it records. A block dated late only asks for a re-run.
- **A record that checks work takes the moment its run started**: right after `strip-run-flags`, in `/conformance`, `/release-notes` and `/document` alike. That fixed point needs no judgement, it comes before any read, and it exists on every run. Some runs read no implementation record at all, such as a `/release-notes` run without diff grounding. Work that lands while the run is going on then counts as implemented since. The instant is carried in the run and written when the record is.

1. **`/implement`'s block entry gains `at:`**, written after `pushed:` and before any `accepted:`. It holds the instant Phase 4.7 appends the block. `lineage.py accept` appends `accepted:` at the end of the block, so the order is `pushed:`, `at:`, `accepted:`. `implementation-format` §1's two examples show it.
   - **A multi-entry block.** A block written before `dev-workflows` 4.7.0 may carry several entries. It has an instant only where every entry carries the same valid `at:`. A block a hand edit leaves otherwise has none.
2. **The conformance record's header gains `- **At:** <instant>`**, as the line after `- **Run:**`. It holds the instant the `/conformance` run started, written at Phase 5.
   - **The guard.** An `At:` whose date part is more than one day from its record's `Run:` date is no instant. That catches a stale `At:` an older `/conformance` re-run kept beside a new `Run:` date (§3.4).
   - `source-truth` §7.8's malformed test reads the `Run:` line only, so a record without `At:` stays well-formed.
3. **The release-note scope comment gains `at: <instant>`**, a line after `stage:` and before the `read:` lines. It holds the instant the `/release-notes` run started, written at Phase 8 step 1.
   - `release-note-types` §1 currently says `stage:` is "the comment's only line that is neither its first nor a `read:` line". That sentence changes to name `at:` too.
4. **`pr-draft.md` gains a last line, `<!-- implementation records read: <instant> -->`**, the instant the `/document` run started.
   - **Why last.** The draft's DO-NOT-MERGE banner must stay its first line (`document.md:1316`; `docs-workflows`' own `references/finish-and-handoff.md` §5, which owns the draft's composition).
   - **The PR body.** `/document` prints the draft without that line, so the Bitbucket footer's "paste the body" pastes no comment. `gh pr create --body-file` passes the file as written, and GitHub hides an HTML comment.
   - **Stated as a limit:** a user who pastes from the file itself, not the printed draft, onto a host that does not hide HTML comments will show the line.
   - **`/ready`'s read.** It reads the draft's last line from `<default-ref>` with `git show`, against exactly `^<!-- implementation records read: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) -->$`. `ready.md:211`'s "its text is not read" narrows to "only its last line is read".
   - **A draft without that line** (every draft written before this change) is dated as today: `git log -1 --format=%cs`, the committer date in the committer's zone, a date-only record.
   - **A shallow repository.** The fallback first tests `git -C "$SPECS_PATH" rev-parse --is-shallow-repository`. Where that prints `true`, the draft "could not be dated", because a `--depth` clone prints its boundary commit's date, which is too late. This fixes today's claim that a shallow clone "prints no date", which does not hold.

### 3.3 The comparison — one rule, stated once in `ready.md` and cited by both steps

A pair is ordered by instant where both carry a valid one: the later instant is later, and an equal one is not. Where either lacks one, the pair is compared by its dates as written, exactly as today, and today's two limits apply to that pair alone.

- **The block's date** is its heading date.
- **The record's date** is its `Run:` date.
- **The note's date** is its first line's date.
- **An old `pr-draft.md`'s date** is its `%cs`.
- **A new `pr-draft.md`** carries an instant, unless §3.1 makes its value none — hand-removed or invalid — and then it is dated as an old draft.

**Step 2b, condition 6.** The record fails where any block in the PRD's tree is later than it under the pair rule. The tree is read in condition 6's existing order, and the first later block names the reason.

**Step 2c.** Each signal is compared with **every** block, not with "the latest block's date". Under mixed records there is no single latest, and a union-merged `implementation.md` is not in time order.
- **Documentation.** The signal holds where no block in the tree is later than the draft.
- **Release note.** The signal holds where **at least one** `stage: dev` draft is later than or equal to every block, that is, where no block is later than that draft. With every value a bare date, this equals today's rule, which takes the latest draft date.

**The reason lines keep their shape.** A block is named by its unit key and heading date, plus ` at <instant>` where it carries one.
- **For `pr-draft.md`:** the reason names `<its date>` as its instant where it has one, else its `%cs`.
- **For the release note**, where no `stage: dev` draft holds, the reason names:
  - the draft whose first-line date is latest, the last such draft in the file on a tie, with its instant where it has one;
  - and the first block, in condition 6's reading order, that is later than that draft.
- **The `Delivery:` line** keeps `(checked <Run: date>)`.

**`source-truth` §7.8 rule 1 takes the same pair rule.** The Epic's record "carries a later `Run:`" where both records carry an `At:` and the Epic's is later, or where either lacks one and its `Run:` date is later. Its wording "the Epic run traced the code after the PE ruled" becomes "the Epic run started after the PRD run started", since `At:` is a start instant.
- **A limit for rule 1.** An older `/conformance` PRD re-run on the same day as its stale `At:` passes the guard in §3.2 item 2. It can make a newer Epic record read as later, and the PE's ruling then yields to it. This needs mixed versions and a re-run that keeps a line it does not know.

### 3.4 Coupling and mixed versions

- **A newer `/ready` beside older writers.** No record carries an instant, so every pair compares by date, as today.
- **An older `/ready` beside newer writers.** It reads the labels it knows and passes over `at:`, `At:` and the comment line, as today. An older `/ready` still parses a new `pr-draft.md`'s presence.
- **An older `/conformance` re-running over a newer record.** It writes its own header. Where its rewrite keeps a stale `At:`:
  - for `/ready`, the result is only a false "work implemented since", which asks for a re-run;
  - for §7.8 rule 1, §3.2's one-day guard drops it, except on the same day (§3.3's rule-1 limit).
- **A newer `/ready` beside an older `docs-workflows`.** No draft carries an instant, so both drafts compare by date, as today.
- **An older `/release-notes` beside a newer scope comment.** It passes over the `at:` line.
- The coupling bullet names all five cases.

## 4. Who changes what

- **`workflows-core`:**
  - `implementation-format` §1: `at:` (definition, reader, both examples, the multi-entry rule), and the header sentence at its lines 10–11;
  - `source-truth` §7.8: rule 1, its reason wording, and the header-field list at line 589. Regenerate its reference parts if it has any;
- **`dev-workflows`:**
  - `/implement` Phase 4.7 writes `at:`;
  - `conformance-format` §2 gains `At:`. Its reader list (§6), the `/ready` paragraph and the two paragraphs for `/release-notes` and `/document` each say `At:` is read where it is;
  - `/conformance` takes the instant at the run's start and writes it at Phase 5;
  - `/ready` Phase 1 steps 2b and 2c and line 917;
  - `workflow-states` lines 32 and 37;
  - the pages `docs/commands/ready.md` (lines 58–68 and 101), `docs/commands/conformance.md:89` and `docs/workflow.md:75`.
- **`docs-workflows`:**
  - `release-note-types` §1, including line 56 and the "only line" sentence;
  - `/release-notes` takes the instant at the run's start and writes it at Phase 8 step 1, including the line list at line 668. Its Phase 0 read list at line 217 names `At:`;
  - `references/finish-and-handoff.md` §5 (`docs-workflows`' own): the draft's last line;
  - `/document` takes the instant at the run's start, writes `pr-draft.md`'s last line, and prints the draft without it. Its Phase 3 read list, near line 446, names `At:`;
  - the pages `docs/commands/release-notes.md:62` and the `/document` page.
- **`product-workflows`:** `docs/workflow.md:225`.
- **`workflows-core` page:** `docs/family-map.md:193`.
- **Rules:** `.claude/rules/release-notes.md:35`, and `.claude/rules/dev-workflows.md` lines 37 and 71. `docs/maintainers/rationale.md:483` where it states the limit.
- **The claim sweep is by subject:** how `/ready` and §7.8 order these records. The sites above are the population found on 2026-11-12, not the population. Re-derive it by subject (`claim-sweep` refinements 6–8) before editing, and count before and after.
- **Tests:**
  - `lineage.py`'s selftest: a block with `at:` that `accept` still finds and writes into, with `accepted:` after `at:`.
  - `session-branch.py`'s selftest: a union of two same-day blocks carrying `at:`, which pins that the field changes no heading split.
- **`to-fix.md`:** D50 is deleted. The session-hygiene follow-up is added as its own entry.
- **Release:** `workflows-core`, `dev-workflows`, `docs-workflows` and `product-workflows` (one page), with one coupling bullet (§3.4).

## 5. Left to the builder

- The exact sentences, under the family's prose rules.

## 6. Rulings (to check)

- **A UTC `Z` instant**, not a local time with an offset. It compares as text and needs no zone arithmetic. A human reading it sees UTC.
- **New fields and lines, not changed ones**, for the regex and the presence tests in §2's anti-goal.
- **Which moment each record takes.** A block takes its writing moment; a check takes its run's start. Each errs only toward a re-run.
- **`pr-draft.md` carries its own instant in an HTML comment, as its last line,** instead of a git date. The git date is the landing time, which can be long after `/document` read the records. The cost: one comment line in a file that becomes a PR body, handled by printing without it.
- **The clock-skew limit is stated, not engineered away.**

# Threat intake — threats sent back to the architect (shared reference)

Single source of truth for which threats of an ARD threat model are **sent back to the architect** — a threat sent back being a live threat of the model, readable and not stale, that a design or a conformance record sends to the architect, in one or more of the three kinds below — and for how what is read to find them is held. `/product-workflows:create-ard` loads it, and no other command or agent does, at its Phase 4.3 on a refine of the model its folder holds, and tests for this file's first line, whole, before it reads anything for it. It is read beside `workflows-core:threat-model-format`, which that run has loaded and which is cited below as *format §N*: the model, its threats and their dispositions are the format's. **`/dev-workflows:conformance` states the rules this reference restates — the entry reading, the reasons an `unanswered` threat takes, and where an `open` on a decision goes — in its own Phase 1 (b), Phase 5 and `### Next step`, and does not cite this reference**: beside an older `workflows-core`, which has none, a `/conformance` citing it would lose its threat states.

## 1. The threats tested

Of the model's live threats, as format §10 reads them, a threat the check (format §6) found stale is not tested, unreadable or not: it is re-disposed as a stale threat. Of the rest, a threat format §10 finds not in format §4's form — a field missing or repeated, its Where, its Disposition in none of the three forms, its id heading more than one threat — is **unreadable**, save one whose `Accepted — ` Disposition is faulted for its review date alone, missing or malformed. An unreadable threat is never sent back: the run prints `Threat model: [TH#N] is unreadable — not tested as sent back; the review takes it`, once for each such id, and the threat keeps its own route, the review. Every other one is tested.

**The threat's ref**, `<ref>`, is its id in the cross-folder form (format §5), `[[<K>]] [TH#N]`, `<K>` the run's own key for the model's folder — never one read out of a file.

## 2. The files read

**The files**, each at a known path, never found by a search, `<F>` being the run's own path for the model's folder, relative to `$SPECS_PATH`:
- `<F>/design.md` and `<F>/_conformance.md`;
- on a PRD-level run — `F` a PRD folder, a BRD-route slice included — the `design.md` and `_conformance.md` of each Epic folder the guard below lets the run read;
- on an Epic-level run, also the `_conformance.md` of the PRD folder above `F`, at the run's own path for that folder: a PRD run's record holds entries on an Epic's decisions.

**`<F>`, and on an Epic-level run the PRD folder's path, are the run's own resolved folders.** Each stands in the commands below as it stands in every other command of the run, and the guard below does not test it.

**The two listings**, each of `<default-ref>` — the ref that represents the specs repository's default branch (`workflows-core:specs-repo-git` §3.2):
1. `git -C "$SPECS_PATH" -c core.quotePath=false ls-tree -d --name-only "<default-ref>" -- "./<F>/" 2>/dev/null`, the folders directly under `F`, made on a PRD-level run only;
2. `git -C "$SPECS_PATH" -c core.quotePath=false ls-tree -r --name-only "<default-ref>" -- "./<F>/" 2>/dev/null`, the files under `F`, made on a PRD-level and an Epic-level run alike, since the working-tree-only test below reads it.

Each is read from its standard output alone, as text, and **a line ends at a line feed and at nothing else**: a U+0085, U+2028 or U+2029 a name holds is part of its line. Each prints a path relative to `$SPECS_PATH`, as `<F>/<name>`, never a bare name, and `--full-name` is never added. `core.quotePath=false` prints a byte above 0x7F as it stands, whatever the user's own setting; a path holding a control character, `"` or `\` is still printed whole in git's quoted form, opening `"`. A listing fails where it exits non-zero, and then adds nothing and stops nothing; where either fails, the run prints, once however many fail, `Threat model: a listing of the default branch failed — the Epic folders under it may be unread, and a design only the working tree holds is not named`. `<PRD>` below is the run's key for `F`, on a PRD-level run.
- **A folder directly under `F`** is a line of the first listing that is, whole, `<F>/` followed by one path component — no `/` in it. That component is its name, each name taken once. A line of any other form, git's quoted form included, is a folder named by position, and not read.
- **A candidate** is a folder whose name begins `EPIC-`. It is read only where four tests pass, in this order: its name matches, whole, `^EPIC-[A-Za-z0-9._-]+$`; its `epic.md` at the ref, `git -C "$SPECS_PATH" show "<default-ref>:./<F>/<name>/epic.md" 2>/dev/null`, exits 0 and asserts a key — its frontmatter, the lines after a first line that is, whole, `---` up to the next line that is, whole, `---`, holds exactly one line opening `key: `, and the rest of that line is the key — and that key matches, whole, `workflows-core:addressing` §1's grammar, written `^[A-Z][A-Z0-9_]*(-[0-9]+)+$`; the name begins, whole, `EPIC-<that key>-`, as `workflows-core:addressing` §4.1 tests a prefix; and the key is not, whole, `<K>`, and no candidate of another name that passes the first three tests asserts it — two such candidates both fail. The name is tested before it enters any command, and the key read is then the run's key for the folder. A candidate that fails a test, and a line of another form, is named in one line, and neither of its files is read: `Threat model: an Epic folder not read — entry <n> of the default branch's listing under [[<PRD>]], its name or its key outside what this run reads`, `<n>` its position among the lines the first listing printed, counting from 1. **This is a guard on Epic folder names, not a naming rule**: a class of folder names stated in `workflows-core:addressing` §2 would replace it.
- **A folder with no `EPIC-` prefix is never read, and never resolved through `workflows-core:addressing`.** Count those for which the second listing holds a line that is, whole, `<F>/<its name>/design.md` or `<F>/<its name>/_conformance.md`, and, where the count is not zero, print `Threat model: <n> folder(s) under [[<PRD>]] with no EPIC- prefix hold a design.md or a _conformance.md on the default branch — not read for threats sent back`. No such name enters a command or is shown.
- **A copy only the working tree holds.** For `<F>/design.md`, and, on a PRD-level run, for the `design.md` of each directory directly under `F` in the working tree — as the first tree listing below lists them — whose name matches, whole, `^EPIC-[A-Za-z0-9._-]+$`: where the file stands in the working tree, a regular file and no symbolic link (`[ -f "$SPECS_PATH/<path>" ] && [ ! -L "$SPECS_PATH/<path>" ]`), and the second listing holds no line that is, whole, its path, print `Threat model: <path> is not on the default branch — it nominates nothing`, and nothing of that file is read. That line is a design's alone: a record only the working tree holds nominates nothing, and no line names it. **Where the second listing fails, this test is not made and no such line is printed**: a failed listing never reads as an absent file.

**The two tree listings**, read as the two listings are, a line ending at a line feed alone, and each line compared whole:
1. `(cd "$SPECS_PATH" && find "./<F>" -mindepth 1 -maxdepth 1 -type d) 2>/dev/null | LC_ALL=C sort`, the directories directly under `F`, in byte-wise order, each line `./<F>/` followed by one path component;
2. `(cd "$SPECS_PATH" && find "./<F>" -mindepth 2 -maxdepth 2 -type f \( -name design.md -o -name _conformance.md \)) 2>/dev/null`, those two files in each of them, a folder holding one where a line is, whole, `./<F>/<its name>/design.md` or `./<F>/<its name>/_conformance.md`.

No name is ever an argument of either, and `-type` lists no symbolic link.

**The limits.** A legacy Epic folder with no prefix, which `/dev-workflows:conformance` places by its resolved kind, has its threats reported there and is not read here; nor is an Epic folder whose name holds a character outside the guard's class. A `design.md` the working tree alone holds in any other directory under `F` is not named: the run reads no design in such a folder, so it is no consumer of that file, and no unguarded name is tested. Where `<F>` itself holds a control character, `"` or `\`, which git quotes under any setting, no line of either listing is of a form above: every folder under `F` is named by position, and `<F>/design.md` takes the working-tree-only line, though the ref may hold it, and nominates nothing.

**How each is read.** Each file is read as `<default-ref>` holds it, `git -C "$SPECS_PATH" show "<default-ref>:./<path>" 2>/dev/null`, `<path>` its path above, its standard output being the file only where it exits 0 — never the working tree's copy and never another ref, so a design or a record that has not landed nominates nothing. No gate runs on it, no repair is offered, and nothing is switched; a `git show` that exits non-zero reads nothing, stops nothing and names nothing. A `design.md` so read is a **design read**, and a `_conformance.md` so read a **record read** once §4 lets it be read. **On a specs tree that is no git repository** (`git -C "$SPECS_PATH" rev-parse --git-dir` fails) there is no other copy: each file is read from the tree, only where it is a regular file and no symbolic link (`[ -f "$SPECS_PATH/<path>" ] && [ ! -L "$SPECS_PATH/<path>" ]`); the first tree listing stands for the first listing, with `./<F>/` for `<F>/`, held to the same guard; the folders with no `EPIC-` prefix are counted from the second tree listing, the count line's `on the default branch` reading `in the specs tree`, and the Epic-folder line's `the default branch's listing` reading `the specs tree's listing`; and neither the `not on the default branch` line nor the line a failed listing prints is ever printed. A tree listing that fails in part — a directory it cannot read — lists less and says so nowhere: a design or record it misses nominates nothing, and nothing is read, written or decided from what it does not list (a stated limit of a tree that is no git repository).

## 3. An entry, and the three kinds

**An entry**, as `/dev-workflows:conformance` reads one. A design **holds the section** where one of its lines is, whole, `## Threat review`, outside any fenced block, the section running from the first such line to the next `## ` heading outside a fenced block, or the end of the file. In a design read that holds the section, an **entry** is each `### [DT#N]:` heading at the start of a line in that section, outside any fenced block, `N` matching `^[1-9][0-9]*$`, with its block, which runs to the next `### ` or `## ` heading, and is **live** where its block holds no `- **Withdrawn:**` list item at the start of a line. An entry answers a threat where its block holds `- **Answers:**` exactly once, as a list item at the start of a line, and its `Answers` is, whole, the threat's ref. Its Disposition is read only where its block holds `- **Disposition:**` exactly once, as a list item at the start of a line — for each opening below, and for a new threat's entry. A live entry is ***M*** where that Disposition opens `Mitigated — Rule: ` — none is where its `[DT#N]` heads more than one entry of the design.

**The deferred part**, as `/dev-workflows:conformance` reads one: the threat's Disposition opens `Deferred to design: `, or holds `; the rest deferred to design: `. An `Accepted — ` Disposition has none.

A threat tested takes **every kind that holds**, listed in the order 1, 2, 3. Kinds 1 and 2 exclude each other; either may hold beside kind 3.
1. **`returned`** — it has a deferred part; no live *M* entry of a design read answers it; and a live entry answering it bears a Disposition opening `Returned to the architect — `.
2. **`taken by no design`** — the same, save that no live entry answering it bears that opening, and one bears a Disposition opening `Not this design's — `. An Epic-level run reads no other Epic's design, so there an entry opening `Not this design's — answered in ` counts as one opening `Not this design's — `, though `/dev-workflows:conformance`'s Epic run reads it as answered elsewhere.
3. **`open on a decision`** — its Disposition opens `Mitigated by `, and a record read holds an entry that names one of its pairs' decisions and nominates (§4): `/dev-workflows:conformance`'s `open` on a decision the team will not build, read off the records the default branch holds.

A threat no live entry and no record names in these ways is not sent back: `no design answers it` is the Dev's.

## 4. The records

**The record test is this reference's own**, not `workflows-core:source-truth` §7.8's. The record set is the `_conformance.md` files of §2. A path whose `git show` exits non-zero is no record, and no line names it. A record is read only where its frontmatter, read as §2 reads a candidate's `epic.md`, holds exactly one line opening `key:`, that line is, whole, `key: <the run's key for the record's folder>`, and no line of the record begins `<<<<<<<` or `>>>>>>>`. Any other is not read, and the run prints `Threat model: <path> not read — its key is not its folder's, or it holds a conflict marker`. A record in a folder whose key the run could not take — an Epic folder the guard did not let it read — is not read either, and that folder's line names it. **No instant is used**: nothing here orders two records, so `At:` and its guard are never read.

A record's lines are read in the forms `dev-workflows:conformance-format` §3 writes, stated here since this run cannot load that reference:
- **An entry** is each line, outside any fenced block, that is, whole, `### [DD#<n>] <requirement id>`, `<n>` matching `^[1-9][0-9]*$`, with its block, which runs to the next `### ` or `## ` heading.
- **`document:`** — the block's line opening `- **document:** `, written `- **document:** <file>, in <KEY>`.
- **`decision:` and `status:`** — its line opening `- **decision:** `, which is, whole, `- **decision:** <decision> — **status:** <status>`, `<decision>` one of `fix-code`, `amend-document` and `accept`, `<status>` one of `proposed`, `final` and `resolved`.
- **`flags:`** — its line opening `- **flags:** `, the rest split on `, `, each item, whole, one of `stale`, `orphaned`, `fixed`, `still open` and `requirement withdrawn`. No such line is no flag.
- **`superseded-by:`** — a list item at the start of a line opening `- superseded-by: `: what a PRD run writes into an Epic entry the PE overrules.
- **The `Run:` date** — the text after the last ` — ` of the one line opening `- **Run:** ` before the record's first `## ` heading.

A `document:` line, or a `decision:` line with its `status:`, that is missing, repeated or outside its known set, and a `flags:` line repeated or holding an item outside the five, means the entry nominates nothing.

**An entry names a pair's decision** where its heading's requirement id and its `document:` line are, whole, the two the run composes from the pair, and nothing is read out of either. The threat's pairs are read in format §4's form — the text after `Mitigated by `, up to `; the rest deferred to design: ` where it holds one, split on `, ` — each `N` matching `^[1-9][0-9]*$`, and a pair in neither form below names nothing:
- for `<ARD file> [AD#N]`, a decision of the model's own folder, `<ARD file>` being `ard.md` or a name matching, whole, `^ard-[A-Za-z0-9._-]+\.md$` — the names `/dev-workflows:conformance` lists a decision under: `[AD#N] Rule` for `ard.md` and `[AD#N] Rule (<ARD file>)` for an area file, and `- **document:** <ARD file>, in <K>`;
- for `[[<PRD-KEY>]] ard.md [AD#N]`, which counts only where `<PRD-KEY>` is, whole, the run's PRD key (format §6): `[AD#N] Rule`, and `- **document:** ard.md, in <PRD-KEY>`.

It **nominates** where its `status:` is not `resolved`, its `flags:` name neither `orphaned` nor `requirement withdrawn`, its block holds no `superseded-by:` line, and its `decision:` is, whole, `amend-document` or `accept`. An Epic's entry and a PRD's on one decision both nominate, each shown with its own record's date; an overruled Epic entry is dropped by its `superseded-by:` line. **A limit:** an area file's decision that a record still writes in the legacy form, `[AD#N] Rule` with `document: ard.md`, fails the comparison and nominates nothing, though `/dev-workflows:conformance` matches it by `dev-workflows:conformance-format` §3's legacy match.

## 5. Compose and compare, and a nomination

**Compose and compare, never extract.** No key, id or path is taken out of a design or a record. The exceptions are the two numbers a heading's fixed position holds, `N` of `[DT#N]` and `n` of `[DD#n]`, and a record's `Run:` date, each shape-tested and shown; an Epic's key is read off its `epic.md`, as `workflows-core:addressing` §4 reads a folder's key off its carrier, and is shape-tested before the guard uses it.

**It is a nomination.** A record may be older than the code, and a design may not say what the code does: this reference decides only which threats the architect is asked about, and settles none. *Keep it as it stands* is always an answer: a threat sent back is not wrong, as a stale one is.

## 6. What is shown, and how it is held

Each value read, and its test:

| Value | From | Test, else |
|---|---|---|
| an Epic folder's name | the first listing | the guard of §2, else named by position and not read |
| an Epic's key | its `epic.md`, at the ref | `workflows-core:addressing` §1's grammar, else the folder is not read, as the guard has it |
| a record's `key:` | the record | equals, whole, the run's key for the record's folder, else the record is not read; nor is one in a folder whose key the run could not take |
| `N` of `[DT#N]`, `n` of `[DD#n]` | a heading's fixed position | `^[1-9][0-9]*$`, else the heading heads no entry |
| `Answers`, a Disposition's opening, a heading's requirement id, `document:` | a design, a record | compared whole with what the run composed, else it answers, opens or names nothing |
| `decision:`, `status:` | a record | whole, one of the values §4 lists, else the entry nominates nothing |
| `flags:` | a record | split on `, `, each item whole one of the five — `stale`, `orphaned`, `fixed`, `still open`, `requirement withdrawn` — else the entry nominates nothing |
| the `Run:` date | a record | `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`, else shown as `date unreadable` |
| a reason; a new threat's Threat line | a design | free text — the three rules below |

**Free text is shown in a question's text alone, by three rules, in this order:**
1. **One line.** It is made one line, by format §9's *Every value is one line*.
2. **The backstop, at its strictest, over the whole of it.** A text holding a match of either of format §9's two patterns is not shown: `withheld: it held a security finding id or register path` stands in its place. Nothing here was given in a brief, so no match is one the run carried, and every match is withheld.
3. **The cut, and the label.** Only then is it cut at 300 characters, ending `…`, so a cut never splits a match; and it is quoted behind the label `the design's own words:`.

A record's `shipped:` and `rationale:` are never shown, nor any other text of an entry but what *What sent each kind* names.

**What sent each kind.** For kinds 1 and 2: each live entry answering the threat that bears the kind's opening, named `[[<KEY>]] design.md [DT#N]`, `<KEY>` the run's key for its design's folder, with its reason — its Disposition's text after `Returned to the architect — ` or `Not this design's — `. For kind 3: each entry that nominates, named `<KEY>/[DD#n]`, `<KEY>` the run's key for its record's folder, with its `decision:`, its `status:` and its record's `Run:` date.

**Nothing read from a design or a record is written** — into the model, an ARD draft, the run's report or any other file — **or reaches an agent**: it is shown in a question's text alone. The run's report carries keys, ids and fixed words only.

**A returned threat that answers none of the model's** — a live entry of a design read whose block holds `- **Answers:**` exactly once, its value, whole, `—`, and whose Disposition, read as §3 reads one, opens `Returned to the architect — ` — is **listed, never converted**: named `[[<KEY>]] design.md [DT#N]`, with its Threat line — the text of its `- **Threat:**` item, where its block holds that item exactly once, as a list item at the start of a line, and `—` otherwise — and its reason. The entry stands until the Dev withdraws it.

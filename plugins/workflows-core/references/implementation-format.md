# Implementation record — Shared Reference

The shape of `implementation.md`, the file `/implement` appends to when it finishes work for a keyed
run, and the commit convention that makes work findable when the plugin was not the one that did it.
Design authority: `docs/superpowers/specs/2026-08-31-specs-native-pipeline-design.md` §7.3 and §7.3.1 (removed from the tree 2026-09-23; `git show 62e791e8:docs/superpowers/specs/2026-08-31-specs-native-pipeline-design.md` retrieves it).

**Written by `/implement`. Read by `/document` and `/release-notes`**, which hand the refs it records
to `diff-summarizer`; and, for whether it holds a block (§1) or for the repositories its entries
name, by `references/epic-picker.md`'s ● marker, `/ready`, `/specify` and `/epics`. §3's commit
convention is a separate thing with a wider writer set — all three of the commands that change code
— and §3 says how each of them writes it.

## 1. The block

One `## <YYYY-MM-DD> — /implement` block per run, with one entry: the code repository the run branched. A change another code repository needed is a later run from there, with a block of its own. A block appended before `dev-workflows` 4.7.0 may carry one entry per repository that run touched, and a reader takes every entry. For example:

```markdown
# Implementation — ACME-77-01 order intake

## 2026-08-31 — /implement
- repo:    orders-service
  branch:  feat/ACME-77-01-order-intake
  base:    main
  commit:  a3f91c2
  pushed:  true

## 2026-09-02 — /implement
- repo:    billing-api
  branch:  feat/ACME-77-01-order-intake
  base:    main
  commit:  7be0d41
  pushed:  false            # local only — resolvable on this machine
```

**Append-only.** No command edits or removes a block, and a re-run adds a block rather than
replacing one. This is the shape `grounding/baselines.md` already uses, one layer up. The one hand
edit this file names is the operator's move below.

**A record is present only where it holds a block.** Every reader that tests whether a folder has a
record — `/implement`'s ● marker (`references/epic-picker.md`), `/ready`'s artifact inventory, and
any other — tests whether its `implementation.md` holds at least one `## <YYYY-MM-DD> — /implement`
block. A file holding only its heading records nothing, which is what a PRD folder's file is left
as when its one block is moved out (below).

**Where it lives: in the folder of the unit the run implemented.** `/implement` implements one unit
per run — an Epic, whether its address named the Epic's folder or the run chose the Epic under a
PRD address, or a broad PRD-level slice — and the record is that Epic's folder's, or the PRD
folder's for the slice. A file the run creates opens with `# Implementation — <key> <slug>`, the
key and slug of the folder it sits in. **A block names no unit**: nothing in the shape above says
which, so the folder is what attributes a block to one, and no reader infers a unit from a branch
name. That is what lets an Epic-level reader read its Epic's record alone, the picker mark an Epic
done from its own folder, and a PRD-level reader take the PRD folder's record and every Epic's
under it.

**A block an earlier run left in the PRD folder for an Epic is the PRD folder's.** Until
`dev-workflows` 4.1.2 `/implement` wrote into the folder its address resolved, so a PRD-addressed
run that chose an Epic — through its picker, or as the PRD's only Epic — appended its block to the
PRD folder's record. That block says nothing of the Epic, so it is read as every PRD-folder block
is: by a PRD-level reader, and by no Epic-level one. No run moves or copies it — the file is
append-only — and the picker's ● marker, which reads the Epic's own folder, does not count it.

**Until that block is moved, the Epic reads as not implemented to everything Epic-level.**
`/implement`'s picker marks it ◐ where its `design.md` stands and ○ where it does not, a ◐ row
taking the default cursor; `/ready` derives its phase from an Epic folder holding no record; and an
Epic-level `/document` or `/release-notes` reads none of its refs. **Population: every Epic
implemented under a PRD address before `dev-workflows` 4.1.2.** And where the PRD folder also holds
a flat `specification.md`, a PRD-level `/ready` counts the block as the **broad PRD-level slice's
own record**, the PRD folder's record being the slice's — which moves the slice to *In Progress*
only where the PRD folder also holds a `design.md`, since `/ready` Phase 3(0) takes the furthest
rung whose expected artifacts all exist and the lower rung where they straddle
(`dev-workflows:workflow-states`, the Epic ladder). **Population: every PRD folder holding both a
flat `specification.md` and such a block, from `dev-workflows` 4.1.2, whose `/ready` is the first to
read that record.**

**The way out is the operator's: move that block by hand — cut it from the PRD folder's
`implementation.md` and append it to the Epic folder's**, creating the Epic's file where the folder
has none, under the heading a run would write: `# Implementation — <key> <slug>` with the Epic
folder's key and slug. Append-only binds the commands that write this file, not the operator, and
the move edits no block: it changes only the folder that attributes the block, which is the job
this section gives the folder. **A move, not a copy**: a copy left in the PRD folder is harmless to
the diff readers, since a read that takes both records counts the ref once (§4), but `/ready` still
counts it toward the broad slice.

**Which block is the Epic's is not written anywhere, so it is read off the code.** A block names no
unit, and before `dev-workflows` 4.1.2 the commit it records carried the PRD's key in its subject
too (§3), so neither the block nor its commit subject says which unit the work was for. The
operator identifies it by what the commit changed: `git show <commit>` in the repository the entry
names, read against the Epic's own `specification.md`. **A block that cannot be attributed that way
stays where it is and stays the PRD folder's** — a block moved on a guess attributes work to an
Epic that did not get it, and every Epic-level reader then reports it as that Epic's.

**Branch for convenience, commit for durability.** A merged branch is usually deleted, so the record
names the commit as well — the one commit `/implement` Phase 4.6 made for the run. After a merge
commit or a fast-forward that commit is reachable from the base; after a squash or a rebase merge the
base holds a copy of the change rather than the commit, so once the branch is deleted no branch
reaches it and it survives only while a clone still holds it — which is why `diff-summarizer` falls
back to a key-commit search there, where its caller supplies keys — `/document` does; `/release-notes`
does not, and there the element comes back unread. `diff-summarizer` accepts the branch or the commit, and recording
both is what makes the file survive branch cleanup; how it reads a commit that has already landed on
the base is that agent's own rule.

**`pushed:` is recorded, not assumed.** A later run reading `pushed: false` says *"this was never
pushed"* rather than reporting an empty diff against a ref the remote does not have.

## 2. What it does not hold

**No summary of what was implemented.** A summary is a *description*, and `references/source-truth.md`
exists because descriptions drift from the code they describe — one here would be a new, unverified
description sitting in a folder of grounded artifacts, with nothing to check it against.

A ref cannot drift. Git resolves it or it does not, and either answer is true.

**Two limits, and the second is narrower than it used to be:**

- **`/implement` in direct mode writes nothing** — no address, no folder, nothing to append to. A
  directly-implemented change has no block, exactly as before.
- **This file records only what the plugin did.** Work done by hand or by another tool leaves no
  block — which is why it is not the only source. §3's convention and the scan that reads it recover
  that work, and §4 says how the two are combined.

## 3. The commit convention — and who actually writes it

**The key goes where a human will see it and copy it.** Who writes it is narrower than it first
appears, and the difference matters:

| Command | What it does with the code | What it does about the convention |
|---|---|---|
| `/implement` | branches, then commits and pushes through `dev-workflows:code-handoff`'s `finish-code-branch` (Phase 4.6) | **writes the subject itself** |
| `/upgrade` | branches, commits each component in step 6.5, pushes once in step 7.5 | **writes the subject itself** |
| `/vuln` | `vuln-fixer` branches and applies the fix; the orchestrator commits and pushes in Step 3.9, using its own template | **writes the subject itself**, from the template in `/vuln`'s Git Workflow |

**All three write it, and the history is worth keeping** because it explains why the convention is
also *documented* rather than merely emitted. Until `code-handoff.md` existed, `/implement` and
`/upgrade` left the working tree dirty and could only ask the operator to name the key — strictly
weaker than doing it, and a command that does not commit cannot write a commit subject. That is no
longer any command's situation: the commit is prompt-free (`code-handoff.md` §1 rule 5), so a run
ends uncommitted only by choice — it typed `--no-commit` — or where no commit could be made — for example a failed
gate or a hook rejection (`code-handoff.md` §2.1 and §2.3 respectively, each reported on a
`NOT committed` line, §3.1). The convention still needs to be
written down, because the people whose commits the §4 scan has to find are mostly not running the
plugin at all — which is what `docs/reference/commit-convention.md` is for.

- **The commit subject ends with `[<key>]`** — `feat(orders): add order intake [ACME-77-01]`.
  **The key is the unit's** — the Epic's wherever the run implemented an Epic, even one
  `/implement` chose under a PRD address, and otherwise the folder the address resolved: the folder
  §1 puts `/implement`'s block in, so a commit is found by the same key as the record beside it.
- **A `Work-Item: <workitem_key>` trailer**, when that unit's folder carries one
  (`references/prd-format.md`). Never invented; the trailer is simply absent when the field is.
- **The branch carries the key too** — `<prefix>/<key>-<slug>`, per `references/branch-naming.md`,
  the same unit's key. That is a recovery path for a **person** reading the log or the branch list,
  never for §4's scan: a key inside a branch name is followed by `-` and the slug, and §4 matches a
  token only as a whole key, so the scan never reads one there.

**In the subject rather than a trailer, and that is the whole point.** A trailer does not survive
`git log --oneline`, so it is invisible to the person deciding what their own commit should look
like — and people copy the shape of the commits already in the log. A convention stated only in a
trailer is a convention nobody sees.

**The convention is documented as a convention**, in `docs/`, not merely implied by what the plugin
emits: a contributor who has never run `/implement` still has to be able to write a commit the scan
can find.

## 4. Reading it — the two sources, and their boundaries

A consumer combines **this file's blocks** with a **scan of commit messages** for the identifiers
the run already holds:

```
git -C <repo> log --no-merges --extended-regexp --regexp-ignore-case \
    --grep='(^|[^A-Za-z0-9_-])<key>([^A-Za-z0-9_-]|$)' \
    --grep='(^|[^A-Za-z0-9_-])<workitem_key>([^A-Za-z0-9_-]|$)'
```

over the repositories this file names — or, when it names none, the repositories resolved from
`$REPOS_PATH` — with one `--grep` for each key and each `workitem_key` below; git lists a commit
that matches any of them anywhere in its message, its trailers included.

**The scan takes no merge commit (`--no-merges`).** A merge commit's range is the whole branch it
merged — work the blocks and the scan already reach commit by commit, which it would report a second
time — or, where the base was merged into a work branch, the base's own work, which is not this
key's at all. A forge writes a merged pull request's title, `[<key>]` included, into the merge
commit, so without the flag nearly every merge-commit landing would come back as unrecorded work.
Every commit the scan returns therefore has at most one parent — a root commit has none, and so does
a shallow clone's boundary commit, a merge there included, which shows no parents and is returned —
and a commit with a parent, or a true root read against the empty tree, has its own change as its
whole content; a shallow clone's boundary has none the clone can show.
**The cost:** work a merge commit's message carries alone — a hand-made branch whose own commits name
no key — is not found. The unanchored probe below is the one `git log` here that keeps merge
commits, since a branch name, or a whole key, inside a merge commit's message is what it looks for.

**A token matches only as a whole key.** Each `--grep` wraps its token in
`(^|[^A-Za-z0-9_-])` and `([^A-Za-z0-9_-]|$)`, every ERE metacharacter in the token
(`\ . [ ] ( ) { } * + ? ^ $ |`) escaped with a backslash, so the token neither follows nor is
followed by a letter, a digit, `_` or `-` — the characters a key is made of
(`references/addressing.md` §1). Unanchored, the scan over-matched: a PRD key `ACME-7` also matched
`[ACME-77]` and `[ACME-70-01]`, a `workitem_key` `PROJ-12` matched `PROJ-123`, and every such commit
reached `diff-summarizer` as this scope's unrecorded work. It is the rule `specs-repo-git.md` §3.5's
`branch-key` follows — a key the run holds, tested at a boundary, never one read out of the text —
with a stricter boundary: a branch name continues a key with `-` or `_` and a slug, so there those
two end a key, while here they belong to it.

**The one thing that legitimately continues a key in a commit message is a branch name inside it**,
and the boundary deliberately does not reach it. A merge commit's own subject is
`Merge branch 'feat/ACME-7-order-intake'`, built `<prefix>/<key>-<slug>` by
`references/branch-naming.md` §1.4, so the key there is followed by `-` — and admitting `-` or `_`
to reach it would admit `[ACME-70-01]` and `[ACME-7-01]` again, which is the over-match this
boundary exists to remove. A boundary aware enough to tell the two apart, admitting `-` only where
a digit does not follow, would still not reach the merge commit, which the scan does not take
(`--no-merges`, above). What it would add is a one-parent commit whose message names a branch — on a
forge that writes the branch into a squash commit (`Merged in <branch> (pull request #N)`), that
branch's whole landed work. It is not taken here because it changes the one boundary every reader of
this file shares, which is its own change to make; until then the probe below reports such a commit
on a repository the scan left at zero matches.

**What that costs:** the scan finds no commit of a branch whose own messages name no key: its
merge commit is not scanned (above), and where the subject the forge wrote for it names the key only
inside the branch name, this boundary would not reach it even if it were. **Population: every `/document` scan,
and every `/release-notes` scan with diff grounding on, over a repository where a key's work is
carried by a branch name alone — from `workflows-core` 1.7.1, since the unanchored grep it replaces
did match inside a branch name, and matched every longer key with it — and, from `workflows-core`
1.10.0, over one where it is carried by a merge commit's message alone, the `--no-merges` cost
above.**

**The recovery is a report, not a read: where the whole-key scan matches nothing in a repository,
run one unanchored probe over it.** Repeat that repository's `git log` with **its tokens bare** and without `--no-merges` —
the same token set the scan used there, one `--grep` each, every ERE metacharacter in each still
escaped exactly as above, but with neither `(^|[^A-Za-z0-9_-])` nor `([^A-Za-z0-9_-]|$)` around
them — and print each commit it matched by **its SHA, date and subject**, as *"may name this key
inside a branch name or in a merge commit — inspect by hand"*. The escaping is not optional here: a `workitem_key`
carrying a `.` matches any character without it, which is a wider probe than the one this exists to
recover from. **Nothing is read.** Not one of those commits is handed to `diff-summarizer`, none
enters the run's read set, and none enters a drop set, so the probe owes no boundary rule of its
own and leaves nothing behind for a later run: the operator is told where to look, and the run's
own sources are exactly what they were.

**The probe is also where the `--no-merges` cost shows**: on a repository the scan left at zero matches, a merge
commit whose message names the key whole, which the scan skips, comes back here, and so does one
naming it inside a branch name. Where the scan matched anything, the probe does not run, and work
only a merge commit's message carries shows nowhere.

**The trigger is per repository, and stays there.** It fires **only** on a repository the whole-key
scan left at zero matches — the one state in which the loss above is indistinguishable from a
repository holding no work for this run's tokens at all. Where that scan matched something in a
repository, the probe would add over-matches **beside** anything it recovered: a repository holding
both `[ACME-7]` and `Merge branch 'feat/ACME-7-hotfix'` returns the merge commit — the genuine case
the loss names — and any `[ACME-77]` or `[ACME-70-01]` the repository holds with it, in a
repository whose work the scan has already reported. So the trade is signal-to-noise, not
correctness, and it is only worth taking where the scan reported nothing at all. Scoping the
trigger per **token** instead would fire wherever any one token matched nothing, which on a PRD
with many Epics is most of them, and take that noise in a repository the scan has already reported
on the strength of the tokens that did match.

**Making the scan itself match a branch form was considered and refused**: a repository's
own documented convention wins over `references/branch-naming.md` §1.4's shape
(`references/branch-naming.md` §1.1), so there is no branch form to derive; the loss lives mostly in
branches people named by hand, which no derived form matches; and where a derived form *would*
match, those commits already carry their key and the scan already has them.

**The keys are those of the records the read takes, so its scope decides them.** An Epic-level read
greps that Epic's key and its `workitem_key`. A PRD-level read, which takes the PRD folder's record
and every Epic's under it (§1), greps the PRD folder's key and every `EPIC-` folder's, each with its
`workitem_key`. **The per-Epic greps are what find an Epic's commits at PRD level**: matched whole,
the PRD's key no longer reaches the Epic keys `/epics` mints by extending it (`<PRD-KEY>-NN`), and
it never reached an Epic's `workitem_key`, or an Epic key that does not extend the PRD's.

**This is a search for tokens the run already holds, never an extraction.** Each key is read off
its folder's carrier (`references/addressing.md` §4) — an Epic's off the `EPIC-` folder the run
listed under the PRD folder — and each `workitem_key` off the same folder. Nothing parses an
identifier out of a commit message, which is the rule `CLAUDE.md` states and the difference between
resolving and guessing.

**Merged and deduped by SHA.** A ref two records name — the same repository and the same commit, as
where an operator copied a block into its Epic's record rather than moving it (§1) — is one ref,
counted once by a read that takes both. **Every comparison against a block's `commit:` resolves it
first.** §1's template writes that field abbreviated — seven characters in its example — so testing
it against a `git log` SHA by equality matches nothing, and every recorded commit then comes back
from the scan as unrecorded work on a run whose record is complete. Resolve each block's `commit:`
in its own repository (`git rev-parse`) and compare the resolved values, never the values as
written; `docs-workflows:release-note-types` §1 fixes the 12-character form a read set is written
and compared in, which is that comparison's own case. What the scan finds beyond the recorded
blocks is reported as **unrecorded work**, named as such with its commits listed — a run that
quietly folds hand-made commits into the recorded set makes the record look more complete than it
is.

**The two consumers take different boundaries, and the difference is not stylistic:**

- **`/document` reads every block under its scope** — the PRD's, which is the PRD folder's record
  and every Epic's under it, or, on an Epic address, that Epic's (§1). It documents the feature as
  it now stands, so every change that reached it is in scope, and no note bounds its scan: every
  block in its scope is read, so merging by SHA already keeps each recorded commit out of the
  unrecorded work.
- **`/release-notes` reads only what no earlier note covering it read.** A second release must not
  re-describe the first one's work, and with no imported release field the notes already in
  `release-notes.md` are the only honest boundary. Each records its scope and every commit its run
  read (`docs-workflows:release-note-types` §1, which fixes the form): a note for the PRD covers
  every record under it, and a note for an Epic that Epic's record alone, so a note drafted for one
  Epic moves no other Epic's boundary. **A note's boundary is the set of commits it read, never a
  date**, because a date cannot say whether a note saw a commit: a branch committed before a note
  and merged after it is dated inside the span the note covers, and no note read it. So for each
  record the run reads — by the same scope as `/document` — it takes every block that records a
  commit no earlier note covering that record read, that record's own notes and the PRD's; a block
  is skipped only where every commit it records is in such a note's read set. **That test is
  block-granular while the scan below is commit-granular, so a partly-covered block is read
  whole**: where a note covered every commit a block records but one, the block is taken, the
  covered ref goes to `diff-summarizer` again and a change the earlier note already described is
  summarised a second time — so this bullet's opening *reads only what no earlier note covering it
  read* holds per block, not per commit. It is chosen rather than inherited: a block is one
  `/implement` run's refs, and handing the writer a run with a hole in it is the worse failure.
  **Population: every `/release-notes` run with diff grounding on over a note that covered a block
  only partly** — a block appended before `dev-workflows` 4.7.0, when one run could record several repositories, naming two where the earlier run resolved one and not the
  other, or where one dispatch failed, since a commit that run could not read is no part of its
  read set (`docs-workflows:release-note-types` §1). **The run names the blocks it used**, which
  makes a wrong boundary visible rather than silent, but it names such a block as it names any
  other.

  **The scan takes the same boundary**, or every commit a covered block records, and every
  hand-made commit an earlier note already described, comes back from the scan as unrecorded work
  on every later run. It drops every commit whose SHA a block in the records the read takes names
  — covered or not, since an uncovered block's commits are read from the block — and every commit
  in the read set of an earlier note covering a record whose token it matched: the PRD folder's
  record for the PRD's key or `workitem_key`, an Epic's for that Epic's. It drops nothing else,
  save what the one fallback below drops. So **a commit is skipped only where an earlier note
  covering it read it — or, under that fallback alone, where its date, or the heading date of a
  block recording it, puts it behind a note whose read set is unrecorded, which the run then
  lists, the commit itself or the block that accounts for it** — and outside that fallback a
  commit no note read comes back however it is dated. **The block's date is a second route and not
  a restatement of the first**: the first of the two drops above — the SHA drop — takes a commit
  whose SHA a block names whether or not that block was read, so a block the fallback date-skipped
  still takes its commits out of the scan, and a rebase or a cherry-pick that dates a commit
  *after* its own block's heading puts it behind the note by that heading alone.

  **The one fallback is an earlier note that records no read set** — a draft carrying no scope
  line at all, which is every draft appended before `docs-workflows` 1.2.2, and one carrying the
  one-line `<!-- release-note scope: <KEY> <YYYY-MM-DD> -->` form that release replaced before it
  shipped. It still bounds by date, as notes did before: a block or a commit dated before the
  latest such note covering its record is dropped, and one dated on that note's day or later is
  read; a commit matching several records' tokens is dropped by date only where every one of them
  drops it. A block is dated by its heading, and a commit by its committer date as `git log
  --date=short-local --format=%cd` prints it — in the zone of the machine running the scan, so
  that at least every date git supplies is read in one zone, where `--date=short` prints each
  committer's own and moves a late-evening commit onto the wrong day. **A block heading and a
  scope line are taken as written and are not converted**: each was written in the zone of
  whatever machine ran that command, so a block a run in another zone appended, and a note written
  on another machine, can each sit a day off the zone this scan reads its commit dates in. One
  zone for git's dates is what this buys, and not one zone for the whole comparison. **This
  fallback can drop what no note described**: a commit merged after such a note but dated before
  it, a block that reached the specs checkout after it, a commit whose own date clears the note
  while the heading of a block recording it does not, and a commit or a block within a day of the
  boundary wherever the writer of either worked in another zone. **Population: every
  `/release-notes` run with diff grounding on over a `release-notes.md` an earlier release wrote,
  and none of the notes written from `docs-workflows` 1.2.2
  on, since a note that records its read set never reaches this rule.** So the run lists, beside the
  ones it used, **every block the date rule dropped — by its record and heading date — and every
  commit that rule dropped by that commit's own date, by SHA, date and subject.** A commit dropped
  **with a block recording it** is not written out again: **that block's listing accounts for it**,
  the listing naming the record and the heading date and the block itself naming its commits. So
  nothing is dropped silently, though a block's listing does not say which of its commits cleared
  the note — a rebased commit dated after that heading is found by comparing the two dates by hand,
  which is what the listing gives the operator the material for.

**What is honestly still lost, and what a run therefore says out loud:** only a non-merge commit whose
message names the key is findable, no convention compels a human to follow one, and so **the run reports how
many commits it scanned — the non-merge commits it walked, `git -C <repo> rev-list --no-merges
--count HEAD` — and how many matched**. A zero-match scan in a repository that has commits is
a signal about the convention, not proof that no work happened.

# Session hygiene (embedded — shared reference)

<!-- reference-parts
part core always
part resume-pointer
part guidance
alias resume-pointer "§1" "Location" "Skipped"
alias guidance "§2" "§3" "§4" "§5"
-->

<!-- part: core -->
The plugin-wide contract for **session-hygiene suggestions**: after a big command
finishes, the pipeline first **flushes resume-critical state to disk**, then **suggests
the right context action** (`/compact` or `/clear`) plus a session **`/rename`** aid.
Cited by the pipeline commands and by `next-phase-offer.md` / `context-management.md`,
so the contract lives in ONE place (the same shape as `next-phase-offer` and the
`emit-block` invariant).

Everything here is **guidance-only** — the plugin NEVER auto-invokes `/compact`,
`/clear`, or `/rename`. The goal is to stop relying on a human to keep asking "prepare
for a compact/clear": the pipeline does the prep and prompts the choice itself.
<!-- /part -->

<!-- part: resume-pointer -->
## 1. Prepare-checkpoint (runs FIRST — unconditional for PRD-scoped runs, save one carrying `specs_git: misrooted`)

At command finalization — AFTER the deliverable artifact is saved/committed, AFTER
`emit-cost` / feedback / follow-up, and BEFORE the terminal `commit-artifacts` step
(`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` §4) — a PRD-scoped run
writes/overwrites a **resume pointer**. It runs regardless of which suggestion (or none)
fires: **prepare always, suggest adaptively.**

**The write is its own terminal step — not part of the printed suggestion, and not part
of `emit-cost`.** The `### Context hygiene` block in a command's report carries the
`/compact` | `/clear` | `/rename` guidance only. The pointer is written by a **discrete
step that runs after the cost phase's `emit-cost` call has returned and before
`commit-artifacts`** — placed at the end of the command's terminal cost phase, but never
folded into `emit-cost`'s own procedure. `cost-emission.md` owns that procedure and
writes no resume pointer; giving it one would split ownership of `resume.md` across two
references. The order is three separate steps, as §5 rule 2 states: **cost →
`resume.md` → `commit-artifacts`**.

Binding the write to the printed block instead would break it twice over: several
commands compose their Final Report *before* their follow-up and cost phases run, so the
write would land before the cost entry it is supposed to follow, and it would stay
uncommitted, since `commit-artifacts` runs after cost. Prepare-first (§5 rule 2) is still satisfied:
the write happens before the run ends, and therefore before the user can act on the
printed suggestion.

**Not written on a run that carries `specs_git: misrooted`** (`specs-repo-git.md` §3.1): `$SPECS_PATH` is misplaced, so the pointer would land where the next run, with the variable corrected, never looks.

**Skipped**: `/idea` (its brief is the anchor, and it is written and handed off in the same run), `/implement`
**direct** mode, `/document` **doc-edit** mode (Mode B), `/vuln`, `/upgrade`, `/frames`. There the
durable state is the artifact / branch / PR already on disk; no resume pointer is written.

**Three reasons sit in that list, and only one of them is "no PRD anchor".** `/implement` direct mode
and `/document` Mode B have no PRD directory to write into. `/vuln` and `/upgrade` are non-pipeline
runs whose durable state is the branch or PR already on disk, which is the reason §3 gives for them —
not a missing directory, since a keyed run of either resolves a folder and writes into it. `/idea` and
`/frames` do resolve one — but neither is a pipeline *phase* that a later run resumes: `/idea` hands its brief off in the
same run, and `/frames` rebuilds an index, which is a repair rather than a step with a next one. A
pointer to a phase nobody resumes is a file that only goes stale, so state the exemption in the
command rather than writing one.

**Location** (mirror `followup-emission.md` §2 resolution):

1. `$SPECS_PATH` resolvable + writable + the PRD dir exists → `<PRD-dir>/dev-workflows/resume.md`. *[primary]*
2. `$SPECS_PATH` writable but no PRD dir matched → skip the file; rely on the printed `### Next step`.
3. `$SPECS_PATH` not writable → skip the file; the suggestion still fires with a one-line
   `⚠ could not persist a resume pointer — set $SPECS_PATH`.

`resume.md` is a **"last known position" pointer, OVERWRITTEN each run** (NOT an append
log). It is intentionally tiny — one line per item, and an item leaves it once it is settled:

```markdown
# Resume — <KEY>[ / <EPIC-KEY>] (<role>)

- **Last completed:** <command> <args> — <phase or 'command complete'> (<ISO datetime>)
- **Artifact:** <relative path to the deliverable just written/committed, or 'none (read-only)'>
- **Next step:** <the exact next command from ### Next step, or 'PRD fully processed'>
- **Suggested session name:** <KEY>-<slug>-<role>   (omit this line on a run whose own `### Context hygiene` block carries no `/rename` suggestion — that block is this command's own, so the test is decidable from the command being executed and needs no list to look up; §4 names which commands carry the line and why the rest do not)
- **Carry-forward decisions:** <0–N one-line items: the decisions the next phase needs that are NOT already in the artifact, and every item the pointer being overwritten carried that is not settled, by the one test *Read the pointer you overwrite first* gives — each of its carry-forward items, and each open item of its Next step that this run's Next step does not name; 'none' if none>
```

**Read the pointer you overwrite first.** It is the one `resume.md` its folder holds, written by
every run of every Epic and every role under that folder, so an item it carries may be another
Epic's or another lane's — a pending refine, a PRD update, a re-run, a push, a merge order — that
the next phase of this run's own lane never needs. The overwrite replaces the position, never an
open item: each item the old pointer carried — each of its carry-forward items, and each open item
of its *Next step* that this run's *Next step* does not name — goes into the new *Carry-forward
decisions* line, one line each, unless it is settled. **An item is settled where this run settled
it, or where the check for what the item waits on shows it settled** — each check a read that
fetches nothing and writes nothing, each settling only the kind of item named beside it; an item
that names several branches, commands, questions or paths is settled only once that check shows
every one of them settled:
- **an item that waits on a merge** — of a branch, or of the pull request it names — by the merged
  check alone, never by a push. In the specs repository, `specs-repo-git.md` §3.5's
  `branch-merged` answers merged for the ref `phase-handoff.md` §2.2 rule 3 resolves —
  `refs/remotes/origin/<name>` where it exists, else `refs/heads/<name>` — or this run's
  preflight found that branch merged (§3.5 B2), as the block it printed says, or, in a command
  that keeps its run state in a file, as that file records. In a code repository, the branch's
  tip is an ancestor of the default branch's tip in the refs the run holds, or
  `workflows-core:implementation-format` §5's merged test, where the run applied it to that
  branch, shows it merged;
- **an item that asks for a push** — its `origin/<branch>` ref holds the local branch's tip;
- **an item that asks for a follow-up to be done** — its line is ticked in its `follow-ups.md`;
- **an item that asks for a command to run** — the record that command writes in the folder the
  item names (an `implementation.md` block, a `_conformance.md` or `_security.md` entry, the
  deliverable itself) is later than the old pointer's *Last completed* datetime, by the datetime
  it records, or, where it records a day alone or no date, by the specs repository's last commit
  touching it;
- **a decision or a fact it states, or an open question** — recorded, the question with its
  answer, in a deliverable the next phase reads at the top level of the folder it belongs to:
  `prd.md`, `ard.md`, `epic.md`, `specification.md`, `design.md`, a `decisions.md` register or a
  `_*.md` record, never `resume.md` itself or a session file under `dev-workflows/`. This is the
  template's *NOT already in the artifact* test, applied to each of those deliverables rather than
  to this run's own artifact alone;
- **a path it names** — the path no longer exists.

A settled item is dropped. The run that settled an item may keep one line saying so instead, and
the next run drops that line: a line saying its item is settled is settled. An item not settled —
by this run or by the check for what it waits on — is carried, without the run having to show it
still open; one a file the next run reads already records — `follow-ups.md`, say — is carried as
one line naming that file. An item that waits on a pull request names that pull request's branch
and its repository, so a later run can make the merged check. These stay longer than they need:
a code repository's branch merged by a squash or a rebase, until a run applies
`workflows-core:implementation-format` §5's merged test to it — a run of the Epic the branch
belongs to, or `/dev-workflows:conformance <PRD>`; a branch in a repository the run holds no ref
for, or only refs older than the merge — a code repository the run did not open or did not fetch,
or a branch never fetched here — until a run holding current refs settles it; a specs-repository branch with neither its local nor its `origin/`
ref left — deleted by an earlier run's preflight that wrote no pointer here, then pruned — which,
without a fetch, cannot be told from a branch never fetched here, so it stays carried; and an item
an older pointer wrote naming a pull request by its number alone, until a run settles it. Where
no pointer stands yet, there is nothing to carry.

**Redact before writing.** The `Carry-forward decisions` line may summarize
content pulled from a PRD or the session — redact any secret,
credential, token, or PII. A resume pointer records *what to do next*, never a
sensitive value.
<!-- /part -->

<!-- part: guidance -->
## 2. The suggestion — role-aware (reads next-phase-offer's role labels)

`next-phase-offer.md` already role-labels every next option (PM / PA / PE / Dev / Security Engineer). For
each next option the offer names, compare its role to the just-finished command's role:

- **Same role** (e.g. `/design E1 → /design E2`, Dev→Dev) → suggest **`/compact`** —
  context still relevant, keep the thread.
- **Different role** (e.g. `/epics` PE → `/design` Dev) → suggest **`/clear`** as the
  better choice when one person keeps wearing both hats (the prior role's reasoning is
  now noise). `/compact` still works if continuing right away; a genuinely different
  person just starts fresh and re-reads disk.
- Next options **span both** (e.g. `/create-prd` → PM `/release-notes` OR hand to PA/PE) →
  present **both branches**: "continuing as PM → `/compact`; handing off (even to
  yourself) → `/clear`."
- **User is done / ending the session** → suggest nothing.

Do NOT hardcode a per-command compact/clear verdict — read the role labels the command's
own `next-phase-offer` output already carries. The role graph is owned by
`next-phase-offer.md`; it is not duplicated here.

## 3. Mid-run suggestions & non-pipeline big commands

- **`/implement` suggests no `/compact` mid-run.** Its step groups are dispatched back to
  back, with no user turn between them to act on a suggestion, and its run-state file
  carries the run across an automatic compaction; a step list past one run's reach is
  decomposed into a unit of its own (`context-management.md`'s *Decompose*).
- **`/vuln`, `/upgrade`** (big, non-pipeline, no role transition) → a plain end-of-run
  **`/compact`** suggestion only; no `resume.md` (durable state is the branch/PR).

## 4. Session-name aid

**A command prints the aid where its own `### Context hygiene` block carries the line — that block,
not any argument shape, is what settles it.** Read off those blocks, the set is the PA/PE/Dev ladder —
`/create-ard`, `/epics`, `/specify`, `/design`, `/ready`, `/implement`, `/document`,
`/release-notes` — plus the two PM effort-proposal commands, `/prd-proposal` and `/brd-proposal`.
For those, print a suggested `/rename <KEY>-<slug>-<role>` line so the user can relocate the session
in `claude --resume` later (e.g. after going home).
<!-- /part -->

<!-- part: core -->
`<KEY>` is the key that named the folder this run resolved — a PRD key on the PA/PE/Dev ladder, the
root BRD key for `/brd-proposal` — and `<role>` is the just-finished command's lane tag
(pm / pa / pe / dev).
<!-- /part -->

<!-- part: guidance -->
Guidance-only — a command cannot run `/rename` itself.

**Do not restate that set as "every command that takes a `<PRD>`".** Argument shape does not settle
it: `/implement`'s address is optional (absent → the run is **direct**) and `/document`'s Mode B
takes none at all, so the phrase is false of two of the commands named above — both of those modes
sit in §1's `**Skipped**` list and write no pointer, so the aid question never reaches them; and
`/brd-proposal` resolves a BRD container rather than a PRD, so the phrase excludes a command that
does print the line. The block a command carries is the whole of the test.

**`/idea` and `/create-prd` are excluded** from the rename aid, and the reason is the phase
rather than the key. It is **not** that a PM run has no key to name a session after: both
commands take a mandatory key as their first argument and refuse without one
(`IDEA_NEEDS_KEY`, `CREATE_PRD_NEEDS_KEY`), so the key naming the folder is in hand before
either writes anything. The exclusion stands because the PM ideation phase is short enough
that no label is worth auto-suggesting; the PM names the session manually if they want one.

**`/update-prd` and all six commands of the BRD-to-PRD route carry no `/rename` line either** —
`/brd-intake`, `/brd-split`, `/prd-ground`, `/brd-interview`, `/brd-package`, `/brd-reconcile`.
Each of the seven writes a resume pointer, so §1's omit-condition has to dispose of them, and it
does so off their own blocks rather than off this list. None of them states a reason of its own and
none is invented here; `/prd-ground` is the one that also runs off the route, on an idea-route PRD
folder, and carries no line there either.

## 5. Contract (5 rules)

1. **Guidance-only** — never auto-invokes `/compact`, `/clear`, or `/rename`.
2. **Prepare-first** — the disk flush (resume pointer) always happens before the run
   ends, so acting on the printed suggestion is safe. Prepare is unconditional
   (PRD-scoped), save on a run carrying `specs_git: misrooted` (§1); only the
   suggestion is adaptive. The canonical terminal order is:
   **deliverable + handoff → feedback → follow-ups → cost → `resume.md` →
   `commit-artifacts` → the run's last printed output**. What binds every
   command is the **emitter tail** — feedback → follow-ups → cost →
   `resume.md` → `commit-artifacts`. A command's deliverable-side finish may
   sit anywhere relative to the tail, including between its members, at
   whatever point suits it: `/document`'s conditional `Phase 8.5 — Finish &
   handoff` sits between feedback and follow-ups — it is the docs-repo git
   finish, while `emit-auto` writes into `$SPECS_PATH`, so the two touch
   different repositories and their relative order carries no consequence
   (`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` §4).
3. **Role-aware via a single graph** — the compact/clear split reads
   `next-phase-offer.md`'s role labels; the role graph is not duplicated here.
4. **Mode-aware** — direct / doc-edit / non-pipeline / pre-PRD runs → no
   `resume.md`, no `/rename`, and the suggestion degrades to a plain optional `/compact`
   note (or is omitted, consistent with `next-phase-offer`'s mode-aware omission).
   **Three reasons sit in that set and only one of them is "no PRD anchor"**, exactly as §1
   separates them: `/implement` direct mode and `/document` Mode B have no PRD directory to
   write into; `/vuln` and `/upgrade` are non-pipeline runs whose durable state is the branch
   or PR already on disk (§3); and `/idea` and `/frames` do resolve one, and are exempt
   because neither is a phase a later run resumes.
5. **Never blocks** — a nudge appended to the Final Report, exactly like the next-phase offer.

## Surface

A short **`### Context hygiene`** block appended right after the `### Next step` section
at the END of the command's Final Report (guidance-only prose), plus one invariant citing
this reference. `/vuln` + `/upgrade` place the `/compact` line near their
`impl-maintenance` handoff. `/implement` places none mid-run (§3).
<!-- /part -->

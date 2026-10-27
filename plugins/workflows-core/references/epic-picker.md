# Progress-aware Epic picker — Shared Reference

How an **Epic-unit** command chooses which Epic to work on when it was given a PRD folder rather than
an Epic folder. Extracted from the retired tracker-input front-end, which owned it only because that
front-end happened to be where key classification lived; nothing about the pattern was ever
tracker-specific.

**Consumed for the Epic pick itself by** `/specify`, `/design` and `/implement`. **No PRD-level command
makes that pick**: `/epics`, `/document` and `/release-notes` operate on the PRD as a whole and must keep
working for a PRD with no Epics at all.

**A second, larger set consumes the *picker rules* without making that pick, and this file used to deny
it existed**: every command that builds a picker from a listing of its own — directories, waiting
files, or a PRD's Epics for some other purpose than choosing the unit to work on — and cites *The cap*,
some of them the auto-select-at-one and typed-answer rules too. Several resolve no PRD folder at all,
so *PRD-level commands never use it* was true of the Epic pick and false of the file. **This set is
described rather than listed**, because a list of its members went stale twice as members joined.
**Re-derive both sets** with `grep -rl epic-picker plugins/*/commands plugins/*/agents plugins/*/references`,
reading each hit for which of the two it is, if either: the paragraphs a change to the
`AskUserQuestion` arity constraint would touch — *The cap*, its remainder option's description, and
the rule resolving a typed answer against the items listed — are read by every member of either set,
not only by the three above.

## The picker

Given a resolved `PRD-` folder (`references/addressing.md` §3) and no Epic in the address:

1. **Enumerate the `EPIC-` folders directly under it.** A directory listing — the tree *is* the
   hierarchy, so there is nothing to read and nothing to import.
2. Branch on how many there are:

- **The address named an `EPIC-` folder** → no picker; proceed for that Epic.
- **Exactly one `EPIC-` folder** → no picker; auto-proceed for it, and emit a one-line notice saying
  which, so an auto-selection is never silent — save where the command's own policy asks instead:
  `/implement` puts that Epic and one broad PRD-level slice to the operator where the PRD folder
  also holds a flat `specification.md`, the broad slice `/design` designs as one unit (`/implement`
  Phase 0) — never on a multi-component PRD, where that file is a requirements source and no slice (`${CLAUDE_PLUGIN_ROOT}/references/components.md` §3); and `/specify`, on a multi-component PRD with no PRD-level `specification.md`, puts that Epic and the broad PRD-level spec to the operator, the spec recommended (`/specify` Phase 2).
- **Two or more** → render the picker, one row per Epic: its marker, its `key` (read from the
  folder's frontmatter per §4, never parsed from the directory name) and its title — **capped at four
  options, see *The cap* below**.
- **None** → the command's own no-Epics policy — typically: split with `/product-workflows:epics` first,
  or author one broad PRD-level artifact.

## The marker, and where it comes from

**Each command supplies its own done-predicate, and the predicate is always a file in the Epic
folder** — never a status somebody declared:

- **○ not started** — the command's output artifact is absent → selectable.
- **◐ in progress** — a resume file exists but the final artifact does not → selectable as a resume.
- **● done** — the artifact exists → shown greyed and not default-selectable; selecting it does what
  the command's own ● rule says — `/specify` rewrites the specification behind an archive, and stops on a
  published one. For `/implement` the artifact is a record — an `implementation.md` holding at least one
  block, never a file holding only its heading (`references/implementation-format.md` §1).

Default cursor on the first actionable row, in-progress before not-started.

## The cap

`AskUserQuestion` renders at most four options (`${CLAUDE_PLUGIN_ROOT}/references/escalation-rules.md`
§0), and this picker is built from a directory listing — so a PRD with five Epics overflows it, and a
`/specify` or `/implement` run that appends its own option overflows at four. A picker that is one
row per Epic is a picker that stops working on a perfectly ordinary PRD, which is why this is part
of the picker rather than advice beside it.

**Print every Epic as prose above the prompt** — marker, key and title, one line each, in the
ordering above — because a greyed ● row reads better there than in an option. **The picker does not
depend on that list being seen, though**: what guarantees that every Epic is named is the remainder
option's description, below, which the dialog shows whatever else the run prints. **Where the Epics
and the option the command adds, if any, fit in four, the array carries them all**, and the prose
list is still printed. **Otherwise the cap applies**: the array carries **at most three Epic rows plus
one remainder option**, fewer Epic rows where the command adds its own option (below). **The
remainder option is labelled `Another Epic (you'll be prompted for its key)`, and its `description`
names every Epic the array leaves out** — marker, key and title each, in the picker's order, after
`Not shown as an option:` — because `AskUserQuestion` renders each option's description under its
label, so an Epic the array leaves out reaches the user even where the prose list was never
printed. Five Epics, with no option added:

    Epics under PRD-ACME-77 orders:
      ◐ EPIC-ACME-77-02  order intake       (in progress)
      ○ EPIC-ACME-77-03  billing hand-off
      ○ EPIC-ACME-77-05  refund path
      ○ EPIC-ACME-77-04  tax rules
      ● EPIC-ACME-77-01  catalogue sync     (done — selecting it does what the command's ● rule says)

    choices: ["◐ EPIC-ACME-77-02 order intake (Recommended)", "○ EPIC-ACME-77-03 billing hand-off", "○ EPIC-ACME-77-05 refund path", "Another Epic (you'll be prompted for its key)"]
    description of the last option: "Not shown as an option: ○ EPIC-ACME-77-04 tax rules; ● EPIC-ACME-77-01 catalogue sync (done)"

Choosing the last option asks for the key in plain text, and a key typed straight into the
harness's free-text option is taken as given (`${CLAUDE_PLUGIN_ROOT}/references/escalation-rules.md`
§0, *A selection carries no text*); either way the run resolves the typed key **against the keys the
picker listed** — the array's rows and the remainder option's description — never by parsing one
out of the answer (`${CLAUDE_PLUGIN_ROOT}/references/addressing.md` §1).

**The description rule binds every picker built from a listing, not only this one** — every member
of the second set above. No option of such a picker points at "the list above": its remainder
option is labelled `Another <item> (you'll be prompted for <what it asks>)`, and its `description`
names every item the array leaves out, each as the prose list shows it and in the prose list's order, after
`Not shown as an option:`. A picker whose array carries no item at all, only dispositions — *all of
them*, *name the ones to include*, *none* — leaves every item out, so the option that asks for names
carries all of them in its description. A typed answer is resolved against the items the picker
listed, the description's included, never parsed out of the answer.

**The first actionable row carries `(Recommended)`**, whether or not the cap applied: the row the
default cursor lands on (*The marker, and where it comes from*), ◐ before ○, as the example's first
row does. A command's own rule recommends something else in two places, both questions of the
one-Epic branch above rather than rows of this picker: `/specify` recommends the broad PRD-level spec
over the one Epic of a multi-component PRD with no PRD-level `specification.md` (`/specify` Phase 2),
and `/implement` recommends neither the one Epic nor the broad PRD-level slice where the PRD folder
also holds a flat `specification.md` and the PRD is not multi-component (`/implement` Phase 0).
**Where every Epic row is ●, nothing is actionable and no option carries the marker**: say so in
prose beside the list (`${CLAUDE_PLUGIN_ROOT}/references/escalation-rules.md`,
*When no option is safe to recommend*).

**A command that adds its own option to this picker counts it against the four.** `/specify`
appends *"Author one broad PRD-level spec instead"* on every run — it is the command that authors
the spec, so nothing can condition it — so up to three Epics fit beside it, and with four or more
its array carries at most **two** Epic rows plus that option plus the remainder option. `/implement` appends *"Implement one broad PRD-level slice
instead"* **only where the PRD folder holds a flat `specification.md` and the PRD is not multi-component** (`${CLAUDE_PLUGIN_ROOT}/references/components.md` §3), the same condition its
one-Epic branch above carries, so, where the Epics and that option do not fit in four, its array carries at most **two** Epic rows where it appends that option and at most **three** where it does not, the freed row going back to the Epics. The added
option is never the one the **cap** drops: it is the alternative to picking any Epic at all, and a
picker that hides it to fit forces a choice the command means to leave open. `/implement`
withholding it is a different thing and not an exception to that — where no flat `specification.md`
stands the slice is a unit nothing specified, and on a multi-component PRD the flat file is a requirements source its Epics are built from rather than a unit, so in neither case is there a choice to leave open.

**Reading the artifact rather than a declared status is the point, not an accident of the rewrite.**
A status is a human's claim about the work and can lag it — which is why the version of this picker
that read one had to print the raw status text beside each row as a hedge. A file either exists or
does not.

**A command whose done-predicate artifact does not exist yet shows the markers it can support and
says which it cannot.** Claiming ● on a signal the tree cannot supply is worse than a shorter legend.
Every consumer can support all three today — `/specify` on `specification.md`, `/design` on
`design.md`, `/implement` on `implementation.md` — so this is a rule for the next command that adopts
the picker, not a live caveat.

## What the picker does not do

**One Epic per invocation, with no "next Epic?" loop where the command's own work is heavy.**
`/implement` is explicit about this — code-writing is branchy, so each run targets one Epic. A
lighter command may offer a next-Epic loop; that is the command's call, not this file's.

**It never picks silently.** Auto-selection at one Epic emits a notice; a greyed ● row is selectable
only deliberately; and "author one broad PRD-level artifact instead" is an explicit option wherever
the command offers it, rather than something inferred from an empty selection.

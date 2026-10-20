# Coverage ledger format (embedded authority)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

These shared references load by part — `escalation-rules`, `finding-triage`, `next-phase-offer` and `session-hygiene`. A citation of one names a rule: before applying it, load the part that holds it, `Skill(skill: "workflows-core:reference", args: "<name> <part>")`, the part its rule index names (`args: "<name> index"` loads the index; every part carries it), unless that part is already in this conversation. A citation that names no rule the index holds loads the whole reference, `args: "<name>"`. Never apply a rule of these references from memory.

The canonical shape of the **coverage ledger** (`coverage-ledger.md`): the row a BRD (business
requirements document) keeps per requirement, the states that row can carry, and the rule that
blocks a split until every row has one. Design authority:
`docs/superpowers/specs/2026-08-29-brd-to-prd-workflow-design.md` §4, §4.1 (removed from the tree 2026-09-23; `git show 62e791e8:docs/superpowers/specs/2026-08-29-brd-to-prd-workflow-design.md` retrieves it). Requirement and defect
identifiers (`[BR#n]`, `[DEF#n]`) are defined once in `references/brd-format.md` — cited here, not
restated; key grammar and folder resolution are defined once in `workflows-core:addressing`.

## 1. Purpose

The coverage ledger is **the only authoritative record of a requirement's fate.** Every other BRD
artifact — the inventory, the defect log, the grounding findings, the decisions — describes what a
requirement says or what is known about it; `/brd-split`'s `slices.md` does write down the fates its
run assigned, with a rationale for each, but as a narrative of that run that nothing gates on. Only
the ledger is read for what happened to it: built here, owned by another named BRD, deferred,
rejected, or superseded.

This matters most on the failure a long BRD invites: one BRD is split into several children, each
child looks at the same requirement, and each one — independently, reasonably — decides it is
somebody else's problem to build. No single child did anything wrong; nothing built the
requirement anyway, and nothing noticed, because nowhere recorded that every child had waved it
past. The ledger exists to make that failure visible: a row left `unallocated` (§3), or a set of
rows that resolve to nothing but `covered-by` pointing at each other's children, is a fact the
ledger states plainly rather than a gap that only a careful re-read of every child would surface.

**The ledger line is where that promise is kept.** A `covered-by` row records which BRD owns a
requirement, not that any BRD built it, so §6 resolves every one of them one hop through the named
BRD's own ledger before it counts anything — the named child on a source-owning BRD, the named
sibling or parent on a slice (§3): a requirement that BRD deferred, rejected or never allocated is
reported as exactly that, and the line names how many were delegated and then not built. Counting
`covered-by` as covered on its own word is what would let the failure above pass this file's own
arithmetic unremarked.

One ledger exists per BRD, at either level a `<BRD-KEY>` can name — a BRD that owns its source
document, or a slice one level inside it (`workflows-core:addressing` §6 caps nesting there). **What
its rows are is not the same at both levels**, and §3's creator table is the authority: a
source-owning BRD gets one row per `[BR#n]` in the inventory `/brd-intake` extracted, while a slice
gets one row per `[BR#n]` its `brd-link.md` claims **at the moment `/brd-split` creates it**. That
is a floor, not a ceiling: a slice's ledger can later hold a row `claims:` no longer names, and §2
says why. Only a slice has a `claims:` field — `/brd-split` writes it, and only into a child — so a
consumer that defines a BRD's requirement set over `claims:` at both levels reads an empty set on
every source-owning BRD, which is every parent.

## 2. Row shape

| Field | Meaning |
|---|---|
| `id` | `[BR#n]` — the requirement this row tracks, per `brd-format.md` §2 |
| `text` | the requirement, verbatim, or its first sentence plus a source anchor, same convention as the inventory row it mirrors |
| `disposition` | exactly one of the six values in §3 |
| `defects` | a `[DEF#n]` list — the defects (`brd-format.md` §3) raised against this requirement, empty when it carries none |
| `evidence` | a `[CG#n]` / `[DG#n]` list — the grounding findings that bear on this requirement, empty until grounding has run and written by the run that grounds it (below) |

**The file's layout is fixed**, its cells written by the one encoding every table file of the route
shares (`references/brd-format.md` §2.3):

````markdown
---
kind: coverage-ledger
key: <this ledger's BRD's key>
---

# Coverage ledger: <that key>

| id | text | disposition | defects | evidence |
|---|---|---|---|---|
| [BR#1] | The monthly report lists every invoice. | unallocated | [DEF#1] | |
| [BR#2] | Every monthly report must include these fields: … Invoice number | covered-by: EPIC-008-01 | [DEF#2] | |
````

`kind: coverage-ledger` names this document, not the folder: a kind outside `brd`, `prd` and `epic`,
so `workflows-core:addressing` §4 passes over it even at the folder's top level, where this file
sits, and never reads the folder's identity off it. The title line names the same key. The table
carries the five fields above as its five columns, in that order, one row per `[BR#n]` in id order —
`id` bracketed, `text` copied from the inventory row it mirrors as that cell stands, `disposition`
written exactly as §3 spells it (`covered-by: <BRD-KEY>`, `rejected: [DEF#n]`, …), and `defects`
and `evidence` as `brd-format.md` §2.3 writes a list. **A ledger holding no row** is its
frontmatter, its title and the table's header — what `/brd-intake` writes after an `EMPTY` read on a
first intake (`commands/brd-intake.md` Phase 3). A ledger written before this layout was fixed is
read as it stands (`brd-format.md` §2.3).

A row's `id` is permanent for the same reason its inventory counterpart is (`brd-format.md` §2):
once a ledger row exists for a `[BR#n]`, it is never deleted and never renumbered, even after the
row reaches a terminal disposition.

**`evidence` has exactly one writer of a value once the ledger exists, and it is `/prd-ground`.** The two creators in §3 write the column empty, because grounding has not run when a ledger is built — and so does `/brd-intake` re-run over a source-owning BRD, which rewrites an existing ledger whole (§3, and `commands/brd-intake.md` Phase 5) and empties the column along with every disposition, since the rows it writes are the ones grounding has not yet seen; `/prd-ground`'s Phase 8 then rebuilds it over **every** row of the ledger of the BRD it just ground, from the finding set that phase leaves on file — a row takes the id of every `[CG#n]`/`[DG#n]` whose `claim` names that row's `[BR#n]` (`workflows-core:grounding-format` §2), in id order, and a row no finding names keeps an empty cell. It is rebuilt in **every** mode of that command, `--no-code` included, since a run that writes only `[DG#n]` still produces findings the column would otherwise never index. **The column indexes; it never adjudicates.** The verdict, the evidence and the verifier outcome stay in the grounding file the id resolves to, so the two can disagree about nothing: the only datum here is which findings bear on which row, which is immutable once written — a finding's `claim` never changes its `[BR#n]`, and an id is assigned once and never renumbered (`workflows-core:grounding-format` §2). That is also why a finding marked `verdict: SUPERSEDED` stays listed rather than being filtered out: its id still resolves, its own block names what replaced it, and a column filtered by verdict would disagree with the file it is an index of. **Without this write the column is empty on every ledger forever**, and since both the ledger and the two grounding files ship in the customer bundle (`references/bundle-packaging.md` §1.1), a package hands the customer the one document that lists every requirement and cannot tell a checked one from an unchecked one, beside a grounding file showing which were checked. A live `/brd-package` run shipped exactly that, and its own adversarial reviewer raised it unprompted on both of its passes.

**On a slice, `claims:` may therefore name fewer rows than the ledger holds.** A row in that gap is called an **orphan row** throughout this file, and the term is defined by what the row *is* rather than by how it got there: a ledger row for a `[BR#n]` this slice no longer claims. **Three routes reach it, and all three are the parent's Phase 4 withdrawing a claim the slice had.** The first withdraws a claim that was never more than provisional — `/brd-split` Phase 3 writes a child's `claims:` list **provisionally** and seeds one `unallocated` ledger row per claimed `[BR#n]`, and Phase 4's walk on the **parent's** ledger is what actually allocates, so it may settle a provisionally-claimed `[BR#n]` somewhere other than that child — the walk of the run that keyed the slice, or of a later run where that one stopped before its Phase 4 Step 3 reconciled the slice, which that later run's Step 3 then does. The second withdraws a claim the slice had committed to and then recorded that it would not build: the re-cut of §3.2, where that same walk moves the row to a sibling. Either way the `claims:` entry and the copied `brd/brd-inventory.md` row are withdrawn together — a slice's inventory is defined over `claims:` (`brd-format.md` §2.1) — and **the ledger row stays**, because the rule above admits no exception and because deleting it would erase the one record that a claim was made and withdrawn. **The third keeps the slice's own decision on the row**: where the slice's own walk had already settled the row before the parent's allocation of it moved — which only a `/brd-intake` re-run over the parent does, resetting its every row for a new walk (§3) — and that new walk settles the row somewhere other than this slice, the parent's reconcile step withdraws the claim and leaves the row's disposition standing, since it never rewrites a disposition another run recorded (`commands/brd-split.md` Phase 4 Step 3). Such an orphan row can read any terminal disposition, `covered-here` and `deferred-to: <this slice>` included, and §6.1 counts it through the parent's current disposition rather than as it reads. Where the new walk gives the row back to this slice instead — which it may, because the slice still claims it (§3.2) — no claim is withdrawn and no orphan row arises. **On every route the orphan row bars the slice from that `[BR#n]` for good**: no walk of the parent offers a child a `[BR#n]` it holds an orphan row for (§3.2), so the requirement goes to another slice, a new one included, or takes a terminal disposition on the parent.

**An orphan row is never left `unallocated`**, and that guarantee is about the row, never about how many steps wrote it: on the first two routes the row goes straight from the disposition it held to the terminal disposition that walk settled (§3), and on the third it is never rewritten at all and keeps the terminal disposition the slice's own walk gave it, so it never blocks §4 and the slice can still complete its own split. **The step count is what differs between the first two routes.** On the provisional route the single step that withdraws the claim writes the disposition with it. On a re-cut (§3.2) the disposition is written first and the claim withdrawn after it (`commands/brd-split.md` Phase 4), so the row moves from `deferred-to: <this BRD>` to `covered-by: <the receiving sibling's key>` with no moment in between at which it reads `unallocated` — which is the whole of what §4 needs, and it holds identically on both of those routes. Its `text` and `defects` are the ones already copied into it, which is why it stays readable with no inventory row beside it; its `evidence` stays empty, because `/prd-ground` grounds a slice's *inventory* and an orphan row is not in one.

## 3. Dispositions

Exactly six. Only the last one blocks the gate in §4.

| Disposition | Meaning |
|---|---|
| `covered-here` | This folder builds it; a `PRD-` slice folder carrying one is therefore PRD-eligible (§5). Never written on a root: a container builds nothing itself |
| `covered-by: <BRD-KEY>` | A named BRD owns it. On a BRD that owns its source document the key is a **child**; on a slice it is a **sibling under the same parent, or that parent** — never a child, because none can exist below a slice (see below) |
| `deferred-to: <this BRD>` | Kept as a live obligation of this BRD, not built now |
| `rejected: [DEF#n]` · `rejected: <SLICE-KEY>/[CD#n]` | Not built, citing what justifies it: the `[DEF#n]` a rejection rests on, or the customer decision that withdrew the requirement. The second is written only by `commands/brd-reconcile.md`, onto its own slice's ledger, where a customer withdrew a requirement and no defect-log entry was written `withdrawn` for it — none still `open` was raised on it — qualified by that slice's key, as a `resolved-by` value is (`references/brd-format.md` §4), because the row is also read from other folders: one hop from its parent's line (§6.1) and from a sibling's interview |
| `superseded-by: [BR#n]` | Replaced by another requirement, named by its `[BR#n]` |
| `unallocated` | The initial state; the only one of the six that blocks §4 |

**`unallocated` is the state every row is written in when its ledger is first built** — no row
starts in any other disposition.

**`rejected` has two spellings and one meaning**: nobody builds the requirement, and the ledger
line counts both as `rejected` (§6). What tells a customer's withdrawal apart from a rejection the
delivery side made is the citation, never the disposition. `rejected: <SLICE-KEY>/[CD#n]` is always
the customer's; `rejected: [DEF#n]` is the customer's where the defect log resolves that entry
`withdrawn`, and otherwise the delivery side's, written by `/brd-split`'s walk. A reader that
parses a `rejected` row's value therefore accepts both spellings, and a slice resolves a
`[DEF#n]` one hop up (below) and a `[CD#n]` in the register of the slice the key names.

**Two commands create a ledger, one per level, and both seed every row `unallocated`:**

| Level | Creator | Rows |
|---|---|---|
| A BRD with a source document of its own | `/brd-intake` (`commands/brd-intake.md` Phase 5) | one per `[BR#n]` in the inventory it just extracted |
| A slice — nested in its parent's folder as a `PRD-` folder | `/brd-split` (`commands/brd-split.md` Phase 3) | one per `[BR#n]` the slice's `brd-link.md` claims |

`/brd-intake` never runs on a slice — a slice has no document to intake (`brd-format.md` §2.1) — so
if `/brd-split` did not write the slice's ledger at the moment it created the slice's folder,
nothing ever would, and the slice could never be ground in its own right: `/prd-ground` Phase 0
gates on that ledger. `/brd-split` is also the only command holding both the parent's rows and the
allocation that says which of them the slice claims.

**Two commands allocate or settle a row once the ledger exists, and they write different subsets.**
`/brd-split` walks every `unallocated` row to a terminal disposition (§4), and it is the only command
that may write `covered-here` or `covered-by`: allocation — which BRD builds a requirement — is that
walk and nothing else. `commands/brd-reconcile.md` moves a row to `deferred-to`, `rejected` or
`superseded-by` when a `decided` `[CD#n]` settles the requirement's fate differently; it never
allocates, because a customer decision is not a statement about which BRD in the delivery
organisation owns the work, and **no command moves a row back to `unallocated`, save one** — that is
the initial state, and returning a row to it reopens a gate that has already been satisfied. The one
exception is `/brd-intake` re-run over a source-owning BRD whose read finds a requirement: it
rewrites that BRD's ledger with every row `unallocated`, and only once the operator has consented to
exactly that (`commands/brd-intake.md` Phase 0 step 7, which names each disposition it discards). It
writes no slice's ledger, so no row of a slice's ever moves back.

**A slice's ledger is walked by `/brd-split` like any other.** The one-level cap stops that run
from creating children below the slice; it does not stop it from allocating the slice's own rows
(`commands/brd-split.md` Phase 0 step 5 — a notice, not a stop). Otherwise every row of every slice
would stay `unallocated` forever and no slice could ever satisfy §5, which is the same allocation
deadlock §1 exists to prevent, reached from the other direction. The same requirement therefore
carries a fate twice, at two levels, and the two say different things: `covered-by: <CHILD-KEY>` on
the parent's ledger records **which** BRD owns it, and the slice's own row records **what that BRD
decided to do with it**. A requirement whose claim a parent's walk withdrew carries it a third
time, on the slice that no longer claims it — an **orphan row** (§2), which records neither of
those but the fact that this slice claimed it and does not any more, naming the BRD that took it.

**`covered-by` is the one disposition whose meaning depends on level, and the only one with a
different writer at each.** On a BRD that owns its source document it names a **child** and is
written by that BRD's own Phase 4 walk. On a slice it names a **sibling under the same parent, or
that parent**, and is written by the **parent's** run — its Phase 4 walk, or its Phase 4.5 removal
repair, which re-points a row naming a removed child onto `<PARENT-KEY>` (§3.2) — never by the
slice's own. It is
never a child at either level below the root: nesting is capped at one level
(`workflows-core:addressing` §6), so **no child can exist below a slice** and no key a slice
writes could name one.

**The slice form exists for exactly one state — an orphan row (§2) — and for no other.** **What §3.2 adds is a second *route* to that one state, never a second state**, and the distinction is load-bearing: §2 defines an orphan row by what it *is*, a ledger row for a `[BR#n]` the slice no longer claims, so a re-cut row is one of those and not a third kind of row beside them. §5, §6.1 and §6.4 each turn on a slice's `covered-by` rows being **among** its orphan rows — rows it does not claim, once the parent's reconcile step has run — and §6.1 counts every orphan row, whatever it reads, through the parent's current disposition, which is what keeps each of them exhaustive now that an orphan row need not read `covered-by`. Both routes are written by the **parent's** walk in the same run that withdraws the slice's claim, and both land on the table below; §3.2 states what a re-cut additionally requires before that walk may move a row that already carries a fate. A slice's `covered-by` row is on either route a claim the parent's walk withdrew — still provisional on the first, committed by an earlier run and then deferred by the slice itself on the second — and the key it carries is whichever BRD that same walk allocated the requirement to:

| The parent's walk settled the withdrawn row | The withdrawn slice's orphan row reads |
|---|---|
| `covered-by: <SIBLING-KEY>` — another child builds it | `covered-by: <SIBLING-KEY>` |
| `covered-here` — the parent builds it | `covered-by: <PARENT-KEY>` |
| `deferred-to: <the parent>` — a live obligation of the parent | `covered-by: <PARENT-KEY>` |
| `rejected: [DEF#n]` | `rejected: [DEF#n]` |
| `superseded-by: [BR#n]` | `superseded-by: [BR#n]` |

The last two carry across unchanged because they say the same thing at either level. Each cites an
id that is the **parent's** — the `[DEF#n]` in the parent's defect log, the `[BR#n]` in the parent's
inventory — and a slice resolves both one hop up, exactly as it already resolves the `[DEF#n]` on a
row it claims (`brd-format.md` §2.1, §4). So the replacing `[BR#n]` on an orphan row need not be one
this slice claims or holds a row for; §6.3 excludes that row from this slice's counts either way and
says where a reader follows the obligation.

The first three all say *another BRD owns this*, which is what `covered-by` means and what none of
the other five can say: `deferred-to: <this BRD>` would falsely book it as the slice's own live obligation,
and `superseded-by` names a requirement, not a BRD. Both keys resolve: `resolve-address` finds a
sibling one level under `specifications/` and the parent at the top level
(`workflows-core:addressing` §3), so neither form names a folder that does not exist.

**This is not a general-purpose delegation, and a slice's own walk never writes it.** Every row a
slice's walk visits is a row that slice `claims:` — a row the parent's ledger allocated *here*.
Delegating one onward from inside the slice would contradict the parent's ledger about which BRD
owns it, and would point at a sibling whose own inventory holds no row for that `[BR#n]` at all. So
the slice form is confined to rows the parent withdrew, which the parent writes in the same walk that
withdraws them (`commands/brd-split.md` Phase 4) and which are therefore never `unallocated` when
the slice's walk runs. §4's disclaimer about the command owning its own interaction flow is
unchanged: which resolutions a picker offers stays `commands/brd-split.md`'s to state.

### 3.1 What `covered-by` means downstream — the row leaves this BRD's scope

**A `covered-by` row's requirement is not this BRD's to question, to decide, or to put to a
customer.** §3 says the named BRD *owns* it; ownership is the whole content of the disposition, and
a BRD that owns nothing about a requirement has nothing to ask about it. Every consumer that puts a
requirement to a customer or into an interview round therefore reads it over the rows this BRD is
answerable for — `covered-here`, `deferred-to`, `rejected` and `superseded-by` — and **never over a
`covered-by` row.** (`/brd-split`'s sibling re-cut does put a parent's `covered-by` row in front of
the operator, §3.2 — as an allocation to make, never as a question about the requirement.)

**Which consumers, and why each needs saying.** `commands/brd-interview.md` generates its round from
the findings and the inventory; `commands/brd-package.md` states the review's scope to the customer
from the ledger and the inventory. **The inventory is the wrong set at one of the two levels**, and
that asymmetry is the whole reason this section exists: a slice's inventory is exactly the rows it
claims (`references/brd-format.md` §2.1), so a slice is correctly scoped by reading it — while a
source-owning BRD's inventory holds **every** `[BR#n]`, including the ones its own walk delegated. A
consumer that reads the inventory alone is therefore right on a slice and wrong on a split parent,
which is the shape a defect hides in longest: it is invisible on the level most runs exercise.

**The failure it prevents is a customer asked the same question twice.** The parent raises a
question about a delegated `[BR#n]`; the child, ground and interviewed on its copied row for that
same id, raises it again; both reach a package, and the customer answers one requirement in two
reviews. `references/interview-tagging.md` §5 names that outcome for the within-a-BRD case — "asking
a customer the same question twice is not an inefficiency, it is an invitation to a different
answer, and two customer answers to one question is a contradiction the decision register has no way
to resolve" — and the cross-level case is the same failure, reached by a different route. It costs
two `[VD#n]` records in two registers that can disagree about one requirement with nothing linking
them.

**In scope as context, out of scope as subject.** A delegated row is not struck from the reader's
view: what this BRD keeps may genuinely turn on what it gave away, and a question about a
`covered-here` row may need to *cite* a delegated one to make sense. What the rule forbids is the
delegated row being the thing asked about. The test is whose answer would settle it — if it is the
BRD that owns the row, the question belongs to that BRD's own round.

**A source-owning BRD carries no `claims:` field, so this is read off the `disposition` column and
never off `claims:`** — the same trap `references/coverage-ledger-format.md` §5 and
`commands/create-prd.md`'s gate set already spell out. Intersecting with `claims:` here would read an
empty set on every source-owning BRD and put *nothing* in scope.

**On a slice, an orphan row (§2) is out of scope as a subject whatever it reads, and that one test
reads `claims:`.** An orphan row is the slice's record of a claim its parent's walk withdrew, and it
carries the fate that walk settled — `covered-by` another BRD, or, across unchanged, the parent's
`rejected: [DEF#n]` or `superseded-by: [BR#n]` (§3's orphan table) — so a `rejected` or
`superseded-by` orphan row reads exactly like a row the slice settled itself, and the disposition
column cannot tell the two apart. `claims:` can: it is the record that the claim was withdrawn. So a
consumer standing on a slice — `commands/brd-interview.md`'s question scope and
`commands/brd-package.md`'s review scope — takes the four dispositions above less every row whose
`[BR#n]` `claims:` no longer names, and reads `claims:` for that test and for nothing else; the
decision an orphan row records is the parent's, and a slice that put it to the customer would put a
question nobody on that slice is answerable for. A source-owning BRD holds no orphan row, so the
test never reaches the trap above.

**Deferring is itself an allocation.**
`deferred-to: <this BRD>` discharges the gate exactly as the other four terminal dispositions do;
the ledger's job is to record a requirement's fate, not to force every requirement to be built.

### 3.2 The re-cut — a sibling takes a row its owner deferred

**A row is re-cuttable only where two ledgers already agree that nobody is building it: the parent's row for a `[BR#n]` reads `covered-by: <A>`, and A's own row for that same `[BR#n]` reads `deferred-to: <A>`.** That pair is not a precondition attached to the design, it *is* the design. `deferred-to: <A>` is A stating in its own ledger that it is not building this, so the parent re-points against a refusal the row's owner wrote down, never over a live commitment — and that is the whole of what makes moving a row that already carries a fate honest. A row A still intends to build reads `covered-here` and is untouchable here; a row A never took does not read `covered-by: <A>` on the parent to begin with. **Both halves are read from the `disposition` column** — the parent's row and the child's — and never from `claims:`, never from an inventory. That is the trap §3.1 already names from the other side: a source-owning BRD carries no `claims:` field, and the folder a re-cut is made from is always one.

**Two rows decide the move, and the parent's is written first.** The parent's row takes `covered-by: <B-KEY>` for the receiving sibling B, and A's row takes `covered-by: <B-KEY>` in the same step; B's own ledger row for that `[BR#n]` is seeded `unallocated`, as every row of every ledger is when it is first written (§3), and B's walk takes it from there. **That is a claim about a row being written for the first time, so B must hold no row for that `[BR#n]` already, and a child that holds one is not a receiver for that row.** The exclusion is **per row**, never a property of the child: a child excluded for one `[BR#n]` remains a receiver for any other it holds no row for. **The reason is the invariant this whole section rests on.** **The parent's ordinary walk applies the same exclusion to orphan rows** (`commands/brd-split.md` Phase 4 Step 2's *Assign to a named slice*, and its Step 1 bulk set): a child holding a row for a `[BR#n]` its `claims:` does not name (§2) is not offered that `[BR#n]`, for the reason below. **A child that still claims the `[BR#n]` is offered it** — its own row reading `unallocated` from Phase 3's seed, or a terminal disposition its own walk wrote before a `/brd-intake` re-run reset the parent's row — because re-assigning a still-claimed row needs no new row: the parent's reconcile step finds the child in step for it and writes nothing, so neither of the two writes below arises. **The one still-claimed row it bars reads `covered-by`**: no slice's own walk writes that disposition, so a claimed row carrying it is a re-cut withdrawal interrupted between the donor's write and the parent's reconcile step, and re-assigning it would strand the requirement exactly as below; that reconcile step finishes the withdrawal instead, leaving the row as the second route's orphan row (§2). **Apart from those per-row bars, a whole child is barred where its inventory or its ledger is missing or unreadable**: `commands/brd-split.md` Phase 0 step 9 marks it unreconcilable and no walk of that run offers it a row, since that command's reconcile step writes nothing into it, so the claim a row adds could never gain the rows it needs. There is no new row to be born where one exists, so a receiver already holding the row leaves only two writes, and both are forbidden or dishonest: `unallocated` onto the row it has returns a terminal row to the initial state, which no command may do (§3); and leaving that row as it stands strands the requirement, because B would then `claims:` a `[BR#n]` whose own ledger row names somebody else, and B's own walk visits only `unallocated` rows, so that row could never reach `covered-here`. Every §4 gate in the tree reads satisfied and nobody builds the requirement — §1's named failure, reached from inside the mechanism that exists to prevent it — and two of this file's guarantees go false with it: §5's *`claims:` names none of them*, over a slice's `covered-by` rows, and §6.1's own bullet, which classifies such a row as malformed and counts it `unresolved` permanently. **The state is ordinary rather than exotic**: a child whose provisional claim on that same `[BR#n]` an earlier walk withdrew holds exactly one orphan row for it (§2) and stays standing on its other claims, which is the child an operator is most likely to name as the receiver. **Where the requirement is genuinely that child's to build, two routes already work**: `commands/brd-split.md` Phase 4.5's removal repair, which on removing an empty child re-points every row naming it onto the parent and returns the requirement to the parent's own live obligations, and a **new sibling**, which holds no row for anything and is eligible for every candidate by construction. Neither is a rewrite of a disposition, which is what keeps this edge inside the rule the rest of this section states. **The order is not a tidiness question, and the reason is recorded here because a later edit will otherwise swap the two writes as a clean-up.** Parent-first leaves an interrupted run with the parent pointing one hop at B — resolved `unallocated` by §6.1 where B's seeded row is readable, and `unresolved` by §6.2 otherwise, under whichever of that section's causes applies: for a **standing** receiver B's ledger is on the tree and readable but holds no row for that `[BR#n]` until the claim is reconciled, and for a receiver this run keys B's ledger may not be on the tree at all — and leaves A exactly as it stood: two accurate readings, neither of which hides a requirement. Child-first leaves the parent naming A while A names B, which is a **second hop** under a resolution §6.1 requires to terminate in one, and it falsifies §6.1's own argument for why one hop is exhaustive for as long as the run stays interrupted.

**Two rows decide the move; they are not always the only two rows that change, and the difference is §6.1's to enforce.** A `[BR#n]` can be named by `covered-by` on more than one ledger at a time: a child D whose provisional claim on that same row an earlier walk withdrew holds an orphan row `covered-by: <A>` for it (§2), so D names the donor too. Left as it stands, D's line resolves one hop onto A's row, meets a `covered-by` there, and is counted `unresolved` (§6.1) — a requirement D once claimed is then reported as unreadable rather than as owned by the BRD that now owns it. So every **other** ledger holding a `covered-by: <A>` row for that `[BR#n]` takes `covered-by: <B-KEY>` too. **That is not a further relaxation and moves nothing's ownership**: each such row is already an orphan row recording a claim withdrawn long ago, and re-pointing it re-states the same fact against the BRD that now holds the requirement. **Which ledgers are read, in what order, and how the sweep is reported are `commands/brd-split.md` Phase 4's**, which performs the identical read before removing an empty child; this file fixes only that no ledger is left naming the donor for a row the donor no longer holds. B is never in that sweep, because a child already holding a row for this `[BR#n]` is not its receiver (above).

**What A keeps.** A's `claims:` entry and its copied `brd/brd-inventory.md` row are withdrawn together, exactly as for any row a walk moves off `covered-by: <A>` — that is the withdrawal `commands/brd-split.md` Phase 4 Step 3 already performs, over a set that walk has to widen to reach this row. **The behaviour is existing; the input set was widened to reach it.** Step 3 visits two kinds of row: rows that were `unallocated` when Phase 0 read the ledger, and — on the re-cut path — the candidate rows Step 2R re-pointed, which were never `unallocated` that run; a re-cut row is therefore in its set (`commands/brd-split.md` Phase 4 Step 3), and the widening is the command's, not a new rule of this file's. What the withdrawal produces is what makes A's row an **orphan row** — the second of the two routes §2 names. **A's ledger row is never deleted** (§2). **A's grounding findings and its decision register are not touched.** A ground the row before deferring it, so a `[CG#n]` or `[DG#n]` in A's grounding files may cite a `[BR#n]` A no longer owns. Those findings cannot move — a finding's id is contiguous within its prefix and is assigned once — and they cannot be inherited either, because `workflows-core:grounding-format` §8 holds a finding carried in from an earlier run to be unverified by definition. So B re-derives against the same pins rather than inheriting, at the cost of one row's grounding. A's decisions stay, and stay true, for the same reason: a `[VD#n]` or a frozen `[CD#n]` taken about deferring this row records *A's refusal to build it*, which the re-cut does not disturb. What a run surfaces about those decisions is `commands/brd-split.md`'s to state; what this file fixes is that neither file is edited.

**The receiver has not been interviewed.** B is a sibling under the same parent — never a child of A, and never A itself — that holds no `decisions.md` carrying a `[VD#n]` or `[CD#n]` record and no `interview/round-*.md` on disk — a record `references/decision-register-format.md` §8 calls a torn write counting for nothing here, as it counts for nothing anywhere: it decided nothing, and no conversation was recorded as started. `references/decision-register-format.md` §4 admits exactly two causes for reopening a decision, a new grounding finding or an incoming customer decision, and adding scope to a slice is neither; a register that exists and holds decisions is therefore closed to this, and the two-part test is the cheapest honest reading of "the customer conversation about B has not started". **This eligibility test is the re-cut's alone.** It says nothing about which children an ordinary walk may write `covered-by` against, and widening it there is out of scope: that walk allocates rows carrying no fate yet, which is a different act from moving one that already carries a fate, and the eligibility test exists only to license the second.

**Where the receiver is later removed.** A child left standing while claiming nothing is resolved by removal or kept against a recorded reason (`commands/brd-split.md` Phase 4.5). Where the child removed is one a re-cut pointed at, the parent's row takes `deferred-to: <PARENT-KEY>` — which on the parent's own ledger is §3's `deferred-to: <this BRD>`, a live obligation of the parent, kept and not built now — and every other child whose ledger reads `covered-by: <that removed child>` for the same `[BR#n]`, A among them, takes `covered-by: <PARENT-KEY>`. **Neither is a new mapping.** Both are §3's own orphan-table row for a parent's deferral, quoted from that table rather than adapted: left column `deferred-to: <the parent>` — a live obligation of the parent — and right column `covered-by: <PARENT-KEY>`. The row goes **not** back to A, which recorded that it will not build it, and **not** to `unallocated`, which `/brd-split` never writes onto a row already carrying a fate (§3).

**What this does not relax, said because a reader will reach for each of them.** No row returns to `unallocated`, so §4's gate is never reopened: every write above replaces one terminal disposition with another. The one-level nesting cap (`workflows-core:addressing` §6) is untouched — a re-cut carves a **sibling**, never a child, so no `covered-by` key written here names a child of a slice, at either level. What relaxes is only the weaker rule that `/brd-split` never re-allocates a row already carrying a fate — apart from the key repair a removal performs (`commands/brd-split.md` Phase 4.5, *Where the receiver is later removed* above) — and it relaxes against the owner's own recorded refusal and against nothing else. **The consequential re-points above are not a second relaxation, and the test is whether a write changes who owns the requirement.** Two rows decide that — the parent's and the donor's — and both move only against the donor's written refusal. Every other row the same run rewrites is an **orphan row** (§2): a record that some BRD claimed this `[BR#n]` and does not any more, whose `covered-by` key names whichever BRD took it. Re-pointing one asserts nothing new about ownership; it re-states the same withdrawn claim against the BRD that now holds the requirement, which is the only reading of it that stays true. This file already writes exactly that under *Where the receiver is later removed* above, over the same set and by quoting the same table, and the removal repair shipped before the re-cut did.

## 4. The allocation gate

`/brd-split` cannot complete while any row in this BRD's ledger is `unallocated`.
It opens the gate by giving every remaining `unallocated` row a terminal disposition.
**The walk is one row at a time, and that is its default**; where one answer is uniform by
construction, the command may instead offer a single confirmation that settles a set of rows — an
offer it states in full and the operator may refuse row by row. **The paths available are
not the same set at both levels**, and the difference is no longer a disposition §3 withholds from
a slice: §3 makes `covered-by` legal at both. It is a difference of **writer and of row**. The slice form of
`covered-by` records an orphan row (§2) and is written by the *parent's* walk in the same run that
withdraws the claim, so it is already terminal before a slice's own walk ever reads the
ledger — a slice's walk never stands on a row it could write, and therefore never offers it.
**No number is written here**, for the same reason the paragraph below refuses to re-enumerate the
picker: a level-general count is wrong at one of the two levels the moment it is written, and a
level-specific pair drifts the next time either §3 or the picker changes. §3 is where a
disposition's meaning and its writer are decided;
`commands/brd-split.md` Phase 4 is where the paths a walk offers are decided — read each off the
file that owns it, and never take one as the count of the other. Re-running a **bare** `/brd-split` on a
BRD whose ledger is already fully allocated changes **no row of that BRD's own ledger** — save the key
repair a Phase 4.5 removal performs, where that ledger still names the standing empty child removed
(`commands/brd-split.md` Phase 4.5): no other row there moves, and the command still reports the
ledger line (§6). It can still write a **child's** ledger:
where a child's `claims:`, its inventory and this ledger's `covered-by: <that child>` rows disagree —
a carve stopped before it reconciled them — the run reconciles that child, seeding a new
`unallocated` row for a claim it adds and settling a withdrawn claim's still-`unallocated` row by §3's
table, and never writing `unallocated` over a terminal row (`commands/brd-split.md` Phase 4 Step 3). **An instructed re-run on that same ledger is a different run**, and
the difference is this file's to state because it is dispositions that move: `/brd-split <PARENT-KEY> "<what to peel off>"`
on a fully-allocated parent is the re-cut's invocation (§3.2), and a re-cut moves at least two rows — the parent's and the donor's, plus any orphan row on another child that named the donor for the same `[BR#n]`. The first sentence above holds
of the bare form and of nothing else. **Whether that makes the whole run a no-op is not
this file's to say, and it is no longer only about the ledger** — that command also resolves a child
left standing while claiming nothing, which no ledger records and which this file therefore cannot
see, and reconciles a child out of step with this ledger. Read the no-op test off `commands/brd-split.md` Phase 0, the same way the picker's shape is
read off its Phase 4; a run that "changes no disposition" and a run that "does nothing" stopped
being the same run once that resolution existed.

**The set of resolutions the command offers, how each one writes its row, and how a row ever
reaches `covered-here` are `/brd-split`'s own behavior** — see `commands/brd-split.md` Phase 4 —
**not this reference's.** This file fixes the disposition
vocabulary (§3) and the one rule every caller must honor: no row may stay `unallocated` past this
gate. It does not fix, and does not re-enumerate, the command's interaction flow — the picker's
shape is the command's to own, and a count of it recorded here would only drift the next time that
picker changes.

**How many rows one answer settles is part of that interaction flow, and it is the command's too.**
What this file fixes is the outcome: every row leaves this gate carrying one of §3's terminal
dispositions, written on that row, whatever interaction put it there. A bulk confirmation is the
same per-row write taken more than once behind one answer — it introduces no disposition and exempts no
row, so nothing in §3, §5 or §6 reads differently after one. **Which rows one may move is §3's question, never this
paragraph's**: an ordinary walk's bulk answer settles rows that were `unallocated`, and a re-cut's (§3.2) moves rows
that were already terminal, each under the rule §3 states for it. Taking the write more than once behind one answer
adds no authority to either. **The one-at-a-time walk is that phase's default, not this file's requirement**: the
requirement is that no row stays `unallocated` past the gate, and a run in which the operator
answered once for forty rows satisfies it exactly as one in which they answered forty times does.
Whether such an offer is made, on what condition, over which rows and with which dispositions in its
vocabulary is stated in `commands/brd-split.md` Phase 4 and read from there — a condition recorded
here would drift the next time that phase changed, exactly as a picker count would.

## 5. PRD eligibility

**A folder is PRD-eligible if and only if it is a `PRD-` slice folder *and* at least one of its
ledger rows for a `[BR#n]` its `brd-link.md` claims is `covered-here`** — §5.2's gate set, which
leaves out an orphan row whatever it reads (§2). Two tests, and the first one is about the **folder**, not about any
row.

**The level test is a check the consumer performs, and it comes first.** A BRD is a container and is
never the folder a PRD is authored in, so a consumer handed a `BRD-` folder refuses it **before
opening `coverage-ledger.md` at all** — on the resolved folder's prefix, never on what its rows say.
The check is: the `BRD-` prefix `workflows-core:addressing` §2 fixes, read off the resolved folder's
name — a prefix as that file's §4.1 defines one, the name beginning `BRD-<the resolved key>-`, so a
legacy folder keyed `BRD-12` is not a container by its name. A `PRD-` or an `EPIC-` prefix is not a
container and needs no further test; an **unprefixed** folder is answered by §5.1's positive test.

**Never the folder's asserted `kind:`.** `/brd-split` writes `kind: brd` into the `brd-link.md` it
places inside a `PRD-` slice folder, so a slice **asserts `brd` while being exactly the folder a PRD
belongs in**: a consumer gating on the asserted kind would refuse every slice and accept nothing.

**Stating it this way rather than as an inference from the walk is deliberate.** It was previously
argued that a parent cannot be eligible because `covered-here` "is not a resolution its walk is
offered" (`commands/brd-split.md` Phase 4). That is true, and it is the wrong load-bearing
sentence: it makes a structural rule depend on a picker's current shape, so a ledger written before
that picker changed — or edited by hand — reads as eligible at root and no consumer catches it. The
rule is structural. Eligibility is a property of the `PRD-` folder a split produces, which is the
folder the PRD is authored in; and since a split always produces at least one, the requirements
always have somewhere eligible to land.

**Why a container, rather than letting a BRD hold its own PRD.** A BRD that could be split *and* be
PRD-eligible itself would hold PRD folders and its own Epic folders as siblings — two kinds in one
namespace, which `workflows-core:addressing` §2's second invariant forbids, and which `/brd-split`
Phase 0 step 9's child enumeration would then have to tell apart. One slice always existing means the
requirements always land somewhere a PRD can be written, and that somewhere is always one level down.
This argument is stated **here**, in the authority the refusals cite, rather than only in the command
that carves the slices.

- **Eligible.** At least one `covered-here` row exists. The folder may go on to author its own
  `prd.md`, which is what `/create-prd` on the BRD route runs against it to write.
- **Not eligible.** No row is `covered-here`. Every row therefore resolves to one of the other four
  terminal dispositions — `covered-by: <BRD-KEY>`, `deferred-to: <this BRD>`, `rejected` (§3)
  or `superseded-by: [BR#n]` — in any mix, and **all four reach this case equally**: eligibility is
  the presence of a `covered-here` row and nothing else, so a disposition bears on it exactly by not
  being `covered-here`. A folder whose every row is `rejected` is ineligible owing nobody
  anything, and one whose every row was `superseded-by` another `[BR#n]` is ineligible too, even
  though §6.3 excludes those rows from the ledger line's counts — a line the eligibility check never
  reads anyway (see the paragraph below on reading dispositions off the file). **Every parent BRD
  reaches this case**, by construction rather than by outcome, and that is not a failure state: it
  is what "a BRD is a container" means, and its consumer is told where the requirements went. This
  folder holds no PRD of its own. A consumer that reaches this state must refuse to author a PRD here and
  say **where the requirements went**, rather than producing an empty or placeholder document.

  **What there is to say depends on how the state was reached, and the first way is settled on the
  folder rather than on any row:**

  | How every row left `covered-here` | What the consumer says |
  |---|---|
  | **The folder is a `BRD-` container** — decided on the folder, before a row is read | Every row of a root's ledger ends `covered-by`, `deferred-to`, `rejected` or `superseded-by`; `covered-here` is not among them, and a root row carrying one is a ledger written before a BRD became a container, or edited by hand. Refuse on the level and name the `PRD-` slices under the container, one PRD each — enumerated by `/brd-split` Phase 0 step 9's positive test (an immediate subdirectory whose `brd-link.md` `parent:` names this BRD), never by a name match. Where the container holds no slice at all, the run that carves one is `/brd-split <BRD-KEY> "<how to cut it>"` — a run with rows still to place has no findings to group them by and refuses without the instruction — and it is a **no-op** on a ledger with no `unallocated` row (§4), so a consumer naming it must say what the operator does then rather than leaving the offer to fail silently |
  | Some rows are `covered-by: <SLICE-KEY>` — the ordinary shape on a parent | Name those slices — and, per §6.1, which of them did not build the row delegated to it. A slice that deferred, rejected or has not allocated it is not somewhere to send the reader |
  | No row is `covered-by` | Name no slice, because none holds one of these rows — and say what the rows *did* resolve to rather than calling them all obligations. The three remaining dispositions say different things: a `deferred-to` row is a live obligation of this folder, a `rejected` one is an obligation of nobody and cites the `[DEF#n]` justifying it or the customer decision that withdrew it, and a `superseded-by` one was absorbed into the `[BR#n]` that replaced it. This is also the only shape a **slice** reaches, for the reason the paragraph below gives: no row of the set eligibility is read over on a slice can be `covered-by`. On a slice, add that a PRD needs one row resolved `covered-here` first |


  **A root row `covered-here` is repairable one row at a time, and the narrow repair is named before
  the wide one.** The illegal state is **one row wide**: every other row of that ledger is already
  legal and terminal, and no command in this plugin wrote the illegal one. So a consumer that
  reports it names, **first**, hand-editing that single row's `disposition:` in
  `coverage-ledger.md`, leaving every other row untouched — to `deferred-to: <this BRD>`,
  `rejected: [DEF#n]` or `superseded-by: [BR#n]` where the requirement is not to be built here, or
  back to `unallocated` where it is, which is the state `/brd-split`'s walk consumes and which lets
  that run confirm a slice whose own walk may legally write `covered-here`. §3's *no command moves a
  row back to `unallocated`, save one* binds the **commands**; a hand repair of a value no command
  wrote is not one of them, and the row above already names hand editing as how this state arises.
  **Second**, and only where the whole inventory is to be re-taken, `/brd-intake` re-run over the
  same folder rewrites the ledger with **every** row `unallocated` wherever its read finds a
  requirement (`commands/brd-intake.md` Phase 0 step 7 lists what a re-run keeps and what it
  changes, and Phase 5 writes the ledger), discarding every `deferred-to`, `rejected` and
  `superseded-by` the walk decided — each has to be re-taken, and a `rejected` row re-cited against
  its `[DEF#n]`. **A consumer naming that option names those decisions**: "the dispositions are
  replaced" is not the disclosure, because it does not say which judgement is destroyed.

  **The neighbouring state needs no repair and is still not sealed.** A container whose one slice was
  removed as a standing empty child holds no illegal row at all — every row is legally `deferred-to`,
  `rejected` or `superseded-by`, and nothing is owed to anybody. That is an **ending**, and a
  consumer reporting it names no command for the decision to un-defer a requirement, which is taken
  with the customer (`workflows-core:escalation-rules`, *When no option is safe to recommend*). It must not,
  however, report it as a state with no exit: once that decision is taken it is carried out by the
  same two repairs, in the same order — the one row moved back to `unallocated` by hand so
  `/brd-split` has a row to walk, or the `/brd-intake` re-run that reopens every row wherever its
  read finds a requirement (`commands/brd-intake.md` Phase 0 step 7).

  "Name the slices that do" is right in the first two rows only. In the third there is nothing to
  name, and a consumer that goes looking for a slice to point at finds none and must not invent
  one — the honest report is what each row actually resolved to, and, for the deferred ones, by whom.
  "The requirements are deferred" is the common shape of that case, not the whole of it:
  a folder whose every row is `rejected` reaches it owing nobody anything, and
  saying it deferred them would be false.

**A slice reaches eligibility by exactly this rule**, through the same Phase 4 walk on its own
ledger. The one difference is which rows the rule is read over, and it is why a slice still reaches
the "not eligible" case entirely through `deferred-to`, `rejected` and `superseded-by`, in any mix,
and never through a row pointing at another BRD. A slice's `covered-by` rows exist (§3) but are
exactly its **orphan rows** (§2) — claims the parent's walk withdrew — and `claims:`
names none of them, so none is in the set eligibility is read over. Every row that *is* in that set
is a row this slice claims, and a claimed row is settled by this slice's own walk, which never
writes `covered-by`. There is still no child below a slice for any row to point at.

**Eligibility is read over the rows this ledger holds, which §1 and §3 fix per level and which
`claims:` narrows only on a slice.** A source-owning BRD carries no `claims:` field, so a consumer
that intersects with one there tests an empty set and finds no `covered-here` row in it — which on a
parent is the right answer for the wrong reason, and on the day someone reuses that consumer against
a slice it is simply wrong. Read the ledger's own rows. On a slice the narrowing does real work
rather than coinciding with the ledger, and
it is what makes an orphan row safe in both directions: **an orphan row can neither create
eligibility nor withhold it, because the narrowing leaves it out.** One the parent's run writes is
never `covered-here` — §3's table gives it `covered-by`, `rejected` or `superseded-by` and nothing
else, and the parent's Phase 4.5 removal repair writes `covered-by` too — but one left standing as
the slice's own earlier decision (§2's third route) can read `covered-here`, and only the narrowing
keeps it from making an ineligible slice look eligible; and no orphan row is ever `unallocated`, so
none can make an eligible slice look unallocated.

This is **read from the ledger, not decided in advance.** Slicing a BRD entirely and slicing it
only partially are both ordinary, supported outcomes; the ledger is what tells a later consumer
which one happened, without the operator having declared which they were doing at the time. A row
still `unallocated` **as written on this BRD's own ledger** when eligibility is checked means the
gate in §4 was never satisfied — a consumer must treat that as a hard refusal, never as an implicit
`covered-here` or `deferred-to` in either direction.

**Read that from the ledger file, never from the §6 line.** Since §6.1 resolves a delegated row
through the BRD that owns it, the line's `unallocated` term also counts rows this BRD wrote
`covered-by` and that BRD has not walked yet — rows whose fate this BRD *has* recorded. A consumer
keying the refusal off that term would hard-refuse a BRD whose own gate is fully satisfied. The
refusal is about this ledger's own written dispositions, and about nothing else.

### 5.1 The unprefixed folder — a positive test, never an absence

A folder resolved through `workflows-core:addressing` §5's legacy fallback carries **no prefix at
all**, and neither does an unprefixed folder a command's `@<path>` names, which that file's §3
resolves without the fallback and so without its `legacy:` flag — so the prefix test cannot answer
either. **The answer must be positive evidence that this folder is a BRD, never the absence of a
file** — because a pre-prefix specs repo holds *two* unprefixed shapes and only one of them is a
container:

- a **root BRD folder**, `specifications/<KEY>-<slug>/`, written by `/brd-intake` before the kind
  prefixes shipped — a current run writes `BRD-<KEY>-<slug>/` and never reaches this test
  (`commands/brd-intake.md` Phase 0 step 7, `workflows-core:addressing` §2);
- a legacy **idea-route PRD folder**, `specifications/<KEY>-<slug>/` holding `idea.md` and `prd.md`,
  written before the kind prefixes shipped.

**Neither carries a `brd-link.md`.** `/brd-intake` writes none — only `/prd-ground`, `/brd-split`,
`/brd-package` and `/brd-reconcile` ever do, and all but `/brd-split` write only `depends-on:`,
never `parent:` (`/brd-reconcile` only where a returned review's correction asks to add a
prerequisite, its *Apply the required corrections* table's `brd-link.md` row) — and the idea route
has never written one at all. So "no `brd-link.md`, or one carrying
no `parent:`", which is the correct test for **root versus slice** *once a folder is known to be on
the BRD route*, separates nothing here: used as the container test it refuses the legacy idea-route
PRD folder too, and then offers `/brd-split` on a folder holding no coverage ledger to walk — a stop
naming a remedy that cannot run. An unprefixed idea-route folder is not an exotic input: it misses
`workflows-core:addressing` §3's `*-<KEY>-*` prefixed glob by construction and lands in §5's fallback
every time.

**What a root BRD carries and an idea-route PRD folder never does is the BRD bookkeeping**, and
exactly two commands create it: `coverage-ledger.md` (`/brd-intake` Phase 5; `/brd-split` Phase 3
step 5 for a slice) and `brd/brd-inventory.md` (`/brd-intake` Phase 3; `/brd-split` Phase 3 step 4
for a slice). **No command on the idea route writes either, ever**, so their presence — not any
absence — is the test. On an unprefixed folder:

| What the folder carries | What it is | The container refusal |
|---|---|---|
| **Neither** `coverage-ledger.md` **nor** `brd/brd-inventory.md` | a legacy **idea-route PRD folder** — the ordinary unprefixed shape | **does not fire.** The consumer proceeds exactly as it does on a `PRD-` folder |
| Either file, **and** a `brd-link.md` carrying `parent:` | a legacy **slice** | does not fire — a slice is the folder a PRD is authored in |
| Either file, and **no** `brd-link.md` carrying `parent:` | a legacy **root BRD container** | **fires** |

**Either file, not both, and deliberately.** The two are written by the same run, so an ordinary
root BRD carries both; requiring both would let a folder left half-written by an interrupted intake
pass the test and take a PRD authored into it. One of them is already evidence that the BRD route
touched this folder, which is the only question this test asks.

**It reads no PRD artifact, and that is what lets every consumer share one rule.** The build-ladder
and route consumers are `/create-prd` (Phase 0 step 5a), `/create-ard` (step 1a), `/specify`
(step 0), `/epics` (step 1a), `/prd-ground` (step 5a), `/brd-interview` (step 5a), `/brd-package`
(step 5a) and `/brd-reconcile` (step 5a); **the effort-proposal pair and their reviewer take the same
§5.1 test and were missing from this paragraph** — `/prd-proposal` (Phase 0 step 4, refusing a `BRD-`
container), `/brd-proposal` (Phase 0 step 4, refusing a `PRD-` slice on the same test with the
disposition inverted) and `proposal-reviewer`; **two more of this plugin's own commands take it and
were missing too** — `/idea` (Phase 0, refusing a container with `IDEA_NOT_AN_IDEA_FOLDER`, through
`workflows-core:addressing` §4.1) and `/update-prd` (Phase 0 step 4's no-PRD table, citing §5.1
directly to word its stop); **two route commands take it too, neither to refuse a container, since
both run at the root** — `/brd-intake` (Phase 0 step 7, through `workflows-core:addressing` §4.1,
to accept as a re-run only a folder the test places as a container) and `/brd-split` (Phase 0
step 5, citing §5.1 directly to refuse the legacy idea-route shape with `BRD_SPLIT_NOT_A_BRD`, and
step 8, through §4.1, to word its full-mode empty-inventory stop); and the companion plugins' commands that take it through
`workflows-core:addressing` §4.1, which states the same positive test for a plugin that cannot read
this file — `dev-workflows`' `/design`, `/implement` and `/ready`, and `docs-workflows`' `/document`
(keyed mode) and `/release-notes` — take it too. The recipe below reaches a command that takes the
test through §4.1 only where its remedy text happens to cite §5 as well, so run
`grep -ln 'addressing. §4\.1' plugins/*/commands/*.md` beside it, each hit opened, since that grep
also returns commands citing §4.1 for placement alone. **Read that as a list, not as a count, and
re-derive it against the tree rather than adjusting it** — the recipe is `grep -rn 'coverage-ledger-format.*§5'
plugins/*/commands/*.md plugins/*/agents/*.md`, each hit opened, since a hit may cite §5 for
something other than this test — `/brd-intake` also names §5.1 to describe the other commands'
refusals, and `/brd-split` cites §5 for what makes a slice PRD-eligible — and neither of those two
citations is what makes either a consumer. The sentence said *all
eight* while the tree held more, which is the arithmetic this paragraph's own closing instruction
exists to prevent. `/create-prd` cannot test for `prd.md` — it is the run that is about to
write it — so a test keyed off the PRD's presence would have to be worded differently in
`/create-prd` than in every other consumer, and one copy of this rule per consumer is the drift this
file exists to prevent. The route four — `/prd-ground`, `/brd-interview`, `/brd-package` and
`/brd-reconcile` — take this test for a different consequence than the build-ladder four before them —
they refuse to *run at all* against a root, rather than refusing to *author into* one — but the test
itself, the positive evidence of BRD-ness, is the one this section fixes and is unchanged either way.

**`/epics` is a consumer even though it *can* read `prd.md`, and that is the point.** Its step 1b
gates on `prd.md`'s own `kind: prd`, which an unprefixed container fails for holding no `prd.md` —
so an absence test looks sufficient. It is not, because 1b's stop names `/create-prd` as the remedy
and `/create-prd` takes this test and refuses the same folder as a container: a stop whose remedy
stops. The container refusal must therefore be taken one step earlier, at 1a, on the same evidence
`/create-prd`, `/create-ard` and `/specify` use. A rule stated as covering three consumers while a
fourth needed it is how that dead end shipped.

A prefixed tree never reaches this test at all, exactly as it never reaches `workflows-core:addressing` §5.

### 5.2 Offering `/create-prd` — three refusals, not one

`/create-prd` refuses **three** shapes on the BRD route, and an offer that names it is safe only
once it has tested all three. The container refusal is the one an offering command remembers,
because it is usually the one that command took itself; the other two are data refusals read off the
resolved slice's own ledger (`commands/create-prd.md` Phase 0 step 7):

| Tested on | Fires when | What `/create-prd` then names |
|---|---|---|
| the resolved folder's prefix, or §5.1's evidence where it has none (§5, §5.1) | it is a `BRD-` container | `CREATE_PRD_BRD_NOT_SLICED` — the `PRD-` slices under it, or `/brd-split <BRD-KEY> "<how to cut it>"` where there are none |
| the gate set | a row is still `unallocated` | `CREATE_PRD_BRD_UNALLOCATED` — `/brd-split <SLICE-KEY>`, whose walk moves exactly those rows |
| the gate set | no row is `covered-here`, and none `unallocated` (the row above is tested first) | `CREATE_PRD_BRD_NOT_ELIGIBLE` — where the gate set is **empty** (a standing empty child), `/brd-split <PARENT-KEY>`, in the form the parent's own ledger decides: `/brd-split <PARENT-KEY> "<how to cut it>"` where it still holds an `unallocated` row (a bare run stops there with `BRD_SPLIT_NEEDS_INSTRUCTION`), the bare `/brd-split <PARENT-KEY>` where it holds none, and neither form, the parent's ledger reported by path, where it cannot be read; **no command at all** where the gate set is non-empty |

**The gate set is this slice's own `coverage-ledger.md` rows, narrowed by its `brd-link.md`
`claims:`** — the same set Phase 0 step 7 defines, read the same way, and read **out of the ledger
file, never off a `ledger:` line**: that line's `unallocated` term is a *resolved* count and does not
track §4's gate (§6.1), so keying an offer to it would withhold the option from a slice whose own
gate is fully satisfied. An orphan row can neither add the option nor withhold it — `claims:` names
none of them, so the gate set never reaches one. An orphan row is never `unallocated` (§2), and one
left standing as the slice's own earlier decision can read `covered-here` (§2's third route) without
making the slice eligible, for that same reason.

**`<PARENT-KEY>` is read, never derived.** It is the `parent:` field of the same `brd-link.md` the
`claims:` list came from (`workflows-core:addressing` §4) — the offering run has already opened that
file to build the gate set, so the key is in hand and is never parsed out of the slice's own key or
its folder name.

**Only a BRD-route folder has a gate set at all.** A resolved folder carrying no `brd-link.md` is an
idea-route PRD folder: neither data refusal exists for it, and `/create-prd <ADDRESS>` is reachable
on the container test alone.

**The converse — a `brd-link.md` with no `coverage-ledger.md` beside it — is reachable only by hand
damage, and it is not an empty gate set.** `/brd-split` writes both files in the same Phase 3 and
commits them together, so no run of this plugin leaves a slice carrying one and not the other. A
consumer that meets it can evaluate neither data refusal, and must not read the absent file as a gate
set of zero rows: that is the *standing empty child* — a slice whose ledger exists and whose `claims:`
list is empty — which the table above resolves to `/brd-split <PARENT-KEY>` (with or without an
instruction, as the parent's ledger decides), and resolving a missing file to the same offer would send an operator to keep-or-remove a slice on evidence nobody has.
**Name no option at all.** Report the absent `<slice-dir>/coverage-ledger.md` by path, say that
`/brd-split` wrote it and landed it with the slice, and leave recovering it from the specs repo's
history to the operator — nothing in this plugin rewrites a slice's ledger in place. **A
`coverage-ledger.md` that is present and cannot be read is the same state for this purpose**: its
rows are `unresolved` (§6.2), so neither data refusal can be evaluated either — name no option, and
report the file by path with the read error. The rule is
stated here, in the authority every offering command already cites; each command that reads a slice's
ledger to shape an offer or a remedy carries a row for this state that cites it.

**Where a data refusal would fire, drop the `/create-prd` option and say which test failed.** The
precedent is `commands/brd-reconcile.md` Phase 14, which runs both data tests before offering
`/product-workflows:create-prd <SLICE-KEY>` and **drops** the option rather than annotating it, on the
stated ground that a hard refusal in another command's Phase 0 is not a state the reader can judge
for themselves. Dropping is not going quiet: name what moves the failing test where a command exists
— `/brd-split <SLICE-KEY>` for an `unallocated` row, `/brd-split <PARENT-KEY>` for a standing empty
child, in the table's form: with a slicing instruction where the parent still holds an `unallocated`
row, bare (the keep-or-remove run) where it holds none, and neither, reporting the parent's ledger by
path, where it cannot be read — and where none exists, say so. **The non-empty
`CREATE_PRD_BRD_NOT_ELIGIBLE` branch is the one that must never be offered into**: it names no
command by design, so an offer that sends the operator there hands them a stop with no way out, and
nothing in this plugin moves a slice's `deferred-to`, `rejected` or `superseded-by` row back to
`unallocated` (§3).

## 6. The ledger line

Every command of the BRD-to-PRD route ends its final report with exactly one line — the five
`/brd-*` commands of that route, and `/prd-ground`'s too on `route: brd`, which cites this section
for the format — so the ledger's state is visible without opening the file or running anything else.
**The glob is not the test, and this sentence used to read as though it were**: `/brd-proposal`
matches `/brd-*` without being a phase of the route, reads a container's ledger only to compute the
coverage statement inside the document it writes, and prints no line here.

```
ledger: <N> requirements — <covered> covered, <deferred> deferred, <rejected> rejected, <unallocated> unallocated, <unresolved> unresolved (<delegated> delegated, <not-built> not built)
```

### 6.1 A `covered-by` row is counted through the BRD it names

Delegating a requirement records **which** BRD owns it (§3); it does not record that the BRD built
it. So before any count below is taken, every `covered-by: <BRD-KEY>` row is resolved **one hop** —
read that BRD's own `coverage-ledger.md`, take the disposition of its row for the same `[BR#n]` —
and this row is counted as whatever that BRD decided. **The hop is the same operation at both
levels**, and only the key differs: on a source-owning BRD it lands in the named **child**, and on
a slice it lands in the named **sibling or parent** (§3). Nothing below is level-specific, so a
slice's line resolves its orphan rows exactly as a parent resolves its delegated ones:

| The named BRD's row for that `[BR#n]` | This `covered-by` row counts as |
|---|---|
| `covered-here` | `covered` |
| `deferred-to` | `deferred` |
| `rejected` | `rejected` |
| `unallocated` | `unallocated` |
| `superseded-by` | excluded from every count and from the total (§6.3) |
| unreadable | `unresolved` (§6.2) |

**Every orphan row (§2) on a slice is counted through the parent's current disposition for that `[BR#n]`, never as it reads.** An orphan row records a claim the parent withdrew, and what became of that requirement is the parent's ledger's to say. Read the parent's row for the same `[BR#n]` and count this row as §3's orphan table maps that disposition — `covered-by: <SIBLING-KEY>` or `covered-by: <PARENT-KEY>`, resolved one hop by the table above and counted among the delegated rows (§6.4), or `rejected`/`superseded-by` verbatim. Where the parent's row is `unallocated` — after a `/brd-intake` re-run, before a walk re-allocates it — count this row `unallocated`; where the parent's ledger cannot be read, count it `unresolved`, as §6.2 counts any read that fails. **The row and the count usually agree, and the rule is for where they do not.** The first two routes write the mapping of the parent's row as it stood when they withdrew the claim, so the two differ only where the parent's allocation has moved since: a third-route row, which holds the slice's own overruled decision (§2), or a first- or second-route row whose parent row an intake reset and a later walk have changed, which nothing re-points. Counting such a row as written would report a requirement this slice no longer holds as covered or deferred here — and, summed across siblings, twice. Reading the parent's row fixes what this row counts as; it is not a hop, and the one hop the mapping may then take is the only one.

**One hop is exhaustive**, and it stays exhaustive now that a slice's row may carry `covered-by`
(§3). The argument is no longer that a slice cannot delegate; it is that a hop can never land on a
row that does:

- **A parent's hop lands on a row the child `claims:`.** The parent wrote `covered-by: <CHILD-KEY>`
  precisely because it allocated that `[BR#n]` to that child, so the child claims it — and a
  claimed row is settled by the child's own walk, which never writes `covered-by` (§3, §4). A child
  row that nevertheless carries `covered-by` for a row its parent delegated to it is malformed; it
  is counted `unresolved` rather than followed.
- **A slice's own `covered-by` rows are exactly the rows its parent did *not* delegate to it** —
  orphan rows, withdrawn claims (§2) — so no parent's hop ever lands on one.
- **A slice's hop lands on a sibling that claims the row, or on the parent.** The sibling case is
  the first bullet one level across. The parent case lands on a row the parent resolved
  `covered-here` or `deferred-to` (§3's orphan table), never on another `covered-by`: a parent row
  reading `covered-by: <SIBLING-KEY>` is what produces the sibling form instead of the parent one.

Nesting is capped at one level throughout (`workflows-core:addressing` §6), so there is no third
level for a chain to reach even if one were somehow written.

This is the arithmetic §1 promises. The failure §1 names — every child independently deciding the
same requirement is somebody else's problem — stays invisible while a parent row reading
`covered-by` counts as covered on its own say-so. Resolved through the child, each such row is
reported as the `deferred`, `rejected` or `unallocated` it actually is, and the trailing figures
say how many requirements this BRD handed to a child that the child is not building.

`covered` therefore sums `covered-here` rows and the delegated rows that resolved to `covered`.
`deferred`, `rejected`, and `unallocated` each sum their own matching disposition on this ledger
plus the delegated rows that resolved to it. `unresolved` counts nothing but delegated rows whose
named BRD could not be read.

**"Delegated" means every `covered-by` row this ledger holds** — on a slice, every orphan row the
rule above counts as a `covered-by` one, whatever the row itself reads (§2). That is deliberate and is the audit trail §1 exists for: a requirement a slice
once claimed and no longer does still appears in that slice's own arithmetic, resolved through the
BRD that took it, so no report can say it was lost. It is counted there and on the parent's ledger
under two different questions — the parent's line asks which BRD owns it, this one asks what became
of a claim this slice made — and neither is a second count of the same obligation at the same
level.

**Every term in this line is a resolved count, not a census of what the file says**, and the term
that most visibly differs is `unallocated`. **The line's `unallocated` term does not track §4's
gate.** §4 is satisfied when no row **as written on this ledger** is `unallocated`; a delegated row
is written `covered-by` and stays written `covered-by` whatever the child does with it. The very run
that satisfies the gate seeds each child it creates with rows the child has not walked yet (§3's
creator table), so a completed `/brd-split` routinely reports a non-zero `unallocated` term for rows
whose fate this BRD has fully recorded — that is the resolution working, not a gate left open.
**A consumer testing the gate reads the dispositions in the ledger file; it never reads this line.**

### 6.2 A ledger that cannot be read is `unresolved`, never `covered`

Resolution reads the named BRD's `coverage-ledger.md` **from the working tree**, through
`resolve-address` (`workflows-core:addressing` §3) — not from git, because this line reports what
the run can actually see. A delegated row is `unresolved` when no folder resolves for the
`<BRD-KEY>` it names; when that folder holds no `coverage-ledger.md`; when the tree the run is
standing in does not carry that BRD at all, because the split that created it has not merged; or
when its ledger holds no readable row for that `[BR#n]`.

It gets its own term rather than joining one of the four:

- **Not `covered`** — an absent answer is not a positive one, and counting it as covered is exactly
  the defect this section exists to remove.
- **Not `unallocated`** — this row **is** allocated: it carries `covered-by`, a terminal
  disposition (§3). Reporting an unreadable BRD under the one disposition this row demonstrably
  does not have would also put a BRD nobody could read in the same bucket as one that *was*
  read and has simply not walked its ledger yet — two different facts, and the second is the one a
  reader can act on.
- **Not dropped** — dropping the row would shrink the total and hide the requirement altogether,
  which is §1's failure in a new costume.

**`unresolved` is a reporting state, not a disposition.** §3's six are unchanged, no row is ever
written `unresolved`, it is never offered by any picker, and it never blocks §4. A non-zero
`unresolved` is a prompt to look at the named BRD, not a defect in this BRD's allocation.

**The line mixes two provenances, and a reader should know which term came from where.** The ledger
being reported on is gated wherever a gate exists — but only `/prd-ground` gates **this file**, in
its Phase 0 step 6. `/brd-split` and `/brd-interview` each gate `grounding/code-grounding.md` there
and then read the ledger from the working tree, `/brd-interview` stopping on it twice
(`BRD_INTERVIEW_UNALLOCATED`, `BRD_INTERVIEW_ALL_DELEGATED`). That is sanctioned — a command may
read the worktree and refuse what it finds; what it may not do is *claim* the file is merged because
a sibling's gate passed (`workflows-core:phase-handoff` §4.0) — but it does mean this line's
guarantee is `/prd-ground`'s alone. Meanwhile the ledgers resolved into it are
read from the working tree and gated by nothing. So a `covered` this line reports for a delegated row can rest
on another BRD's decision that has not merged and could still change, and an `unresolved` can mean nothing
worse than a pull request still open. That asymmetry is the price of reporting what the run can
actually see instead of reporting nothing, and it is why this line is a report and not an input to
any gate.

### 6.3 `superseded-by` is excluded from every count and from the total

A superseded row's obligation was absorbed into the `[BR#n]` that replaced it; counting it again
anywhere in this line would double-count the same requirement under two ids. That holds at both
levels: a row this ledger itself marks `superseded-by`, and a delegated row the named BRD resolved
`superseded-by`, are both dropped before anything else is computed.

A supersession the named BRD recorded is **not** "delegated and then not built". That BRD may only
supersede a `[BR#n]` its own inventory holds, and every id in that inventory is the source-owning
BRD's, copied row for row (`commands/brd-split.md` Phase 3 step 4) — so the replacing requirement
is a row of the **source-owning BRD's** ledger, carrying its own fate and its own contribution to
that BRD's line. Supersession moves an obligation; it does not drop one.

**On a parent's line the replacing row is a row of *this* ledger too**, so the move is visible in
the same line the drop happened in. **On a slice's line an orphan row (§2) breaks that**, in either
of the two ways one can be superseded: the row may carry `superseded-by: [BR#n]` verbatim, written
by the parent's walk and naming a `[BR#n]` of the parent's inventory this slice never claimed; or it
may be a `covered-by` row whose named sibling superseded it into one. The obligation is still not
lost — it is on the parent's ledger, where every id lives and where this section's guarantee holds
in full — but a reader who wants to see where a slice's orphan row went after a supersession reads
the parent's ledger, not this line.

### 6.4 The two trailing figures

`<delegated>` counts the `covered-by` rows — on a slice, the orphan rows §6.1 counts as
`covered-by` ones — that survive the §6.3 exclusion. `<not-built>` counts
those among them the named BRD deferred, rejected, or left `unallocated`.

Every delegated row lands in exactly one of three places, so
`<delegated>` = the delegated rows the named BRD covers + `<not-built>` + `<unresolved>`.

**Both figures are printed even when both are zero**, and so is a zero `unresolved`: an omitted
clause is indistinguishable from a check that never ran, and the whole point of §6.1 is that this
resolution is visible rather than assumed. A BRD with no `covered-by` row at all reports
`0 unresolved (0 delegated, 0 not built)` and says so plainly. That is the ordinary shape of a BRD
nobody split, and of a slice whose parent's walk withdrew none of its claims — but it
is **not** a property of being a slice. A slice holding orphan rows (§2) reports each through the parent's
current disposition for its `[BR#n]` (§6.1) — as delegated wherever that maps to `covered-by`,
resolved one hop through the sibling or parent the mapping names.

### 6.5 Worked example

A synthetic BRD `EPIC-008` holds seventeen ledger rows, seven of them delegated to its one child
`EPIC-008-01`:

| This BRD's disposition | Rows |
|---|---|
| `covered-here` | 4 |
| `covered-by: EPIC-008-01` | 7 |
| `deferred-to: <this BRD>` | 2 |
| `rejected: [DEF#n]` | 1 |
| `superseded-by: [BR#n]` | 2 |
| `unallocated` | 1 |

Resolving those seven one hop into `EPIC-008-01`'s own ledger:

| What `EPIC-008-01` did with it | Rows | Counts on `EPIC-008` as |
|---|---|---|
| `covered-here` | 2 | `covered` |
| `deferred-to` | 1 | `deferred` |
| `rejected` | 1 | `rejected` |
| `unallocated` | 1 | `unallocated` |
| `superseded-by` | 1 | excluded (§6.3) |
| no row for that `[BR#n]` | 1 | `unresolved` (§6.2) |

Three rows are dropped before anything is computed: this BRD's own two `superseded-by` rows, plus
the one delegated row the child superseded. 17 − 3 = 14 requirements. Six delegated rows survive
that exclusion; of those, the child covers 2, is not building 3 (1 deferred + 1 rejected +
1 `unallocated`), and 1 could not be resolved.

- covered = 4 `covered-here` + 2 delegated-and-covered = 6
- deferred = 2 here + 1 delegated = 3
- rejected = 1 here + 1 delegated = 2
- unallocated = 1 here + 1 delegated = 2
- unresolved = 1

6 + 3 + 2 + 2 + 1 = 14, and 6 delegated = 2 covered + 3 not built + 1 unresolved:

```
ledger: 14 requirements — 6 covered, 3 deferred, 2 rejected, 2 unallocated, 1 unresolved (6 delegated, 3 not built)
```

**What the unconditional rule reported instead.** Counting every `covered-by` row as covered on its
own word, the same ledger read `15 requirements — 11 covered, 2 deferred, 1 rejected, 1 unallocated`:
three requirements nobody is building were reported as covered, one delegated requirement nobody
could account for was reported as covered, and a row the child had already superseded was still
counted as a live requirement. That line is what §1 says the ledger exists to prevent.

### 6.6 Worked example — a slice's line, with an orphan row

A second synthetic tree, separate from §6.5's: `EPIC-009` with two slices, `EPIC-009-01` and
`EPIC-009-02`. Splitting `EPIC-009`, Phase 3 provisionally gave `EPIC-009-01` four rows —
`[BR#3]`, `[BR#4]`, `[BR#5]`, `[BR#6]` — and seeded four `unallocated` ledger rows in it. Phase 4's
walk on `EPIC-009`'s own ledger then allocated the first three `covered-by: EPIC-009-01` and the
fourth `covered-by: EPIC-009-02`. So `[BR#6]`'s `claims:` entry and its copied inventory row were
withdrawn from `EPIC-009-01`, and its ledger row stayed, written `covered-by: EPIC-009-02` (§2, §3).

`/brd-split EPIC-009-01` then walks the three rows still `unallocated` — the ones it claims — and
resolves `[BR#3]` and `[BR#4]` `covered-here` and `[BR#5]` `deferred-to: EPIC-009-01`. It never
stands on `[BR#6]`: that row was terminal before this run opened the file.

| `EPIC-009-01`'s row | Disposition | Counts as |
|---|---|---|
| `[BR#3]` | `covered-here` | `covered` |
| `[BR#4]` | `covered-here` | `covered` |
| `[BR#5]` | `deferred-to: EPIC-009-01` | `deferred` |
| `[BR#6]` — orphan | `covered-by: EPIC-009-02` | resolved one hop (§6.1) into `EPIC-009-02`, which built it: `covered` |

Nothing is excluded by §6.3, so the total is 4. One row is delegated, and the sibling covers it:

```
ledger: 4 requirements — 3 covered, 1 deferred, 0 rejected, 0 unallocated, 0 unresolved (1 delegated, 0 not built)
```

3 + 1 + 0 + 0 + 0 = 4, and 1 delegated = 1 covered + 0 not built + 0 unresolved.

**Three things this line settles.** §4 is satisfied — no row is `unallocated` as written, so
`/brd-split EPIC-009-01` completes. §5 is satisfied — `[BR#3]` and `[BR#4]` are `covered-here` and
both are rows `claims:` names, so the slice is PRD-eligible on its own remaining rows. And `[BR#6]`
is reported, not lost: here as a delegated row resolved through the sibling that built it, and on
`EPIC-009`'s own line as `covered-by: EPIC-009-02` resolved through the same sibling. Two lines
answer two different questions about it; neither is silent.

**The ordinary case is unchanged.** Had the parent's walk settled `[BR#6]` `rejected: [DEF#4]`
instead, the orphan row would read `rejected: [DEF#4]` — the disposition carries across unchanged
(§3) — count in `rejected`, contribute nothing to `delegated`, and the line would read
`4 requirements — 2 covered, 1 deferred, 1 rejected, 0 unallocated, 0 unresolved (0 delegated, 0 not built)`.
That is exactly what this file said before the orphan row was kept, except that the row is now
there to be counted at all.

# Decision register format (embedded authority)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

The canonical shape of the BRD→PRD workflow's **decision register**: the record every `[VD#n]`
(delivery-team decision) and `[CD#n]` (customer decision) carries, the five statuses one can hold,
the rule that makes `argumentation` mandatory, the rule that makes reopening explicit, what
`conditional_on` means and what it buys, the prohibition on a decision resting solely on a
`will-change` finding, and the `[AS#n]` assumption record that must reach the customer. Design
authority: `docs/superpowers/specs/2026-08-29-brd-to-prd-workflow-design.md` §6.2 and decision rows
D14 and D19 in §3 (removed from the tree 2026-09-23; `git show 62e791e8:docs/superpowers/specs/2026-08-29-brd-to-prd-workflow-design.md` retrieves it).

Three neighbouring rules are owned elsewhere and cited, not restated: the `horizon` a grounding
finding carries and the `[CG#n]`/`[DG#n]` finding record itself belong to
`workflows-core:grounding-format` (§5 and §2); the `[G]`/`[V]`/`[C]` tag that decides which register
a question's answer lands in, and the rounds a decision is stamped with, belong to
`references/interview-tagging.md` (§1 and §5); the `<BRD-KEY>` grammar a `conditional_on` uses
belongs to `workflows-core:addressing` §1.

**Consumed by `commands/brd-interview.md`**, which writes `[VD#n]` and `[AS#n]` records against this
shape, enforces §6, and — on §4's first cause — reopens a `decided` `[VD#n]` or `[CD#n]` a
`--rebaseline` pass moved the ground under, and which puts the question of a record reading
`reopened` again wherever no question putting it is in flight, whichever run reopened it; by `commands/create-prd.md`, which writes an `[AS#n]` — and only an `[AS#n]` —
for a customer-authority gap that only PRD authoring could surface (§7); by `agents/brd-package-reviewer.md`, which reads them; and by
`commands/brd-package.md`, which surfaces every open `[AS#n]` in the customer prompt (§7) and finds
every position resting on a prerequisite by its `conditional_on` field (§5); and by
`commands/brd-reconcile.md`, which mints the `[CD#n]` records — the only command that does — and
enforces §6 on them as it freezes them, supersedes the `[AS#n]` each one settles, reopens what an incoming customer decision overturns under
§4, re-decides in place a `[CD#n]` whose reopened question the customer has answered, and runs the propagation sweep §5 exists to serve. **It has more readers than those**: the three
commands §1's `altitude` row names each read the register filtered on their own value and stamp
`consumed_by` on what they drew on, and `commands/prd-ground.md`, `commands/brd-split.md`'s re-cut
report, `commands/prd-proposal.md`'s tier grading, `agents/proposal-reviewer.md` and
`agents/customer-review-reader.md` read it too. `grep -l 'decisions\.md' commands/*.md agents/*.md`
lists every command and agent that names the register. It is not a list of readers in either
direction: a file may name it only to compare it with what a proposal priced or to describe another
command's write, and `agents/customer-review-reader.md` reads it without naming it — it is handed
the register by path, as its `assumptions` input. **Every one of them reads the register through
§8** — the agent through its caller, which applies §8 to what the agent returns, since it reads the
files it is handed as they stand: an item a stopped `/brd-interview` run left, which no round record
names, is never counted.

## 1. Record shape

**The file opens with one line, `# Decision register: <BRD-KEY>`** — the key of the BRD whose folder
it sits in — and holds its records after that line, one block per record. **Every command that
creates the file writes that line first**: `commands/brd-interview.md` on the first register it
creates, whether or not the round recorded anything; `commands/create-prd.md` where it creates the
register for a roundless `[AS#n]` (§7); and `commands/brd-reconcile.md` where a `--sent` run finds
no register on file, whether or not it then freezes a `[CD#n]` (its *Freeze the customer decisions*
phase). **A register holding no record is that line alone**, and it is an ordinary state —
`/brd-interview` writes it so where a round it records produced no `[VD#n]` or `[AS#n]`, and
`/brd-reconcile` where the register it creates takes no `[CD#n]` — which every reader treats as a
register with nothing in it, never as a missing one. A register written before 3.7.0 may lack the
line, and no reader keys on it: records are found by their own ids.

Each `[VD#n]` and `[CD#n]` carries:

```yaml
id: [VD#7]
statement: <the decision, one sentence>
options_considered: [<option>, <option>, ...]
chosen: <option>
argumentation: |
  <why — mandatory>
evidence: [[CG#12], [DG#3]]
defects: [[CDF#2]]                        # omitted unless the decision turns on a recorded code defect
settles: [[DEF#4]]                        # [CD#n] only, never a [VD#n]: omitted unless it answers a defect's question
altitude: product | architecture | implementation
conditional_on: <BRD-KEY>/<decision-id>   # omitted unless the decision depends on a prerequisite
status: open | decided | reopened | superseded | withdrawn
consumed_by: PRD | ARD | specification | none
round: 2
```

| Field | Notes |
|---|---|
| `id` | `[VD#n]` or `[CD#n]` — contiguous within its own prefix, assigned once, never renumbered, never reused after a terminal status; a removed torn write is the one exception to each (§8) |
| `statement` | one sentence, stating the decision itself and not the discussion that produced it |
| `options_considered` | what was actually on the table, including the one chosen — save on a `[CD#n]` whose customer answered outside it (below). **A question put as yes or no, listing no options, records `["yes", "no"]`**; one that listed its options records them as put — the set a customer answering yes or no was offered, written down rather than left for a reader to infer. **A `[CD#n]` answering what put no options records a fixed pair**: an `[AS#n]`, which asserts rather than offers, `["as assumed", "not as assumed"]`; an escalated `[SR#n]`, which sets the package's position against an attack on it, `["as the package states", "as the finding argues"]` |
| `chosen` | exactly one member of `options_considered` — **or, on a `[CD#n]` only, where the customer answered with none of the options put, their answer quoted after one fixed marker**: `chosen: "outside the options: <the customer's answer, verbatim>"`. `options_considered` then stays exactly as put and is never widened to take the answer in: it records what the customer was offered, and an option added afterwards would claim they were offered what they volunteered. The marker is the only way a `chosen` may name no member, so a reader tells the two cases apart by the field alone. **Quote it so YAML reads it back exactly**: a one-line answer carrying no `"` and no `\` in the double-quoted form above; any other — spanning lines, or carrying either character — as a literal block scalar, `chosen: |`, its first line `outside the options: ` and the answer following verbatim, so the answer's own line breaks and quotes are never escaped or folded. A `[VD#n]` never takes it: an option the operator names joins `options_considered` before it is chosen (`commands/brd-interview.md`, *Put each `[V]` to the operator*) |
| `argumentation` | why — **mandatory**, §2 |
| `evidence` | the `[CG#n]`/`[DG#n]` findings the decision rests on, per `workflows-core:grounding-format` §2; the list is what §6 inspects. **Never omitted: a decision resting on no finding writes `evidence: []`**, the one form, so a record with no evidence is never mistaken for one whose field was lost. The field applies to every decision, so `[]` is a known value — a list with nothing in it — and not the not-applicable case `workflows-core:grounding-format` §2.1 omits a field for. An `[AS#n]` carries its why-no-evidence statement here instead (§7). **A `[CD#n]` copies it**, as `altitude` below is copied and for the same reason — the customer's answer carries no finding list of its own: from the held `[C]` question's own `- **Findings:**` line (`commands/brd-interview.md`, *Hold every `[C]`*) and nothing else in the entry, so `evidence: []` there says the question was put against no finding and never that a line could not be read |
| `defects` | the `[CDF#n]` code-defect entries this record turns on, per `references/code-defect-log-format.md`; omitted when absent. **Never in `evidence`** — §6's will-change rule inspects that list, and a non-finding id in it would silently change what D19 fires on |
| `settles` | the `[DEF#n]` requirement-defect entries a `[CD#n]` answers — the one the `[C]` question it answers was raised by (`references/interview-tagging.md` §1), or, for a question about a row rejected on a defect, the one it carries (`commands/brd-interview.md`, *Round 1 is generated from the grounding*), copied by `/brd-reconcile` from that question's held entry — its `- **Requirement defect:**` line, and nothing else in it — never inferred from the customer's answer. **Only ever on a `[CD#n]`**: a requirement defect is in the customer's statement and is settled by the customer. Omitted when absent |
| `altitude` | which level the decision sits at, so the spec's §7 altitude routing can send it to the right downstream artifact. **The test is that artifact**: `product` where the answer is the PRD's to state (`commands/create-prd.md`), `architecture` where it is the ARD's (`commands/create-ard.md`), `implementation` where it is the specification's (`commands/specify.md`) — the three commands that each read the register filtered on the value that is theirs. **A `[CD#n]` copies it** from what its answer answers — the held `[C]` question's own `- **Altitude:**` line, which `commands/brd-interview.md` decides by this same test when it holds the question, or an `[AS#n]`'s field — because the customer's answer carries no altitude of its own (`commands/brd-reconcile.md`, *Freeze the customer decisions*) |
| `conditional_on` | omitted unless the decision depends on a prerequisite — §5 |
| `status` | one of the five in §3 |
| `consumed_by` | the same field, values, and starting-at-`none` rule as `workflows-core:grounding-format` §2, applied to a decision instead of a finding |
| `round` | the interview round that produced the decision, per `references/interview-tagging.md` §5. **Omitted where the decision came from no round** — a `[CD#n]` answering an `[AS#n]` that itself carries none (§7) is the case that occurs, and inventing a value there would put it into the set `/brd-package` derives the rounds from. That is the only route to a round-less `[VD#n]`/`[CD#n]`: one taken in a round always carries it |

**Which prefix a decision gets is fixed by the tag of the question it answers, not by who typed it.**
A question tagged `[V]` produces a `[VD#n]`; a question tagged `[C]` produces a `[CD#n]`
(`references/interview-tagging.md` §1). A delivery-team position does not become a `[CD#n]` because
the customer later nodded at it, and a customer answer captured in free text does not become a
`[CD#n]` at all until an operator confirms it (D14) — the register records confirmed decisions, and
normalising prose into one is inference, not authority.

**`defects` is not `evidence`, and the separation is load-bearing rather than tidy.** `evidence`
holds `[CG#n]`/`[DG#n]` findings and §6 **inspects that list** — the will-change rule fires when
every finding in it carries `horizon: will-change`. A `[CDF#n]` placed there would change what D19
fires on, in the one rule whose whole purpose is that a decision resting on ground that is about to
move says so. The two fields also answer different questions: `evidence` says what established the
premise, and `defects` says what has to be repaired before the position can be delivered.

**`settles` is neither `evidence` nor `defects`.** `defects` names defects in the *code*, `[CDF#n]`,
that a position has to repair; `settles` names defects in the *customer's document*, `[DEF#n]`
(`references/brd-format.md` §3), that the decision answers — and it is what lets `/brd-reconcile`
resolve each one `resolved-by: <SLICE-KEY>/[CD#n]` (`references/brd-format.md` §4) from a field
rather than from a reading of the customer's prose.

`options_considered` and `chosen` do not apply to an `[AS#n]`, which is not a choice; §7 accounts
for all thirteen of these fields on an assumption record, one by one.

### 1.1 How a record is serialised

The table above fixes the field **names**; this section fixes the **bytes**, for the reason
`workflows-core:grounding-format` §2.1 gives for a finding and which applies here with more force:
this file is **parsed by field**, not read as prose — `commands/brd-package.md` restates its
records into a customer prompt and derives the rounds a BRD has from the `round` values,
`commands/brd-reconcile.md` matches records to answers and sweeps them by field, and §4 writes
individual fields in place on a record another run wrote. A writer free to choose between two
renderings produces a register whose readers disagree about what is in it, and a missed record
reads downstream as a decision nobody took.

- **One record per block, unfenced**, in the field order the §1 table gives, every key of a block
  at the same indentation, and **no blank line between one key of a block and the next**. The
  `# Decision register: <BRD-KEY>` header line stands alone at the top.
- **A blank line inside a block scalar's content is part of the value, not a boundary**, and §4
  requires one: a cause is appended to `argumentation` as a **closing paragraph** beneath what the
  field already holds, and on a `[CD#n]` beneath the customer's quotation — two paragraphs in one
  literal block scalar, separated by a blank line. A rule that forbade that would force a writer to
  fold them together, and `references/bundle-packaging.md` §6.3 tells the plugin's words from the
  customer's by exactly that separation. **So the record boundary needs a positive test rather than
  the absence of a blank line**: a boundary is a blank line **followed by a line at block
  indentation** — a key of the next record — where a blank line followed by more indented content
  is inside the scalar above it. `workflows-core:grounding-format` §2.1 carries the simpler rule
  safely because nothing appends a paragraph to a finding field; this section has §4 and cannot.
- **One space after every key's colon — never padding, never alignment**, whatever the longest key
  in that block happens to be. Alignment is a rendering choice made per block, which makes the
  bytes of a record a property of its neighbours and defeats a field-anchored scan.
- **No code fence around a record.** A fenced block reads as an example rather than as data, and
  the two readers above walk this file for records rather than for examples.
- **A multi-line value is a literal block scalar** — `argumentation: |`, and `chosen: |` in the
  outside-the-options form §1 fixes — so the customer's own line breaks and quotes survive
  unescaped and unfolded, which is what makes a quotation checkable against the package it came
  from.
- **A field that does not apply is omitted, never written empty**, per its own row above; the one
  deliberate exception is `evidence`, whose `[]` is a known value and not an absence (§1).

## 2. `argumentation` is mandatory

There is no valid record with an empty `argumentation`. Not "to be filled in later", not a restated
`statement`, not the name of whoever decided it.

**A decision without a recorded reason cannot be defended when the customer challenges it weeks
later.** The challenge arrives long after the context has evaporated: the constraint that made the
chosen option the only workable one, the option that looked better until a finding ruled it out,
the cost the rejected alternative would have carried. Without that written down, the delivery team
is defending a position it can no longer explain, in front of the party that has to live with it.
What is actually on the page — "we chose B" — reads as arbitrary, and a position that reads as
arbitrary loses whether or not it was right.

**And it cannot be safely reopened.** Reopening a decision means deciding whether the new
information changes the answer, which is impossible without knowing what the old answer turned on.
A reopening that cannot see the original reasoning is not a reopening; it is a fresh decision
wearing the old one's identifier, and it will silently drop whatever constraint the first pass
respected and the second pass never learned about.

The test for sufficiency is the one implied by both failures: **argumentation is adequate when a
reader who was not in the room can say what would have to change for the answer to change.** A
reason that survives being read back a month later names the constraint, not the preference.

## 3. Statuses

Exactly five.

| Status | Meaning |
|---|---|
| `open` | Raised, not yet settled. A decision may not be consumed downstream while it is open |
| `decided` | Settled, with `chosen` and `argumentation` filled in |
| `reopened` | Was `decided`, and a cause under §4 has reopened it |
| `superseded` | Replaced by a later decision, which the record names in a closing `Superseded <YYYYMMDD>: by [XD#m]` paragraph appended to its `argumentation` (§4); the identifier is retained, never reused |
| `withdrawn` | No longer asked for at all — the question stopped applying rather than being answered |

**`withdrawn` is first-class, and it is not a tidier spelling of `superseded`.** A superseded
decision was answered and then answered differently; a withdrawn one stopped being a question. The
case that earns it the status: the delivery team records a request — say, an amendment to the source
BRD — and the customer's answer to some *other* question makes that request unnecessary. Nothing
replaced it, and nothing about it is still true, so `superseded` would be a lie and leaving it
`open` would be worse.

Worse, specifically, in the customer's copy. **A request that is still `open` keeps appearing in
customer-facing text**, because that is what open requests are for. So the customer receives, in the
next package, a request they already dealt with — which reads either as the delivery team not having
read their answer, or as a second bite at something they thought was closed. `withdrawn` is the
status that stops the asking without falsifying the record: the request is still there, still
identified, still carrying the reason it was withdrawn, and it is no longer requested of anybody.

`superseded` and `withdrawn` are terminal. `decided` is not: §4 is the one route out of it.

## 4. Reopening is explicit

**Only two things may reopen a decision:**

1. **A new grounding finding** that bears on it — including a finding that supersedes one already in
   the decision's `evidence` list (`workflows-core:grounding-format` §3). A verifier's `contradict`
   on an on-file finding is recorded as a supersession (`workflows-core:grounding-format` §8), so it
   reaches this cause like any other supersession, and so is a grounding run's move of an on-file
   finding's horizon (`workflows-core:grounding-format` §5).
2. **An incoming customer decision** that contradicts or constrains it.

Nothing else. Not a later reader's discomfort, not a fresh idea, not a review pass that would have
decided differently. A decision the register holds as `decided` is settled until one of those two
arrives.

**The reopening records its cause**, naming the finding or the customer decision that triggered it.
A `reopened` record whose cause is unnamed is indistinguishable from someone simply changing their
mind, and once one of those exists nobody can trust that the rest were caused either. The cause is
also what the eventual re-decision is argued against under §2: it names what changed, so the new
`argumentation` can say why that change moves the answer — or, just as legitimately, why it does not
and the original `chosen` stands.

**The cause is written in the record's `argumentation`**, as a closing paragraph appended beneath
what the field already holds and opening `Reopened <YYYYMMDD>:` — never in place of the reasoning
the re-decision has to argue against. None of §1's thirteen fields is a cause, and `argumentation`
is the one that already answers *why*. On a `[CD#n]`, whose `argumentation` is the customer's own
reason quoted, the paragraph follows the quotation and leaves it exactly as written; its opening
marker is what tells the plugin's words from the customer's (`references/bundle-packaging.md` §6.3).

**A supersession names its replacement the same way**, because §3's `superseded` says the record
names the decision that replaced it and a status alone names nothing: a closing paragraph appended
to `argumentation` beneath what the field already holds, reading `Superseded <YYYYMMDD>: by [XD#m]`
— `[XD#m]` being the replacing record's id, `[VD#m]` or `[CD#m]`, bare, since a supersession is
always by a record of the same BRD's `decisions.md`: a `[VD#n]` by the `[VD#m]` that answered its
question put again, or by the `[CD#m]` a customer's answer replaced it with, a `[CD#n]` by the
`[CD#m]` that answered its, and an `[AS#n]` by the `[CD#m]` that settles it (§7) — where the
replacing record is of the other prefix it is still in the same file, which is what a bare id
resolves against (below). **Superseding moves `status` to `superseded` and adds that
paragraph; nothing else on the record moves** — it is neither a re-decision nor a reversion, so none
of the per-field rules below applies to it, and the superseded position stays on the page exactly as
it was taken, which is what lets a reader see what was replaced. Every writer of `superseded` writes
it this way: `commands/brd-interview.md` for a `[VD#n]` reading `open` or `decided` whose question
a later round put again and answered — one the will-change rule held, or a reopened one a
propagation sweep's reversion returned to `open` or `decided` while its question waited (*A
decision the re-grounding moved*); and `commands/brd-reconcile.md` for a
`[VD#n]` or `[CD#n]` a later customer answer replaces and for an `[AS#n]` a `[CD#n]` settles (its
*Freeze the customer decisions* phase, steps 2 and 3; §7).

**Cause 1 has a command that observes it.** A `commands/prd-ground.md` `--rebaseline` pass marks
every finding it replaces `verdict: SUPERSEDED`, and so does any `commands/prd-ground.md` run whose
verifier contradicts an on-file finding, or whose horizon pass moves one's horizon, appending its
successor; and `commands/brd-interview.md` (*A decision the re-grounding moved*) takes each
`decided` record §6 did not hold, **any** one of whose `evidence` findings a run has superseded — a
supersession replaces findings one at a time, so waiting for the whole list would leave the record
standing on a premise the code no longer shows: it reopens the record, naming the successor findings
as the cause, unless those successors confirm its premise by the test that section fixes, and puts
its question in the next round it opens. A finding of the list no run superseded stands as cited and
takes no part in the test. That section also fixes which findings are a superseded finding's
successors. The test is mechanical and the same for a `[VD#n]` and a `[CD#n]`: every superseded
finding in the record's `evidence` carries a `prior_verdict` — the verdict it carried, kept on it
when it was superseded (`workflows-core:grounding-format` §2) — and has at least one successor, and
every successor carries that verdict and the superseded finding's own `horizon`, which superseding
leaves as it stood. A finding carrying no `prior_verdict`, superseded before the field existed,
confirms nothing, and nor does one no successor answers: "every successor" is not read as true of
none. The horizon is compared, not required to be `current`, because a record §6 left `decided` may
rest on a `will-change` finding beside a `current` one, and a pass before the prerequisite ships
re-grounds it `will-change` again — the ground as it stood. A successor that has moved from
`will-change` to `current` does not confirm: the prerequisite shipped, and the premise the record
was decided on moved with it. A record whose successors confirm is not reopened — the ground was
re-derived and came back as it stood, which is no cause.

**This section names one set — a record's *decision fields*, all thirteen §1 defines — and fixes
what each of them does when a record already on file is written again.** A re-decision and a
reversion both write in place, against the record's own id. **A file that needs to name the fields
of a decision record cites this set, never part of it**: an enumeration written somewhere else is
an enumeration that omits whichever field mattered on the day it was read, which is how a
stale-reference sweep came to leave `settles` — the one structured field holding a `[DEF#n]` —
outside a rule built for exactly that id.

**Seven are written afresh** — `statement`, `options_considered`, `chosen`, `evidence`, `defects`,
`conditional_on` and `status` — each under the rule §1 gives it, and `evidence` and `conditional_on`
under §6's will-change rule as well; on an `[AS#n]`, only those of them §7 admits, an assumption
having no `options_considered` and no `chosen`. **`argumentation` is appended to and never
rewritten**: what stands in it stays, and both writes go after it. **`round`, on these two writes
and on no other**, takes the round that produced the position now on record — on a re-decision, the
round that re-decided it; on a reversion, the round of the position being restored, a propagation
sweep being no round at all and having none of its own to give — omitted entirely, as §1 requires,
where the position it names came from no round. That is this section's rule for a record written
again, and **not** a redefinition of the field: what a record takes when it is **first** written is
§1's, and a `[CD#n]` takes there the round that raised the question the customer answered
(`commands/brd-reconcile.md`, *Freeze the customer decisions*). **`consumed_by` returns to `none`**
on both, because a downstream artifact that drew on this record drew on the position just replaced
and has to be shown it again — which is exactly
what §1's starting-at-`none` rule is for, and what lets `commands/create-prd.md`,
`commands/create-ard.md` and `commands/specify.md` report the record as unconsumed at their own
altitude. **`altitude` stays**: re-deciding moves the answer, never the level the question sits at.
**`id` and `settles` stand** — the record's identity, and the `[DEF#n]` the `[C]` question it
answers was raised by, which the answer's being re-taken does not change. That is all thirteen.

A **re-decision**, taken by the run that reopened the record or by a
later one, writes its argumentation after the `Reopened` paragraph: why the change moves the answer,
or why it does not. A record is re-decided only by an answer to a question that puts it again, and
whichever run reopened it, a later one reaches it: `commands/brd-interview.md` puts the question of
every record reading `reopened` whose question no round holds in flight (its *A decision reopened
elsewhere*), and the answer re-decides the record the question's `- **Re-puts:**` line names —
`commands/brd-interview.md` for a `[VD#n]`, `commands/brd-reconcile.md` for a `[CD#n]`. A **reversion** — `commands/brd-reconcile.md`'s propagation sweep writes
one, and nothing else does — returns those fields to the position that stood before the prerequisite
moved it and appends its `Reverted <YYYYMMDD>:` paragraph. Neither replaces the `Reopened` paragraph
or anything above it, so the record carries the original reasoning, each cause and each answer to a
cause in the order they happened.

**Where a reversion reads the position it restores, and what it therefore cannot recover.** The
seven and `round` were written afresh when the position moved, so the record's own fields hold what
replaced it and no earlier value: **the only place an earlier position survives is
`argumentation`**, which this section never rewrites — its original reasoning, each `Reopened`
paragraph and each re-decision's answer to one. A reversion is argued from those paragraphs, and it
restores only what they establish. **A field they do not establish is not recoverable here**, and no
value is invented for it: a reversion the record cannot support is not written, the item is not
recorded `reverted`, and it goes to whoever can settle it — `commands/brd-reconcile.md`'s
propagation sweep states what that means for its own disposition picker. This is a bound on the
reversion, not on the sweep's other three dispositions, none of which restores a value.

**A cause from another BRD is named with that BRD's key, in prose.** That is the propagation
sweep's case: `commands/brd-reconcile.md` reopens a dependent's record on a `[CD#n]` the
prerequisite's own reconciliation froze, and its `Reopened` paragraph names it `<BRD-KEY> [CD#n]`,
the one qualified prose spelling `references/bundle-packaging.md` §6.2 fixes. The same sweep's
`reverted` and `withdrawn` writes name the changed id the same way, in a closing paragraph opening
`Reverted <YYYYMMDD>:` or `Withdrawn <YYYYMMDD>:` — the reason a withdrawn record carries (§3), in
the withdrawn case. **Never §5's slash shape, `<BRD-KEY>/[CD#n]`**: that is the spelling of a
structured field whose owning authority declares it — `conditional_on` is the one in this register —
and `references/bundle-packaging.md` §6.2's relation 1 reads it as qualified only in a field its
table lists. No sweep write names the changed id in one of those fields: a `reverted` write that
restores `conditional_on` restores the value the record held, in that field's own shape, and names
the changed id only in its `Reverted` paragraph. A bare `[CD#n]` names a record of the register it
sits in — the wrong one where this register holds that id, none where it does not — and this
register ships in its own BRD's package, whose citation check resolves a bare id the same way. An
unnamed cause and a cause naming the wrong record fail alike: neither says what changed.

The rule's purpose is not ceremony. A register that can be reopened freely is a register whose
`decided` status means nothing, and a customer who signed off on a set of decisions signed off on
something that can drift underneath them. Bounding reopening to two external causes is what makes
"decided" a claim about the world rather than about the moment.

**A worked consequence — a sibling that holds decisions cannot receive a re-pointed row.** `references/coverage-ledger-format.md` §3.2 lets a parent's walk move a requirement its owner recorded `deferred-to` against onto a sibling BRD that has not been interviewed, and *has not been interviewed* is this rule read from the other end: giving that sibling new scope would put a requirement in front of a register that decided its scope without it, and neither cause above has arrived — no new grounding finding, and no incoming customer decision. So a folder holding a `decisions.md` with a `[VD#n]` or `[CD#n]` in it is closed to a re-cut. **The converse does not follow and is not stated here**: §3.2's eligibility test is broader than this clause — it also refuses a folder holding an `interview/round-*.md`, which is a customer conversation that has started whether or not it froze a record — so eligibility is never inferred from the absence of a decision record alone. This file states the rule; §3.2 executes it, and the test a run actually applies is that section's to fix.

## 5. `conditional_on`

`conditional_on: <BRD-KEY>/<decision-id>` records that **this decision is correct only while a named
decision of a named prerequisite BRD holds.** The key follows the grammar in
`workflows-core:addressing` §1; the second half names one specific decision in that BRD's own
register, never the BRD as a whole — a prerequisite carries many decisions and only one of them is
the one this position rests on.

The field is omitted entirely when the decision depends on no prerequisite. An empty or
placeholder `conditional_on` is worse than an absent one: it looks like a dependency somebody
forgot to finish naming.

**What it buys is findability.** A position built on a prerequisite is not wrong — often it is the
only sensible position available while the prerequisite is still in flight. What makes it dangerous
is that it is *invisible*: when the prerequisite's decision changes, nothing about this decision's
own text says it should be re-examined, and the drift is discovered by whoever eventually notices
that two BRDs disagree. `conditional_on` is what makes `/brd-reconcile`'s propagation sweep able to
find this decision mechanically when that prerequisite's decisions change, instead of relying on
somebody remembering — which is why that sweep takes the `conditional_on` positions first, before it
looks for anything citing a changed id in prose. A conditional decision that does not say so is exactly
the decision a sweep cannot reach.

It follows that `conditional_on` is written by whoever takes the decision, at the moment they take
it, and not reconstructed later. The person who knows the position rests on a prerequisite is the
person taking it; a sweep cannot infer the dependency from a `statement` that never mentions it.

## 6. The will-change rule (D19)

**A decision may not rest solely on a `will-change` finding.** Where *every* finding in a decision's
`evidence` list carries `horizon: will-change` (`workflows-core:grounding-format` §5), the decision
may not be closed as an unconditional `decided`. Both commands that write a decision enforce it:
`/brd-interview` refuses to close a `[VD#n]` on such a list, and `/brd-reconcile`'s *Freeze the
customer decisions* phase writes a `[CD#n]` on one with the customer's answer intact but conditional
or open rather than unconditionally decided — `conditional_on` the prerequisite where every
`will-change` finding names the same one and each names it with its BRD key, `status: open` where
they name more than one or any names a bare id carrying no BRD key, which is never resolved or
parsed into one (`conditional_on` needs `<BRD-KEY>/<decision-id>`, §5) — and lists it, with any
such unqualified value, under what still needs a human. A customer's answer does not make a premise
the code is going to falsify any firmer than an operator's does.

The reason is the one D19 states: a finding is true of a pinned commit, and a `will-change` finding
is one an approved-but-unbuilt prerequisite is going to make false. A decision resting on nothing
else is standing on ground that is about to move — correct today, wrong the moment the prerequisite
ships, and nothing in the record would say so.

Three resolutions, and exactly three — `/brd-reconcile` takes only the second and third, because
the first changes a `[CD#n]`'s `evidence`, which is copied from the question the customer was put:

| Resolution | Recorded as |
|---|---|
| Re-base it on a `current` finding | the decision's `evidence` list changes |
| Make it explicitly conditional on the prerequisite | `conditional_on: <BRD-KEY>/<decision-id>` |
| Defer it until the prerequisite ships | `status: open`, with the blocking prerequisite named |

**The resolution holds the record, never the question.** The question was answered — by the
delivery team or by the customer — so it takes its terminal disposition and its round can close;
another answer to it against the same findings would fire this rule again, so nothing is gained by
keeping it open. **A held record's exit is a later round** — and, for one written `conditional_on`,
also `commands/brd-reconcile.md`'s propagation sweep (§5), which reaches it by that field the day
the prerequisite's decision moves and may revert it or reopen it in place, as it may any `decided`
record. One held `open` carries no `conditional_on`, so the sweep's field pass never reaches it; its
citation pass may, where the record names a changed id, and may withdraw or revert it. Otherwise its exit is
the round. The round comes once the prerequisite has shipped, and **the route observes that as a
successor finding that no longer carries `horizon: will-change`**: a `commands/prd-ground.md`
`--rebaseline` pass marks every finding it re-grounds `SUPERSEDED` and writes its successor
(`workflows-core:grounding-format` §3, §5), but it keeps `will-change` on a successor until the
naming decision ships, so a supersession alone observes nothing — every pass after the pinned code
moves writes one. A verifier's `contradict` on an on-file finding writes a successor carrying the
superseded finding's own horizon, so it observes nothing either; and a run whose horizon pass moves
an on-file finding's horizon supersedes it with a successor carrying the new one, which moves off
`will-change` only where that pass saw the naming decision ship. So once every finding in the
record's `evidence` is `SUPERSEDED`, each has a successor, and no successor is `will-change`,
`commands/brd-interview.md` counts the record's question among those that make a new round askable
and puts it again in that round, under the tag it had, against the current findings (its *A decision
the re-grounding moved*); until then the record waits on its prerequisite, and that run reports it
so — except where a superseded finding is one no successor will come to, because it cannot be
matched to one — its own source cannot be decided, or it is a frame-only finding written before
such findings named their field — or because the run that retired it re-ground its frame set and found none, when the
record is put again at once, naming that finding. The answer is tested by this
rule like any other, and what it does turns on the held record's `status` as the answer's writer
reads it —
`commands/brd-interview.md` for a `[VD#n]`, and `commands/brd-reconcile.md` for a `[CD#n]`, from
the answering question's `- **Re-puts:**` line and from the register as it stood before that run
wrote anything: `open` or `decided`, the answer is a new record and the held one is `superseded` by
it (§3, §4); `reopened`, the answer re-decides it in place (below); and `withdrawn` or
`superseded`, which are terminal (§3), the held record does not move — the answer is a new record
all the same, and the earlier one is named with it under what still needs a human. **The re-put
round never completes or re-decides a held record in place** — one held `open` was never `decided`,
so §4 has nothing to reopen; what may move one written `conditional_on` in place is the sweep
above, and a record it reopened is re-decided in place, not superseded, by the answer to a question
that puts it again — `reopened`, as the answer's writer reads it, means a re-decision.

Three things the rule does not say. It does **not** forbid a `will-change` finding in an `evidence`
list — a decision resting on one `current` finding and two `will-change` ones is not caught, because
the `current` finding is ground that holds. It does **not** fire on `evidence: []`: a decision that
rests on no finding rests on no `will-change` finding either, and "every finding in the list" is not
read as true of an empty one. And it is **not** satisfied by deleting the `will-change` finding from
the list: a decision whose evidence was thinned until the rule stopped firing — to nothing, or to
something — rests on exactly what it rested on before, minus the record of it.

## 7. Assumptions — `[AS#n]`

An `[AS#n]` records **something the package asserts without evidence.** It is not a decision: nothing
was chosen, so nothing was weighed. It uses the same thirteen fields as §1, and because `/brd-package`
puts every open one of them in front of the customer (below), which fields apply is not a
detail an author may settle for themselves. All thirteen are accounted for here.

| §1 field | On an `[AS#n]` |
|---|---|
| `id` | **As-is**, under its own prefix: `[AS#1]`, `[AS#2]`, … contiguous within that prefix, assigned once, never renumbered or reused, a removed torn write aside (§8) |
| `statement` | **As-is**: one sentence, saying what is assumed — the assumption itself, never the reason for it and never the reason it is unevidenced |
| `options_considered` | **Not applicable.** An assumption is an assertion, not a choice between options; a record that weighs options is a decision and takes a `[VD#n]` or `[CD#n]` |
| `chosen` | **Not applicable**, for the same reason: there is nothing to choose from |
| `argumentation` | **Different meaning**, still mandatory: for a decision it says why this option beat the others (§2); here it says **why the package is proceeding on the assumption rather than stopping to establish it** — what establishing it would cost, and what depends on not waiting |
| `evidence` | **Different meaning**, still never blank: it holds **no** `[CG#n]`/`[DG#n]` ids, and instead carries the explicit statement of **why no evidence exists** — see below |
| `altitude` | **As-is**: an assumption sits at a level like anything else, and the spec's §7 routing needs it for the same reason |
| `conditional_on` | **As-is**, and omitted when absent: an assumption can rest on a prerequisite's decision exactly as a position can, and §5's sweep must be able to reach it for exactly the same reason |
| `defects` | **As-is**, and omitted when absent: an assumption can turn on a known code defect exactly as a position can, and the customer who reads the assumption needs the same access to what would have to be repaired |
| `settles` | **Not applicable.** An assumption answers no question, so it settles no requirement defect; a customer who confirms one does so in a `[CD#n]`, which carries `settles` only where the question it answers was raised by or carries a defect |
| `status` | **Narrowed vocabulary**, from §3's five: an `[AS#n]` reaches `open`, `superseded` and `withdrawn` only. `decided` cannot apply — an assumption is never settled by being chosen; when the customer confirms it, the confirmation is a `[CD#n]` and the assumption is `superseded` by it (below). `reopened` follows `decided`, so it is unreachable too |
| `consumed_by` | **As-is**, with the same starting-at-`none` rule |
| `round` | **As-is where there is one, and omitted where there is not.** An assumption recorded in an interview round carries that round. One recorded outside any round — `/create-prd` writing a customer-authority gap at PRD authoring (below) — **omits the field entirely**, per `workflows-core:grounding-format` §2.1's rule that a field which does not apply is omitted rather than written empty. It is not given the last closed round's number, which would claim it was in front of whoever answered that round, and not given an invented value, which `/brd-package` would read as a round and demand a round record for |

**`evidence` is the field that carries the why-no-evidence explanation.** This is the same
discipline `workflows-core:grounding-format` §2 applies to a finding asserting an absence — an
explicit statement of what was searched and why it fell short, rather than an empty field — applied
to the record whose whole content is an absence. It does not go in `statement`, which holds the
assumption and nothing else, and it does not go in `argumentation`, which answers a different
question: `argumentation` says why we are proceeding anyway, `evidence` says why we cannot do
better. A reader who confuses the two ends up with a record that argues for the assumption while
never admitting it is one.

A worked `[AS#n]` against a synthetic BRD `EPIC-008`:

```yaml
id: [AS#4]
statement: The upstream feed emits one record per transaction, not one record per batch.
argumentation: |
  Every read path this package describes assumes per-transaction grain. Establishing the
  grain needs a sample the customer has not sent; waiting for one blocks the whole package,
  and proceeding on a stated assumption the customer can correct in one sentence is cheaper
  than stalling.
evidence: |
  No evidence exists. Nothing in the pinned commit reads this feed — searched the ingestion
  paths at the pinned commit and found no reader — so the repository cannot settle the grain
  either way, and no [CG#n] was produced for it.
altitude: implementation
status: open
consumed_by: none
round: 1
```

A bare sentence with no account of its own groundlessness is a claim, not an assumption record.

**§6 cannot fire on an `[AS#n]`.** The will-change rule tests the horizons of the findings in an
`evidence` list, and an assumption's list holds none. That is not a loophole to route a shaky
position through: a record with findings behind it is not an assumption, and calling one an
assumption to escape §6 is the evidence-thinning §6 already refuses.

**Every open `[AS#n]` is surfaced in the customer prompt.** Not the ones that seem material, not the
ones somebody remembered — every open one, automatically, because the selection step is where this
rule would fail. `/brd-package` does the surfacing, twice over — once where the customer is asked to
decide, and once where they are invited to attack; this file fixes that no assumption is exempt.

**An assumption that never reaches the customer is a liability disguised as a fact.** It was written
down as an assumption by someone who knew it was one, and every reader after that meets it as a flat
statement in a package full of grounded findings. Nothing in the sentence distinguishes it from the
findings around it, so it is read as settled, built on, and argued from. The customer is the one
party who could have said "no, it does not work like that" in a single sentence — and they are the
one party who was never shown it. Surfacing every open assumption is what converts the cheapest
possible correction into one the customer can actually make.

**`/brd-interview` is not the only writer, and the second one is why this record exists at all.**
An assumption is recorded wherever the delivery team first has to assert something without evidence,
and that is not always during an interview: `/create-prd` authoring a slice's PRD reaches questions
**only PRD authoring surfaces** — a scope boundary the requirement text never drew, a rule the
acceptance criteria need and nobody stated — and some of them are settled by an authority only the
customer holds (`interview-tagging.md` §2). Written into the PRD's `## Assumptions & open questions`
alone, such a question reaches nobody: the customer never receives `prd.md`. Written as an `[AS#n]`,
it reaches them automatically, because `/brd-package` surfaces every open one. **That is the whole
route back, and it needs no new machinery** — which is the answer to the objection that a PRD-stage
question has missed the interview: the assumption record was always the mechanism for a thing
asserted without evidence, and when it was written matters less than that the customer sees it.

**Such a record carries no `round` at all, and the omission is the whole of the mechanism.** An
assumption recorded at PRD authoring belongs to no interview round. Giving it the last closed round's
number would claim it was in front of whoever answered that round; giving it any *invented* value is
worse, because **`round` is read, not just displayed** — `/brd-package` derives the set of rounds a
BRD has from the distinct `round` values across every record in it — `[VD#n]`, `[AS#n]` and `[CD#n]` alike — and then requires
an `interview/round-<N>.md` for each. A record carrying a value no round record answers to makes the
BRD permanently unpackageable, which is the precise opposite of why this record exists. Omitting the
field leaves that derivation reading exactly the rounds that happened, and `[AS#n]` records with no
round contribute nothing to it — which is correct, because they came from no round.

An `[AS#n]` that the customer confirms does not silently become a fact: their confirmation is a
customer decision, entering the register as a `[CD#n]` under §1's confirmation rule (D14), with the
assumption recorded as `superseded` by it — its closing `Superseded <YYYYMMDD>: by [CD#m]` paragraph
naming that decision (§4). An `[AS#n]` the customer contradicts is `superseded` the
same way, by the decision that contradicts it, and everything that was built on it is reopened under
§4 — the incoming customer decision is precisely one of the two causes that rule admits.

## 8. Torn writes

`commands/brd-interview.md` writes a round's deliverables in one phase, *Write the register and the
round record*, and in one order: `code-defect-log.md`, then `decisions.md`, then
`interview/customer-questions.md`, then `interview/round-<N>.md` **last** — the log first, so a
counted decision never cites a `[CDF#n]` that is on no file. **The round record is the commit
point**: a round's deliverables count only once its record names them. Two writes sit outside that
order, each keyed to the record so that no interruption can falsify it: a **baseline** line,
appended to a round record that predates the lines below before anything new is written, and each
**re-disposition** of a `[CDF#n]`, applied to the log only **after** the round record names it. A run that stops
between those writes — a crash, a lost session, a context exhausted mid-phase — leaves items on disk
that claim a round no record holds, and a reader that counted them would act on questions nobody
recorded asking and decisions nobody recorded taking. Such an item is a **torn write**. This section
defines it once; every reader cites it and none restates it.

**An item stamped with round N is a torn write where `interview/round-<N>.md` in the same BRD folder
does not exist, or does not name it.** The items, what stamps each with a round, and what naming it
means:

| Item | Stamped with round N by | Named by round N's record where |
|---|---|---|
| a `[VD#n]` whose `argumentation` carries no `Reopened` paragraph | its `round: N` | a question in the record carries the state *decided* naming that id |
| an `[AS#n]` | its `round: N` | the record exists: an assumption is recorded only by the run that generates its round (`commands/brd-interview.md`, *Generate the round's question set*), and that run's write of the record is its first |
| a `[CDF#n]` (`references/code-defect-log-format.md`) | its `round: N` | one of the record's `code defects:` lines names it raised, or its `code defects on file:` baseline line lists it; or a record that is not itself a torn write cites it in `defects`. A record carrying neither line was written before both existed, and names every `[CDF#n]` of its round — no run that writes to such a record leaves it so (the baseline, below) |
| an entry in `interview/customer-questions.md` | its heading, `## Round <N>, question <position>` | the question at `<position>` carries the tag `[C]` in its last recorded state — *held for the customer*, or *answered by the customer* |
| a `- **Requirement defect:** [DEF#n]` line on an entry that is not itself a torn write and carries no `- **Re-puts:**` line | its entry's heading | one of the record's `requirement defects:` lines lists that `[DEF#n]` asked, or its `requirement defects on file:` baseline line lists it. A record carrying neither line was written before both existed, and names every such line — no run that writes to such a record leaves it so (the baseline, below) |

**Nothing else is ever a torn write**, and four things in particular are not:

- **A record carrying a `Reopened` paragraph** (§4). It was on file before the run that last wrote
  it, so no rule may remove it. A re-decision a stopped run wrote onto it stands and is counted:
  what it replaced survives only in `argumentation` (§4) and cannot be restored. A reopen a stopped
  run wrote stands too, and the question that run held for it, never on a counted record, is put
  again by `commands/brd-interview.md`'s *A decision reopened elsewhere*.
- **A `[CD#n]`.** `commands/brd-reconcile.md` mints it by its own rules, and a customer's answer is
  never removed by a rule about another command's interruption.
- **A record carrying no `round`** (§1, §7), and an entry whose heading has not that form.
- **A change made in place to an item the stopped run did not first write** — a reopen — which is
  not stamped with that run's round and stands. A `[CDF#n]`'s re-disposition is not among them: it
  reaches the log only after the round record names it (below), so a stopped run leaves none. **One
  exception**: a `Superseded <YYYYMMDD>: by [VD#m]` paragraph naming a `[VD#m]` that is a torn write
  is part of that torn write. A reader reads the record it sits on as it stood before it, with the
  `status` it held before that supersession, and the removal below restores exactly that. Superseding
  moves nothing else (§4), and `commands/brd-interview.md` supersedes only a record reading `open` or
  `decided`, so that status is read off the record's other fields by §6: `open` where it carries no
  `conditional_on` and every finding in its `evidence`, of which there is at least one, carries
  `horizon: will-change` — the only shape in which §6 lets a `[VD#n]` stand `open` — and `decided` otherwise, a
  held record written `conditional_on` and a reverted one alike.

**A reader never counts a torn write.** A torn record is read as absent from the register, a torn
entry as absent from the question set, and a torn defect line as absent from its entry. The test
reads the worktree's round records, never a ref: whether a round record has merged is
`workflows-core:phase-handoff`'s question and not this one. A round record that exists and cannot be
read decides nothing; a reader that needs the answer treats the item as undecidable, by its own rule
for an unreadable input.

**`commands/brd-interview.md` removes torn writes, and nothing else does.** Its *Write the register
and the round record* phase removes every torn write in this BRD's folder in the same writes, before
it appends its own, restoring each `superseded` paragraph above; the path on which it opens no round,
itself a completed run, does the same before its handoff and reports what it removed. That removal is the one deletion any run makes inside a register,
a question set or a log it leaves standing, and it deletes nothing any reader ever counted. **Its *Resolve inputs*
phase reports each torn write it finds**, by id or heading, so an operator sees what an interrupted
run left before anything is removed.

**The baseline.** A round record that `commands/brd-interview.md` is about to write to — a round it
resumes or re-opens — and that carries no `code defects:` line, or no `requirement defects:` line,
was written before that line existed, and the table above reads it as naming every item of its kind
in its round. That reading is right for the items on file when the run began, and wrong for any this
run writes, so **before its first write of the round's deliverables** the run appends to the record
a baseline line for each line it lacks, naming the known set exactly — the items of that kind the
run read at its start, none of them a torn write:

```
code defects on file: [CDF#n], …
requirement defects on file: [DEF#n], …
```

— each reading `none` where the set is empty. From then on the record carries a line of that kind,
so the pre-line reading no longer applies to it, and an item this run writes counts only once a line
the record's later writes carry names it. The baseline names nothing new, so an interruption right
after it falsifies nothing. **A baseline line is not an account line**: `commands/brd-interview.md`'s
*Resolve the round* reads round 1's `requirement defects:` account line to learn whether the
requirement-defect source has run there, and a `requirement defects on file:` line never answers
that test.

**A re-disposition is written after the record that names it.** A `[CDF#n]`'s `disposition`, with
the `blocked_on` that goes with it, moves in the log only once the round record's `code defects:`
line has named the move — `re-dispositioned [CDF#m] #k <old> → <new>` — so a run that stops before the
record leaves the entry as it was, and the next run offers the re-disposition again. **`#k` orders
one `[CDF#n]`'s moves**: `k` is one more than the number of numbered moves counted round records
already name for that `[CDF#n]`, so it is read off a known set and never off a date or a round
number — round numbers are not time order, since a `--round N` re-open writes an earlier round's
record after later rounds exist. A move a torn run numbered was never counted, so the next run
reuses its number. **The latest move is the one with the highest `k`.** A move reported before the
`code defects:` line existed carries no number: it was applied to the log in the run that reported
it, so there is nothing to complete, and it ranks below every numbered move and counts toward no
`k`. **A run that stops after the record and before the move is completed by the next**: every run
of `commands/brd-interview.md`, at its start, reads the latest move any counted round record names
for each `[CDF#n]`, and where the log still reads that move's `<old>`, applies `<new>` — the latest
only, so a later move back is never undone by an earlier one. Until it does, the log
disagrees with a counted record: a reader that only reads takes the record's `<new>`, and one that
ships the log whole refuses it as it refuses a torn write (`commands/brd-package.md`, Phase 0
step 5c).

**Ids.** A rule that continues an id sequence from the highest id on file reads a torn write as on
file, so no id ever names two blocks at once. A number a removed torn write held may be assigned
again, since nothing counted ever named it, and one assigned after it before the removal leaves a
gap. That gap is the only break in §1's contiguity, and in `references/code-defect-log-format.md` §2's.

**A round record written and not yet handed off is not a torn write.** Its items are named, and they
count. They are simply on no ref — the state a declined handoff leaves, with the same remedy, which
`commands/brd-package.md` names where it gates the register, the question set and log, and the
round records (Phase 0 steps 6, 6b and 7).

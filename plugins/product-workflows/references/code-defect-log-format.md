# Code-defect log format (embedded authority)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

The canonical shape of the BRD-to-PRD route's **code-defect log**: the record every `[CDF#n]`
carries, the five dispositions one can hold, the rule that every entry cites a verified `[CG#n]`
for the behaviour and names its intent basis separately, and the two spellings `blocked_on` takes.
Design authority: `docs/superpowers/specs/2026-09-08-code-defect-record-design.md` (removed from the tree 2026-09-23; `git show 62e791e8:docs/superpowers/specs/2026-09-08-code-defect-record-design.md` retrieves it).

**Written by `commands/brd-interview.md`**, which is the only writer; **shipped to the customer**
by `commands/brd-package.md`, per `references/bundle-packaging.md` §1.1; and **read by more than
those two** — among them `agents/brd-package-reviewer.md`, which raises a finding where an
`argumentation` asserts a recorded defect that no `defects:` field names, `commands/brd-package.md`'s
own Phase 0 gate, `commands/brd-reconcile.md` (its inputs and its propagation sweep, which reaches a
dependent's log), `/prd-proposal`'s defect sweep (`references/proposal-format.md` §7) and
`agents/proposal-reviewer.md`, which confirms a driver's cited `[CDF#n]` is on file. `grep -l
'code-defect-log' commands/*.md agents/*.md references/*.md`, run from this plugin's root, lists
every file that names the log. It is not a list of readers in either direction: a file may name
the log only to say it is a different register, and a command that reads it only through a
reference appears as that reference — `/prd-proposal` does, through `references/proposal-format.md`
§7, and its own command file is not in the list. **Every reader, whichever route it reaches the log
by, never counts an entry `references/decision-register-format.md` §8 calls a torn write.**

## 1. Why this is not a grounding finding

`workflows-core:grounding-format` §1 fixes grounding's question as *"is this specific claim true of
this specific commit?"* and states that grounding **adjudicates, it does not scope**. A `REWRITTEN`
verdict says the code does X. It says nothing about whether X is intended.

Calling X a defect is a claim about the code's **own intent**, which grounding has no authority over
and no field for. A finding with an opinion attached is not a record. So every entry here splits the
two halves: the `[CG#n]` supplies the behaviour, and this record supplies the intent and what says
so.

**The family's sibling precedent is `workflows-core:source-truth` §7.5**, which writes
`<KEY>-implementation-gaps.md` on the documentation route. That artifact is a draft to file elsewhere
rather than a register — no bracketed id, no status, no disposition — and its fields are
documentation-run specific. It is named here so that a reader looking for a code-defect record finds
the two that exist rather than building a third.

## 2. The record

Each `[CDF#n]` carries:

```yaml
id: [CDF#1]
statement: <one sentence — what is wrong>
behaviour: [CG#12]
intent: <one sentence — what the code is supposed to do instead>
intent_basis: <a file:line or document path | `operator-judgment` — <why>>
disposition: open | in-scope | out-of-scope | conditional | withdrawn
blocked_on: <what would settle the scope question>   # required when `conditional`, omitted otherwise
round: 2
```

| Field | Notes |
|---|---|
| `id` | `[CDF#1]`, `[CDF#2]`, … — contiguous, assigned once, **never renumbered and never reused**, with no terminal-status qualifier: unlike a decision, this record has no state a later run may reopen. A re-run continues from the highest id on file. The one exception is an entry a stopped run left, which no round record names: `references/decision-register-format.md` §8 calls it a torn write, no reader counts it, and `/brd-interview` removes it |
| `statement` | one sentence stating what is wrong, not the investigation that found it |
| `behaviour` | exactly one **verified** `[CG#n]` in this BRD's own `grounding/code-grounding.md`, whose verdict is one that states what the code does — `CONFIRMED`, `AMENDED`, `REWRITTEN` or `FALSE-FRIEND` (`workflows-core:grounding-format` §3). There is no entry without one. **`NOT-PROVABLE` does not qualify**: it is the correct and final answer that the repository cannot settle the claim, so it establishes no behaviour for an `intent` to be judged against, and an entry resting on one would assert a defect nothing found. **Nor does a finding whose verifier `outcome` is `unprovable`**, whatever verdict it keeps: the verifier could not settle the claim either way (`workflows-core:grounding-format` §8), so its verdict states a behaviour nobody confirmed. An entry already on file that cites one stands as written — `behaviour` never moves once written (`commands/brd-interview.md`, its re-disposition bounds) — so this binds an entry's first raise, never one raised before it. Neither does `SUPERSEDED`, whose premise a later finding replaced — cite that later finding instead. `commands/brd-interview.md`'s Phase 6 offer fires on the narrower three, which is a trigger and not this rule: an entry may be raised against a `CONFIRMED` finding at any point |
| `intent` | one sentence stating what the code is supposed to do instead |
| `intent_basis` | what says so — §3 |
| `disposition` | one of the five in §4 |
| `blocked_on` | **required when `disposition` is `conditional`, omitted otherwise** — §5 |
| `round` | the interview round the defect was raised in, per `references/interview-tagging.md` §5 |

**Four fields are absent, and each absence is a rule.** There is no `commit`, no `repo` and no
`evidence`: the cited `[CG#n]` carries all three, already verified, and restating them is the drift
`workflows-core:followup-emission` §1 forbids as *"link, never restate"* — a defect whose location
the finding's evidence does not cover is a defect that finding did not establish. There is no
`altitude`: a code defect is always implementation altitude, and a field with one legal value is
noise that invites an author to fill it wrong. There is no `consumed_by`: nothing downstream draws
on a defect, so the workflow's altitude routing has nothing to route.

**Every field here is customer-visible prose.** The log ships in the review package
(`references/bundle-packaging.md` §1.1), so `statement`, `intent` and an `operator-judgment`
reasoning are written to the standard `references/decision-register-format.md` §2 sets for
`argumentation`: name the constraint, never the internal preference, and never internal disagreement
about the package. This is not a new discipline — it is the one every other shipping record in the
folder is already held to.

## 3. `intent_basis` has exactly two shapes

Either a pointer into a repository or a document that says what the code should do — a `file:line`,
a schema, a test, a sibling code path, a documentation page — or the literal `operator-judgment`
followed by the reasoning.

That split is the field's whole purpose: it makes *"is there something that says so, or is this a
person's call?"* a property of the record rather than a matter of prose tone. Both are legitimate.
Only one of them is checkable, and the record has to say which it is.

## 4. Dispositions

Exactly five.

| Disposition | Meaning |
|---|---|
| `open` | Raised, not yet dispositioned |
| `in-scope` | The repair is part of the work this route is scoping |
| `out-of-scope` | Recorded, and deliberately not this engagement's work |
| `conditional` | Cannot be settled until something else is; carries `blocked_on` (§5) |
| `withdrawn` | The intent basis turned out to be wrong; it is not a defect |

**A code defect never resolves itself on this route, and `withdrawn` is not the back door.** There is
no `fixed` disposition, because nothing on the BRD-to-PRD route builds anything and no command can
observe a repair. `withdrawn` means one thing only — the intent basis turned out to be wrong, so
there was never a defect — and using it for a defect that was fixed would put a false statement in a
document the customer reads. A repaired defect keeps whatever disposition it had: this log records
what was true of the pinned commit, exactly as the finding it cites does.

## 5. `blocked_on` has exactly two spellings, and that is this file's to fix

`conditional` exists for the scope question that cannot be settled yet — *"whether the new surface
renders this is a property of code nobody has written"*. That is not a decision in anyone's
register, so a field accepting only `<BRD-KEY>/<decision-id>` would force an author to invent one,
or to assert the repair is in scope and contradict their own stated boundary.

So `blocked_on` takes either: the qualified `<BRD-KEY>/<decision-id>` naming one specific decision in
a named prerequisite's own register, exactly as `references/decision-register-format.md` §5's
`conditional_on` does; or **prose naming no bracketed identifier.**

**The second constraint is not stylistic.** The log ships, so `blocked_on` reaches the bundle, where
`references/bundle-packaging.md` §6.2 relation 1 discharges *"a structured field whose format another
authority fixes"* and says that a new such field *"is that authority's to declare"*. This file is
that authority, and fixing both spellings is what keeps `blocked_on` out of the state §6.2 has to
handle for `workflows-core:grounding-format` §5's `prerequisite` — which fixes no spelling, so an
unqualified value there has to be **reported** rather than resolved, because a silent pick lands on a
real record of the wrong package and the check goes green.

## 6. Non-goals

- **A code defect is never a customer question.** The customer sees every entry, because the log
  ships; the operator settles every disposition. A defect does not become a `[C]` and never reaches
  `interview/customer-questions.md`. A customer who disagrees says so in the returned review, which
  `commands/brd-reconcile.md` already reads.
- **This log holds no requirement defects.** Those are `[DEF#n]`, in `brd/brd-defect-log.md`, owned
  by the BRD that owns the source document and reached one hop up from a slice
  (`references/brd-format.md` §4). This log is **slice-owned** and there is no hop: a code defect
  belongs to the slice's own grounding, and grounding is slice-only.

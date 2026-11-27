# Interview tagging (embedded authority)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

The canonical tagging rule for the BRD→PRD workflow's interview: the three tags every question
carries **before it is asked**, the rule each tag fixes about who may answer it, what happens to a
`[G]` that grounding cannot settle, why a question carrying two tags is a defect in the question
rather than a gap in the taxonomy, and how a round opens and closes. Design authority:
`docs/superpowers/specs/2026-08-29-brd-to-prd-workflow-design.md` §6.1 and decision rows D8, D9 and
D14 in §3 (removed from the tree 2026-09-23; `git show 62e791e8:docs/superpowers/specs/2026-08-29-brd-to-prd-workflow-design.md` retrieves it). The `NOT-PROVABLE` verdict and the finding record a re-tagged `[G]` produces are defined
once in `workflows-core:grounding-format` §3 — cited here, not restated; requirement identifiers
(`[BR#n]`) are defined once in `references/brd-format.md`.

**Consumed by `commands/brd-interview.md`**, which tags every question against §1 and applies §3–§5
— its whole discipline is this file's rule — by `agents/brd-package-reviewer.md`, which applies §2's
test to a question already routed, and by `commands/brd-package.md`, which routes the `[C]` questions
into the customer review prompt and reads §5's round vocabulary at its gate, and by
`commands/brd-reconcile.md`, which writes §5's terminal disposition *answered by the customer* when
an operator confirms a returned answer, or where the question has stopped applying — a record it put again since withdrawn, or every requirement defect it carries withdrawn with its requirement while it has no record of its own — no answer frozen against it and no `Re-puts:` line — the only command that closes a held `[C]` while it is a `[C]`; the one other way a round holding a `[C]` closes is `commands/brd-interview.md` re-tagging that `[C]` `[V]` under §3, before any package has carried it, where a delivery-team answer shows it was the delivery team's to decide all along.
`commands/create-prd.md` applies §2's test outside any round, to triage a gap its grill could not
close by who could settle it, and `agents/customer-review-reader.md` cites §2 for why an escalated
`[SR#n]` reaches the customer under its own id rather than as a `[C]`.
What this file fixes is the contract every one of them is built against, so that the tag on a
question means the same thing to whichever one is holding it.

## 1. The three tags

Every question this workflow raises is tagged when it is written, not when it is about to be asked,
and the tag decides **who may answer it**. There are exactly three.

| Tag | Meaning | Who may answer |
|---|---|---|
| `[G]` | Answerable from code or design grounding | **Nobody.** The command answers it from the findings (D8) |
| `[V]` | A delivery-side design decision | The **delivery team**, with recorded argumentation. Never routed to the customer (D9) |
| `[C]` | A genuine business decision | The **customer**, and only via the review package |

The two "never"s in that table are rules, not tendencies.

**A `[G]` is never put to a human** — not the customer, not the delivery team, not the operator
watching the run. It is answered from the grounding findings, or it stops being a `[G]` by the
route in §3. There is no third path in which someone is asked "just to confirm."

**A `[V]` is never routed to the customer as a business question.** A delivery-side choice may be
*shown* to the customer as a position the delivery team has taken and argued — that is what
recorded argumentation is for — but it is never handed over as a question for them to settle.

**A `[C]` reaches the customer only through the review package**, never through a side channel, and
the customer's answer becomes a recorded decision only when an operator confirms it (D14). The
customer answering and the decision register recording an answer are two separate acts
(`references/decision-register-format.md` §1), and this file fixes only the first: who may be
asked.

**A question raised by a requirement defect is always `[C]`.** The slice that owns an open `[DEF#n]`
of a class grounding cannot settle (`references/brd-format.md` §3) raises one for it, once across
all the slices (`commands/brd-interview.md`) — which of two readings the customer meant, which of
two conflicting requirements governs, whether an obligation only a picture states binds at all. The
defect is in the customer's own statement, so only the customer can settle it. A delivery-team
preference may travel inside the question as the reading proposed for confirmation; it never turns
the question into a `[V]`, and a `[G]` part split off it under §4 takes its own tag without changing
this one.

**Tagging precedes asking, always.** A question with no tag is not asked, of anyone. The order is
load-bearing rather than tidy: a question asked first and classified afterwards has already reached
whoever it reached, and no later re-classification takes that back.

## 2. Why the rule exists

An implementer who has only the table above will route questions correctly until the first
ambiguous case, and then route one wrongly. The taxonomy is not the point; these two failures are.

**A `[G]` put to a person returns their belief about the system rather than the system.** Ask
someone whether the current system expires stale approvals and you learn what they think it does —
which may be what it did two releases ago, or what they specified and assumed was built, or what
the screen appears to do. The answer arrives in the same shape as any other interview answer, is
recorded like any other, and becomes a requirement. Nothing downstream distinguishes it from a fact
established at a pinned commit, and nobody re-checks a settled question. The repository could have
answered it exactly, and instead a recollection is now load-bearing (D8).

**A `[V]` dressed as a `[C]` extracts authority the customer never meant to give and cannot defend
later.** Asking the customer which layer holds a retry, or whether two records should share a table,
gets an answer — people answer questions put to them by people building their system. But they
answered a question they had no basis to answer, and the answer now carries customer sign-off. When
it turns out badly, they are holding a decision they did not understand, made on our behalf, with
our name nowhere on it. That is worse than a wrong technical choice: it is a wrong technical choice
the customer cannot repudiate and we cannot own (D9).

**The test to apply on an ambiguous question is what kind of thing would settle it.** A repository
at a pinned commit settles it → `[G]`. A trade-off between options the delivery team owns and can
argue → `[V]`. An authority only the customer holds — what the business wants to be true, what it
is willing to pay for, what it will accept as a rule — → `[C]`. Where two different kinds of thing
would settle two different parts of it, that is not an ambiguous question; it is two questions, and
§4 says so.

**The two mis-taggings are not equally recoverable, and it is worth knowing which way the asymmetry
runs.** A `[C]` mistakenly handled as a `[V]` is recorded as a delivery-team position with its
argumentation attached; when the customer sees that position and disagrees, the disagreement is
visible, the reasoning is on the page, and the position can be reopened against a recorded cause. A
`[V]` mistakenly asked as a `[C]` has already spent the customer's authority by the time anyone
notices, and there is no equivalent way to un-spend it. Neither mis-tagging is acceptable; when a
question genuinely resists the test above and cannot be split, the recoverable failure is the one
to prefer.

## 3. Re-tagging

**A `[G]` that grounding cannot settle does not silently become a question.** It becomes a
`NOT-PROVABLE` finding — a complete and legitimate terminal verdict, per
`workflows-core:grounding-format` §3 — and the question is then **re-tagged**, usually to `[V]`.
**A finding whose verifier outcome is `unprovable` is the same case, whatever verdict it keeps**:
the verifier could not settle the claim either way (`workflows-core:grounding-format` §8), so the
finding settles nothing a question could rest on, and everything below said of a `NOT-PROVABLE`
finding holds of it, the re-tag naming it with its verdict and that outcome.

**Grounding cannot settle a claim only where no repository can.** A row raises a question for an
unsettled claim only where no repository in the run settles it; a repository settles it where its
verified finding carries a verdict other than `NOT-PROVABLE` and a verifier outcome other than
`unprovable`. A finding reading `SUPERSEDED` neither raises nor settles anything: its successors are
read in its place. A BRD grounded against several repositories can hold a finding from each on a
row, and a repository that lacks the feature raises no such question on its own where a sibling
settles the row: the rule reads only whether some repository settles it, never the verdict the
lacking repository's finding is given. **That verdict may itself settle the row** — `AMENDED` or
`REWRITTEN` under `workflows-core:grounding-format` §3, *A rule about a surface the commit does not
have* — and the interview then reads it as an **absence finding**, by its own correction or
evidence, never by inference: an absence finding raises no premise-moved question either while
another repository's finding on the row is neither an absence finding nor unsettled (`NOT-PROVABLE`,
or carrying the outcome `unprovable`), and where every finding that settles the row is one, the
row raises one such question, never one per repository. So where a repository that has the surface
settles the row, the repositories that lack it raise no question for an unsettled claim or a moved
premise, whichever verdict — `NOT-PROVABLE`, or an absence finding's `AMENDED` or `REWRITTEN` —
grounding gives their absence, while a finding showing the surface present and behaving otherwise
is a genuine amendment and is asked as one. A row no
repository settles raises one question, never one per repository, carrying every finding on it
that could not settle it, and a `[G]` is never re-tagged while a sibling's finding settles it
(`commands/brd-interview.md`, *Round 1 is generated from the grounding* — its first two bullets —
and *Answer every `[G]` from the findings*).

Usually `[V]`, because of what a `NOT-PROVABLE` verdict actually reports where no repository settles
the row: the code does not answer this, so somebody must now choose. Choosing, with reasons, in a
domain the delivery team owns, is the definition of a `[V]`. Re-tagging to `[C]` is available and
is the exception — correct only when what the repository could not settle turns out to be a
business question that was mistaken for a technical one, not merely a technical question that
turned out to be hard. "The code does not tell us" is never on its own a reason to ask the
customer.

**Every re-tag records its cause.** The finding that could not settle the question is that cause —
every such finding bearing on it, where several repositories each hold one, since a row no
repository settles raises one question carrying them all — and the re-tagged question names each,
with its verdict and, where it is the cause, its `unprovable` outcome. Without the naming, the
trail from "we asked the code" to "we asked a person" disappears, and a reader months later sees only a `[V]` that looks as though it was always a `[V]` —
with no way to tell that a repository was consulted first and came back empty. That trail is what
lets the question be revisited if the repository later gains the answer.

**Re-tagging out of `[G]` is a grounding outcome; a move between `[V]` and `[C]` is not.** A question
moving between `[V]` and `[C]` is a correction of a mis-tagging, and it is handled by re-applying
§2's test or by the split in §4. It carries the same obligation to record why the tag changed, and
the same prohibition on the change being silent.

**The one such correction an interview makes after tagging is a held `[C]` that a delivery-team
answer shows was the delivery team's to decide all along** (`workflows-core:question-budget` §8):
`commands/brd-interview.md` re-tags it `[V]`, its cause recorded on a line of its own,
`- **Re-tagged:** [C] → [V] — <reason>`, which is no disposition — the question's state is the one
it then reaches as a `[V]`, written with that line, applied from that answer where the answer
alone decides it and otherwise put to the delivery team like any `[V]`. The
customer's authority is not spent by it, since the customer was never asked, and the
recoverable direction of §2's asymmetry is kept: a correction that was itself wrong is a `[V]` with
its reasoning on the page. **It is never made on a `[C]` a package has already carried** — the
customer holds it as asked, and `commands/brd-reconcile.md` matches their answer to it by round and
position — **nor on one that is a `[C]` by rule**: a requirement defect's question (§1), or a
rejected row's, whose acceptance only the customer can give. Short of a re-tag, the same answer may
put the answer the delivery team would propose beside a held `[C]`, for the customer to confirm or
correct; that answers nothing, and the question stays held.

## 4. Untaggable questions

**A question carrying more than one tag is a defect in the question.** It is split until each part
carries exactly one tag, and the parts — not the original — are what get asked.

Take a compound question against a synthetic BRD `EPIC-008`: *"Should approvals expire after thirty
days, and does the system already do that?"* It splits into three:

- `[G]` — does the pinned commit expire approvals at all, and after how long?
- `[C]` — does the business want approvals to expire?
- `[V]` — if they expire, where does the timer live?

**Answer the `[G]` part first.** Its answer routinely changes what the `[C]` part should ask: if
grounding shows approvals already expire at ninety days, the business question is no longer "do you
want expiry" but "you have expiry at ninety days today — is thirty what you want instead?", which is
a materially different question and gets a materially better answer.

**The failure the split prevents is a compound question routed by its most alarming clause.** A
question that is nine parts grounding and one part business, asked whole, is asked of the customer —
because the business clause is the one that catches the eye. The customer answers all of it,
including the part the repository would have settled exactly, and the whole answer arrives carrying
customer authority. That is D8's failure coming in through the side door, and it is harder to spot
afterwards than a plain `[G]` misrouted on its own, because the resulting record looks like a
legitimate customer decision with some technical detail attached.

**A question nobody can tag is under-specified, not untaggable.** It is rewritten until the test in
§2 has something to bite on, and it is not filed with a guessed tag in the meantime. Guessing a tag
to unblock a round is precisely how a `[V]` reaches a customer.

## 5. Rounds

The interview runs in numbered rounds, and rounds are **resumable**.

**A round closes only when every question in it has a disposition.** A disposition is what happened
to the question, not merely that someone looked at it: answered from findings (`[G]`), decided by
the delivery team with argumentation (`[V]`), answered by the customer through the review package
(`[C]`), re-tagged under §3, or split under §4 — or, for a question a person would otherwise be
asked, closed without asking it, by the rules of `workflows-core:question-budget`: *applied*, a
`[V]` an earlier answer or a decision on file determines, recorded as a `[VD#n]` naming the
decision it follows (§8 there); *merged* into another question of its tag that asks the same
substance, whose answer it takes (§5 there); *dropped*, with its reason, where no answer to it would
change what gets built, what the customer is asked or a recorded decision (§2 there); or *confirmed
in a table*, a `[V]` whose recommended answer was accepted as a table's row (§9 there). Each of
those leaves its trace in the round record, so no question disappears without one. A split
question's own disposition is *split*,
naming the parts it became; the parts carry their own dispositions in whichever round can settle
them, and the round holding a part is not necessarily the round that held the original.

**A round does not close early because the interesting questions are answered.** The remaining
questions are typically the tedious ones, and the rule exists to resist exactly the pressure to
leave them. A round with an outstanding `[C]` stays open until that answer comes back through the
package, or until its question stops applying — the record it put again withdrawn, or every
requirement defect it carries withdrawn with its requirement while it has no record of its own —
no answer frozen against it and no `Re-puts:` line — or until, before any package has carried it, a
delivery-team answer shows it was the delivery team's to decide all along and it is re-tagged `[V]`
under §3, after which it closes as a `[V]`; and the customer's turnaround is not a reason to declare
the round finished around them.

**Resumability is a property of the record, not of the session.** Because a round is a set of
questions each of which either has a disposition or does not, an interrupted run resumes at the
first question without one; it does not restart the round. This matters most for `[C]` questions:
asking a customer the same question twice is not an inefficiency, it is an invitation to a different
answer, and two customer answers to one question is a contradiction the decision register has no way
to resolve — one `[CD#n]` record holds one `chosen` (`references/decision-register-format.md` §1).

**Round numbers are permanent and contiguous, and every decision records the round that produced
it.** That is what makes it answerable later what was known at the time a position was taken — a
decision from round 1 was taken without anything round 2 discovered, and saying so requires the
round number to still be there.

**A strategic sitting is a sitting of the round being worked, and its questions are that round's.**
Where more questions are open for a person than one sitting holds, `commands/brd-interview.md`
plans strategic questions over the round's questions and every other open one on file
(`workflows-core:question-budget` §7; that command's *Plan the sittings*): a strategic `[V]`, put
to the delivery team in a strategic sitting, and a strategic `[C]`, held for the customer. Each is a
question of the round that run works, tagged like what it covers and addressed by that round and a
position like any other: it takes the next position after the highest the round holds — on its
record, or among the questions the run holds for it — in the order the plan gives them, so a later
strategic sitting's questions continue after the last. The round record carries each strategic
question's *Why we ask* and what it covers, and its state like any question's; each question its
answer closes is recorded applied from that answer's decision, in whichever round holds it, and a
question it covers that its answer did not close is asked in detail, never grouped again.

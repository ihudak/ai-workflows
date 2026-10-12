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
an operator confirms a returned answer, or where the question has stopped applying — a record it put again since withdrawn, or every requirement defect it carries withdrawn with its requirement while it holds no answer of its own — the only command that ever closes a round holding a `[C]`.
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

Usually `[V]`, because of what a `NOT-PROVABLE` verdict actually reports: the repository does not
answer this, so somebody must now choose. Choosing, with reasons, in a domain the delivery team
owns, is the definition of a `[V]`. Re-tagging to `[C]` is available and is the exception — correct
only when what the repository could not settle turns out to be a business question that was
mistaken for a technical one, not merely a technical question that turned out to be hard. "The code
does not tell us" is never on its own a reason to ask the customer.

**Every re-tag records its cause.** The `NOT-PROVABLE` finding is that cause, and the re-tagged
question names it. Without the naming, the trail from "we asked the code" to "we asked a person"
disappears, and a reader months later sees only a `[V]` that looks as though it was always a `[V]` —
with no way to tell that a repository was consulted first and came back empty. That trail is what
lets the question be revisited if the repository later gains the answer.

**Re-tagging runs out of `[G]`, not between `[V]` and `[C]`.** A question moving between `[V]` and
`[C]` is not a grounding outcome; it is a correction of a mis-tagging, and it is handled by
re-applying §2's test or by the split in §4. It carries the same obligation to record why the tag
changed, and the same prohibition on the change being silent.

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
(`[C]`), re-tagged under §3, or split under §4. A split question's own disposition is *split*,
naming the parts it became; the parts carry their own dispositions in whichever round can settle
them, and the round holding a part is not necessarily the round that held the original.

**A round does not close early because the interesting questions are answered.** The remaining
questions are typically the tedious ones, and the rule exists to resist exactly the pressure to
leave them. A round with an outstanding `[C]` stays open until that answer comes back through the
package, or until its question stops applying — the record it put again withdrawn, or every
requirement defect it carries withdrawn with its requirement while it holds no answer of its own —
and the customer's turnaround is not
a reason to declare the round finished around them.

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

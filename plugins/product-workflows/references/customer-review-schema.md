# Customer review schema (embedded authority)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

The canonical shape of the file the **customer's reviewer** writes and sends back: the twelve
sections it must carry, in the order it must carry them, the rule that puts the review's evidence
limitations in front of every claim that rests on them, and the rule that makes the review exactly
one new file. Design authority: `docs/superpowers/specs/2026-08-29-brd-to-prd-workflow-design.md`
§8.4 and §8.1, and decision rows D12, D13 and D20 in §3 — D12 governs section 1 here, D13 section
3, and D20 section 6. That design spec was removed from the tree 2026-09-23; `git show 62e791e8:docs/superpowers/specs/2026-08-29-brd-to-prd-workflow-design.md` retrieves it.

**This file is unlike every other reference here: its body is rendered verbatim into text a customer
pastes into a vanilla agent with nothing installed.** The rendered body is **everything from section
2 onward**; this preamble and section 1 are addressed to the delivery team and are not rendered.
Section 1 states what the body may therefore never contain. Read it before editing anything below
it.

Neighbouring rules are owned elsewhere and cited **here, in the unrendered part**, because the
rendered body may cite nothing the customer does not have — including this plugin's own references,
this repository's design spec, and the decision rows above:

- the degradation tier the review's section 1 must state, and how the bundle it describes is built —
  `references/bundle-packaging.md` §3 and §1
- the finding record, the six verdicts, and the `baseline-integrity` procedure whose three commands
  are handed to the customer's reviewer to re-run — `workflows-core:grounding-format` §2, §3 and §4
- the `[CD#n]` and `[AS#n]` record shape, the mandatory `argumentation`, and the rule (D14) that a
  customer answer becomes a `[CD#n]` only once an operator confirms it —
  `references/decision-register-format.md` §1, §2 and §7
- the coverage ledger's dispositions, which a returned review never sets —
  `references/coverage-ledger-format.md` §3
- the `[BR#n]` requirement identifier — `references/brd-format.md` §2; the `<BRD-KEY>` grammar —
  `workflows-core:addressing` §1
- the citation check that resolves every numbered identifier in the rendered prompt against the
  package's own records, which is why section 1 forbids one even as an example —
  `references/bundle-packaging.md` §6.2, relation 1

**Consumed by two shipped commands.** One renders the body below into the prompt a customer
pastes — from the boundary this preamble declares, never in full. The other parses a returned review
against the same body, in the two modes its reading agent supports, and confirms every inferred
decision with an operator before it becomes a `[CD#n]`. Neither command is named in this file, and
section 1 says why; both are named in `docs/reference/references.md`.

## 1. This file is rendered into the customer's prompt

The reader of the rendered text has **a vanilla agent and nothing installed** — no plugin, no
skills, no MCP server (D12). They have the bundle, and whatever repositories they were able to
obtain. Everything this file says has to be followable by that reader, on that footing, with no
further reading.

Four things this file therefore never contains:

1. **No path rooted at the plugin's install directory.** Every other reference in this directory is
   reached through the plugin-root variable; this one names no such path, because the customer has
   no plugin and therefore no root to resolve it against.
2. **No slash command name — not even the name of the command that renders this file.** A command
   name in the rendered text reads as an instruction, and the instruction cannot be carried out.
3. **No agent or subagent type, no skill name, no harness-specific tool name.** The reviewer's agent
   has one dispatcher: itself.
4. **No instruction a plugin-less agent could not follow.** The vocabulary is the vocabulary any
   agent has — *read the file named X*, *search this bundle for a file whose name contains Y*, *run
   this in a terminal*.

**Nor does it carry an identifier with a number in it, even as an example**, for a reason of its
own rather than the four above. An example of the package's identifiers is written in the
placeholder form, `[BR#n]` or `[CG#n]`, never with a number in the place of `n`. The prompt this
body is rendered into is itself a document of the bundle, and the bundle's citation check resolves
every numbered identifier in it against that package's own records: an example number names a
record nobody meant wherever the package holds one — which the customer then reads as the record the
rule is about — and stops the package as a dead citation wherever it does not. No operator edit can
repair either, because the text is rendered from this file on every run, whatever package it runs
on.

**The prohibition on command, agent and skill names is stated over the whole file, not just over the
rendered part.** A render boundary is easy to move and easy to misjudge; a file that contains no
command name anywhere cannot leak one no matter where a later editor draws the boundary. Citations
are the one thing the unrendered part may carry that the body may not, and they are kept together in
the preamble for that reason.

**Inside the rendered body, "section N" always means a section of the review being written, never a
section of this schema.** The body has two numbered spines running through it and the customer's
reviewer only has one of them; this schema's own rules are referred to by name — *the
evidence-limitations rule*, *the one-new-file rule* — so that a bare "section 4" is never ambiguous
to the reader who matters.

**Documents are named, never pathed.** The review refers to a bundle document by its filename, and
the reviewer is told to find it by searching for that name. Paths drift the moment a bundle is
extracted and renamed (`references/bundle-packaging.md` §1).

**The editor's test.** Read the sentence you just changed as somebody who has this bundle and
nothing else. If it only makes sense to a reader who also has this plugin, it does not belong in
this file.

## 2. Rule — evidence limitations come first

**The review's section 1 states what the reviewer actually had, before the review makes any claim
that rests on it.** Not the last section, not an appendix, not a footnote under the verdict.

The prompt tells the reviewer which degradation tier they are in and what their section 1 must
therefore state. A review written against unpinned repositories is a review whose code claims are
true of *an unidentified snapshot*, and a review written against no repositories at all has verified
no code claim independently. Both are perfectly good reviews — provided the reader meets that
sentence before the findings, not after them.

**A reader who meets the limitations after the findings has already believed them.** By the time the
caveat arrives, the verdict has been read, the traceability table has been skimmed, and the
confirmations have been taken as confirmations. The caveat then reads as modesty rather than as the
scope statement it is, and nobody goes back to re-weigh what they already accepted. Ordering is the
whole of the rule: a limitations section at the end satisfies a checklist and fails the reader.

Section 1 also records what the reviewer could not open at all — a document that would not render,
an image that did not arrive, a repository they could not obtain — and, when the prompt supplied a
pin-verification procedure, whether it was run and what it returned.

## 3. Rule — exactly one new file, and nothing in the package is modified

**The reviewer writes one new file and modifies nothing else.** Not the documents, not the prompt,
not the images. Nothing is renamed, moved, deleted, reformatted or re-saved. No "corrected copy" is
attached alongside the review.

This rule is stated twice in the rendered text — once at the top and once again where the output is
described — because an agent asked to review documents will otherwise helpfully edit them.

Two reasons, and both survive the file being read in isolation:

- **The two copies stay byte-identical.** The delivery team's copy of the bundle and the customer's
  are the same bytes, so every claim the review makes is checkable against a known document — months
  later, by somebody who was not in the room.
- **Nobody can otherwise tell what was sent from what was changed.** A returned package with edits
  in it has two authors and no way to separate them; the sentence under discussion may be the one
  that was delivered or the one the reviewer rewrote, and there is no third copy to adjudicate.

**Required changes to package documents are requested, never applied** — they go in the review's
section 12 as instructions to edit. That section of the review exists because this rule closes every
other channel.

The output file is named `<BRD-KEY> Customer Review <YYYYMMDD>.md`, where `<YYYYMMDD>` is **the date
you finish this review** — not any date already printed in the package. If you finish on 22 April
2026 and the key is `EPIC-008`, the file is `EPIC-008 Customer Review 20260422.md`. State that same
date in your section 1. It is the only file to send back.

## 4. The twelve sections

Numbered 1 to 12, in this order, in the returned review. (This file's own section numbers are not
the review's; the table below is the review's spine.)

| No. | Section | What it must carry |
|---|---|---|
| 1 | Review identity and evidence limitations | The `Package reviewed:` line the prompt gives, copied exactly as its own line; who reviewed, in what role, on what date; the documents and repositories actually available; the tier statement the evidence-limitations rule obliges; anything that could not be opened |
| 2 | Executive verdict | One of `approved`, `approved-with-required-changes`, `not-approved`, and one paragraph saying why |
| 3 | Approved and deferred scope | What is approved to proceed now, what is deferred, and what a deferral is waiting for |
| 4 | Requirement traceability | Per requirement in scope, exactly one of four values and no other: `confirmed` — the package's reading matches the customer's intent, including a requirement the package says will not be built where the customer agrees it should not be; `corrected` — it does not, and the row says what the customer meant; `missing` — a requirement the package left out entirely, stated as its own row; `withdrawn` — the customer drops the requirement, saying why in this row; where the package put a question about that requirement, the answer to that question goes in section 7 as every answer does, and a withdrawal the package asked about nowhere is stated here alone. Where the package includes its transcription of the customer's images, that transcription — for each image bearing on a requirement in scope — is part of its reading, and the reviewer confirms or corrects it as they do a requirement. A correction the transcription itself must carry is also entered in section 12, as a required change naming the document that holds the transcriptions by its filename and the image by its heading there |
| 5 | Code-grounding confirmations and challenges | Both: which code claims the reviewer confirms and how, and which they challenge and on what evidence |
| 6 | Design review | The design positions the package takes, confirmed or challenged, including anything that contradicts the customer's own environment |
| 7 | The decision log | One row per decision the package asked the customer to take: the answer, and the reason for it |
| 8 | Accepted assumptions and rejected alternatives | One row per assumption the package surfaced, and every alternative the customer rules out, with the reason |
| 9 | Ownership | Who on the customer side owns each approved area and each decision, and who to ask when a later question arises |
| 10 | Unresolved blockers | What prevents this proceeding, what would clear it, and who clears it |
| 11 | Readiness statement | One explicit sentence: what the delivery team is clear to proceed with, and what it is not |
| 12 | Required changes to downstream documents | Per change: which document, which section or identifier, and what must change — instructions, not edits |

**Every section is present, even when it is empty.** An omitted section is indistinguishable from an
overlooked one. A section with nothing in it says `none` and says why — *no design position was
challenged*, *no repository was available so no code claim was confirmed* — because those two
sentences mean very different things and an absent section means neither.

**The review cites identifiers; it does not mint them.** Every row that answers something names the
package's own identifier for it, copied exactly as it appears — every identifier the package uses is
bracketed, a short prefix, a `#` and the record's number, shown here as `[BR#n]` or `[CG#n]` with
`n` standing for that number, whatever kind of record it names, and a question is cited by the
round and position that identify it. The review never assigns identifiers of its own in
those namespaces: the registers on the delivery-team side own that numbering, and an identifier
whose origin is ambiguous is worse than no identifier. Plain list numbers inside a review section
are local to the review and are not identifiers.

**Every claim in the review is traceable to something the reviewer had.** A statement that rests on
the reviewer's own knowledge of the customer's environment rather than on a bundle document says so
— that is often the most valuable thing in the review, and it is worthless if it cannot be told
apart from a reading of the package.

## 5. Rules the individual sections carry

**Section 2 — the verdict is not a summary.** It is one of the three values, chosen deliberately,
and it has to survive being read next to sections 10 and 12: `approved` alongside an unresolved
blocker is a contradiction, and so is `approved` alongside a required change to a document.

**Section 4 — the section is about intent, not about bookkeeping.** The question is whether the
package understood what the customer asked for. Requirements the package missed entirely are the
highest-value rows here and are stated as their own rows rather than folded into a correction. The
review does not set the delivery team's coverage bookkeeping.

**Section 5 — confirmations without challenges are not a review.** A section holding only
confirmations has either been rubber-stamped or has hit a limit the reviewer has not admitted, and
section 1 is where that limit belongs. Each confirmation says *how* it was checked, or states
plainly that it was accepted on the package's word. Each challenge names what the package claims,
what the reviewer believes instead, and the best evidence available for it — a filename and a line,
a screenshot, or the fact that the reviewer runs the system and it does not behave that way. The
review does not assign the package's own verdict vocabulary to a claim; it confirms or challenges,
and the delivery team re-adjudicates.

**Section 7 — a decision without a reason cannot be applied.** The answer alone leaves the delivery
team unable to tell an instruction from a preference, and unable to defend the position when it is
challenged later. A question the customer declines to answer this round still gets a row, saying so
and saying what they would need in order to answer it: silence is otherwise indistinguishable from
oversight, and it will be re-asked. To drop the requirement it is about instead, give the
withdrawal as the answer to a question the package put about that requirement — this one, where it
is the only one — and say when it should be asked again, should the requirement return: a question
raised only about defects in a requirement dropped that way is closed, unless it already holds an
earlier answer of yours; any other that touches it may still be asked. A requirement marked withdrawn in section 4
alone is passed to the delivery team and drops nothing until they act on it.

**Section 8 — every assumption the package surfaced gets exactly one row**, marked accepted,
corrected, or cannot-say. Cannot-say is a real answer and is not a failure to respond. An assumption
the customer corrects is the cheapest correction in the whole loop, and it is only cheap while it is
still an assumption.

**Rejected alternatives are recorded with their reasons**, in the same section, so the option is not
re-proposed next round by somebody who never learned why it was ruled out.

**Section 9 — a review nobody owns cannot be acted on.** Roles and names on the customer side, per
approved area and per decision, so a question three weeks from now has a destination.

**Section 11 — the readiness statement is not the verdict again.** The verdict judges the package;
the readiness statement authorises work. It says what may start, and it says what may not, and it is
one sentence long so it can be quoted without being softened.

**Section 12 — this is the only channel for a change to a package document.** The one-new-file rule
closes every other one. Each row names the document by filename, the section or identifier inside
it, and what must change. A change described only as "fix the architecture section" cannot be
applied by anyone who was not the reviewer.

## 6. Where a returned review may still be provisional

A package may ship while a prerequisite it depends on is not yet customer-reviewed, provided the
prompt says so and names which positions could still move. Where it does, the review's section 3
states which of its approvals are contingent on that prerequisite, and section 10 does **not** list
the prerequisite as a blocker — it is not blocking, it is unsettled, and the two get very different
treatment on the delivery side.

A reviewer who was told nothing could move writes no such rows, and their absence then means what it
says.

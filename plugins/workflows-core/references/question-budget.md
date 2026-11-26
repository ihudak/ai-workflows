# Question budget (shared reference)

The single source of truth for how the BRD route puts questions to people: the delivery team in
`/brd-intake`'s defect walk and in `/brd-interview`, and the customer, through the block §13
carries into the package prompt. It owns which questions earn a place (§2), how many one sitting
asks (§3), the shape of every question (§4), merging (§5), ranking (§6), strategic sittings (§7),
applying each answer to the whole registry (§8), the tail table (§9), the end-of-sitting list
(§10), the account (§11) and the registry (§12). A caller reads it whole — it has no entry point —
and cites its sections by number, keeping only what is its own: which items are candidates, what an
answer writes, and when a sitting starts. Its citers are what
`grep -lE 'workflows-core:question-budget|args: "question-budget' plugins/*/commands/*.md plugins/*/agents/*.md`
lists.

## 1. Terms

- **Sitting** — one continuous stretch of questions to one person: an intake walk, one session of an
  interview round, one session of a customer working through the package.
- **Budget** — the most questions one sitting asks (§3). An asked question counts one, and so does a
  table (§9); the end-of-sitting list (§10), a question that opens or closes a sitting, and §4's
  clarifying question and "why" count none.
- **Registry** — every question of a run that a person may be asked, with its tag, the rows and
  findings it cites, and what became of it (§12). It is kept whole: no question leaves it, and the
  account (§11) proves that none did.
- **Open for a person** — a registry question still open and not carried, of a tag that person
  answers: a `[V]` for the delivery team in an interview, a `[C]` for the customer, a
  requirement-defect candidate for the operator at intake. A `[G]` is never asked of anyone
  (`product-workflows:interview-tagging` §1).
- **Strategic question** — one whose answer determines a group of detailed questions, which it
  lists as its coverage, the registry field `covers` (§7).
- **Applied answer** — a question closed without being asked, because an earlier answer determines
  it; it names that answer's decision in the field `applied_from` (§8). Neither field is ever called
  `settles`, which names the `[DEF#n]` a `[CD#n]` answers (`product-workflows:decision-register-format`
  §1).
- **Held `[C]`** — a `[C]` written for the customer that no answer has closed. **Carried** — a held
  `[C]` a package has already put to the customer: its round and position appear in a bundle on
  file, or whether a package carried it cannot be established from the bundles on file.
- **Proposal** — a held `[C]` with the answer the delivery team would give, for the customer to
  confirm or correct (§8).
- **The planner** and **the applier** — the two agents a caller dispatches: the planner merges,
  groups, ranks and plans a sitting (§5–§7, §9); the applier reads the open registry against each
  answer (§8). Each writes its whole result to a file and replies with that file's path and counts,
  never the result inline; where the caller keeps a run folder, each goes through
  `workflows-core:run-folder`'s `run-dispatch`, so a resumed run reuses its results.

## 2. The value test

A question is put to a person only where all three hold:

1. its answer would change what gets built, what the customer is asked, or a recorded decision;
2. no decision on file (§8, *What is on file*) and no earlier answer already determines it —
   otherwise it is an applied answer (§8);
3. no other open question in the registry asks the same substance — otherwise it is merged (§5).

A question that fails the first is **dropped**, with its reason, which the end-of-sitting list
(§10) and the run's final report both show, and which can be undone there; never silently. A fact
the run can read is read, never asked (`workflows-core:grilling-technique`, *Fact-vs-decision
split*).

**The budget is never a reason.** A question that passes the test is not dropped, applied, tabled
or answered to fit a sitting: one over the budget waits in the registry for a later sitting (§3).
Fewer questions come from merging, applying and planning, never from hiding an uncertainty.

## 3. The budget

**25 questions a sitting** by default. A caller that takes `--budget <N>` accepts a whole number
from 5 to 50 and stops on anything else with
`<CMD>_BAD_BUDGET: --budget takes a whole number from 5 to 50`, `<CMD>` being its own stop prefix
(`BRD_INTAKE`, `BRD_INTERVIEW`). The registry records the budget it was made with (§12); a resumed
run given `--budget` asks by the value given, passing it to `next` as `--limit`, and one given none
by the recorded value. *The budget*, anywhere in this file, is the one in force. The customer's
sittings take the default, which §13 states as a number.

**Each asked question is numbered against the budget**, `Q<n>/<budget>`, the form
`workflows-core:grilling-technique`'s *Depth* gives a capped question: a sitting whose queue empties
at `Q9/25` is finished, not truncated.

**At the budget the sitting stops**, every answer already given written first (§12, *Answers are
written as they are given*), and the rest stays open in the registry for the next sitting. The
caller then offers the next sitting now or later and, where it names one, a bulk path — the
interview's *defer the rest with one shared reason*, recorded per question, or intake's *send the
rest on as open defects*, recorded per candidate as not reviewed at intake. A bulk path is the
operator's explicit choice and never the recommended option, so nothing over the budget is closed
or sent on by default.

## 4. The question shape

Every question, in every place, stands on its own — it never leans on a question before it — and
carries, in this order:

1. **One plain line saying what is being decided**, in the reader's terms, not the plugin's or the
   code's: a tag, a defect class or an identifier may stand beside it, never in its place.
2. **What the agent saw** — why it asks, concretely: the two readings side by side, the two
   clashing rows quoted, the measure missing, the finding that left it open. A strategic question
   adds *Why we ask* and its coverage, in plain words and as a count.
3. **The options**, two to four (`workflows-core:escalation-rules` §0), each with **what it does**
   in one short line: logged and later asked of the customer, dropped, recorded as a decision.
4. **A recommendation, where the agent has one**: that option labelled
   `<label> (Recommended — <why>)`, resolved per showing through a placeholder, as
   `workflows-core:escalation-rules`' *The `(Recommended)` marker is unconditional* allows. Where no
   option is safe to recommend, the marker is left out and the question's own text says so.

And for every question:

- **Selecting the recommended option records `<why>` as the argumentation**; free text given with
  it overrides that reason.
- **"Why" is asked only for a choice with no stated reason and no free text** — a non-recommended
  option chosen bare — as one plain-text question, never after a choice that carries its reason.
- **A typed answer is read as the option it expresses**, its other words kept as the reason; **one
  clarifying question** is asked only where the text maps to no option; **the same dialog is never
  put twice**.
- **Every claim the question makes about a `[BR#n]`, a finding or the code is checked against its
  source before the question is written** — the row's text in the inventory, the finding's verdict
  and evidence in its grounding file, the code as `workflows-core:grilling-technique`'s *A premise
  about the existing system is read before it is put* reads it. A claim that cannot be checked is
  stated as unverified, or left out.
- **One question per prompt.** A table (§9) and the end-of-sitting list (§10) are the only prompts
  that carry several items.

## 5. Merging

After a round's questions are generated and tagged, and before the first is asked, questions that
ask the same substance are merged into one, which cites every `[BR#n]` and every finding the merged
ones cited. Identical text is the easy case; the same substance in other words is the one that
matters. The planner proposes each merge with its reason, the caller records it (`merge`, §12), and
the end-of-sitting list shows it, where it can be undone (§10). A merged question takes the answer
of the question it was merged into.

- **Never across a tag.** A `[V]` and a `[C]` asking the same thing are a mis-tag, corrected under
  `product-workflows:interview-tagging` §3 with its reason recorded, never merged.
- **Never a carried question**, on either side of a merge, and never into a question that is not
  open (§8, *Reach*). A question whose substance a carried question already asks is dropped
  instead, its reason `already asked as <round>/<position> in a sent package`, so it never reaches
  the customer twice; the customer's answer to the carried question is applied to the rest like any
  other answer (§8).

## 6. Ranking

The queue is ranked by **coverage first** — how many open questions an answer would close, its own
included, more first — then by `workflows-core:grilling-technique`'s **Impact × Uncertainty**, the
least certain and the most rows touched first. There is no second ranking rule. The planner writes
each question's rank into the registry, lower first, and `next` (§12) returns the open questions
strategic first, then by rank: a sitting asks them in that order, up to the budget.

## 7. Strategic sittings

**The registry is kept whole.** Every detailed question is generated, tagged and merged first;
strategic questions are planned over the registry and never replace it. Each answer closes the
registry questions it determines (§8); whatever no answer closes is still there in its detailed
wording, and is asked in detail afterwards.

**Trigger.** After generation, tagging and merging, where the questions open for a person exceed one
budget, the run says so before its first question — how many, by tag; the plan, strategic sittings
first; the dispatches it expects — and plans strategic questions.

**Planning.** The planner groups open questions into strategic questions, each in §4's shape with
*Why we ask* and its `covers`, ranked by §6. A strategic question takes the tag of what it covers:

- covering `[V]`s, it is a `[V]`, asked of the delivery team in a strategic sitting;
- covering held `[C]`s, it is a `[C]`, written for the customer — an entry of the current round,
  with a round and position like any held `[C]`, which the customer meets first (§13) — and never
  answered by the delivery team; its `covers` names open held `[C]`s of any round on file, never a
  carried one;
- covering both, it is split in two.

**After each strategic sitting** its answers are applied forward (§8), what is left is planned again,
and the run offers another strategic sitting or the detailed walk, recommending one by the **stop
rule**, measured over the questions still open for the person the sittings ask:

- at most 2 × budget open: the detailed walk is recommended;
- more than that, with fewer than 3 strategic sittings run: another strategic sitting is
  recommended;
- after 3 strategic sittings: both are offered, the detailed walk recommended.

**Split.** An operator who answers a strategic question by asking to split it, chosen or typed, has
it dropped with that reason; the questions it covers stay open, to be asked in detail.

**The detailed walk** follows: the questions left, within the budget, in §4's shape, ranked by §6,
with §9's table for the tail. How strategic sittings map onto rounds is the caller's; its record
accounts for every strategic question, its answer and every question it closed (§11).

## 8. Applying forward

**After each answer** — strategic or detailed, asked or confirmed in a table — and before the next
question, the registry is checked for every question that answer determines, worded the same or
not, across every open question on file (*Reach*). **The next question shown is never one an answer
has already closed.**

1. **Coverage first.** Each question the answered one `covers` is closed as applied from it, its
   reason the coverage, where the answer chose one of the options. A free-text answer that chose
   none sends its coverage to the applier with the rest.
2. **The applier reads the rest** — given the answer, the open questions the coverage did not close,
   and the decisions on file — and returns per question **determined** (the derived answer, the
   decision it follows and a one-line reason), **narrowed** (the question rewritten to what is still
   open) or **untouched**.
3. **It closes only what it can derive in one line.** A question it cannot derive with confidence
   is narrowed or left untouched, never closed on a guess; it stays for a later sitting, where its
   recommendation may cite the answer.

**A determined `[V]`** is recorded as a `[VD#n]` marked as applied, naming the decision it follows
(`applied_from`), its argumentation derived from that decision and the one-line reason. Every
recorded decision says how it was taken — asked, applied from a named decision, or confirmed in a
table — in the fields its caller's register format names.

**A held `[C]` is never answered by the delivery team.** Where a delivery-team answer determines
what the team would propose, the `[C]` becomes a **proposal** — "we propose X, because `[VD#m]`;
confirm or correct" — which the customer meets in a table (§13). Where the question was the
delivery team's to decide all along, it is re-tagged to `[V]` under
`product-workflows:interview-tagging` §3, its cause recorded, and then applied like any `[V]`.
Nothing but a customer answer confirmed at `/brd-reconcile` becomes a `[CD#n]`.

**A carried `[C]` is left exactly as the customer holds it**, since `/brd-reconcile` matches the
customer's answer to it by round and position: it is never rewritten, narrowed, re-tagged, merged or
closed. What the applier found about it is recorded beside it as a proposed answer, which the next
package shows.

**A deferred `[V]` may name the held `[C]`s it waits on**; once those carry a customer's answer, the
next interview surfaces it with that answer as its recommendation.

**Reach.** Applying forward, narrowing and merging reach every open question on file in the slice —
every round, rounds written before this rulebook included — save a carried `[C]`.

**What is on file.** This slice's `decisions.md`, the registers of its sibling slices under the same
parent, and those of each BRD its `depends-on:` resolves to, a decision outside the slice cited in
the cross-BRD `<KEY>/[id]` form `product-workflows:decision-register-format` §5 uses. There is no
separate artifact of principles: a principle the operator states — *a requirement that changes
working behaviour is a change, not a defect* — is recorded as a `[VD#n]`, usually the answer to a
strategic question, and applied like any other.

**When the source moves.** Where a decision an applied answer follows is reopened, superseded or
withdrawn, every answer applied from it is reopened with it, open in the registry again, and every
answer applied from those in turn (`reopen --follows`, §12). Every reopening applies this —
`/brd-reconcile`'s propagation sweep among them, following `applied_from` as it follows
`conditional_on` — so a customer-side applied answer that became a `[CD#n]` is reopened too. A
decision never stands on a basis that is gone.

## 9. The tail table

Where more questions remain than a sitting's budget allows, those an earlier decision determines,
or whose recommendation the planner rates `high`, may be put as **one table**: each row the
question, the recommended answer and its reason; accept all, or name the exceptions. The table
counts as one question of the budget. Each accepted row is recorded as confirmed in a table
(`table`, §12), so a later reader can tell it was not asked singly; each exception named returns to
the queue and is asked singly.

- **An item the agent is not confident about never goes in a table.** It waits for a later sitting,
  or is deferred.
- A table holds only what the person it is put to answers: never a held `[C]` in an interview. The
  customer's proposals are put as tables by §13.
- Intake's list of what needs no human — the candidates recorded without a question and the
  restatements noted in the inventory — is put the same way: one list, one question, all fine or
  name the ones to look at.

## 10. The end-of-sitting list

At the end of every sitting, before the sitting's answers are written to the caller's record, the
run shows what the sitting closed without asking it singly (`sitting-list`, §12):

- every answer applied in it — the question, the derived answer, what it follows — **grouped by the
  answer it follows**, so that one answer misread shows as one group;
- the merges and the drops made, each with its reason;
- the rows confirmed in a table.

It asks **once**: all correct, or name the ones — or a whole group — to reopen. A reopened question
is open in the registry again, and so is every answer applied from its decision, in turn; an undone
merge or drop reopens the question it closed. Because the list comes before the write, a question reopened there was never
recorded as decided. The list counts nothing against the budget, and a sitting that closed nothing
this way shows none. A merge or drop made before a sitting's first question is recorded with that
sitting's number, so that its list shows it.

## 11. The account

No question disappears without a trace. Every round record, and the run's final report, reconciles
per tag — `[V]`, `[C]`, and at intake the requirement-defect candidates:

```
generated + retagged in = merged + dropped + auto + applied + table + answered + deferred + open + retagged out
```

each term listing its questions — by round and position in an interview — each applied one naming
what it follows, each dropped or merged one its reason. *Auto* is a candidate recorded without a
question (intake only); *table*, confirmed in a table; *retagged* in and out, moved between tags
with its reason. At intake the terms read: asked (`answered`), recorded without a question
(`auto`), noted in the inventory or confirmed in a table (`table`), carried to the next sitting
(`open`), sent on as open by the operator's choice (`deferred`).

`account` (§12) computes it. A run whose sum does not close reports the gap as a defect of the run,
as `workflows-core:finding-triage`'s *Reporting* contract does for findings.

## 12. The registry

The registry is one JSON file, `question-registry.json`, under `scratch/` in the caller's run folder
(`workflows-core:run-folder` §1) — where the run has no folder, a `mktemp` file
(`workflows-core:run-flags` §7), which a later session cannot resume from. Only
`scripts/question-registry.py` writes it. `product-workflows` ships the script, and a command calls
it by its own plugin's path from its own text, never from this reference; the script's docstring is
its contract, and this section maps it to the rules above.

| Subcommand | What it does | Rules |
|---|---|---|
| `init` | makes the registry: the budget, and every question on file with any state a round already wrote | §3, §8 |
| `add` | adds questions, strategic ones (`strategic`, `covers`) among them | §7 |
| `merge` | closes questions as merged into another, with the reason | §5 |
| `drop` | closes a question as dropped, with the reason | §2, §7 |
| `record` | one event: `answered`, `applied`, `table`, `deferred` or `auto` closes the question; `narrowed`, `proposed` or `retagged` leaves it open | §4, §8, §9 |
| `reopen` | `--qid`, one question; `--follows <decision-id>`, every one applied from that decision, transitively | §8, §10 |
| `next` | the open, uncarried questions to ask, strategic first, then by rank, up to the budget | §3, §6 |
| `sitting-list` | one sitting's end-of-sitting list | §10 |
| `account` | the account per tag, and whether it closes | §11 |

**`init` runs once per run**, on a fresh run folder; a resumed run finds the registry there and
reuses it. A carried `[C]` is marked `carried` when it enters the registry, and the script then
refuses every event but `proposed` on it, and every merge, drop or reopen that names it.

**Its exits.** 0: it ran. 3: it refused the caller's input — rebuild the input and send it once
more; a second refusal is reported as a defect of the run, the question left as it was. 2: the
registry is absent, unreadable or invalid — the run asks nothing more, writes every answer already
given, and names the registry as the cause in its final report. 4, from `account` only: the account
does not close (§11).

**Answers are written as they are given.** Each answer is recorded before the next question is
shown: as a recorded question of the caller's run folder (`workflows-core:run-folder`'s `run-gate`,
*Interviews*; a "why" asked after a choice is the second question of a two-part answer there), and
by `record` in the registry. The caller's own record — a round record, a defect log — is written
per sitting, after its end-of-sitting list (§10), or at the run's end, as the caller says. So a
sitting that stops — at its budget, by the operator's choice, at a compaction or a restart — loses
no answer given. A round written over several sittings adds its account and `Status:` lines once, at
the run's last write, not on every write.

## 13. The customer block

The customer's agent has nothing installed, so these rules reach it as plain text: the command that
renders the customer's prompt (`product-workflows:customer-review-schema`) copies the lines between
the two markers below into it verbatim, and the rendered prompt still passes the plugin-free scan
(`product-workflows:bundle-packaging` §1.2). So the block names no command, agent, skill, plugin
path, variable or tool, cites no section of this file, and carries no numbered identifier; a
"section N" in it is a section of the review the customer writes. Each item is one unwrapped line,
as rendered output is (`workflows-core:prose-formatting`).

<!-- question-budget:customer:begin -->
**Putting the package's questions to the reviewer.** Put the questions to the reviewer in sittings, and make every question earn its place. These rules shape how you ask; the sections of the review stay as this prompt describes them.

1. **Strategic questions first.** Where the package marks a question as strategic — it says why it is asked, which other questions its answer covers, and the answer the package proposes — ask every such question before any other.
2. **At most 25 questions a sitting.** A table counts as one question; the list of applied answers at the end of a sitting counts as none. When a sitting reaches 25, write the answers given so far into the review, say how many questions remain, and offer to stop there and continue in a later sitting.
3. **One question at a time, each standing on its own:** one plain line saying what is being decided; what the package says that raises it, quoted; the options, the one the package proposes marked with its reason; and what each answer will do. Read a typed answer as the option it expresses, ask one clarifying question only where it matches none, and never put the same question twice. Ask for a reason only where the chosen answer carries none.
4. **Apply each answer forward.** After each answer, look through every question still to be asked for those the answer decides, worded the same or not, and do not ask them. Treat a question as decided only where the answer decides it plainly, in one line of reasoning; otherwise ask it, saying what the earlier answer already decided. Record each question decided this way as its own row of the decision log (section 7): the answer, the one-line reason, and `applied from <round>/<position>`, the round and position of the question whose answer it follows.
5. **Show the applied answers at the end of each sitting**, grouped by the answer they follow, so that one misread answer shows as one group. Ask once: are they all correct, or which ones — or which whole group — should be asked after all. Ask those as ordinary questions, and replace their rows with the answers given.
6. **Put proposals as tables.** Where the package proposes an answer for the reviewer to confirm or correct, put those questions together as one table — the question, the proposed answer, its reason — and ask once: confirm all, or name the ones to correct. Each row confirmed is the reviewer's answer to that question, recorded in the decision log like any other; ask each one named as an ordinary question.
7. **Requirement traceability (section 4).** For each requirement in scope, compare the package's reading with the customer's own source text. Where they match, propose `confirmed`, and put those rows to the reviewer as one table to accept, or to name the ones to look at; ask about each row where you see a mismatch on its own.
<!-- question-budget:customer:end -->

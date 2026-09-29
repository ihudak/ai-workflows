# /brd-package

Turns a **decided** BRD into a package a customer can actually review. It attacks the package before
the customer does, refuses to build anything while a single self-review finding is undisposed, then
renders a self-contained prompt and a de-Obsidianised bundle for a reviewer with **a vanilla agent
and nothing installed** — no plugin, no skills, no MCP server. It writes the self-review, the prompt,
the delivery note, and the dated bundle.

## Who runs it

`/brd-package` runs in the [pm](../roles-and-phases.md#pm--product-management) role,
cost-attribution phase `brd-to-prd` — the phase shared by every command of the BRD-to-PRD route. It
runs once the slice's own `/brd-interview` round has settled — that register, and the `[C]`
questions it held, are what this command gates on and packages.

## Synopsis

```
/brd-package <BRD-KEY> [--depends-on <BRD-KEY>…] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]
```

- **`<BRD-KEY>`** (mandatory) — the slice this run packages. `resolve-address` searches every
  level it bounds (three) — a root, a slice, an idea-route PRD folder or an Epic folder alike — because a root has to resolve before it can be refused by name;
  format-validated only, never checked against a tracker. **Only a slice is packaged**: a resolved
  root stops with `BRD_PACKAGE_ROOT_LEVEL`, naming [`/brd-split`](brd-split.md) as the way to carve one, and an idea-route PRD folder — a `PRD-`
  folder no BRD carved, carrying no `brd-link.md` — stops with `BRD_PACKAGE_NOT_A_SLICE`, naming
  [`/create-ard`](create-ard.md) and [`/specify`](specify.md) as the way that route goes on. An `EPIC-` folder stops with `BRD_PACKAGE_EPIC_LEVEL`, naming the slice the Epic sits in where it sits in one.
- **`--depends-on <BRD-KEY>`** (optional, repeatable) — declares a prerequisite BRD. Persisted
  additively to `brd-link.md`, never replacing what is already there. Any key at any level is
  admissible as the value, so a slice depending on a source-owning BRD and a slice depending on a
  sibling express identically; the declarer is always the slice being packaged. Each resolved prerequisite's own package is copied into the bundle and marked *not
  for re-review*, and each one whose decisions are not yet customer-reviewed is named to the
  customer under *what could still move*.

There is **no `--no-docs` flag**, because this command does no documentation grounding at all — see
[What it does not do](#what-it-does-not-do).

All three run flags apply to this command. `--skip-costs` (or `WORKFLOWS_SKIP_COSTS`) skips Phase 11's session-cost entry, still advancing the checkpoint and dropping any deferred cost record a ceded `/prompt-brainstorm` or `/prompt-grill-me` run left pending in this session (`workflows-core:run-flags` §5 step 3) — see [Session cost](../reference/session-cost.md). `--skip-feedback` (or `WORKFLOWS_SKIP_FEEDBACK`) narrows Phase 11's maintenance step to bugs-only, dispatching `defect-reporter` in place of `impl-maintenance` — see [Session feedback](../reference/session-feedback.md). `--enforce-model=<model>` (or `WORKFLOWS_ENFORCE_MODEL`) pins every dispatched agent in this run — `brd-package-reviewer` (overriding its frontmatter Opus pin), `workflows-core:impl-maintenance`, and, under `--skip-feedback`, `defect-reporter` — to one model, and it is also the flag that changes a degrade path: if no Opus resolves, Phase 1 otherwise degrades `brd-package-reviewer` to the best-available model and records it, which does not happen under enforcement since the enforced model is used instead — see [Model routing](../reference/model-routing.md).

## Everything it sends is read outside your organisation

That single fact is what the command is built around. What it keeps for you — its adversarial
self-review, below, and the run's own bookkeeping — never goes in the bundle or the email. The
customer's reviewer has the bundle and whatever repositories they were able to obtain, and nothing
else: no plugin to resolve a path against, nobody to ask what a citation means, and no way to tell a
missing file from a withheld one.
So the rendered prompt, the delivery note and every document in the bundle carry **no path rooted at
the plugin's install directory, no `references/…` citation, no slash command, no agent or skill name,
and no `§` section reference** of the plugin's own — the rules in
[`bundle-packaging.md`](../../references/bundle-packaging.md) §1 and
[`customer-review-schema.md`](../../references/customer-review-schema.md) §1.

**How the command guarantees that** is a property of its phase order, not of its prose. The review
schema is rendered out of its own file from the boundary that file declares, never in full — the
part above the boundary is where that file deliberately keeps its citations. Every part of the
prompt is assembled from a named artifact rather than written fresh. The de-Obsidianising pass
renders a copy and never edits a source. And the plugin-free scan runs last, over the *finished*
text of the prompt, the note and every bundle document — a hit **stops the run and never sanitises**
(inside the customer's own verbatim content, or a locator naming their own files and headings, it
is reported for the operator to rule on instead), because a citation that reached the prompt reached
it from a sentence that assumed a reader who has this plugin, and deleting four characters leaves
that assumption in place.

## How it runs

```mermaid
flowchart TD
    p0["Phase 0 — Resolve inputs and gate the decided BRD"] --> p1["Phase 1 — Classify + model routing"]
    p1 --> p2["Phase 2 — Resolve prerequisites and their packages"]
    p2 --> p3["Phase 3 — The adversarial self-review"]
    p3 --> p4["Phase 4 — The disposition gate"]
    p4 --> p5["Phase 5 — Assign the degradation tier"]
    p5 --> p6["Phase 6 — Render the customer prompt"]
    p6 --> p7["Phase 7 — Render the delivery note"]
    p7 --> p8["Phase 8 — Assemble the bundle"]
    p8 --> p9["Phase 9 — Handoff"]
    p9 --> p10["Phase 10 — Next steps"]
    p10 --> p11["Phase 11 — Session maintenance, feedback & cost"]
```

`brd-package-reviewer` is dispatched on Opus (frontmatter-pinned; no override unless `--enforce-model`/`WORKFLOWS_ENFORCE_MODEL` enforces one) for the adversarial pass, and once more when a `fixed`
disposition changed the package the review was written against. `workflows-core:impl-maintenance` runs in the
terminal phase for session lessons-learned — replaced by `defect-reporter` under `--skip-feedback`/`WORKFLOWS_SKIP_FEEDBACK`. No other subagent is dispatched.

## What it needs

- **`<BRD-KEY>`** — mandatory; absent or malformed stops the run with `BRD_PACKAGE_NEEDS_KEY`.
- **A slice, not a root and not an idea-route PRD folder.** The moment the folder resolves, its
  prefix is tested — `BRD-` is a root, `EPIC-` an Epic folder, `PRD-` a slice or an idea-route PRD folder — never the
  folder's asserted `kind:`. An `EPIC-` folder stops with `BRD_PACKAGE_EPIC_LEVEL` before any gate runs: an Epic holds none of what this command reads, so the stop names `/brd-package <SLICE-KEY>` on the slice above it where there is one, and no command where there is none. A `PRD-` folder carrying no `brd-link.md` was never carved from a BRD
  and stops with `BRD_PACKAGE_NOT_A_SLICE` before any gate runs: it has no register and no customer to package for, so the stop sends it on along the
  idea route — `/create-ard` or `/specify`. A resolved root stops with
  `BRD_PACKAGE_ROOT_LEVEL`, naming `/brd-split <BRD-KEY> "<how to cut it>"` to carve a slice and
  then `/brd-package <SLICE-KEY>` on it; where the root already carries package artifacts written
  under the earlier two-level model, the stop names those files and leaves them in place, unread.
- **An existing BRD folder.** No folder for `<BRD-KEY>` — searched at every level
  `resolve-address` bounds (three below `specifications/`) — stops with `BRD_PACKAGE_NOT_FOUND`, which names both ways a folder comes to exist
  rather than asserting one.
- **No torn write in the folder.** An item stamped with a round whose `interview/round-<N>.md` does
  not exist or does not name it — what a [`/brd-interview`](brd-interview.md) run left when it
  stopped before writing that record — counts for nothing
  ([`decision-register-format.md`](../../references/decision-register-format.md) §8), and the bundle
  carries the register, the question set and the code-defect log whole, so a package built now
  would ship them. The run stops with `BRD_PACKAGE_TORN_WRITES`, naming each; any
  `/brd-interview` run that reaches its handoff removes them, save on a slice that kept no
  requirement of its own, which that command refuses and this stop says so. A round record that
  exists and cannot be read stops the run with `BRD_PACKAGE_ROUND_UNREADABLE` instead, since it
  decides nothing. This test runs before the register gate below, so that gate's remedy — commit
  the register — never lands a torn write first.
- **`/brd-interview`'s register already merged to the specs repo's default branch.**
  `require-on-main` runs against `decisions.md` before any content is read; an unmerged pull
  request stops the run naming the branch/PR state. Where the gate reports the register is on no ref
  at all, the run **splits a state the gate cannot**, as [`/brd-reconcile`](brd-reconcile.md) does on
  its own row F: no `decisions.md` in the folder means no interview has written one
  (`BRD_PACKAGE_NEEDS_INTERVIEW`, run [`/brd-interview`](brd-interview.md)). That run writes it for
  a BRD never interviewed, and for one interviewed before it wrote the register on every round —
  resuming a round still open, or on its no-new-round path where every round is closed; for a BRD
  whose every row is delegated it stops instead, since that BRD kept nothing to package. A
  register in the folder means the run that wrote it — the interview, ordinarily, or
  [`/create-prd`](create-prd.md) or [`/brd-reconcile`](brd-reconcile.md) where either created it —
  had its handoff declined (`BRD_PACKAGE_REGISTER_NOT_HANDED_OFF`, land the files that are already
  on disk). The second must
  **not** send the operator back to `/brd-interview`: a bare re-run of that command hands off only
  the files it writes itself — nothing at all where it finds nothing new to ask, and where it opens a
  new round, that round's record and not the earlier ones already on disk.
- **The question set and the code-defect log on the default branch too, each where it is in the
  folder.** The bundle ships both whole, and the register being merged says nothing about either: a
  handoff declined and landed in part, or a later interview run that lands the register without a
  question set an earlier run left, merges `decisions.md` alone. Each is gated with
  `require-on-main`, and one in the folder and on no ref stops the run with
  `BRD_PACKAGE_SHIPPED_NOT_HANDED_OFF`. A file absent from the folder is not gated: a slice whose
  rounds held no `[C]` has no question set, and one whose decisions turned on no code defect has no
  log.
- **Every round the register or the held questions name, on the default branch.** The rounds this
  BRD has are the distinct `round` values `decisions.md` records, together with the round of every
  held `[C]` question in **interview/customer-questions.md** — a round of held `[C]` questions puts
  no record in the register — and each one's **interview/round-`<N>`.md** is gated with
  `require-on-main`; any on no ref stop the run together with `BRD_PACKAGE_ROUNDS_NOT_ON_MAIN` —
  save a round whose record exists nowhere, not even in the folder, which is named only by a
  re-decision an interrupted `/brd-interview` run left standing: there is nothing to land, so that
  one stops with `BRD_PACKAGE_ROUND_NOT_RECORDED`, naming `/brd-interview` as the run that writes
  the record. The
  set is derived from those two sources rather than from the **interview/** listing, which is what
  makes a partial merge visible — enumerating the directory finds the rounds that landed and never
  learns a third was owed.
- **An interview that happened at all.** A BRD whose **interview/** holds no round record stops
  with `BRD_PACKAGE_NOT_INTERVIEWED`, naming `/brd-interview`, whatever its register holds — an open
  `[AS#n]` that [`/create-prd`](create-prd.md) wrote included — rather than being reported as a
  finished state it never reached.
- **Every interview question settled, or held for the customer.** Any question still *deferred*,
  *needs grounding* or *untagged* stops with `BRD_PACKAGE_ROUND_UNSETTLED` — see
  [Gates](#gates) for why *held for the customer* is the one holding state this command admits.
- **Something for the customer to decide.** No `[C]` question, no open `[AS#n]` and no `[VD#n]` at
  all stops with `BRD_PACKAGE_NOTHING_TO_REVIEW`: every question the rounds asked was settled from
  verified findings, so there is nothing in them to ask a customer. Whether that leaves the BRD
  decided is [`/brd-interview`](brd-interview.md)'s to say, and the stop does not guess — when that
  command opens a round is its own rule, which the stop cites rather than restates. Where
  `/brd-interview` would open a new round, or names the `--round 1` re-open for open requirement
  defects no round has asked, running it is the fix; a bare run says which, and hands off nothing
  where neither applies. `/prd-ground <BRD-KEY> --rebaseline` can also make a round askable, where the re-grounding moves a
  decision or raises a question; a status change alone opens no round. Where none of
  that applies, the BRD is decided — a **finished** state rather than a missing step. A package
  carrying `[VD#n]` positions and no `[C]` question is legitimate and is packaged.
- **`$SPECS_PATH`** (required) — if unset, the run stops naming `SPECS_PATH`.
- **No repository, and no `$REPOS_PATH`.** Every commit this package cites was pinned and proven
  clean by `/prd-ground`; the repo→SHA table is read from that run's `baselines.md`, and the three
  pin-verification commands are handed to the customer's reviewer to run rather than re-run here.

## What it produces

Under the resolved BRD folder — `$SPECS_PATH/specifications/BRD-<BRD-KEY>-<slug>/` for a root
BRD, and the `PRD-<SLICE-KEY>-<slug>/` slice folder inside it for a slice
([addressing](../reference/references.md) §2, §6), all stamped with one date taken once:

| Artifact | What it is | In the bundle? |
|---|---|---|
| `self-review-<date>.md` | The adversarial pass: every `[SR#n]` with its class, target, attack and disposition, plus the per-pass account | **no** — see below |
| `customer-review-prompt-<date>.md` | The self-contained prompt the customer pastes, in the fixed eleven-part order, with the review schema inlined | yes |
| `bundle-<date>/` | Plain markdown and images, de-Obsidianised save the customer's own files, which go in byte for byte, plus a manifest and any dependency package | it *is* the bundle |
| `customer-delivery-note-<date>.md` | The covering letter, under a 200-word ceiling | **no** — it is the email, not a package document |

`brd-link.md` also gains any prerequisite this run declared, merged additively.

**The self-review never travels, and the reason is the disposition gate.** A `[SR#n]` disposed
`rejected-with-reason` has its reason recorded there and it "stays inside the delivery
organisation"; the `[SR#n]` content the customer may see reaches them **filtered** — `accepted-risk`
findings under *where to attack us hardest*, quoted as the reviewer wrote them, which it writes for
a customer to read without this plugin, and `escalated-to-customer` findings under *the decisions
the customer must make*. Shipping the file would defeat that filter and hand the customer an
internal disagreement to referee. What the bundle *does* hold is an allow-list, not a deny-list, and
[`bundle-packaging.md`](../../references/bundle-packaging.md) §1.1 is its authority: the prompt; the
customer's own source document, every markdown file captured with it, its defect log and — where one
exists — the transcription of each image (the parent's on a slice); the inventory; the coverage
ledger; the three grounding files; the decision register; the code-defect log where the folder holds
one; the `[C]` question set; each prerequisite package; the images those reference and every image
the transcription covers — one the latest intake did not capture only where a requirement still
anchors on it; and the manifest, which maps each captured file's path — the form a transcription,
an anchor or a question names it by — to its bundled filename. The customer's own files go in byte
for byte, unrendered. A document reaches the bundle only where a part of the prompt sends the
reviewer to it — everything else in the folder is a working record and stays.

Behind a consent choice, these are committed, pushed, and a pull request opened against the specs
repo's default branch under the shared `brd/<BRD-KEY>-<slug>` branch prefix. The committed bundle
serves both delivery routes, and the run settles which one at the delivery note — which is why the
consent is asked there rather than at the handoff phase that acts on it: the note is one of the
files the handoff commits, so its route cannot wait on the handoff's outcome. Where the specs repo
passes the handoff's gate (an existing git repository whose `.git` is writable, on no detached
HEAD), has an `origin` remote to push to, and the operator consents, the run asks, recommending that
the customer pull the bundle; where any of the three fails — declining the handoff among them, which
declines only the handoff and ends nothing else — nothing this run does puts the bundle where a
customer can pull it, so it takes the archive route without asking and says so. The note names no
branch, because the branch is settled by the handoff and the bundle reaches the default branch only
when the handoff's pull request merges: on the repository route the run prints, beside the note and
before it offers to send it, the branch and pull request the handoff pushed and says the note is
true once that pull request merges — or, where nothing was pushed, what must happen first, and
where the handoff declared a path and staged nothing for it, that the note is not true for that file
on any outcome; the *Send it* next step waits on the same condition. The archive command is printed
only on the archive route. **The prompt itself
names no route** — it is handed on to a reader the run cannot see, and a path is correct exactly
once, so only the delivery note names where the bundle is.

## The prompt's eleven parts

Assembled from the package, never hand-written, in a fixed order that is not re-ordered or merged.

| # | Part | Filled from |
|---|---|---|
| 1 | Setup | the tier, the assumed capability set, the route-neutral locating instruction, the OS note, and the one-new-file rule |
| 2 | What each package in the bundle is for | this BRD, plus each prerequisite package, marked *not for re-review* |
| 3 | Documents to review | the manifest, by its bundled filename, then every other document the bundle admits, by the bundled filename it carries — the names the manifest lists |
| 4 | Code baselines and the verification procedure | `baselines.md`, with the three pin commands written out |
| 5 | The single most important claim to verify first | the finding the most decisions rest on, else the most-relied-on open assumption, else the finding the most held `[C]` questions bear on — or a statement that none rests on one |
| 6 | Review scope | the ledger's dispositions — the rows this slice answers for, each orphan row (a claim the parent withdrew) as another BRD's, `<PARENT-KEY> [BR#n]`, not for review — plus every `in-scope` `[CDF#n]` |
| 7 | The decisions the customer must make | the `[C]` question set, every open `[AS#n]`, every escalated `[SR#n]` |
| 8 | What could still move | prerequisites not yet customer-reviewed, every `conditional_on` position, and every `conditional` `[CDF#n]` |
| 9 | Where to attack us hardest | every open `[AS#n]`, and every `accepted-risk` `[SR#n]` |
| 10 | The required output file, its exact name, and the inlined schema | the one-new-file rule, the `Package reviewed` line section 1 repeats, and the rendered schema |
| 11 | What this session cannot settle | the ledger, the prerequisites, the review's own limits, and every `out-of-scope` `[CDF#n]` |

**Parts 8 and 9 are the two that are easy to lose and expensive to omit.** A package that names its
own weak points gets a review worth having; one that does not gets a rubber stamp. And a customer
being asked to accept positions built on a prerequisite nobody has reviewed yet is entitled to know
which positions those are, by identifier.

**Every open `[AS#n]` appears in both part 7 and part 9, deliberately.** Part 7 asks the customer to
decide it — an assumption corrected while it is still an assumption is the cheapest correction in the
whole loop. Part 9 invites them to attack it. Removing either copy as redundant always loses the
attack.

## Gates

- **Phase 0 — the root refusal, tested the moment the folder resolves.** A resolved `BRD-` root
  stops with `BRD_PACKAGE_ROOT_LEVEL` before any other gate runs: packaging happens at the slice and
  nowhere else. A resolved `EPIC-` folder stops with `BRD_PACKAGE_EPIC_LEVEL` at the same moment. An idea-route PRD folder stops next, with `BRD_PACKAGE_NOT_A_SLICE`, before any
  other gate runs.
- **Phase 0 — the register merged, the rounds settled, something to review.** All three run before
  anything else is read. The rounds gate admits exactly one holding state, *held for the customer*,
  and refuses the other three. That reading is forced: a round holding a `[C]` stays open **until the
  answer comes back through the package**, and the package is what this command builds, so requiring
  every round to be closed would deadlock the route. The other three holding states each name work
  that is still the delivery team's.
- **Phase 0 — a dated bundle is never rewritten.** A `bundle-<date>/` that already exists stops the
  run with `BRD_PACKAGE_BUNDLE_EXISTS`. Rewriting it destroys the only evidence of what the reviewer
  of that date was looking at, and the command cannot tell whether the existing directory was already
  sent — the operator can.
- **Phase 4 — the disposition gate.** No bundle is built while any `[SR#n]` is undisposed. The gate
  is keyed on **every finding carrying a non-`undisposed` value**, and on nothing else: the reviewer
  agent returns no severity and no PASS/BLOCK verdict by design, so the disposition is the only gate
  there is. The four values are `fixed`, `accepted-risk`, `escalated-to-customer` and
  `rejected-with-reason`, and the array carries those four and nothing else. The harness always
  supplies a free-text option, so the picker cannot decline one — what protects the closed vocabulary
  is what the run *does* with the answer: a free-text reply is normalised into one of the four, or the
  finding is re-asked. It is never written through, because a fifth disposition is one nothing
  downstream can read ([`workflows-core:escalation-rules`](../reference/references.md) §0).
- **Phase 4 — what `fixed` may name.** Only what this command itself writes: the prompt, the
  delivery note, the self-review, the bundle's rendered copies and an `[SR#n]`'s own record. Never a
  register record, a held `[C]` entry, a ledger disposition or a verified finding — those belong to
  other commands, and a finding the team agrees with but cannot act on here takes `accepted-risk`
  with a `fixed-by:` marker — naming the command that fixes it, or, where no command writes that
  artifact at all, the person who must write it by hand. The marker is written either way: part 9
  renders the customer's *we agree, this is ours to repair* sentence from its presence, so a finding
  left unmarked reads on the page as a risk the team weighed and accepted. Two of the five exist when the gate
  runs; the other three are written by later phases, so a correction against one of those is
  recorded against the finding at the gate and carried out when that phase writes the artifact.
- **Phase 4 — a `fixed` correction re-opens the review, exactly once, whatever artifact it named.**
  The correction changes what the customer will be shown, and one made under one finding can break a
  position another left standing — so the reviewer runs again, with this run's self-review, the
  corrections recorded in it, in `prior_reviews`. Once, not until clean: an unbounded loop trades
  the customer's review for the delivery team's.
- **Phase 4 — a finding escalated again says which earlier one it is.** Every package numbers its
  findings from `[SR#1]` again, so on a re-package a finding taking `escalated-to-customer` that
  matches one an earlier package escalated — the same class, and a target that is the same single
  record id, compared as whole values and never read out of prose — is shown to the operator beside
  the earlier finding's words, and only where they
  confirm the two are one finding does it get a
  `- **Re-escalates:** self-review-<date>.md [SR#k]` line in this run's self-review, naming the most
  recent earlier match. [`/brd-reconcile`](brd-reconcile.md) follows that line, so the customer's new
  answer is judged against the answer they gave before. No match on those fields, two in one file, or an
  operator who does not confirm writes no line, and the answer is frozen fresh.
- **Phase 5 — the tier is assigned from what was shippable.** Full, Partial or Documents only, never
  promoted, never chosen by the reviewer, and never quietly Full because the repositories were
  *probably* at the right commit. A tier is not a quality grade: a documents-only review that states
  its tier can be weighed correctly, and a full-tier review that states nothing cannot be weighed at
  all. Its free-text answer is normalised the same way the `[SR#n]` picker's is, for the same reason:
  a fourth tier is one neither the prompt nor a returned review's section 1 could state, so a reply
  landing on none of the three re-asks rather than inventing one.
- **Phase 6 — the render boundary.** The schema is rendered from section 2 onward, and the run stops
  with `BRD_PACKAGE_SCHEMA_BOUNDARY` if that file no longer declares where its boundary falls. The
  rendered headings are renumbered so the customer's copy runs from 1 rather than visibly beginning
  at 2; that is safe because the schema refers to its own sections by name and never by number, which
  the render verifies by requiring the extracted body to contain no `§` at all. It verifies, too,
  that the body holds no identifier with a number in it, and stops with
  `BRD_PACKAGE_SCHEMA_EXAMPLE_ID` on one: the schema writes every example as a placeholder,
  `[BR#n]`, because the prompt is a bundle document and the citation-resolution check would resolve
  an example number against this package's own records — to a requirement or finding nobody meant,
  or to nothing.
- **Phases 6, 7 and 8 — the plugin-free scan.** Run over the finished prompt, the finished note and
  every bundle document. A hit stops the run with `BRD_PACKAGE_PROMPT_LEAK`, naming the token, the
  part it landed in and the artifact it came from — except inside the customer's own verbatim
  content (their captured files, and the parts of the transcription, the inventory, the coverage
  ledger and the register that quote them) or a locator naming their own files, headings and links,
  in the positions where `bundle-packaging.md` §6.3 recognises one; both sets are defined there,
  once. There a `§ 4.2` or a `D3` is the customer's own and the only fix would falsify it, so the
  hit is reported, grouped as that section fixes, and put to the operator on one question per pass —
  ship it as the customer's own (recommended), or hold the package, which stops with
  `BRD_PACKAGE_CUSTOMER_CONTENT_HELD` and hands nothing off; a hit an earlier ruling in the run
  covered is not asked about again, and the report opens its list of them with a
  `Customer content:` line — or, where that section says so, it is no hit at all. The identifiers
  the package's own registers, logs and grounding files mint are **not** in the scan's classes and
  are meant to travel — the classes are enumerated once, in `bundle-packaging.md` §6.1's table,
  rather than restated here. They are how the returned review cites the package without minting
  identifiers of its own; whether each one actually lands is what the citation-resolution check
  below verifies.
- **Phase 7 — the delivery note's 200-word ceiling.** A ceiling, not a target. Over it, the note is
  shortened and re-rendered; the two facts that are never trimmed are which file is the prompt and
  which file comes back.
- **Phase 8 — the citation-resolution check.** Run over every document in the assembled bundle,
  after the plugin-free scan, because both of its inputs — the identifier corpus and the set of
  bundle filenames — are facts about the bundle only once it is assembled. Three relations: every
  identifier reference resolves inside its own partition's corpus for its class, unless it carries
  another BRD's key at the point of use — one naming its own partition, such as a slice's
  `resolved-by` in that slice's own bundle, is resolved there like an unqualified id; a class-4
  `[DG#n]`'s `cites` resolves within the same partition and names the same requirement as the citing
  finding's own claim; and a bare `<name>.md` token names a document that is actually in the bundle
  — scoped to the tokens that claim to be bundle references, meaning the token carries the
  `<BRD-KEY>-` prefix every bundle document's filename carries or exactly matches the working
  filename of a document the allow-list admits or excludes by name. That scoping is the relation:
  unscoped, it would refuse a bundle over a correct `docs/api.md:12` sitting in a grounding
  finding's `evidence` list. It never tests a repository locator in that list, nor the manifest's
  quotation of a customer's target as written, which sits beside the bundled filename it maps to,
  nor a captured file's own link to another captured file. Its exemptions are `bundle-packaging.md`
  §6.3's: `[SR#n]` is exempt entirely, because the self-review file it would resolve against is
  excluded from the bundle by rule and its content reaches the customer filtered through the prompt;
  and a hit inside the customer's own verbatim content or a locator naming their files and headings
  — a `[BR#n]` or a filename visible in their screenshot among them, or one they wrote into an
  answer or a reason the register quotes — is reported and put to the operator rather than stopping
  the run by itself, for the same reason the plugin-free scan treats it that way, and only the
  operator's *hold* stops it. A reference that resolves to nothing stops with
  `BRD_PACKAGE_DEAD_CITATION`. A requirement this slice does not claim, cited bare in a question, a
  held entry or a register record written before 3.7.0, is such a reference — the package carries
  this slice's inventory alone, and 3.7.0 is the release from which the interview, the PRD's
  assumptions, the reconciliation and this command's prompt write such a row `<PARENT-KEY> [BR#n]` —
  so where the stop names one, qualify that id by hand in that form, with this slice's `parent:` as
  the key, and change nothing else in the sentence. One that resolves to the wrong requirement stops
  with `BRD_PACKAGE_CITATION_MISMATCH`; a corpus file holding record-shaped content that yields no
  ids stops with `BRD_PACKAGE_CORPUS_UNREADABLE` — a corpus holding no record-shaped content at all
  is legitimately empty and passes.
- **Phase 8 — the set-resolution check.** Run last, and the three passes hunt different failures: a
  token the reviewer cannot resolve, a token they resolve to the wrong thing, and a **set restated
  wrongly** — every identifier resolving, every filename real, and the set they compose not being
  the one its source holds. Three relations, all comparing membership rather than counts, because
  two sets of the same size with different members read as correct: a part that enumerates
  identified records names exactly what its filter selects; the manifest and the bundle name the
  same review documents; and the delivery note's repositories and pins are the bundle's baselines'.
  **Each is narrower than its obvious form, and every narrowing was measured against assembled
  packages** — the review-scope part renders prose rather than identifiers, save the requirements it
  names as another BRD's, which the check leaves to review; a part writes `[AS#1]`–`[AS#4]` as a
  range rather than naming each; a manifest writes filenames with or without the extension and names
  images only sometimes; and a delivery note abbreviates its commits, against a baselines document
  that records one entry per repository *per run* and so may hold the same commit twice. The obvious
  form of each relation fires on a correct bundle. A mismatch stops with `BRD_PACKAGE_SET_MISMATCH`;
  an empty source side with `BRD_PACKAGE_SET_UNREADABLE`.

## What it does not do

- **No documentation grounding, and no `--no-docs` flag.** `/brd-intake` and `/prd-ground` already
  ground this BRD against the shipped product documentation when `$DOCS_PATH` resolves. This command
  establishes no claim of its own at all — it renders what other commands recorded — so a
  documentation page could only introduce an ungrounded sentence into a bundle whose whole value is
  that every sentence in it is traceable. There is nothing to switch off, so no flag exists to switch
  it.
- **It sends nothing anywhere.** The bundle is written and, behind consent, committed; the delivery
  note is printed for pasting. Delivery is the operator's.
- **It writes no `[CD#n]`, and it ingests no returned review.**
  [`/brd-reconcile`](brd-reconcile.md) is what turns a returned answer into a confirmed customer
  decision, so the round holding each `[C]` stays open until that run records it.
- **It changes no ledger disposition.** The final report's ledger line reports where allocation
  stands; allocation itself is `/brd-split`'s walk. Two other runs may move a row afterwards, and
  neither is this one: [`/brd-reconcile`](brd-reconcile.md) freezes a customer decision that settles
  it differently, and a [`/brd-split`](brd-split.md) **re-cut** on the parent re-points a row this
  BRD's own walk sent to `deferred-to: <itself>` onto a sibling that will build it — writing
  `covered-by` on this BRD's row for it. Being interviewed disqualifies a re-cut's *receiver* and
  never its *donor*, so a BRD that has reached this command is an ordinary donor
  ([`coverage-ledger-format.md`](../../references/coverage-ledger-format.md) §3.2).

## Example

Package a synthetic customer BRD once its interview round has settled, declaring one prerequisite:

```
/product-workflows:brd-package EPIC-008 --depends-on EPIC-014
```

The run gates on `decisions.md` being merged and on every question carrying a terminal disposition or
being held for the customer, dispatches the adversarial reviewer, walks each `[SR#n]` to a
disposition, asks which tier the customer can be given, renders the prompt, asks whether to branch,
commit, push and open a pull request — and, on a yes where the specs repo can take the commit and
has a remote to push to, how the customer gets the bundle — renders the note, assembles
`bundle-<date>/` with the prerequisite's package copied in and marked *not for re-review*, and hands
it off as answered. The next-step phase prints the delivery note in full and, directly after it and
before its offer, the delivery route and why — the archive command with an absolute path on the
archive route, or a line saying none was produced because the customer pulls the committed bundle,
with the branch and pull request the note waits on — and the report names both rather than
repeating them, then prints the repo→SHA table and the ledger line.

## See also

- [Roles and phases](../roles-and-phases.md) — what the `pm` role owns and hands off.
- [Model routing](../reference/model-routing.md) — the classification rules this command applies.
- [`bundle-packaging.md`](../../references/bundle-packaging.md) — the authority for plugin-free
  construction, the de-Obsidianising pass, the three degradation tiers, the delivery note's ceiling,
  the citation-resolution and set-resolution checks, and where the bundle lands.
- [`customer-review-schema.md`](../../references/customer-review-schema.md) — the twelve sections the
  returned review carries, and the file whose body this command inlines from section 2 onward.
- [`decision-register-format.md`](../../references/decision-register-format.md) — the `[VD#n]` /
  `[CD#n]` / `[AS#n]` record, `conditional_on`, and the rule that every open assumption reaches the
  customer.
- [`interview-tagging.md`](../../references/interview-tagging.md) — the `[C]` tag, and the rule that
  a customer question reaches the customer only through this package.
- `workflows-core:grounding-format` — the finding record and the
  `baseline-integrity` commands the prompt hands the customer to re-run.
- [`coverage-ledger-format.md`](../../references/coverage-ledger-format.md) — the dispositions the
  review-scope part reads, and §6's ledger line the final report ends with.
- [Agents](../reference/agents.md) — `brd-package-reviewer`'s and `impl-maintenance`'s full
  contracts.
- [Session cost](../reference/session-cost.md), [Session feedback](../reference/session-feedback.md),
  and [Resume and checkpoints](../reference/resume-and-checkpoints.md) — the terminal bookkeeping
  every run emits.

# Conformance record format

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

Single source of truth for `_conformance.md`, the record `/dev-workflows:conformance` writes into the folder it checked — an Epic folder on an **Epic run**, a PRD folder on a **PRD run** — and for the rules a later run, and a later reader, apply to it. The command is its only writer. Design authority: `docs/superpowers/specs/2026-10-12-conformance-design.md` in the plugin source repository.

## 1. Where it lives and what it is

One `_conformance.md` per checked folder, beside that folder's own documents. Its frontmatter names it and its unit:

```yaml
---
kind: conformance-record
key: <the folder's key>
---
```

Where `/dev-workflows:conformance`'s lineage check was answered *Proceed*, an `accepted:` block follows `key:` — written only by `workflows-core:document-lineage`'s script, never an `upstreams:` block, since the record is not built from those documents but checks code against them.

`conformance-record` is not a folder kind, so `workflows-core:addressing` §4 never reads this file as the folder's carrier. The record is a phase deliverable: it lands on the specs repository's default branch through `workflows-core:phase-handoff` `handoff-to-main`, on a `conformance/` branch, behind the run's consent choice. Until that branch merges, a later run finds the record there and acts on it before it reads a requirement (`/dev-workflows:conformance` Phase 0 step 5).

## 2. The header

```markdown
# Conformance: <KEY>

- **Run:** <Epic | PRD> — role `<dev | pe>` — <YYYY-MM-DD>
- **At:** <instant>
- **Code checked:** <repo slug> at <the ref traced: its default branch, or on an Epic run the Epic's branch> @ <commit>, one line per repository
- **Not traced:** none, or [<n> requirement(s) — ]<each requirement-bearing document not read, followed by (requirements uncounted); each repository with no clone or no default branch, with the count of requirements it left untraced>
- **Not shown merged:** none, or <KEY>, one per unit traced under Phase 1 (c)'s *Trace anyway* — each Epic, or the PRD itself where it has no Epic folder
- **Verdicts:** <n> satisfied · <n> partial · <n> missing · <n> contradicts · <n> not-checkable · <n> unverified
- **Threats:** <one of the two forms below, and only where the run had threat input>

## Satisfied

- <requirement id, or its quoted text> — <file:line@commit>, one per evidence location[ — sibling parts: <EPIC-KEY> (<component id>), one per sibling Epic]

## Unverified

- <requirement id, or its quoted text> — <the verdict the re-check could not settle> — <what would settle it>

## Not checkable

- <requirement id, or its quoted text> — <the tracer's reason>

## Threats

- **Models read:** <each model's path relative to $SPECS_PATH, or none>
- [[<KEY>]] [TH#N] <title> — <state>[ — <reason>][ — <each mitigation, with its verdict or [DD#n]>]
- [[<KEY>]] [DT#N] <title> — <state> — <why it stands alone>

## Discrepancies
```

**`At:` is the instant the run started**, in UTC, exactly `^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$`, on the line right after `Run:`. `/dev-workflows:conformance` takes it right after `strip-run-flags`, before it reads any record or document, by pasting the output of `date -u +%Y-%m-%dT%H:%M:%SZ` verbatim, carries it through the run, and writes it with the header (its Phase 0 step 1 and Phase 5), so work that lands while the run is going on counts as implemented since the record. Where the run no longer holds that value verbatim, it writes no `At:` line, never a new reading of the clock, which would be later than its start. `Run:` keeps the writer's own date, so its day and the instant's can differ. A value that does not match the pattern — hand-typed, in an offset form, truncated — is no instant, and neither it nor a missing line makes the record unreadable. **The guard: an `At:` whose date part is more than one day from the record's `Run:` date is no instant either.** It drops a stale `At:` that a re-run by a `dev-workflows` older than 4.63.0, which does not know the line, kept beside the new `Run:` date it wrote; a stale `At:` within a day of that date passes it. An `At:` is an instant only where

```
python3 -c 'import sys,datetime as d; print(abs((d.date.fromisoformat(sys.argv[1][:10])-d.date.fromisoformat(sys.argv[2])).days)>1)' "<At value>" "<Run: date>"
```

prints `False`. Where it prints `True`, the `At:` is more than a day from its `Run:` date; where either date is impossible — `2026-11-31`, `9999-99-99`, or a malformed `Run:` date — it fails and prints nothing; and where it prints anything but `False`, that `At:` is no instant. **The guard also drops a genuine `At:`.** `Run:` carries the day the run wrote the record, in its writer's zone, so a run whose `Run:` date falls more than a day after its start's date — one that ran across days — has no instant, and is ordered by date, as every record was before `dev-workflows` 4.63.0: to `/dev-workflows:ready`, work implemented while it ran then reads as covered. A record written before `dev-workflows` 4.63.0 carries no `At:` unless a hand edit put one there, and a record with none has no instant. A reader that orders this record against another record or an `implementation.md` block compares instants only where both carry one, and dates otherwise (§6). **`/dev-workflows:ready` holds the line to three more tests** (its Phase 1 step 2b). A header with more than one `At:` line gives the record no instant. Nor does a value that names no real UTC time, where `python3 -c 'import sys,datetime; datetime.datetime.strptime(sys.argv[1],"%Y-%m-%dT%H:%M:%SZ")' "<At value>"` exits non-zero, as it does for `2026-11-12T25:00:00Z`. Nor does a value later than the instant `/ready`'s own run started, since a future value would sort after every block. `workflows-core:source-truth` §7.8 holds the line to the first two of those tests and not the third, since it orders two records against each other, never against a reader's clock.

**`Not traced:` names the documents and repositories the run left untraced, and counts what it can** — the requirement-bearing subset of the report's *Scope* line *Not traced* (`/dev-workflows:conformance` Phase 7), which may name more: each requirement-bearing document the run should have traced but could not read — `prd.md`, an Epic's `epic.md` or `specification.md`, or a PRD-level `specification.md` that exists — and each repository with no clone or no default branch, with the count of requirements it left untraced. It never names a `design.md` or a `threat-model.md` — a design's `[DT#N]` Rules are traced as requirements, but the design is not a document this line names, and a model or a design the run did not read is the `Threats:` line's to name (below) — nor a PRD-level `specification.md` that does not exist, or an Epic that gave no requirement of its own. `<n>` counts the requirements the repositories it names left untraced, each once, and is written, with its dash, only where the line names a repository. A document not read adds none to it, since its requirements were never listed, so the line marks each such document `(requirements uncounted)` — a line naming only documents is never read as zero requirements untraced. **`Not shown merged:` names**, by key and comma-separated, each unit a PRD run traced under *Trace anyway* (`/dev-workflows:conformance` Phase 1 (c)) — each Epic, or the PRD itself where it has no Epic folder and its own blocks were the ones not shown merged — the units the report's *Scope* line *Traced where not shown merged* names. Each line reads `none` where it names nothing, and on an Epic run `Not shown merged:` always does. A re-run rewrites both, as it does the rest of the header. **A record without them predates them**, and a reader never takes their absence for `none`.

**`Threats:` and `## Threats` say where each threat that applies to the unit stands, and are written only where the run had threat input** — where its `threat_input` (`/dev-workflows:conformance` Phase 1 (b)) is not `none`: a `threat-model.md` stood at a known path, on the default branch or in the working tree, or a `design.md` the run read holds a `## Threat review`. Otherwise the record carries neither, as one written before them does, and a record without them is never read as counting zero threats. The `Threats:` line follows `Verdicts:`, in one of two forms:

```
- **Threats:** <n> verified · <n> open · <n> not checked · <n> unanswered · <n> accepted · <n> review due · <n> stale · <n> unreadable[ — not read: <each model unused, as "<path> (<why>)"; each model not landed; each design not read>]
- **Threats:** not traced — update workflows-core
```

The run writes the first where it traced the threats (`threat_input: traced`), and the second, whole, where it could not (`threat_input: not-traced`): it had threat input, but the loaded `workflows-core:threat-model-format` holds no §10, *The threats that land on a unit*, or would not load — `## Threats` then holding its `Models read:` line alone, reading `none`, since the run read no model. **Every count is written, zero included**: each is the number of lines of `## Threats` below `Models read:` — threats and stand-alone entries alike — whose state it names. The `not read:` tail stands only where it names something, `; `-separated, in this order: each model the run could not use, as `<path> (<why>)`; each model only the working tree holds, as `<path> (not landed)`; and each design not read, as `<path> (absent)` — every path relative to `$SPECS_PATH`. `<why>` is one of six, in the words of the run's own printed line: `no ARD resolves for it`; `no component set resolves`; `the Epic's target is not in the component set`; `its ARD is not on the default branch`; `its ARD's working copy differs from the default branch's`; `threats not traced`. **A design not read** is a `design.md` that `/dev-workflows:conformance` Phase 0 step 4's gate returned `absent` for, in a folder whose model the run read; no other design is, since one the gate stops on stops the run. A file at a model's path whose `kind:` is not `threat-model` is no model, and the line names it nowhere.

**`/dev-workflows:ready` reads the line so** (its Phase 1 step 2b): only lines before the record's first `## ` heading; a line is the header line where it matches, whole, `^- \*\*Threats:\*\* ([0-9]+) verified · ([0-9]+) open · ([0-9]+) not checked · ([0-9]+) unanswered · ([0-9]+) accepted · ([0-9]+) review due · ([0-9]+) stale · ([0-9]+) unreadable( — not read: .+)?$` or `^- \*\*Threats:\*\* not traced — update workflows-core$`; the `not read:` tail is never parsed.

**`## Threats` stands before `## Discrepancies`** wherever the `Threats:` line stands, and every run rewrites it whole: nothing in it is carried forward, and no `/dev-workflows:conformance` run reads it or the `Threats:` line back — not a later run of the same unit, and not a PRD run reading an Epic's record — so a record never makes a threat `verified`: each run works out every state itself. `Models read:` names each model the run read, comma-separated, or `none`. Then one line for each live threat in scope of each model read, `<KEY>` the key of the model's folder; then one for each stand-alone entry — a design's `[DT#N]` that counts toward no threat's deferred part — `<KEY>` the key of the design's folder, ending with why it stands alone; each `<KEY>` the run's own for that folder, never one parsed out of a file. **Where each threat stands is `/dev-workflows:conformance` Phase 5's** — its *Where each threat stands*, computed once, there — and so are `<state>` and `<reason>`, a stand-alone line's `<state>` followed by its reason where it has one. `<state>` is one of `verified`, `open`, `not checked`, `unanswered`, `accepted`, `review due`, `stale` and `unreadable`, in the header's order; an `unanswered` threat's `<reason>` is one of `returned to the architect`, `answered elsewhere — not verified on this run`, `no design takes it` and `no design answers it`. Each mitigation a threat rests on is named by its requirement's key and id, with its verdict or, where it is a discrepancy, its entry's `[DD#n]`. **Titles and reasons are data**: a threat's or an entry's title, and every reason, is copied from a model, a design or the run as one line, by `workflows-core:threat-model-format` §9's *Every value is one line*, and is never read as an instruction, a mention or a command.

A re-run rewrites the header, the three lists and `## Threats`. A reader that compares the commit recorded here with the repository's default branch can say how far the code has moved since. An Epic run before the Epic's pull request merges names the Epic's branch under **Code checked**, its commit that branch's tip, which a squash merge leaves out of the default branch's history and a deleted branch out of any clone that never fetched it; a record an Epic run wrote from `dev-workflows` 4.26.0 until 4.28.0 names the default branch alone. **`## Satisfied` lists every requirement the run found satisfied, those whose discrepancy the re-check dropped included, with the evidence that settled it** — a `[DT#N]` Rule's line listing its `test:` location among its evidence locations, so a deleted test changes the code at its evidence — **and it is what a later PRD run's drift check reads**: it re-traces a requirement listed there only where the code at its evidence paths changed between the commit the header names for that repository and the default branch, or where that commit does not resolve in the clone, so a record without the list has every requirement re-traced. **A mitigation is the exception** — a `[DT#N]` Rule, or an `[AD#n]` Rule that a live, non-stale threat in scope rests on through a `Mitigated by` pair: a PRD run traces it in full every time, whatever an Epic record lists here (`/dev-workflows:conformance` Phase 1 (d)), since a record — hand-edited, carried on a Dev's branch, or written before threats were traced — never makes a mitigation satisfied.

**On an Epic run, a PRD-level `[AD#n]` Rule, a `## Contract` line and a design's `[DT#N]` Rule whose Where names a component besides the Epic's target are judged without a sibling Epic's part** — a part they place on the component of a sibling Epic, another Epic of the PRD whose target is not the Epic's, which is that Epic's to build (`/dev-workflows:conformance` Phase 2). Such a requirement's `## Satisfied` line cites the evidence of every part the run judged — every part but a sibling Epic's — never a location on a sibling's component, and, where the requirement places a part on one, ends `— sibling parts:`, naming each such Epic by key with its component id. The suffix names no location, so the drift check reads the evidence before it. An `[AD#n]` Rule that binds only components other than the Epic's own target is `not-checkable` on that run: counted in the header, listed under `## Not checkable` with the components it binds, and traced in full by a later PRD run. A `## Contract` line's side on the Epic is always the Epic's own.

**`## Not checkable` lists every requirement the run found `not-checkable`, with the tracer's `reason`** — a manual process, an outcome measured in production, a side of a `## Contract` line none of whose repositories was traced, or on an Epic run a Rule that binds only components other than the Epic's, naming each component it binds and the sibling Epic that targets it. It is optional: left out where no requirement is `not-checkable`, and absent from every record written before `dev-workflows` 4.43.0, whose header counts such requirements only. Like `## Unverified` it is neither satisfied nor an entry: it takes no `[DD#n]`, nobody is asked about it, and a later PRD run traces each requirement listed there in full, since it is not under `## Satisfied` — the list says which ones, and why, where the count alone said neither.

**`## Unverified` lists every requirement the re-check could settle neither way** — a `satisfied` citing no `file:line` among them — with what would settle it. It is neither satisfied nor an entry: it takes no `[DD#n]`, nobody is asked about it, and a later run of either kind traces it in full, since it is not under `## Satisfied`.

## 3. An entry

One entry per discrepancy, in id order, under the header's `## Discrepancies` heading — its own heading, so no entry reads as part of `## Unverified`, which a later run traces in full. A record written before `dev-workflows` 4.26.0 has no such heading, its entries following `## Unverified`: a reader takes each `### [DD#n]` heading as an entry wherever it sits, and `## Unverified` as its `- ` lines alone.

```markdown
### [DD#<n>] <requirement id, or the quoted text where the requirement has no id>

- **document:** <specification.md | epic.md | prd.md | ard.md | ard-<area>.md | design.md>, in <KEY>
- **verdict:** <partial | missing | contradicts | satisfied (an entry now resolved)>
- **shipped:** <one sentence on what the code does>
- **evidence:** <file:line@commit, or a tight range file:<first>-<last>@commit>, one per repository it was found in
- **shared-cause:** <only where the walk grouped this entry in a cluster: the cluster's one shared evidence location, file:line@commit or file:<first>-<last>@commit, and every other [DD#n] of the cluster>
- **sibling parts:** <Epic run only, where the requirement places one (§2): <EPIC-KEY> (<component id>), one per sibling Epic — that Epic's, never this entry's discrepancy>
- **decision:** <fix-code | amend-document | accept> — **status:** <proposed | final | resolved>
- **rationale:** <the person's own words>
- **effect:** <"follow-up proposed: " and the follow-up line, the note's location, "recorded", or, on a [DT#N] decided amend-document, "no note — revise the design with /dev-workflows:design <KEY>">
- **ruling:** <PRD run only: confirms <EPIC-KEY>/[DD#k] | overrules <EPIC-KEY>/[DD#k] | resolved <EPIC-KEY>/[DD#k]>
- **flags:** <any of stale, orphaned, fixed, still open, requirement withdrawn>
- **lists:** <PRD run only, in place of ruling: <EPIC-KEY>/[DD#k] — an Epic entry the run only listed>
- **withdraws:** <PRD run only: a follow-up line, verbatim — one field per line>
- superseded-by: <PRD-KEY>/[DD#n]   ← written into an Epic entry by the PRD run that overruled it
```

`[DD#n]` is cited outside its record as `<KEY>/[DD#n]`.

**A requirement is `(key, id, document)`**: the heading names its id as the run's inventory does, and `document:` the file that holds it, with the key of that file's folder. A design's Rule — a live entry of its `## Threat review` whose Disposition opens `Mitigated — Rule: `, traced as a requirement (`/dev-workflows:conformance` Phase 1 (b)) — is `[DT#N]` with `document: design.md`. An ARD decision is `[AD#n] Rule` with `document: ard.md` where the folder's `ard.md` holds it, and **`[AD#n] Rule (ard-<area>.md)` with `document: ard-<area>.md` where an area file holds it**, the file being the one `workflows-core:ard-resolution` returns as the decision's `file:`. The form is a property of the decision, so it never changes when another area file of the folder takes the same number: two area files' `[AD#n]` are two requirements.

**The legacy match.** A record written before an area file's decision carried its file wrote each such decision as `[AD#n] Rule` with `document: ard.md`, so it is read, and next written, by two rules:
1. **Exact identity first.** The legacy match is tried only for what matches no requirement of the inventory: an entry whose heading reads `[AD#n] Rule` with `document: ard.md`, where the folder that `document:` names holds no live decision of that number in its `ard.md`; or a `## Satisfied` line whose id reads `[AD#n] Rule`. Where exactly one area file of that folder holds that number, such an entry is that file's decision, `[AD#n] Rule (ard-<area>.md)`, and is read as any entry is from there on; otherwise it is `orphaned`, its requirement no longer in the document it names (§4). Where exactly one `ard-<area>.md` of the `ard_paths` of the unit whose record it stands in holds that number, such a line lists that file's decision; otherwise it lists no requirement, and spares none a trace.
2. **The unit's own record is rewritten in the new form** when the record is written. **An Epic record is never rewritten for it, and a PRD entry that rules on or lists a legacy-form Epic entry keeps that Epic entry's heading and `document:` verbatim**, so every test that compares a heading and a `document:` — `workflows-core:source-truth` §7.8's rule 1, `/dev-workflows:conformance` Phase 4's paragraph opening `An entry the record on file already decided`, its Phase 5's *An overrule held back*, and §5's last paragraph — still matches; such a PRD entry reaches its requirement by rule 1. Once an Epic's own re-run rewrites its record in the new form, the PRD record's entry keeps the legacy heading until the next PRD run, where Phase 4's same-requirement test fails once and the PE is asked again; that run writes the new form.

**A `[DT#N]` entry decided `amend-document` takes no note, on either run**: the design is the Dev's, and its `## Threat review` holds no `- [ ]` line. Its `effect:` reads `no note — revise the design with /dev-workflows:design <KEY>`, `<KEY>` the key its `document:` names.

**One entry per requirement, a cluster included.** Where `/dev-workflows:conformance` Phase 4 asked several discrepancies as one cluster — the items whose evidence holds one shared location, the same `file:line` at one commit or overlapping ranges in one file, never a chain of pairwise overlaps, each item in at most one cluster — each keeps its own entry, its own `[DD#n]` and its own `document:`, and each carries `shared-cause:`, naming that location and the cluster's other ids, so a reader sees that one cause sits behind them. The cluster's one decision and rationale are written into each of its entries; a cluster decided `fix-code` queues one follow-up, whose line every entry of the cluster carries as its `effect:`. A cluster the person split keeps `shared-cause:` on each entry, since the shared location is a fact about the evidence, while each entry carries the decision and rationale given for it alone, and a `fix-code` among them its own follow-up. A later run asks again only about an entry whose discrepancy is new, or an `accept` on a mitigation, which §5 puts again on its own, so a cluster's carried-forward entries are listed, never re-clustered.

**An entry for an Epic entry a PRD run only listed** takes its heading, `document:`, `verdict:`, `shipped:`, `evidence:`, `decision:` and `status:` from that Epic entry, carries the run's `flags:` for it and any `withdraws:`, and names it in `lists:` in place of `ruling:`, so Phase 4 of `/dev-workflows:conformance` never takes it as ruled. While its flag holds, a later PRD run lists that Epic entry again, never asks about it, and carries this entry forward under §5 rather than adding another. Once its flag has cleared and the PE rules on it, that run writes `ruling:` in place of `lists:`, with the PE's `decision:` at `status: final`, `rationale:` and `effect:`.

**`withdraws:` carries a follow-up line a PRD run ruled must not be built**, on that run's entry for the Epic entry it rules on or lists, or, on a re-run, on the record's own `fix-code` entry it marks `requirement withdrawn` or `orphaned`: the line of an overruled `fix-code` entry, or of one whose requirement was withdrawn or is gone from its document. It is that entry's `effect:` text — the Epic entry's, or the record's own — after `follow-up proposed: `, read from whichever copy of that record the run read — a Dev's unmerged branch included — and written verbatim, never paraphrased, one field per line. It is written whether or not the run could tick the line in its checkout: `/dev-workflows:implement`'s follow-up read-back skips an open task whose line equals a `withdraws:` value of the PRD folder's record, so a line that reaches a checkout before the tick, or without it — from a Dev's branch, or a session branch — is still not built. It is never rewritten.

**`effect:` on a `fix-code` entry records the follow-up proposed, never one written.** The record is committed at the run's handoff, and the follow-up preview that comes after it can still cancel the line, so whether the follow-up was written is read from `follow-ups.md` — where the next run's re-check reads it — never from this field. Nothing rewrites the field after the preview — save where a later PRD run's ruling on an entry it only listed writes the PE's own (§3 above).

## 4. Statuses and flags

- `proposed` — an Epic run's decision, the Dev's.
- `final` — a PRD run's decision, the PE's. It wins over `proposed` wherever both exist.
- `resolved` — the code now satisfies the requirement. A re-run sets it; so does the PE marking a `stale` entry resolved.
- `stale` — an `amend-document` or `accept` entry whose requirement the merged code now satisfies, though the decision still stands: the code was changed later without the record changing. The PE marks it resolved or keeps it.
- `orphaned` — an entry whose requirement text is no longer in its document (an edited `epic.md` bullet, which has no id), or a legacy `[AD#n] Rule` entry that §3's legacy match ties to no one decision.
- `fixed` — a `fix-code` entry whose requirement the merged code now satisfies: the fix happened, and the PRD run lists it and records it `resolved` without asking.
- `still open` — a `fix-code` entry whose requirement the merged code still does not satisfy; the PE confirms or overrules it.
- `requirement withdrawn` — the requirement was superseded or withdrawn after the entry was recorded (`workflows-core:prd-format`); for a `[DT#N]` Rule, its design's entry is withdrawn or its Disposition is no longer `Mitigated` (§5).

A verdict the re-check could not settle is no flag: it is listed under `## Unverified` (§2), never as an entry.

## 5. Re-runs

A `[DD#n]` is permanent: never renumbered or reused, and its entry is never deleted. A re-run:

- carries each decided entry forward without asking again while its discrepancy persists — save an `accept` on a mitigation, which it puts again (below);
- marks an entry `resolved` once the code satisfies its requirement — which is how a fix is confirmed;
- marks an entry `requirement withdrawn` where its requirement is superseded or withdrawn — a `[DT#N]` Rule where its design's entry is withdrawn or its Disposition is no longer `Mitigated` — carries it forward, never asks about it again, and never counts it as an open fix;
- numbers new discrepancies after the highest id on file, and asks only about those and about each entry it puts again.

**An `accept` on a mitigation is put again** — the exception the first bullet names. A mitigation (§2; `/dev-workflows:conformance` Phase 1 (b) finds them) is never accepted as shipped: only the architect accepts a risk, in the threat model. So an entry of the unit's own record decided `accept`, whose discrepancy persists and whose requirement is now a mitigation, is put again at the array `/dev-workflows:conformance` Phase 4 gives a mitigation, its earlier decision shown, and keeps its `[DD#n]`. On a PRD run, the record's own entry whose `ruling:` confirms a Dev's `accept` — `confirms <EPIC-KEY>/[DD#k]`, that Epic entry decided `accept` — is put again as an overrule while its discrepancy persists, and the answer is applied as any overrule is: `ruling: overrules`, and `superseded-by` in the Epic's entry, as the last paragraph of this section says. A *Cancel* there is the walk's: the run writes nothing, and the record on file stands.

**A run that traces no threat** — its `Threats:` line reads `not traced — update workflows-core` (§2) — carries each `[DT#N]` entry on file forward as it stands: never `resolved`, never `requirement withdrawn`, its follow-up kept, since it read no `[DT#N]` Rule to judge it by.

A `requirement withdrawn` or `orphaned` entry is listed, never asked again. Where it was a `fix-code`, its follow-up is withdrawn per `workflows-core:followup-emission` § *Withdrawing a follow-up*, with the reason `(requirement withdrawn)` or `(orphaned)`.

A PRD run writes `superseded-by: <PRD-KEY>/[DD#n]` into each Epic entry it overrules — save while an unmerged `conformance/` branch carries that Epic's newer record, when it names the entry in its report and keeps the overrule in its own entry's `ruling:`, which a later PRD run applies once no `conformance/` branch carries that Epic's record, and only to an Epic entry whose heading names the same requirement, with the same `document:` — and never deletes or rewrites any other field of an Epic record.

## 6. Readers

A reader takes a `final` decision over a `proposed` one and says where it used a proposal; it treats a missing record as the absence of one, never as a prerequisite. **A reader that turns a recorded decision into a documentation decision takes which entries are open, the precedence between two entries and the mapping from `workflows-core:source-truth` §7.8**, the one authority on them. **An entry whose `document:` names `design.md` is never open there**: §7.8 leaves it out — a mitigation the design owns, settled in the design and never by a documentation decision — so neither `/docs-workflows:document` nor `/docs-workflows:release-notes` takes one, or opens a `design.md` for one. The record's readers include `/dev-workflows:conformance`'s own later runs, `/dev-workflows:implement`'s follow-up read-back of the `withdraws:` lines in the PRD folder's record (§3), and the three commands below.

**`/docs-workflows:release-notes` reads the record from another plugin and cannot load this reference.** It reads every record in its scope, with diff grounding on or off, and states in its own Phase 0 and Phase 3 what it reads: §2's `Run:`, `At:`, `Code checked:` and `Verdicts:` lines, and each `### [DD#n]` entry's heading, `document:`, `verdict:`, `shipped:`, `decision:`, `status:`, `flags:`, `ruling:`, `lists:` and `superseded-by:`. `workflows-core:source-truth` §7.8 maps each decision, and `docs-workflows:release-note-types` §8 says how a claim so settled is worded in the release note. A change to any of those fields, or to what a status or flag means (§4), is a change to that command too.

**`/docs-workflows:document` reads the record from another plugin too, and cannot load this reference either.** It reads every record in its scope and states in its own Phase 3 what it reads: the frontmatter `key:`, §2's `Run:`, `At:` and `Code checked:` lines, and each `### [DD#n]` entry's heading, `document:`, `decision:` with its `status:`, `flags:`, `ruling:`, `lists:` and `superseded-by:`. Its Phase 5.8 takes the decision a record already holds on a claim, matched and mapped as §7.8 says, in place of asking the PE again. A change to any of those fields, or to what a status or flag means (§4), is a change to that command too, and to `workflows-core:source-truth` §7.8, which states the fields its rules read.

**`/dev-workflows:ready` reads the PRD folder's record from the default branch, never the working tree,** and tests from it whether the PRD reaches the optional *Delivery verified* stage, as its Phase 1 states: §2's `Run:` line, its date included, its `At:` line, its `Not traced:` and `Not shown merged:` lines, its `Threats:` line, read as §2 says, `## Unverified`, and each entry's `decision:`, `status:`, `flags:` and `lists:` — and, beside the record, each `implementation.md` block in the PRD's tree, its heading's date and its `at:` (`workflows-core:implementation-format` §1), since a block later than the record leaves the stage unreached: later by instant where the block and the record both carry one — the record's `At:` only where §2's guard leaves it one and it passes `/ready`'s three tests there: the header's one `At:` line, a real time, and not later than `/ready`'s own start — and otherwise by the block's heading date against the `Run:` date, an equal instant or date never later. It maps no decision, so its test is its own, not §7.8's. A change to any of those, or to what a status or flag means (§4), is a change to that command too.

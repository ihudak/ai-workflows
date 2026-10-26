# /conformance

Checks what was built against what was specified — every requirement of an Epic or a PRD, traced against the Epic's branch — before its pull request merges, or after it where the branch has gone on since — or each repository's default branch once the work has merged — and has a person settle each discrepancy: fix the code, amend the document, or accept it as shipped. It needs no documentation repository, changes no code, and rewrites no requirement.

## Who runs it

The role follows the address:

- **An Epic** — the [dev](../roles-and-phases.md#dev--build-verify-and-deliver) who implemented it runs `/conformance <EPIC-KEY>` **after `/implement`, before its pull request merges**, on the Epic's branch — in each repository, the one the latest `/implement` run recorded there. A fix it finds goes back to `/implement`, which continues on that branch, so the fix joins the open pull request. The Dev's decisions are recorded as `proposed`: they record what the Dev found and thought, and the PE makes the final call.
- **A PRD** — the PE runs `/conformance <PRD-KEY>` **once every Epic is done and its pull request merged**, closing the implementation phase the PE opened with `/product-workflows:epics` and `/product-workflows:specify`. The PE's decisions are `final`, and the PE rules on every decision a Dev recorded.

Cost-attribution phase: [conformance](../roles-and-phases.md#conformance).

## Synopsis

```
/conformance <EPIC-KEY | PRD-KEY> [--skip-costs] [--skip-feedback] [--enforce-model=<model>]
```

Type it as `/dev-workflows:conformance`. It takes one address, resolved against `$SPECS_PATH`: an `EPIC-` folder is an Epic run, a `PRD-` folder (a BRD-route slice included) a PRD run. A `BRD-` container is refused with `CONFORMANCE_BRD_NOT_SLICED`, which names its slices; no address, or one that is not a key, stops with `CONFORMANCE_NEEDS_KEY`.

## How it runs

```mermaid
flowchart TD
    p0["Phase 0 — Resolve the address and gate the documents"] --> r0{"Records on file current?"}
    r0 -->|"yes"| p1["Phase 1 — Inventory"]
    r0 -->|"no — a record on an unmerged branch, or a checkout behind the default branch"| stopr(["Run ends — CONFORMANCE_RECORD_UNMERGED or _BEHIND"])
    p1 --> k{"Which run?"}
    k -->|"Epic run"| e0{"The Epic's branch, in each repository"}
    e0 -->|"found — or its work merged: the default branch"| p15["Phase 1.5 — Classify"]
    e0 -->|"no /implement run recorded"| stopi(["Run ends — CONFORMANCE_NOT_IMPLEMENTED"])
    e0 -->|"missing: every answer is Trace the default branch there"| p15
    e0 -->|"missing: any answer is Stop until the branch is found"| stopb(["Run ends — CONFORMANCE_BRANCH_MISSING, nothing traced"])
    e0 -->|"missing: Cancel, and no Stop"| stop
    k -->|"PRD run"| d0{"Every Epic shown merged?"}
    d0 -->|"yes"| p15
    d0 -->|"Trace anyway"| p15
    d0 -->|"Stop until it is merged / Cancel"| stop(["Run ends — nothing traced"])
    p15 --> p2["Phase 2 — Trace (conformance-tracer, one per repository)"]
    p2 --> p3["Phase 3 — Re-check before asking"]
    p3 --> p4["Phase 4 — The walk"]
    p4 --> p5["Phase 5 — Effects and the record"]
    p5 --> d1{"Hand off the record and notes? (consent choice)"}
    d1 -->|"Branch + commit + push + PR"| p7["Phase 7 — Report"]
    d1 -->|"Write only — no commit"| p7
    p7 --> p89["Phase 8 — Maintenance, feedback, follow-ups / Phase 9 — Session cost and commit"]
```

## What it reads, and the code it checks

**Requirements.** On an Epic run: the Epic's `specification.md` (each `[Uxx]` and `[Uxx]/[ACxx]`), the acceptance criteria and `## Contract` lines of its `epic.md`, and the `Rule` of each applicable `[AD#n]` in the ARD. The Epic's `design.md` is context for the walk, never traced. On a PRD run: every live `[AC#n]` and `[FR#n]` of `prd.md`, and each live `[US#n]` with no criteria beneath it; the PRD-level spec; and the Epics' requirements, as below. Test cases (`[TCxx]`), use cases (`[UC#n]`) and success metrics (`[SM#n]`, `[SMC#n]`) are not traced: no commit can show any of them either way. Where nothing at all is left to trace, the run stops with `CONFORMANCE_NO_REQUIREMENTS`, naming what each document lacked, rather than write a record that says nothing.

**Code — the Epic's branch, or the default branch.** Neither run switches a branch: each reads its code at a ref. Whether work has merged in a repository is read from the latest `/implement` run `implementation.md` records there, by the shared implementation-record reference (`workflows-core:implementation-format` §5). The Epic run takes the answer of that reference's branch lookup, `unit-branch`; the PRD run takes its merged test, fetching each Epic's branch first as the Epic run does. The two agree on whether work merged: the merged test reads the branch's content as well as its history — a commit carrying the unit's key counts only where the branch's own work is in it, so a teammate's commit following the convention does not mark an open pull request merged — where your clone holds the recorded commit or the branch and the pull request's work does not conflict with that commit; otherwise the key alone still counts — and a squash whose subject lost the key counts where the branch survives and the default branch already holds everything it adds.

- **An Epic run** finds, in each repository its implementation record names, the branch the latest `/implement` run recorded there — fetching that branch by name first, so a single-branch clone sees it too, and dropping a tracking ref whose branch `origin` no longer has — and traces that branch's tip, read on `origin` where your local copy is behind it, so you can run it before the pull request merges. Once that work has merged, it traces the default branch instead; where the branch went on after its merge, it traces the branch and the report says so. Where the record holds no `/implement` run at all, it stops with `CONFORMANCE_NOT_IMPLEMENTED` before writing anything. Where a recorded branch is neither shown merged nor found in the clone or on `origin`, it asks about each such repository in turn, saying on the question what it already knows — that the branch was never pushed, that `origin` does not have it, or that the clone was read as last fetched. You either stop, with `CONFORMANCE_BRANCH_MISSING` — fetch the branch where the clone was read as last fetched, push it from the clone that committed it where it was never pushed, or re-run `/implement` where its pull request closed without merging — or trace the default branch there, where you know its pull request merged under a subject that lost the key; the run goes on only if every answer is the second. A default branch traced that way on a clone read as last fetched is named as such in the report, with its age. A repository with no clone is not traced, and the report names it.
- **A PRD run** first confirms every Epic merged, in every repository it touched, by the same test, and asks before tracing where one is not shown merged.

Before reading, it fetches each writable clone's remote refs (never switching or pulling), and on a read-only mount prints the age of any ref older than fourteen days. In a shallow clone, on either run, the report warns that merged work may read as unmerged, since its merge can lie beyond the clone's depth; the run never deepens the clone. A repository with no clone under `$REPOS_PATH`, or a clone whose default branch cannot be resolved, is named, and its requirements are listed as not traced; where no repository of the run has a clone with a default branch to read, the run stops with `CONFORMANCE_NO_CODE` instead, naming each with what would fix it, and writes no record. The specifications, designs and other documents it reads are gated onto the specs repo's default branch first, before anything is read, and so is the ARD: the run stops while it sits on an unmerged branch.

Each requirement is traced where its code can live: an Epic's in its target repository and in any other repository its implementation record names, a `## Contract` line on a PRD run on both sides, and a PRD-level requirement, which names no repository, in every one. A contract line is satisfied only where both sides satisfy it, a side through any of its Epic's repositories; a side no code could show, or none of whose repositories was traced, leaves the line not-checkable unless another side has a discrepancy. Any other requirement is satisfied where one repository satisfies it and none contradicts it, so a repository that does not implement it is no discrepancy.

**A sibling Epic's part, on an Epic run.** A PRD-level `[AD#n]` Rule can bind any component of its PRD, and a `## Contract` line has a side on another Epic's component, so either can ask for something a sibling Epic — another Epic of the same PRD, with a target other than this Epic's — builds, on its own branch: the ratings service's half of a rule whose storefront half this Epic builds, say. On an Epic run each is traced without a sibling Epic's part: a part on a sibling Epic's component — read off each Epic's `target:` — is that Epic's, never a discrepancy here and never put to you, and the record names that Epic beside the requirement. A Rule that binds only components other than this Epic's — a sibling's, or one no Epic targets, such as a service the PRD only calls — is not checkable on an Epic run: the report names each component it binds, and the sibling Epic that targets it where one does, and the PRD run traces it in full. A contract line always has this Epic's own side to check. An Epic with no `target:` has nothing to tell its part by, and its run traces every part. A PRD run traces every part.

**The records on file, checked first.** Before Phase 1 reads a requirement, asks a question or scans a clone, every run checks the record of the Epic or PRD it checks — and, on a PRD run, each Epic's record — against the default branch and every `conformance/` branch, after fetching those branches from the specs repo's remote, best-effort and refs only, pruning any the remote deleted. Where an unmerged `conformance/` branch other than the one your checkout stands on carries a version of the unit's record the default branch does not hold — the record of a run whose pull request is still open, say a Dev's re-check after a fix — it stops with `CONFORMANCE_RECORD_UNMERGED`, naming the branch. Where that branch is the unit's own: merge its pull request, switch `$SPECS_PATH` to it to resume that run, or discard that record by deleting the branch both on the remote — close its pull request and delete the branch there, or `git -C "$SPECS_PATH" push origin --delete <branch>` — and locally, `git -C "$SPECS_PATH" branch -D <branch>`, since the run reads local branches as well as remote ones and a branch left on the remote comes back with the next fetch; then re-run. Deleting it is also how to clear one whose pull request has merged already or was closed without merging. Where it is another run's branch — a PRD run's that marked the Epic's entries superseded, say — merge it, or, where its pull request has merged already or was closed without merging, delete it on the remote and locally the same way. A branch does not count where the default branch's history has ever held its copy of the record — merged by a merge, a squash or a rebase, even where the default branch changed other lines beside it — or where it only inherited the record from the default branch. A squash or rebase whose merge combined the record with another change to it — a conflict resolution, or a clean merge beside a nearby edit of the record — lands a copy the branch never held, so that merged branch still counts until you delete it, and so does one closed without merging. On a PRD run such a branch is no newer record: answer *Use the merged record instead* (or, where there is none, *Trace this Epic in full instead*) and delete it. On a PRD run, a Dev's unmerged record of an Epic stops nothing: the run asks whether to read it from its branch, beside or in place of a merged one. Where your checkout lacks a record the default branch holds, or holds an older copy that predates its last change, it stops with `CONFORMANCE_RECORD_BEHIND`. On another branch — a stale `design/` or `ready/` branch the preflight kept you on, which only the default branch's catch-up would have refreshed — switch to the default branch, or merge the default branch into it; on the default branch itself, behind its remote because a guard kept the preflight from catching it up, run `git -C "$SPECS_PATH" pull --ff-only`; then re-run. A checkout on your own `conformance/` branch, whose newer record is built on the merged one, is a resumed run and goes on. Where a PRD folder holds two Epic folders asserting one key, it stops with `CONFORMANCE_EPIC_FOLDERS`, naming them, for you to merge. Carrying on past any of these would number decisions over ones already taken, rule on a Dev's old entries, and queue follow-ups twice.

**A PRD run does not re-trace every Epic.** It traces the PRD-level requirements in full, and any Epic with no record. For each Epic, a record a Dev left on an unmerged `conformance/` branch — pushed from the Dev's own clone included — is offered to read from there, beside an older merged one or where there is none. While such a branch is open, the run writes nothing into that Epic's record, whichever copy it read: an entry the PE overrules is named in the report, and the PRD's own record keeps the ruling, which a later PRD run applies once no `conformance/` branch carries that Epic's record — and only to an entry naming the same requirement, since a record discarded unmerged frees its numbers for reuse. A follow-up is withdrawn all the same wherever your checkout's `follow-ups.md` holds it; a line your checkout does not hold yet is ticked by a later PRD run once your checkout holds it. Either way the PRD's record carries the line as `withdraws:`, so `/implement` never builds it wherever it turns up, a Dev's branch or a session branch included — as long as the PRD's record is on the default branch or in your working copy. For an Epic with a record, it re-checks each of the Dev's entries against the merged code: an *amend* or *accept* the code now satisfies is flagged *stale* — how a Dev who fixed the code later without updating the decision is caught — and a *fix the code* the merged code satisfies is *fixed*, listed and resolved without asking. A requirement the Epic run found satisfied, which the record lists with its evidence, is re-traced only where the code at that evidence has changed since, or where the commit the Epic run traced — its branch's tip, before the merge — is not in your clone. A re-run of either kind asks only about what is new.

Before tracing, every run prints how many requirements it will trace across how many repositories.

## The walk

Every discrepancy the re-check confirms is put to you, one question at a time, with no answer recommended — which one is right is the question itself:

- **Fix the code** — the document is right. A follow-up task goes to the Epic's folder in the form the next `/implement` of that Epic reads back on its own. On an Epic run it goes out at once. On a PRD run, a PRD-level requirement needs an Epic to carry the fix: the PRD's only Epic, or the one Epic whose `## Covers` lists it — or lists the user story it sits under — where exactly one does, and otherwise you are asked which, each Epic that lists it marked; only a PRD with no Epics takes the task in its own folder, for `/implement <PRD-KEY>`.
- **Amend the document** — the code is right. On a PRD run the run adds a note under `## Engineering review` on the spec, PRD, `epic.md` or ARD, recommending the command that changes it. On an Epic run it is recorded as a proposal only, for the PE.
- **Accept as shipped** — the difference stands, recorded with your rationale.

On a PRD run, the Dev's decisions where the implementation won come first, then the Dev's *fix the code* decisions, then anything no Epic recorded. Overruling a Dev decision marks it superseded in the Epic's record and withdraws its follow-up — while an unmerged branch carries that Epic's newer record, the mark waits for a later PRD run, as above, and so does a follow-up your checkout does not hold yet; confirming a *fix the code* whose follow-up is no longer open — done, cancelled at the Epic run's preview, or one the PRD's own record withdraws — queues it again, while one your checkout does not hold yet but the Dev's unmerged `conformance/` branch does is left to arrive with that branch, and named in the report beside it. One only a session branch holds is one the run cannot see, so it is queued again, and the two stand side by side once that branch merges. A *fix the code* whose requirement has since been withdrawn, or whose text is gone from its document, has its follow-up withdrawn by any run that re-checks it and can reach the line.

## What it produces

- `_conformance.md` in the checked folder: the ref and commit it checked in each repository — the Epic's branch where an Epic run traced it, and otherwise the default branch — the counts by verdict, and one `[DD#n]` entry per discrepancy with its decision and status. Its ids are permanent, and a re-run asks only about what is new, marking an entry resolved once the code satisfies it.
- Follow-up tasks for *fix the code*, and `## Engineering review` notes for *amend the document* on a PRD run.
- A handoff of the record and the notes on a `conformance/` branch, behind the usual consent choice. On a PRD run whose record withdraws follow-ups, the choice first says how many: `/implement` on another clone skips them only once the record is on the default branch, so declining keeps them in your working copy alone.

## Gates

No agent decides anything. Each discrepancy a tracer reports is re-checked at the location it cites before you see it; one that does not hold is dropped, with the reason in the report, and on an Epic run one that rests on a sibling Epic's part is judged again without it. One the re-check can settle neither way — a "satisfied" without evidence among them — is unverified: listed in the report and the record with what would settle it, never put to you, and traced again in full by the next run. The documents it reads must be on the specs repo's default branch.

## Cost

Each run is charged to phase `conformance`, with the role taken from the folder: `dev` for an Epic run, `pe` for a PRD run, and `pe` too for a `BRD-` container it refuses. `--skip-costs` (or `WORKFLOWS_SKIP_COSTS`) skips the cost entry; see [Session cost](../reference/session-cost.md).

## Session feedback

The maintenance phase runs as on `/ready`, and its plugin-facing lessons are persisted as feedback. `--skip-feedback` (or `WORKFLOWS_SKIP_FEEDBACK`) narrows it to bug capture only; see [Session feedback](../reference/session-feedback.md).

## Example

`/implement BOOK-1-02` opens its pull request, and the Dev runs `/conformance BOOK-1-02`, which traces the Epic's branch. The spec says a restock notice fires within one minute; the branch schedules it every five. The Dev chooses *Fix the code*: `[DD#1]` is recorded as proposed, and the follow-up is read back by the next `/implement BOOK-1-02`, which continues on the Epic's branch, so the fix joins the open pull request; a re-run then marks `[DD#1]` resolved, and the pull request goes to review. Once every Epic of `BOOK-1` has merged, the PE runs `/conformance BOOK-1`: overrules one Dev decision, marks a stale one resolved, and settles a PRD-level gap by amending the PRD.

## See also

- [`/implement`](implement.md) — offers this command as its next step after an Epic, to run before its pull request merges, on the Epic's branch.
- [`/ready`](ready.md) — the readiness gate before implementation; this command is the check after it.
- [Follow-up tasks](../reference/follow-ups.md) — where *fix the code* follow-ups land, and how a withdrawn one is marked.
- [Roles and phases](../roles-and-phases.md) — the Dev's Epic run and the PE's PRD run.

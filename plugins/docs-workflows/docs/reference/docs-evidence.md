# Evidence and walkthroughs

A documentation page makes claims: this button is called that, this endpoint takes those fields, this service talks to that one. **Evidence is what a claim rests on**, and this family treats it as a recorded thing rather than an assumption — because the alternative is a page that was right when somebody wrote it and has been quietly wrong ever since.

This page explains what counts as evidence, what happens to a claim nobody could check, and how to walk a verification checklist by hand. The runnable version is the plugin's own `references/docs-audit/evidence-contract.md`.

## What counts as evidence depends on who the page is for

There is one set of rules with two implementations — one for a page a person uses the product with, one for a page somebody builds it with:

| | A page for users | A page for engineers |
|---|---|---|
| Shaped like | A Diátaxis quadrant — tutorial, how-to, reference, explanation | An architecture section, a decision record, a runbook, a generated API reference |
| Evidence comes from | Routes, views, the interface strings themselves, plus a walkthrough | Code, config, and the ARDs and design docs in the specs repo |
| A claim is settled by | **Looking** — a walkthrough step confirms it | **Reading the code** |
| It goes stale when | Behaviour changes: a route, a label, a flow | Structure changes: an interface, a module, a dependency |

**The third row is the one that matters.** A claim about what a user sees is a claim about what is on the screen, and reading the code that renders it is a different act from looking at it — plenty of labels come from a translation file, a feature flag, or a config value nobody remembered. A claim about how the system is put together is settled exactly by reading the code, and no amount of clicking establishes it. Swapping the two methods is how a page ends up confidently wrong about the half nobody actually checked.

## The three kinds of evidence

A page records its sources in its frontmatter. There are three kinds:

| Kind | Records | How it gets re-checked |
|---|---|---|
| `code` | The repository, the file path, and the commit | Read that path, then read it again at today's commit |
| `walkthrough` | The walkthrough's id | Walk it again |
| `artifact` | The path of a committed document, and `ref` — the commit it was read at | Read it again at that `ref` and see whether the wording moved |

```yaml
evidence:
  - { kind: code, repo: example-webapp, path: src/routes/orders/new.tsx, ref: <sha> }
  - { kind: walkthrough, id: W-001 }
  - { kind: artifact, path: specifications/PRD-ACME-77-orders/release-notes.md, ref: <commit> }
```

**`artifact` is for a claim whose source is a document rather than code or a screen** — a release-notes draft, an ARD, a design doc. It is its own kind because prose changes by being re-worded, not by being re-implemented, and that is a different thing to watch for.

It always records the commit, in `ref`, and that is the whole reason it is worth recording. A path on its own only tells you the document is still there. A path and a `ref` tell you whether it still *says* what the page claims it says, and only the second of those is evidence.

## A claim nobody could check is marked, not smoothed over

Individual sentences are not tracked. The frontmatter says what the page as a whole rests on; nothing keeps a map from claims to sentences, because a map like that is out of date two edits after somebody stops maintaining it.

What is tracked is the exception. **A claim that could not be verified is marked inline, in the prose, using the same `[NEEDS CLARIFICATION]` marker `/idea` uses.** It looks like this on the page:

```markdown
The export runs nightly [NEEDS CLARIFICATION: no schedule found in the code; confirm with the owning team].
```

**A marked claim never quietly becomes a fact.** There are exactly two things that can happen to it: a verification pass confirms it, and the marker comes off because the claim has been settled — or the page ships with the marker still visible. There is no third option, and in particular "the page is being published now, so let us tidy that up" is not one. A reader who meets a marker learns something true; a reader who meets the smoothed-over version learns something the writer did not know.

This is also why a page carrying markers is not counted as done. [The backlog's](docs-backlog.md) coverage fraction counts units that reached `published`, and a marked page cannot get there by either route: it has not been verified, and an audit refresh that finds it reads the markers and files the unit as `drafted` instead. Resolve the markers and the page counts; leave them and the grid keeps saying, correctly, that the work is not finished.

## Walking a checklist by hand

A **walkthrough** is a short structured file: a role, the environment it was written against, its preconditions, and numbered steps, each with an action, a target and what you should see. It lives beside the backlog, at `.dev-workflows/walkthroughs/<id>.yml` — `W-001` in `W-001.yml` — and the unit that uses it records the id rather than the path. It is stored in that shape from the start so that a browser driver can execute the very same file later without anybody rewriting it.

**A step's action is one of five words, and there is no sixth.** `navigate`, `click`, `type`, `select`, `wait`. The list is closed because a driver has to implement every verb in it, and a verb a writer invented is one no driver supports — so a step you cannot write with these five is worth reporting rather than working around. You will be writing these by hand for now, so it is worth knowing the list is short on purpose.

Today you walk it yourself. Take each step in order, do the thing, and answer with one of three:

| Your answer | Means | You also write down |
|---|---|---|
| `confirmed` | it did what the step says it would | nothing |
| `differs` | it worked, and showed you something else | **what it actually said** — required |
| `blocked` | you could not establish what the step did | why — a precondition that was not met, an environment that would not start, or a step you took whose expected result you had no way to check |

**Writing down the actual text on a `differs` is the part that pays for the whole exercise.** "Step 4 failed" sends somebody back to the environment to find out what it says instead. "Step 4 shows *Create order*, not *New order*" **is** the page edit, already written down by the person who was looking at the screen — a correction rather than a red X. A `differs` with nothing written down is an incomplete answer: the verification command will ask you again rather than record it, and walking by hand the rule is the same — do not write the answer down until you have the text in front of you.

Your answers are written back into the same file, on the step they belong to. `outcome` is one of the three words above, and **each of the two other fields belongs to exactly one outcome**: `observed` carries the text you saw and is written on a `differs` and on nothing else, and `note` carries the reason and is written on a `blocked` and on nothing else — a note on a `confirmed` step is a comment nothing has a rule for.

```yaml
  - n: 2
    action: click
    target: { label: "Add item" }
    expect: { kind: visible, label: "Item details" }
    result: { outcome: differs, observed: "Line item details" }
  - n: 3
    action: click
    target: { label: "Submit" }
    expect: { kind: visible, label: "Order placed" }
    result: { outcome: blocked, note: "payment sandbox would not come up" }
```

When a driver arrives, it reads that same file, takes the same steps and writes the same three outcomes back in the same place. Nothing about the format changes — which is why it is worth writing walkthroughs in it now, before there is anything to run them.

## See also

- [The documentation backlog](docs-backlog.md) — the file that tracks which pages exist and which state each one is in.
- [The coverage model](docs-coverage-model.md) — what the audit counts, and what decides the order pages get written in.

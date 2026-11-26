# The documentation route

A portal is not finished when it builds. [`/docs-init`](commands/docs-init.md) gives you a site that builds, lints and serves with a stub in every section, and [`/docs-audit`](commands/docs-audit.md) gives you a prioritised list of every page that site is missing — and then you are holding a backlog with no stated order to work through it. This page is that order: from an empty repository to a portal whose coverage grid says the work is done, step by step, with the parts no command runs written out as the procedure a person actually follows.

**Five of the eight steps below run a command. The other three you do by hand, and this page says how.** Read *by hand* as **no command of this plugin does that step for you** — not as *no command helps*: [`/document`](commands/document.md) in direct mode will apply an edit you describe to a page and style-check it, though it reads no backlog and moves no unit. Where a command is planned to automate a step, it is named at the end of that step, as what may change later and never as something to type. **Nothing on this page asks you to run a command that is not installed.**

## The route

```mermaid
flowchart TD
    subgraph ONCE["Once — stand the portal up"]
        INIT["▶ start — /docs-init — scaffold the repository"]
        SERVE["/docs-serve — look at it"]
        AUDIT["/docs-audit — the backlog"]
        INIT --> SERVE
        SERVE --> AUDIT
    end
    subgraph LOOP["Repeatedly — until the coverage threshold is met"]
        WRITE["/docs-write — write the next unit"]
        CAPTURE["capture what the page shows — by hand"]
        VERIFY["verify the marked claims — by hand"]
        WRITE -->|"a how-to or a tutorial"| CAPTURE
        WRITE -->|"anything else"| VERIFY
        CAPTURE --> VERIFY
        VERIFY --> WRITE
    end
    subgraph CADENCE["On a cadence"]
        REFRESH["/docs-audit --refresh — the product grew a surface"]
        ROT["re-read what review_by has aged — by hand"]
    end
    AUDIT --> WRITE
    VERIFY --> REFRESH
    VERIFY --> ROT
    REFRESH --> WRITE
    ROT -->|"a page rewritten by hand — walk it"| VERIFY

    classDef entry stroke:#dc2626,stroke-width:3px
    class INIT entry
```

Every node carrying *by hand* is a step nothing in this plugin runs for you. The loop in the middle opens with [`/docs-write`](commands/docs-write.md), which drafts a unit's page from the product's code and specifications, and goes on by hand on purpose: a page drafted from the code has not been checked against the product, and walking its claims — on the screen for a user page, in the code for an engineering one — is what checks it. [Workflow overview](workflow.md) draws all eight of this plugin's commands and where each sits; this page draws only the ones on this route, plus the work between them.

---

## Once, to stand the portal up

### 1. `/docs-init` — scaffold the repository

```
/docs-workflows:docs-init /workspace/docs
```

Confirm the code repositories the portal documents — that set becomes the denominator every later coverage figure is a fraction of, and where you confirm one it is written into the profile, so the audit in step 3 does not have to ask again. Approve the logo and colour pair [`/docs-brand`](commands/docs-brand.md) extracts when the run offers them; it never applies branding silently. The run commits the scaffold on a branch and drafts a pull-request message, and **it never pushes and never merges** — pushing the branch, opening the pull request and merging it are yours. What you have afterwards is a content tree with a stub in every section saying what belongs there, two builds over it — a public site and an internal one, or one if you passed `--public-only` — a linter, a CI workflow carrying the visibility gates, and `.dev-workflows/docs-profile.yml`. The run verifies both builds, the linter and the visibility gate against built output; it never starts a server, which is what step 2 is for.

A documentation repository that already exists does not need this step. Run [`/docs-profile`](commands/docs-profile.md) against it instead — that writes the same profile the rest of this route reads — and start at step 2.

### 2. `/docs-serve` — look at it

```
/docs-workflows:docs-serve
```

It starts the repository's own dev server and reports a URL; opening it is yours. **Expect the caveated one.** `/docs-serve` reports the profile's `public_base_url` where one is recorded and the in-container address with an explicit caveat where none is — and `/docs-init` deliberately does not invent that value, so on this route, one step after the scaffold, the caveated address is the case you will get. Inside a container it will not open from your browser until somebody records the real host mapping in `dev_servers.servers[].public_base_url`; until then, reach the port your container publishes.

This step is here because seeing the empty portal is what makes the rest of the route concrete — a skeleton of stubs reads very differently on a screen than in a directory listing.

### 3. `/docs-audit` — the backlog, and the first real decision

```
/docs-workflows:docs-audit
```

The run enumerates the surfaces the product has, crosses each with the page types it earns, ranks the result and writes `.dev-workflows/docs-backlog.yml`. **Then read what it printed, because everything downstream obeys that file.** Three things are yours to settle before you write a line of prose:

- **The top twenty units and the `priority_reason` under each.** Correct the ones that are wrong. A reason you edit is preserved by every later run — the test is mechanical, so nothing has to guess what you touched.
- **The tutorial candidates.** Which journey a role should learn first is the one judgement no scan can make, so the run proposes and you pick, by setting `picked: true` on a `tutorial_candidates[]` entry. The pick becomes a real unit on the **next `--refresh` run** (step 7), once each and never twice.
- **Commit the file, and the profile with it.** The run leaves the backlog in the working tree and neither branches nor commits in the documentation repository; the backlog is meant to be tracked and reviewed in a pull request like anything else. Where the run recorded the code repositories you confirmed as the profile's `source_repos[]`, the profile has changed too. [`/docs-write`](commands/docs-write.md), step 4, starts only once both files are tracked and neither has changed since its last commit: otherwise it stops before writing anything and names the file to commit, on the branch the repository stands on. Where one of your project's own `.gitignore` rules catches the path, the run names the rule and the file it is in and writes the backlog anyway, rather than force-adding past a rule your project chose. Getting it committed is then yours to decide — changing the rule is the cleaner answer, and forcing the add is the other one.

**A run that enumerated no surface at all writes no backlog**, and that is not a failure: no plan is made, an existing file is left exactly as it was, and the report says whether the product genuinely has none of these things or the scan could not tell. Settle that before step 4, which has nothing to open otherwise.

[The documentation backlog](reference/docs-backlog.md) is what each block holds; [the coverage model](reference/docs-coverage-model.md) is what the words in it mean.

---

## Then, repeatedly, until the coverage threshold is met

These three steps are the loop: [`/docs-write`](commands/docs-write.md) drafts a unit's page, and the two steps after it are yours.

### 4. Write the next unit — `/docs-write`

```
/docs-workflows:docs-write --next
```

[`/docs-write`](commands/docs-write.md) drafts the page for a backlog unit from that unit's own evidence, and commits the page, its navigation and the unit's move to `drafted` together, in one commit on a branch of the documentation repository. `--next` takes the next unit it can draft. Name one instead with `/docs-write <unit-id>`, or take up to ten in one run with `--batch <n>`, which leaves out tutorials and how-tos, whose process a batch should not draft unwatched.

**What it selects, and what it refuses.** `--next` goes through the units lowest priority number first, then in file order, and takes the first it can draft. That is a unit whose `status` is `missing` **and whose `blocked_by` is empty** — the second half is not a formality: a run records `blocked_by` and leaves the `status` alone, so a blocked unit is still `missing`. It is also a unit whose backlog entry has a `page_path:` line (`null` until a page exists), no page already carries the id of, whose surface still resolves, whose type, audience and visibility the coverage model admits, whose walkthrough, where it names one, is a regular file of at most 1 MiB under `.dev-workflows/walkthroughs/`, whose evidence the run can read, for which, where it is internal, the profile records an internal build to keep it off the public site, and which is not the *What's new* page of a release version, whose content is that version's [`/release-notes`](commands/release-notes.md) drafts, pasted in by hand. `--next` and `--batch` pass over a unit that fails any of these, and over one that a branch not yet merged, or the default branch since your branch left it, has already moved; a unit you name that fails one stops the run, with a line naming the one thing to change. [`/docs-write`'s failure modes](commands/docs-write.md#failure-modes) list them all.

`[surface-removed]` means the last `--refresh` no longer found that unit's surface — and since a refresh re-derives `surfaces[]`, the row the unit's evidence came from is gone with it — while `[page-missing]` means its recorded page is not where the backlog says. Both are judgements a run cannot make and left for you: a surface vanishing is as likely to be a repository nobody mounted as a feature genuinely removed. Settle each token, then clear `blocked_by`; until you do, `--next` and `--batch` pass the unit over, and naming it stops the run. The list is open, so a unit may carry a token somebody added by hand for a reason of their own.

**What the unit tells it.** Its `type` is the shape of the page — the four user types are the Diátaxis quadrants (`tutorial`, `how-to`, `reference`, `explanation`) and the four engineering types take the shape their own tradition fixes: an `architecture` page is an arc42 or C4 section, a `decision` page is a MADR record, a `runbook` is a runbook, and `api-reference` is generated API reference. Its `audience` decides what its claims may rest on. Where the unit names a `surface`, that row in `surfaces[]` carries the `evidence[]` list of the files to read; where the unit's `surface` is `null` — a page somebody added by hand for something the code does not imply — the evidence is on the **unit** instead, in its own `evidence` list, and a tutorial's journey adds the evidence of each surface it passes through. The run scans each code repository that evidence names at its default branch, and reads an architecture decision record, the one specs document it reads, at the specs repository's default branch — never a working-tree copy. [Evidence and walkthroughs](reference/docs-evidence.md) is what those files entitle a page to assert: a claim about what a user sees is settled by looking at it, and a claim about how the system is put together is settled by reading the code, and swapping the two is how a page ends up confidently wrong about the half nobody checked.

**What it asks before it writes.** It takes the unit's recorded `page_path`, or finds a place for the page, then asks once, showing each unit with its page path, each file that will gain the page's entry, each code repository and decision record it will read — one outside `$REPOS_PATH` marked as admitted only by your answer — the branch, and every build and lint command it will run, verbatim. Nothing is written, and no repository is scanned, before that answer. It then continues on the branch you stand on, or cuts a new one from the default branch, asking which where you stand on a branch other than the default, and asks about any uncommitted change it finds there before it writes. That question says how many commits of the default branch your branch lacks, where it lacks any — counted against `origin`'s default branch as last fetched, or the local one where `origin` has none. Where the default branch moved a unit the run will draft after your branch left it — a unit drafted and merged meanwhile, which only a unit you named can be — it names the unit and says continuing drafts it a second time, since the run reads your branch's backlog; where the run could not tell, in a shallow clone, on an orphan branch or where a backlog could not be read, it says continuing may. Either way it recommends neither answer: cutting a new branch, or merging the default branch into yours first, reads the move.

**What the page carries.** Its frontmatter, and the lines that open its body:

- **The four keys this family reserves** — `type`, `audience` and `visibility`, from the unit, and **`unit: <the unit's id>`**, which is the link in both directions: it is what a later `--refresh` matches the page back to. The run writes `unit:` only in the commit that moves the unit, so a page that never reached that commit carries no unit id, and no refresh ever matches it to the unit.
- **`evidence:`** — one entry per source the page rests on, in the three-kind shape [Evidence and walkthroughs](reference/docs-evidence.md) fixes. A `code` entry's `ref` is the commit the run's scan of that repository read, never the commit the backlog recorded, and an `artifact` entry's `ref` is the specs commit the decision record was read at. Step 6 re-reads the code *at the ref the evidence entry records*.
- **`review_by`** — a date: the day of the run plus 90 days for a surface of `high` volatility, 180 for `medium`, 365 for `low`, and 180 for a unit with no surface. Step 8 sorts your pages by it.
- **The markers.** Every claim the evidence does not ground is marked `[NEEDS CLARIFICATION: why]` inline, where a reader meets it, and the page's first body line is one more marker, for the page as a whole, saying it was drafted from the product's code and specifications and has not been checked against the product itself. On an internal page that line comes second, after the internal marker below. Step 6 is where they come off.
- **The internal marker, where the page is internal** — `<!-- docs-visibility: internal -->`, the first line after the frontmatter, for the reason the procedure below gives.
- **Image slots.** Where the unit names a walkthrough, each capture it lists becomes a `<!-- docs-image-slot: <slot> -->` comment where the page describes what that capture shows, for step 5 to fill.

**The navigation.** Where the profile records its builds and every build config carries the generated `nav:` block a `/docs-init` scaffold writes, the run regenerates that block — each section's pages sorted on their frontmatter `order`, then `title`, a page with no `order` after every page that has one — so you place nothing. Otherwise it adds the page's entry beside its siblings in each navigation config holding a `nav:` block and in each page its placement search names as linking to the new one, each listed in the question above — an internal page's entry going only on internal pages and into the internal build's config. Where there is neither, the repository's own navigation decides.

**The build, the review and the commit.** Before the unit moves, the page goes through a style check — the repository's own linter and the semantic prose pass, with one fixer pass over what they find and a question to you over anything left — then every build the question showed, which must pass, and an Opus review, its findings triaged before any fix, with one fix cycle and one re-review. Then the page, its navigation and the unit's move — `status: drafted`, and its `page_path` where none was recorded — go into one commit, `docs: draft <unit-id> (<type>, <audience>)` or your profile's commit convention where it takes only a summary. After the last unit the run offers one push, never forced, and prints a pull-request draft in its report — the units moved, their pages, the review verdicts, the builds and the markers left — which it writes to no file; no pull request is opened. A batch's units stack on one branch, and so make one pull request.

**A unit that does not commit** — a build still failing, a review finding you defer, a cancel once the branch is settled — carries no `unit:` line. Every file the run created for it is moved under `.dev-workflows/unfinished/<unit-id>/`, or the next free `-2`, `-3` directory, every file it edited for it is restored, nothing is deleted, and a batch ends there, the units before it committed. The next run names each such directory and reads nothing in it; they block nothing, and what becomes of them is yours.

**Watch `visibility` against `page_path`.** The two-build split decides by path: a page is internal because it sits under `docs/internal/`, and nothing in either build reads the `visibility` value. So a unit marked `visibility: internal` whose `page_path` is outside that tree describes a page that **ships publicly**, with both build gates green. `/docs-write` puts an internal unit's page under its content root's `internal/`, refuses an internal unit whose recorded `page_path` lies elsewhere, and refuses one outright where no build the profile records keeps an internal page off the public site. By hand, set the pair in one edit. [Documentation visibility](reference/docs-visibility.md) is the model behind it.

#### A page written any other way

A page `/docs-write` does not write — one it refuses, such as a release's *What's new* page or a unit resting on a document it does not read — is written by hand, and these steps are then yours. Create the page under the section its surface belongs to, in the content root the profile declares for it. Then its frontmatter, and one line beneath it:

- **The four reserved keys** — `type`, `audience`, `visibility` and `unit: <the unit's id>`, as above.
- **`evidence:`** — **a `code` entry carries a `ref`, and where the evidence came from a surface this frontmatter is where that `ref` first gets written**: a surface's `evidence[]` rows carry a repository and a path and no commit, so the commit to record is that repository's entry in the backlog's own `sources[]`, which is the commit the audit's scan read. (A `surface: null` unit's own `evidence` list already carries its refs — copy them across.) A page written without one leaves step 6 nothing to read against.
- **`review_by`** — a date. Nothing sets it on a page written by hand, so a page written without one is a page step 8 can never surface.
- **The internal marker, where the page is internal.** Every file under `docs/internal/` carries `<!-- docs-visibility: internal -->` as its **first line after the frontmatter**. It is an HTML comment because it has to survive into the built output, where the CI marker gate greps for it — a frontmatter key would be consumed by the renderer and never reach the artefact. A hand-written internal page missing it fails nothing at all and silently weakens that gate, which is the only defence against an internal snippet leaking into a public page.

Mark every claim you could not ground with `[NEEDS CLARIFICATION: why]`, in the prose, where a reader meets it — a marked claim is never quietly smoothed into a fact, and a page ships with its markers showing rather than being held back over one unresolved sentence.

**Add the page to the navigation.** The scaffold's configs list every page in a `nav:` block, sorted in each section by the pages' frontmatter `order`, then `title`, and the public build runs in strict mode with a page missing from that list reported — so a page left out fails `mkdocs build --strict`, locally and in CI. On a page written by hand, place its entry yourself, exactly where that sort puts it: a public page into `mkdocs.yml` and, where the scaffold has one, `mkdocs.internal.yml`; an internal page into `mkdocs.internal.yml` alone. Placed by the rule, the entry is what the next regeneration of the block — by `/docs-write`, or by a keyed `/document` run — holds anyway; placed anywhere else, it is moved there the next time the block is regenerated.

**Then update the unit** in the same commit as the page: `page_path` to where you put the page, and `status: drafted`.

### 5. Capture what the page shows — by hand

A `how-to` or a `tutorial` needs the sequence of screens it describes, and **that sequence is not derivable from routes** — which is why this step exists whether or not a command ever runs it.

**Walk the flow in a real environment** and screenshot each step the page describes. Where the unit names a `walkthrough`, follow it; no command composes one, so a unit has one only because somebody wrote it. Where there is none, walk the flow yourself and consider writing the file as you go — the format is frozen now so that a browser driver can execute the very same file later, without anybody rewriting it.

A walkthrough lives at **`<top>/.dev-workflows/walkthroughs/<id>.yml`**, where `<top>` is the git top level of the documentation repository — the same home as the backlog and the profile, and not the content root, which matters where the site sits in a `site/` or `website/` directory below it. The unit records the **id** and never the path. This is the whole shape:

```yaml
walkthrough:
  id: W-001
  unit: U-001
  role: customer
  environment: docker              # which environment it was written against
preconditions:
  - "catalog seeded"
  - "signed in as customer"
steps:
  - n: 1
    action: navigate               # navigate | click | type | select | wait — and no sixth
    target: "/orders/new"
    expect: { kind: heading, text: "New order" }
captures:
  - { slot: img-order-form, after_step: 1, shows: "the empty order form" }
```

**The action vocabulary is closed at those five words**, because a driver has to implement every one of them and a verb a writer invented is a verb no driver supports; a step you cannot express with the five is worth reporting rather than working around. `expect.kind` is deliberately *not* closed. Each entry in `captures` names a **slot** — a placeholder in the page, which the screenshot you take then fills; on a page `/docs-write` drafted it is already there, as a `<!-- docs-image-slot: <slot> -->` comment, and on a page written by hand you leave it yourself — so `slot` is the name that connects the image you produce to the place it belongs.

**Where the images go is the profile's `images.policy`, and it has three values — check which one your repository records before you save anything:**

| `images.policy` | Where a screenshot goes | Replacing one |
|---|---|---|
| `in-repo` (the scaffold's default) | Committed under `images.root` (default `docs/assets`) and referenced by relative path — **but an internal-only image goes under `docs/internal/` instead**, see below | Overwrite the same path — one path per slot, never a new filename beside the old one |
| `object-store` | An S3-compatible bucket; every public-build URL must resolve under `images.public_prefix`, internal media under `images.internal_prefix` | Overwrite in place, as above — and sweep orphans, since deleting a page does not delete its objects |
| `cdn` | You upload it and supply the URL; no binary is ever committed | A CDN URL is immutable, so a replacement is a **new** URL and the page edit is a URL swap |

Under `in-repo`, `images.max_bytes` (default 300 KB) is the CI budget checked per image, and one over it fails that check — prefer SVG, then an optimised PNG. `images.root` and `images.max_bytes` mean nothing under the other two policies, and `images.public_prefix` means nothing under `in-repo`.

**Under `in-repo`, an image only internal pages may see belongs under `docs/internal/` and never under `images.root`.** This is the trap in the step, and it is invisible from inside the repository: a file under `images.root` is copied into **both** builds whether or not any page references it, because MkDocs copies the content tree and does not trace references. So a screenshot of an internal screen, saved to the shared assets directory and referenced only by an internal page, **ships in the public site** — and neither CI gate fires. The first sees no cross-link, because there is no link; the second greps the public output for the visibility marker, which an image cannot carry. Knowing the rule alone is not enough here, which is why the mechanism is spelled out: the instinct that an unreferenced file is harmless is exactly the instinct that is wrong. The same separation that drops internal *pages* from the public build drops internal *files*, and it works on path and on nothing else. [Documentation visibility](reference/docs-visibility.md) is the whole model.

*Later: `/docs-capture` is planned to drive the capture and fill the slots a walkthrough names. No such command exists yet.*

### 6. Verify the marked claims — by hand

**For a user page**, walk the steps in a real environment and answer each one:

| Answer | Means | You also write down |
|---|---|---|
| `confirmed` | it did what the step said it would | nothing |
| `differs` | it worked, and showed something else | **the text you actually saw** — required |
| `blocked` | you could not establish what the step did | why: a precondition unmet, an environment that would not start, an expected result you had no way to check |

**Writing the observed text down on a `differs` is what pays for the exercise.** "Step 4 failed" sends somebody back to the environment to find out what it says instead; "step 4 shows *Create order*, not *New order*" **is** the page edit, already written by the person who was looking at the screen. A `differs` with nothing written down is an incomplete answer — do not record it until you have the text in front of you.

Answers go back into the walkthrough file, on the step they belong to, and **each of the two extra fields belongs to exactly one outcome**: `observed` carries the text you saw and is written on a `differs` and on nothing else; `note` carries the reason and is written on a `blocked` and on nothing else. A note on a `confirmed` step is a comment nothing has a rule for.

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

**For an engineering page**, re-read the code at the ref the evidence entry records, and again at today's commit. There is no environment to stand up and nothing to walk — the reading is the whole of it.

**Then dispose of each marker.** A claim that survives becomes prose and its `[NEEDS CLARIFICATION]` marker comes off, because the claim has been settled. One that does not **stays marked** and ships marked — there is no third disposition, and "the page is being published now, so let us tidy that up" is not one of them.

**A drafted page's own marker comes off once every claim is walked.** A page `/docs-write` drafted carries a marker for the page as a whole, saying it has not been checked against the product: its first body line, or, on an internal page, the line after `<!-- docs-visibility: internal -->`, which stays where it is. Remove the page-level marker once you have walked every claim on the page; until then a `--refresh` that meets the page lands its unit on `drafted`, never `published`.

**Then set the status, and the two cases end differently.** A page you resolved every marker on goes `status: verified`, and then `published` when the page actually ships. **A page still carrying a marker takes `drafted` and stops there** — it may be merged and deployed with the marker showing, which is what *ships marked* means, but its unit may not reach `published` by any route: not the ordinary one, which runs through `verified`, and not the `--refresh` reconciliation, which reads the page, finds the marker and lands the unit on `drafted` itself. Resolve the marker and the unit moves on; until then the grid says, correctly, that this one is not finished.

**`verified → published` has no command behind it, now or later** — that transition is a branch merged and a site deployed, which happens in your repository. It is worth knowing which arrow that is, because `published` is the state the coverage fraction counts, and there is deliberately no arrow from `drafted` straight to it: if there were, the grid could go green over pages the family knows it never walked.

*Later: `/docs-verify` is planned to render the checklist, take the answers and write them back. No such command exists yet.*

---

## Then, on a cadence

### 7. `/docs-audit --refresh` — when the product grows a surface

```
/docs-workflows:docs-audit --refresh
```

Run it after a new integration, a new role or a new release, so the denominator grows with the product rather than freezing at day one. It re-derives the sources, the surfaces and every coverage figure against today's code, and it is read-only about your edits: every unit you added stands, your tutorial picks stand, a `priority_reason` you corrected stands with the re-derived one reported beside it rather than written over it, and a candidate you marked `picked: true` becomes a unit — once, with its id recorded so no later run mints a second page for the same journey. A unit whose surface has left the scan is marked `blocked_by: [surface-removed]` and reported rather than deleted, and one whose recorded page is no longer there gets `[page-missing]` the same way; a surface vanishing is as likely to be a repository nobody mounted as a feature genuinely removed, and only you can tell those apart.

### 8. Re-read what `review_by` has aged — by hand

`review_by` in a page's frontmatter is the calendar backstop for the rot no diff can see: a product renamed, a process changed, a policy that moved, none of which touches a line of the code a page's evidence points at. Sort your pages by that date and re-read what has aged past it. A page that is still right takes a new date. **One that is not you rewrite by hand, in place** — `/docs-write` drafts only a unit still `missing`, and nothing on this route rewrites a page for you. The rewrite is the same whatever the unit's status: edit the page where it stands, keeping its path and its `unit:` line; mark each claim you can no longer ground rather than leave it standing; set each `code` and `artifact` evidence entry's `ref` to the commit you read it at, so that step 6 reads against what you read; and give the page a new `review_by`. What becomes of the unit turns on its `status`, because the backlog's lifecycle allows only the moves [its diagram](reference/docs-backlog.md#the-states-a-page-moves-through) draws:

- **`drafted`** — the page has not been verified yet. Rewrite it; the unit stays `drafted`, and step 6's walk covers the rewrite.
- **`published`** — the lifecycle leads back to `drafted` only through `stale`. Mark the unit `stale` in the backlog when you find the page out of date, move it on to `drafted` in the commit that rewrites the page, then walk the page as step 6 says.
- **`verified`** — its one move is to `published`, which you make by hand when the page ships. Publish it as it stands, before you rewrite it — a page carrying a marker may never be marked `published` — then take the `published` route above.

*Later: `/docs-drift` is planned to watch the evidence side of this — diffing a surface's evidence paths between the ref the backlog recorded and today, and re-queueing the units that fan out from it. The calendar side stays a human judgement either way, so this step does not disappear when that command ships.*

---

## What to expect, stated honestly

The four user page types do not cost the same, and one of the four prioritisation signals — *write first what can be grounded now* — leans the ranking the same way:

| Page type | What it takes |
|---|---|
| `reference`, `explanation` | Ground almost entirely from code; `/docs-write` drafts them, a batch included, and little human input remains beyond walking the draft |
| `how-to` | Drafts from code, and **requires** a capture — a sequence of screens is not derivable from routes; a batch leaves it out |
| `tutorial` | Needs a human to choose the journey first (step 3), then a capture; a batch leaves it out |

So the realistic order front-loads reference and explanation — which is also where a reader with no documentation at all gets the most immediate value, and the cheapest way to make a portal stop being empty. It is a lean and not a rule: the signal that outweighs every other is *does this page's absence block the primary journey*, which points squarely at how-tos, and a separate rule biases a **high-churn** surface away from step-by-step toward explanation and reference because those survive churn. A ranked backlog is the resultant of all four signals, not of this table.

**Done is a threshold, not a feeling.** Every unit whose `priority` number is at or below the backlog's `threshold` — priorities 1 and 2, at the seeded value of 2 — has reached `published`, and every claim on the pages behind them is either evidence-backed or visibly marked. **Those two halves are not independent:** a page that still carries a marker ships with it showing, and its unit stays at `drafted` and counts toward nothing, so *visibly marked* describes what a page may look like on its way to done and never what a `published` unit rests on. The threshold is a number you set: the first run seeds it at 2 and says so, `--threshold <n>` sets it, and every later run writes back whatever you left there.

## See also

- [`/docs-init`](commands/docs-init.md) — step 1: what the scaffold writes and what it leaves on the branch.
- [`/docs-serve`](commands/docs-serve.md) — step 2: starting, stopping and checking the dev server.
- [`/docs-audit`](commands/docs-audit.md) — steps 3 and 7: the flags, the phases, the gates and every failure mode.
- [`/docs-write`](commands/docs-write.md) — step 4: the selectors, the consent, the gates, the commit and every failure mode.
- [`/document`](commands/document.md) — the two modes, and what direct mode does with the prose of a page you write yourself.
- [The documentation backlog](reference/docs-backlog.md) — the file this route is worked through: each block, the status lifecycle, what the coverage fraction counts.
- [The coverage model](reference/docs-coverage-model.md) — surfaces, the page types a surface earns, and what decides the order.
- [Evidence and walkthroughs](reference/docs-evidence.md) — what a claim may rest on, what a marked claim looks like, and how to walk a checklist.
- [Documentation visibility](reference/docs-visibility.md) — the two-build public/internal split behind step 4's `visibility` warning.
- [Workflow overview](workflow.md) — all eight commands of this plugin, including the ones off this route.
- [Getting started](getting-started.md) — install, the environment variables, and a first run end to end.

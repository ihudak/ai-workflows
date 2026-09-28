---
name: idea
description: Idea-refinement workflow (PM phase, front of the PRD-creation flow). Takes one source — an inline prompt, a markdown file (whose links are walked in full — wikilinks, inline markdown links and images, reference-style definitions and HTML img src alike — asking the operator before reading past two levels of pages, twelve pages or six images, and whose linked images are transcribed and read as context), a community post, or a saved file (product feedback, or an existing Product Requirements Document the idea extends, parallels, or rewrites) — and, through a bounded one-question-at-a-time grill (--deep for relentless), authors a well-refined idea.md — a lean one-page brief that seeds the future /create-prd. Copies the sources it actually read into the PRD folder (markdown into attachments/, images into design/idea-sources/ with the index that frame set requires) and rewrites idea.md's links onto the copies. Writes into the PRD folder the key names; no code change; `idea.md` lands in `$SPECS_PATH/specifications/PRD-<KEY>-<slug>/` on the first write and is never relocated (D7), and on a completed handoff the run also opens a pull request for it (`workflows-core:phase-handoff` §2) — declining leaves it written in place but not on the default branch; its session artifacts are committed by `commit-artifacts`.
allowed-tools: Read Edit Write Bash Glob Grep Task Skill WebFetch
---

Refine an idea into `idea.md`: $ARGUMENTS

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

`/idea` is the **front door of the PRD-creation flow** (PM phase) — upstream of `/create-prd` and
the existing pipeline. It ingests one source, refines it through a grill, and writes a lean one-page
`idea.md` (per `${CLAUDE_PLUGIN_ROOT}/references/idea-format.md`) that seeds the Product Requirements Document. It is
**not** a PRD: no code change. Output lands in the PRD folder the key names, on the first write and never relocated.
It then **vendors what it read into that same folder** (Phase 4.5) so the record the specs repo keeps is
one whose links resolve for everybody, not only for the operator whose disk the sources came off.

Flags: `--deep` switches the grill from bounded (≤10 questions) to relentless (until convergence).
`--no-docs` turns off documentation grounding (see Phase 1).
`--docs <path>` points documentation grounding at `<path>` instead of `${DOCS_PATH:-/workspace/docs}`
(see Phase 1); the token after it is always its value.
`--ground-code [<repo>[,<repo>…]]` grounds the idea against mounted code (see Phase 2.6) — bare it derives the repo set, with a value it scans exactly those repos. The token after `--ground-code` is its value **only** when it contains no whitespace and every comma-separated part matches a top-level directory basename under `${REPOS_PATH:-/workspace}`; otherwise the flag is bare and the token is idea text.

---

## Phase 0 — Resolve the address + model routing

1. **The address (mandatory).** Parse the first token that is neither a flag nor a flag's value — `--docs` always consumes the token after it, and `--ground-code` only as the Flags paragraph above conditions it, and a value skipped as "non-flag" would be read as the key and validate it with `key-valid`
   (`workflows-core:addressing` §1). Absent or malformed → stop:
   `IDEA_NEEDS_KEY: /idea needs a PRD key (^[A-Z][A-Z0-9_]*(-\d+)+$, e.g. ACME-77) — it names the folder this idea will live in. Re-run '/product-workflows:idea <PRD-KEY> [<prompt>|@<file>]'.`

   **The key is an argument because there is nowhere keyless to write.** `idea.md` lands in its final
   folder on the first write — `PRD-<KEY>-<slug>/` under `$SPECS_PATH/specifications/`. **So `$SPECS_PATH`
   comes first:** if it is unset, stop naming it (`choices: ["Set SPECS_PATH (enter the path)", "Cancel"]`,
   `workflows-core:escalation-rules` *Required path environment variable unset*) — resolution and Phase 4's
   write both need it, and an empty one would aim `idea.md` at `/specifications/` under the filesystem root.
   **Then run the specs-repo preflight below**, its run key set the one key this step validated
   (`workflows-core:specs-repo-git` §3.2), before the folder is resolved or anything in it is read: a
   stale plugin branch it switches away from would otherwise hide the `brd-link.md`, `prd.md` or
   coverage ledger the test below reads, and the run would refuse the folder with the wrong remedy,
   or take a folder as an idea-route one that is not.
   Resolve the folder here with `resolve-address` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`,
   §3): `found` is the folder this run writes into — **where it is an idea-route PRD folder**, below
   — and `ambiguous` is §3's hard stop. **On `absent` nothing is created here**, because Phase 0
   holds no slug to name a folder with: the folder is created by Phase 4's first write, as
   `PRD-<KEY>-<candidate_slug>/` (`workflows-core:addressing` §2), `candidate_slug` being the one
   Phase 2's digest returns. Creating it with `idea.md`, which carries its `kind` and `key`, is also
   what keeps it from ever being keyless (§4). Either way it is never relocated afterwards, and
   `/create-prd <KEY>` finds it there.

   **A `found` folder must be an idea-route PRD folder.** Test the folder, never the kind it asserts
   — a BRD-route slice is `PRD-`-prefixed and asserts `kind: brd` through its `brd-link.md`
   (`workflows-core:addressing` §4) — in this order, stopping on the first that holds. A folder
   carrying a `brd-link.md` naming a `parent:` at its top level is a BRD-route slice, whatever its
   name. Then, where the resolution record reads `legacy: false`, test the prefix: `BRD-` is a BRD
   container, `EPIC-` an Epic folder. Where it reads `legacy: true` there is no prefix to test —
   §5's unprefixed name starts with the key, and a key may itself begin with a kind token, so
   `BRD-12-checkout/` is a legacy folder keyed `BRD-12` and not a BRD container — so place it by
   positive evidence instead, as `workflows-core:addressing` §4.1 does: `coverage-ledger.md` or
   `brd/brd-inventory.md` present is a BRD container, a resolved `kind: epic` an Epic folder. An
   idea brief seeds the PRD authored beside it, and none of these takes one: a BRD container never
   holds a PRD, a slice's PRD is seeded from its BRD with no idea ladder, and an Epic folder sits
   below its PRD:
   `IDEA_NOT_AN_IDEA_FOLDER: <KEY> resolves to <folder path>, <a BRD container | a BRD-route slice | an Epic folder> — /idea writes only into an idea-route PRD folder. <remedy> For a separate idea, give it a key of its own: '/product-workflows:idea <NEW-KEY> [<prompt>|@<file>]'.`
   `<remedy>` names the run that does take that folder's work, by what the folder is — and, in the
   slice and Epic rows below, names a run **only where that run can itself take the folder**, since
   each command it could name refuses some shape of it. **The BRD container row is the exception**:
   it names each slice's `/create-prd` as where a PRD belongs, not as a run promised to start, and
   `/brd-split` with its no-op case said beside it. The slice rows read the gate set
   `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5.2 defines — this slice's own
   `coverage-ledger.md` rows narrowed by its `brd-link.md` `claims:`, read out of the ledger file
   and never off a `ledger:` line (§6.1) — exactly as `/product-workflows:update-prd` Phase 0 step 4
   and `/product-workflows:epics` Phase 0 step 1b read it:

   | The folder is | `<remedy>` |
   |---|---|
   | a BRD-route slice already holding a `prd.md` | `Its PRD is already authored: revise it with '/product-workflows:update-prd <KEY>'.` |
   | a BRD-route slice holding no `prd.md`, whose `coverage-ledger.md` is **absent**, or present and unreadable, while its `brd-link.md` claims rows | Name no command: report `<slice-dir>/coverage-ledger.md` by path, as missing or as unreadable with the read error, and say `/brd-split` wrote it with the slice. This is not an empty gate set — `claims:` names rows and the evidence for judging them is gone — so neither data refusal can be evaluated, and §5.2 forbids resolving it to the empty row's `/brd-split <PARENT-KEY>` (`/product-workflows:create-prd` Phase 0 step 7 names no option on it either) |
   | a BRD-route slice holding no `prd.md`, whose gate set leaves **no** row `unallocated` **and** at least one `covered-here` | `Its PRD is authored from its BRD: run '/product-workflows:create-prd <KEY>'.` |
   | a BRD-route slice holding no `prd.md`, a gate-set row still `unallocated` | Not `/create-prd`, which raises `CREATE_PRD_BRD_UNALLOCATED`: `Its rows are not all allocated yet: run '/product-workflows:brd-split <KEY>' (allocate-only on a slice; its own Phase 0 stops naming '/product-workflows:prd-ground <KEY>' where this slice's grounding findings do not each carry a verifier verdict), then '/product-workflows:create-prd <KEY>' where that walk leaves a claimed row covered-here.` |
   | a BRD-route slice holding no `prd.md`, no gate-set row `covered-here`, the gate set **empty** | Not `/create-prd`, which raises `CREATE_PRD_BRD_NOT_ELIGIBLE`: `This slice claims nothing: keep or remove it with '/product-workflows:brd-split <PARENT-KEY>'.`, `<PARENT-KEY>` read off the same `brd-link.md` the `claims:` list came from — in the form the **parent's** own ledger decides, exactly as `/product-workflows:create-prd` Phase 0 step 7's empty-gate-set row decides it: where that ledger still holds an `unallocated` row, name `'/product-workflows:brd-split <PARENT-KEY> "<how to cut it>"'` instead, since that run walks the row too and stops with `BRD_SPLIT_NEEDS_INSTRUCTION` without an instruction; where it holds none, the bare form above; where it cannot be read, report it by path and name neither form |
   | a BRD-route slice holding no `prd.md`, no gate-set row `covered-here` and none `unallocated`, the gate set **non-empty** | Name no command, and say why: this slice holds no PRD of its own, `/create-prd` would raise `CREATE_PRD_BRD_NOT_ELIGIBLE`, and nothing in this plugin moves a slice's terminal row back to `unallocated` — report what its gate-set rows resolved to |
   | a BRD container | `A BRD holds no PRD of its own: it is authored in one of its PRD- slices.` Then name each slice under it — found by `/product-workflows:brd-split` Phase 0 step 9's positive test (an immediate subdirectory whose `brd-link.md` `parent:` names this BRD), never by a name match — with `'/product-workflows:create-prd <SLICE-KEY>'`, as the statement that a PRD belongs there rather than a promise that the slice is eligible; where it holds none, `'/product-workflows:brd-split <KEY> "<how to cut it>"'` carves one, and say beside it that that run is a no-op on a ledger with no `unallocated` row |
   | an Epic folder whose parent holds a `prd.md` asserting `kind: prd` | `An Epic is refined from the PRD above it: revise that PRD with '/product-workflows:update-prd <PRD-KEY>', re-refine this Epic with '/product-workflows:epics <KEY>', or specify it with '/product-workflows:specify <KEY>'.` — where this folder holds no `epic.md`, `/product-workflows:epics <KEY>` refuses it (`EPICS_NO_PRD`), so that clause names `'/product-workflows:epics <PRD-KEY>'` instead, which drafts the PRD's Epics in folders of its own |
   | an Epic folder whose parent holds no such `prd.md` | Not `/update-prd`, which stops `UPDATE_PRD_NO_PRD` there, nor `/epics <KEY>`, which stops `EPICS_EPIC_NOT_UNDER_PRD` or `EPICS_NO_PRD`: where the parent is a `PRD-` folder, `The PRD folder above it holds no PRD yet: author one there with '/product-workflows:create-prd <PARENT-KEY>'.`, `<PARENT-KEY>` being that folder's own `key`, subject to the slice rows above applied to *that* folder where it carries a `brd-link.md`; anywhere else, name no parent and say so |

   `<PRD-KEY>` is the key of the folder above the Epic folder, read off that folder's carrier
   (`workflows-core:addressing` §4) — never parsed out of either folder's name.

   It is a user halt, so `emit-block` does not fire, and it is taken here, after the specs-repo
   preflight and before anything else is read or written.

   **Validated for shape and checked against no tracker** — resolved only against the specs tree,
   above — exactly as `/brd-intake <BRD-KEY>` already asks. Nothing else looks a key up: there is no
   tracker to look it up in.

   **Accepted cost:** an idea abandoned after Phase 4 wrote its brief leaves a folder in
   `specifications/`; a run that stops before Phase 4 creates none. Reintroducing a staging area to
   avoid that would restore the relocation step this removes.
2. **Resolve model routing.** Invoke the `model-routing` skill (Skill tool,
   `skill: "workflows-core:model-routing"`), then record:
   ```yaml
   model_routing:
     classification: MODERATE          # idea refinement is typically MODERATE
     reason: <one-line>
     current_model: <the model this orchestrator/grill is running under>
     detection_model: <§2.1 Sonnet chain: claude-sonnet-5, fallback claude-sonnet-4-6/4-5>   # idea-reader
     authoring_model: <= current_model>   # the interactive grill + idea.md authoring (session model, not a delegated subagent)
     opus_available: <true if a §2 Opus model resolved, else false>
     notes: <any §2/§2.1 fallback or degradation>
   ```
   The grill + authoring run inline on `current_model` (the §2 Opus chain — interactive judgment, not a
   delegated subagent). `idea-reader` runs on `detection_model`. If no Opus resolves, **degrade to the
   best available and record the degradation** in `notes` and the final report — do NOT hard-block (a PM
   must not be blocked from capturing an idea by a momentary Opus outage). A `--ground-code` run does
   **not** floor the classification at `SIGNIFICANT`: §1.1's multi-source floor is written for
   `/implement`, and §8.3's purpose — the strongest available model on synthesis — is already met
   here, because the grill and authoring run inline on `current_model` while the scanners run on
   `detection_model`.

**Specs-repo preflight** — run in step 1, as soon as `$SPECS_PATH` is known and before the folder is resolved. Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git specs-preflight")` and execute its `specs-preflight` entry point (§3) inline: flush any leftover session artifacts from an earlier run,
retry an artifact commit that failed to push, and settle the branch. Prompt-free and silent when the
specs repo is clean and on its default branch. If a guard fires, emit its §5 notice; if it returns
`specs_git: blocked` (§3.3 G0), carry that flag for the whole run — the terminal `commit-artifacts`
step skips on it.

---

## Phase 1 — Classify the source

Classify what is left of `$ARGUMENTS` once **the Phase 0 key token and every recognised flag with its value** are removed (`--deep`, `--no-docs`, `--docs <path>` with its value, and `--ground-code` with its optional comma-separated repo value), by precedence. Remove them all before classifying: an unstripped flag lands inside the `prompt` branch's raw idea text and is handed to `idea-reader` as if the user had written it; an unstripped key does the same on every prompt run, and turns a correct `<KEY> @<file>` invocation into a path that resolves to nothing — Case B below, on a run with nothing wrong. The token after `--ground-code` is its value **only** when it contains no whitespace and every comma-separated part matches a top-level directory basename under `${REPOS_PATH:-/workspace}`; otherwise the flag is bare and the token is idea text — strip only the flag itself. **A leading `@` marks a file, and the path is the text after it**: that path, never the `@`, is what rule 1 tests and what Phase 2 hands `idea-reader`.

1. An existing `.md` path, written `@<path>` or bare → **markdown** (a community post is just a
   markdown file, typically under `Projects/Products/…` — the reader tags it `community-post`; an
   existing `idea.md` passed back for re-refinement is detected here too).
2. Otherwise → **prompt** (the argument text is the raw idea).

**There is no tracker-export source type, and there is no third classification.** A key used to
resolve an export and be typed from a frontmatter field on it; nothing exports anything now, so an
existing PRD reaches `/idea` the way every other file does — as a path — and `/create-prd --from-prd`
is the route that seeds one PRD from another. **Case A of the confirmation below went with it**: it
asked which of two tracker item types an unrecognised one should be read as, and there are no item
types to disambiguate.

**Confirm the classification — conditionally.** Per `workflows-core:escalation-rules` ("When a choice list fires"), a list is shown only where the answer genuinely varies. One case here does, Case B; the rest do not.

**B — the argument is path-like (contains `/`, ends in `.md`, or starts with `@`) but resolved to no existing file.** Without this gate it falls through precedence rule 2 to **prompt** and the path string itself becomes the raw idea text — a mistyped path silently ingested as prose:
```
choices: ["Re-enter the path (Recommended)", "Read the argument as a prompt — the literal text is the idea", "Cancel"]
```

**Everything else** — a `.md` path that resolves, and plain prose — is unambiguous. State the resolution in one line that invites correction and **proceed without waiting**; the list would have one plausible answer. (A dedicated `--as prompt|markdown|prd` override is future work — this inline confirmation covers a mis-detection.)

**Resolve documentation grounding here, before the run's real work.** Run `resolve-docs-grounding idea` per `Skill(skill: "workflows-core:reference", args: "docs-grounding resolve-docs-grounding")` — its step 3.5 index prompt included — and show the `docs grounding:` line from what it returns, in the form that reference fixes — `ON <root> (retrieval: …)` or `OFF (<reason>)` — verbatim, including any index-build, staleness, or shadowing clause it carries (off switch: --no-docs). It runs here and nowhere later because step 3.5 asks its one-time index question before any of the run's real work, and Phase 1.5's walk and Phase 2's readers are that work. This is the run's one resolution (`workflows-core:docs-grounding`, *Invariants*): Phase 2.5 dispatches on the state it returns and resolves nothing again.

---

## Phase 1.5 — Walk the source's links

**Only for a `markdown` source** — a prompt carries no links, and this phase is skipped silently for
one.

Run the walk `${CLAUDE_PLUGIN_ROOT}/references/linked-sources.md` §4 defines, from the source file. It
is read-only — it copies nothing, reads no image and dispatches nothing — and its record is what
Phase 2 hands the readers, so nothing after this phase finds a link on its own.

**Ask only where an older bound would have cut.** This command once read pages at most two levels of
links deep, twelve markdown files counting the source, and six images, and reported the rest unread.
Where the walk stayed inside all three, take everything it reached, print the counts line, and ask
nothing. The counts line gives: how many files the walk reached (the source counted first), the
markdown pages among them by depth, the images, and what was unresolved (a reason
`linked-sources.md` §6 names) or `other`. **Every clause is printed on every run, a count of `0`
included** — an omitted clause is indistinguishable from a forgotten one, the same reason the Final
report names what was left unread even when nothing was. **A clause is one of the named parts that
sentence lists** — markdown by depth, images, unresolved, *other*, beside the headline total, which
counts the source and so is never zero — and the by-depth tally is one clause rather than a row of
them: inside it there is one entry per depth at
which the walk reached a markdown page, and those depths run contiguously from 1 — only a markdown
file is opened (`linked-sources.md` §4), so no page sits at a depth without one above it — which is
why the tally never has an interior zero to print. **A depth the walk reached only with an image is
not a page depth and gets no entry**: an image at depth 4 says a page at depth 3 linked it, and
`depth 4: 0` would report a page count for a depth no page can be at. Where the walk reached no
markdown page at all beyond the source, the clause itself is the zero and prints as `markdown by
depth — none`. **The headline total is the walk's visited
set** (`linked-sources.md` §4) — the source, plus every file a link resolved to — so an *other* file
counts toward it, and an unresolved link, which resolved to no file, does not. **The by-depth tally
is of that set less the source**, which has no depth to be counted at, so it always runs one short
of the headline's markdown; the `source + <n>` half of the headline is where the source is. For
example:

```
7 files reached (source + 6): markdown by depth — depth 1: 3, depth 2: 1; images: 1; unresolved: 1; other: 1.
```

Where it reached past any of them, **print the counts line all the same** — the Final report reports
the walk in both branches, and this is where it comes from — then find the set that is past a bound:
the union of every markdown file deeper than 2 (the depth bound is on pages, never on images), the
markdown files after the twelfth in the walk's order (the source counted first — so this ordering
runs one ahead of the counts line's by-depth tally, which leaves the source out, and the file that
tally shows twelfth is the thirteenth here), and the images
after the sixth in the walk's order. Put the question with its text fixed — a line naming the bounds
the walk crossed, of the three, then one line per file in that set, each file once, in the walk's
order, with every bound it is past, joined as the template shows where a file is past two; then the
line saying what *Read all* takes, and, where the walk reached nothing below depth 1, the line
saying the second option takes that same set — and then the array:

**Three things about how the question's lines print are fixed here, because a run composes them from
the template below and nothing downstream corrects them.** First, **a file is past two bounds at
most** — both page bounds apply only to a markdown file and the image bound only to an image, and
`linked-sources.md` §4 gives every resolved file exactly one kind — so the per-file join never has a
third name to place. Second, the
crossed-bounds line and each file line **join with `", "`, so no bound's name carries a comma of its
own**: three names joined that way print as three fragments, and a name holding a comma prints as a
fourth, reading like a fourth bound with nothing below it to say otherwise — which is why the page
bound is named *twelve pages counting the source* rather than with the source counted off after a
comma. Third, **the file lines' path form**, because they are the only operator-facing place a path
appears and an absolute one runs ten times the length of a relative one: a file the walk record
marks `inside: true` (`linked-sources.md` §5) prints relative to the source file's own directory,
and a file it marks `inside: false` prints as the resolved absolute path — where the reader most
needs to see where it came from, and would otherwise be counting `../` segments.

```text
The walk reached past <the bounds it crossed, of: two levels of pages · twelve pages counting the source · six images — joined with ", " in that order>:
<the file's path — relative to the source file's own directory where the walk record marks it inside that directory, and the resolved absolute path where it does not> — <every bound it is past, of: deeper than two levels · after the twelfth page · after the sixth image — joined with ", " in that order>
…
Reading all takes the source and every one of the <n> files the walk reached beside it, not only the files listed here.
<where the walk reached nothing below depth 1, one further line: "Every one of them is linked by the source itself, so the second option below takes that same set.">
```

```
choices: ["Read all <n> (Recommended)", "Only what the source links directly", "Stop"]
```

`<n>` is the counts line's headline total less the source — every file the walk reached but the
source, *other* files included, the `+ 6` of the example above — and that is exactly the set
*Read all* takes beside the source, as the branch above takes it. **It is not the count of the
list just printed**, which names only the files past a bound and is usually a good deal shorter —
which is why the fixed text above closes with the line saying what *Read all* takes, printed rather
than left to be inferred: an operator otherwise reads a number against a five-line list and answers
about twenty-two. **That line names `<n>` itself, and names the source apart from it**, so the
printed sentence and the option label under it describe one set rather than two: on the fixture,
`23 files reached (source + 22)`, then *Reading all takes the source and every one of the 22 files
the walk reached beside it*, then `Read all 22` — all three the same 23 files. A line asserting a
set of 23 directly above a label reading 22 left the reconciliation in a command body the operator
cannot see, and gave a run they meant to take whole a reason to answer *Stop*. An *other* file it
takes is still never opened: `idea-reader` enumerates it into `links_other`, taken or not (Phase 2). *Only what the
source links directly* takes depth 1 — every file the source links itself, of any kind — and leaves
every deeper file `excluded` (`linked-sources.md` §6, §7), which Phase 4.5 reports rather than copies.
**Where the walk reached nothing below depth 1 that option reduces nothing, and the extra printed
line is what says so.** Two of the three bounds are crossable with every file at depth 1 — twelve
pages counting the source, and six images — so a source linking ten images directly, or a hub note
linking twenty pages, fires this question over a walk record whose every entry is depth 1, where
*Only what the source links directly* takes exactly what *Read all* takes. `escalation-rules`'
*When a choice list fires* makes a list written for a question whose answer is already determined a
defect; the array is fixed text and is presented verbatim, so the printed line above it is where
the operator is told — before they answer, rather than after the same set has been read, copied and
left dirty either way. *Stop* ends the run with
nothing written — an operator halt, so `emit-block` does not fire.

Record the outcome on the walk record itself, as `linked-sources.md` §7 has a caller do, so every
entry carries `taken`: `taken: true` on every entry naming a file this phase took, and `taken: false`
with `reason: excluded` on every entry naming one it left out. An entry carrying one of the walk's
own reasons names no file to take and carries `taken: false`, its reason unchanged. An entry linking
back to the source file carries `taken: true` — the source is read — and `idea-reader` skips it,
reading the source as the source (`agents/idea-reader.md`, *What the caller hands over*).

---

## Phase 2 — Ingest the source (idea-reader)

**First the figures.** Where Phase 1.5 took any image, dispatch `figure-reader` over the taken images
before the reader, at most 10 per dispatch and at most 4 dispatches in a single response, in further
waves until none remain:

→ Agent (subagent_type: "product-workflows:figure-reader", model: opus — frontmatter-pinned):
  > "figures: [absolute path of each taken image in this batch, in the walk's order]"

An `INPUT_MISSING` return is this run's defect — it sent an empty batch — and is fixed and
re-dispatched, never recorded as an unread image. **Collect each dispatch's own `notes` for the
Final report** — an image too low in resolution for its small text, say — because a transcription
the operator is not told was partial reads as a complete one.

**Then the reader**, handed everything it is to read:

→ Agent (subagent_type: "product-workflows:idea-reader", model: `<detection_model — §2.1 Sonnet chain>`):
  > "Ingest this idea source and return the structured digest:
  >
  > argument:        [what Phase 1 classified — the prompt text, or the file's path with no leading `@`]
  > provenance_hint: [prompt | markdown — the only two Phase 1 computes; the reader upgrades to community-post or prd off the file itself]
  > walk:            [Phase 1.5's walk record, every entry with its `taken` state — omit for a prompt]
  > figures:         [every entry `figure-reader` returned, in the walk's order — omit where no image was taken]"

Wait for the digest. If `status: NOT_FOUND` (a missing or unreadable file), surface:
```
choices: ["Re-enter the source", "Cancel"]
```
This is an environment/user halt — do NOT `emit-block`. On `OK`, carry forward `raw_context`,
`stated_scope` (the settled scope Phase 3 grills against), `signals`, `images`, `candidate_title`, `candidate_slug`, `source_refs`, `provenance`, `tracked` (a
`prd` source only), all three wikilink lists — `wikilinks_followed`, `wikilinks_not_followed`,
`wikilinks_broken` — and `links_other`. `source_refs`/`provenance` feed the `sources:` frontmatter
entry in Phase 4 — `source_refs` holds exactly one entry for a markdown source and none for a
prompt — and `tracked` seeds `## Prior art`. **Every one of those lists is also Phase 4.5's
input**: `wikilinks_followed` and the read `images` are what gets copied beside the source file
`source_refs` names, and the other three are what gets reported instead. **Carry each entry whole,
`target` included.** Every link array names the target **as written** beside the path it resolved to;
that pairing, with the `source_refs[].ref` of the source — the one copied file no link array holds —
is the only map Phase 4.5 has from a link in `idea.md` back to the copy it belongs to, and dropping it
would force that phase to resolve links itself — which it is forbidden to do.

**What the digest now carries, and what it is worth.** The reader reads every markdown file Phase
1.5's walk took, however deep and however many, and every image's transcription, which
`figure-reader` produced without seeing the source; the digest carries a `description` of what each
frame shows — the transcription's `depicts` sentence — rather than a bare path. Both are **context**:
they inform the grill and the prose Phase 4 writes. Neither is grounded evidence — an image here is
never a `[DG#n]` finding and gets no verifier pass here (`workflows-core:grounding-format` §6
governs *that*; this run never reaches it — `/prd-ground` is what later grounds this same vendored
frame set against the PRD's own rows, on its own pass, not this one). Phase 4.5 does write the
index its vendored frame set requires — §6.1 makes that mandatory for any set — but an index makes
a set **readable**, which is not the same as reconciling it into evidence. Treat a described frame
the way you treat a sentence in the source file: something the operator handed over, to be put back
to them as a question, never a fact about what ships.

**Everything not read is surfaced, never swallowed.** An `images` entry with `read: false` names its
`reason` (`excluded`, `missing`, `unreadable`, `not_an_image`); `wikilinks_not_followed` names each page
the operator's Phase 1.5 answer left out; `wikilinks_broken` names each target the walk could not
resolve in a page that was read (the source, or a page the walk took), an `ambiguous` wikilink with
every candidate it matched; and `links_other` names each link that resolved to a file nothing reads
— a PDF, an archive, any other binary — enumerated and never opened. Carry all of them to the Final
report: a read the operator is not told was partial is indistinguishable from a source that said
less, and a link nothing copied and nothing reported is indistinguishable from a link that was
never there.

**Name the idea's capability themes last.** From the digest's `raw_context`, name 1–5 capability
themes — short noun phrases for what the idea asks the product to do, such as *invoice line
disputes* or *per-project dark mode*. This orchestrator names them: `idea-reader` returns none, and
its contract does not change for them. Never take them from `signals`, which carry demand evidence
rather than capabilities and are empty for most sources. Phase 2.5 hands these themes to the docs
grounder, and Phase 2.6 proposes its repos from them and hands them to its scanners.

---

## Phase 2.5 — Grounding: documentation (optional)

This phase dispatches one grounding agent, the docs grounder. Code grounding is Phase 2.6's, run after this phase and never in the same response; docs grounding being OFF never suppresses it, nor the reverse.

**Docs.** Phase 1 already resolved documentation grounding and showed its line; this phase consumes that result and resolves nothing again. Where Phase 1 resolved `docs_grounding: ON`, `dispatch-docs-grounder` (`workflows-core:docs-grounding`) with `feature_summary` = the `idea-reader` digest's problem/outcome, `themes` = the capability themes Phase 2 named; pass `key` = the run's own key, which enables the git-grep backstop. Where it resolved OFF, dispatch nothing and move on.

Carry the digest into Phase 3 with **grill-rank** consumption — its challenges compete for the ≤10 question slots, they do not add slots. (One digest, not two: prior-art discovery was removed with its finder, so `docs_challenges` is the only challenge set an agent produces here. There is no `area_proposal` to carry either — nothing proposes a write path now that the key names the folder.)

---

## Phase 2.6 — Code grounding (optional)

Runs only when `--ground-code` was given; otherwise take the OFF branch at the end of this phase. Kept separate from Phase 2.5 because the repo gate needs a user answer (which cannot happen inside a parallel dispatch) and because the scan is two-round and therefore sequential.

**1. Resolve the repo set.** The token after `--ground-code` is its value **only** when it contains no whitespace and every comma-separated part matches a top-level directory basename under `${REPOS_PATH:-/workspace}`; otherwise the flag is bare and the token is idea text. Validate each resolved path is a directory; a repo that is not mounted is handled by the `Repo missing (after resolution)` rule in `workflows-core:escalation-rules` — never invented, never silently dropped. A repo the user drops is carried to Phase 5 by name, with the themes it would have grounded left unverified. With `--ground-code <repo>[,<repo>…]`, use exactly those repos and skip the derivation below. Bare, derive them:

- **Cheap discovery.** List the top-level directories under each `${REPOS_PATH:-/workspace}` entry (may be colon-separated) with `ls`. Optionally attach each directory's one-line identity — `timeout 5 git -C <dir> remote get-url origin 2>/dev/null` (slug) or its README's first heading. Do **not** deep-scan to guess relevance.
- **Propose** a candidate set from the capability themes Phase 2 named.
- **Gate** — this list's answer varies every run, so it fires unconditionally:
  ```
  choices: ["Ground the proposed set (Recommended)", "Ground a different set (you'll be prompted)", "Ground nothing — continue without a code scan", "Cancel"]
  ```
- **Empty proposal — do not show that list.** When no theme matches any mounted repo its first option names a set that does not exist. Escalate instead per the `No repos derivable — /epics` rule in `Skill(skill: "workflows-core:reference", args: "escalation-rules")`. Every option in a shown list must name something that exists.
- **"Ground nothing — continue without a code scan"** ends this phase for the run: no scanner is dispatched, Phase 4 writes no `## Feasibility grounding` section, and the Final report shows `code grounding: declined at the repo gate` — distinct from `code grounding: off`, which means the flag was never given at all.

**2. Round 1 — broad.** Spawn `code-scanner` on the confirmed set in **batches of up to 4 concurrent agents per Agent message**, on `detection_model` per `workflows-core:model-routing/classification` §8.3. For each repo in the batch:

→ Agent (subagent_type: "workflows-core:code-scanner", model: `<detection_model — §2.1 Sonnet chain>`):
  > "Scan this repo for the brief:
  >
  > repo_path:        <resolved absolute path>
  > capability_themes: <the capability themes Phase 2 named>
  > context:          <3–5 sentences: the idea's problem + desired outcome, and what a finding would change>
  > search_hints:     <symbols/paths/keywords derived from the idea, if any>
  > refresh:          { switch_to_default_branch: false, pull: false }"

Handle every returned status through the list `workflows-core:escalation-rules` already carries for it — `REPO_MISSING` → *Repo missing (after resolution)*. `prep.read_only: true` is **not** a failure: the scan ran at `prep.scanned_ref`; escalate per *Read-only mount — ref stale or diverged* **only** when `prep.ref_committed_at` is more than 14 days old or `prep.head_divergence.ahead > 0`, and cite evidence at `prep.scanned_ref` either way. With `switch_to_default_branch` and `pull` both false, every repo is scanned read-only as it stands, at `prep.scanned_ref`, without switching branches or pulling — `code-scanner`'s dirty-tree status is gated on `pull: true`, a condition never met here, so this scan never produces it.

**3. Round 2 — narrow.** Apply §8.5 of the model-routing reference: for each theme round 1 left **inconclusive** (`classification` `partial` / `absent` / `error`, or **two or more** scanners' per-theme `capability_map[].gap_summary` texts point at each other's repo in a cycle, or at a component/subsystem that no scanned repo covers), and for which round 1 produced at least one evidence anchor, dispatch `code-scanner` again with `capability_themes` holding exactly **one** question and `search_hints.paths` / `.symbols` / `.keywords` seeded from that round's verified `evidence[].path` and `.symbols`; where an evidence entry carries `lines`, name the anchor as `<path>:<line>` in the round-2 `context` prose, since `search_hints` has no line-number field. Round 2 reuses round 1's `refresh:` block verbatim — `switch_to_default_branch: false`, `pull: false` — so the read-only posture and that round's claim that `code-scanner`'s dirty-tree status is gated on `pull: true` and so is never produced here hold for both rounds. Cap **4 dispatches, one round only** — there is no round 3, and a theme still inconclusive is carried to Phase 4 as a `[NEEDS CLARIFICATION]`, never guessed at. A theme confirmed `absent` — by round 2, or by round 1 when no anchor existed to seed a round 2 — is a **resolved** finding: it belongs in Section 7's *What's missing*, not in Open questions. `[NEEDS CLARIFICATION]` is for a theme the scan could not settle — mutual deferral, or `error`.

**OFF branch** (no `--ground-code`). Run one detection and print at most one line. Tokenise the raw argument and the digest's `raw_context`; match tokens case-insensitively against the basenames of the **git repositories** (a `.git` entry present) directly under each `${REPOS_PATH:-/workspace}` entry, excluding `$DOCS_PATH` and `$SPECS_PATH`. Exact token match only — no substring, no stemming. On ≥1 match print:

```
This idea names <repo>; re-run with --ground-code to verify it against the code.
```

and **proceed without waiting** — an inline confirmation per `workflows-core:escalation-rules` ("When a choice list fires"), not a gate. No match ⇒ silent. There is no auto-trigger: grounding is a fan-out across every confirmed repo plus a second seeded round, and starts only on the user's explicit flag.

---

## Phase 3 — Refine via grill

**Interview technique (grilling — embedded; no runtime dependency).** Follow the shared technique in `Skill(skill: "workflows-core:reference", args: "grilling-technique")` — one question at a time, recommend each answer, fact-vs-decision split (look up facts from the `idea-reader` digest, put only decisions to the user), walk the design tree in dependency order. **Depth: bounded by default (below); `--deep` = relentless.**

Scan for gaps against an idea-stage **ambiguity taxonomy**: *problem clarity, target users, desired
outcome/value, scope boundaries, evidence/demand sufficiency, success signal, terminology.* Rank gaps by **Impact × Uncertainty**, ranking every `docs_challenges` entry from Phase 2.5 into that same list. Challenges **compete** for the slots below; they never add slots. **Code findings are facts, not questions.** A Phase 2.6 finding answers a gap rather than raising one — look it up, cite it, and do not spend a question on it. The one exception is the finding that **contradicts the idea's premise** (the capability already exists, or the gap is far smaller than the idea assumes): that becomes a challenge ranked into the same Impact × Uncertainty list, competing for a slot exactly like a `docs_challenges` entry and never adding one. At most **2** such challenges.

**Source-stated scope is settled before the first question.** Seed the design tree with every `firm` entry of the Phase 2 `stated_scope` as an already-made decision (`workflows-core:grilling-technique`, "A decision the source already states is settled"). Those boundaries are not gaps and take no slot. A `tentative` entry is a gap: confirm it with its quote, recommending the source's position. Before putting any question, check its recommended answer **and its rationale** against `stated_scope`. A recommendation that argues from breadth, effort, or overlap the source has excluded (*"this spans web, mobile and the API"* when the source excludes mobile) must be rewritten before it is shown. To argue that a stated boundary is wrong, raise that as an explicit challenge quoting it; it competes for a slot like any other challenge. Where a grounding digest (docs, code) describes a wider surface than the source scopes, that is context for the boundary, not a reason to widen it.

**A described image is material for the grill, not an answer in it.** Where a Phase 2 `images` entry carries a `description`, use it the way you use the source's own prose — to sharpen a question (*"the mockup shows the toggle per project; is the setting per project or per account?"*) and to avoid asking about something the operator has already shown you. It never closes a gap on its own and it never adds a question slot, because a frame is what somebody drew, not what anything does. **Never write a described frame into `idea.md` as fact** unless the grill confirms it or the source's prose already says it. An image left `read: false` — not transcribed: excluded, or the transcription failed — contributes nothing at all: never reason from its filename or its path.

- **Default (bounded):** ask **≤10** questions across the ranked gaps, then stop. Remaining high-impact
  gaps become `- [NEEDS CLARIFICATION: <question>]` in the `idea.md` **Open questions & assumptions**
  section, **capped at 3**; reasonable defaults are recorded as `- **Assumption:** <text>`.
- **`--deep`:** relentless — keep walking the design tree one question at a time until you and the user
  reach shared understanding; the cap does not apply.

---

## Phase 4 — Write idea.md

Author `idea.md` per `${CLAUDE_PLUGIN_ROOT}/references/idea-format.md` into the folder Phase 0
resolved — or, where it returned `absent`, the one this write creates (**Path**, below) — applying the no-hard-wrap prose convention in `Skill(skill: "workflows-core:reference", args: "prose-formatting")`:

- **Path.** `idea.md` in the folder Phase 0 resolved, or created now: where Phase 0 returned
  `absent`, this write creates `$SPECS_PATH/specifications/PRD-<KEY>-<candidate_slug>/` with
  `idea.md` as its first file (Phase 0 step 1). There is no container derivation, no write-path
  gate and no `prd_disposition`: the operator named the folder when they named the key, which is
  what removes the question.
- **`## Prior art`:** write the section per `${CLAUDE_PLUGIN_ROOT}/references/idea-format.md` when the
  source is a `prd` the user supplied — its Phase 2 `tracked` block (key, status, summary), which
  appears there **and** in `sources:`. Omit the section entirely otherwise. **Nothing discovers prior
  art any more**; what the user hands over is the only prior art there is.
- **`## Feasibility grounding`:** write the section per
  `${CLAUDE_PLUGIN_ROOT}/references/idea-format.md` when Phase 2.6 ran **and** returned at least one
  finding; omit it entirely otherwise. Head it with each grounded repo as `<repo>@<scanned_ref>`; give
  every bullet a repo-qualified `<repo>/<path>:<line>` citation (the first entry of that evidence's
  `lines`, or `<repo>/<path>` when it has none); write a **Reframing** line only when a finding
  contradicted the idea's premise. A theme still inconclusive after round 2 becomes a
  `[NEEDS CLARIFICATION]` in **Open questions & assumptions**, never a hedged bullet.
- **Existing file:** if `idea.md` already exists at that path, offer:
  ```
  choices: ["Refine the existing idea.md (Recommended)", "Cancel"]
  ```
  On *refine*, re-open it, resolve its open `[NEEDS CLARIFICATION]` items, and append the new source
  to `sources` — `{provenance, ref}` from Phase 2's `provenance` and its one `source_refs` entry, or
  `{provenance: prompt}` with no `ref` for a prompt run, whose `source_refs` is empty
  (`${CLAUDE_PLUGIN_ROOT}/references/idea-format.md`, *Frontmatter*).

  **There is no "write a second one beside it" option, and the reason is structural.** The key was
  fixed in Phase 0, so a second brief under a different slug is a second folder asserting the *same*
  key — `workflows-core:addressing` §3's hard `ambiguous` stop (`resolve-key` step 5), which makes the
  key unaddressable by every command that resolves one, `/create-prd <KEY>` — the command this run is
  about to recommend — included. A genuinely separate idea is a separate key: say so, and name
  `/product-workflows:idea <ANOTHER-KEY> <the same source>` as the way to write one.
- **`kind` and `key`:** write `kind: prd` and `key: <the key this run was invoked with>` into the
  frontmatter (`${CLAUDE_PLUGIN_ROOT}/references/idea-format.md`). Where Phase 0 returned `absent`,
  this command creates the folder, with this file, so until `/create-prd` writes `prd.md` this file
  is the only one in it whose frontmatter holds `key:` beside a `kind:` naming a folder kind — the
  carrier `workflows-core:addressing` §4 resolves the folder's identity from — and §4's own
  invariant is that a folder is never keyless, not even between its creation and its first
  document. Where Phase 0 returned `found`, the folder already resolved to this key, and the pair
  written here is the one it already asserts.
- **`## Rough scope` carries the source's boundaries.** Every `stated_scope` entry is written into **In** or **Out** as the source put it, unless the user reversed it during the grill, in which case write what they decided. Before writing the section, name each source-stated boundary to the user so a lost one is caught before it is written. A boundary is never dropped silently because the grill did not touch it.
- **`status`:** set frontmatter `status: refined` IFF zero `[NEEDS CLARIFICATION]` markers remain;
  otherwise `status: draft`.

---

## Phase 4.5 — Vendor the sources into the PRD folder

Runs after Phase 4 and before Phase 5, because the handoff stages what this phase writes.

**Why this phase exists.** `$SPECS_PATH` is the system of record, and Phase 4 has just written
`idea.md` there with links still pointing at wherever the operator's source happened to live. Left
alone, the record holds a provenance document nobody but that operator can follow. Cite
`${CLAUDE_PLUGIN_ROOT}/references/idea-format.md` and execute its **Vendored sources** rules inline —
that file owns the two destinations, the copy set, the collision rule and the rewriting rule, and
cites `workflows-core:grounding-format` §6.2 for the index format and its
reconciliation contract. This phase restates none of them.

**It changes nothing the brief says.** `idea-reader` distilled every source into `raw_context` in
Phase 2 and the grill consumed it in Phase 3, so this phase never revisits what `idea.md` claims. It
repairs where `idea.md` points.

1. **Build the copy set from the Phase 2 digest, and from nothing else.** The source file (unless
   `provenance: prompt`), every `wikilinks_followed[]` entry, and every `images[]` entry with
   `read: true`. This phase opens no path of its own and reads no file Phase 2 did not already
   read, so the set Phase 1.5's walk took bounds it without a second bound being written anywhere.
   Drop any entry that already sits inside the PRD folder Phase 4 wrote `idea.md` into: it is
   vendored already, and its link stays as written.
2. **Copy each entry to its destination** — text and markdown to `<PRD-folder>/attachments/`, images
   to `<PRD-folder>/design/idea-sources/` — under the name
   `${CLAUDE_PLUGIN_ROOT}/references/idea-format.md` *The collision rule* gives it: all four of its
   rules, executed from there and restated nowhere here, since a partial copy of them is a second
   rule that disagrees with the first.
3. **Rebuild `design/idea-sources/index.md` per `workflows-core:grounding-format`
   §6.2** — the one index format and reconciliation contract every writer of a frame-set index follows,
   executed inline and restated nowhere. That section owns the filename, the frontmatter, the table
   shape, the `Linked from` semantics, and every one of its six reconciliation steps, including what
   each of them reports — run them from there, never from a copy of them here. **What this run
   accounts for** is §6.2's writer table: the images step 2 copied, described from their digest
   `description`, transcribed verbatim and never invented. An image the collision rule *reused* (its
   rule 1) is not a new frame and gets no second row; the row already describing it stands. **Every
   placeholder this run writes is §6.2 step 4's first literal, `_no description on record_`, and that
   is a consequence of the writer table rather than a
   choice made here.** Step 4's second literal records a describer that looked at a file and could not
   read it; this run copies only images `figure-reader` actually read, so a frame it accounts for
   nowhere is one it either never looked at or already had a byte-identical copy of — the collision
   rule's rule 1 reuses such a file rather than copying it (`idea-format.md`), and the writer table
   gives this run only what it *copied* — and a later `/workflows-core:frames` run can still
   describe either. **The index is not optional**:
   `workflows-core:grounding-format` §6.1 makes its absence a refusal of design grounding, recovered
   only by writing one (`/workflows-core:frames` is the supported way; a hand-written index serves
   too), so images written without one would be a frame set `design-grounder` refuses on sight until
   someone does. **Writing it is still not
   grounding it** — nothing here dispatches `design-grounder`, produces a `[DG#n]`, or reaches a
   verifier, and this phase keeps that true. What changes is that the set this phase writes is read
   later: `/prd-ground` grounds it against this same PRD's `[AC#n]`/`[FR#n]`/`[US#n]` rows, whenever an
   operator runs it (§6.1 says so). A set left with rows the run could not describe is repaired by
   `/workflows-core:frames <KEY>`, which reads the frames themselves and fills exactly those rows.
4. **Rewrite `idea.md`'s links onto the copies** — `[[wikilinks]]`, `![[embeds]]`, `[text](path)` and
   `![alt](path)`, absolute and relative alike — replacing the target, preserving the display text, and
   **writing every rewritten link as standard markdown**. **Those four are the forms `idea.md` itself
   carries**, and that is why the list here is narrower than
   `${CLAUDE_PLUGIN_ROOT}/references/linked-sources.md` §1's, which also recognises a reference-style
   definition and an HTML `<img src>`: that set is about the *source*, which this phase never
   re-reads, while this file was authored by Phase 4 against
   `${CLAUDE_PLUGIN_ROOT}/references/idea-format.md` and every link this phase writes into it is
   standard markdown. `$SPECS_PATH` is a git repo read on a forge and
   in editors, not an Obsidian vault: nothing there resolves `[[name]]`, so a link repointed into the repo
   but left in wikilink syntax still resolves nowhere the record is actually read. `[[rollout]]` becomes
   `[rollout](attachments/rollout.md)`, `[[rollout|the plan]]` becomes `[the plan](attachments/rollout.md)`,
   `![[toggle-01.png]]` becomes `![toggle-01](design/idea-sources/toggle-01.png)` (alt from the **original**
   basename, never the collision-rule name), and `![[note]]` on a markdown file becomes the plain link
   `[note](attachments/note.md)` — a transclusion has no standard equivalent and renders nowhere here
   either way, so a link that resolves beats an embed that does not. **Rewrite only a link whose target
   this phase actually copied.** Every other link is left byte-for-byte as it stands, **syntax included**:
   a surviving `[[rollout]]` is the signal that nothing was copied for it, and the author may want to
   vendor that file by hand. The copies themselves are never edited.
   **Rewrite from the digest's own written-form → copy map, and re-resolve nothing.** Every link array
   carries the target **as written** beside the path it resolved to — `images[].target` and
   `wikilinks_followed[].target`, each beside its own `from` — and step 2 knows the name each copy took;
   pair them and match `idea.md`'s links against **both** key forms that file defines — the target as
   written, and the entry's resolved absolute path — because Section 5 lets a bullet cite either, splitting
   a trailing `#anchor` off before matching and re-appending it after. **The source file is a key too**
   — it sits in no link array, so that file's map (*Link rewriting*) keys it by its `source_refs[].ref`
   exactly as the digest records it, beside its `attachments/` copy, and a link to the source is
   repointed like any other vendored file. This phase opens no path of its own, so a form that matches
   no key is a link nothing copied and is left alone. Where two entries share one written target but
   resolved to **different** files, that target is ambiguous — `idea.md` records nothing per
   occurrence to separate them — so **leave every occurrence as written and report it** rather than
   repoint one at the wrong copy. Targets that merely *look* alike but differ as strings
   (`settings/toggle-01.png` vs `onboarding/toggle-01.png`) are two keys and each is rewritten to its own
   copy.
5. **Record `vendored:`** beside the `ref:` of the `sources:` entry this run added, where step 2
   copied its source file. `ref` is not rewritten — it answers how the idea arrived, and that is still
   true of a path nobody else can resolve. **A linked page or image gets no `sources:` entry and no
   `vendored:`**: it is not an ingested source (`idea-format.md`, *Frontmatter*), and its copy is
   recorded by the rewritten link in `idea.md` that points at it and, for an image, by its index row.
6. **Create nothing empty — but creating a directory and writing its index are not the same act.**
   `attachments/` is created only where a file lands in it and `design/idea-sources/` only where an
   image does; the index, per §6.2 step 6, is written whenever that frame set holds at least one frame,
   **including on a run that copied no image into a set an earlier run populated** — which is how a row
   whose image is gone gets dropped. A bare-prompt run over a folder holding no frame set creates
   neither directory and writes no index; over a folder an earlier run populated it creates neither
   directory either and writes that set's index all the same, by the rule just given — a
   bare-prompt run being exactly a run that copied no image, and `/idea <KEY> "<more text>"` over an
   existing brief being a state Phase 4 supports. Either way it rewrites no link and hands Phase 5
   the deliverable set it would have handed it before this phase existed, that one `index.md`
   apart.
7. **Nothing here is fatal.** A copy that fails — permissions, a full disk, an unreadable source that
   was readable in Phase 2 — leaves that file unvendored, leaves its link exactly as written, and is
   reported beside the four sets below. A failed copy never blocks the handoff and never fails the run.
8. **Report what was not copied, in the Final report** — `wikilinks_not_followed[]` with its
   `excluded` reason, `wikilinks_broken[]`, every `images[]` entry with `read: false` and its reason, and
   every `links_other[]` entry with its extension. None of the four is copied, none of them has its
   link rewritten, and none of them is fatal. **Report three more things the steps above produce**: every
   ambiguous target step 4 declined to rewrite (with each source path and each copy), every frame step 3
   indexed as `_no description on record_`, and every index row step 3 dropped because its image is gone.

Hold the vendoring outcome — what landed in each destination, what was skipped and why, and any name
substituted or refreshed by the collision rule — for the Final report, and carry into Phase 5's
`deliverable_paths` the literal list of paths this phase **wrote or reused**. Reused belongs in it:
a byte-identical copy was not written by this run, but `idea.md` links it and an earlier run may have
left it on no ref, so omitting it is a link to a file that never lands.

**The bookkeeping steps do not stage any of this.** `workflows-core:specs-repo-git`
§2.1 classifies `attachments/**` and `design/**` as OTHER, so `commit-artifacts` never touches them —
they are deliverables, and they reach the default branch only through Phase 5's handoff.

**What a run without a handoff therefore leaves behind, stated at its real size.** Not one file:
`idea.md` **and every path this phase wrote** — one copy in `attachments/` for the source and for
every markdown file Phase 1.5 took, one in `design/idea-sources/` for every image `figure-reader`
read, and that set's `index.md` — a number Phase 1.5 fixes and no cap bounds, so a source that links
a hub note leaves dozens of dirty OTHER paths. Three routes reach that state, and only one of them
is a decline: Phase 5's `status: refined` branch offers the handoff and the operator may decline it;
its `status: draft` branch **never offers one at all** — so a draft run leaves the whole set
dirty by construction rather than by a choice; and a `status: refined` run whose handoff was
**taken** and whose `workflows-core:phase-handoff` §2.1 gate then refused it committed nothing
either, which is the *Gate failed* line §4.1 emits and which Phase 5 already names beside a decline.
That third one is reachable rather than theoretical: §2.1 fails on path, repo or permission grounds
**or** on `specs_git: blocked`, and Phase 0 carries that flag for the whole run whenever its own
preflight returns `workflows-core:specs-repo-git` §3.3's G0. The other non-landing §4.1 rows are not
further routes — *No remote* and *Push failed* both committed on a branch first (§2.4 runs before
§2.5), and *Nothing to commit* changed nothing.

On the next run of any command sharing that repo, §3.3's **G1** matches. Its consequences are three, not
one: the preflight **ends** there, at advisory severity, listing the paths — no commit, no branch switch,
no push — and because §3.4's leftover flush and §3.5's branch disposition run only when stage 1 matched
nothing, **both are suppressed for the rest of that session**. G1 does **not** set `specs_git: blocked`,
so the terminal `commit-artifacts` still runs and nothing is lost or halted; the suppression repeats on
every later run until those paths are committed or the handoff is taken.

---

## Phase 5 — Handoff: adaptive next-phase offer

Report where `idea.md` was written and its `status`, and what Phase 4.5 vendored beside it, then offer
the next phase — **adapted to status**:

- **`status: refined`** — offer the handoff. Invoke `Skill(skill: "workflows-core:reference", args: "phase-handoff")`
  and present its §4.3 consent choice verbatim — the **gated — falling back** variant (§4.1
  bullet 2), because `/product-workflows:create-prd <KEY>` runs `require-on-main` on this `idea.md`
  (§3.4's first row), which settles the class as **gated**, and that row is the *only* one naming
  this file: it preserves the Phase 0 idea ladder instead of stopping, so §4.1's quantifier takes
  the falling-back half. The **gated — stopping** array would promise a refusal `/create-prd` does
  not make: on `absent` it names the file without reading it and goes on down its idea ladder,
  which is what the falling-back array's parenthetical and the declined outcome line both warn of.
  Then on the first option execute `handoff-to-main` (§2) with all five of its §2.9 inputs: `prefix: idea`;
  `feature_folder` = the folder Phase 4 wrote `idea.md` into; `deliverable_paths` = `idea.md`,
  **plus every file Phase 4.5 wrote or reused** — each copy under `attachments/`, each image copy
  under `design/idea-sources/`, and that frame set's `index.md`. **Reused counts**: a copy the
  collision rule matched byte-for-byte was not written by this run, but `idea.md`'s link points at it
  and an earlier run may have left it on no ref — naming a path whose content is unchanged stages
  nothing, while omitting one is a link to a file that never lands; `title: <KEY> Add idea brief`;
  and `body_facts` = the idea's one-line goal, the number of `[NEEDS CLARIFICATION]` markers left
  open, the logged assumptions, whether docs grounding ran, and what was vendored.
  **All five are required** — §2.4's commit subject and §2.7's pull-request title are both derived
  from `title`, and §2.6 supplies every `gh` argument precisely so the run never blocks on an
  interactive editor; passing three of five leaves both unsourced.

  **The vendored files are named literally, one path each — never a directory and never a glob.**
  §2.3 stages by enumeration and classifies everything it was not handed as OTHER, so a copy left out
  of this list is a copy that never reaches the default branch: `idea.md` would land there pointing at
  `attachments/` paths that exist on the operator's disk and on no ref, which is a worse record than
  the one this feature set out to repair. Phase 4.5 hands over that literal list; pass it through
  unchanged. A bare-prompt run vendored nothing and passes `idea.md` alone, exactly as before this
  phase existed — save one over a folder an earlier run had populated a frame set in, which passes
  that set's `index.md` beside it, Phase 4.5 step 6 having rewritten it.
  On option 2 or 3 `handoff-to-main` does not run; emit §4.1's *Declined by the user*
  line (§4.3, *What each option means*), and the run's emitter tail still runs, as it does after
  option 1. Then, **whichever option was taken**, recommend
  `/product-workflows:create-prd <KEY>` `<merge-clause>`, which finds `idea.md` in that folder —
  `<merge-clause>` resolved from the `Phase handoff:` line §4.1 just emitted, per
  `Skill(skill: "workflows-core:reference", args: "next-phase-offer")`'s resolution table, and never written
  unconditionally. **The clause sits outside the command's own code span**, per that reference's
  placement paragraph, which states the rule for every adopter and gives the reason; it binds with
  particular force here, because this offer *is* the one line an operator copies, with nothing
  beside it to mark where the command ends. **The clause is load-bearing here,
  not decoration**: `/create-prd` Phase 0 step 3 rung 1 runs `require-on-main` on exactly this
  `idea.md`, so while the pull request this offer just
  opened is still open that command stops on rows D/E — an unqualified recommendation sends the
  operator into a stop this run itself caused.

  **On a decline, or where §4.1's *Gate failed* line was emitted, offer the `@<path>` route beside
  it** — the one the draft branch below names for the same on-disk state:
  `/product-workflows:create-prd <KEY> @<the absolute path of this idea.md>`. Neither outcome
  committed anything, so `idea.md` is written and on no ref, exactly as a draft is, and `/create-prd
  <KEY>` with no path then finds it on no ref (row F), names it without reading it, and goes on down
  its idea ladder — which comes back to this brief only through its same-session rung or a path the
  operator types, and otherwise grills the PRD from scratch. Named as a path, the file is read where
  it sits on rung 2's terms: never relocated, never gated, reported once as out-of-contract. The
  merge-clause route is for an operator who will land the files first; the `@<path>` route is the
  one that does not wait for them.

  **There is no key to wait for and no disposition to branch on.** The key was given in Phase 0, the
  folder was resolved from it or created by Phase 4's write, and `idea.md` was written there — so the
  three states this offer used to distinguish (rewrite in place, mint a new key, or neither) collapse
  into one.
- **`status: draft`** (N open `[NEEDS CLARIFICATION]`) — **never hand off**, and do not ask. By the
  governing principle the phase is not finished, so there is nothing to hand over. **Offer a next
  step even so**, because an offer left empty here is what makes a draft disappear: the file is
  written, on no branch, and the command that would read it does not. Two steps, in order:
  1. **Recommended — `/product-workflows:idea <KEY> <the same source>`.** Re-running over the folder
     this run wrote into takes Phase 4's *Refine the existing `idea.md`* path, re-opens this file, and
     puts the N open markers one at a time. Closing all of them sets `status: refined`, and the
     handoff offer above fires on that run instead. No merge clause: this run handed nothing off, so
     there is no pull request to wait for.
  2. **Only where the PRD is to be grilled from the draft as it stands —
     `/product-workflows:create-prd <KEY> @<the absolute path of this idea.md>`.** The `@<path>` is
     required, for the reason the refined branch gives on a decline. Nothing was handed off, so
     `/create-prd`'s in-contract rung 1 runs `require-on-main` against this file, finds it on no ref
     and returns row F `absent` — which is a fall-through rather than a stop, and no later rung of
     that ladder looks in the folder again. Named as a path, the file is read where it sits on
     rung 2's terms — never relocated, never gated, reported once as out-of-contract — and its open
     markers are folded into that command's own grill. `/product-workflows:create-prd <KEY>` with no
     path resolves the same folder, names this file without reading it, and goes on down its idea
     ladder — back to this file only through its same-session rung or a path the operator types,
     otherwise to a PRD grilled from scratch: that is the wait this offer names in place of a merge
     clause, and it is discharged by the path, not by a merge.

Also report the code grounding when Phase 2.6 ran: the grounded repos with their `scanned_ref`s, any
repo descoped or unmounted with the themes left unverified, any theme still inconclusive after round 2,
and — first, because it is the most consequential thing a run can produce — the **Reframing** line if
one was written. A reframing that changed the idea's Problem section must not be reported only inside
the file.

`/create-prd` is a separate command; this offer is guidance the user acts on — it never auto-invokes
another command. (Per `workflows-core:next-phase-offer` — the plugin-wide
next-phase-offer contract; `/idea` is one reference implementation.)

### Context hygiene

Continuing to `/product-workflows:create-prd` (still the PM phase)? → run **`/compact`** to free context; your
`idea.md` is already on disk. (No resume pointer or `/rename` label here — not for want of a
key, since Phase 0 required one before this run wrote anything, but for two different reasons:
no pointer because this run hands its brief off in the same run rather than being a phase a
later run resumes (`workflows-core:session-hygiene` §1), and no label because the ideation
phase is short (§4).) Guidance only — see
`workflows-core:session-hygiene`.

---

## Phase 6 — Session maintenance, feedback & cost

Terminal phase — runs after Phase 5, NEVER interrupts an earlier phase.

**Capture-at-block invariant.** If an EARLIER phase **halts on a plugin / skill / command / reference
gap** (a capability the run needed but the plugin lacked), `emit-block` (per
`workflows-core:feedback-emission`) at that halt **before** escalating — so a run
abandoned at the block still records the gap. NEVER `emit-block` for an environment / user halt (bad
source-not-found, cancellation).

**Session-hygiene invariant.** End Phase 5 with a `### Context hygiene` note per
`workflows-core:session-hygiene` — a same-role `/compact` suggestion, and neither a `resume.md`
nor a `/rename` label. Two different reasons, neither of them a missing key: no pointer because
this run hands its brief off in the same run rather than being a phase a later run resumes (§1),
and no label because the ideation phase is short (§4). Guidance only, never auto-run.

1. **Invoke `impl-maintenance`** (subagent_type: "workflows-core:impl-maintenance", model: `<detection_model — §2.1 Sonnet chain>`):
   > "Analyse this session and return a Lessons Learned report.
   >
   > Session handoff:
   > - Command run: /idea
   > - What was done: [one-paragraph summary of the idea refined + source type]
   > - Key events: [source-detection corrections, unresolved clarifications, broken links, links the operator's Phase 1.5 answer left out, images that were not transcribed, links to files nothing opens, sources that failed to vendor — or 'none']
   > - Workarounds used: [manual steps not automated by the workflow — or 'none']
   > - Review verdict: N/A (no reviewer in /idea)
   > - Test result: N/A (no tests in /idea)
   > - Project root: [the idea.md folder]"
2. **Persist plugin feedback (automatic).** Invoke `Skill(skill: "workflows-core:reference", args: "feedback-emission emit-auto")` and call its `emit-auto` entry point (§6)
   with the Lessons Learned report, `command: /idea`, `key` = the run's own key, the run's `source`, and
   `plugin_version` (read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). It renders only the
   plugin-facing slice (§4), dedupes by stable `id` (§3), resolves the target via the §2 specs-first
   ladder, and writes silently. Surface the persisted path (or "no plugin-facing signal — nothing
   persisted").
3. **Session cost (ALWAYS runs).** Invoke `Skill(skill: "workflows-core:reference", args: "cost-emission emit-cost")` and call its `emit-cost` entry point with `command: /idea`, `phase: prd-creation`, `role: pm`, `key` = the run's own key,
   the run's `source`, and `plugin_version`. The key is always present — `/idea` refuses to run without
   one — so the entry lands on the keyed tier and never on the pending ladder (§9), which
   **advances the chained checkpoint** (§3); surface the persisted path (or the report-only notice).
4. **Commit session artifacts (terminal).** Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git commit-artifacts")` and execute its `commit-artifacts` entry point (§4) inline — the LAST action of the run. It stages
   ONLY the §2.1 bounded artifact paths inside `$SPECS_PATH`, commits `<KEY> Add dev-workflows
   session artifacts (/idea)` — the key is mandatory here, so `NOISSUE` never applies — and pushes. It NEVER
   touches a code/docs repo, or the current working directory, where it is not the specs repository; NEVER force-pushes; NEVER
   fails the run; and skips entirely when the run carries `specs_git: blocked` (§3.3 G0), re-emitting
   that notice. Hold its §6 outcome line for the Final report.

ADDITIVE — this phase NEVER fails the run, NEVER commits the deliverable (idea.md itself is handed off separately, before this phase, via `workflows-core:phase-handoff` §2, behind Phase 5's §4.3 consent choice; the terminal step above commits only the bounded session-artifact paths in `$SPECS_PATH`), and NEVER writes into a code/docs repo or the current working directory, where it is not the specs repository; no user name is ever written.

---

## Final report

Report: the `idea.md` path + `status` (refined / draft with N open clarifications); the source type and
`sources`; the count of `[NEEDS CLARIFICATION]` items and Assumptions; the source-stated scope boundaries (`stated_scope`) and any the grill reversed, with the user's reason; any source-detection correction
or broken links; **what the source read cost and what it left** — Phase 1.5's walk (how many files
it reached, at which depths, and the operator's answer where one was asked), every
`wikilinks_not_followed` entry with its `excluded` reason, how many linked images were transcribed,
every image left with `read: false` and why, and beside them the `notes` Phase 2 collected from
`figure-reader`. Report these even when nothing was excluded ("all N linked images transcribed; no
link left unfollowed"), because the absence of a notice of what was left unread is only informative
once the run is known to print one; **what the
run vendored and what it did not** — the count of files copied into `attachments/`, **saying whether
the source is among them**, since one copy lands there for the source and for every markdown file
Phase 1.5 **took** — **a count of what this run copied, never of what the walk reached**, so unlike
the walk's own two counts, which both count what was reached, it does not stand in a fixed relation
to anything on the counts line: it runs one ahead of that line's markdown tally only where the walk
took every page it reached and every one of them was written, and where it does not, the report
names which of the four states it was (the operator's *Only what the source links directly* answer,
a copy the collision rule reused rather than wrote, a copy that failed at Phase 4.5 step 7, or a
markdown source step 1 dropped as already inside the PRD folder) rather than asserting the relation;
and of images copied into `design/idea-sources/`; **and beside both, every copy
the collision rule *reused* rather than wrote** (its rule 1), which is in `deliverable_paths` and in
neither count and is otherwise reported nowhere — the one run state that rule exists to serve;
whether that frame set's `index.md` was written and how many rows it now
holds against how many this run added, every name the collision rule substituted or refreshed, the
number of links rewritten in `idea.md` **and every target left unrewritten because two copied entries were written
identically** (with each source and each copy), every frame indexed with no description on record, every
index row dropped because its image is gone, and every source left uncopied with its reason
(`excluded`, broken, `ambiguous`, `missing`, `unreadable`, `not_an_image`, a linked file nothing
opens — not markdown, not an image — with its extension, or a copy that failed) — stated plainly
where nothing was vendored at all ("no source to vendor: the idea came from a prompt", or "nothing
linked"), and naming no
directory this run did not actually create; the resolved model routing (+ any Opus degradation); the feedback path; the cost
path (or notice); the `Specs repo:` outcome line from `commit-artifacts`
(`workflows-core:specs-repo-git` §6), with any guard notice repeated in full; the
`Phase handoff:` outcome line (`workflows-core:phase-handoff` §4.1) — `handoff-to-main`'s on the
first option, and the *Declined by the user* line on either other (Phase 5), that line being the one
saying the files are written and not on the default branch; **a `status: draft` run prints none of
them**, Phase 5's draft branch offering no handoff and asking nothing, so there is no entry point
run and no offer declined for §4.1 to have a line about; the code grounding outcome — the grounded repos with their `scanned_ref`s, any
descoped or inconclusive ones, and — first, because it is the most consequential thing a run can
produce — the **Reframing** line if one was written; or, when no scan ran, `code grounding: off` (no
`--ground-code`) or `code grounding: declined at the repo gate` (`--ground-code` given, "Ground
nothing" chosen); and the adaptive next-phase recommendation.

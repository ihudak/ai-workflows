# D50 — the claim sweep's population

Recorded by Task 1 on 2026-11-12, before any edit, at commit `a26afb32` on `fix/d50-same-day-ordering`. Line numbers are that commit's; an edit above a site moves it, so Task 5 finds each site again by its phrase, never by its number.

**The subject:** how `/dev-workflows:ready` and `workflows-core:source-truth` §7.8 order the four records — `/implement`'s block, the conformance record, the dev-stage release note, `pr-draft.md` — and what each record's date is.

**Method:** `.claude/rules/claim-sweep.md` refinements 4, 6–8, over `plugins/` (every `CHANGELOG.md` included), the repo-root `README.md`, `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/`. Each seed phrase of the brief was searched wrap-insensitively, with whitespace collapsed across the file and the phrase. The subject was then searched by its other wordings: `no work implemented`, `no work was implemented`, `no work has been implemented`, `work implemented on the PRD`, `latest work`, `newest work`, `older than work`, `older than that work`, `predates work`, `dates of the implementation`, `dates of the \`implementation.md\``, `date of each \`implementation.md\``, `time of day`, `last commit that changed`, `its last commit`, `the newest such draft`, `dated by`, `later Epic run`, `\`Run:\` line naming`, `the role, the date`, `header's \`Run:\``, `§2's \`Run:\``, `Delivery verified`, `Release Preparation`, `pr-draft.md`, `stage: dev` and `%cs`. Each hit was read in its paragraph. The exclusivity probe (refinement 3) took `only line that is neither`, `No other reader`, `the only writer` and `Only … writes it`, then, over what a block holds, `refs and nothing else`, `refs only`, `holding refs`, `only refs`, `never a summary` and `A ref cannot drift`.

Sites the brief did not seed are marked **(new)**.

## A. `/ready`'s ordering and dating — the command

- `plugins/dev-workflows/commands/ready.md:195` — "and by whether work was implemented after that PRD record (the test's condition 6)" **(new)**
- `plugins/dev-workflows/commands/ready.md:197` — "one whose `<YYYY-MM-DD>` date cannot be read" (record unreadable) **(seed)**
- `plugins/dev-workflows/commands/ready.md:198` — "`workflows-core:implementation-format` §1 the block heading condition 6 reads" **(new)**
- `plugins/dev-workflows/commands/ready.md:204` — "is dated later than the record's `- **Run:**` date"; "**A block dated the record's own day is not counted**"; "carry a date and no time"; "**Nor a zone**"; "the dates are compared as written"; "the first block dated later fails the condition" **(seed)**
- `plugins/dev-workflows/commands/ready.md:205` — "`work implemented since the record (<unit key>, <block date>)`" **(seed)**
- `plugins/dev-workflows/commands/ready.md:207` — "(checked <the record's Run: date>)" — the `Delivery:` line, which the spec keeps **(new)**
- `plugins/dev-workflows/commands/ready.md:211` — "its date is that of the last commit that changed it on `<default-ref>`"; "`log -1 --format=%cs`"; "a shallow clone that lacks the commit"; "Its text is not read." **(seed)**
- `plugins/dev-workflows/commands/ready.md:212` — "Such a draft is dated by the `<YYYY-MM-DD>` its comment's first line ends with"; "the latest of those dates is the dev-stage release note's date"; "a change to the `stage:` line or the first line's date there is a change here too" **(seed)**
- `plugins/dev-workflows/commands/ready.md:213` — "holds only where its date is no earlier than that of the latest `## <YYYY-MM-DD> — /implement` block"; "The dates are compared as written"; "neither carries a time or a zone"; "its reason names the latest block" **(seed)**
- `plugins/dev-workflows/commands/ready.md:215` — "`pr-draft.md on <default-ref> could not be dated`"; "`pr-draft.md (<its date>) predates work implemented since (<unit key>, <block date>)`"; "`the latest dev-stage release note (<its date>) predates work implemented since`" **(seed)**
- `plugins/dev-workflows/commands/ready.md:523` — "(checked <the record's Run: date>)" — the report template, which the spec keeps **(new)**
- `plugins/dev-workflows/commands/ready.md:627` — "(checked <the record's Run: date>)" — the brief's `delivery` line, which the spec keeps **(new)**
- `plugins/dev-workflows/commands/ready.md:917–918` — "neither signal holds where it is dated before the latest `implementation.md` block in the PRD's tree, compared by date as step 2b's condition 6 compares" **(seed)**
- `plugins/dev-workflows/agents/readiness-reviewer.md:35` — "(checked <the record's date>)" — the `delivery` input, which the spec keeps **(new)**

## B. `/ready`'s ordering — references and rules

- `plugins/dev-workflows/references/workflow-states.md:31` — "with no work implemented after it" **(new)**
- `plugins/dev-workflows/references/workflow-states.md:32` — "neither dated before the latest `implementation.md` block in the PRD's tree, a same-day block not counted" **(seed)**
- `plugins/dev-workflows/references/workflow-states.md:37` — "no `implementation.md` block in the PRD's tree is dated after the record"; "older than work implemented since" **(seed)**
- `plugins/dev-workflows/references/conformance-format.md:125` — "the date of each `implementation.md` block in the PRD's tree, since work implemented after the record's `Run:` date leaves the stage unreached" **(seed)**
- `plugins/workflows-core/references/implementation-format.md:10–11` — "for the date each block's heading carries, by `/dev-workflows:ready`'s *Delivery verified* test, which counts a block dated after the PRD's conformance record as work implemented since" **(seed)**
- `plugins/docs-workflows/references/release-note-types.md:53–58` — "`/dev-workflows:ready` reads this line, and the first line's date"; "the newest such draft is dated no earlier than the latest `implementation.md` block in the PRD's tree"; "a change to either line is a change to that command too" **(seed)**
- `.claude/rules/release-notes.md:35` — "dating it by the first line's date, which must be no earlier than the PRD tree's latest `implementation.md` block"; "a change to the stage line or the first line's date is a change to `/ready` too" **(seed)**
- `.claude/rules/dev-workflows.md:37` — "no implementation.md block in the PRD's tree dated after its Run: date"; "neither dated before that tree's latest block" **(seed)**
- `.claude/rules/dev-workflows.md:71` — "the dates of the `implementation.md` blocks in the PRD's tree"; "no block dated after its `Run:` date, a same-day block not counted" **(seed)**
- `.claude/rules/dev-workflows-conformance.md:22` — "and from the dates of the `implementation.md` blocks in the PRD's tree, whether the PRD reaches the optional *Delivery verified* rung" **(new)**

## C. `source-truth` §7.8 — the ordering of two conformance records

- `plugins/workflows-core/references/source-truth.md:587` — "or one with no `Run:` line naming `Epic` or `PRD` and a date" — the malformed test, which the spec keeps reading `Run:` alone **(new)**
- `plugins/workflows-core/references/source-truth.md:589` — "of the record's header, the `Run:` line's date and the `Code checked:` lines" **(seed)**
- `plugins/workflows-core/references/source-truth.md:593` — "where the Epic's record carries a later `Run:` date than the PRD folder's"; "the Epic run traced the code after the PE ruled" **(seed)**
- `plugins/docs-workflows/docs/commands/document.md:100` — "no `Run:` line naming an Epic or PRD run and its date"; "unless a later Epic run has since closed it" **(new)**
- `plugins/docs-workflows/docs/commands/release-notes.md:47` — "no `Run:` line naming an Epic or PRD run and its date"; "unless a later Epic run has closed the entry" **(new)**

## D. What each record's date is — formats, writers and read lists

- `plugins/workflows-core/references/implementation-format.md:19` — "One `## <YYYY-MM-DD> — /implement` block per run that committed" (§1, and its examples at 21–37 and 45–55) **(new; in the brief's Files list)**
- `plugins/workflows-core/references/implementation-format.md:57` — "No other reader of this file takes the field." (exclusivity; `accepted:`'s, re-read beside the new `at:` paragraph) **(new)**
- `plugins/workflows-core/references/implementation-format.md:61` — "holds at least one `## <YYYY-MM-DD> — /implement` block" — the presence test, which stays **(new; in the brief's Files list)**
- `plugins/dev-workflows/commands/implement.md:1313` — "naming `repo` (its `<repo-slug>`, as §1 says), `branch`, `base`, `commit` and `pushed`" — Phase 4.7, the block's writer **(new)**
- `plugins/dev-workflows/references/conformance-format.md:27` — "`- **Run:** <Epic | PRD> — role `<dev | pe>` — <YYYY-MM-DD>`" — §2, the record's date **(new)**
- `plugins/dev-workflows/references/conformance-format.md:121` — "§2's `Run:`, `Code checked:` and `Verdicts:` lines" — what `/release-notes` reads **(new)**
- `plugins/dev-workflows/references/conformance-format.md:123` — "§2's `Run:` and `Code checked:` lines" — what `/document` reads **(new)**
- `plugins/dev-workflows/commands/conformance.md:392` — "**Write `_conformance.md`** into the unit's folder per `conformance-format.md`: §2's header" — Phase 5, the record's writer **(new)**
- `.claude/rules/dev-workflows-conformance.md:13` — "write _conformance.md — its header's Not traced: … and Not shown merged: … lines" — `/conformance`'s map line **(seed)**
- `plugins/docs-workflows/references/release-note-types.md:37` — "`<!-- release-note scope: ACME-77-01 2026-09-20`" — §1's example comment **(new)**
- `plugins/docs-workflows/references/release-note-types.md:44–45` — "and the date the run appended the draft" — the first line's date **(new)**
- `plugins/docs-workflows/references/release-note-types.md:48` — "it is the comment's only line that is neither its first nor a `read:` line" (exclusivity) **(seed)**
- `plugins/docs-workflows/commands/release-notes.md:217` — "its `Run:` line (an Epic or a PRD run, the role, the date)" — Phase 0's read list **(new)**
- `plugins/docs-workflows/commands/release-notes.md:668` — "its first line `<!-- release-note scope: <KEY> <YYYY-MM-DD>` … and the date today's; then the line `stage: <run_phase>`" — Phase 8 step 1, the note's writer **(new)**
- `plugins/docs-workflows/commands/document.md:446` — "its header's `Run:` line and its `Code checked:` lines" — Phase 3's read list **(new)**
- `plugins/docs-workflows/commands/document.md:1317` — "**Write + show**: write `pr-draft.md` to the resolved PRD folder (ask if none) AND print it." — Phase 8.5 step 3, the draft's writer **(new)**
- `plugins/docs-workflows/references/finish-and-handoff.md:91–93` — "Compose the draft and BOTH write and show it: **write** to the resolved PRD folder as `pr-draft.md`" — §5, the draft's composition **(new)**

## E. The pages

- `plugins/dev-workflows/docs/commands/ready.md:3` — "no work has been implemented after it"; "neither is older than the latest work implemented on the PRD" **(new)**
- `plugins/dev-workflows/docs/commands/ready.md:58` — "is dated later than the record. A block dated the record's own day does not count, since neither records a time of day"; "older than work implemented since"; "the date of the first later block it found" **(seed)**
- `plugins/dev-workflows/docs/commands/ready.md:59` — "dated no earlier than the latest `/implement` record … dated the same way"; "`pr-draft.md` by the date of the last commit that changed it on the default branch, the release note by the date its newest dev-stage draft was appended"; "A draft dated the same day as that record still counts"; "older than that work" **(seed)**
- `plugins/dev-workflows/docs/commands/ready.md:66` — "(checked <the record's date>)" — the `Delivery:` line, which the spec keeps **(seed)**
- `plugins/dev-workflows/docs/commands/ready.md:68` — "dated before the latest work implemented" **(seed)**
- `plugins/dev-workflows/docs/commands/ready.md:101` — "with no work implemented after it" **(seed)**
- `plugins/dev-workflows/docs/commands/conformance.md:89` — "and no work implemented after it, by the dates of the PRD's and its Epics' implementation records" **(seed)**
- `plugins/dev-workflows/docs/workflow.md:50` — "no work implemented after it"; "neither is dated before the latest work implemented on the PRD" **(new)**
- `plugins/dev-workflows/docs/workflow.md:75` — "from the dates of the implementation records, since work implemented after the record leaves the stage unreached"; "since work implemented after the drafts leaves the stage unreached" **(seed)**
- `plugins/dev-workflows/docs/reference/references.md:18` — "with no work implemented after it"; "neither dated before the latest work implemented on the PRD" **(seed)**
- `plugins/product-workflows/docs/workflow.md:134` — "beside the dates of the implementation records"; "or work implemented after it" **(new)**
- `plugins/product-workflows/docs/workflow.md:225` — "from the dates of the implementation records, since work implemented after the record leaves the stage unreached"; "after the drafts" **(seed)**
- `plugins/workflows-core/docs/family-map.md:193` — "no work has been implemented after it"; "neither is dated before the latest work implemented on the PRD" **(seed)**
- `plugins/docs-workflows/docs/commands/release-notes.md:62` — "naming the PRD's key …, the date"; "counted only while no work implemented on the PRD is dated after the newest such draft's date" **(seed)**
- `plugins/docs-workflows/docs/commands/document.md:70` — "counted only while no work implemented on the PRD is dated after its last commit there" **(new)**

## F. Maintainer tier

- `docs/maintainers/rationale.md:483` — "two same-day `/implement` blocks on one unit, each `pushed: true`, became one block" — named by spec §4 "where it states the limit". Read: it records LC11's measured `union` defect and the entry-set merge that replaced it, and states no `/ready` ordering limit. Task 5 re-reads it; on this reading it stays. **(new; named by the spec)**

## G. What a block holds — exclusivity claims `at:` reaches

Found by the exclusivity probe (refinement 3) over the block's contents: `at:` is an instant, neither a ref nor a summary.

- `plugins/dev-workflows/commands/implement.md:1318` — "**Beyond that field, it records refs and nothing else.**" — false once Phase 4.7 writes `at:` **(new)**
- `.claude/rules/workflows-core.md:36` — "(refs only, never a summary — a ref cannot drift and a description can)" — false once a block carries `at:` **(new)**
- `plugins/workflows-core/docs/reference/references.md:31` — "with one entry — the code repository the run branched — holding refs and never a summary" — not exclusive as written; re-read **(new)**

**Count: 65 sites** — A 14, B 10, C 5, D 17, E 15, F 1, G 3. In the brief's Step 1 seed list: 31; not in it: 34. Counted as the `- ` lines under headings A–G.

## Examined and left out — not the subject

These were read and are not counted. Each either falls under a non-goal of the spec or states no ordering or dating of the four records.

- **Non-goal: the session-hygiene resume-pointer rules** (spec §2). `plugins/workflows-core/references/session-hygiene.md:151–199`, its generated part `plugins/workflows-core/reference-parts/session-hygiene/resume-pointer.md:166–214`, and the two pages `plugins/dev-workflows/docs/reference/resume-and-checkpoints.md:65–86` and `plugins/product-workflows/docs/reference/resume-and-checkpoints.md:65–86` ("A block of the same day is dated by the commit that added its heading line").
- **Non-goal: `implementation-format` §4's date fallback** (spec §2). `plugins/workflows-core/references/implementation-format.md:368–391`, and `plugins/docs-workflows/references/release-note-types.md:96–102` ("is dated by the file's last write before a scope line first reached it").
- **`implementation-format` §5's `unit-branch` date.** `plugins/workflows-core/references/implementation-format.md:461` ("`<date>` comes from the block's own `## <YYYY-MM-DD> — /implement` heading"), and its summary in `.claude/rules/workflows-core.md:36` ("since the block's date"). Spec Task 1 step 4 leaves §5 unchanged; the heading stays.
- **Mentions of the readers with no date or order in them.** `plugins/dev-workflows/agents/readiness-reviewer.md:47` and `:138` (it never reads the drafts or the record); `plugins/dev-workflows/commands/ready.md:377–398` (Phase 3(0) derives the rungs from `delivery.state` and `release_preparation.state`); `plugins/docs-workflows/docs/reference/references.md:29`, `plugins/docs-workflows/docs/commands/release-notes.md:74` and `plugins/dev-workflows/docs/roles-and-phases.md:45` and `plugins/dev-workflows/docs/README.md:24` (name the reader or the stage, no date); `plugins/workflows-core/docs/reference/references.md:41` ("which of two entries on one claim wins", no date); `plugins/dev-workflows/references/conformance-format.md:94` and `:119` (`final` over `proposed`, no date); `plugins/workflows-core/references/next-phase-offer.md:363` and its part `reference-parts/next-phase-offer/dev.md:181`; `.claude/rules/docs-workflows.md:79`.
- **History.** Every `CHANGELOG.md` hit — `plugins/dev-workflows/CHANGELOG.md:87`, `:99`, `:103`, `:104`; `plugins/product-workflows/CHANGELOG.md:63`, `:71`; `plugins/workflows-core/CHANGELOG.md:155`; `plugins/docs-workflows/CHANGELOG.md:70` — sits in a dated, released section. None of the four changelogs holds an `— Unreleased` section. A released entry records what that release did, which this change does not falsify. `.claude/rules/plugin-updates-coupling.md:21` is the released 4.61.0 coupling bullet, and states no date order.
- **Other subjects that share a phrase.** `plugins/docs-workflows/docs/commands/docs-profile.md:54` ("compared as written"), `plugins/workflows-core/references/specs-repo-git.md:366` ("dated by"), the `security-workflows` `register.py` hits ("dated before"), and `plugins/product-workflows/commands/*` hits for "dated by" and "dated before". The fetch sites that say "refs only" of a `git fetch` (`plugins/dev-workflows/commands/conformance.md:73`, `:103`, `:119`, `plugins/dev-workflows/commands/implement.md:413`, `plugins/dev-workflows/docs/commands/conformance.md:68`, `plugins/workflows-core/references/implementation-format.md:452`), the session-hygiene "only refs older than" sites, `plugins/docs-workflows/docs/roles-and-phases.md:36` and `plugins/workflows-core/references/specs-repo-git.md:1188`. `plugins/workflows-core/references/implementation-format.md:133`, "A ref cannot drift", sits in §2's case against a summary and claims no exclusivity.

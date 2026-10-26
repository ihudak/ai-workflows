# To test on a real project — behaviour no live run has exercised yet

Each item below shipped verified by the gate chain and a rule-by-rule reading, not by a live run. Work through it in an environment that has the family's plugins installed from this marketplace and a real specs repository and code repository to run them on — the e2e copies the piece-review runs used are the model. **Run an item, then delete it** in the same commit as the run's record, and add any defect it finds to `docs/superpowers/to-fix.md`. A failed expectation is a defect, never a reason to edit the expectation, unless the item itself was wrong, which the commit then says.

Before the first item, install the releases each section names — `claude plugin update <plugin>@<marketplace>` for each, then restart Claude Code (`.claude/rules/plugin-updates.md`).

## Fix batch B16 — `workflows-core` 1.52.0, `product-workflows` 3.43.0, `dev-workflows` 4.35.0

Install all three together: `/epics`' offer and the `/specify` and `/implement` picker caps rely on 1.52.0.

- **B16-1 — `/epics` offers to apply the MINOR and NIT findings a review leaves open** (FBB-B21). Setup: a PRD whose `epic-reviewer` verdict comes back `PASS WITH RECOMMENDATIONS` with at least one surviving MINOR or NIT finding whose fix is only an edit — a vague criterion wording is the usual one. Expect, in order:
  - `doc-fixer` takes the MAJOR findings only;
  - the offer `Apply them (Recommended)` / `Go on without applying them …` lists each MINOR and NIT with its severity, and says a re-review remains;
  - on **Apply them**, the orchestrator edits the Epic itself, never `doc-fixer`, and reads each edit against what it overlaps;
  - the unspent re-review is offered next;
  - after the re-review, where it is not `BLOCK`, the offer is made once more for what is left open, and no review follows it;
  - the final report's version line names those edits.

  Also check that no *Epic size* finding, unverified finding or user-resolved text appears in the offer.
- **B16-2 — the version line names by id what changed in substance** (FBB-B15). Setup: any authoring run — `/specify` is the easiest — where you apply a finding after the verdict that changes a criterion's meaning, not only its wording. Expect `Changed in substance since: [ACxx]` (the criterion's own id) on the version line in the final report, in the session record, and in the specs pull request's body. A wording-only edit should be counted among the edits but appear in no such list.
- **B16-3 — the Epic picker carries every Epic where they fit in four** (GIT-B4). Setup: PRDs with two, three, four and five Epic folders.
  - `/implement <PRD>` on a PRD with a flat `specification.md`: two or three Epics give every Epic row plus the broad-slice option, with no *Another Epic …* row; four or five give two Epic rows, the broad-slice option and *Another Epic …*.
  - `/implement <PRD>` without a flat `specification.md`: up to four Epics give every row, with no *Another Epic …*; five give three rows plus *Another Epic …*.
  - `/specify <PRD>`: three Epics give all three plus *Author one broad PRD-level spec instead*; four give two Epic rows, that option and *Another Epic …*.
  - The prose list above the prompt names every Epic in every case.
- **B16-4 — the merge clause after a failed commit** (GIT-B3). Setup: in the specs copy, add a `pre-commit` hook that exits non-zero, then run `/specify <EPIC>` through to its handoff and accept it. Expect the handoff line `Phase handoff: NOT handed off — the commit failed (…)`, and the next-step offer of `/dev-workflows:design` carrying `(once the deliverable staged on <branch> is committed, pushed and its pull request merged)`, naming the real branch — never the catch-all `(once this phase's artifacts are on the default branch)`. Remove the hook afterwards.
- **B16-5 — `/brd-package`'s next step on the repository route** (BRD3-B24). Setup: a BRD slice packaged on the repository route. Expect the offered reconcile line to read `/product-workflows:brd-reconcile <BRD-KEY>` with `@<review-file>` only as the alternative for a review sent back as a file — never a required path.
- **B16-6 — the PE lane's `/design <PRD>` offer** (D17 nit). Setup: `/specify <PRD>` at PRD level on a single-component PRD whose Epic folders hold no `specification.md` on the default branch. Expect no offer of `/dev-workflows:design <PRD>` as designing those Epics; with one Epic's `specification.md` merged, expect it.

## `dev-workflows` 4.33.0 — the fixes from the review of piece review (#85)

- **433-1 — `/design` reads a stale `_N/A` above drawn pieces as malformed** (F3, F2). Setup: a `design.md` whose `## Pieces` section holds `_N/A — …` followed by a `Reason:` line and two pieces, reached by `/design` revising it. Expect Phase 5.5 to report the section malformed (`the section holds an _N/A line beside other lines`), fix it once, re-run the parse, and — where the fix does not settle it — remove the section, naming each defect, fix and removal in the Final report. It must ask nothing and never loop.
- **433-2 — `/implement`'s split round verifies before it collapses** (F1). Setup: run C's — `/implement BOOK-3-01` on a design drawing two pieces at the parser contract, from the code start state of `docs/superpowers/verification/2026-10-25-implement-piece-review.md` §3. Expect two piece reviews and the overall review. In the run-state `triage` entries and the Phase 5 report, every finding of every review is verified on its own; a finding the overall review repeats at a piece review's location with the same claim is collapsed only where both got the same disposition, its triage line naming both reviews; where the two differ, each keeps its own. Compare cost with run C's $84.51: this change should move it little.
- **433-3 — `pieces.py` output stays valid UTF-8** (F4). Setup: in a scratch clone, a file whose name holds a byte that is not UTF-8, changed on a run whose design draws no pieces. Expect one review and no `## Pieces unusable` line.

## `dev-workflows` 4.35.1 — a `MODERATE` `/implement` run's review receives the specification (#91)

- **4351-1 — the review gate of a `MODERATE` keyed run carries `applicable_spec`, and splits by the design's pieces.** Setup: a small test-only Epic in the e2e copies whose `specification.md` and `design.md` are merged, its design drawing two pieces with a stated `Reason:` (written by hand is fine: this tests `/implement`'s split, not `/design`'s drawing), and a change `/implement` classifies `MODERATE` that touches the files of both pieces. Expect:
  - run-state `spec_context.applicable_spec` written in Phase 2A, before the plan;
  - the review brief carrying `applicable_spec:` and `Spec-named tests:`;
  - two piece reviews and the overall review, the overall review alone tracing requirements and writing `conformance.summary`;
  - the Phase 5 report listing each scope's verdict.

  Before 4.35.1 this run made one review with no `applicable_spec`, so a review brief without that line, in the session's transcript, means the fix did not take.

## Live checks kept in `to-fix.md`

These stay in `docs/superpowers/to-fix.md`, which holds their detail; they are named here so a test session sees every live check in one place.

- **PR2** — measure the first `/implement` of a design drawing more than two pieces.
- **PR3** — `/design` on a genuinely small Epic should draw no `## Pieces`; run it in the same session as 433-1 if convenient.
- **PR5** — watch whether the overlap read `workflows-core` 1.51.0 added runs, on any `/design` or `/specify` run.

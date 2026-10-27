# To test on a real project — behaviour no live run has exercised yet

Each item below shipped verified by the gate chain and a rule-by-rule reading, not by a live run. Work through it in an environment that has the family's plugins installed from this marketplace and a real specs repository and code repository to run them on — the e2e copies the piece-review runs used are the model. **Run an item, then delete it** in the same commit as the run's record, and add any defect it finds to `docs/superpowers/to-fix.md`. A failed expectation is a defect, never a reason to edit the expectation, unless the item itself was wrong, which the commit then says.

Before the first item, install the releases each section names — `claude plugin update <plugin>@<marketplace>` for each, then restart Claude Code (`.claude/rules/plugin-updates.md`).

## Fix batch B16 — `workflows-core` 1.52.0, `product-workflows` 3.43.0, `dev-workflows` 4.35.0

Install all three together.

- **B16-5 — `/brd-package`'s next step on the repository route** (BRD3-B24). Setup: a BRD slice packaged on the repository route. Expect the offered reconcile line to read `/product-workflows:brd-reconcile <BRD-KEY>` with `@<review-file>` only as the alternative for a review sent back as a file — never a required path. The slice must be one whose interview has settled. Neither BOOK-2 slice on the e2e specs copy qualifies: BOOK-2-01's reconciliation of 2026-10-12 deferred four answers to another round, and BOOK-2-02 was never interviewed. So this item rides with the next live run of the BRD route, as its user decided on 2026-10-27, rather than costing an interview round of its own.

## `security-workflows` 0.4.0 — the paths sub-project A's end-to-end run never took

Sub-project A's Task 12 never merged the Epic's pull request (`docs/superpowers/verification/2026-10-15-security-workflows-scan.md`), so these ran at script level only. Setup for each: the e2e copies, with a register seeded as for run 6 of `docs/superpowers/verification/2026-10-26-live-checks.md`, but from a real change scan, so that a `fixing` finding has a patch and a follow-up line.

- **SEC-A1 — `--verify-fixes` closes a fix that merged.** After `/dev-workflows:implement <EPIC>` lands the fix on the Epic's branch and its pull request merges, run `/security-workflows:scan <repo> --verify-fixes` as the Security Engineer. Expect a scan of the fixed file at the default branch's head in a temporary worktree, removed afterwards, and the `fixing` finding closed `fixed` by itself (`security-register-format` §5 rule 2). The follow-up line must still read as the run left it. Before the merge, the same run stops with `SECURITY_NOTHING_TO_VERIFY`.
- **SEC-A2 — `/dev-workflows:conformance` after the Epic merged.** Expect `unit-branch` to read `merged` and the Epic run to trace the default branch.
- **SEC-A3 — the register in session-branch mode.** With `workflows.sessionBranch` set on the specs copy, run a change scan. Expect the register's paths, `runs/`, `scans/`, `register.json` and `register.md`, committed on `session/<identity>` with the run's session files and pushed there, the default branch untouched, and the next run's preflight finding them through the overlay.

## `security-workflows` 0.5.0, `workflows-core` 1.60.0 — the move a reserved record's merge makes

Install both together.

- **LC10 — the triage report names the move before the push** (to-fix LC10, live checks of 2026-10-26). Setup: run 6's in `docs/superpowers/verification/2026-10-26-live-checks.md` — the seeded register's `[SEC#1]` CWE-79 and `[SEC#2]` CWE-319 on `main`, a record from a scratch clone, dated earlier, allocating `[SEC#1]` to CWE-601, pushed by the watcher once the run asks its first triage question — then `/security-workflows:scan <repo> --triage`, marking `[SEC#1]` a false positive. Expect 7.1's plan to print `reserved_moves` with CWE-79's move from 1 to 3, naming the planted record, beside `"renumbered": []`; and the report's `### Register` to name `[SEC#1]` → `[SEC#3]` as provisional, once that record merges, on its *Moves on merge* line, from `reserved_moves` and before the push, with no dry rebuild of the run's own, and under it the check to run after each pull, its values written in and its stop. After the settle line's merge, run that check: `rebuild` should give CWE-79's origin `[SEC#3]` in `numbers` and list its move from `[SEC#1]` in `renumbered`, so the first run that records reports it; with no `held_by` and the planted record in `runs/`, the check stops there, CWE-79 standing under `[SEC#3]`. The false positive's evidence line is shown in the reply's text or in the next question's own, not only in a command's output.

## Live checks kept in `to-fix.md`

These stay in `docs/superpowers/to-fix.md`, which holds their detail; they are named here so a test session sees every live check in one place.

- **PR2** — measure the first `/implement` of a design drawing more than two pieces.
- **LC5** — after its fix, `/design` revising a `design.md` whose `## Pieces` holds a stale `_N/A` above two pieces should fix it with no question.
- **LC6** — after its fix, the offer made after a re-review lists each open finding with its severity in its own question.
- **LC9** — after its fix, `/specify`'s next step offers `/design <PRD>` on a multi-component PRD holding Epics only once an Epic's `specification.md` is merged. This replaces B16-6, whose single-component setup could not reach the case.

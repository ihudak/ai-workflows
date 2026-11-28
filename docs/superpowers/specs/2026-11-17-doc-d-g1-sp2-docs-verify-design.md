# DOC-D-G1 sub-project 2: `/docs-verify`

Date: 2026-11-17. Status: **revision 3, approved by the maintainer 2026-11-17** with the recommended answer to each of the four questions: Q1 an unresolvable unit stays `drafted`, tagged `claims-unresolved` in its three cases only, `explanation` pages verified by hand at route step 6; Q2 the parameter-free shared steps extracted into `references/docs-iteration/backlog-run.md` as batch 1; Q3 the fourth option *Stop — keep these answers for a later run*, with a record commit for every walk that ends without its move; Q4 four batches, each released on its own. Its four GIT-G1 edits are truth-only, under the maintainer's 2026-11-17 standing OK for DOC-D-G1. This is the design-questions step P-D1 gives sub-project 2. Revision 2 answered design review 1 (`.superpowers/design-review-1.md`: 1 Critical, 13 Important, 12 Minor). Revision 3 answers design review 2 (`.superpowers/design-review-2.md`: 2 Important, 7 Minor, all new), whose verdict is that no further review is needed once these are fixed.

The parent is `docs/superpowers/specs/2026-11-17-doc-d-g1-docs-iteration-design.md` (revision 3, approved 2026-11-17), and it is the authority. This document settles what the parent leaves open: its *What is left to the builder* (:194), and whatever else a plan needs. A departure from an approved decision is named, and goes to the maintainer as a question.

Base: `main` at `74d3e8d1e` (`docs-workflows` 1.43.0, `workflows-core` 1.97.0, with sub-project 1 shipped as PR #210). `file:line` citations are at that commit. Anything not grounded in a citation is marked *assumption*. The four questions at the end are the maintainer's; each `S2-D<n>` is the author's.

**Abbreviations**, under `plugins/docs-workflows/` unless named:

| | Path or meaning |
|---|---|
| **BF**, **EC**, **FH**, **ST**, **SRG**, **PH** | as in the parent |
| **ROUTE** | `docs/docs-workflow.md` |
| **DW** | `commands/docs-write.md` |
| **UB** | `references/docs-iteration/unit-brief.md` |
| **GL** | `references/gate-ledger.md` |
| **BL** | `scripts/backlog-lines.py` |
| **AUD** | `commands/docs-audit.md` |
| **WRT** | `agents/doc-writer.md` |
| **REV** | `agents/doc-reviewer.md` |
| **CS** | `plugins/workflows-core/agents/code-scanner.md` |
| **SRC** | `plugins/workflows-core/references/source-truth.md` |
| **ROR** | `plugins/workflows-core/references/read-only-repos.md` |
| **MR** | `plugins/workflows-core/references/model-routing/classification.md` |
| **WCG** | `.claude/rules/workflows-core-git.md` |
| **BKR** | `.claude/rules/docs-workflows-backlog.md` |
| **P-D1** to **P-D17** | the parent's decisions |

## Revision 3 — review 2's findings

| Finding | Where it is settled |
|---|---|
| **N1** | S2-D15 and S2-D4. The stamp test and P-D11's *Take these answers* question move into batch 3, so a stopped or blocked walk's answers survive the next run. Batch 4 keeps `--prepare`, its stamp write, the printed checklist and EC §5's text. Each batch's "usable" line is re-read |
| **N2** | S2-D6 and Q1. `--block` is passed only for Q1's three cases; a blocked, unanswered or stopped walk records with no token and stays resumable |
| **N3** | S2-D4, *Images*: the slot question is asked when answers are taken, too |
| **N4** | Q1: *Leave it undecided*; the decision is recorded in the report and FH §6.6's draft |
| **N5** | Q1: the token stops `--next` once its branch merges; alternative 1's cost falls on a user unit |
| **N6** | Q4, new, and S2-D15 |
| **N7** | S2-D5: the rejected no-Bash alternative is a bounded export of the evidence blobs; a plan-time check of agent frontmatter |
| **N8** | S2-D1: the row with no reader is dropped |
| **N9** | S2-D1: the reach tests' path set is a parameter |
| **I11** (review 1, residual) | S2-D5: accepted as review 2 says, with the plan-time check |
| **I13** (review 1) | S2-D9, unchanged |
| Review 2 §2's older gap | *to-fix*: BASE-MOVED-STALE |

## Revision 2 — where review 1's findings are settled

**Critical and Important.**

| Finding | Where it is settled |
|---|---|
| **C1** | S2-D2: `moved` gains an opt-in `--own-moves`, which `/docs-write` does not pass (S2-D14) |
| **I1** | S2-D5: the ancestor read is dropped; the ARD is read at `<default-ref>` alone, and BKR invariant 5 stands. The old question 4 goes with it |
| **I2** | GIT-G1 edit 4 |
| **I3** | S2-D6, posed as Q1 and Q3: the FH exclusion and the uncommitted kept walk are gone, and the P-D8 reasoning is replaced |
| **I4** | Q1; S2-D3, the claim set; S2-D5 |
| **I5** | S2-D6 and Q3 |
| **I6** | S2-D7 |
| **I7** | S2-D8, the frontmatter program; S2-D7, the title |
| **I8** | S2-D3 and S2-D7 |
| **I9**, **I10** | S2-D4 |
| **I11** | S2-D3, S2-D5 and S2-D11 |
| **I12** | S2-D1 and Q2 |
| **I13** | S2-D9 |

**Minor.**

| Finding | Where it is settled |
|---|---|
| **m1**, **m3** | S2-D3 |
| **m2** | S2-D7 |
| **m4** | S2-D5 |
| **m5**, **m9**, **m10** | S2-D4 |
| **m6** | S2-D8 |
| **m7** | S2-D2 |
| **m8** | S2-D14 |
| **m11** | S2-D10 |
| **m12** | *Files touched* |

Revision 1's Q1 is now decision S2-D10. The batching is S2-D15. The questions follow the review's ranking.

## Intent

Route step 6, verifying a drafted page's claims, is still done by hand (ROUTE:179-214). It ends: "*Later: `/docs-verify` is planned … No such command exists yet.*" (ROUTE:216).

Every page `/docs-write` drafts carries the page-level marker until a verification removes it (EC:63). So a backlog run's page sits at `drafted`, and the grid does not move for it (BF:116; the parent's *Risks*, :200).

This document designs `/docs-verify` to P-D11's contract:

- one `drafted` unit per run;
- its claims resolved by its audience's method: a person's walk, or a code reading;
- the unit moved to `verified` in the commit that holds the resolved page.

## What ships today

**The contract.** P-D11 (:128-135) sets the selectors, the two backends, `--prepare` and its stamp, `doc-writer` as the applier, what `verified` asserts, and bounded questions. P-D8 (:104) places the move in "the commit holding … the resolved page and the walk's results". P-D9 (:113) and P-D12 (:139) set the image rules. P-D13 (:151) sets who sees what.

**What sub-project 1 left for this command.** UB reserves `answers`, `BLOCKED` (UB:53, :71, :107). FH §6 is written for "a run of `/docs-workflows:docs-write`" (FH:151); its message, created paths and push condition are `/docs-write`'s (FH:177, :182, :197). BL `edit` writes `status`, and `page_path` where unset, nothing else, and requires `--status` (BL:44-48, :906-931, :1039). BL `moved` compares a ref's status with the working status (BL:38-40). GL §9's Phase column is `/docs-write`'s (GL:177). Two DW programs find the page-level marker (DW:110-116, :383-393) by a phrase BL's self-test pins (BKR:25).

**What nothing does yet:** compose a walkthrough (EC:101); render the checklist and write results back (EC:107); read a claim at two commits, since `code-scanner` "does not accept a branch override" (CS:142); remove the page-level marker (EC:63).

The walkthrough is YAML that EC §4 freezes (EC:67-101). It is read only with the Read tool, as data (DW:148, UB:43), and "no YAML parser ships with the plugin's scripts" (P-D8 :102; BF:65).

## Goals, non-goals, anti-goals

**Goals.**

1. `/docs-verify <unit-id>|--next` takes one `drafted` unit to `verified` by its audience's method (EC:19-26), in one commit with the resolved page.
2. A user walk can run outside the session, bound to the page by P-D11's stamp.
3. A hand-written walkthrough that misses claims is extended, never rewritten.
4. Every unit that cannot reach `verified` has a defined exit (Q1).
5. `/docs-write`, `/document`, `/docs-audit` and the agents behave as before, save for what S2-D14 names.
6. Four GIT-G1 truth edits, and no new behaviour.

**Non-goals.**

- `/docs-capture` and `captured`.
- Every `stale` edge, and `verified → drafted` (S2-D13).
- `verified → published` (BF:111, :125).
- A browser driver (EC:129).
- `--batch` (P-D11).
- `release` units (P-D14).
- Any change to `/document`'s command file.
- A `schema_version` bump.
- A pull request opened by the plugin.
- An attestation outcome (Q1's rejected alternative).

**Anti-goals.**

- A page edited by a run that does not move its unit (Q1).
- A marker removed for any reason but a resolved claim (EC:136).
- A user claim resolved by code, or an engineering claim by observation (EC:137).
- Answers taken without a stamp naming the page as it stands, or without the question that shows them and names their source (P-D11).
- A specs-versus-code winner picked without a person (SRC:292).
- A walk lost to a later failure.
- A specs document read anywhere but at `<default-ref>` (P-D14; PH:628).
- A value from a walkthrough, an answer, a page or the profile reaching a path, a ref or a command before its class test (P-D13).

## Decisions

### S2-D1. The phases; what is shared by citation

Signature: `/docs-verify <unit-id>|--next [--prepare] [--docs-repo <path>] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]`.

- **0. Resolve.** DW Phase 0 steps 1–12 (DW:71-116), with these changes:
  - no `--batch`;
  - `--prepare` is a bare flag;
  - the toolchain preflight is read against GL §10;
  - the profile's `images` block is held to S2-D4's classes.

  Then routing (S2-D12).
- **1. Select** (S2-D2).
- **2. Resolve the evidence.**
  - For a user unit: the walkthrough file, its stamp and its results, through S2-D10's reader.
  - For an engineering unit: the page's own `evidence:`, held to S2-D11's classes and resolved by DW's *Sources* (DW:162-168).
- **3. Consent.** The question names:
  - the unit, the page and the backend;
  - for a user unit:
    - the walkthrough, which is named, found at the fixed-id path (S2-D3), or to be composed;
    - one Opus `walkthrough-composer` dispatch;
    - any recorded answers, and whether they bind the page;
    - any hand-recorded results a walk would clear (m5);
    - the slots, and the `images` values;
  - for an engineering unit: each clone (flagged where only this answer admits it), and each artifact;
  - the branch;
  - every profile command, verbatim (DW:193).

  The choices are `["Verify it (Recommended)", "Cancel"]`; under `--prepare`, `["Prepare it (Recommended)", "Cancel"]`.
- **4. Branch.** FH §6.2, then DW:217-223's re-check: the entry, the page's blob, the walkthrough reader's output, and the profile with its `images` block, all as the consent showed them.
- **5. Walk or read** (S2-D3 to S2-D5), ending at S2-D6's move test. A failed move test, an unfinished walk, and `--prepare` each commit here (S2-D6), then go to Phase 11.
- **6. Apply.**
  1. Images are placed.
  2. `doc-writer` runs with `answers` (S2-D7), under DW's first two reach tests (DW:265). S2-D8's frontmatter program replaces the third.
  3. The page-level marker is removed (S2-D8).
- **7. Style.** The command's own phase, on DW Phase 6's pattern (DW:296-324).
- **8. Build.** The command's own phase, on DW Phase 7's pattern (DW:330-336). It runs builds only: `title` never changes (S2-D7), and there is no placement target.
- **9. Review.** The command's own phase, on DW Phase 8's pattern (DW:342-377). It uses S2-D7's apply brief and fix routing, one fix cycle and one re-review. Its escalation list's *Defer* says the unit does not move and the walk is recorded.
- **10. Commit** (S2-D8).
- **11. Finish.** FH §6.5–§6.6.
- **12–15.** The report, then the tail: feedback, follow-ups, cost (`documenting`/`dev`, fixed, as DW:528), the resume pointer, and `commit-artifacts` last.

**Ending early.** Five ends take no tail, as DW:20's do: an unknown flag, a bad selector, a run-flag stop, *Cancel* at the ladder, and a target in no work tree. Each comes before the target is resolved, and the last keeps SRG:132's "Three runs' command bodies lead to that last case" true. Every later stop takes the stop route.

**Shared by citation (Q2, I12).** P-D4 rules out a second prose copy. The blocks that need no parameter but a stop prefix move out of DW into a new `references/docs-iteration/backlog-run.md`. Both commands cite it, and so will `/docs-capture`. The blocks are:

- the untrusted-input rules (DW:22), less their per-command who-sees-what sentence;
- the classes, the class and containment programs, and the `python3` rule (DW:24-63);
- *Sources* and the clone test (DW:162-168);
- *The base* (DW:160);
- *Copies* and the first two reach tests (DW:263-265);
- the two marker programs (DW:110-116, :383-393).

**Parameters.**
- Stop codes are written `<RUN>_…`, and each command names its prefix.
- Temp templates are written `<run>-XXXXXX`.
- "Phase 4's *Repo missing*" becomes "the scan phase's".
- The reach tests' set of paths a writing agent may change is the command's (N9): for `/docs-write`, "the unit's page and its placement targets"; for `/docs-verify`, the page alone.

**What stays in DW**: its unit tests, consent, Style, Build, Review and Commit phases, report and tail. `/docs-verify` writes its own Style, Build and Review, which are shorter, since it has no placement targets.

**What stays literal in each command body**, because a gate or recipe reads `plugins/*/commands/*.md`:

| Step | Read by |
|---|---|
| The core-references preamble | `check-docs.sh` check 16 |
| The load-by-part paragraph | `reference-parts.py check-citations` |
| **Load the question rules.** | `check-questions` |
| `strip-run-flags`, the `workflows-core:model-routing` call, the `workflows-core:impl-maintenance` dispatch | the `run-flags` and caller recipes (`.claude/rules/workflows-core.md`:30, :59) |
| `emit-cost` | check 8 |
| `args: "specs-repo-git commit-artifacts` | WCG:26's recipe |
| `scan-refresh` | `.claude/rules/docs-workflows.md`:73's recipe |

If DW's tail moved, `/docs-write` would leave WCG:26's count.

### S2-D2. Selection

Unit tests, in order. Under `<unit-id>` a failure stops the run with its line; under `--next` it passes the unit over, with that line as the reason (DW:140).

1. **The status is `drafted`.** Any other status is refused, and the refusal names it. A `missing` unit's line names, from `backlog-lines.py moved --id '<id>'` (without `--own-moves`), each ref where its status differs, in class, at most twenty. Where none does, it says no unmerged branch drafted it (m7).
2. **`blocked_by` is empty** (DW:143). This includes Q1's `claims-unresolved`.
3. **The surface is not `release`** (DW:145; P-D14).
4. **The type, audience and visibility are legal** (DW:146).
5. **The page.**
   - `page_path` passes the page-path test (DW:27).
   - The page is a regular file, not a link.
   - Its `unit:` equals the id, read as DW:144 reads it.
   - No other page carries the id (DW:144's grep).
   - It is **tracked and clean**: `git -C '<top>' status --porcelain -z -- ':(literal)<page path>'` prints nothing, and `ls-files --error-unmatch` succeeds. This is the command's own test, and FH §6.1 is unchanged.
6. **The backend's inputs.**
   - For a user unit: the entry has a `walkthrough:` line (BF:48), as DW:149 needs `page_path:`. A named walkthrough passes DW:148's admission and S2-D10's shape. An unnamed one takes S2-D3's fixed id.
   - For an engineering unit: the page's `evidence:` holds a code or artifact entry, each passing S2-D11 and *Sources*. `--prepare` is refused.

**`--next` (C1).** The candidates are units that are `drafted`, not blocked, not `release`, with an id in class, in priority and then file order (DW:154). Each takes tests 1–6. Then the unmerged-branch read is **`backlog-lines.py moved --own-moves`**.

`--own-moves` is new. With it, a ref moves a unit only where the ref itself changed the status: where its status differs from the working status **and** from its status at the ref's merge base with the base.

- The merge base's backlog is read by object id, within `moved`'s existing limits.
- A ref sharing no merge base counts as `moved` counts it today.
- An unreadable merge-base backlog makes the ref `unreadable`, which the consent discloses (P-D7).

Without the flag, an open draft branch still holding a candidate as `missing` passes over every legitimate unit, as the review reproduced. `/docs-write` does not pass the flag, so its output is byte-identical, and the self-test pins both modes (S2-D14).

Rejected: a reading of the branches in `/docs-verify` itself. It would be a second reader of the line shape, against BKR invariant 1.

### S2-D3. The walkthrough, and the composer

**Which file.**

- **A walkthrough the unit names** is used (EC:99).
- **An unnamed one** is composed at `.dev-workflows/walkthroughs/<unit-id>.yml`, so **its id is the unit id**. The id is fixed, not minted, so a later run finds the file before the backlog names it.
  - An existing file at that path is taken only where its `walkthrough.unit` is the id; the reader prints that value only in class. The consent then names it as a file found at the fixed-id path that the unit does not name (m3).
  - Otherwise the unit is refused, naming the file.

**Extension.** Every user run checks its file against the page: a composed file, a hand-written file, or a run that takes answers.

- Steps the composer adds are appended after the last `n`.
- No step is rewritten, renumbered, reordered or removed, and no `captures[]` entry is added.

**A composed file has no captures (m1).** A code-first page has no slot comment (UB:87), so it gets no image from this command. The parent's M3 note holds only where the unit named a walkthrough at drafting. Rejected: composing captures, which would add slot comments that no answer makes.

**Order in Phase 5.**

1. The composer runs after the branch step.
2. The operator sees the coverage counts (claims covered, steps appended, claims `uncoverable`) and every appended step.
3. An `uncoverable` claim takes Q1's exit before anything is written.
4. Nothing is written to the walkthrough until the walk starts (S2-D6).

**The agent is `walkthrough-composer`, new, in `docs-workflows`, on the §2 Opus chain** — MR:575's synthesis/planner row. It decides which observation settles each claim, and its coverage is what `verified` rests on. Its `model:` is passed as DW:134 passes `doc-writer`'s.

Rejected:

- `doc-writer` under a third brief kind — a page writer turned YAML writer, for an unrelated job.
- `doc-planner`, which is shaped for PRDs.

Its contract:

- **Tools: Read alone (I11)**, of its handoff file and the page. Without Glob or Grep, it cannot read product code and so resolve a user claim by code (EC:137). It writes nothing; the orchestrator writes through S2-D10.
- **Inputs:** `mode` (`compose` | `extend`); the page's path; the unit's id, title, type, audience and roles; and, in `extend`, the walkthrough's text.
- **The claim set (I4)** is every claim on the page — each statement of fact, marked or not; the page-level marker says none has been observed (EC:63).
  - Each claim is covered by a step in the closed vocabulary (EC:93) whose `expect` states it.
  - A claim no five-verb step expresses is returned `uncoverable`, with the reason (EC:93's "finding rather than a licence"). Rationale and design statements are in the set, and are `uncoverable`.
  - In `compose` it also proposes `role` (one of the unit's) and `preconditions`. The person names `environment` once, in plain text, on one line.
- **Return:** `status`; `steps` (all, or those appended); `coverage` — per claim, its quote and line, then its covering steps or `uncoverable: <why>`; notes.
  - **The coverage goes into the apply brief as data (I8)**, so the writer and the reviewer read one map. It is written to no file (EC:55).
- It carries the untrusted-content block (P-D13).

### S2-D4. The walk, the recorded answers and the images

**In session.** The run writes the stamp (S2-D9), clearing every result; the consent has named any hand-recorded results this erases (m5). Then it asks one question per step, in `n` order.

- The text gives the step's number, action, target and expect, each written as DW:22 writes free text.
- The array is P-D11's, in the form check 12 and `escalation-rules` §0 require (a label never promises text; reworded at batch 3's Task 3.3): `["confirmed", "differs (you'll be prompted for what you saw)", "blocked (you'll be prompted for why)"]`. Q3 asks for a fourth.
- `differs` asks for the observed text, and `blocked` for the reason. Each is plain text, required, and one line (EC:113, :115, :127), and is re-asked when empty or multi-line.
- A free-text answer naming one outcome is that outcome; any other is re-asked (CLAUDE.md, *choices*).
- **Each answer is written to the file as it is given** (S2-D10). Rejected: writing at the walk's end, which would lose a dying session's answers.

**Answers recorded in the file (batch 3).** These are answers a stopped or blocked walk left in the file, or a walker recorded after a prepare. They count only where the stamp is in shape, names `page_path`, and its blob equals the page's (S2-D9). Otherwise the consent says why (no stamp, another page, or another version), and the walk restamps the file.

Where they count, Phase 5 asks P-D11's question verbatim: `["Take these answers (Recommended)", "Walk it again here", "Cancel"]`. **Its text shows what *Take* admits (I9):**

- each `differs` step's observed text, and each `blocked` step's note, escaped as DW:22 writes free text;
- each step the composer appended;
- the counts;
- the source: the last commit that touched the file, or *uncommitted in your working tree*.

**The source (m9).** The commit is what `git -C '<top>' log -1 --format=… -- ':(literal).dev-workflows/walkthroughs/<id>.yml'` prints: its id, its author (free text) and its date. It is the last commit to touch the file, which may not be the one that wrote the results. P-D11's "the commit that last changed them" allows this, and the question says so.

**The three choices.**

- *Take* takes every result. It then walks in session each step with no result, each `blocked` step (which settles nothing), and each `differs` with no observed text.
- *Walk it again* restamps and walks all.
- *Cancel* takes the stop route.

**Uncommitted answers** dirty the tree, so FH §6.2's dirty-tree question asks about them, with its approved text. The consent says to choose *Proceed anyway*, or to commit them first. *Stash* hides them, and the Phase 4 re-check then stops the run, failing closed.

**`--prepare` (P-D11; batch 4).**

1. After the branch step, compose or extend the walkthrough.
2. Stamp it, clearing every result.
3. Commit (S2-D6).
4. Print the checklist — the stamp, preconditions, each step with its `expect`, each slot, all free text escaped — with the instruction to record results as EC:117-125 shows and run `/docs-verify <unit-id>`.
5. Then Phase 11, the report and the tail.

**Images** (P-D11: "each slot's screenshot taken here").

- **When.** For each slot in class whose comment the page carries, the run asks after the step a capture's `after_step` names in a walk, or, in a run that takes answers, once they are taken (N3). The question:
  - under `in-repo`, the run asks `["I have it (you'll be prompted for the file's path)", "Skip — the slot keeps its placeholder"]`;
  - under `object-store` and `cdn`, where the person uploads (docs-profile-schema.md:136-138), it asks the same for a URL.
- **The profile's values (I10)**, held at Phase 0, shown in the consent, and equal at Phase 4's re-check. A failure stops the run, naming the field.
  - `images.policy` is one of the three.
  - `images.root` passes `rel-path` and the containment test against `<top>`, printing `inside`.
  - `images.max_bytes` is digits.
  - Each prefix passes the URL class below.
- **The person's values.** A failure is refused, never printed, and re-asked.
  - A path passes `abs-path`, is a regular file by `lstat`, is within `images.max_bytes`, and has an image extension.
  - A URL starts with `https://`. It holds no whitespace, no control character, and none of `(`, `)`, `<`, `>`, `"`, `'` or a backtick (m10). It starts with `images.public_prefix`, or with `images.internal_prefix` for an internal unit's `object-store` image.
- **Placement.** The orchestrator copies an `in-repo` image:
  - for a public page, to `<images.root>/<unit-id>/<slot>.<ext>`;
  - for an internal page, to `<content root>/internal/assets/<unit-id>/<slot>.<ext>`, inside the internal tree (ROUTE:175; `visibility.md` §1).

  The name comes from the slot, never the source file (P-D13), one path per slot. An overwritten file is an edited path; a new one is a created path. `object-store` and `cdn` commit nothing (P-D9).
- **The reference.** `doc-writer` writes it on the line after the slot comment, which stays. Rejected: `doc-writer` copying images (WRT:52-53).
- **Unfilled slots.** An unfilled slot does not block the move, and the report names it.
- **The fitness question.** P-D12's question runs once, after the walk and before any apply, over every image by path, with nothing recommended: `["They show nothing that must not be published", "Cancel — nothing is published, and the walk is recorded"]`.

**Never automated:**

- taking a step;
- seeing a screen;
- the observed text;
- why a step is blocked;
- taking or uploading a screenshot;
- judging an image fit;
- taking answers recorded elsewhere;
- naming the environment;
- the answer for an unexpressible claim, or for a specs-versus-code claim (Q1).

### S2-D5. The engineering backend and the claim reader

**Today's commit** is read as DW Phase 4 reads it (DW:236-257). There is one `code-scanner` per clone the page's code entries resolve to, under `scan-refresh`'s fixed policy. Its themes are the unit's and the surface's titles, and its `search_hints.paths` are the entries' paths. `prep.scanned_ref`, resolved to a commit (DW:257), is that repository's **today**.

It is reused for its handling of dirty trees, read-only mounts and the session's own repository, and its map goes to the reader as hints. Each clone passes both parts of the clone test, and admission, before any dispatch names it (DW:167-168).

**Artifacts (I1).** Each ARD is read by the orchestrator at `<default-ref>` alone, by commit, as DW:231 reads one. That holds P-D14, the answer to parent question 3, PH:628, and BKR invariant 5, which stands.

- The entry's own `ref` is never read. EC §2's "at that ref" (EC:38) is the half a backlog run does not make, and the report says per entry "not read at the recorded ref: an ARD is read at the default branch alone".
- **When the ARD at `<default-ref>` may differ from the one at the entry's `ref`**, the run cannot tell, since it reads no other commit, so it fails closed:
  - each claim the ARD grounds is graded against today's text alone, never confirmed on the strength of the recorded ref;
  - a claim today's text states is `confirmed`;
  - a claim it states otherwise, in one phrasing, is `differs`;
  - anything else is `unresolvable`, and an ARD gone at today is an evidence path gone;
  - the entry's `ref` advances to today only in the verify commit.

**The agent is `claim-reader`, new, in `docs-workflows`, on the §2 Opus chain.** Its reading is SRC §4.2's verification, which `doc-planner` runs at Opus (MR:575), and here it is what `verified` asserts. `doc-reviewer` spot-checks only three to five claims (REV:64).

Rejected:

- `code-scanner`, which classifies themes (CS:82-86) and reads only present-day code (CS:142).
- `doc-reviewer`, which grades the edits that apply the readings — one agent reading and grading would be a command certifying its own prose.

Its contract:

- **Tools: Read and Bash.**
  - It reads only through ROR §4's ref primitives (`git grep`, `ls-tree`, `show` at a commit), as `git -c safe.bareRepository=explicit -C '<clone>'`, every value single-quoted, never the working tree.
  - Page text reaches git only through a pattern file (`grep -F -f`) under `run-flags` §7's TMPDIR.
  - A commit the clone lacks is *not read*.
  - **The read-only rule is held by the prompt (I11)**: the named residual, which `code-scanner` and the family's other Bash-holding agents carry (CS:139-142).
  - *Assumption*: an agent's `tools:` names tools and takes no command pattern. All 45 lists in the family are bare names, with no pattern and no `disallowedTools`.
  - **Plan-time check.** Does agent frontmatter accept a tool pattern, or `disallowedTools`? Verify it with `claude plugin validate`. If it does, `claim-reader` takes one that admits only `git` read commands.
  - Rejected: **no Bash**, with the orchestrator writing the blobs the evidence entries name, by object id, as regular files, at both commits. That export is bounded and carries no symbolic links. Its real cost is that the reader could not follow a claim to a file the evidence does not name — which is where SRC §3's techniques look: schemas, constants, UI strings and tests (SRC:151-204) (N7).
- **Inputs:** the page's path; the unit; per clone `{repo, path, today, evidence refs}`; the code entries after S2-D11's classes; per artifact `{path, today_ref, text_today}`; and the scanner returns.
- **Grading,** by SRC §3's techniques (SRC:126-222), mapped from SRC:250-261:
  - **`confirmed`** — today's source states the claim (VERIFIED).
  - **`differs`** — today's source states something else, in one phrasing, returned as `observed` (CONTRADICTED). Code is the truth an engineering page answers to (EC:23, :26).
  - **`unresolvable`** — nothing at today settles the claim (NOT_FOUND); phrasings disagree (AMBIGUOUS); code cannot settle it; or its evidence path is gone at today.
  - **`specs-vs-code`** — a specs document and the code disagree. SRC:292 forbids picking a winner, so the claim goes to Q1's bounded question.
  - The read at a code entry's evidence `ref` is reported beside each claim (held, differed, absent, or not read). It decides nothing.
- **An ARD-only claim (m4).** A claim only an ARD grounds, as on a `decision` page, is confirmed by reading that document at today. `verified` then asserts a document read: EC §2's re-check for an `artifact` (EC:38), a precision of P-D11's "code read", not a departure.
- **Return:** per claim, its quote, line, outcome and source (repo or artifact, path, lines, commit); `observed` and `why` where they apply; the ref read; and each entry whose path is gone.

**The readings question.** Where the move test passes, the run asks once: `["Apply these readings (Recommended)", "Cancel"]`. The text names each `differs` with the code's phrasing and location, and counts the rest. A person turns a reading into an edit (SRC:12-13).

**Note, 2026-11-18 — `claim-reader`'s tools, by the maintainer's answer to plan review 1's QP3 (*Export, no shell*).** The approved text above stands; this note records the departure from it that the maintainer approved.
- **Tools.** `claim-reader` takes `tools: ["Read", "Grep", "Glob"]` and no Bash. Its contract's *Tools: Read and Bash*, its ROR §4 primitives and its pattern file are replaced: the agent runs no command, so neither the page's text nor a repository's file names reach a shell, and its read-only rule is held by its tools rather than its prompt (the residual I11 named is gone for this agent). It reads only under the export directory it is handed.
- **The export.** The command writes the commits the reader reads into a scratch directory under `workflows-core:run-flags` §7, by one fixed program, `backlog-lines.py export`: each admitted clone's whole tree at today's commit, and the evidence paths at each recorded `ref` where this design reads at it. The program takes only class-tested refs and paths, single-quoted; runs git as an argument list with `-c safe.bareRepository=explicit`; writes regular files only, following and creating no symbolic link; and skips links, submodules, names outside class and files above 1 MiB, counting each. Above 50,000 files or 512 MiB the repository is *not read* and its claims stay marked. Today's whole tree is there, so the reader can still follow a claim to a file the evidence does not name — the cost *Rejected: no Bash* named does not arise.
- **The return.** A reading's source is the export path the reader read; the command maps it back to the repository-relative path through the export's own file list, a known set, and tests `path` and `lines` by class before either becomes an `evidence:` entry.
- **Where it is built:** the plan's R19, R27, R29 and R30 and its Task 2.1 (`docs/superpowers/plans/2026-11-17-doc-d-g1-docs-verify.md`, revision 2).

### S2-D6. The move test, the commits, and the walk recorded

**The move test.** It is deterministic, and it runs before any apply.

- **User units:** every step is answered; none is `blocked`; every `differs` has its observed text (S2-D10's counts); and no claim is `uncoverable`.
- **Engineering units:** nothing is `unresolvable`; no evidence path is gone; and every `specs-vs-code` claim is answered "as the code reads" (Q1).

**Which failures take Q1's exit (N2).** Q1's exit, and `edit --block`, apply only to Q1's three cases:
- an `uncoverable` claim;
- an `unresolvable` reading;
- a `specs-vs-code` claim left undecided.

Any other failure — a `blocked` step, an unanswered step, a `differs` without observed text, or a stopped walk — makes the record commit with **no token**. The unit stays resumable: the next run takes the answers and walks those steps in session (S2-D4).

**Three commits.** Each is one commit, by FH §6.3, on the run's branch.

| Commit | Holds | Status |
|---|---|---|
| **verify** | the page; each image; the walkthrough with its results, where this run changed it; the backlog's move | moved — P-D8's commit |
| **prepare** | the walkthrough, stamped, with no results; a composed file's id in the backlog | no move (P-D11) |
| **record** (Q3) | the walkthrough with its stamp and results; a composed file's id; and the token, for Q1's three cases only | no move |

An engineering unit's Q1 exit commits the token alone.

**Every unfinished walk makes the record commit (Q3; I3, I5).** From the first write to the walkthrough (a composed file, an appended step, or the stamp), every end other than the verify commit records:

- a failed move test;
- *Stop*;
- a failed build;
- a review that stayed blocked;
- the fitness *Cancel*;
- a refused verify commit;
- any later stop.

FH §6.4 first runs over every other path. The walkthrough is never in its lists. Then the record commit runs, against the restored backlog: `edit --from drafted --status drafted [--walkthrough] [--block]`.

A hook that refuses the record commit leaves the walkthrough dirty, and the report says so. The next run's FH §6.1 and §6.2, with their approved text, make a person commit it or proceed. **FH §6.1 and §6.2 gain no exclusion**, and nothing is kept uncommitted by design.

**P-D8, read soundly.** "The commit holding … the walk's results" is met by the verify commit's **tree**, which always holds the walkthrough with its results:

- from this commit, after a walk in session;
- from an earlier commit, when the answers were taken from the file.

Revision 1 read P-D8 as the commit's own diff. P-D11's own flow breaks that reading, so it is withdrawn. A success makes one commit rather than a record followed by a verify, for a shorter history. P-D8 does not require it.

### S2-D7. Applying the answers: `unit-brief.md` and the two agents

UB stops reserving `answers` (UB:53). A brief carrying `answers` as a top-level field is an **apply brief**. Neither agent's pointer paragraph changes (WRT:9, REV:10). Rejected: a new `brief_kind: verify`, which would add a second pointer to each agent, where P-D4 keeps every difference in UB.

**The apply brief** is UB §2's brief, with these changes:

- `write_targets` is `[{kind: extend-existing, path: <page>}]` alone.
- `evidence` is **advanced**:
  - engineering: code `ref`s become today's commit, artifact `ref`s become the specs commit read, and a source a reading names is added;
  - user: the code entries are unchanged, and `{kind: walkthrough, id}` is added.
- `review_by` becomes the run's date plus UB:44's interval.
- `walkthrough` carries the file's text (user units).

It also carries new fields:

- `answers`: `{backend, source, steps: [{n, outcome}] | readings: [...], images: [{slot, ref}]}`;
- `coverage` (S2-D3);
- `page_before`, the copy taken before the dispatch;
- `review_findings`, on a repair dispatch only;
- for the reviewer, UB §4.1's fields plus `fixer_reports`: the style and build cycles' Fix Reports.

**`doc-writer`.** UB gains §3.4. UB §1's three entries for the writer each take §3.4's text where `answers` is present (m2).

- **Inputs**: the apply brief's fields.
- **Entry validation**: the page exists and is the only target; it carries `unit:` equal to the id and the page-level marker; and every step or reading has an outcome. Otherwise the writer returns `BLOCKED`.
- **Write mechanics, step 2**: only `evidence:` and `review_by` change. **`title` never changes (I7):** it is the unit's name, composed from the unit's `title` at drafting, and is not a claim. No `changelog:` is written.
- **Step 4**: no snippets, as in §3.3.
- **Step 5**: each `images` entry is referenced on the line after its slot comment, with alt text from `shows`.
- **Step 7**, per claim, read through `coverage` or the readings:
  - **confirmed**: the marker is removed, and the words are kept;
  - **differs**: the claim is rewritten to say what was observed or read, and nothing more, and its marker is removed;
  - **blocked, unresolvable or unanswered**: the claim stays marked. This is a defence; the move test keeps the run off this path.
- **Rules for every step**:
  - Answer text reaches the page **as words**: markup, links, HTML, includes and tokens are written as literal text.
  - **The writer never removes the page-level marker.**
  - **On a repair dispatch (I6)**, given `review_findings`, it reworks only the claims those findings name.

**`doc-reviewer`.** UB gains §4.6, and UB §1 gains one row for this brief only: *Source-code accuracy*.

- **Inputs**: it refuses without `answers` and `page_before`.
- **Method, step 2**: it reads the page against `page_before`, the answers, `coverage` and `fixer_reports`, testing P-D11's "each edit says what was answered and nothing more".
- **Factual correctness (I6).** Each change from `page_before` must be one of:
  - a marker removed from a claim an answer confirms;
  - a claim rewritten to an answer's text;
  - an image reference at a slot;
  - `evidence:` or `review_by`;
  - an edit a Fix Report in `fixer_reports` names, bounded to the wording of the sentence its finding cites, adding or removing no claim.

  Any other change is a BLOCKER, and so is each of: a claim no answer covers left unmarked; a `differs` not applied; markup an answer brought in; and any marker left on the page.
- **Completeness vs plan**: every answer is applied.
- **Coverage**: `N/A — graded at drafting`.
- **YAML frontmatter**: `unit:` equals the id; `type`, `audience`, `visibility` and `title` are as in `page_before`; `evidence:` and `review_by` are the brief's.
- **Screenshots**: each `images` entry is at its slot, and nothing more.
- **Source-code accuracy**: `N/A` on a user page (EC:137); the row stands on an engineering page.
- **Verification-gate integrity**: against GL §10.
- **Next step**: names `/docs-verify`'s phases.

**Fix routing (I6).** Phase 9's one fix cycle sends each surviving finding about an answer's application to **`doc-writer`**, re-dispatched once under the same brief with those findings as `review_findings`. Every other survivor goes to `doc-fixer`. Then the one re-review runs.

If the review stays blocked, the escalation list's *Manual fix notes* go through the agent the finding belongs to. `doc-fixer` is never handed answers (P-D11; `doc-fixer.md:26`). UB's *Phase numbers* (UB:29) become per command.

### S2-D8. The move and its commit

1. **The page-level marker.** At the end of Phase 6, after `DONE` and the reach tests, a program does three things:
   - it confirms that the first body line is EC §3's marker, byte for byte, as DW:383-393 reads it;
   - it confirms that no other `[NEEDS CLARIFICATION:` stands outside fenced code;
   - it deletes that line and the blank line after it.

   Failing either test ends the unit. Every gate thus sees the committed page, and BL's self-test pins the phrase with DW's two (BKR:25).

   Rejected: removing the marker after the review, where no gate would see the committed page; and letting `doc-writer` remove it, since it would also do so on runs that fail.
2. **The frontmatter program (I7)** runs after every writing dispatch, and again at Phase 10. It exits 1, ending the unit, unless all of these hold:
   - the page is a regular file, not a link;
   - its frontmatter equals `page_before`'s once the `evidence:` key (with its more-indented lines) and the `review_by:` line are dropped from both;
   - on an internal page, the visibility marker is still the first line after the frontmatter.

   It replaces DW's third reach test, which compares a placement target and cannot apply here. No *Override* passes it.
3. **Phase 10.** Both programs pass, the backlog is copied, and then `backlog-lines.py edit --id '<id>' --from drafted --status verified` runs, with `--walkthrough '<id>'` for a composed file.
4. **BL `edit` gains three flags (batch 1)**, each with its docstring line and self-test cases:
   - **`--from <status>`** refuses an entry whose status is not that, with exit 3, `status-differs`. A walk takes time, and BL:50-53 narrows only the script's own read.
   - **`--walkthrough <id>`** sets the line where it is unset (`null`, `~` or empty). It refuses `walkthrough-set` where the line names another walkthrough, and `no-walkthrough` where the line is absent, as `--page-path` does (BL:45-48).
   - **`--block <token>`** sets `blocked_by:` to `[<token>]` where it is `[]` or empty, and otherwise refuses with `blocked` (Q1).

   `/docs-write` passes none of the three.
5. **One commit, by FH §6.3**: `docs: verify <unit-id> (<type>, <audience>)`. Prepare and record take the same form with their own verbs.
6. **The finish.** FH §6.5's push offer, once; FH §6.6's draft, printed; **no pull request** (FH:207, BKR:28).
7. **Cutting a branch (m6).** FH:161's question usually continues the drafting branch. *Cut a new branch from `<base>`* fails closed in two cases, which the question's text names:
   - the unit is `missing` on `<base>`, so the re-check stops with `UNIT_CHANGED`;
   - a modified tracked walkthrough refuses §6.2 step 4's switch, so the run ends as *Cancel* does.

**FH §6, generalised.** Each change still reads as before for `/docs-write`.

- §6's opening (FH:151) names `/docs-verify`.
- §6.3's "once the page carries its `unit:` line" becomes "once its command's writes for the unit are made". Its verb is the command's: `draft` for `/docs-write`.
- §6.4's path examples gain the page, the images and the walkthrough.
- §6.5's "committed a unit" becomes "made a commit".
- §6.6 gains, for `/docs-verify`: the backend, the source, the counts or readings, the images, and any record or prepare commit.
- **§6.1 and §6.2 keep their text.**

WHY-UNDO-COPY: `/docs-verify` quotes no stderr line, and cites §6.4 as DW:401 does.

**What `verified` asserts** is P-D11's (:134), unchanged:

- no marker remains;
- nothing is blocked or unresolved;
- the evidence advanced to what the run read;
- each claim was observed as the walkthrough names, read in code at the commit recorded, or, for an ARD-only claim, read in the ARD at today (m4).

One precision: answers taken from a commit or the working tree assert that the operator took them behind a question naming their source, not that the named author walked. The sweep qualifies BF:120's "a human's assertion" and BF:129's sentence by who removed the marker (MARKER-ASSERTION).

### S2-D9. The stamp

A top-level mapping, directly after the `walkthrough:` block:

```yaml
stamp:
  page: docs/guides/place-an-order.md
  blob: 3f6c2a7e0d4b5c1f8a9e2b7d6c5a4f3e2d1c0b9a
  at: "2026-11-17T14:03:09Z"
```

**`page`** is the unit's `page_path`, in `PAGE_PATH` (DW:27).

**`blob`** is in `OBJECT_ID` (DW:29). **One computation, named once, serves both the write and the test (I13):** `git -C '<top>' hash-object --path='<page path>' -- './<page path>'`, the computation P-D11 names.

- It applies the repository's clean filters and line-ending settings, as `/implement` does (`plugins/dev-workflows/commands/implement.md:54`), and does not consult the index.
- So its value is **not** always the blob at `HEAD`. The review reproduced a CRLF page committed before `* text=auto`, `core.autocrlf=true` or `input`: the page is clean, yet the two differ. Revision 1's equality sentence is withdrawn.
- Equality still holds wherever both sides compute it the same way: the same commit and committed `.gitattributes`.
- Where settings differ between the two runs (another machine's `core.autocrlf`, or a filter configured since), the values differ and the answers do not count. This fails closed, reported as "another version of the page, or line-ending or filter settings changed".
- A configured `clean` filter runs with `git status`'s trust: it comes from git config, not from committed data.
- Rejected: `rev-parse 'HEAD:./<path>'` on both sides. It is config-independent, but departs from P-D11's named computation.

**`at`** is `date -u +%Y-%m-%dT%H:%M:%SZ`, pasted and double-quoted. It is never tested, since a clock is no evidence (SRC:596-602).

The mapping has one key and three lines, in this order, at a two-space indent. The writer writes nothing else, and the reader accepts nothing else.

**Writing and testing.** The stamp is written only by a prepare and at the start of a walk in session, and each write clears every `result:` (P-D11). A later run tests that:

- the stamp is in shape, and there is exactly one;
- `page` equals `page_path`, whole;
- `blob` equals the named computation now.

On any failure the results do not count, and the run reports why.

**EC gains the stamp.** EC §4 gains the key, its form, and a note that a driver reading `steps[]` ignores it. EC §5 gains three rules:

- `/docs-verify` takes results only behind a stamp naming the page as it stands;
- a person verifying by hand (ROUTE step 6) writes no stamp: results in a walkthrough that carries none do not count, and results added by hand behind a stamp that still names the page as it stands count as any other recorded results, shown by P-D11's question, since a stamp proves no walk;
- `/docs-capture` writes no stamp and keeps its results out of any walkthrough whose stamp would count them, so they never count.

**What the stamp never authenticates**: who walked; that anybody walked; the environment; when; or the steps. Any committer can write a matching stamp, and P-D11's question is the control.

Rejected: a digest of the steps, since P-D11 binds answers to the page; and a stamp nested in `walkthrough:`, which a driver ignores anyway.

**Note, 2026-11-28 — the stamp and its test as built (`docs-workflows` 1.46.0 and 1.47.0).** The approved text above stands; this note records how the stamp is written and tested at the close of batch 4, and each place where the built thing departs from that text, with the ruling behind it.
- **One computation (the plan's R13).** *The page's blob* is computed in `/docs-verify`'s body alone, `git -C '<top>' hash-object --path='<page path>' -- './<page path>'` held to `OBJECT_ID` (`commands/docs-verify.md` *Classes and tests*). The run takes it at Phase 1 for the unit it takes (at Phase 2 for a `--next` candidate not yet taken), compares it at Phase 4's re-check and on the walk's copy of the page (*The walk* step 1), hands it to `walk-stamp --blob` (*The walk* step 5), and compares it in the stamp test with the `stamp.blob` that `walk-check` printed. `backlog-lines.py` never hashes the page: it writes and reads the values it is handed.
- **The write.** `walk-stamp` removes any `stamp:` block and every step's `result:` with the lines under it. It writes `stamp:`, `  page:`, `  blob:` and `  at: "…"` directly after the `walkthrough:` block's last line that is neither blank nor a comment, in the file's line ending, and prints the steps it cleared. `--at` is `command date -u +%Y-%m-%dT%H:%M:%SZ`, held to `STAMP_AT` by the walk's class test before the verb runs and again by the verb's own argument test. A walk writes the stamp at *The walk* step 5 unless *Take these answers* was chosen, and *Walk it again here* restamps. A prepare writes it always (*The prepare* step 1).
- **The read.** `walk-check` prints `stamp.state`: `none`; `ok`, with `page` and `blob`, where the block is in its one form; or `out`, with one of `STAMP_REASONS` — `form`; `keys`; `page`, not a plain scalar in `PAGE_PATH` or above 4,096 bytes; `blob`, not a plain `OBJECT_ID`; `at`, not a double-quoted `STAMP_AT`. A stamp out of its form never puts the file out of shape (`evidence-contract.md` §4).
- **The test** (`commands/docs-verify.md` Phase 2, *A user unit*). Phase 2 holds the answer and the blob from Phase 1 test 6's read. The test passes where `stamp.state` is `ok`, its `page` equals `page_path` whole, as text, and its `blob` equals *The page's blob*. Passing, the results the file holds are *recorded answers that count*, which *The walk* step 4 asks whether to take — save in a prepare, whose stamp clears them. Failing, they are *results a walk would clear*, for the reason held with them: no stamp, a stamp out of its form with its reason, a stamp naming another page, or "another version of the page, or line-ending or filter settings changed".
- **Measured at batch 4's close** (`walk-check` on `evidence-contract.md` §4's example, in a scratch repository): the stamp after `walkthrough:` and the stamp appended at the end each read `ok`; keys swapped read `out` `keys`; `blob: HEAD` reads `out` `blob`; `at: "yesterday"` reads `out` `at`; and two stamps put the file out of shape, `duplicate-key`, at the second.

Where the built thing departs from the approved text:
- **"Directly after the `walkthrough:` block" binds the writer only.** The reader takes one top-level `stamp:` wherever it stands, since its position is no part of its form. This follows the plan's Task 3.1 interface, whose case `walk_stamp_replaces` reads a stamp standing after `steps:`, and the Task 3.1 review's M4 rewrote `evidence-contract.md` §4's stamp paragraph so that it no longer implies position is form.
- **"Exactly one" is held by the file's shape, not by the stamp test.** A second `stamp:` is a top-level key given twice (`duplicate-key`). The whole walkthrough is then out of shape, and Phase 1 test 6 refuses the unit (`DOCS_VERIFY_WALKTHROUGH_SHAPE`, or passed over under `--next`), where the approved text has the results simply not count. The ruling is the plan's R20 and its Task 3.1 shape: each top-level key at most once.
- **`at` "is never tested".** Its value is never compared, and its time is never checked, so a clock is still no evidence. Its form is held, though — double-quoted and in `STAMP_AT` — by `walk-stamp`'s argument test, by the command before the verb, and by the reader, for which an `at` outside it puts the stamp `out` (the plan's Task 3.1: "`at` a double-quoted `STAMP_AT`").
- **`page` is held to `PAGE_PATH` and to at most 4,096 bytes**, so that `walk-check` never prints an unbounded value (the Task 3.1 review's M2).
- **The second and third rules of `evidence-contract.md` §5** stand above as batch 3 truth-edited them: results added by hand behind a stamp that still names the page as it stands count (`83b4469b4`, the Task 3.4 review's I1), and `/docs-capture` keeps its results out of any walkthrough whose stamp would count them (`14158fb14`, that review's re-review N2). Batch 4 adds *Recording results by hand for a later run* to §5: the prepare's checklist, the one-line `result:` forms, and the stamp and the page left as they stand.
- **A prepare's stamp is observed in its commit before the checklist names it.** The checklist gives the stamp's `page` and `blob` as the walk's check printed them, with the time handed to `walk-stamp`. Before it is printed, *the `prepare` commit's hold after it* (`commands/docs-verify.md` *The walkthrough, held*) reads three blobs and a commit: the walkthrough's bytes, the blob git would store from them, the blob the commit HEAD stands on holds at that path, and that commit's short id. It holds where the first is the run's last blob and the third equals the first or the second, so a walkthrough committed with CRLF line endings under `core.autocrlf` or `text=auto` holds. Where it does not hold, the run stops with `DOCS_VERIFY_WALK_WRITE` in its third form, runs no §6.4, since the unit's paths stand committed, and prints no checklist. The approved prepare (S2-D4, steps 1 to 5) has no such hold. The rulings are the Task 4.1 review's M13 (hardening, taken), its re-review 1's N1 (the CRLF rule, reproduced under `true`, `input` and `text=auto`), and its re-review 2's N6.
- **What the stamp never authenticates** is unchanged. *Take these answers* names the last commit to touch the walkthrough and its author, and stays the control: batch 4's close traced a prepare, another author's committed answers and the run that took them.

### S2-D10. Reading and writing the walkthrough

**Decided**, moving revision 1's Q1 here by ruling: **BL gains walkthrough verbs**, staying the one implementer of BF §1's line grammar (BF:65-68). The walkthrough's structure is a new EC §4 paragraph, which the self-test reads as it reads BF §1's.

- **`walk-check`** prints counts and in-class values only, never text (BL:71-73): the unit id, the step numbers, the stamp's `page` and `blob`, the steps per outcome, each `differs` without observed text, and the slots.
- **`walk-stamp`** writes the stamp and clears every result.
- **`walk-record`** writes one step's result from a JSON file the run writes, as a double-quoted, escaped scalar on one line.
- **`walk-append`** and **`walk-new`** write the composer's steps in a canonical form that is in shape.

Each verb keeps every byte it does not write, writes atomically and reads the write back, and follows BL's exits and the caller's rule (BL:78-99). A hand-written file that is out of shape stops the run, naming the line and the reason, as BF:70 does. EC's example (EC:71-91) is in shape.

**Three texts change (m11):** BL's docstring ("opens no file but the backlog and writes nothing but the backlog"), its opening line, and BKR's first invariant, which comes to name both shapes.

Rejected:

- **A sibling `walkthrough-lines.py` with its own self-test.** It would leave the three texts unchanged, but either holds a second copy of the grammar — the drift BKR's first invariant exists to stop — or imports BL through `importlib`, coupling two scripts by an interface no document states.
- **Edit-tool writes and a narrow reader.** A hand-recorded result in another layout would read as unanswered, and nothing would prove that an edit touched only result lines.

**Note, 2026-11-28 — the walkthrough's shape and its verbs as built (`docs-workflows` 1.46.0 and 1.47.0).** The approved text above stands; this note records the shape a walkthrough is read in, the verbs' exits and the command's holds around them at the close of batch 4, and each place where the built thing departs from the approved text, with the ruling behind it.
- **The shape (the plan's R20)** is `evidence-contract.md` §4's paragraph *The shape a walkthrough is read in.*: BF §1's line rules, at most 1 MiB, and a walkthrough's own structure. Its top-level keys are among `walkthrough`, `stamp`, `preconditions`, `steps` and `captures`, each once. `walkthrough:` is a block mapping holding a plain `id` and `unit`. Each step opens `- n: <number>`, the numbers strictly increasing, its keys among `n`, `action`, `target`, `expect` and `result`, and its `action` one of the five verbs. A `result:` is a one-line flow mapping or a one-level block mapping, its `outcome` a plain `confirmed`, `differs` or `blocked`, with `observed` on `differs` alone and `note` on `blocked` alone. `captures:` entries are mappings one level deep, keyed among `slot`, `after_step` and `shows`. A key appears once in each mapping at any depth, two keys being compared by their text.
- **Its reasons** are `WALK_REASONS` in `scripts/backlog-lines.py`: the 19 `REASONS` less the four that belong to the backlog's units (`units-twice`, `units-not-block`, `entry-opener`, `status`), plus `top-key`, `walkthrough`, `step-opener`, `step-number`, `step-key`, `action`, `outcome`, `result` and `capture` — 24 in all. As a set they equal the 24 the §4 paragraph names, which the self-test's `walk_shape_paragraph_pinned` holds, and §4's example is in shape (`walk_ec_example_in_shape`; measured at batch 4's close: `ok`, steps 1 and 2, the one slot after step 2).
- **`walk-check`** prints, beyond the list above, the walkthrough's own `id`, which Phase 1 test 6 compares with the id it read it by; `blocked_no_note`; the stamp's `state` and `reason`; and `slots_outside_class`. It never prints text.
- **The verbs' exits (the plan's R14)** are 0, 2 and 3, with no 4: a composed walkthrough is untracked, so no `git diff` could hold a write for an undo. Before it writes, each writing verb checks that every line it does not write is byte-equal and in order, and that the file it would write reads in shape. It then writes a new file beside the walkthrough, renamed over it, refusing `changed-while-reading` where the file changed since its read, and reads the result back. Exit 3 refuses on the walkthrough's content and leaves it untouched: `shape`, `step-absent`, `no-steps`, `too-many-steps`, `too-large`, `changed-while-reading` or `exists`. A verb that did not finish — exit 2, or anything the caller's rule reads as 2 — stops the run with `DOCS_VERIFY_WALK_WRITE` and makes no record commit, since the file's state is then unknown.
- **`walk-record`** writes `result: { outcome: <o> }`, with `observed: "<e>"` or `note: "<e>"` added on `differs` or `blocked`, at the step's key indent. That is one line, and the text is the escaped double-quoted scalar the approved text names: `\` and `"` escaped, and every C0, DEL, C1 and bidirectional control written `\uXXXX`. It writes from a JSON file the run wrote with the Write tool, which the command's answer test holds first.

Where the built thing departs from the approved text:
- **Six verbs, not five.** `id-class --id` reads and writes nothing. It tests an id against the unit-id class and against the class `edit --walkthrough` and `walk-new` hold a walkthrough id to — one YAML reads back as text — so Phase 1 test 6 can tell whether the unit's id can serve as the fixed id of a walkthrough to compose. The ruling is batch 3's pre-flight carry 1 for Task 3.1: a non-writing class-test verb for `--walkthrough` ids.
- **The command holds the walkthrough around every verb** (`commands/docs-verify.md` *The walkthrough, held*), beyond the approved "keeps every byte it does not write, writes atomically and reads the write back". Each `walk-check` and each write runs in one Bash call bracketed by the walkthrough's blob (`hash-object --no-filters`), and a write runs only where the file still holds the run's last blob. A bracket that fails prints `not-hashed`, `not-held` or `no-blob`, each a route into `DOCS_VERIFY_WALK_WRITE` with its own reason, and a Read of the file for a question is held before and after. This was Task 3.3's design choice, sent to its Fable review as a named target; the markers are from the Task 3.3 re-review 1's N1 and N2 (`eb93f6ffe`).
- **A walkthrough holding no step is refused** at Phase 1 test 6, since `walk-append` writes only after the last step (Task 3.3, `bd98fd60e`).
- **The three texts (m11)** changed as approved. The docstring's opening line names the walkthrough. Its sentence on what the script opens and writes names a walkthrough under `.dev-workflows/walkthroughs/` and the JSON file a walk verb names. BKR's first invariant names both shapes and both pinned paragraphs.

Departures in the walk and the prepare that this decision's verbs carry:
- **The check-12 labels** (S2-D4). The approved arrays had labels that promised typed text — the step's *differs* and *blocked*, and the image slot's *I have it*. The built arrays take the prompted form, `(you'll be prompted for …)`. The ruling is Task 3.3's concern 1: check 12 and `escalation-rules` §0 enforce a `CLAUDE.md` hard constraint, which outranks the plan's copy. `b48fac649` truth-edited the plan and both designs, so S2-D4 above already carries the prompted form.
- **The renamed-control rule**, which no approved text states. A control or a route found under another name is `differs`, its observed text the name it has now and what the step then showed, and the page's instruction is rewritten to that name. One not found at all is `blocked`, save where the step's `expect` says it is hidden or absent, when not finding it is `confirmed`. The command's step question, the prepare's checklist and `evidence-contract.md` §5 each state it, and a walked step is never rewritten (STEP-RETARGET in `docs/superpowers/to-fix.md`). The rulings are the Task 3.5 review's I3 (`8218fbabf`: the unit brief's Fable-reviewed rewrite of a contradicted instruction stands, so the walk's earlier "never `differs`" changed) and its re-review 1's O1 (the hidden-or-absent exception) and O2 (the rule in §5 and in both by-hand tables), fixed in its round 2 (`e6d0f0482`).
- **F4's unmapped token** (Q1, S2-D6). The composer's return test prints `unmapped`: each line of the page's copy holding a claim's marker that no coverage entry names. Any such line takes the unresolved exit with `claims-unresolved`, nothing written to the walkthrough — a case beyond Q1's "three cases only". The ruling is the batch 3 final review's F4 (`a8c9a4419`), its widening named in batch 3's pull request by the ledger's ruling.
- **A prepare runs no toolchain preflight** (S2-D12). A prepare runs no build, lint or style check, so its Phase 0 skips the preflight, records no `toolchain_preflight` row and keeps no ledger, and `gate-ledger.md` §10's row reads "as §9, outside a prepare". The approved registry runs the preflight at Phase 0 for every unit. The ruling is Task 4.1's concern 1, accepted, which Task 4.2's review M1 carried to `toolchain-preflight.md`, the gates rules and the references page.
- **The post-commit hold** is in the note under S2-D9.
- **A prepare that changed nothing commits nothing** (S2-D6). Where a prepare appends no step, the unit already names the walkthrough, and its restamp wrote nothing — its time the committed stamp's own, in the same second, over a file holding no result — the nothing-to-record test finds nothing, no commit is made, and the hold after it reads the commit that already holds the walkthrough. The ruling is the Task 4.1 review's M2, reproduced and fixed in `79018bf56`.

### S2-D11. Untrusted input

The command takes DW's rules by citation (DW:22, moved by S2-D1), and adds these:

- **The page's own `evidence:` values (I11)** are frontmatter any committer edits. Before any command names them:
  - `kind` must be `code`, `artifact` or `walkthrough`;
  - `ref` must be in `OBJECT_ID`;
  - a code `path` must pass `rel-path`, and its `repo` must resolve against `sources[].repo`, whole;
  - an artifact `path` must be in `ARTIFACT_PATH`.

  A failing entry refuses the unit, which is named by its position.
- **The walkthrough.** Ids and slots are held to `UNIT_ID`. Step text, observed text, notes and authors are free text, written as DW:22 writes it in a question, the checklist and the handoff. Outcomes come only from the reader's closed set. The writer takes text from a JSON file, never an argument, so it "never reaches a shell" (P-D13).
- **An answer becomes page prose (EC:115).** It is written as words (S2-D7), the reviewer's BLOCKER backs that, and P-D11's question shows it before it is taken (I9).
  - A steered composer can still report full coverage for weak steps, and re-running it is the same agent reading the same text. The residual is named: the operator sees the counts and each appended step.
- **Source repositories.** Both parts of the clone test, and admission (DW:167-168); `-c safe.bareRepository=explicit` on every call; reads by object id through ROR §4.
- **Images.** Each profile and typed value is held to its class (S2-D4).
- **Carried forward from sub-project 1's reviews:**
  - CLONE-BARE-REPO's clone test;
  - TP-QUOTE: single-quoted tool tokens (DW:104);
  - PR-TEMPLATE-COMMENT: the template as data (FH:219);
  - `:(literal)` pathspecs and `'./<path>'` for `check-ignore` (FH:151, :175);
  - WHY-UNDO-COPY: no second copy of BL's undo line.
- **Who sees what** (P-D13), one unit each:
  - the composer: its handoff file and the page;
  - the reader: the page, its classed evidence, its clones at two commits, today's ARD texts, and the scanner returns;
  - `code-scanner`: as in DW;
  - `doc-writer` and `doc-reviewer`: the apply brief;
  - `docs-style-checker` and `doc-fixer`: the page and their findings.

### S2-D12. Gates and routing

**GL gains §10, `/docs-verify`'s registry**, as GL §7 allows (GL:161). It holds §9's four gates, at phases 0, 7, 7 and 8, with §9's notes by citation: one ledger per unit, and `build_check` decides the commit. UB's gate row reads §9 or §10, by command. Rejected: one §9 with a column per command.

**MODERATE** per unit, as DW:118.

- `doc-writer`, `walkthrough-composer` and `claim-reader` run on the §2 Opus chain.
- `doc-reviewer` runs at its pin.
- `code-scanner`, `docs-style-checker`, `doc-fixer` and `impl-maintenance` run on §2.1.

A unit costs three Opus dispatches. A repair dispatch and a re-review add one each.

### S2-D13. The lifecycle

No edge changes, and `/docs-verify` writes `drafted → verified` (BF:110).

**VERIFIED-NO-DRAFTED is left to DOC-D-G2.** `/docs-verify` verifies; it does not re-queue. P-D6 left every other edge alone (:88), and `/docs-drift` owns re-queueing. ROUTE step 8's workaround stands (ROUTE:236), and the entry is re-owned. Rejected: a by-hand edge now.

Under Q1, BF §4 gains a third token, `claims-unresolved`, in the same shape as the other two: record, report, leave the status alone (BF:137). **MARKER-ASSERTION** is closed by this sweep.

### S2-D14. No regression; versions and coupling

Deliberate changes, each named:

- **`/docs-write`:**
  - the parameter-free blocks move and are cited, with behaviour and stop codes identical and the self-test's pins following;
  - its *Next step* (DW:477) and follow-ups (DW:514) name `/docs-verify`;
  - FH §6's generalised wording reads as before;
  - it passes none of BL's new flags.
- **BL:** `moved --own-moves` (C1), whose absence leaves the output byte-identical, with both modes pinned; `edit --from`, `--walkthrough` and `--block`; and the walkthrough verbs.
- **UB:** `answers` changes from `BLOCKED` to an apply brief, which no `/docs-write` brief carries.
- **`doc-writer`, `doc-reviewer`:** their descriptions and openings name `/docs-verify` (WRT:3, :11; REV:3, :12-14).
- **`/document`:** none.
- **`/docs-audit`, `docs-audit-reviewer`:** none; BF §3 and §4 change in text only. A verified page whose moves a merge lost carries no marker, so `--refresh` lands it on `published`, which BF:129 already names.
- **`code-scanner`, `docs-style-checker`, `doc-fixer`:** unchanged; their caller lines gain `/docs-verify`.
- **A verified page:** its `review_by` advances to the verification date (m8), its `evidence:` gains the sources a reading names, and a user page gains a walkthrough entry.
- **`workflows-core`:** the sites in *Files touched*. One is a count: `escalation-rules`' "Seven stash choices" (:377) becomes eight.
- **BKR:** invariant 1, the map line, and the apply-brief and move invariants. **Invariant 5 stands.**

**Versions (S2-D15, Q4).** Under Q4's recommendation: batches 1, 3 and 4 are each a `docs-workflows` minor, and batch 2 is a minor of both plugins.

**Coupling (batch 2).** A newer `docs-workflows` beside an older `workflows-core`:

- leaves the cost entry pending forever (`cost-emission` §8 does not name the command);
- leaves the namespace map without the command;
- leaves `branch-naming` without its slug.

Update both together. The reverse is harmless. `schema_version` stays 1. An older `/docs-write` ignores a `stamp:`, and UB:43 gains "and its `stamp`".

### S2-D15. Batches and releases

**One plan in four batches.** One plan keeps the decisions, the sweep and the fixtures in one place. Whether each batch is also its own release is Q4.

1. **Groundwork.** `/docs-write`'s behaviour is unchanged. The batch holds Q2's extraction, BL's `moved --own-moves` and its `edit` flags, and FH §6's wording, proven by `/docs-write`'s fixtures and the self-test.

   *Usable:* the same `/docs-write`, and the script flags the later batches call.
2. **Engineering units.** The spine:
   - select, consent and branch;
   - the scans and `claim-reader`;
   - the readings question;
   - the apply brief;
   - both programs;
   - the verify commit;
   - Q1's exit;
   - GL §10.

   Plus every registration: the `workflows-core` sites, the four GIT-G1 edits, the docs and the counts. A user unit is refused with a line naming the next release.

   *Usable:* an engineering page reaches `verified`. A unit that cannot resolve leaves the run by Q1's exit.
3. **User units walked in session, and resumed (N1).** It holds:
   - BL's walkthrough verbs, and EC §4's shape paragraph and stamp key;
   - the composer;
   - the walk, *Stop* and the record commit;
   - **the stamp's write and its test**;
   - **P-D11's *Take these answers* question**, which walks the steps left;
   - images and the fitness question.

   *Usable:* a user page reaches `verified` in one sitting. A stopped or blocked walk is resumed by the next run, which takes its answers — so Q3's option text is true in the release that ships it.
4. **`--prepare`.** It holds the prepare commit, its stamp write, the printed checklist, and EC §5's text on recording results by hand for a later run.

   *Usable:* the asynchronous walk. Its answers are taken by batch 3's question.

## Questions for the maintainer

1. **A unit that cannot fully resolve, and `explanation` pages.** The run can meet three cases:
   - a user claim no five-verb step expresses — rationale, which every `explanation` page holds (`coverage-model.md` :51, :58, :77), as does any page with a sentence of it;
   - an engineering claim no reading settles;
   - a claim on which a specs document and the code disagree.

   P-D11 says the text is "marked", but gives the run no exit.

   **Recommended:**
   - **No page edit without the move.** The unit stays `drafted`, and every marker, the page-level one included, stays. A partial page would get a new blob and void every recorded answer.
   - **The run records the outcome.**
     - A user unit's walk goes into the record commit (Q3).
     - **For these three cases only (N2)**, the same commit sets `blocked_by: [claims-unresolved]` (`edit --block`). An engineering unit's commit holds the token alone.
     - A blocked, unanswered or stopped walk records with no token and stays resumable.
     - The token stops `--next` on the branch that holds it, and everywhere once that branch merges (N5).
     - The report lists each claim and why.
   - **Specs against code gets one bounded question per claim**, as SRC §7.3 asks: `["Document as the code reads (Recommended)", "Leave it undecided — the unit stays drafted"]` (N4).
     - The decision is recorded in the report and in FH §6.6's draft, as SRC §7.4 records one.
     - There is no "as the ARD reads" option, since that drafts SRC §7.5's gap file into a PRD folder this run lacks.
   - **The exit.** A person edits the page or its source, clears the token, and re-runs. Or a person verifies by hand (ROUTE step 6) and moves the unit by hand (BF:116).
   - **`explanation` pages: accept the hole, with ROUTE step 6 by hand as the named route.** `verified` asserts observation or a read, and nothing observes a rationale. The run says so before the walk.

   **Alternatives:**
   - P-D11's clause as written: commit the partial page, marked, with no move. For a user unit this voids every recorded answer. For an engineering unit the cost is only a commit without a move (N5).
   - An attestation outcome for an unexpressible claim. This changes what `verified` asserts (P-D11 :134) and EC §5's table.
   - No token, so `--next` re-chooses the unit every run.
2. **Where the shared steps live.**

   **Recommended:** extract only the parameter-free blocks into `references/docs-iteration/backlog-run.md`, as batch 1, which changes nothing `/docs-write` does. S2-D1 names what moves, the parameters, and what stays literal. `/docs-verify` writes its own Style, Build and Review. The cost is an edit to a command shipped today, contained by its fixtures.

   **Alternative:** `/docs-verify` cites DW's phases by number, as DW:248 cites AUD. DW stays untouched, but each later DW edit changes `/docs-verify` unseen, and `/docs-capture` becomes a third reader of DW's numbering.
3. **A way out of the walk, and where an unfinished walk rests.**

   **Recommended:**
   - a fourth option on P-D11's per-step array: `"Stop — keep these answers for a later run"`;
   - **a record commit for every walk that ends without its move** — a stop, a blocked step, a failed build, a review that stayed blocked, a fitness *Cancel*, or a refused verify commit (S2-D6).

   FH §6.1 and §6.2 then keep their approved text. From batch 3 on, the next run takes the recorded answers behind P-D11's question and walks only the steps left (N1), so the option's promise holds in the release that ships it.

   **Alternatives:**
   - P-D11's array as written. Interrupting the session is then the only way out, and it skips the tail.
   - Revision 1's design: a record commit only on a failed move test, with every other walk left uncommitted behind a new FH §6.1 and §6.2 exclusion.
4. **Releases: how P-D16's "a minor" reads (N6).** P-D16 says each sub-project is a minor of both plugins.

   **Recommended:** four batches, each released on its own: four `docs-workflows` minors, and one `workflows-core` minor, in batch 2. Each batch then reaches users as soon as it passes review: engineering verification first, then the in-session walk, then the asynchronous walk. Bumping `workflows-core` in batches 1, 3 and 4, which change nothing in it, would be a false release. This reads P-D16's "a minor" per release, which departs from its letter.

   **Alternative:** one release after batch 4 — a minor of both plugins, as P-D16 reads literally. The batches still merge in order, but no user gets engineering verification until the walks are done too, and the release carries four batches of change at once.

## Files touched

**New, in `docs-workflows`:**

- `commands/docs-verify.md`;
- `agents/walkthrough-composer.md` and `agents/claim-reader.md`;
- `references/docs-iteration/backlog-run.md`, with its reference-page docs entry (m12);
- `docs/commands/docs-verify.md`, and the two agents' docs entries.

**Edited, in `docs-workflows`:**

- DW;
- UB: §1's row, §2, §3.4, §4.6 and *Phase numbers*;
- FH §6, wording only;
- GL §10;
- EC: :7, :63, :101, :107, §4 and §5;
- BF: :7, :110, :116, :120, :129, and §4 under Q1;
- BL;
- WRT and REV;
- ROUTE: step 6, :112 and :216;
- `docs/workflow.md`, `roles-and-phases.md`, `README.md` and `commands/docs-write.md`;
- `CHANGELOG.md`, `plugin.json`, and the marketplace description, replaced within its budget.

**Edited, in `workflows-core`:**

- `cost-emission` (§7's row; §8's rung);
- `feedback-emission` §2;
- `branch-naming` (§2.4; §3, `docs-verify-<id>`);
- `next-phase-offer`'s not-pipeline list;
- `escalation-rules` and its parts: the stash count, and its *Repo missing*, *Dirty tree*, *Refresh blocked* and BLOCK-escalation sentences;
- `finding-triage` (:36, :41, :47) and its parts;
- `doc-structure-conventions`' consumer lines;
- `source-truth`'s consumer sentences (SRC:16, :98-99);
- `specs-repo-git` :310 and `phase-handoff` :628, with `reference-parts/phase-handoff/require-on-main.md` regenerated, never hand-edited;
- `scripts/command-namespaces.json`, `CHANGELOG.md` and `plugin.json`.

**The instruction tier:**

- `CLAUDE.md`: :37's command, agent and reference counts, re-derived (m12), and the `docs-grounding.md` row's "25 command files … fourteen";
- `.claude/rules/docs-workflows.md`: :19, :27 and :39-42;
- BKR;
- `docs-workflows-gates.md`: :15;
- `docs-grounding.md`: `paths:` and the reason;
- `workflows-core.md`: :30, :32, :38, :51-52 and :59;
- `workflows-core-model-routing.md`: :30;
- `workflows-core-triage.md`: :14;
- WCG: :26 and :32;
- `plugin-updates-coupling.md`: a bullet.

**`docs/superpowers/`:** `to-fix.md`, the feature-gaps review, and `to-test-on-real-project.md`.

**The sweep.** It runs by subject over refinement 4's scope, counted before and after. The subjects:

- who moves a unit to `verified`;
- who composes walkthroughs and renders the checklist;
- who removes the page-level marker;
- which edges and `blocked_by` tokens have a writer;
- what stays manual on the route;
- which command dispatches each agent;
- which commands consume each shared reference;
- the counts.

The exclusivity probe adds "by that person alone", "Spec 2's", "a later release", "reserved", "no command", "by hand" and "Two values are written".

## The GIT-G1 edits

All four are truth edits, under the standing approval. Each is re-derived at batch 2's landing.

1. **WCG:26.**
   - Before: "Consumed by the thirty-six commands that write into `$SPECS_PATH` — every one of the family's thirty-nine except … returns the same thirty-six: … six of `docs-workflows`'s eight, …"
   - After: "thirty-seven … the family's forty … the same thirty-seven: … seven of `docs-workflows`'s nine, …"
   - The recipe holds because `docs-verify.md` writes `args: "specs-repo-git commit-artifacts` literally (S2-D1).
2. **WCG:32.**
   - Before: "nineteen of the thirty-six callers resolve or run inside an **implementation** repository"; "ten of the thirty-six also resolve for docs grounding"; "Nineteen is all thirty-six minus the seventeen".
   - After: "twenty of the thirty-seven"; "ten of the thirty-seven"; "Twenty is all thirty-seven minus the seventeen".
   - The engineering backend dispatches `code-scanner` over a clone. The "joined" sentence stays. WCG is 19,986 characters (`LC_ALL=C.UTF-8 wc -m`), and edits 1 and 2 add one net.
3. **SRG:310.**
   - Before: "… `/docs-audit`, `/docs-write`, the four logging commands and `/diagnose-session` — runs on …"
   - After: "… `/docs-audit`, `/docs-write`, `/docs-verify`, the four logging commands …"
   - The sentence ends "Those three classes are every caller of this entry point".
4. **PH:628 (I2).**
   - Before: "… and the file is read — save by `/docs-workflows:docs-write`, which refuses there the backlog unit that cites the file."
   - After: "… save by `/docs-workflows:docs-write` and `/docs-workflows:docs-verify`, each of which refuses there the backlog unit that cites the file."
   - `/docs-verify` refuses there by *Sources* step 3. The line sits in the `require-on-main` entry, so `reference-parts/phase-handoff/require-on-main.md` is regenerated.

**Not joined.** No `require-on-main` caller, register row, `branch-check` caller, handoff producer or branch prefix (P-D2), and no other ref is read (I1).

**Left as they stand.**

- SRG:132, which stays true;
- SRG:314;
- SRG:752-762, the no-tail list, which claims no completeness;
- PH:403 and :439;
- PH:628's named readers;
- the `specs-git` skill.

The stash count is `workflows-core`'s, not GIT-G1's.

## Risks

- **The walk's length.** One question per step, and one more per `differs`. `--prepare` is the route for a long walkthrough.
- **Coverage.** A step whose `expect` does not truly test its claim still confirms it. The operator sees the counts and each appended step, and the reviewer sees the map. This risk is stated, not closed.
- **A misread** is bounded by the Opus tier, the readings question and the reviewer's spot check.
- **Opus spend.** Three to five dispatches per unit.
- **The `explanation` hole.** Pages a walk cannot verify are verified by hand (Q1).
- **Batch 1 edits a shipped command.** Its fixtures and the self-test are the check.
- **Forged answers.** Any committer can commit a stamp and answers. P-D11's question, which now shows them, is the only control.
- **Line-ending settings** that differ between runs void the answers. This fails closed (S2-D9).
- **An SVG can carry script.** The fitness question is a person's look, not a scan.
- **A refused record commit** leaves the walkthrough dirty, and FH §6.2 asks about it on the next run.
- **The marker program** reads outside fenced code only, so inline code is the builder's to settle (*assumption*: rare outside this family's docs).

## The to-fix, roadmap and feature-gaps updates

**`to-fix.md`:**

- MARKER-ASSERTION is closed by S2-D8's sweep.
- VERIFIED-NO-DRAFTED is re-owned to DOC-D-G2.
- New: **DW-EDIT-FROM**. `/docs-write` could pass `--from missing` and use `--own-moves`. It is recorded only, since S2-D14 keeps `/docs-write`'s behaviour.
- New: **UNWALKABLE-CLAIMS**, under Q1's recommendation.
- CLONE-BARE-REPO stays open at CS's sites, which this command does not reach.
- New: **BASE-MOVED-STALE**, a gap older than this design (review 2 §2). `moved` drops the base from the refs it reads, so a unit the base has already moved is not passed over on a stale working branch. Phase 4's re-check catches it after a cut, but an adopted stale branch does not.
- Each batch adds what its review leaves.

**Feature-gaps.** The DOC-D-G1 heading (:285) and row (:48) gain sub-project 2's design, then each batch's versions.

**`to-test-on-real-project.md`** gains three checks:

- an engineering `differs` (batch 2);
- a composed walk to `verified` (batch 3);
- a `--prepare` round trip with another author's answers (batch 4).

**Roadmap.** No roadmap file carries this family.

## What is left to the builder

- **Wording:** the `DOCS_VERIFY_*` codes and their lines; the question texts around the fixed arrays; the commit subjects.
- **The agents:** each agent's schemas, and the `environment` class. The plan-time frontmatter check comes first (S2-D5): whether `claim-reader` can take a tool pattern or `disallowedTools`.
- **BL:** the verb names, JSON shapes and exits; the `--own-moves` docstring; EC §4's structure paragraph.
- **`backlog-run.md`:** its layout.
- **Images:** the list of image extensions.
- **The marker program:** how it treats inline code.

**Fixtures, as traced runs.** Selection: two open draft branches, where `--next` chooses (C1); `/docs-write`'s fixtures re-run after batch 1. Engineering: all confirmed, refs advanced; a `differs`; an ARD changed since the page's ref, read at today alone; specs against code, under both answers; an evidence path gone; an `evidence:` value out of class; a bare-repository clone. User: a composed walk to `verified`; a hand-written walkthrough extended; an `explanation` page taking Q1's exit and token; a blocked step's record commit with no token, resumed by the next run; *Stop*, then a resume (batch 3); a build failing after apply, the page restored and the walk recorded. Review: a fixer's wording edit, allowed; a mis-applied answer, repaired by `doc-writer`; a frontmatter change, refused by program. Outside answers: `--prepare`, then another author's answers, taken behind the question that shows them; uncommitted answers through *Proceed anyway*; a page rewritten after a prepare; a CRLF page under `text=auto`. Text and images: a `differs` holding markup; an internal unit's image; an `images.root` outside the repository.

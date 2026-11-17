# DOC-D-G1 sub-project 2: `/docs-verify`

Date: 2026-11-17. Status: **draft for review** — the design-questions step P-D1 gives sub-project 2. The parent, `docs/superpowers/specs/2026-11-17-doc-d-g1-docs-iteration-design.md` (revision 3, approved 2026-11-17), is the authority: this document settles what it leaves open (its *What is left to the builder*, :194, and what else a plan needs) and re-decides nothing it decided. Base: `main` at `74d3e8d1e` (`docs-workflows` 1.43.0, `workflows-core` 1.97.0; sub-project 1, PR #210). `file:line` citations are at that commit; anything not grounded so is marked *assumption*. The three questions at the end are the maintainer's; each `S2-D<n>` is the author's.

Abbreviations, under `plugins/docs-workflows/` unless named — the parent's **BF**, **EC**, **FH**, **ST**, **ROUTE** (`docs/docs-workflow.md`), **SRG**, **PH**, and: **DW** `commands/docs-write.md`; **UB** `references/docs-iteration/unit-brief.md`; **GL** `references/gate-ledger.md`; **BL** `scripts/backlog-lines.py`; **AUD** `commands/docs-audit.md`; **WRT**, **REV** `agents/doc-writer.md`, `agents/doc-reviewer.md`; **CS** `plugins/workflows-core/agents/code-scanner.md`; **SRC** `plugins/workflows-core/references/source-truth.md`; **MR** `plugins/workflows-core/references/model-routing/classification.md`; **WCG** `.claude/rules/workflows-core-git.md`; **BKR** `.claude/rules/docs-workflows-backlog.md`. The parent's decisions are **P-D1** to **P-D17**.

## Intent

Route step 6 — verify a drafted page's claims — is still done by hand (ROUTE:179-214) and ends "*Later: `/docs-verify` is planned … No such command exists yet.*" (ROUTE:216). Every page `/docs-write` drafts carries the page-level marker until a verification removes it (EC:63), so until this command ships a backlog run's page sits at `drafted` and the grid does not move for it (BF:116; the parent's *Risks*, :200). This document designs `/docs-verify` to P-D11's contract: one `drafted` unit per run, its claims resolved by its audience's method — a person's walk, or a code reading — and moved to `verified` in the commit holding the resolved page.

## What ships today

- **The contract**: P-D11 (:128-135) — selectors, backends, `--prepare` and its stamp, `doc-writer` applying answers, what `verified` asserts, bounded questions. P-D8 (:104) puts the move in "the commit holding … the resolved page and the walk's results"; P-D9 (:113) and P-D12 (:139) fix the image rules and the fitness question; P-D13 (:151) says who sees what.
- **What sub-project 1 left for it.** UB reserves `answers`, `BLOCKED` in this release (UB:53, :71, :107). FH §6 is written for "a run of `/docs-workflows:docs-write`" (FH:151), and its message, created-path list and push condition are `/docs-write`'s (FH:177, :182, :197). BL `edit` writes `status` and, where unset, `page_path`, nothing else (BL:44-48, :906-931), and requires `--status` (BL:1039). GL §9's Phase column is `/docs-write`'s (GL:177). Two DW programs find the page-level marker (DW:110-116, :383-393) by a phrase BL's self-test pins (BKR:25).
- **What no file does yet**: compose a walkthrough (EC:101); render the checklist and write results back (EC:107); read a claim in code at two commits — `code-scanner` reads present-day code and "does not accept a branch override" (CS:142); remove the page-level marker (EC:63).
- **The walkthrough** is YAML frozen by EC §4 (EC:67-101), read by `/docs-write` with the Read tool as data (DW:148, UB:43); nothing reads or writes it line-wise, and "no YAML parser ships with the plugin's scripts" (P-D8 :102; BF:65).

## Goals, non-goals, anti-goals

**Goals.** (1) `/docs-verify <unit-id>|--next` takes one `drafted` unit to `verified` by its audience's method (EC:19-26), in one commit with its resolved page. (2) A user walk can run outside the session, bound to the page by P-D11's stamp. (3) A hand-written walkthrough that misses claims is extended, never rewritten. (4) `/docs-write`, `/document`, `/docs-audit` and the agents behave as before, save what S2-D14 names. (5) Three GIT-G1 truth edits, no new behaviour.

**Non-goals.** `/docs-capture` and `captured` (sub-project 3); every `stale` edge, and `verified → drafted` (DOC-D-G2, S2-D13); `verified → published` (BF:111, :125); a browser driver (EC:129); `--batch` (P-D11); `release` units (P-D14); any change to `/document`'s command file; a `schema_version` bump; a pull request opened by the plugin; settling a claim no walk or reading settles — it stays marked, and a person decides.

**Anti-goals.** A page edited by a run that does not move its unit (S2-D6). A marker removed but by a resolved claim (EC:136). A user claim resolved by code, or an engineering claim by observation (EC:137). Answers taken without a stamp naming the page as it stands, or without the question naming their source (P-D11). A winner picked between a specs document and the code (SRC:292). A walk's answers lost to a later phase's failure. A value from a walkthrough, an answer, a page or a commit reaching a path, ref or command before its class test (P-D13).

## Decisions

### S2-D1. The phases, and what is shared by citation

Signature: `/docs-verify <unit-id>|--next [--prepare] [--docs-repo <path>] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]`.

- **0 Resolve** — DW Phase 0 steps 1–12 by citation (DW:71-116), with no `--batch`, `--prepare` a bare flag, and the toolchain preflight read against GL §10 (S2-D12); then routing (S2-D12).
- **1 Select** — S2-D2.
- **2 Resolve the evidence** — user: which walkthrough file, its stamp and its results, through S2-D10's reader; engineering: the page's own `evidence:` entries, sorted and resolved by DW's *Sources* (DW:162-168).
- **3 Consent** — the unit, its page and backend; user: the walkthrough (named, to compose, or to check for missed claims — an Opus `walkthrough-composer` dispatch either way), its recorded answers and whether they bind the page as it stands, the slots and `images.policy`; engineering: each clone, marked where only this answer admits it, and each artifact; the branch; every profile command verbatim, as DW:193's. `["Verify it (Recommended)", "Cancel"]`; under `--prepare`, `["Prepare it (Recommended)", "Cancel"]`.
- **4 Branch** — FH §6.2, then DW:217-223's re-check: the entry, the page's blob, the walkthrough reader's output and the profile all equal to what the consent showed.
- **5 Walk or Read** — S2-D3 to S2-D5, ending at S2-D6's move test; `--prepare`, and a walk that cannot move the unit, commit here and go to Phase 11.
- **6 Apply** — images placed; `doc-writer` with `answers` (S2-D7) under DW's reach tests (DW:265-278); the page-level marker removed (S2-D8).
- **7 Style** — DW Phase 6 (DW:296-324).
- **8 Navigation and build** — DW Phase 7 (DW:330-336): a `differs` answer can retitle the page, so ST §4's **regenerate** runs where it applies; there is no placement target.
- **9 Review** — DW Phase 8 (DW:342-377) on the apply brief, with the command's own escalation list, whose *Defer* says the unit does not move and the walk is kept.
- **10 Commit** — S2-D8. **11 Finish** — FH §6.5–§6.6, generalised. **12–15** — the report, then DW's tail: maintenance and feedback, follow-ups, cost (`documenting`/`dev`, fixed, as DW:528), the resume pointer and `commit-artifacts` last.

**Ending early** is DW:20's: five ends take no tail — an unknown flag, a bad selector, a run-flag stop, the ladder's *Cancel*, a target in no work tree — each before the target is resolved, the last keeping SRG:132's "Three runs' command bodies lead to that last case" true (P-D3). Every later stop takes the stop route.

**Shared by citation (Q2).** P-D4 rules out a second prose copy. What both commands run identically — the untrusted-input rules (DW:22), the classes and the two test programs (DW:24-63), *Sources* and the clone test (DW:162-168), *The base* and the unmerged-branch read (DW:154-160), *Copies* and the reach tests (DW:263-278), the style, build and review phases, and the marker programs — moves out of DW into a new `references/docs-iteration/backlog-run.md`, cited by both commands and later by `/docs-capture`, its stop codes written `<RUN>_…` for each command to prefix. Each command keeps its selection tests, phase order, arrays, report and prefix.

### S2-D2. Selection

Unit tests in order — for `<unit-id>` the first failure stops the run with its line; for `--next` it passes the unit over, those words its reason (DW:140):

1. **`drafted`.** Anything else is refused, naming it; a `missing` unit's line names the branch that drafted it as where to run, since a unit drafted on an unmerged branch is `missing` on the base (P-D7 :94).
2. **`blocked_by` empty** (DW:143).
3. **Not a `release` surface** (DW:145; P-D14): `--refresh` can land a hand-written What's new page on `drafted`, and its claims rest on `release-notes.md`, outside P-D14's artifact set.
4. **Type, audience and visibility legal** (DW:146).
5. **The page**: `page_path` set and passing the page-path test (DW:27); a regular file, no link; its frontmatter's `unit:` equal to the id, read as DW:144 reads it; no other page under a content root carrying the id, by DW:144's `git grep` (two is AUD's no-match case); and committed and clean (FH §6.1 widened, S2-D8), since the stamp binds a page in history.
6. **The backend's inputs.** User: the entry has a `walkthrough:` line (BF:48), which S2-D8's edit needs, as DW:149 needs `page_path:`; a named walkthrough passes DW:148's admission and S2-D10's shape; an unnamed one takes S2-D3's fixed id. Engineering: the page's `evidence:` holds a code or artifact entry, each passing *Sources* (S2-D5); `--prepare` is refused — there is nothing to walk.

**`--next`**: candidates `drafted`, `blocked_by` empty, not `release`, id in class, by priority then file order (DW:154); tests 1–6; then `backlog-lines.py moved` unchanged (BL:26-42), which passes over a unit a branch not merged into the base has moved — so a unit verified on an unmerged branch is not walked twice. Rejected: `--next` without that read, for exactly that reason.

### S2-D3. The walkthrough, and the composer

**Which file.** A named walkthrough is used (EC:99). An unnamed one is composed at `.dev-workflows/walkthroughs/<unit-id>.yml`: **its id is the unit id** — fixed, not a minted `W-<n>`, so the next run finds a composed file an earlier run left uncommitted (S2-D6). Where that file already exists, it is taken only where its `walkthrough.unit` is the id (the reader prints it only in class); otherwise the unit is refused, naming the file.

**Extension.** Every user run — composed file, hand-written file, or answers being taken — has the composer check the file against the page, after the branch step, over the page the branch holds. Steps it adds are appended after the file's last `n`; no step is rewritten, renumbered, reordered or removed, and no `captures[]` entry is added. Each appended step is printed before the first question; in an answers run they are walked here once the answers are taken (S2-D4).

**The agent: `walkthrough-composer`, new, in `docs-workflows`, on the §2 Opus chain** — MR:575's synthesis/planner row: it decides which observation settles each claim, and its coverage is what `verified` rests on — its `model:` passed as DW:134 passes `doc-writer`'s. Rejected: `doc-writer` under a third brief kind — a page writer turned YAML writer, adding a third replaced-section set to UB §1 for an unrelated job; `doc-planner`, whose inputs are a PRD folder and diffs.

- **Tools**: Read, Glob, Grep. It writes nothing; the orchestrator writes through S2-D10's writer.
- **Inputs** (a handoff file): `mode` (`compose` | `extend`); the page's path; the unit's id, title, type, audience, roles; in `extend`, the walkthrough's text.
- **Job**: take every claim on the page its audience can observe, marked or not — the page-level marker says none was observed (EC:63) — and cover each with a step in the closed vocabulary (EC:93) whose `expect` states it, an existing step in `extend`, a new one otherwise; return a claim no five-verb step expresses as `uncoverable`, with why — EC:93's "finding rather than a licence". `compose` also proposes `role` (one of the unit's) and `preconditions`; `environment` is the person's, asked once in plain text before the walk or the prepare.
- **Return**: `status` (`DONE` | `BLOCKED`); `steps` (all, or the appended, possibly none); `coverage` — per claim, its quote and line, and the steps covering it or `uncoverable: <why>`; notes. The coverage lives only for the run — EC:55 rules out a maintained claim map. It carries the family's untrusted-content block (P-D13).

**An `uncoverable` claim means no `verified` this run** (S2-D6): the run says so before the first question and asks `["Walk to record the answers — the unit stays drafted", "Cancel"]`. A user page whose claims are rationale, not observation — an `explanation` — may never verify by a walk; that stays a person's (*Risks*).

### S2-D4. The walk, the recorded answers and the images

**In session.** The run writes the stamp (S2-D9), clearing every result, then asks one question per step in `n` order, its text giving the step's number, action, target and expect — each written as DW:22 writes a free-text value — with P-D11's array verbatim: `["confirmed", "differs — I'll type what I saw", "blocked — I'll say why"]` (Q3). `differs` asks for the observed text, `blocked` for the reason, each in plain text, required, one line (EC:113, :115, :127); empty or multi-line is re-asked. A free-text answer naming one outcome is that outcome; any other is re-asked (CLAUDE.md, *choices*). **Each answer is written to the file as it is given** (S2-D10), so a dying session, a stop or a later failure loses none. Rejected: writing them at the walk's end.

**Answers recorded outside the session** count only where the stamp is in shape, names the unit's `page_path`, and its blob equals the page's (S2-D9). Otherwise the consent says why — no stamp, another page, another version — and the walk restamps, clearing them. Where they count, Phase 5 asks P-D11's question verbatim, `["Take these answers (Recommended)", "Walk it again here", "Cancel"]`, its text giving the outcome counts and the source: the commit that last changed the file (`git -C '<top>' log -1 --format=… -- ':(literal).dev-workflows/walkthroughs/<id>.yml'` — object id, author written as DW:22 writes free text, date), or *uncommitted in your working tree* where the file differs from `HEAD` or is untracked. *Take* takes every result and walks here only steps with none — an interrupted walk, an appended step — or a `differs` without observed text; *Walk it again* restamps and walks all; *Cancel* takes the stop route.

**`--prepare`** (P-D11): after the branch, compose or extend; stamp, clearing every result; commit (S2-D6); print the checklist — the stamp, preconditions, each step with its `expect`, each slot, all free text escaped — and the instruction to record results in EC:117-125's form and run `/docs-verify <unit-id>`; then Phase 11's push offer, the report and the tail.

**Images** — P-D11's "each slot's screenshot taken here". After the step a capture's `after_step` names — in a walk, or as answers are taken — for each slot in class whose comment the page carries, the run asks `["I have it — I'll give the file", "Skip — the slot keeps its placeholder"]` under `in-repo`, or the same asking for the URL under `object-store` and `cdn`, where the person uploads (docs-profile-schema.md:136-138). A path must pass `abs-path`, be a regular file by `lstat`, within `images.max_bytes`, with an image extension; a URL must start `https://`, hold no whitespace or control character, and start with `images.public_prefix` (`images.internal_prefix` for an internal unit's `object-store` image). A failure is refused, never printed, re-asked. **The orchestrator** copies an `in-repo` image to `<images.root>/<unit-id>/<slot>.<ext>`, under the internal tree for an internal unit (ROUTE:175) — named from the slot, never the source file (P-D13), one path per slot, an overwrite an edited path, a new file a created one; `object-store` and `cdn` commit nothing (P-D9); `doc-writer` writes the reference on the line after the slot comment, which stays. Rejected: `doc-writer` copying, as `/document`'s does (WRT:52-53) — the orchestrator holds the class tests and the policy. **An unfilled slot does not block the move**: its comment renders nothing, and the report names it. After the walk, before any apply, P-D12's fitness question, once, every image by path, none recommended: `["They show nothing that must not be published", "Cancel — nothing is committed, and the answers are kept"]`.

**Never automated**: taking a step; seeing a screen; the observed text; why a step is blocked; taking or uploading a screenshot; judging an image fit; taking answers recorded elsewhere; naming the environment; what becomes of a claim no step expresses.

### S2-D5. The engineering backend and the claim reader

**Today's commit** is read as DW Phase 4 reads one (DW:236-257): a `code-scanner` per clone the page's code entries resolve to, under `scan-refresh`'s fixed policy, themes the unit's and its surface's titles, `search_hints.paths` the entries' paths; `prep.scanned_ref` resolved to a commit (DW:257) is that repository's **today**. Reused for its handling of dirty trees, read-only mounts and the session's own repository; its capability map goes to the reader as hints. Each clone passes both parts of the clone test and admission first (DW:167-168), so CLONE-BARE-REPO's open CS sites (`docs/superpowers/to-fix.md`) are not reached.

**Artifacts.** The orchestrator reads each ARD by commit: at `<default-ref>` (today), and at the entry's `ref` only where that commit is an ancestor of `<default-ref>` (`git -C "$SPECS_PATH" merge-base --is-ancestor`) — a commit that was the default branch's when `/docs-write` read it (DW:231); otherwise not read there, and reported. Nothing unlanded is read; BKR:29's "at `<default-ref>` alone" gains that ancestor (S2-D14).

**The agent: `claim-reader`, new, in `docs-workflows`, on the §2 Opus chain** — SRC §4.2's verification, which `doc-planner` runs at Opus (MR:575), and here the reading `verified` asserts; `doc-reviewer` spot-checks three to five claims (REV:64), so it cannot catch a misreading. Rejected: **`code-scanner`**, which classifies themes rather than reading claims (CS:82-86) and reads only present-day code (CS:142); **`doc-reviewer`**, which grades the edits that apply the readings — reading and grading in one agent is a command certifying its own prose (a parent anti-goal).

- **Tools**: Read, Bash (git, read-only).
- **Inputs**: the page's path; the unit; per clone `{repo, path, today, evidence refs}`; the page's code entries; per artifact `{path, ref, text_at_ref | null, today_ref, text_today}`; the scanner returns.
- **Reads by object id only**: `git -c safe.bareRepository=explicit -C '<clone>'` with `show '<commit>:./<path>'`, `grep -n -F -f '<pattern file>' '<commit>' -- ':(literal)<path>'` or `ls-tree`, each value single-quoted; a term built from page text reaches git only through a pattern file under `run-flags` §7's TMPDIR, never on a command line; never the working tree, a switch, a fetch or a write. A commit the clone lacks (`cat-file -e` failing) is *not read*.
- **Grading**, by SRC §3's techniques (SRC:126-222), outcomes mapped from SRC:250-261: **`confirmed`** — today's source states the claim (VERIFIED); **`differs`** — today's source states something else, in one phrasing, returned as `observed` (CONTRADICTED), to which the page is rewritten, code being the truth an engineering page answers to (EC:23, :26); **`unresolvable`** — nothing at today settles it (NOT_FOUND), phrasings disagree (AMBIGUOUS), code cannot settle it, its evidence path is gone at today, or **a specs document and the code disagree on it** — SRC:292: never pick a winner; it stays marked, and a person decides. The read at the evidence `ref` is reported beside each — held, differed, absent, not read — telling drift from a drafting error; it decides nothing.
- **Return**: per claim, quote, line, outcome, source (repo or artifact, path, lines, commit), `observed` on `differs`, `why` on `unresolvable`, the ref read; and each evidence entry whose path is gone at today.

**The readings question.** Where the move test passes (S2-D6), the run asks once, `["Apply these readings (Recommended)", "Cancel"]`, naming each `differs` claim with the code's phrasing and location and counting the rest: a person, not the reader, turns a reading into an edit (SRC:12-13). Where it fails, nothing is asked or written; the report lists every reading and the unit stays `drafted`.

### S2-D6. The move test, the three commits, and the walk kept

**The move test**, deterministic, before any apply. User: every step answered, none `blocked`, every `differs` with its observed text (S2-D10's counts), and no `uncoverable` claim. Engineering: no `unresolvable` reading, no evidence path gone at today.

**No page edit without the move.** A partly resolved page would get a new blob and void every recorded answer (P-D11: "A rewritten page has another blob"), costing a full re-walk for a partial gain, and P-D8 ties the resolved page to the move. Rejected: committing confirmed claims unmarked and the rest marked, with no move.

So a run makes one of three commits, each one commit by FH §6.3:
- **prepare** (`--prepare`): the walkthrough, stamped, results cleared, and a composed file's `walkthrough` id in the backlog. No move (P-D11).
- **record** (a user unit failing the move test): the walkthrough with its stamp and results, and a composed file's id. No move. The person can finish a blocked step in the file and run again; the stamp still matches, since the page did not change. Engineering has none: a reading is cheap to repeat, and no file holds it.
- **verify**: the page, each image placed, each config regenerated, the walkthrough with its results (user), the backlog — P-D8's commit.

**The walk is kept.** A unit-level end after the walk — a failed build, a review that stayed blocked, the fitness *Cancel*, a refused commit — runs FH §6.4 over the run's paths, but **the command leaves the walkthrough holding the answers out of both lists it hands §6.4**: neither restored nor moved, it stays with its stamp and results, a composed file untracked at its fixed path. §6.4 restores the page to the bytes the stamp names, so the next run takes the answers behind P-D11's question (*uncommitted in your working tree*); the report says so, and FH §6.1 and §6.2 learn to pass that one file (S2-D8). This keeps P-D8's one commit. Rejected: committing the results ahead of the apply — the move's commit would then lack them, against P-D8's wording.

### S2-D7. Applying the answers: `unit-brief.md` and the two agents

UB stops reserving `answers` (UB:53): a brief carrying it as a top-level field is an **apply brief**, and UB gains its fields and texts. Neither agent's pointer paragraph (WRT:9, REV:10) changes — both already send `brief_kind: unit` to UB. Rejected: a new `brief_kind: verify`, a second pointer in each agent where P-D4 keeps every difference in UB once.

**The apply brief** is UB §2's, but: `write_targets` is `[{kind: extend-existing, path: <page>}]` alone, and `page_path` names the existing page; `evidence` is **advanced** — engineering: each code entry's `ref` its repository's today, each artifact's the specs commit read, a source a reading names that the list lacks added; user: code entries unchanged (no code was read), `{kind: walkthrough, id}` added where absent; `review_by` the run's date plus UB:44's interval, the page having just been checked; `walkthrough` the file's text (user); and new fields — `answers` (`{backend, source, steps: [{n, outcome}] | readings: [...], images: [{slot, ref}]}`, the outcomes from S2-D10's counts, the observed texts in the walkthrough's text), `page_before` (the copy taken before the dispatch, *Copies*), and UB §4.1's reviewer fields.

**`doc-writer`** — UB gains §3.4; §1's list for it is unchanged, the same four sections replaced by §3.4 where `answers` is present.
- *Entry validation*: the page exists, is the only target, carries `unit:` equal to the id and the page-level marker; every step or reading has an outcome. Else `BLOCKED`.
- *Step 2*: `evidence:` and `review_by` take the brief's values; nothing else in the frontmatter changes — not `unit:`, `type`, `audience`, `visibility` or `title` — and no `changelog:` entry.
- *Step 5*: each `images` entry referenced on the line after its slot comment, alt text from the capture's `shows`.
- *Step 7*, per claim: **confirmed** — its marker, where it has one, removed, its words kept; **differs** — rewritten to say what was observed or read and nothing more, its marker removed; **blocked, unresolvable or unanswered** — marked (a defence; the move test keeps the run off this path). Observed or read text reaches the page **as words**: markup, a link, HTML, an include or a token in it is written as literal text. **It never removes the page-level marker** — the orchestrator does (S2-D8), as only the orchestrator writes `unit:` in DW.

**`doc-reviewer`** — UB gains §4.6, and §1's list gains one row for this brief only, *Source-code accuracy*.
- *Inputs*: refuses without `answers` and `page_before`. *Method step 2*: the page is read against `page_before` and the answers — P-D11's "each edit says what was answered and nothing more".
- *Factual correctness*: every change from `page_before` is a marker removed from a confirmed claim, a claim rewritten to an answer's text, an image reference at a slot, or `evidence:`/`review_by`; anything else is a BLOCKER, as is a claim no answer covers left unmarked, a `differs` not applied, or markup an answer brought in. No page-level marker (the orchestrator removed it) and no claim marker remain.
- *Completeness vs plan*: every answer applied, a missed one the BLOCKER above. *Coverage*: `N/A — graded when the page was drafted`.
- *YAML frontmatter*: `unit:` present and equal to the id (absent: BLOCKER); `type`, `audience`, `visibility`, `title` as in `page_before`; `evidence:` and `review_by` the brief's.
- *Screenshots*: each `images` entry at its slot, no other image added. *Source-code accuracy*: on a user page `N/A — a user page's claims are resolved by observation` (EC:137); on an engineering page it stands. *Verification-gate integrity*: against GL §10. *Recommended next step*: /docs-verify's phases.

`doc-fixer` is handed no answers (P-D11; `doc-fixer.md:26`). UB's *Phase numbers* (UB:29) becomes per command.

### S2-D8. The move and its commit

1. **The page-level marker** is removed at Phase 6's end, by the orchestrator, after `doc-writer` returns `DONE` and the reach tests pass: a program confirms the first body line (after the visibility marker on an internal page) is EC §3's marker byte for byte, as DW:383-393 reads it, and that the body holds no other `[NEEDS CLARIFICATION:` outside fenced code; it then deletes that line and the blank line after it. Either test failing ends the unit. Removed **before** style, build and review, the page every gate sees is the page committed; BL's self-test pins its phrase with DW's two (BKR:25). Rejected: removing it after the review, which no gate would see; `doc-writer` removing it, on runs that then fail to move.
2. **At Phase 10**, the same program confirms no marker remains; the backlog is copied; then `backlog-lines.py edit --id '<id>' --from drafted --status verified`, with `--walkthrough '<id>'` for a composed file.
3. **BL `edit` gains two flags**, with its docstring and `--selftest`. `--from <status>` refuses, exit 3 `status-differs`, an entry not at that status: a walk can take an hour, and nothing else guards the window between the re-check and the edit (BL:50-53 narrows only its own read). `--walkthrough <id>` sets `walkthrough:` where unset (`null`, `~`, empty), refusing `walkthrough-set` where it names another and `no-walkthrough` where the line is absent, as `--page-path` does (BL:45-48). A prepare or record commit passes `--from drafted --status drafted --walkthrough '<id>'`. `/docs-write` passes neither, unchanged.
4. **One commit**, FH §6.3, over the page, each image, each config regenerated, the walkthrough (user) and the backlog; subject `docs: verify <unit-id> (<type>, <audience>)`, the prepare and record subjects with their own verbs.
5. **Finish**: FH §6.5's push offer, once; §6.6's draft, printed; **no pull request** (FH:207, BKR:28). The adopt question (FH:161) usually continues on the branch that drafted the page, so the verify commit joins its pull request.

**FH §6, generalised** — each reading as before for `/docs-write`: §6's opening (FH:151) names `/docs-verify`; §6.1 tests the backlog, the profile **and the files its command names** — for /docs-verify the page, and the walkthrough, which may stand uncommitted only where it holds a stamp in shape; §6.2 step 3's clean-tree read and stash pathspec exclude, beside `unfinished/`, the one path the command names — the walkthrough holding answers, whose id's class holds no glob character, so `':(exclude)…'` needs no `literal`; §6.3's "once the page carries its `unit:` line" becomes "once its command's writes for the unit are made", and its subject's verb the command's (`draft` for `/docs-write`); §6.4's examples of created and edited paths gain the page, images and walkthrough; §6.5's "committed a unit" becomes "made a commit"; §6.6's draft gains, for /docs-verify, the backend, the answers' source, the walk's counts or the readings, the images, and a record or prepare commit. WHY-UNDO-COPY: /docs-verify quotes no stderr line; it cites §6.4, as DW:401 does.

**What `verified` asserts** is P-D11's (:134), unchanged: no marker; nothing blocked or unresolvable; evidence advanced to what the run read; each claim observed in the environment and role the walkthrough names, or read in code at the commit recorded. One precision: answers taken from a commit or the working tree assert that the operator took them behind a question naming their source — not that the named author walked. So the sweep qualifies BF:120's "a human's assertion" and BF:129's sentence by who removed the marker (MARKER-ASSERTION).

### S2-D9. The stamp

A top-level mapping, directly after the `walkthrough:` block:

```yaml
stamp:
  page: docs/guides/place-an-order.md
  blob: 3f6c2a7e0d4b5c1f8a9e2b7d6c5a4f3e2d1c0b9a
  at: "2026-11-17T14:03:09Z"
```

`page` is the unit's `page_path`, relative to `<top>`, in `PAGE_PATH` (DW:27). `blob` is in `OBJECT_ID` (DW:29): `git -C '<top>' hash-object --path='<page path>' -- './<page path>'`, which applies the clean filters as `/implement` does (`plugins/dev-workflows/commands/implement.md:54`), so on a page FH §6.1 holds clean it equals the blob at `HEAD`. `at` is `date -u +%Y-%m-%dT%H:%M:%SZ`, pasted, double-quoted. One key, three lines in that order, two-space indent: the writer writes nothing else, and the reader accepts nothing else.

**Written** only by a prepare and at a session walk's start, each write clearing every `result:` (P-D11), so no answer outlives the stamp that binds it. **Tested** by a later run: in shape and exactly one; `page` equal to `page_path`, whole; `blob` equal to the page's blob now. Any failure: the results do not count, and the reason is reported — no stamp, another page, another version. `at` is never tested: a clock is no evidence (SRC:596-602's guard shows why).

**EC §4 gains** the key, its form, and that a driver reading `steps[]` ignores it. **EC §5 gains** that /docs-verify takes results only behind a stamp naming the page as it stands; that a person verifying by hand (ROUTE step 6) records results with no stamp, as before; and that `/docs-capture`'s results carry none and never count (P-D11).

**It never authenticates** who walked, that anybody walked, the environment, when, or the steps — a step edited after the stamp keeps its result, which then describes the step as it reads. Any committer can write a stamp with the right blob; P-D11's question naming the commit and author is the control, and a git author is what the committer typed. Rejected: a digest of the steps in the stamp — P-D11 binds answers to the page, and a result describes its step as it reads; the stamp nested in `walkthrough:` — nested-key rules for a key a driver ignores.

### S2-D10. Reading and writing the walkthrough (Q1)

Recommended: **BL gains walkthrough verbs**, staying the one implementer of BF §1's line grammar (BF:65-68), the walkthrough's structure stated in a new EC §4 paragraph its self-test reads as it reads BF §1's. `walk-check` tests the shape and prints only counts and values in class, never text (BL:71-73): the unit id, the step numbers, the stamp's `page` and `blob`, each outcome's steps, each `differs` without observed text, the slots. `walk-stamp` writes the stamp and clears every result. `walk-record` writes one step's result from a JSON file the run writes, the text a double-quoted scalar, escaped, one line. `walk-append` and `walk-new` write appended steps or a composed file from the composer's JSON, in canonical in-shape form. Each keeps every byte it does not write, writes atomically and reads its write back, with BL's exits and caller's rule (BL:78-99). A hand-written walkthrough out of shape stops the run naming the line and reason, BF:70's remedy for the backlog; EC's example (EC:71-91) is in shape.

### S2-D11. Untrusted input

DW's rules by citation (DW:22, moved by S2-D1), and:
- **The walkthrough** is anyone's who commits. Ids and slots are held to `UNIT_ID`; a step's text, an observed text, a note and a commit's author are free text, written as DW:22 writes one in a question, the checklist and the handoff file; outcomes come from the reader's closed set; the writer takes text from a JSON file, never an argument, so it "never reaches a shell" (P-D13).
- **An answer's text becomes page prose** by design (EC:115): it reaches the page as words (S2-D7), the reviewer's BLOCKER backs that, and the question naming the source is the human control.
- **The page** is data to the composer, the reader, the writer and the reviewer; its claims reach git only through a pattern file (S2-D5).
- **Source repositories**: both parts of DW's clone test and admission before any dispatch names a path (DW:167-168); `-c safe.bareRepository=explicit` on every git call in a clone; reads by object id.
- **Images**: a typed path or URL held to its class; a destination named from the unit id and slot; an SVG named in the fitness question like any image (*Risks*).
- **Sub-project 1's hardening, carried**: the bare-repository clone test (CLONE-BARE-REPO); profile tool tokens and `cd` directories single-quoted after their class (TP-QUOTE, DW:104); the pull-request template as data (FH:219, PR-TEMPLATE-COMMENT); `:(literal)` pathspecs and `'./<path>'` for `check-ignore` (FH:151, :175); no second copy of BL's undo line (WHY-UNDO-COPY).
- **Who sees what** (P-D13): `walkthrough-composer` the page, the unit and the walkthrough; `claim-reader` the page, its evidence, its clones at two commits each, the ARD texts the orchestrator read, the scanner returns; `code-scanner` as in DW; `doc-writer` and `doc-reviewer` the apply brief; `docs-style-checker` and `doc-fixer` the page and their findings. One unit, always.

### S2-D12. Gates and routing

GL gains **§10, `/docs-verify`'s registry**, as GL §7 lets an adopter declare its own (GL:161): §9's four gates, its Phase column 0, 7, 7, 8, and §9's notes by citation — one ledger per unit, `build_check` deciding whether the unit commits. UB's Verification-gate integrity row reads §9 or §10 by command. Rejected: one §9 table with a column per command, an edit to `/docs-write`'s registry.

**MODERATE** per unit, as DW:118: one page, an Opus apply and an Opus review, one unmerged branch. `doc-writer`, `walkthrough-composer` and `claim-reader` on the §2 Opus chain; `doc-reviewer` at its pin; `code-scanner`, `docs-style-checker`, `doc-fixer` and `impl-maintenance` on §2.1. A unit takes three Opus dispatches — composer or reader, writer, reviewer — and a fourth where a re-review runs.

### S2-D13. The lifecycle

No edge changes; /docs-verify writes `drafted → verified` (BF:110). **VERIFIED-NO-DRAFTED is left to DOC-D-G2**: a `verified → drafted` edge has no writer here — /docs-verify verifies and does not re-queue — P-D6 left every other edge as it stands (:88), and `/docs-drift` will own re-queueing; ROUTE step 8's workaround (ROUTE:236) stands until then, and the `to-fix` entry is re-owned. Rejected: a by-hand `verified → drafted` edge now — a change to P-D6's machine for an edge with no writer in this track. **MARKER-ASSERTION is closed by this sweep** (S2-D8).

### S2-D14. No regression; versions and coupling

The deliberate changes each piece sees:
- **`/docs-write`**: its shared text moves to `backlog-run.md` and is cited (behaviour identical; the marker programs move, BL's self-test following); its *Next step* (DW:477) and Phase 13 follow-ups (DW:514) name `/docs-verify` in place of walking by hand; FH §6's generalised text reads as before for it; it passes neither new BL flag.
- **UB**: `answers` from `BLOCKED` to an apply brief — no `/docs-write` brief carries it.
- **`doc-writer`, `doc-reviewer`**: their descriptions and openings name /docs-verify (WRT:3, :11; REV:3, :12-14); nothing else.
- **`/document`**: none — its dispatches carry no `brief_kind`.
- **`/docs-audit`, `docs-audit-reviewer`**: none; BF §3's text only. A page /docs-verify verified whose moves a merge lost carries no marker, so `--refresh` lands it on `published` — the case BF:129 already names, "one whose marker its verification removed".
- **`code-scanner`, `docs-style-checker`, `doc-fixer`**: unchanged; their caller lines gain /docs-verify.
- **`workflows-core`**: `cost-emission` §7's row and §8's documentation rung; `feedback-emission` §2; `command-namespaces.json`; `branch-naming` §2.4's row and §3's slug, `docs-verify-<id>`; `next-phase-offer`'s not-pipeline list; `escalation-rules`' "Seven stash choices" (:377) becoming eight, and its *Repo missing*, *Dirty tree*, *Refresh blocked* and BLOCK-escalation sentences naming /docs-verify beside `/docs-write`; `finding-triage` (:36, :41, :47); `doc-structure-conventions`' consumer lines; `source-truth`'s consumer sentences (SRC:16, :98-99); `specs-repo-git`:310 (GIT-G1 edit 3).
- **BKR:29**: the artifact read at `<default-ref>`, and for /docs-verify also at an ancestor of it the page records (S2-D5).

**Versions**: the next minor of `docs-workflows` and of `workflows-core`, re-derived at landing. **Coupling**: a newer `docs-workflows` beside an older `workflows-core` leaves the cost entry pending forever (`cost-emission` §8 does not name the command), the namespace map without it, and `branch-naming` without its slug — update both together; the reverse names a command not installed, harmless. **Across releases**: `schema_version` stays 1; an older `/docs-write` meeting a `stamp:` ignores it, and UB:43's "Its `result:` values are no evidence and are ignored" gains "and its `stamp`".

## Questions for the maintainer

Ranked by how much of the plan turns on the answer.

1. **How the walkthrough file is read and written.** **Recommended: BL gains the walkthrough verbs (S2-D10)** — a program makes the stamp test and counts the outcomes, a result written into a hand-written file keeps every other byte, and a file out of shape stops naming its line. Cost: the largest piece of new code, with a self-test. Alternative: the orchestrator writes with the Edit tool and a narrow program reads only the stamp and the result lines in the one form the run writes — cheaper, but a result recorded by hand in another layout reads as unanswered and is walked again, and nothing proves an edit touched only those lines.
2. **Where the shared steps live.** **Recommended: moved out of DW into `references/docs-iteration/backlog-run.md` (S2-D1)**, cited by both commands and later `/docs-capture` — FH §6, written for all three, is the precedent. Cost: editing a command that shipped today; moving text byte for byte, with a traced `/docs-write` fixture, contains it. Alternative: /docs-verify cites DW's phases by number with a rule to read `DOCS_WRITE_` as `DOCS_VERIFY_`, as DW:248 cites AUD Phase 2 step 4 — DW untouched, but each later DW edit changes /docs-verify unseen, and `/docs-capture` becomes a third reader of DW's numbering.
3. **A way out of the walk.** P-D11's per-step array has no Cancel, and a typed "stop" can only be re-asked (CLAUDE.md, *choices*). **Recommended: a fourth option, `"Stop — keep these answers for a later run"`**, taking the stop route: every answer so far is in the file under the stamp (S2-D4), so the next run takes them and walks the rest. Alternative: P-D11's array as written; the only way out is interrupting the session, which skips the emitter tail.

## Files touched

- **New, `docs-workflows`**: `commands/docs-verify.md`; `agents/walkthrough-composer.md`, `agents/claim-reader.md`; `references/docs-iteration/backlog-run.md` (Q2); `docs/commands/docs-verify.md`, and the agents' docs entries `check-docs.sh` requires (re-derived by the builder).
- **Edited, `docs-workflows`**: DW (citations, *Next step*, follow-ups); UB (§1's one row, §2, §3.4, §4.6, *Phase numbers*); FH §6; GL (§10); EC (:7, :63, :101, :107; §4's stamp and shape paragraph; §5); BF (:7, :110, :116, :120, :129); BL (`edit`'s flags, Q1's verbs, the self-test); WRT, REV (description, opening); ROUTE (step 6, :112, :216); `docs/workflow.md`, `docs/roles-and-phases.md`, `docs/README.md`, `docs/commands/docs-write.md`; `CHANGELOG.md`, `plugin.json`, the marketplace entry (its description replaced within budget, never appended to).
- **Edited, `workflows-core`**: the references `cost-emission`, `feedback-emission`, `branch-naming`, `next-phase-offer`, `escalation-rules` and its parts, `finding-triage` and its parts, `doc-structure-conventions`, `source-truth`, `specs-repo-git` (:310); `scripts/command-namespaces.json`; `CHANGELOG.md`, `plugin.json`.
- **Instruction tier**: `CLAUDE.md` (:37's counts; the `docs-grounding.md` row's "25 command files … fourteen"); `.claude/rules/docs-workflows.md` (:19, :27, :39-42); BKR (the map line, the two agents' caller lines, invariants on the walkthrough shape, the apply brief, the move's commit and the artifact read); `docs-workflows-gates.md` (:15); `docs-grounding.md` (`paths:`, /docs-verify's reason for resolving no grounding); `workflows-core.md` (:30, :32, :38, :51-52, :59); `workflows-core-model-routing.md` (:30); `workflows-core-triage.md` (:14); WCG (:26, :32 — GIT-G1); `plugin-updates-coupling.md` (a bullet).
- **`docs/superpowers/`**: `to-fix.md`, the feature-gaps review, `to-test-on-real-project.md`.

**The sweep** runs by subject (refinement 6) over refinement 4's scope, counted before and after (refinement 7): who moves a unit to `verified`; who composes a walkthrough or renders the checklist; who removes the page-level marker; which edges have a writer; what is manual on the route; which command dispatches each agent; which commands consume each shared reference; the counts. The exclusivity probe adds "by that person alone", "Spec 2's", "a later release", "reserved", "no command", "by hand".

## The GIT-G1 edits

All three are truth edits, within the maintainer's standing approval; none adds behaviour. Each is re-derived at landing, after any other track's count change.

1. **WCG:26** — "the thirty-six commands" and "returns the same thirty-six" → thirty-seven; "the family's thirty-nine" → forty; "six of `docs-workflows`'s eight" → seven of nine. The recipe is re-run: /docs-verify ends through `args: "specs-repo-git commit-artifacts`, DW:532's phrasing, which it matches.
2. **WCG:32** — "nineteen of the thirty-six callers" → twenty of thirty-seven; "ten of the thirty-six" → ten of thirty-seven; "Nineteen is all thirty-six minus the seventeen" → "Twenty is all thirty-seven minus the seventeen". The criterion is resolving or running inside an implementation repository, and the engineering backend dispatches `code-scanner` over a clone, as `/docs-audit` and `/docs-write` do; the "joined" sentence stays as it is, a list that claims no completeness. WCG is 19,986 characters (`LC_ALL=C.UTF-8 wc -m`); the two edits add about one, under the 20,000 warning.
3. **SRG:310** — the class "a command for which the specs repository holds only its bookkeeping" gains `/docs-verify` after `/docs-write`, since the sentence ends "Those three classes are every caller of this entry point".

**What it joins.** No `require-on-main` caller, `phase-handoff` register row, `branch-check` caller, handoff producer or branch prefix (P-D2): the caller lists it joins are those three. **Left as they stand**: SRG:132's "Three runs' command bodies" (kept true, S2-D1); SRG:752-762's no-tail list, which claims no completeness and which `/docs-write` does not join either; PH:628's named readers; PH:403 and :439; the `specs-git` skill and script. Bounded questions do not cede control (P-D11), so SRG §4's ceding list is untouched.

## Risks

- **A long walk**: one question a step, one more per `differs`. `--prepare` is the route for a long walkthrough.
- **Wrong coverage**: a step whose `expect` does not test a claim would confirm it. The person sees each composed or appended step and walks each `expect`; the reviewer checks edits against answers, not that a step tests its claim. Stated, not closed.
- **A misread**: the Opus tier, the readings question and the reviewer's spot check are three separate checks.
- **Opus spend**: three or four Opus dispatches per unit.
- **Unwalkable claims**: an `explanation` page's rationale is `uncoverable`; such a unit stays `drafted`, verified by a person.
- **Q2's move can regress `/docs-write`; Q1's verbs grow BL.**
- **Forged answers**: any committer can commit a stamp and answers; P-D11's question is the only control.
- **SVG** can carry script that runs when opened directly; the fitness question is a person's look, not a scan.
- **A kept walkthrough** stays in the working tree after a failed apply; FH §6.2 reads past it, and a person who deletes it loses the walk.
- **The marker program** reads outside fenced code; a page quoting the marker in inline code is the builder's to settle (*assumption*: rare outside this family's own docs).

## The to-fix, roadmap and feature-gaps updates

`docs/superpowers/to-fix.md`: **MARKER-ASSERTION** closed by S2-D8's sweep; **VERIFIED-NO-DRAFTED** re-owned to DOC-D-G2 (S2-D13); new **DW-EDIT-FROM** — `/docs-write`'s edit could pass `--from missing` to close the same window, recorded and not changed, since S2-D14 keeps its behaviour; new **UNWALKABLE-CLAIMS** — a user claim no five-verb step expresses keeps its unit from `verified` by a walk; **CLONE-BARE-REPO** stays open at CS's sites, which /docs-verify does not reach (S2-D5); and what each review leaves. The feature-gaps DOC-D-G1 heading (:285) and index row (:48) gain sub-project 2 "designed in" this file, then its versions. `to-test-on-real-project.md` gains a live check: a composed walkthrough walked to `verified`; a `--prepare` round trip with answers another author committed; an engineering unit with a `differs` reading. No roadmap file carries this family (the parent).

## What is left to the builder

The `DOCS_VERIFY_*` stop codes and lines; each question's text around its fixed array; the prepare and record commit subjects. The composer's and reader's handoff and return schemas, and the class for `environment`. Per Q1, BL's verb names, JSON shapes and exits, and EC §4's structure paragraph; per Q2, `backlog-run.md`'s layout and its `<RUN>_` convention. The image extension list and the internal unit's image directory. The marker program's treatment of inline code. And the fixtures, as traced runs: a user unit composed, walked and verified; a hand-written walkthrough missing a claim, extended; `--prepare`, answers committed by another author, taken behind the question; answers uncommitted; a page rewritten after the prepare, its answers not counted; a blocked step — a record commit, no move; a stop mid-walk (Q3) and its resumption; a build failing after the apply — the page restored, the walk kept, taken by the next run; an engineering unit all confirmed, its refs advanced; an engineering `differs`, rewritten; an ARD the code contradicts — unresolvable, nothing written; an evidence path gone at today; a clone failing the bare-repository test; a stamp with a matching blob from an unknown author, the question naming them; a `differs` text holding markup, written as text; an internal unit's image under the internal tree; `--next` passing over a unit verified on an unmerged branch; `/docs-write`'s own fixtures, re-run unchanged after Q2's move.

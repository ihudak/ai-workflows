# LADDER-ORDER batch 3 — a keyed `/document` asks before it documents work nobody built — verification record

**Plan:** `docs/superpowers/plans/2026-11-16-ladder-order-b3-document-asks.md`. **Design:** `docs/superpowers/specs/2026-11-14-ladder-order-design.md`, §2 (M6), §5.3 with its *Settled while building (batch 3, 2026-11-16)* note, and §5.5. **Measurements:** `docs/superpowers/plans/2026-11-16-ladder-order-b3-measurements.md`. **Population:** `docs/superpowers/plans/2026-11-16-ladder-order-b3-sweep-population.md`. **Release:** `docs-workflows` 1.40.0, `workflows-core` 1.94.1, `product-workflows` 3.83.2 and `dev-workflows` 4.68.1, each changelog section dated 2026-11-16. **Branch:** `feat/ladder-order-b3`, cut from `main` at `ee6ac5d4`. Measured at `97e1dd62`, the head, after the final review's fix wave, its touch-up and the controller's five wordings. **`origin/main` has moved since the branch was cut** — 46 commits, to `8ee5bb80` — and the branch has not merged it; among those commits is a release that takes version numbers this branch also takes (*Versions*, below). Every figure below was obtained here, with its command beside it; where a figure is the ledger's or a report's and was not re-run, the sentence says so.

The rulings summary is `2026-11-16-ladder-order-b3-rulings.md` beside this file, and the controller's ledger, verbatim, is `2026-11-16-ladder-order-b3-ledger.md`: `awk '/^```text$/{f=1;next} /^```$/{f=0} f' docs/superpowers/verification/2026-11-16-ladder-order-b3-ledger.md | diff - .superpowers/sdd/2026-11-16-ladder-order-b3-document-asks/progress.md` prints nothing, and both hash to md5 `b742cda9f0cccc0b91801b1b409c4085`, 99 lines. Every *ledger line* below is a line of that file: `progress.md`'s line *n* is its line *n* + 5. *Ruling N* is row N of the rulings file's table, and *R n* its row R*n*, the plan's.

**Where and how it was measured.** One 12-core machine (`nproc`), Python 3.15.2, git 2.43.0, node v26.13.0, uid 502 (`id -u`). Every command ran from the worktree root, `/workspace/.worktrees/ladder-order-b3`, on the tree `97e1dd62` commits; `git log --oneline -1` printed `97e1dd62` before any of them. `git fetch origin` printed `ee6ac5d49..8ee5bb809  main -> origin/main`; then `git rev-parse origin/main` prints `8ee5bb809ad4110542333b484d97f3c468fdee7d`, `git merge-base HEAD origin/main` prints `ee6ac5d49b3c2f1ff83771190601b7e5eefe09db`, and `git log --oneline HEAD..origin/main | wc -l` prints 46. `$S` below is a scratch directory outside the repository; `$S/base-tree` is the base unpacked there with `git archive ee6ac5d4 | tar -x -C $S/base-tree`, and `$S/main-tree` is `origin/main` (`8ee5bb80`) unpacked the same way.

## What was verified

**The branch.** `git log --oneline ee6ac5d4..HEAD | wc -l` gives 17, the same with `--first-parent`, and `git log --merges --oneline ee6ac5d4..HEAD | wc -l` gives 0: every commit is the branch's own, and none is a merge. By task (the ledger's lines 24 to 104):

- the plan and the measurements, outside any task: `c7166a4a`;
- Task 1, Phase 0 — the record read, the early scan, the question: `e6702f39`, fix rounds `15645ee6` and `7075f441`;
- Task 2, `document.md`'s later phases: `3031db14`, fix round `0c0b5264`;
- Task 4, `/release-notes`' two offers (built before Task 3, ruling 6): `1fb8de7e`, fix round `f9a31747`;
- Task 3, the pages, shared references, rules and rationale: `e6e39560` and `c41c47de`, fix round `60a28544`;
- Task 5, the release: `bb8537c2`;
- the final fix wave: `762aad41`, `9842be89`, `fbd046bf`; the touch-up `691f9e49`; the controller's five wordings `97e1dd62` (ruling 18).

**The files.** `git diff --stat ee6ac5d4 HEAD | tail -1` prints `50 files changed, 1183 insertions(+), 116 deletions(-)`; `git diff --name-only ee6ac5d4 HEAD`, grouped by area: 12 under `plugins/workflows-core` (`document-lineage.md`, `escalation-rules.md`, `implementation-format.md` and `next-phase-offer.md` under `references/`, six regenerated files under `reference-parts/` — `escalation-rules/stops.md` and `next-phase-offer/` `dev.md`, `epics-precondition.md`, `pa.md`, `pe.md` and `pm.md` — the changelog and `plugin.json`), 11 under `plugins/docs-workflows` (the commands `document.md` and `release-notes.md`, the references `key-discovery.md` and `finish-and-handoff.md`, the two command pages, `getting-started.md`, `docs/reference/environment.md`, `docs/reference/session-feedback.md`, the changelog and `plugin.json`), 9 under `plugins/product-workflows` (the commands `create-ard.md`, `specify.md` and `update-spec.md`, their three pages, `docs/workflow.md`, the changelog and `plugin.json`), 7 under `plugins/dev-workflows` (the commands `conformance.md`, `design.md` and `implement.md`, `docs/reference/commit-convention.md`, `docs/reference/environment.md`, the changelog and `plugin.json`), three `.claude/rules/` files (`docs-workflows.md`, `docs-workflows-gates.md`, `plugin-updates-coupling.md`), `docs/maintainers/rationale.md`, six under `docs/superpowers` (the plan, the measurements, the population, the design, `to-fix.md` and `to-test-on-real-project.md`) and `.claude-plugin/marketplace.json`. `git diff --name-only ee6ac5d4 HEAD | grep -vE '\.md$'` lists only the marketplace and the four `plugin.json` files, and `git diff --name-only ee6ac5d4 HEAD -- 'plugins/*/agents' 'plugins/*/hooks' 'plugins/*/skills' 'plugins/*/scripts' scripts .github | wc -l` gives 0: no script, workflow, agent, hook or skill changed. `CLAUDE.md` is not among the files. The commit that carries the three close-out records comes after `97e1dd62` and changes only them.

**`origin/main` since the base.** `git log --oneline ee6ac5d4..origin/main` lists 46 commits, the last the merge of pull request #205 (`feat/sec-g2-d-security-conformance`), whose own commits say it was *renumbered above #204 (workflows-core 1.95.0, dev-workflows 4.69.0, product-workflows 3.83.2, security-workflows 0.12.6)* and split the coupling file. `comm -12` of the two sides' `git diff --name-only ee6ac5d4 …` lists 21 files changed on both, and `git merge-tree --write-tree --name-only --no-messages HEAD origin/main`, a merge computed in memory that moves no ref and touches no file, exits 1 and names 15 files in conflict: the marketplace, `.claude/rules/plugin-updates-coupling.md`, `docs/superpowers/to-fix.md` and `to-test-on-real-project.md`, the `plugin.json` and changelog of `dev-workflows`, `docs-workflows` and `workflows-core`, `product-workflows`' changelog and `docs/workflow.md`, `plugins/dev-workflows/commands/conformance.md`, and `next-phase-offer.md` with its generated `dev.md`. `product-workflows`' `plugin.json` is not among them because both sides set it to 3.83.2. This record measures the branch as it stands; it does not merge, and every *`origin/main`* figure below is labelled as `8ee5bb80`'s or the base's.

Below, DOC is `plugins/docs-workflows/commands/document.md`, RN `plugins/docs-workflows/commands/release-notes.md`, KD `plugins/docs-workflows/references/key-discovery.md`, NPO `plugins/workflows-core/references/next-phase-offer.md`, IF `plugins/workflows-core/references/implementation-format.md`, PH `plugins/workflows-core/references/phase-handoff.md`, *page* `plugins/docs-workflows/docs/commands/document.md`, TT `docs/superpowers/to-test-on-real-project.md`, DES the design, CPL `.claude/rules/plugin-updates-coupling.md`, and DW-CL, WC-CL, DV-CL and PW-CL the 2026-11-16 changelog sections of `docs-workflows`, `workflows-core`, `dev-workflows` and `product-workflows`; every line number is at `97e1dd62`.

## What the batch delivered against the design's §5.3

| §5.3, and the plan's ruling | Where on the tree |
|---|---|
| The record is read at the end of Phase 0 step 1 (R1) | DOC:207 to :219 (*Read the implementation record in the run's scope — step 3a turns on it*), carried as `record_blocks` (DOC:214) |
| Only where it holds no block: the repositories question, the map, the scan and the question, after the docs repository is resolved and before the profile (R1) | DOC:248 (step 3a), :250 to :254 (the repositories question), :256 (the scan) |
| A run whose record holds a block keeps today's order | DOC:248 (*On a run whose record holds a block it does nothing at all*) |
| Two options, the first recommended; neither names a command; a free-text answer normalised or asked again | DOC:267 (the array), DOC:269 |
| The lines above the question; never *nothing built* for a scan that did not look (R4, R5) | DOC:261 to :264 |
| *Stop* names what each unit's first missing document needs, never a run that stops on arrival (R2, R3; L8, L12) | DOC:271 to :275 |
| *Go on* recorded in the report and in `pr-draft.md` (R8) | DOC:277; DOC:1388 (`pr-draft.md`); DOC:1559 (`### Assumptions & limitations`) |
| Nothing is asked twice, and a later base is scanned (R7) | DOC:493 (*Revise plan*), DOC:506 and :509 (Phase 3 takes Phase 0's work), DOC:539, DOC:541 (*A later scan that finds none*), DOC:634 (Phase 4); KD:9, :21, :27 |
| Phase 5's aggregate gate only where the run holds a ref (R6) | DOC:676, DOC:681, DOC:1463 |
| A legacy `commit: null` block is a block (R9) | DOC:217 |
| `/release-notes`' two offers wait for a landed PRD (R10) | RN:782 to :785; `plugins/product-workflows/docs/workflow.md:48`, `:49` |
| `/document` takes no PH §3.4 row | PH's §3.4 recipe below names no `/document`; `grep -c require-on-main` on DOC gives 0 |
| The question is not a gate | *The question as it stands*, below |

## The gates

**The chain, run here.** Every `run:` step of `.github/workflows/validate-catalog.yml` as it stands at the head (`git diff --stat ee6ac5d4 HEAD -- .github` prints nothing), in order, as one `&&` chain, reading the chain's own exit status. With no `yaml` module in this container, the steps were extracted by the script below — batch 2's record's: a step is a line whose first text is `run:` and not a `#` comment, a block step (`run: |`) the deeper-indented lines after it, with a `### step NN` line echoed before each. It extracts **35 steps**, at workflow lines 82 to 354 (it prints them); the two other `run:` matches in the file, lines 342 and 343, are inside a comment. Each step runs as the default Linux shell of a workflow step does, `bash --noprofile --norc -eo pipefail <step file>`; the mermaid parser's `npm ci` step ran again as one of them.

```python
import re, sys
L = open(sys.argv[1], encoding="utf-8").read().split("\n"); out = sys.argv[2]; steps = []; lines = []; i = 0
while i < len(L):
    m = re.match(r"^(\s*)(?:-\s+)?run:\s?(.*)$", L[i])
    if m and not L[i].lstrip().startswith("#"):
        ind, rest = len(m.group(1)), m.group(2).rstrip()
        if rest[:1] in "|>" and rest:
            j = i + 1
            while j < len(L) and (not L[j].strip() or len(L[j]) - len(L[j].lstrip()) > ind): j += 1
            body = L[i + 1:j]
            while body and not body[-1].strip(): body.pop()
            cut = min(len(b) - len(b.lstrip()) for b in body if b.strip())
            steps.append("\n".join(b[cut:] for b in body)); lines.append(i + 1); i = j; continue
        steps.append(rest); lines.append(i + 1)
    i += 1
for n, s in enumerate(steps, 1): open(f"{out}/step-{n:02d}.sh", "w").write(s + "\n")
print(" && ".join(f"echo '### step {n:02d}' && bash --noprofile --norc -eo pipefail {out}/step-{n:02d}.sh" for n in range(1, len(steps) + 1)))
print("steps", len(steps), "workflow lines", lines, file=sys.stderr)
```

`python3 -I $S/steps.py .github/workflows/validate-catalog.yml $S/steps` prints the chain, run as `bash -c "<the chain>"`, then `echo "CHAIN_EXIT=$? steps=<the count of ### step lines>"`. The chain ran from the worktree root at `97e1dd62`, with `git status --short` printing nothing before it and after it — the three close-out files held outside the work tree — from 15:14:29 to 15:27:57 UTC on 2026-11-16, and printed **`CHAIN_EXIT=0 steps=35`**, all 35 `### step` lines reached. Among its lines: `0 error(s), 0 warning(s) across 1 repo(s).`; `PASS: no dash-form requirement IDs under .`; `PASS: the spec-ID census under . equals scripts/spec-id-baseline.txt`; check-docs' `PASS: docs are consistent with the plugin(s) under …`; the four `reference-parts` checks' PASS lines (36 generated files fresh; 4 split references' citations; 37 commands load the question rules; 24 run `branch-check`); `PASS: all 50 mermaid blocks in 1243 tracked markdown files parse (mermaid 11.17.2, marked 16.4.2)`; `run-state selftest: PASS (252 checks)`; `specs-git selftest: PASS (1201 checks)`; and `mutants: 23 checked, 0 stale`. This is the first run of the full chain on `97e1dd62`: the ledger records the controller's covering chain on it (line 100: exit 0, `validate-catalog` 0/0) and the fixer's full chain on `691f9e49` (line 96: 35 steps, exit 0).

**Then, each on its own, same tree, still clean:**

```
$ ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .
PASS: docs are consistent with the plugin(s) under plugins/dev-workflows plugins/guideline-reviewers plugins/workflows-core plugins/docs-workflows plugins/product-workflows plugins/security-workflows plugins/prose-style
rc=0
$ python3 scripts/validate-catalog.py
0 error(s), 0 warning(s) across 1 repo(s).
rc=0
```

`ASSERT_PUBLISHED=1` also printed two `check 9 cost-emitting-commands assertion not applicable` lines, for `plugins/guideline-reviewers` and `plugins/prose-style`, which ship no `docs/reference/session-cost.md`.

**Re-run with the three close-out files in the work tree and staged**, each exiting 0: `./scripts/check-docs.sh --root .` (PASS), `ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .` (PASS), `./scripts/check-id-grammar.sh --root .` (`PASS: no dash-form requirement IDs under .`), the same with `--baseline` after it (the same line) and `./scripts/check-id-grammar.sh --baseline` as the workflow runs it (`PASS: the spec-ID census under . equals scripts/spec-id-baseline.txt`), `node scripts/mermaid/check-mermaid.mjs --root .` (`PASS: all 50 mermaid blocks in 1246 tracked markdown files parse` — three more files than the chain's 1243, none holding a mermaid block), and `python3 scripts/validate-catalog.py` (`0 error(s), 0 warning(s)`). They were run once more after this paragraph was written, with the same results.

## The ruled-in fixes are in the tree

The previous batch's close-out found two ruled-in edits that its fix wave had dropped, so every item was looked for at the head. Each text was searched for wrap-insensitively — whitespace collapsed across each file and across the string — over every tracked `.md` file save this directory and the generated parts, by a script that prints each hit's file and line; a few items were read in place where the change is an order or a definition (marked *read*). **Every item was found; none is missing.**

**The ledger's rulings that order a change to a file.**

| Ruling | What it orders | At the head |
|---|---|---|
| 1 | The design amended to match the plan's rulings, in Task 5 | DES:168 to :187 (*Settled while building (batch 3, 2026-11-16)*, items (1) to (19)); DES:230 (§5.5's *Batch 3* marked built) |
| 2 | `DOCUMENT_NO_PRD`'s pre-rename remedy names `/product-workflows:specify`; `RELEASE_NOTES_NO_PRD` checked for the same; the release text lists it | DOC:153, RN:148 (*under its name from before the artifact filenames lost their keys*); DW-CL:36 |
| 3 | `Left out as never code: <slugs> — the scan did not look there`; KD's *the code stays scanned* qualified | DOC:262; KD:23 (*documentation kept inside a code repository that `implementation.md` names is that code's, and the code stays scanned. Where `implementation.md` does not name it, …*) |
| 4, 7 | The last line's three forms, the middle one naming the repositories not read | DOC:264, each form once |
| 5, revised by 8 | Not built: the question is put in Phase 0 step 3a or not at all | DOC:539 and :541 (*the nothing-built question is put in Phase 0 step 3a or not at all*) |
| 8 | The later-scan line; `nothing_built_answer: unasked — a later scan found none`; R8's second form; Phase 4's member of the class | DOC:541 (line and value); DOC:1388 and :1559 (*an earlier scan had found commits, and the scan over <the base or clone named> found none*); DOC:634 (*A re-run here that finds none*) |
| 9 | ` — the commit scan did not look: <reason>` | DOC:1388; the report's copy DOC:1559 |
| 10 | PLACEMENT-STOP-SECOND-PRD filed | `docs/superpowers/to-fix.md:243`; DW-CL:41 (`### Notes`, with Task 5's M3 workaround) |
| 12 | NPO's *`/epics` precondition*: a `prd.md` asserting no `kind: prd` | NPO:368 (*Where the caller's PRD folder holds a `prd.md` asserting no `kind: prd`*), NPO:400; WC-CL:10, :21 |
| 14 | DOCS-IN-CODE-REPO-SCAN filed and named in the release | `docs/superpowers/to-fix.md:249` (section heading `:239`, intro `:241`); DW-CL:42 |
| 17 | The fixer's concern 2, ruled: `/design`'s *Add the component first* stands on a `prd.md` with no `kind: prd` | `plugins/dev-workflows/commands/design.md:283` (*which keeps the two forms above*); DV-CL:19 |
| 18 | The controller's five wordings | below, with the touch-up |

Rulings 11, 13 and 15 send items to the wave, whose items follow; rulings 6 and 16 order no change to a file.

**Every item of `final-fix-wave.md`.**

| Item | At the head |
|---|---|
| F-1, the question's own text | DOC:269; page:71; DW-CL:17; DES:185 (note (17)); TT:197 |
| F-2, Phase 3 reads again where it no longer holds the entries or the map | DOC:509 (*Where the run no longer holds every entry of those blocks verbatim*), DOC:506 (*where step 3a built one and the run no longer holds it path for path, build it again here*); DOC:593 |
| F-3, Phase 5's two paragraphs and the report's test | DOC:676 (*the run holds at least one ref — one a record entry gave, or one built from the scan's latest result —*), DOC:681 (*Where the run holds no ref at all*, naming *a Phase 4 re-run of key discovery*), DOC:1463 |
| F-4, `<default-ref>` by `specs-repo-git` §3.2's rule, the ref tested first, *unset or empty* | DOC:275, with RN:782's wording for the ref |
| F-5, the multi-component test loaded | DOC:273 (`args: "components multi-component-test"`) |
| F-6, `/conformance`'s two line forms verbatim | DOC:275 and `plugins/dev-workflows/commands/conformance.md:74`, each form once in each; DW-CL:18 |
| F-7, *finds no commit for the Epic's tokens* | IF:96; WC-CL:15 |
| F-8, `<n>` for step 3a's result | DOC:541 (*for Phase 0 step 3a's result, the count its Readiness row printed*) |
| F-9, the could-not-read clause | DOC:1388, DOC:1559; DW-CL:19 |
| F-10, *the repositories question* in the coupling bullet | CPL:26 (*put the repositories question in Phase 1 alone*) |
| F-11, the precondition's case and its sweep; WC-CL no longer *wording only* | NPO:368, :400; its copies counted below (*asserting no `kind: prd`*); WC-CL:10 (*One rule changes*), :21; *No rule changes* stands only in an older release's section, `plugins/workflows-core/CHANGELOG.md:2786` (1.3.3's) |
| F-12, DOCS-IN-CODE-REPO-SCAN | `to-fix.md:249`; DW-CL:42 |
| F-13, the line before the scan | DOC:256; DW-CL:15; DES:186 (note (18)); TT:197 |
| F-14, the design note's two items, the second a fix in the changelog | DES:183 (15), DES:184 (16); DW-CL:37 |
| Task 1's deferred minor | dropped by ruling |
| Task 2's deferred items 1 to 8 | 1 by F-3's wording (DOC:676, :681, :1463); 2 DOC:634; 3 DOC:539 (*Where it finds none, or does not look*), :541 (`[ — it did not look: <reason>]`); 4 DOC:1388 (*its `you answered` reads `the operator answered`*); 5 DOC:1559 (*whether or not that phase ran*); 6 KD:9 (*replaces the `$REPOS_PATH` step 3a resolved, or undoes* Proceed without the repos *there*); 7's narrowing dropped by ruling, the class named at DOC:681; 8 DOC:493 (*records that its pages were written from the PRD alone*) |
| Task 4's deferred minor | RN:783 (*once that edit is merged to the default branch or, where the PRD folder's own file decides, once it is made*) |
| I1, live check 9's setup | TT:207 |
| M1, M2 | DW-CL:10 (*Two headline behaviour changes.*; *without asking whether anything was built*) |
| M3 | DW-CL:41 |
| M4 (and B-N11) | DW-CL:14 (*names one of the scope's tokens (its keys and their `workitem_key`s), and none that*) |
| M5, M6 | CPL:26 (*Update `workflows-core` 1.94.1 with `docs-workflows` 1.40.0*; *Between the dependents:*) |
| M7 | TT:210 (`commit -m "<KEY> <summary>"`) |
| M8 | TT:197 (*Released 2026-11-16; no item below has been run.*) |
| M9 | DES:168 |
| M10 | TT:213 to :218, the five grouped items and a sixth for F-11; the temp-file check in TT:197's defaults |

**The touch-up's items (`691f9e49`) and the controller's five wordings (`97e1dd62`).**

| Item | At the head |
|---|---|
| A-N1 | DOC:275 (*the file in its folder decides, and this paragraph's sentences below on a specs tree that is no git repository take both cases.*) |
| A-N2 | page:71 — *read*: the scan-line sentence now follows *Phase 1 does not put it again* (character 965 against 934 of that line) |
| A-N3 | DOC:541 (`[ — it could not read <the not-read slugs>]`) |
| A-N4 | DOC:273 (`<UNIT>: `, `<UNIT>` the unit,) |
| A-N5 | DOC:275 — *read*: *A unit folder outside the work tree* (character 688) now stands before *Otherwise test the ref first* (character 966) |
| B-N1 | TT:215 (*Move the specs clone out of `$REPOS_PATH`*) |
| B-N2 | `plugins/product-workflows/docs/commands/specify.md:100` |
| B-N3 | `plugins/product-workflows/commands/specify.md:1486`, `create-ard.md:1144`; the pages, `docs/commands/specify.md:146` and `docs/commands/create-ard.md:229` |
| B-N4 | `plugins/product-workflows/commands/update-spec.md:162` |
| B-N5 | `plugins/product-workflows/commands/create-ard.md:1259` |
| B-N6 | `create-ard.md:1047` (*say instead, in the question's own text*), and the mark at `:1080` |
| B-N7 | CPL:26 (*the older side naming `/create-prd`, or `/epics` itself, there as before*) |
| B-N8 (the controller's) | WC-CL:21 (*rather than the edit that lets `/epics` read it*) |
| B-N9 | DV-CL:19, through `design.md:283` |
| B-N10 | `docs/superpowers/to-fix.md:252` (*the middle form where it read another clone*) |
| B-N11 | DW-CL:14 (as M4) |
| B-N12 | TT:218 (*whose ARD, if any, records at most one code component*) |
| B-N13 | TT:217 (*save `branch-check`'s stop first*) |
| Concern 2 | `design.md:283` (ruling 17) |
| W1 (the controller's) | DOC:275 (*— as on a specs tree that is no git repository, which this paragraph's sentences below on one take too —*) |
| W2 (the controller's) | page:71 (*Before the scan, which can take minutes, the run prints one line saying so*) |
| W3 (the controller's) | `create-ard.md:1080`, the mark *(without its `/epics` option on a `prd.md` asserting no `kind: prd` — the precondition above)* now twice on the line, after both arrays |
| W4 (the controller's) | *Without a `prd.md`,* at `docs/commands/specify.md:146` and `docs/commands/create-ard.md:229` |

The old forms the five wordings replaced count 0 each: *stands in is read as that rule reads one, and a command named for it*, *Before the scan, which can take minutes, it prints one line saying so*, *so the offer named a run that writes no PRD* and *and leaves `/epics` unable to read it* (the claim sweep, below), and *Without a PRD,*. `git diff --word-diff=plain 691f9e49 97e1dd62` shows six replacements in six files and nothing else, each the checker's suggested words: W1's inserted clause, W2's *it* → *the run*, W3's mark, W4's *PRD,* → *`prd.md`,* twice, and B-N8's *and leaves … unable to* → *rather than the edit that lets*. That is a comparison with the checker's wordings, not a review of the commit.

## The question as it stands

Quoted from DOC at `97e1dd62`.

- **The test, first half** — DOC:248: "This step runs only where `record_blocks` (step 1) is empty." `record_blocks` is, at DOC:214, *every `## <YYYY-MM-DD> — /implement` block in that scope, or none*, the scope being, at DOC:212 and :213, *the focus Epic's own where `focus_key` is set, and otherwise the PRD folder's and every `EPIC-` folder's under it*.
- **The test, second half** — DOC:258: "**Where the scan found a commit, nothing is asked.** A commit in the result's `commits[]` — one whose own message names a token (`via: message`), or one that a merged pull request the script read landed (`via: pull-request`) — is work found: go on to step 4." And DOC:260: "**Otherwise, the nothing-built question.** Where no commit was found — the scan ran and found none, or it did not look — print these lines, in this order, then put **the nothing-built question**".
- **The array** — DOC:267: `choices: ["Stop — implement it first (Recommended)", "Go on — document from the PRD alone"]`.
- **The question's own text** — DOC:269: "**The question's own text** is the last of the lines printed above it, in the form those lines selected, followed by `Stop and implement it first, or go on and document from the PRD alone?` — so the dialog itself says what the scan could not tell, never only the lines printed before it."
- **The *Stop* line's first sentence** — DOC:271: "**On *Stop***, the run ends as *Ending early* says every run-ending answer does — a user halt, so `emit-block` does not fire — and prints `Stopped at your answer: nothing in <docs_repo_path> was touched.`, then, on the line after it, `<how it is built>, then re-run '/docs-workflows:document <ADDRESS>'.`, `<ADDRESS>` this run's address — the slice's key where step 1 entered one at `DOCUMENT_BRD_NOT_SLICED`."
- **The last line above the question, its three forms** — DOC:264, chosen by the lines above it:
  - where no line of the `<slug>: <scanned> commits …` form was printed: `Nothing naming <keys> was found, and the scan did not look in any repository — it cannot tell whether anything is built.`
  - where one was, beside a `not read` line or the `Left out as never code:` line: `Either nothing is built for <keys> yet, or it was built without the key in any commit message, or in a repository the scan did not read (<the not-read and left-out slugs>) — the scan cannot tell which.`
  - otherwise, every clone in the map read: `Either nothing is built for <keys> yet, or it was built without the key in any commit message — the scan cannot tell which.`
- **The `pr-draft.md` line, its two forms** — DOC:1388, as its first body line, or its second after the DO-NOT-MERGE banner:
  - `nothing_built_answer` `go-on`: `No implementation record and no commit naming <keys> was found; these pages were written from the PRD alone, by the operator's answer.`
  - `unasked — a later scan found none`: `No implementation record and no commit naming <keys> was found — an earlier scan had found commits, and the scan over <the base or clone named> found none; these pages were written from the PRD alone.`

  Each takes ` — the commit scan did not look: <reason>` where the latest scan did not look, or ` — the commit scan could not read <the not-read slugs>` where it read some repositories and returned others with an `error`.

**Never called a gate.** Searched wrap-insensitively over `plugins/`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/` and `README.md` (the claim-sweep script below): *nothing-built gate*, *nothing built gate* and *nothing-built check* count 0. Every sentence holding *nothing-built* was then searched for the word *gate*: one hit, DOC:58's list of run-ending answers, where *gate* is in `gate-ledger.md`, another item of the list. Inside step 3a, DOC:248 to :277, *gate* occurs once, DOC:275's *where its gate passed*, which is `specs-preflight`'s. `plugins/docs-workflows/references/gate-ledger.md` is unchanged (*Frozen files*, below).

**One noun each, no variant.** Every one of the 49 occurrences of *nothing-built* (39 live, 10 history) is followed by *question*; *nothing built question* and *Nothing-built question* count 0. *repositories question* (22 live, 4 history) is preceded by *the* or *The* in each hit but one, *whose repositories question*, the same noun. The other nouns a reader might take for it — *repos question* (1 live), *repository question* (12 live, 3 history) and *`REPOS_PATH` question* (8 live, 1 history) — were read hit by hit: each names another command's own question (`/create-ard`, `/brd-split`, `/prd-ground`, `/epics`, `/specify`, `/release-notes`, `/docs-audit`, `/docs-init`, `/docs-brand`, `/docs-profile`, `/idea`, `/implement`'s target-repository question), none `/document`'s.

## The claim sweep's counts

Counted at `97e1dd62` and in `$S/base-tree` (`ee6ac5d4`), each string wrap-insensitively — whitespace collapsed across each whole file and across the string, the match mapped back to its source line — over `plugins/`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/` and `README.md`, every file that decodes as UTF-8. Each hit is put in one bucket: *history* (any `CHANGELOG.md`, any `.claude/rules/plugin-updates-coupling*.md`), *generated* (`plugins/workflows-core/reference-parts/`), else *live*. The script, batch 2's record's, run as `python3 -I $S/wic.py '<string>' …` from the root of the tree measured:

```python
import os, re, sys
def files():
    for r in ["plugins", "CLAUDE.md", ".claude/rules", "docs/maintainers", "README.md"]:
        if os.path.isfile(r): yield r; continue
        for d, ds, fs in os.walk(r):
            ds[:] = sorted(x for x in ds if x not in ("node_modules", "__pycache__")); yield from (os.path.join(d, f) for f in sorted(fs))
T = []
for p in files():
    try: raw = open(p, encoding="utf-8").read()
    except (UnicodeDecodeError, OSError): continue
    out, idx, ws = [], [], False
    for k, ch in enumerate(raw):
        if ch.isspace():
            if ws: continue
            ws = True; out.append(" ")
        else: ws = False; out.append(ch)
        idx.append(k)
    b = "history" if p.endswith("CHANGELOG.md") or re.match(r"\.claude/rules/plugin-updates-coupling.*\.md$", p) else "generated" if "/reference-parts/" in p else "live"
    T.append((p, raw, "".join(out), idx, b))
for a in sys.argv[1:]:
    s = re.sub(r"\s+", " ", a).strip(); H = {"live": [], "generated": [], "history": []}
    for p, raw, c, idx, b in T:
        j = c.find(s)
        while j >= 0: H[b].append(f"{p}:{raw.count(chr(10), 0, idx[j]) + 1}"); j = c.find(s, j + 1)
    print(f"== {a!r}: " + ", ".join(f"{k} {len(v)}" for k, v in H.items()))
    for k, v in H.items(): print("".join(f"   {k}: {h}\n" for h in v), end="")
```

(`dw/` is `plugins/docs-workflows/`, `wc/` `plugins/workflows-core/`, `dv/` `plugins/dev-workflows/`, `pw/` `plugins/product-workflows/`.)

**The retired strings.** Live and generated counts are 0 at the head for eight of the eleven; the other three have live hits, each read in place and each true.

| String | `ee6ac5d4` (live / generated / history) | `97e1dd62` | The hits at the head, and why each stands |
|---|---|---|---|
| `Phase 1 took` | 7 / 0 / 2 | 4 / 0 / 2 | live `pw/commands/brd-intake.md:485` (*what Phase 1 took and never walks again*), `pw/commands/epics.md:661` (*the repo short names Phase 1 took*), `pw/references/brd-format.md:47` (*that `/brd-intake` Phase 1 took*) and `.claude/rules/brd-route.md:25` (*every file Phase 1 took from its own directory*): other commands' own Phase 1, not `/document`'s. History `dw/CHANGELOG.md:573` and `pw/CHANGELOG.md:1059`, past releases. In DOC it counts 0 |
| `keyed mode's Phase 1` | 1 / 1 / 0 | 0 / 0 / 1 | history `wc/CHANGELOG.md:14`, 1.94.1's own line: *It said keyed mode's Phase 1* |
| `no commit naming` (as a statement of the question's test) | 0 / 0 / 0 | 6 / 0 / 3 | none states the test. DOC:541 (the later-scan line, *found no commit naming <keys>*), DOC:1388 twice and DOC:1559 twice (R8's two forms, *No implementation record and no commit naming <keys> was found*) say what a run that went on records; `docs/maintainers/rationale.md:690` states the test as *the commit scan finds no commit (L2)* and uses the phrase in its reason (*no block and no commit naming the key can mean that nothing is built or that it was built by hand without the key in a commit message*), M6's own wording, not the test. History `dw/CHANGELOG.md:19`, `:20` twice: the same lines quoted |
| `finds no commit naming the Epic` | 0 / 0 / 0 | 0 / 0 / 0 | — (Task 3's wording, replaced by F-7) |
| `at least one ref was in scope` | 0 / 0 / 0 | 0 / 0 / 0 | — (Task 2's first wording of R6) |
| `Phase 3 built at least one ref` | 0 / 0 / 0 | 0 / 0 / 0 | — (its fix round's, replaced by F-3) |
| ``the `REPOS_PATH` question`` | 1 / 0 / 0 | 1 / 0 / 0 | live `pw/commands/prd-ground.md:91` (*where its operator answered the `REPOS_PATH` question*): `/brd-split`'s own question, unrelated and the same on the base. CPL's copy is 0 (F-10) |
| `holds no PRD, which the BRD route reaches` | 1 / 5 / 0 | 0 / 0 / 0 | — (NPO's old wording, F-11) |
| `only a slice can fail it` | 2 / 0 / 0 | 0 / 0 / 0 | — (`/specify`'s and `/create-ard`'s copies, F-11's sweep) |
| ``and leaves `/epics` unable to read it`` | 0 / 0 / 0 | 0 / 0 / 0 | — (B-N8's first replacement, rewritten by the controller) |
| `Without a PRD,` | 2 / 0 / 0 | 0 / 0 / 0 | — (the two pages, W4) |

**The new strings.**

| String | `ee6ac5d4` | `97e1dd62` (live / generated / history) | Where |
|---|---|---|---|
| `the nothing-built question` | 0 / 0 / 0 | 22 / 0 / 3 | live: DOC:248, :260 twice, :383, :493, :539, :541 twice, :547 three times, :1475, :1486; `dw/docs/getting-started.md:114`; page:52, :66, :71, :89; KD:23, :27; `.claude/rules/docs-workflows.md:39`; `docs/maintainers/rationale.md:690`. History: `dw/CHANGELOG.md:24`, `:25` twice |
| `the repositories question` | 0 / 0 / 0 | 19 / 0 / 3 | live: DOC:58, :248, :250, :254, :406 twice, :411 twice, :481, :506, :597, :614, :676, :1486; page:67, :71; KD:19; `.claude/rules/docs-workflows.md:39`; `rationale.md:690`. History: `dw/CHANGELOG.md:27`, `:32`; CPL:26 |
| `Stop — implement it first (Recommended)` | 0 / 0 / 0 | 1 / 0 / 1 | live: DOC:267, the array. History: `dw/CHANGELOG.md:17` |
| `Left out as never code:` | 2 / 0 / 0 | 6 / 0 / 2 | live: DOC:262 twice, :264 twice, :1484 (the report's line, on the base at :1413); KD:58 (§5, on the base). History: `dw/CHANGELOG.md:16`, `:42` |
| `unasked — a later scan found none` | 0 / 0 / 0 | 3 / 0 / 0 | DOC:541 (the value set), :1388 (the draft), :1559 (the report) |
| ``asserting no `kind: prd` `` | 3 / 0 / 1 | 26 / 6 / 5 | live: NPO:368, :400; `dv/commands/conformance.md:602`, `design.md:128` twice, `:283`, `implement.md:229` twice; DOC:137; RN:132; `pw/commands/create-ard.md:1026`, `:1043`, `:1080` twice, `:1087`, `:1097` twice, `:1144`, `:1256`, `:1259`, `create-prd.md:258`, `specify.md:676`, `:1417`, `:1430`, `:1446`, `:1486`. Generated: `wc/reference-parts/next-phase-offer/dev.md:179`, `:205`, `epics-precondition.md:73`, `pa.md:187`, `pe.md:208`, `pm.md:191`. History: `dv/CHANGELOG.md:19`, `dw/CHANGELOG.md:915`, `pw/CHANGELOG.md:18`, `:19`, CPL:26. On the base: DOC:134, RN:132, `create-prd.md:258` |
| `The first missing document` | 26 / 11 / 9 | 33 / 11 / 14 | live: `dv/commands/conformance.md:74` twice, `design.md:108`, `:128`, `implement.md:228`, `:229`, `:368`, `:371`, `:423`, `:435`, `:1910`, `ready.md:700` twice; DOC:150, :275 twice; RN:145, :782, :784, :785; `plugins/security-workflows/commands/scan.md:550` twice; `wc/references/components.md:122`, `:126`; NPO:361, :387, :400; PH:327 twice, :617 twice; `.claude/rules/dev-workflows-conformance.md:31`; `rationale.md:688`. Generated: the eleven of the base, in `next-phase-offer/` and `phase-handoff/require-on-main.md`. History: `dv/CHANGELOG.md:30`, `dw/CHANGELOG.md:10`, `:18`, `:29`, `:36`, `plugins/security-workflows/CHANGELOG.md:10`, `wc/CHANGELOG.md:25`, `:29` twice, `:34`, `:41`, `:48`, CPL:25, :26 |

**The citers of *The first missing document*,** by the recipe PH §4.4 itself gives (PH:617, *`grep -rln 'The first missing document' plugins/*/commands plugins/*/references` re-derives the files that hold them*), run as written: 10 files at the head — `plugins/dev-workflows/commands/conformance.md`, `design.md`, `implement.md` and `ready.md`; **`plugins/docs-workflows/commands/document.md` and `release-notes.md`**; `plugins/security-workflows/commands/scan.md`; and `plugins/workflows-core/references/components.md`, `next-phase-offer.md` and `phase-handoff.md`. `document.md` and `release-notes.md` are among them, and are the two the base lacks: in `$S/base-tree` the recipe returns the other eight, and in `$S/main-tree` (`8ee5bb80`) the same eight. §4.4 says they are *this reference, and each command and reference that cites the rule — never `/product-workflows:create-ard` or `/product-workflows:specify`*; neither is among them.

## The numbers

**Consumers whose §3.4 row stops**, by the recipe written in `.claude/rules/workflows-core-handoff.md:24`, run as it stands there:

```bash
awk '/^### 3.4/{f=1} /^### 3.5/{f=0} f' plugins/workflows-core/references/phase-handoff.md | awk -F' \\| ' '/^\| `\// && $3 ~ /^\*\*stops/ {print $1}' | grep -o '`/[a-z:-]*`' | sort -u | wc -l
# 13
```

Without the `wc -l`, at the head: `/brd-interview` `/brd-package` `/brd-proposal` `/brd-reconcile` `/brd-split` `/create-ard` `/design` `/epics` `/implement` `/prd-ground` `/prd-proposal` `/specify` `/update-spec`. The same recipe in `$S/main-tree` (`8ee5bb80`, a `git archive` copy) gives 13, the same list, and in `$S/base-tree` 13. Batch 3 adds no caller of the gate, and the two numbers are equal; the rules file says *count the thirteen with* the recipe on both sides.

## The population file

Counted from `docs/superpowers/plans/2026-11-16-ladder-order-b3-sweep-population.md` by a script that takes each section's table rows (a line beginning `|` whose first cell is neither a separator nor a header) and reads each row's last cell; nothing was re-walked here.

**The rows.** The section `## The rows` holds 84 table rows: P-1 to P-71, the measurements' §9 copied, and S3-1 to S3-13, which Task 3's subject sweep and its review added. Their `Status` cells: 45 begin `done`, 39 begin `stays true`, and **0 are `open`**.

**The walks.** A row is counted as matching where its *Match* cell begins `yes`.

| Section | Rows | Matching | What the rows are |
|---|---|---|---|
| `## Task 1 walks` | 24 | 24 | states (a) to (t) with (e1) to (e3) and (i1) to (i3) — the ledger's 23 at Task 1's return (line 25) and 24 after its fix round (line 35); (e2), the PRD under its pre-rename file name, matches *at step 1's stop, which comes first; the state cannot reach the question* |
| `## Task 2 walks` | 23 | 23 | 16 rows, and 7 under its `### Fix round 1 rows` (the ledger's *7 new walk rows match*, line 55) |
| `## Task 4 walks` | 16 | 15 | the ledger's *16 walk rows match* (line 45); the sixteenth, (n′), the same pre-rename file in a legacy unprefixed folder, reads *as expected (unchanged); the remedy's `/create-prd` clause is a pre-existing defect of the same class, reported* — the state filed as PLACEMENT-STOP-SECOND-PRD (ruling 10), not a mismatch with what the batch built |
| `## Final fix wave` | 27 | 27 | W1 to W23 for the wave's behaviour items (the fix report: *Every row: match*), and W24 to W27 for the touch-up, under its own table |

## Versions

Each version from its `plugin.json` (`python3 -c "import json; print(json.load(open('plugins/<p>/.claude-plugin/plugin.json'))['version'])"`), its `.claude-plugin/marketplace.json` entry, and the first `## [` heading of its changelog (`grep -m1 -n '^## \[' plugins/<p>/CHANGELOG.md`), against the base's and `origin/main`'s (`git show <ref>:plugins/<p>/.claude-plugin/plugin.json`):

| Plugin | `plugin.json` | marketplace | Changelog heading | Base `ee6ac5d4` | `origin/main` `8ee5bb80` |
|---|---|---|---|---|---|
| `docs-workflows` | 1.40.0 | 1.40.0 | `8:## [1.40.0] — 2026-11-16` | 1.39.7 | 1.39.8 (`8:## [1.39.8] — 2026-11-16`) |
| `workflows-core` | 1.94.1 | 1.94.1 | `8:## [1.94.1] — 2026-11-16` | 1.94.0 | **1.95.0** |
| `product-workflows` | 3.83.2 | 3.83.2 | `8:## [3.83.2] — 2026-11-16` | 3.83.1 | **3.83.2** — the same number, another release |
| `dev-workflows` | 4.68.1 | 4.68.1 | `8:## [4.68.1] — 2026-11-16` | 4.68.0 | **4.69.0** |

**Against the base**, the release is as R11 ruled, and `git diff ee6ac5d4 HEAD -- .claude-plugin/marketplace.json` changes exactly the four version lines. **Against `origin/main` it is stale**: `origin/main` holds `workflows-core` 1.95.0 and `dev-workflows` 4.69.0, above this branch's 1.94.1 and 4.68.1, and its own `product-workflows` 3.83.2, so the branch's 3.83.2 names a second release with the same number; `docs-workflows`' 1.40.0 is still above `origin/main`'s 1.39.8. R11 says *Re-read `origin/main` before the release commit; renumber if it moved*; it had not moved then (ledger line 77), and it has since. Merging `origin/main` and renumbering — with the coupling bullet, the four changelog headings, the live-check section's heading and every other text that names these four numbers — is owed before the pull request; this record does neither.

**No other plugin took a version.** `git diff --stat ee6ac5d4 HEAD -- plugins/<name>` prints nothing for `acli`, `guideline-reviewers`, `prose-style` and `security-workflows`, and their `plugin.json` and marketplace entries equal the base's (0.1.4, 1.2.10, 0.8.3, 0.12.5); for the four released plugins it prints 11, 12, 9 and 7 files. `grep -n '^## .*Unreleased' plugins/*/CHANGELOG.md | wc -l` gives 0. **The dates.** Each new section is dated 2026-11-16, the day of the release commit (`git log -1 --format='%h %ad' --date=short bb8537c2` prints `bb8537c2 2026-11-16`) and of this record (`date -u +%F`). No gate compares a section's date with the day: `check-docs.sh`'s check 18 fires only on an `— Unreleased` heading. The coupling bullet is CPL:26, *Update `workflows-core` 1.94.1 with `docs-workflows` 1.40.0 — and never `docs-workflows` 1.40.0 beside a `workflows-core` below 1.94.0*, which names `dev-workflows` 4.68.1 and `product-workflows` 3.83.2 in its body.

## Budgets

`LC_ALL=C.UTF-8 wc -m`, since a bare `wc -m` counts bytes in this container (it gives 36,148 for `CLAUDE.md`, and `wc -c` 20,310 for `.claude/rules/docs-workflows.md`); `scripts/validate-catalog.py` sets `CLAUDE_MD_WARN = 36_000`, `CLAUDE_MD_MAX = 40_000` and `RULES_FILE_WARN = 20_000`, all in characters. The files: `CLAUDE.md`, and every `.claude/rules/` file `git diff --name-only ee6ac5d4 HEAD -- .claude CLAUDE.md` lists (`CLAUDE.md` is not among them).

| File | `97e1dd62` | Base `ee6ac5d4` | `origin/main` `8ee5bb80` | Limit | Under the warning by |
|---|---|---|---|---|---|
| `CLAUDE.md` (unchanged on the branch) | 35,898 | 35,898 | 35,989 | warns 36,000, fails 40,000 | 102 |
| `.claude/rules/docs-workflows.md` | 19,998 | 19,986 | 19,986 | warns 20,000 | **2** |
| `.claude/rules/docs-workflows-gates.md` | 4,323 | 3,908 | 3,908 | warns 20,000 | 15,677 |
| `.claude/rules/plugin-updates-coupling.md` | 19,922 | 17,970 | 15,876 | warns 20,000 | 78 |

Each `origin/main` figure is `git show origin/main:<file> | LC_ALL=C.UTF-8 wc -m`, and each base figure the same for `ee6ac5d4`. These agree with the ledger's and reports' figures for the same files (lines 73, 75, 77, 80, 90, 96: `docs-workflows.md` 19,993 then 19,998; `docs-workflows-gates.md` 4,317 then 4,323; the coupling file 19,404, 19,901, 19,922; `CLAUDE.md` 35,898). Two rules files sit within 100 characters of their warning: `docs-workflows.md` (2) and the coupling file (78) — on `origin/main` the coupling file was split to 15,876, so a merge changes the second figure.

## Frozen files

`git diff --stat ee6ac5d4 HEAD -- '*.py' '*.sh' '*.mjs' scripts plugins/docs-workflows/references/gate-ledger.md` prints nothing: no script changed — `key-discovery.py` and `bounded.py` among them — and `gate-ledger.md` is untouched, as the plan's Global Constraints require.

## Generated files

`python3 scripts/reference-parts.py check-parts` exits 0 and its last line is `reference-parts check-parts: PASS -- 4 split reference(s), 3 entry file(s), 36 generated file(s) fresh`, after 117 `FLAG` lines (`| grep -c '^FLAG'`), which it prints and does not fail on. `$S/base-tree`'s and `$S/main-tree`'s own scripts on their own trees print the same line and 117 too, and the head's and the base's sets, line numbers stripped, are equal (`diff` prints nothing).

## The reviews

From the ledger, whose counts are the findings files'; read here, not re-derived.

| Review | Model | Head reviewed | Verdict and findings | Fix rounds | Final state |
|---|---|---|---|---|---|
| Pre-flight scan of the plan | the controller | the plan | ten rows, no conflict, no ruling needed (lines 9 to 22) | — | — |
| Task 1, Phase 0 | Opus | `e6702f39` | spec met; not approved: 1 Important (F1), 3 Minor (F2 to F4); one stale site sent to Task 2 (line 28) | 2: `15645ee6`, re-reviewed on Sonnet (F4 not as worded: 1 new Important, 1 Minor, line 38); `7075f441`, re-reviewed on Sonnet (both addressed, 1 Minor, line 50) | clean after two rounds; 1 Minor deferred (lines 51, 52) |
| Task 2, the later phases | Opus | `3031db14` | spec met; not approved: 2 Important (F1, F2), 5 Minor (F3 to F7); run (H) walked and its class found (line 41) | 1: `0c0b5264`, re-reviewed on Opus (F1 to F7 addressed; 8 new Minor, line 62) | clean of Important; 8 Minor deferred (lines 63 to 70, 72) |
| Task 4, `/release-notes`' offers | Opus | `1fb8de7e` | spec met; not approved: 1 Important (F1), 4 Minor to fix, 1 needing no change; three concerns judged valid (line 53) | 1: `f9a31747`, re-reviewed on Sonnet (F1 to F5 addressed, the departure sound, 1 optional nit, line 59) | clean after one round; 1 Minor deferred (lines 60, 61) |
| Task 3, pages, references, rules | Opus | `c41c47de` | spec met; not approved: 1 Important (low impact), 6 Minor, 2 sites the sweep missed (line 75) | 1: `60a28544`, re-reviewed on Sonnet (all nine addressed, no new breakage, line 82) | clean after one round (line 83) |
| Task 5, the release | Opus | `bb8537c2` | spec met save the live checks; not approved: 1 Important (I1), 10 Minor (M1 to M10) (line 84) | none of its own: to the wave (ruling 13) | fixed in the wave (re-review B, line 93; line 103) |
| Whole branch | Fable | `60a28544`, base `ee6ac5d4` | ready to merge after the fix wave: 0 Critical, 3 Important (F-1 to F-3), 11 Minor (F-4 to F-14); every ruling held — *I would overturn none* (line 86) | the wave: `762aad41`, `9842be89`, `fbd046bf` (35 items: 30 done, 2 done differently, 2 dropped by ruling, 0 not done, line 90) | below |
| The wave's re-review, half A (`762aad41`) | Opus | `fbd046bf` | every item addressed; 1 Important (N1), 4 Minor (N2 to N5) (line 92) | the touch-up `691f9e49` (ruling 17) | — |
| The wave's re-review, half B (`9842be89`, `fbd046bf`) | Opus | `fbd046bf` | every item addressed; 3 Important (N1 to N3), 10 Minor (N4 to N13); the fixer's concern 2 a pre-existing imprecision (line 93) | the touch-up `691f9e49` (ruling 17) | — |
| The touch-up's narrow re-check | Opus | `691f9e49`, base `fbd046bf` | 18 of 19 items addressed, B-N8 not; four wording items (W1 to W4); nothing that makes a run print or do anything false (line 99) | the controller's five wordings, `97e1dd62` (ruling 18) | read by no reviewer after it was applied; *Final review: clean … Parked: none* (line 101) |

## What departs from the design or the plan

The rulings file's *Departures from the process* gives each with its reason. In short: the plan was written by the controller from a dispatched measurement and built without a go-ahead (ruling 1); reviews ran beside the next task's build, and Task 5's review and the final review ran in parallel (lines 23, 79, 81); Task 4 was built before Task 3 (ruling 6); the wave's re-review was split between two reviewers (ruling 16); a touch-up followed the one wave the process allows (ruling 17); the controller applied five wordings itself, verified by the gates and not by a reviewer (ruling 18); the run paused about nine and a half hours on the account's usage limit (line 98); the close-out was written by a dispatched agent (line 104); and the final whole-branch review ran on Fable, where the design's §10 says *each batch gets an Opus review before its pull request*. On the design's text: §5.3 is amended by R1 to R10 in its *Settled while building* note (DES:168 to :187); on the plan's: R6's test was reworded twice (rulings file, R6), ruling 5 was revised by ruling 8 before it was built, and the F-11 sweep made two patch releases change behaviour (R11's row). And the release no longer stands above `origin/main` (*Versions*).

## What was not verified

- **The live checks have not been run.** TT:195 opens the section *LADDER-ORDER batch 3 — `docs-workflows` 1.40.0, `workflows-core` 1.94.1, `dev-workflows` 4.68.1, `product-workflows` 3.83.2*, whose intro (TT:197) says *no item below has been run*; it holds 20 checks (`awk '/^## LADDER-ORDER batch 3/{f=1;next} /^## /{f=0} f' docs/superpowers/to-test-on-real-project.md | grep -c '^- \*\*'` gives 20, lines 199 to 218). None has run on a real project, and the ledger records no choice of when they run. The section's heading and intro name the four version numbers *Versions* finds stale against `origin/main`.
- **Filed and told, not fixed**: DOCS-IN-CODE-REPO-SCAN (`docs/superpowers/to-fix.md:249`) and PLACEMENT-STOP-SECOND-PRD (`:243`); and, from the ledger's line 102, `conformance.md`'s own `<UNIT>: ` prefix with two meanings, `ready.md`'s `SUPPORTED` offer in its older line form, F-13's `<n>` counting clones the scan then leaves out, `.claude/rules/docs-workflows.md` 2 characters under its warning, and batch 4 open. The rulings file's *Left open* holds each with where it is recorded.
- **The last commit had no reviewer.** `97e1dd62`, the controller's five wordings, was verified by the controller's exact-match assertion and covering chain (ruling 18), and here by the chain above and by a word diff against the checker's wordings — not by a reviewer reading it after it was applied.
- **The merge with `origin/main`** was not attempted beyond the in-memory `git merge-tree` above, and nothing here was measured on a merged tree: the 15 conflicting files, the renumbered versions, the coupling file's split and `CLAUDE.md`'s 35,989 characters on `origin/main` are all ahead of the pull request.
- **Not re-derived here:** the walks' verdicts (counted, not re-walked); every scratch test in the task reports and the fix report; the reviews' findings and their counts, which are the ledger's; the implementers' and the fixer's earlier chain runs; and the population's per-row dispositions beyond the strings counted above. This record, the rulings summary and the ledger copy were not reviewed before they were committed.

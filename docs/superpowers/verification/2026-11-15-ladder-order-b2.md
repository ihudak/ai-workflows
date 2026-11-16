# LADDER-ORDER batch 2 — a keyed `/implement` stops without its specification and design — verification record

**Plan:** `docs/superpowers/plans/2026-11-15-ladder-order-b2-implement-stops.md`. **Design:** `docs/superpowers/specs/2026-11-14-ladder-order-design.md`, §2 (M1, M2, M3), §5.2, §5.5 and §11 (*Done when*). **Population:** `docs/superpowers/plans/2026-11-15-ladder-order-b2-sweep-population.md`. **Release:** `dev-workflows` 4.68.0, `workflows-core` 1.94.0, `security-workflows` 0.12.5 and `product-workflows` 3.83.1, each changelog section dated 2026-11-15. **Branch:** `feat/ladder-order-b2`, cut from `main` at `aeedacf0`, which `origin/main` still is, so the branch merged nothing. Measured at `741ee399`, the head, after the final review's fix wave, its touch-up, its micro-fix, the two dropped clauses, the last check and its fixes, and the controller's clause to the coupling bullet, before the push. This record was first written at `4e15c0c1`, on `14224194`; it is rewritten here last, every value re-derived on `741ee399`, not carried from that version. Every figure below was obtained here, with its command beside it; where a figure is the ledger's or a report's and was not re-run, the sentence says so.

The rulings summary is `2026-11-15-ladder-order-b2-rulings.md` beside this file, and the controller's ledger, verbatim, is `2026-11-15-ladder-order-b2-ledger.md`. Every *ledger line* below is a line of that file: `progress.md`'s line *n* is its line *n* + 5. *Ruling N* is row N of the rulings file.

**Where and how it was measured.** One 12-core machine (`nproc`), Python 3.15.2, git 2.43.0, node v26.13.0, uid 502 (`id -u`). Every command ran from the worktree root, `/workspace/.worktrees/ladder-order-b2`, on the tree `741ee399` commits. `git fetch origin`, then `git rev-parse origin/main` and `git merge-base HEAD origin/main` both print `aeedacf033814b2b63f8107abd7580d79826ece1`: `origin/main` has not moved from `aeedacf0` since the branch was cut, and `git log --oneline HEAD..origin/main | wc -l` prints 0. `$S` below is a scratch directory outside the repository, and `$S/main-tree` is `origin/main` unpacked there with `git archive origin/main | tar -x -C $S/main-tree`; `$S/t14224194` is `14224194` unpacked the same way, for the strings the last commits changed.

## What was verified

**The branch.** `git log --oneline aeedacf0..HEAD | wc -l` gives 32, the same with `--first-parent`, and `git log --merges --oneline aeedacf0..HEAD | wc -l` gives 0: every commit `origin/main` lacks is the branch's own, and none is a merge (ledger line 123: *main had not moved*). By task:

- the plan and the design, outside any task: `4289cc69` (the plan, and three points settled at planning in design §5.2), `1d6989e6` (the plan: eight points settled after Task 1's measurements), `97078420` (the plan and the design: a resumed run gates what it recorded, ruling 9) and `f2d70c17` (the plan: what must not change for a resumed run, ruling 20);
- Task 1, the population: `3a46bb9a`, fix round `32ae8e93`;
- Task 2, `phase-handoff` and `next-phase-offer`: `ac629efd`, fix round `c1f30676`;
- Task 3, `/implement`'s gate and four stops: `206fde49`, fix round `247cb604`;
- Task 5, `/design`, `/conformance`, `/ready` and `/security-workflows:scan` (built before Task 4, ruling 18): `0b020ca9`, fix round `e4f79925`;
- Task 4, `/implement <PRD>`'s pickers and Phase 4.5: `386d746d`, fix round `e2c809f4`;
- Task 6, the statements elsewhere: `6b314dd7`;
- Task 7, the release: `879d66f4`;
- the final fix wave: `0cdba580`, `36f9f977`, `83cf6138`, `739ea7be`, `564a9427`, `0414c27b`, `6e12cd41`, `83df1829`, `28a1d6a0`, `b35b1257`; the touch-up `8a49fd77`; the micro-fix `14224194`;
- Task 8, the close-out's first version: `4e15c0c1`;
- after it: `500f8fbc` (the two clauses ruling 23 had sent to the wave, ruling 40), `57389868` (the last check's fixes, ruling 42) and `741ee399` (the controller's clause to the coupling bullet).

**The files.** `git diff --stat aeedacf0 HEAD | tail -1` prints `64 files changed, 2176 insertions(+), 212 deletions(-)`: 22 under `plugins/workflows-core` (`phase-handoff.md`, `next-phase-offer.md`, `components.md`, `epic-picker.md` and `implementation-format.md` under `references/`, 14 regenerated files under `reference-parts/` — 12 of `next-phase-offer`, 2 of `phase-handoff` — `docs/reference/references.md`, the changelog and `plugin.json`), 14 under `plugins/dev-workflows` (the commands `conformance.md`, `design.md`, `implement.md` and `ready.md`, their four pages, `docs/getting-started.md`, `docs/reference/environment.md`, `docs/roles-and-phases.md`, `docs/workflow.md`, the changelog and `plugin.json`), 7 under `plugins/product-workflows` (`epics.md`, `specify.md`, `update-spec.md`, the `/epics` and `/update-spec` pages, the changelog and `plugin.json`), 4 under `plugins/security-workflows` (`scan.md`, its page, the changelog and `plugin.json`), six `.claude/rules/` files (`dev-workflows-conformance.md`, `dev-workflows.md`, `gates.md`, `plugin-updates-coupling.md`, `security-workflows.md`, `workflows-core-handoff.md`), `CLAUDE.md` (one table cell: `git diff --stat origin/main HEAD -- CLAUDE.md` prints 1 insertion and 1 deletion), `docs/maintainers/rationale.md`, eight under `docs/superpowers` (the plan, the population, the design, `to-fix.md`, `to-test-on-real-project.md`, and this record, the rulings and the ledger copy as `4e15c0c1` wrote them) and `.claude-plugin/marketplace.json`. `git diff --name-only aeedacf0 HEAD | grep -vE '\.md$'` lists only the marketplace and the four `plugin.json` files, and `git diff --name-only aeedacf0 HEAD -- 'plugins/*/agents' 'plugins/*/hooks' 'plugins/*/skills' 'plugins/*/scripts' scripts .github | wc -l` gives 0: no script, workflow, agent, hook or skill changed. The commit that carries this version of the three records comes after `741ee399` and changes only them.

Below, IMPL is `plugins/dev-workflows/commands/implement.md`, DES `plugins/dev-workflows/commands/design.md`, CONF `plugins/dev-workflows/commands/conformance.md`, PH `plugins/workflows-core/references/phase-handoff.md`, NPO `plugins/workflows-core/references/next-phase-offer.md`, SCAN `plugins/security-workflows/commands/scan.md`, and every line number is at `741ee399`.

## What the batch delivered against the design's §5.2

| §5.2 | Where on the tree |
|---|---|
| A fresh keyed `/implement` gates the unit's own `specification.md`, then its `design.md`, whether or not each is on disk (M3) | IMPL:363 (*Gate the unit's specification and design.*), its mapping at IMPL:366 to :369; the Invariants at IMPL:1910 |
| `absent` with the file in the unit's folder: `IMPLEMENT_SPEC_NOT_HANDED_OFF`, `IMPLEMENT_DESIGN_NOT_HANDED_OFF`, landing the file, never re-running its producer | IMPL:367; the uncommitted and committed forms at IMPL:377 and :388, :397 and :408 |
| `absent` with the file not in it: `IMPLEMENT_NEEDS_SPEC`, `IMPLEMENT_NEEDS_DESIGN`, naming what the first missing document needs, and the direct run as a way out | IMPL:368; the stops at IMPL:419 and :432 |
| A resumed run is not stopped by the four (rulings 9 and 14) | IMPL:94 (*Resuming*, step 7) |
| A unit folder outside the specs repository's work tree, tested only where `$SPECS_PATH` names an existing directory and is a git repository (rulings 31, 38, 39, 42) | IMPL:371; PH:327 and PH:617 |
| PH §3.4's `/implement` row begins `**stops**` | PH:327 |
| §4.4's rule, *The first missing document*, with its classes, its recipe and its one exception | PH:617 |
| `/implement <PRD>` lists only units holding both, and names each one left out | IMPL:228 (*Each Epic left out is counted and named*) |
| L9: `/conformance <PRD>` with no unit built stops | `CONFORMANCE_PRD_NOT_IMPLEMENTED`, CONF:141 |
| The offers of `/implement <KEY>` name what the first missing document needs where the pair is not on the default branch | NPO:380 (*The `/dev-workflows:implement` precondition*) |
| A PRD under its pre-rename file name is offered the rename through `/specify <PRD>`, never `/create-prd`, wherever `/epics` would be named (ruling 23, carried out by rulings 40 and 42) | NPO:358 (the *`/epics` precondition*); DES:128; IMPL:229; `plugins/product-workflows/commands/update-spec.md:166`; `/epics`' own `EPICS_NO_PRD`, `plugins/product-workflows/commands/epics.md:254` |
| `/conformance`'s `amend-document` offers name what a document needs where it is not on the default branch | NPO:393 |

Each id is spelled one way wherever it appears: `grep -rhoE '\bIMPLEMENT_[A-Z_]+' plugins CLAUDE.md .claude docs/maintainers README.md | sort | uniq -c` prints the four new ids (`IMPLEMENT_NEEDS_SPEC` 23, `IMPLEMENT_NEEDS_DESIGN` 24, `IMPLEMENT_SPEC_NOT_HANDED_OFF` 14, `IMPLEMENT_DESIGN_NOT_HANDED_OFF` 14) and four that `origin/main`'s IMPL already held, and no other; `grep -rhoE '\bCONFORMANCE_PRD_[A-Z_]+' …` prints `9 CONFORMANCE_PRD_NOT_IMPLEMENTED` alone.

## The gates

**The chain, run here.** Every `run:` step of `.github/workflows/validate-catalog.yml` as it stands at the head (`git diff --stat 4e15c0c1 HEAD -- .github` prints nothing), in order, as one `&&` chain, reading the chain's own exit status. With no `yaml` module in this container, the steps were extracted by the script below — the batch 1b record's script, with a `### step NN` line echoed before each step: a step is a line whose first text is `run:` and not a `#` comment, a block step (`run: |`) the deeper-indented lines after it. It extracts **35 steps**, at workflow lines 82 to 354 (it prints them); the two other `run:` matches in the file, lines 342 and 343, are inside a comment. Each step runs as the default Linux shell of a workflow step does, `bash --noprofile --norc -eo pipefail <step file>`:

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

`python3 -I $S/steps.py .github/workflows/validate-catalog.yml $S/steps` prints the chain, run as `bash -c "<the chain>"`, then `echo "CHAIN_EXIT=$?"`. The chain ran from the worktree root at `741ee399` with `git status --short` printing nothing before it and after it — this version of the three close-out files held outside the work tree, their `4e15c0c1` versions in it — from 00:18:01 to 00:29:38 UTC on 2026-11-16, and printed **`CHAIN_EXIT=0 steps=35`**, all 35 `### step` lines reached. Among its lines: `0 error(s), 0 warning(s) across 1 repo(s).`; `PASS: no dash-form requirement IDs under .`; `PASS: the spec-ID census under . equals scripts/spec-id-baseline.txt`; check-docs' `PASS: docs are consistent with the plugin(s) under …`; the four `reference-parts` checks' PASS lines (36 generated files fresh; 37 commands load the question rules; 24 run `branch-check`); `PASS: all 50 mermaid blocks in 1240 tracked markdown files parse (mermaid 11.17.2, marked 16.4.2)`; `run-state selftest: PASS (252 checks)`; `specs-git selftest: PASS (1201 checks)`; and `mutants: 23 checked, 0 stale`. This record's first version ran the same chain on a clean `14224194`, also `CHAIN_EXIT=0 steps=35` (ledger line 150).

**Then, each on its own, same tree:**

```
$ ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .
PASS: docs are consistent with the plugin(s) under plugins/dev-workflows plugins/guideline-reviewers plugins/workflows-core plugins/docs-workflows plugins/product-workflows plugins/security-workflows plugins/prose-style
rc=0
$ python3 scripts/validate-catalog.py
0 error(s), 0 warning(s) across 1 repo(s).
rc=0
```

`ASSERT_PUBLISHED=1` also printed two `check 9 cost-emitting-commands assertion not applicable` lines, for `plugins/guideline-reviewers` and `plugins/prose-style`, which ship no `docs/reference/session-cost.md`. The ledger's own chain runs (among them lines 112, 123, 137, 143, 146, 152 and 156: exit 0 at `6b314dd7`, `879d66f4`, `b35b1257`, `8a49fd77`, `14224194`, `500f8fbc` and `57389868`) are the implementers' and the fixer's; the ledger records `validate-catalog` 0/0 for `741ee399` (line 156) and no chain run on it, so this record's run is the only chain on the head.

**Re-run with this version of the three close-out files in the work tree and staged**, each exiting 0: `./scripts/check-docs.sh --root .` (PASS), `ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .` (PASS), `./scripts/check-id-grammar.sh --root .` (`PASS: no dash-form requirement IDs under .`) and `--baseline` (PASS), `python3 scripts/validate-catalog.py` (`0 error(s), 0 warning(s)`), and `node scripts/mermaid/check-mermaid.mjs --root .` (`PASS: all 50 mermaid blocks in 1240 tracked markdown files parse`, the same count as the chain's, the three files being tracked since `4e15c0c1`; none holds a mermaid block).

**Generated files.** `python3 scripts/reference-parts.py check-parts` exits 0 and prints `reference-parts check-parts: PASS -- 4 split reference(s), 3 entry file(s), 36 generated file(s) fresh`, after 117 `FLAG` lines (`| grep -c '^FLAG'`), which it prints and does not fail on; `$S/main-tree`'s own script on `origin/main` prints 117 too, and the two sets, line numbers stripped, are equal (`diff` prints nothing). The ledger's line 39 gives the same (*check-parts FLAG lines 117 before and after*), and the last check found 117 at `500f8fbc` (`last-check-findings.md`, item 8).

## The numbers

**Consumers whose §3.4 row stops**, by the recipe written in `.claude/rules/workflows-core-handoff.md:24`, run as it stands there:

```bash
awk '/^### 3.4/{f=1} /^### 3.5/{f=0} f' plugins/workflows-core/references/phase-handoff.md | awk -F' \\| ' '/^\| `\// && $3 ~ /^\*\*stops/ {print $1}' | grep -o '`/[a-z:-]*`' | sort -u | wc -l
# 13
```

Without the `wc -l`: `/brd-interview` `/brd-package` `/brd-proposal` `/brd-reconcile` `/brd-split` `/create-ard` `/design` `/epics` `/implement` `/prd-ground` `/prd-proposal` `/specify` `/update-spec`. The same recipe in `$S/main-tree` (`origin/main`, unmoved) gives 12, the same list without `/implement`. The rules file says *the thirteen consumers with a row that stops* and *count the thirteen with* the recipe; the ledger's runs say 13 (lines 55, 137, 143, 146, 152, 156).

**The citers of *The first missing document*,** by the recipe §4.4 itself gives (PH:617, *`grep -rln 'The first missing document' plugins/*/commands plugins/*/references` re-derives the files that hold them*), run as written: 8 files — `plugins/dev-workflows/commands/conformance.md`, `design.md`, `implement.md` and `ready.md`, `plugins/security-workflows/commands/scan.md`, and `plugins/workflows-core/references/components.md`, `next-phase-offer.md` and `phase-handoff.md`. §4.4 says they are *this reference, and each command and reference that cites the rule — never `/product-workflows:create-ard` or `/product-workflows:specify`*; neither is among them, and `update-spec.md` and `epics.md`, which `57389868` gave the pre-rename case, cite the *`/epics` precondition*, not the rule. In `$S/main-tree` the recipe returns nothing. Re-review B reports the same eight (ledger line 140).

**The releases.** Each version from its `plugin.json` (`python3 -c "import json; print(json.load(open('plugins/<p>/.claude-plugin/plugin.json'))['version'])"`), its `.claude-plugin/marketplace.json` entry, and the first `## [` heading of its changelog (`grep -m1 -n '^## \[' plugins/<p>/CHANGELOG.md`), against `git show origin/main:plugins/<p>/.claude-plugin/plugin.json`:

| Plugin | `plugin.json` | marketplace | Changelog heading | `origin/main` |
|---|---|---|---|---|
| `dev-workflows` | 4.68.0 | 4.68.0 | `8:## [4.68.0] — 2026-11-15` | 4.67.1 |
| `workflows-core` | 1.94.0 | 1.94.0 | `8:## [1.94.0] — 2026-11-15` | 1.93.0 |
| `security-workflows` | 0.12.5 | 0.12.5 | `8:## [0.12.5] — 2026-11-15` | 0.12.4 |
| `product-workflows` | 3.83.1 | 3.83.1 | `8:## [3.83.1] — 2026-11-15` | 3.83.0 |

Every other plugin's `plugin.json` and marketplace entry equal `origin/main`'s (`docs-workflows` 1.39.7, `prose-style` 0.8.3, `guideline-reviewers` 1.2.10, `acli` 0.1.4); `git diff origin/main HEAD -- .claude-plugin/marketplace.json` changes exactly the four version lines (8 changed lines); `git diff 4e15c0c1 HEAD -- '*/plugin.json' .claude-plugin/marketplace.json` prints nothing, so the last three commits changed no version. `grep -n '^## .*Unreleased' plugins/*/CHANGELOG.md | wc -l` gives 0. **The dates.** Each section is dated 2026-11-15, the day the release was cut (the release commit `879d66f4`, ledger line 123, is dated 2026-11-15 by `git log -1 --format=%ad --date=short`); the last three commits added lines to those sections without redating them (`git diff 4e15c0c1 HEAD -- '*/CHANGELOG.md' | grep '^[-+]## '` prints nothing), and this record is written on 2026-11-16 (`date -u +%F`). No gate compares a section's date with the day: `check-docs.sh`'s check 18 fires only on an `— Unreleased` heading, and the chain and `ASSERT_PUBLISHED=1` above both pass. `dev-workflows` and `workflows-core` take a minor (new stops, a new §3.4 row behaviour, a new §4.4 rule); `security-workflows` a patch, by ruling 27; `product-workflows` a patch: one sentence of `/specify`'s next step, one clause of `/epics`' Phase 2.7 question, a clause each of `/update-spec`'s next step and `/epics`' `EPICS_NO_PRD` for a PRD under its pre-rename file name, and the `/epics` and `/update-spec` pages (its 3.83.1 section). The coupling bullet is `.claude/rules/plugin-updates-coupling.md:25`, *Update `workflows-core` 1.94.0 with `dev-workflows` 4.68.0 and `security-workflows` 0.12.5*, whose 3.83.1 clause `741ee399` completed.

**Budgets** (`LC_ALL=C.UTF-8 wc -m`, since a bare `wc -m` counts bytes in this container: it gives 36,148 for `CLAUDE.md`; `scripts/validate-catalog.py` sets `CLAUDE_MD_WARN = 36_000`, `CLAUDE_MD_MAX = 40_000` and `RULES_FILE_WARN = 20_000`, all counted in characters). The files: `CLAUDE.md`, and every `.claude/rules/` file `git diff --name-only aeedacf0 HEAD -- .claude CLAUDE.md` lists:

| File | `741ee399` | `origin/main` (`git show origin/main:<file> \| LC_ALL=C.UTF-8 wc -m`) | Limit | Under the warning by |
|---|---|---|---|---|
| `CLAUDE.md` (one cell, same length) | 35,898 | 35,898 | warns 36,000, fails 40,000 | 102 |
| `.claude/rules/dev-workflows-conformance.md` | 8,302 | 6,326 | warns 20,000 | 11,698 |
| `.claude/rules/dev-workflows.md` | 19,743 | 19,142 | warns 20,000 | 257 |
| `.claude/rules/gates.md` | 19,991 | 19,997 | warns 20,000 | 9 |
| `.claude/rules/plugin-updates-coupling.md` | 17,970 | 14,396 | warns 20,000 | 2,030 |
| `.claude/rules/security-workflows.md` | 19,559 | 19,435 | warns 20,000 | 441 |
| `.claude/rules/workflows-core-handoff.md` | 7,334 | 6,234 | warns 20,000 | 12,666 |

`.claude/rules/dev-workflows-implement.md`, which the pre-flight scan held at 19,991 (ledger line 18), is unchanged at 19,991 (`git diff --stat aeedacf0 HEAD -- .claude/rules/dev-workflows-implement.md` prints nothing). The coupling file's 17,970 agrees with the ledger's (line 156); it was 17,672 at `57389868` and `741ee399` added the rest. The ledger's earlier budget figures, measured at each commit with `git show <sha>:<file> | LC_ALL=C.UTF-8 wc -m`, all agree in characters: the handoff rules file 7,137 at `c1f30676` (line 55); `dev-workflows.md` 19,161 at `0b020ca9` (line 71); at `6b314dd7` (line 112) `CLAUDE.md` 35,898, `dev-workflows-implement.md` 19,991, `gates.md` 19,994 (19,997 at `e2c809f4`), `dev-workflows.md` 19,743, `dev-workflows-conformance.md` 8,051 and `security-workflows.md` 19,559; the coupling file 17,192 at `879d66f4` (line 123), 17,667 at `b35b1257` (line 137) and 17,672 at `8a49fd77` (line 143); `gates.md` 19,991 at `b35b1257` (line 137). Three rules files sit within 500 characters of their warning: `gates.md` (9), `dev-workflows.md` (257) and `security-workflows.md` (441).

**Frozen files.** `git diff --stat aeedacf0 HEAD -- plugins/dev-workflows/scripts plugins/workflows-core/scripts plugins/security-workflows/scripts plugins/workflows-core/references/security-register-format.md` prints nothing: `run-state.py`, `weakness-classes.py`, `register.py` and the register format are untouched. The plan let `run-state.py` and `weakness-classes.py` change only if Task 1's measurements 8 and 7 required it (plan lines 129 and 167); ruling 7 kept `weakness-classes.py`, its selftest and the register format's §7 untouched, and the fix wave's rulings froze `run-state.py`, `weakness-classes.py` and the register format (`final-fix-wave.md`, *Discipline*).

**The population file's totals**, by the command in its header, extracted from the file (`sed -n '/^```bash$/,/^```$/p' <file> | sed -n '2,12p'`) and run as extracted:

```
rows 150 malformed []
rewrite 90 {'Task 2': 13, 'Task 3': 12, 'Task 4': 20, 'Task 5': 27, 'Task 6': 18} beyond plan 18 ruling 0 ruled 10
keep 59
later {'later 4': 1}
duplicate ids []
```

This is the total the file's header records *after fix round 1, Task 4 and Task 6*, line for line. `git log --oneline -3 -- <file>` shows its last change in `14224194` (walks FW-W15 and FW-W16); no commit since has touched it. Its *Final fix wave* section records string counts and walks, not rows, so no row is the wave's.

## The claim sweep

The subject, the scope and the searches are the population file's header and §1; its before-counts are its §2, taken at `4289cc69`, whose plugin files are `aeedacf0`'s. Counted here at `741ee399`, in `$S/main-tree` (`origin/main`, `aeedacf0`) and, for the strings the last commits changed, in `$S/t14224194`, each string wrap-insensitively — whitespace collapsed across each whole file and across the string, the match mapped back to its source line — over `plugins/`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/` and `README.md`, every file that decodes as UTF-8, not only `.md`. Each hit is put in one bucket: *history* (any `CHANGELOG.md`, any `.claude/rules/plugin-updates-coupling*.md`), *generated* (`plugins/workflows-core/reference-parts/`), else *live*. The script, the batch 1b record's, run as `python3 -I $S/wic.py '<string>' …` from the root of the tree measured:

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

(`dw/` is `plugins/dev-workflows/`, `wc/` `plugins/workflows-core/`, `sw/` `plugins/security-workflows/`, `pw/` `plugins/product-workflows/`.)

**The retired strings.** Live and generated counts are 0 at the head for eleven of the thirteen; the two strings of the removed specs question have one live hit each, the same line of the rationale, which tells the question's removal; and `where $SPECS_PATH is set and` has one live hit in unrelated text.

| String | `origin/main` (live / generated / history) | `14224194` | `741ee399` | The hits at the head, and why each stands |
|---|---|---|---|---|
| `Proceed without specs` | 2 / 0 / 1 | — | 1 / 0 / 2 | live `docs/maintainers/rationale.md:688`, the batch's own paragraph, which says the question went: *so the specs question, Point me at a specs directory or Proceed without specs, went whole (L6)* — true; history `dw/CHANGELOG.md:24`, 4.68.0's *A keyed run no longer asks where its specs are* (*is gone*), and `:5229`, 2.51.0's bullet on the Environment-prerequisites section, a past release |
| `Point me at a specs directory` | 1 / 0 / 1 | — | 1 / 0 / 3 | live `rationale.md:688`, as above; history `dw/CHANGELOG.md:24` (as above), `:1118` (4.25.0's relabelled options, a past release) and `.claude/rules/plugin-updates-coupling.md:25`, 1.94.0's bullet: what an older `/implement` still asks beside 1.94.0 — true of that pair |
| `one hard exception` | 3 / 0 / 0 | — | 0 / 0 / 0 | — |
| `this plugin's one exception` | 2 / 0 / 0 | — | 0 / 0 / 0 | — |
| `only an **in-scope** spec is gated` | 1 / 1 / 0 | — | 0 / 0 / 0 | — |
| `epic_spec` | 4 / 0 / 0 | — | 0 / 0 / 3 | `wc/CHANGELOG.md:22`, 1.94.0's *`components` §6 loses the `epic_spec` and `epic_design` rows*; `.claude/rules/plugin-updates-coupling.md:25` twice, 1.94.0's bullet: what an older `components` §6 still returns beside 4.68.0, and what 1.94.0's no longer returns beside an older `/implement` — each true of its pair |
| `epic_design` | 4 / 0 / 0 | — | 0 / 0 / 3 | the same three, beside `epic_spec` in each |
| ``no consumer of `design.md` stops`` | 1 / 0 / 1 | — | 0 / 0 / 1 | `dw/CHANGELOG.md:824`, 4.39.1's account of Phase 4.5's falling-back array, a past release |
| `with the mapping that run had` | 0 / 0 / 0 | — | 0 / 0 / 0 | — (the controller's phrase, written and withdrawn on the branch, ruling 14) |
| `and that command finds` | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | — (written by the touch-up, replaced by the micro-fix's `'<that command>' finds`) |
| ``where `$SPECS_PATH` is set and`` | 1 / 0 / 0 | 4 / 2 / 2 | 1 / 0 / 0 | live `plugins/docs-workflows/docs/commands/release-notes.md:74`, `/release-notes`' page on its draft's pull request (*where `$SPECS_PATH` is set and the PRD folder lies inside its work tree*): unrelated text, the same on `origin/main`, in a plugin the branch does not change (`git diff --stat aeedacf0 HEAD -- plugins/docs-workflows` prints nothing). The micro-fix's condition at IMPL:371, PH:327 and PH:617 reads *names an existing directory and* since `57389868` (the last check's Minor 2), and its two changelog copies, `wc/CHANGELOG.md` 1.94.0 and `dw/CHANGELOG.md` 4.68.0, *names an existing directory that is a git repository* |
| `printing other than it prints` | 0 / 0 / 0 | 3 / 2 / 0 | 0 / 0 / 0 | — (the micro-fix's pointer at IMPL:371, PH:327 and PH:617, reworded by `57389868`, the last check's Minor 3) |
| `resolve that to` | 2 / 0 / 0 | 2 / 0 / 0 | 0 / 0 / 0 | — (on `origin/main` and at `14224194`, DES's and IMPL's *Split* options, where *that* was `/create-prd`; `500f8fbc`'s rename clause put another command nearest, and `57389868` wrote *resolve `/product-workflows:create-prd <PRD>` to*, once in each file, the last check's Minor 4) |

Each *before* figure agrees with the population's §2 where it records the string: S1 `Point me at a specs directory` 1 (IMPL:318), S2 `Proceed without specs` 2 (IMPL:318, :320), S6 1 with its generated copy, S10 1 (IMPL:1366), S12 2, S13 3, S22 and S23 4 each (COMP:93, :111, :117, :119).

**The new strings**, 0 everywhere in `$S/main-tree` save the last:

| String | `741ee399` (live / generated / history) | Where |
|---|---|---|
| `IMPLEMENT_NEEDS_SPEC` | 17 / 3 / 3 | live: IMPL:16, :229, :308, :368, :369, :419, :439 twice, :441, :1910; `dw/docs/commands/implement.md:132`; PH:327 twice, :358; `.claude/rules/dev-workflows-conformance.md:31`, `dev-workflows.md:33`, `workflows-core-handoff.md:24`. Generated: `wc/reference-parts/phase-handoff/require-on-main.md:163` twice, `:194`. History: `dw/CHANGELOG.md:17`, `:27`; `wc/CHANGELOG.md:19` |
| `IMPLEMENT_SPEC_NOT_HANDED_OFF` | 10 / 2 / 2 | live: IMPL:16, :367, :377, :388, :1910; `dw/docs/commands/implement.md:131`; PH:327, :358; `.claude/rules/dev-workflows-conformance.md:31`, `workflows-core-handoff.md:24`. Generated: `require-on-main.md:163`, `:194`. History: `dw/CHANGELOG.md:16`; `wc/CHANGELOG.md:19` |
| `IMPLEMENT_NEEDS_DESIGN` | 16 / 3 / 5 | live: IMPL:16, :309, :368, :369, :432, :439 twice, :1910; `dw/docs/commands/implement.md:132`, `:134`; PH:327 twice, :358; `.claude/rules/dev-workflows-conformance.md:31`, `workflows-core-handoff.md:24`; `docs/maintainers/rationale.md:688`. Generated: `require-on-main.md:163` twice, `:194`. History: `dw/CHANGELOG.md:10`, `:17` twice, `:27`; `wc/CHANGELOG.md:19` |
| `IMPLEMENT_DESIGN_NOT_HANDED_OFF` | 10 / 2 / 2 | live: IMPL:16, :367, :397, :408, :1910; `dw/docs/commands/implement.md:131`; PH:327, :358; `.claude/rules/dev-workflows-conformance.md:31`, `workflows-core-handoff.md:24`. Generated: `require-on-main.md:163`, `:194`. History: `dw/CHANGELOG.md:16`; `wc/CHANGELOG.md:19` |
| `CONFORMANCE_PRD_NOT_IMPLEMENTED` | 8 / 0 / 1 | live: CONF:74, :105, :141, :662; `dw/docs/commands/conformance.md:37`, `:60`; `.claude/rules/dev-workflows-conformance.md:13`; `rationale.md:688`. History: `dw/CHANGELOG.md:36` |
| `Gate the unit's specification and design.` | 1 / 0 / 0 | IMPL:363, the section's title |
| `The first missing document` | 26 / 11 / 9 | live: CONF:74 twice; DES:108, :128; IMPL:228, :229, :368, :371, :423, :435, :1910; `dw/commands/ready.md:700` twice; SCAN:550 twice; `wc/references/components.md:122`, `:126`; NPO:361, :380, :393; PH:327 twice, :617 twice; `.claude/rules/dev-workflows-conformance.md:31`; `rationale.md:688`. Generated: `wc/reference-parts/next-phase-offer/dev.md:172`, `:185`, `:198`, `epics-precondition.md:66`, `pa.md:180`, `pe.md:201`, `pm.md:184`; `require-on-main.md:163` twice, `:249` twice. History: `dw/CHANGELOG.md:17`; `sw/CHANGELOG.md:10`; `wc/CHANGELOG.md:10`, `:14` twice, `:19`, `:26`, `:33`; `.claude/rules/plugin-updates-coupling.md:25`. At `14224194` it was 22 / 5 / 8: `500f8fbc`'s two clauses added NPO:361, :393, DES:128, IMPL:229 and the five `next-phase-offer` parts that carry the precondition |
| `is outside the work tree of SPECS_PATH` | 2 / 1 / 0 | live: IMPL:371, PH:617. Generated: `require-on-main.md:249`. Outside the scope, `docs/superpowers/to-fix.md` carries it once (ATPATH-OUTSIDE-TREE) and `docs/superpowers/to-test-on-real-project.md` twice, the live check at `:180` expecting it and the one at `:179` its absence |
| ``names an existing directory and `git -C`` | 3 / 2 / 0 | live: IMPL:371, PH:327, PH:617 — the outside-tree condition's three sites, as ledger line 156 says. Generated: `require-on-main.md:163`, `:249`. 0 at `14224194` |
| `under its pre-rename file name` | 15 / 8 / 9 | live: CONF:74; DES:117, :128; IMPL:229, :425, :426; `dw/commands/ready.md:700`; `pw/commands/create-ard.md:279`, `epics.md:254`, `specify.md:322`, `update-spec.md:166`; NPO:358; PH:321, :322, :617. Generated: `next-phase-offer/dev.md:169`, `epics-precondition.md:63`, `pa.md:177`, `pe.md:198`, `pm.md:181`; `require-on-main.md:157`, `:158`, `:249`. History: `dw/CHANGELOG.md:28`; `pw/CHANGELOG.md:10`, `:16` (3.83.1), `:68`, `:84`; `wc/CHANGELOG.md:14`, `:26` (1.94.0), `:103`, `:108`. Not new to the branch: on `origin/main` it is 4 / 2 / 4, batch 1's `create-ard.md:279`, `specify.md:322` and PH:321, :322 with their generated copies; at `14224194` 10 / 3 / 5. `500f8fbc` and `57389868` added NPO:358, DES:128, IMPL:229, `update-spec.md:166` and `epics.md:254`, with the five `next-phase-offer` parts |

A plain `grep -rhoE` per id over the same scope (above) gives the same totals as the live, generated and history buckets added (23, 14, 24, 14; 9), the ids holding no whitespace.

## The walks

Counted from the population file, not re-walked here. A row is counted as matching where every one of its result cells begins `Matches`, by a script that takes each section's table rows whose first cell is a walk id (`W-`, `T5-W`, `T4-W`, `FW-W`). The file has not changed since `14224194`, whose commit added FW-W15 and FW-W16:

| Section | Rows | Matching | What the rows are |
|---|---|---|---|
| `## Task 3 walks` | 51 | 51 | W-1 to W-43, walked before Task 3's edit (the ledger's *walk 43/43*, line 53) — W-1 to W-28 each with four result cells, first run, later run, companion run and tasks-only run, 112 cells, all `Matches`; four re-walk rows marked *(again)* (the first, *W-1, W-8, W-15, W-22 (again)*); and W-44 to W-47, added by fix round 1 (line 76) |
| `## Task 5 walks` | 66 | 66 | T5-W1 to T5-W54 (the ledger's *walk 54/54*, line 71) and T5-W55 to T5-W66, added by fix round 1 (line 92) |
| `## Task 4 walks` | 50 | 50 | T4-W1 to T4-W31 (*walk 31/31*, line 87), ten re-walk rows marked *(again)*, and T4-W32 to T4-W40, added by fix round 1 (line 101) |
| `## Final fix wave` | 16 | 16 | FW-W1 to FW-W16, under its `### Final fix wave walks`; FW-W15 and FW-W16 are the micro-fix's. The section also holds 64 rows of string counts, before and after, for the wave's items, which are counts, not walks |

The walks' line numbers are at each task's commit, or the wave's. No walk row covers `500f8fbc`'s or `57389868`'s pre-rename case; the last check walked it instead (`last-check-findings.md`, item 4: `/specify <PRD>` on an idea-route folder holding only a pre-rename file reaches its *Gate the PRD* and stops with the rename form), and the fixer walked `/epics`' `EPICS_NO_PRD` (ledger line 156).

## The reviews

From the ledger and the findings files in the scratch directory, whose counts are the ledger's.

| Review | Model | Head reviewed | Verdict and findings | Fix rounds | Final state |
|---|---|---|---|---|---|
| Pre-flight scan of the plan | the controller | the plan | eight rows; one conditional (`weakness-classes.py` changed only if measurement 7 requires) and one budget constraint | — | the conditional closed by ruling 7 (unchanged); the constraint held |
| Task 1, the population | Opus (line 22) | `3a46bb9a` | Needs fixes: 7 Important, 5 Minor | 1 (`32ae8e93`), re-reviewed on Sonnet | all addressed, no Important breakage; 1 Minor deferred |
| Task 2, `phase-handoff` and `next-phase-offer` | Opus | `ac629efd` | Needs fixes: 3 Important (I1 to I3, I2 the controller's own phrase), 8 Minor | 1 (`c1f30676`), re-reviewed on Opus | all addressed, the six cases applying cleanly, no Critical or Important breakage; 6 Minor deferred |
| Task 3, `/implement`'s gate and stops | Opus | `206fde49` | Needs fixes: 2 Important, 6 Minor | 1 (`247cb604`), re-reviewed on Opus | no Critical or Important open; Minor 5 fixed in the Invariants, not on the page; 2 new Minor; 7 Minor deferred in all |
| Task 5, the commands naming `/implement` | Opus | `0b020ca9` | Needs fixes: 4 Important (all in `/design`), 10 Minor | 1 (`e4f79925`, with the SCAN clause), re-reviewed on Opus | all addressed, four walks of `/design`'s Phase 0 holding, no Critical or Important breakage; 6 Minor deferred |
| Task 4, `/implement <PRD>` and Phase 4.5 | Opus | `386d746d` | Needs fixes: 1 Important (the row-G stop catching a tree that is no git repository), 9 Minor; the implementer's decisions judged sound | 1 (`e2c809f4`, with COMP:122), re-reviewed on Opus | all addressed, seven walks holding, no stop on an unmanaged tree; 7 Minor deferred |
| Task 6, the statements elsewhere | Opus | `6b314dd7` | Approved: 0 Critical, 0 Important, 6 Minor | none | 7 Minor deferred (its six and one leftover, `conformance.md:314`) |
| Task 7, the release | Opus | `879d66f4` | Needs fixes: 1 Important (I1, a false *as before*), 8 Minor; the live-check section holds 18, not 17 | none of its own: into the wave (ruling 29) | I1, M1 to M6 and M8 fixed in the wave; M7, the patch, stands |
| Whole branch | Fable | `879d66f4`, base `aeedacf0` | With fixes: 0 Critical, 3 Important (F-1 to F-3), 9 Minor (F-4 to F-12); all 34 deferred minors real, none worse than minor; no ruling overturned, four flagged | the wave, ten commits `0cdba580` to `b35b1257` | below |
| The wave's re-review, half A (commands and pages) | not named in the ledger | `b35b1257` | 27 of 28 items addressed, F-10 not as worded; 7 Minor; 4 copies differing; one out-of-scope gap (F-2's class in four more commands) | the touch-up (`8a49fd77`) | — |
| The wave's re-review, half B (references, rules, release text) | not named in the ledger | `b35b1257` | every item addressed; 1 new Important (N1); 9 Minor (N2 to N10); the same out-of-scope gap | the touch-up (`8a49fd77`) | — |
| The touch-up check (the narrow re-check) | Opus | `8a49fd77`, base `b35b1257` | every touch-up item addressed, the fixer's two departures sound; 1 new Important (the outside-tree test firing on a specs tree that is no git repository); 4 Minor | the micro-fix (`14224194`) | read by the controller (line 146), then by the last check |
| The last check | Opus | `14224194` and `500f8fbc`, read from `git archive 500f8fbc` | all eight items hold (the outside-tree test reproduced in its four cases, nine rows, and an extra one, a set-but-empty `$SPECS_PATH`; the sentence one string; the precondition's new case true of `/specify`'s own stop; the `/conformance` line matching `/conformance` clause by clause); 1 Important (`/update-spec`'s copy of the `/epics` remedy without the pre-rename case), 5 Minor, and this record stale | `57389868`, then `741ee399` | verified by the controller's script comparison with the checker's wordings and by the gates, not by a reviewer after application (ruling 42); *Parked: none* (line 157) |

## What departs from the design or the plan

The rulings file's *Departures from the process* gives each with its reason. In short: Task 5 was built before Task 4 (ruling 18); every task from Task 2 on was built while an earlier task's review or re-review ran; the final review ran in parallel with Task 7's review (ruling 28); the wave's one re-review was split between two reviewers (ruling 36); the one fix wave was followed by five more commits — a touch-up, a micro-fix, the two dropped clauses, the last check's fixes and the controller's clause to the coupling bullet (rulings 37, 39, 40, 42) — with a last check between them (ruling 41); the final whole-branch review ran on Fable, where the design's §10 says *each batch gets an Opus review before its pull request*; the plan's Task 8 names the controller as this record's writer, and a close-out writer was dispatched instead, and resumed (ledger lines 20, 149, 158). On the plan's text: *A direct run (no key) resolves no unit and is byte-identical in behaviour* (plan line 35) has the one exception below; *every run for the unit* (M3) is read as every fresh keyed run (rulings 9, 14), the plan's *What must not change* reworded to match (ruling 20); `/design`'s tests, which the plan froze, change on a tree that is no git repository (ruling 22) and before its enumeration on rows I and G (ruling 34); `product-workflows` is released (ruling 8), and its 3.83.1 grew in the last commits to `/update-spec` and `/epics`' `EPICS_NO_PRD` (ruling 42); and `weakness-classes.py`, which the plan allowed to change if measurement 7 required, is untouched (ruling 7).

**The one exception to "a direct run is unchanged"** (the final review's F-11, ruled to take no text change and to be recorded here, ruling 35). `/implement` Phase 4.5 (IMPL:1481; IMPL:1472 at `879d66f4`) now presents §4.3's **gated — stopping** consent array *whichever of `specification.md` and `design.md` the set holds*, where `origin/main`'s IMPL:1366 presented the **gated — falling back** array for an annotated `design.md` alone (*because no consumer of `design.md` stops on row F*). A direct run reaches it only where a spec-folder token under `$SPECS_PATH` added a `design.md`, step 7.5 annotated that file alone, and the default branch lacks it: on `main` that run saw the falling-back array; now it sees the stopping one. `phase-handoff` §4.1's any-row rule — one stopping row makes an artifact a stopping one — makes the new array correct by class, so no text changed. Not re-walked here; the statement is the final review's.

## Found while measuring

- **The live-check section's intro is behind the release it describes.** `docs/superpowers/to-test-on-real-project.md:171` says `product-workflows` 3.83.1 *changes one sentence of `/specify`, one clause of `/epics` and the `/epics` page*; since `57389868` its changelog section also lists `/update-spec`'s next step and `/epics`' `EPICS_NO_PRD` for a PRD under its pre-rename file name, and the `/update-spec` page, and `741ee399` completed the coupling bullet to match. The file was last changed in `14224194` (`git log --oneline -1 -- docs/superpowers/to-test-on-real-project.md`).
- **No live check covers the pre-rename case** that `500f8fbc` and `57389868` added: the section's 20 items (below) hold no `/update-spec` item, no `EPICS_NO_PRD` item and no item on a folder holding its PRD under the old file name.

Neither is an edit this record makes; both are told in the close-out's report.

## What was not verified

- **The live checks have not been run.** `docs/superpowers/to-test-on-real-project.md:169` opens the section *LADDER-ORDER batch 2 — `dev-workflows` 4.68.0, `workflows-core` 1.94.0, `security-workflows` 0.12.5, `product-workflows` 3.83.1*, whose intro says *no item below has been run*; it holds 20 checks (`awk '/^## LADDER-ORDER batch 2/{f=1;next} /^## /{f=0} f' docs/superpowers/to-test-on-real-project.md | grep -c '^- \*\*'` gives 20, lines 173 to 192). None has run on a real project, and the ledger records no choice of when they run (line 148), so the design's §11 item 4 is half done for this batch, as for batches 1 and 1b. The file is unchanged since `14224194`, which reworded the items at `:179` and `:180`; no item has been added or reworded since this record's first version.
- **Filed, not fixed**: ATPATH-OUTSIDE-TREE (`docs/superpowers/to-fix.md:232`), batch 1's `/specify`, `/create-ard` and `/epics` on an `@<path>` folder outside the specs work tree. The rulings file's *Left open* holds the rest: `/design`'s and `/ready`'s silent re-mapping of such a folder; `components` §6's known limit (COMP:89); the `<merge-clause>` sentence's reach at NPO:380; the offers owed by batches 3 and 4 in design §5.5; COMP:126's uncovered case; two concerns of the fix report and one observation of the last check with no ledger line.
- **Ruling 23's two `next-phase-offer` edits**, which this record's first version found missing at `14224194`, were carried out in `500f8fbc` (ruling 40): NPO:358 names the rename through `/specify <PRD>` for a pre-rename PRD, and NPO:393 says what `/conformance`'s `amend-document` offers name where a document is not on the default branch. The last check then found one copy the clause had left behind, `/update-spec`'s, fixed in `57389868` with `/epics`' own `EPICS_NO_PRD` (ruling 42).
- **What no reviewer read after it was applied.** `14224194` and `500f8fbc` were read by a narrow Opus check (`last-check-findings.md`: eight items hold, one Important and five Minor found). Its fixes, `57389868`, and the controller's clause, `741ee399`, were verified only by the controller's script comparison of the applied text with the checker's wordings and by the gates (ruling 42; ledger line 156) — and here by this record's chain.
- **The one exception to "a direct run is unchanged"**, above, is the final review's reading, not re-walked here.
- **Not re-derived here:** the walks' verdicts (counted, not re-walked); every scratch test in the task reports, the fix report and the last check (F-2's `cat-file` and `--show-toplevel` transcripts, the micro-fix's reproduction, the last check's cases, the fixer's empty-`$SPECS_PATH` case); the controller's script comparison of `57389868` with the checker's wordings; the population's per-row dispositions and its after-counts beyond the strings counted above; the reviews' findings and their counts, which are the ledger's; and the implementers' and the fixer's earlier chain runs. This record, the rulings summary and the ledger copy were not reviewed before they were committed.

## After this record

One commit follows the tree this record measured (`741ee399`) and the ledger copy beside it, made by the controller to close the two findings under *Found while measuring*: `docs/superpowers/to-test-on-real-project.md`'s batch 2 section now says in its intro all that `product-workflows` 3.83.1 changes (one sentence of `/specify`, one clause of `/epics`' Phase 2.7 question, `/epics`' `EPICS_NO_PRD` remedy and `/update-spec`'s next step for a PRD still under its pre-rename file name, and the two pages), and gains one item, *A PRD still under its pre-rename file name*, so the section holds 21 items where this record says 20 — `awk 'NR>=169 && NR<=194 && /^- \*\*/' docs/superpowers/to-test-on-real-project.md | wc -l` prints 21. The commit changes that file and this section, and no file under `plugins/`, `.claude/` or `scripts/`; `./scripts/check-docs.sh --root .`, `./scripts/check-id-grammar.sh --root .` and the mermaid gate were run on it and exit 0, and the pull request's CI runs the whole chain on it. None of the 21 items has been run. No reviewer read this commit.

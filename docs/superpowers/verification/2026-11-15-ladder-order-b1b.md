# LADDER-ORDER batch 1b — `/epics` stops on an unlanded PRD, and two fixes — verification record

**Plan:** `docs/superpowers/plans/2026-11-15-ladder-order-b1b-epics-gate.md`. **Design:** `docs/superpowers/specs/2026-11-14-ladder-order-design.md`, §2 (M8, M9, M10), §5.5, §5.6 and §11 (*Done when*). **Population:** `docs/superpowers/plans/2026-11-15-ladder-order-b1b-sweep-population.md`. **Release:** `product-workflows` 3.83.0, `workflows-core` 1.93.0 and `dev-workflows` 4.67.1, each changelog section dated 2026-11-15. **Branch:** `feat/ladder-order-b1b`, cut from `main` at `632e73d6` with the plan commit `e1b64243` on it, and `main` merged twice: `d48d439f` (PR #200) at `3878e7be`, and `ec60ad47` (PR #202) at `88f84f6c`. Measured at `61a6d172`, the head, after the final review's fix wave, its two addenda, its touch-up and the controller's one design line, before the push. Written last. Every figure below was obtained here, with its command beside it; where a figure is the ledger's or a report's and was not re-run, the sentence says so.

The rulings summary is `2026-11-15-ladder-order-b1b-rulings.md` beside this file, and the controller's ledger, verbatim, is `2026-11-15-ladder-order-b1b-ledger.md`. Every *ledger line* below is a line of that file: `progress.md`'s line *n* is its line *n* + 5.

**Where and how it was measured.** One 12-core machine (`nproc`), Python 3.15.2, git 2.43.0, node v26.13.0, uid 502 (`id -u`). Every command ran from the worktree root, `/workspace/.worktrees/ladder-order-b1b`, on the tree `61a6d172` commits; the gate chain ran before this record and the two files beside it were added, and the checks named as re-run after them ran with the three in the tree. `git fetch origin`, then `git merge-base HEAD origin/main` prints `ec60ad47`, which is `origin/main`, and `git log --oneline HEAD..origin/main | wc -l` prints 0. `$S` below is a scratch directory outside the repository.

## What was verified

**The branch.** `git log --oneline ec60ad47..HEAD | wc -l` gives 27, and the same with `--first-parent` lists the same 27, so every commit `origin/main` lacks is the branch's own, the two merges of `main` among them:

- the plan and the design: `e1b64243` (decisions M8 to M10, the design's §5.6 and the plan), and three design commits outside any task: `3ec93929` (§5.6, five points settled once the population was measured), `72824f0c` (§5.6, the `/update-spec` fix carries a change) and `61a6d172` (§5.6 (4), the narrow re-check's one Minor, ledger line 125);
- Task 1, the population: `de738147`, `1ee281b3`;
- Task 2, `phase-handoff` and `next-phase-offer`: `47052c37`, `587eba32`;
- Task 3, `/epics`: `72a8b164`, `bcadfa7c`;
- Task 5, the two fixes (built before Task 4, rulings file ruling 11): `3c3e2eeb`, `94a49afb`, `8cb4c65a`, `ec54b2f1`, `37dfb05c`;
- Task 4, the statements and offers elsewhere: `a102b42c`, `56d853b5`;
- Task 6, the merges and the release: `3878e7be`, `88f84f6c`, `f0ea1be1`;
- the final fix wave: `ffd84234`, `ff7ac30c`, `cf9faafb`, `bfbbf7d4`; addendum 1 `0dd68fdc`; addendum 2 `f24b5430`; the touch-up `887b4580`.

`git diff --name-only ec60ad47 HEAD | wc -l` gives 49 files: 20 under `plugins/product-workflows` (nine commands — `brd-intake`, `create-ard`, `create-prd`, `epics`, `idea`, `prd-ground`, `specify`, `update-prd`, `update-spec` — eight command pages and `docs/roles-and-phases.md`, the changelog and `plugin.json`), 13 under `plugins/workflows-core` (`phase-handoff.md`, `next-phase-offer.md`, `document-lineage.md`, eight regenerated files under `reference-parts/`, the changelog and `plugin.json`), 6 under `plugins/dev-workflows` (four pages, the changelog and `plugin.json`), three `.claude/rules/` files (`plugin-updates-coupling.md`, `product-workflows.md`, `workflows-core-handoff.md`), `docs/maintainers/rationale.md`, five under `docs/superpowers` (the plan, the population, the design, `to-fix.md`, `to-test-on-real-project.md`) and `.claude-plugin/marketplace.json`. `git diff --name-only ec60ad47 HEAD | grep -vE '\.md$'` lists only the marketplace and the three `plugin.json` files: no script, workflow, agent, hook or skill changed. `CLAUDE.md` is not among the 49.

Below, EP is `plugins/product-workflows/commands/epics.md`, PH `plugins/workflows-core/references/phase-handoff.md`, ARD `plugins/product-workflows/commands/create-ard.md`, UPS `plugins/product-workflows/commands/update-spec.md`, and every line number is at `61a6d172`.

## What the batch delivered against the design's §5.6

| §5.6 | Where on the tree |
|---|---|
| `/epics` Phase 0 executes `require-on-main` on the PRD folder's `prd.md`, after the preflight, step 1a and the branch check, before step 1b's table | EP:195 (*Gate the PRD.*), the mapping by `stopped` first at EP:197, `pass` / `pass_amending` / `unmanaged` / `absent` at EP:198–201 |
| `absent` waits for step 1b; where its table accepts, `EPICS_PRD_NOT_HANDED_OFF` in the uncommitted or committed form | EP:316 (*Stop on a PRD never handed off*), the two forms at EP:331 and EP:349, *Neither form is a plugin gap, so `emit-block` does not fire.* at EP:359 |
| The gate in the Invariants | EP:1305 |
| PH §3.4's row, beginning `**stops**`, with the behaviour change dated | PH:339 |
| The threat-model line names `/create-prd` where the PRD folder holds no `prd.md` (M9) | ARD:904 |
| `/update-spec` reads and records a differing grounding file at the default branch's copy (M10) | UPS:81 (the differing-copy test, `hash-object -- "./<path>" 2>/dev/null` against `rev-parse`), cited by UPS:59, :68, :94, :137, :158 and :198; `document-lineage` §1 at `plugins/workflows-core/references/document-lineage.md:23` |

The id is spelled one way wherever it appears: `grep -rhoE '\bEPICS_[A-Z_]*(HANDED|HANDOFF)[A-Z_]*' plugins CLAUDE.md .claude docs/maintainers README.md | sort | uniq -c` prints `25 EPICS_PRD_NOT_HANDED_OFF` and nothing else; `grep -c` and `grep -o … | wc -l` both give 7 in EP, and the command's page names it once (`plugins/product-workflows/docs/commands/epics.md:71`).

## The gates

**The chain, run here.** Every `run:` step of `.github/workflows/validate-catalog.yml` as it stands at the head, in order, as one `&&` chain, reading the chain's own exit status. With no `yaml` module in this container, the steps were extracted by the script below: a step is a line whose first text is `run:` and not a `#` comment, a block step (`run: |`) the deeper-indented lines after it. It extracts **35 steps** (workflow lines 82 to 354; the two other `run:` matches in the file, lines 342 and 343, are inside a comment) and runs each as the default Linux shell of a workflow step does, `bash --noprofile --norc -eo pipefail <step file>`:

```python
import re, sys
L = open(sys.argv[1], encoding="utf-8").read().split("\n"); out = sys.argv[2]; steps = []; i = 0
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
            steps.append("\n".join(b[cut:] for b in body)); i = j; continue
        steps.append(rest)
    i += 1
for n, s in enumerate(steps, 1): open(f"{out}/step-{n:02d}.sh", "w").write(s + "\n")
print(" && ".join(f"bash --noprofile --norc -eo pipefail {out}/step-{n:02d}.sh" for n in range(1, len(steps) + 1)))
print("steps", len(steps), file=sys.stderr)
```

`python3 -I $S/steps.py .github/workflows/validate-catalog.yml $S/steps` prints the chain. The run itself used a longer form of this script that also prints a `### step NN` line before each step; the 35 step files the two write are byte-identical (`cmp` on each pair). The chain ran from the worktree root at `61a6d172`, before the three close-out files were added, from 13:53:33 to 14:05:17 UTC, and printed **`CHAIN_EXIT=0 steps=35`**. Among its lines: `0 error(s), 0 warning(s) across 1 repo(s).`; `PASS: no dash-form requirement IDs under .`; `PASS: the spec-ID census under . equals scripts/spec-id-baseline.txt`; check-docs' `PASS: docs are consistent with the plugin(s) under …`; the four `reference-parts` checks' PASS lines (36 generated files fresh; 37 commands load the question rules; 24 run `branch-check`); `PASS: all 50 mermaid blocks in 1232 tracked markdown files parse (mermaid 11.17.2, marked 16.4.2)`; `specs-git selftest: PASS (1201 checks)`; and `mutants: 23 checked, 0 stale`. `git status --short` printed nothing after it.

**Then, each on its own, same tree:**

```
$ ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .
PASS: docs are consistent with the plugin(s) under plugins/dev-workflows plugins/guideline-reviewers plugins/workflows-core plugins/docs-workflows plugins/product-workflows plugins/security-workflows plugins/prose-style
rc=0
$ python3 scripts/validate-catalog.py
0 error(s), 0 warning(s) across 1 repo(s).
rc=0
```

The ledger's own chain runs (lines 106, 116, 121 and 124: exit 0 at `f0ea1be1`, `bfbbf7d4`, `f24b5430` and `887b4580`) are the fixer's and implementers'; this run is the one on the head.

**Re-run after the three close-out files were added and staged**, each exiting 0: `./scripts/check-docs.sh --root .` (PASS), `ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .` (PASS), `./scripts/check-id-grammar.sh --root .` (`PASS: no dash-form requirement IDs under .`) and `--baseline` (PASS), `python3 scripts/validate-catalog.py` (`0 error(s), 0 warning(s)`), and `node scripts/mermaid/check-mermaid.mjs --root .`, which printed `PASS: all 50 mermaid blocks in 1235 tracked markdown files parse (mermaid 11.17.2, marked 16.4.2)` — three files more than the chain's 1232, none holding a mermaid block.

## The numbers

**Consumers whose §3.4 row stops**, by the recipe written in `.claude/rules/workflows-core-handoff.md:24`, run as it stands there:

```bash
awk '/^### 3.4/{f=1} /^### 3.5/{f=0} f' plugins/workflows-core/references/phase-handoff.md | awk -F' \\| ' '/^\| `\// && $3 ~ /^\*\*stops/ {print $1}' | grep -o '`/[a-z:-]*`' | sort -u | wc -l
# 12
```

Without the `wc -l`: `/brd-interview` `/brd-package` `/brd-proposal` `/brd-reconcile` `/brd-split` `/create-ard` `/design` `/epics` `/prd-ground` `/prd-proposal` `/specify` `/update-spec`. The same recipe over `git show origin/main:plugins/workflows-core/references/phase-handoff.md` gives 11; the rules file says *the twelve consumers with a row that stops*.

**The releases.** Each version from its `plugin.json` (`python3 -c "import json; print(json.load(open('plugins/<p>/.claude-plugin/plugin.json'))['version'])"`), its `.claude-plugin/marketplace.json` entry, and the first `## [` heading of its changelog (`grep -m1 -n '^## \[' plugins/<p>/CHANGELOG.md`), against `git show origin/main:plugins/<p>/.claude-plugin/plugin.json`:

| Plugin | `plugin.json` | marketplace | Changelog heading | `origin/main` |
|---|---|---|---|---|
| `product-workflows` | 3.83.0 | 3.83.0 | `8:## [3.83.0] — 2026-11-15` | 3.82.1 |
| `workflows-core` | 1.93.0 | 1.93.0 | `8:## [1.93.0] — 2026-11-15` | 1.92.0 |
| `dev-workflows` | 4.67.1 | 4.67.1 | `8:## [4.67.1] — 2026-11-15` | 4.67.0 |

Every other plugin's `plugin.json` and marketplace entry equal `origin/main`'s (`docs-workflows` 1.39.7, `security-workflows` 0.12.4, `prose-style` 0.8.3, `guideline-reviewers` 1.2.10, `acli` 0.1.4), and `git diff origin/main HEAD -- .claude-plugin/marketplace.json` changes exactly the three version lines. `product-workflows` and `workflows-core` take a minor, a new stop on a run that went on and a new §3.4 row; `dev-workflows` a patch, pages only. The coupling bullet is `.claude/rules/plugin-updates-coupling.md:24`, *Update `workflows-core` 1.93.0 with `product-workflows` 3.83.0*.

**Budgets** (`LC_ALL=C.UTF-8 wc -m`; `scripts/validate-catalog.py` sets `CLAUDE_MD_WARN = 36_000`, `CLAUDE_MD_MAX = 40_000` and `RULES_FILE_WARN = 20_000`, all counted in characters). The files: `CLAUDE.md`, and the `.claude/rules/` files `git diff --name-only ec60ad47 HEAD -- .claude CLAUDE.md` lists:

| File | `61a6d172` | `origin/main` (`git show origin/main:<file> \| LC_ALL=C.UTF-8 wc -m`) | Limit | Under the warning by |
|---|---|---|---|---|
| `CLAUDE.md` (unchanged) | 35,898 | 35,898 | warns 36,000, fails 40,000 | 102 |
| `.claude/rules/plugin-updates-coupling.md` | 14,396 | 12,681 | warns 20,000 | 5,604 |
| `.claude/rules/product-workflows.md` | 17,529 | 17,016 | warns 20,000 | 2,471 |
| `.claude/rules/workflows-core-handoff.md` | 6,234 | 5,891 | warns 20,000 | 13,766 |

`.claude/rules/docs-workflows.md`, which the plan said takes no growth, is unchanged at 19,986. The ledger's budget figures, measured here at each commit with `git show <sha>:<file> | LC_ALL=C.UTF-8 wc -m`, all agree in characters: the handoff rules file 6,145 at `587eba32` (ledger line 47); `product-workflows.md` 17,477 at `a102b42c` (line 81) and 17,539 at `37dfb05c` and `56d853b5` (lines 84, 94); `CLAUDE.md` 35,972 and `docs-workflows.md` 19,986 at `56d853b5` (line 94); the coupling file 14,292 at `f0ea1be1` (line 106) and 14,396 at `bfbbf7d4` (line 116). The plan's own figures are `main` `632e73d6`'s (`CLAUDE.md` 35,972, coupling 19,749, `product-workflows.md` 17,026, handoff 5,802, each re-measured here at that commit); `main` then moved them by its own merges, #202 among them, which moved the coupling file's older bullets to a fourth history file (ledger line 106).

**Generated files.** `python3 scripts/reference-parts.py check-parts` exits 0 and prints `reference-parts check-parts: PASS -- 4 split reference(s), 3 entry file(s), 36 generated file(s) fresh`, after 117 `FLAG` lines (`| grep -c '^FLAG'`), which it prints and does not fail on; `origin/main`, unpacked with `git archive origin/main | tar -x -C $S/main-tree` and checked with its own script, prints 115. The ledger's line 38 gives the same two figures for Task 2's new row (*115 -> 117, both "the folder above" in the new row, non-failing*).

**The population file's totals**, by the command in its header (`python3 -I - docs/superpowers/plans/2026-11-15-ladder-order-b1b-sweep-population.md <<'EOF' …`, run verbatim):

```
rows 143 malformed []
rewrite 80 {'Task 2': 14, 'Task 3': 18, 'Task 4': 48} beyond plan 32 ruling 4
keep 53
later {'later 2': 7, 'later 3': 2, 'later 4': 1}
duplicate ids []
```

This is the last total the header records, *After the wave's addendum, which added P-142 and P-143*. Task 5 kept walks, not rows (the population's *Final fix wave* intro), so no row is Task 5's.

## The claim sweep

The subject, the scope and the searches are the population file's header and §1; the before-counts are its §2, taken at `e1b64243`, whose plugin files are `632e73d6`'s. Counted here at `61a6d172`, and for comparison at `632e73d6` (unpacked with `git archive 632e73d6 | tar -x -C $S/base-tree`), each string wrap-insensitively — whitespace collapsed across each whole file and across the string, the match mapped back to its source line — over `plugins/`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/` and `README.md`, every file that decodes as UTF-8, not only `.md`. Each hit is put in one bucket: *history* (any `CHANGELOG.md`, any `.claude/rules/plugin-updates-coupling*.md`), *generated* (`plugins/workflows-core/reference-parts/`), else *live*. The script, run as `python3 -I $S/wic.py '<string>' …` from the root of the tree measured:

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

**The retired strings.** Live and generated counts are 0 at the head for all eight; every remaining hit is history.

| String | `632e73d6` (live / generated / history) | `61a6d172` (live / generated / history) | The history hits at the head, and why each stands |
|---|---|---|---|
| `prd_landed` | 8 / 0 / 0 | 0 / 0 / 1 | `plugins/product-workflows/CHANGELOG.md:23`, 3.83.0's *The landing note is gone*: says it was removed |
| `landing sentence` | 5 / 0 / 1 | 0 / 0 / 2 | `plugins/product-workflows/CHANGELOG.md:23`, the same bullet; `plugins/workflows-core/CHANGELOG.md:1847`, 1.8.5's *the documentation commands' landing sentences*, another subject |
| `Note whether the PRD is landed` | 2 / 1 / 1 | 0 / 0 / 4 | `plugins/product-workflows/CHANGELOG.md:23` (gone); `plugins/workflows-core/CHANGELOG.md:19`, 1.93.0's PE lane, *which is gone*; `.claude/rules/plugin-updates-coupling.md:21`, 3.82.0's bullet, true of that pair; `:24`, 1.93.0's bullet, what an older `workflows-core` still cites (*gone in 3.83.0*) |
| `offers only, never a gate` | 1 / 0 / 0 | 0 / 0 / 0 | — |
| `gates it nowhere` | 2 / 1 / 0 | 0 / 0 / 0 | — |
| `wherever the checkout stands` | 0 / 0 / 0 | 0 / 0 / 0 | — (the branch wrote it into its changelog and the design and removed it, F-2; population FW-5) |
| `through /product-workflows:update-prd` | 1 / 0 / 0 | 0 / 0 / 2 | `plugins/product-workflows/CHANGELOG.md:30`, twice, 3.83.0's *Fixed* bullet: *It always ended …*, and *… `through /product-workflows:update-prd` otherwise*. ARD:904 now writes `through <command>` |
| `last pulled the default branch` | 0 / 0 / 0 | 0 / 0 / 0 | — (written by addendum 1, removed by the touch-up; population FW-32, FW-33) |

**The new strings**, 0 everywhere at `632e73d6`:

| String | `61a6d172` (live / generated / history) | Where |
|---|---|---|
| `EPICS_PRD_NOT_HANDED_OFF` | 17 / 2 / 6 | live: EP:24, :201, :226, :253, :331, :349, :1305; `create-prd.md:922`; `update-prd.md:235`; UPS:164; `pw/docs/roles-and-phases.md:10`; `pw/docs/commands/epics.md:71`; PH:339, :358; `.claude/rules/product-workflows.md:38`; `.claude/rules/workflows-core-handoff.md:24`; `docs/maintainers/rationale.md:686`. Generated: `reference-parts/phase-handoff/require-on-main.md:175`, `:194`. History: `pw/CHANGELOG.md:17`, `:20`, `:24`, `:26`; `wc/CHANGELOG.md:14`; `.claude/rules/plugin-updates-coupling.md:24` |
| `Gate the PRD.` | 1 / 0 / 0 | EP:195, the section's title |
| `This run's branch, <branch>, carries a change` (the amending sentence's opening) | 1 / 0 / 0 | EP:199, where Phase 0 defines it; Phase 2.7 and Phase 9 print it by reference |
| `does not stand on a default branch pulled since` | 6 / 0 / 3 | EP:45 twice, ARD:214, `specify.md:292`, `pw/docs/commands/epics.md:71` twice; history `pw/CHANGELOG.md:16` twice, `:22` — population FW-32's after-count, 6 with 3 in the changelog |

(`pw/` is `plugins/product-workflows/`, `wc/` `plugins/workflows-core/`.) Each *before* figure agrees with the population's §2 where it records the string: S1 8, S2 5, S11 3 in its scope (EP, NPO, the coupling file) and 1 in `reference-parts/`, S8 1, S5 2 and 1; and `through /product-workflows:update-prd` 1 at ARD:904 (*Task 5 walks* (A)).

## The walks

Counted from the population file, not re-walked here. `## Task 3 walks` holds 35 rows — W-1 to W-28 (seven gate returns × PRD or Epic address × idea route or slice), RF-1 to RF-4 (Review Focus 1 to 4) and R-1 to R-3 — and `## Task 5 walks` 16 — T5-A1 to T5-A5 (the threat-model line) and T5-B1 to T5-B10 with T5-B2′ (`/update-spec`). Every row's *Result* cell begins `Matches`: 35 of 35 and 16 of 16 (`awk '/^## Task 3 walks/{f=1;next} /^## /{f=0} f' <file> | grep -E '^\| (W|RF|R)-[0-9]+ \|' | awk -F' \\| ' '{print $NF}' | grep -c '^Matches'`, and the same with `^\| T5-` for Task 5). The re-walks the file notes are its own fix rounds': Task 3's fix round 1 re-walked W-9 to W-12, W-19 to W-28, R-3 and RF-1; Task 5's fix round 1 re-walked T5-B1, B2, B2′, B3 and B5 and added B8 and B9; its fix round 2 re-walked B3, B8 and B9 and added B10. **The file notes no re-walk by the final fix wave**: its `## Final fix wave` section records string counts, FW-1 to FW-38, and no walk, and the walks' line numbers are at Task 3's and Task 5's commits.

## The reviews

From the ledger and the findings files in the scratch directory, whose counts are the ledger's.

| Review | Model | Head reviewed | Verdict and findings | Fix rounds | Final state |
|---|---|---|---|---|---|
| Pre-flight scan of the plan | the controller | the plan | nine rows; one conflict (Task 2 against its own Step 7, if check 11 fired) | — | closed by Task 1's measurement 3: check 11 requires nothing (ledger line 27) |
| Task 1, the population | Opus | `de738147` | Needs fixes: 2 Important (P-97's keep false after M8; three page copies of the F9 remedies missing), 6 Minor | 1 (`1ee281b3`, 135 rows) | all addressed, no new breakage |
| Task 2, `phase-handoff` and `next-phase-offer` | Opus | `47052c37` | Needs fixes: 1 Important (PH:402's advisory example named `/epics` on `prd.md`), 6 Minor | 1 (`587eba32`) | all addressed; 1 Minor deferred, judged not real at the final review |
| Task 3, `/epics` | Opus | `72a8b164` | Needs fixes: 1 Important (the amending sentence's claim, the controller's dictated wording), 6 Minor | 1 (`bcadfa7c`) | all addressed, no Critical or Important breakage; 4 Minor deferred |
| Task 5, the two fixes | Opus | `8cb4c65a` | Needs fixes: (A) approved; (B) 1 Important (I1, `consumed_by:`-only hunks carried), 7 Minor (M1 to M7) | 2: `ec54b2f1` (1 new Important, N1, and 2 new Minor), `37dfb05c` | all addressed, no Critical or Important breakage; 4 Minor deferred |
| Task 4, the statements and offers | Opus | `a102b42c` | Needs fixes: 1 Important (`/create-prd` and `/update-prd` said `/epics` stops on an unmerged revision), 8 Minor | 1 (`56d853b5`) | all addressed, the widening to five more sites judged true; 6 Minor deferred |
| Task 6, the merges and the release | Opus | `f0ea1be1` | Needs fixes: merges, versions, changelogs, coupling bullet and generated files correct; 1 Important (batch 1's live checks `:136` and `:147` unreachable from 3.83.0), 2 Minor | none of its own: into the final fix wave (rulings file ruling 27) | addressed, by the wave's re-review |
| Whole branch | Fable | `f0ea1be1`, base `ec60ad47` | With fixes: 0 Critical, 2 Important (F-1 `EPICS_NOT_FOUND`'s text; F-2 four *wherever the checkout stands* statements), 3 Minor (F-3 to F-5); of the deferred Minors, 2 not real and the rest real; M6 to be filed | the wave (`ffd84234`, `ff7ac30c`, `cf9faafb`, `bfbbf7d4`), addendum 1 (`0dd68fdc`), addendum 2 (`f24b5430`) | below |
| The wave's re-review | Opus | `f24b5430`, over `f0ea1be1..f24b5430` | all 27 items addressed (22 listed, addenda 1 a/b/c and 2 a/b); frozen things held; 0 Critical or Important; 9 new Minor (N1 to N9) and 3 copies differing | the touch-up (`887b4580`) | — |
| The narrow re-check | Sonnet | `887b4580` | N1 to N9 and the copies addressed; one optional Minor in the design | the controller's `61a6d172` | clean, *Parked: none* (ledger line 126); `61a6d172` had no review after it |

## What departs from the design or the plan

The rulings file's *Departures from the process* gives each with its reason. In short: Task 5 was built before Task 4; every task but Task 1 was built while an earlier task's review or re-review ran; the final review ran in parallel with Task 6's review; the one fix wave was followed by two addenda, a touch-up and a narrow re-check on Sonnet; the final whole-branch review ran on Fable where the design's §10 says *each batch gets an Opus review before its pull request*, every task review and the wave's re-review running on Opus; the plan's Task 7 names the controller as this record's writer, and a close-out writer was dispatched instead (ledger line 128). On the plan's text: `EPICS_NOT_FOUND`, `CREATE_ARD_NOT_FOUND` and `SPECIFY_BRD_NOT_FOUND`, which the plan froze, carry a new clause (rulings 28 and 30); `EPICS_NO_PRD`'s Epic row gained a clause beyond the sanctioned one (ruling 13); `/update-spec`'s change grew past the differing-copy test to a line-based no-change rule (ruling 17); `dev-workflows` is released, which the plan's Task 6 allowed (*any other plugin whose files this branch changed*); and the plan's expected `prd-proposal.md` and `workflows-core/docs/family-map.md` are unchanged, kept by the population (P-100, P-105, P-109).

## What was not verified

- **The live checks have not been run.** `docs/superpowers/to-test-on-real-project.md:155` opens the section *LADDER-ORDER batch 1b — `product-workflows` 3.83.0, `workflows-core` 1.93.0, `dev-workflows` 4.67.1*, which holds 9 checks (`awk '/^## LADDER-ORDER batch 1b/{f=1;next} /^## /{f=0} f' docs/superpowers/to-test-on-real-project.md | grep -c '^- \*\*'` gives 9, lines 159 to 167), and batch 1's section holds the two this batch rewrote (`:136`, `:147`). None has run on a real project, and the ledger records no choice of when they run (line 127). The design's §11 item 4 is therefore half done for this batch, as it was for batch 1.
- **Two issues filed, not fixed**: LINEAGE-FILTERS (`docs/superpowers/to-fix.md:216`) and RESOLVE-BEFORE-FETCH (`:221`), with the rulings file's *Left open* for the rest of what stays open: `phase-handoff` §6.1's unchanged stack test, the threat-model line on a slice whose ledger would refuse `/create-prd`, the offers owed by batches 2 to 4 in the design's §5.5, and the re-review's two observations no ledger line takes up.
- **Not re-derived here:** the walks' verdicts (counted, not re-walked); every scratch test in the task reports and the fix report (the HEAD test, the `--from-ref` capture and the hash test, `lineage.py compare` on the stamp cases, the CRLF measurements behind LINEAGE-FILTERS); the population's per-row dispositions and its after-counts beyond the strings counted above; the paragraph-level pass's blocks; the merges' resolutions, which Task 6's review checked word by word in both directions; the controller's and the fixer's earlier chain runs, whose logs are in the session's scratchpad; and the review findings' counts, which are the ledger's. This record, the rulings summary and the ledger copy were not reviewed before they were committed.

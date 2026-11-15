# LADDER-ORDER batch 1b — the sweep population, before any edit

**Written:** 2026-11-15, by Task 1 of `docs/superpowers/plans/2026-11-15-ladder-order-b1b-epics-gate.md`, on branch `feat/ladder-order-b1b` at `e1b64243`, before any plugin file was edited. `e1b64243` is `main` `632e73d6` plus the plan commit, which touched only the design and the plan, so every line cited here is the same at `632e73d6`.

**The subject** (claim-sweep refinement 6): *what `/epics` does with `prd.md`'s branch state* — that it reads the PRD from the working tree, gates it nowhere, notes its landing for its offers only, or drafts from an unmerged PRD — together with every list of the commands that stop on a PRD not on the default branch (which `/epics` now joins), every offer of `/product-workflows:epics` by a run that wrote `prd.md` or from a state where it would now stop, and every statement of where `/epics` runs its gates.

**Scope** (refinement 4): `plugins/` — every `CHANGELOG.md` searched and never rewritten (§6), `reference-parts/` searched and never edited (§5a) — plus `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/` and the repo-root `README.md`.

**Abbreviations.** The plan's: PH = `plugins/workflows-core/references/phase-handoff.md`, EP = `plugins/product-workflows/commands/epics.md`, PP = `.../prd-proposal.md`, ARD = `.../create-ard.md`, UPS = `.../update-spec.md`, NPO = `plugins/workflows-core/references/next-phase-offer.md`. Also SPEC = `.../specify.md`, CPRD = `.../create-prd.md`, UPRD = `.../update-prd.md`, PG = `.../prd-ground.md`, IDEA = `.../idea.md`, BI = `.../brd-intake.md` (all `plugins/product-workflows/commands/`); `pw/` = `plugins/product-workflows/`, `dw/` = `plugins/dev-workflows/`, `wc/` = `plugins/workflows-core/`, `dcw/` = `plugins/docs-workflows/`.

**Dispositions.** **rewrite** — this batch, with the task that owns it; *beyond plan* marks a row the plan's file lists or named sites do not name; *ruling* marks a row the controller should rule on before the task edits it (§8). **keep** — still true after the change, with why. **later 2**, **later 3** — a dev-side or docs-side offer of `/epics` that L8 reaches but design §5.6 does not (§5.6 binds only the offers of a run that wrote `prd.md`), left as batch 1 left the dev-side and docs-side namings of `/create-ard` and `/specify` (design §5.5). **later 4** — a BRD-route slice form design §5.4 gives batch 4.

A phrase hit dispositions its whole paragraph (refinement 1), so a row cites the paragraph's line where it is one line, or a range. A row's first words are the start of the statement.

**Totals (after fix round 1, P-121 to P-135 added and P-111 moved from keep to Task 4; then Task 2's review, P-70 moved from keep to Task 2): 135 rows — 72 rewrite (Task 2: 14, Task 3: 17, Task 4: 41; 28 of them *beyond plan*, 4 marked *ruling*, since ruled, §8), 53 keep (one of them, P-66, ruled too), 10 later (batch 2: 7, batch 3: 2, batch 4: 1).** The first pass's totals were 120 rows (62, 52, 6). Derived with this command, from the worktree root, which splits the table cells on unescaped `|` as GitHub does:

```bash
python3 -I - docs/superpowers/plans/2026-11-15-ladder-order-b1b-sweep-population.md <<'EOF'
import re,sys,collections as C
rows=[[c.strip() for c in re.split(r"(?<!\\)\|",l)[1:-1]] for l in open(sys.argv[1],encoding="utf-8") if re.match(r"^\| P-\d+ \|",l)]
bad=[r[0] for r in rows if len(r)!=6 or not all(r[:5])]
rw=[r for r in rows if r[3].startswith("rewrite")]
print("rows",len(rows),"malformed",bad)
print("rewrite",len(rw),dict(sorted(C.Counter(re.match(r"Task \d",r[4]).group(0) for r in rw).items())),"beyond plan",sum("beyond plan" in r[4] for r in rw),"ruling",sum("ruling" in r[4] for r in rw))
print("keep",sum(r[3].startswith("keep") for r in rows))
print("later",dict(sorted(C.Counter(r[3] for r in rows if r[3].startswith("later")).items())))
ids=[r[0] for r in rows]; print("duplicate ids",[i for i,n in C.Counter(ids).items() if n>1])
EOF
```

It prints, after fix round 1:

```
rows 135 malformed []
rewrite 71 {'Task 2': 13, 'Task 3': 17, 'Task 4': 41} beyond plan 27 ruling 4
keep 54
later {'later 2': 7, 'later 3': 2, 'later 4': 1}
duplicate ids []
```

## 1. Searches run

All from the worktree root. Each hit was read in its paragraph before it was dispositioned. `<scope>` is the five roots above; every search below skips `CHANGELOG.md` and `reference-parts/` unless it says otherwise (the CHANGELOG search is §6's).

```bash
# the brief's starters, line-based
grep -rnE 'prd_landed|landing sentence|Land <PRD-KEY>|never as a gate|gates it nowhere|knowingly reads the (worktree|working tree)|offers only, never a gate|eleven consumers|in its Phase 2\.6' <scope>
# every offer of /epics, then read per file
grep -rnE '/(product-workflows:)?epics <' <scope>
# lists of the commands that stop on a PRD not on the default branch
grep -rnE 'stops? on (this|that|the|their|its) PRD folder|each stop on|Ignored, (every|each)' <scope>
grep -rnE 'as it would with no gate|no gate at all|no PRD gate|reads the PRD unconditionally|gates? only (a|the) PRD-level|gates? no file this run writes|waits on nothing this run wr' -i <scope>
grep -rnE "handoff merged|its handoff merged|PRD's handoff merged" <scope>
grep -rn 'PRD_NOT_HANDED_OFF' <scope>
# the order exception /epics' docs-grounding resolution takes
grep -rnE 'consent-ordering exception|deliberate exception to|ahead of (its|a|the|Phase 2\.5)[^.]{0,40}(gate|require-on-main)' <scope>
# remedies that chain a PRD write into an immediate /epics run
grep -rnE "(then|and) (re-?run )?['\`]?/(product-workflows:)?epics <|epics <[A-Z-]+>['\`]? (partitions|drafts)|second, once that PRD|then re-run '/product-workflows:epics" <scope>
# the /epics precondition and its callers
grep -rnE 'epics-precondition|`/epics` precondition|One precondition governs' plugins
```

**The paragraph-level pass.** Line searches miss a statement whose subject and wording sit on different lines of one wrapped paragraph, so each blank-line-separated block was collapsed and flagged where it names `/epics` and carries landing or gate wording. It flags 110 blocks; the 54 whose two patterns fall within 250 characters of each other were read through those windows, and the other 56 sentence by sentence (every sentence naming `/epics`).

```bash
python3 -I - <<'EOF'
import os,re
S=re.compile(r"/(product-workflows:)?epics\b|`epics`")
L=re.compile(r"working tree|worktree|as it stands|un-?landed|not landed|landed|unmerged|not merged|default branch|on no ref|no ref|gates? (it )?nowhere|never as a gate|never a gate|prd_landed|landing|warns?\b|pull request (is )?(still )?open|open pull request|reads? (the|its|a) (PRD|prd\.md)")
for r in ["plugins","CLAUDE.md",".claude/rules","docs/maintainers","README.md"]:
  ps=[r] if os.path.isfile(r) else sorted(os.path.join(d,f) for d,_,fs in os.walk(r) for f in fs if f.endswith(".md"))
  for p in ps:
    if p.endswith("CHANGELOG.md") or "/reference-parts/" in p: continue
    lines=open(p,encoding="utf-8").read().split("\n")+[""]; s=None
    for i,l in enumerate(lines,1):
      if l.strip() and s is None: s=i
      elif not l.strip() and s is not None:
        t=re.sub(r"\s+"," "," ".join(lines[s-1:i-1]))
        if S.search(t) and L.search(t): print(f"{p}:{s}-{i-1}")
        s=None
EOF
```

**The enumeration pass.** Every sentence that names two or more of `/create-ard`, `/specify`, `/prd-ground`, `/prd-proposal`, names `prd.md` or the PRD, carries *gate* or *stop*, and does not name `/epics` — the lists `/epics` may now belong in: 59 sentences, each read.

**The exclusivity probe** (refinement 3), over every sentence naming `/epics` and the PRD, a gate, the default branch or a landing: `only when`, `is the only`, `nothing else`, `and no other`, `only ever`, `the only <noun>`, `the sole`, `no other command`, `the one command`, `the only place`, `the one input|gate|reason`, `one exception`, `gates only`, `its only`, `this is the input`. Its subject hits are P-27 (*this is the input `/epics` gates*), P-53 (*`/epics` gates only a PRD-level `specification.md`*), P-5 (*save where it reaches the artifact it gates only at a later step*) and EP:217 (*This table is the one reason `/epics` reads a coverage ledger*, which stays true: the ledger is still read only at step 1b's refusals). The rest were about the `EPIC-` folder's one creator, unrelated.

**Fix round 1** (2026-11-15, from the review of `de738147`). The review's probes found what the passes above missed: a gloss stating `/epics`' gates in the *has written* wording the starter `gates? no file this run writes` cannot match (P-121), the page copies of the F9 refusals, which no search keyed on `/epics` near landing wording reaches because they say *re-refine* (P-122 to P-124), and copies and twins of rows already filed (P-125 to P-135). Re-run here before the rows were added, each hit read:

```bash
# /epics within 300 characters of a statement of its gates, whitespace collapsed (the review's probe 15)
python3 -I - <<'EOF'
import os,re
S=re.compile(r"/(product-workflows:)?epics\b")
L=re.compile(r"gates no file|its gates are|gates only|waits on nothing|does not gate|gate(s|d)? nothing|no PRD gate")
for r in ["plugins","CLAUDE.md",".claude/rules","docs/maintainers","README.md"]:
  ps=[r] if os.path.isfile(r) else sorted(os.path.join(d,f) for d,_,fs in os.walk(r) for f in fs if f.endswith(".md"))
  for p in ps:
    if p.endswith("CHANGELOG.md") or "/reference-parts/" in p: continue
    t=re.sub(r"\s+"," ",open(p,encoding="utf-8").read())
    for m in L.finditer(t):
      if S.search(t[max(0,m.start()-300):m.end()+300]): print(p,"…",t[max(0,m.start()-160):m.end()+80])
EOF
# every re-refine site, commands and pages (the review's probe 17)
grep -rnE 're-refin' <scope>
# every /epics mention in the docs pages of specify and create-ard, and the review's other cited sites, by line
grep -n 'epics' plugins/product-workflows/docs/commands/specify.md plugins/product-workflows/docs/commands/create-ard.md
```

The gate-statement probe's only hit not already a row was SPEC:244–246 (P-121). `pw/docs/commands/create-ard.md:204`, the walkthrough's copy of P-92's slice offer, was found beside the review's two lines and is in P-130.

## 2. Baseline counts

Every literal string a row changes, counted wrap-insensitively (refinement 7: whitespace collapsed across each file and across the string), over the scope less `CHANGELOG.md` and `reference-parts/`, before any edit. Each later task re-runs the count for the strings its rows change and fills the last column. The command, with the string as its one argument:

```bash
python3 -I - '<string>' <<'EOF'
import os,re,sys
s=re.sub(r"\s+"," ",sys.argv[1]).strip()
for r in ["plugins","CLAUDE.md",".claude/rules","docs/maintainers","README.md"]:
  ps=[r] if os.path.isfile(r) else sorted(os.path.join(d,f) for d,_,fs in os.walk(r) for f in fs if f.endswith(".md"))
  for p in ps:
    if p.endswith("CHANGELOG.md") or "/reference-parts/" in p: continue
    raw=open(p,encoding="utf-8").read(); idx=[]; out=[]; ws=False
    for k,ch in enumerate(raw):
      if ch.isspace():
        if ws: continue
        ws=True; out.append(" ")
      else: ws=False; out.append(ch)
      idx.append(k)
    c="".join(out); j=c.find(s)
    while j>=0: print(f"{p}:{raw.count(chr(10),0,idx[j])+1}"); j=c.find(s,j+1)
EOF
```

`R1` is the stopping-consumer recipe written in `.claude/rules/workflows-core-handoff.md:24`, run as it stands there.

| Id | String | Before | Sites | After |
|---|---|---|---|---|
| R1 | the recipe's count of `/commands` with a §3.4 row whose column 3 begins `**stops` | **11** | `/brd-interview` `/brd-package` `/brd-proposal` `/brd-reconcile` `/brd-split` `/create-ard` `/design` `/prd-ground` `/prd-proposal` `/specify` `/update-spec` (12 on the scratch copy with the test row, measurement 3) | **12** (Task 2): the eleven, and `/epics` |
| S1 | `` `prd_landed` `` | **8** | EP:304, :308, :421, :493, :1082, :1148, :1154, :1269 | |
| S2 | `landing sentence` | **5** | EP:310, :493, :1082, :1148, :1154 | |
| S3 | `Land <PRD-KEY>'s prd.md` | **1** | EP:311 | |
| S4 | `for this run's offers, never as a gate` | **1** | EP:296 | |
| S5 | `gates it nowhere` | **2** | EP:297, NPO:329 (+1 in `reference-parts/`) | **1** after Task 2: EP:297, Task 3's; NPO's gone (RP 0) |
| S6 | `knowingly reads the worktree` | **1** | PH:451 (+1 RP) | **1** (Task 2): PH:452, the rule kept, its `/epics` example gone (S12) (RP 1) |
| S7 | `knowingly reads the working tree` | **2** | EP:298, `docs/maintainers/rationale.md:684` | |
| S8 | `offers only, never a gate` | **1** | `.claude/rules/product-workflows.md:38` | |
| S9 | `the eleven consumers with a row that stops` | **1** | `.claude/rules/workflows-core-handoff.md:24` | **0** (Task 2); `the twelve consumers with a row that stops` **1**, rules:24 |
| S10 | `` `/epics` in its Phase 2.6 `` | **1** | PH:624 (+1 RP) | **1** (Task 2): PH:625, kept and extended; bounded `` `/epics` in its Phase 2.6, `/specify` `` 1 → **0** (RP 1, the extended form) |
| S11 | `Note whether the PRD is landed` | **3** | EP:296, NPO:330, `.claude/rules/plugin-updates-coupling.md:26` (+1 RP) | **2** after Task 2: EP:296, Task 3's; coupling:26, keep (P-114); NPO's gone (RP 0) |
| S12 | `` — `/epics` on `prd.md`, `` | **1** | PH:451 (+1 RP) | **0** (Task 2) (RP 0) |
| S13 | `` `/product-workflows:epics` gates no file this run writes `` | **1** | CPRD:916 | |
| S14 | `` `/epics` gates only a PRD-level `specification.md` `` | **1** | `pw/docs/commands/update-prd.md:96` | |
| S15 | `` `/epics` waits on nothing this run wrote `` | **1** | `pw/docs/commands/create-prd.md:168` | |
| S16 | `no PRD gate at all` | **2** | `pw/docs/roles-and-phases.md:20`, `:42` | |
| S17 | `reads the PRD unconditionally` | **1** | `pw/docs/roles-and-phases.md:20` | |
| S18 | `` since it reads `prd.md` from the working tree `` | **1** | UPS:165 | |
| S19 | `Ignored, /create-ard and /specify each stop on this folder until it holds a merged` | **4** | ARD:287, ARD:301, SPEC:328, SPEC:342 | |
| S20 | `Ignored, every /create-ard and /specify run on this folder stops here` | **4** | ARD:311, ARD:318, SPEC:352, SPEC:359 | |
| S21 | `the Epics and release-note routes do not` | **1** | UPRD:235 | |
| S21b | `the Epics and release-note routes wait on nothing this run wrote` | **1** | `pw/docs/commands/update-prd.md:96` | |
| S22 | `"Hand to a Product Engineer — /product-workflows:epics <ADDRESS> (PE)"` | **1** | CPRD:901 | |
| S23 | `"Re-run epics — /product-workflows:epics <KEY> (PE, if Epics exist)"` | **1** | UPRD:210 | |
| S24 | `— /product-workflows:epics <KEY> (PE, if Epics exist)` | **2** | UPRD:205, UPRD:210 | |
| S25 | ``hand to PE → `/product-workflows:epics <PRD>` (or`` | **1** | NPO:205 (+1 RP) | **0** (Task 2) (RP 0); ``hand to PE → `/product-workflows:epics <PRD>`, which gates this PRD and so carries `<merge-clause>` too`` **1**, NPO:205 (RP 1, `next-phase-offer/pm.md`) |
| S26 | `` `/epics` partitioning a PRD whose pull request is still open `` | **1** | PH:77 (+3 RP) | **0** (Task 2) (RP 0) |
| S27 | `` `/epics` on an open `prd/` branch that changed `prd.md` `` | **1** | PH:654 (+1 RP) | **0** (Task 2) (RP 0) |
| S28 | `` the way `/epics` would partition a PRD whose revision is still on its open `prd/` branch `` | **1** | PH:657 (+1 RP) | **0** (Task 2) (RP 0) |
| S29 | `` is conditional on the folder it names holding an authored `prd.md` `` | **1** | NPO:342 (+5 RP) | **1** (Task 2): NPO:342, kept, F2's sentence added after it; bounded ``(`/product-workflows:epics` Phase 0 step 1b). Where the`` 1 → **0** (RP 5) |
| S30 | `` `/epics` resolves docs grounding ahead of its `require-on-main` gates `` | **1** | BI:262 | |
| S31 | `` `/product-workflows:create-ard` and `/product-workflows:specify` both gate `prd.md` with their own `require-on-main` `` | **1** | PG:542 | |
| S32 | `` The run reads `prd.md` from the PRD folder as it stands and does not require it on the specs repo's default branch `` | **1** | `pw/docs/commands/epics.md:67` | |
| S33 | `` this is the input `/epics` gates `` | **1** | `pw/docs/commands/epics.md:69` | |
| S34 | `` Not taken: gating `/epics`' read of `prd.md` (L13) `` | **1** | `docs/maintainers/rationale.md:684` | |
| S35 | `[note whether prd.md is on the default branch — offers only, never a gate]` | **1** | `.claude/rules/product-workflows.md:38` | |
| S36 | `` and so do its `/create-ard` and `/specify` `` | **2** | `dw/docs/getting-started.md:108`, `dw/docs/commands/design.md:59` | |
| S36b | `` and `/create-ard` and `/specify`, whose PRD was optional to them `` | **1** | `dw/docs/roles-and-phases.md:10` | |
| S37 | ``[`/specify`](commands/specify.md) stop on the PRD, which was optional to them until 2026-11-14`` | **1** | `pw/docs/roles-and-phases.md:10` | |
| S38 | `` lets `/epics` read the file as it stands `` | **1** | EP:232 | |
| S38b | `` lets `/epics` read it as it stands `` | **1** | `pw/docs/commands/epics.md:21` | |
| S39 | `then re-run /product-workflows:epics <KEY>.` | **1** | EP:292 | |
| S40 | `then re-run '/product-workflows:epics <KEY>'.` | **1** | EP:253 | |
| S41 | `second, once that PRD exists` | **1** | EP:224 | |
| S42 | `` whether it then passes step 1b depends on whether a `prd.md` has been authored in that slice `` | **1** | EP:122 | |
| S43 | `` authors the PRD and `/product-workflows:epics <SLICE-KEY>` partitions it `` | **1** | EP:129 | |
| S44 | `` `/create-ard`, `/specify`, and `/epics` now hard-stop `` | **1** | PH:356 (+1 RP) | **1** (Task 2): PH:357, kept; the paragraph gains the 2026-11-15 decision (`A third followed on 2026-11-15` **1**) (RP 1) |
| S45 | `` `/create-ard`'s and `/specify`'s rows for the idea-route PRD do, dated 2026-11-14 `` | **1** | PH:316 (+1 RP) | **1** (Task 2): PH:316, kept; bounded `dated 2026-11-14. A stop only on a file` 1 → **0**, `/epics`' sentence between (RP 1) |
| S46 | `or specify it with '/product-workflows:specify <KEY>', that PRD's handoff merged.` | **1** | IDEA:98 | |
| S47 | `or re-refine this Epic with '/product-workflows:epics <KEY>'.` | **1** | CPRD:240 | |
| S48 | `to re-refine this Epic instead, run '/product-workflows:epics <KEY>'.` | **1** | UPRD:42 | |
| S49 | `` `/epics` has no PRD gate at all, but it does gate two other inputs `` | **1** | `pw/docs/roles-and-phases.md:42` | |
| S50 | `with no PRD gate at all — see PE below for the input it does gate` | **1** | `pw/docs/roles-and-phases.md:20` | |
| S51 | `` and, where no `prd.md` is in the folder, not `/product-workflows:epics <PRD>` (`EPICS_NO_PRD`) `` | **1** | UPS:164 | |
| S52 | `` and not `/epics` where no `prd.md` is in the folder `` | **1** | `pw/docs/commands/update-spec.md:96` | |
| S53 | `` the companion `product-workflows` commands whose gated input was never optional stop too: `` | **1** | `dw/docs/getting-started.md:108` | |
| T2-a | `EPICS_PRD_NOT_HANDED_OFF` (added by Task 2) | **0** | — | **3** (Task 2): PH:338 (the row), PH:357, `.claude/rules/workflows-core-handoff.md:24` (RP 2) |
| T2-b | `The architecture, Epics and specification routes each gate this PRD and so carry` (P-10, added by Task 2) | **0** | — | **1** (Task 2): NPO:206 (RP 1, `next-phase-offer/pm.md`) |
| S54 | `and gates no file this run has written — its gates are` (fix round 1) | **1** | SPEC:245 | |
| S55 | ``or [`/epics`](epics.md) to re-refine the Epic (on the Epic's key`` (fix round 1) | **1** | `pw/docs/commands/create-prd.md:78` | |
| S56 | ``and [`/epics`](epics.md) for re-refining the Epic itself`` (fix round 1) | **1** | `pw/docs/commands/update-prd.md:45` | |
| S57 | ``or [`/specify <KEY>`](specify.md) to specify it, once that PRD's handoff is merged`` (fix round 1) | **1** | `pw/docs/commands/idea.md:159` | |
| S58 | ``as its `/create-ard` and `/specify` do on an idea-route PRD`` (fix round 1) | **2** | `dw/docs/commands/ready.md:55`, `:94` | |
| S59 | ``document `/create-ard` and `/specify` cannot yet see`` (fix round 1) | **1** | `pw/docs/commands/prd-ground.md:454` | |
| S60 | ``in `/epics`' place wherever a route above names it`` (fix round 1) | **1** | UPS:166 | |
| S61 | ``(§3.4's `/epics` row)`` (fix round 1) | **1** | SPEC:1406 | |
| S62 | `` `/epics` on a `prd.md` stating no requirements `` (Task 2's review, P-70) | **1** | PH:402 (+1 RP, `phase-handoff/handoff-to-main.md`) | **0** (Task 2's fix round) (RP 0); `` `/brd-split` on a root's `brd/brd-inventory.md` holding no row, `BRD_SPLIT_EMPTY_INVENTORY` `` 0 → **1**, PH:402 (RP 1, `handoff-to-main.md`) |

## 3. The population — rows this batch rewrites

### Task 2 — `phase-handoff`, `next-phase-offer`, the handoff rules file

| # | file:line | First words | Disposition | Owner, and why | Strings |
|---|---|---|---|---|---|
| P-1 | PH:337 (the row after it) | "\| `/prd-proposal` \| `prd.md` \| **stops**, and **splits row F on a test this gate cannot make** …" | rewrite | Task 2 (in plan). §3.4 gains `/epics` · `prd.md` beside this row, its column 3 beginning `**stops**` and dated 2026-11-15; R1 then returns 12 (measured, measurement 3) | R1 |
| P-2 | PH:316 | "Several consumers map `absent` to a hard stop, and each is legitimate for one of two reasons." | rewrite | Task 2, *beyond plan* (§3.4 prose; the plan names only the table). Its two reasons are *never optional* and *a recorded decision*, its decided example `/create-ard`'s and `/specify`'s 2026-11-14 rows. `/epics`' row is both: none in the folder stops as it always has (step 1b's `EPICS_NO_PRD`, EP:196, older than the gate, as `/design`'s stop is), and one in the folder and on no ref, or on an unmerged branch, stops by M8. The paragraph has to say which reason holds for which half | S45 |
| P-3 | PH:356 | "For the consumers that predate this gate, rows D and E add the only new stop the gate itself makes …" | rewrite | Task 2, *beyond plan*. Four clauses: *`/create-ard`, `/specify`, and `/epics` now hard-stop* (rows D/E) — keep, it becomes true of `/epics` on `prd.md` too; *A second change came later … since 2026-11-14 `/create-ard` and `/specify` stop on row F for the PRD* — M8 is a third, 2026-11-15, for `/epics`; the list of consumers whose row stops on `absent` *because their input shipped with them*, *but `/design`'s, whose stop predates this gate* — `/epics`' row has to be placed; and ***`/create-ard` and `/specify` stop on `absent` for the PRD as decided*** | S44 |
| P-4 | PH:451 | "**So the test is not "does this command stop", it is "does this command claim".** A command that knowingly reads the worktree — `/epics` on `prd.md`, …" | rewrite | Task 2 (in plan). Loses the `/epics` example; the rule stands for `/brd-interview` and `/ready` | S6, S12 |
| P-5 | PH:624 | "2. A command that **consumes** one cites and executes `require-on-main` (§3) before its first subagent dispatch …" | rewrite | Task 2 (in plan). `/epics` gates `prd.md` in its Phase 0, beside its Phase 2.6 gate | S10 |
| P-6 | PH:77 | "**Where a new branch is cut.** … — `/create-ard` stamping the grounding findings an unmerged `/prd-ground` branch wrote, `/epics` partitioning a PRD whose pull request is still open, …" | rewrite | Task 2, *beyond plan* (F1). Past the gate no `/epics` run partitions a PRD whose pull request is open (rows D/E stop it; a revision on a `prd/` HEAD meets row C, whose repair switches to the default branch), save through row B (measurement 2) | S26 |
| P-7 | PH:654 | "- **It does** — a `prefix` was passed, and either HEAD is exactly the name §2.2 gives that prefix … `/epics` on an open `prd/` branch that changed `prd.md`, …" | rewrite | Task 2, *beyond plan* (F1). §6.1's stack test is by name and changed files, not by caller, so it still classes a `prd/` branch that changed `prd.md` as one `/epics` builds on and names the merge into it; the re-run then stops at the PRD gate (D/E) or is switched away (C). The example is false, and the remedy it selects for `/epics` sends the operator round twice | S27 |
| P-8 | PH:657 | "**Neither test is row B's, on purpose.** … the way `/epics` would partition a PRD whose revision is still on its open `prd/` branch." | rewrite | Task 2, *beyond plan* (F1). Reading the default branch's older copy is now what `/epics`' gate does on purpose for a revision on a `prd/` branch (row C) | S28 |
| P-9 | NPO:205 | "- `/product-workflows:create-prd <ADDRESS>`: `/docs-workflows:release-notes <PRD>` (PM …); … or hand to PE → `/product-workflows:epics <PRD>` (or `/product-workflows:specify <PRD>`, which gates this PRD and so carries `<merge-clause>` too)." | rewrite | Task 2 (in plan). `/epics` gates this PRD too, so its offer carries `<merge-clause>` | S25 |
| P-10 | NPO:206 | "- `/product-workflows:update-prd <KEY>` — re-entry, not a linear node: … Candidate routes are …, `/product-workflows:epics <PRD>` (PE), …" | rewrite | Task 2 (in plan). Names the routes and not which carry the clause; `/epics`' now does, as `/create-ard`'s does | — |
| P-11 | NPO:326–330 | "- `/product-workflows:epics <PRD>` → `/product-workflows:specify <EPIC>` (per Epic); optional PA → `/product-workflows:create-ard <EPIC>` — each after the landing of the PRD folder's `prd.md` …" | rewrite | Task 2 (in plan). *reads that file from the working tree and gates it nowhere* and the cite of *Note whether the PRD is landed* go; past `/epics`' gate both offers stand without a landing | S5, S11 |
| P-12 | NPO:342–356 | "**Every `/product-workflows:epics` option the routing graph names is conditional on the folder it names holding an authored `prd.md`** …" | rewrite | Task 2, *beyond plan* (F2). The one condition every `/epics` offer is held to is now two: an authored `prd.md`, on the default branch wherever the specs tree is a git repository. Its own last sentence names the defect: *An offer whose run stops the moment it starts* | S29 |
| P-13 | `.claude/rules/workflows-core-handoff.md:24` | "… the eleven consumers with a row that stops instead are `/design`, `/update-spec`, …" | rewrite | Task 2 (in plan). Twelve, with `/epics`, its reason worded as P-2's; the recipe beside it returns 12 | S9, R1 |

### Task 3 — `/epics` and its page

| # | file:line | First words | Disposition | Owner, and why | Strings |
|---|---|---|---|---|---|
| P-14 | EP:296–312 | "**Note whether the PRD is landed — for this run's offers, never as a gate.** This run reads the `prd.md` step 1b's table accepted from the folder as it stands, and gates it nowhere …" | rewrite | Task 3 (in plan): the paragraph, `prd_landed` and the landing sentence go; the gate takes their place before step 1b | S1, S2, S3, S4, S5, S7, S11 |
| P-15 | EP:421 | "- **Revise** → ask what to change, … names `/product-workflows:create-ard <PRD>`, which records it — after the PRD's landing, where Phase 0's `prd_landed` is false" | rewrite | Task 3 (in plan) | S1 |
| P-16 | EP:493 | "Where Phase 0's `prd_landed` is false, a remedy that names `/product-workflows:create-ard <PRD>` or `/product-workflows:specify <PRD>` …" | rewrite | Task 3 (in plan) | S1, S2 |
| P-17 | EP:1082 | "- First: [Phase 0's landing sentence, verbatim] — _only where Phase 0's `prd_landed` is false …_" | rewrite | Task 3 (in plan) | S1, S2 |
| P-18 | EP:1148 | "[Per `workflows-core:next-phase-offer`'s *PE — breakdown & specification* lane — guidance only, never auto-invoked. Where Phase 0's `prd_landed` is false, open with Phase 0's landing sentence …" | rewrite | Task 3 (in plan). Past the gate the PRD is on the default branch, save on `pass_amending` (measurement 2), which this block must then word | S1, S2 |
| P-19 | EP:1154 | "- **First: [Phase 0's landing sentence, verbatim]** — _only where Phase 0's `prd_landed` is false; omit otherwise_" | rewrite | Task 3 (in plan) | S1, S2 |
| P-20 | EP:1269 | "- ALWAYS report landing-order inversions (Phase 2.5) and contract omissions (Phase 5) … — preceded by the PRD's landing where Phase 0's `prd_landed` is false —" | rewrite | Task 3 (in plan): the invariant that names it | S1 |
| P-21 | EP:232 | "**Every row above that names `/product-workflows:create-prd <KEY>` is qualified by one more fact … adding the `kind: prd` and `key:` its format carries … is what lets `/epics` read the file as it stands.**" | rewrite | Task 3, *beyond plan* (F6). After the gate, adding those fields to a `prd.md` the default branch holds leaves a working copy the gate stops on (rows C″/C′/C), and to one on no ref leaves `EPICS_PRD_NOT_HANDED_OFF`: the edit lets `/epics` read the file only once it lands. Within the Global Constraints' *save a sentence that says `/epics` reads an unlanded PRD* | S38 |
| P-22 | EP:120–130 | "- **One or more slices** — the ordinary shape … whether it then passes step 1b depends on whether a `prd.md` has been authored in that slice, which the offer **states** rather than promises. … - **No slice at all** — … after which `/product-workflows:create-prd <SLICE-KEY>` authors the PRD and `/product-workflows:epics <SLICE-KEY>` partitions it." | rewrite | Task 3, *beyond plan* (F5). `EPICS_BRD_NOT_SLICED`'s remedy, which the Global Constraints do not freeze: the run it offers now also stops until that slice's `prd.md` is on the default branch, and *authors the PRD and … partitions it* skips the merge between | S42, S43 |
| P-23 | EP:224 | "\| An `EPIC-` folder — its name beginning `EPIC-<the resolved key>-` … holding no `epic.md` \| … name `/product-workflows:epics <PRD-KEY>` … `/product-workflows:create-prd <PARENT-KEY>` first, … and `/product-workflows:epics <PARENT-KEY>` second, once that PRD exists. …" | rewrite | Task 3, *ruling* (F5). `EPICS_NO_PRD`'s text is frozen *save a sentence that says `/epics` reads an unlanded PRD*. *Once that PRD exists* now needs *on the default branch*; and the gate runs before this table, on the folder above's `prd.md`, so where that file is in the folder and on no ref the run reaches this row (`absent`, table refuses) and names `/epics <PRD-KEY>`, which stops `EPICS_PRD_NOT_HANDED_OFF` on arrival | S41 |
| P-24 | EP:250–254 | "`<remedy>` has two forms. Where the folder above is a `PRD-` folder holding no `prd.md` … `author one with '/product-workflows:create-prd <PARENT-KEY>', then re-run '/product-workflows:epics <KEY>'.`" | rewrite | Task 3, *ruling* (F5). `EPICS_EPIC_NOT_UNDER_PRD` is frozen as P-23's stop is; the re-run it names now stops until that PRD's handoff merges | S40 |
| P-25 | EP:292 | "`EPICS_PRD_NO_REQUIREMENTS: <PRD-KEY>'s prd.md at <path> states no requirements … Add them with /product-workflows:update-prd <PRD-KEY>, then re-run /product-workflows:epics <KEY>.`" | rewrite | Task 3, *ruling* (F5). After `/update-prd`, the re-run meets the gate: on that run's `prd/` branch, row C, whose repair switches to the default branch and reads the copy with no requirements, stopping here again; on the default branch with the edit uncommitted, row C″. The re-run needs the merge first | S39 |
| P-26 | `pw/docs/commands/epics.md:67` | "- **A PRD folder, or an Epic folder under one** — … The run reads `prd.md` from the PRD folder as it stands and does not require it on the specs repo's default branch; …" | rewrite | Task 3 (in plan) | S32 |
| P-27 | `pw/docs/commands/epics.md:69` | "- **An optional PRD-level `specification.md`** — this is the input `/epics` gates on the specs repo's default branch (Phase 2.6); …" | rewrite | Task 3 (in plan). *the input* reads as the only one | S33 |
| P-28 | `pw/docs/commands/epics.md:107` | "- **The PRD's `prd.md` is not on the specs repo's default branch** — … → land it there first: the report says so ahead of every offer …" | rewrite | Task 3 (in plan): the run stops there now, so the bullet goes | — |
| P-29 | `pw/docs/commands/epics.md:21` | "**A folder is accepted by what its own PRD or Epic file declares.** … and adding the `kind: prd` and `key:` the file's format carries lets `/epics` read it as it stands." | rewrite | Task 3, *beyond plan*, with P-21 | S38b |
| P-30 | `pw/docs/commands/epics.md:17` | "**`/epics` accepts exactly two shapes and refuses everything else.** … the stop's own row for it names `/epics <PRD-KEY>` where the folder above holds a PRD … `/create-prd <PARENT-KEY>` first where that `PRD-` folder holds none yet …" | rewrite | Task 3, *ruling*: follows P-23 and P-24; keep if both are ruled kept | — |

### Task 4 — the statements and offers elsewhere

| # | file:line | First words | Disposition | Owner, and why | Strings |
|---|---|---|---|---|---|
| P-31 | CPRD:901 | "choices: ["Draft the release note now — /docs-workflows:release-notes <ADDRESS> (PM) (Recommended)", …, "Hand to a Product Engineer — /product-workflows:epics <ADDRESS> (PE)", "Stop here"]" | rewrite | Task 4 (in plan, Step 1): the PE option carries `<merge-clause>`. Check 11 cannot see it (measurement 3) | S22 |
| P-32 | CPRD:914 | "- **`/product-workflows:epics <ADDRESS>`** (PE) — hand to a Product Engineer to split the PRD into Epics (or author a PRD-level spec → `/product-workflows:specify <ADDRESS>` `<merge-clause>`, … — name it with the clause)." | rewrite | Task 4 (in plan): `/epics` gates this PRD as `/specify` does | — |
| P-33 | CPRD:916 | "The other two options carry no clause — … and `/product-workflows:epics` gates no file this run writes — its gates are `<PRD-dir>/specification.md` … and the PRD-level ARD …, and this run writes neither." | rewrite | Task 4 (in plan) | S13 |
| P-34 | CPRD:237–246 | "`<remedy>` names the parent PRD as the likely intended target wherever there is one. … `This is probably the PRD you meant: revise it with '/product-workflows:update-prd <PRD-KEY>', or re-refine this Epic with '/product-workflows:epics <KEY>'.`" | rewrite | Task 4, *beyond plan* (F9). `CREATE_PRD_EPIC_FOLDER`'s remedy names an `/epics` run that now stops where that parent `prd.md` is not landed; batch 1 gave the same refusals' `/specify` the *its handoff merged* clause (its K65) | S47 |
| P-35 | UPRD:205 | "  • Re-run epics            — /product-workflows:epics <KEY>                     (PE, if Epics exist)" | rewrite | Task 4 (in plan, Step 1): the offer box line carries `<merge-clause>`, as the spec and architecture lines do | S24 |
| P-36 | UPRD:210 | "choices: ["Revise the spec — …", "Re-run architecture — …", "Re-run epics — /product-workflows:epics <KEY> (PE, if Epics exist)", "Stop here"]" | rewrite | Task 4 (in plan, Step 1). Check 11 cannot see it (measurement 3) | S23, S24 |
| P-37 | UPRD:235 | "**The spec and architecture routes carry `<merge-clause>` when offered; the Epics and release-note routes do not.** … `/product-workflows:epics` gates `<PRD-dir>/specification.md` and the PRD-level ARD, neither of which this run writes, …" | rewrite | Task 4 (in plan). The paragraph's *On a branch* / *Modified against a merged copy* / *On no ref* walk now covers `/epics` too | S21 |
| P-38 | UPRD:42 | "`<remedy>` names the parent PRD as the likely intended target wherever there is one: … `This is probably the PRD you meant: re-run '/product-workflows:update-prd <PRD-KEY>'; to re-refine this Epic instead, run '/product-workflows:epics <KEY>'.`" | rewrite | Task 4, *beyond plan* (F9), as P-34 | S48 |
| P-39 | IDEA:98 | "\| an Epic folder whose parent holds a `prd.md` asserting `kind: prd` \| `An Epic is refined from the PRD above it: … re-refine this Epic with '/product-workflows:epics <KEY>', or specify it with '/product-workflows:specify <KEY>', that PRD's handoff merged.`" | rewrite | Task 4, *beyond plan* (F9). The trailing clause, written for `/specify` (batch 1's K65), now binds `/epics` too; as it stands it reads as the last item's | S46 |
| P-40 | ARD:287 | "`CREATE_ARD_NEEDS_PRD: <PRD> has no prd.md — none on any ref, and none in <path>. …` … Ignored, /create-ard and /specify each stop on this folder until it holds a merged PRD." | rewrite | Task 4 (in plan, Step 2). `/epics` stops on the folder too (`EPICS_NO_PRD` now, then `EPICS_PRD_NOT_HANDED_OFF` or rows D/E until the PRD merges) | S19 |
| P-41 | ARD:301 | "(the rename form) … Then open a pull request from <new-branch> into <default>, merge it, and re-run '/product-workflows:create-ard <ADDRESS>'. Ignored, /create-ard and /specify each stop on this folder until it holds a merged prd.md." | rewrite | Task 4 (in plan, Step 2), as P-40 | S19 |
| P-42 | ARD:311 | "(`CREATE_ARD_PRD_NOT_HANDED_OFF`, uncommitted form) … Ignored, every /create-ard and /specify run on this folder stops here until prd.md is on <default>." | rewrite | Task 4 (in plan, Step 2) | S20 |
| P-43 | ARD:318 | "(`CREATE_ARD_PRD_NOT_HANDED_OFF`, committed form) … Ignored, every /create-ard and /specify run on this folder stops here until prd.md is on <default>." | rewrite | Task 4 (in plan, Step 2) | S20 |
| P-44 | SPEC:328 | "`SPECIFY_NEEDS_PRD: <PRD> has no prd.md — none on any ref, and none in <path>. …` … Ignored, /create-ard and /specify each stop on this folder until it holds a merged PRD." | rewrite | Task 4 (in plan, Step 2) | S19 |
| P-45 | SPEC:342 | "(the rename form) … Ignored, /create-ard and /specify each stop on this folder until it holds a merged prd.md." | rewrite | Task 4 (in plan, Step 2) | S19 |
| P-46 | SPEC:352 | "(`SPECIFY_PRD_NOT_HANDED_OFF`, uncommitted form) … Ignored, every /create-ard and /specify run on this folder stops here until prd.md is on <default>." | rewrite | Task 4 (in plan, Step 2) | S20 |
| P-47 | SPEC:359 | "(`SPECIFY_PRD_NOT_HANDED_OFF`, committed form) … Ignored, every /create-ard and /specify run on this folder stops here until prd.md is on <default>." | rewrite | Task 4 (in plan, Step 2) | S20 |
| P-48 | UPS:164 | "**Where step 6 went on past a PRD `/specify` stops on** — … Name none: not `/product-workflows:specify` on it, …; and, where no `prd.md` is in the folder, not `/product-workflows:epics <PRD>` (`EPICS_NO_PRD`)." | rewrite | Task 4, *beyond plan* (F10: `update-spec.md` is Task 5's file too). `/epics` now stops where a `prd.md` is in the folder and on no ref as well (`EPICS_PRD_NOT_HANDED_OFF`), so it leaves the routes named in both states | S51 |
| P-49 | UPS:165 | "- **A `prd.md` in the folder, on no ref** → land it: … `/product-workflows:epics <PRD>` is still named wherever a route above names it, since it reads `prd.md` from the working tree." | rewrite | Task 4, *beyond plan* (F10). False past the gate | S18 |
| P-50 | PG:541–546 | "**The gate is here, not skipped, for the reason step 6 already gates the ledger …** `/product-workflows:create-ard` and `/product-workflows:specify` both gate `prd.md` with their own `require-on-main` before reading it as the PRD …" | rewrite | Task 4 (in plan, Step 2): `/epics` is a third command that now takes no `prd.md` the default branch lacks as the PRD | S31 |
| P-51 | BI:262–263 | "**The `/epics` consent-ordering exception does not apply to this command.** `/epics` resolves docs grounding ahead of its `require-on-main` gates because a later stop would sit after the run's only consent-bearing step …" | rewrite | Task 4, *beyond plan* (F7). Its PRD gate now runs in Phase 0, before Phase 2's resolution; *ahead of its gates* stays true only of Phase 2.5's and 2.6's (EP:399, which the Global Constraints keep) | S30 |
| P-52 | `pw/docs/commands/create-prd.md:166–168` | "- **Hand to a Product Engineer** (PE) → [`/epics <ADDRESS>`](epics.md), or [`/specify <ADDRESS>`](specify.md) … `/epics` waits on nothing this run wrote: what it gates is a PRD-level `specification.md` and a PRD-level ARD, and this run writes neither." | rewrite | Task 4 (in plan) | S15 |
| P-53 | `pw/docs/commands/update-prd.md:96` | "The spec and architecture routes gate this PRD on the specs repo's default branch, …; the Epics and release-note routes wait on nothing this run wrote, since `/epics` gates only a PRD-level `specification.md` and a PRD-level ARD, …" | rewrite | Task 4 (in plan) | S14, S21b |
| P-54 | `pw/docs/commands/update-spec.md:96` | "- **The PRD is one `/specify` would stop on** — … Until then it names no run that would stop on that PRD — not `/specify`, …, not [`/prd-proposal`](prd-proposal.md), and not `/epics` where no `prd.md` is in the folder — …" | rewrite | Task 4, *beyond plan* (F10), with P-48 | S52 |
| P-55 | `pw/docs/roles-and-phases.md:10` | "- **No such branch carries it** — … Several of this plugin's own commands are the exception. … [`/create-ard`](commands/create-ard.md) and [`/specify`](commands/specify.md) stop on the PRD, which was optional to them until 2026-11-14 …" | rewrite | Task 4 (in plan, `pw/docs/**`): the page's list of commands that stop on absence now lacks `/epics`, which stops on a PRD never handed off | S37 |
| P-56 | `pw/docs/roles-and-phases.md:20` | "- **Hands over at the seam:** `/idea` writes `idea.md` … [`/epics`](commands/epics.md) reads the PRD unconditionally through the folder read, with no PRD gate at all — see PE below for the input it does gate." | rewrite | Task 4 (in plan) | S16, S17, S50 |
| P-57 | `pw/docs/roles-and-phases.md:42` | "- **Hands over at the seam:** `/specify` gates on the PRD the same way `/create-ard` does, … `/epics` has no PRD gate at all, but it does gate two other inputs: …" | rewrite | Task 4 (in plan) | S16, S49 |
| P-58 | `.claude/rules/product-workflows.md:38` | "/epics               → [note whether prd.md is on the default branch — offers only, never a gate] → [resolve-docs-grounding — a deliberate exception to §5 rule 2's ordering] → …" | rewrite | Task 4 (in plan, Step 3): opens with `[require-on-main: prd.md]`, as `/prd-proposal`'s line does | S8, S35 |
| P-59 | `docs/maintainers/rationale.md:684` | "**Not taken: gating `/epics`' read of `prd.md` (L13).** `phase-handoff` §4.0 records that a command which knowingly reads the working tree asserts nothing false and needs no gate, …" | rewrite | Task 4 (in plan, Step 4). A note that a feature does not ship, standing beside the feature (`CLAUDE.md`, claim expiry): mark it overruled by M8 beside the new paragraph | S7, S34 |
| P-60 | `dw/docs/getting-started.md:108` | "**A gate.** `/design` refuses to start if `specification.md` is not found on the specs repo's default branch — … (the companion `product-workflows` commands whose gated input was never optional stop too: `/update-spec` …; and so do its `/create-ard` and `/specify` …)" | rewrite | Task 4, *beyond plan* (F8): a list after a colon, presented whole, which `/epics` now joins. A `dev-workflows` page, so Task 6 releases `dev-workflows` as a patch, as batch 1 did for E11–E16 | S36, S53 |
| P-61 | `dw/docs/roles-and-phases.md:10` | "(The companion `product-workflows` has several of its own — each command whose gated input was never optional: `/update-spec` …; and `/create-ard` and `/specify`, whose PRD was optional to them until a decision of 2026-11-14 made it required: …)" | rewrite | Task 4, *beyond plan* (F8), as P-60 | S36b |
| P-62 | `dw/docs/commands/design.md:59` | "**Of the inputs this plugin gates on the default branch, this is the one that genuinely stops on absence**: … (the companion `product-workflows` commands whose gated input was never optional stop too, and so do its `/create-ard` and `/specify` on an idea-route PRD that was never written and, on either route, on a `prd.md` in the folder that was never handed off)" | rewrite | Task 4, *beyond plan* (F8). Names who stops on a `prd.md` never handed off; one wording with P-60's copy (refinement 8) | S36 |
| P-111 | `dw/docs/commands/ready.md:55` | "- **The gated ARD/spec/design themselves — `/ready` is the one command here whose gated inputs never stop it.** … the companion `product-workflows` commands whose gated input was never optional stop on absence too, as its `/create-ard` and `/specify` do on an idea-route PRD that was never written and, on either route, on a `prd.md` in the folder that was never handed off." | rewrite | Task 4, *beyond plan* (F8). Fix round 1: its line corrected from :57, and moved from keep. *as … do* gives an example, but P-62 rewrites the same claim in `design.md:59`, so the `dev-workflows` copies take one wording (refinement 8), with P-62 and P-125. Its *this plugin's one gated input that genuinely stops on absence* clause is batch 2's (design §5.5) | S58 |
| P-121 | SPEC:244–246 | "That remedy runs in the state this stop reports: `/product-workflows:epics` takes the PRD address this step already resolved, and gates no file this run has written — its gates are `<PRD-dir>/specification.md` and the PRD-level ARD, and this run has written neither." | rewrite | Task 4, *beyond plan* (fix round 1). The gloss on `SPECIFY_EPIC_NOT_FOUND`, whose stop text P-97 keeps. `/epics` now gates `prd.md` too, and the stop is taken in Phase 0 step 3, before *Gate the PRD* (SPEC:318), so where the PRD is not landed the remedy does not run in the state the stop reports: it stops `EPICS_PRD_NOT_HANDED_OFF` or on rows D/E. The claim of S13 and S14/S21b, in a wording the starter probe missed | S54 |
| P-122 | `pw/docs/commands/create-prd.md:78` | "- **Where the folder above holds a `prd.md`**, the stop names that PRD's key, with [`/update-prd`](update-prd.md) to revise it or [`/epics`](epics.md) to re-refine the Epic (on the Epic's key where its folder holds an `epic.md`, otherwise on the PRD's)." | rewrite | Task 4, *beyond plan* (F9): the page copy of P-34, one wording with it | S55 |
| P-123 | `pw/docs/commands/update-prd.md:45` | "- **`<KEY>`** — mandatory, … Where the folder above holds a `prd.md`, the stop names that PRD's key as the likely target, and [`/epics`](epics.md) for re-refining the Epic itself (on the Epic's key where its folder holds an `epic.md`, otherwise on the PRD's). …" | rewrite | Task 4, *beyond plan* (F9): the page copy of P-38 | S56 |
| P-124 | `pw/docs/commands/idea.md:159` | "- **An Epic folder whose parent holds a PRD** → [`/update-prd <PRD-KEY>`](update-prd.md) for that PRD …, [`/epics <KEY>`](epics.md) to re-refine the Epic …, or [`/specify <KEY>`](specify.md) to specify it, once that PRD's handoff is merged wherever the specs tree is a git repository." | rewrite | Task 4, *beyond plan* (F9): the page copy of P-39, the same trailing clause, read as the last item's, which now binds `/epics` too | S57 |
| P-125 | `dw/docs/commands/ready.md:94` | "- [`/design`](design.md) — the opposite extreme on the same gate: … (the companion `product-workflows` commands whose gated input was never optional stop too, as its `/create-ard` and `/specify` do on an idea-route PRD that was never written and, on either route, on a `prd.md` in the folder that was never handed off) …" | rewrite | Task 4, *beyond plan* (F8), with P-62 and P-111: one wording across the `dev-workflows` copies. Its *the only gated input in this plugin that does* clause is batch 2's (design §5.5) | S58 |
| P-126 | `pw/docs/commands/prd-ground.md:453–454` | "On the idea route, `prd.md` itself — a claim list read off an unmerged artifact would ground a document `/create-ard` and `/specify` cannot yet see." | rewrite | Task 4 (in plan, Step 2): the page copy of P-50; `/epics` is a third command that takes no unlanded `prd.md` as the PRD, one wording with P-50 | S59 |
| P-127 | UPS:166 | "- **No `prd.md`, on the idea route** → `/product-workflows:create-prd <PRD>`, in `/epics`' place wherever a route above names it: …" | rewrite | Task 4, *beyond plan* (F10), with P-48 and P-49. Read with :164's *each run left out follows once it is cleared*, it names a PRD-writing run in `/epics`' place with `/epics` to follow; as the controller has decided (§8, fix round 1), that remedy gains the merge of `/create-prd`'s handoff, since writing the PRD does not clear the state for `/epics` (nor, since batch 1, for `/specify`) | S60 |
| P-128 | SPEC:1406 | "… **PRD-level spec** (`focus_key` is null …) → `/product-workflows:epics <PRD>` (PE) `<merge-clause>`, which stops rather than skipping wherever this spec reached a branch (§3.3 rows D/E) and, wherever it reached none, skips exactly as it did before (§3.4's `/epics` row) — …" | rewrite | Task 4, *beyond plan* (the pointer face of `CLAUDE.md`'s sentence-context bullet). Since Task 2 §3.4 holds two `/epics` rows, `prd.md`'s and the PRD-level `specification.md`'s, and the pointer means the second: name it. The offer itself is P-95's, kept | S61 |

## 4. The population — rows kept

| # | file:line | First words | Disposition | Why | Strings |
|---|---|---|---|---|---|
| P-63 | PH:314 | "Row F is the difference between "this phase was not handed off" and "this phase never happened". … **An input that was optional before this gate existed stays optional unless a recorded decision makes it required, and the row that then stops on it says so**" | keep | `/epics`' row stops by a recorded decision (M8) and says so; its PRD was never optional to `/epics` (`EPICS_NO_PRD`). Re-read after Task 2 | — |
| P-64 | PH:263 | "\| H \| — \| — \| gate of §3.1 fails \| **silent skip** — … `/create-ard`'s and `/specify`'s PRD rows (§3.4) testing the folder's own `prd.md` and `/update-spec`'s base row stopping among them" | keep | *among them* lists by example; `/epics` on `unmanaged` goes on as today, step 1b testing the folder's own file (EP:191–196) | — |
| P-65 | PH:352 | "**What the refusal does to their rows is nothing** … `/create-ard`'s and `/specify`'s PRD rows say *"Gate the PRD — on every route"* …" | keep | An example of a build-ladder row read on its own Input's route; `/epics`' row is on both routes too, and the sentence does not list. Re-read after Task 2 | — |
| P-66 | PH:268 | "\| B \| present \| differs \| a branch **this run itself created or reused during this run** …" | keep | The row's text is right; measurement 2 shows it reachable for `prd.md` on an `/epics` run, and the plan sends `pass_amending` on to step 1b (F3, *ruling*). No PH edit unless the ruling asks for one | — |
| P-67 | PH:530, :537 | "- **gated — stopping** (§4.3's first array), where **any** §3.4 row naming the artifact says *stops* …" / "**The PRD is what the quantifier was written for** …" | keep | Measurement 4: the PRD is gated — stopping already; one more stopping row changes neither class nor array. :537 says *Read the rows; never carry either membership list above* | — |
| P-68 | PH:412 | "\| `idea.md`, the PRD, the ARD, `specification.md`, … \| gated \| each is named in a §3.4 row" | keep | The PRD is still named in §3.4 rows (measurement 4) | — |
| P-69 | PH:441 | "\| `epic.md` \| gated \| named in §3.4's `/create-ard` `/specify` **(an Epic)** row … so `/epics`, whose set it lifts to *gated*, presents §4.3's falling-back array …" | keep | The new row names `prd.md`, which `/epics` never hands off (EP:931); its own array is unchanged (measurement 4) | — |
| P-70 | PH:398–402 (PH:402 after Task 2) | "\| **advisory** \| no §3.4 row, **but** a command reads the artifact … (`/prd-ground` stops on a moved pin …; `/epics` on a `prd.md` stating no requirements) …" | rewrite | Task 2, *beyond plan* (Task 2's review, Important 1; first kept here on its contents-stop half alone): the clause gave `/epics` reading `prd.md` as a stop inside an *advisory* artifact, which the new §3.4 row and the register (the PRD is *gated*, PH:413) contradict. The example becomes `/brd-split` on a root's `brd/brd-inventory.md` holding no row, `BRD_SPLIT_EMPTY_INVENTORY`, which the register classes advisory and calls a contents stop (PH:424; `brd-split.md` step 8) | S62 |
| P-71 | PH:231 | "Runs in most callers' Phase 0 immediately after `specs-preflight`, … a caller whose check runs a phase or more after its preflight too — `/ready`, `/epics`, …" | keep | `/epics`' Phase 2.6 check still does; the sentence does not deny a Phase 0 gate beside it. Re-read after Task 2 | — |
| P-72 | NPO:136 | "**Where this rule applies:** … every one of them that names a downstream gate its run feeds carries the placeholder. … the fifth, `/product-workflows:update-prd`, named two downstream commands that gate this run's own PRD …" | keep | The rule binds `/create-prd`'s and `/update-prd`'s `/epics` offers once `/epics` gates `prd.md`; Task 4 Step 1 (P-31, P-35, P-36) makes them carry the placeholder. *the fifth … named two* is the history of that conversion | — |
| P-73 | NPO:146 | "**The family scope is deliberate** … the two downstream offers that intersect it (`/specify`, `/create-ard`) already carry `<merge-clause>` …" | keep | A recorded measurement, and re-measured here (measurement 3): even widened, check 11 derives no `prd.md` writer for `/update-prd` or `/create-prd`, so their `/epics` offers would not fire either | — |
| P-74 | NPO:304 | "- `/product-workflows:create-ard <PRD>` (PRD-level) → PE → `/product-workflows:epics <PRD>` (recommended) or `/product-workflows:specify <PRD>` …" | keep | `/create-ard` passed its own PRD gate (ARD:277), so `prd.md` is on the default branch (or the tree is unmanaged) when it offers `/epics` | — |
| P-75 | NPO:316 | "- `/product-workflows:specify <PRD>` (PRD-level spec) → `/product-workflows:epics <PRD>`, …" | keep | `/specify` passed its own PRD gate (SPEC:318) | — |
| P-76 | NPO:331–338 | "- `/product-workflows:update-spec <KEY>` (a merged specification revised in place) → … Where the PRD folder holds no `prd.md`, or its Phase 0 went on past a PRD `/product-workflows:specify` stops on, its Phase 8 says what it names first and names no run that would stop on that PRD." | keep | Generic; true once P-48 and P-49 make UPS's Phase 8 leave `/epics` out in both states | — |
| P-77 | `.claude/rules/workflows-core-handoff.md:24` | "… sixteen consumers call `require-on-main` — `/create-prd`, …, `/epics`, …" | keep | `/epics` is already counted | — |
| P-78 | EP:399 | "**Documentation grounding (optional, independent of code scan).** … This runs ahead of Phase 2.5/2.6's `require-on-main`/`workflows-core:ard-resolution` gates — a deliberate exception …" | keep | Still ahead of Phase 2.5/2.6's gates, as the Global Constraints require; re-read after Task 3 for what the new Phase 0 gate makes false | — |
| P-79 | EP:61–70, :174, :272–281 | "**Then settle the specs checkout, before step 1a or 1b reads anything.**" / "**Check the branch the run stands on.**" / "**Specs-repo preflight** — run at the end of step 1 …" | keep | The order the new gate slots into: after the preflight, step 1a and branch-check (PH:632: branch-check runs *before anything reads or gates the folder's documents*), before step 1b. Re-read after Task 3 | — |
| P-80 | EP:24 | "**Ending early.** Every stop in this command — each `EPICS_*` stop, …, a stopping `require-on-main` state, …" | keep | Covers `EPICS_PRD_NOT_HANDED_OFF` and the gate's stopping rows by class | — |
| P-81 | EP:14 | "`/epics` is the **keyed Epic-writing** workflow. Given a Product Requirements Document key, it reads the PRD plus its existing Epics from the resolved PRD folder, …" | keep | It still reads them from the folder, past the gate | — |
| P-82 | EP:3 | "description: "Drafts the child Epics of a PRD … refuses a BRD- container and a PRD- folder with no PRD yet."" | keep | A capability blurb naming refusals by example; it says nothing of landing, so nothing in it is false. Task 3 may extend it within the 1024-character budget | — |
| P-83 | EP:968 | "On the first choice, execute `handoff-to-main` … a later `/epics` run on the same PRD while that pull request is open reuses the branch (§2.2 rule 3; the preflight's B3 has already kept the run on it); …" | keep | True; the B3 stay it names is what makes row B reachable for `prd.md` (measurement 2) | — |
| P-84 | EP:959–966 | "Runs once Phase 7.4 has returned, and before Phase 8. … present §4.3's **gated — falling back** array … save where any declared `epic.md` is **edited** …" | keep | Measurement 4: `prd.md` is not in `/epics`' handoff set; `epic.md`'s rows are unchanged | — |
| P-85 | `pw/docs/commands/epics.md:68` | "- **A specs checkout not behind for the PRD** — … merge the default branch in, where this run builds on that branch — its own `epics/` branch, or an earlier phase's open branch it stacks on — …" | keep | Describes §6.1 as it runs; follows P-7's ruling (F1): rewrite in Task 3 if PH §6.1 drops `/epics`' stack case | — |
| P-86 | `pw/docs/commands/epics.md:19` | "Every refusal of a resolved folder is taken after the specs-repo preflight has settled the specs checkout's branch — …" | keep | Still true; the gate's stops sit between the branch check and the shape refusals, which Task 3 says. Re-read after Task 3 | — |
| P-87 | `pw/docs/commands/epics.md:71` | "- **`$DOCS_PATH`** (optional, default `/workspace/docs`) — resolved in Phase 2, **before** the Phase 2.5/2.6 ARD and spec gates, a deliberate ordering exception …" | keep | Still before those gates; re-read after Task 3 | — |
| P-88 | CPRD:882–886 | "Then **offer** (commit-when-asked — never automatic), … presenting its **gated — stopping** array verbatim …" | keep | Measurement 4 | — |
| P-89 | CPRD:941 | "- **Handing to PA (`/product-workflows:create-ard <ADDRESS>`) or PE (`/product-workflows:epics <ADDRESS>`), even yourself?** → run **`/clear`** …" | keep | Context hygiene; names no wait for either command | — |
| P-90 | UPRD:192 | "4. **Hand off** (commit-when-asked — never automatic). … present its **gated — stopping** array verbatim …" | keep | Measurement 4 | — |
| P-91 | ARD:1025–1043 | "**One precondition governs every `/product-workflows:epics` option below, and only a slice can fail it.** …" | keep | Still true: this run passed its own PRD gate on the same file, so wherever a `prd.md` is there it is on the default branch (or the tree is unmanaged), which `/epics`' new gate asks | — |
| P-92 | ARD:1072, :1084, :1095–1100 | "- **PRD-level ARD** (the idea route …): if the PRD has 0 Epics → `choices: ["Hand to a Product Engineer — /product-workflows:epics <ADDRESS> (PE) (Recommended) <merge-clause>", …]` …" | keep | Offers by a run past its own PRD gate; the clause is there for the ARD, and the PRD is landed | — |
| P-93 | ARD:1157 | "- **Handing to PE (`/product-workflows:epics <PRD>` / `/product-workflows:specify <EPIC>`) or Dev …, even yourself?** → run **`/clear`** …" | keep | Context hygiene; names no wait | — |
| P-94 | SPEC:1408–1420 | "**One precondition governs every `/product-workflows:epics` option above, and only a slice can fail it.** …" | keep | As P-91 | — |
| P-95 | SPEC:1406, :1459 | "… **PRD-level spec** (`focus_key` is null …) → `/product-workflows:epics <PRD>` (PE) `<merge-clause>` …" / "- **`/product-workflows:epics <PRD>`**, on a PRD-level spec only …" | keep | A run past its own PRD gate; the clause is for the `specification.md` it wrote | — |
| P-96 | SPEC:624–688 | "- **PRD with exactly 1 Epic, on a multi-component PRD …** … `choices: ["Split into Epics first with /product-workflows:epics (Recommended)", …]` … **`/product-workflows:epics` is only offered where the resolved folder holds an authored `prd.md`.**" | keep | Step A runs after Phase 0's PRD gate, so an authored `prd.md` there is a landed one | — |
| P-97 | SPEC:243 | "`SPECIFY_EPIC_NOT_FOUND: no Epic folder for <EPIC> under <the resolved PRD dir> — … Run '/product-workflows:epics <PRD>' to draft this PRD's Epics, then re-run '/product-workflows:specify <EPIC>'.`" | keep | F13: taken before `/specify`'s PRD gate, so where the PRD is not landed the `/epics` run it names stops `EPICS_PRD_NOT_HANDED_OFF`, which names the landing (one more round, L12's cost). Outside design §5.6's L8 scope, which binds offers by a run that wrote `prd.md`. The stop text only: its gloss at :244–246, which states `/epics`' gates, is P-121, rewritten (fix round 1) | — |
| P-98 | UPS:162 | "End the report with a `### Next step` … `/product-workflows:epics <PRD>` `<merge-clause>` to refine, where the PRD folder holds a `prd.md` …" | keep | The clause is for the `specification.md` it wrote; the unlanded-PRD case is P-48's | — |
| P-99 | PG:564, :576 | "… Ignored, every /prd-ground run on this folder stops here until prd.md is on <default>." | keep | Read per the brief for whether `/epics` belongs: it names the stop's own command and enumerates no consumers, so it does not | — |
| P-100 | PP:218, :228, :266, :281 | "… Ignored, every /prd-proposal run on this folder stops here until it holds a merged prd.md." (and the three like it) | keep | As P-99 | — |
| P-101 | PG:742–743 | "The `/epics` consent-ordering exception — resolving *ahead* of a `require-on-main` gate (`commands/epics.md` Phase 2) — is deliberately not taken here …" | keep | *a* gate: still ahead of Phase 2.6's | — |
| P-102 | `pw/docs/commands/brd-intake.md:118` | "… The [`/epics`](epics.md) consent-ordering exception does not apply here: `/brd-intake` runs no `require-on-main` gate, …" | keep | Says nothing of where `/epics`' gates sit | — |
| P-103 | BRD route, `brd-split.md:1415`, `brd-intake.md:153`, `:232`, `brd-proposal.md:40` | "… BRD-route detection in `/product-workflows:create-prd`, …, `/product-workflows:epics` step 1a …" (and the three like it) | keep | The brief's `/brd-*` offers: `/brd-interview`, `/brd-package` and `/brd-reconcile` name `/epics` nowhere, and these four name it only as a reader of `brd-link.md` or a container refusal | — |
| P-104 | `pw/docs/commands/update-spec.md:94` | "- **An Epic's `## Covers` or the PRD's `_coverage.md` was named** → [`/epics <PRD>`](epics.md) (PE), to refine the Epics — where the PRD folder holds a `prd.md`, which `/epics` needs. …" | keep | The unlanded-PRD case is the bullet at :96 (P-54) | — |
| P-105 | `pw/docs/workflow.md:56`, `wc/docs/family-map.md:117` | "createvi -->\|prd.md\| epics" / "createprd -->\|"prd.md"\| epics" | keep | The sibling edges into `/create-ard` and `/specify` carry the bare artifact too; no edge label names a landing save the one into `/prd-proposal` | — |
| P-106 | `pw/docs/reference/environment.md:13` | "**When it points somewhere unreadable.** … Most commands then go on without the check. … `/create-ard` and `/specify` go on where the PRD folder holds a `prd.md`, …" | keep | `/epics` on an unmanaged tree is unchanged: it goes on with a `prd.md` and stops `EPICS_NO_PRD` without one, as before the gate | — |
| P-107 | `pw/docs/getting-started.md`, `pw/docs/brd-workflow.md`, `pw/docs/workflow.md` | (the brief's pages) | keep | Read whole for `/epics`: they name it as a reader of `DOCS_PATH` and `REPOS_PATH`, as the primary style checker's user, in the diagram, the role table and the BRD route's mechanisms, and state nothing about its PRD's branch state | — |
| P-108 | `wc/docs/reference/references.md:27` | "- `phase-handoff.md` — … or a stop where its input was never optional, where a recorded decision made it required, as one did on 2026-11-14 for the PRD `/create-ard` and `/specify` build from on the idea route, or where the input is in the folder and was never landed …" | keep | Its categories cover `/epics`' row; the 2026-11-14 decision is an example | — |
| P-109 | `wc/docs/family-map.md:196` | "- **`/dev-workflows:conformance` is drawn twice, once per role.** … `/epics` for an `epic.md`, …" | keep | The amend-document recommendation; P-110's rule carries the clause | — |
| P-110 | `dw/commands/conformance.md:572–586` | "- a PRD run → … `/product-workflows:epics <PRD-KEY>` or `/product-workflows:create-ard <KEY>`, as the note names; … An offer carries `<merge-clause>` … where Phase 6 handed off a document the offered command gates …" | keep | The rule is by gate, so the `/epics` offer takes the clause wherever Phase 6 handed off an annotated `prd.md`, once `/epics` gates it — no edit | — |
| P-112 | `dw/docs/reference/environment.md:13` | "… a command that requires the document it gates says what it does instead, as the companion `product-workflows` plugin's `/update-spec` stops …, and its `/create-ard` and `/specify` stop where an idea-route PRD folder holds no `prd.md`." | keep | Unmanaged-tree examples; `/epics` is unchanged there | — |
| P-113 | `dcw/docs/reference/environment.md:13` | "… Most callers proceed as they would with no gate at all; a caller that requires its document, or a merged state, says what it does instead — among them …" | keep | *among them*; `/epics` unchanged on an unmanaged tree | — |
| P-114 | `.claude/rules/plugin-updates-coupling.md:26` | "- **Update `workflows-core` 1.91.0 with `product-workflows` 3.82.0**: … its `/epics` and `/update-spec` load 1.91.0's PE lane, which cites `/epics`' Phase 0 *Note whether the PRD is landed* …" | keep | A release-pair bullet, true of that pair; Task 6 writes this release's | S11 |
| P-129 | `pw/docs/commands/specify.md:23`, `:45`, `:100`, `:139` | "- **A PRD with 0 Epics and an authored `prd.md`** — offered *Split into Epics first with /product-workflows:epics* …" / "noepics -->\|"Split first — authored PRD exists"\| split[…]" / "… and [`/epics`](epics.md) **only where the PRD folder — the slice — holds an authored `prd.md`** …" / "- **PRD-level spec** → [`/epics <PRD>`](epics.md) (PE), after the merge, where the folder holds an authored `prd.md`; …" | keep | Fix round 1: the page copies of P-94 to P-96, offers by a run past its own PRD gate, so an authored `prd.md` there is a landed one | — |
| P-130 | `pw/docs/commands/create-ard.md:204`, `:217`, `:221` | "Its next-step offer names `/product-workflows:specify ACME-001-01`; the second option is `/product-workflows:epics ACME-001-01` **only where the slice already holds an authored `prd.md`**." / "- **PRD-level ARD on the idea route, no Epics yet** → [`/epics <PRD>`](epics.md) (PE, recommended) …, both after the merge." / "  - `/epics <SLICE-KEY>` (after the merge) where the slice holds an authored `prd.md`;" | keep | Fix round 1: the page copies of P-91 and P-92, offers by a run past its own PRD gate | — |
| P-135 | `dcw/commands/release-notes.md:767` | "- **A PA/PE phase still pending for this PRD (e.g. `/product-workflows:create-ard`, `/product-workflows:epics`), even yourself?** → run **`/clear`** before switching roles." | keep | Fix round 1: P-119's *Context hygiene* twin. It names no wait for either command, as P-89's and P-93's lines name none; the review proposed *later 3*, and batch 3 reads it beside P-119 | — |

## 5. Later batches, recorded and left

| # | file:line | First words | Disposition | Why | Strings |
|---|---|---|---|---|---|
| P-115 | `dw/commands/design.md:115–116` | "- **No Epic folder, and a flat `specification.md` on `<default>`** → ask: `choices: ["Split into Epics first — /product-workflows:epics <PRD> (Recommended)", …]` — the *Split* option only where the PRD folder holds an authored `prd.md`, which `/epics` needs; …" | later 2 | L8: `/design` does not test `prd.md`'s landing, and `/epics` now stops on an unlanded one. Restates NPO's precondition (P-12), so it moves with that ruling; batch 1 left the like `/create-ard` offer of `design.md` to batch 2 (L-B2-27) | — |
| P-116 | `dw/commands/design.md:240–241` | "`choices: ["<Re-split — /product-workflows:epics <EPIC> \| Add the component first — /product-workflows:create-ard <PRD>> (Recommended)", …]`" | later 2 | As P-115 | — |
| P-117 | `dw/commands/implement.md:219` | "… save **0 Epics**, which asks `choices: ["Split into Epics first — /product-workflows:epics <PRD> (Recommended)", …]` — the *Split* option only where the PRD folder holds an authored `prd.md`, which `/epics` needs; …" | later 2 | As P-115 | — |
| P-118 | `wc/references/components.md:120–123` | "- `epic_target` `missing` or `outside_set` → `/product-workflows:epics <EPIC>`, … else `/product-workflows:epics <PRD>` …" | later 2 | Remedies `/implement` and `/ready` print (at `epics` scope `/epics` prints them past its own gate) | — |
| P-119 | `dcw/commands/release-notes.md:760` | "[… If earlier pipeline phases remain, continue — hand to PA → `/product-workflows:create-ard <PRD>` or PE → `/product-workflows:epics <PRD>`; …]" | later 3 | Batch 1's L-B3-7 for the same line's `/create-ard`: `/release-notes` tests `prd.md` only in the working tree | — |
| P-120 | `pw/docs/workflow.md:49` | "rnpm -.->\|"an earlier phase still pending — hand to PE"\| epics" | later 3 | The diagram edge of P-119's offer | — |
| P-131 | SPEC:676–677 | "`"Author the PRD first — /product-workflows:create-prd <PRD> (Recommended)"` (without `(Recommended)` on the multi-component array), which is the run that writes the PRD `/epics` then reads and takes the single address this run already resolved." | later 4 | Fix round 1. A slice-only form — an idea-route folder with no `prd.md` stops at *Gate the PRD* first (SPEC:674–675) — of the zero-Epics question design §5.4 gives batch 4; `/epics` now reads that PRD only once it lands | — |
| P-132 | `dw/commands/implement.md:270–271` | "- **PRD with 0 Epics** → offer: split with `/product-workflows:epics` first, or implement one broad PRD-level slice (`focus_key` stays null). …" | later 2 | Fix round 1: the prose twin of P-117 | — |
| P-133 | `dw/docs/commands/implement.md:17` | "`/implement` implements **one Epic per run**. … a PRD with no Epics offers to split with `/product-workflows:epics` first, or to implement a broad PRD-level slice. …" | later 2 | Fix round 1: P-117's page copy | — |
| P-134 | `wc/references/epic-picker.md:42` | "- **None** → the command's own no-Epics policy — typically: split with `/product-workflows:epics` first, or author one broad PRD-level artifact." | later 2 | Fix round 1: the shared no-Epics policy `/design` and `/implement` follow (P-115, P-117); `/specify`, which follows it too, does so past its own PRD gate | — |

## 5a. Generated copies — `plugins/workflows-core/reference-parts/`

Never edited; Task 2 regenerates them with `python3 scripts/reference-parts.py generate` after editing PH and NPO. Copies of the changed strings found at `e1b64243`: S5 `next-phase-offer/pe.md:170`; S6 `phase-handoff/require-on-main.md:230`; S10 `require-on-main.md:251`; S11 `next-phase-offer/pe.md:171`; S12 `require-on-main.md:230`; S25 `next-phase-offer/pm.md:166`; S26 `phase-handoff/branch-check.md:41`, `handoff-to-main.md:57`, `require-on-main.md:49`; S27 `branch-check.md:75`; S28 `branch-check.md:78`; S29 `next-phase-offer/dev.md:157`, `epics-precondition.md:51`, `pa.md:165`, `pe.md:181`, `pm.md:169`; S44 `require-on-main.md:192`; S45 `require-on-main.md:152`. The §3.4 table, and so P-1's new row, is in `require-on-main.md`.

## 6. CHANGELOG hits — history, never rewritten

`pw/CHANGELOG.md:25` (*`/epics` leads its offers with the PRD's landing. It still reads `prd.md` from the working tree, ungated, …*), `:27` (*the `/epics` page that it names the PRD's landing*), `wc/CHANGELOG.md:18` (*The PE lane offers `/product-workflows:specify <EPIC>` and `/product-workflows:create-ard <EPIC>` after `/product-workflows:epics`, each after the landing …*). Searched with `grep -n "landing first\|names the landing\|land the PRD\|epics.\{0,120\}not on the default branch\|epics.\{0,200\}landing" plugins/*/CHANGELOG.md` and the starters above; Task 6's sections say what changed.

## 7. The four measurements

### Measurement 1 — `/epics <KEY>` with the PRD on an unmerged `prd/` branch and the checkout on the default branch

**Today the preflight never moves the checkout onto that branch, and the run never reaches the PRD.** On the default branch §3.5's first row is *B1 \| On the default branch \| Nothing further.* (`wc/references/specs-repo-git.md:530`); B3, the row that stays on a plugin branch, applies only where HEAD already is one (`:532`). The one preflight switch onto an existing plugin branch is *A re-run in the same run switches back first* (`:625–636`), made only by a command that runs the preflight twice in one run (`/document`, `/release-notes`); `/epics` runs it once, at the end of step 1 (EP:61–70, EP:272). So the PRD folder in the working tree holds no `prd.md`, and:

- **(a) The folder is on the default branch through another carrier** — `idea.md` that `/idea` landed, or a slice's `brd-link.md`. The address resolves; branch-check passes (§6.1 applies only where HEAD is a plugin branch, PH:644; §6.2 asks only about an open `epics/` branch, PH:663); step 1b's table finds no `prd.md` (EP:191–196, *Anything else*) and stops **`EPICS_NO_PRD`** (EP:236), whose remedy on an idea-route folder is `/product-workflows:create-prd <KEY>` (EP:225) — a second PRD while the first waits on its pull request — and on a slice whatever its ledger resolves, `/create-prd <KEY>` where the gate set clears (EP:226–230).
- **(b) The folder exists only on the `prd/` branch** — a `/create-prd` with no `/idea` before it writes `PRD-<KEY>-<slug>/` on its first write (EP:47–49), so its handoff left the folder on that branch alone. `resolve-address` globs the working tree and keeps only a folder whose carrier asserts the key (`wc/references/addressing.md:470–495`), finds none, and the run stops **`EPICS_NOT_FOUND`** before the preflight (EP:41–45; a run that stops on its address runs none, `specs-repo-git.md:286–287`), naming `/product-workflows:create-prd <KEY>` as the run that writes a PRD into the folder (EP:45). No gate placed after the preflight reaches this state (F4).
- **(c) The one way today's run reaches that PRD from the default branch** is §6.2: where an earlier `/epics` run's `epics/` branch — cut stacked on the `prd/` branch because that run read `prd.md` there (PH:77) — holds open work under the root, branch-check asks `["Switch to <branch> and continue there (Recommended)", "Stop — …"]` (PH:663–669); on *Switch* the run reads `prd.md` from that branch, step 1b accepts, and the run drafts, `prd_landed` false, warning only (EP:296–311).

(With the checkout on the `prd/` branch itself, not the state asked, B3 keeps it there, since `branch-key` resolves `prd/<KEY>-<slug>` to the run's key (`specs-repo-git.md:532`, `:588–602`), and today's run drafts from it, warning.)

**For Task 3's walk:** with the gate after branch-check and before step 1b, (a) stops on the gate's row D or E — `prd.md` not on `<default-ref>`, found on the `prd/` plugin ref (PH:272–273) — before `EPICS_NO_PRD`, which is Review Focus 2; (c) stops on D or E as well; the `prd/`-HEAD case stops on D/E (a new PRD) or meets row C (a revision of a merged one); (b) is unchanged.

### Measurement 2 — can `require-on-main` return `pass_amending` for `prd.md` on an `/epics` run?

**Yes.** `pass_amending` is row B (PH:380): `prd.md` present on `<default-ref>`, the working copy different, and HEAD *a branch this run itself created or reused during this run* — *reused because `specs-repo-git.md` §3.5 B3 kept the preflight checkout on it AND the branch is the caller's own — its prefix is this caller's and its key is in the run key set* (PH:268) — with row B′ not firing: the default branch has not changed `prd.md` since that branch forked (PH:267). `/epics`' prefix is `epics` (EP:20) and a re-run stands on its own unmerged `epics/<PRD-KEY>-<slug>` branch by design: *a later `/epics` run on the same PRD while that pull request is open reuses the branch (§2.2 rule 3; the preflight's B3 has already kept the run on it)* (EP:968; B3 at `specs-repo-git.md:532`, `epics/` among `branch-key`'s prefixes at `:588`). `/epics` never writes `prd.md` itself (EP:931), so a difference on its branch is always inherited or someone else's. The states:

1. **A stacked `epics/` branch.** An `/epics` run that read `prd.md` on an open `prd/` branch cuts its own branch at HEAD (PH:77, *the run builds on that branch's work* — *`/epics` partitioning a PRD whose pull request is still open*). Where that `prd/` branch is an `/update-prd` revision of a merged PRD, `<default-ref>` holds revision 1, the `epics/` branch revision 2, committed, and the fork point revision 1, so B′'s test (`git diff --quiet "$(git merge-base HEAD <default-ref>)" <default-ref> -- ./<path>`, PH:267) exits 0 and row B passes: `pass_amending`, printing *reading <path> from your in-progress epics/…, which amends the approved version on <default>* (PH:268). The run then drafts from a revision whose pull request is open — the state M8 refuses. Every such branch an `/epics` run cuts before batch 1b ships stays reachable; after it, no `/epics` run reaches its handoff from a `prd/` HEAD that changed `prd.md` (rows D/E stop it, or row C, PH:271, switches it to the default branch), so none is cut again.
2. **A commit that touched `prd.md` on the `epics/` branch**, made by hand — the same reading.
3. **An uncommitted edit of `prd.md` with the checkout on the `epics/` branch** — a hand edit, or an `/update-prd` run made there whose handoff was declined. `prd.md` is an OTHER path, so G1 fires and ends the preflight before §3.5 runs (`specs-repo-git.md:407`, *Any match ends the preflight*, and G1 at `:413`), leaving HEAD on the branch. Whether row B's *reused because §3.5 B3 kept the preflight checkout on it* covers a branch G1 left HEAD on is not settled by the text: if it does, `pass_amending`; if not, row C′ or C (PH:269, :271).

Not row B, on a literal reading: a branch §6.2's *Switch* moved the run onto (PH:663–669), since row B names only the run's own handoff and B3; such a run meets C′/C on a differing `prd.md`.

**What the offers print there.** Today `prd_landed` is true on `pass_amending` — the file is on `<default-ref>` (EP:304–307) — so no landing sentence prints, and the offers of `/product-workflows:specify <EPIC>` and `/product-workflows:create-ard <EPIC>` (EP:1148) name runs that, on the same checkout, meet row C′, C″ or C on that `prd.md`: HEAD is an `epics/` branch, not their prefix, so row B does not pass them (PH:268) — a repair offer that switches to the default branch, or a stop. The plan's table sends `pass_amending` on to step 1b; Task 3 has to say what the offers print, and the controller whether `/epics` should go on at all (F3).

### Measurement 3 — check 11 once PH §3.4 names `/epics` on `prd.md`

**It then requires `<merge-clause>` of no array, and prints nothing.** The test: a copy of `HEAD` (`git archive HEAD | tar -x`) in the session's scratchpad; in the copy only, `| \`/epics\` | \`prd.md\` | **stops** — test row |` inserted after PH:337, the `/prd-proposal` · `prd.md` row; then `./scripts/check-docs.sh --root <copy>`, from the worktree. Exit 0, and the output byte-identical to the same run on the unmodified copy (`cmp` reports no difference):

```
  check 9 cost-emitting-commands assertion not applicable: plugins/guideline-reviewers ships no docs/reference/session-cost.md
  check 9 cost-emitting-commands assertion not applicable: plugins/prose-style ships no docs/reference/session-cost.md
PASS: docs are consistent with the plugin(s) under plugins/dev-workflows plugins/guideline-reviewers plugins/workflows-core plugins/docs-workflows plugins/product-workflows plugins/security-workflows plugins/prose-style
```

Check 11 prints no line on a pass. Why, read from a copy of the script (scratch only) instrumented to print its three relations: the targets gain `epics|prd.md` beside `epics|specification.md`; the family is every `/product-workflows:brd-*` and `/product-workflows:prd-*` command (`CHECK11_FAMILY="glob"`, `scripts/check-docs.sh:161`; the scope line NPO:136; `CHECK11_OFFER_SCOPE="file"`, `:173`; `CHECK11_PROSE=0`, `:167`) — `brd-intake`, `brd-interview`, `brd-package`, `brd-proposal`, `brd-reconcile`, `brd-split`, `prd-ground`, `prd-proposal` — and none of the eight has a `choices:` option naming `/epics`, nor declares `prd.md` among its `deliverable_paths`. The arrays the new row bears on, `/create-prd`'s (CPRD:901) and `/update-prd`'s (UPRD:210), are outside the family; and with the family widened, in a second scratch copy, to `create-prd*` and `update-prd*`, the check still requires nothing, because neither declares a backticked `prd.md` (`deliverable_paths` = *the PRD file*, CPRD:888; *the canonical PRD file*, UPRD:192; their extracted writers `decisions.md prd-seed.md` and `code-grounding.md design-grounding.md`). No command of the family declares a backticked `prd.md` in its `deliverable_paths`. So the clause on those two arrays (P-31, P-36) is held by review alone. On the copy with the row, R1 returns 12.

### Measurement 4 — PH §4's class for `prd.md`, and the consent arrays

**`prd.md` is *gated — stopping* today, and a new stopping row changes no array.** The register classes the PRD *gated* (PH:412). Inside *gated*, the class is *stopping* where **any** §3.4 row naming the artifact says *stops* (PH:530), and PH:537 records that the PRD moved out of the falling-back bullet for that reason — *one stopping row decides the half*. Four rows naming `prd.md` stop today: `/create-ard` (PH:321), `/specify` (PH:322), `/prd-ground` idea route (PH:336), `/prd-proposal` (PH:337); `/update-spec`'s (PH:323) and `/conformance`'s (PH:331) fall back. A fifth stopping row moves nothing. `/create-prd` presents the *gated — stopping* array (CPRD:882–886) and so does `/update-prd` (UPRD:192), each `"Just write the files — I'll handle git (the next phase will stop until this is on main)"` (PH:565) — unchanged. `/epics`' own handoff never carries `prd.md` (EP:931; its set at EP:957–968), and `epic.md`'s rows (PH:324, :331) are untouched, so its falling-back array and the stopping one for an edited Epic (EP:959–966, PH:441) are unchanged too.

## 8. Found beyond the plan, and notes for the controller

- **F1 — PH §2.2 and §6.1 use `/epics` on an open `prd/` branch as their worked example** (P-6, P-7, P-8). After M8 no `/epics` run builds on such a branch. Worse, §6.1's *It does* test is mechanical, so branch-check still classes a `prd/` branch that changed `prd.md` as one `/epics` builds on and names the merge of the default branch into it; the re-run then stops at the PRD gate (rows D/E for a new PRD) or meets row C (a revision), whose repair switches away from that branch. Task 2's file list names neither section. The page line P-85 follows the ruling.
- **F2 — NPO's *`/epics` precondition* (P-12) holds every `/epics` offer to an authored `prd.md` and nothing else.** M8 adds *on the default branch*. Task 2 names NPO:205–206 and :326–330 only. Of the callers that restate the test, `/create-ard`'s and `/specify`'s (P-91, P-94) stay true — their runs passed their own PRD gate — while `dev-workflows`' `/design` and `/implement` (P-115, P-117) test only authorship: rewriting the precondition without them leaves two live instructions at odds, so the ruling on P-12 decides whether they stay *later 2*.
- **F3 — `pass_amending` is reachable for `prd.md` on an `/epics` run** (measurement 2; P-66). The plan's table sends it on to step 1b, so a re-run on an `epics/` branch stacked on an open `/update-prd` pull request drafts from that unmerged revision — what M8 refuses. Row B's rationale is the branch's own amendment, and `/epics` never amends `prd.md`. A ruling is needed: go on (and say what the offers print), or stop on row B for this input.
- **F4 — A PRD folder that exists only on an unmerged `prd/` branch** (a `/create-prd` with no `/idea` before it, the checkout since moved to the default branch) resolves to nothing, and `EPICS_NOT_FOUND` names `/create-prd <KEY>` before any preflight or gate runs (measurement 1 (b)). `/create-ard` and `/specify` share it since batch 1. The design's mapping does not handle it; recorded, not proposed.
- **F5 — `/epics`' own remedies chain a PRD write straight into an `/epics` run** that now stops until the PRD lands: P-22 (not frozen), and P-23, P-24, P-25, P-30 (frozen by the Global Constraints *save a sentence that says `/epics` reads an unlanded PRD*). Each implies `/epics` reads the PRD just written; the ruling is whether they fall under that saving clause.
- **F6 — P-21 and P-29:** *adding the `kind: prd` and `key:` … lets `/epics` read the file as it stands* is false past the gate, which stops on the edited copy until it lands. Review Focus 4's state is next to it: a `prd.md` asserting no `kind: prd`, on no ref, is refused by step 1b, and its remedy must not print *land it*.
- **F7 — `brd-intake.md:262–263` (P-51)** states the `/epics` order exception as *ahead of its `require-on-main` gates*, plural, which the Phase 0 gate makes false. Not in Task 4's expected files.
- **F8 — `dev-workflows` pages** (P-60, P-61, P-62) list the companion commands that stop on a PRD never handed off. Task 4's files name no `dev-workflows` page, so Task 6 owes `dev-workflows` a patch release, a dated `CHANGELOG.md` section and a coupling bullet, as batch 1 did for E11–E16.
- **F9 — The Epic-folder refusals of `/create-prd`, `/update-prd` and `/idea`** (P-34, P-38, P-39) name `/epics <KEY>`, which now stops where the parent `prd.md` is not landed; batch 1 gave the like `/specify` naming the *its handoff merged* clause (K65). Not in Task 4's expected files.
- **F10 — `update-spec.md` is Task 5's file (M10) and holds two rows of this subject** (P-48, P-49, with its page P-54). Tasks 4 and 5 both edit it; one should follow the other.
- **F11 — Check 11 sees none of the `/epics` offers this batch changes** (measurement 3), even widened; the `<merge-clause>` on P-31 and P-36 is review's to hold.
- **F12 — Dev-side and docs-side offers of `/epics`** (P-115 to P-120) name a run that can now stop on arrival but fall outside §5.6's L8 scope; recorded *later 2* and *later 3*, as batch 1's like offers of `/create-ard` and `/specify` were.
- **F13 — `SPECIFY_EPIC_NOT_FOUND`** (P-97) names `/epics <PRD>` before `/specify`'s own PRD gate has run; kept under §5.6's scope. Its gloss, which states `/epics`' gates, is not kept: P-121 (fix round 1).

**Controller rulings, fix round 1** (2026-11-15), applied to the dispositions of P-121 to P-135; the rows they settle stand as dispositioned. `pass_amending` goes on with row B's message, and Phase 9 prints one sentence about it (Task 3; P-66, F3). Every `/epics` remedy that names a PRD-writing run and then an `/epics` re-run gains the merge of that run's handoff — Task 3 for EP and its page (P-22 to P-25, P-30), Task 4 elsewhere (P-127). `dev-workflows` and `docs-workflows` offers of `/epics` are *later 2* and *later 3* (F12; P-132 to P-134 join them). `EPICS_NOT_FOUND` for a folder that exists only on a `prd/` branch is not changed (F4). One disposition departs from the review: P-135, which the review proposed as *later 3*, is kept, as the other *Context hygiene* lines are (P-89, P-93). P-111 and P-125 are rewritten with P-62 rather than kept, so the three `dev-workflows` copies of the claim take one wording.

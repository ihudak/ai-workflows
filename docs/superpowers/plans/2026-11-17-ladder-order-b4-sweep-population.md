# LADDER-ORDER batch 4 — the sweep population

The population every task of this batch sweeps, and the plan's working list: the rows `S-1` to `S-117` of `docs/superpowers/plans/2026-11-17-ladder-order-b4-measurements.md` §10 (*M §10*), each under its own id, with its site, the words measured there, its verdict, the design bullet or ruling that owns it, and the task of `docs/superpowers/plans/2026-11-17-ladder-order-b4-brd-route.md` that takes it; then the rows `N-1` to `N-8`, which the measurements name outside §10's tables or the plan found, and which the plan gives a task. Every line reference is a line of the measurements' tree (`main` at `67b4c740`) and a hint only: find each site by its words.

**Columns.** *Site* and *As measured* are M §10's cells, copied; for the page rows, where §10 gives no quote, the words are M §9's. *V* is the measurer's verdict: **F** false after batch 4 · **U** describes a branch the stop makes unreachable (removed, design §5.4 bullet 4) · **I** incomplete, extend · **R** re-read: true, or true by citation, if the plan keeps it · **T** stays true, checked. *Owner* is the design bullet (§5.4's nine, §5.5's Batch 4 list of twelve, counted in order) or the plan's ruling (R1 to R15) or call (P1 to P7) that decides the row; where the measurements say "found now", the owner is what the plan rules it under. *Taken by* is the plan's task and step. *Status* is kept current by each task: `open`, `done in Task <n> — <what, and the line>`, `stays true — checked (Task <n>): <why>`, or `left as it stands — <reason>`. No row is unassigned: 113 rows have a task, and 4 (S-37, S-59, S-66, S-116) are left as they stand, each with its reason.

**The abbreviations** are the measurements': CPRD, ARD, SPEC, INT, REC, CLF, PH, NPO, IMPL, DES, CONF, RDY, DOC, RN, SCAN, and `pw/docs/` for `plugins/product-workflows/docs/`.

## The rows

### `product-workflows` commands

| Row | Site | As measured (M §10; pages, M §9) | V | Owner | Taken by | Status |
|---|---|---|---|---|---|---|
| S-1 | ARD:23–26 | "`/create-ard <SLICE-KEY>` → an ARD on the **BRD route** … A `BRD-` container is refused (Phase 0 step 1a)." | I | §5.4, its table (M: found now) | Task 2, Step 5 | open |
| S-2 | ARD:161–164 | container refusal: "Name every slice and offer `/product-workflows:create-ard <SLICE-KEY>` once per slice" | I | L8 → R1 (c) (M: found now (L8)) | Task 2, Step 5 | open |
| S-3 | ARD:245, :261–269 | advisory "on a PRD-level run with no `prd.md` — a slice"; "the ordinary BRD-route state, since on that route `/create-prd` is not a prerequisite" | R | §5.4 bullet 8 (M: found now) | Task 2, Step 5 (re-read) | open |
| S-4 | ARD:280, :283 | Gate the PRD: slice holding none → "the slice's ordinary state, kept as it was" | I | §5.4 bullet 8 → R8 (M: §5.4 (placement)) | Task 2, Steps 2 and 5 | open |
| S-5 | ARD:322 | slice form, register sentence | R/decide | §5.5 Batch 4 bullet 4 → R10 (M: §5.5 bullet 4) | Task 7, Step 3 (re-read; batch 1's separation stands) | open |
| S-6 | ARD:330–352 | "**…a slice holding no `prd.md` still goes on.** … still not a prerequisite for this command" | I | §5.4 bullet 8 (M: found now) | Task 2, Step 5 | open |
| S-7 | ARD:378–387 | `CREATE_ARD_REGISTER_NOT_HANDED_OFF` | I (committed form) | §4; §5.4 bullet 7 → R10 (M: §4, §5.4) | Task 7, Step 3 | open |
| S-8 | ARD:496–506 | Phase 2: "reaches this phase only on the BRD route … the slice's **ordinary** state" | I | §5.4 bullet 8 (M: found now) | Task 2, Step 5 | open |
| S-9 | ARD:536–550 | the overturned statement; "Two places do open the ledger" | F | §5.4 bullet 5 (M: §5.4) | Task 2, Step 4 | open |
| S-10 | ARD:921 | requirement-gap line | R (reason) | §5.5 Batch 4 bullet 12 (M: §5.5 last bullet) | Task 2, Step 5 | open |
| S-11 | ARD:1042–1068 | precondition, "naming `/create-prd` without the test below…" | I | §5.5 Batch 4 bullet 12 (M: §5.5 last bullet) | Task 2, Step 5 | open |
| S-12 | ARD:1070–1080 | "has cleared only the container refusal"; "five rows pick among the last five of the six literal arrays" | F | §5.4 bullet 4 (M: §5.4) | Task 2, Step 3 | open |
| S-13 | ARD:1085–1088 | table rows 2–5 | U | §5.4 bullet 4 (M: §5.4) | Task 2, Step 3 | open |
| S-14 | ARD:1090–1095 | dropping rather than annotating | I | §5.4 bullet 4 (M: §5.4) | Task 2, Step 3 | open |
| S-15 | ARD:1100–1104, :1111–1114 | "Six literal arrays"; arrays 3–5, and 6's ledger states | U (keep 6 for `kind: prd`) | §5.4 bullet 4 (M: §5.4) | Task 2, Step 3 | open |
| S-16 | ARD:1115–1119 | "`/specify <SLICE-KEY>` is always reachable from this state" — reason | I | §5.4 bullet 4 (M: found now) | Task 2, Step 3 | open |
| S-17 | ARD:1120–1135 | `/epics` bullet, :1126–1131 | F | §5.4 bullet 4 (M: §5.4) | Task 2, Step 3 | open |
| S-18 | ARD:1136–1148, :1159 | `/brd-split` clause halves | U | §5.4 bullet 4 (M: found now (§5.4's class)) | Task 2, Step 3 | open |
| S-19 | ARD:1149 | "none of the six arrays" | I | §5.4 bullet 4 (M: found now) | Task 2, Step 3 | open |
| S-20 | ARD:1194 | "The ten argument-, tree- and git-shaped stops" | I (+2 ids) | §5.4, its table (the two ids) (M: found now) | Task 2, Step 5 | open |
| S-21 | SPEC:26–28 | usage: "a `BRD-` container is refused (Phase 0 step 0)" | I | §5.4, its table (M: found now) | Task 3, Step 4 | open |
| S-22 | SPEC:80–83 | container refusal: "offer `/product-workflows:specify <SLICE-KEY>` once per slice" | I | L8 → R1 (c) (M: found now (L8)) | Task 3, Step 4 | open |
| S-23 | SPEC:323, :326 | Gate the PRD: slice holding none, ordinary state | I | §5.4 bullet 8 → R8 (M: §5.4 (placement)) | Task 3, Steps 2 and 4 | open |
| S-24 | SPEC:365 | slice form, register sentence | R/decide | §5.5 Batch 4 bullet 4 → R10 (M: §5.5 bullet 4) | Task 7, Step 3 (re-read; batch 1's separation stands) | open |
| S-25 | SPEC:373–392 | "…still goes on." | I | §5.4 bullet 8 (M: found now) | Task 3, Step 4 | open |
| S-26 | SPEC:418–427 | `SPECIFY_REGISTER_NOT_HANDED_OFF` | I | §4; §5.4 bullet 7 → R10 (M: §4) | Task 7, Step 3 | open |
| S-27 | SPEC:603–611 | Step A: no `prd.md` "reaches this step only on the BRD route … the slice's ordinary state" | I | §5.4 bullet 8 (M: found now) | Task 3, Step 4 | open |
| S-28 | SPEC:683–697 | zero-Epics slice form; P-131 sentence :685–686; "the only one of its three refusals this run has cleared" :687–688 | U/F | §5.4 bullet 4; §5.5 Batch 4 bullet 7 (b1b P-131) (M: §5.4, §5.5 (P-131)) | Task 3, Step 3 | open |
| S-29 | SPEC:773–788 | the overturned statement; "Three places do open the ledger" | F | §5.4 bullet 5 (M: §5.4) | Task 3, Step 4 | open |
| S-30 | SPEC:1261 | capture-at-block list of every `SPECIFY_*` | I | §5.4, its table (the two ids) (M: found now) | Task 3, Step 4 | open |
| S-31 | SPEC:1417–1435 | precondition, "naming `/create-prd` without the test below" | I | §5.4 bullet 4 (M: found now) | Task 3, Step 4 | open |
| S-32 | SPEC:1437–1440 | "has cleared only the container refusal" | F | §5.4 bullet 4 (M: §5.4) | Task 3, Step 3 | open |
| S-33 | SPEC:1453–1456 | table rows 2–5 | U | §5.4 bullet 4 (M: §5.4) | Task 3, Step 3 | open |
| S-34 | SPEC:1458–1462, :1474–1479 | dropping; "only a BRD-route slice has a gate set, so the table above is where a slice with no `prd.md` and no `covered-here` row stops the `/create-prd` recommendation" | I/F | §5.4 bullet 4 (M: found now) | Task 3, Step 3 | open |
| S-35 | CPRD:270–375 | step 7, the test's source | R | §5.4 bullet 2 → R6, P6 (M: §5.4 bullet 2 (home)) | Task 1, Steps 2 and 5 | open |
| S-36 | CPRD:405–414 | `CREATE_PRD_REGISTER_NOT_HANDED_OFF` | I | §4; §5.4 bullet 7 → R10 (M: §4) | Task 7, Step 3 | open |
| S-37 | CPRD:909–931 | Phase 6 offers `/create-ard`, `/specify` on the slice | T (same run's ledger passed) | — | — | left as it stands — the same run's step 7 passed the slice's ledger tests before Phase 6 offers either command; Task 1 re-reads it after R6's change |
| S-38 | INT:2524–2535 | *level test alone* | F | §5.4 bullet 3; §5.5 Batch 4 bullet 1 → R5 (M: §5.4, §5.5) | Task 6, Step 2 | open |
| S-39 | INT:2545–2552, :2557 | prose list; eligible array | I | §5.5 Batch 4 bullet 1 → R5 (M: §5.5 (landed)) | Task 6, Step 2 | open |
| S-40 | INT:2563 | not-eligible array | F | §5.4 bullet 3 → R5 (M: §5.4) | Task 6, Step 2 | open |
| S-41 | INT:2573–2591 | "Five of the six lists…"; "which of the three authoring commands comes first" | R | §5.4 bullet 3 (M: —) | Task 6, Step 2 (re-read) | open |
| S-42 | INT:2624–2629 | context hygiene for the authoring ladder | R | §5.4 bullet 3 (M: found now) | Task 6, Step 2 (re-read) | open |
| S-43 | REC:3011–3030 | *always offered* | F | §5.4 bullet 3; §5.5 Batch 4 bullet 1 (M: §5.4, §5.5) | Task 6, Step 3 | open |
| S-44 | REC:3071–3086 | advance list and array — arity where all three drop | I | §5.4 bullet 3 → R4 (M: found now (arity)) | Task 6, Step 3 | open |
| S-45 | REC:3190–3199 | "a refusal this phase can make and their own Phase 0s cannot — unlike the level refusal above, which each of them now makes for itself" | I | §5.4 bullet 3 (M: found now) | Task 6, Step 3 | open |
| S-46 | REC:3201–3214 | "What the clause does not cover … `/create-ard`'s and `/specify`'s on `prd.md`, a file this run does not write either" | R | §5.5 Batch 4 bullet 1 (M: —) | Task 6, Step 3 (re-read) | open |
| S-47 | REC:377–384 | `BRD_RECONCILE_PACKAGE_NOT_HANDED_OFF` | I | §4; §5.4 bullet 7 → R11, P1 (M: §4) | Task 7, Step 4 | open |
| S-48 | `brd-package.md:302`, `:318` | the two stops | I | §4; §5.4 bullet 7 → R11, P1 (M: §4) | Task 7, Step 4 | open |
| S-49 | `brd-package.md:367`, `:466` | `BRD_PACKAGE_ROUNDS_NOT_ON_MAIN` | I | §4 → R11, P1 (M: found now) | Task 7, Step 4 | open |
| S-50 | `brd-proposal.md:444–455` | `BRD_PROPOSAL_SLICE_NOT_HANDED_OFF` | I | §4; §5.4 bullet 7 → R11, P1 (M: §4) | Task 7, Step 4 | open |
| S-51 | `prd-ground.md:337`, `:430` | the two slice stops | I | §4; §5.4 bullet 7 → R11, P1 (M: §4) | Task 7, Step 4 | open |
| S-52 | `epics.md:1212`; `:486`, `:508`, `:728`, `:1146–1149`, `:1334` | offers of `/specify <EPIC>`, `/create-ard <EPIC>`; `### Targets` "`/product-workflows:create-ard <PRD-KEY>` (refine)" | R/decide | L8 → R1, R3, P2 (M: found now (L8, changed-ledger state)) | Task 6, Step 5 | open |
| S-53 | `update-prd.md:204`, `:210` | "Re-run architecture — `/product-workflows:create-ard <KEY>`" | R/decide | L8 → R1, R3, P2 (M: found now) | Task 6, Step 5 | open |
| S-54 | `prd-proposal.md:816`, `:820` | "Raise the tier first — `/product-workflows:create-ard <KEY>`" / `/specify <KEY>` | R/decide | L8 → R1, R3, P2 (M: found now) | Task 6, Step 5 | open |
| S-55 | `idea.md:98` | Epic-folder remedy "specify it with '/product-workflows:specify <KEY>'" | R/decide | L8 → R1, R3, P2 (M: found now) | Task 6, Step 5 | open |
| S-56 | `update-spec.md:52`; `:57`; `:164–166` | `UPDATE_SPEC_NO_BASE` "Author one with '/product-workflows:specify <ADDRESS>'"; the step-6 carve-out (L5); Phase 8 | I | §5.1 (the carve-out), L5 → R3, P2 (M: found now; §5.1 (carve-out)) | Task 3, Step 5 | open |

### `product-workflows` reference

| Row | Site | As measured (M §10; pages, M §9) | V | Owner | Taken by | Status |
|---|---|---|---|---|---|---|
| S-57 | CLF:332–381 | "## 5. PRD eligibility"; "may go on to author its own `prd.md`"; "must refuse to author a PRD here" | I (widen or cite) | §5.4 bullet 2 → R7, R14, R3 (M: §5.4 bullet 2) | Task 1, Step 3; Task 4, Step 5 | open |
| S-58 | CLF:552–611 | "### 5.2 Offering `/create-prd` — three refusals, not one"; the empty-set vs missing-ledger wording | I | §5.4 bullet 2 → R6 (M: §5.4 bullet 2) | Task 1, Step 4 | open |
| S-59 | CLF:508–524 | §5.1's consumer list | T (container test) | — | — | left as it stands — §5.1's list is the container test's consumers, a different test; Task 1 checks the new consumer sentence is not written into it |

### `workflows-core`

| Row | Site | As measured (M §10; pages, M §9) | V | Owner | Taken by | Status |
|---|---|---|---|---|---|---|
| S-60 | PH:321, :322 | `/create-ard` and `/specify` rows: "on a BRD-route slice, the pre-existing behaviour, kept … since a slice holding no `prd.md` is the route's ordinary state" | R | §11.1 (no row) (M: §11.1 (no row)) | Task 4, Step 3 (re-read) | open |
| S-61 | PH:358 | "a slice holding no `prd.md` still falls back for both"; "a slice holding none still goes on" | I | §11.1 (M: found now) | Task 4, Step 3 | open |
| S-62 | PH:617 | `prd.md` rung on a slice, "do not yet apply" | F | §5.4 bullet 6; §5.5 Batch 4 bullet 9 (F-12); L12 → R2, P4 (M: §5.5 F-12, L12) | Task 4, Steps 1 and 2 | open |
| S-63 | PH:615 | row F's two forms | T (cited) | §4 → P1 (M: §4) | Task 7, Step 2 | open |
| S-64 | NPO:219–227 | interview advance offers | F | §5.5 Batch 4 bullet 2 (L-B4-8) (M: §5.5 L-B4-8) | Task 6, Step 4 | open |
| S-65 | NPO:256–269 | "the other two carry none of their own…"; "the level test and `/create-prd`'s eligibility test are each enforced by the offered command's own Phase 0" | F | §5.5 Batch 4 bullet 2 (L-B4-8) (M: §5.5 L-B4-8) | Task 6, Step 4 | open |
| S-66 | NPO:244–249 | "The BRD route on `/create-prd`, `/create-ard` and `/specify` all ship" | T | — | — | left as it stands — true: the route ships on all three commands; Task 6 re-reads it beside the part it rewrites |
| S-67 | NPO:326–335 | PE: `/epics <PRD>` → `/specify <EPIC>`, `/create-ard <EPIC>` | R/decide | L8 → R1, P2 (M: found now) | Task 6, Step 5 | open |
| S-68 | NPO:283–286 | proposals: "`/product-workflows:create-ard <KEY>` at tier 2, `/product-workflows:specify <KEY>` at tier 3" | R/decide | L8 → R1, P2 (M: found now) | Task 6, Step 5 | open |
| S-69 | NPO:354–367 | `/epics` precondition: "which the BRD route reaches legitimately since `/create-prd` is not a prerequisite for `/create-ard` there"; ledger resolution "applied by each offering command" | I | §5.4 bullet 6 → R2 (M: §5.4 bullet 6 (mechanism)) | Task 4, Step 4 | open |
| S-70 | NPO:387 | the `/implement` precondition | R (by §4.4) | §5.4 bullet 6 → R2 (M: —) | Task 4, Step 4 (re-read) | open |
| S-71 | NPO:400 | "save `/product-workflows:create-ard` on a BRD-route slice holding no `prd.md`, which it takes as it stands" | F | L8 → R1 (a) (M: found now) | Task 4, Step 4 | open |
| S-72 | NPO:401 | threats → PA `/product-workflows:create-ard <KEY>` | R | L8 → R2 (M: found now) | Task 4, Step 4 (re-read) | open |
| S-73 | `components.md:120` | "`ard_contract` → `/product-workflows:create-ard <PRD>`, `prd_spec` → `/product-workflows:specify <PRD>`" | R | L8 → R2 (M: found now) | Task 4, Step 4 (re-read) | open |
| S-74 | `workflows-core/docs/family-map.md:98–99`, `:101–102` | handover edge labels | I | §5.5 Batch 4 bullet 3 → R13 (M: found now) | Task 9, Step 2 | open |

### `dev-workflows`, `docs-workflows`, `security-workflows`

| Row | Site | As measured (M §10; pages, M §9) | V | Owner | Taken by | Status |
|---|---|---|---|---|---|---|
| S-75 | IMPL:198–200 | `IMPLEMENT_BRD_NOT_SLICED` remedy | I | §5.5 Batch 4 bullet 8 (b2 P-140) → P5 (M: §5.5 b2 P-140) | Task 5, Step 4 | open |
| S-76 | IMPL:229 | "or, on a BRD-route slice, whatever its ledger tests resolve…" | R | §5.4 bullet 6 → R2 (M: §5.4 bullet 6 (mechanism)) | Task 5, Step 3 | open |
| S-77 | IMPL:424 | "**No gap** — … or nowhere on a BRD-route slice" | F | §5.4 bullet 6; §5.5 Batch 4 bullet 9 (F-12) (M: §5.4 bullet 6, §5.5 F-12) | Task 5, Step 2 | open |
| S-78 | DES:67–68 | `DESIGN_BRD_NOT_SLICED` "Design within a slice instead" | R/decide | L8 → P5 (M: found now (same shape as P-140)) | Task 5, Step 4 | open |
| S-79 | DES:115 | "no gap — … or nowhere on a BRD-route slice" | F | §5.5 Batch 4 bullet 9 (F-12) (M: §5.5 F-12) | Task 5, Step 2 | open |
| S-80 | DES:128 | the same "whatever its ledger tests resolve" | R | §5.4 bullet 6 → R2 (M: found now) | Task 5, Step 3 | open |
| S-81 | DES:282–283 | "Add the component first — /product-workflows:create-ard <PRD>" | R | §5.5 Batch 4 bullet 9 → R2 (M: found now) | Task 5, Step 7 (re-read) | open |
| S-82 | DES:259, :265, :540, :572, :713, :826 | threat lines naming `/create-ard <KEY>` for the architect | R | §5.5 Batch 4 bullet 9 → R2 (M: found now) | Task 5, Step 7 (re-read) | open |
| S-83 | CONF:74, :141 | by §4.4 | R | §5.5 Batch 4 bullet 9 → R2 (M: §5.5 F-12) | Task 5, Step 7 (re-read) | open |
| S-84 | CONF:702 | "save `/product-workflows:create-ard` on a BRD-route slice holding no `prd.md`, which it takes as it stands" | F | L8 → R1 (a) (M: found now) | Task 5, Step 5 | open |
| S-85 | CONF:707 | `### Threats` PA → `/create-ard <KEY>` | R | §5.5 Batch 4 bullet 9 → R2 (M: found now) | Task 5, Step 7 (re-read) | open |
| S-86 | RDY:701 | by §4.4 | R | §5.5 Batch 4 bullet 9 → R2 (M: §5.5 F-12) | Task 5, Step 7 (re-read) | open |
| S-87 | `dev-workflows/docs/commands/implement.md:132`, `ready.md:66`, `design.md:54` | "(a BRD-route slice needs none)" | F | §5.5 Batch 4 bullet 9 (F-12) (M: §5.5 F-12) | Task 5, Step 2 | open |
| S-88 | DOC:270–276 | step 3a *Stop* line | R | §5.5 Batch 4 bullet 11 (M: §5.5 b3 bullet) | Task 5, Step 7 (re-read) | open |
| S-89 | RN:815, :830–833 | *The two offers wait for a landed PRD* | I | §5.5 Batch 4 bullet 10 → R1 (b) (M: §5.5 b3 bullet) | Task 5, Step 6 | open |
| S-90 | SCAN:448, :554 | `pa_next_step` → `/product-workflows:create-ard`; PRD test | R | §5.5 Batch 4 bullet 9 → R2 (M: found now) | Task 5, Step 7 (re-read) | open |
| S-91 | `security-workflows/docs/commands/scan.md:168` | "(a BRD-route slice needs none)" | F | §5.5 Batch 4 bullet 9 (F-12) (M: §5.5 F-12) | Task 5, Step 2 | open |

### `product-workflows` pages

| Row | Site | As measured (M §10; pages, M §9) | V | Owner | Taken by | Status |
|---|---|---|---|---|---|---|
| S-92 | `brd-workflow.md:296–301` | "while `/create-ard` on the BRD route and `/specify` on the BRD route carry none of their own, since neither reads the ledger as an authoring input"; "the level test and `/create-prd`'s eligibility test are each refused by the offered command's own Phase 0" | F | §5.5 Batch 4 bullet 3 (L-B4-10) (M: §5.5 (L-B4-10)) | Task 9, Step 1 | open |
| S-93 | `brd-workflow.md:305–308` | "neither of the other two waits on an unauthored PRD, so an ARD or a specification can be authored from a BRD whose ledger will never qualify for a PRD of its own" | F | §5.5 Batch 4 bullet 3 (L-B4-10) (M: found now) | Task 9, Step 1 | open |
| S-94 | `brd-workflow.md:327–328` (cell at 199/200) | "Refuses a `BRD-` container; offered on any advancing slice run. … Never authors from the ledger. …" (199 of 200 characters); "Otherwise offered on the same terms as `/create-ard`." | F | §5.5 Batch 4 bullet 3 (L-B4-10) (M: §5.5 (L-B4-10)) | Task 9, Step 1 | open |
| S-95 | `brd-workflow.md:92–95` | "On a slice with no `prd.md`, `/create-ard` and `/specify` offer `/create-prd` where the slice can take a PRD, and otherwise hand back into the route through `/brd-split`…" | F | §5.5 Batch 4 bullet 3 → R13 (M: found now) | Task 9, Step 2 | open |
| S-96 | `brd-workflow.md:72–75` (edges), `:55–59` (handover labels) | the edges labelled "BRD slice, no prd.md — a row still unallocated" (to `splitslice`) and "an empty slice — keep or remove it" (to `splitroot`); the handover labels, which state no ledger condition for `/create-ard` and `/specify` | U / I | §5.5 Batch 4 bullet 3 → R13 (M: found now) | Task 9, Step 2 | open |
| S-97 | `workflow.md:143`, `:145` | "`/create-ard <SLICE-KEY>` and `/specify <SLICE-KEY>` add none of their own, since neither reads the ledger as an authoring input…"; "`/create-ard` and `/specify` on the slice level alone, `/create-prd` only where the slice is PRD-eligible" | F | §5.5 Batch 4 bullet 3 (L-B4-11) (M: §5.5 (L-B4-11)) | Task 9, Step 1 | open |
| S-98 | `workflow.md:202–203` | "On a slice, with no further condition — gates and reads `prd.md`, going on where the slice holds none and stopping on one never handed off; never authors from the ledger" (169 characters); "On a slice, on exactly the same terms as `/create-ard`" | F | §5.5 Batch 4 bullet 5 (E17) (M: §5.5 (E17)) | Task 9, Step 1 | open |
| S-99 | `workflow.md:48`, `:151` | the edge labelled "an earlier phase still pending, prd.md on the default branch — hand to PA" (`rnpm` to `createard`); "which hands on to `/create-ard` or `/epics` where an earlier phase is still pending, once the PRD's `prd.md` is on the specs repo's default branch" | I | §5.5 Batch 4 bullet 10 (M: §5.5 b3 bullet) | Task 5, Step 6 | open |
| S-100 | `workflow.md:141`, `:149` | "On a BRD-route slice holding no `prd.md`, `/create-ard` and `/specify` offer `/create-prd` in place of `/epics` where the slice can take a PRD, and `/brd-split` on the slice or on its parent where it cannot yet"; "the edges from `/create-ard` and `/specify` back into the route" | F/I | §5.5 Batch 4 bullet 3 → R13 (M: found now) | Task 9, Step 2 | open |
| S-101 | `workflow.md:106–109` (edges), `:120–124` (labels) | the same two edges as S-96; the handover edge labels | U / I | §5.5 Batch 4 bullet 3 → R13 (M: found now) | Task 9, Step 2 | open |
| S-102 | `roles-and-phases.md:24` | "…and `/create-ard` and `/specify` on the level test alone, since neither reads the ledger as an authoring input…" | F | §5.5 Batch 4 bullet 3 (L-B4-15) (M: §5.5 (L-B4-15)) | Task 9, Step 1 | open |
| S-103 | `getting-started.md:150` | "`/brd-reconcile` offers [`/specify`] `ACME-80-01` and [`/create-ard`] `ACME-80-01`, and `/create-prd ACME-80-01` where the slice is PRD-eligible" | I | §5.5 Batch 4 bullet 3 (M: found now) | Task 9, Step 1 | open |
| S-104 | `commands/brd-reconcile.md:712`, `:727`, `:728` | "→ [`/create-ard <SLICE-KEY>`] and [`/specify <SLICE-KEY>`], and [`/create-prd <SLICE-KEY>`] where no claimed ledger row is still `unallocated` and at least one is `covered-here`"; "**On a slice**, with no further condition" twice, the first cell adding "it reads neither `claims:` nor the ledger as an authoring input" (189 characters) | F | §5.5 Batch 4 bullet 3 (L-B4-16, L-B4-13) (M: §5.5 (L-B4-16, L-B4-13)) | Task 6, Step 6 | open |
| S-105 | `commands/brd-reconcile.md:700–701` | "the other two would still be offered" | F | §5.5 Batch 4 bullet 3 (M: found now) | Task 6, Step 6 | open |
| S-106 | `commands/brd-interview.md:613`, `:627` | "[`/create-ard`] and [`/specify`] always" | F | §5.5 Batch 4 bullet 3 (M: found now) | Task 6, Step 6 | open |
| S-107 | `commands/create-ard.md:88`, `specify.md:89` | "**No coverage-ledger check.** … That is a decision, not an omission — [`/create-prd`] is where the gate lives. The run does open the ledger in two places [three, on the specify page]…" | F | §5.5 Batch 4 bullet 6 (L-B4-12) (M: §5.5 (L-B4-12)) | Task 2, Step 6 (page `create-ard`); Task 3, Step 6 (page `specify`) | open |
| S-108 | `commands/create-ard.md:17`, `:54–59`, `:78`; `specify.md:70`, `:86` | where each page lists the command's stop ids; "**The PRD gate runs here too … — but a slice needs no PRD.** … A slice with no `prd.md` is reported and the run architects [specifies] from the resolved folder" | I | §5.4, its table; bullet 8 (M: found now (ids; "a slice needs no PRD")) | Task 2, Step 6 (page `create-ard`); Task 3, Step 6 (page `specify`) | open |
| S-109 | `commands/create-ard.md:233–238`, `:249–254` | the slice replacement list (the `/brd-split` forms, "no second option") | U | §5.4 bullet 4 (M: found now) | Task 2, Step 6 | open |
| S-110 | `commands/specify.md:23`, `:100`, `:141–145` | "On a BRD slice with no `prd.md` … the first option instead names the applicable PRD-authoring or BRD-allocation prerequisite, or is absent when none can be offered"; "this run has cleared only the container one" | U | §5.4 bullet 4 (M: found now) | Task 3, Step 6 | open |
| S-111 | not-handed-off stop pages: `create-prd.md:89`, `create-ard.md:79`, `specify.md:86`, `prd-ground.md:259`, `:292`, `brd-package.md:135`, `:145`, `:152`, `:172`, `brd-reconcile.md:200`, `brd-proposal.md:56` | each stop's page entry, which states the uncommitted form alone | I | §7; §5.4 bullet 7 (M: §7) | Task 7, Step 5 | open |

### Instruction tiers

| Row | Site | As measured (M §10; pages, M §9) | V | Owner | Taken by | Status |
|---|---|---|---|---|---|---|
| S-112 | `.claude/rules/brd-route.md:32` | map line "/create-ard <SLICE-KEY> [ard-seed.md; the PRD gate runs, and its absent branch architects from the slice folder where the slice holds no prd.md…] → /specify <SLICE-KEY> […the same absent branch…]" | I | §7 (the rules files) (M: found now) | Task 9, Step 3 | open |
| S-113 | `.claude/rules/brd-route.md:44` | "`product-workflows:coverage-ledger-format` §5 is the authority all three refusals cite; do not re-express D5 … as a new ledger rule" | I ("all three") | §5.4 bullet 2; `.claude/rules/brd-route.md` binds (M: binds) | Task 9, Step 3 | open |
| S-114 | `.claude/rules/product-workflows.md:42`, `:45` | map lines "a slice holding none goes on, reported where absent" | I | §7 (the rules files) (M: found now) | Task 9, Step 3 | open |
| S-115 | `.claude/rules/workflows-core-handoff.md:24` | "while a BRD slice holding none still falls back" | R | §11.1 (M: §11.1) | Task 9, Step 3 (re-read; Tasks 4 and 8 run its recipe) | open |
| S-116 | `CLAUDE.md` § Hard constraints, last bullet; the kind-gate bullet | — | T | — | — | left as it stands — both bullets stay true: the ledger stops are a recorded decision (M4), and the kind-gate bullet is what Tasks 2 and 3 obey; Task 10 changes one table row of `CLAUDE.md`, on another subject |
| S-117 | `docs/maintainers/rationale.md:668`, `:674` ("which batch 4 gives `/create-ard` and `/specify` (M4)"), `:680` ("wait for batch 4") | — | I (+ batch 4 paragraph) | §7 (M: §7) | Task 9, Step 4 | open |

### Rows added at planning

Sites the measurements name outside §10's tables (the section is given), or that the plan's own calls reach.

| Row | Site | Subject | V | Owner | Taken by | Status |
|---|---|---|---|---|---|---|
| N-1 | CONF:60 | `CONFORMANCE_BRD_NOT_SLICED`: "run '/dev-workflows:conformance <SLICE-KEY>' for each slice: <slice keys>" — the shape of S-75 and S-78 (M §7) | I | L8 → P5 | Task 5, Step 4 | open |
| N-2 | `brd-package.md:302`, `:318`, `:367`, `:466`; REC:377; `prd-ground.md:430`; `brd-proposal.md:444` | the stops that land several files, which "can have files split across states — some committed, some untracked — which the one-HEAD-test form does not decide" (M §6) | I | §4 → P1 | Task 7, Steps 2 and 4 | open |
| N-3 | `brd-split.md:185`; INT:244 | `BRD_SPLIT_NEEDS_GROUNDING` and `BRD_INTERVIEW_NEEDS_GROUNDING`: "no grounding findings on file … run /product-workflows:prd-ground <BRD-KEY> first" on row F, with no test of whether `grounding/code-grounding.md` is in the folder (M §6, last paragraph); and their two PH §3.4 rows | I | §4 (L1's class) → R11, P7 | Task 8 | open |
| N-4 | page `create-ard`, `:144` | the page's copy of Phase 4.3 step 8's requirement-gap line: "through [`/create-prd`] where the PRD folder holds no `prd.md` when the line is written — a BRD slice'…" (M §13) | R | §5.5 Batch 4 bullet 12 | Task 2, Step 6 | open |
| N-5 | page `create-prd`, `:94–95` | the page's copy of step 7's refusals (M §1) | I | §5.4 bullet 2 → R6 | Task 1, Step 5 | open |
| N-6 | CPRD:333–334 | the missing-ledger row's condition "while `brd-link.md` claims rows", and the empty-gate-set row, which a `claims:`-empty slice with no ledger reaches today (M §2 (c), M §14.6) | F | §5.4 bullet 2 → R6 | Task 1, Step 5 | open |
| N-7 | `.claude/rules/plugin-updates-coupling.md:10`, `:16–18`; `.claude/rules/plugin-updates.md:24`; `CLAUDE.md:116` | the coupling file's three oldest bullets and every sentence that names where the history files divide: "The bullets up to `workflows-core` 1.91.1 continue in …", "read all five" (M §12) | I | §10 → R12, P3 | Task 10 | open |
| N-8 | page `update-spec` | where the page describes step 6's gates and the stops `/update-spec` does not take | I | §5.1 (the carve-out), L5 → R3 | Task 3, Step 6 | open |

### Outside the sweep's scope, taken by Task 11

`docs/superpowers/to-fix.md:135`, the LADDER-ORDER entry (*"**Open:** batch 4 (the BRD route)"*), which leaves with this batch (design §11.5); `docs/superpowers/to-test-on-real-project.md`, which gains one live check per new stop (design §11.4); and the design's own §5.4 and §5.5, which take a dated *Settled while building* note. ATPATH-OUTSIDE-TREE (`to-fix.md:227`) owns the same *Gate the PRD* sections Tasks 2 and 3 edit beside: it is not this batch's, and no task changes what it describes.

## The counts before any edit

M §10's, re-run when this file was written, wrap-insensitively over the sweep's scope (`plugins/` without changelogs and `reference-parts/`, `README.md`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/`); each matched. Task 9's Step 5 states what each must be afterwards.

| String | Count | Where |
|---|---|---|
| `level test alone` | 2 | INT; `pw/docs/roles-and-phases.md` |
| `slice level alone` | 1 | `pw/docs/workflow.md` |
| `with no further condition` | 3 | page `brd-reconcile` ×2; `pw/docs/workflow.md` |
| `No coverage-ledger check` | 2 | pages `create-ard`, `specify` |
| ``reads no `claims:` list and no coverage ledger`` | 2 | ARD; SPEC |
| `none of their own` | 3 | `pw/docs/brd-workflow.md`; `pw/docs/workflow.md`; NPO |
| `are always offered` | 1 | REC |
| `always reachable from this state` | 1 | ARD |
| `a BRD-route slice needs none` | 4 | pages `design`, `implement`, `ready` (`dev-workflows`), `scan` (`security-workflows`) |
| `nowhere on a BRD-route slice` | 2 | DES; IMPL |
| `do not yet apply` | 1 | PH |
| `as an authoring input` | 8 | REC; ARD; SPEC; `pw/docs/brd-workflow.md`; page `brd-reconcile`; `pw/docs/roles-and-phases.md`; `pw/docs/workflow.md`; NPO |
| `holding none goes on` | 3 | `.claude/rules/product-workflows.md` ×2; `plugins/docs-workflows/docs/reference/environment.md` |
| `still goes on` | 4 | REC; ARD; SPEC; PH |
| `six literal arrays` | 2 | ARD ×2 |
| `of the six arrays` | 2 | ARD; `prd-ground.md` (another subject) |
| `whose ledger will never qualify` | 1 | `pw/docs/brd-workflow.md` |
| `ledger tests resolve` | 2 | DES; IMPL |
| `which it takes as it stands` | 2 | CONF; NPO |
| ``reads neither `claims:` nor the ledger`` | 1 | page `brd-reconcile` |
| `the slice's ledger tests` | 0 | — (the noun this batch introduces, R14) |

## The walks

Each command task writes its table here before it edits — `## Task <n> walks`, columns `State | Expected, from the design and the rulings | What the text does (file:line) | Match` — with the states the plan's *The walk states* lists, and fills the last two columns from the text as written. Task 2 and Task 3 also record here, before removing anything, the confirmation that each branch they remove is unreachable (design §5.4 bullet 4); Task 1 its line-by-line itemisation of `/create-prd`'s step 7 against CLF §5 and §5.2.

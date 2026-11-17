# LADDER-ORDER batch 4 — measurements

Tree: `/workspace/.worktrees/ladder-order-b4`, branch `feat/ladder-order-b4`, at `main`'s tip `67b4c740` (PR #208 merged; PR #207 before it). Every `file:line` below is a line of that tree unless marked *design* (the design's own number, at `34f4068f`). Abbreviations: CPRD = `plugins/product-workflows/commands/create-prd.md` (1004 lines), ARD = `…/commands/create-ard.md` (1277), SPEC = `…/commands/specify.md` (1503), INT = `…/commands/brd-interview.md` (2768), REC = `…/commands/brd-reconcile.md` (3383), CLF = `plugins/product-workflows/references/coverage-ledger-format.md` (902), PH = `plugins/workflows-core/references/phase-handoff.md` (690), NPO = `plugins/workflows-core/references/next-phase-offer.md` (428), IMPL = `plugins/dev-workflows/commands/implement.md` (1930), DES = `…/dev-workflows/commands/design.md`, CONF = `…/dev-workflows/commands/conformance.md`, RDY = `…/dev-workflows/commands/ready.md`, DOC = `plugins/docs-workflows/commands/document.md`, RN = `…/docs-workflows/commands/release-notes.md`, SCAN = `plugins/security-workflows/commands/scan.md`; `pw/docs/` = `plugins/product-workflows/docs/`. Line counts by `wc -l`.

**The design's line numbers have moved**, by four batches and PRs #205–#208. Each site found by its text (`git show 34f4068f:<file> | sed -n` for the design's text, then grep on today's tree):

| Design cites | Text there at `34f4068f` | Today | Changed by |
|---|---|---|---|
| CPRD:268–336 | step 7, "`PRD-` folder whose `brd-link.md` carries a `parent:` — step 5a guarantees it. Read that file…" to the `CREATE_PRD_BRD_NOT_ELIGIBLE` message | CPRD:276–344 (step 7 whole: 270–375) | text unchanged, shifted |
| ARD:466–480 | "`brd-link.md` — for `parent:` and `depends-on:` only. This run reads no `claims:` list…" | ARD:536–550 | unchanged, shifted |
| ARD:834–837 | precondition table rows 2–5 | ARD:1085–1088 (row 1 at :1084) | unchanged text, shifted |
| ARD:860–863 | the four failing-ledger arrays | ARD:1111–1114 | :1114 gained the `kind: prd` case (b3 ruling (19)) |
| ARD:875–880 | "`/epics` refuses one (`EPICS_NO_PRD`). **This route is where the second half of that test matters most** … `CREATE_PRD_BRD_NOT_ELIGIBLE` …" | ARD:1126–1131 (inside the `/epics` bullet :1120–1135) | shifted |
| SPEC:616–627 | "**Passing that command's container refusal is not enough to name it**…" | SPEC:687–697 | batch 1 removed "A folder carrying no `brd-link.md` has no gate set and takes `/product-workflows:create-prd <PRD>` on the container test alone" (idea-route no-PRD now stops in Phase 0) |
| SPEC:702–717 | "`brd-link.md` — for `parent:` and `depends-on:` only…" | SPEC:773–788 | shifted |
| `specify.md:678` (b1b P-131, "its line at that batch's branch") | "`"Author the PRD first — /product-workflows:create-prd <PRD> (Recommended)"` … which is the run that writes the PRD `/epics` then reads" | SPEC:684–686 | unchanged |
| IMPL:219 | the multi-component 0-Epic bullet ("On a multi-component PRD — `multi-component-test`…") | IMPL:229 (0-Epics bullet: :293–317) | batch 2 rewrote both bullets |
| `brd-interview.md:2528`, `:2563` | the *level test alone* sentence; the not-eligible array | INT:2528–2529, INT:2563 | **unmoved** |
| `brd-reconcile.md` Phase 14 ~`:3011–3027` | the *always offered* bullet | REC:3011–3030 (Phase 14 opens :2971) | unmoved |
| `pw/docs/workflow.md:140`, `:142`, `:148`, `:199–200`, `:48` | — | :143, :145, :151, :202–203, :48 | b3 relabelled :48 |
| `pw/docs/brd-workflow.md:298–299`, `:327–328` | — | :296–299, :327–328 | unmoved |
| `pw/docs/roles-and-phases.md:24`; `pw/docs/commands/brd-reconcile.md:712`, `:727`, `:728` | — | same lines | unmoved |
| `pw/docs/commands/create-ard.md`, `specify.md` *No coverage-ledger check.* | — | create-ard page :88; specify page :89 | — |
| PH:617 (§4.4 *The first missing document*) | — | PH:617 (one line) | written by batch 2 |

---

## 1. `/create-prd`'s tests on a slice, exactly

**Where in the run (execution order, not text order).** Step 0 strips flags and holds **Load the question rules** (CPRD:45). Step 1 reads the token (`read-key`); "The address is resolved once, with `resolve-address` (step 5), and that resolution is taken as soon as step 2b has settled `$SPECS_PATH` — ahead of step 2's profile default and step 3's ladder" (CPRD:58–60). Step 2b: `$SPECS_PATH` question if unset (CPRD:98, the run's first possible `choices:`), then **`specs-preflight`** (CPRD:98–100). Step 5 resolves; 5a refuses a `BRD-` container, "before `coverage-ledger.md` is opened at all" (CPRD:156–159); 5b refuses an `EPIC-` folder (CPRD:219–236); 2a's `--from-prd` refusal on the BRD route (CPRD:71–79); **branch-check** with `prefix: prd` (CPRD:113); step 3 (idea ladder, "Skipped entirely on the BRD route", CPRD:115); step 6 prior-PRD presence test (CPRD:269); **step 7, the BRD gate (CPRD:270–375)**; step 7a, the only `require-on-main` on the BRD route, on `decisions.md`, "Taken after step 7's refusals, so a slice that holds no PRD of its own is told that first, and before Phase 1 resolves documentation grounding" (CPRD:377–381); then Phase 1 (first ordinary question). So on a slice the ledger test runs after the preflight and branch-check, before the run's only gate, before every grill question and dispatch. A slice that already holds a `prd.md` still meets step 7 before Phase 1's existing-PRD question (step 6 only tests presence).

**An Epic-level run.** `/create-prd` has none: step 5b refuses every `EPIC-` folder (`CREATE_PRD_EPIC_FOLDER`). Its remedy names `/product-workflows:create-prd <PARENT-KEY>` on the folder above, "subject to step 7's data refusals applied to *that* folder where it carries a `brd-link.md`" (CPRD:261–264). "The slice above" is `/create-ard`'s and `/specify`'s `prd_dir` (§3, §4 below).

**The reads, in order** (CPRD:273–309):
1. "Read that file [`brd-link.md`] for its `parent:` and any `depends-on:`; then read `<slice-dir>/coverage-ledger.md` and take the **`disposition` written on each row of the gate set**" (CPRD:276–278).
2. The gate set: "this slice's own ledger rows, narrowed by its `brd-link.md` `claims:`" (CPRD:280); orphan rows are outside it and "must not be read anyway" (CPRD:286–289); "A slice claiming nothing has an empty gate set … and reaches refusal 2 by the empty-set row of the table below, never refusal 1" (CPRD:289–291).
3. "**Read every disposition from the ledger file, never from any `ledger:` line.**" (CPRD:304).
4. "All three refusals are read **as this run finds the tree**" (CPRD:372) — working tree, no gate on the ledger.

**Refusal 1** (CPRD:311–321) — a gate-set row still `unallocated`:
```
CREATE_PRD_BRD_UNALLOCATED: <SLICE-KEY>'s coverage-ledger.md still writes `unallocated` on <n> of the <total> requirement rows this slice claims — <[BR#n] list>. coverage-ledger-format.md §5 makes that a hard refusal: the allocation gate was never satisfied, and an unallocated row is neither an implicit `covered-here` nor an implicit `deferred-to` in either direction. Run '/product-workflows:brd-split <SLICE-KEY>' to walk each one to a terminal disposition, then re-run '/product-workflows:create-prd <SLICE-KEY>'.
```
Plus, beside it: "its own Phase 0 gates on this slice's grounding findings each carrying a verifier verdict, and stops naming `/product-workflows:prd-ground <SLICE-KEY>` when they do not. Say so beside the offer" (CPRD:318–321).

**Refusal 2** (CPRD:323–359) — no gate-set row `covered-here`. Table (CPRD:330–334), three rows:
- non-empty gate set, none `covered-here` → "Name **no** sibling slice … say what the gate-set rows *did* resolve to … Then say a PRD needs one row resolved `covered-here` first";
- "`coverage-ledger.md` is **absent**, or present and cannot be read, while `brd-link.md` claims rows" → "**Name no option at all** — report the file by path, as missing or as unreadable with the read error, and stop" (cites CLF §5.2);
- empty gate set → `/product-workflows:brd-split <PARENT-KEY>`: `"<how to cut it>"` where the parent's ledger still holds an `unallocated` row, bare where none, plus "an instruction on that same run — `/product-workflows:brd-split <PARENT-KEY> "<what to peel off>"` — can additionally re-cut that row onto this slice", and "Where the parent's ledger cannot be read, report it by path and name neither form".
```
CREATE_PRD_BRD_NOT_ELIGIBLE: no row of <SLICE-KEY>'s coverage-ledger.md that its brd-link.md claims is `covered-here`, so this slice holds no PRD of its own (coverage-ledger-format.md §5). <where the requirements went, per the row above that matches>
```
"In the **first** case **no command is offered at all, and the stop says why**" (CPRD:351); nothing marked `(Recommended)` (CPRD:357–359).

**Shared text.** "**None of the three refusals carries a merge clause**" (CPRD:361–370). Phase 7: "`CREATE_PRD_BRD_UNALLOCATED` and `CREATE_PRD_BRD_NOT_ELIGIBLE` (slice-only, step 7) each report the state of the operator's own BRD tree … so none of them `emit-block`s" (CPRD:959). Page copy: `pw/docs/commands/create-prd.md:94–95`.

**Which is tested first where the ledger is missing.** With no readable ledger no row reads `unallocated`, so refusal 1 does not fire and refusal 2's missing-ledger row takes it — the id is `CREATE_PRD_BRD_NOT_ELIGIBLE`.

## 2. `coverage-ledger-format` §5 and §5.2

**§5 (CLF:332–462), heading `## 5. PRD eligibility`.** Opening rule (CLF:334–337): "**A folder is PRD-eligible if and only if it is a `PRD-` slice folder *and* at least one of its ledger rows for a `[BR#n]` its `brd-link.md` claims is `covered-here`** — §5.2's gate set". Level test first, "before opening `coverage-ledger.md` at all" (CLF:339–345). "- **Eligible.** … The folder may go on to author its own `prd.md`, which is what `/create-prd` on the BRD route runs against it to write." (CLF:368–369). "- **Not eligible.** … A consumer that reaches this state must refuse to author a PRD here and say **where the requirements went**" (CLF:370–381). Table (CLF:386–390) — its third row is the slice's: "On a slice, add that a PRD needs one row resolved `covered-here` first". The unallocated rule: "A row still `unallocated` **as written on this BRD's own ledger** when eligibility is checked means the gate in §4 was never satisfied — a consumer must treat that as a hard refusal" (CLF:453–456); "**Read that from the ledger file, never from the §6 line.**" (CLF:458).

**§5.2 (CLF:552–611), heading `### 5.2 Offering \`/create-prd\` — three refusals, not one`.** "`/create-prd` refuses **three** shapes on the BRD route, and an offer that names it is safe only once it has tested all three" (CLF:554–555). Table (CLF:559–563): container → `CREATE_PRD_BRD_NOT_SLICED`; "the gate set | a row is still `unallocated` | `CREATE_PRD_BRD_UNALLOCATED` — `/brd-split <SLICE-KEY>`"; "the gate set | no row is `covered-here`, and none `unallocated` (the row above is tested first) | `CREATE_PRD_BRD_NOT_ELIGIBLE` — where the gate set is **empty** (a standing empty child), `/brd-split <PARENT-KEY>`, in the form the parent's own ledger decides … **no command at all** where the gate set is non-empty". Gate set (CLF:565–572), "the same set Phase 0 step 7 defines, read the same way"; `<PARENT-KEY>` "is read, never derived" from `parent:` (CLF:574–577); a folder with no `brd-link.md` has no gate set (CLF:579–581); a missing or unreadable ledger "is not an empty gate set … **Name no option at all.**" (CLF:583–597); "**Where a data refusal would fire, drop the `/create-prd` option and say which test failed.**" (CLF:599–611).

**Is `/create-prd`'s test stated whole there?** Almost; the command adds five things §5/§5.2 do not hold:
- (a) the `/prd-ground` note beside the `/brd-split <SLICE-KEY>` remedy (CPRD:318–321);
- (b) the re-cut form `/brd-split <PARENT-KEY> "<what to peel off>"` in the empty-gate-set row (CPRD:334);
- (c) the missing-ledger row's condition "while `brd-link.md` claims rows" (CPRD:333). **§5.2 disagrees on one state**: it says a ledger-less slice "is not an empty gate set" and defines the standing empty child as "a slice whose ledger exists and whose `claims:` list is empty" (CLF:587–588), so `claims:` empty + ledger absent → no option (§5.2) vs the empty-set row naming `/brd-split <PARENT-KEY>` (CPRD:334). ARD:1086/1088 and SPEC:1454/1456 copy CPRD's conditions. Hand-damage state only (CLF:583–585).
- (d) the two ids and their message texts;
- (e) "read as this run finds the tree", no merge clause, no `emit-block`.

**Its name and wording speak only of a PRD**: "PRD eligibility", "PRD-eligible", "may go on to author its own `prd.md`", "must refuse to author a PRD here", "Offering `/create-prd`". ARD:538–539 and SPEC:775–776 lean on exactly that wording ("§5's rule about authoring a **PRD**, applied 'when eligibility is checked', and an ARD is not that artifact").

**Rule binding the plan** (`.claude/rules/brd-route.md:44`): "`product-workflows:coverage-ledger-format` §5 is the authority all three refusals cite; do not re-express D5 as a sixth disposition or as a new ledger rule."

**Who cites §5 / §5.2 today.** Recipe: `python3 -I scripts/wgrep.py 'coverage-ledger-format(\.md)?`?\)?,? ?§ ?5(\.2)?(?![.0-9])'` (wrap-insensitive; collapses whitespace) over `git ls-files 'plugins/*.md'` minus `CHANGELOG.md` and `reference-parts/` — **50 citation sites**; the reference's own recipe (`grep -rn 'coverage-ledger-format.*§5' plugins/*/commands/*.md plugins/*/agents/*.md`, CLF:528) misses wrapped ones. By what each cites §5 *for* (each hit opened):
- **Data refusals / eligibility (the test batch 4 copies) — 14:** CPRD:274, :313, :344; ARD:538 ("rule about authoring a **PRD**"); SPEC:775; INT:938 (`BRD_INTERVIEW_ALL_DELEGATED` "holds no PRD of its own"), INT:2534 (the PRD-eligible offer test); REC:2989; `brd-split.md:56`, `:595`, `:1042`, `:1485`; `prd-ground.md:2482`; NPO:258 ("the two refusals its Phase 0 raises").
- **§5.2's offer table (naming `/create-prd`) — 15:** CPRD:333; ARD:546, :1071, :1088; SPEC:692, :784, :1438, :1456; REC:3008; `epics.md:242`; `idea.md:84`; `prd-proposal.md:234`; `update-prd.md:35`, `:59`; NPO:367 ("the authority, applied by each offering command").
- **Container / level test or root-row repair — 20:** CPRD:166, :205, :217; ARD:154, :188; SPEC:74, :107; `epics.md:171`; `brd-intake.md:199`, `:229`, `:1531`; REC:2984; DES:69; IMPL:200; RDY:71; DOC:115; RN:114; PH:354; `addressing.md:204`; NPO:248. Plus CLF:237 (self).
- §5.1 citations (container positive test) are a separate population and untouched by a data-test change.
- No `docs/` page cites CLF by section.

## 3. `/create-ard` on a slice today

**Phase 0 order** (ARD:37–428): step 1 strips run flags (:40), **Load the question rules** (:42), strips own flags (:44–52), parses one address, takes step 2's `$SPECS_PATH` check (`choices:` at :211) and resolves (:54–57); on `found` fixes the run key set and runs the **specs-repo preflight** "before step 1 places the folder and before step 1a or any later step reads it" (:65–75, :273); places the folder by prefix (:77–92); carries **`prd_dir`** — "the resolved folder itself on a PRD-level run (the `PRD-` slice on the BRD route), and the folder containing it on an Epic-level one" (:94–104); detects the route: "a `PRD-` folder holding a `brd-link.md` → the BRD route" (:83) — a presence test, nothing read inside it; step 1a container refusal (:112–208); step 3 `CREATE_ARD_NOT_FOUND` on `absent` (:212–229); **branch-check** `prefix: ard` (:231); step 4 prior ARD (:233); step 5's advisory is *written* here but "**taken after *Gate the PRD*, *Gate the decision register* and *Gate the Epic***" (:234–236) and runs at "Now take Phase 0 step 5's optionality advisory." (:428), with `choices: ["Author the ARD anyway", "Stop — no ARD needed"]` (:246); ***Gate the PRD*** (:277–352); ***Gate the decision register*** (:354–388); ***Gate the Epic*** (:414–426). First dispatch: Phase 3 `code-scanner` (:664). So **Phase 0 reads no `claims:` and no ledger today**; Phase 1 only stats `brd-link.md`'s `parent:`/`depends-on:` (:434), Phase 2 reads them (:536).

**The Epic-level route.** Gate the PRD splits on "the route, read off that same folder, which on an Epic-level run is the one above the Epic — a slice where it carries a `brd-link.md`" (:277); Phase 2: "where its containing directory is a `PRD-` slice carrying `brd-link.md`, this is the BRD route with that slice as the BRD folder and this Epic as the focus" (:475–478).

**Gate the PRD on a slice** (:277–283), batch 1's: `absent` + `prd.md` in the folder → `CREATE_ARD_PRD_NOT_HANDED_OFF` "on either route", HEAD test choosing uncommitted (:304–311) or committed (:314–318) form; "`absent`, no `prd.md` in the PRD folder, on a slice → the slice's ordinary state, kept as it was: the existing folder-read fallback applies — but report it: *"No authored PRD on `<default>` for `<PRD>` — architecting from the resolved folder at `<path>`. If a PRD exists on a branch, this run would have stopped; it does not, so none does."*" (:280); `unmanaged` on a slice → "behave exactly as before this feature" (:281, :283). `CREATE_ARD_NEEDS_PRD` is idea-route only (:279, :282). Defence paragraph: "**The BRD route runs this gate too, and a slice holding no `prd.md` still goes on.** … On a slice `/product-workflows:create-prd` is still not a prerequisite for this command." (:330–352).

**The overturned statement** (ARD:536–541, with :543–550):
> - **`brd-link.md`** — for `parent:` and `depends-on:` only. This run reads no `claims:` list and no coverage ledger **as an authoring input**: PRD eligibility and the allocation gate are `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5's rule about authoring a **PRD**, applied "when eligibility is checked", and an ARD is not that artifact. Not checking it here is a decision, not an omission — `/product-workflows:create-prd` on the BRD route is where that gate lives, and this command is reachable without it.
>
>   **Two places do open the ledger, and neither gates anything this run does.** Phase 7's next-step offer opens it and the `claims:` list … The Final report opens the ledger alone …

"Two places" becomes three once Phase 0 opens it (exclusivity probe hit).

**Phase 7** (ARD:1036–1174). The precondition (:1042–1068): "**One precondition governs every `/product-workflows:epics` option below, and only a slice, or a `prd.md` asserting no `kind: prd`, can fail it.**" … "Offering `/epics` on a folder holding no PRD would name a run that stops on arrival, and naming `/create-prd` without the test below does the same thing one command further on." (:1058–1060). Then :1070–1080: "**`/create-prd` refuses three BRD-route shapes, not one** … A PRD-level run has cleared only the container refusal, by resolving a `PRD-` folder itself. … On the BRD route its five rows pick among the last five of the six literal arrays below". The table (:1082–1088):

| Row | Text (abridged) | Reachable after a Phase 0 ledger stop? |
|---|---|---|
| :1084 | "No row `unallocated`, and at least one `covered-here` → `/product-workflows:create-prd <SLICE-KEY>`" | yes — the only row |
| :1085 | "A row still `unallocated` → `/product-workflows:brd-split <SLICE-KEY>` instead…" | no |
| :1086 | "No row `covered-here`, gate set **empty** → `/product-workflows:brd-split <PARENT-KEY>` …" | no |
| :1087 | "No row `covered-here` and none `unallocated`, gate set **non-empty** → **Drop the option and name nothing**" | no |
| :1088 | "No readable `coverage-ledger.md` … while that file claims rows → **Drop the option**" | no |

The arrays (:1100–1114), "**Six literal arrays, one per branch of that test** — the standing-empty-child branch split in two by the parent's ledger, the missing-ledger branch and a `prd.md` asserting no `kind: prd` sharing the last" (:1103–1104):
- :1109 slice holds an authored `prd.md` (`/specify`, `/epics`, `Stop here`) — reachable;
- :1110 no `prd.md`, gate set clears both (`/specify`, `/create-prd`, `Stop here`) — reachable;
- :1111 unallocated (`/brd-split <SLICE-KEY>`), :1112 empty + parent unallocated (`/brd-split <PARENT-KEY> \"<how to cut it>\"`), :1113 empty + parent none (bare) — **unreachable**;
- :1114 `["…/specify <SLICE-KEY> … (Recommended) <merge-clause>", "Stop here"]` for "either no row `covered-here` and none `unallocated` with the gate set non-empty, or no readable `coverage-ledger.md` …, or the gate set empty and the parent's `coverage-ledger.md` unreadable; or a `prd.md` asserting no `kind: prd`" — **stays reachable for the `kind: prd` case only**.

Text on those states:
- :1120–1135, the `/epics` bullet: "a slice that is ground and fully allocated with every claimed row `deferred-to` or `rejected`, and no `prd.md`, is an ordinary state of *this* route, and naming `/product-workflows:create-prd <SLICE-KEY>` there would send the operator into `CREATE_PRD_BRD_NOT_ELIGIBLE`" (:1126–1131, design ARD:875–880) — that state now stops in Phase 0;
- :1136–1148, "The three replacement commands differ over the clause" (both `/brd-split` forms) — unreachable halves;
- :1149, "offered on this route by none of the six arrays" — a count;
- :1159, "`/product-workflows:brd-split` on this slice stops on its own `require-on-main` … **The option carrying none names no gate this run feeds** — `/product-workflows:brd-split <PARENT-KEY>`, in either form";
- :1090–1095, "Dropping rather than annotating … the array still holds `/product-workflows:specify <SLICE-KEY>` and `"Stop here"`";
- :1115–1119, "**`/product-workflows:specify <SLICE-KEY>` is always reachable from this state.**" — its reason names the container refusal and ARD resolution, not the ledger.

**Reachability today** of rows :1085–1088 and arrays :1111–1114: any slice run with no `prd.md` whose ledger fails — ordinary on this route (ARD:1126–1129 says so). **With a Phase 0 ledger stop** they become unreachable within one run: `/create-ard` writes no `coverage-ledger.md` (it stamps `consumed_by` in grounding files and the register only, ARD:1139–1144), so Phase 7 reads the ledger Phase 0 passed. On an Epic-level run Phase 7 names neither `/epics` nor a replacement (:1054–1056), so the table is PRD-level only.

**Phase 4.3 step 8's line** (ARD:921): "`<command>` names the run through which the requirement can enter the PRD, tested when the line is written: `/product-workflows:create-prd` where `prd_dir` — on an Epic-level run the folder above the Epic — holds no `prd.md`, since `/product-workflows:update-prd` stops on such a folder (`UPDATE_PRD_NO_PRD`), and `/product-workflows:update-prd` otherwise. Past *Gate the PRD*, which stops an idea-route run without a `prd.md`, the `/product-workflows:create-prd` ending is a slice's case alone." It disagrees with :1058–1060 ("naming `/create-prd` without the test below does the same thing one command further on") on a slice whose ledger refuses `/create-prd`. That is b1b rulings 15 and 20: "until batch 4 the line names a run whose own stop names `/brd-split`". With the Phase 0 stop no run reaches step 8 on such a slice, so the line becomes true as written; its *reason* sentence names only *Gate the PRD*. A line an earlier run wrote keeps its command (:921, "A line that already stands keeps the command it ends with").

**Other `/create-ard` statements on a slice:** :245 (advisory on "a PRD-level run with no `prd.md` — a slice"); :266–267 ("the ordinary BRD-route state, since on that route `/product-workflows:create-prd` is not a prerequisite"); :496–506 Phase 2 ("A PRD folder holding no `prd.md` reaches this phase only on the BRD route … That is the slice's **ordinary** state"); :1161 commercial step ("on a folder holding none — a slice"). Capture-at-block: "**The ten argument-, tree- and git-shaped stops are of that second class**: `CREATE_ARD_NEEDS_KEY`, … `CREATE_ARD_ARD_NOT_ON_MAIN`" (:1194).

## 4. `/specify` on a slice today

**Phase 0 order.** Step 0's text (route, container refusal, SPEC:36–127) stands first but runs after step 1's resolution and the preflight: step 1 strips run flags (:131), **Load the question rules** (:133), strips own flags, parses one address, takes step 2's `$SPECS_PATH` check (`choices:` :213), resolves (:143–190); "**Then, where the resolution returns `status: found`, settle the specs checkout before step 0's refusal or step 1's placement reads the folder.**" (:198–209); preflight (:309–314); step 0's refusal; placement; `prd_dir` (:151–164); step 3 (:217–298; `SPECIFY_BRD_NOT_FOUND` :292, `SPECIFY_EPIC_NOT_FOUND` :243); **branch-check** `prefix: spec` (`reuse: later` on a PRD address, :300); step 4 prior run (:302); ***Gate the PRD*** (:320–392); ***Gate the decision register*** (:394–428); ***Gate the Epic*** (:456–471; on a PRD address deferred to Step B). Route on an Epic address: "the one above the Epic — a slice where it carries a `brd-link.md`, the idea route where it carries none, as step 0 and step 3's *Look one level up* detect it" (:320, :271–275). Phase 0 reads no `claims:` and no ledger today.

**Gate the PRD on a slice:** :323 "**`absent`, no `prd.md` in the PRD folder, on a slice** → the slice's ordinary state, kept as it was: `/specify`'s existing specs-tree behaviour is unaffected — but report it: *"No authored PRD on `<default>` for `<PRD>` — specifying from the resolved folder at `<path>`. If a PRD exists on a branch, this run would have stopped; it does not, so none does."*"; :326 unmanaged slice; :373–392 "**The BRD route runs this gate too, and a slice holding no `prd.md` still goes on.** … On a slice `/product-workflows:create-prd` is still not a prerequisite for this command."

**`/update-spec` cites these sections** (`update-spec.md:57`): "**Gate the inputs**, as `/specify` gates them — its *Gate the PRD*, *Gate the decision register* (BRD route) and *Gate the Epic* sections, each applied to this folder, with their stops named `UPDATE_SPEC_` in place of `SPECIFY_` — **save the two stops *Gate the PRD* makes where the PRD is on no ref**". A ledger stop written inside any of those three sections reaches `/update-spec` as `UPDATE_SPEC_BRD_*` unless the carve-out names it (L5; design §5.1 "Batch 4 does the same for the ledger tests").

**The overturned statement** (SPEC:773–778, :780–788), the same as ARD's with "**Three places do open the ledger**: Phase 2 Step A's zero-Epics choice and the `### Next step` offer open it and the `claims:` list … The Final report opens the ledger alone".

**The zero-Epics question** (SPEC:667–697). Array :668 `["Split into Epics first with /product-workflows:epics (Recommended)", "Author one broad PRD-level spec now", "Cancel"]`, multi-component swap :669. Slice form (:683–697):
> … A folder holding no `prd.md` is a slice, since Phase 0's *Gate the PRD* stops an idea-route run without one, and on a slice it is the ordinary state. There the `/epics` choice — the first, or the second on the multi-component array, which keeps its own marker on the broad-spec option — becomes `"Author the PRD first — /product-workflows:create-prd <PRD> (Recommended)"` (without `(Recommended)` on the multi-component array), which is the run that writes the PRD `/epics` then reads and takes the single address this run already resolved. **Passing that command's container refusal is not enough to name it**, and it is the only one of its three refusals this run has cleared: … Resolve that choice from the same table the `### Next step` uses (`…coverage-ledger-format.md` §5.2, applied there) — the `/product-workflows:create-prd` option where the gate set clears both data tests, the corresponding `/product-workflows:brd-split` where one fails and a command exists, and **no such choice at all** where none does, leaving the other two.

After a Phase 0 ledger stop only the first branch is reachable. "the only one of its three refusals this run has cleared" (:687–688) becomes false. P-131's sentence (:685–686, "the run that writes the PRD `/epics` then reads") owes the merge of `/create-prd`'s handoff, since `/epics` gates `prd.md` (b1b). The `/brd-split` forms are named in prose only — no literal array for them.

**`### Next step`** (SPEC:1413–1499). Precondition :1417–1435, "**One precondition governs every `/product-workflows:epics` option above, and only a slice, or a `prd.md` asserting no `kind: prd`, can fail it.**" … "on the BRD route this run does **not** require a PRD … naming `/create-prd` without the test below does the same thing one command further on" (:1422–1429). :1437–1440 "Of the three, the tested folder has cleared only the container refusal". Table :1450–1456: row :1452 (clears → `/create-prd <SLICE-KEY> <merge-clause>`) reachable; rows :1453 (unallocated → `/brd-split <SLICE-KEY>`), :1454 (empty → `/brd-split <PARENT-KEY>`), :1455 (non-empty, none covered-here → name neither, `/dev-workflows:design <SPEC-KEY>` still recommended), :1456 (unreadable) unreachable after the stop. :1458–1462 "Dropping rather than annotating" (a prose offer, "dropping an option costs it no arity"). :1474–1479 the `/epics` bullet: "**Its replacement is not**: only a BRD-route slice has a gate set, so the table above is where a slice with no `prd.md` and no `covered-here` row stops the `/create-prd` recommendation from being made at all" — the reachable set shrinks. The table applies "to a PRD-level spec only (`focus_key` null)" (:1425); on a per-Epic spec under a slice the ledger is read nowhere in Phase 2 / Next step. Capture-at-block lists every `SPECIFY_*` stop by name (:1261).

## 5. The offers that would now stop

**(a) `/brd-interview`, Phase 11, `package_offerable: nothing-to-review`** (INT:2504–2564). INT:2524–2535:
> **A slice that needs no customer review goes to the authoring ladder without a reconciliation**: `/product-workflows:create-prd`, `/product-workflows:create-ard` and `/product-workflows:specify` each gate this slice's `decisions.md` on the default branch and read no reconciliation record. They are offered here on the conditions `/product-workflows:brd-reconcile`'s own advancing list applies, and for the same reasons: **`/product-workflows:create-ard <BRD-KEY>` and `/product-workflows:specify <BRD-KEY>` on the level test alone** — this command runs on a slice only (`BRD_INTERVIEW_ROOT_LEVEL`) — and **`/product-workflows:create-prd <BRD-KEY>` only where the slice is PRD-eligible**: no row of the gate set … is still `unallocated`, and at least one of them is `covered-here` (`…coverage-ledger-format.md` §5). This command's own gate has already found no row `unallocated`, so the covered-here test is the one left to read.

Prose list :2545–2552 (PRD, architecture, specification, re-ground, interview another). Arrays:
- :2557, eligible: `["Stop here — every question was settled from the findings and this BRD needs no customer review", "Author this slice's PRD — /product-workflows:create-prd <BRD-KEY> (PM) <merge-clause>", "Author this slice's architecture — /product-workflows:create-ard <BRD-KEY> (PA, optional) <merge-clause>", "Author this slice's specification — /product-workflows:specify <BRD-KEY> (PE) <merge-clause>"]`
- :2563, not eligible: `["Stop here — every question was settled from the findings and this BRD needs no customer review", "Author this slice's architecture — /product-workflows:create-ard <BRD-KEY> (PA, optional) <merge-clause>", "Author this slice's specification — /product-workflows:specify <BRD-KEY> (PE) <merge-clause>", "Re-ground every claim against current commits — /product-workflows:prd-ground <BRD-KEY> --rebaseline (a changed finding is what can make a new round askable)"]`

*Condition today:* the level test (slice-only command). *In hand:* the ledger — Phase 0 step 8 counted `unallocated` "as written on this ledger" over **all** rows (INT:338–340, `BRD_INTERVIEW_UNALLOCATED`); the gate set via `claims:` for the PRD-eligible test; `BRD_INTERVIEW_ALL_DELEGATED` already stopped an all-orphan slice (INT:938). It holds **no read of `prd.md`**, and its loaded `phase-handoff require-on-main` file (Phase 0 gate on `grounding/code-grounding.md`) holds §3.2, §3.5 and §4.4. *What the two conditions need:* the ledger test reduces to "at least one `covered-here`" (unallocated already excluded), so **it equals the PRD-eligible test**: on the not-eligible branch both authoring options go and the :2563 array becomes Stop + re-ground (two options; arity holds). The landed test needs a new read, as RN:830 reads it (below), only "where one is written".

**(b) `/brd-reconcile`, Phase 14** (REC:2971–3086). The *always offered* bullet (REC:3011–3030):
> - **`/product-workflows:create-ard <SLICE-KEY>` and `/product-workflows:specify <SLICE-KEY>` are always offered**, with no condition of their own, and that is read out of their own Phase 0s rather than assumed symmetric with `/create-prd`'s. … both run the PRD gate — on every route, as of increment E — but neither waits on a PRD the slice has not got, because on a slice holding no `prd.md` that gate's `absent` branch proceeds and reports, so `/create-prd` on the BRD route is still not a prerequisite for either (`commands/create-ard.md` and `commands/specify.md`, *The BRD route runs this gate too, and a slice holding no `prd.md` still goes on*); what makes either stop on that gate is a `prd.md` that exists and was never handed off — on an unmerged branch, or in the slice folder and on no ref, where each stops with its `*_PRD_NOT_HANDED_OFF` — a file this run neither writes nor reads, so not a condition it tests for the operator; and neither reads the `claims:` list or the coverage ledger **as an authoring input** — each opens them only to shape its own offers and report — because PRD eligibility is §5's rule about authoring a **PRD** and an ARD is not that artifact and neither is a specification. …

`advance_ready: yes` (REC:3071–3086), prose :3076–3082 and array :3085 `["Stop here — the decisions are frozen and both sweeps are recorded", "Author this slice's PRD — … (PM) <merge-clause>", "Author this slice's architecture — … (PA, optional) <merge-clause>", "Author this slice's specification — … (PE) <merge-clause>"]`; "Where either test fails, **drop the option from the array**" (:3001–3002). *In hand:* `coverage-ledger.md` "as this run left it" (it writes ledger rows in Phase 9, REC:2268ff — `deferred-to`, `rejected`, `superseded-by`, never `covered-here`, never back to `unallocated`), and the gate set via `claims:` (:2991–2995). It does not read the parent's ledger (its unallocated/no-covered-here wording at :3002–3005 names `/brd-split <SLICE-KEY>` and "§5 is where its requirements went", no empty-gate-set form), and **reads no `prd.md`** (:3022–3023 says so). Phase 14 loads `next-phase-offer brd`; the run requested `phase-handoff require-on-main` in Phase 0 and `handoff-to-main` in Phase 13 (:2932). **Arity:** with all three advance options dropped the array is `Stop here` alone — below `AskUserQuestion`'s two; REC states the rule for the other list: "never *Stop here* alone, which no picker may hold (`workflows-core:escalation-rules` §0)" (REC:3149–3150). REC can reach a failing ledger on a slice: its own Phase 9 can move the last `covered-here` row away, and a `--sent` run "gates no ledger" (:3005–3006).

**(c) `next-phase-offer`'s BRD part** (part `brd`, NPO:209–274; generated `reference-parts/next-phase-offer/brd.md`). NPO:219–227 (interview): "→ `/product-workflows:create-ard <BRD-KEY>` (PA, optional) or `/product-workflows:specify <BRD-KEY>` (PE), and `/product-workflows:create-prd <BRD-KEY>` (PM) where the slice is PRD-eligible — the same conditions `/product-workflows:brd-reconcile`'s advancing list applies". NPO:256–266 (reconcile): "On an advancing slice run, `/product-workflows:create-prd <SLICE-KEY>` carries the further condition … the other two carry none of their own: neither reads the ledger as an authoring input, and although both now run the PRD gate on every route, that gate's `absent` branch proceeds on a slice holding no `prd.md` … and the offering run, which reads no `prd.md`, does not test for it. **That difference is where the conditions come from, and it matters:** the level test and `/create-prd`'s eligibility test are each enforced by the offered command's own Phase 0, so offering either wrongly hands over a run that stops". It holds nothing itself; the offering commands hold what (a) and (b) say.

**(d) `/release-notes`' *The two offers wait for a landed PRD*** (RN:830–833; template :815, "each named only where *The two offers wait for a landed PRD*, after this report, says"). *Condition today:* `prd.md` on `<default-ref>` (ref tested first with `rev-parse --verify --quiet`, then `git -C "$SPECS_PATH" show "<default-ref>:./<the PRD folder…>/prd.md"`), unmanaged/unset → the folder's file, outside-tree → §4.4, row G → neither named; `/epics` also on `kind: prd`. *In hand:* the PRD folder's `prd.md` (Phase 0 stopped with `RELEASE_NOTES_NO_PRD` otherwise, RN:131–169, whose slice remedies — RN:152–169 — **already restate the ledger tests** in RN's own text: missing ledger → name nothing; unallocated → `/brd-split <KEY>`; empty → `/brd-split <PARENT-KEY>` forms; non-empty → no command); whether the folder carries `brd-link.md`. It reads no ledger at the Next step: Phase 0 reads it only where no `prd.md` is there. `phase-handoff` loaded whole at :830. *What batch 4 adds:* on a slice, `/create-ard <PRD>` takes the ledger test too. `/epics` takes no ledger test. A slice reaching here holds a `prd.md`, so the failing ledger is the changed-after-`/create-prd` state (§14). Pages following: `pw/docs/workflow.md:48` (`rnpm -.->|"an earlier phase still pending, prd.md on the default branch — hand to PA"| createard`) and :151 ("which hands on to `/create-ard` or `/epics` where an earlier phase is still pending, once the PRD's `prd.md` is on the specs repo's default branch"). b3's walk row (k) says only a slice holding a `prd.md` reaches it.

**The landed-`prd.md` read, by precedent:** RN:830 (above); SCAN:448 (`git show "<specs-default-ref>:./…/prd.md"`, `kind: prd`, unmanaged → the folder's file); SCAN:554's not-landed sentence; NPO:387's `cat-file -e "<default-ref>:./<path>"`. "Where one is written" — in the folder, or on a plugin branch — needs §4.4's state read (§3.2, §3.5), as RN:832 does.

## 6. The BRD-route `*_NOT_HANDED_OFF` stops

Recipe `grep -rno -E '[A-Z_]+_NOT_HANDED_OFF' plugins/*/commands/*.md`: 16 distinct ids across 12 command files, counting files that only cite one. Defined in their own command (each read):

| Stop | Route | Form today | File tested | Prefix named |
|---|---|---|---|---|
| `PRD_GROUND_PRD_NOT_HANDED_OFF` (`prd-ground.md:564`, :576) | idea | both (batch 1) — **the model** | `prd.md` | `prd/` |
| `PRD_PROPOSAL_PRD_NOT_HANDED_OFF` (`prd-proposal.md`) | idea | both (batch 1) | `prd.md` | `prd/` |
| `CREATE_ARD_PRD_NOT_HANDED_OFF` (ARD:304, :314), `SPECIFY_PRD_NOT_HANDED_OFF` (SPEC:347, :357) | both | both (batch 1) | `prd.md` | `prd/` |
| `EPICS_PRD_NOT_HANDED_OFF` | both | both (b1b) | `prd.md` | `prd/` |
| `IMPLEMENT_SPEC/_DESIGN_NOT_HANDED_OFF` (IMPL:377–413) | — | both (batch 2) | spec / design | `spec/` `design/` |
| `CREATE_PRD_REGISTER_NOT_HANDED_OFF` (CPRD:405–414) | BRD | **uncommitted only** | `decisions.md` | `brd/` |
| `CREATE_ARD_REGISTER_NOT_HANDED_OFF` (ARD:378–387) | BRD | uncommitted only | `decisions.md` | `brd/` |
| `SPECIFY_REGISTER_NOT_HANDED_OFF` (SPEC:418–427) | BRD | uncommitted only | `decisions.md` | `brd/` |
| `PRD_GROUND_INVENTORY_NOT_HANDED_OFF` (`prd-ground.md:337–344`) | BRD | uncommitted only | `brd/brd-inventory.md` | `brd/` |
| `PRD_GROUND_NOT_HANDED_OFF` (`prd-ground.md:430–437`) | BRD | uncommitted only | `coverage-ledger.md` (+ inventory added) | `brd/` |
| `BRD_PACKAGE_REGISTER_NOT_HANDED_OFF` (`brd-package.md:302–309`) | BRD | uncommitted only | `decisions.md` + each `interview/round-<N>.md` | `brd/` |
| `BRD_PACKAGE_SHIPPED_NOT_HANDED_OFF` (`brd-package.md:318–325`) | BRD | uncommitted only | `interview/customer-questions.md`, `code-defect-log.md` | `brd/` |
| `BRD_RECONCILE_PACKAGE_NOT_HANDED_OFF` (REC:377–384) | BRD | uncommitted only | the dated prompt, self-review, delivery note, `bundle-<date>/` files (+ `brd-link.md` where changed) | `brd/` |
| `BRD_PROPOSAL_SLICE_NOT_HANDED_OFF` (`brd-proposal.md:444–455`) | BRD | uncommitted only, one block per slice | each included slice's `proposal.md` | `prd/` |
| **found now:** `BRD_PACKAGE_ROUNDS_NOT_ON_MAIN` (`brd-package.md:367–374`, and a second message at :466–473) | BRD | uncommitted only — a row-F-in-folder stop the design's grep misses (its id has no `_NOT_HANDED_OFF`) | `interview/round-<N>.md` | `brd/` |

**The model — PH §4.4 row F** (PH:615): "Which form the stop prints turns on whether HEAD holds the file … `git -C "$SPECS_PATH" cat-file -e "HEAD:./<path>" 2>/dev/null` … **Where HEAD does not hold it** … the file goes on a new branch: `switch --no-track -c <new-branch> <default-ref>`, then `add -f`, then `commit` … **Where HEAD holds it** … the branch is landed instead. On a branch other than `<default>`: the commands row E gives … On `<default>` itself … the commands row C″ gives…". Command model, PRD-GROUND:576 + :580:
> `PRD_GROUND_PRD_NOT_HANDED_OFF: <KEY>'s prd.md at <path> is committed on <branch>, a branch this plugin does not hand off, and is not on <default>. This run read none of it and grounded nothing. Land that branch with the commands printed beneath this message; do not re-run /product-workflows:create-prd, which would rewrite the PRD rather than land the one committed. Then open a pull request from <branch> into <default> and merge it, or merge the one already open from <branch>, and re-run '/product-workflows:prd-ground <KEY>'. Ignored, every /prd-ground run on this folder stops here until prd.md is on <default>.`
> `<the commands §4.4's row F gives for a file HEAD holds, as the slot rules below say>`

followed by :580's slot rules (`<branch>` from `symbolic-ref --short HEAD`; three sentences change for `<default>`, for no `origin`, and where row F's reads select no command). Page model: `pw/docs/commands/create-ard.md:55`.

**The four parts as they stand in the BRD-route stops:**
- `CREATE_*`/`SPECIFY_REGISTER_NOT_HANDED_OFF` carry all four: found, "This run read none of it and wrote nothing", commands, "Ignored, every /create-prd, /create-ard and /specify run on this slice meets this register's gate again until it is on <default> — this stop, or, where the register has since been committed to a branch, the stop for a register on a branch." Note that last clause: a committed register is said to meet "the stop for a register on a branch", but a register committed on a non-plugin branch is row F again (§3.4) — the case the committed form exists for.
- `BRD_PACKAGE_REGISTER_NOT_HANDED_OFF`, `BRD_RECONCILE_PACKAGE_NOT_HANDED_OFF`, `PRD_GROUND_INVENTORY_NOT_HANDED_OFF` have parts 1 and 3 and a "do not re-run" clause, but **no "what the run did not do" sentence and no "Ignored, …" clause**.
- `BRD_PACKAGE_SHIPPED_NOT_HANDED_OFF` has "Nothing was written." but no "Ignored" clause.
- `PRD_GROUND_NOT_HANDED_OFF` has `<the clause below>` (:430, :448ff) and no "did not do"/"Ignored".
- `BRD_PROPOSAL_SLICE_NOT_HANDED_OFF` has found + consequence ("the umbrella would roll up numbers no later reader can reproduce"), commands, an alternative ("or re-run this command and exclude it"), no "Ignored".
- `BRD_PACKAGE_ROUNDS_NOT_ON_MAIN` has found, commands, "do not re-run" (:367); its second message (:466) has no "do not re-run".

Multi-file stops (`BRD_PACKAGE_*`, `BRD_RECONCILE_PACKAGE_*`, `PRD_GROUND_NOT_HANDED_OFF`, `BRD_PROPOSAL_SLICE_*`) can have files split across states — some committed, some untracked — which the one-HEAD-test form does not decide. §4.4 row F speaks of "the file", "with one `add` and `commit` path per file". A case the design does not decide.

**The slice form of the PRD stops and the register sentence** (ARD:322, identically SPEC:365):
> **On a slice, the uncommitted form tests the register too.** `/product-workflows:create-prd`'s handoff on the BRD route lands the slice's `decisions.md` beside `prd.md` … so a declined one can leave both unlanded, and the re-run that landing `prd.md` alone leads to then stops at *Gate the decision register*. Where the PRD folder is a slice, the stop tests that `decisions.md` before it prints … it is unlanded where `git -C "$SPECS_PATH" ls-files --others -- "./<register>"` prints it … or where `git -C "$SPECS_PATH" diff --quiet HEAD -- "./<register>"` and `git -C "$SPECS_PATH" diff --quiet "<default-ref>" -- "./<register>"` both exit non-zero … Where it is unlanded, the first sentence ends at `its handoff was declined.` … and `This slice's decisions.md is not on <default> as it stands either; the re-run stops on it next and names its commands.` comes before the sentence opening `Ignored`. The commands stay `prd.md`'s alone: the stop cannot tell a change `/create-prd` made from one made by hand, and the register's own stop names what lands it.

It applies to the **uncommitted** form only. In the committed form, landing the branch carries a register committed with it. b1 ruling 41 kept the test as tightened, because "the printed `switch` replaces that copy". §5.5's last-but-two Batch 4 bullet asks batch 4 to re-read this beside the register stops' committed form and decide whether "the two stops a declined handoff leads to are worded as one remedy".

**Row-F stops of the same class outside the design's list (found now):** `BRD_SPLIT_NEEDS_GROUNDING` (`brd-split.md:185`) and `BRD_INTERVIEW_NEEDS_GROUNDING` (INT:244) say "no grounding findings on file … run /product-workflows:prd-ground <BRD-KEY> first" on row F. They never test whether `grounding/code-grounding.md` is in the folder, so a declined `/prd-ground` handoff is told to re-ground, not to land.

## 7. `/implement`'s stop on a slice

`IMPLEMENT_NEEDS_SPEC` (IMPL:419–421) prints `<the PRD's state>` and `<what the first missing document needs>` per IMPL:423–428. The slice state is IMPL:424:
> - **No gap** — `prd.md` on `<default-ref>`, or nowhere on a BRD-route slice, a PRD folder carrying a `brd-link.md` → `<the PRD's state>` is empty, and the step reads `'/product-workflows:specify <UNIT>' writes the specification: run it and merge its handoff.`

After batch 4, `/specify <UNIT>` stops on a slice whose ledger fails — with or without a landed `prd.md` (§5.4's test is on the slice, not the PRD) — so both halves of "No gap" on a slice name a run that stops (L8). `<UNIT>` may be an Epic under the slice: `/specify <EPIC>` tests the slice above.

**The rung, in PH §4.4** (PH:617):
> **The `prd.md` rung reads as `/product-workflows:specify` Phase 0's *Gate the PRD* reads it.** On a BRD-route slice — a PRD folder carrying a `brd-link.md` — a `prd.md` that is nowhere is no gap, since a slice holding none is specified as it stands, and the rule reads none of the route's coverage-ledger tests, which `/product-workflows:create-prd` applies to a slice and `/product-workflows:create-ard` and `/product-workflows:specify` do not yet apply to their own runs.

"do not yet apply" is a claim with an expiry date. "**Which stops use it.** `/product-workflows:create-ard`'s `CREATE_ARD_NEEDS_PRD` and `/product-workflows:specify`'s `SPECIFY_NEEDS_PRD` … take its `prd.md` rung alone" (same line). It sits in `reference-parts/phase-handoff/require-on-main.md:249` (generated). Recipe `grep -rln 'The first missing document' plugins/*/commands plugins/*/references` returns **10 files** today: implement, ready, conformance, design, document, release-notes, scan, components, next-phase-offer, phase-handoff (b3 added document and release-notes).

**Restatements of the slice exception** (F-12's list, verified with wrap-insensitive search for `nowhere on a BRD-route slice|BRD-route slice needs none|…`):
- IMPL:424 ✓;
- DES:115 "no gap — on `<default-ref>`, or nowhere on a BRD-route slice → `'/product-workflows:specify <UNIT>' writes the specification…`" ✓;
- `plugins/dev-workflows/docs/commands/implement.md:132` "(a BRD-route slice needs none)" ✓;
- `…/docs/commands/ready.md:66` ✓;
- `plugins/security-workflows/docs/commands/scan.md:168` ✓;
- `plugins/dev-workflows/docs/commands/design.md:54` ✓;
- PH:617 and its generated copy ✓.

No restatement found beyond F-12's list.

**Readers through §4.4 without restating:** CONF:74 (*What a stop or an offer names in place of a run that would stop on arrival*) with step 4's gate (CONF:72) and `CONFORMANCE_NO_REQUIREMENTS` (:141 "specify it with '/product-workflows:specify <KEY>'"); RDY:701; DOC:270–276 (step 3a's *Stop* line and *A document's state, and what each state names*); RN:832; SCAN:550/554; `components.md:120–126`; NPO:387 (the `/dev-workflows:implement` precondition).

**`IMPLEMENT_BRD_NOT_SLICED`'s remedy** (IMPL:198–200): "`Implement within a slice instead: '/dev-workflows:implement <SLICE-KEY>' — <each slice's key>.`" (b2 P-140: "the remedy naming for each slice what its own ladder resolves, once batch 4 has given `/specify` the slice's coverage-ledger tests"). Same shape, not on the design's list: `DESIGN_BRD_NOT_SLICED` (DES:67–68, "`Design within a slice instead: '/dev-workflows:design <SLICE-KEY>'`"), `CONFORMANCE_BRD_NOT_SLICED` (CONF:60).

**How `dev-workflows` reads the BRD route today (IMPL:219 → IMPL:229, and DES:128).** The multi-component 0-Epic *Split* option, where the folder holds no `prd.md`, "becomes what `Skill(skill: "workflows-core:reference", args: "next-phase-offer epics-precondition")`'s *`/epics` precondition* names in its place: … or, on a BRD-route slice, whatever its ledger tests resolve `/product-workflows:create-prd <PRD>` to — `/product-workflows:create-prd <SLICE>` where both clear, a `/product-workflows:brd-split` where one fails — still marked `(Recommended)`". NPO's precondition (NPO:363–367) says only: "on a BRD-route slice the two data refusals on that slice's own ledger are tested first and the offer resolves to `/product-workflows:brd-split` against one of two keys, or to no option at all, where either fails (`product-workflows:coverage-ledger-format` §5.2, the authority, applied by each offering command)". **No `workflows-core` text states the gate set, the dispositions to read, the order, the parent's ledger for the empty set, or the missing-ledger rule**; a `dev-workflows` command cannot load CLF (CLAUDE.md: "a reference file does not" cross a plugin boundary). IMPL:229 and DES:128 also omit the non-empty-NOT_ELIGIBLE and missing-ledger states, where NPO says "no option at all". Precedents for stating the test outside `product-workflows`: DOC:156–174 and RN:152–169 restate it in the command's own text; `workflows-core:addressing` §4.1 restates CLF §5.1's container test "for a plugin that cannot read this file" (CLF:522–523).

**What `/implement` would need in hand** at IMPL:424 on a slice: the slice's `brd-link.md` (`claims:`, `parent:`), its `coverage-ledger.md` dispositions over the gate set, and, for an empty gate set, the parent's `coverage-ledger.md`. Today it holds only the `brd-link.md` presence test and §4.4's state reads.

## 8. `/document` step 3a, `/conformance`, `/ready`

None restates the slice rung; each changes with PH:617.
- **DOC:270–276.** *Stop* prints `<how it is built>`: on an Epic, `/dev-workflows:implement <EPIC>` where the pair is on the default branch, "and otherwise … what the Epic's first missing document needs". DOC:275: "each — the unit's `specification.md` and `design.md`, and the PRD folder's `prd.md` — is read as `workflows-core:phase-handoff` §4.4's *The first missing document* reads one (`Skill(skill: "workflows-core:reference", args: "phase-handoff")`, the whole reference)". On a slice with no spec, it names `/specify <UNIT>` today.
- **CONF:74.** "(b)'s `CONFORMANCE_NO_REQUIREMENTS`, (c)'s `CONFORMANCE_NOT_IMPLEMENTED` and `CONFORMANCE_PRD_NOT_IMPLEMENTED`, and Phase 7's offers of `/dev-workflows:implement`, `/product-workflows:update-spec`, `/product-workflows:create-ard` and `/product-workflows:epics` each name … what the first missing document needs". Separately, Phase 7's amend-document line (CONF:692–705) carries its own slice exception: "save `/product-workflows:create-ard` on a BRD-route slice holding no `prd.md`, which it takes as it stands" (CONF:702). Its twin is NPO:400. Both fall under batch 4; the design names neither (found now).
- **RDY:701.** SUPPORTED → `/dev-workflows:implement <ADDRESS>` "only where the unit it builds has its `specification.md` and `design.md` on the default branch … otherwise, in its place, what the unit's first missing document needs (`workflows-core:phase-handoff` §4.4)". States come from Phase 1 step 2.

So whatever §4.4's `prd.md` rung says about a slice — the ledger tests resolved to `/specify`, `/brd-split …` or nothing — reaches all three by citation. What each prints must still be read against the new rung, the unit possibly being an Epic under a slice. Their sweep entries are re-reads, not edits, unless the new rung needs inputs (a ledger read) these commands do not hold.

## 9. The pages

§5.5's Batch 4 list:
- `pw/docs/brd-workflow.md:296–299` — "On an advancing slice run, `/create-prd` on the BRD route carries one further condition — the reconciled ledger leaves no row `unallocated` and at least one `covered-here` (the two refusals its own Phase 0 raises) — while `/create-ard` on the BRD route and `/specify` on the BRD route carry none of their own, since neither reads the ledger as an authoring input, and the PRD gate both run reports a slice holding no `prd.md` rather than stopping on it, and stops on a `prd.md` the slice holds that was never handed off." And :300–301 "the level test and `/create-prd`'s eligibility test are each refused by the offered command's own Phase 0".
- `brd-workflow.md:327` (cell **199 characters**, check 6's cap 200): "Refuses a `BRD-` container; offered on any advancing slice run. Gates `prd.md`: goes on with none, stops on one never handed off. Never authors from the ledger. One address (`CREATE_ARD_ONE_ADDRESS`)"; :328 "Otherwise offered on the same terms as `/create-ard`."
- `pw/docs/workflow.md:143` "`/create-ard <SLICE-KEY>` and `/specify <SLICE-KEY>` add none of their own, since neither reads the ledger as an authoring input, and the PRD gate both run reports a slice holding no `prd.md` rather than stopping on it…"; `:145` "`/create-ard` and `/specify` on the slice level alone, `/create-prd` only where the slice is PRD-eligible".
- `workflow.md:202` (cell 169 characters) "On a slice, with no further condition — gates and reads `prd.md`, going on where the slice holds none and stopping on one never handed off; never authors from the ledger"; `:203` "On a slice, on exactly the same terms as `/create-ard`".
- `pw/docs/roles-and-phases.md:24` "…and `/create-ard` and `/specify` on the level test alone, since neither reads the ledger as an authoring input…".
- `pw/docs/commands/brd-reconcile.md:712` "→ [`/create-ard <SLICE-KEY>`] and [`/specify <SLICE-KEY>`], and [`/create-prd <SLICE-KEY>`] where no claimed ledger row is still `unallocated` and at least one is `covered-here`"; `:727` "**On a slice**, with no further condition | Consults no tracker; on a slice holding no `prd.md` the PRD gate's `absent` branch proceeds, so no wait on an unauthored PRD; it reads neither `claims:` nor the ledger as an authoring input" (cell 189); `:728` "**On a slice**, with no further condition".
- `pw/docs/commands/create-ard.md:88`, `specify.md:89` — "**No coverage-ledger check.** … That is a decision, not an omission — [`/create-prd`] is where the gate lives. The run does open the ledger in two places [three, on the specify page]…".
- `workflow.md:48` and `:151` (§5 (d) above).

Found now (each states `/create-ard`/`/specify` on a slice go on, or describes their unreachable branches):
- `brd-workflow.md:305–308` "neither of the other two waits on an unauthored PRD, so an ARD or a specification can be authored from a BRD whose ledger will never qualify for a PRD of its own" — false after batch 4.
- `brd-workflow.md:92–95` "On a slice with no `prd.md`, `/create-ard` and `/specify` offer `/create-prd` where the slice can take a PRD, and otherwise hand back into the route through `/brd-split` — on the slice, to allocate a row still `unallocated`, or on its parent, to keep or remove a slice left empty."
- Diagram edges `brd-workflow.md:72–75` and `workflow.md:106–109`: `createard -.->|"BRD slice, no prd.md — a row still unallocated"| splitslice`, `… |"an empty slice — keep or remove it"| splitroot` — edges for offers batch 4 makes unreachable. :70–71 and :104–105 (`no prd.md — author the PRD`) stay.
- Handover edges whose labels state no ledger condition for `/create-ard` and `/specify`: `workflow.md:120–121`, `:123–124`; `brd-workflow.md:55–59`; `plugins/workflows-core/docs/family-map.md:98–99`, `:101–102`. The `/create-prd` edges carry "PRD-eligible".
- `workflow.md:141` "On a BRD-route slice holding no `prd.md`, `/create-ard` and `/specify` offer `/create-prd` in place of `/epics` where the slice can take a PRD, and `/brd-split` on the slice or on its parent where it cannot yet"; `:149` "the edges from `/create-ard` and `/specify` back into the route".
- `pw/docs/getting-started.md:150` step 10 "`/brd-reconcile` offers [`/specify`] `ACME-80-01` and [`/create-ard`] `ACME-80-01`, and `/create-prd ACME-80-01` where the slice is PRD-eligible".
- `pw/docs/commands/brd-interview.md:613` "[`/create-ard`] and [`/specify`] always"; `:627`.
- `pw/docs/commands/brd-reconcile.md:700–701` "the other two would still be offered".
- `pw/docs/commands/create-ard.md:78` and `specify.md:86` "**The PRD gate runs here too … — but a slice needs no PRD.** … A slice with no `prd.md` is reported and the run architects [specifies] from the resolved folder".
- `create-ard.md` page :233–238 and :249–254, the slice replacement list (brd-split forms, "no second option").
- `specify.md` page :23 "On a BRD slice with no `prd.md` … the first option instead names the applicable PRD-authoring or BRD-allocation prerequisite, or is absent when none can be offered", :100 ("this run has cleared only the container one"), :141–145.
- Pages listing the stop ids batch 4 adds to: create-ard page :17, :54–59, :78–88; specify page :70, :86–89 (model: create-prd page :94–95).
- Pages of the BRD-route not-handed-off stops: create-prd :89, create-ard :79, specify :86, `prd-ground.md` :259, :292, `brd-package.md` :135, :145, :152, :172, `brd-reconcile.md` :200, `brd-proposal.md` :56.

## 10. The sweep population

Scope: `git ls-files` under `plugins/` (every `CHANGELOG.md` and `reference-parts/` excluded — the latter generated), `README.md`, `CLAUDE.md`, `.claude/rules/*.md`, `docs/maintainers/*.md`. Searches run, all wrap-insensitive (`scripts/wgrep.py`: collapse whitespace per file, regex, map offset to line):
1. **Phrases** (the claim's words): `level test alone`, `slice level alone`, `with no further condition`, `No coverage-ledger check`, ``reads no `claims:` list and no coverage ledger``, `none of their own`, `are always offered`, `always reachable from this state`, `as an authoring input`, `holding none goes on`, `still goes on`, `a slice needs no PRD`, `not a prerequisite for (this command|either|/create-ard|/specify)`, `whose ledger will never qualify`.
2. **The F-12 subject:** `nowhere on a BRD-route slice`, `a BRD-route slice needs none`, `do not yet apply`, `ledger tests resolve`, `which it takes as it stands`.
3. **Unreachable branches:** `six literal arrays`, `of the six arrays`, `row still unallocated`, `keep or remove`, `cleared only`, `has cleared`, `only one of its three refusals`, `Two places do open`, `Three places do open`.
4. **Exclusivity probe** (refinement 3), within 200 characters of `ledger|eligib|covered-here|unallocated`: `only when`, `is the only`, `nothing else`, `and no other`, `only ever`, `the sole`, `only writer|caller|consumer`, `no other command`, `the one command`, `the only place`, `all three refusals`, `where … gate lives`. 49 hits.
   - On this subject: `brd-route.md:44` ("all three refusals cite"); SPEC:687 ("it is the only one of its three refusals this run has cleared").
   - The table rows "all three refusals cleared" (ARD:1084, SPEC:1452, `epics.md:256`, `update-prd.md:75`): T.
   - Other commands' own claims about where they open a ledger (`epics.md:123`, `prd-proposal.md:238`, `update-prd.md:83`): T, untouched.
   - Search 3's noun forms found the rest of the class: ARD:543 "Two places", SPEC:780 "Three places", ARD:1072 and SPEC:1439 "cleared only the container refusal", specify page :89, :100, create-ard page :233.
5. **Subject sweep for the id class:** `grep -rno -E '[A-Z_]+_NOT_HANDED_OFF'` (§6), plus row-F-in-folder stops read by hand (`ROUNDS_NOT_ON_MAIN` found).
6. **Execution-phrase sweep for L8:** every `product-workflows:create-ard` / `product-workflows:specify` in commands, references and agents — 327 hits in 53 files. Each offering site was opened and classed by whether the offering run can stand on a slice whose ledger fails.

**Counts before any edit** (search 1–3, the same scope): `level test alone` 2 · `slice level alone` 1 · `with no further condition` 3 · `No coverage-ledger check` 2 · ``reads no `claims:` list and no coverage ledger`` 2 · `none of their own` 3 · `are always offered` 1 · `always reachable from this state` 1 · `a BRD-route slice needs none` 4 · `nowhere on a BRD-route slice` 2 · `do not yet apply` 1 · `as an authoring input` 8 · `holding none goes on` 3 · `still goes on` 4 · `six literal arrays` 2 · `of the six arrays` 2 (one, `prd-ground.md:2417`, another subject) · `whose ledger will never qualify` 1 · `ledger tests resolve` 2 · `which it takes as it stands` 2 · ``reads neither `claims:` nor the ledger`` 1.

Verdicts: **F** false after batch 4 · **U** describes a branch the stop makes unreachable (remove, §5.4) · **I** incomplete, extend · **R** re-read: true, or true by citation, if the plan keeps it · **T** stays true, checked. *Owner* = the design bullet, or "found now".

### `product-workflows` commands

| Row | Site | Quote / subject | Owner | V |
|---|---|---|---|---|
| S-1 | ARD:23–26 | "`/create-ard <SLICE-KEY>` → an ARD on the **BRD route** … A `BRD-` container is refused (Phase 0 step 1a)." | found now | I |
| S-2 | ARD:161–164 | container refusal: "Name every slice and offer `/product-workflows:create-ard <SLICE-KEY>` once per slice" | found now (L8) | I |
| S-3 | ARD:245, :261–269 | advisory "on a PRD-level run with no `prd.md` — a slice"; "the ordinary BRD-route state, since on that route `/create-prd` is not a prerequisite" | found now | R |
| S-4 | ARD:280, :283 | Gate the PRD: slice holding none → "the slice's ordinary state, kept as it was" | §5.4 (placement) | I |
| S-5 | ARD:322 | slice form, register sentence | §5.5 bullet 4 | R/decide |
| S-6 | ARD:330–352 | "**…a slice holding no `prd.md` still goes on.** … still not a prerequisite for this command" | found now | I |
| S-7 | ARD:378–387 | `CREATE_ARD_REGISTER_NOT_HANDED_OFF` | §4, §5.4 | I (committed form) |
| S-8 | ARD:496–506 | Phase 2: "reaches this phase only on the BRD route … the slice's **ordinary** state" | found now | I |
| S-9 | ARD:536–550 | the overturned statement; "Two places do open the ledger" | §5.4 | F |
| S-10 | ARD:921 | requirement-gap line | §5.5 last bullet | R (reason) |
| S-11 | ARD:1042–1068 | precondition, "naming `/create-prd` without the test below…" | §5.5 last bullet | I |
| S-12 | ARD:1070–1080 | "has cleared only the container refusal"; "five rows pick among the last five of the six literal arrays" | §5.4 | F |
| S-13 | ARD:1085–1088 | table rows 2–5 | §5.4 | U |
| S-14 | ARD:1090–1095 | dropping rather than annotating | §5.4 | I |
| S-15 | ARD:1100–1104, :1111–1114 | "Six literal arrays"; arrays 3–5, and 6's ledger states | §5.4 | U (keep 6 for `kind: prd`) |
| S-16 | ARD:1115–1119 | "`/specify <SLICE-KEY>` is always reachable from this state" — reason | found now | I |
| S-17 | ARD:1120–1135 | `/epics` bullet, :1126–1131 | §5.4 | F |
| S-18 | ARD:1136–1148, :1159 | `/brd-split` clause halves | found now (§5.4's class) | U |
| S-19 | ARD:1149 | "none of the six arrays" | found now | I |
| S-20 | ARD:1194 | "The ten argument-, tree- and git-shaped stops" | found now | I (+2 ids) |
| S-21 | SPEC:26–28 | usage: "a `BRD-` container is refused (Phase 0 step 0)" | found now | I |
| S-22 | SPEC:80–83 | container refusal: "offer `/product-workflows:specify <SLICE-KEY>` once per slice" | found now (L8) | I |
| S-23 | SPEC:323, :326 | Gate the PRD: slice holding none, ordinary state | §5.4 (placement) | I |
| S-24 | SPEC:365 | slice form, register sentence | §5.5 bullet 4 | R/decide |
| S-25 | SPEC:373–392 | "…still goes on." | found now | I |
| S-26 | SPEC:418–427 | `SPECIFY_REGISTER_NOT_HANDED_OFF` | §4 | I |
| S-27 | SPEC:603–611 | Step A: no `prd.md` "reaches this step only on the BRD route … the slice's ordinary state" | found now | I |
| S-28 | SPEC:683–697 | zero-Epics slice form; P-131 sentence :685–686; "the only one of its three refusals this run has cleared" :687–688 | §5.4, §5.5 (P-131) | U/F |
| S-29 | SPEC:773–788 | the overturned statement; "Three places do open the ledger" | §5.4 | F |
| S-30 | SPEC:1261 | capture-at-block list of every `SPECIFY_*` | found now | I |
| S-31 | SPEC:1417–1435 | precondition, "naming `/create-prd` without the test below" | found now | I |
| S-32 | SPEC:1437–1440 | "has cleared only the container refusal" | §5.4 | F |
| S-33 | SPEC:1453–1456 | table rows 2–5 | §5.4 | U |
| S-34 | SPEC:1458–1462, :1474–1479 | dropping; "only a BRD-route slice has a gate set, so the table above is where a slice with no `prd.md` and no `covered-here` row stops the `/create-prd` recommendation" | found now | I/F |
| S-35 | CPRD:270–375 | step 7, the test's source | §5.4 bullet 2 (home) | R |
| S-36 | CPRD:405–414 | `CREATE_PRD_REGISTER_NOT_HANDED_OFF` | §4 | I |
| S-37 | CPRD:909–931 | Phase 6 offers `/create-ard`, `/specify` on the slice | — | T (same run's ledger passed) |
| S-38 | INT:2524–2535 | *level test alone* | §5.4, §5.5 | F |
| S-39 | INT:2545–2552, :2557 | prose list; eligible array | §5.5 (landed) | I |
| S-40 | INT:2563 | not-eligible array | §5.4 | F |
| S-41 | INT:2573–2591 | "Five of the six lists…"; "which of the three authoring commands comes first" | — | R |
| S-42 | INT:2624–2629 | context hygiene for the authoring ladder | found now | R |
| S-43 | REC:3011–3030 | *always offered* | §5.4, §5.5 | F |
| S-44 | REC:3071–3086 | advance list and array — arity where all three drop | found now (arity) | I |
| S-45 | REC:3190–3199 | "a refusal this phase can make and their own Phase 0s cannot — unlike the level refusal above, which each of them now makes for itself" | found now | I |
| S-46 | REC:3201–3214 | "What the clause does not cover … `/create-ard`'s and `/specify`'s on `prd.md`, a file this run does not write either" | — | R |
| S-47 | REC:377–384 | `BRD_RECONCILE_PACKAGE_NOT_HANDED_OFF` | §4 | I |
| S-48 | `brd-package.md:302`, `:318` | the two stops | §4 | I |
| S-49 | `brd-package.md:367`, `:466` | `BRD_PACKAGE_ROUNDS_NOT_ON_MAIN` | found now | I |
| S-50 | `brd-proposal.md:444–455` | `BRD_PROPOSAL_SLICE_NOT_HANDED_OFF` | §4 | I |
| S-51 | `prd-ground.md:337`, `:430` | the two slice stops | §4 | I |
| S-52 | `epics.md:1212`; `:486`, `:508`, `:728`, `:1146–1149`, `:1334` | offers of `/specify <EPIC>`, `/create-ard <EPIC>`; `### Targets` "`/product-workflows:create-ard <PRD-KEY>` (refine)" | found now (L8, changed-ledger state) | R/decide |
| S-53 | `update-prd.md:204`, `:210` | "Re-run architecture — `/product-workflows:create-ard <KEY>`" | found now | R/decide |
| S-54 | `prd-proposal.md:816`, `:820` | "Raise the tier first — `/product-workflows:create-ard <KEY>`" / `/specify <KEY>` | found now | R/decide |
| S-55 | `idea.md:98` | Epic-folder remedy "specify it with '/product-workflows:specify <KEY>'" | found now | R/decide |
| S-56 | `update-spec.md:52`; `:57`; `:164–166` | `UPDATE_SPEC_NO_BASE` "Author one with '/product-workflows:specify <ADDRESS>'"; the step-6 carve-out (L5); Phase 8 | found now; §5.1 (carve-out) | I |

### `product-workflows` reference

| Row | Site | Quote | Owner | V |
|---|---|---|---|---|
| S-57 | CLF:332–381 | "## 5. PRD eligibility"; "may go on to author its own `prd.md`"; "must refuse to author a PRD here" | §5.4 bullet 2 | I (widen or cite) |
| S-58 | CLF:552–611 | "### 5.2 Offering `/create-prd` — three refusals, not one"; the empty-set vs missing-ledger wording | §5.4 bullet 2 | I |
| S-59 | CLF:508–524 | §5.1's consumer list | — | T (container test) |

### `workflows-core`

| Row | Site | Quote | Owner | V |
|---|---|---|---|---|
| S-60 | PH:321, :322 | `/create-ard` and `/specify` rows: "on a BRD-route slice, the pre-existing behaviour, kept … since a slice holding no `prd.md` is the route's ordinary state" | §11.1 (no row) | R |
| S-61 | PH:358 | "a slice holding no `prd.md` still falls back for both"; "a slice holding none still goes on" | found now | I |
| S-62 | PH:617 | `prd.md` rung on a slice, "do not yet apply" | §5.5 F-12, L12 | F |
| S-63 | PH:615 | row F's two forms | §4 | T (cited) |
| S-64 | NPO:219–227 | interview advance offers | §5.5 L-B4-8 | F |
| S-65 | NPO:256–269 | "the other two carry none of their own…"; "the level test and `/create-prd`'s eligibility test are each enforced by the offered command's own Phase 0" | §5.5 L-B4-8 | F |
| S-66 | NPO:244–249 | "The BRD route on `/create-prd`, `/create-ard` and `/specify` all ship" | — | T |
| S-67 | NPO:326–335 | PE: `/epics <PRD>` → `/specify <EPIC>`, `/create-ard <EPIC>` | found now | R/decide |
| S-68 | NPO:283–286 | proposals: "`/product-workflows:create-ard <KEY>` at tier 2, `/product-workflows:specify <KEY>` at tier 3" | found now | R/decide |
| S-69 | NPO:354–367 | `/epics` precondition: "which the BRD route reaches legitimately since `/create-prd` is not a prerequisite for `/create-ard` there"; ledger resolution "applied by each offering command" | §5.4 bullet 6 (mechanism) | I |
| S-70 | NPO:387 | the `/implement` precondition | — | R (by §4.4) |
| S-71 | NPO:400 | "save `/product-workflows:create-ard` on a BRD-route slice holding no `prd.md`, which it takes as it stands" | found now | F |
| S-72 | NPO:401 | threats → PA `/product-workflows:create-ard <KEY>` | found now | R |
| S-73 | `components.md:120` | "`ard_contract` → `/product-workflows:create-ard <PRD>`, `prd_spec` → `/product-workflows:specify <PRD>`" | found now | R |
| S-74 | `workflows-core/docs/family-map.md:98–99`, `:101–102` | handover edge labels | found now | I |

### `dev-workflows`, `docs-workflows`, `security-workflows`

| Row | Site | Quote | Owner | V |
|---|---|---|---|---|
| S-75 | IMPL:198–200 | `IMPLEMENT_BRD_NOT_SLICED` remedy | §5.5 b2 P-140 | I |
| S-76 | IMPL:229 | "or, on a BRD-route slice, whatever its ledger tests resolve…" | §5.4 bullet 6 (mechanism) | R |
| S-77 | IMPL:424 | "**No gap** — … or nowhere on a BRD-route slice" | §5.4 bullet 6, §5.5 F-12 | F |
| S-78 | DES:67–68 | `DESIGN_BRD_NOT_SLICED` "Design within a slice instead" | found now (same shape as P-140) | R/decide |
| S-79 | DES:115 | "no gap — … or nowhere on a BRD-route slice" | §5.5 F-12 | F |
| S-80 | DES:128 | the same "whatever its ledger tests resolve" | found now | R |
| S-81 | DES:282–283 | "Add the component first — /product-workflows:create-ard <PRD>" | found now | R |
| S-82 | DES:259, :265, :540, :572, :713, :826 | threat lines naming `/create-ard <KEY>` for the architect | found now | R |
| S-83 | CONF:74, :141 | by §4.4 | §5.5 F-12 | R |
| S-84 | CONF:702 | "save `/product-workflows:create-ard` on a BRD-route slice holding no `prd.md`, which it takes as it stands" | found now | F |
| S-85 | CONF:707 | `### Threats` PA → `/create-ard <KEY>` | found now | R |
| S-86 | RDY:701 | by §4.4 | §5.5 F-12 | R |
| S-87 | `dev-workflows/docs/commands/implement.md:132`, `ready.md:66`, `design.md:54` | "(a BRD-route slice needs none)" | §5.5 F-12 | F |
| S-88 | DOC:270–276 | step 3a *Stop* line | §5.5 b3 bullet | R |
| S-89 | RN:815, :830–833 | *The two offers wait for a landed PRD* | §5.5 b3 bullet | I |
| S-90 | SCAN:448, :554 | `pa_next_step` → `/product-workflows:create-ard`; PRD test | found now | R |
| S-91 | `security-workflows/docs/commands/scan.md:168` | "(a BRD-route slice needs none)" | §5.5 F-12 | F |

### `product-workflows` pages

| Row | Site | Owner | V |
|---|---|---|---|
| S-92 | `brd-workflow.md:296–301` | §5.5 (L-B4-10) | F |
| S-93 | `brd-workflow.md:305–308` | found now | F |
| S-94 | `brd-workflow.md:327–328` (cell at 199/200) | §5.5 (L-B4-10) | F |
| S-95 | `brd-workflow.md:92–95` | found now | F |
| S-96 | `brd-workflow.md:72–75` (edges), `:55–59` (handover labels) | found now | U / I |
| S-97 | `workflow.md:143`, `:145` | §5.5 (L-B4-11) | F |
| S-98 | `workflow.md:202–203` | §5.5 (E17) | F |
| S-99 | `workflow.md:48`, `:151` | §5.5 b3 bullet | I |
| S-100 | `workflow.md:141`, `:149` | found now | F/I |
| S-101 | `workflow.md:106–109` (edges), `:120–124` (labels) | found now | U / I |
| S-102 | `roles-and-phases.md:24` | §5.5 (L-B4-15) | F |
| S-103 | `getting-started.md:150` | found now | I |
| S-104 | `commands/brd-reconcile.md:712`, `:727`, `:728` | §5.5 (L-B4-16, L-B4-13) | F |
| S-105 | `commands/brd-reconcile.md:700–701` | found now | F |
| S-106 | `commands/brd-interview.md:613`, `:627` | found now | F |
| S-107 | `commands/create-ard.md:88`, `specify.md:89` | §5.5 (L-B4-12) | F |
| S-108 | `commands/create-ard.md:17`, `:54–59`, `:78`; `specify.md:70`, `:86` | found now (ids; "a slice needs no PRD") | I |
| S-109 | `commands/create-ard.md:233–238`, `:249–254` | found now | U |
| S-110 | `commands/specify.md:23`, `:100`, `:141–145` | found now | U |
| S-111 | not-handed-off stop pages: `create-prd.md:89`, `create-ard.md:79`, `specify.md:86`, `prd-ground.md:259`, `:292`, `brd-package.md:135`, `:145`, `:152`, `:172`, `brd-reconcile.md:200`, `brd-proposal.md:56` | §7 | I |

### Instruction tiers

| Row | Site | Quote | Owner | V |
|---|---|---|---|---|
| S-112 | `.claude/rules/brd-route.md:32` | map line "/create-ard <SLICE-KEY> [ard-seed.md; the PRD gate runs, and its absent branch architects from the slice folder where the slice holds no prd.md…] → /specify <SLICE-KEY> […the same absent branch…]" | found now | I |
| S-113 | `.claude/rules/brd-route.md:44` | "`product-workflows:coverage-ledger-format` §5 is the authority all three refusals cite; do not re-express D5 … as a new ledger rule" | binds | I ("all three") |
| S-114 | `.claude/rules/product-workflows.md:42`, `:45` | map lines "a slice holding none goes on, reported where absent" | found now | I |
| S-115 | `.claude/rules/workflows-core-handoff.md:24` | "while a BRD slice holding none still falls back" | §11.1 | R |
| S-116 | `CLAUDE.md` § Hard constraints, last bullet; the kind-gate bullet | — | — | T |
| S-117 | `docs/maintainers/rationale.md:668`, `:674` ("which batch 4 gives `/create-ard` and `/specify` (M4)"), `:680` ("wait for batch 4") | — | §7 | I (+ batch 4 paragraph) |

**Population: 117 rows**, covering about 200 line sites. By verdict:
- F 28
- U 8
- I 44
- R 20
- R/decide 9
- T 5
- mixed 3 (S-28 U/F, S-34 I/F, S-100 F/I)

By owner:
- 53 rows are owned by a bullet or section of the design (§4, §5.4, §5.5);
- **52 are found now** — 38 in commands or references, 14 in pages, diagrams and instruction tiers;
- 12 are owned by neither, as "—", "§7", "§11.1" or "binds".

Counted with a Python pass over this file's `| S-n |` rows, last two columns.

Out of sweep scope, for the plan: `docs/superpowers/to-fix.md:135` ("**Open:** batch 4 (the BRD route)"); `to-test-on-real-project.md`, batch 3's block at :202; to-fix ATPATH-OUTSIDE-TREE (:227) owns the same *Gate the PRD* sections.

## 11. The error ids

`CREATE_ARD_BRD_UNALLOCATED`, `CREATE_ARD_BRD_NOT_ELIGIBLE`, `SPECIFY_BRD_UNALLOCATED`, `SPECIFY_BRD_NOT_ELIGIBLE`: **none exists** outside the design (`grep -rn` over the tree prints only `docs/superpowers/specs/2026-11-14-ladder-order-design.md:193–194`). **No gate reads error ids** (`grep -n -i -E "error id|_NOT_HANDED_OFF|NEEDS_" scripts/check-docs.sh scripts/validate-catalog.py scripts/reference-parts.py` prints nothing; `check-id-grammar.sh` gates `[PREFIX#N]` only). Where ids are listed by hand, and each needs the four (or two per command):
- ARD's *Ending early* (:33 — generic "each `CREATE_ARD_*` stop", true as written) and capture-at-block's enumerated list "The ten …" (:1194);
- SPEC:30 (generic) and SPEC:1261 (enumerated);
- the command pages' *What it needs* / BRD route bullets (create-ard page :54–59, :78–88; specify page :70, :86–89);
- `.claude/rules/product-workflows.md:42`, `:45` map lines (they name `CREATE_ARD_PRD_NOT_HANDED_OFF`, `SPECIFY_NEEDS_PRD`) and `.claude/rules/brd-route.md:32`;
- the CHANGELOGs; a live check each in `to-test-on-real-project.md` (§11 *Done when* 4).

**PH §3.4 takes no row** (§11.1: "Batch 4's ledger stops map no gate return and take no row there"), so check 11 (gate targets from §3.4 column 2) and the thirteen-consumer recipe in `.claude/rules/workflows-core-handoff.md:24` are unaffected. A new §3.4 row would change both, and would make check 11 demand `<merge-clause>` on `/create-ard` options in any `/brd-*` command writing `coverage-ledger.md`, `/brd-reconcile` among them.

## 12. Gates and budgets

**Checks a change meets:**
- **check 12** — each new or rewritten literal `choices:` array, arity 2–4, no "Other", no promised text. REC's advance array where all three drop would hold one option, and INT:2563 loses two.
- **check 11** — `/brd-*`/`/prd-*` arrays' `<merge-clause>` where the offered command gates a file the run writes; INT and REC's options keep theirs.
- **check 6** — 200-character cells: `brd-workflow.md:327` is at 199; `workflow.md:202` 169; brd-reconcile page :727 189. Measured with a column split on `|`.
- **mermaid gate** on any edge edit (`workflow.md:48`, :106–109, :120–124; `brd-workflow.md:55–59`, :72–75; `family-map.md:97–102`), with labels quoted where they hold `[ ] ( ) { } | #`.
- **check 15** — every command in `workflow.md`'s diagram (unaffected).
- **check 28** — a page naming a command links its page (already linked on these pages).
- **checks 13 and 14** on new prose.
- **check 16** — loader contract, if a `workflows-core` reference gains a citation.

**`reference-parts.py`:**
- `generate`, then `check-parts`, after editing PH (§4.4 is in the `require-on-main` entry file; PH:601 `<!-- entry: require-on-main -->`) or NPO (parts `brd`, `epics-precondition`, `dev`, `pe`, `proposals`);
- `check-citations` for any §4.4 or §3.x citation added in a `##` section of INT, REC, IMPL or CPRD/ARD/SPEC (PH §5 rule 4's three cases; RN:830's precedent loads PH whole in the sentence);
- `check-questions` — every command's first question after its **Load the question rules.** paragraph; ARD:42 and SPEC:133 come before any Phase 0 stop, and a stop with no `choices:` is not a question.

**`validate-catalog.py`:**
- fails `CLAUDE.md` above 40,000 and warns above 36,000;
- warns on a rules file above 20,000;
- fails a rules file without `paths:` or with a dead glob;
- plugin descriptions ≤1024.

Run the gates as the `run:` steps of `.github/workflows/validate-catalog.yml`, in order, one `&&` chain.

**Budgets** (`LC_ALL=C.UTF-8 wc -m`):

| File | Characters | Left before warning |
|---|---|---|
| `CLAUDE.md` | 35,978 | **22** (36,000) |
| `.claude/rules/brd-route.md` | 18,391 | 1,609 |
| `brd-route-detection.md` | 2,367 | 17,633 |
| `product-workflows.md` | 17,771 | 2,229 |
| `product-workflows-prd-flow.md` | 5,590 | — |
| `workflows-core-handoff.md` | 7,334 | — |
| `workflows-core.md` | 19,150 | 850 |
| `dev-workflows.md` | 19,761 | 239 |
| `dev-workflows-implement.md` | 19,991 | **9** |
| `dev-workflows-conformance.md` | 16,792 | 3,208 |
| `docs-workflows.md` | 19,998 | **2** |
| `release-notes.md` | 11,618 | — |
| `security-workflows.md` | 19,559 | 441 |
| `plugin-updates-coupling.md` | 19,503 | **497** |
| `plugin-updates-coupling-history-4.md` | 17,838 | 2,162 |
| `docs/maintainers/rationale.md` | 213,803 | no budget |

**Versions** (`plugin.json`; `marketplace.json` agrees):

| Plugin | Version | Top `CHANGELOG.md` heading |
|---|---|---|
| `workflows-core` | 1.96.1 | `## [1.96.1] — 2026-11-17` |
| `product-workflows` | 3.84.0 | `## [3.84.0] — 2026-11-17` |
| `dev-workflows` | 4.70.1 | `## [4.70.1] — 2026-11-17` |
| `docs-workflows` | 1.41.0 | `## [1.41.0] — 2026-11-17` |
| `security-workflows` | 0.12.6 | `## [0.12.6] — 2026-11-16` |

Newest coupling bullets (`plugin-updates-coupling.md:25–26`): "**Update `dev-workflows` 4.70.0 with `product-workflows` 3.84.0 and `workflows-core` 1.96.0**" and "**Update `workflows-core` 1.96.1 with `docs-workflows` 1.41.0**". A batch-4 bullet will push that file past 20,000. Its header and `CLAUDE.md:116` and `plugin-updates.md:24` all say history-4 holds "1.84.0 to 1.91.1". Moving bullets :16–18 (`workflows-core` 1.92.0–1.93.0) there fits history-4's 2,162; the range text in four places changes at equal length. A new history file costs a `CLAUDE.md` table row, which 22 characters cannot hold.

**Plugins batch 4 touches, by the population above:**
- `product-workflows` — CPRD/ARD/SPEC, INT, REC, BRD-route stops, CLF, pages;
- `workflows-core` — PH §4.4, NPO `brd`/`dev`/`epics-precondition`, family-map;
- `dev-workflows` — IMPL, DES, CONF, pages;
- `docs-workflows` — RN, maybe DOC;
- `security-workflows` — page :168, maybe SCAN.

Not ported (L10).

## 13. Collisions

- **ARD Phase 0, :277–428, and SPEC Phase 0, :320–471.** These hold, in one stretch: the ledger stop's placement; the slice rows of *Gate the PRD* (:280/:283, :323/:326); the register sentence (:322, :365); the "still goes on" defence (:330–352, :373–392); the register stops' committed form (:378, :418); and, in ARD, the advisory hand-off at :428. The same sections are ATPATH-OUTSIDE-TREE's (to-fix :227) and `/update-spec`'s citation target (`update-spec.md:57`).
- **ARD Phase 7, :1042–1159.** One precondition paragraph holds three things: b3 ruling (19)'s `kind: prd` sentence (:1060–1068); the §5.5-last-bullet sentence (:1058–1060); and the table and arrays §5.4 removes. Array :1114 is shared between the unreachable ledger states and the `kind: prd` case, which stays.
- **SPEC Step A slice bullet, :673–697.** It holds b3 (19)'s `kind: prd` sentence (:676–683), P-131's merge sentence (:685–686), and §5.4's ledger forms (:687–697).
- **SPEC Next step, :1417–1479.** It holds the same three subjects.
- **INT :2524–2564 and REC :3011–3086** each take two new conditions in one paragraph and one array, plus REC's arity.
- **NPO part `brd` (:209–274)** is one generated part holding both commands' offers. NPO:400 (Dev part) sits next to :401, which PR #207 rewrote (threat routes).
- **PH:617** is a single line holding the slice rung, "do not yet apply", *Which stops use it* and the recipe. Any wording lands in one line of `reference-parts/phase-handoff/require-on-main.md`.
- **RN:830–833.** PR #208 shifted it (b3's RN:782) without changing its text; #208's RN hunks are Phase 3 and the report (RN:390–539, :757).
- **PR #207** rewrote ARD Phase 2's Epic read (:487–489) and Phase 4.3 steps 3 and 7 (threat intake, :812–905) — next to step 8's requirement-gap line (:921), not in it. It also rewrote the create-ard page :144–189, whose :144 restates the requirement-gap line ("through [`/create-prd`] where the PRD folder holds no `prd.md` when the line is written — a BRD slice'…").
- **PR #208** rewrote DOC step 3a's lines *above* the question (DOC:245–305); the *Stop* line (DOC:270–276) is unchanged.
- **The design's §5.5 text** cites line numbers at batch branches; this file's §0 table maps them.

## 14. Where the design is wrong, incomplete or silent

Facts first; **Recommendation (mine)** marks the rest.

1. **The design undercounts the L8 population.** §5.4/§5.5 name `/brd-interview`, `/brd-reconcile`, NPO's BRD part, RN and the pages. The tree has more offers of `/create-ard` or `/specify` on a slice whose offering run reads no ledger:
   - container refusals (S-2, S-22);
   - CONF:702 and NPO:400's explicit slice exception (S-71, S-84) — **false after batch 4** wherever that slice's ledger fails: "which it takes as it stands" is the claim the stop overturns;
   - `UPDATE_SPEC_NO_BASE` (S-56);
   - `/epics`, `/update-prd` and `/prd-proposal`'s offers (S-52–S-54); `idea.md:98`;
   - `DESIGN_BRD_NOT_SLICED` (S-78);
   - DES/CONF threat routes and `components.md:120` (S-81–S-82, S-73).

   Most of these reach a failing ledger only where the ledger changed after an earlier `/create-ard`/`/specify` passed (item 3). The plan must say, per site, whether it tests the ledger, names the stop's remedy, or is left with a recorded reason (L8 "for the folder the offering run has just read").

2. **The mechanism for `dev-workflows` is unwritten.** §5.4 bullet 6 says `/implement` reads the ledger tests "through `workflows-core:next-phase-offer`'s *`/epics` precondition* as IMPL:219 reads them". That precondition (NPO:363–367) holds no test, only "§5.2 … applied by each offering command", and `dev-workflows` cannot load §5.2. IMPL:229 and DES:128 already reference "whatever its ledger tests resolve" with no executable text, and omit the no-command states. Batch 4 widens this to IMPL:424, DES:115, CONF, RDY, DOC and SCAN by way of PH:617. **Recommendation (mine):** state the slice's ledger rung once in PH §4.4's `prd.md` rung — reads, order, three outcomes — as `addressing` §4.1 restates CLF §5.1 for companion plugins. Have NPO's precondition cite it. That is one `workflows-core` copy beside CLF §5 instead of a copy per citer. `.claude/rules/brd-route.md:44` forbids re-expressing it "as a new ledger rule", so the copy must say it is CLF §5's test, verbatim in substance.

3. **A slice with a landed `prd.md` whose ledger later fails.** Reachable: REC Phase 9 moves a slice's `covered-here` rows to `deferred-to`/`rejected`/`superseded-by` on a later customer round. Pre-batch-4 slices also exist whose specs and ARDs were authored without the test. M4 and §5.4 ("On a slice, stops unless …") stop `/create-ard` and `/specify` there although a PRD exists. `/create-prd` stops too (its step 7 precedes the existing-PRD question). `/update-prd` does not stop (`update-prd.md` applies §5.2 only to name `/create-prd`), nor do `/epics` and `/update-spec` (L5). The design does not decide whether that is intended, nor whether `/update-spec`'s carve-out (L5) is restated for the ledger (§5.1 says "Batch 4 does the same"). **Recommendation (mine):** put it to the maintainer as the batch's one behaviour question; the design's text answers "stop", and the cost is a refused refine of an existing ARD or spec on a slice the customer has since emptied.

4. **`/brd-reconcile`'s advance array can fall to one option.** With all three authoring commands dropped on a failing ledger, `["Stop here …"]` alone violates escalation-rules §0 and check 12, which only sees literal arrays. REC already names the rule for its other list (REC:3149–3150). The design is silent. INT's not-eligible array keeps two (Stop and re-ground).

5. **The two conditions are not independent in `/brd-interview`.** Its gate already refuses any `unallocated` row, so "the ledger test" there equals "PRD-eligible". The two arrays collapse to "eligible: three authoring options" / "not: none". The landed-`prd.md` condition needs a read neither INT nor REC makes today: INT holds §4.4 through its `require-on-main` file; REC requested that file in Phase 0. That read is model on RN:830–832, with its row-G, unmanaged, unset-`$SPECS_PATH` and outside-tree cases.

6. **§5.2 and CPRD disagree on one ledger-less state** (§2 (c)): `claims:` empty and no ledger. §5.4 bullet 2 asks for one statement; the plan must pick one wording, and CPRD:333–334, ARD:1086/1088 and SPEC:1454/1456 follow. §5.2 also lacks CPRD's re-cut instruction form and the `/prd-ground` note, so "stated whole" is not yet true.

7. **§5's name.** Every word of §5 and §5.2 is about a PRD ("PRD eligibility", "author its own `prd.md`", "Offering `/create-prd`"). ARD:538 and SPEC:775 build their refusal-to-check on that wording. **Recommendation (mine):** keep the section number and test, and add one sentence naming `/create-ard` and `/specify` as consumers of the same two tests on a slice — CLF:508–524 is the model for a consumer list. Do not rename §5: 50 sites cite it by number — 14 for the eligibility test and 15 for §5.2.

8. **Placement in Phase 0 is undecided.** It must come after the container refusal and placement (CLF §5: level test first), after the preflight (it reads the working tree a stale branch would hide), and before the advisory (ARD:428) and every Phase 1 question. Its order against *Gate the PRD* and *Gate the decision register* is open. CPRD's precedent is ledger before register (CPRD:377–381), so a slice "that holds no PRD of its own is told that first". Placing it inside *Gate the PRD* or *Gate the decision register* drags it into `/update-spec` by citation (`update-spec.md:57`).

9. **Further states the design's tests do not decide:**
   - an Epic under a slice: tested on `prd_dir`, the stop's re-run naming `<ADDRESS>` = the Epic, the remedy naming the slice's key (`/brd-split <SLICE-KEY>`);
   - a legacy unprefixed slice: placed as `PRD-` by `brd-link.md` naming `parent:` (ARD:89–91), so the test applies;
   - an unmanaged tree (L7): moot for the ledger, which is read from the working tree on every tree (CPRD:372), but `/brd-split` remedies there name no merge;
   - a `--sent` REC run: the ledger may be absent;
   - an Epic-level `/specify` whose Step B Epics are under a slice: the test runs once in Phase 0, on `prd_dir`.

10. **What the design calls "the slice form of `CREATE_ARD_PRD_NOT_HANDED_OFF`"** applies to the uncommitted form only (ARD:322, SPEC:365). In the committed form a register committed on the same branch lands with it. One remedy for the uncommitted case would add `decisions.md`'s `add -f`/`commit` paths beside `prd.md`'s; b1 kept them apart "since the stop cannot tell whose change the register holds". The register stops' own "Ignored … the stop for a register on a branch" clause (CPRD:412, ARD:385, SPEC:425) is false for a register committed on a non-plugin branch: that is row F again.

11. **The design's id grep misses a stop.** `BRD_PACKAGE_ROUNDS_NOT_ON_MAIN` (two messages, `brd-package.md:367`, `:466`) is a row-F-in-folder stop without the committed form. Most BRD-route stops also lack parts 2 and 4 of PH §4.4's contract (§6). Several land more than one file, so one HEAD test does not choose the form for all of them. `BRD_SPLIT_NEEDS_GROUNDING` and `BRD_INTERVIEW_NEEDS_GROUNDING` never split row F on a file in the folder (§6, last paragraph) — the L1 class, outside the design's list.

12. **Budgets constrain where text can go.** `CLAUDE.md` has 22 characters left; `docs-workflows.md` 2, `dev-workflows-implement.md` 9, `dev-workflows.md` 239. The rules-file map lines (`brd-route.md:32`, 1,609 left; `product-workflows.md:42`, `:45`, 2,229 left) can take the ledger stop. The coupling file (497 left) needs bullets moved to history-4 (2,162 left) before a batch-4 bullet fits.

13. **Diagrams draw offers batch 4 removes.** `workflow.md:106–109` and `brd-workflow.md:72–75` draw them. If the stop's remedy is still drawn — the stop naming `/brd-split <SLICE-KEY>` or `<PARENT-KEY>` — the edges can be relabelled as the stop's remedy rather than deleted. A plan decision: `workflow.md:141` says the diagram draws offers.

14. **One noun.** The design says "the coverage-ledger tests", "the ledger tests", "`/create-prd`'s tests", "the two data refusals", "PRD eligibility". The tree adds "the gate set", "PRD-eligible", "the eligibility test". Refinement 8 asks for one noun across every copy. **Recommendation (mine):** "the slice's ledger tests", defined once at CLF §5.

15. **Release.** Every plugin above changes. `workflows-core` changes if PH or NPO does; a command citing a new §4.4 rung needs a coupling bullet naming the `workflows-core` that holds it, in both directions where the older side misleads. Versions must be re-derived at release: `main` moved twice during batch 3 (b3 R11's renumbering).

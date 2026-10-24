<!-- Copied unchanged from lean context D's SDD workspace (W/worse-small.md), a read-only Opus investigation run after the first live runs, preserved by Ruling 23 so every fix it recommended or refused keeps its argued evidence. The paths it names under .superpowers/sdd/ and .worktrees/ were scratch and are removed after the merge; paths under ~/ or /home/<user>/ are on the maintainer's machine; /tmp/.../scratchpad/ paths were session scratch. Where it and the shipped text disagree, the shipped text is the authority. Companion to 2026-10-22-lean-context-handoff-part.md. -->

# Small defects in the D/P1 live runs: where the text lets them happen

Read-only investigation of WT (`.worktrees/lean-context-handoff-part`). Transcripts are under `~/.claude/projects/-workspace-e2e-bookstore/`. Verdicts are under `~/e2e-live/lean-context-D/`. All line numbers are WT's.

**Variance under unchanged text.** None of the governing text changed between P1 (`0f68a91e`) and WT. `git diff 0f68a91e HEAD` touches `implement.md` (the question-rules load only), `code-handoff.md` (an `owner-repo` citation), `scan.md` (the question-rules load) and `conformance.md` (rule 3). It does not touch `session-hygiene.md`, `next-phase-offer.md`, `finding-triage.md` or `implementation-format.md`. So each defect is one the text permits on either revision. Several recur on both sides once you look past the one run the judge flagged.

## Ranked fix list

| # | Fix | Where | Class | Recommend |
|---|---|---|---|---|
| A | The resume pointer carries every item the old pointer held that this run did not settle | `session-hygiene.md` §1 (template line 82 + one paragraph), plus 2 docs copies | rule gap, invited by "the next phase needs" | **yes** |
| C | `workitem_key` is the folder's frontmatter field, `null` when absent; a trailer is never copied from the log | `implement.md:172-175, :308`; `code-handoff.md` §2.11 row (:263) and §2.3 (:99-105); same phrase in `vuln.md:273`, `upgrade.md:225` | invited by the text + placement | **yes** |
| B | "The remaining Epics" is resolved to keys and ordered by the ARD's `### Landing order` | `next-phase-offer.md` contract (new paragraph by rule 2/5) + the lane lines `:322/:324/:326` and their copies | rule gap, invited by the template's fixed order | **yes** |
| D | After a report composed before the tail, print only the tail's own lines: no recap, no second `Code repo:` | `specs-repo-git.md` §4 step 7 (:855) or §7 rule 3; `implement.md:1371` and the false invariant `:1407` | rule ignored, rule misplaced and self-contradicted | **yes** |
| E | The re-triage note's trigger covers a `### Declined to judge` line ruled a defect, and only that, with step 5's grade | `implement.md:240` and `:975` | rule gap | yes (small) |
| F | Conformance evidence-citation relevance | `conformance-tracer.md:27` | judgement variance | **no** |

---

## 1. The resume pointer drops open carry-forward items (fix A)

### Origin

**Design D (`3a0d7096`).**
- The run read the part file `reference-parts/session-hygiene/resume-pointer.md` at 17:21:19 and the existing pointer at 17:22:16 (`cat $S/resume.md`). The old pointer carried five carry-forward lines, among them:
  - "Still open from /epics: alerts' dev and Kubernetes ports …; whether alerts joins ingest's config/version fan-out; [SM#1]'s measurement source; requests naming the client current at send time."
  - "ARD omissions still open … — /product-workflows:create-ard BOOK-1 refine pending; … /product-workflows:update-prd BOOK-1 pending (follow-ups.md)."
- At 17:23:33 it wrote a pointer with four new lines. Of the five old ones it kept only what its own design settled: the ports, now answered. The PM's pending `/update-prd`, the PA's refine for the ARD omissions, the config/version fan-out question, [SM#1]'s source and the client-at-send-time question were all dropped.
- P1 (Y) kept them under "Still open from earlier phases".

**Scan P1 (`796118d3`).**
- It read the old pointer at 18:50:59, inside a listing of the PRD's Epics.
- At 18:52:40 it wrote one carry-forward line, "Landing order: ratings before web". It dropped "The [AD#4]–[AD#7] Rules were traced web-side only on this Epic; their ratings half belongs to BOOK-2-01-01 and the PRD run". The scan changed nothing about that decision.
- Scan D (`afedd011`, 11:58:59 read, 11:59:05 write) kept both lines.

**The same class on the other side of every pair:**
- Both scan runs dropped the old pointer's open *Next step* items: push the unpushed `conformance/BOOK-2-01-02-…` branch; merge #15 → #13 → #16 (ratings before web); re-run `/dev-workflows:conformance BOOK-2-01-01` to settle [DD#1]–[DD#6]. Neither checked whether any of them was done.
- Both route-3 runs dropped "Landing order is unchanged" (route-3 verdict §3).

That makes at least six pointer writes across four runs that lost a live item. It recurs.

### Governing text

`session-hygiene.md:72-83` (the `resume-pointer` part):
- `resume.md` is "a **"last known position" pointer, OVERWRITTEN each run** (NOT an append log)". It is "intentionally tiny".
- Line 82: `- **Carry-forward decisions:** <0–N one-line decisions the next phase needs that are NOT already in the artifact; 'none' if none>`.

Nothing tells the run to read the pointer it overwrites, or what to do with the old pointer's open items. The pointer is **one file per PRD folder** (`:67`), overwritten by every run of every Epic and every role. The filter "the next phase needs" is phase-scoped. So it actively licenses dropping an item that belongs to another role (PA refine, PM `/update-prd`) or to another Epic (BOOK-2-01-01's conformance re-run). Design D's `/implement` does not "need" the PM's `/update-prd`, and the overwrite then deletes it from the only place that held it as a pending step.

**Class: rule gap, invited by the phase-scoped filter.** Placement is not the problem: every command writes the pointer only through this part (`design.md:510`, `implement.md:1352`, `scan.md:541`, …), and design D had it in hand when it wrote.

### Fix

Change `session-hygiene.md` §1:
- **Line 82:** the line holds what the next phase needs, **plus every item the pointer being overwritten carried — its carry-forward lines and any open item of its *Next step* the new *Next step* does not name — that this run did not settle.** An item this run settled is dropped, or kept as one line saying it is settled. An item already recorded in a file the next run reads (e.g. `follow-ups.md`) stays as one line pointing at that file.
- **One paragraph after the template:** *Read the pointer you overwrite first.* It is the PRD folder's single file, written by every Epic's and every role's runs, so an item in it may be another Epic's or another lane's. The overwrite replaces the position, never an open item. Keep each item to one line.

Would it have prevented the defects?
- **Design D and scan P1: yes.** The dropped lines were unsettled by those runs.
- **Both scans' dropped *Next step* items: yes.** They would have been carried as open items. The rule does not require proving them still open; the run carries what it cannot see settled.

Sentences this touches:
- `:72` "OVERWRITTEN each run (NOT an append log)": stays true, because items are carried, not logged.
- `:73` "intentionally tiny": keep it, but it now rests on one line per item and on dropping settled items. Say so.
- The verbatim copies of the template line and the overwrite sentence must change with it (refinement 8): `dev-workflows/docs/reference/resume-and-checkpoints.md:7, :16` and `product-workflows/docs/reference/resume-and-checkpoints.md:7, :16`.
- `scan.md:541`, which names a worktree 7.4 failed to remove in the line: still consistent.
- Regenerate `reference-parts/` after the edit. Never edit the part.

**Would not do:**
- Make `resume.md` an append log. It grows without bound, and §1/§5 are built on one current position.
- Copy the rule into each command. That breaks `specs-repo-git` §7 rule 4's style: one owner, cited.

---

## 2. A scan's next step says "the remaining Epics" against the landing order (fix B)

### Origin

**Scan D (`afedd011`).**
- At 11:57:13–11:57:22 it loaded `next-phase-offer dev`, `session-hygiene index`, `guidance` and `resume-pointer`, then wrote the report. Its `### Next step` reads:
  - "**Dev:** take the `feat/BOOK-2-01-02-storefront-ratings` pull request through review and merge … **Dev:** then finish the remaining Epics of `BOOK-2-01`."
- It did not read the old pointer until 11:58:59, after the report. It never listed the PRD's Epic folders and never read the ARD.
- Its pointer's *Next step* copies the report ("Then the remaining Epics"), while its own carry-forward line says "ratings before web". BOOK-2-01-01 (target `bookstore:ratings`) was unmerged.

**Scan P1 (`796118d3`).** At 18:50:59, before composing, it listed `EPIC-*/` folders with their implementation blocks and read the old pointer. Its report names "the remaining Epic BOOK-2-01-01, including its own `/security-workflows:scan BOOK-2-01-01`" and "landing after the BOOK-2-01-01 ratings work, ratings before web".

**The same template on the implement side.** Route-3 D named the sibling ("BOOK-2-01-01 is implemented, but its branch is not merged"). Route-3 P1 printed a raw `<SIBLING-EPIC>` placeholder (verdict §4, from the `implement.md:1289` Context-hygiene template).

### Governing text

- `scan.md:494` (*after a change scan*): "…the pull request's review and merge … — then the remaining Epics, then the PE's `/dev-workflows:conformance <PRD-KEY>`".
- The same phrase and the same fixed order appear in:
  - `next-phase-offer.md:326` (scan), `:324` (Epic conformance) and `:322` (implement: "then finish remaining Epics (breadth)");
  - `conformance.md:473`;
  - `security-workflows/docs/commands/scan.md:167`.
- Rule 2 (`next-phase-offer.md:52`) says an offer "names the concrete command(s)". Yet the lane line itself writes a bare phrase with no command and no keys.
- Rule 5's breadth branch ("the SAME command for the NEXT Epic", `:66-75`) applies "to the per-Epic commands only: create-ard, specify, design, implement", so it does not reach scan or conformance at all.
- Nothing ties the order to the ARD's `### Landing order` (`product-workflows:ard-format`, `ard-format.md:70`). Here that section exists: `bookstore-specs/…/PRD-BOOK-2-01-verified-ratings/ard.md:135-139` lists orders, ratings, web.

**Class: rule gap, invited by the text.** The template hands the run a literal phrase in a fixed order: this Epic's merge first, then the rest. Copying it literally (D) is following the text. P1 went beyond it.

### Fix

Add one paragraph to the `next-phase-offer.md` contract part, beside rule 2 or rule 5. It reaches `/implement`, `/conformance` and `/scan` through the `dev` part, which needs `contract`.

> **The remaining Epics are named.** Where a lane line says "the remaining Epics", the printed offer lists each other `EPIC-` folder under the PRD by key, with its next command and the state the run can see (no implementation record; implemented, not merged; or "could not tell"). It orders them, and this Epic's own merge, by the ARD's `### Landing order`: each Epic's `target:` is looked up in that ordered component list. Where that order puts a remaining Epic's target before this Epic's, the offer says this Epic's pull request merges after that one. Where there is no ARD landing order, there is no asserted order.

This resolves against known sets: the folder listing, each `epic.md`'s `target:`, and the ARD's list. It never parses "ratings before web" out of a carry-forward line.

Then change the ordering phrase in each lane copy so the copies do not contradict the rule: "…the pull request's review and merge, and the remaining Epics', in the ARD's landing order". The copies are `next-phase-offer.md:322, :324, :326`, `scan.md:494`, `conformance.md:473` and the docs copy at `security-workflows/docs/commands/scan.md:167`. A rule plus untouched copies in fixed order would be two live instructions.

Would it have prevented scan D's defect? **Yes.** The run would have listed BOOK-2-01-01, read the ARD's order and printed it ahead of the web Epic's merge. The resume pointer's *Next step* copies the report, so it is fixed too. It also removes route-3 P1's raw `<SIBLING-EPIC>`, since the Next step must name keys.

**Would not do:** read the landing order from the resume pointer's free text. That is parsing an identifier out of prose, which `CLAUDE.md` § Editing discipline forbids.

---

## 3. `/dev-workflows:implement` route 3, D run (`b931a312`)

### 3a. An invented `Work-Item:` trailer (fix C)

#### Origin

1. At 12:57:05 the run read both Epics' `epic.md` heads. The frontmatter holds `kind`, `key`, `target` and `kept_whole`, and **no `workitem_key`**.
2. At 12:57:59 it created the run-state file with `"unit_key":"BOOK-2-01-02","workitem_key":"BOOK-2-01-02"`.
3. Only afterwards did it read `code-handoff.md` §2.3 (12:58:14) and `implementation-format.md` §3 (12:58:40, "Never invented; the trailer is simply absent when the field is").
4. At Phase 4.6 (14:22:59) it opened run-state, printed `workitem_key` (`BOOK-2-01-02`) and printed `git log -1 --format=%B eb694d0`. That message ends `Work-Item: BOOK-2-01-02`, written by the baseline run.
5. Its commit carries `Work-Item: BOOK-2-01-02` (`route3/blind/X/commit-message.txt:23`).

**P1 (`586ecaf9`) wrote the same wrong value at init** (21:21:11, `"workitem_key":"BOOK-2-01-02"`), but its commit omitted the trailer. So run state was wrong in **both** runs, and two of three commits on this Epic (baseline `eb694d0`, D) carry the invented trailer. It is systematic, not variance.

#### Governing text

- `implement.md:172-175`: "into run-state `unit_key`, `workitem_key` and `unit_folder` at Phase 1.4 … Its `workitem_key` is that same folder's."
- `implement.md:308`: "`focus_key`, `unit_key` and its `workitem_key`".
- Neither says *frontmatter field*, nor `null` when absent. "Its `workitem_key`" reads naturally as the unit's key.
- The rules that do say it, `implementation-format.md:151-152` and `code-handoff.md:99, :105`, are loaded only **after** init (12:58), so placement is wrong for the moment the value is set.
- Phase 4.6 then trusts run-state by design: "acts on its keys, never on memory", `:1166`.
- `code-handoff.md:101` ("Everything the convention leaves open comes from the repository … match what [the log] shows") invites copying the log's trailer as well as its style.
- `vuln.md:273` and `upgrade.md:225` use the same loose phrase "from the folder", and the §2.11 row `code-handoff.md:263` says "that unit's folder's `workitem_key`, or `null`".

**Class: invited by the text, plus a placement gap.**

#### Fix

- **`implement.md:172-175`, with the same words at `:308`:** "`workitem_key` is the value of the `workitem_key:` field in that folder's own document frontmatter (`workflows-core:prd-format`), `null` where the field is absent, as it usually is; never `unit_key` or any other key."
- **`code-handoff.md` §2.11 row (`:263`):** the same definition, so `/vuln` and `/upgrade` read it too.
- **`code-handoff.md` §2.3 `:101`, one clause:** "the log decides the subject's style, never the trailers: `Work-Item:` comes from the `workitem_key` input alone."

Would it have prevented the defect? **Yes.** At init the run had just read a frontmatter with no such field, and the definition at that point would give `null`. Phase 4.6 then writes no trailer whatever `eb694d0` carries.

Sentences to re-read: `vuln.md:273` and `upgrade.md:225` become consistent through the §2.11 row. `docs/reference/commit-convention.md:53` is already right.

**Would not do:** have `run-state.py` reject `workitem_key == unit_key`. That is a pattern guess, not resolution against the field.

### 3b. A closing recap with a false "four files" claim and a second `Code repo:` line (fix D)

#### Origin

- The Phase 5 report (`route3/blind/X/user-visible-text.md:270`) correctly says "The three non-test files are now byte-identical to … `eb694d0`" and prints `Code repo:` once in `### Branch`.
- After Phase 7's tail, at 14:27:22, the run's final message is a free recap. It says "The four files are now byte-identical to the reviewed Epic commit `eb694d0`", which is false: the spec file differs. It repeats `Code repo: <commit> … — not pushed at your request.` just before `Specs repo:`.
- P1 printed the report, then `Session cost:`, then `Specs repo:`, with no recap.

**The same pattern elsewhere.** Both scan runs printed a closing recap after their report. Scan D's recap carries the judge's defect X2: "Not covered: … did not look at the server-side ratings service … A whole-repository scan would cover those", a claim the run cannot know and a wrong route. The defects sit in the recap, the part the user reads last, and not in the report.

#### Governing text

- `implement.md:1172`: emit `Code repo:` "in the Phase 5 report's `### Branch` section — once, and verbatim".
- `implement.md:1407`: "ALWAYS produce the Phase 5 report as the final output". That is **false as written**, because Phase 7 prints `Session cost:` and then "its §6 outcome line here, as the run's last output" (`:1369-1371`). A rule the command itself breaks reads as loose.
- `scan.md:541` asks only that `Specs repo:` be the last output.
- `specs-repo-git.md` §6 (`:986-991`) lets the line sit "as its own terminal block where the report was composed earlier", and says nothing about what else that block may hold.
- Nothing at the moment the last message is written (Phase 7 / §4 step 7) forbids a restatement.

**Class: rule ignored; the rule is misplaced (an invariant at the bottom) and contradicted by the command's own Phase 7.**

#### Fix

- **Family-wide, in `specs-repo-git.md` §4 step 7 (`:855`), or §7 rule 3 (`:1044`).** Every family command executes it as its last step, so it is read at the moment it applies: "Where the run's report was printed before the tail, the run's last message holds only the tail's own lines — the follow-up and cost lines and this outcome line, last — never a summary or restatement of the report and never its `Code repo:` or `Phase handoff:` line again: the report is the run's account."
- **Rewrite `implement.md:1407`** to that true statement.
- **Reconcile the same "final output" invariant** in `document.md:1500, :1957`, `epics.md:1146` and `docs-profile.md:301` (refinement 8).

Would it have prevented the defects? **Yes** for both route-3 D defects and for scan D's "Not covered" claim. The cost is that the user's last screen is the tail lines, with the report above. If the user wants a closing paragraph, the softer variant is "at most one line pointing to the report, stating no fact the report does not". It is weaker, because a model restates.

### 3c. A [SEC#2] re-triage note with no severity, against its own ruling (fix E)

#### Origin

- At 14:05:12 `code-review` set [SEC#2] aside under `### Declined to judge`, noting for the security reviewer that line 70 "only tests that the value is non-empty".
- At 14:05:59 triage ruled the line "**stands** — outside this task and this diff".
- At 14:18:28 the run nevertheless wrote the re-triage note: "…and this run's review disputes it — …:69-71 … **set aside ungraded** under Declined to judge; a grep of web/src finds nothing that sets returnUrl…". There is no severity, and the note contradicts the "stands" ruling.
- P1 ruled the same line a **defect, MAJOR by effect**, under `finding-triage` step 5, and wrote the note with location and severity.

#### Governing text

- `implement.md:240` triggers the note only where "a finding Phase 3B step 7's triage keeps or marks unverified names that `[SEC#n]`". The template needs "<the finding, by its location and severity>". `:975` repeats the trigger.
- `code-review.md:111-121` expects `[SEC#n]` "in `### Declined to judge` or in a finding".
- `finding-triage.md:121-124` (step 5) rules a set-aside line "stands" or "defect … with its grade by effect".
- The trigger covers neither step-5 outcome. Both runs met that case and resolved it differently.

**Class: rule gap.**

#### Fix

At `implement.md:240`, and the same words at `:975`, widen the trigger to "a finding triage keeps or marks unverified, **or a `### Declined to judge` line it rules a defect** (`finding-triage` step 5), names that `[SEC#n]` — the note giving the grade step 5 recorded". Add: "a line that stands writes no note: this run did not dispute the ruling".

Would it have prevented the defect? **Yes.** D would have had to choose: "stands", which writes no note, or "defect", which writes a note with a grade. Either result is consistent.

Sentences to re-read:
- `:1315` ("its re-triage note, where this run's review disputed the ruling"): still true.
- The docs page `dev-workflows/docs/commands/implement.md:69` ("where its review disputes that ruling, the report says so"): still true.

---

## 4. `/dev-workflows:conformance` re-run, D (`c34bb2f1`) — no fix (F)

### Origin

The citations are the tracer's own (subagent `agent-a53429e6…`, `conformance-tracer`).

**The books delete.** For [U06]/[AC02] ("The storefront shall send the ratings service no removal request … from any screen") it returned:
- `shipped`: "RatingService has only GET, POST and PUT. `git grep -i delete` over web/src/app/ratings … found nothing, and the book list's deletes go to BookService."
- `evidence`: `RS:42-98@eb694d0, BL.ts:39-64@eb694d0`.

So the "irrelevant" books-delete citation is the place it checked to rule out a look-alike on another screen. "From any screen" is in the requirement.

**The "weaker" citations.** The `book-details.component.html:27-29` citations for "other details as usual" are the prior record's own (`prior-record.md:48`).

### Governing text

`conformance-tracer.md:27`: "`file:line@<commit>` for each place you relied on". The tracer did rely on that place.

**Class: judgement variance.**

### Fix

**None recommended.** Narrowing "evidence" to "the lines that do what the requirement says" would strip the negative evidence a "from any screen" requirement needs. The weak citations are inherited, not introduced. The judge rates the item low and all 88 verdicts are correct.

---

## Recommendation summary

**Do A, C, B, D, E, in that order.**
- **A** is recurrent across both revisions and loses cross-role pending work.
- **C** is systematic: wrong in run state in both runs, and invented in permanent history twice.
- **B** gives merge-order advice that, followed literally, ships the consumer before its producer.
- **D** removes the message where three of the false or duplicated statements sat.
- **E** is a one-clause trigger widening.

**Do not do F.**

**Bumps and regeneration:**
- A, B and D touch `workflows-core` references. Regenerate `reference-parts/` for `session-hygiene` and `next-phase-offer` after editing their sources.
- C, D and E touch `dev-workflows`.
- B touches `security-workflows`: `scan.md:494` and its docs page.

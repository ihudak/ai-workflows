# GIT-G1 audit — group A

Read-only, `main` at `4fef611b`. Paths are under `plugins/`; `SRG` = `workflows-core/references/specs-repo-git.md`, `PH` = `workflows-core/references/phase-handoff.md`, V-ids and §-numbers are the contract's (`gitg1-contract.md`). Class: **R** reference-defined, **P** purposeful (reason quoted), **D** drift, **U** unclear.

Cross-cutting facts used below, checked once:

- **`inputs_read` is named by no command in the family** (`grep -c inputs_read plugins/*/commands/*.md` → 0 everywhere). PH §2.9 (`PH:215–224`) lists six inputs, `inputs_read` the sixth, "recorded as it reads, so a compacted context still holds it"; §2.2's stack test reads it (`PH:77`), and PH names `/dev-workflows:design` on an open `epics/` branch as the stacking case it exists for. It was added after the producers were written (`workflows-core/CHANGELOG.md:920`). `/frames` and `/idea` still say "all five of its §2.9 inputs".
- **The restated `commit-artifacts` skip clause has three extents.** SRG §4 step 1 (`SRG:722–729`) names four setters of `misrooted`: §3.1's notice, `specs-root-check`'s stop, SH §7 `env-check`, SH §6 *Stop*. `/design:638` restates all four; `/feedback`, `/prompt`, `/prompt-brainstorm`, `/prompt-grill-me`, `/frames`, `/ready`, `/implement`, `/upgrade`, `/vuln` say "(§3.1, or `specs-root-check`'s stop)"; `/diagnose-session:80` says "(§3.1)". The skip is keyed on the flag, not the setter, so no run behaves differently today — a narrower gloss, not a bug. `/conformance` and `/scan` restate nothing (they only cite) and are the model.
- **No command in this group states which single key the `commit-artifacts` subject takes on a two-key run** except `/implement` (run-state `key`, `implement.md:1471`). SRG leaves it open (contract §8.4).

---

## workflows-core/commands/feedback.md

| where | part | cls | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|
| :30–37 | start | R | V1.1, V1.3, V1.4(c) | Preflight-first, with no address; bookkeeping-only, runs on with `$SPECS_PATH` unset | an empty key set |
| :30–37, :69 | start | U | V1.3 | The key set is never stated. The note's `key` is resolved later, "from recent context" (:69), so the preflight is keyless by default and SRG §3.5 B4 switches the checkout off any unmerged plugin branch the user stands on. Only `/diagnose-session` says "empty run key set" | settle: whether a logging command passes the key it already holds from context at its call site (SRG §3.2 "each key already resolved at the call site"), or stays keyless; state it either way |
| :98–104 | end | R | §3.2 last ¶ | Commit key is Phase 2's `key`, resolved after the keyless preflight | `key` at the end call |
| :92–96 | end | R | tail | Tail is feedback → cost → commit (no follow-ups or `resume.md`) | tail members optional |
| :104–111 | end | R | 2.1 placement | Line held for the Phase 4 report | return the line, don't force-print it |
| :104 | end | D | — | Narrower setter list (above) | delete on switch |

Restated rules: :31–37 preflight gloss (flush/retry/settle, §1 rule 1, prompt-free, guard notice, carry flag) — same extent; :99–104 commit gloss — narrower setters; :92–96 tail order (SH §5) — same extent; :113–116 never-commits — same.
**Verdict: ready** (the U is about behaviour today, not the switch).

## workflows-core/commands/prompt.md

| where | part | cls | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|
| :30–37 | start | R | V1.1, V1.3, V1.4(c) | As `/feedback` | empty key set |
| :30–37, :51–54 | start | U | V1.3 | Keyless by default (key set unstated), then Phase 2 **edits the files it corrects** (:53). Right after a producer's handoff the checkout stands on that producer's unmerged `spec/…`-style branch (PH §2.3 leaves HEAD there); B4 switches to `<default>` and pulls, so the correction lands on the default branch's copy — or on a file that isn't there — as uncommitted OTHER dirt, which G1 then reports on every later run. **Possible latent bug** | settle as for `/feedback`; here the cost of staying keyless is a misplaced edit |
| :91–98 | end | R | §3.2 last ¶ | Commit key from Phase 3's `key` | `key` at end |
| :86–89 | end | R | tail | feedback → cost → commit | optional members |
| :102–105 | end | R | 2.1 placement | Line held for Phase 4 | return the line |
| :97 | end | D | — | Narrower setter list | delete |

Restated rules: as `/feedback` (:31–37, :92–97, :107–111).
**Verdict: ready** (settle the U before or after; the switch doesn't change it).

## workflows-core/commands/prompt-brainstorm.md

| where | part | cls | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|
| :25–32 | start | R | V1.1, V1.3, V1.4(c) | As `/feedback` | empty key set |
| :25–32 | start | U | V1.3 | Keyless by default; B4 as `/prompt` (the brainstorm may lead to edits after the cede) | settle as `/feedback` |
| :100–108 | end | R | V2.1 | `commit-artifacts` runs before Phase 3 cedes the session; line printed there | end call usable mid-run as the last output before a cede |
| :69–98 | end | R | V2.1 / tail | Cost is a deferred `cost-emission` §13 intent record, written before the commit, no `emit-cost` | tail member variant |
| :108, :116–120 | end | P | — | After the `Specs repo:` line, Phase 3 prints the absent-skill message in place of the hand-off. Reason: "never a hand-off that will not happen" (:58); SRG §4 step 7 allows "any line the command names to follow it" | the end call must not assume it prints last |
| :107–108 | end | D | — | `Run flags:` line repeated **after** the `Specs repo:` line ("here too"), where `/feedback:109` and `/prompt:102` print it before. Both orders are allowed by SRG §4 step 7; it's an ordering difference with no stated reason | pick one order when the line is returned to the caller |
| :107 | end | D | — | Narrower setter list | delete |

Restated rules: preflight gloss :26–32; commit gloss :101–107 (narrower setters).
**Verdict: needs option** — V2.1 (already in the contract) plus a caller line after the outcome line.

## workflows-core/commands/prompt-grill-me.md

| where | part | cls | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|
| :29–36 | start | R | V1.1, V1.3, V1.4(c) | As `/feedback` | empty key set |
| :29–36 | start | U | V1.3 | Keyless by default; the grill's "confirmation gate before the fix is acted on" (:114) can lead to edits after a B4 switch | settle as `/feedback` |
| :93–102 | end | R | V2.1 | Commit before the Phase 3 grill | as brainstorm |
| :62–91 | end | R | V2.1 / tail | Deferred §13 cost record | as brainstorm |
| :101–102 | end | D | — | `Run flags:` after `Specs repo:` (as brainstorm) | one order |
| :100 | end | D | — | Narrower setter list | delete |

Restated rules: preflight gloss :30–36; commit gloss :94–100.
**Verdict: needs option** — V2.1.

## workflows-core/commands/diagnose-session.md

| where | part | cls | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|
| :27 | start | R | V1.1, V1.3, V1.4(c) | Says outright "with an empty run key set" — the only logging command that does | empty key set |
| :76–80 | end | R | tail | cost → commit, no feedback emitter, no follow-ups or `resume.md`; subject fixed `NOISSUE` | optional members |
| :102 | end | R | 2.1 placement | Line in the Final report | return the line |
| — | end | R | SRG §7 rule 2 | No **Ending early.**: no stop is stated (`session-diagnosis.md` §2 names none; only `--skip-costs` applies) | none |
| :80 | end | D | — | Setter list "(§3.1)" only — the narrowest in the group | delete |

Restated rules: preflight gloss :27; commit gloss :80.
**Verdict: ready.**

## workflows-core/commands/frames.md

| where | part | cls | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|
| :79–86, :136–141 | start | R | V1.1, V1.2, V1.3 | Resolve-first; key set = resolved key + an Epic's parent; address stops run none | key set incl. Epic parent |
| :43–52 | start | R | V1.4(a) | Unset `$SPECS_PATH` stops before resolution | — |
| :88–116, :143 | start | R | PH §6 order | `branch-check` (`prefix: frames`) after the carrier and kind refusals, as PH §6 asks | — |
| :336–355 | handover | P | V3.12 (extends) | Offers **no** handoff where every index it wrote already matches `<default-ref>` (`cat-file -e` + `diff --quiet`). Reason: "every answer the choice offers would end the same way" (:352) | a caller-side skip before the offer, and the "already on `<default>` as written" test §2.3 already uses, exposed as a check |
| :354, :498–501 | handover | P | V3.12 | On that skip it prints `Phase handoff: not offered — …`. Reason: "nothing was declined there, and §4.1 has no row for it" (:500). **Conflicts with `PH:463`**: "A run that never reaches an offer prints no line for it" | the step must allow a caller-owned not-offered line — or PH gains a *Not offered* row; one of the two texts has to change |
| :357–358 | handover | R | V3.1, V3.3 | Advisory, cited with its class named | — |
| :359–363 | handover | D | — | "with **all five** of its §2.9 inputs" — §2.9 has six. Right: PH §2.9. **Latent bug**: read literally, the stack test sees only the indexes, never the frame images `frame-describer` read — a frame set added on an open branch gets an index PR cut from `<default-ref>` without the images. Narrow | `inputs_read` as a required argument |
| :371–381 | handover | P | — | After a declining answer, prints what declining costs (G1 on every later run). Reason :373 "it is not free" | a caller hook after a declining answer, before or beside the step's own line |
| :349–350 | handover | R | V3.12 | No index written → no offer | — |
| :409–452 | end | R | tail | maintenance → feedback → cost → commit; no `resume.md` (SH §1 skip list), no follow-ups | optional members |
| :33 | end | R | V2.2, V2.5, PH §6.3 | Ending early: refusal tail, pre-preflight stops included | — |
| :448–451 | end | D | — | Gloss commits "`<KEY> Add …`" with no `NOISSUE`, though Ending early's address stops reach it with key `null`; narrower setter list | delete (SRG §4 step 4 decides) |

Restated rules: preflight gloss :137–141; commit gloss :447–451 (narrower, no `NOISSUE`); **:374–379 restates G1 as suppressing the flush and branch settle "for the rest of that session"** — SRG §3.3 (`SRG:398`) ends *that run's* preflight; each later run repeats it while the paths stay dirty. Wording overstates the extent; harmless, delete or fix.
**Verdict: needs option** — pre-offer skip + check, a not-offered line (after PH and `/frames` are reconciled), a post-decline hook, `inputs_read`.

## dev-workflows/commands/design.md

| where | part | cls | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|
| :52–60, :90–96 | start | R | V1.1, V1.3 | Resolve-first; Epic parent's key added; preflight before placement | — |
| :84–88 | start | R | V1.4(a) | *Set SPECS_PATH* question, taken before step 1 | — |
| :98, :127 | start | R | V5.1 | `reuse: later` with `<EPIC>` null, second call after step 4 | — |
| :105 | start | R | V4.3, PH §5 rule 2 | `require-on-main` on `specification.md`; `absent` → `DESIGN_NO_SPEC`; after `branch-check` | — |
| :538 | handover | R | §3.3 (SH §6 pt 2) | Run-environment comparison before the deliverable write; *Stop* → `misrooted`, hands nothing off | — |
| :538–540 | handover | P | — | Decision-completeness refusal and the lineage stamp before staging. Reason: "before anything stages it" (:540) | ordering only: caller does both before the handover call |
| :542–543 | handover | R | V3.1, V3.3 | Gated — stopping, quoted | — |
| :545 | handover | D | — | Parameters omit `inputs_read`. PH §2.2 names this command as the stacking case `inputs_read` exists for ("`/dev-workflows:design` reading the target an unmerged `/epics` refinement set"). **Latent bug**: read literally, the design PR is cut at `<default-ref>` without the `epic.md` refinement it was built on | `inputs_read` required |
| :547–554 | handover | D | V3.13 | The *Next Epic* loop runs "Phases 2–7" again, so one run offers a 2nd, 3rd… consent choice, handoff and `Phase handoff:` line. `PH:476–477`: `/brd-reconcile` "is the only such producer today; every other command … offers `handoff-to-main` at most once". `/design` labels no line, its Final report (:545) and `<merge-clause>` (:668) assume one, and the loop re-enters step 5 → Phase 1 step 2 → Phase 1.5 → Phases 2–7 (`dev-workflows/CHANGELOG.md:334`) but not step 4's `branch-check`, so §6.2's reuse question is never asked for the looped Epic. **Latent bug**: with an unmerged `design/<EPIC-2>…` branch, the second handoff's rule 3 switches onto it and git refuses (*Switch refused*) over the `design.md` this run just wrote. `/specify:1158` has the same loop shape (outside group A) | see *needs preparation* |
| :559, :30 | end | R | §2.3 (SH §6 pt 3) | Comparison before the tail, on a stop too; *Stop* → cost report-only, commit skips | a hook before the tail's first write |
| :556–639 | end | R | tail | maintenance → feedback → cost → `resume.md` → commit; no follow-ups | optional members |
| :634 | end | U | §8.4 | Subject `<KEY>`: on an Epic run, or a PRD address whose picker chose an Epic, the run holds two keys, and which one is unstated | settle by naming it, as `create-ard` does |
| :558 vs :629–630 | end | D | — | Phase 8 runs "before the Final report is presented" (and :639 holds the line for it), but Phase 9's resume step says the context-hygiene guidance "already appeared in the report". One sentence is wrong; it decides where the returned line is printed | pick the report-after-tail order :558/:639 state |
| :634–638 | end | D | — | Gloss "pushes the branch this run's handoff phase created" — narrower than SRG §4.1 (declined, stopped → default or G2 branch). Its setter list is the full four, the only one in the group | delete |

Restated rules: :91–94 preflight gloss; :96 "`require-on-main` performs no `fetch` of its own" (same extent as PH §3 opening); :633–638 commit gloss (narrower push target).
**Verdict: needs preparation** — make the *Next Epic* loop one handover per Epic: rerun `branch-check` (prefix `design`) on the looped Epic's folder before its work, label each `Phase handoff:` line, and say which line the report and `<merge-clause>` read — or end the run at the first handoff and offer the next Epic as a fresh command. Also pass `inputs_read`.

## dev-workflows/commands/ready.md

| where | part | cls | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|
| :47–55, :111–115 | start | R | V1.1, V1.3 | Resolve-first, Epic parent's key | — |
| :104–109 | start | R | V1.4(a) | *Set SPECS_PATH* question | — |
| :117–148 | start | P | PH §6 ¶1 | After the preflight, a clean-main test that re-implements SRG §2.1 step 1's `-z` parse and step 2's classifier, excludes session files in session-branch mode and its own `_readiness.md`, then asks. Reason: "a non-`main` or dirty checkout may show unmerged, in-flight artifacts as if they were the handed-off truth" (:142–143) | the §2.1 classifier (ARTIFACT/OTHER over porcelain `-z`) and the `mode` result, exposed |
| :150 | start | R | V5.4 | `branch-check` `prefix: ready`; a §6.1 stop recorded as a finding | — |
| :181 | start | R | V4.1, V4.2, V4.3 | `require-on-main` in Phase 1, every stop read without stopping, `absent` = missing | — |
| :481–525 | handover | P | — | Pre-handoff documentation and instructions agents, bracketed by porcelain + fingerprint reads; `maintenance_paths` joins `deliverable_paths`. Reason :481 (edits made after the handoff "fired §3.3's G1 advisory on every later run") | accept a caller-built path list |
| :527 | handover | P | — | Prints the declared edits "just above the array — before the one line §4.3 prints immediately above it" | a **caller slot before** the flag / no-remote line (contract §3.3's order has none) |
| :527–528 | handover | R | V3.1, V3.3 | Advisory, quoted | — |
| :530–533 | handover | D | — | `inputs_read` missing | required argument |
| :534–536 | handover | R | V3.7 | `-2`/`-3` suffix expected (restated) | — |
| :787–792 | end | R | SRG §4 step 7 | Line printed after the Phase 5 report, as last output | return the line |
| :645–792 | end | R | tail | Full tail: maintenance/feedback → follow-ups → cost → `resume.md` → commit | — |
| :788 | end | U | §8.4 | `<KEY>` on an Epic run (two keys) unstated | name it |
| :790 | end | D | — | Narrower setter list | delete |

Restated rules: :112–115 preflight gloss; :119–136 §2.1 parse/classify; :534–536 collision; :788–790 commit gloss (narrower); :824 invariant (same extent).
**Verdict: needs option** — the classifier and a pre-line caller slot.

## dev-workflows/commands/conformance.md

| where | part | cls | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|
| :43–52 | start | R | V1.1, V1.3 | Resolve-first; `@<path>` key read off its carrier; Epic parent's key | — |
| :50 | start | R | V1.4(a) | *Set SPECS_PATH* question | — |
| :54 vs :56–66 | start | D | — | `branch-check` runs **before** step 3's placement refusals (`CONFORMANCE_BRD_NOT_SLICED`, `CONFORMANCE_EPIC_FOLDERS`). PH §6 (`PH:610`) puts it after "the refusals that place the folder by its carrier", as `/design`, `/ready` and `/frames` do. No reason given. Minor latent: on a BRD container a branch-check stop (or §6.2's question) comes before the refusal that names the real problem | standardize to PH order |
| :68 | start | R | V4.3, PH §5 rule 2 | `require-on-main` on every document read, `absent` falls back | — |
| :70–87 | start | P | — | Record check: its own capped `fetch --prune` of `conformance/*`, `ls-tree`, `diff`, `merge-base`, `for-each-ref`, and SRG §3.5's `branch-merged` and `branch-key` called directly. Reason :70 (a stale record would renumber entries and "reuse or collide with the branch that holds the newer record") | expose `branch-merged <ref>` and `branch-key <branch>` (against the run key set) as callable primitives; output `<default>`, `<default-ref>`, `remote`, read-only mount |
| :98 | end | R | V2.2, V2.5 | Ending early sits in Phase 1, not at the top (position only) | — |
| :405–434 | handover | P | — | Pre-handoff maintenance (as `/ready`) | as `/ready` |
| :443–459 | handover | R | V3.1, V3.3 | Class = strongest of a varying set (annotated document → gated-stopping, else advisory), quoted | caller passes the class |
| :461–471 | handover | P | — | Caller lines above the array — the declared edits, then the `withdraws:` line — before §4.3's flag / no-remote line | caller slot before the line |
| :473–477 | handover | D | — | `inputs_read` missing | required argument |
| :581–613 | end | R | tail | Full tail; follow-ups per item's own `unit_folder` | — |
| :613 | end | U | §8.4 | Commit key on an Epic run (two keys) unstated | name it |

Restated rules: :52 and :613 cite only — no restatement.
**Verdict: needs option** — primitives and outputs (:70–87), a pre-line slot; fix the `branch-check` order.

## dev-workflows/commands/implement.md

| where | part | cls | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|
| :26–49, :76 | start | R | V1.2 | Session-model gate, cwd test, `IMPLEMENT_IN_SPECS_REPO`, token checks, no-description stop, design-doc guard — all before the preflight, which then runs none | — |
| :78–84 | start | R | V1.1, V1.3 | Resolve-first; keyed (Epic parent's key) or direct (keyless) | — |
| :56–61 | start | R | V1.4(a)(b)(c) | `<KEY>` asks *Set SPECS_PATH*; `@<path>` runs on; direct runs on | — |
| :76 | start | P | V1.13 | SBP `mode` called **before** the preflight on a direct run inside the specs repository, to word its notice. Reason: "its §8.1 `mode` call only reads, so it runs here, ahead of the preflight" | `mode` as a standalone read-only call (contract has it only inside §3.2 / §4 step 1) |
| :93–97 | start | P | — | Persists `specs_git` and the branch B2 found merged and left (`specs_merged_branch`) in run-state. Reason: the resume pointer reads it, "since … B2 may have deleted the only ref that showed it" | preflight **output** B2's left branch (contract §0.1 lists B4's, not B2's) |
| :99 vs :101–103 | start | D | — | `branch-check` before Epic-unit placement and `IMPLEMENT_BRD_NOT_SLICED` — the `/conformance` order departure; no reason. Minor (no `prefix`, so §6.1 only) | standardize to PH order |
| :99 | start | R | V5.2 | No `prefix`: "this command's own handoff is conditional, and onto prefixes it does not own" (PH §6.1 "exempts itself") — contract V5.2 omits `/implement` | add to V5.2 |
| :230 | start | P | V4.1 | `require-on-main` after the `focus_key` picker, a departure from PH §5 rule 2 stated with reason; every stop "naming `$SPECS_PATH` explicitly — `/implement` stands in a **code** repo" | stop wording that names `$SPECS_PATH`; add `/implement` to V4.1 |
| :391, :1256 | start/end | R | V1.13, SRG §8.2–8.3 | Direct run inside the specs repository: `lift` at the clean-tree check, `commit` + `lift` + `put-back` around Phase 4.6 | SBP `commit`/`lift`/`put-back` callable by the command |
| :1232 | handover | R | V3.12 | Silent no-op without notes, or on a direct run inside the specs repository | — |
| :1234–1242 | handover | R | V3.2 | Per-run array (stopping vs falling back, `cat-file -e` on `<default-ref>`); `prefix` `spec` or `design` by the set | caller passes class/half |
| :1244 | handover | D | — | `inputs_read` missing | required argument |
| :1244 | handover | P | — | "`handoff-to-main` (reads run-state `specs_git`)"; its line is written to run-state `conformance.handoff_line` for Phase 5 | accept flags from the caller's state; return the line |
| :1246 | handover | P | — | Placed after Phase 4, before Phase 4.6. Reason given (:1246, :1266) | ordering only |
| :1465 | end | R | tail | `resume.md` on keyed runs only | — |
| :1471 | end | P | — | `run-state.py remove` runs between `resume.md` and `commit-artifacts`, after `specs_git`, `key` and `session_branch_created` are read from it. Reason :1471 | the end call takes these as arguments, or keeps its own state file that `remove` doesn't touch |
| :1483–1484, :1520 | end | R | SRG §4 step 7 | Line printed last, after the Phase 5 report | return the line |
| :1475, :1482 | end | D | — | Gloss "`<KEY> Add …`" with no `NOISSUE` (direct runs are keyless); narrower setter list | delete |
| `dev-workflows/scripts/run-state.py:113–121` | end | U | §8.2 | The run-state file holds `specs_git`, but not the notice that set `misrooted`, the fired guard's §5 block, the `Environment:` line or `session_branch` — all read late (SRG §4 steps 1 and 7, SH §7 `env-check`, §8) in a run the rules say keeps "every fact a later phase … reads" in that file. Whether they survive compaction today is untested | settle by testing; the shared state file would hold them |

Restated rules: :87–93 preflight gloss; :1474–1482 commit gloss (no `NOISSUE`, narrower setters); :1517, :1520 invariants (same extent).
**Verdict: needs preparation** — specs-repo state is split between `run-state.py` and the conversation, and the shared step would add a third home. Decide who owns `specs_git`, `session_branch_created` and `specs_merged_branch`, and make the shared state outlive `run-state.py remove`. Then the options above: standalone `mode`, B2 output, `$SPECS_PATH`-naming stop text, SBP primitives, flags in and line out of the handover.

## dev-workflows/commands/upgrade.md

| where | part | cls | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|
| :32–36 | start | R | V1.1, V1.3, V1.4(c) | Preflight-first, keyless "never one derived from a branch name" | — |
| — | start | R | V5.9, V3.16 | No `branch-check`, `require-on-main` or handoff | — |
| :28, :259 | end | P | — | **No cost member**: the refusal tail "is step 10's `commit-artifacts` alone". Reason: `workflows-core/references/cost-emission.md:528` ("a decision about what the number is for") | an end call with no cost member (contract V2.2 assumes one) |
| :28, :240 | end | P | — | The stop message, then the step 7.6 handoff-file removal, come before `commit-artifacts` | caller actions before the commit call |
| :259 | end | R | tail | `NOISSUE` stated; no `resume.md` (SH §1); line last | — |
| :259 | end | D | — | Narrower setter list | delete |

Restated rules: :36 preflight gloss; :259 commit gloss.
**Verdict: needs option** — a tail with no cost member.

## dev-workflows/commands/vuln.md

| where | part | cls | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|
| :42 | start | R | V1.1, V1.3, V1.4 | Preflight-first; per-token keys via `read-key` or an `@<path>` carrier; an `@<path>` with `$SPECS_PATH` unset asks first | key set of several keys |
| :48 | start | P | V1.1 | "A folder Step 0 read a carrier from that the preflight has since switched off the checkout stops the run" — the preflight-first order's own consequence | ordering only |
| :49 | start | R | V5.2 | No `prefix`, once per distinct root | — |
| :22, :312, :361 | end | P | — | No cost member (as `/upgrade`); handoff files removed before the commit | as `/upgrade` |
| :361 | end | U | §8.4 | Subject "`<KEY>` … or `NOISSUE` when the run resolved no key", but a run of several `ADDRESS:CVE` tokens can hold several keys, and nothing says which (`emit-auto` at :359 has the same "the run's `key`") | settle: state the rule for a multi-key run |
| :361 | end | D | — | Narrower setter list | delete |

Restated rules: :42 preflight gloss; :361 commit gloss.
**Verdict: needs preparation (small)** — define the one commit key on a multi-key run; the shared end call takes one key. Then the no-cost option.

## security-workflows/commands/scan.md

| where | part | cls | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|
| :91–93 | start | R | V1.1, V1.3, V1.10 | Resolve-first; a repository path is keyless; `register_rebuild` passed to the preflight | — |
| :89 | start | R | V1.4(a) | `$SPECS_PATH` required on every run | — |
| :93–95 | start | P | — | **Stops on `specs_git: misrooted`** (`SECURITY_SPECS_MISROOTED`); `blocked` carries on (V2.6). Reason: "the register lives under `$SPECS_PATH`, and nothing is written under a misplaced one" — no other group-A command stops on the flag | the flag returned before the caller's next step (it is) |
| :99 | start | R | V5.2 | No `prefix` | — |
| :118–121 | start | P | — | Reservations: its own capped `fetch --prune` of `session/*`, `for-each-ref`, `ls-tree`, `show`; tests `origin` and read-only mount itself. Reason :118 | output `remote` and read-only mount |
| :583, :51–54 | end | P | — | `$run_dir` removed immediately before `commit-artifacts`, on a finished run and in the refusal tail | caller actions before the commit call |
| :583 | end | R | V1.10 | `register_rebuild` to `commit-artifacts` | — |
| :585–589 | end | R | V2.13 | After the line: a settle line chosen by the §6 row (replay rows vs *push rejected* advising `pull --rebase`), its sha7 (`diff-tree`), and the replay's moves under `security/<slug>/` | return the **row id, sha7 and replay moves** as fields, not only the rendered line |
| :46–67 | end | R | V2.2 | Refusal tail: worktree removal, cost, `$run_dir`, commit, settle line | — |
| :532–583 | end | R | tail | maintenance → feedback → follow-ups (+ a second `register.py commit` on a cancelled line) → proposals → cost → `resume.md` → commit | — |

Restated rules: none on either entry point (cites only); :554, :575–577 restate G1's cost of an uncommitted edit at its true extent.
**Verdict: needs option** — structured outcome fields, a pre-commit caller slot.

---

## 1. D items that are latent bugs today

1. **`/design` *Next Epic* loop** (`design.md:547–554`) — several handoffs in one run, no `branch-check` per looped Epic, unlabelled lines, a report and `<merge-clause>` that assume one line. An unmerged `design/<next Epic>` branch gets *Switch refused* at the second handoff, the failure §6.2 exists to prevent. PH:476–477's "only such producer" claim is false while this loop stands (`/specify:1158` the same).
2. **`inputs_read` never passed** (`/frames:359` "all five"; `/design:545`, `/ready:530`, `/conformance:473`, `/implement:1244`). PH §2.2's stack test then sees only the declared paths. Sharpest at `/design`, the very case PH names (a design built on an open `epics/` refinement is cut from `<default-ref>` without it). The orchestrator may rebuild the list from PH-h2m §2.9 at handoff time, so whether it bites depends on the session; the command text, read literally, omits it.
3. **`branch-check` before the placement refusals** in `/conformance:54` and `/implement:99`. A branch-check stop (and, in `/conformance`, §6.2's question) can come before `*_BRD_NOT_SLICED` / an unplaceable-folder stop. Low severity: a wrong first message, no wrong write.

Not bugs: the narrower restated setter lists (the skip is keyed on the flag), the missing `NOISSUE` in glosses, the `Run flags:` order, `/design`'s report-order contradiction, `/frames`' "for the rest of that session".
Possible latent bug, classed **U**: `/prompt` (and the other logging commands) run keyless, so B4 moves the checkout off an in-progress branch before `/prompt` edits the files it corrects (`prompt.md:30–37, :51–54`).

## 2. Options the shared step must offer that the contract does not already list

1. Preflight **output: the branch B2 found merged and left** (`/implement:93–97`; contract §0.1 has B4's only).
2. **Standalone read-only `mode`** before any preflight (`/implement:76`).
3. **`branch-merged <ref>` and `branch-key <branch>`** callable by a command (`/conformance:78–84`).
4. Outputs **`remote` present** and **read-only mount** beside `<default>`/`<default-ref>` (`/conformance:71`, `/scan:119`).
5. The **§2.1 classifier** (ARTIFACT/OTHER over porcelain `-z`) callable (`/ready:119–136`).
6. Handover: a **caller slot before the flag / no-remote line** (`/ready:527`, `/conformance:461–471`).
7. Handover: a **caller-side skip before the offer**, with the "already on `<default>` as written" test exposed and a **caller-owned not-offered line** — the line needs PH and `/frames` reconciled first (`/frames:336–355`; `PH:463`).
8. Handover: a **hook after a declining answer** (`/frames:371–381`).
9. Handover: **several offers per run, each labelled** — V3.13 generalised beyond `/brd-reconcile` (`/design:547–554`, `/specify:1158`).
10. Handover: **flags taken from the caller's state** and **the line (and row) returned** for the caller to store (`/implement:1244`).
11. `require-on-main`: **stop wording that names `$SPECS_PATH`** for a caller standing in a code repository (`/implement:230`).
12. End: **a tail with no cost member** (`/upgrade:28`, `/vuln:22`; contract V2.2 assumes cost).
13. End: **caller actions between `resume.md` and `commit-artifacts`** — `/implement:1471` run-state removal, `/scan:583` `$run_dir`, `/upgrade:240` and `/vuln:312` file removal — so the commit stays a separate call, or the bundled tail has a pre-commit hook; and **flags, key and `session_branch_created` passed in** (or a state file that outlives `run-state.py remove`).
14. End: **structured outcome** (row id, sha7, replay moves) besides the rendered line (`/scan:585–589`; V2.13 names the prose, not the fields).
15. **SBP `commit` / `lift` / `put-back` callable by a command** (`/implement:391, :1256`; V1.13 notes the moves, not the access).
16. Contract list fixes: `/implement` belongs in **V5.2** (no prefix) and **V4.1** (later `require-on-main`).

## 3. Commands marked *needs preparation*

- **`/design`** — the *Next Epic* loop has to become one handover per Epic (its own `branch-check`, a labelled line, a stated line for the report and `<merge-clause>`), or the run has to end at the first handoff. Also pass `inputs_read`.
- **`/implement`** — its specs-repo run state (`specs_git`, `session_branch_created`, `specs_merged_branch`) lives in `run-state.py`, the rest in the conversation, and the shared state would be a third home. Settle ownership, and make the shared state outlive `run-state.py remove` (which runs before the commit) before switching.
- **`/vuln`** (small) — say which single key the `commit-artifacts` subject takes when the tokens carry several.

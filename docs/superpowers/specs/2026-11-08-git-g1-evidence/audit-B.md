# GIT-G1 audit — group B

Scope: `plugins/docs-workflows/commands/{docs-audit,docs-brand,docs-init,docs-serve,document,release-notes}.md`, `plugins/product-workflows/commands/{idea,create-prd,update-prd,create-ard,specify,update-spec}.md`, read on `main` at `4fef611b`. Paths below drop the `plugins/<plugin>/commands/` prefix. SRG = `workflows-core/references/specs-repo-git.md`, PH = `workflows-core/references/phase-handoff.md`, EF = `workflows-core/skills/reference/entry-files.md`, V-ids and §§ = `gitg1-contract.md`. Classes: R (the references define it), P (purposeful, reason quoted), D (drift), U (unclear).

---

## 0. Items common to several commands (cited by ID below)

| ID | Sites | Part | Class | Departure | What the shared step must offer / which version is right |
|---|---|---|---|---|---|
| **C1** | idea.md:662, create-prd.md:878, update-prd.md:190, create-ard.md:768, specify.md:1150, update-spec.md:158, release-notes.md:706–713 | handover | **D, latent bug** | No producer passes `inputs_read`. PH §2.9 (phase-handoff.md:224) lists six caller-supplied inputs; `inputs_read` was added in workflows-core 1.35.0 (workflows-core/CHANGELOG.md:920, 2026-10-08) and `grep -c inputs_read plugins/*/commands/*.md` finds 0 in every command. `/idea` still says "all five of its §2.9 inputs" (idea.md:662) and "**All five are required**" (:671). | PH §2.9 is right. **What goes wrong today:** PH §2.2's stack test (phase-handoff.md:77) reads `deliverable_paths` + `inputs_read`. With only the declared paths, a run that read an unmerged file on a branch it was standing on, without declaring that file, gets cut at `<default-ref>` instead of stacked, so its PR does not show that it depends on the other branch. Concrete case: `/update-prd` reads `ard.md`/`specification.md`/grounding without gating them (update-prd.md:101). It stands on a B3-kept `ard/<KEY>-…` branch, which branch-check §6.1 treats as one it "builds on", yet its `prd/` branch is cut from `<default-ref>`. Gated inputs are safe, because `require-on-main` stops on another prefix's unmerged copy (PH §3.3 rows D/E). Standardizing fixes this if the shared handover requires `inputs_read` or derives it (N14). |
| **C2** | idea.md:141–144, create-prd.md:98–100, update-prd.md:105, create-ard.md:270, specify.md:306–309, release-notes.md:174–180, document.md:46–52, docs-init.md:34, docs-brand.md:45, docs-audit.md:34 | start | restated | The same preflight paragraph is copied into each of these commands: "flush … retry … settle the branch. Prompt-free; it prints its `Environment:` line … If a guard fires, emit its §5 notice; if it returns `blocked`/`misrooted`, carry that flag for the whole run — the terminal `commit-artifacts` step skips on it." The docs commands and `/document` add SRG §1 rule 1 ("`git -C`, never a `cd`"). docs-init/docs-brand/docs-audit also add the SRG §8.1/§8.2 session-branch sentence. | Removal candidate. **The scope differs:** it names `commit-artifacts` as the only reader of the flag. SRG §7 rule 1 and the contract (§0.1) also make the handoff, `require-on-main`, `branch-check` and every tail emitter readers. Not a bug, because each reader tests the flag itself. `update-spec.md:42` cites the preflight and does not restate it, which is the form to aim for. |
| **C3** | idea.md:801–805, create-prd.md:958, update-prd.md:255, create-ard.md:951, specify.md:1259–1265, update-spec.md:184, release-notes.md:868–876, document.md:1526–1537 & :1997–2008, docs-init.md:342, docs-brand.md:376, docs-audit.md:399 | end | restated | Copies SRG §4: stages only §2.1, the message `<KEY> Add dev-workflows session artifacts (<cmd>)`, no `Co-Authored-By`, NEVER force-pushes / fails the run, "skips entirely when … `blocked` … or `misrooted` (§3.1, or `specs-root-check`'s stop), re-emitting that notice". | Removal candidate. **The scope differs in two places:** (a) the list of `misrooted` setters leaves out SH §7 `env-check` and SH §6 *Stop*. Only specify.md:1265 lists them, which is the correct scope per SRG §7 rule 1. (b) The five product commands' "pushes the branch this run's handoff phase created (§4.1)" leaves out the rule-3 reused branch and the declined / no-handoff landings that SRG §4.1 lists. Not a bug: SRG §4 step 1 gates on the flag "whichever of §3.1's setters set it" (specs-repo-git.md:697–699). |
| **C4** | product: "Hold its §6 outcome line for the Final report" (create-prd.md:958 etc.); docs: "Print its §6 outcome line here, as the run's last output" (release-notes.md:876, document.md:1534, docs-init.md:342, docs-brand.md:376, docs-audit.md:399) | end | R | The product commands print their Final report after the tail. The docs commands print their report first, then the tail, then the line. | SRG §6 ¶1 / §7 rule 3. The end call must both return the rendered line (product) and allow printing it at once (docs). The contract already marks placement as caller-owned (§2.1). |
| **C5** | docs-init.md:20, docs-brand.md:21, docs-audit.md:18 | end | **P** | The "stop route" goes to the report and then the **whole** emitter tail, maintenance and feedback included. Reasons: "so its cost and feedback are recorded" (docs-audit.md:18); "so its cost is recorded and `commit-artifacts` runs as the last action" (docs-init.md:20, docs-brand.md:21). | SRG §7 rule 2 allows it ("save where a stop's own text names another route"). **But SRG §4's refusal-tail bullet "Feedback writes nothing … a command's maintenance phase, which a refused run never reaches" (specs-repo-git.md:649) is false for these three**: the reference over-generalises. The shared "end" must be `commit-artifacts` alone, and which tail members run must stay the command's decision. It must not be a "refusal-tail mode" that skips members. |
| **C6** | SRG §4 step 4 for docs-repo commits: docs-init.md:223, docs-brand.md:260, document.md:902 (also docs-profile.md:219, finish-and-handoff.md:50 outside the group); PH §2.7.1 for PR drafts: document.md:1293 (also finish-and-handoff.md:100, code-handoff.md:203) | end/handover | **P** | Procedures of the specs-repo entry points are cited for repositories that are not `$SPECS_PATH`. | If GIT-G1 moves SRG §4 step 4 (pathspec commit + index restore) or PH §2.7.1 (PR-template fill) into the script/skill, those sections must stay citable text, or the script must expose a primitive that works on any repository (e.g. `--repo <root>`). |

---

## 1. `/product-workflows:idea`

| # | file:line | part | class | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|---|
| I1 | idea.md:52, :141 | start | R | V1.1 | Preflight-first: the key comes from `read-key`, or from the carrier of an `@<path>` folder; the preflight runs "before the folder is resolved". A whole folder name is the stated exception. | Accept a key set built before resolution. |
| I2 | idea.md:146 | start | R | V5.3 | `branch-check` runs only "where step 1 found the folder", with `prefix: idea`. | Allow no `branch-check` for a folder this run will create. |
| I3 | idea.md:29, :760 | end | R | V2.2 | Refusal tail = Phase 6 steps 3+4. No `resume.md` on any run; the reason is at :753 ("no pointer because this run hands its brief off in the same run"). | End call independent of `resume.md`. |
| I4 | idea.md:649–661 | handover | R | V3.1, V3.2, V3.3 | Cites *gated — falling back* (naming class and half). The per-run test `cat-file -e "<default-ref>:./<path>"` switches it to the quoted stopping array. | `<default-ref>` available before the consent; the caller chooses the array. |
| I5 | idea.md:662, :671 | handover | **D** | — | "all five" inputs, but §2.9 has six (C1). | PH §2.9 is right; latent bug per C1. |
| I6 | idea.md:683–684 | handover | R | PH §4.3 | "On option 2 or 3 `handoff-to-main` does not run; emit §4.1's *Declined by the user* line" — the run emits the decline itself. | **N10**: call the shared handover on options 2/3 too, so it prints the row and records the declined paths for SRG §6's append. |
| I7 | idea.md:698–712 | handover | **P** | — | Reads *which* §4.1 row fired (*Declined*, *Gate failed*, *Commit failed*, *Switch refused*) to add the `@<path>` route. Reason: "None of the four outcomes committed anything." | **N6**: return the outcome as a row id, not only as text. |
| I8 | idea.md:716 | handover | R | V3.12 | `status: draft`: no offer and no line. | — |

Restated rules: C2, C3; idea.md:629–636 restates SRG §3.3 G1's consequences ("Its consequences are three…"). Same scope; removal candidate.
**Verdict: needs option** (N6, N10); C1 needs preparation unless N14.

## 2. `/product-workflows:create-prd`

| # | file:line | part | class | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|---|
| CP1 | create-prd.md:49, :97–100, :142 | start | R | V1.1 | Preflight-first (read-key or `@<path>` carrier); resolution is taken "as soon as step 2b has settled `$SPECS_PATH`". | — |
| CP2 | create-prd.md:102–108 | start | **P** | — | Reason quoted: "Step 3's `require-on-main` performs no fetch of its own … a merged `idea.md` reads as 'on a branch and never handed off'". History: "for a time the only `commit-artifacts` caller running no preflight … the G0 guard … was inert". | Ordering guarantee: the preflight's fetch comes before `require-on-main` (contract §1.3 already has it). |
| CP3 | create-prd.md:111 vs :154, :217 | start | **U** | — | The `branch-check` paragraph sits after 2b. Steps 5a/5b (carrier refusals) fire "the moment step 5 returns found", which is "as soon as step 2b". Which runs first is not stated; PH §6 ¶1 puts `branch-check` after carrier refusals. | Settled by a sentence placing `branch-check` after 5a/5b. |
| CP4 | create-prd.md:121 | start | R (+P) | V4.3 | `require-on-main` on `idea.md`: row F falls through, and a worktree copy "exists but is on no ref" is reported. | Row F returned; the worktree test stays the caller's. |
| CP5 | create-prd.md:372–397 | start | R | V4.3 | 7a: `require-on-main` on `decisions.md`, with row F split by worktree presence. Own stop texts (`CREATE_PRD_REGISTER_NOT_ON_MAIN`, :388, :392) are built from "the state require-on-main reported — on branch <branch> with PR #<n> … changed in the working tree against <default> (<files>) …". B′'s remedy is used "with its closing re-run left out". | **N4**: the result must carry the row id, files, and B′ remedy with the re-run clause separable. |
| CP6 | create-prd.md:872–875 | handover | R | V3.3 | Quotes the gated-stopping array. | — |
| CP7 | create-prd.md:878 | handover | **D** | — | No `inputs_read` (C1). | Per C1. |
| CP8 | create-prd.md:958 | end | **P** | contract §8.4 | On the BRD route the commit key is `<SLICE-KEY>`: "this is a specs-repo commit-message prefix, not a tracker lookup, and the slice key is the key this run resolved". | End call takes an explicit key. |

Restated: C2, C3 (also "or `NOISSUE` … when the run resolved no key at all").
**Verdict: needs option** (N4); C1.

## 3. `/product-workflows:update-prd`

| # | file:line | part | class | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|---|
| UP1 | update-prd.md:37, :105 | start | R | V1.1, V1.3 | Resolve-first; the key set gains the Epic parent's key (step 3a then refuses Epic folders). | — |
| UP2 | update-prd.md:101 | start | R (+P) | V4.8 | No `require-on-main`, by design: "Gating advisory grounding would block a legitimate PRD refresh because an unrelated ARD sits on a branch". | The shared step must not impose `require-on-main`. |
| UP3 | update-prd.md:190 | handover | R | V3.3 | Quotes the stopping array. | — |
| UP4 | update-prd.md:190 | handover | **D** | — | No `inputs_read` (C1). This is C1's concrete latent case. | Per C1. |

Restated: C2, C3.
**Verdict: ready**, apart from C1.

## 4. `/product-workflows:create-ard`

| # | file:line | part | class | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|---|
| CA1 | create-ard.md:60–66, :270 | start | R | V1.1, V1.3 | Resolve-first; an Epic run carries two keys. | — |
| CA2 | create-ard.md:272–358 | start | R | V4.3, V4.8 | Three `require-on-main` calls (PRD, register, Epic), each with its own `absent` report and own stop texts (:309, :313). | **N4**. |
| CA3 | create-ard.md:768 | handover | R | V3.1, V3.2 | Two quoted arrays, chosen by the deliverable set and the per-run `cat-file -e "<default-ref>:./<path>"` test. | `<default-ref>` exposed; the caller chooses the array. |
| CA4 | create-ard.md:768 | handover | **D** | — | No `inputs_read` (C1). | Per C1. |
| CA5 | create-ard.md:774, :931–937 | end | **P** | §8.4 | Commit key = the key of the folder Phase 0 resolved (the Epic key on an Epic run): "so the cost and feedback entries land on those references' primary tier". | Explicit key. |
| CA6 | create-ard.md:831 | after handover | R | — | The next-step offer reads `<default-ref>` again. | `<default-ref>` must persist past the handover. |

Restated: C2, C3.
**Verdict: needs option** (N4); C1.

## 5. `/product-workflows:specify`

| # | file:line | part | class | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|---|
| SP1 | specify.md:200, :306 | start | R | V1.1, V1.3 | Resolve-first; the key set includes the Epic parent's key. | — |
| SP2 | specify.md:295, :627, :630 | start | R | V5.1 | `reuse: later` on a PRD address, re-run after Step A (re-pointed Epic, or broad spec). | — |
| SP3 | specify.md:311–400, :636–638 | start | R | V4.1 | Gates PRD and register in Phase 0. The Epic is gated in Step B "every time [Step A] sets it, Phase 7's *Next Epic* re-render included". | — |
| SP4 | specify.md:30, :1118, :1179, :1265 | start/handover/end | R | SH §6 | SH §6 points 1–3. *Stop* sets `misrooted` with a `RESUME_ENVIRONMENT_CHANGED:` notice that `commit-artifacts` repeats. | Shared state must accept a flag plus notice set outside the shared calls. |
| SP5 | specify.md:1145–1147 | handover | R | V3.3 | Quotes the stopping array. | — |
| SP6 | specify.md:1150 | handover | **D** | — | No `inputs_read` (C1). | Per C1. |
| SP7 | specify.md:1152–1158 | handover | R | EF (entry-files.md:5, "A producer offering a second handoff in one run … the first handoff's answer never stands for it") | The *Next Epic* loop re-runs Phases 3–7, giving **N handoffs, N consent choices and N outcome lines in one run**. The contract's V3.13 names only `/brd-reconcile`. | **N3**: consent memory and outcome lines kept per handoff (per `feature_folder`). |
| SP8 | specify.md:1278 | end | **D** | — | The Final report lists "the `Phase handoff:` outcome line" in the singular although SP7 emits several. PH §4.1: "exactly one per offer". | One line per handoff is right. Latent reporting gap (an earlier Epic's line can be dropped); fix the text. |
| SP9 | specify.md:1194–1198 | end | **P** | §8.4 | Key = the folder Phase 0 resolved (the PRD key even when the handoff landed on `spec/<EPIC>`). | Explicit key. |

Restated: C2; C3 (specify.md:1265 is the one copy with the full list of `misrooted` setters).
**Verdict: needs option** (N3, N4, SP4 flag injection); C1; SP8 text fix.

## 6. `/product-workflows:update-spec`

| # | file:line | part | class | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|---|
| US1 | update-spec.md:42 | start | R | V1.1 | Resolve-first; the preflight is **cited, not restated** (the target shape). | — |
| US2 | update-spec.md:44 | start | **P** (+R) | V5.2 | `branch-check` with **no prefix**, though it is a producer (`spec`). Reason: "step 5 stops on a branch that changed `specification.md`, the open work §6.2 would ask about". PH §6.1 (phase-handoff.md:633) anticipates "or exempts itself from passing a prefix". | **N8**: V5.2 must not treat "no prefix" as meaning "non-producer". |
| US3 | update-spec.md:47 | start | **P** | V4.3 | `unmanaged` → stop (other callers proceed): "no specification is merged on a default branch — /update-spec revises a merged one". | Return `unmanaged` without mapping it. |
| US4 | update-spec.md:48–52 | start | R | V4.3 | Rows D/E/F → own stops naming "the state require-on-main reported". | **N4**. |
| US5 | update-spec.md:53 | start | **P** | — | Rows C/C′/C″: the command's pending-change test runs **before** the row-C repair offer, and it must "**never** offer `require-on-main`'s switch, which would leave that change behind". | **N5**: a classify-only mode that returns row C without asking, plus a separately callable repair. |
| US6 | update-spec.md:55 | start | **P** | — | Scans `spec/`, `design/`, `conformance/` branches (local and `origin/`) with B′'s fork-point diff and SRG §3.5 `branch-merged`. | **N7**: expose `branch-merged` and the fork-point test. |
| US7 | update-spec.md:154–156 | handover | R | V3.3 | Stopping array; correct, since the base is on `<default-ref>`. | — |
| US8 | update-spec.md:158 | handover | **D** | — | No `inputs_read` (C1). | Per C1. |
| US9 | update-spec.md:170 | end | R | SH §6 | Keeps no session file, so there is nothing for SH §6 to compare. | — |
| US10 | update-spec.md:178 | end | **P** | §8.4 | Key = the folder Phase 0 resolved, "as /specify passes it". | Explicit key. |

Restated: C3 (no C2).
**Verdict: needs option** (N4, N5, N7, N8). US5 interleaves the command's test inside `require-on-main`, but the command text already orders it, so N5 is enough and no restructuring is needed. C1.

## 7. `/docs-workflows:release-notes`

| # | file:line | part | class | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|---|
| RN1 | release-notes.md:47–53, :174–176 | start | R | V1.2, V1.4(b) | `$SPECS_PATH` is asked for only on a key address; an `@<path>` run continues when it is unset; an address stop runs no preflight. | — |
| RN2 | release-notes.md:58–66, :174 | start | R | V1.1, V1.3 | Resolve-first; the Epic adds the PRD key; the preflight runs before the placement stops. | — |
| RN3 | release-notes.md:99–108 | start | R | V1.9 | Slice re-entry runs the preflight again with the slice key set and switches back to the B4 branch via `branch-key`. | Re-callable in one run with a changed key set, remembering B4's branch. |
| RN4 | release-notes.md:182 | start | R | — | `branch-check` on the PRD folder (above an Epic), `prefix: prd`, **after** placement, which is PH §6's order. | — |
| RN5 | release-notes.md:680–690 | handover | **P** | — | No offer where `$SPECS_PATH` is unset or the PRD folder's realpath is outside `$SPECS_PATH`'s work tree. Reason: "a handoff would cut a `prd/` branch in `$SPECS_PATH`, stage nothing there, and leave the checkout on that branch for the terminal session commit". The report says why no offer was made. | **N2**: an applicability test plus a "no offer: <reason>" result. |
| RN6 | release-notes.md:696–701 | handover | **P** | — | Prints a line on the cost of declining "immediately above [the array], or above §4.3's flag or no-remote line where that section prints one". Reason: "since neither the array nor §4.1's *Declined by the user* line says it". | **N1**: a caller-preamble hook printed before the flag/no-remote line. |
| RN7 | release-notes.md:702–704 | handover | R | V3.1, V3.3 | Advisory array quoted and its class named. | — |
| RN8 | release-notes.md:706–713 | handover | **D** | — | No `inputs_read` (C1). | Per C1. |
| RN9 | release-notes.md:707–709 | handover | R | — | `feature_folder` = the PRD folder above an Epic; the title's key is `focus_key` where it is set. | — |
| RN10 | release-notes.md:868–871 | end | **U** | §8.4 | `<KEY>` in the commit message is not defined for an Epic address (two keys). The title uses `focus_key`; cost uses "the run's `key` (or `null`)" (:850). | Settled by stating which key. |
| RN11 | release-notes.md:876 | end | R | C4 | Line printed as the last output, after the Phase 8 report. | — |

Restated: C2 (plus SRG §3's runs-none list and §1 rule 1); C3. :714–718 and the :700 line restate SRG §3.3 G1's effect (the line is RN6's purposeful copy). :901–902 restate SRG §1 rule 1, §2.2, §3.5, §8.2.
**Verdict: needs option** (N1, N2, RN3 re-call); RN10 U; C1.

## 8. `/docs-workflows:document`

| # | file:line | part | class | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|---|
| DO1 | document.md:37–52 | start | R | contract §1.3 | One preflight in the shared `## Mode detection`, serving both modes; Mode B is keyless. | — |
| DO2 | document.md:30, :46 | start | R | V1.4(b),(c) | `$SPECS_PATH` is asked for only on a `<KEY>`; `@<path>` and Mode B continue when it is unset. | — |
| DO3 | document.md:71 vs :73–90 | start | **D** | (V5.2 R for the missing prefix) | `branch-check` runs **before** "Place the folder" and its carrier refusals (`DOCUMENT_BRD_NOT_SLICED`, `_FOLDER_NOT_PLACED`, `_PRD_NO_KEY`, `_NO_PRD`). PH §6 ¶1 puts it after "the refusals that place the folder by its carrier"; the twin `release-notes.md:182` does so. | release-notes is right. Latent effect is minor: a branch-check stop pre-empts the placement stop. Standardizing does not fix it; moving the call does. |
| DO4 | document.md:103–108 | start | R | V1.9 | Slice re-entry runs the preflight again. | As RN3. |
| DO5 | document.md:56, :232–246 | end | R | V2.3, SRG §4 step 7 | A stop after 4(c)'s docs-repo commit takes the refusal tail, and the *left-on-a-branch* notice prints **after** the `Specs repo:` line. | The end call must not assume it prints the last line (contract §2.3 has this). |
| DO6 | document.md:56 | end | R | V2.4 | Direct-mode stops before a write target exists take no tail. | — |
| DO7 | document.md:56 | end | R | V2.3 | "no maintenance phase the run had not already reached" (Phase 8 runs before 8.5's *Cancel*). | Tail membership stays the command's (C5/N11). |
| DO8 | document.md:1267–1300 | handover | R | V3.16 | Docs-repo finish with its own array (:1283), not PH §4.3. | The shared handover must not be applied here. |
| DO9 | document.md:902, :1293 | — | **P** | C6 | Borrows SRG §4 step 4 and PH §2.7.1. | N9. |
| DO10 | document.md:1526–1531 | end | **U** | §8.4 | Keyed `<KEY>` is not defined for an Epic address. | State which key. |
| DO11 | document.md:1630–1634, :1997 | start/end | R | V2.11 | Mode B: "Do not run it a second time"; one commit text per mode. | — |

Restated: C2 (plus §1 rule 1); C3 (both modes); :1586 and :2022 restate SRG §2.2, §8.1, §8.2.
**Verdict: needs option** (re-call per V1.9, a line after the outcome line, N9); DO3 text fix; DO10 U.

## 9. `/docs-workflows:docs-init`

| # | file:line | part | class | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|---|
| DI1 | docs-init.md:32–34 | start | R | V1.3, V1.4(c) | Keyless preflight after the docs target is resolved (step 1). | — |
| DI2 | docs-init.md:20 | end | **P** | V2.4, C5 | Stop route: report, then tail 9–11 including maintenance and feedback. No tail before step 1 resolves a target. | N11. |
| DI3 | docs-init.md:20 | end | R | V2.3 | `DOCS_INIT_UNRESOLVED_BLOCKER` after the scaffold is written is reported like a review-gate stop. | — |
| DI4 | docs-init.md:136–153 | start/end | R | V1.12, V2.12 | Runs `/docs-brand --inline` through the Skill tool. That run does no preflight, no commit, and inherits `run_flags`. | **N12**: state scoped to the top-level run; a Skill-invoked inline command opens no scope. |
| DI5 | docs-init.md:223 | — | **P** | C6 | Borrows SRG §4 step 4. | N9. |
| DI6 | docs-init.md:342 | end | R | C4 | Line printed last, after the 8.5 report. | — |

Restated: C2 (plus §1 rule 1 and the session-branch sentence); C3; the :368 invariant.
**Verdict: needs option** (N9, N11, N12).

## 10. `/docs-workflows:docs-brand`

| # | file:line | part | class | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|---|
| DB1 | docs-brand.md:25–45 | start | R | V1.2 | Preflight after steps 1–3 (resolve the docs repo; git-worktree and Material-theme stops). These check inputs that need no specs-repo state. | — |
| DB2 | docs-brand.md:21 | end | **D** | SRG §7 rule 2 | *Ending early* omits "a stop before the preflight skips only the preflight", although steps 2–3 (`DOCS_BRAND_NOT_A_GIT_WORKTREE`, `_REPO_NOT_WRITEABLE`, `_NOT_MKDOCS`) stop before it and take the stop route. Every other preflight-running command in the group states it. | No bug: SRG §4 step 1 handles a run with no preflight (V2.5). Text fix. |
| DB3 | docs-brand.md:21 | end | **P** | V2.4, C5 | Stop route through the report and tail 12–14; no-tail exceptions. | N11. |
| DB4 | docs-brand.md:39–45, :328, :366 | start/end | R | V1.12, V2.12 | `--inline`: no preflight, no tail, no commit. | No shared call on that path. |
| DB5 | docs-brand.md:260 | — | **P** | C6 | Borrows SRG §4 step 4. | N9. |
| DB6 | docs-brand.md:376 | end | R | C4 | — | — |

Restated: C2 (plus §1 rule 1 and the session-branch sentence); C3; the :394 invariant.
**Verdict: needs option** (N9, N11, `--inline` makes no calls).

## 11. `/docs-workflows:docs-audit`

| # | file:line | part | class | V-id | departure | shared step must offer / right version |
|---|---|---|---|---|---|---|
| DA1 | docs-audit.md:34 | start | R | V1.3, V1.4(c) | Keyless preflight after the docs repo is resolved. | — |
| DA2 | docs-audit.md:18, :389–391 | end | **P** | V2.4, C5 | Stop route records "cost and feedback". No tail for step 1's three flag stops or step 2's *Cancel*. | N11. |
| DA3 | docs-audit.md:142 | start | R | V5.9 | Reads the specs tree at large; no `branch-check` and no `require-on-main`. | — |
| DA4 | docs-audit.md:399 | end | R | C4 | — | — |
| DA5 | docs-audit.md:18 vs docs-init.md:20 | end | **D** (wording) | — | Same stop-route rule, worded differently ("the family invariant every command writing into `$SPECS_PATH` holds" vs "which `workflows-core:specs-repo-git` §4 requires…"). | No behavioural difference. |

Restated: C2 (plus extras); C3; the :427 invariant.
**Verdict: needs option** (N11 only); otherwise ready.

## 12. `/docs-workflows:docs-serve` — no preflight, confirmed

docs-serve.md:32 ("**No `specs-preflight`.** This is deliberate, not an omission: `/docs-serve` writes nothing into `$SPECS_PATH`…"), the :281 invariant ("NEVER run `specs-preflight` or `commit-artifacts`"), `.claude/rules/docs-serve.md:15`, and CLAUDE.md § Active plugins ("absent from every caller list by design"). It makes no handoff, `require-on-main` or `branch-check` call.

**What the shared step must not do to it:**
1. Run implicitly: through a hook, through a wrapper every command loads, or bundled with `strip-run-flags` (docs-serve runs `strip-run-flags` at :24 but no preflight).
2. Be required of every command by a new gate. No current gate requires a preflight call (`scripts/` has none). A GIT-G1 gate must exempt docs-serve and the other non-callers listed in contract §7.
3. Print an `Environment:` line, open per-invocation state, or run `env-check` for it.
4. Count its own writes (`<repo-root>/.dev-workflows/docs-serve.state.json`, the `info/exclude` line, `dw-serve-*` logs) as session artifacts or as dirt.

**Verdict: n/a** (stays outside).

---

## 13. Findings

### (1) Every D that is a latent bug today
- **C1 — `inputs_read` is never passed** by any handoff producer in the group (idea, create-prd, update-prd, create-ard, specify, update-spec, release-notes). Consequence: PH §2.2's stack test is blind to files the run read but did not declare, so a run on a B3-kept branch that it read from gets cut at `<default-ref>` and its PR does not show the dependency. Concrete: `/update-prd`'s ungated ARD/spec reads (update-prd.md:101). Fixed by standardizing **if** the shared handover requires or derives `inputs_read`. `/idea`'s "all five … All five are required" (:662, :671) is the visible symptom.
- **SP8 — `/specify` Final report names one `Phase handoff:` line** while the *Next Epic* loop emits one per Epic (PH §4.1 "exactly one per offer"). Low-severity reporting gap; fix the text.
- **DO3 — `/document` runs `branch-check` before its carrier-placement refusals** (document.md:71 vs PH §6 ¶1; release-notes.md:182 is right). The wrong stop is shown first. Low severity; move the call. Standardizing does not fix it.
- Not bugs: C2/C3's narrower scope (the references test the flags themselves), DB2 (V2.5 covers it), DA5 (wording only).

### (2) Options the shared step must offer that the contract does not already list
- **N1** Handover: a caller preamble line printed *above* PH §4.3's flag/no-remote line (release-notes.md:696–701).
- **N2** Handover: an applicability test with a "no offer: <reason>" result where `$SPECS_PATH` is unset or `feature_folder` lies outside its work tree (release-notes.md:680–690).
- **N3** Handover: consent memory and outcome lines kept **per handoff** for in-run loops: `/specify`'s *Next Epic* (specify.md:1152–1158). V3.13 names only `/brd-reconcile`; EF:5's general rule covers it.
- **N4** `require-on-main`: the result must carry the **row id, the file list, and B′'s remedy text with its closing re-run separable**. create-prd/create-ard/specify/update-spec compose their own stops from them (create-prd.md:388–392, create-ard.md:309–313, specify.md:346–350, update-spec.md:48–54). The contract §4.2 return (`on_main, stopped, branch, pr, degraded`) lacks them.
- **N5** `require-on-main`: a **classify-only mode** that returns row C/C′/C″ without the repair offer, with the repair callable separately (update-spec.md:53).
- **N6** Handover: return the §4.1 outcome as a **row id** (idea.md:698–712 branches on *Declined*/*Gate failed*/*Commit failed*/*Switch refused*).
- **N7** Expose SRG §3.5 `branch-merged` and the B′ fork-point test as primitives (update-spec.md:55).
- **N8** `branch-check` without a prefix for a **producer that exempts itself** (update-spec.md:44; PH:633). Contract V5.2 lists only non-producers.
- **N9** Keep SRG §4 step 4 and PH §2.7.1 citable, or expose repo-agnostic primitives (C6: docs-init, docs-brand, document, plus docs-profile, finish-and-handoff, code-handoff).
- **N10** Handover invoked on options 2/3 as well, to print *Declined by the user* and record the declined paths for SRG §6's append. Commands today emit that line themselves (idea.md:683).
- **N11** "End" = `commit-artifacts` alone; tail membership stays the command's. The docs stop route runs maintenance and feedback (C5). SRG §4's "Feedback writes nothing" (specs-repo-git.md:649) is false for three commands.
- **N12** Shared state scoped to the top-level run; a Skill-invoked `--inline` command opens no scope (docs-init.md:136–153).
- **N13** Shared steps are never implicit, and no all-commands gate (docs-serve; `docs-brand --inline`).
- **N14** Derive `inputs_read` from the run's own reads (e.g. Read calls under `$SPECS_PATH` in the transcript, as cost-emission reads it), or reject a handoff call without it.
- Also: the end call takes an **explicit key**. release-notes and `/document` leave the Epic-address key undefined (RN10, DO10, U). The contract §8.4 already notes the reference gap.

### (3) Commands marked `needs preparation`
- **None needs restructuring for the start, end or handover calls themselves.** update-spec's in-gate test (US5) fits N5, release-notes' preamble and no-offer (RN5/RN6) fit N1/N2, and specify's loop fits N3.
- **Conditional preparation, C1:** all seven handoff producers (idea, create-prd, update-prd, create-ard, specify, update-spec, release-notes) keep no record of `inputs_read`. That state does not exist today, not even in the conversation. Unless the shared step derives it (N14), each must first record its `$SPECS_PATH` reads.
- Text fixes, not restructuring: SP8, DO3, DB2, and stating the key for RN10/DO10.

### Counts (rows above; C1 counted once per producer)
R 52 · P 18 · D 11 (7 are C1; 3 latent bugs listed in (1)) · U 3. Common rows: C1 D, C4 R, C5 P, C6 P (included in the per-command rows where cited).

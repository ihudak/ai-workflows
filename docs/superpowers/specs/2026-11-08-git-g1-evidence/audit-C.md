# GIT-G1 audit — group C (product-workflows: kb, epics, proposals, BRD route)

Read-only audit of `main` at `4fef611b`. Paths are under `plugins/product-workflows/commands/` unless shown; `ap` = `plugins/workflows-core/references/architecture-promotion.md`. V-ids are the contract's (`gitg1-contract.md`). Classes: **R** reference-defined, **P** purposeful (reason quoted), **D** drift, **U** unclear. New options the contract does not list are tagged **N1–N10** and collected at the end.

Two findings recur in most files, so they are stated once here and cited by tag in the tables:

- **[PROBE]** The command quotes the §4.3 array with "present its §4.3 choice array verbatim" and never names §2.1's push-target probe or the flag / no-remote line §4.3 prints above the array. `brd-interview.md:2339–2356` records why that is a defect: "**The probe is named here because quoting the array is what invites skipping it.** A live run of this phase read the instruction above, presented the array and ran no probe, offering a `(Recommended)` push-and-open-PR on a specs repo with no `origin` and no notice". So it is **D, a latent bug**. The shared handover call (probe, then line, then array) fixes it.
- **[EE-PRE]** The **Ending early.** paragraph sends every stop to the refusal tail, and never says that a stop before the preflight skips only the preflight. SRG §7 rule 2 asks for that sentence. **D, wording only.** SRG §4 step 1 already handles a run with no preflight, so no behaviour is lost. Across the family, 14 command files carry "skips/skipping only the preflight" (`grep -l`). In this group, only `/epics` (`epics.md:24`) and `/harvest-decisions` (`harvest-decisions.md:18`, "Phase 4 needs no preflight to run") state it.

---

## /harvest-decisions (`harvest-decisions.md`)

| file:line | part | class | V-id | departure | shared step must offer / which is right |
|---|---|---|---|---|---|
| :24 | start | D | V1.4 | `$SPECS_PATH` unset → own `HARVEST_NEEDS_SPECS_PATH` stop, with no *Set SPECS_PATH* offer. `escalation-rules` *Required path environment variable unset* says it is "Used when a command stops … because a path environment variable it requires is unset". No reason is given. | The escalation-rules form is right. No latent bug, only a less helpful stop. |
| :25 | start | R | V1.2 | `python3` check, and a stop, before the preflight | — |
| :26 | start | R | V1.3 | keyless preflight; "§3.5's row B4 moves the checkout off any unmerged plugin branch" | empty key set |
| :26 | start | P | V1.6 | `misrooted` → stop: "the script reads the repository's top level" | Return `misrooted` plus the setter's notice (already listed). |
| :27 | start | P | — | stop unless HEAD is `<default-ref>`'s branch: "the `kb/` branch is cut from the checkout, so a harvest from anywhere else would carry that branch's commits into its pull request" | Output fields: the current branch and the guard that fired (listed in §0.1). |
| :27 | start | D | V1.5/V1.7 | The stop names "what kept the preflight there (§3.3: G0…, G1…, G2…)". It omits §3.1's silent no-op on a read-only `.git` and a B4 switch git refused. Either one leaves the checkout off default with none of G0–G2, so the message names a wrong cause. | A preflight output field saying why the checkout is where it is. The stop still fires, so no wrong action. |
| :28 | start | P | — | Pending `kb/` stop. It loads the **whole** `phase-handoff` (`args: "phase-handoff"`) for §2.6.1's `owner-repo`, "here before this command's handoff phase". | **N6** (standalone `owner-repo`) |
| :48 | handover | R | V3.1, V3.3 | quoted **gated — stopping** array, reason given, probe named. No flag line, but none is reachable: `misrooted` stops at :26, and `blocked` (detached HEAD) stops at :27. | — |
| :52 | handover | R | V3.6 | `prefix: kb`, no `feature_folder`. No `inputs_read`, which is harmless: :27 puts HEAD on default, so §2.2's stack test never applies. | — |
| :54–56, :10 | end | P | V2.2 | The tail is `commit-artifacts` alone, with no cost, feedback, follow-ups or `resume.md`: "This command dispatches no agent, routes no model and emits no cost or feedback entry" | **N8** (a tail with no cost member; this is not `skip-cost`, which advances the checkpoint) |
| :60 | end | R | SRG §4 step 7 | next-step line printed after the `Specs repo:` line ("a line the command names after it") | — |
| :18 | end | R | V2.2, V2.5, V2.6 | Ending early (commit-artifacts only) | — |

**Restated rules.** :18 restates SRG §4 step 1: unset → "does nothing and prints nothing", and `misrooted` → "repeats the notice". The extent is the same, and it is a removal candidate.

**Verdict: needs option** (N6, N8, and the preflight's guard-fired / current-branch outputs).

## /promote-decisions (`promote-decisions.md`, handover via `ap` §11)

| file:line | part | class | V-id | departure | shared step must offer / which is right |
|---|---|---|---|---|---|
| :33; ap:20–38 | start | R | V1.2 | Architecture-repo guards 1–3 run before the specs preflight. They include a `fetch`, and guard 3's *Behind* question at ap:36. | Preflight-first, after the command's own checks. |
| ap:40 | start | D | V1.4 | own `PROMOTE_NEEDS_SPECS_PATH` stop, no *Set SPECS_PATH* (same as harvest :24) | escalation-rules form; no bug |
| ap:41 | start | R+P | V1.3, V1.6 | keyless preflight; `misrooted` → stop "as `/product-workflows:harvest-decisions` does: the scripts read the repository's top level" | as harvest |
| ap:43 | start | P | — | checkout on `<default-ref>`'s branch, "as harvest Phase 0 step 4 requires" | as harvest |
| ap:44 | start | P | — | `architecture/` uncommitted → stop: "this run reads the default branch, so it would propose those records again" | — |
| ap:84, ap:214 | handover | P | — | `owner-repo` derived, as PH §2.6.1 derives it, for the **architecture** repository, not `$SPECS_PATH` | **N6** for any repository path |
| ap:208, ap:227, ap:235 | handover | P | — | The mark plan is checked in §11.1 step 2 and written by `--mark` before the consent. Declining leaves the marks uncommitted. Reason (ap:208): "a plan refused after the push would leave the drafted records unmarked" | Command steps before the call; `body_facts` carries the architecture PR URL from §11.1. |
| ap:229 | handover | R | V3.3, V3.6 | Cited (not quoted) **gated — stopping**, with the class named; `kb` keyless. | — |
| :86; ap:229 | handover | D | — | The handoff is reached by citation from a workflows-core reference. There is no `Skill(… "phase-handoff handoff-to-main")` request, so the command preamble (:14) loads the whole 183 KB reference instead of PH-h2m. §4.3's flag line is not named, but it is unreachable: both flags stop at Phase 0. | Standardizing fixes the load path. No bug. The switch edits `ap` §11.2, not the command. |
| :102 | end | P | — | "**No session cost entry.** Like `/product-workflows:harvest-decisions`, this command has no PRD to attribute spend to." No follow-ups and no `resume.md` either; the tail is maintenance → feedback → commit. | **N8** |
| :23 | end | R | V2.3 | Stops "after the branch is cut" (architecture repo) take a command-stated tail: commit-artifacts only, no maintenance or feedback. | per-stop tail profile |

**Restated rules.** None of the five entry points' rules is restated.

**Verdict: needs option** (N6, N8; `ap` §11.2 must call the shared handover).

## /epics (`epics.md`)

| file:line | part | class | V-id | departure | shared step must offer / which is right |
|---|---|---|---|---|---|
| :33 | start | R | V1.4(a) | 0a *Set SPECS_PATH* before resolution | — |
| :58–66 | start | R | V1.1, V1.3 | resolve-first; an Epic address adds the parent's key | — |
| :171 | start | R | PH §6 Inputs | `branch-check` on `prd_dir` (the parent on an Epic address), `prefix: epics` | — |
| :390 | start | R+P | V4.1 | docs grounding runs before `require-on-main`: "a deliberate exception … kept here … because `resolve-docs-grounding`'s only expensive step is itself behind its own consent prompt" | Order is caller-owned. |
| :451 | start | R | V4.1, V4.3 | `require-on-main` at Phase 2.6; `absent` → skip | — |
| :888–946 | handover | P | — | Pre-handoff maintenance agents edit files that stood committed and clean, and those edits join `deliverable_paths` (reason :888: post-handoff edits "missed the pull request … fired §3.3's G1 advisory on every later run") | Command steps before the call. |
| :920 | handover | P | — | Loads the **whole** `phase-handoff` for §4.0's register of declared artifacts: "the load Phase 7.5 makes next, which then has it" | **N10** (a §4.0-register lookup), or keep this load. The sentence must be rewritten once 7.5 no longer loads PH. |
| :950 | handover | P | — | lineage `record` §5 step 2 on each `epic.md` "before the offer below stages anything" | hook before staging |
| :950 | handover | R | V3.2 | per-run array: each declared `epic.md` sorted new / unchanged / edited against `<default-ref>` | — |
| :950 | handover | P | — | Prints the maintenance edits "just above the array — before the one line §4.3 prints immediately above it (the `specs_git` flag line, or the no-remote line …), which keeps that place — so the operator consents to those edits knowing they ride the same commit" | **N2** (a caller preamble slot before the flag / no-remote line) |
| :959 | handover | R | PH §2.7 | `body_facts` per-Epic next-command sentence by the same sort | — |
| :24, :896 | end | R+P | V2.3 | Post-write stops (Phase 6 `DONE`, Phase 7 *Cancel the whole run*, the size questions) take the refusal tail, "once Phase 7.4's removal has run on every file `temp_files` holds" | per-stop tail profile; command step before the tail |
| :1204–1214 | end | R | V2.1 placement | the line is printed after the Phase 9 report, as the last output | — |
| :1206 | end | U | §8.4 | On a focus run, is the commit key `<KEY>` the Epic's key or `<PRD-KEY>`? The text uses "the run's `key`" (:1009, :1187). | Settled by stating which key; the reference leaves it open. |

**Restated rules.**
- :268–274: the preflight's behaviour. Same extent as SRG §3 and §7 rule 1.
- :1204–1214: the commit-artifacts behaviour. Its misrooted setters are "(§3.1, or `specs-root-check`'s stop)", which is narrower than SRG §4 step 1: it omits the setters in SH §7 `env-check` and SH §6 *Stop*.
- :1229 and :1231: "switching only branches the plugin created (§2.2)". SRG §2.2 limits which branches the plugin switches *away from* or deletes; B4 switches *to* the default branch. Extent differs, no bug.
- :1230: the G1 cost of a declined handoff. Same extent.

All are removal candidates.

**Verdict: needs option** (N2, N10, V3.2).

## /prd-ground (`prd-ground.md`)

| file:line | part | class | V-id | departure | shared step must offer / which is right |
|---|---|---|---|---|---|
| :45–58 | start/end | R | V2.4 | `PRD_GROUND_TYPED_ONLY` takes no tail | per-stop "no tail" |
| :139 | start | R | V1.4(a) | *Set SPECS_PATH* | — |
| :142 | start | R+P | V1.1, V1.3 | Preflight-first. The key set is "the one key step 1 read … **and never a `--depends-on` or `--from-split` key** … they name other folders, and a branch of theirs is not this run's to stay on" | The caller passes an explicit key list. |
| :258 | start | R | PH §6 | `branch-check` prefix by route (`brd` / `prd`) | — |
| :262–275 | start | P | V4.2-adjacent | Two `require-on-main` gates (ledger, then inventory) are both resolved before either stop prints. The ledger's stop is printed, with one exception, for a stated reason ("an inventory stop printed first would name the wrong remedy") | **N4** (`require-on-main` returns the stop instead of printing it) |
| :275ff, :512ff | start | R | V4.3 | row F split on worktree tests (in folder / not) | — |
| :2243 | handover | D | V3.4 | [PROBE] | **latent bug**; shared call fixes it |
| :2243–2249 | handover | R | V3.1 | **gated — stopping** in every mode, with the class reasoned | — |
| :2251–2262 | handover | R | PH §2.9 | prefix by route; rule-3 reuse of a shared `prd/` branch explained | — |
| :2264–2300 | handover | P | — | Conditional `deliverable_paths`: `brd-link.md` "where the working tree's copy differs from `HEAD`" (`status --porcelain -z`), and the ledger where the script printed `"written": true`: "naming an unchanged path in a handoff is how a commit comes to claim work it did not do" | Caller-built list. |
| :2494–2510 | end | R+P | V2.3 | Stops in Phase 3, 5 or 7 run maintenance (the stop among its key events), feedback, cost and commit, with no `resume.md` ("a stopped run printed none") | per-stop tail profile |
| :2551 | end | R | placement | line held for the final report | — |
| :39 | end | D | — | [EE-PRE] | wording |

**Restated rules.**
- :142–144: preflight boilerplate. Same extent.
- :2548–2551: "pushes the branch Phase 9's handoff created per §4 step 5". This is narrower than SRG §4.1, where a declined or absent handoff leaves the commit on the default branch, and session-branch mode puts it on the session branch.
- :2257–2262: PH §2.2 rule 3. Same extent.

**Verdict: needs option** (N4; per-stop tail profiles).

## /prd-proposal (`prd-proposal.md`)

| file:line | part | class | V-id | departure | shared step must offer / which is right |
|---|---|---|---|---|---|
| :93 | start | R | V1.4(a) | *Set SPECS_PATH* | — |
| :105–112 | start | R | V1.1, V1.3 | resolve-first; the preflight runs before the container and Epic refusals | — |
| :180 | start | R | PH §6 | `branch-check` `prefix: prd` | — |
| :182–200 | start | R | V4.3 | `require-on-main` on `prd.md`; row F split by worktree | — |
| :720 | handover | D | V3.4 | [PROBE] | **latent bug** |
| :720–741 | handover | R | V3.1, V3.3 | quoted **gated — stopping**, with the class named and reasoned | — |
| :743–750 | handover | R | PH §2.9 | shared `prd` prefix; `.dev-workflows/proposal-profile.yml` declared on every run | — |
| :75 | end | R | V2.3 | Stops after Phase 7 wrote `proposal.md` (Phase 9 answers) take the refusal tail: "A stop after Phase 7 leaves `proposal.md` written and uncommitted" | — |
| :875, :908–913 | end | R | placement | line held for the report, which continues after it (next step, "gates nothing") | — |
| :75 | end | D | — | [EE-PRE] | wording |

**Restated rules.**
- :105–109: preflight boilerplate.
- :870–876: commit-artifacts, with "pushes the branch this run's handoff phase created (§4.1)". Narrower than §4.1, and its misrooted setters omit SH §7 and §6.

**Verdict: ready.** Switching also fixes [PROBE].

## /brd-proposal (`brd-proposal.md`)

| file:line | part | class | V-id | departure | shared step must offer / which is right |
|---|---|---|---|---|---|
| :84 | start | R | V1.4(a) | *Set SPECS_PATH* | — |
| :96–104 | start | R | V1.1, V1.3 | resolve-first; key set fixed from resolution | — |
| :163 | start | R | PH §6 | `branch-check` `prefix: brd` | — |
| :315–335 | start | P | — | "Current" umbrella: "three of `require-on-main`'s read-only primitives and never the gate itself — this is a read, so nothing here prompts, switches a branch or stops" | The `<default-ref>` output (listed); optionally a non-gating probe. |
| :424–447 | start | R+P | V4.1 | Gate at Phase 4 (a later site), swept over every included slice and "Emit one stop at the end of the sweep": "A programme of six slices whose proposals are all unmerged should be one stop naming six" | **N4** (per-path return with §4.4's four parts as fields) |
| :793 | handover | D | V3.4 | [PROBE] | **latent bug** |
| :793–807 | handover | R | V3.1 | **advisory** array, class reasoned | — |
| :809–815 | handover | R | PH §2.9 | `brd` prefix; profile declared every run | — |
| :67, :339, :403 | end | P | V3.12 | Three operator ends (*Stop — the umbrella is current*, *Price/Re-price the slice first*, *End the run*) run "the whole emitter tail, as a completed run takes it", with no handoff: "an operator's finished decision rather than a refusal" | per-stop tail profile (full tail, no offer) |
| :67, :339, :403 | end | U | — | Those ends write `resume.md` (:905) but skip Phase 12, whose `### Next step` SH §1's pointer reads | Settle what the pointer records on these ends. |
| :67 | end | R | V2.3 | stops after Phase 8's write → refusal tail | — |
| :67 | end | D | — | [EE-PRE] | wording |

**Restated rules.** :96–100 (preflight); :909–915 (commit-artifacts, with the narrower push / misrooted extent as in prd-proposal).

**Verdict: needs option** (N4; the full-tail-without-offer profile).

## /brd-intake (`brd-intake.md`)

| file:line | part | class | V-id | departure | shared step must offer / which is right |
|---|---|---|---|---|---|
| :35–61 | start | R | V1.2, V1.4(a) | Missing key, missing source and PDF stops come before the preflight. *Set SPECS_PATH* loops back on `needs-tree`. | — |
| :44, :68 | start | R | V1.1 | Preflight-first. The key comes from `read-key`, or from the carrier of an `@<path>` | — |
| :164 | start | R | V5.3 | `branch-check` only "Where the folder was found" | optional call |
| :232–234 | start | R | V4.8 | no `require-on-main` (named exclusion) | — |
| :1472 | handover | D | V3.4 | [PROBE] | **latent bug** |
| :1472–1480 | handover | R | V3.1 | **gated — stopping**, reasoned (`/brd-reconcile` gates the defect log) | — |
| :1483–1495 | handover | P | — | Every captured file is enumerated, plus every untracked file already under `brd/source*`: "nothing else in the plugin ever stages it, so undeclared it stays untracked and the specs-repo preflight reports it … (G1) on every later run" | Caller-built list. |
| :1499–1503 | handover | R | PH §4.1 | the *Declined by the user* line on options 2 and 3 | — |
| :1505–1510 | handover | P | — | "name beside the outcome line the command its clause calls the next phase" | line and clause returned (listed) |
| :25 | end | R | V2.3 | stops after Phase 2's first write → refusal tail | — |
| :1644, :1694 | end | R | placement | line held; the ledger line ends the report | — |
| :25 | end | D | — | [EE-PRE] | wording |

**Restated rules.** :68–70 (preflight); :1639–1644 (commit-artifacts, with the narrower push / misrooted extent).

**Verdict: ready.** Switching also fixes [PROBE].

## /brd-split (`brd-split.md`)

| file:line | part | class | V-id | departure | shared step must offer / which is right |
|---|---|---|---|---|---|
| :97–100 | start | R | V1.4(a), V1.1 | preflight-first | — |
| :164 | start | R | PH §6 | `branch-check` `prefix: brd` | — |
| :166–200 | start | R | V4.3 | `require-on-main` only in `allocate-only`; row F split | — |
| :170 | start | U | PH §4.0 | "this file's presence on `origin/<default>` implies `grounding/design-grounding.md` and `brd-link.md` merged with it". The clause covers `--no-code` for `design-grounding.md` only. A `--no-code` `/prd-ground` also hands a changed `brd-link.md` off on its own (`prd-ground.md:2271–2276`), and PH §4.0 ("Never infer an artifact's merged-ness from a sibling's gate") forbids the inference without a clause. | Settle whether any `allocate-only` step depends on `brd-link.md` being merged. |
| :1401 | handover | D | V3.4 | [PROBE] | **latent bug** |
| :1401–1413 | handover | R | V3.1 | two arrays chosen by the declared set (strongest class) | — |
| :1415–1432 | handover | P | — | A removed child's three files are named individually: "a folder-shaped declaration matches none of them, so `slices.md` and the parent ledger land … while the removal does not" | Caller-built list. |
| :1519–1525 | handover→end | P | — | *Ground now* is offered only where the §4.1 outcome is `PR opened`, `PR already existed`, or `nothing to commit` with the deliverable already on default | **N1** (structured outcome row and nothing-to-commit location) |
| :1534 | handover→end | P | — | "record the commit Phase 6's handoff pushed — `git … rev-parse HEAD`, since nothing has committed since" | (obtainable; an output field would be cleaner) |
| :1687–1691 | end | R | V2.1 | *Ground now* cedes control: commit-artifacts runs before the continuation, and the line is held for the report | — |
| :1775–1800 | end | P | — | The merge gate runs SRG §3.5's `branch-merged` on the handoff branch and on the recorded commit | **N7** |
| :1802–1815 | end | P | — | Complete, nested `/prd-ground` runs (Skill tool) start after this run's own commit-artifacts: "Each is a complete run, never an `--inline` one" | **N9** |
| :59 | end | R | V2.3 | A mid-walk *Cancel* after rows are written → refusal tail; *Stop here* → all of Phase 8 | per-stop tail profile |
| :59 | end | D | — | [EE-PRE] | wording |

**Restated rules.** :100–102 (preflight); :1687–1691 (commit-artifacts, with the narrower push / misrooted extent).

**Verdict: needs option** (N1, N7, N9).

## /brd-package (`brd-package.md`)

| file:line | part | class | V-id | departure | shared step must offer / which is right |
|---|---|---|---|---|---|
| :147–150 | start | R | V1.4(a), V1.1 | preflight-first | — |
| :136, :150 | start | **D** | V1.3 | The key set is never stated, yet step 2 reads every `--depends-on` key with `read-key` before the preflight. SRG §3 says "the keys … `read-key` reads off its arguments", which literally includes those keys. `/prd-ground` (:142) excludes them explicitly, and its reason is right. | **Latent bug:** a dependency BRD's unmerged `brd/` branch could be kept by B3 and reused by PH §2.2 rule 3 for this run's handoff. Fix: the shared preflight takes an explicit key list. |
| :215–234 | start | U | PH §6 | Step 5c reads `decisions.md`, the round records and the logs **before** `branch-check` (:246). PH §6 says `branch-check` runs "before anything reads or gates the folder's documents". The reason ("before any gate, so no gate's remedy lands one") is about `require-on-main`'s commit remedy; `branch-check`'s remedies commit nothing. A §6.2 *Switch* after 5c leaves 5c's verdict about a worktree the run then leaves. | Settle whether 5c moves after `branch-check`, or re-runs after a switch. The shared step needs a slot between resolve and `branch-check` only if 5c stays first. |
| :246 | start | R | PH §6 | `branch-check` `prefix: brd` | — |
| :248–300, :330–345, :428–436 | start | R+P | V4.3 | Several gated paths; row-F results are collected and the run stops once, naming every file or round collected | **N4** |
| :1446–1465 | handover | P (R by EF) | §3.3 EF | Consent is taken in Phase 7, two phases before §2 runs. Phase 7 tests "§2.1's gate conditions — each is a read", runs the probe, prints the flag / no-remote line, and carries the answer and `remote` to Phase 9: "taken there because the note's route depends on it" | **N3**: split prepare / ask from execute, with a gate-verdict output and the carried `remote` |
| :1465–1475 | handover | P | — | The command's own route question, and the note write, sit between the shared ask and the shared execute | interleaving |
| :1990–1996 | handover | R | PH §4.1 | *Declined by the user* line on options 2 and 3 | — |
| :1998–2026 | handover | P | — | It reads the outcome row (pushed / not) and each *Declaration unaccounted for* path, to settle the delivery-route item | **N1** (structured row and unaccounted paths) |
| :61 (Phase 8 stops) | handover/end | U | PH §4.1 | Consent answered in Phase 7, then a Phase 8 stop: no `Phase handoff:` line is printed. PH §4.1 says "a declined offer still prints its line" and has no row for a consent given and never executed. | Settle in PH: what line, if any, an answered-but-unexecuted offer prints. |
| :61 | end | R | V2.3 | later stops → refusal tail; writes stay uncommitted | — |
| :2167 | end | R | placement | line held | — |
| :61 | end | D | — | [EE-PRE] | wording |

**Restated rules.** :150–153 (preflight); :2162–2167 (commit-artifacts, with the narrower push / misrooted extent).

**Verdict: needs preparation.** The handover is interleaved with the command's own work: ask in Phase 7, route question and writes, then execute in Phase 9. The run either needs N3, or must fold the route question in after a single call. The key-set statement must also be added (latent bug). U and the PH §4.1 gap must be settled.

## /brd-interview (`brd-interview.md`)

| file:line | part | class | V-id | departure | shared step must offer / which is right |
|---|---|---|---|---|---|
| :153–159 | start | R | V1.4(a), V1.1 | preflight-first, before the gate (same ordering as `/prd-ground`) | — |
| :223 | start | R | PH §6 | `branch-check` `prefix: brd` | — |
| :227–245 | start | R | V4.3 | `require-on-main` on `code-grounding.md`; row F split | — |
| :229 | start | U | PH §4.0 | the same sibling implication as `brd-split.md:170`, with `brd-link.md` not covered | as brd-split |
| :348–371 | start | R+P | V4.2 | Step 8a reads a stop without stopping. If the row-C repair is **taken**, "every read steps 6 to 8 made stands on a checkout that is gone: **run this phase again from step 6**" | **N5** (whether row C's repair ran or was declined) |
| :69 | start/end | **D** | V4.2 | Ending early: "Two *Cancel*s are not stops: row C's repair offer in Phase 0 … decline what they offer, and the run goes on". That holds only for step 8a (:366). Step 6 (:232) maps "any stopping row → stop", and PH §3.3 does not define what *Cancel* returns. | **Latent bug:** two contradictory instructions at step 6. A literal run would go on past an unsatisfied grounding gate. Fix: restrict the sentence to step 8a; the shared `require-on-main` should define *Cancel* → `stopped: true, declined: true`. |
| :2268–2335 | handover | P | — | The defect-resolution offer and write come first, "before the probe below, so what it writes is in the set this phase hands off" | Command steps before the call. |
| :2339–2356 | handover | P | V3.4 | "execute §4.3 in full rather than its array alone", with the probe named and `remote` carried. The reason is the live failure quoted under [PROBE]. | This is the standard. The shared call makes it automatic, and the paragraph can go. |
| :2358–2380 | handover | R | PH §2.9 | `deliverable_paths` includes the parent's defect log, outside the folder; a log is declared where `status --porcelain` reports it changed (an emptiness test, so `-z` is not needed) | — |
| :2382–2393 | handover | P | — | Where a resolution was written and the handoff "commits nothing", it says so beside the outcome line and gives the manual commit | **N1** (a committed / not-committed field) |
| :2397–2409 | handover | R | V3.9 | no-new-round path → `nothing to commit` | — |
| :69 | end | R | V2.3 | later stops → refusal tail | — |
| :2684 | end | R | placement | line held | — |
| :69 | end | D | — | [EE-PRE] | wording |

**Restated rules.** :156–159 (preflight); :2679–2684 (commit-artifacts, with the narrower push / misrooted extent).

**Verdict: needs option** (N1, N5; fix the :69 contradiction first).

## /brd-reconcile (`brd-reconcile.md`)

| file:line | part | class | V-id | departure | shared step must offer / which is right |
|---|---|---|---|---|---|
| :219–225 | start | R | V1.4(a), V1.1 | preflight-first | — |
| :288 | start | R | PH §6 | `branch-check` `prefix: brd`, "the prefix of its first handoff" | — |
| :121 | mid-run | R | V5.2, V5.4, V4.2 | Cross-BRD guard: `branch-check` with no `prefix` on another root, its stop recorded and not stopped on; `require-on-main` "record, never write" | — |
| Phase 0 step 6 | start | R | V4.2 | the three stop-reading sites PH §3.7 names | — |
| :764 | handover | D | V3.4 | [PROBE] (first handoff) | **latent bug** |
| :764–791 | handover | R | V3.13, V3.1 | First handoff is mid-run (advisory, labelled "the review's handoff"); the run continues | the label input; mid-run call; state "branch created by this run's own handoff" for rule-3 reuse and for row B (listed in §0.1) |
| :768–777 | handover | D | PH §2.9 | The first handoff passes `title` and no `body_facts`, where every other call in the group passes them | The PR body carries only derived paths. Not a bug: the body is thinner. A required parameter in the shared call surfaces it. |
| :2912–2916 | handover | P | — | lineage `accept` before the second handoff ("Never `stamp` it — step 7a says why") | hook before staging |
| :2918 | handover | D | V3.4 | [PROBE] (second handoff) | **latent bug** |
| :2924–2952 | handover | R | V3.13, V3.7 | The second handoff reuses the first's branch (rule 3); its declared paths lie outside the folder (dependents' `decisions.md`, the parent's logs) | — |
| :64 | end | R | V2.3 | Stops after Phase 2's handoff take the refusal tail, and the commit lands on the cut `brd/` branch | — |
| :3304 | end | R | placement | line held | — |
| :64 | end | D | — | [EE-PRE] | wording |

**Restated rules.** :222–225 (preflight); :3299–3304 (commit-artifacts, with the narrower push / misrooted extent); :785–800 explains PH §4.1's two-line rule (same extent).

**Verdict: needs option** (V3.13 label and mid-run call, with persisted run-created-branch state; V5.4 / V4.2 non-stopping reads).

---

## Cross-command note (not one command's departure)

Stops after a write in a later phase leave each command to choose its tail (SRG §4: "what its tail does is that command's to state").
- `/prd-ground` (:2494–2510) runs maintenance and feedback on its Phase 3/5/7 stops, and gives a reason.
- `/epics`, `/prd-proposal`, `/brd-proposal`, `/brd-intake`, `/brd-split`, `/brd-package`, `/brd-interview`, `/brd-reconcile` and `/promote-decisions` give their post-write stops the refusal tail (no maintenance, no feedback), with no reason given.

**U:** whether a stop after real work should capture feedback is a family rule no reference states. The shared end step must offer the profiles either way.

## Summary of counts

| class | count |
|---|---|
| R | 79 (8 of them R+P) |
| P | 31 |
| D | 22 |
| U | 7 (6 in the tables + the cross-command note) |

D breakdown:
- 7 × [PROBE]: prd-ground, prd-proposal, brd-proposal, brd-intake, brd-split, and brd-reconcile ×2.
- 8 × [EE-PRE].
- 2 × own `$SPECS_PATH` stop (harvest, promote).
- 1 × each of the following: the harvest guard-cause list; promote's citation load; the brd-package key set; the brd-interview row-C extent; the brd-reconcile `body_facts`.
- epics' restated switching rule is listed under restated rules, not counted here.

Counts are table rows, tallied by an `awk` over this file's class column; a row marked R+P counts once, as R.

## (1) D items that are latent bugs today

1. **[PROBE]**: `prd-ground.md:2243`, `prd-proposal.md:720`, `brd-proposal.md:793`, `brd-intake.md:1472`, `brd-split.md:1401`, `brd-reconcile.md:764` and `:2918`. Each quotes the array without naming §2.1's probe or the flag / no-remote line. `brd-interview.md:2351–2353` records a live run that, from that same wording, offered a recommended push-and-PR on a repository with no `origin`. **The shared handover call fixes all seven.**
2. **`brd-package.md:136/:150`**: the run key set is unstated, while `--depends-on` keys are read with `read-key` before the preflight. SRG §3's literal wording ("the keys `read-key` reads off its arguments") puts them in the set. B3 could then keep a dependency BRD's `brd/` branch, and PH §2.2 rule 3 could reuse it for this run's handoff. `prd-ground.md:142` states the exclusion and the reason. **A shared preflight that takes an explicit key list fixes it.**
3. **`brd-interview.md:69` vs `:232`**: the Ending early paragraph says a row-C repair *Cancel* "in Phase 0" lets the run go on. That is true of step 8a (:366) only. At step 6 the grounding gate maps every stopping row to a stop. This is two live contradictory instructions. **Standardizing does not fix it by itself:** restrict the sentence, and have the shared `require-on-main` define *Cancel*'s return.

Not bugs: harvest :27's incomplete cause list (wrong message, right action); brd-reconcile :768's missing `body_facts` (thinner PR body); [EE-PRE] (SRG §4 step 1 covers a run with no preflight); the two own `$SPECS_PATH` stops (less helpful, not wrong).

## (2) Options the shared step must offer that the contract does not list

- **N1** — §4.1 outcome as structured fields: the row, the nothing-to-commit location variant, the branch, the PR URL, committed or not, and the *Declaration unaccounted for* paths. Needed by brd-split :1519 and :1775, brd-package :1998–2026, brd-interview :2382.
- **N2** — a caller preamble slot printed before §4.3's flag / no-remote line (epics :950).
- **N3** — prepare / ask returns a §2.1 gate verdict and `remote` without executing; execute later on the carried answer. Needed by brd-package Phase 7 → 9. The contract §8.1 split has no gate-verdict output, and PH §4.1 has no rule for an answered offer whose execution never comes.
- **N4** — `require-on-main` returns the stop (§4.4's four parts as fields) instead of printing it. Callers then defer, order or aggregate stops: prd-ground :262–275 (two gates, a fixed stop order), brd-proposal :424–447 (one stop for a sweep), brd-package :296ff, :330ff and :428ff (row F collected). V4.2 lists only the callers that never stop.
- **N5** — `require-on-main` reports whether row C's repair was taken (the checkout switched) or declined, and defines *Cancel*'s return. Needed by brd-interview :366–371, which re-runs from step 6 after a repair.
- **N6** — a standalone `owner-repo` for any repository path: harvest :28 for the specs repository; `ap` :84 and :214 for the architecture repository.
- **N7** — a standalone `branch-merged` (SRG §3.5) for a named branch and for a recorded commit (brd-split continuation, :1775–1800).
- **N8** — a tail with **no cost member at all**: no `emit-cost` and no `skip-cost` checkpoint advance (harvest :10 and :56, promote :102). V2.10 covers `--skip-costs` only.
- **N9** — run state scoped to one invocation, and safe when a complete nested run starts after the parent's commit-artifacts in the same session (brd-split *Ground now* → `/prd-ground` via Skill, :1802ff). The parent's row-B ownership, `Environment:` line and B4 memory must not leak into the child. Contract §8.2 says "per-invocation" but not nesting.
- **N10** — a lookup of PH §4.0's register of declared artifacts. epics :920 loads the whole PH for it "the load Phase 7.5 makes next".

Per-stop tail profiles must cover:
- full tail;
- full tail with no offer (brd-proposal operator ends);
- maintenance + feedback + cost + commit without `resume.md` (prd-ground);
- refusal tail;
- commit only (harvest, promote);
- no tail (prd-ground `TYPED_ONLY`).

These are V2.2–V2.4 in kind, but the shared call needs them as named choices.

## (3) Commands marked `needs preparation`

- **/brd-package.** Its consent is asked in Phase 7. Its own route question and its note, prompt and bundle writes follow. §2 executes in Phase 9 on the carried answer and `remote`. So the shared handover is interleaved with command work.

  Preparation needed:
  1. adopt N3, or restructure so the route question follows a single handover call (not possible as is: the note it writes is in the handoff's declared set);
  2. state the run key set, excluding `--depends-on` keys (latent bug 2);
  3. settle U on step 5c vs `branch-check` order (:215 vs :246);
  4. settle what line an answered-but-unexecuted offer prints when a Phase 8 stop follows the Phase 7 consent.

No other command in group C needs preparation:
- *ready*: `/prd-proposal`, `/brd-intake`.
- *needs option*: `/harvest-decisions`, `/promote-decisions`, `/epics`, `/prd-ground`, `/brd-proposal`, `/brd-split`, `/brd-interview`, `/brd-reconcile`.

`/brd-interview` should have its :69 contradiction fixed before or with the switch.

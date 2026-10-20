# Loader map: `workflows-core:specs-repo-git`

File: `/workspace/ai-workflows/plugins/workflows-core/references/specs-repo-git.md`, 1,094 lines, **118,635 characters** (119,617 bytes; it contains `§`, `—`, `⚠`, `′`). All sizes below are characters including each line's newline, measured with a Python counter over 1-indexed line ranges. Read end to end before mapping.

## Callers and what they expect

- 28 command files invoke both entry points through the loader (`args: "specs-repo-git specs-preflight"` 28 times, `args: "specs-repo-git commit-artifacts"` 29 times; `docs-workflows/commands/document.md` calls `commit-artifacts` twice, once per mode).
- Six `workflows-core` commands (`/feedback`, `/prompt`, `/prompt-brainstorm`, `/prompt-grill-me`, `/diagnose-session`, `/frames`) cite the file **by path** (`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md`), not through the loader, so they always get the whole file whatever the loader does.
- No agent cites the file.
- The citing lines expect the loaded text to hold: §1 rule 1 (`git -C`), §3.1 (the misrooted notice), §3.3 G0 (`specs_git: blocked`), §5 (the guard notice), §6 (the `Specs repo:` line), §2.1 (the bounded paths), §2.2 (the prefixes), §4 step 5 (push rules), §4's cede-control exception (`/brd-split`), §8 (session-branch mode), and §3.2 (the run key set, which `security-workflows/commands/scan.md` cites before invoking).

## Section map

| Section | Lines | Chars |
|---|---|---|
| Preamble: title, intro (3–8), Purpose (10–16), Scope (18) | 1–19 | 1,822 |
| §1 Hard rules (rules 1–8; rule 8 = 52–75, 1,794) | 20–76 | 3,963 |
| §2 heading | 77–78 | 31 |
| §2.1 Paths | 79–230 | 18,336 |
| — shapes code block | 81–96 | 1,554 |
| — prose: security register (97), documentation shape (99), `<docs-repo-slug>` definition (101–104) and rationale (106), inner `dev-workflows/` (108), single-file shapes (110–128), history (130–147), screenshots (149–162), sources (164–170) | 97–171 | 12,649 |
| — staging procedure: step 1 (`-z`), step 2 classifier, exclusion rationale (203–219), step 3, `-A` note (223–229) | 172–230 | 4,118 |
| §2.2 Branches | 231–247 | 814 |
| **§3 `specs-preflight` intro** | 248–265 | 1,716 |
| §3.1 Gate | 266–291 | 10,550 |
| §3.2 Resolution inputs | 292–361 | 5,697 |
| §3.3 Stage 1 — guards | 362–374 | 2,038 |
| §3.4 Stage 2 — flush leftovers | 375–428 | 5,164 |
| §3.5 Stage 3 — branch disposition | 429–512 | 10,824 |
| §3.6 Why B3 exists | 513–528 | 3,207 |
| §3.7 Detached HEAD is blocking | 529–549 | 1,386 |
| **§4 `commit-artifacts`** (intro 552–618, steps 1–7 619–857) | 550–857 | 22,504 |
| §4.1 Where the commit lands | 858–882 | 3,011 |
| §5 Notice contract | 883–985 | 6,211 |
| §6 The outcome line | 986–1028 | 9,280 |
| §7 Caller contract | 1029–1050 | 1,342 |
| §8 Session-branch mode (intro 1051–1054, 692) | 1051–1094 | 10,740 |
| — §8.1 / §8.2 / §8.3 / §8.4 | 1055–1064 / 1065–1075 / 1076–1084 / 1085–1094 | 2,205 / 3,389 / 2,637 / 1,817 |

### What a mechanical extractor has to deal with

- **The headings name both entry points literally**, inside backticks and between other text: `## 3. \`specs-preflight\` — run start` (line 248) and `## 4. \`commit-artifacts\` — terminal step` (line 550). An extractor must match the backticked token, not the whole heading.
- **§4's body runs on into `### 4.1`.** An extractor that stops at the next heading of any level cuts off §4.1, which `commit-artifacts` needs. It has to stop at the next `## `.
- **Several terms are defined only in bold run-in paragraphs, list items or table rows, never under a heading**, and other sections use them:
  - `branch-merged <ref>` (442) and `branch-key <branch>` (452), both in §3.5.
  - `push-scope` (763), a bullet inside §4 step 5.
  - The §3.4 catch-up (379), which §4 step 2 runs.
  - `<record>` (§1 rule 8), the only definition of the push-refusal record's path.
  - `<default-ref>` (303).
  - ARTIFACT/OTHER (194).
  - `<docs-repo-slug>` (101).
  - `specs_git: misrooted` (286) and `specs_git: blocked` (G0 row, 371).
  - `session_branch` (1059).

  None of these can be addressed by heading.
- **§4's steps 1–7 are list items, not headings.** "§4 steps 2–6", which `specs-preflight` depends on, cannot be cut out at heading granularity.

---

## Entry point 1: `specs-preflight`

### 1. Definition

`## 3.` heading, lines **248–549** (§3 intro plus §3.1–§3.7), **40,582 chars**. The heading names it literally.

### 2. Dependencies inside the file (transitive)

| Part | Lines | Chars | Why it is needed |
|---|---|---|---|
| Preamble: intro and Scope | 1–19 | 1,822 | Scope (18) is operative: only §2.1 paths, only inside `$SPECS_PATH`, never the cwd or a code or docs repo, neither entry point opens a PR. Intro (3–8): the orchestrator owns printed output. Purpose (10–16, 517) is rationale. |
| §1 Hard rules 1–8 | 20–76 | 3,963 | Stated once for both entry points:<br>• rule 1: `git -C`, never `cd`.<br>• rule 2: `add -A -- <paths>`.<br>• rule 3: which branches B2, B4 and the retry may switch, delete or push.<br>• rule 4: no force, `-D`, merge, rebase or reset, and no `index.lock` deletion. The catch-up cites it for `--no-rebase`.<br>• rule 5: never fatal.<br>• rule 6: no trailer on the flush commit.<br>• rule 7: prompt-free, and the silence rule.<br>• rule 8: the **only** definition of `<record>`. B2 removes the record, the retry reads it through §4 step 5, and step 6 writes it. |
| §2.1 shapes block | 77–96 | 1,600 | The ten shapes in readable form. |
| §2.1 staging procedure and `-A` note | 172–230 | 4,118 | The ARTIFACT/OTHER classifier that G1 (OTHER) and the §3.4 flush (ARTIFACT) use: the `-z` read, the second field of a rename record, the reserved-subdirectory exclusion, and `add -A --`. |
| §2.2 Branches | 231–247 | 814 | The plugin-owned pattern; a named branch is committed on but never pushed; a detached HEAD goes to G0. |
| **§4 steps 2–6** | 653–854 | 14,480 | **Not obvious, and the critical one.** §3.4 says "commit them … per §4 steps 2–6". The retry uses step 5's three conditions and **`push-scope`, which is defined only in step 5**. B4's report counts with `push-scope`. Step 4's commit by pathspec and its index restore, and step 6's failure taxonomy with its flush-specific `Specs preflight:` messages, also live only here. |
| §4.1 | 858–882 | 3,011 | Step 5's first condition and §5's direct-`/implement` variant cite §4.1 for the code branch a direct `/implement` run cuts in the specs repo. |
| §5 Notice contract | 883–985 | 6,211 | §3.3: "Every guard emits the §5 notice". This covers the G0, G1 and G2 blocks, the session-mode variant of G2 (964) and the direct-`/implement` variant (966–984). |
| §6 refusal remedy text | 986–994, 1003–1004, 1021–1024 | 4,523 | Step 6's in-flush message embeds "<the remedy §6's push-refused line gives>" (1004). Line 1021 gives the `<record>` and config-key wording and the could-not-record wording. Line 1023 rewrites that remedy in session-branch mode, and says the default-branch refusal turns the mode on. Safe practice is to take **§6 whole (9,280)**, because those rows and paragraphs interleave. |
| §8 whole | 1051–1094 | 10,740 | §3.2 resolves the mode (§8.1, which needs §8's intro for the script path, `--specs`, the JSON output and exit-2 handling). The §3.4 flush commits through §8.2 and pushes per §8.4. B2, B4, the catch-up and the re-run switch-back are wrapped in §8.3's `lift`/`put-back`, and "the preflight ends with `put-back` in the mode". |

The internal cross-reference chain closes on itself: the §3.4 flush leads to §4 step 2, and step 2 leads back to "§3.4's catch-up". No dependency leaves the set above.

**Not needed by `specs-preflight`'s own steps:**
- §2.1 prose, 97–171 (12,649). See *Sibling consumers* below: 99–107 is needed by other references in the same run.
- §4's intro, refusal tail, step 1, step 3 and step 7: 552–652, 660–663 and 855–857 (8,222).
- §7 (1,342).

### 3. Other reference files it relies on

- **Executed at run time:**
  - `workflows-core:addressing` §3 `specs-root-check`. §3.1 (280) says "run the tests … exactly as that entry point defines them", and the notice it prints is that entry point's stop text. Address-less callers such as `/upgrade`, `/docs-init` and `/feedback` never load `addressing` themselves (`grep` finds no `addressing` load in those files), so this citation must survive any slicing.
  - `${CLAUDE_PLUGIN_ROOT}/scripts/session-branch.py`, with its `mode`, `commit`, `lift` and `put-back` subcommands.
- **Caller-side input:** `workflows-core:addressing` §1 `read-key`, the source of the run key set, which also sets the order of the steps.
- **Meaning only (rationale, or what another entry point does):**
  - `phase-handoff` §2.1, §2.2, §2.5, §3 rows B, B′, C, D, E and I, and §4.3.
  - `escalation-rules`' *Required path environment variable unset*.
  - `cost-emission` §8 and §9, `feedback-emission` §2, `followup-emission` §2, `session-hygiene` §1.
  - `prd-format`, and `branch-naming` §2 (the script implements the identity rungs).
  - `addressing` §2 (the exclusion regex already restates it inline).
  - The §2.1 sources: `source-truth` §7.5, `security-register-format` §1, `docs-workflows:finish-and-handoff` §5.

### 4. Minimal safe set

| Set | Chars | Share of file |
|---|---|---|
| Strict closure: 1–19, 20–76, 77–96, 172–230, 231–247, 248–549, 653–854, 858–882, 883–985, 986–994, 1003–1004, 1021–1024, 1051–1094 | **91,864** | 77.4% |
| **Minimal safe set:** strict + §6 whole + `<docs-repo-slug>` 99–107 for sibling consumers (next section) | **101,794** | **85.8%** |
| Heading granularity, no restructure: every `##` except §7 | 117,294 | 98.9% |
| Whole file | 118,635 | 100% |

### 5. Verdict: **SAFE-WITH-RESTRUCTURE**

- **Extracting §3 by heading alone is UNSAFE.** It loses:
  - §1, including the only definition of `<record>`;
  - the §2.1 classifier;
  - the §4 commit, restore and push machinery, with `push-scope`;
  - the §5 notice blocks;
  - the §6 remedy text;
  - §8 entirely.

  The §3.4 flush would then `git commit` without a pathspec, which takes whatever the user had staged. It could also push the user's own commits (no `push-scope`), retry a branch `origin` refused (no `<record>`), and skip the session-branch overlay.
- **Heading extraction plus a declared list loses nothing** only when the list is every `##` section but §7 (98.9%). That is SAFE-AS-IS in name only; it saves 1.1%.
- **A real saving needs these edits first:**
  1. Put §4 steps 2, 4, 5 (with `push-scope`) and 6 under a heading of their own, so the preflight can depend on them without §4's intro, refusal tail and steps 1, 3 and 7.
  2. Give the §3.4 catch-up paragraph (379) its own heading. `commit-artifacts` step 2 needs it, and it does not need the flush or the retry.
  3. Gather the refusal remedy wording (§6 rows 1003–1004, 1021, 1023) in one addressable place, or declare §6 whole.
  4. Give `<docs-repo-slug>` (99–107) a heading. Then either keep it in the preflight's declared list, or make it an entry point that `cost-emission` §8, `feedback-emission` §2 and `/document` load.

### 6. Rationale, history and worked examples inside the minimal set

| Lines | Chars | What | Needed by a model executing the steps? |
|---|---|---|---|
| 10–16 | 517 | Purpose | No |
| ~60–63 (inside rule 8) | ~300 | why a file and not git config (read-only `.git/config`) | No: the fallback to the config key is stated as a step |
| inside 175–193 | 384 | the `zahlungsauslösung` example for `-z` | No: `-z` and the rename handling are steps |
| 203–219 | 1,237 | exclusion rationale and the maintainer rule "when the register gains a name, this pattern gains it too" | No: the regex encodes it |
| 223–229 | 537 | `-A` history (git < 2.0) | No |
| 276 | ~1,560 of 1,606 | caller taxonomy for an unset `$SPECS_PATH` | No: the operative clause is "unset → silent no-op"; callers stop before reaching it |
| inside 278 | 281 | history ("Under the old blanket silence…") | No |
| 280 | ~1,200 of 2,128 | worked examples of correct and wrong roots (`<repo>/specifications`, `<repo>/specs`) | **Partly yes:** they say which of the two notices fires and that a correct root stays quiet |
| 282 | ~800 of 1,928 | which caller prints which notice, and in what order | No (caller-facing); the operative "skip where the inside-tree notice fired" must stay |
| 286 (tail) | ~350 | why emitters go report-only | No |
| 288–290 | ~1,000 of 1,843 | what the other three entry points do under `misrooted` | No for the preflight; yes for sibling references |
| 305 | 866 | why `<default-ref>` has two cases | Mostly no; the last sentence ("none names `origin/<default>` literally") is operative |
| 326–353 | 2,004 | `/create-prd` contributes a key; neither route is keyless; a key is a folder identity | **Yes for edge cases:** it stops a model from passing an empty key set on the `/idea` or BRD route, which leads to B4 and a duplicate branch |
| inside 379 | 440 | why the catch-up exists | No |
| 392–402 | 776 | `push-scope` never reads `@{u}` (history) | Helpful: it guards against an `@{u}` shortcut that exits 128; step 5 already encodes it |
| ~420–424 | ~330 | why the other-branch retry exists | No |
| 448 | 491 | ancestry-only history | No |
| 472–484 | 972 | why `branch-key` resolves rather than extracts; the `PRODUCT-1234-2fa-rollout` example | **Helpful:** the worked example of the separator boundary |
| 485–491 | 507 | two-segment keys | No |
| 505–511 | 543 | no auto-merge (a guard for maintainers) | No |
| 513–528 (§3.6) | 3,207 | why B3 exists | No: the B3 row ("Stay on it") is complete. It is a guard for maintainers |
| 529–549 (§3.7) | 1,386 | why G0 blocks | No: the operative parts are in the G0 row, §4 step 1 and §5 |
| 703–706 | 245 | the commit form is shared with `phase-handoff` and the docs commands | No for this entry point; sibling references rely on step 4 being loaded |
| ~735–738 | ~250 | upstream history (forks) | No |
| ~774–778 | ~400 | why `push-scope` is not measured against the remote as a whole | Helpful |
| inside 783–792 | 569 | what a failing commit means (somebody else's, or a hook's) | **Yes:** it selects the hook variant of §6's `push-scope` line |
| 826–827, 844–846 | 292 | why the refusal is recorded; why the switch is needed | The second: yes-ish, it stops the model from dropping the `switch` from the message |
| 885–888, 904–906 | ~500 | the notice contract's rationale | No |
| 1074 (tail) | 238 | why `session-branch.py` runs no hooks | No |

Roughly 15–17k of the minimal set is rationale. About 4–5k of that (the key-set paragraphs, the `branch-key` example, the root examples, the `push-scope` failure meaning) does help with edge cases.

---

## Entry point 2: `commit-artifacts`

### 1. Definition

`## 4.` heading through the end of `### 4.1`, lines **550–882**, **25,515 chars**. That is §4 at 22,504 plus §4.1 at 3,011. The heading names it literally, and §4.1 belongs to it.

### 2. Dependencies inside the file (transitive)

| Part | Lines | Chars | Why it is needed |
|---|---|---|---|
| Preamble: intro and Scope | 1–19 | 1,822 | Scope is operative, as for the preflight. |
| §1 Hard rules 1–8 | 20–76 | 3,963 | Rule 4 sanctions step 4's `restore --staged` and §8.3's `lift`. Step 4 cites rule 6 (no trailer). Rule 7: one outcome line. Rule 8 is the only definition of `<record>`, which step 5's third condition reads, step 6 writes, and §6's refused rows name. |
| §2.1 shapes and staging procedure | 77–96, 172–230 | 5,718 | Step 1's test for G0 on a run with no preflight needs "step 2's enumeration would stage ≥1 ARTIFACT path". Step 2 stages. Step 5's `push-scope` tests that every path is ARTIFACT. |
| §2.2 | 231–247 | 814 | Step 5's first condition (plugin branch or default branch). |
| §3.1 whole | 266–291 | 10,550 | Step 1: "All of §3.1's environment conditions". The three dispositions decide the silent no-op. Defines `specs_git: misrooted` and what it leaves alone. Holds the notice step 1 and §6 re-emit verbatim. |
| §3.2 default branch, default ref, freshness | 292–312 | 2,204 | `<default-ref>` is used by the catch-up, by §6's session row and by §8. Step 5 needs "the default branch as §3.2 names it, resolved here the same way on a run that ran no preflight". §8.1's `mode --default <default>` needs it too. |
| §3.2 key-set note | 355–361 | 390 | "`commit-artifacts` resolves its own key independently — a single key, at the end of the run (§4 step 4)": the key in step 4's commit message. |
| §3.3 guards table | 362–374 | 2,038 | G0 is the flag step 1 gates on. G1 explains why step 4 commits by pathspec. G2 is step 5's first condition. Step 7 repeats the notice "when a guard fired at §3.3". |
| §3.4 catch-up (and its `misrooted` lead-in) | 375–380 | 1,961 | Step 2: "On the default branch, run §3.4's catch-up first". The catch-up is defined **only** there. |
| §3.4 `push-scope` / `@{u}` note | 392–402 | 776 | Conservative: why step 5's base never reads `@{u}`. |
| §3.7 | 529–549 | 1,386 | Conservative: step 1 cites "(§3.7)". |
| §4 and §4.1 | 550–882 | 25,515 | The entry point itself. |
| §5 whole | 883–985 | 6,211 | Step 1 prints the G0 block for the first time on a run with no preflight. Step 7 repeats the G1 or G2 block verbatim, including the session and direct-`/implement` variants. |
| §6 whole | 986–1028 | 9,280 | Steps 3, 5, 6 and 7 all emit a §6 line. |
| §7 | 1029–1050 | 1,342 | Conservative: §6's intro defers placement to "its own contract (§7)"; rule 3 says to emit the line exactly once. |
| §8 whole | 1051–1094 | 10,740 | Step 1 resolves the mode (§8.1) on a run with no preflight. Step 2 wraps the catch-up in §8.3, step 4 commits through §8.2, and step 5 pushes per §8.4. §6 carries the session rows. |

**Not needed by `commit-artifacts`:**
- §3 intro, 248–265 (1,716).
- §3.2 run key set, 313–354 (3,103).
- §3.4 flush and retry bullets, 381–391 and 403–428 (2,427).
- §3.5 (10,824) and §3.6 (3,207).
- §2.1 prose, 97–171 (12,649).

### 3. Other reference files it relies on

- **At run time:**
  - `session-branch.py`.
  - `workflows-core:addressing` §3 `specs-root-check`'s stop text, re-emitted verbatim where that stop set the flag. The text is in the run's own earlier output.
- **The refusal-tail paragraph (568–618) names what the other members of the tail do on a refusal:**
  - `feedback-emission`'s `emit-auto` and `emit-block`;
  - `followup-emission` §6;
  - `workflows-core:run-flags` `skip-cost`;
  - `cost-emission` §8, §9 and §11;
  - `session-hygiene` §1;
  - `/prd-ground`'s `PRD_GROUND_TYPED_ONLY`, the one stop that takes no tail at all.

  The commit step itself needs none of them; its own behaviour on a refusal is the "This step runs" bullet (598–601).
- **Meaning only:** `phase-handoff` §2.1 (why `origin`), §2.4 (the same commit form), §2.5 (an unwritable config), §2.9 and §4.1 *Commit failed*; `architecture-promotion` §11.2; `branch-naming` §2.

### 4. Minimal safe set

| Set | Chars | Share of file |
|---|---|---|
| Strict closure: 1–19, 20–76, 77–96, 172–230, 231–247, 266–291, 292–312, 355–361, 362–374, 375–376, 379–380, 550–882, 883–985, 986–1028, 1051–1094 | **80,637** | 68.0% |
| **Minimal safe set:** strict + 377–378, 392–402, §3.7, §7 | **84,710** | **71.4%** |
| `###` granularity, no restructure: preamble, §1, §2.1, §2.2, §3.1–§3.4, §3.7, §4 + §4.1, §5–§8 | 102,889 | 86.7% |

### 5. Verdict: **SAFE-AS-IS**

Every dependency can be addressed at `###` granularity. A heading extractor with the declared list {preamble, §1, §2.1, §2.2, §3.1, §3.2, §3.3, §3.4, §3.7, §4 with §4.1, §5, §6, §7, §8} loses nothing, at 86.7%. Reaching 71.4% means splitting §3.2's run-key-set paragraphs (313–354) and §3.4's flush and retry away from the catch-up: SAFE-WITH-RESTRUCTURE.

The list is easy to get wrong in three places:
- **§3.4 looks like the preflight's own**, but `commit-artifacts` step 2 runs its catch-up.
- **§1 looks generic**, but it holds the only definition of `<record>`.
- **§3.1 and §3.2 look like the preflight's**, but step 1's gate and step 5's default branch are defined there, and a run that refused before its preflight never loaded them.

### 6. Rationale, history and worked examples beyond those listed for the preflight

| Lines | Chars | What | Needed? |
|---|---|---|---|
| inside 555–566 | ~500 | why "last" stops protecting once control leaves the command | Helpful: it marks the exception as narrow |
| 576–597 | 1,762 | feedback, follow-ups, cost and `resume.md` on a refusal: each member's own rules restated | No for the commit step; callers and `addressing` rely on it (see below) |
| 603–617 | ~900 of 1,155 | why the tail is not keyed on writes under `$SPECS_PATH` | No, but the `PRD_GROUND_TYPED_ONLY` "no tail" rule inside it is operative for that caller |
| inside 623–638 | ~600 | why the flag outcome takes precedence | Helpful |
| inside 687–690 | 60 | "measured on git 2.43" | No |
| §7 | 1,342 | caller contract (for command authors) | No |

---

## Sibling consumers: the most important risk

Today the preflight's whole-file load leaves all 118,635 characters in context for the rest of the run, and **other references cite sections of this file by path without loading it**. They depend on that. Anything they cite that runs **between the preflight and `commit-artifacts`** has to be in the preflight's slice, or they need a load of their own.

| Consumer | Cites | When it runs | In the preflight's minimal safe set? |
|---|---|---|---|
| `cost-emission` §8 rung 2 (line 566); `feedback-emission` §2 tier 2 (line 120); `docs-workflows/commands/document.md` 1770 and 1909 | `<docs-repo-slug>` definition, §2.1 lines 99–107 (5,173). The two references each say "**cited, never re-derived here**" | the emitter tail, before `commit-artifacts` | **Only because it was added.** It is not in either entry point's own closure. |
| `phase-handoff` (`handoff-to-main`, `require-on-main`) | §3.5 `branch-key` and `branch-merged`; §3.2 `<default-ref>`; §4 step 4 commit and restore; §8.3 `lift`/`put-back`; §2.1 shapes and `-z`; §1 rules 1–4; §3.3 G0/G2; §3.1 | mid-run | yes |
| `docs-workflows:finish-and-handoff` (line 43) | §4 step 4 commit and restore form | mid-run | yes (653–854) |
| `dev-workflows:code-handoff` | §1 rules, §2.1, §3.1, §3.3 G0, §3.7 | mid-run | yes |
| `addressing` (`resolve-address`, `specs-root-check`, line 513) | §2.1 classifier, §3.1, §3.3 G0, **§4's refusal tail (568–618)** | Phase 0 | §2.1, §3.1 and §3.3 G0: yes. The refusal tail: **no**. `addressing` restates the outcome ("the cost entry and the terminal commit, and no feedback, follow-ups or `resume.md`"), so the risk is low. |
| `followup-emission`, `session-hygiene`, `security-register-format`, `branch-naming`, `implementation-format`, `bundle-packaging`, `architecture-*` | §2.1, §2.2, §3.1, §3.5, §4, §6 (`push…` line), §8 | various | yes (§6 whole is in the safe set) |

**The drop of `<docs-repo-slug>` would fail silently, in a way the file itself records.**
1. A loader built from the entry points' own closures drops lines 99–107.
2. The emitters then derive the directory without its one-segment flattening.
3. The `^documentation/[^/]+/dev-workflows/` classifier puts the entry in OTHER, so it is never staged.
4. §3.3 G1 then fires on every later preflight of every caller.

Lines 130–147 record this exact failure mode five times.

---

## Parts no requested entry point needs

The union of both strict closures is 1–96, 172–1028 and 1051–1094: **104,645 chars (88.2%)**. What remains, **13,991 chars (11.8%)**:

| Lines | Chars | What |
|---|---|---|
| 97–98 | 899 | the security register is bookkeeping (the regex encodes it) |
| 99–107 | 5,173 | documentation shape, **`<docs-repo-slug>` definition** and its rationale. **Needed by sibling references; keep it in the preflight's set.** |
| 108–109 | 825 | the inner `dev-workflows/` names the family; no new branch prefix |
| 110–129 | 2,195 | single-file shapes: why files and not folders; `release-notes.md` left the set |
| 130–148 | 1,752 | history of shapes missed, and the maintainer rule to re-derive |
| 149–163 | 1,311 | screenshots are not a shape (`/document` excludes them itself) |
| 164–171 | 494 | sources |
| 1029–1050 (§7) | 1,342 | caller contract; carried conservatively by `commit-artifacts` |

Without the slug paragraph, what is genuinely unneeded at run time is about 8,800 chars (7.4%).

## "Usually nothing to do" machinery

These are checks whose common outcome is a no-op: on a clean default branch, with no guard, the mode off, and a successful push.

| Machinery | Lines | Chars | Common outcome |
|---|---|---|---|
| §1 rule 8, the push-refusal record | 52–75 | 1,794 | no record stands |
| §3.1 failed-gate dispositions; `specs-root-check` and `show-prefix` tests; `misrooted` semantics | 274–291 | 10,212 | the gate passes and both tests stay quiet |
| §3.3 guards G0/G1/G2 | 362–374 | 2,038 | no guard fires |
| §3.4 catch-up, flush, push retry, other-branch retry | 377–428 | 5,129 | not behind; no leftovers; no plugin branch holds unpushed commits |
| §3.5 B2/B3/B4, `branch-merged`, `branch-key`, re-run switch-back | 429–512 | 10,824 | B1 (on the default branch): nothing |
| §3.6–§3.7, rationale for those branches | 513–549 | 4,593 | — |
| §4 cede-control exception and refusal tail | 555–618 | 5,208 | an ordinary run, no refusal (the exception covers three commands) |
| §4 step 1 flag tests and the G0 test for a run with no preflight | 619–652 | 2,513 | passes |
| §4 step 4 index restore | 687–702 | 1,107 | nothing to restore (no hook rewrote anything, nothing pre-staged) |
| §4 step 5 nowhere-to-push states (`pushRemote`, branch deleted on the remote, record stands) | 724–762 | 2,767 | none applies |
| §4 step 6 failure taxonomy | 805–854 | 4,087 | the push succeeds |
| §5 notice blocks | 883–985 | 6,211 | no guard fires |
| §6 rare rows and appendices (everything but *pushed* and *nothing to commit*) | 996–1007, 1009–1013, 1015–1028 | 8,806 | one of the two common rows |
| §8 session-branch mode | 1051–1094 | 10,740 | `mode` prints off |

Together these come to **75,991 chars, 64.1% of the file**. Two themes cut across that list:
- **Session-branch mode:** §8 plus its inline sentences at 403–407, 440, 708–709, 964, 996–998 and 1023, **15,563 chars**.
- **`misrooted`:** 280–291, 364, 377, 450 and 1012, **9,266 chars**.

Every one of these checks still has to be evaluated on every run, because each guards a silent-loss state: a commit no ref can reach, the user's staged changes swept into the commit, the user's commits pushed, a refused branch pushed again, a branch the remote deleted recreated. So "usually a no-op" here means "usually prints nothing", never "safe to omit".

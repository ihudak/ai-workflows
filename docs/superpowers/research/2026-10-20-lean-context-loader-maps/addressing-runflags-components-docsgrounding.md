# Loader map: addressing, run-flags, components, docs-grounding

Read-only mapping of the entry points that callers ask the `workflows-core:reference` loader to run. Tree at `b1f3adba` (main). Every reference is under `plugins/workflows-core/references/`.

## Conventions

- **Characters** are Unicode code points with newlines included. They were counted with `scratchpad/loader-map/rc.py <file> a-b …`, which prints per-range counts and the union. `wc -c` gives bytes, which run higher where a file has `—`, `§` or `→`: `addressing.md` is 64,114 characters and 64,547 bytes.
- **Section-granular minimal set** means what an extractor would return if it took whole headed blocks: the entry point's own heading plus a declared list of other headings. **Tight set** means the same thing cut below the heading level, where a single line or table row is the only part a dependency needs. **Steps-only floor** means the minimal set less the rationale, history and maintainer text listed under item 6. The floor is given for scale only; it is not a recommendation.
- **Collateral dependency** is something no entry point needs, but which a caller uses at a *later* step. The caller cites it bare (`workflows-core:docs-grounding`, `components` §2) and makes no loader call. It works today only because an earlier loader call read the whole file into context. A narrowed loader would drop it silently.
- Caller sets come from `grep -l 'args: "<ref> <entry>' plugins/*/commands/*.md plugins/*/agents/*.md plugins/*/references/*.md`.

---

## 1. `addressing.md` (797 lines, 64,114 chars)

### Block inventory

| Lines | Block | Chars |
|---|---|---|
| 1-17 | preamble: consumers, design-authority history | 1,262 |
| 18-38 | `## 1. Key grammar`: the regex, *Shape is not depth*, *One grammar*, *Shape only* | 1,138 |
| 39-43 | `### Entry point: key-valid` | 235 |
| 44-98 | `### Entry point: read-key` | 5,749 |
| 99-189 | `### Entry point: key-summary` | 4,689 |
| 190-240 | `## 2. Directory naming` | 3,923 |
| 241-242 | `## 3. Resolution` heading | 18 |
| 243-272 | `### Entry point: resolve-address` | 2,287 |
| 273-466 | `### Entry point: specs-root-check` | 19,276 |
| 467-499 | `### Entry point: resolve-key` | 2,808 |
| 500-525 | `### The resolution record` plus three trailing paragraphs | 2,024 |
| 526-585 | `## 4.` kind/key read, never parsed | 4,315 |
| 586-636 | `### 4.1` placed by prefix / positive evidence | 4,074 |
| 637-699 | `## 5. The legacy layout` | 5,228 |
| 700-739 | `## 6. Nesting` | 2,313 |
| 740-797 | `## 7. The shared fallback` | 4,775 |

The file lists six entry points: `key-valid`, `read-key`, `key-summary`, `resolve-address`, `specs-root-check` and `resolve-key`. Each one's heading names it literally.

### 1.1 `resolve-address` (22 loader callers; `/frames` reads the file whole by path)

**1. Definition.** `### Entry point: resolve-address <ARG> [<KIND>]`, lines 243-272: 2,287 chars, or 2,305 with the `## 3` heading. The heading names it literally.

**2. In-file dependencies.** All of these are explicit § or entry-point references; each is followed transitively.

| Lines | Chars | Part | Why it is needed |
|---|---|---|---|
| 273-466 | 19,276 | `specs-root-check` | Step 0 runs it on every call where `$SPECS_PATH` is set. It produces the `misrooted` hard stop, its three stop forms (437-440), the "value to set" walk, the leftover-files line, the run-wide `specs_git: misrooted` flag and the emitter-tail consequence (367-374). |
| 44-98 | 5,749 | `read-key` | Step 2 uses it, and returns `invalid` on `invalid`/`needs-tree`. It also carries rules that bind every resolve-address caller: the whole name that resolves `absent` after the preflight stop (82-86); "the run's key is `key`, never the token" (88-90); and the creating-command rule with its prefix-mismatch stop text (93-97). |
| 18-43 | 1,373 | grammar + `key-valid` | `read-key` reading 1 and reading 3 call `key-valid`, which tests the regex at line 21. *Shape is not depth* (25-27) is a rule that §3's bound relies on. |
| 467-499 | 2,808 | `resolve-key` | Step 2. It holds the three-level glob, the assertion filter, the `absent` and `ambiguous` outcomes, and the `@<path>` way through the stop. |
| 500-525 | 2,024 | resolution record | The return shape every caller maps. 513-515 is a caller obligation: a Phase 0 refusal on this record still runs its emitter tail. |
| 190-240 | 3,923 | §2 | The three kinds (read-key reading 3; §4.1's prefix test). The reserved-name register (208-218), which read-key reading 2, specs-root-check (b), §4's pass-over and the glob all exclude. Invariant 2 gives the three-level depth. |
| 526-585 | 4,315 | §4 | The carrier rule (541-551), which step 1, resolve-key step 2, read-key reading 2 and specs-root-check (b) all read. The rule that reserved subdirectories are not candidates (573-580). The key-disagrees-with-name hard stop (582-584). |
| 586-636 | 4,074 | §4.1 | Step 1 hands placement of a no-carrier folder to §4.1. The prefix definition (594-599) is used by read-key reading 2 and specs-root-check (b). The positive-evidence placement and its stop (601-630) cover legacy results. |
| 637-699 | 5,228 | §5 | resolve-key step 4's fallback. The record semantics for a folder with no carrier, which step 1 and the record's `key` comment need. `legacy: true` is reported once per run (667-669). Step 1's stop says "give it a carrier (§5)", and 671-680 is where §5 says which artifact gets `key:`/`kind:`. |

**3. Other reference files relied on.**
- `workflows-core:specs-repo-git`: §3.1 (the same signals as a notice), §3.2 (run key set), §3.3 G0 (analogy) and §4 (emitter tail; *A run that refuses before it has written anything*).
- `cost-emission` §8, `feedback-emission` §2, `followup-emission` §2 and `session-hygiene` §1: the report-only tiers under `misrooted`.
- `escalation-rules`: *Required path environment variable unset*. `needs-tree` callers take that stop, and line 442 sets the misroot stop against it.
- `run-flags` §3: the mode-test remark at line 66, informative only.
- Stated inline, so no load is needed: `product-workflows:coverage-ledger-format` §5/§5.1 (the container test) and `/brd-split` Phase 0 step 9 (the positive slice test).
- Informative only: `brd-format` §2.1, `idea-format`, `grounding-format` §6.1-6.2, `proposal-format` and `bundle-packaging`, which own the reserved names. `ard-resolution` is mentioned as a co-caller.

**4. Minimal safe set.**
- **Section-granular:** lines 18-98 and 190-699, **51,075 of 64,114 (79.7%)**. It excludes the preamble, `key-summary`, §6 and §7, which total 13,039.
- **Steps-only floor:** about 42,145 (65.7%).

**5. Verdict: SAFE-AS-IS** for the file itself. Nine headed blocks must be declared (§1's untitled part, key-valid, read-key, §2, specs-root-check, resolve-key, the record, §4, §4.1, §5); with those, an extractor loses nothing.
- The yield is small, about 13k chars, and the declared list is long.
- **Caller contract: SAFE, low risk.** `brd-split` cites §6 seven times (lines 45, 143, 331, 378, 607, 672, 922) and §7 once (620), and `prd-ground:2041` cites §6. In each case the operative content is restated inline: the one-level nesting cap, "create inside the resolved folder", and "created with the §2 prefix". `release-notes:402` cites §7 for provenance only.

**6. Rationale, history and worked examples inside the minimal set.**

| Lines | Chars | What it is | Needed for edge cases? |
|---|---|---|---|
| 29-38 | 751 | rationale ("one grammar", "shape only") wrapped around a rule | The rule is also at 21; keep it for the "never checked against anything" framing. |
| 68-72 | 385 | history (a live `/design EPIC-BOOK-1-01` incident) | no |
| 73-81 | 763 | rationale with edge cases: `EPIC-008` stays a key; an all-digit slug `PRD-ACME-1-2024` is read as a folder | Yes as a guard, although the reading order alone produces both. |
| 220-233 | 1,267 | maintainer register of who owns each reserved name, plus a sync note with `key-summary`'s `RESERVED` | no |
| 234-240 | 508 | rationale for `PRD-PRD-…` | no; the `EPIC-008` case is restated at 597-599 |
| 282-287 | 484 | why an `@<path>` is tested too | no |
| 448-461 | 1,162 | the two unsupported layouts, explained | Mostly no; the signals already decide both. |
| 462-466 | 364 | how `specs-repo-git` §3.1 relates | no |
| 514-515 | about 110 | incident sentence | no |
| 517-525 | 702 | why resolution terminates; segment count buys no depth | no |
| 553-572 | 1,682 | why a kind outside the three is skipped, why byte-wise order, why step 2 exists | no; the rule is at 541-551 |
| 682-699 | 1,613 | history: the "need never rename" claim narrowed to filenames | no; the carrier consequence follows from §4 |

**Usually nothing to do on the common path:**
- **specs-root-check on a correctly rooted or unset `$SPECS_PATH`.** It runs its tests and passes through. The value walk, stop forms, leftover line and stop texts (343-441, about 11,371 chars) are reached only when a signal fires.
- **§5's legacy fallback** runs only when the prefixed glob misses.
- **read-key readings 2 and 3**, and their printed line, apply only to a token that is not a bare key.
- **The whole-name-absent stop** applies only to a whole-name token.
- **The creating-command prefix check** applies only to `/idea`, `/create-prd` and `/brd-intake` on `absent`.
- **§4.1 positive evidence** applies only to an unprefixed folder.
- **The `ambiguous` and key-disagreement stops.**

### 1.2 `key-summary` (3 callers: `/idea`, `/create-prd`, `/brd-intake`; each loads it itself)

1. **Definition.** `### Entry point: key-summary`, lines 99-189, 4,689 chars. The heading names it literally.
2. **In-file dependencies:** none needed for execution. The instruction is "Run it and print what it prints". The embedded Python (120-185, 3,001 chars) encodes §2's reserved names, §3's three-level bound and §4's carrier order on its own.
   - **Soft dependencies.** The prose at 110-118 cites §2, §3 and §4. A model that emulated the script by hand, for example where `python3` fails, would need §2 208-219, §4 538-552 and 573-581. No such hand fallback is written.
3. **Other reference files:** none.
4. **Minimal safe set:** **4,689 of 64,114 (7.3%)**. With the soft dependencies it is 7,596 (11.8%).
5. **Verdict: SAFE-AS-IS.**
6. **Rationale inside the set:** 106-108, why it proposes no key (about 280 chars). 110-118 is prose that duplicates the script (846). Neither is needed.

**Not a no-op:** it runs only beneath a missing-key or invalid-key stop.

### 1.3 The other listed entry points (no loader args request them; callers cite them bare)

| Entry point | Defined | Minimal set (section-granular) | Bare citers |
|---|---|---|---|
| `key-valid` | 39-43 (235) | + grammar 18-38 = **1,373 (2.1%)** | `/brd-split` and `/epics`, when minting. Both load `resolve-address`, so they get it. |
| `read-key` | 44-98 (5,749) | + 18-43, §2 190-219, §4 526-552 + 573-585, §4.1 prefix 586-600, §5 637-670 = **15,644 (24.4%)** | 18 commands, plus `specs-repo-git` and `run-flags` |
| `specs-root-check` | 273-466 (19,276) | + §2 190-219, §4 carrier 526-552 + 573-585, §4.1 prefix 586-600 = **25,139 (39.2%)** | About 29 commands, plus `specs-repo-git`, `cost-emission` and `feedback-emission` |
| `resolve-key` | 467-499 (2,808) | + the record, §2 reserved names, §4, §5 637-681 = **13,228 (20.6%)** | 5 commands |

**Cross-file note (pre-existing, not caused by narrowing).**
- `specs-repo-git` §3.1, which runs in `specs-preflight`, says to "run the tests of `workflows-core:addressing` §3 `specs-root-check`, exactly as that entry point defines them".
- Its 28 callers include `/upgrade`, `/docs-init`, `/docs-brand`, `/docs-audit`, `/feedback` and the `/prompt*` commands. None of those loads `addressing` at all, so `specs-preflight` already depends on a file it never brings into context.

### Per-file: parts no requested entry point needs

- 1-17, the preamble (1,262)
- §6, 700-739 (2,313)
- §7, 740-797 (4,775)
- Inside needed blocks: 220-240 (1,775)

`/brd-split` and `prd-ground` use §6 and §7 collaterally, but restate what they need.

---

## 2. `run-flags.md` (128 lines, 30,294 chars)

### Block inventory

| Lines | Block | Chars |
|---|---|---|
| 1-4 | preamble | 320 |
| 5-24 | `## 1. The flags` | 2,969 |
| 25-59 | `## 2. Model aliases` (alias table, Haiku rows, Reachability, stops, unpriced check) | 7,082 |
| 60-93 | `## 3. strip-run-flags entry point` | 14,454 |
| 94-97 | `## 4. Skip-feedback` | 1,310 |
| 98-118 | `## 5. skip-cost entry point` | 2,511 |
| 119-128 | `## 6. Reporting` | 1,648 |

### 2.1 `strip-run-flags` (36 callers)

**1. Definition.** `## 3. strip-run-flags entry point`, lines 60-93, 14,454 chars. The heading names it literally.

**2. In-file dependencies.**

| Lines | Chars | Part | Why it is needed |
|---|---|---|---|
| 5-24 | 2,969 | §1, all of it | Step 2 cites "§1's precedence" and "§1's table". Steps 1 and 4 cite "§1's boolean grammar" (line 15). The empty-env-is-unset rule (19) applies in step 2. The pair-form rule (21), that the next token is always consumed, applies in step 1 and the trailing run. Line 21 also holds the missing-value case for `RUN_FLAGS_BAD_MODEL` and the case-insensitivity of `routing`. |
| 25-59 | 7,082 | §2, all of it | Step 4 uses the alias table, the "seven forms", Reachability and both stops, plus the stop messages and the hint for a run-flag token the pair form consumed (37). Step 4 also needs the Haiku rows (39-42), the unpriced-model check and its warning text (58), and the price-table ladder. Step 7 needs "§2's table" and the family-only harness rules (47-50). Line 54 (stops only for an applicable flag) and line 56 (stops happen in Phase 0, before `specs-preflight`, with no feedback entry) are exception rules stated only here. |
| 119-128 | 1,648 | §6 | Step 6 renders `<id>` "exactly as §6 renders the `Model routing: bypassed` line" (126). The rule that the final report repeats the `Run flags:` line (128) is a caller obligation that callers cite as §6. |

**3. Other reference files relied on.**
- **`model-routing/classification.md`**: §2 (the Opus rows), §2.1 (Sonnet) and §5 (dispatch form). They are needed to resolve `opus`/`sonnet` in a harness that accepts ids, and, in a family-only harness, to test whether a version-specific form is "its family's newest chain row".
  - This is **not in context at strip time**: strip runs before the model-routing skill (`implement` line 18 vs 20, `create-prd` 24 vs 416, `document` 24 vs 348).
  - It is a pre-existing latent gap. Narrowing does not change it.
- **`workflows-core:addressing` §1 `read-key`** for `/document`'s mode test (step 1). In `/document`, strip runs at line 24 and addressing loads at 59, so this is also pre-existing. The inline gloss "a bare key, one behind its kind prefix, or its folder's whole name" approximates it, but a whole-name reading needs the tree walk and §4's carrier.
- **`cost-prices.yaml` under `workflows-core`'s `${CLAUDE_PLUGIN_ROOT}`** (only `workflows-core` ships it), and `$DEV_WORKFLOWS_COST_PRICES`. A loader that returns extracted text must still tell the model `workflows-core`'s root.
- **The Agent tool's `model` parameter documentation**, which is environment, not a file.

**4. Minimal safe set.**
- **Section-granular:** §1 + §2 + §3 + §6 = **26,153 of 30,294 (86.3%)**.
- **Steps-only floor:** about 24,659 (81.4%). That is less the maintainer recipes (64: 440; 74: 572), the why-not-grep aside (74: 224) and three rationale clauses (15/56/58: 258).
- Lines 123-125 (450) are the skip-cost and skip-feedback report lines, which strip itself does not print.

**5. Verdict: SAFE-AS-IS** for the file itself, with declared dependencies §1, §2 and §6. The yield is only about 4.1k chars: the preamble, §4 and §5.
- **Caller contract: SAFE, low risk.**
  - §4 is cited bare 33 times at callers' maintenance phase, and callers restate its content. The defect-reporter swap, `Plugin root:`, the model, emit-bugs vs emit-auto and "otherwise load nothing" are restated in each. "emit-block unaffected" is restated in 10 commands; the `Session feedback: bugs-only` line in 33.
  - `classification.md` §10 and lines 130/133 cite run-flags §2 and §3 step 7, and both are in the set.

**6. Rationale and examples inside the set.**

| Lines | Chars | What it is | Needed? |
|---|---|---|---|
| 64 (part) | 440 | maintainer recipe (`grep -ln "verbatim"`), "never the runtime test" | no |
| 64 (part) | 315 | "Today's members are …", an informative list | Helps edge cases such as `/document` direct mode; keep. |
| 72 | 1,345 | "The costs, stated plainly": a worked consequence, including that an inapplicable trailing flag is still stripped and reported | **Yes as an edge-case guard.** It tells the model not to "save" prose that ends in a flag. |
| 74 (part) | 572 + 224 | maintainer `grep` recipes, and why the runtime test is not a grep | no; the operative runtime test is in the same line |
| 15, 56, 58 (clauses) | 258 | why the boolean grammar is stated; why stops emit no feedback; why the price check is inlined | no |

**Usually nothing to do.**
- **A run with no flag tokens and no `WORKFLOWS_*` env.** Steps 1 and 3 remove and notify nothing, step 4 resolves nothing, step 5 builds the default record, and steps 6 and 7 print nothing.
  - On that path none of §2 is used (7,082), nor the free-text prose-span and trailing-run machinery (64-72, 7,232).
- **The applicability notice** fires only for an explicit flag on a command it does not apply to.
- **The unpriced warning** and the **step 7 session-model mismatch** fire only under enforcement.

### 2.2 `skip-cost` (28 callers)

1. **Definition.** `## 5. skip-cost entry point`, lines 98-118, 2,511 chars. The heading names it literally.
2. **In-file dependencies: none.** It is self-contained by design ("restated here, in full, because this path must never load `cost-emission.md`").
   - §6 line 124 (`Session cost: skipped …`) is restated verbatim by every caller.
   - Lines 117-118 (485) are a rule for `/prompt-brainstorm` and `/prompt-grill-me`, which are not skip-cost callers and restate it at 77/80. Section-granular extraction carries it anyway.
3. **Other reference files relied on.**
   - `cost-emission` §1 is restated; `<sid8>` is omitted but unneeded.
   - `cost-emission` §13.1 is the deferred file's shape, a JSON array of records each carrying `command`. Step 3 needs it to count records and fill `<command>`. It is deliberately not loaded. `<command>` reads as the record's `command` field only by inference, which is a pre-existing ambiguity that narrowing does not affect.
   - `${CLAUDE_PLUGIN_ROOT}/scripts/session-cost.py` must resolve to `workflows-core` (line 112 says so). Any new loader must keep supplying `workflows-core`'s root.
4. **Minimal safe set:** **2,511 of 30,294 (8.3%)**, or 2,026 without 117-118.
5. **Verdict: SAFE-AS-IS.**
6. **Rationale inside the set:** the clause in step 3 "a checkpoint that has already advanced past those records' boundaries could never match them anyway" (about 110 chars). It is not needed.

**Usually nothing to do:** step 3, when no `deferred-<session_id>.json` exists (the common case), and step 5's failure path.

### Per-file: parts no requested entry point needs

- 1-4, the preamble (320)
- §4, 94-97 (1,310): collateral, restated by callers
- 117-118 (485): restated by the two commands it binds

---

## 3. `components.md` (132 lines, 18,460 chars)

### Block inventory

| Lines | Block | Chars |
|---|---|---|
| 1-6 | preamble: citer register, sweep rule, *Why it exists* | 1,955 |
| 7-17 | `## 1. Component and id`, including the `<repo-slug>` derivation | 1,293 |
| 18-21 | `### 1.1 component-of` | 435 |
| 22-42 | `## 2. enumerate-components` (table; deploy row at line 35, 154 chars) | 3,433 |
| 43-54 | `## 3. multi-component-test` | 1,673 |
| 55-68 | `## 4. Ride-along` | 1,316 |
| 69-83 | `## 5. The ARD components: entry` (kind default at line 82, 723 chars) | 1,066 |
| 84-124 | `## 6. multi-component-prereqs` | 6,090 |
| 125-132 | `## Consumers (informative)` | 1,199 |

Loader requests:
- `multi-component-prereqs` (3 callers: `implement`, `ready`, `epics`)
- `multi-component-test` (4 callers: `design`, `ready`, `implement`, `specify`)
- whole file (2 callers: `specify:774`, `epics:402`, the latter conditional on an ARD set)

### 3.1 `multi-component-prereqs`

**1. Definition.** `## 6. multi-component-prereqs`, lines 84-124, 6,090 chars. The heading names it literally.

**2. In-file dependencies.**

| Lines | Chars | Part | Why it is needed |
|---|---|---|---|
| 43-54 | 1,673 | §3 | Step 1 says "Run §3". It supplies the known-set sources and their order, the two-or-more-`kind: code` rule, the empty set where there is no source, and the "checked *in* the set only for `ard`/`epics-run`" rule, which `in_set` in steps 2-4 needs. |
| 7-17 | 1,293 | §1 | Step 3 cites "§1's derivation, from its top level" for `target_repo_matches`, including `unknown` with no `origin`. §1 also defines the vocabulary every step uses: component, id, kind and paths, with kind defaulting to `code` at line 16. |
| 35 (+26-27 table header) | 207 | §2's deploy-directory row | §3's `epic-targets` rule says "an id whose path is one of §2's deploy directories counts as `kind: deploy`". A heading extractor must take all of §2 (3,433) unless the list is hoisted. |
| 82 | 723 | §5's kind and paths defaults | Needed when counting `kind: code` entries of an ARD set whose entries omit `kind`. Line 16 already states the `code` default, so this is soft. "A grouped component's id names one of its paths" helps the `in_set` test. |

**3. Other reference files relied on.**
- **`workflows-core:phase-handoff`**:
  - §3.1: the gate and row H, which produce `unmanaged`.
  - §3.2: the ref-existence test (inline), the **plugin-branch scan (not inline)**, and `<default-ref>`.
  - §3.3: row G, which produces `unverified`.
  - All three callers load `phase-handoff` whole and `require-on-main`.
- **`workflows-core:ard-resolution`**: the `components` and `contracts` fields, whose rows carry `ad`, `producer`, `consumers` and `status: new|changed|exists`. All three callers load it whole.
- **`dev-workflows:workflow-states`**: the Ready rung, informative at `ready` scope.
- **`workflows-core:bounded-run`**: `bounded.py`; the call form is inline.

**4. Minimal safe set.**
- **Section-granular:** §1 + §2 + §3 + §5 + §6 = **13,555 of 18,460 (73.4%)**.
- **Tight:** §1, the §2 header plus line 35, §3, line 82 and §6 = **9,986 (54.1%)**.

**5. Verdict: SAFE-AS-IS**, with declared §1, §2, §3 and §5. Optional restructure: hoist §2's deploy-directory list (line 35) into §1, so §2 need not be declared.
- **Caller contract: SAFE.** `implement` and `ready` also load `multi-component-test`. Every bare citation they make is §1 or §3, which is in the set: `implement:232/236/246/331/369` and `ready:338`.

**6. Rationale inside the set.**
- §1 line 14, the `/docs-audit` aside (178)
- §2 line 39, rationale tail (200), and line 41, worked examples (366)
- §3 line 53, its first sentence (204): why the third source exists
- §6 line 89 clause (32) and the line 103 clause "the consumer's to fix" (about 70)

None is needed for the steps.

**Usually nothing to do.**
- **A single-component PRD**, which is the common case. Step 1 returns `{multi_component: false}`, plus `target` at `implement` scope. Steps 2-5 and the remedy list (about 4,835 chars) are unused.
- **`$SPECS_PATH` not a git repository:** every row is `unmanaged`, and the caller proceeds as before.
- **Step 5** runs only when `contracts` is not null.

### 3.2 `multi-component-test`

1. **Definition.** `## 3. multi-component-test <PRD folder>`, lines 43-54, 1,673 chars. The heading names it literally.
2. **In-file dependencies.**
   - §1 7-17: the component vocabulary, kind, and the `code` default.
   - §2's deploy row (line 35): needed for kind inference under `epic-targets`.
   - §5 line 82: the kind and paths defaults in the ARD set; soft.
   - §3 cites §4 (line 51) and §6 (line 53) only as explanation, so they are not needed.
3. **Other reference files:** `ard-resolution`'s `components` field, and `product-workflows:ard-format` through it.
4. **Minimal safe set.**
   - **Section-granular:** §1 + §2 + §3 + §5 = **7,465 of 18,460 (40.4%)**.
   - **Tight:** 3,896 (21.1%).
5. **Verdict: SAFE-WITH-RESTRUCTURE**, for the caller contract. The entry point itself is SAFE-AS-IS.
   - **The collateral problem.** `design.md`'s only `components` load is `multi-component-test` (line 104). Design then uses more of the file:
     - §2 `enumerate-components` at line 390 (design-reviewer's `Repository modules:`)
     - §2's shared ground at line 299
     - §4 ride-along at line 299 ("that no ride-along covers")
   - With narrowing, `/design` loses §4, and §2 too if the tight cut is used.
   - **Edit:** add a `components enumerate-components` load and a §4 load at those sites, or declare §2 + §4 as dependencies (8,781, 47.6%).
   - **Pre-existing, not caused by narrowing.** Design's load at 104 is inside the "`<EPIC>` null on a multi-component PRD" bullet. An Epic-level `/design` run, the ordinary case, therefore reaches 299 and 390 with **no `components` load at all**. Likewise:
     - `/epics` on a no-ARD run reaches Phase 5.5's `enumerate-components` / `component-of` (lines 624-632) before any load. Its whole-file load at 402 is conditional on an ARD set, and its prereqs load is reached from 5.5 step 5, after step 1.
     - `/implement` uses §1 at 232 and 236, before its 242 prereqs load. Its 113 test load runs only on PRD-level addresses.
6. **Rationale:** line 51 (part) and 53's first sentence (204). Not needed.

**Usually nothing to do:** no source, meaning no ARD `components:` and no Epic `target:`. The result is an empty set and `false`.

### Per-file: parts no requested entry point needs

- 1-6, the preamble (1,955)
- §1.1 (435): used by `/epics` 5.5 via a whole or unloaded read
- §4 (1,316): collateral for `/design`; also used by `epic-writer` and the reviewers through their briefs
- Consumers, 125-132 (1,199)

The whole-file callers (`/specify`, `/epics`) need everything.

---

## 4. `docs-grounding.md` (173 lines, 15,111 chars)

### Block inventory

| Lines | Block | Chars |
|---|---|---|
| 1-21 | preamble: intro 1-8 (458); **rules 9-13 (252)**: read-only, "every miss is a silent, non-blocking skip — never an error, never `emit-block`"; consumers 14-21 (489) | 1,199 |
| 22-77 | `## Procedure — resolve-docs-grounding <command-name>` (step 3.5 at 37-71: 5,046) | 6,529 |
| 78-101 | `## Plan-approval line`: the forms, the "shown means printed" rule, fallback-form choice, **staleness read (98)**, **Shadow detection (100)** | 2,796 |
| 102-121 | `## Dispatch — dispatch-docs-grounder` | 928 |
| 122-164 | `## Consumption`: grill-rank, the `/brd-intake` variant, writer-attach, lead-only | 2,752 |
| 165-173 | `## Invariants` | 907 |

### 4.1 `resolve-docs-grounding` (9 callers)

**1. Definition.** `## Procedure — resolve-docs-grounding <command-name>`, lines 22-77, 6,529 chars. The heading names it, prefixed with "Procedure —".

**2. In-file dependencies.**

| Lines | Chars | Part | Why it is needed |
|---|---|---|---|
| 9-13 | 252 | preamble rules | Stated once, for every step: read-only, and every miss is a silent non-blocking skip that is never an error and never `emit-block`. These govern the probes' unexpected failures. |
| 78-101 | 2,796 | Plan-approval line | Step 3.5 appends "the shadow clause" and "the partial-coverage clause" to "the plan-approval line", and step 4 says its value "drives … the line below". Every caller shows "the `docs grounding:` line … in the form that reference fixes", verbatim. Two parts hide here and are easy to miss. **Shadow detection** (100) is cited explicitly ("below") and is the parse of `Index:`. **Docs-checkout staleness** (98) is an executable read (`git -C "$docs_root" log -1 --format=%cI`, 14-day threshold) that the Procedure never mentions: it is an implicit, hidden step that exists only here. |
| 165-173 | 907 | Invariants | "Runs **exactly once per run** … any later invocation consumes the cached result; never re-prompts, re-probes, or re-refreshes" is stated only here. "Never blocks", and "build needs consent, refresh bounded at 60s", restate the procedure. |

**3. Other reference files relied on.**
- **`workflows-core:bounded-run`**: `bounded.py`; the call form is inline. "Fails or times out" relies on bounded-run's exit 124, which is not stated inline; soft.
- **`docs-grounder`**: rung 3 is mentioned to explain parity, informative only.
- **`read-only-repos` §5**: shares the 14-day threshold, informative only.
- **`escalation-rules` §0**: the `choices:` arrays are presented verbatim, with free text supplied automatically. All 9 callers load it whole.
- **The `qmd` CLI.**

**4. Minimal safe set.**
- **Section-granular:** preamble + Procedure + Plan-approval + Invariants = **11,431 of 15,111 (75.6%)**.
- **Tight**, with only preamble lines 9-13: **10,484 (69.4%)**.
- **With the collateral the callers need** (below): the whole file, 15,111 (100%).

**5. Verdict: SAFE-WITH-RESTRUCTURE. Narrowing as-is is UNSAFE for all nine callers.**
- The entry point itself is SAFE-AS-IS if Plan-approval line and Invariants are declared dependencies. Moving the staleness read into the Procedure, as a step 3.6, would make the heading self-describing.
- **The collateral problem.** All nine callers later run `dispatch-docs-grounder` and apply a consumption mode with **no loader call**, relying on the Phase-1 whole-file load:
  - `create-prd:528/535`
  - `idea:357/359`
  - `update-prd:116`
  - `create-ard:581`
  - `specify:848`
  - `brd-intake:1136/1142`
  - `prd-ground:954`
  - `epics:545`
  - `release-notes:393`
- **What would be lost:**
  - **Dispatch** (928): the `subagent_type`, the model tier with its §10 override, the prompt shape, and the `ERROR` → OFF and `EMPTY` handling.
  - **Consumption** (2,752): grill-rank's no-append rule and `/idea`'s ≤10-slot bound; `/brd-intake`'s ranking and raising behind human confirmation; writer-attach's handoff as `docs_grounding`; and lead-only's never-evidence rule, which is `/prd-ground`'s blind-grounding guard.
- **Required edits.**
  - Add a loader call at each of those nine sites, `docs-grounding dispatch-docs-grounder` plus a consumption entry point.
  - The consumption modes are bold labels, not headings, so the file needs a heading or entry-point name for them.

**6. Rationale and history inside the set.**

| Lines | Chars | What it is | Needed? |
|---|---|---|---|
| 1-8 | 458 | why docs grounding exists | no |
| 41 (part) | 311 | why positive vectors cannot explain an empty registry, plus field-run history (160) | no; the operative choices and recommendation sit beside it |
| 37 (clause) | 143 | "mirrors docs-grounder's rung 3" | no |
| 51 (clause) | 140 | why `qmd update` is safe | no |
| 67 (clause) | 65 | why a consented build is uncapped | no |
| 69 | 242 (181 rationale) | why index building never happens inside the agent | The rule is needed; the rationale is not. |
| 70 (part) | 280 | why partial embedding coverage matters | no |
| 74-77 | 293 | default-safety note with "do not change that" (maintainer) | no |
| 98 (parts) | 136 + 113 | why staleness matters; the shared threshold | no |
| 100 (tail) | 157 | why shadow detection exists | no |

**Usually nothing to do.**
- **No docs root**, for example a host without `/workspace/docs`: OFF at step 3, and all of step 3.5 (5,046) and its three prompts are skipped.
- **`qmd` absent, or a probe that fails:** fallback, silently.
- **A covering collection with nothing changed:** `qmd update` is instant and asks nothing.
- **The staleness clause** is skipped when the root is not a git checkout or is less than 14 days old.
- **Shadow detection** fires only on a non-user-scope `Index:`.
- **Any second invocation in a run** is a cache read.

### Per-file: parts no requested entry point needs

- 1-8, the intro (458)
- 14-21, the consumer list (489)
- Dispatch (928) and Consumption (2,752): needed collaterally by every caller, as above

---

## Cross-cutting findings

1. **The most important risk is collateral reliance.**
   - Callers use sections at later phases through bare citations (`dispatch-docs-grounder (workflows-core:docs-grounding)`, `components` §2/§4, `run-flags` §4/§6, `addressing` §6/§7). These resolve only because an earlier loader call read the whole file.
   - The loader's own contract says the file is the source of truth "for the current step". The callers rely on more than that.
   - A narrowed loader turns this into **silent** loss: nothing errors, and the model improvises a dispatch or a consumption rule.
   - Severity per file:
     - **docs-grounding:** all 9 callers; dispatch and consumption are not restated, so this is **high**.
     - **components:** `/design`'s §2/§4; **medium**.
     - **run-flags and addressing:** operative content is restated at the citing site; **low**.
2. **Bare citations are already unpoliced.**
   - `/design` (Epic-level runs), `/epics` (no-ARD Phase 5.5) and `/implement` (lines 232 and 236) reach `components` text that no prior load in that run supplies.
   - Several whole-loaded references cite these files by `${CLAUDE_PLUGIN_ROOT}/references/<file>.md` § and never load them. Examples: `epic-picker` → `components` §3, `next-phase-offer` → `addressing` §4.1, and `ard-resolution` → both.
   - Any narrowed loader should come with a gate: every `<ref>` § or entry-point name a command cites after a loader call must be covered by a loader call that returns it.
3. **Cross-file dependencies a dependency list must name**, because today's whole-file load does not supply them either:
   - `strip-run-flags` → `classification.md` §2/§2.1 (version-specific `--enforce-model`), and `addressing` `read-key` (`/document`'s mode test)
   - `specs-preflight` → `addressing` `specs-root-check`
   - `multi-component-prereqs` → `phase-handoff` §3.1-§3.3, and `ard-resolution`'s `contracts`
4. **`${CLAUDE_PLUGIN_ROOT}` must keep meaning `workflows-core`** in returned text for `skip-cost` (`session-cost.py`) and for `run-flags` §2 (`cost-prices.yaml`). Only `workflows-core` ships those files. Every plugin ships `bounded.py`, so that one is unaffected.
5. **The yield is small where the risk is large.**
   - `resolve-address` needs about 80% of `addressing.md`, and `strip-run-flags` about 86% of `run-flags.md`.
   - The real savings are `skip-cost` (8%), `key-summary` (7%) and `multi-component-test` (21-40%).
   - The biggest savings available inside `resolve-address` are in `specs-root-check`'s stop machinery (343-441, about 11.4k), which is used only when a signal fires. That would need a two-stage, signal-gated load rather than a static dependency list.

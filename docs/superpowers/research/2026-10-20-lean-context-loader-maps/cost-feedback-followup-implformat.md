# Loader map — cost-emission, feedback-emission, followup-emission, implementation-format

All four files are under `plugins/workflows-core/references/`. Line ranges are inclusive and taken from the tree at `b1f3adba`. "chars" means Unicode code points with one newline per line, so `wc -c`, which counts bytes, reads higher.

| File | Lines | chars | bytes (`wc -c`) |
|---|---|---|---|
| `cost-emission.md` | 911 | 66,724 | 67,277 |
| `feedback-emission.md` | 295 | 27,123 | 27,396 |
| `followup-emission.md` | 144 | 16,103 | 16,261 |
| `implementation-format.md` | 438 | 43,070 | 43,353 |

The counts came from a per-line script in the scratchpad (`secsize.py <file> a-b …`), which you can re-run.

## 0. Findings that cut across all four files

1. **Some rules sit outside the heading that names their entry point.**
   - `emit-auto`'s projection rule is at feedback-emission lines 189–196, under `### 4.1 Defect predicate`. `emit-auto`'s own body cites only "§4".
   - `unit-branch`'s subject leg depends on implementation-format §4's whole-key boundary (lines 196–205). That boundary sits inside an 18 K section the entry point otherwise does not need.
   - `emit-cost` needs all of §7, including every inference rule, for **every** caller. Any run can replay a deferred record, and the replay resolves that record's `target_command` through §7.
2. **Some dependencies are reachable only from another heading's lead text.**
   - feedback-emission's §6 lead (lines 218–226) is the only place that sends every entry point to §1.1's redaction. Neither `emit-auto` nor `emit-bugs` cites §1.1 from its own body.
   - cost-emission's preamble states three runtime rules once: lines 22–25, 34–45 and 55.
   - So the dependency list must be **declared**. Deriving it by following `§` cites from the entry point's body loses rules.
3. **Some citations name bold-lead paragraphs, not headings**, so a heading-keyed extractor cannot address them:
   - followup-emission § *Withdrawing a follow-up*, *Re-queuing a confirmed fix* and *A security finding's line*;
   - implementation-format §5's *The merged test* and *A unit's work is merged*.
4. **Some stale `§1` pointers would pull an unrelated section** if followed mechanically. Each pointer below sits next to a roster that §1 does not hold. The cost is harmless today, because §1 is in each set anyway.
   - cost-emission line 649 and line 852: "(§1)" after "twenty-eight commands that measure themselves". cost-emission §1 is session-artifact resolution.
   - feedback-emission line 227, in the heading "(… maintenance phases, §1)". feedback-emission §1 is the entry format.
5. **`${CLAUDE_PLUGIN_ROOT}` inside a slice has to mean workflows-core's root.** The paths affected include `session-cost.py`, `cost-prices.yaml` and `specs-repo-git.md`.
   - Two paragraphs say so: cost §2 line 85 and the `plugin_version` paragraph at cost line 699. feedback §3 line 155 and §4 line 164 make the inverse point.
   - A loader that returns text, not a file it was seen to read, must either state the root or substitute it.
6. **Some entry points are used without any loader call naming them.** A slicing loader still has to serve these, or keep whole-file loads for them:
   - `emit-block` is cited "per `workflows-core:feedback-emission`" by 27 command files with no `args:`.
   - `emit-manual` and `emit-prompt` are read by path by workflows-core's own commands.
   - The writer side of cost §13.1 is read by path by `/prompt-brainstorm` and `/prompt-grill-me`.
   - `/implement` Phase 1, line 232, cites followup §6 and § *Withdrawing* with no load at that point.

---

## 1. `cost-emission.md` — `emit-cost`

**Callers.**
- 24 command files load it through the loader with `args: "cost-emission emit-cost"`.
- 4 workflows-core commands (`/feedback`, `/prompt`, `/frames`, `/diagnose-session`) cite the file by path and call `emit-cost`.
- `/prompt-brainstorm` and `/prompt-grill-me` read §13 and §13.1 by path.
- `/statusline` cites §5.
- `run-flags` `skip-cost` restates §1, so that it never loads this file.

What callers cite, counted by `§` across `plugins/`: §7 54, §8 22, §13 12, §9 9, §13.1 5, §5 4, §11 4, §3 3, §1 2, §4 2, §6.1 1, §13.2 1 (from `dependencies.md` only), §13.3 1.

### 1.1 Definition
`## 11. Caller contract — \`emit-cost\``, lines 646–723, **6,959 chars**. The heading names the entry point literally. Inputs are lines 661–699 and Behavior steps 1–8 are lines 701–722.

### 1.2 Dependencies inside the file

| Lines | chars | Part | Why `emit-cost` needs it |
|---|---|---|---|
| 22–25 | 276 | preamble | The orchestrator owns every prompt; this reference owns the rest. This governs §9's prompt. |
| 34–45 | 1,085 | preamble "Cost is computed, never read" | Forbids reading Claude Code's `cost-state`. Says compactions are billed but unpriced, which §2 and §5 rely on. |
| 47–53 | 502 | preamble "Relationship to siblings" | Included as a doubtful case: no dedup or cross-reference with feedback or follow-ups, per-session `cost/` files, and no `impl-maintenance`. |
| 55 | 666 | preamble "Cost runs unless the user skipped it" | Always computes and always advances. The exceptions are `--skip-costs` and `PRD_GROUND_TYPED_ONLY`. The write is silent and §9 is the only prompt. Partly restated at line 659. |
| 57–69 | 677 | §1 | Behavior step 1, session-artifact resolution. |
| 70–138 | 4,757 | §2 | Step 2. Holds the invocation (74–83), the rule against `--commands-dir` and for `--namespaces` only on fixtures (85), the output schema (95–113), claims versus remainder (115–121), `unpriced-model` (123–126) and `compactions` (128–137). |
| 139–163 | 1,486 | §3 | Step 2 (the checkpoint path, and no checkpoint on the first command) and step 7 ("advance ALWAYS"). |
| 164–165, 219–229 | 866 | §4 heading plus its resolution order | Step 1 "resolve the price table (§4)": env var, then repo-local, then shipped. |
| 230–267 | 2,408 | §5 | Step 2 "the snapshot (§5) when present". Says when `cost_statusline_usd` is null and omitted, and that the field is never emitted once any claim matched. |
| 268–329 | 2,951 | §6 | Step 4 builds the entry: location, frontmatter, header, `id`, the omission rules for `cost_statusline_usd` and `compactions`, the four null `note:` values and `modifiers:`. |
| 330–366 | 2,068 | §6.1 | Step 4 applies the dominance warning per built entry, replays included, in every tier. |
| 367–553 | 13,109 | §7 | Step 4 attribution and the §13.3 replay. **All of it, for every caller**: a replay resolves a deferred record's `target_command` through any row. That includes one level of `/release-notes`, `/frames` or `/conformance` inference, the `/scan` target rule and the `n/a` rules. The Keys rule is lines 550–552. |
| 554–598 | 5,203 | §8 | Step 5, the ladder: the `misrooted` pre-tier, then tier 1, tier 2's documentation, security and Otherwise branches, tiers 3 and 4, and the fall-through on a failed write. |
| 599–638 | 2,328 | §9 | Step 5: the pending file, the reconciliation prompt, pre-selection (never for `plugin-feedback`) and move-then-delete. |
| 639–645 | 274 | §10 | Cited by §6 ("No user name anywhere in the file (§10)"). |
| 750–761 | 717 | §13 lead | What deferral is, and that a `skip: true` record is carved out and discarded. |
| 762–805 | 3,406 | §13.1 | Step 2 "read the §13.1 deferred file": its path (769), the array shape, and field semantics. The replay uses the **record's** `plugin_version`, uses `ceded_at` as `date` and in the `id`, routes `key`, `epic` and `source` to §8, and writes no entry for `skip: true`. |
| 850–887 | 2,317 | §13.3 | Step 6 replay: the record's own key and source, `skip: true` building no entry, and the replaying run committing the result. |
| 888–911 | 1,684 | §13.4 | Step 3: an unmatched claim gets one report line and no entry, the deferred file is still deleted, and Option B is omitted once any claim matched. |

**Not needed by `emit-cost`:**
- Lines 1–21 and 26–33 (roster and purpose, about 1.7 K).
- §4's engine and pricing documentation, lines 166–218 (4,464). The script reads the table; the model only picks which file.
- §12, the maintainer checklist, lines 724–749 (1,586). §6.1's printed warning only names it.
- §13.2, lines 806–849 (5,226). This is how `session-cost.py` cuts windows, guarded by `--selftest`. Outside this file only `dependencies.md` cites it, and for the manifest's rationale.

### 1.3 Other references and files the entry point relies on
- **Files it runs or reads:** `scripts/session-cost.py`, `scripts/command-namespaces.json` and `references/cost-prices.yaml`.
- **`workflows-core:specs-repo-git`:**
  - §2.1: the `<docs-repo-slug>` definition, the staging shapes for `documentation/*/dev-workflows/**` and `security/*/**`, and the OTHER classifier.
  - §3.1: `specs_git: misrooted`.
  - §4: the terminal `commit-artifacts`, and the ceding exception.
- **`workflows-core:addressing`:**
  - §3: `resolve-address`, and `specs-root-check`'s stop.
  - §4: kind read off the carrier, for `/frames`.
  - §4.1: placement by prefix, for `/conformance`.
  - §2: the `<KIND>-<KEY>-<slug>/` folder naming. §8 tier 1's restated glob `…/<KEY>{-|_}<slug>/…` matches only the unprefixed legacy shape, so tier 1 in practice rests on §7 Keys' "reuse the run's own resolution".
- **`workflows-core:security-register-format`:** §1 (the register's `<repo-slug>`) and §2 (`role`).
- **`workflows-core:components`:** §1 (`<repo-slug>` derivation, in §8's security branch).
- **`workflows-core:run-flags`:** §5 (`skip-cost`; a replaying run under the flag drops the record).
- **`/docs-workflows:document` Phase 0 step 3:** the direct-mode write target, in §8's documentation branch.
- **Rationale only:** `feedback-emission.md` §6 (§7 line 511–515) and `feedback-emission.md`'s ladder (§8 line 556, which restates the ladder in full).
- **Maintainer only:** `model-routing/classification.md` §2 (§12).

### 1.4 Minimal safe set
- **Fine-grained: 53,739 / 66,724 chars (80.5 %).** This is everything in the 1.2 table. It needs §4 split.
- **At heading granularity: 59,912 (89.8 %).** This drops only §12 and §13.2, keeping the preamble and all of §4.
- **No per-caller cut is safe.** A fixed-label caller still needs the inference rules whenever it replays a record, and whether a deferred file exists is known only at run time (step 2). The only safe conditional split is two packs:
  - a core pack: §1–§6.1, the §7 table and Keys, and §8–§11;
  - a replay pack: **all** of §7, plus §13, §13.1, §13.3 and §13.4, loaded once step 2 finds a deferred file.

### 1.5 Verdict
**SAFE-AS-IS at heading granularity**, with the declared list: preamble, §1–§11, §13, §13.1, §13.3, §13.4.

**SAFE-WITH-RESTRUCTURE to reach the fine-grained figure:**
- Split §4 into "resolution order" (lines 219–228) and "pricing engine" (lines 166–218).
- Split the preamble into its runtime rules (22–25, 34–45, 47–53, 55) and its roster and purpose.
- Fix the two "(§1)" pointers at lines 649 and 852.

The saving is small either way, at most about 20 %.

### 1.6 Rationale, history and worked examples inside the minimal set
None of these are needed for the steps unless the "edge" column says so.

| Lines | chars | Kind | Needed for an edge case? |
|---|---|---|---|
| 34–45 (all but the first sentence) | ~900 | Explains message-id dedup and accuracy drift | No for the steps. It helps the model not "correct" the figure against `/cost`. |
| 85, the history half | 592 of 1,474 | History of the `--commands-dir` flag | The rule half (no flag; `--namespaces` only for fixtures) **is** needed. The history is not. |
| 128–137 | 752 | Why `compactions` exists | Yes, to explain an entry carrying `compactions:` or an A/B gap. |
| 154–162 | 634 | Cede semantics, user semantics | No. |
| 253–266 | 983 | Option B caveats | No for the steps; useful when a user asks why A and B differ. |
| 433–438 | 435 | `/frames` "no third branch" | Mostly no. It holds the fact that `/frames` refuses other kinds. |
| 501–515 | 2,211 | Why `/vuln` and others emit no cost, plus history | No. No caller of `emit-cost` is among those commands. |
| 517–536 | 1,475 | Why the two commands defer | No. |
| 538–541 | 297 | Epic presence is not a signal | Keep: a negative rule for `/release-notes` inference. |
| 543–548 | 415 | Why `proposal` is its own phase | No. |
| 570–576, 578–589 | 499 + 954 | Why the documentation and security rungs exist; history of `/document` direct mode | Mostly no. They clarify that `/document` keyed mode is tier 1's and that older pending files stay pending. |
| 610–615 | 589 | `/idea` never reaches pending | No. It says to derive the set from tier 2. |
| 791 | 1,206 | Why the record carries `plugin` | No. The replay never reads `plugin`. |
| 864–871 | 571 | The positional-pairing trap | No. This is script behaviour. |
| 878–882 | 361 | Partition rounding | Only to explain cents of difference. |
| 908–911 | 318 | Not a general skip mechanism | No (maintainer). |

**Worked examples that are needed as schemas:** the JSON output at 95–113 (588), the entry template at 289–309 (863) and the deferred record at 779–787 (296).

### 1.7 Parts no caller needs, and what a script could absorb
- **Parts no `emit-cost` caller needs:** §12, §13.2, §4 lines 166–218, and preamble lines 3–20 and 27–32. The §13.1 writer side (lines 764–787) is needed only by the two ceding commands, which read it by path.
- **What a script could absorb** (`session-cost.py` already prices, partitions and has `--advance-only`, which writes the checkpoint itself):
  - §1: the cwd slug, newest transcript, `sid8` and subagents directory.
  - §4: the resolution order.
  - §13.1: reading the record and building `--claim` arguments, oldest first.
  - Step 7: writing `new_checkpoint` back, as `--advance-only` already does, and deleting the deferred file.
  - §7: the fixed-table lookup, plus every mechanical inference: the `/release-notes` glob for `specification.md` and `design.md`, the `/conformance` prefix, the `/scan` `run_role` map, the `target_command` map with its one-level recursion and `n/a` rules, and `/frames` from a passed folder kind.
  - §6: rendering, meaning the header, `id`, YAML, omissions, notes and modifiers.
  - §6.1: the trigger and its warning text.
  - §8: tier selection from passed facts (`specs_git`, whether `$SPECS_PATH` is writable, the resolved folder, the command name, the docs or repo slug), creating or appending the file, and falling through on a failed write.
  - §9: the pending write, listing pending files (date, session, commands, total) and the move-then-delete once given a selection.
  - §13.3: per-claim entries.
  - §13.4: the report line.
- **What must stay with the model:**
  - Assembling the caller inputs from run context: labels, `target_command`, `run_role`, `key`, `source`, and the slug from the run's own resolution.
  - The §9 reconciliation prompt and the user's selection.
  - Printing the output.
- **Two facts a script has to settle rather than copy:**
  - The PRD folder must come from the caller's own resolution, never from §8 tier 1's glob.
  - §8 tier 2's "the run is `/docs-init`…" is ambiguous for a **replayed** record: does "the run" mean the replaying run or the ceded one?

---

## 2. `feedback-emission.md` — `emit-auto` and `emit-bugs`

**Callers.**
- `emit-auto`: 27 command files through the loader. `document.md` calls it twice. `/frames` reads the file by path for `emit-auto`.
- `emit-bugs`: 28 command files through the loader, `/frames` included. `run-flags.md:96` names the call.
- A run calls one of the two. `--skip-feedback` swaps `emit-auto` for `emit-bugs`, and `emit-bugs` is loaded only when `defect-reporter` returned a defect (line 295).
- `emit-block` is cited without a loader call by 27 commands (see 0.6).

### 2.1 `emit-auto`

**Definition:** `### \`emit-auto\` — automatic callers (…, §1)`, lines 227–241, **991 chars**. The heading names it literally. Its "§1" pointer is stale (see 0.4).

**Dependencies:**

| Lines | chars | Part | Why |
|---|---|---|---|
| 3 | 488 | preamble | Steps run inline; the orchestrator owns every prompt; this file owns format, ladder, dedup, predicate and contract. |
| 5–11 | 815 | preamble "Purpose" | Specs-first, committed by `commit-artifacts`, the emitter never touches git, and under `misrooted` §2 writes nothing. Mostly restated elsewhere. Included as a doubtful case. |
| 18–22 | 332 | preamble | No dedup against follow-ups. Included as a doubtful case. |
| 24–28 | 333 | preamble | `emit-auto` projects the `impl-maintenance` report and "never analyses a session itself". |
| 30–85 | 2,137 | §1 | Entry format, required fields, the `category` and `impact` vocabularies, the `id` shape. |
| 86–105 | 5,597 | §1.1 | Redaction, reached **only** through the §6 lead at line 222. It holds the slug rule (90), the ordered table (94–99), numbering, what to keep, and the report clause (104). |
| 106–139 | 3,266 | §2 | The ladder: `misrooted`, the docs branch, the unfiled notice, tiers 3 and 4, zero loss, fall-through. |
| 140–156 | 1,878 | §3 | Append-only, `SKIP — already logged`, `author` from git config, `plugin_version` supplied by the caller. |
| 157–177 | 2,016 | §4 | The plugin-facing predicate. Reference-doc gaps resolve to the running command's plugin, **not** `${CLAUDE_PLUGIN_ROOT}`. Also `unfollowed-rule`, `environment-defect`, and no target-project advice. |
| 178–197 | 1,883 | §4.1 | **Lines 189–196 (769) are `emit-auto`'s own projection rule**: which `impl-maintenance` sections to keep, and which to discard (`CLAUDE.md rules`, `Hooks and checks`, target-project unfollowed rules). Lines 180–187 set the ai-containers scope that `environment-defect` follows, and line 187 says that widening applies to `emit-auto`. |
| 198–208 | 636 | §5 lead and the `emit-auto` bullet | No curation gate. Writes silently. The caller prints the path or "no plugin-facing signal — nothing persisted", and a routine session writes nothing. |
| 218–226 | 636 | §6 lead | The caller supplies `plugin_version`; §1.1 redaction runs before dedupe; never commits; never writes into a docs or code repo or the cwd. |

**Other references:**
- `workflows-core:specs-repo-git` §2.1, §3.1 and §4 step 5.
- `workflows-core:addressing` §1, for the key-grammar exception in the Secrets row of §1.1, and §3 `specs-root-check`.
- The **`impl-maintenance` agent's report section names**. The projection keys on them.
- `/document` Phase 0 step 3.
- `cost-emission.md` §8, for rationale only (line 126).

**Minimal set:** **21,008 / 27,123 (77.5 %)**. At heading granularity (lines 1–241, everything before `emit-manual`) it is 22,145 (81.6 %).

**Verdict: SAFE-AS-IS**, with the declared list: preamble, §1, §1.1, §2, §3, §4 **with** §4.1, §5, §6 lead, `emit-auto`. There are three traps for whoever writes the list:
- Taking "§4" to mean everything up to the next heading of any level drops §4.1.
- §1.1 is cited only from the §6 lead.
- The projection paragraph sits under a heading named for `emit-bugs`' predicate.

One small optional edit removes the third trap: move lines 189–196 under §4 or into `emit-auto`.

**Rationale inside the set:**

| Lines | chars | Kind | Needed? |
|---|---|---|---|
| 5–11 | 815 | Purpose | No |
| 18–22 | 332 | Relationship | No |
| 125–129 | 388 | History | No |
| 155 | 908 | Mixed | The first sentence is a rule. The rest explains the sibling-plugin hazard. |
| 159 | 442 | Mixed | One sentence is history. |
| 164 | 526 | Mixed | Its explanation is the reason the rule exists, so keep it. |
| 187 | 465 | Mixed | |
| 200–203 | 260 | Rationale | The first sentence is the no-curation rule. |
| 88 | 629 | Mixed | The second and third sentences are rationale. |

The template at 50–69 (708) and the redaction table at 94–99 (2,963) are rules or schemas, not rationale.

### 2.2 `emit-bugs`

**Definition:** `### \`emit-bugs\` — bugs-only callers (\`--skip-feedback\`, \`workflows-core:run-flags\` §4)`, lines 289–295, **1,289 chars**. The heading names it literally.

**Dependencies:**
- Preamble line 3 (488), 5–11 (815) and 18–22 (332). The last two are doubtful cases.
- §1 and §1.1 (lines 30–105). §1.1's line 104 sends the redaction clause to the bugs-only line.
- §2 and §3 (lines 106–156). Together, §1–§3 come to 12,878.
- §4.1 lines 178–187 (1,112), included as a doubtful case. `defect-reporter` applies the predicate upstream, but `emit-bugs` assigns `environment-defect` versus other categories by the same ai-containers-versus-user-machine line.
- §5 lead 198–204 (308) and the `emit-bugs` bullet at 216 (304).
- §6 lead 218–226 (636).
- **Not needed:** preamble 24–28; §4 lines 157–177; the projection paragraph at 189–196; `emit-auto`, `emit-manual`, `emit-prompt` and `emit-block`.

**Other references:**
- `workflows-core:run-flags` §4 and §6. §6 is the bugs-only report line, where the redaction clause goes.
- The **`defect-reporter` output format**: `impact` is `blocker | friction`, with location, evidence and repro.
- `workflows-core:specs-repo-git` and `workflows-core:addressing` §1, as for `emit-auto`.

**Minimal set:** **18,162 / 27,123 (67.0 %)**. At heading granularity (preamble, §1–§3, §4.1, §5, §6 lead, `emit-bugs`) it is 20,427 (75.3 %).

**Verdict: SAFE-AS-IS**, with that declared list.

**Rationale inside the set:** the same rows as `emit-auto`, less lines 159, 164 and 189–196.

### 2.3 Parts no loader caller needs, and what a script could absorb
- **Parts no loader caller needs:**
  - `emit-manual` (384), `emit-prompt` (983) and `emit-block` (2,322). All three are still needed by path readers and by the 27 commands that cite `emit-block` by name.
  - Preamble lines 13–16 (299).
  - The history at 125–129.
- **What a script could absorb:**
  - Resolving the §2 target.
  - File creation with frontmatter.
  - §3 id dedupe and `-2`/`-3` suffixing.
  - Reading `author` from git config.
  - Appending.
  - The deterministic §1.1 rows: secret shapes, emails, home paths, private and routable IPs, single-label and `.internal`/`.local`/… hosts, plus the keep-list patterns.
  - The redaction counts.
- **What must stay with the model:**
  - Projecting a free-form `impl-maintenance` report.
  - Splitting it into distinct signals.
  - `category`, `impact` and the short slug.
  - The judgement rows of §1.1: "an organisation's own internal domain", and "when a hostname could be either, redact it". A script can flag candidates; the model rules on them.

---

## 3. `followup-emission.md` — whole-file loads, no entry point

**Callers:** 12 commands, through `args: "followup-emission"`: `/implement`, `/ready`, `/conformance`, `/epics`, `/prd-proposal`, `/brd-proposal`, `/document` (twice), `/release-notes`, `/docs-init`, `/docs-brand`, `/docs-audit`, `/security-workflows:scan`. Each "executes its steps inline".

The de facto entry point is §8's closing paragraph (lines 138–144), which fixes the order: §6 filter, §2 resolve, §1–§3 render and place, §5 dedupe, §7 confirm, then write. Callers cite §6 11×, §2 7×, §4 4×, §5 4×, §8 3×, §7 2× and §1 1×.

### 3.1 What callers actually use

| Lines | chars | Part | Used by |
|---|---|---|---|
| 16–22, 28–30 | 467 | §1 line form, plain markdown, "link, never restate" | all |
| 32–46 | 1,146 | §2 target, `unit_folder`, `misrooted` and no-folder report-only notices, never the cwd | all. `/docs-brand` cites the no-folder rung. |
| 53–57 | 216 | §3 notes in the same file | all |
| 72–78 | 1,599 | §5 stable key, other-repository and unit identity compared change by change, `SKIP — already exists` | all |
| 80 | 1,854 | § *Withdrawing a follow-up* (bold lead, no heading) | `/conformance`. `/implement` Phase 1 cites it with no load. It ends "No other caller edits a line", a negative rule for everyone. |
| 82 | 1,020 | § *Re-queuing a confirmed fix* | `/conformance`'s PRD run |
| 84 | 1,038 | § *A security finding's line* | `/scan`, and **any caller whose line carries a `[SEC#n]`**. `/implement`'s Phase 6 lines can. |
| 86–107 | 4,117 | §6 qualifying predicate, the other-repository line form and `<repo-slug>` naming, the residual, the no-op rule | all. The first bullet (91–93, 3,008) matters most to `/implement`, `/conformance` and `/scan`. |
| 109–122 | 651 | §7 batch preview and `choices: ["approve-all","select","cancel"]` | all. `/scan` cites it. |
| 124–144 | 1,322 | §8 inputs, per-item `unit_folder`, phase order, additive, never commits | all |

**Not needed by any caller:**
- §4, lines 62–71 (552). This is history of chores that no longer exist.
- Preamble lines 1–15 (989). They hold the caller recipe and the "no longer mirroring" note.
- The history paragraphs at 23–27 (389), 47–52 (498) and 58–61 (212).

**Other references:**
- `workflows-core:specs-repo-git` §3.1, §4 and §8 (session branch, for `/conformance`).
- `workflows-core:components` §1 (`<repo-slug>`) and §3 (known set).
- The design's `Target span:` line.
- `dev-workflows:conformance-format` §3 (`withdraws:`). This is a **cross-plugin** citation from a core reference.
- `workflows-core:security-register-format` §3 (`[SEC#n]`).
- `workflows-core:escalation-rules` §0, implicitly: §7's array is presented verbatim.
- A dangling pointer: lines 77 and 111 tell the reader to "mirror `/wiki-tasks-extract`", which is an `obsidian-llm-wiki` command. Line 11 says the file no longer mirrors anything.

### 3.2 Minimal set and verdict
- **Union over the 12 callers: 13,462 / 16,103 (83.6 %).** At heading granularity (§1, §2, §3, §5, §6, §7, §8; preamble and §4 dropped) it is 14,562 (90.4 %).
- Without the two `/conformance`-only paragraphs, the set is 10,588 (65.8 %).
- **Verdict: SAFE-AS-IS** as an entry point at heading granularity, but there is nothing worth saving.
- A per-caller cut of §5 is **SAFE-WITH-RESTRUCTURE**. The three bold-lead paragraphs would need headings first. The [SEC#n] paragraph must stay in every caller's set, because the rule is keyed on the token, not on the caller.

**Rationale inside the set:** small.
- §6's residual, *The key holds only as far as the name does* (680 chars inside line 91), is needed: `/implement` acts on "§6's residual".
- The "mirrors" pointers (77, 111) are history.
- The worked line at 93 (181) is a needed form.

### 3.3 What a script could absorb
- **Mechanical:**
  - Resolving the target (`unit_folder` or the resolved folder; report-only under `misrooted` or with no folder).
  - Appending.
  - The `[SEC#n]` open-line match.
  - The exact ``repository `<name>` `` and `` `/dev-workflows:implement <KEY>` `` identity comparison. These are the emitter's own fixed forms, compared against the run's own key, never extracted.
  - Grouping the preview by target file.
  - Ticking a withdrawn line with its suffix.
- **Judgement:**
  - §6 qualification.
  - The "change by change … in any words" semantic match.
  - Line wording.
  - The §7 prompt.

---

## 4. `implementation-format.md` — `unit-branch`, plus whole-file loads

**Callers.**
- `unit-branch`: `/conformance`, `/implement` and `/security-workflows:scan`, through `args: "implementation-format unit-branch"`.
- Whole-file loads: 6 commands, each with a different purpose:
  - `/implement` Phase 4.7 appends a block (§1 and §2).
  - `/upgrade` and `/vuln` use the §3 subject and trailer.
  - `/document` and `/release-notes` follow §4.
  - `/conformance` uses §5's merged test and "a unit's work is merged", plus §1's record-present rule and the remedy for a leftover block.

### 4.1 `unit-branch`

**Definition:** `## 5. The unit's branch — \`unit-branch\``, lines 374–438, **12,775 chars**. The heading names it literally.
- Steps 1–3 are lines 393–418, Output 420, `after_merge` 422, the tip 424, and the local-refs and fetch rule 426.
- *The merged test* (428–434) and *A unit's work is merged* (436) are bold-lead paragraphs placed **after** Output and cited as "below".
- Line 438 is a consumer grep that the entry point does not need.

**Dependencies:**

| Lines | chars | Part | Why |
|---|---|---|---|
| 15–35 | ~1,050 | §1 block shape and example | Step 1 needs the block heading `## <YYYY-MM-DD> — /implement` (also used for the `--since` date) and the fields `repo`, `branch`, `base`, `commit`. Line 17 adds that a block written before 4.7.0 may carry **several entries**, so step 1 must pick the entry whose `repo:` matches. |
| 37–39 | 242 | Append-only | A re-run adds a block, which is why step 1 takes the latest *matching* block. |
| 41–45 | 441 | "A record is present only where it holds a block" | A file holding only its heading gives `none`. |
| 47–55 | 787 | Where it lives; "a block names no unit … no reader infers a unit from a branch name" | Settles the "this file, in the unit's own folder" input, and forbids inferring the unit from a branch name. |
| 57–68 | 1,046 | A PRD-folder block left for an Epic belongs to the PRD folder | Included as a doubtful case. It guards against a plausible mistake: falling back to the PRD folder's record when an Epic has none. Line 67–68 states `unit-branch` answers `none` there. |
| 196–205 | 873 | §4 "A token matches only as a whole key" | **Needed.** The merged test's subject leg says "each subject matched as §4 matches a key". Without the wrap `(^|[^A-Za-z0-9_-])…([^A-Za-z0-9_-]|$)` and the ERE escaping, `ACME-7` matches `[ACME-77]`. That falsely passes the merged test, which yields a wrong `after_merge: true`, or a wrong `merged` wherever the content test cannot run (git < 2.38, a shallow clone). |
| 271–275 | 410 | §4 "search for tokens the run already holds, never an extraction" | Included as a doubtful case: `<key>` is the folder's key and is never read from a subject. |

**Not needed:**
- §1 lines 69–107: `/ready`'s rule, the operator's move, durability and `pushed:`.
- §2.
- §3. The merged test restates what it needs at lines 430 and 434.
- §4 apart from the two ranges above (16,678 chars).

**Other references:**
- `workflows-core:components` §1 (`<repo-slug>`).
- `workflows-core:read-only-repos` §1, the read-only probe that step 2's scratch-object block depends on. **None of the three callers loads `read-only-repos` through the loader. They cite §1 by name.**
- `workflows-core:read-only-repos` §3 (`<ref>`).
- `workflows-core:addressing` §1 (the characters a key is made of, cited by the boundary).

**Minimal set:** **17,431 / 43,070 (40.5 %)**. At heading granularity (§1 + §4 + §5) it would be 37,979 (88 %), which defeats the purpose.

**Verdict: SAFE-WITH-RESTRUCTURE.** Two edits are needed first:
- **(a)** Give the whole-key boundary (196–205) a heading of its own, or restate the regex inside *The merged test*.
- **(b)** Split §1 so that block shape, presence and location (15–55, plus 57–68) can be addressed apart from `/ready`'s and the operator's material (69–107).

Two further edits would help:
- Give *The merged test* a heading, since `/conformance` cites it by name.
- Settle one ambiguity: line 430 says the subject must carry "`[<key>]` … as a whole token" and also be "matched as §4 matches a key". §4's boundary also matches a bare `ACME-7`, so it is unclear whether the brackets are required.

**Rationale and edge-case text inside the set:**

| Lines | chars | Kind | Needed? |
|---|---|---|---|
| 376–382 | 347 | Consumer list | Context only. |
| 399 | 584 of 1,386 | Why split Bash calls fail | **Keep.** It is the guard against splitting the block. |
| 407 | ~200 | Why `rc` is kept | Keep: a conflict on git 2.43 could read as "adds nothing". |
| 409 | 395 + 278 | The deliberate misses | Needed by consumers to word a report. Not needed to compute the state. |
| 413 | 899 | Trade-offs of removing a stale tracking ref | Edge-case explanation only. |
| 434 | 349 | Why the squash keeps the subject, and why the date matters | Rationale. |
| 200–205 | 545 | History of the over-match | Rationale. |
| 57–62 | 572 | Pre-4.1.2 history | Edge guard; see the dependency row for lines 57–68. |

The worked example at 19–35 (400) is needed as the block schema.

### 4.2 Whole-file callers — what each actually uses

| Caller | Parts used | chars | Share of file |
|---|---|---|---|
| `/implement` Phase 4.7 (append) | §1 15–55, 95–108; §2 109–124 | 4,569 | 10.6 % |
| `/upgrade`, `/vuln` (subject and trailer) | §3 table rows 125–135 and bullets 147–157 | 1,686 | 3.9 % |
| `/document`, `/release-notes` | §1 whole, §2, §3's third bullet (147–156), §4 whole | 27,000 | 62.7 % |
| `/conformance` (whole-file load beside `unit-branch`) | §1 15–93, §4 196–205 and 271–275, §5 374–437 | 19,935 | 46.3 % |

**Cross-file needs of these callers:**
- `dev-workflows:code-handoff` §1 rule 5, §2.1, §2.3, §3.1.
- `workflows-core:branch-naming` §1.1 and §1.4.
- `workflows-core:prd-format` (`workitem_key`).
- `docs-workflows:release-note-types` §1 (the read-set form and the 12-character SHA).
- `docs-workflows:key-discovery` (the script that runs §4's scan, probe and PR layer).
- `workflows-core:epic-picker`.
- `dev-workflows:workflow-states`.
- `workflows-core:components` §3.
- `workflows-core:source-truth`.
- `workflows-core:specs-repo-git` §3.5.

**Verdict:** **SAFE-WITH-RESTRUCTURE.** The file has four audiences behind one name. Splitting it would need these entry points: `record-block` (§1–§2), `commit-convention` (§3), `two-source-read` (§1, §2, §3's third bullet, §4), `unit-branch` and `merged-test`. Whole-file loads stay safe until then.

**History inside §4:** the population paragraphs and the refused alternatives (for example 258–262, 441 chars; 220–227; 316–321; 356–359) are rationale. They are not needed to run the scan, but they are needed to explain a loss to the user.

### 4.3 Parts no caller needs, and what a script could absorb
- **Parts no caller needs:**
  - Line 5 (238), the design-authority history.
  - Lines 136–145 (932), §3's history.
  - §4's refused-alternative and population paragraphs, which are explanatory only.
- **What a script could absorb:**
  - **`unit-branch`, entirely.** It takes `repo`, `slug`, `key`, `implementation.md` and `ref`, and returns JSON `{state, branch, base, commit, tip, after_merge}` plus flags for read-only, shallow and not-compared. The script would:
    - parse the blocks and pick the entry;
    - run the ancestry leg, and the subject leg with the whole-key regex and the `--since` date;
    - run the content test, including detecting `--write-tree` from `merge-tree -h`, the scratch object directory on a read-only mount, and reading `rc`;
    - run step 3;
    - optionally do the refspec fetch and remove a stale tracking ref (writable clones only).

    That would replace about 12.7 K of prose with a contract of about 2 K. Each consumer's handling of each state stays in the consumer.
  - §1 append: a block with a file header. This is mechanical.
  - §3 subject suffix. Already in `code-handoff`.
  - §4's scan, probe and PR layer: already in `key-discovery.py`. The remaining `/release-notes` prose could be absorbed there too: block-granular boundary, SHA resolution and dedupe, the date fallback, and its listings.
- **What must stay with the model:** the wording of the consumers' reports, and choosing scope. The records a read takes are mechanical once the folder tree is resolved.

---

## 5. Summary table

| Entry point | Definition (chars) | Minimal set | Heading-granularity set | Whole file | Verdict |
|---|---|---|---|---|---|
| `cost-emission emit-cost` | 6,959 | 53,739 (80.5 %) | 59,912 (89.8 %) | 66,724 | SAFE-AS-IS at heading granularity; SAFE-WITH-RESTRUCTURE for the fine cut (split §4 and the preamble). Never cut per caller. |
| `feedback-emission emit-auto` | 991 | 21,008 (77.5 %) | 22,145 (81.6 %) | 27,123 | SAFE-AS-IS with a declared list, which must include §4.1 and the §6 lead. |
| `feedback-emission emit-bugs` | 1,289 | 18,162 (67.0 %) | 20,427 (75.3 %) | 27,123 | SAFE-AS-IS with a declared list. |
| `followup-emission` (whole) | n/a (§8 lead) | 13,462 (83.6 %) | 14,562 (90.4 %) | 16,103 | SAFE-AS-IS; there is nothing to gain. |
| `implementation-format unit-branch` | 12,775 | 17,431 (40.5 %) | 37,979 (88 %) | 43,070 | SAFE-WITH-RESTRUCTURE: give the §4 whole-key boundary a heading and split §1. |
| `implementation-format` (whole, 6 callers) | — | 1.7 K–27 K per caller | — | 43,070 | SAFE-WITH-RESTRUCTURE: four audiences, so four entry points. |

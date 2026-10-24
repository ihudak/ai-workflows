<!-- Copied unchanged from lean context D's SDD workspace (W/worse-cost.md), a read-only Opus investigation run after the first live runs, preserved by Ruling 23 so every fix it recommended or refused keeps its argued evidence. The paths it names under .superpowers/sdd/ and .worktrees/ were scratch and are removed after the merge; paths under ~/ or /home/<user>/ are on the maintainer's machine; /tmp/.../scratchpad/ paths were session scratch. Where it and the shipped text disagree, the shipped text is the authority. Companion to 2026-10-22-lean-context-handoff-part.md. -->

# Lean context D: where the extra cost in runs 2, 3 and 4 comes from

Read-only investigation, written 2026-10-23. It covers D (worktree `lean-context-handoff-part`, text diff `11a4fa70..HEAD`) against part 1 ("P1"). Every dollar figure is replayed from the transcripts. The per-call replay reproduces each session's measured cost to the cent: $8.80, $6.69, $15.64, $12.51, $22.88 and $24.67.

## 0. Summary

1. **Part of each gap is a measurement artifact, not cost.** The P1 sessions were recorded by Claude Code **2.1.306** (run 1's by 2.1.304). In those versions a subagent's transcript rows store the streaming-start placeholder for `output_tokens` (values like 2, 3, 8 or 16), not the final count. The D sessions were recorded by 2.1.309, which stores the real count, including `thinking_tokens`. Examples:
   - The P1 run-4 `risk-planner` records 755 output tokens for 27,174 visible output characters.
   - The P1 run-2 `code-grounder` records 1,192 tokens for 36,735 characters.
   - The final ~8k-character report message of each P1 `code-review` records 9 and 3 tokens.

   Main-session rows are correct in both versions. P1's subagent output, re-estimated with D's own tokens-per-visible-character ratio for each agent type, is missing **$3.28 in run 2, $0.21 in run 3 and $1.17 in run 4** (and $0.18 in run 1). Run 5's P1 was recorded by 2.1.307, which records correctly, so it needs no correction. The controller's "in run 2 more subagent spend" is entirely this artifact: corrected, D's run-2 subagents cost about the same as P1's ($8.39 vs ~$8.46). On the input side, which is recorded reliably, D's are $0.17 cheaper.
2. **What D's own text costs is small, and it is not only the core load.**

   | Run | D's own text, net |
   |---|---|
   | 2 | +$0.28 |
   | 3 | +$0.31 |
   | 4 | −$0.26 |

   The parts:
   - **Core load: $0.16–0.23 a run.** That is about twice the $0.07 stated, because the loader's own body (~2.1k tokens) is injected for that request too.
   - **Loader body growth: $0.16–0.28 a run.** D added a ~2.2k-character paragraph to `skills/reference/SKILL.md`, and that file is re-injected on *every* loader request, about 0.68k tokens each time.
   - **A second read of the `require-on-main` file: $0.06–0.07 a run.** The file is about 26.4k tokens, more than one Read returns.
   - **`phase-handoff.md` grew by 4.5k: about $0.02.**
   - **Offset by the `require-on-main` part file:** −$0.84 against run 4's whole read, −$0.19 against run 2's sliced P1 read.
3. **Most of the true gap comes from the model's choices, through one mechanism that recurs on every run: loading a reference takes 2–7 turns** (Skill call alone → `wc -l` → Read → Read …). P1's run-1 and run-2 sessions issued the Skill call and the Read in the same turn; D's did not. Collapsing each load to ≤2 turns would save **$0.48–1.72 a run on D's runs** (and $0.02–1.53 on P1's). That is the one fix worth making now.
4. **Part 1's text, applied by one side only:**
   - The `commit-artifacts` whole re-read under Ruling 69 costs $0.68 (run 3) and $0.71 (run 4) with its turns. Each time one run's model skipped it.
   - The handoff phase's whole read under Ruling 68 costs $0.25 (run 2); P1 sliced it.
   - Run 3's `security-register-format` load costs $0.37.
   - Run 3's loader requests that P1 bypassed by reading the files by path cost $0.34.

## 1. Per-run attribution

Classes: **meas** = P1 subagent output that Claude Code ≤2.1.306 did not record. **a** = caused by D's text (`11a4fa70..HEAD`, as it stood at each run; run 2 ran at `06bc6845`, before the 8b grounding changes). **b** = part 1's merged text, present in both runs but followed by only one. **c** = model/run variance. A positive figure is D more expensive.

Method:
- `scratchpad/cost/sim.py` replays each main session call by call: cache read of the carried context, the 1h write of the new content, and output, at Opus 5.5 rates. It then removes or merges the turns and content of one mechanism and re-prices the run.
- `outfix.py` makes the output correction. `an.py` breaks the cost down per subagent.

The scratchpad is `/tmp/claude-502/-workspace-ai-workflows/80e0a056-a775-409e-9cb9-213f6b475bf7/scratchpad/cost/`.

### Run 2 — `/prd-ground BOOK-2-01 --no-docs` (D ffdfa804 vs P1 8fa7aefc)

Recorded gap +$6.34 (main +$3.13, subagents +$3.21). True gap about **+$3.06**.

| Class | $ | What |
|---|---|---|
| meas | +3.28 | P1 subagent output not recorded: `code-grounder` +0.99, the four `grounding-verifier` dispatches +0.21/+0.93/+0.81/+0.32, `impl-maintenance` +0.02. Same dispatches on both sides (1 grounder, 4 verifiers including one retry pair, 1 maintenance), same models (Opus/Sonnet). Brief sizes match: compare brief 46.8k vs 43.2k. |
| a | +0.17 | `escalation-rules core`: 3.8k tokens of content plus 2.1k of loader body, carried for ~100 calls |
| a | +0.17 | Loader body +0.68k tokens on each of 13 main requests |
| a | +0.05 | The same growth inside the 5 grounding agents (2 loader requests each) |
| a | +0.06 | `require-on-main` file tail re-read (call 20) |
| a | +0.02 | `phase-handoff.md` +4.5k, read whole at the handoff phase |
| a | −0.19 | `require-on-main` part file (70k) instead of P1's 90.5k Phase-0 slice. Against a whole read, which Ruling 68 asks for, it would save ~$0.8. |
| b | +0.25 | The handoff phase read `phase-handoff` whole (143k, Ruling 68); P1 read 93k of it in slices |
| c | +1.36 | Reference-loading turn pattern: 51 loading-only turns vs P1's 31. D called the Skill alone (12 turns), then `wc -l` (8 turns), then the reads. P1 put Skill, Read and Read in one turn every time. |
| c | +1.29 | 8 more non-loading main turns at 450–550k context (a leading-slash investigation, Edit plus Python checks, handoff steps), and a code-grounding file 35% longer (+0.10) |
| c | −0.12 | Subagent remainder after correction (input side −0.17) |

### Run 3 — `/security-workflows:scan BOOK-2-01-02` (D afedd011 vs P1 796118d3)

Recorded gap +$2.40 (main +$2.11, subagents +$0.29). True gap about **+$2.19**.

| Class | $ | What |
|---|---|---|
| meas | +0.21 | P1's 7 `scan-researcher`s plus maintenance agents; output not recorded |
| a | +0.155 | `escalation-rules core` (batched with run-flags, so no extra turn): 3.9k content plus 2.1k loader body |
| a | +0.155 | Loader body +0.68k tokens × 13 requests |
| b | +0.675 | `commit-artifacts` re-read `specs-repo-git` whole (123k = 45.7k tokens) in 3 turns (Skill, Read, Read). Ruling 69's bound requires it from Phase 7. P1's model worked from its Phase-0 read. Content alone ≈ $0.41; the controller's "$0.39" left out the turns. |
| b | +0.367 | `security-register-format` loaded (Skill, `wc -l`, Read: 26k). `scan.md:18` cites it as the register's authority; P1 never loaded it. |
| b | +0.338 | Six loader requests made as their own turns (specs-preflight, read-only-repos, model-routing, next-phase-offer, session-hygiene ×2, feedback-emission). P1 read those files directly by path, against `scan.md:10` ("never by path"). |
| c | +0.42 | 7 more main turns: extra Bash steps in Record and Close, one more wait poll |
| c | +0.08 | Subagents: one researcher took 8 calls vs 5 |

### Run 4 — `/dev-workflows:implement BOOK-2-01-02` (D b931a312 vs P1 586ecaf9)

Recorded gap +$0.67 (main −$1.78, subagents +$2.45). True gap about **−$0.50**: D is cheaper.

| Class | $ | What |
|---|---|---|
| meas | +1.17 | P1 subagent output not recorded: `risk-planner` +0.51, `code-writer` +0.19, two `code-review`s +0.28, `test-baseliner`/`code-scanner`/maintenance +0.19 |
| a | −0.84 | `require-on-main` read its part file (62.0k + 7.9k, ~26.6k tokens) where P1 read `phase-handoff` whole (138.7k, ~51k tokens), carried ~132 calls |
| a | +0.23 | `escalation-rules core` (content plus loader body) |
| a | +0.26 | Loader body growth × 15 main requests (+0.02 in 4 subagent requests) |
| a | +0.07 | `require-on-main` tail re-read turn |
| b | −0.71 | P1 re-read `specs-repo-git` whole at `commit-artifacts` (Ruling 69). D's model committed from its Phase-0 read, with no loader call at all. |
| c | +0.36 | D loaded `bug-diagnosis` (its model ran the SEC#1 fix as `task_shape: bug`) |
| c | +0.25 | D read `code-handoff` almost whole in Phase 1 (57.8k); P1 read slices and then the rest at the end |
| c | −1.40 | P1 made 10 more main turns at 500–700k context, 5 of them loading turns |
| c | +1.26 | Subagents after correction (below) |

**Run 4 subagents, +$2.45 recorded:**

| Share | $ |
|---|---|
| Measurement | 1.17 |
| D's text (loader body in 4 agent requests) | 0.02 |
| Variance | ≈1.26 |

The variance by agent:

| Agent | D vs P1 corrected | Why |
|---|---|---|
| `risk-planner` | +$0.70 ($2.02 vs $1.32) | 17 vs 14 calls, max context 185k vs 116k: it read more code. Brief 5.2k vs 6.6k. |
| First `code-review` | +$0.52 ($1.56 vs $1.04) | 25 vs 15 calls. P1's orchestrator pasted a 13.1k brief, D's 5.8k, so D's reviewer explored more itself. |
| `code-writer` | +$0.15 | |
| `code-scanner` | +$0.06 | |
| Re-review | −$0.10 | |
| The rest | ≈0 | |

None of these agents or their briefs' templates changed in D. `implement.md`'s diff is the core step and the session-model gate wording only.

## 2. Is D's own cost only the core load? (task 3)

No. The other effects of D's text, measured:

| Effect | Per run | Runs |
|---|---|---|
| Core load, including the loader body its request injects | +$0.16–0.23 | all (36 commands) |
| `SKILL.md` +2.2k chars (lines 57–84 and the "save …" clauses at 17–18 and 88–90), re-injected with every request: D's loader body is 6.6k chars (~2.0k tokens) vs P1's 4.2k (~1.35k) | +$0.16–0.26 main, +$0.02–0.05 in subagents | every run: 9–16 requests a run; grounding, review and planning agents make their own |
| `require-on-main` part file vs whole/sliced reads | −$0.19 (run 2, vs a P1 that sliced), −$0.84 (run 4, vs whole) | 1, 2, 4, 5 |
| Its second read: the 229-line, 69.8k-char file is ~26.4k tokens, above the Read cap. Even with `allow_large` the first read returns lines 1–192, so every consumer reads 193–229 again in a turn of its own. | +$0.06–0.07 | 1, 2, 4, 5 |
| `phase-handoff.md` +4.5k (region markers 0.46k, re-placed §2.6.1 and the declaration block), read whole at handoff | ≈ +$0.02 | runs with a handoff phase |
| `ard-resolution.md` +0.56k | ≈ +$0.01 | 4 |
| Reworded citations: prd-ground's two path-form citations, the held-section citation rule | not measurable. Run 2's `coverage-ledger`/`brd-format` slices match P1's in count and size. | — |
| check-questions steps | none beyond the core step itself | — |

So D's text costs **+$0.28 (run 2), +$0.31 (run 3) and −$0.26 (run 4)**. The rest of each gap is the measurement artifact, part 1's text, or variance.

## 3. Recurring mechanisms, governing text, fixes

WT = `/workspace/ai-workflows/.worktrees/lean-context-handoff-part`.

### M1. A reference load takes 2–7 turns (biggest; fix it)

Each loader request, made after the run already holds the loader's text, is often its own turn. The model typically:
1. calls `Skill(workflows-core:reference, …)` alone;
2. runs `wc -l <file>` alone, because `SKILL.md` requires a whole read "in consecutive ranges from its first line to its last" and Read truncates silently with `allow_large`;
3. issues the reads one per turn.

Sometimes it also `cat`s a large file, gets back a pointer to a saved copy, and Reads that.

Measured loading-only turns:

| Run | D | P1 |
|---|---|---|
| 1 | 49 | 30 |
| 2 | 54 | 30 |
| 3 | 29 | 16 |
| 4 | 46 | 58 |
| 5 | 46 | 46 |

`wc -l`-only turns are 3–17 in D and 3–6 in P1. P1's runs 1 and 2 issued Skill and Read together in every load (14/14 and 12/12), and that is why they were cheap. It is variance in the model's habit, not a text difference; nothing in either text says to batch.

- **Governing text.**
  - WT `plugins/workflows-core/skills/reference/SKILL.md:86-93`: the whole read in consecutive ranges, the source of the `wc -l` pre-check.
  - `SKILL.md:21-34`: reuse.
  - Every command's "Core references." preamble, e.g. WT `plugins/security-workflows/commands/scan.md:10`, `plugins/dev-workflows/commands/implement.md:12`, `plugins/product-workflows/commands/prd-ground.md:9`, which says how to load, not when.
- **Fix.** Add one paragraph to `SKILL.md`, after line 93, in substance: *"Where this text is already in this conversation from an earlier request in this run, you know the paths it names: make a request's Skill call and the reads it names in one turn — the file's `wc -l` where a whole read needs its length, and its first read, with the Read tool, never `cat` — then any further ranges together in one more turn. Where the text that arrives names a different read, make that read as well."*
- **Rules at the moment they apply.** The loader's body still arrives with every request, before the step executes. The reads are the ones the request makes anyway. A misprediction costs one read, never a rule. The first request of a run is unaffected: the path is not yet known.
- **Saving.** Collapsing each loader group to ≤2 turns, replayed per run:
  - D: $1.72, $1.30, $0.60, $1.03 and $0.48 (runs 1–5), about $1.0 a run.
  - P1: $0.38, $0.80, $0.02, $1.16 and $1.53.
  - Collapsing to 1 turn is the upper bound: $0.95–2.52.
  - The extra text costs about 0.12k tokens × ~13 requests ≈ $0.03 a run.
- **Who benefits.** All five runs, and every command, since each makes 9–16 loader requests. One live run should confirm the model complies; P1's runs 1 and 2 show that a parallel Skill+Read works in this harness.

### M2. The loader body is re-injected on every request, and D made it 55% bigger (fix it, lower priority)

`SKILL.md` (6,233 bytes) comes back as a ~2.0k-token meta message on each `Skill(workflows-core:reference)` call. Over a D run that is $0.46–0.75; over a P1 run, $0.06–0.53. D's paragraph at `SKILL.md:57-84` (plus the clauses at 17–18 and 88–90) applies only to requests on `phase-handoff`, yet rides on every request: +$0.16–0.26 a run in the main session.

- **Governing text.** WT `plugins/workflows-core/skills/reference/SKILL.md:57-84`, and the held-list check in `scripts/reference-parts.py check-citations`, which reads the list from `SKILL.md` (commit fa82fbe0).
- **Fix.**
  - Move the paragraph's body to a generated file read only on a `phase-handoff` request, e.g. `reference-parts/phase-handoff/loading.md` or the head of the entry-point file.
  - Leave one trigger sentence in `SKILL.md`: *"A request on `phase-handoff`, with or without a second argument, first reads `…/reference-parts/phase-handoff/loading.md` unless its text is in this conversation."*
  - Point the gate at the new file.
- **Rules at the moment they apply.** The trigger fires on every `phase-handoff` request, including a held-section citation that comes before the request in the same `##` section, so every case the paragraph decides still has it in front of the model.
- **Saving.** About $0.15–0.25 a run net: the growth removed, minus ~0.7k tokens read once in runs that use `phase-handoff`, and no extra turn under M1. It benefits every run.
- **Fallback.** If the gate change is unwelcome, rewrite the paragraph to half its length. The second half restates the complement of the first. That saves about $0.08 a run.

### M3. The `require-on-main` file needs two reads (fold into M1; no separate change)

At 69.8k characters (WT `plugins/workflows-core/reference-parts/phase-handoff/require-on-main.md`, generated from `references/phase-handoff.md`'s region markers), the file exceeds one Read. That costs one extra turn, $0.06–0.07, in runs 1, 2, 4 and 5.

Under M1 the tail read joins the follow-up turn. Trimming rules to fit is not acceptable. The optional extra: have the generator write the file's line count in the line under its title, so that both ranges go out at once without `wc -l`. That saves about $0.06 a run, and is low priority.

### M4. `commit-artifacts` re-reads `specs-repo-git` whole at the end of the run (no change now)

The re-read is 123k characters (~45.7k tokens) plus 3 turns: $0.68 in run 3 (D) and $0.71 in run 4 (P1). Run 2 paid it on both sides. Two of the six sessions (P1 run 3, D run 4) skipped it. Their terminal commit ran from the Phase-0 read, which means Ruling 69's bound went unapplied. That is worth noting as a quality observation, not a cost to cut.

- **Governing text.**
  - WT `SKILL.md:21-29`: the reuse bound (Rulings 69 and 82, which stand by the user's decisions of 2026-10-21 and 2026-10-22).
  - `plugins/workflows-core/references/specs-repo-git.md:550` (§4).
  - The terminal steps `implement.md:1360`, `prd-ground.md:2146` and `scan.md:541`.
- **Why no change.** A `commit-artifacts` entry-point file still needs ~71% of the file (D spec, first table). It would save ~$0.12 a run and still take two reads. Part 3's script is the lever, as planned.
- **The same applies to `specs-preflight`'s whole Phase-0 read.** Carried over the whole run, it is the largest single reference cost, $1.0–1.6 a run in both D and P1, and no part of the gap.

### M5. Run 3's `security-register-format` load (no change)

`scan.md:18` names it the register's authority, and Phases 4–5 apply its §5 rules (`scan.md:181`, `:200`, `:317`, `:554`). D loaded it once ($0.37). P1 never did, so P1 worked without those rules in front of it. Keeping it is the quality-first answer. If anything, the load should become an explicit step at Phase 4, which is a quality change, not a cost one.

### M6. Subagent spend (no change)

Once the measurement is corrected:
- Run 2's subagents are equal on both sides.
- Run 3's differ by +$0.08.
- Run 4's +$1.26 comes from two Opus agents exploring more: `risk-planner` with 3 more calls and +69k of peak context, and the first `code-review` with 10 more calls after a 5.8k brief vs P1's 13.1k.

The dispatch counts, models and brief templates are the same on both sides, and D changed none of them. No text drives this.

### Measurement fix (do before the next comparison)

When any baseline was recorded by Claude Code ≤2.1.306, re-estimate subagent output (as `outfix.py` does), or re-run the baseline. With the correction, the five runs come out:

| Run | D | P1 corrected | Gap |
|---|---|---|---|
| 1 | $12.66 | ~$12.63 | +0.2% |
| 2 | $24.03 | ~$20.97 | +14.6% |
| 3 | $10.65 | ~$8.46 | +25.9% |
| 4 | $30.36 | ~$30.86 | −1.6% |
| 5 | $30.92 | $31.82 | −2.8% |

The plugin's own `session-cost.py` entries written on those Claude Code versions under-report the same way.

## 4. Recommendation

1. **Do M1:** one paragraph in `SKILL.md`, verified by one live run. It is the only change worth about $1 a run, it reaches every command, and no rule moves.
2. **Do M2** if a change to the gate's held-list source is acceptable; otherwise compress the paragraph. Either removes most of D's own recurring cost.
3. **No change** for M3 beyond M1, M4 (Part 3), M5 or M6.
4. Treat run 3's remaining gap as Ruling 69 and the register load (text that is followed) plus loader turns (fixed by M1). Treat run 2's as loader turns plus variance. Neither calls for undoing D: D's text is net +$0.28, +$0.31 and −$0.26 on runs 2–4, and the `require-on-main` part file is a saving in every run that reads it whole.

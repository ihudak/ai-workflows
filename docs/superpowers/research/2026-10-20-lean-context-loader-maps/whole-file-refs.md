# Whole-file shared references: who needs which part

Scope: five references under `plugins/workflows-core/references/` that callers load whole through `Skill(skill: "workflows-core:reference", args: "<name>")`. Read-only map for deciding whether callers could load only the part they need. Quality is the governing constraint: where a part's need was uncertain, it is counted as needed and the reason given.

## Method and caveats

- **Sizes are characters** (Python `len` over the file, headings and blank lines included), not bytes. `wc -c` reports slightly more bytes because of em-dashes and arrows: escalation-rules is 53,832 chars against 54,221 bytes.
- **Callers.** Every mention of the reference name was grepped over `plugins/*/commands`, `plugins/*/agents`, `plugins/*/references/**` and `plugins/*/skills/**`, with `docs/` and `CHANGELOG.md` excluded. Each mention was matched to the nearest named rule in a ±300-character window and then hand-corrected. Scratch outputs are `esc-ctx2.txt`, `npo-ctx.txt`, `ft-ctx.txt` and `sh-ctx.txt` beside this file. Where a rule's own citer list names more callers than the grep attributed to it, the extra callers are added below.
- **Two ways a caller loads.**
  - An *explicit* loader call: `args: "<name>"` (escalation-rules 48 calls in 23 files, next-phase-offer 20/20, session-hygiene 23/23, untrusted-content 28 command calls plus the file's own quoted sentence, finding-triage 11/11).
  - A *citation-only* caller writes `workflows-core:<name>` and loads through its **Core references** preamble ("Load it with `Skill(skill: "workflows-core:reference", args: "<name>")`"). That preamble names a file, never a part, so today a citation-only caller also loads the whole file. Example: `/brd-split` cites escalation-rules 14 times and makes no explicit call.
- The loader reads the whole file on every call and says *"Never paraphrase, summarise, or cache its contents"*. A caller with four calls (`/specify`, `/epics`, `/design` for escalation-rules) therefore re-reads 54k four times.
- **Live-run evidence.** `../r3m-reads.txt` (the 2026-10-20 route-3 `/implement` run, main session) shows:
  - `finding-triage` read whole (18.1k) at the triage sub-step, after a review that had no findings.
  - `session-hygiene` read as §1 only, via `awk`, at the resume-pointer step (4.3k).
  - No load at all of `escalation-rules`, `next-phase-offer` or `untrusted-content`.

  So partial reading already happens informally, and the largest file was not read even once in that run.

---

## 1. escalation-rules.md (53,832 chars, 651 lines)

### 1.1 Structure

| # | Section | Lines | Chars |
|---|---|---|---|
| H | Title + precedence sentence ("Command bodies are authoritative; where `/document` and `/epics` differ … both variants are listed") | 1–5 | 211 |
| A | §0 Array shape (2–4 options, harness free-text; *A selection carries no text*) | 6–40 | 2,541 |
| B | Choice lists are presented verbatim | 41–54 | 934 |
| C | Closed-vocabulary pickers must normalise the free-text answer (the eleven-row table) | 55–128 | 7,915 |
| D | The `(Recommended)` marker is unconditional (incl. placeholder rule, *When no option is safe to recommend*) | 129–158 | 2,075 |
| E | When a choice list fires (incl. inline-confirmation form) | 159–186 | 1,490 |
| F | key dir not found | 187–202 | 989 |
| G | Required path environment variable unset | 203–249 | 3,894 |
| H1 | Repo unresolved (zero matches) — /document | 250–258 | 526 |
| H2 | Repo unresolved (zero matches) — /epics (**holds the shared "Specify a different absolute path" paragraph, L266–269**) | 259–270 | 641 |
| H3 | Repo unresolved (zero matches) — /prd-ground | 271–279 | 585 |
| I | No repos derivable — /epics (+ /prd-ground variant) | 280–301 | 1,457 |
| J | Repo missing (after resolution) | 302–314 | 765 |
| K | Stashing the user's changes | 315–348 | 2,976 |
| L | Dirty working tree | 349–379 | 2,351 |
| M | Branch prefix undetected | 380–391 | 1,742 |
| N | Refresh blocked | 392–401 | 573 |
| O | Read-only mount — ref stale or diverged | 402–411 | 1,163 |
| P | A recorded verdict names the version it was taken against | 412–445 | 3,021 |
| Q | Findings a review leaves open — the offer to apply them | 446–485 | 3,295 |
| R | Edits after a verdict that is not BLOCK — the unspent re-review | 486–532 | 4,167 |
| S | An inline fix is read against what it overlaps | 533–569 | 2,725 |
| T | A finding left open that needs a decision is recorded in the artifact | 570–625 | 4,415 |
| U1 | Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline | 626–632 | 1,630 |
| U2 | … — /document | 633–640 | 712 |
| U3 | … — /epics | 641–652 | 1,040 |

### 1.2 Who relies on what, and when

The file has 244 mentions across 46 files: 23 commands make explicit calls, the remaining files are citation-only, and 13 are references that cite it.

| Section(s) | Callers | Citing phrase (example) | When in the run |
|---|---|---|---|
| A §0 | 26 files: nearly every interactive command (`/design` `/implement` `/ready` `/conformance` `/document` `/release-notes` `/docs-profile` `/specify` `/create-ard` `/create-prd` `/update-prd` `/epics` `/scan` and every `/brd-*` and proposal command), plus `epic-picker`, `grilling-technique`, `next-phase-offer`, `architecture-promotion`, `brd-format`, `coverage-model` | `/design` L130: "Use `choices` arrays; 2–4 options, and never author an "Other" option — the harness supplies the free-text escape itself (`Skill(… "escalation-rules")` §0)"; `/implement` L276: "(`workflows-core:escalation-rules` §0, *A selection carries no text*)" | Explicitly loaded at **Phase 1 ("Rule: Ask, don't guess")** and restated in **Invariants**. Binds every prompt from Phase 0 to the final next-step offer. |
| B verbatim | `/implement` `/document` `/release-notes` `/create-prd` `/update-prd` `/create-ard` `/prd-ground` `/brd-split` `/brd-proposal` `/prd-proposal` `/idea` `/scan`, plus `gate-ledger`, `toolchain-preflight`, `phase-handoff` §4.3, `next-phase-offer` | `/document` Invariants L1486: "the "Choice lists are presented verbatim" rule … binds every prompt in this command"; `/prd-proposal` L744: "`<merge-clause>` … are substitutions, not rewordings (*Choice lists are presented verbatim*)" | Every prompt; cited most at **Next steps** and at mid-run walks (`/brd-split` Phase 4 Steps 1, 2 and 2R). |
| D `(Recommended)` / *no option safe* | `/conformance` (Phase 4 walk), `/design` (Phase 5), `/vuln` (test-failure prompt), `/document` (Phase 1.5), `/create-prd` (Phase 0), `/brd-intake` (Phases 0, 3, 4 and 8), `/brd-interview` (Phase 11), `/brd-package` (Phases 5 and 10), `/brd-reconcile` (Phases 10 and 14), `/brd-split` (Phases 4 and 7), `coverage-ledger-format` §5 | `/brd-intake` L194: "the omission is deliberate per the `When no option is safe to recommend` guidance in `Skill(…)`"; `/brd-split` L1461: "`<later-recommended>` is a placeholder this run resolves once, as … *The `(Recommended)` marker is unconditional* sanctions" | Wherever a list is shown. Explicit loads in `/create-prd` Phase 0, `/brd-intake` Phases 0 and 8, `/brd-interview` Phase 11, `/brd-package` Phase 5 and `/brd-reconcile` Phase 10. |
| E fires / inline confirmation | `/idea` (Phases 1, 1.5 and 2.6), `/brd-package` (Phase 5), `/brd-split` (Phase 4 Step 1). The rule itself says it binds every command. | `/idea` L155: "Per `workflows-core:escalation-rules` ("When a choice list fires"), a list is shown only where…" | Mid-run decision points. |
| C closed vocabulary | the 7 owners of its 11 rows: `/conformance` Phase 4, `/implement` Phase 3B step 7, `/brd-reconcile` Phases 4 and 10, `/brd-interview` Phase 8, `/brd-package` Phases 4 and 5, `/prd-proposal` Phase 2, `/brd-proposal` Phase 5 | `/conformance` L258: "(`workflows-core:escalation-rules`, the `/conformance` decision picker)" | Only at the owner's picker. |
| F key dir not found | `/conformance` `/design` `/ready` `/implement` `/document` `/release-notes` `/specify` (Steps A and B) `/update-prd` `/scan` | `/conformance` L37: "`absent` → stop with the `key dir not found` rule of `Skill(…)`" | **Phase 0** address resolution. 6 of the explicit calls sit here. |
| G env var unset | SPECS_PATH: `/implement` `/document` `/release-notes` `/idea` `/frames` `/scan` and every `/brd-*`, `/prd-ground` and proposal command. REPOS_PATH: `/design` `/specify` `/create-ard` `/epics` `/document` `/release-notes` `/prd-ground`, and `/brd-split` Phase 7 (*Ground now*). Also `addressing` `specs-root-check` and `specs-repo-git` §3.1. | `/brd-intake` L52: "If unset, stop naming `SPECS_PATH`, per the `Required path environment variable unset` rule" | **Phase 0** (SPECS_PATH) or **Phase 1** (REPOS_PATH). |
| H1–H3, I, J repo resolution | `/document` Phases 4–5; `/epics` Phases 4–5; `/design` Phase 3; `/specify` Phases 3–4; `/prd-ground` Phase 1; `/idea` Phase 2.6; `/create-ard` Phase 3; `/release-notes` Phase 5; `/implement` Phase 1.7; `/docs-audit` Phase 2 | `/epics` L561: "zero matches → escalate per the `Repo unresolved (zero matches) — /epics` rule"; `/idea` L376 (explicit call): "`No repos derivable — /epics`" | Repo-resolution phase, and again when a scanner returns `REPO_MISSING`. |
| K stashing | `/docs-init` Phase 2.5, `/docs-brand` Phase 7, `/docs-profile` Phases 5–6, `/document` Phases 0 and 6.2, plus L's Stash choice | `/docs-init` L92: "A stash runs `workflows-core:escalation-rules` § *Stashing the user's changes*" | The branch phase, **and again at run end** (step 4: "Name it wherever the run ends"; `/docs-profile` L221 hands the record back; `/document` L196 names it in Phase 9). |
| L dirty tree | `/document` Phase 5, `/design` Phase 4, `/release-notes` Phase 5, `/create-ard` Phase 3, `/implement` Phase 1.7, `/docs-audit` (own 3-option list); `/epics` and `/specify` reproduce it inline | `/document` L558: "escalate per the `Dirty working tree` rule …, which says what each choice does" | When a scanner or summarizer returns `DIRTY_TREE`. The answer "holds for the rest of the run". |
| N refresh blocked | `/design` `/create-ard` `/docs-audit` `/release-notes` `/implement`; `/document` and `/epics`/`/specify` inline | `/design` L273 | When an agent returns `REFRESH_BLOCKED`. |
| O read-only mount | `/design` `/implement` `/document` `/epics` `/specify` `/create-ard` `/release-notes` `/idea` `/docs-audit`; `read-only-repos` §5 | `/design` L274: "Escalate per the `Read-only mount — ref stale or diverged` rule … **only** when…" | After a scan returns `prep.read_only: true`. |
| M branch prefix | Indirectly, every branch-creating command, via `branch-naming` §2.5 ("canonical wording in `escalation-rules.md` → "Branch prefix undetected""): `/implement` `/document` (keyed) `/docs-profile` `/docs-init` `/docs-brand` `/upgrade` `/vuln`. The rule omits `/promote-decisions`, which `branch-naming` §2's table lists. | — | Branch creation, and only when the identity ladder yields nothing. |
| P version line | `/design` `/implement` `/upgrade` `/vuln` `/document` `/epics` `/specify` `/create-ard` `/create-prd` `/update-prd` `/prd-proposal` `/brd-proposal` | `/create-prd` L772: "per the `A recorded verdict names the version it was taken against` rule in `Skill(…)`" | **Review gate**, then again at **handoff** (`body_facts`, e.g. `/create-prd` L809) and at the **final report**. |
| Q offer to apply | the seven inline fixers (`/create-prd` `/update-prd` `/create-ard` `/specify` `/design` `/prd-proposal` `/brd-proposal`), plus `/implement` (through `review-fixer`) and `finding-triage` (two places) | `/create-ard` L704: "offer to apply them before going on, per the `Findings a review leaves open — the offer to apply them` rule" | After each review that is not BLOCK. |
| R unspent re-review | the seven inline fixers, plus `/implement` `/document` `/epics` | `/specify` L993: "per the `Edits after a verdict that is not BLOCK — the unspent re-review` rule" | Before the handoff (`/implement`: before step 7.5). |
| S overlap read | the seven inline fixers; `grilling-technique` | `/create-prd` L766: "read the fix against what it overlaps per the `An inline fix is read against what it overlaps` rule" | At each inline fix, before the step that follows. |
| T open question recorded | `/create-prd` `/update-prd` `/create-ard` `/specify` `/epics`. **Also read at run start** by `/create-ard` Phase 2 (L397), `/specify` Step B (L622) and the `epic-writer` agent (L158): a `[NEEDS CLARIFICATION]` marker is "a decision `/epics` left open" | `/epics` L813 | After the last review, immediately before the handoff. Plus the **start-of-run** read above. |
| U1 | the seven inline fixers | `/specify` L975: "escalate per the `Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline` rule" | After a re-review that stays BLOCK. |
| U2 / U3 | `/document` Phase 7 / `/epics` Phase 7 | `/document` L1085 | After a fixer `NEEDS HUMAN`, or after a review that stayed blocked. |
| whole list | `feedback-emission` L286 lists the escalation cases only to exclude them from `emit-block` | "(repo-missing, dirty-tree, …, and the other `escalation-rules.md` cases)" | Needs no rule text, only the names. |

**Where the 48 explicit calls sit:**

| Count | Need | Calls |
|---|---|---|
| 8 | §0 only | Phase 1 of `/design` `/implement` `/epics` `/create-ard` `/specify` `/docs-profile`; `/scan` ×2 |
| 6 | key dir not found | Phase 0 of `/conformance` `/design` `/ready` `/document` `/release-notes` `/update-prd` |
| 6 | D's *no option safe* | `/create-prd` P0, `/brd-intake` P0 and P8, `/brd-interview` P11, `/brd-package` P5, `/brd-reconcile` P10 |
| 2 | repo-resolution group | `/idea`, `/prd-ground` |
| 26 | review cluster P–U | at the review gate |

### 1.3 Candidate parts and their dependencies

**ER-core = H + A + B + D + E (7,251).**

- Depends on `next-phase-offer`'s overflow rule (external, 1,277) when an offer exceeds four options. A's consequence 2 points there.
- Pointer defect today: A L25 says "must handle the answer instead — see the next section". The next section is B (verbatim); the intended target is C (closed vocabulary). The pointer is already stale, and a split would hide it further.
- E says "governed by the two rules above". Those are B and D, both in the part.
- **Verdict: SAFE-WITH-RESTRUCTURE.**
  - Point L25 at *Closed-vocabulary pickers* by name.
  - Make ER-core a mandatory co-load of every other part. Every other part's arrays use A's "(you'll be prompted)" convention, are presented under B, and carry D markers. L, N, O and U say so explicitly: L "per the "Choice lists are presented verbatim" convention above", O "well-formed under the rules at the top of this file".

**ER-closed = C (7,915). Depends on:**

- A ("Under §0 they cannot") — in ER-core.
- Positional references that stay internal to the part: "the first three, and the ninth", "the eighth", "the tenth keeps its Cancel", "rows 6, 7 and 11".
- External: `decision-register-format` §3 and §6, `bundle-packaging` §3 and §6.3, `proposal-format` §4 and §7, `conformance-format` §5, `interview-tagging` §2 (cited, not loaded).

**Verdict: SAFE-AS-IS** with ER-core, loaded only by the 7 owners at their picker. Each owner already names the picker in its citation, which is an observable trigger. A non-owner never presents one of these arrays.

**ER-stops = F + G (4,883). Depends on:**

- A's *A selection carries no text* — in ER-core.
- `addressing` §1, §3 (external, loaded by the caller at Phase 0 anyway).

G's REPOS_PATH half (rules on "asked only where no entry resolves" and "a citer's own way on … no option is marked") is operative for the 8 REPOS_PATH citers. **Verdict: SAFE-AS-IS** with ER-core. F and G could also load separately.

**ER-repos = H1 + H2 + H3 + I + J (3,974). Internal dependencies:**

- The paragraph that tells every variant and J what *Specify a different absolute path* does sits at L266–269, inside H2.
- H3 says "Same options, same order as the `/epics` variant above".
- I's `/prd-ground` form says "for the reason the `— /prd-ground` heading above gives" (H3).

**Verdict:** SAFE-AS-IS as one group. UNSAFE split per variant: `/document` or `/prd-ground` loading only its own heading, or a caller loading J alone, loses the H2 paragraph. Make it SAFE-WITH-RESTRUCTURE by moving L266–269 into a lead-in shared by H1–J.

**ER-tree = K + L (5,327). Dependencies:**

- L depends on K (its Stash choice) and on B.
- K step 1 refers back to L ("Where the choice was § *Dirty working tree*'s, present that choice again").

**Verdicts:**

- K alone for `/docs-init`, `/docs-brand`, `/docs-profile` and `/document` 6.2: **SAFE-AS-IS** (2,976). The back-reference is conditional on a choice those callers never present. K step 4 must also be in context at **run end**, so the part is needed twice.
- L alone: **UNSAFE** without K.

**ER-refresh = N + O (1,736).** Depends on B (N), on D's reason annotation and on A's free text (O), plus `read-only-repos` §5. **Verdict: SAFE-AS-IS** with ER-core. Practically, load it with ER-repos and K + L as one "scan escalations" part (11,037) for the 9 scanning commands.

**ER-branch = M (1,742).** Depends on A and on `branch-naming` §2 (external), which already carries the same two arrays and the identity prompt. **Verdict: SAFE-AS-IS** with ER-core.

**ER-review = P + Q + R + S + T + U1–U3 (21,005).** Densely cross-referenced, by position and in both directions:

- P → Q ("whom the next section asks") and R ("the section after the next").
- Q → P (version line), S (*below*), T (by name), R ("next section"), and `finding-triage` (unverified never applied).
- R → P ("the no-fixed-point argument above"), Q ("the offer above counts such a verdict" — R's trigger definition), U1 (*below*), T, and `finding-triage` § On re-review.
- S → Q.
- T → Q, R, P (by name), `specification-format` and `epic-writer`.
- U1 → R (*above*), S, `finding-triage` § On re-review, `pre-lint`. U3 → T.

**Verdict:** SAFE-AS-IS as one 21k part, loaded at the review gate by the 12 review-gated commands. **UNSAFE** sub-split by caller without restructure: for example `/document` needs P + R + U2, but R's trigger is defined through Q. Possible SAFE-WITH-RESTRUCTURE sub-parts:

- P alone (3,021) for `/vuln` and `/upgrade`. R itself says their re-review is spent in the fix pass, so "the offer never arises". Edit: replace P's two forward pointers with a sentence naming which callers make the Q and R offers.
- Every other sub-split needs R's trigger restated without "the offer above", and U1's "(above)" made explicit.

**Typical per-run cost after a split.** `/specify` needs core 7.3k at Phase 1, stops 4.9k at Phase 0, scan escalations 11.0k at Phases 3–4 and review 21.0k at Phase 6: 44.2k in total if each loads once, against 4 × 53.8k loaded today. `/brd-intake` needs core plus stops, about 12.1k.

### 1.4 Parts that must always come along

ER-core (7,251): H, A, B, D, E. B, D and E each state "This rule binds every command in the family … not only the ones documented below". H's precedence sentence decides between a command-body list and the list here. A defines the "(you'll be prompted)" convention every later array uses.

### 1.5 Rationale, history and worked examples (classification only)

| Passage | Lines | Chars | Needed to apply the rules? |
|---|---|---|---|
| A: the replaced "Other…" rule and its 136 duplicates | 15–19 | ~400 | No: history |
| B: the `/document` Phase 6.5 anecdote | 48–50 | ~300 | No |
| C: why the eighth row is listed; "outliving its own run" falsified by seven rows | 84–104 | 1,961 | No for applying the normalisation; it is guidance for whoever edits the table |
| C: D14, why the customer-authority pickers matter | 109–117 | 864 | **Edge cases, yes**: explains why a free-text answer on rows 1–3 and 9 must never be frozen as the customer's |
| C: "No operator is trapped" | 119–124 | 619 | **Contains a rule** (state an abort's consequence in the walk's prose) |
| G: citer list with phase numbers; "State the set by its property…" | 215–226, 238–243 | ~1,800 | Finding aid / maintainer. The REPOS_PATH rules interleaved there (~1,300) are operative. |
| F: "(The folder read is an inline step … no longer exists.)" | 199–201 | ~200 | No |
| I: "the `— /epics` suffix … is historical" | 287–291 | ~300 | **Yes**: it is what licenses `/idea` and `/specify` to use the rule |
| O: "scanning an unmerged tree is what caused this feature's original defect" | 406 | ~200 | Low |
| P: three live runs; phrase-grep derivation; why a reporting rule | 412–420, 429–445 | ~1,970 | Mostly no. L441–444 carry rules ("Where no edit followed the verdict, say that too"; "not BLOCK has not spent the cap"). |
| Q: the `/design` namespace-restart run | 446–456 | ~800 | Low (worked example) |
| R: the `/create-prd` run | 486–496 | ~950 | **First sentence is the rule** ("A verdict that is not `BLOCK` spends neither half of the cap"), not history |
| S: the `/specify` and `/create-ard` runs; "costs one read" | 533–542, 563–565 | ~980 | Worked example; useful for spotting overlaps in edge cases |
| T: the `/specify` four gaps | 570–581 | ~890 | Frames the rule's reason (the next phase reads the artifact); moderately useful |

About 12.5k (~23%) is history or rationale, and several passages hold the rule in their first or last sentence.

---

## 2. next-phase-offer.md (41,835 chars, 264 lines)

### 2.1 Structure

| # | Section / paragraph | Lines | Chars |
|---|---|---|---|
| H | Title + purpose | 1–7 | 360 |
| R | The offer contract — rules 1–7 | 8–43 | 4,162 (r1 793, r2 255, r3 145, r4 236, r5 1,254, r6 613, r7 833) |
| M1 | "A next-step offer that names a downstream command must also name the merge" | 45 | 404 |
| M2 | "…never unconditional"; `<merge-clause>` placeholder; multi-handoff rule | 47 | 1,131 |
| M3 | Resolution table (§4.1 outcome → clause) | 49–59 | 904 |
| M4 | Table commentary (appends, eight rows, *three rows name a branch*) | 61 | 1,246 |
| M5 | Where the placeholder sits in the text | 63 | 1,468 |
| M6 | Scope / adopter history (incl. the **attach condition**) | 65 | 5,246 |
| M7 | What `check-docs.sh` check 11 enforces and does not | 67–73 | 3,343 |
| M8 | Family-scope measurement (why check 11 is not widened) | 75 | 2,916 |
| M9 | Resolving the placeholder is not a rewording | 77 | 458 |
| S | Surface: universal minimum (362) + overflow rule (1,277) | 79–104 | 1,641 |
| G | Routing graph: PM ideation 1,586 · BRD route 7,048 · proposals 1,909 · PA 587 · PE 1,773 · Dev 3,680 | 105–248 | 16,588 |
| N | Not pipeline nodes | 249–258 | 1,575 |
| C | Session hygiene co-fires here | 259–265 | 384 |

### 2.2 Who relies on what, and when

The file has 87 mentions in 30 files: 20 explicit calls, all at the end of the run, plus citation-only callers `/brd-intake`, `/prd-proposal`, `/brd-proposal`, `/docs-audit` and `/docs-init`, and path citations from `/frames` and `/statusline`.

| Need | Callers | Citing phrase | When |
|---|---|---|---|
| R + M1–M5 + M9 + S + C (the offer contract and clause resolution) | the 20 explicit callers and every pipeline offer | `/implement` L1402: "ALWAYS end the Phase 5 report with a `### Next step` recommendation (per `Skill(… "next-phase-offer")`) — guidance only, never auto-invoked; omitted in direct mode"; `/create-prd` L845: "resolved per `Skill(…)`'s resolution table"; `/brd-split` L1506: "*A next-step offer that names a downstream command must also name the merge* rule" | **End of run** (`### Next step` / Next-steps phase) |
| M2's multi-handoff rule | `/brd-reconcile` Phases 2 and 14 | L2860: "(`workflows-core:next-phase-offer`, *where a run emitted more than one*)" | End of run. Phase 2 cites it ahead. |
| r6, r7 | `/prd-proposal`, `/brd-proposal` (Next steps); `/statusline` L22 (r6, by path) | `/brd-proposal` L788: "fully qualified (… rule 6), … exactly one positional address (rule 7)" | End of run |
| S overflow only | `/document` Phase 0 (docs-repo pick), `/brd-interview` Phase 6 (candidate picker), `/scan` Phase 5 (triage candidates), `/update-prd` Phase 6, `/brd-reconcile` Phase 14, `/prd-ground` Phase 10 | `/brd-interview` L1467: "Past three candidates, the overflow rule applies (`workflows-core:next-phase-offer`)" | **Mid-run** for the first three |
| S universal minimum + N | `/docs-serve`, `/docs-init`, `/docs-brand`, `/docs-audit` | `/docs-serve` L268: "per `Skill(…)`'s Surface section — the universal-minimum prose form"; `/docs-init` L282: "**This offer carries no `<merge-clause>`.** … the merge-clause rule applies where an offer names a downstream command whose `require-on-main`…" | End of run |
| G's PE `/epics` precondition (L214–228) | `/design` Phase 0 L106, `/implement` Phase 0 L113 (multi-component redirect); `/brd-intake` L1500 and `/brd-package` L423 cite its "an offer whose run stops the moment it starts" principle | "it becomes what `workflows-core:next-phase-offer`'s `/epics` precondition names in its place" | **Phase 0** for `/design` and `/implement` |
| G, own node | each pipeline command spells its own offer out, but cites the graph for conditions: `/prd-ground` L1979 cites the BRD-route node's reason for `/brd-reconcile`'s offer; `/prd-proposal` L724 quotes the proposals node ("the next sibling holding no current proposal"); `/brd-reconcile` and `/brd-interview` rely on the BRD-route advance/re-entry split, which "is enforced nowhere downstream — so the station that offers them must make it" | — | End of run |
| C (co-fires) and r2 role labels | read by `session-hygiene` §2 through the command's own `### Next step` output | `session-hygiene` L96: "read the role labels the command's own `next-phase-offer` output already carries" | End of run |

### 2.3 Candidate parts and their dependencies

**NPO-core = H + R + M1–M5 + M9 + S + C (12,158).**

- External: `phase-handoff` §3 and §4.1 (outcome lines, already emitted by the caller), `escalation-rules` §0 and B (overflow, verbatim), `addressing` §4.1 (r7).
- **Missing from this part as drawn: the attach condition.** "An offer that names none [no downstream gate its run feeds] does not [carry the clause]", stated "against the gate the offer names rather than against membership of the family", lives only inside M6's history paragraph. M1 alone ("names a downstream command must also name the merge") would put a false wait on `/brd-proposal`, `/scan`, `/frames` and every `/docs-*` offer.

**Verdict: SAFE-WITH-RESTRUCTURE.** Lift M6's attach-condition sentences (~500) into M1. M4's "three rows name a branch" and M7 point 1 ("picking the wrong row is a real, shipped defect … on a declined handoff") are resolution guidance: keep M4, and M7 point 1 is covered by M3 + M4.

**NPO-maint = M6 + M7 + M8 (11,505).** Adopter list, check-11 coverage and the widening measurement, for maintainers. **Verdict: UNSAFE to drop as-is** (it holds the attach condition, plus per-command facts: `/idea`'s `status: draft` → `@<path>` form, `/create-ard`'s `/harvest-decisions` clause, the one proposal option that carries the clause). It becomes **SAFE-WITH-RESTRUCTURE** once the attach condition moves into core. The per-command facts are each also written in that command's own `### Next step`: verified: `/idea` L676–704, `/prd-proposal` L748, `/create-ard` L795.

**NPO-graph = G (16,588) + N (1,575).** Split per lane: PM 1,586, BRD 7,048, proposals 1,909, PA 587, PE 1,773, Dev 3,680, not-pipeline 1,575. Cross-lane dependencies:

- The PE node's `/epics` precondition ("Every `/product-workflows:epics` option above and below…") binds every lane that offers `/epics`: PM (`/create-prd`, `/update-prd`), PA (`/create-ard`), PE (`/specify`) and Dev Phase-0 redirects.
- The BRD node's `/brd-interview` line points at "the same conditions `/brd-reconcile`'s advancing list applies".
- The proposals node is referenced from PA/PE nodes ("the command that would raise the tier").
- r5 (Epic fan-out) is needed by the per-Epic commands (`/create-ard`, `/specify`, `/design`, `/implement` at Epic scope).

**Verdict: SAFE-WITH-RESTRUCTURE.** Lift the `/epics` precondition (~1.5k) into its own part loaded by any command whose offer can name `/epics`, and each caller loads its own lane. A non-pipeline docs command needs only N + S + r1/r3/r6 (~3.5k).

**NPO-overflow = S overflow (1,277) + r3 (145).** For mid-run pickers. Depends on `escalation-rules` §0 (ER-core). Its "the array carries `Stop here` plus the three…" is offer-shaped. The mid-run callers already state their own ranking and their own `None`/`A different finding` option. **Verdict: SAFE-AS-IS** for those callers.

Per run after a split: `/implement` needs 12.2k + Dev 3.7k = 15.9k, against 41.8k. `/brd-reconcile` needs 12.2k + BRD 7.0k + PE precondition 1.5k = 20.7k.

### 2.4 Always comes along

For every pipeline offer: R, M1–M5 plus the lifted attach condition, M9, S and C (~12.7k). For non-pipeline printers: r1, r3, r6 + S + N.

### 2.5 Rationale and history

| Passage | Chars | Needed? |
|---|---|---|
| M6 adopter history | ~4,700 of 5,246 | No, except the attach condition (~500), which is needed |
| M7 check-11 coverage | 3,343 | No (maintainer); "an offer can satisfy check 11 and still be false" is a caution, not a rule |
| M8 measurement | 2,916 | No |
| M4 "It stood at six for a release…" | ~500 | No; the rest of M4 is resolution guidance |
| M5 "Re-derive it rather than trusting this paragraph — grep…" | ~500 | No; the placement rule (~900) is needed |
| r1 why the exception exists | ~200 | Low |
| BRD node explanations ("The set is what the run did…", "That difference is where the conditions come from") | ~2,000 | **Edge cases, yes**, for `/brd-split`, `/brd-reconcile` and `/brd-interview`, whose offer sets they define |

About 13.5k (~32%) is maintainer material or history.

---

## 3. session-hygiene.md (11,808 chars, 175 lines)

### 3.1 Structure

| # | Section | Lines | Chars |
|---|---|---|---|
| H | Title, purpose, guidance-only | 1–13 | 748 |
| §1 | Prepare-checkpoint (resume pointer). Sub-paragraphs: timing/discrete step 1,209 · why not bound to the block 447 · misrooted 205 · skipped list 301 · "three reasons" 757 · location 426 · template 915 · redact 234 | 14–78 | 4,502 |
| §2 | The suggestion — role-aware | 79–98 | 1,173 |
| §3 | Mid-run suggestions; `/vuln`, `/upgrade` | 99–107 | 565 |
| §4 | Session-name aid (rule 818; three "do not / excluded" paragraphs ~1,630) | 108–140 | 2,451 |
| §5 | Contract, 5 rules (r2 terminal order 725; r4 mode-aware 662) | 141–169 | 2,037 |
| Surf | Surface | 170–176 | 333 |

### 3.2 Who relies on what, and when

The file has 102 mentions. **All 23 explicit calls sit at the terminal resume-pointer step and cite §1.**

| Need | Callers | Citing phrase | When |
|---|---|---|---|
| §1 (write the pointer) | `/conformance` `/design` `/implement` `/ready` `/document` `/release-notes` `/brd-*` (6) `/create-ard` `/create-prd` `/update-prd` `/specify` `/epics` `/prd-proposal` `/brd-proposal` `/scan` | `/design` L506: "**Write the resume pointer.** Invoke `Skill(… "session-hygiene")` and, per its §1, write/overwrite `<PRD-dir>/dev-workflows/resume.md` now — after the cost entry above…" | **Terminal cost phase**, between `emit-cost` and `commit-artifacts` |
| §1 location rung 2 only | `/docs-audit` L391, `/docs-brand` L364, `/docs-init` L330 | "With no PRD dir, entry 2 of its **Location** ladder applies: skip the file" | Terminal. They load 11.8k to learn they skip. |
| §1 skip list | `/vuln` L341, `/upgrade` L241, `/document` Mode B L1923, `/frames` L376, `/idea` L732 | "No `resume.md` is written for `/vuln` (`workflows-core:session-hygiene` §1 skip list…)" | Terminal (citation only) |
| §2, §4, §5 r4 (the guidance block) | every pipeline command's `### Context hygiene`: `/create-prd` L852 ("outside that reference's §4 rename-aid set, so it **omits the session-name line**"), `/brd-reconcile` L2916 ("§2's *Next options span both* bullet"), `/brd-interview` L2327 ("§2's *Same role* bullet") | — | **Final report.** Cited, not loaded, at that point; most commands' blocks are pre-written. |
| §3 | `/implement` Phase 3B L918 (no mid-run `/compact`), `/vuln` L337 / `/upgrade` L237 (compact only), `context-management` | "(`workflows-core:session-hygiene` §3)" | Mid-run (`/implement`), end (`/vuln`, `/upgrade`) |
| §5 r2 terminal order | `/prd-proposal` L775, `/brd-proposal` L830, `/feedback` L92, `/prompt` L85 | "The order below is the canonical emitter tail (`workflows-core:session-hygiene` §5 rule 2)" | Terminal phase heading |
| §1 as authority | `specs-repo-git` §2.1, §3.1, §4; `addressing` `specs-root-check` | resume tier 1; misrooted skip; "`resume.md` is NOT written" on a Phase-0 refusal | — |

### 3.3 Candidate parts

**SH-write = H + §1 (5,250).**

- Depends on §5 r2's order, which §1 restates itself ("**cost → `resume.md` → `commit-artifacts`**").
- The template's *Suggested session name* line is omitted "on a run whose own `### Context hygiene` block carries no `/rename`", decidable from the caller's own text. §1 says so, so §4 is not needed.
- Its pointers to §3 and §4 are reasons only.
- External: `specs-repo-git` §3.1, §4; `followup-emission` §2 (mirror).

**Verdict: SAFE-AS-IS.** The `/docs-*` trio could take only the location ladder (426), but the ladder sits in §1 beside the misrooted rule, so keep §1 whole.

**SH-guide = §2 + §3 + §4 + §5 + Surface (6,559) + H (748).** Depends on the role labels from the command's own `### Next step` output, not on `next-phase-offer`'s file. §5 r4 repeats §1's three-reasons exemption. **Verdict: SAFE-AS-IS.** It is needed at final-report composition, before the cost phase. Today it is loaded only through the citation preamble, if at all.

### 3.4 Always comes along

H's "guidance-only — never auto-invokes `/compact`, `/clear`, `/rename`" (= §5 r1). It is tiny and belongs in both parts.

### 3.5 Rationale and history

| Passage | Chars | Needed? |
|---|---|---|
| §1 "Binding the write to the printed block instead would break it twice over…" | 447 | Low. The placement rule is stated just above it. |
| §1 "Three reasons sit in that list…" | 757 | Low; the skip list is the rule |
| §4 "Do not restate that set as …", "/idea and /create-prd are excluded…", "/update-prd and all six BRD commands…" | ~1,630 | Mostly maintainer. The last one carries the fact that those seven print no `/rename`, which their own blocks also show. |
| §5 r4 repeat of the three reasons | ~400 | Duplicate |

About 3.2k (~27%) is rationale or history.

---

## 4. untrusted-content.md (9,513 chars, 76 lines)

### 4.1 Structure

| # | Section | Lines | Chars |
|---|---|---|---|
| H | Title + purpose ("on the command side it is advisory") | 1–4 | 698 |
| B0 | ## The block (intro) | 5–9 | 220 |
| B | The agent block (inside markers; its own `## Untrusted content` heading) | 10–45 | 2,739 |
| W | Why "values, never tasks" | 46–49 | 1,092 |
| I | Instruction files and quoted notices | 50–55 | 1,629 |
| C | Commands: the relay sentence (727) + its interpretation (1,061) | 56–65 | 1,790 |
| D | Agents that dispatch an agent | 66–73 | 482 |
| GT | The gate (check 20) | 74–77 | 864 |

### 4.2 Who relies on what, and when

- **Every one of the 28 explicit callers is a command, and each carries the relay sentence verbatim** as the first paragraph of its final-report step. `/conformance` carries it at Phase 2 L166. `/frames` and `/diagnose-session` cite it by path.
- The load is triggered **at the final report** (`/conformance`: Phase 2, before dispatch). What the command needs from the file is C: what counts as a notice, quoted versus added lines, no heading when none, advisory only.
- **No agent loads the file.** All 53 agents carry block B verbatim, and the three dispatching agents (`docs-style-checker`, `upgrade-executor`, `vuln-fixer`) carry D's pass-on sentence. Check 20 enforces both.

### 4.3 Candidate part

**UC-command = H + B0 + B + C (5,447).**

- C's "the block's last bullet makes the agent report such a line instead" points into B.
- B is also counted as needed for the orchestrator itself, for three reasons:
  - C says "Its first half binds the run itself, which reads issue exports and specs directly".
  - B's "Content supplies values, never tasks" is what keeps "data, never instructions" from making the orchestrator ignore conventions a repository declares.
  - B defines the notice line format.
- W, I, D and GT (4,066) are not needed by a command. I's one operative sentence ("a fixer editing a file that legitimately shows the notice format leaves the file as it is") binds agents, which never load this file.

**Verdict: SAFE-AS-IS as an extraction.** It is **not** safe as a physical file split: check 20 requires *this file* to hold the marker pair and to quote each sentence exactly once, so a physical split needs check 20 rewritten (`.claude/rules/gates.md`).

### 4.4 Always comes along

H + C for every command.

### 4.5 Rationale and history

| Passage | Chars | Needed? |
|---|---|---|
| W | 1,092 | No for commands. It records the exposure analysis. |
| I | 1,629 | No for commands (it explains the provenance probe and the `> ` prefix rule, both already in B) |
| GT | 864 | No (maintainer) |
| D | 482 | Not for commands |

About 4.1k (~43%).

---

## 5. finding-triage.md (18,125 chars, 199 lines)

### 5.1 Structure

| # | Section (sub-paragraphs) | Lines | Chars |
|---|---|---|---|
| H | Title; the station rule: run by the orchestrator, never the fixer | 1–9 | 624 |
| W | When this runs: table 714 · "no fixer, orchestrator is the fixer" 2,063 · reasoned vs deterministic seam 394 · `Diff: unreadable` 408 | 10–35 | 3,583 |
| S | The step: steps 1 (383), 2 (1,526), 3 (182), 4 (539), 5 (389); two-grade reviewers (268); only survivors (93) | 36–77 | 3,383 |
| E | When triage empties the survivor set: intro 482 · steps 1–2 560 · step 3 + both settle prompts + Keep/Proceed/Cancel 1,745 · **"A `BLOCK` whose survivors hold no `BLOCKER` and none the caller's fixer takes is this case"** 917 · "governs the first review" 352 | 78–120 | 4,059 |
| P | The patch gate: rule 708 · why 862 | 121–142 | 1,572 |
| R | On re-review: definition 730 · carry 906 · rule 1 610 · **rule 2, "stayed blocked"** 859 · rule 3 + prompt 828 | 143–185 | 3,936 |
| Rep | Reporting | 186–200 | 969 |

### 5.2 Who relies on what, and when

The file has 60 mentions in 18 files.

**Orchestrators with a fixer agent.** `/implement` (Phase 3B step 7, step 8), `/vuln`, `/upgrade`, `/document` keyed (Phase 7), `/epics` (Phase 7).

- Citing phrase: "**Triage sub-step** (before any fixer dispatch, and on every re-review): invoke `Skill(… "finding-triage")` and follow it".
- They need H, W (attachment; `/document` and `/epics` attach to the reviewer-fed dispatch only), S, E, R and Rep.
- Timing: at the **review gate** (S, E), at the **re-review** (R: "Triage the re-review under `workflows-core:finding-triage` § On re-review"), at the **final report** (Rep: "`### Review triage` … per `workflows-core:finding-triage` § Reporting"), and in Invariants ("or a `workflows-core:finding-triage` settle prompt's **Proceed** settles it as one").
- `/implement` also writes Rep's terms into its run-state `triage` record (L320, defined at Phase 1.4).
- `/epics` cites R at **Phase 6.2**, before its review (L744).

**Orchestrator as the fixer, no re-review.** `/docs-init` Phase 7.5, `/docs-brand` Phase 9, `/docs-audit` Phase 5.5.

- Citing phrase: "**Triage before applying anything.** Invoke … and follow it"; "bound by `finding-triage.md`'s patch gate".
- They need H, W's orchestrator-as-fixer paragraph, S, E (the three-option form), P and Rep. They do **not** need R.

**Orchestrator as the fixer, with re-review.** `/prd-proposal` Phase 9, `/brd-proposal` Phase 10.

- Citing phrase: "3. **Triage before anything is edited.** … — the orchestrator runs the triage, never a fixer".
- They need everything, including P, R and S's two-grade paragraph (`proposal-reviewer` files `BLOCKER`/`RECOMMENDATION`).

**Fixer agents.**

- `review-fixer` (explicit call, L81: "Apply the **patch gate** (`Skill(…)`)"), at its fix method, on every dispatch. It needs **P only**, plus "every finding you receive is a survivor … do not re-triage", which its own L36 states.
- `doc-fixer` reads the file by path (L45), for P only.

**`/conformance` Phase 3.** "Verify each … verdict at the location it cites, in the manner of `workflows-core:finding-triage`'s verification step". Citation-only, so the preamble loads the whole file. It needs S steps 1–3 (2,091) and no fixer, prompt or reporting.

**Reviewer agents.** `docs-audit-reviewer` L14, `docs-scaffold-reviewer` L12, `proposal-reviewer` L19/L298: "the caller triages … per `workflows-core:finding-triage`". The citation is **descriptive**: they need nothing. All three carry the Core-references preamble, so a literal reading loads 18k for nothing.

**Other references.** `escalation-rules` Q, R, U1–U3 point at R (stayed blocked, re-review triage). `model-routing/classification` §6 points at S's dispositions.

### 5.3 Candidate parts and their dependencies

- **FT-gate = P (1,572).** "Survivor" is defined in S, but each fixer's own text already says every finding it receives is a survivor. P's "A fixer agent is not handed the diff, so it applies the clause by the finding's location" is self-contained. **Verdict: SAFE-AS-IS** for `review-fixer` and `doc-fixer`. This saves ~16.5k per `review-fixer` dispatch.
- **FT-verify = S steps 1–3 (2,091).** Step 2's unverified branch cites "raised by effect as step 4 says" and grades that `/conformance` does not use. **Verdict: SAFE-WITH-RESTRUCTURE.** Give it an entry point that maps keep, unverified and dismiss to `/conformance`'s own confirmed/dropped outcomes. Otherwise the part carries step 4 (539) too.
- **FT-first-review, no re-review = H + W + S + E + P + Rep (14,190).** E refers twice into R:
  - L91: "a user who keeps the verdict says the review stayed blocked (§ On re-review)".
  - L114: "as § On re-review rule 2 names that stop".

  For `/docs-init`, `/docs-brand` and `/docs-audit`, E's own L103–106 defines Keep the verdict locally. **Verdict: SAFE-WITH-RESTRUCTURE** (make those two pointers self-sufficient), saving 3.9k.
- **FT-first-review for `/implement`: UNSAFE without R.** R rule 2's "a caller whose own rule keeps a first review's `BLOCKER` from the fixer, because its fix lies in another code repository, counts that `BLOCKER` as one" is a **first-review** rule, which `/implement` L973 applies ("the review stayed blocked"). Splitting along first-review and re-review lines drops it.
- **FT-re-review = R (3,936).** It depends on S (the re-review's findings are "triaged by § The step"), E (the user's re-review choice is the carry exception; "first settle prompt" naming) and `escalation-rules` Q. **Verdict:** only useful **added to** the first-review part, never alone.

Net: for triaging orchestrators the useful cuts are R for the three no-re-review commands, the rationale paragraphs, and the zero-findings fast path (§6 below). The big safe wins are the fixer agents (FT-gate), `/conformance` (FT-verify) and the three reviewer agents (nothing).

### 5.4 Always comes along

- For every triaging orchestrator: H (station rule), S and Rep (5,000).
- For the orchestrator-as-fixer callers: W's sentence "Everything below applies unchanged with "the fixer" read as "the orchestrator's own edit": survivors only, the patch gate binds that edit, and an emptied survivor set is settled by the user".

### 5.5 Rationale and history

| Passage | Chars | Needed? |
|---|---|---|
| H: why (Sonnet fixer vs Opus reviewer) | ~400 | Low; the rule is the first sentence |
| W "no fixer" paragraph: D25 reasons; "stronger, not moot" | ~1,200 of 2,063 | Low. The grouping sentence ("a new caller states which group it follows") is for maintainers. The reading rule (~400) and the per-caller group facts are needed. |
| W seam paragraph | 394 | Half rule ("attaches to the reviewer-fed dispatch only"), half rationale |
| E intro "Triage disposes of findings; it does not restate the verdict…" | 482 | **Edge cases, yes**: explains why a non-PASS verdict with nothing behind it is the user's to settle |
| P "why": guard clause; instruction-file clause | 862 | The guard-clause paragraph explains the commonest false fix: useful. The instruction-file paragraph holds the rule "applies the clause by the finding's location". |

About 3k (~17%). This is the least rationale-heavy of the five.

---

## 6. finding-triage after a review that returned zero findings

A zero-finding review still triggers the triage sub-step. In the route-3 `/implement` run the whole 18.1k was read (`r3m-reads.txt`, 06:06:10). What such a run still needs, by case:

1. **Always (~2.7k).**
   - S step 5 (389): rule on each `### Declined to judge` line. `code-review` returns that list on every review, "none — nothing set aside" or lines, and it can carry lines when the findings list is empty. A line ruled a defect is "recorded with its grade by effect", so step 4 (539) comes too.
   - S step 3 (182): never drop silently.
   - Rep (969): the one triage line per pass (`0 reviewed: 0 survived, 0 unverified, 0 dismissed`), each `### Declined to judge` ruling, any settle prompt's answer. `/implement` also writes this into run-state `triage`.
   - H (624): the orchestrator runs it.
2. **Verdict is not PASS on a first review (+4,059, E).** E fires on "no finding behind a non-`PASS` verdict survives". With zero findings that holds vacuously: a `PASS WITH RECOMMENDATIONS` or `BLOCK` with an empty findings list must reach the first settle prompt, not a fixer dispatch with nothing to apply and not the unresolved-BLOCKER escalation. A fast path that skipped E would let such a verdict through silently. That is the "Never promote a non-`PASS` verdict to `PASS` silently" rule.
3. **On a re-review with verdict BLOCK (+~2.4k).** R's definition (730), rule 2 (859) and rule 3 with its prompt (828): "Where the second verdict is `BLOCK` and no `BLOCKER` survives" holds with zero findings. The carry step has nothing to carry, and the count `C carried` is 0.
4. **Not needed at all:** W (attachment is decided by the caller invoking the step; the `Diff: unreadable` case carries a BLOCKER, so it is never zero-finding), S steps 1–2 (nothing to verify), P (no fixer), and R's carry and rule 1.

**Verdict: SAFE-WITH-RESTRUCTURE** as a named entry point ("no findings"). It must state the three cases above in its first lines and send case 2 to E and case 3 to R rules 2–3. That is ~2.7k for the common PASS case, against 18.1k.

---

## 7. Risks that cut across all five

1. **Operative rules sit inside paragraphs that read as history or maintainer notes.** Examples:
   - `next-phase-offer` M6 holds the only statement of when `<merge-clause>` is **not** attached.
   - `escalation-rules` R's history paragraph opens with the rule "A verdict that is not `BLOCK` spends neither half of the cap".
   - `finding-triage` R rule 2 holds a first-review rule for `/implement`.
   - `escalation-rules` I's "historical suffix" sentence is what licenses other commands to use the rule.

   A split by heading, or a pass that strips rationale, would drop these without any gate noticing.
2. **Positional cross-references.** These include "above", "below", "next section", "the offer above counts such a verdict", "rows 6, 7 and 11", and the shared paragraph inside the `/epics` variant. One is already stale (`escalation-rules` L25 "see the next section"). Each candidate part above lists its targets.
3. **Mutual cross-file dependencies.** escalation-rules Q, R and U point to finding-triage R; finding-triage E and R point to escalation-rules Q. Further pairs: escalation-rules §0 ↔ next-phase-offer's overflow, next-phase-offer C ↔ session-hygiene §2, and escalation-rules O ↔ read-only-repos §5. A review-gate load needs the matching part of each file, not one file's part.
4. **The universal core is cited early but binds late.** escalation-rules' core (§0, verbatim, marker, fires) is loaded explicitly at Phase 0/1. It binds every later prompt, including the next-step arrays and the review-gate escalations. Any late-step part must co-load it.
5. **The citation-only path cannot express a part.** About half the citers, and every agent preamble, load through "`workflows-core:<name>` → `Skill(… args: "<name>")`". A split needs either a rule-name → part mapping in the loader, or a part token on every citation. Otherwise those callers keep loading whole, or, if the default part becomes the core, silently lose the rule they cited.
6. **Gate constraints on physical splits.**
   - Check 20 pins `untrusted-content.md` as one file.
   - Check 16 pins the citation/preamble contract.
   - Check 11 reads `next-phase-offer`'s families and `phase-handoff` §3.4.

   An extraction loader avoids these; a file split does not.

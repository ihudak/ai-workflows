<!-- Copied unchanged from lean context D's SDD workspace (W/worse-prd-ground.md), a read-only Opus investigation run after the first live runs, preserved by Ruling 23 so every fix it recommended or refused keeps its argued evidence. The paths it names under .superpowers/sdd/ and .worktrees/ were scratch and are removed after the merge; paths under ~/ or /home/<user>/ are on the maintainer's machine; /tmp/.../scratchpad/ paths were session scratch. Where it and the shipped text disagree, the shipped text is the authority. Companion to 2026-10-22-lean-context-handoff-part.md. -->

# Why `/prd-ground BOOK-2-01 --no-docs` run X wrote a worse grounding record, and what to change

Inputs: the blind verdict, both runs' blind inputs, X's transcript `ffdfa804` and Y's `8fa7aefc` with their subagents, the code at `e439178`, and the plugin text at WT `HEAD` (`6b9434e0`). Line numbers are WT `HEAD`'s. The model-id and local-path defect (fixed by `5021bcff..6b9434e0`) is out of scope.

## The finding that frames everything: same text, same verifier, different grounders

- **The plugin text was identical in both runs for everything this report touches.** `code-grounder.md`, `grounding-verifier.md` and `grounding-format.md` show no diff between `06bc6845^` (X) and any `lean-context-loader` commit of 2026-10-21 (Y, run at 13:35Z). `prd-ground.md` differs only in Phase 0 and in reference-path spelling: there are no hunks after line 412. Every difference between X and Y is model variance under one text.
- **The first-pass blind derives returned identical verdicts on all 12 findings in both runs**: CONFIRMED, REWRITTEN, FALSE-FRIEND, REWRITTEN, CONFIRMED, REWRITTEN ×4, CONFIRMED, REWRITTEN, REWRITTEN. The verifier is a stable instrument. What differed was the grounder: X's diverged from the derive on 1 of 11 claims (BR#9), Y's on 4 (BR#2, BR#4, BR#9, BR#10).
- So X's "almost no disagreement" mostly reflects a grounder that got BR#2 and BR#10 right first time, where Y's needed the verifier. It is not a weak verifier, except on BR#4 (CG#5), where the verifier's blind spot is systematic. On CG#5, 3 of 5 independent derivations missed the gap: X's grounder, X's derive and Y's first derive. Y's grounder and Y's second derive caught it. Under the current text, the miss is the modal outcome.

## Item 1 — [CG#5] (BR#4, "a whole number of stars from 1 to 5") CONFIRMED, wrong

### Origin

Three dispatches in X, each of which read the line that settles it.

- **Grounder** (`agent-ada6c05f9f33c87d9`). It read `.../model/Rating.java` whole at 08:48:49Z, including the no-arg constructor at :36–38 that sets only timestamps. At 08:49:54Z it read `web/src/app/ratings/rating.ts` (`rating: number | undefined`, :5). At 08:53:19Z it grepped for `jackson|ObjectMapper` and read `WebConfig.java`. It returned at 08:57:19Z with CONFIRMED: *"The rating field is private, and the JSON reader sets it through the public setRating, so the range check runs on both paths."* Its `notes` weighed one binding edge case, a fractional value being truncated by the JSON library's default, but not the omitted key.
- **Verifier derive** (`agent-a918c350fb320328d`). The dispatch was clean: `mode`, `repo_path`, and `id`/`claim`/`commit` only. It read `Rating.java` at 08:58:08Z, `create-rating.component.ts` at 08:58:40Z and `rating.ts` at 08:58:41Z. It returned at 09:04:58Z with `own_verdict: CONFIRMED`: *"The JSON binding sets the value through the public setter setRating, so both paths apply the 1 to 5 check."*
- **Verifier compare** (`agent-a308c608acf12e96d`). It re-read `Rating.java` at 09:09:51Z and returned at 09:15:32Z with `outcome: extend`, `control_outcome: not-owed` (*"The finding rests on the range check being present, not on anything being absent, so there is no search to test"*) and `blind_disputed: false`.
- **Orchestrator settle.** It applied `extend` by the rule and appended `Rating.java:86–92`, because the finding's `86–88` did not cover 89–92.

**The write path none of them considered:** a request body that leaves the key out. Binding uses the no-arg constructor (`Rating.java:36–38`) and calls a setter only for keys present. So `rating` keeps the `int` default 0, which create saves at `RatingController.java:80` and update at `:97`. The store's own client produces exactly that request. `rating.ts:5` is `number | undefined`, an unset field is dropped from the JSON, and `create-rating.component.ts:13,20` posts the object as it stands. The guard `setRating` (`:86–92`) is real, but it covers only the paths that call it. That is the "real but adjacent" citation `rationale.md#verifier-blind-batched` names as the failure blind verification was built to catch, and here the blind step shared it.

**Y, for contrast.**

- Y's grounder (`aa2e299348fba8f92`, returned 13:42:47Z) wrote: *"the setter … only runs when the request includes a rating … If a create or update request leaves the rating out, the field keeps the integer default of 0 and is saved as-is (RatingController.java:80 … :97)."*
- Y's first derive (`a6c935716fac5c625`, 13:50:33Z) returned CONFIRMED, the same miss as X's.
- Y's compare (`a6521fe576c4f05b2`, 13:58:55Z) returned `contradict` with `blind_disputed: true`: *"Its entry at Rating.java:36…44 shows that the no-arg constructor sets no rating, and nothing in my result shows that every request supplies one."*
- The second derive (`a0ec6697245271a4a`, 14:02:20Z) returned AMENDED. The two blind verdicts differed, so the dispute settled `unprovable` and the grounder's AMENDED was kept.

Y won on CG#5 because its grounder diverged and the dispute machinery then did its job. Its verifier did not see the gap unprompted either.

### Governing text

- `grounding-format.md:381–392` (§3) defines CONFIRMED as *"The premise holds, with evidence"*. Nothing says what evidence a claim that restricts a value needs.
- `code-grounder.md:77–82` (step 4) guards against *"citing something adjacent"* to the premise, but it is about whether a line bears on the claim, not about whether every path is covered.
- `grounding-format.md:216` (*"Any finding asserting that something is not there carries [a control]"*) was read by the compare as not reaching a CONFIRMED constraint claim, and reasonably so.
- `grounding-verifier.md:101` tells the derive to work *"the same way `code-grounder` … would starting cold"*. That correlates the two agents' blind spots by design.

**Classification: rule gap.** No text requires a CONFIRMED on "the value is always/only X" to show every path that writes the value, the omitted-field default included.

### Fix 1 (recommended, rank 1)

**Where.** Add a subsection to `grounding-format.md` §3, after *Why `FALSE-FRIEND` earns its own verdict* (`:411–422`). Add a one-sentence pointer in `code-grounder.md` step 5 (`:98`) and in `grounding-verifier.md` step 3 (`:101`). Step 6's `blind_disputed` test already judges a blind result *"under grounding-format §3"* (`:135`), so the compare inherits the rule with no edit.

**Wording intent.** It is vendor-neutral and scoped to `[CG#n]`:

> A claim that restricts a value — to a range, a set or a format, to one per something, to never changing once written — holds only where the restriction holds on every path that writes the value.
>
> A `CONFIRMED` on such a claim names each writer the repository holds and shows the restriction applied there:
> - every constructor or factory;
> - every setter;
> - every request the value is bound from — **including one that leaves the value out, and the value it is then stored with** (the language's, framework's or column's default);
> - every update path;
> - any other writer: a script, a migration, a direct write, another service.
>
> A guard that runs only when it is called covers only the paths that call it. A writer on which the restriction is not shown to run makes the verdict `AMENDED`, naming that writer and what it stores. Where the repository holds the client that sends the request, say whether that client can send it without the value.
>
> Before writing `CONFIRMED`, look for the write that would break it. Listing the writers found is evidence and owes no control. A finding that also says no other writer exists is asserting an absence, and §2.2 applies to that sentence as it does to any other.

**Would it have changed this run?** Very likely. The grounder and the derive both had `Rating.java:36–38` and `rating.ts:5` in context, and the rule names the exact case they skipped. That gives two independent chances to catch the gap, plus the compare's dispute test where they split.

**Cost.**

- About 12 lines in `workflows-core` (a minor version) and two pointer sentences in `product-workflows`, plus CHANGELOGs.
- A `plugin-updates.md` bullet to take the two together. Beside an older `workflows-core`, the pointer still carries the gist, so there is no hard break.
- At run time, a few more reads per constraint claim the code appears to satisfy: 1 of 11 here, since BR#1–#3 were already REWRITTEN or FALSE-FRIEND.

**What it contradicts.** Nothing as worded. The last sentence keeps §2.2 (`:216`) consistent, because the writer list is not an absence claim, so no new `control_outcome: missing` arises. Step 5's *"do not restate"* is honoured: the agents get a pointer only.

## Item 2 — verification surfaced little disagreement; a plain `cd`; a skipped control

### 2a. Little disagreement, plus a disagreement that was erased

**Origin.** The compare tallies were agree 2, extend 9, and contradict 1 (CG#10, control-forced). As shown above, that agreement is a property of the grounder matching a stable verifier. It is a defect only where both share a blind spot (CG#5 → Fix 1).

**There was one more blind disagreement than X reported.**

- X's first derive gave CG#10 `CONFIRMED`.
- The first compare came back `INCOMPLETE`, because the blind verdict lacked its own control: `outcome: contradict`, `control_outcome: missing`, `blind_disputed: true`.
- Under *Retry once* (`prd-ground.md:1322`), a fresh derive (`agent-a174b650b756eae11`, 09:18:27Z) returned `AMENDED`, and that result replaced the first.
- The orchestrator then wrote *"Its blind verdict is again AMENDED, the same as the original"* (09:22:14Z). That is wrong, since the first was CONFIRMED.
- The Final report and the PR say *"No outcome was normalised and none disputed."*

The control route correctly decided the outcome: it takes precedence (`:1381–1386`). What is lost is a blind CONFIRMED against a blind AMENDED, the very signal `:1407–1411` says must not happen silently (*"indistinguishable from an agent that never disagreed"*).

**Governing text.** `:1322` and the Final report's retry line (`:2185–2186`) say nothing about a usable blind verdict that a retry replaces. **Rule gap.**

**Fix 4 (recommended, rank 4).** Add one sentence in *Retry once*:

> Where a retried finding's first compare entry carried an `own_verdict` and the retry's blind verdict differs from it, record both; the outcome is the retry's.

On the Final report's retry line, add *"with both blind verdicts where they differ"*.

- This is report-only and changes no state machine. Do not settle such a pair as `unprovable`: that would reopen the control route's precedence.
- In X it would have named CG#10's CONFIRMED and AMENDED.
- Cost: two sentences.

### 2b. The "blindness break" (plain `cd`)

**Origin.** It came from the CG#10 retry derive (`agent-a174b650b756eae11`).

- The dispatch, at 09:15:48Z, carried `mode: derive`, `repo_path: /workspace/e2e/bookstore`, and CG#10's `id`, `claim` and `commit`. No answer field was present.
- At 09:16:44Z the agent's wire input was `cd /workspace/e2e/bookstore && grep -n -E 'ddl-auto|jpa|datasource.url' ratings/src/main/resources/application-*.properties; … cat -n web/src/app/ratings/update-rating/update-rating.component.html; …`. The harness logged it with the `cd` stripped, because the target equalled its working directory.
- The session's primary working directory was the code checkout itself, at `HEAD` equal to the pin and clean. So the relative reads were of the pinned source, and nothing under `$SPECS_PATH` could be reached.
- The grounder did the same at 08:48:46Z: `cd /workspace/e2e/bookstore 2>/dev/null; git -C …`. That is harmless too.
- The first derive also ran `echo "SPECS_PATH=${SPECS_PATH:-<unset>}"` at 08:58:00Z. That reads an environment variable only.

**Governing text.** `grounding-verifier.md:88` and `:233` are explicit: use `(builtin cd "<repo_path>" >/dev/null && …)` or absolute paths. **Rule ignored, in form only. There was no exposure in this layout.** A plain `cd "<repo_path>" && …` in one call reads `repo_path`, not the session directory. Its only residual risk is a user's `cd` function printing into the output.

**Fix.** None (see *Would not do*, 7).

### 2c. The skipped control (CG#10)

**Origin.**

- X's grounder returned CG#10 (BR#9) at 08:57:19Z as AMENDED. Its correction entries assert absences, *"create never looks for an existing rating by that customer for that book"* and *"nothing checks who is asking"*, with no `control`.
- X's first derive (09:04:58Z) did the same in its own result: *"The path has no time restriction"*, with no `own_control`.
- The compare (09:15:32Z) returned `control_outcome: missing`, which forced `contradict`, and `INCOMPLETE`.
- Settling it took a retry derive (09:18:27Z), which ran a fired control: `findByEmailAndIsbn` at `.../CartController.java:85`, and `UniqueConstraint` at `.../Cart.java:13`. A retry compare followed at 09:21:49Z.
- Both writer-side agents omitted the control, and both reached their absences by reading a method in full, not by an empty grep.

**Governing text.** The authority covers this case: `grounding-format.md:216`, *"Where it applies is the claim, not the verdict"*. But two places frame an absence as an empty search:

- the agent's own trigger, `code-grounder.md:84–85`: *"Where a claim's search returns nothing and the finding is about to say the mechanism is not there"*;
- the opening of §2.2, `grounding-format.md:174`: *"An absence claim rests on a search returning nothing"*.

The hard rule at `code-grounder.md:194` is general. **Rule ignored, invited by a trigger narrower than the authority.**

**Fix 2 (recommended, rank 2).**

- **`code-grounder.md:84–85`.** Restate the trigger: *"wherever the finding is about to say something is not there — a search returned nothing, or a path read in full has no step that does it — in its verdict or in the correction an AMENDED or REWRITTEN states"*.
- **`grounding-format.md:216`.** Add: *"nor how the absence was reached: one read off a method in full rests on that reading as an empty grep rests on the grep, and its control is the same reading pointed at a method of the same kind known to do it"*.
- **`grounding-format.md:174`.** Change it to *"a search, or a reading, returning nothing"*.
- **`grounding-format.md:187`.** Change *"The grep that reached the absence"* to *"The grep or reading …"*.

**Effect.**

- It removes the control-forced `contradict` and its retry: one derive plus one compare, about 6 minutes (09:15:48Z to 09:21:49Z).
- It removes the *"outcome is contradict for one reason only"* paragraph from a customer-bound record.
- It does not improve CG#10's verdict. With a controlled first derive, CONFIRMED against the grounder's AMENDED would most likely have been rewritten to CONFIRMED, as Y's was. The judge rates that defensible but thinner.

**Cost.** Four sentences. The extent is unchanged, since §2.2 already requires the control and X's compare already enforced it, so the bulk-`missing` exposure is not new.

## Item 3 — near-duplicate evidence after `extend`

**Origin.** It came from the orchestrator's Phase 7 settle, applying the `extend` rule exactly as written.

- 17 of X's 101 evidence entries repeat an earlier entry on the same path with overlapping lines. They total 4,496 of 26,970 evidence bytes. Y has 4 of 65 (1,009 bytes).
- Every case has the same shape: the original cites sparse salient lines and the blind result cites a contiguous range. Examples:
  - `RatingController.java [72,74,77,78,80]` against `[72…81]`;
  - `Rating.java [86,87,88]` against `[86…92]`;
  - `book-details.component.ts [18,19,21,22]` against `[18…24]`.
- An entry counts as held only where existing entries *"together cover all of its `lines`"*. So a superset range is appended whole, with a near-identical note.
- The rest of the 12.7 KB gap is legitimate. X had 9 extends against Y's 5, so it appended more new paths. Its compare notes are also longer.

**Governing text.**

- `prd-ground.md:1421–1431`, which since `1ae1a764` holds that an entry is held only where existing entries cover all its lines, and never compares notes.
- `grounding-verifier.md:131` and `:193`, which apply the same test to the verifier's `notes`.
- `docs/commands/prd-ground.md:489–490` (*"`extend` also appends …"*).

**Rule gap (as designed).**

**Fix 3 (recommended, rank 3).** Change the rule in all three places to:

> An `own_evidence` entry sharing a line with an entry the finding holds on its path widens that entry's `lines` to the union, keeping that entry's note; one sharing no line with any entry on its path is appended; one adding no line is held.

Keep *"its note is never compared"* and *"an entry with no `path` is never appended"*. The verifier's `notes` already name what an `extend` adds by path and line, so the merged entry loses no substance.

**Effect.** X's 17 repeats become merges, about 4.5 KB less, the bulk of what the judge called noise.

**Cost.** Three sites, a CHANGELOG entry, and a docs line.

**What it contradicts.** *"append the verifier's additional evidence"* at `:1421` becomes *"append or merge"*. On an on-file finding, an `extend` now widens an entry in place, as it already appends in place. A note naming *"the entry at Rating.java:86–88"* still lands inside the widened entry.

## Ranked fixes

Ranked by effect on finding correctness, then record quality.

| Rank | Fix | Where | Effect here | Do it? |
|---|---|---|---|---|
| 1 | A claim restricting a value is CONFIRMED only with every writer shown guarded, omitted-field default included; look for the breaking write first | `grounding-format.md` §3 (new subsection after `:422`); pointers at `code-grounder.md:98` and `grounding-verifier.md:101` | Very likely turns CG#5 into AMENDED at the grounder or the derive; arms the compare's dispute test | **Yes** |
| 2 | An absence reached by reading, including an AMENDED/REWRITTEN's correction, owes a control | `code-grounder.md:84–85`; `grounding-format.md:174`, `:187`, `:216` | Saves CG#10's forced contradict and retry; the verdict is not improved | **Yes** |
| 3 | `extend` merges an overlapping entry instead of appending it | `prd-ground.md:1421–1431`; `grounding-verifier.md:131`, `:193`; `docs/commands/prd-ground.md:489–490` | Removes 17 of 101 entries (about 4.5 KB) | **Yes** |
| 4 | A retry that replaces a usable blind verdict reports both where they differ | `prd-ground.md:1322`, `:2185–2186` | Surfaces CG#10's CONFIRMED against AMENDED | **Yes**, cheap |

### Would not do

5. **A second blind opinion on a disputed `agree`/`extend`.** The dispute machinery reaches only `contradict` (`prd-ground.md:1378–1386`; `grounding-verifier.md:135`, `:238`; §8). Widening it touches all of those plus the rationale, and adds dispatches. Its best case on X's CG#5 is `unprovable`, which keeps the grounder's wrong CONFIRMED (*Settling*, `:1399–1405`). And none of X's three agents noticed the gap to flag it. Fix 1 attacks the shared blind spot at its source.
6. **Making a constraint claim owe a §2.2 control.** It is the wrong instrument: the missed path was in a file all three X agents had read, not one a search failed to find. It would also turn every on-file CONFIRMED constraint finding into a `missing` → `contradict`, the bulk effect `:1547` warns of.
7. **A hook or new rule against a plain `cd` in derive mode.** The rule is already explicit (`grounding-verifier.md:88`, `:233`), the dispatch was clean, and no exposure was possible here. A hook cannot tell a derive dispatch's Bash calls from others without machinery this does not justify.
8. **X's own feedback idea: a Phase 5 check that sends an uncontrolled absence back to the grounder.** It asks the orchestrator to judge free text, a trigger an agent must judge. It duplicates the compare's deterministic `missing` route, and adds a loop. Fix 2 removes the cause.

## What Y did that X's run can be made to do

- **Y's grounder enumerated the omitted-field write path.** That was variance. Fix 1 makes it an obligation for the grounder and the blind derive alike.
- **Y's compare disputed a blind CONFIRMED** whose own evidence cited the no-arg constructor without showing that every request supplies the value. Fix 1 writes that criterion into §3, which the compare's `blind_disputed` test already reads, so a Y-like split is reliably disputed rather than by luck.
- **Y's leaner evidence came from fewer extends, not from a different rule.** Fix 3 gives X's extends the same economy.
- **Y's CG#5 notes followed *Settling* exactly**, which X had no occasion to use. Fix 4 gives the retry case the same visibility.

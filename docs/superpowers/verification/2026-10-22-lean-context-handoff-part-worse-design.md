<!-- Copied unchanged from lean context D's SDD workspace (W/worse-design.md), a read-only Opus investigation run after the first live runs, preserved by Ruling 23 so every fix it recommended or refused keeps its argued evidence. The paths it names under .superpowers/sdd/ and .worktrees/ were scratch and are removed after the merge; paths under ~/ or /home/<user>/ are on the maintainer's machine; /tmp/.../scratchpad/ paths were session scratch. Where it and the shipped text disagree, the shipped text is the authority. Companion to 2026-10-22-lean-context-handoff-part.md. -->

# Why run X's `/design` was worse: where each defect entered, and the plugin fixes

Worklist: the verdict's table *Defects in X that Y lacks*, X1 to X10 (`/home/ivan.gudak/e2e-live/lean-context-D/design/blind/verdict.md`).

**Same text, different runs.** `design-reviewer.md`, `design-format.md`, `grilling-technique.md`, `interface-designer.md`, `code-scanner.md`, `session-hygiene.md` and `escalation-rules.md`'s rules used below are the same at Y's revision (the lean-context-loader tip, `bc46824c`) and at WT `HEAD` (`6b9434e0`). `design.md` differs only by Phase 0's question-rules load (`git diff bc46824c HEAD`). Every difference below is therefore run variance under the same text, which matches the judge's finding. Where Y avoided a defect, the plugin text did not cause that.

**References.**
- `X:[n] hh:mm:ss` is line *n* of `3a0d7096-4bcb-4765-aadd-831bf2c7e52d.jsonl` (UTC, 2026-10-23).
- `scan` is `agent-a3d378837e8c76c42`, `rev1` is `agent-ad7481d69bdebfe3d` (first review, 16:06 to 16:18) and `rev2` is `agent-a6a5ff1f5a093a730` (re-review, 16:37 to 16:48).
- `Y:[n]` is a line of `6adf2f0b-...jsonl`; `Yrev1` is `agent-ab8c98f0b54281674` and `Yrev2` is `agent-a9e71f3780725021f`.
- Code is bookstore at `af46545`, and `file:line` refers to the WT plugin text.

## 1. Where each defect entered

| # | Entered (step, transcript) | Should have been caught by | Governing text (WT) | Class |
|---|---|---|---|---|
| X1 | **Main session, BLOCK fix cycle.** At X:[1433] 16:35:47, an inline edit answering rev1's MINOR "About 30 delivered criteria have neither a check nor `n/a`" wrote: *"The fixtures are reserved books (`00000000…`) and reserved clients (`…@bis-journey.invalid`), so the store's bulk loop does not disturb them."* The session had read the ARD at X:[510] 14:50:08: *"The bulk loop truncates storage on every iteration (`IngestController.java:256`)"*. It had also read [AD#11]: *"storage's `delete-all` is unchanged and may remove reserved rows"*. The fix read no deploy file: X:[1375] to [1442] are reads of `design.md` and python replaces. | **rev2.** It read `k8s/ingest.yaml:90-165` at 16:40:40, which includes the sidecar that starts the continuous loop (`:110-132`), and passed the claim. | `design.md:397-402` → `escalation-rules.md:580-592`, which says an operational step is read *"against everything its selector reaches in the deploy files …, stateful workloads and containers with side effects included"*. `grilling-technique.md:13` forbids a rationale whose premise the source contradicts. `design-format.md:153-157`: a check names a signal, a threshold and a window, but nothing about the state it relies on. `design-reviewer.md:93-100`: the same. | **Rule ignored**, plus a **rule gap**. The overlap read was not done, and the ARD text in context was contradicted. The gap: the overlap rule reads what a step *reaches*, not what else in the running system acts on the state the step *relies on*. Neither the format nor the reviewer asks for a check's preconditions. |
| X2 | **Main session interview.** At X:[1088] 15:52:33, the [CI images] option said: *"Images come only from k8s/build_docker_all.sh / push_docker.sh, as declared"*. At X:[1179] 16:03:10 it was drafted as *"alerts' six variants through `k8s/build_docker_all.sh`, or CI's blocks"*. Gate 3 played it back *(inferred)* and the user confirmed it. Seeds: the Epic's ride-along names `build_docker_all.sh` (X:[525]), and scan (X:[672] 15:03:53) said the script *"loops over 6 image variants via k8s/push_docker.sh -p <svc> -g{no,yes,pre}"* without naming a tag. No one in X read `k8s/push_docker.sh`, neither the session nor either reviewer; rev1 read only `build_docker_all.sh`. Related: scan's *"CI has 4 blocks per service"*, generalised from 4 grep hits, became the option's "four image blocks". rev1 corrected that to six. | **rev1 and rev2.** | `grilling-technique.md:12`: a fact is explored, not asked, but only in general terms. `design-format.md:135-137` (§10 rollout) asks for no verification. `grilling-technique.md:17`: the play-back marks *"what you inferred"* for the user to confirm. `design-reviewer.md` has no check on claims about the existing system. | **Rule gap.** No text requires a claim about what an existing script produces to be read before it becomes an option, a rollout step or a play-back line. The play-back sends such a claim to the user, who cannot check it. |
| X3 | **Main session interview.** At X:[934] 15:27:58, the [Config hooks] option marked (Recommended) said: *"All client-facing operations, both notices and the reset call the two hooks first, exactly like books/clients/storage"*. Twenty-four minutes earlier, at X:[680] 15:04:02, the session had read `.../StorageController.java` 15-60 and 140-160, so it had seen `findByISBN` and `delete-all` with no hook. Scan had already reported (X:[672]) that the hooks *"are applied inconsistently: getStorageItemByISBN (51-55), getAll and delete have none"*, and that *"Which alerts endpoints call them is a design choice with no framework default"*. The draft (X/design.md:89) cites `.../BookController.java:55`, a single read handler, for a claim about write and reset handlers. | **rev1 and rev2.** Both read `BookController.java` and `StorageController.java` and flagged nothing. rev2 even built a MINOR on the premise ("No test of the hooks path"). | `grilling-technique.md:13` checks a rationale only against "the source": the prompt, the idea, the PRD and inherited Rules, not the code. `design-format.md:72-73` asks the design to name real files, not to verify a precedent. `interface-designer.md:105-106` binds every take to *"Cite `path:line` for every claim about existing code"*; the orchestrator, which writes `design.md`, carries no such rule. | **Rule gap.** The fact-vs-decision split (`grilling-technique.md:12`) covers it only in general terms, so the run skips it easily. |
| X4 | **Scan, then main-session drafting.** Scan read the email pattern but reported only on case (X:[672]): *"clients/model/Client.java:12 regexp allows mixed case"*. Gate 1 played back *"Email sent URL-encoded so `+` survives (inferred)"*. At X:[1117] 15:58:35 the drafting wrote *"[U01] AC06 … `+` reaches clients as `%2B`. … validated"*. The fix cycle (X:[1433]) added a post-release check needing *"a known fixture client whose email holds `+`"*. No one in X read `setEmail` (`.../Client.java:68-71`). Yrev2 caught it as a MAJOR (Y:[1619] 08:32:48): *"the spec criterion was validated without anyone checking it can be set up against clients as it runs"*. | **rev1 and rev2.** | `design.md:291-292`: *"Interrogate testability … and feasibility against the real code"*, which is general. `design-format.md:67-70` covers challenge notes. Nothing says that a `validated` mark is a claim about the components its test cases need. | **Rule ignored** in letter, since the challenge track does ask for feasibility against the code. The run skips this rule too easily, and no reviewer check stands behind it. |
| X5 | **Main-session drafting.** At X:[1179] 16:03:10, the post-release row *"[U07] AC01 \| The same from the storage pod at `$DT_ALERTS_SERVER`"* sits beside rollout step 2, *"run `k8s/restart.sh -nodb`, which re-applies `configmap.yaml` … first"*. That step re-applies an unchanged storage Deployment, so no storage pod restarts (code:`k8s/restart.sh:8, 29-43`). Y's session raised this itself at drafting as ER6 (Y:[1109] 07:41:23). | **rev1 and rev2.** Both read `k8s/restart.sh`. | `design-format.md:153-157` and `:135-137`, and `design-reviewer.md:93-100`. None of them ties a check's precondition to the rollout as written. | **Rule gap**, with judgement in it: catching it needs the deploy tool's semantics. |
| X6 | **Never raised in X**: not by the main session, rev1 or rev2. Yrev2 raised it as a MINOR: *"Subscribe is designed with 'no transaction held across HTTP' … but no setting stops it holding a database connection across HTTP"*. | none | Nothing specific; the NFR list is at `grilling-technique.md:110`. | **Judgement variance.** |
| X7 | **Drafting.** It wrote *"Service `alerts-svc`, port 91 → 8080, nodePort 30010, debug 32010"* (X/design.md:140) and *"the Testcontainers profile"* (:322, :434). That profile is never defined, and the test profile pins `H2Dialect` (code:`storage/.../application-test.properties:1`). | rev1 and rev2 | `design-format.md:84` (§4: config keys stated concretely). The decision-completeness check at `design-reviewer.md:53-54` counts only `- [ ]`. | **Judgement variance**, with a §4 rule nearby. |
| X8 | **Main session interview.** At X:[956] 15:30:47, [Read SLO] recommended *"p95 ≤ 200 ms at 200 pages … Proposed into the spec's Engineering review; resolves spec OQ3"*, with *"Leave it to the PM"* offered unmarked. The spec edit then ticked the question: *"- [x] … — Answered by `/design` ([ER-3]): … proposed as a criterion."* (X/specification.diff:30). OQ1 and OQ4 were ticked the same way, although their answers propose Scope text. | none. `design-reviewer.md:139-141` keeps spec-level questions out of its gate. | `design.md:204-206`: *"any existing `- [ ]` open questions (spec-level; tolerated — the design may resolve or inherit them)"*, which licenses the run's action. `design.md:293-294` pulls the other way: *"Raise substantive changes to ACs/TCs as proposals — do not unilaterally rewrite them"*. | **Rule gap.** The two sentences pull apart, and the run followed the first. |
| X9 | **Terminal Phase 9.** At X:[1886] 17:22:16 the run `cat`s the existing `resume.md`, which still lists *"ARD omissions still open … /create-ard refine pending; … /update-prd pending"*. At X:[1969] 17:23:33 it writes a new pointer without them. | none | `session-hygiene.md:73-83`: the pointer is *"OVERWRITTEN each run"*, and *Carry-forward* means *"decisions the next phase needs that are NOT already in the artifact"*. A refine pending from an earlier phase is not something the next phase (`/implement`) needs, so the definition drops it. | **Rule gap.** The run followed the text. |
| X10 | **(a)** At X:[690] 15:04:25, the [Uniqueness] preview SQL re-selects `isbn … AND status='PENDING'` in statements 2 and 3; rev1 raised a BLOCKER. **(b)** At X:[827]-[828] 15:18:48-53, the orchestrator's hybrid after the fan-out said: *"Map storage-404-after-found to `Gone`: subscribe answers 404 …, and the sweep withdraws"*. None of the takes proposed that mapping: A answered 201, B answered 503, and C could not represent the case. [AD#5]'s Rule excludes it (*"any other answer from either service … leaves the subscription pending"*), and so does its Prevents (*"a transient error ending subscriptions with a false withdrawal"*). rev1 missed it. rev2 graded it MINOR, although `design-reviewer.md:109` makes an unrecorded Rule violation a BLOCKER, and the reversal went in unreviewed. **(c)** At X:[1263] 16:04:23, the [Whole gate] question names *"[ER-5]/[ER-6] and the notation change"*. Those were written at X:[1193] 16:03:36, after Gate 3's play-back, and were never played back. | (a) rev1 caught it. (b) rev1 missed it; rev2 caught it at the wrong severity. (c) none | (b) `grilling-technique.md:13`: *"An inherited `[AD#N]` Rule is read word for word before you recommend a bound, a match rule, a limit or an enumeration it governs … departing from it is offered only as an ARD deviation"*. `design.md:358-362` asks for a hybrid and does not point to that rule. (c) `grilling-technique.md:16-17`: the whole-artifact gate plays back *"only what changed since its sections were confirmed"*. | (a) **Judgement variance.** (b) **Rule ignored.** The trigger list does not plainly name an outcome mapping, and the fan-out step that invites a hybrid never points to the rule. (c) **Rule ignored.** |

### What the table shows

1. **All five false claims (X1 to X5) entered in the main session**, during the interview, the drafting or a fix. No subagent invented any of them. Scan's report was accurate where it spoke: it said the hooks were inconsistent. It was only incomplete for X2 (it named no tag) and X4 (it reported only on case). Its one false statement, "4 blocks per service", was caught by rev1.
2. **For X1 and X3, the session already held the contradicting fact** (the ARD's bulk-loop edge case; storage's hook-less handlers) and wrote the claim anyway. A rule at the point of entry is necessary, but on its own it will be skipped. The net has to be somewhere else.
3. **The reviewer has no dimension for claims about the existing system**, and its brief has no field for the repositories. Both runs passed the repository path anyway, in free text: X inside the `Target paths` line, Y in a *"Context you may use"* line. Y's reviewers, running the same agent text, then checked deployment claims against the code without being asked. They caught X1's counterpart (Yrev1 MINOR, `ingest.yaml:132`), X2's (Yrev1 MAJOR, `push_docker.sh:76`), X4's (Yrev2 MAJOR, `Client.java:12`) and X6 (Yrev2 MINOR). X's reviewers opened the very files (`BookController.java`, `StorageController.java`, `build_docker_all.sh`, `restart.sh`, `ingest.yaml`) but were never told to test the design's claims against them.
4. **Three of the five false claims (X1, X4, X5) sit in post-release checks.** Each check relies on state that the running system does not provide: fixtures the bulk loop wipes, a client the clients service cannot create, and an environment variable a pod never reloads.

## 2. Fix proposals, ranked by how much they would have changed this run

### F1. Reviewer: a "claims about the existing system" check, and the repositories in its brief (X1, X2, X3, X4; X5 possibly)

**Where:**
- `design-reviewer.md:16-32`, the input contract: add a **Repositories** field holding each confirmed implementation repository's absolute path and the ref Phase 4 scanned (`prep.scanned_ref`). It is required wherever `design.md`'s `Repos` names one; where it is absent, report that claims could not be verified, as `:20-21` already does for a missing specification path.
- `design-reviewer.md:48`: add a new cross-cutting check.
- `design-reviewer.md:3` (description) and `:8-11` (what it reads): mention the repositories.
- `design.md:383-394`, the Phase 6 brief: add `Repositories: <path> @ <scanned ref>`, one line per confirmed repository.

**Intent of the check.**
- **What it covers.** It checks every statement `design.md` makes about the existing system that one of these rests on: a decision, a rollout or release step, a test case, or a requirement marked `validated`. Such statements include:
  - a precedent ("as X does", "like every service");
  - what a script or a job produces;
  - an image tag, a port, a profile or a manifest value;
  - how an existing endpoint answers;
  - what a deploy step changes in running processes;
  - what a running job does to data.
- **How it checks.** The reviewer re-derives each claim from the repository. A claim that generalises is checked across every instance it names, never only the one it cites.
- **Severity.**
  - A claim the code contradicts is a MAJOR.
  - It is a BLOCKER where the claim is the premise of a decision the user confirmed, because the fix is to put the decision to the user again, not to edit a line. This is `grilling-technique.md:13`'s *"a correct decision on a false premise"*, and it is what X3's decision 8 was.
  - A claim stated as fact with nothing in the repository behind it is a MINOR.
- **What it leaves alone.** Architecture-governance citations stay out of scope, so the gotcha at `:142-146` stands.
- **Reading the right ref.** The reviewer has only Read, Glob and Grep, so it reads the working tree. On a writable clone, Phase 4 left the tree at the scanned ref. On a read-only mount that was scanned by ref (`code-scanner.md:59`), the brief says the tree is not at that ref, and the reviewer says which claims it read off the tree.

**Would it have caught them in this run?**
- **X3:** yes, near certain. Both passes had both controller files open.
- **X1:** likely, at rev2. It had `ingest.yaml:110-132` open, and the ARD's edge case is on the same page.
- **X2:** likely. It takes one more read, since `build_docker_all.sh` calls `push_docker.sh`.
- **X4:** likely, because a `validated` mark falls within the check.
- **X5:** possible.

Y is the evidence: the same agent did exactly this when it chose to. The check turns that variance into a requirement.

**Cost:** no new step and no new agent. Each review pass needs the reads the claims require. rev1 already opened about 25 files; I estimate 5 to 10 more Opus reads per pass, and more findings going into the one fix cycle.

**Text that changes with it:**
- `docs/commands/design.md:76`, which lists what the reviewer is given.
- `docs/reference/agents.md:12`, which mirrors the description.
- `design-reviewer.md:8-11`, whose *"Reads the whole design.md and its source specification.md"* must also name the repositories.

### F2. Post-release checks name the state they rely on, and show the running system provides it (X1, X4, X5)

**Where:**
- `design-format.md:153-157`, the *Post-release checks* bullet.
- `design-format.md:118-132`, §8, for any test case run against a deployed system. Y's "Deployment, by the operator" test is an example.
- `design.md:305`, the release-verification grill list.
- `design-reviewer.md:96-100`, the *Release verification* bullet.

**Intent.** Each check names the state it relies on: the records it reads or creates, the configuration the called process must hold, and the jobs that must not run. The design then shows that the running system provides that state:
- **A fixture** can be created through the component that owns it, as that component runs. Otherwise the check says how the fixture is inserted, or it reads `n/a — <reason>`; `design-format.md:155` already allows that, and Y did it for AC06.
- **A configuration change** reaches the process that reads it under the rollout steps as written. A workload that is re-applied unchanged is not restarted.
- **Nothing else in the deployed system** changes that state during the check's window: no scheduled job, load generator, sidecar or reset. Otherwise the check says how that thing is paused, and restarted afterwards.

On the reviewer side: a check whose state the running system cannot provide, or that another running component changes during its window, is a MAJOR.

**Would it have caught them in this run?**
- **X1:** yes. The bulk loop is exactly a job that changes the state during the window, and the ARD in context said so.
- **X4:** yes. "Created through the component that owns it" sends the author to the clients service's create path.
- **X5:** likely, through the configuration-reaches-the-process clause.

**Cost:** three sentences. At authoring time, a read of the deploy files for each group of checks.

**Not done alongside it:** widening `escalation-rules.md:589-592`. A check added in a fix cycle is still written to `design-format` §11, and the re-review applies the reviewer half of F2. The shared bullet reaches seven commands, and this check belongs to `/design` alone.

### F3. At the point of entry: a premise about the existing system is read before it is put, and the play-back never asks the user to confirm a code fact (X2, X3, X4; X1 in part)

**Where:**
- `grilling-technique.md:13`: extend the rationale check from *the source* to *the code*.
- `grilling-technique.md:17`: the play-back.
- `design-format.md:72-73` (§3), or the *Principle* at `:9-21`: mirror `interface-designer.md:105-106` for the author.
- Optional: `code-scanner.md:119-120`. A count or a per-component pattern in a note is measured, not read off a sample of hits. That would have stopped "CI has 4 blocks per service".

**Intent:**
- **(a) Before a question is put.** A premise about the existing system that a question, an option or its rationale states is read in the code before the question is put. That covers a precedent, what a script or a job produces, and a count. The read covers every instance the premise generalises over: "like every service" is checked in each service's matching handler. A citation proves the line it names, never the whole class. Where the premise fails, the option is rewritten or dropped.
- **(b) At the play-back.** The play-back marks inferences about intent and decisions as now. A statement about the existing system is not an inference for the user to confirm: it is read and cited before the play-back, or it is played back as *unverified*, with what would settle it.
- **(c) In `design.md`.** Every statement about the existing system that a decision, a step or a `validated` mark rests on cites the `file:line` it was read at.

**Would it have caught them in this run?**
- **X3:** yes, if followed. Reading the notices' analogues (storage's `delete-all`, books' deletes) refutes the premise before the question is asked.
- **X2:** yes. The [CI images] option cannot be written without reading `push_docker.sh`.
- **X4:** yes. A `validated` mark on AC06 must cite the clients service accepting `+`.

X's session held the contradicting facts for X1 and X3 and wrote the claims anyway. So a run can skip this step, which is why F1 is the net and ranks first.

**Cost:**
- Reads during the grill, about one per load-bearing claim; about 6 to 10 in X.
- One clause in each of two shared bullets.
- **Extent:** `grilling-technique` has ten callers. The clause binds only where a question rests on a premise about existing code: in practice `/specify`, `/create-ard`, `/idea --ground-code` and `/design`. Re-read `:12-18` against each caller (the extent face of sentence-context).

**Text that changes with it:** `grilling-technique.md:17`'s *"An inference the user has not confirmed is still an assumption, and it is the line most worth their reading"* stays true for intent and decisions. The new clause narrows what may be marked *inferred*, so the bullet must say both, or the two will read as contradictory.

### F4. A product question on the specification stays open, with the design's proposal under it (X8)

**Where:** `design.md:204-206`, and `design-format.md:194-200` (*Engineering-review edits to the specification*). Optional: `design-reviewer.md:103-105` (*Challenge coherence*) treats a ticked spec question whose answer adds or changes requirement text as a MINOR.

**Intent:**
- A spec open question whose answer changes no requirement text may be ticked, with the answer recorded.
- An answer that adds or changes a criterion, a scope line, a target or a limit is written under the question as the design's proposal, and the `- [ ]` stays for the specification's owner. The design proceeds on its proposal, and the coverage row reads `proposed-change`.

**Contradiction to avoid:** state the distinction from `design.md:313-315` (*"pushed onto the `specification.md` … and the design waits on it"*). That sentence is for an unknown the design cannot settle; this one is for a product decision the design proposes an answer to. Stated that way, the two do not read as contradictory, and `design.md:204-206`'s "may resolve" becomes this rule.

**Would it have caught it in this run?** Yes, for X8, and it would also have kept OQ1 and OQ4 open with their Scope proposals. Y did exactly this, with an "Engineering answer/proposal (design, ERn)" line under each open question.

**Cost:** none.

### F5. A fan-out recommendation, and a hybrid above all, is checked against the brief's constraints and the inherited Rules before it is offered (X10 b)

**Where:** `design.md:358-362`. In `grilling-technique.md:13`, the list *"a bound, a match rule, a limit or an enumeration it governs"* gains *"or the outcome it assigns to an answer or a state"*.

**Intent:** a hybrid can combine things no take was asked to combine, so it is a new recommendation. It is read against `problem_frame` and against the inherited `[AD#N]` Rules and Prevents, word for word. A departure is offered only as an ARD deviation.

**Would it have caught it in this run?** Yes. [AD#5] assigns storage's other answers the outcome "leaves pending". The final design would not change, because X ended right through an unreviewed edit. The fix removes that unreviewed reversal of a decision the user had confirmed.

**Cost:** none.

### F6. The resume pointer keeps what it carried that this run did not settle (X9)

**Where:**
- `session-hygiene.md:82` is the source. Then regenerate `reference-parts/session-hygiene/resume-pointer.md` with `scripts/reference-parts.py generate`; I did not run it here.
- Copies to update: `dev-workflows/docs/reference/resume-and-checkpoints.md:16` and `product-workflows/docs/reference/resume-and-checkpoints.md:16`.

**Intent:** before overwriting, read the pointer being replaced. Keep each carried item this run did not settle, such as an open follow-up or a pending refine, even where the next phase does not need it. Drop only what this run settled and what the artifact now records. The pointer is still overwritten each run (`:73-74`), not appended to.

**Would it have caught it in this run?** Yes. X read the old pointer at X:[1886] and dropped those items, as the current definition says to.

**Cost:** one read of a file of about 12 lines, which X already made. This is a `workflows-core` change, so it reaches every PRD-scoped command that writes the pointer.

### F7. A gate question names only what its play-back has shown (X10 c)

**Where:** `grilling-technique.md:16-17`.

**Intent:** an item added since the last section gate, such as a new note or a changed notation, is played back by its content, never by its label alone, before the whole-artifact gate asks.

**Would it have caught it in this run?** Yes. **Cost:** none. It has no effect on the design.

### Ranking and recommendation

1. **F1: recommend.** It is the net for X1 to X4, the defects that decided the verdict. Y shows the same agent catching them when it chooses to check.
2. **F2: recommend.** It is cheap, specific, and covers both the author and the reviewer for the three release-time surprises.
3. **F3: recommend**, scoped to load-bearing claims. It is the point of entry, and it saves the review cap. On its own it is skippable, as X1 and X3 show.
4. **F4: recommend.** It removes a sentence that licenses the defect, at no cost.
5. **F5: recommend.** No cost; it keeps confirmed decisions consistent with the ARD.
6. **F6: recommend.** One small read; carried items stop being lost between phases.
7. **F7: optional.** It costs nothing, and it does nothing for the design.

F1, F2, F4 and F5 change `dev-workflows`; F3, F6 and F7 change `workflows-core`, and F6 also needs its parts regenerated. They ship as one `workflows-core` and `dev-workflows` pair.

### Not recommended

- **A rule for X6 (open-in-view).** This is a framework default, and a checklist of one framework's defaults is not general. Y found it through review variance, not through a rule. F1 does not reach it, because it is not a claim about the repository.
- **A value-completeness check in the reviewer for X7.** §4 (`design-format.md:84`) already asks for concrete config keys, and auditing every value costs more than a gap of two items. F1 catches the profile half wherever the design claims the existing test profile is enough.
- **A rule for X10 (a), the SQL race.** It is a question of SQL semantics, and rev1 caught it as a BLOCKER, so the system worked.
- **Widening `escalation-rules.md:589-592` for X1.** F2 covers it through the format the fix edits, and the shared bullet reaches seven commands.
- **A standard Phase 4 scan theme (build → tag → pull, config → process, background jobs).** It would scan every deploy path up front. F3 and F1 read only what a claim needs.

## 3. What Y did that X's text could adopt

- Its reviewer brief carried a line naming the repository and its ref: *"the implementation repository is … at /workspace/e2e/bookstore (master @ af46545)"*. F1 makes that a field.
- Its reviewers verified deployment and code claims: `push_docker.sh:76`, `ingest.yaml:132`, `Client.java:12`. F1 makes that a check.
- It left the spec's open questions `- [ ]`, with an "Engineering answer/proposal (design, ERn)" line under each (F4).
- It scoped its precedent claim to what its citation proves: *"as books' and clients' `find` do (`BookController.java:55-56`)"* (F3).
- Its deployment test spells out stopping and restarting ingest's bulk loop, and it raised the configmap reload as ER6 (F2).
- It raised AC06 as a spec challenge, ER9, with a code citation. That is what the challenge track at `design.md:291-292` asks for, with F3 behind it.
- Its resume pointer kept "Still open from earlier phases" (F6).

## 4. Found in passing

- **`design-format.md:204-206` is false.** Its *Provenance* says the grilling technique *"is embedded in `commands/design.md` … so `/design` has no runtime plugin dependency"*. In fact `design.md:286` loads `workflows-core:grilling-technique`. Prose is executed, so the sentence should be fixed.
- **rev2 under-graded a Rule violation.** It graded an unrecorded [AD#5] Rule violation MINOR, where `design-reviewer.md:109` says BLOCKER. `/design` runs no `finding-triage`, so nothing re-grades a reviewer's severity. The rule is clear, so I propose no text change; this is recorded as reviewer variance.

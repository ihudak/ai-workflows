# SEC-G2 D: security conformance

Date: 2026-11-15. Status: **draft, revision 1** — not yet reviewed. Roadmap row **D** of `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md:104` ("Security conformance: traces each threat-model mitigation to merged code, as `/conformance` traces requirements"; depends on "B or C"), the last of SEC-G2's three sub-projects. It builds on B as built (`docs/superpowers/specs/2026-11-14-sec-g2-b-threat-model-design.md`) and on C as built (`docs/superpowers/specs/2026-11-14-sec-g2-c-design-threat-review-design.md`), both on `main` at `ec60ad47`.

Every decision is written with a recommended answer. The four marked **(maintainer)** at the end are the calls only the maintainer can make; the rest are the author's, stated so they can be corrected. Statements about the tree cite `file:line` at `ec60ad47`; a paragraph opening **Assumption** is the author's reading, which the builder confirms before relying on it.

## Intent

B gave the architecture a threat model and C made `/dev-workflows:design` answer the threats it defers. Both end at a document. Nothing yet says whether the code carries a mitigation out: a threat `Mitigated by ard.md [AD#2]` is closed on paper when the model merges, and a design's `[DT#N] Mitigated — Rule: …` when the design does. And two debts are still uncollected: a deferred threat no design answered, which C's declined review leaves "unanswered" and names D as the one that reports it (C's design, D1 *Declined*, D4 and D7); and an acceptance whose review date has passed, which today only a later `/create-ard` refine lists (`plugins/workflows-core/references/threat-model-format.md:100`).

D makes `/dev-workflows:conformance` collect both. A mitigation is a Rule, and `/conformance` already traces Rules to code at the ref the unit's work stands on. So D adds no command and no agent: it adds the design's `[DT#N]` Rules to the requirements `/conformance` traces, joins each threat to the verdicts of the mitigations it rests on, and lists — for every threat that applies to the unit — where it stands. Nobody is asked to accept a risk, and nothing is written into the model, the design or a findings register.

**Why now:** B and C are built; the format has said since B that `/dev-workflows:conformance` "is to read it later" (`threat-model-format.md:7`, `:126`), and `.claude/rules/threat-model.md:32-34` holds the claim open for D to close.

## What exists today

Facts the decisions rest on.

- **`/conformance` already traces every applicable `[AD#n]` Rule.** Its Epic run resolves the ARD with `workflows-core:ard-resolution` and takes "the `Rule` of each `[AD#n]` it returns as applicable"; its PRD run takes every Epic's set and every part of each PRD-level Rule (`plugins/dev-workflows/commands/conformance.md:108`, `:111`). `ard-resolution` returns each as an `invariants` entry with `id`, `source`, `binds` and `rule` (`plugins/workflows-core/references/ard-resolution.md:67-72`). So the decision a `Mitigated by <pair>` names is, where its ARD is on the default branch, a requirement the run traces today — with no link to the threat.
- **`design.md` is context to `/conformance`, never traced.** Its `## Requirements coverage` notes are carried to the walk (`conformance.md:110`); the record's `document:` is `specification.md | epic.md | prd.md | ard.md` (`plugins/dev-workflows/references/conformance-format.md:74`; `references/handoff/conformance-tracer.md:26`); and `Not traced:` "never names a `design.md`, which is context and never traced" (`conformance-format.md:57`).
- **`/conformance` already gates `design.md`.** Its Phase 0 step 4 runs `require-on-main` on each Epic's `design.md` (`conformance.md:72`; `plugins/workflows-core/references/phase-handoff.md:332`). It gates no `threat-model.md`: the model's one §3.4 row is `/design`'s (`phase-handoff.md:329`).
- **The tracer reads code at a ref and is not inert.** `conformance-tracer` declares `tools: ["Read", "Write", "Glob", "Grep", "Bash", "Skill"]`, reads every file with `git -C <repo_path> show <ref>:<path>`, never switches or writes in the repository, writes one file, and carries the untrusted-content block (`plugins/dev-workflows/agents/conformance-tracer.md:4`, `:13`, `:35-70`). One runs per repository, in parallel, at most four (`conformance.md:187`).
- **The orchestrator re-checks a tracer's `partial`, `missing` and `contradicts` at the evidence, and a `satisfied` only where it cites no `file:line`** (`conformance.md:230-255`).
- **The walk offers three decisions and *Cancel*:** `["Fix the code", "Amend the document", "Accept as shipped", "Cancel"]` (`conformance.md:288`). *Accept* is "recorded with its rationale" (`:351`) — an Epic run's is the Dev's, `proposed`; a PRD run's the PE's, `final` (`conformance-format.md:102-103`).
- **`/conformance` writes upstream only on a PRD run**, a `- [ ]` note under `## Engineering review` of `specification.md`, `prd.md`, `epic.md` or `ard.md` (`conformance.md:344-348`); an Epic run proposes only (`:349`). It writes no note into a `design.md`.
- **A `[DT#N]` entry is built to be traced.** A live `Mitigated` entry carries a testable Rule and a `Test` naming the `## Test strategy` line that checks it; `Answers` is `[[<KEY>]] [TH#N]` or `—`; on an Epic with a `target:` its Where names the target (`plugins/dev-workflows/references/design-format.md:308-337`). C's D4 names what D reads: "D reads one heading form and joins to the model through `Answers`", and "D verifies that the design there holds a `Mitigated` entry answering the threat" for `Not this design's — answered in [[<KEY>]] design.md`.
- **Which threats land on a design is stated in `/design` alone** — its Phase 2.5 steps 5 to 7: the set, format §6's check read-only, and the three bullets by folder and `target:` (`plugins/dev-workflows/commands/design.md:246-253`). `/conformance` cannot cite another command's phase.
- **The Dev never accepts a risk; the PA alone does, in the model** (`threat-model-format.md:74`; `design.md:528`; `.claude/rules/threat-model.md:35`, `:37`).
- **`/create-ard` takes in no returned threat and re-disposes no live, non-stale deferred threat** — RETURNED-INTAKE, logged (`docs/superpowers/to-fix.md:201-205`).
- **The lineage table already expects a note D will not write**: the `threat-model` row's `_source` reads "so a /dev-workflows:conformance note (sub-project D) never reads as a revision" (`plugins/workflows-core/scripts/lineage-kinds.json:141`).
- **`dev-workflows` depends only on `workflows-core`** and `security-workflows` on `workflows-core` and Claude Security (`plugins/dev-workflows/.claude-plugin/plugin.json:12-14`; `plugins/security-workflows/.claude-plugin/plugin.json:12-15`). `design-format` and `conformance-format` are `dev-workflows`' references, so no other plugin can load either.
- **The delivery order is conformance, then the scan**, both on the Epic's branch before the merge; and the PE's PRD run before `--verify-fixes` (the scan design, *Where it sits in the delivery*, `:111-124`; `conformance.md:564-566`).

## Goals

1. **Every mitigation is traced to code.** A design's `[DT#N]` Rule becomes a requirement `/conformance` traces, with the test that checks it; a threat's `Mitigated by` decision is joined to the verdict its `[AD#N]` Rule already gets.
2. **Every threat that applies to the unit has one stated standing** in the record and the report: verified, open, not checked, unanswered, accepted, review due, stale or unreadable. C's expectation is met on the Epic run, before the merge: a declined review's deferred threat reads *unanswered*.
3. **Nobody accepts a risk in `/conformance`**, and it writes nothing into `threat-model.md`, into a `design.md` or into a findings register.
4. **No regression:** a unit with no `threat-model.md` at its known paths and no `## Threat review` in any design it reads gets today's run, record and handoff, byte for byte.
5. **A minimal GIT-G1 footprint**, each edit listed.

## Non-goals

- **`/create-ard`'s intake of returned threats** (RETURNED-INTAKE). D reports a returned threat as unanswered and names the command; the path that re-disposes it is that follow-up's.
- **Judging whether a mitigation is enough.** D traces that the Rule is carried out and tested. Whether the Rule defeats the attack is `ard-reviewer`'s and `design-reviewer`'s question, and what the code still lets through is the scan's.
- **Any link to the findings register.** D reads no register, writes none, matches no `[SEC#n]` finding to a threat by CWE, and adds nothing to `/security-workflows:scan`, `register.py` or the weakness classes.
- **A change to `/dev-workflows:ready`'s *Delivery verified* test** (maintainer question 3), and to what `/document` and `/release-notes` take from a record.
- **`/implement` enforcing a `[DT#N]` Rule while it builds**, and `code-review` gaining a threat dimension. D checks after the build, as `/conformance` does.
- **A new command, agent, branch prefix, id prefix, role, or a dependency on `security-workflows` or `product-workflows`.**
- **Re-running C's review.** D proposes no entry and no answer; an unanswered threat is sent to `/dev-workflows:design`.

## Anti-goals

- **A second place a risk is accepted.** An acceptance outside the model has no owner, no reason the Security Engineer reviewed and no review date.
- **A verdict resting on what the code says about itself.** A comment, a test name or a commit message saying a Rule holds is not evidence; the tracer's rule already says so (`conformance-tracer.md:29`), and D adds the orchestrator's own read of every satisfied mitigation (D9).
- **A model or design that steers the run.** Their field text is data; every value is one line; every id is resolved against a set the run holds.
- **A threat model that becomes a prerequisite.** A missing, unmerged or half-edited model never stops a conformance run.

## Decisions

### D1. A dimension of `/dev-workflows:conformance`, automatic, with no question

D is part of the existing command: more requirements in its Phase 1 inventory, the same tracers, the same re-check, a narrower walk for mitigations (D5), and one optional section in the same record (D6). It runs wherever its inputs exist (D2) and is never offered or declined (maintainer question 4).

- **Why not a step of `/security-workflows:scan`:** the scan cannot load `dev-workflows:design-format`, where `[DT#N]` is defined, nor `conformance-format`; it has no tracer, no walk and no record but the register, which `register.py` alone writes and which holds Claude Security's findings, not requirements. And it runs *after* conformance, so a mitigation follow-up would reach `/implement` after the scan had read the branch.
- **Why not a new command:** it would need `unit-branch`, the clone and ref resolution, the tracer, the re-check, the record's re-run rules and a branch prefix of its own, or become a second writer of `_conformance.md`, whose format says "The command is its only writer" (`conformance-format.md:5`). The roadmap says "as `/conformance` traces requirements", and the format already names the command.
- **Why automatic:** `/conformance` traces "every requirement" of its unit and asks nothing about scope. A `[DT#N]` Rule is a design decision the Dev confirmed and the reviewer passed; leaving it out by a question would let the one skipped check be the security one. It costs no dispatch: the Rules ride in the tracers the run already sends.

### D2. What it reads, and the gate

**Designs.** Each `design.md` the run already gates and reads (`conformance.md:72`), now parsed for a `## Threat review` section outside any fenced block, as `workflows-core:pre-lint`'s design block finds one (`plugins/workflows-core/references/pre-lint.md:162`). No new gate: the section is part of a gated document. An `absent` design falls back as today.

**Models.** Known paths, never a search — on an Epic run, `<Epic folder>/threat-model.md` and the PRD folder's; on a PRD run, the PRD folder's and each Epic folder's that Phase 0 step 3 placed. The test is the file and its `kind: threat-model`, never the folder's asserted kind, so a BRD-route slice is read as any PRD folder.

- **Only where the unit's ARD resolves.** Phase 1 (b)'s `ard-resolution` call decides: on `status: none` no model is gated or read, and where a file stands at a known path the run prints `Threats: <path> not read — no ARD resolves for <KEY>`. `status: unmerged` has already stopped the run (`conformance.md:109`).
- **The gate falls back and never stops** (maintainer question 2). For each path, `require-on-main`, read in §3.7's order: `stopped: true` → fall back; else `pass`, `pass_amending` or `unmanaged` → the model is read from the working tree; `absent` → fall back. A fallback reads nothing at that path and prints one line naming the path and the row — on row F only where the working tree holds a file there. This is `/design`'s mapping (`phase-handoff.md:329`, `:383`), for the same reason: an absent optional input never becomes a prerequisite, and a model in flux must not stop a conformance run that worked before the model existed. Row C's repair offer is the gate's own; declined or failed, it is the fallback.
- **It runs in Phase 1 (b), after `ard-resolution`**, not in Phase 0 step 4: whether a model is read depends on the ARD's status. `phase-handoff` §5 rule 2 holds — the gate still precedes every read of the file.
- **B's check, read-only.** The run loads `workflows-core:threat-model-format` and runs §6's check on each model read, against the ARD files `ard-resolution` returned and the run's component set — format §4's two sources, as `/design` takes them (`threat-model-format.md:59-61`). A stale live threat is listed (D4) and none of its mitigations is joined. Where no set resolves, no model threat is read (`Threats: no component set resolves — the models' threats are not read`); the designs' `[DT#N]` Rules are still traced, since a Rule needs no set.
- **No model joins the lineage `upstream-check`** (`conformance.md:95`), which can ask and stop. A re-disposed `[TH#N]` already shows the design that recorded the model as stale through that design's own lineage record (C's D2).

**Which threats apply — format §10, new.** The rule C wrote into `/design`'s Phase 2.5 step 7 is stated once more, in `threat-model-format` as a new section, *The threats that land on a unit*, in `/design`'s words: an Epic folder's own model, every live threat; the PRD folder's model on an Epic with a `target:`, each live threat whose Where holds the target id or whose `contract <pair>` names a row whose producer or consumers name the target; the PRD folder's model on an Epic with no `target:`, or on a PRD-level unit, every live threat. `/conformance` cites §10. **A PRD run applies no filter**: every live threat of every model it read is in scope.

- **`/design` is not changed.** Its step 7 keeps its own statement, and `.claude/rules/threat-model.md` gains an invariant naming the two places that change together, as invariant 7 does for the line-ending list. **Why not have `/design` cite §10 now:** beside an older `workflows-core` it would find no §10 and could offer no review, so D's release would take C's feature away from a half-updated install. Moving `/design` onto §10 is a clean-up for a later release, not D's.
- **It fails closed.** A `/conformance` whose loaded format holds no §10 — an older `workflows-core` — reads no model, prints `Threats: the models' threats are not read — update workflows-core`, and still traces the `[DT#N]` Rules.

**Rejected:** restating the rule in `conformance.md`. A third prose copy in a second command is the drift §10 exists to prevent, and a fourth reader would add a fourth.

### D3. What is traced: a mitigation is a Rule

**A design's `[DT#N]` Rule — a new requirement.** Each live entry whose Disposition opens `Mitigated — Rule: ` in a `design.md` the run read is listed in Phase 1 (b) with `key` the design's folder key, `id` `[DT#N]`, `document: design.md`, and `text` the Rule, one line. Its `Test` field's text rides beside it as `test_hint`, data. It is routed as any requirement of its unit (`conformance.md:197-202`) and is never marked `own_part`: on an Epic with a `target:`, C's validation already holds its Where to the target.

- **The tracer judges the Rule and its test together.** A `[DT#N]` section returns the usual verdict and one more line, `- test: <file:line@commit of a test that checks the Rule> | none — searched <the searches run>`. The code does what the Rule says and a test checks it → `satisfied`. The code does it and no test checks it → `partial`, its `shipped` saying the test is missing. The rest as for any requirement. The test is evidence that the Rule is checked, never that it holds: the verdict on the code still rests on the code (`conformance-tracer.md:29`).
- **`Never trace [TCxx]` stands** (`conformance.md:112`): no test case becomes a requirement. The test is one part of a `[DT#N]`, as C wrote it into the entry.
- **Why `partial` for a missing test, and not a note:** C's reviewer makes a `Mitigated` entry with no test a BLOCKER (C's D8); a mitigation nobody tests is the regression the next refactor ships. *Fix the code* then queues the usual follow-up, and `/implement` writes the test.
- **An entry that is not readable** — no Disposition, more than one, a `Mitigated` with no Rule — is not traced, and is listed as *unreadable* with what is wrong (D4). `/design`'s pre-lint and reviewer already block one; D only declines to guess.

**A threat's `Mitigated by` decision — joined, never traced twice.** Each pair names an `[AD#N]` of an ARD file. D resolves the pair against the run's inventory — the folder, the ARD file and the decision number together, a `[[<PRD-KEY>]] ard.md` pair read in the inherited PRD-level ARD — and takes that requirement's verdict. A pair the inventory does not hold — its Rule bound only sibling components on an Epic run and is `not-checkable`, or its repository was not traced — leaves the threat *not checked*, with the reason. No Rule is handed to a tracer a second time.

**Assumption:** the inventory keeps, for each `[AD#n]` Rule, the ARD file it came from, so that `ard-payments.md [AD#2]` and `ard-cart.md [AD#2]` in one Epic folder are told apart. `ard-resolution`'s `invariants` carry `id` and `source: prd | epic | area` but no file name (`ard-resolution.md:67-72`), and the record's `document:` enum names `ard.md` only. If the inventory cannot tell them apart, the builder adds the file to the inventory's own entry — never to `ard-resolution`'s output — and a pair it still cannot resolve to exactly one requirement leaves the threat *not checked*; it is never matched by number alone.

### D4. Where each threat stands — eight states, derived and never asked

For every threat in scope (D2) and every live `[DT#N]` entry with `Answers: —`, the run derives one state from what it holds. The vocabulary is closed, and no state is a decision.

| State | Where |
|---|---|
| `verified` | every mitigation it rests on is `satisfied` this run |
| `open` | a mitigation it rests on is a discrepancy (its `[DD#n]` named), is *unverified*, or stands accepted in an earlier entry (D5) |
| `not checked` | a mitigation it rests on was not traced or is `not-checkable` on this run; the reason given |
| `unanswered` | a deferred threat, or the deferred rest of a `Mitigated by …; the rest deferred to design: …`, that no live `Mitigated` entry in scope answers; the reason given, below |
| `accepted` | `Accepted — <owner>; <reason>; review by <date>`, the date not before the day the run started |
| `review due` | an acceptance whose date is before that day, or does not parse as `YYYY-MM-DD` |
| `stale` | format §6's check fails; the tests it fails named |
| `unreadable` | its Disposition is none of the format's three forms, or two threats share its `[TH#N]` |

**What a threat rests on.** `Mitigated by <pairs>` → every pair's Rule. A deferred threat → every live `Mitigated` entry in scope whose `Answers` is, whole, its `[[<KEY>]] [TH#N]`: one that is verified is enough to answer it, and one open leaves it `open`. `Mitigated by …; the rest deferred` → both, the weaker state winning. A design's own threat (`Answers: —`) → its own Rule; `Returned` or `Not this design's` there is listed as the entry says.

**The reasons under `unanswered`**, each naming the entries it read as `[[<KEY>]] design.md [DT#N]`:
- `no design answers it` — no entry in scope names it; where a design in scope holds no `## Threat review` at all, the line says so, which is the declined review C left for D.
- `returned to the architect` — the entries that name it are `Returned to the architect`.
- `answered elsewhere — not verified on this run` — **an Epic run only**: the Epic's entry is `Not this design's — answered in [[<KEY>]] design.md`. That design is another Epic's, on another branch; the PRD run verifies it.
- `no design takes it` — the entries that name it are `Not this design's` with a reason class, or point at a design that holds no live `Mitigated` entry answering it. **On a PRD run this is how C's "answered in" is verified**: the named design is read, and a pointer at a design with no such entry is this reason, naming the pointer.

**The date** is compared with the date part of the run's `started_at` (`conformance.md:394`), never a second reading of the clock.

**Why derived and not asked:** each state has one owner outside this run — the Dev in `/design`, the PA in `/create-ard`, or `/implement` through a mitigation's own entry. A question here could only collect an acceptance (D5).

### D5. The walk: a mitigation is never accepted here

A **mitigation** is a `[DT#N]` Rule, or an `[AD#n]` Rule that a live, non-stale threat in scope names in its `Mitigated by`. A discrepancy on one goes to the walk as any discrepancy does, with two differences (maintainer question 1):

- **Its array has no *Accept as shipped*:** `["Fix the code", "Amend the document", "Cancel"]`; a PRD item with a Dev entry, `["Confirm Dev's decision — <decision>", "<the other decision>", "Cancel"]`. The question's text names each threat the mitigation answers and says that only the architect accepts a risk, in the model, with `/product-workflows:create-ard <KEY>`. A free-text answer that would accept is normalised into no option and the question is asked again, as `/design` does (`design.md:528`).
- **It is asked on its own, never in a cluster**, so a cluster's *Accept — all* cannot reach it. An item with a Dev entry is already asked alone (`conformance.md:276`).

*Fix the code* is today's follow-up to `/dev-workflows:implement`, on the Epic's branch while its pull request is open. *Amend the document* on an `[AD#n]` Rule is today's — a proposal on an Epic run, the `ard.md` note on a PRD run. **On a `[DT#N]` Rule it writes no note on either run**: the design is the Dev's, `/design` refuses a `- [ ]` in the section (`design-format.md:336`), and the entry's `effect:` and the Next step name `/dev-workflows:design <KEY>`, where the Dev rewords the Rule or returns the threat. The Dev decides on an Epic run (`proposed`) and the PE on a PRD run (`final`), as for every entry.

**An entry already decided *accept*** — recorded before D, or before a model named its decision — is carried forward and not asked again, as §5 has it (`conformance-format.md:117`). The threat it bears on reads `open — accepted in <KEY>/[DD#n], outside the threat model`, and stays so until the PA re-disposes the threat or the code satisfies the Rule.

**Why not keep *accept* and flag it:** a flag records that the rule was broken; removing the option keeps it. B's and C's maintainer answers both put acceptance in the model alone, and a `final` *accept* by the PE would outrank it in every reader of the record.

### D6. The record: one optional section, one new `document:` value

`dev-workflows:conformance-format` gains, with the builder fixing the wording:

- **`document: design.md`** on a `[DT#N]` entry and in the tracer's handoff, beside the four values of today.
- **`## Threats`**, optional, after `## Not checkable` and before `## Discrepancies`: a `- **Models read:**` line as `design-format` writes it, then one line per threat in scope and per own-threat entry — `- [[<KEY>]] [TH#N] <title> — <state>[ — <reason>][ — <the mitigations it rests on, each with its verdict or [DD#n]>]`. It is written only where the run read a model or a design holding `## Threat review`; left out otherwise, with no placeholder.
- **A header line `- **Threats:**`**, written under the same condition, after `Verdicts:`: the count per state, and each model or design the run could not read. **`Not traced:` still never names a `design.md` or a model**, so `/ready`'s test reads what it read before.
- **The section is rewritten whole on every run and carries nothing forward**: a state is derived, has no `[DD#n]`, and is never asked about. A `[DT#N]` requirement under `## Satisfied`, `## Unverified` or `## Discrepancies` follows §5's re-run rules unchanged; an entry whose `[DT#N]` is withdrawn is `requirement withdrawn`.
- **Titles and reasons are data, one line each** (format §4 and §9), and the section says so, as `design-format` section 15 does.

**The record's readers** (`conformance-format.md:126-134`; `.claude/rules/dev-workflows-conformance.md`). `/implement` reads `withdraws:` only. `/ready` reads header lines by name, `## Unverified` and each entry's `decision:`, `status:`, `flags:` and `lists:`: an open `fix-code` on a `[DT#N]` keeps the rung unreached exactly as any open fix does, and `## Threats` is not read. **Assumption:** `/document`, `/release-notes` and `workflows-core:source-truth` §7.8 match a claim to an entry "by exact identity only", `key`, `document` and id together (`plugins/workflows-core/references/source-truth.md:611`), and no documentation claim is drawn from a `design.md`, so a `[DT#N]` entry decides none; the builder confirms it in each and, where a reader enumerates the `document:` values, adds the fifth there.

### D7. Who is told, and how

Nothing but the mitigations' own follow-ups is queued. Each threat state reaches its owner three ways: the record's `## Threats`; the Final report, which lists every threat not `verified` or `accepted`; and the handoff's `body_facts`, one line per such threat, verbatim, as `/design` carries its returned entries.

The **Next step** adds, after today's lines and by role:

- **Dev → `/dev-workflows:design <KEY>`** for each design with a threat `unanswered — no design answers it`, and for a `[DT#N]` decided *Amend the document*.
- **PA → `/product-workflows:create-ard <KEY>`** for the model's folder, wherever a threat is `stale`, `review due`, `unreadable`, `unanswered — returned to the architect` or `unanswered — no design takes it`, and wherever one is `open` through an entry accepted outside the model. The line for a returned threat says that `/create-ard` does not yet take it in (RETURNED-INTAKE), so the architect reads the design's entry.
- **The scan** stays where it is: `/security-workflows:scan <EPIC-KEY>` after a clean Epic run. A mitigation's *Fix the code* comes first, since it is a `fix-code` decision like any other (`conformance.md:560-566`).

**D writes nothing into `threat-model.md`** — no `## Engineering review` note. The model is the architect's alone (`.claude/rules/threat-model.md:37`), and `/create-ard`'s refine rebuilds the draft from named sections (C's D7, cost (a)), so a note would be erased. The lineage table's sentence expecting one is corrected (D11).

### D8. When it runs

On both runs, with nothing reordered.

- **The Epic run, the Dev's, before the merge:** the Epic's design and the threats that land on the Epic (D2), traced at the ref `unit-branch` finds. This is where a declined review, a returned threat and an untested Rule surface while `/design` and `/implement` can still act on the Epic's branch.
- **The PRD run, the PE's, after every Epic has merged:** every model and every design under the PRD, on each default branch. It alone verifies `Not this design's — answered in …`, traces a Rule that bound only sibling components, and finds the PRD-level deferred threat no design took. An Epic record's `## Satisfied` `[DT#N]` lines feed the drift check as any line does; no threat state is read from an Epic record, since the PRD run derives its own.
- **Order:** inside `/conformance`, so before the scan on the Epic's branch and before `--verify-fixes` on the PRD, as the delivery sequence already has it.

### D9. Untrusted input, and what bounds an agent that must read code

D adds no agent. C's inert pattern — no tool, foreground only — cannot apply to an agent whose job is to read code, so D bounds the existing tracer by what it is handed and by what is done with its reply.

- **It is handed values, never paths into the specs repository.** A `[DT#N]` requirement is its key, its id, its Rule and its `test_hint`, each one line (format §9's *Every value is one line*), built by the run from labelled list items at the start of a line. The tracer is handed no model, no design, no threat's title or Threat line, and no register. Its read rule is unchanged: one repository, at one ref, by `git show`, `git grep` and `ls-tree` (`conformance-tracer.md:13`).
- **Labels are checked.** A section whose `### <key> <id>` heading is not, whole, a requirement the run routed to that tracer is dropped and counted in the report by number, never by its text.
- **Format §9's backstop runs on every `[DT#N]` section** before any of its text is shown or written — `shipped`, `evidence`, `test`, `reason`, and each notice line: a value holding a `SEC#n` id or a register path the handoff did not carry is withheld, and that requirement is *unverified*, its line saying why in the run's words. §9's text names two commands today and gains the third.
- **The orchestrator reads every satisfied mitigation itself.** Phase 3 re-checks a `satisfied` verdict on a mitigation — a `[DT#N]` Rule or a joined `[AD#n]` Rule — at each evidence location and at the `test:` location, as it re-checks a discrepancy today, and one it cannot confirm is *unverified*. A false `satisfied` is the one error that turns a threat `verified`, and today's re-check reads a `satisfied` only where it cites nothing (`conformance.md:251-253`). This is the bound that does not depend on the tracer obeying its prompt.
- **Foreground only does not carry over.** It was a property of the two no-tool agents, whose tools a background subagent is refused (`.claude/rules/threat-model.md:36`). The tracers keep their dispatch.
- **In the orchestrator**, a model's and a section's field text is data (format §4); a marker counts only as its own list item at the start of a line; an `Answers` is resolved, whole, against the threats of the models the run read; a `[[<KEY>]]` against the folders the run placed; a pair against the inventory; and a state line names a threat by its `ref` and title, each one line.

**What this does not give:** the tracer can still open a file outside its repository. C's guarantee was structural and D's is not; the handoff, the label check, the backstop and the orchestrator's own read are what stand in for it. A tracer with no file tool cannot trace.

### D10. No regression

- **The trigger is the artifact.** Where no file stands at a known model path and no design the run reads holds `## Threat review`, the run loads no threat-model reference, prints no `Threats:` line, hands the tracers today's input, asks today's arrays, and writes a record with no `## Threats` and no `Threats:` header line.
- **A model with no design section, or the reverse,** runs the half that exists.
- **A fallback** — the gate's, no ARD, no set, no §10 — prints its one line and leaves every non-threat requirement traced as today. No fallback stops a run.
- **An `[AD#n]` Rule no in-scope threat names** keeps the four-option array. The narrower array reaches only a requirement a model the run read names.
- **Fixtures.** A conformance transcript or selftest for each of: no model and no section (record and handoff byte-equal to today's); a design whose review was declined with one applicable deferred threat (`unanswered — no design answers it` on the Epic run — C's expectation); a returned threat; a `Mitigated` entry whose test is missing (`partial`); a model the gate falls back on.

### D11. Every site the change touches

- **`phase-handoff` — GIT-G1's file; the edits are listed under *The GIT-G1 edits* below.**
- **Claim sweep, three subjects, each by its subject and never by one site's wording.** *The model's readers*: the format's opening and §8 (`threat-model-format.md:6-7`, `:125-126`), `.claude/rules/threat-model.md`'s authority paragraph and invariant 5, the §4.0 register row, `/create-ard`'s page, `lineage-kinds.json:141`, roadmap row D and the feature-gaps review's SEC-G2 entries. *What `/conformance` does with a `design.md`*: `conformance.md:72`, `:110` and `:396`, `conformance-format.md:57` and `:74`, the handoff file, `/conformance`'s page (`plugins/dev-workflows/docs/commands/conformance.md:53`), and `phase-handoff`'s §4.1 clause. *What C said D would do*: `design.md` and `design-format` wherever they name security conformance. Each counted before and after, as refinement 7 has it.
- **`dev-workflows`:** `conformance.md` (Phases 1, 2, 3, 4, 5, 6, 7 and its invariants), `conformance-format.md`, `agents/conformance-tracer.md` and its handoff file, and their pages. No agent is added, so no count moves.
- **`workflows-core`:** `threat-model-format` (§10, the readers, §9's list of commands), `phase-handoff` and its generated parts, `lineage-kinds.json`'s `_source` text, the family map and reference pages.
- **Rules files:** `.claude/rules/threat-model.md` gains `conformance.md`, `conformance-format.md`, the tracer and its handoff file in `paths:`, a fifth reader in invariant 5 with its expiry sentence removed, the §10 pair invariant, and "the architect's alone" widened to `/conformance`; `.claude/rules/dev-workflows-conformance.md` gains the map line's new steps and `## Threats` among the record's fields; `.claude/rules/workflows-core-handoff.md` wherever it counts §3.7's callers.
- **Not touched:** `specs-repo-git` and its bounded write authority (the record is a deliverable on `conformance/`, as today); `check-id-grammar.sh` (no new prefix); `pre-lint`; `/design`; `/create-ard`; `/ready`; `register.py`; `scan.md`.
- **Versions and coupling.** `workflows-core` minor and `dev-workflows` minor. A patch, pages only, for each of `product-workflows`, `docs-workflows` and `security-workflows` whose pages the readers sweep changes — and a real `docs-workflows` patch only if D6's assumption fails. One coupling bullet: **a newer `dev-workflows` beside an older `workflows-core`** finds no §10 and no §3.4 row, so `/conformance` reads no model and says so, tracing the `[DT#N]` Rules alone — update `workflows-core` with it. The reverse breaks nothing: an older `/conformance` reads no model, and an older `/design` never read §10. An older `docs-workflows` reading a record with `[DT#N]` entries is D6's assumption.

## The GIT-G1 edits

`specs-preflight` and `commit-artifacts` are unchanged: `/conformance` runs both today, D adds no path and no branch prefix, and `specs-repo-git` takes no edit. `phase-handoff` takes **two rows and two sentences**, each needing the maintainer's named approval:

1. **§3.4, one new row** — `/dev-workflows:conformance` | each `threat-model.md` at its known paths, only where its ARD resolution returned `found` | **falls back** on `absent` as on every stopping row (§3.7): no model is read at that path and one line names the path and the row.
2. **§3.7, *Four callers read a stopping row without stopping*** (`:383`) — five, with `/conformance`'s site and its reason added before the closing "No other caller may take any of these exceptions".
3. **§4.0, the `threat-model.md` register row** (`:416`) — "named in §3.4's `/design` row" becomes two rows, and `/dev-workflows:conformance` joins the readers before "No other command reads it as a threat model". Its class stays *gated*, and "No array moves" stays true: both rows fall back.
4. **§4.1, the *gated — falling back* sentence** (`:532`) — "`threat-model.md`, whose one row has `/dev-workflows:design` read no model…" becomes two rows; "`design.md`, … left out of what `/dev-workflows:conformance` traces" is rewritten, since D makes it false; and the closing list of what each fallback does with an un-landed copy gains `/conformance`'s.

**Unchanged because both rows fall back at a §3.7 site:** the *gated* row's "save for an artifact whose every row is a site §3.7 names … `threat-model.md` today" (`:401`), *Row F is the next phase's reading only where …* (`:536`), and `/create-ard`'s choice of consent array. Had `/conformance` stopped on a stopping row, all three would move, and `/create-ard`'s array with them. The phase-handoff register rows that change are therefore the model's alone; `_conformance.md`'s row (`:417`) and `design.md`'s keep their class.

## What is left to the builder

The step numbers; the wording of §10, of `## Threats` and of the `Threats:` lines; whether a `[DT#N]` is routed by its Where's repository rather than as any requirement of its unit; how the inventory records an ARD file (D3's assumption); the three readers' sentences (D6's assumption); whether the Final report groups threat lines by owner; fixtures and selftests.

## Risks

- **`conformance.md` is 111 KB and grows.** The threat steps cite the format and `conformance-format` for detail; the builder measures the command's load before and after.
- **A threat reads `verified` while the attack still works.** D traces the Rule, not the threat. The record says "its mitigations are carried out", the pages say what that does not claim, and the scan is the check on the code.
- **The narrower array blocks a team that truly wants to ship.** The way through is one `/create-ard` run by the PA, which today cannot re-dispose a live, non-stale deferred threat (RETURNED-INTAKE). Until that lands, an `[AD#n]` mitigation the team will not build stays `open`; it stops no merge and no handoff.
- **Two statements of the applicable rule**, `/design`'s and §10: an invariant names the pair, and a later release moves `/design` onto §10.
- **The tracer is not inert** (D9): the orchestrator's read of every satisfied mitigation is the compensating control, and it costs one read per mitigation per run.
- **A falling-back gate hides a model in flux**: one line says so, and the header's `Threats:` line records each model not read, so a clean-looking record is never silent about it.

## Roadmap-row update

Row D of `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md` gains, when D lands: *Built as SEC-G2 D:* `docs/superpowers/specs/2026-11-15-sec-g2-d-security-conformance-design.md`, in the `workflows-core`, `dev-workflows` and page-patch versions the build releases — as a dimension of `/dev-workflows:conformance`, not a command of `security-workflows`. The feature-gaps review's SEC-G2 row and section (`docs/superpowers/reviews/2026-10-26-feature-gaps-review.md:23`, `:97`) are resolved by the same versions, and RETURNED-INTAKE stays open in `docs/superpowers/to-fix.md`.

## Questions for the maintainer

Ranked; each with the recommended answer the decisions above assume.

1. **May a discrepancy on a mitigation be accepted in `/conformance`'s walk?** Recommended: **no** — the array drops *Accept as shipped* for a `[DT#N]` Rule and for an `[AD#n]` Rule a live threat names; acceptance stays the PA's, in the model (D5). The alternative keeps the option and marks the threat `open — accepted outside the model`, which lets a Dev's `proposed` or a PE's `final` acceptance stand in every reader of the record.
2. **How is the model read: through a falling-back gate, or from the default branch with no gate?** Recommended: **the gate**, as C's D2 chose for `/design` — four `phase-handoff` edits (two rows, two sentences). The alternative reads `git show <default-ref>:…/threat-model.md`, as `/ready` reads the PRD record: one `phase-handoff` edit (the register row's reader claim), no repair offer and no working-tree read, but a consumer that runs no `require-on-main`, which C rejected for `/design` on the hard constraint.
3. **Does a threat that is `open`, `unanswered` or `review due` keep a PRD off `/ready`'s optional *Delivery verified* rung?** Recommended: **not in D** — `/ready` is unchanged, an open `fix-code` on a mitigation already keeps the rung unreached, and a threat only the PA can close would otherwise make the model a prerequisite of a rung that today reads delivery alone. The alternative has `/ready` read the new `Threats:` header line as a seventh condition.
4. **Is the dimension automatic wherever a model or a `## Threat review` exists, or offered as C's review is?** Recommended: **automatic** (D1). The alternative asks once per run, and a declined run records `Threats: not traced — declined`, leaving the mitigations out of the record.

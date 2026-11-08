# GIT-G1 — one shared implementation of the specs-repo git procedures

**Date:** 2026-11-08. **Status:** design, for approval. **Track:** GIT-G1 in `docs/superpowers/reviews/2026-10-26-fix-batches.md` § Design tracks (merged gaps CORE-G1, SCR-G1). **Fixes:** PR10 in `docs/superpowers/to-fix.md`. **Evidence:** `2026-11-08-git-g1-evidence/` (the contract and three audits this design argues from; its README says what each holds).

## 1. Intent

Every command that writes into the specs repository carries its own prose around three shared git procedures:

- **start** — `workflows-core:specs-repo-git`'s `specs-preflight`;
- **end** — its `commit-artifacts`, the terminal commit, and the rule for what a stopped run takes (§5.3);
- **handover** — `workflows-core:phase-handoff`'s `handoff-to-main` (branch, commit, push, pull request) with its consent choice and outcome line, plus the gates commands call around it: `require-on-main` and `branch-check`.

The procedures themselves already live once, in two references. What repeats is each command's wrapper around every call: when to call it, what to pass, what to do with what comes back, its own list of things never to do, where the outcome line goes, and what a stop does. **The maintainer's reason for this track is maintenance**, in their words: the same procedures repeat across every command, so the same bug or improvement has to be made N times, and the copies drift — two commands were found handing over differently with no reason to differ. Lower cost per run (PR10) and fewer agent mistakes are welcome side effects, not the goal.

**Measured** (evidence, and `contract.md` §7):

- 36 commands call these procedures; 35 run both the preflight and `commit-artifacts` (`/docs-serve` runs neither, by design).
- Paragraphs that mention them total about 770 KB of the 4.2 MB of command text, roughly 18% — an upper bound, since many of those paragraphs carry other content too.
- The end-of-run commit step: in the 15 commands a filter matched, no two copies are even 85% alike; they range from 0.3 KB to 15 KB.
- The handover phase runs 0.4–12 KB per command, of which the shared part is a few hundred bytes; the rest is command-specific work interleaved with it.
- The consent choice is already uniform: three deliberate variants, from one table in `phase-handoff` §4.0/§4.3.
- `specs-repo-git.md` is 159 KB and read whole twice per run, at the start and at the end (PR10); `phase-handoff.md` is 183 KB, of which a command reads one generated entry file per entry point.
- The audits (`audit-A/B/C.md`) classed every departure of every command from the standard call: **R** 199 (variations the references define), **P** 73 (purposeful, with a stated reason), **D** 55 (drift), **U** 19 (unclear). The latent bugs among the D items were fixed in batch B36.

## 2. Goals, non-goals, anti-goals

**Goals**

1. **One implementation of each procedure**, reused by every command: a fix or an improvement lands in one place.
2. **Commands get smaller and simpler.** Each keeps one call at the start with its keys, one at the end, a handover call with its parameters, and only the work that is genuinely its own.
3. **No command gets worse.** Every R and P variation the audits found is supported by the shared step; a command whose difference cannot be expressed as an option is prepared first (§6).
4. **Deterministic and tested.** The mechanical git work is a script with a selftest, run in CI like the family's other scripts.
5. **The 159 KB reference stops being executed text.** It becomes the contract a maintainer reads — what the shared step guarantees and why — and no agent reads it whole to run a command.

**Non-goals**

- Porting to the internal Claude and Copilot editions. That is a later E-item, after the current to-do list (the maintainer's decision, 2026-11-08). The Copilot edition can run Python, so nothing here rules it out.
- Changing what the procedures do: the bounded paths (§2.1), the branch rules (§2.2, §3.5), the consent classes and arrays (§4.0, §4.3), session-branch mode (§8) and the outcome-line forms (§6, §4.1) keep their meaning. This track moves who executes them, not their rules. A behaviour change found necessary on the way is a separate, named decision.
- Changing each command's own pre-handoff work (stamping lineage, consumption tracking, archives).
- **The rest of the end-of-run sequence** — session maintenance, feedback, follow-ups, the cost entry and the resume pointer. It repeats across the commands as much as the git steps do, and it is the next track after this one (TAIL-G1 in `docs/superpowers/to-fix.md`), reusing this track's skill pattern; it is not kept duplicated. It is separate because its members are mostly agent work with command-specific inputs (the report, the follow-up items, the cost labels) that a script cannot do, because each already has its own shared reference, and because the commit, always the sequence's last step, is a fixed point it builds on (maintainer, 2026-11-08).

**Anti-goals** — a result that works and still fails the track:

- A command that loses a deliberate behaviour because the shared step had no option for it.
- A script that asks the user anything. Questions stay in the main conversation, as `AskUserQuestion` calls with their `choices:` arrays presented verbatim (`workflows-core:escalation-rules` §0).
- A shared step that runs implicitly, or a gate that forces every command to call it: `/docs-serve` runs none of this, and an `--inline` run (`/docs-brand` under `/docs-init`) opens no state of its own (audit-B N12, N13).
- A key parsed out of free text, a branch name or a path. Keys come resolved from the caller (`CLAUDE.md` § Editing discipline, *Resolve an identifier against a known set*).
- One copy of the wrapper replaced by a new copy per command — a call site that restates the shared step's rules is the problem this track exists to remove.

## 3. Constraints

- **The plugin-root boundary.** `${CLAUDE_PLUGIN_ROOT}` resolves to the plugin that holds the reading file, so a `product-workflows` command cannot call a `workflows-core` script by path (`CLAUDE.md` § Internal reference convention). A **skill** crosses that boundary: inside a skill body, `${CLAUDE_PLUGIN_ROOT}` is the skill's own plugin, as the `reference` loader and `model-routing` already use. Agents cross it too, but see §4.
- **Python 3, standard library only**, like `session-branch.py`, `lineage.py` and `bounded.py`. `commit-artifacts` already calls `session-branch.py` for its replay and session-branch mode, so Python is already required wherever these procedures run.
- **Bounded runs.** A git call that can hang runs under `workflows-core:bounded-run`'s rules (`bounded.py`); the push replay needs its own 420-second Bash call, and one preflight can reach a replay once per branch (`contract.md` §8), which a single script call cannot honour as one call — the design must split it or bound it per branch.
- **Questions belong to the conversation.** Three questions in these procedures need the user's answer and cannot be scripted (`contract.md` §5, §8): the handover's consent choice (§4.3), `require-on-main` row C's repair offer, and `branch-check` §6.2's reuse question. Everything else a procedure prints is a notice, which a script can emit.
- **State that lives only in the conversation today** — the last `Environment:` line, the `specs_git: blocked|misrooted` flags, the guard notice to repeat at the end, "once per run" markers, `inputs_read`, `session_branch_created` — must move somewhere a compaction cannot lose it, scoped to one invocation and safe for a complete nested run started after the parent's commit (`/brd-split`'s *Ground now* starting `/prd-ground`, audit-C N9).
- **The gates stay green**: `check-docs.sh` (checks 16, 22–29 among them), `reference-parts.py` (`check-citations`, `check-questions`, `check-branch-check`, `check-parts`), `validate-catalog.py` and the mermaid gate; `.github/workflows/validate-catalog.yml` gains the new script's selftest. A rules file stays under 20,000 characters and `CLAUDE.md` under 36,000.
- **Prose rules**: never hard-wrap prose in new text (`workflows-core:prose-formatting`); cross-plugin docs links are forbidden; a `workflows-core` reference change gets a coupling bullet (`.claude/rules/plugin-updates-coupling.md`); `plugins/workflows-core/reference-parts/` is generated, never edited.

## 4. The shape — decided

**One script and one skill, both in `workflows-core`.**

- **The script** does the deterministic git work of all five entry points. It prints one JSON object per call and exits 2 when it cannot run, as `session-branch.py` and `register.py` do. It carries a selftest that builds real repositories in a temporary directory; B01's merged-branch cases (GIT-B1, GIT-B2) are its first tests.
- **The skill** is the only way a command reaches the script. It resolves `${CLAUDE_PLUGIN_ROOT}` to `workflows-core`, runs the script, and holds the little that needs judgment: which notice or outcome line to print from the script's fields, which consent array to present (the class the caller names), and when to stop. A command calls it with an entry point and its parameters, the way it calls the `reference` loader today.
- **Subagents were considered and rejected**: a subagent would still read the long prose on every run, costs a model call each time, and cannot ask the user mid-run, which the consent question needs.

**What a command keeps:** a start call with its run key set (resolved by the command, never parsed), an end call, a handover call with `prefix`, `feature_folder`, `deliverable_paths`, `title`, `body_facts`, `inputs_read` and the consent class, the `require-on-main`/`branch-check` calls where it gates, and its own work. Its *Ending early* paragraph shrinks to naming which tail profile each stop takes (§5.3); its tail phase keeps its other members until TAIL-G1.

**What the references become:** `specs-repo-git.md` and `phase-handoff.md` keep the contract — what each entry point guarantees, its inputs and outputs, its variation points and the reasons behind its rules — and lose the step-by-step git procedure the script now holds. No command reads either whole to run; the skill's own text is what an agent reads.

## 5. What the shared step must support

These come from the contract's variation points (V-ids) and the audits' new options (N-ids, per audit). A builder may merge or rename them; none may be dropped without showing the command that needed it no longer does.

### 5.1 Start (`specs-preflight`)

- An explicit run key set from the caller, with the keyless form, the Epic-plus-parent form (V1.3), and a set built before address resolution (V1.1).
- Run before or after address resolution, and none on a stop before it (V1.1, V1.2).
- Outputs as fields: `<default>`, `<default-ref>`, `remote` present, read-only mount, the `specs_git` flag and which setter set it, `session_branch` and `session_branch_created`, the branch B2 found merged and left, the branch B4 moved off (audit-A §2 items 1, 4).
- `register_rebuild` passed through (V1.13; `/scan` alone).
- A direct `/implement` run inside the specs repository: G2's notice variant and the §8.3 `lift`/`put-back` around its own branch and commit (V1.10, V4.4); session-branch `commit`, `lift` and `put-back` callable by a command (audit-A §2 item 15).
- Standalone primitives a command can call: `mode` before any preflight (audit-A §2 item 2), `branch-merged` for a named branch or a recorded commit, `branch-key`, the §2.1 ARTIFACT/OTHER classifier over porcelain `-z`, `owner-repo` for any repository path (audit-A §2 items 3, 5; audit-C N6, N7; audit-B N7).
- The start call prints two lines as script output, each at the point it fires, for the run to copy verbatim: the session branch's creation line (`specs-repo-git` §3.4, `specs-repo-git.md:442`), and each guard's four-part §5 notice at detection. Three live runs dropped them (LC31, runs R1, R2, S5a and S5b of `docs/superpowers/verification/2026-11-04-live-checks.md`) because each rested on the run remembering a rule it had read earlier.

### 5.2 Handover (`handoff-to-main`, the consent choice, the outcome line)

- The consent class named by the caller, gated (stopping or falling back), advisory or unread (V3.1–V3.4), re-selected per run where the command edits a copy already on the default branch.
- The push-target probe and the one line above the array, always (B36 made every producer name it; the shared step makes it impossible to skip).
- A caller slot for lines printed above the flag / no-remote line (`/ready`, `/conformance`, `/epics`, `/release-notes`; audit-A §2 item 6, audit-B N1, audit-C N2).
- A caller-side skip of the offer with a not-offered line (`/frames`; audit-A item 7 — reconcile with `phase-handoff` §4.1 first), and a "no offer: <reason>" result (audit-B N2).
- A hook after a declining answer, and a call on options 2 and 3 too, so the shared step prints the decline row and records the declined paths (audit-A item 8, audit-B N10).
- Several offers per run, each labelled `Phase handoff (<the handoff>): …` (`/brd-reconcile`, and the *Next Epic* loops of `/design` and `/specify`; `phase-handoff` §4.1 as B36 left it).
- Prepare, then execute later on the carried answer: a call that runs the gate and the probe and asks nothing, returning the gate verdict and `remote`, and a later call that executes on the answer the command carried (`/brd-package`, consent in Phase 7, execution in Phase 9; audit-C N3). A rule for an answered offer whose execution never comes (a stop between them).
- The outcome as fields as well as the rendered line: the §4.1 row, the nothing-to-commit location, the branch, the pull request, committed or not, the unaccounted paths (audit-A item 10, audit-B N6, audit-C N1).
- `inputs_read` required, or derived from a record the shared state keeps (audit-B N14); `prefix`-less producers (`/vuln`, `/scan`, keyed `/document`, `/implement`; V5.2) and keyless ones (`kb/`; V3.6).
- `phase-handoff` §2.7.1's pull-request template fill and `specs-repo-git` §4 step 4's pathspec commit stay usable for docs-repository commits, which `/docs-init`, `/docs-brand` and `/document` borrow today (audit-B N9).

### 5.3 End (`commit-artifacts` and the stopped run's tail)

- The commit call stays separate from the tail's other members, so a command runs its own actions between `resume.md` and the commit (`/implement`'s run-state removal, `/scan`'s `$run_dir`, `/upgrade`'s and `/vuln`'s file removal; audit-A item 13, audit-B N11).
- Named tail profiles a command assigns to each stop, rather than prose. In this track a profile is a name, defined once in `specs-repo-git` §4 and cited by each command's *Ending early*; the skill runs only the commit, and the other members stay in each command's tail phase until TAIL-G1 makes the skill run them. The profiles: full; full but with no handoff offered first (`/brd-proposal`'s operator ends); maintenance, feedback, cost and commit without `resume.md` (`/prd-ground`'s Phase 11); the refusal tail (cost and commit); commit only, with no cost member at all (`/harvest-decisions`, `/promote-decisions`, `/upgrade`, `/vuln`; audit-C N8, audit-A item 12); and none (`PRD_GROUND_TYPED_ONLY`, and the docs commands' stops before a documentation repository resolves; `specs-repo-git` §4).
- The commit key: the one key the run addressed (`specs-repo-git` §4 step 4, as B36 left it), passed explicitly.
- The outcome as fields as well as the line: row, sha7, replay moves (audit-A item 14); the rendered line returned for a command that prints its report after the tail, and printable in place for one that prints it first (audit-B C4).
- The cede-control exception: the commit before a hand-off to another skill or an open-ended stretch (V2.1; `/prompt-brainstorm`, `/prompt-grill-me`, `/brd-split`'s *Ground now*).

### 5.4 Gates (`require-on-main`, `branch-check`)

- `require-on-main` returns its result as fields — the row, the files, the B′ remedy with its re-run clause separable — instead of printing a stop, so a caller can order two gates, aggregate a sweep, or build its own stop text (audit-B N4, audit-C N4); a classify-only mode that does not offer row C's repair (audit-B N5); and whether row C's repair was taken or declined, with *Cancel*'s return defined (audit-C N5).
- Stop wording that names `$SPECS_PATH` for a caller standing in a code repository (`/implement`; audit-A item 11).
- `branch-check` with `reuse: later` (V5.1), with no prefix for a producer that opts out (audit-B N8), and none for a folder the run is about to create (`/idea`, `/create-prd`'s `status: absent`).
- Later `require-on-main` calls in `/ready`, `/epics`, `/specify` Step A, `/brd-proposal` and `/implement` (V4.1), and callers that read a stop without stopping (V4.2).
- A lookup of `phase-handoff` §4.0's register of declared artifacts (audit-C N10).

### 5.5 State

One state record per invocation, holding what today lives in the conversation (§3), written by the start call, read and updated by the later calls, and gone when the run ends. It must:

- outlive `/implement`'s `run-state.py remove`, which runs before the commit, or hand its fields to the commit explicitly (audit-A §3);
- stay invisible to `commit-artifacts`' staging and to the session-file shapes (§2.1);
- never leak a parent run's state into a nested run (audit-C N9);
- never be opened by an `--inline` run (audit-B N12);
- hold `inputs_read`: the skill gains a call that adds the files a phase read to the record, made once at the end of each phase rather than per read, with the reads of an agent the phase dispatched taken from the agent's return; each command's *Record what the run reads* sentence (batch B36) points at that call. A transcript reader and a hook on Read were considered and refused: the first misses reads made through Bash, and the second runs implicitly, which §2 rules out.

## 6. Commands to prepare first

Two commands cannot switch as they stand; each needs a change of its own, which may be a batch before the part that switches it:

- **`/brd-package`** asks for consent in Phase 7, then runs its own route question and writes its note, prompt and bundle, and executes the handover in Phase 9 on the carried answer. It needs §5.2's prepare-then-execute, and a rule for what line an answered offer prints when a Phase 8 stop comes between (audit-C §3).
- **`/implement`** keeps its specs-repo state partly in `run-state.py` (`specs_git`, `session_branch_created`, `specs_merged_branch`, and since B36 `inputs_read`) and partly in the conversation, and removes its run-state file before the commit. Settle which record owns each field, and make the commit's inputs survive the removal (audit-A §3).

**Rule gaps the references leave open**, each settled in the design-questions step of the part that needs it: (i) whether `phase-handoff` §4.1 gains a *Not offered* row, which `/frames` prints today and §4.1 says no run prints, and whether §5.2's "no offer: <reason>" prints it — Part 3; (ii) what line an answered offer prints when a stop comes before its execution — before `/brd-package`'s preparation; (iii) what `require-on-main` returns when the user cancels row C's repair — Part 3; (iv) whether consent option 3 gets the "remains uncommitted, as you asked" append that `specs-repo-git` gives a decline — Part 2.

No other command needs restructuring; each needs options from §5 (audit verdicts: `needs option` for most, `ready` for `/feedback`, `/prompt`, `/diagnose-session`, `/prd-proposal`, `/brd-intake`, `/update-prd`).

## 7. Order of delivery

Three parts, each shipped and switched on its own, in this order:

1. **The script's core**, with its selftest: the §2.1 classifier, `branch-merged`, `branch-key`, `push-scope`, `owner-repo`, `mode`. No command changes yet; `specs-repo-git` cites the script where it now spells these out. B01's GIT-B1 and GIT-B2 cases are the first tests.
2. **Start and end** on that core: the preflight, the commit with its push and replay (bounded per branch), session-branch integration, the state record, the tail profiles; the skill's start and end entry points. All 35 commands switch their start and end calls; `specs-repo-git` becomes the contract. `/implement`'s preparation lands before or with this part.
3. **The handover and the gates**: `handoff-to-main`, the consent step, `require-on-main`, `branch-check`, and the skill's entry points for them. The producers switch; `phase-handoff` becomes the contract. `/brd-package`'s preparation lands before or with this part.

**A part ships as several batches** (maintainer, 2026-11-08): the script and the skill first, with the references still executable, then the commands in groups — a plugin or a command family per batch. Each batch goes through the family's normal cycle: design questions, build, gates, an independent review, one fix pass, pull request, CI. While a part is in flight, `main` has some commands on the shared step and others on the prose; both follow the same rules, and the script is tested against the reference, so the mix differs in where the text lives, not in what a run does. A reference drops its step-by-step text only in the batch that switches the part's last command. **The window stays days, not weeks**: a part's batches run back to back, with no other work in between, each one a few hours from design questions to pull request.

## 8. How we know it worked

- **Drift has nowhere to live:** every command's start, end and handover is a call to the skill with parameters; no call site restates a rule of the shared step. The builder decides whether a gate pins that (e.g. a `check-docs.sh` check or a `reference-parts.py` check over the call sites) — the maintainer earlier preferred no new gate for a docs-only heading (DQP-G4), but a call-site shape is the kind of thing a gate holds well.
- **PR10 closes:** a run no longer reads `specs-repo-git.md` or a `phase-handoff` entry file to run its start, end or handover; the skill's text is what it reads. Measure the bytes an agent reads for each before and after.
- **Commands shrink:** re-run the measurement in §1 (bytes of command text about these procedures) before and after each part.
- **Nothing got worse:** every R and P row in the three audits is accounted for — supported by an option, or retired with a reason.

## 9. Left to the builder

- The script's and the skill's names, the script's subcommand surface and JSON fields, and whether it is one script or a few that share a module — within §4.
- Where the state record lives (the specs repository's git directory, like `/implement`'s run-state file in the code repository's, is the obvious candidate) and its format.
- How the push replay's 420-second bound and the once-per-branch rule map onto calls.
- How much of `session-branch.py` the new script reuses, imports or absorbs.
- Whether §8's call-site gate is built, and its shape.
- The wording of the skill's entry points and of the slimmed references, under the family's prose rules.

## 10. Rulings made in conversation

- **Maintenance is the goal**; cost and reliability are benefits (maintainer, 2026-11-08).
- **Script plus skill**, not subagents (proposed by the lead, confirmed by the maintainer).
- **All three procedures** — start, end and handover — are in scope, the handover because that is where the drift was seen (maintainer).
- **The internal editions wait** until the current to-do list is done (maintainer).
- **The end step is the commit and the stop rules; the rest of the end-of-run sequence is the next track, TAIL-G1** (lead's recommendation, accepted by the maintainer).
- **A part ships as several batches, back to back, `main` mixed for days** (maintainer).
- **`inputs_read` is kept by a per-phase skill call** (lead's call; §5.5).
- **The four rule gaps are settled in the part that needs each** (lead's call; §6).
- **The differences between commands were audited before the design**, so a deliberate one becomes an option rather than a regression (maintainer's request); the latent bugs the audit found were fixed first, in B36, under the bugs-first policy.

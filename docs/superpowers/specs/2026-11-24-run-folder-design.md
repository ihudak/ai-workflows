# Run folder: a command interrupted mid-run continues where it stopped

Date: 2026-11-24. Status: approach and outline approved by the user in conversation; revised after a builder check (it found `/implement`'s existing resume, D10's session guard, D6a/D6b, D2's identity hash); D7a is the user's ruling on plugin updates mid-run.

## Background

A `/product-workflows:prd-ground` run on a BRD slice of 294 requirements across 7 repositories planned about 2,000 findings, 70 `code-grounder` dispatches and 168 verifier dispatches. It ran for hours over two days in a sandbox container. When the container restarted, the work was lost: the command keeps every agent's result only in the conversation until Phase 8 writes `grounding/*.md`, so nothing on disk said what had been done. The agent had improvised a folder of its own for the dispatch inputs, the results and a progress log (`state.md`), twice in a place that did not survive (`~/.cache`, then the `/workspace` umbrella), and the run was recovered only by replaying session transcripts.

The container side is fixed separately (ai-containers keeps the group's `/var/tmp`, `~/.cache` and `~/.local/state` across restarts, with `TMPDIR` on a per-container folder in `/var/tmp`). What remains is in this repository: **no command says where a run keeps its working state, or how a new session picks it up.**

A survey of the 28 commands that dispatch agents found:

- **`/prd-ground`** is the most exposed: Phases 5–7 (grounders, then verifiers, 100+ dispatches on a large slice) live only in the conversation until Phase 8.
- **`/document`, `/release-notes`, `/epics`, `/conformance`, `/upgrade`, `/vuln`, `/security-workflows:scan`** lose work mid-run: code, branches and pull requests survive, but the approved plan, scan and review results, which components or CVEs are done, and the user's answers at the approval points do not. Their `mktemp` handoff files are removed at the end of a run, and on a host `/tmp` does not survive a reboot.
- **`/brd-interview`, `/brd-intake`, `/brd-split`** are mostly safe: they write each round to the specs repository as they go.
- **`/specify` and `/design`** keep the interview in `_session.md` / `_design-session.md`, but not their scans or review verdicts.
- **`/implement` already resumes** a stopped run (IMP-G5, `docs/superpowers/specs/2026-11-12-imp-g5-implement-resume-design.md`): `dev-workflows/scripts/run-state.py` keeps its state in the worktree's git directory, resumes at the step the run died in, proves the tree holds only the run's work, and stops a session another one has taken over. It meets this design's intent already and is left as it is.
- No other command keeps resumable run state. The durable stores are the specs repository, branches and pull requests, and `resume.md`.

## Intent

**A command interrupted mid-run — a system crash, a container restart, usage limits that force the user to stop for hours — can be started again on the same machine and continue: every agent that finished keeps its result, and the user is not asked again what they already answered.** Some work may be redone (an agent cut off mid-flight starts over); finished work is not.

This holds for every command, not only `/prd-ground`. The user put it as: "I don't want to run into a similar issue with `/implement` or something else."

## Goals

1. One mechanism, owned by `workflows-core`, that every command which dispatches an agent or asks the user to approve something uses the same way.
2. A finished agent's result survives a machine reboot and a container restart, and a resumed run reuses it **only when that agent's input is unchanged**.
3. The user's answers at approval points survive too, and are reused only while what they approved is unchanged.
4. On start, a command that finds its own unfinished run offers to resume it or start over.
5. Nothing is left behind by a run that finishes; an abandoned run's folder is removed after 30 days.

## Non-goals

- **Handing work between commands.** That stays the specs repository's job — committed, pushed, merged — as `workflows-core:phase-handoff` and `specs-repo-git` already require. The run folder lives and dies within one run of one command. `resume.md` (`workflows-core:session-hygiene` §1) is unchanged: it is the pointer between commands.
- **Continuing on another machine.** A run stopped on one machine (or in one container host's group) is not seen elsewhere; there it starts fresh. No syncing, no committing of run state.
- **Resuming an agent mid-flight.** An agent that was running when the session died is dispatched again.
- **Changing `/implement`'s resume.** IMP-G5 stays as it is, with its own script and state file; this design borrows two of its proven pieces (D10).
- **Replacing existing mechanisms.** `_session.md`, `_design-session.md`, `/brd-interview`'s rounds, `/brd-split`'s ledger, on-file idempotence (a re-run that skips what the specs repository already records) and Scope-to-N checkpoints all stay as they are.
- **Resuming the state of another tool's pipeline** (the Claude Security scan's own workflow run inside `/security-workflows:scan`). Only the command's own dispatches and gates are covered.

## Anti-goals

- **Never a command that fails because of its run folder.** If the folder cannot be made or written (no writable `$HOME`, a full disk), the run proceeds exactly as it does today, with one warning that it cannot be resumed.
- **Never a stale result reused.** A saved result whose input has changed in any way — a repository moved, a specs file edited by a colleague, different flags — is not reused. The one exception is a result the user explicitly chooses to keep after its agent's instructions changed (D7a), and the report says so.
- **Never a run that cannot finish.** A large run that hits usage limits, waits, and resumes under newer plugins must not be sent back to the start by every update: only what actually changed is redone, and a large redo is the user's choice (D7a).
- **Never a weaker blind verification.** `/prd-ground`'s verifiers must not be able to find the answers they verify in the run folder.
- **Never per-agent configuration.** The location comes from the XDG convention with a fixed fallback, the same on a host and in a container.

## Terms

- **Run.** One execution of one command, from its first start until it finishes or the user starts over. A resume continues the same run.
- **Run folder.** The directory holding one run's state.
- **Run key.** The name of a run's folder; the same invocation in a new session computes the same key.
- **Dispatch.** One agent invocation by the command's orchestrator.
- **Input.** Everything a dispatch hands its agent, written to a file in the run folder before the dispatch.
- **Fingerprint.** A hash of a dispatch's input (D7).
- **Result.** What the agent returned, saved in the run folder and recorded as complete.
- **Gate answer.** A user's answer at an approval point or question, with a fingerprint of what they were shown.
- **Progress log.** The run's append-only record of phases reached, dispatches reused or made, and gates answered.

## Approaches considered

- **(a) A place only.** Name the folder and tell the agent to keep its working files and a progress note there; on start, offer to continue from it. Small, but what is inside stays improvised, so a resume is only as good as the previous agent's notes, and a large run still overflows the conversation. Rejected by the user in favour of a defined layout.
- **(b) A defined layout, per command.** Each command gets its own resume design. Precise, but about ten separate designs in commands of 1,000–3,000 lines, each resuming in its own way, and the small commands stay uncovered.
- **(c) A defined layout, one shared mechanism** in `workflows-core`, which every command uses through the same entry points. **Chosen by the user**, for every command ("I don't want to run into a similar issue with `/implement` or something else"). One behaviour everywhere, and a new command gets it by following the reference; the cost is one careful rule for when a saved result can be reused (D7), and a real rewrite of `/prd-ground`, whose later phases must read results from files.

## Decisions

### Where and what

**D1 — Location.** `${XDG_STATE_HOME:-$HOME/.local/state}/ai-workflows/runs/<run-key>/`, mode 0700, on the machine that runs the command. In an ai-containers sandbox that is the group's `~/.local/state`, kept across container restarts; on a host it survives reboots. An empty `XDG_STATE_HOME` counts as unset; a relative one is ignored (the XDG specification requires absolute paths).

**D2 — Run key.** `<plugin>.<command>-<KEY>-<h>` for a keyed run (a run whose address resolves to a folder under `$SPECS_PATH/specifications/`), e.g. `product-workflows.prd-ground-MWC-001-01-3f9a2c`, and `<plugin>.<command>-<h>` for a keyless one (`/vuln`, `/upgrade`, `/docs-audit`, and the like). `<KEY>` is the resolved folder's key as `workflows-core:addressing` resolves it — never one parsed out of free text. `<h>` is a short hash of the run's identity: the specs repository (its `origin` URL, or its physical path where it has none), for a command whose run depends on where it is started (`/security-workflows:scan`, `/vuln`, `/upgrade`; not `/prd-ground`, which reads `$REPOS_PATH` and `$SPECS_PATH` and works the same from any directory, so a resume from another directory still finds its run) the working directory's repository root (or its physical path outside a repository), and, for a keyless run, the command's canonical arguments. `run.json` records the same identity in clear. The KEY alone is not enough: a command such as `/security-workflows:scan <KEY>` runs once per repository on the same KEY, and in an ai-containers sandbox the projects of one group share `~/.local/state` while each mounts its own specs repository at the same `/workspace/specs`. Without the hash, a run from repository B would be offered A's unfinished run, and *Start over* would delete it.

**D3 — Layout.** The builder fixes the exact names; the folder holds:
- `run.json` — the run's identity: command, arguments and flags as given, the resolved KEY, the identity D2 hashes, a run id, the plugin versions, start time, the owning session and its last write (D10);
- `progress.md` — the progress log, append-only, readable by a person;
- `inputs/` and `results/` — one input file and one result file per dispatch, named by a dispatch id the command chooses (phase, agent and item, e.g. `p5-code-grounder-backend-03`), never by position;
- `gates/` — gate answers;
- `scratch/` — any other file a later step of the same run reads (what `mktemp` held, D13).

**D4 — One script, called by path.** A `workflows-core` script, `run-folder.py`, does everything mechanical: compute the folder and key, create it, record and check the owning session (D10), fingerprint an input, look up and record results and gate answers, append to the log, list and prune runs, and remove a finished run. It is vendored byte-identical into every plugin that calls it and checked by CI, exactly as `bounded.py` is (`.github/workflows/validate-catalog.yml`, `.claude/rules/workflows-core-bounded-run.md`), and has a `--selftest` like the other scripts. The name is not `run-state.py`, which is `dev-workflows`' script for `/implement` (IMP-G5); `dev-workflows` ships both. A new reference, `workflows-core:run-folder`, is the single source of truth for the protocol and is cited by every command, never restated. *Builder's call:* the script's exact interface.

### The protocol

**D5 — Open, at run start.** Every covered command opens its run as its first step after its run key is known (after address resolution where that comes first), before any dispatch or gate:
- no folder → create it, write `run.json`, proceed;
- an unfinished run → show what it is (when it started, the arguments it ran with, the last phase logged, how many results are saved) and ask **Resume** / **Start over**, through `AskUserQuestion` per `workflows-core:escalation-rules` §0. Resume continues with the arguments typed now; where they differ from the stored ones the question shows both, and D7 redoes exactly the results the difference changes. *(Amended 2026-11-24 while planning Part 1: the first wording resumed with the stored arguments, which made a stop that names a flag to add — `/prd-ground`'s `PRD_GROUND_NEEDS_REBASELINE`, "re-run with --rebaseline" — impossible to resume.)* Start over deletes the folder and begins a new run;
- a keyless command also lists its own unfinished runs whose working directory is this one, so a user who does not remember the exact arguments is still offered them;
- **one question, never two.** A command that already asks a resume question of its own — `/specify` and `/design` from their session files, `/create-ard`'s refine-or-fresh, `/brd-interview`'s open round — keeps its question, adds the run folder's summary to it, and applies the answer to both: resuming resumes the run folder too, and a fresh start starts the run folder over. Asked separately, a user could resume the run folder's gate answers and scan results while discarding the session they came from. D5's own question is asked only where the command has none.

**D6 — Every dispatch.**
1. Write the input file (the full prompt the agent will get, or the file the prompt names).
2. Look it up. A recorded result with the same fingerprint (D7) is reused: log `reused <dispatch id>` and do not dispatch.
3. Otherwise dispatch. An agent whose tools include `Write` or `Bash` is handed a result path and writes its full result there, returning only a short receipt (status and counts), which keeps a large fan-out out of the orchestrator's context. Any other agent — the read-only reviewers — returns its result inline and the orchestrator saves it.
4. Record the result as complete. **A result file with no completion record is not a result**: a session that died between the agent's write and the record re-dispatches.

Parallel batches (`≤4 concurrent per Agent message`) apply the same steps per dispatch; a resumed batch dispatches only the members with no recorded result.

**D6a — A resume replays.** A resumed run walks its phases from the start. Steps that only read run again; each dispatch is looked up (D6 step 2), each gate takes its recorded answer (D8), and phase-level facts come from the log (D9). **Side effects are logged too**: a commit, a push, a pull request, a write into the specs or docs repository is logged as started, then as done. A done one is not repeated. A started one with no done entry is met by the command's own re-run handling where it has one (the specs-repo preflight, `workflows-core:phase-handoff`'s rows B and B′ for a run resuming on its own branch); where it has none, the run stops and asks.

**D6b — A dispatch that changes files.** A writer agent (`doc-writer`, `epic-writer`, `doc-fixer`, `review-fixer`, `test-writer`, `upgrade-executor`, `vuln-fixer`, and any other whose dispatch edits a tree or a file its input names) changes, by finishing, the very state its next input would be built from, so D7's comparison cannot find it. Its completion record therefore also stores what it wrote: the paths it changed and their content hashes, taken from a snapshot of its scope before and after the dispatch. On resume a writer's dispatch is looked up by its dispatch id against the input stored when it ran, and its result stands while what it wrote is still as it left it; the writer is not dispatched again. Where what it wrote has changed since, the run says what changed and asks (keep what is there, or redo the dispatch), never re-dispatching on a guess. This is IMP-G5's rule ("proof, not inference"), applied per dispatch.

**D7 — When a saved result may be reused.** Its fingerprint — a SHA-256 over the input file and every run-folder file it names — equals the new input's. That makes inputs carry their own staleness check, so **every input must name by version each external thing the agent reads**: a repository by its commit (`/prd-ground` already pins one per repository in Phase 3), a specs-repository or docs file by its blob or content hash, a diff by the run-folder file that holds it. An input that leaves an external read unversioned makes its result unsafe to reuse; the builder checks every covered dispatch for this and adds the missing versions to its input. Arguments and flags are part of the input where they change the agent's work.

**D7a — An agent whose instructions or model changed.** The fingerprint also covers the agent's own definition file (`plugins/<plugin>/agents/<agent>.md`) and the model the dispatch ran on. Nothing else in a plugin counts: a version bump, a change to a command, a skill, a reference or another agent redoes nothing. A shared reference the agent reads while it works (`grounding-verifier` reads `workflows-core:grounding-format`) can change its output too, and is deliberately left out — it changes so often that counting it would redo work at nearly every resume; that is a stated limit. On resume, the saved results whose agent file or model changed are counted:
- **10 or fewer in all** are redone without asking, and the log says why.
- **More than 10:** a question asked once both are known — the agent files at once, the models only where the command resolves them (`/prd-ground`: the end of Phase 2), so that is where the question stands *(amended 2026-11-24 while planning Part 1)* — says which agents changed and how many saved results each holds, and offers **Resume and redo them** / **Resume and keep them** / **Start over**. A run of hundreds of dispatches that waits out usage limits would otherwise never finish if each plugin update sent it back. *Keep* is logged, and the final report names the results written under older instructions.
- **A command's own invariant can withhold *keep*.** `/prd-ground`'s verification requires an Opus re-derivation (`.claude/rules/prd-ground-verification.md`), so a verifier result written on a cheaper model is always redone; one written on Opus may be kept under a session that is now on another model.

The threshold, 10, is the user's ruling in substance ("a small re-do is fine, hundreds of batches — ask"); the number is this document's call.

**D8 — Gates.** A gate answer is recorded with a fingerprint of what the user was shown (the plan file, the option list, the finding). On resume, the same gate with the same fingerprint takes the recorded answer and logs it instead of asking; a changed fingerprint (a regenerated plan, a new finding) asks again. An answer given as free text is recorded verbatim.

**D9 — Progress log.** Each phase start and end, each dispatch (made, reused, failed), each gate (asked, reused) and each stop is appended with a timestamp, by the script. The log is what D5 summarises and what a person reads to see where a run stood. It also records phase-level facts a later phase needs that are not a dispatch result (e.g. `/prd-ground`'s Phase 3 pins), so a resume does not recompute them differently.

**D10 — One live session per run.** Borrowed from IMP-G5 (§3.3 of its design), not a time window: an agent can run longer than any window, so a live run cannot be told from a dead one by age. `run.json` records the session that owns the run (`CLAUDE_CODE_SESSION_ID`, null where unset) and when it last wrote.
- **At open,** an unfinished run owned by another session is named in the question with its last write, and the question says it may still be running in another terminal or container.
- **Resuming takes ownership.**
- **A superseded session stops.** Every script call that writes refuses, with a distinct exit code, when `run.json`'s owner and the caller are both non-null and differ. Each covered command treats that exit as a stop with no further side effect: *another session (<id>) took this run over — stopping*. A null on either side passes, since it cannot be told apart. A subagent the superseded session had already dispatched may keep working until that session's next write; that limit is IMP-G5's too.

**D11 — End.** A run that finishes removes its folder just before its terminal `commit-artifacts`, which stays the run's last action, once every other step that reads the folder has read it (the final report's list of kept results among them) — by then everything the run produced is in the specs repository or on a branch. Where the removal finds that another session took the run over at its end, the run makes no terminal commit. *(Amended 2026-11-24 while building Part 1: the first wording removed the folder as the very last step, after the terminal `commit-artifacts`, which `CLAUDE.md` and `workflows-core:specs-repo-git` §4 make the last action of every run.)* A run that stops (a refusal, a `NEEDS HUMAN`, the user ending it) keeps its folder, and its stop message names the folder and says that running the same command again resumes it. A run that dies says nothing; the next start finds it.

**D12 — Pruning.** Each open removes run folders under `runs/` that no session has written for 30 days, and prints one `NOTE:` with how many and how much space. Nothing outside `runs/` is touched.

**D13 — What moves from `mktemp`.** A file a later step of the same run reads — handoff files, plan files, claims files, review packages, diff captures handed to an agent — goes in the run folder (`inputs/`, `results/` or `scratch/`). A file used within one shell command and removed by its own `trap` (the temporary index copies in the diff capture, a `curl` output, Vale's throwaway `XDG_CONFIG_HOME`) stays a `mktemp` file. `dev-workflows/references/context-management.md`'s "remove every file so handed off" rule is rewritten accordingly: the run folder's removal at D11 replaces the per-file removals for files that moved, and the "never inside a repo tree" rule still holds (the run folder is outside every repository).

### Special cases

**D14 — `/prd-ground`'s blind verification.** The invariant (`.claude/rules/prd-ground-verification.md`) stands. Two consequences:
- **Verifiers never see answers.** Verifier inputs and results live in their own subtree of the run folder, apart from the grounders' results; a verifier is handed only its own input and result paths; and `grounding-verifier`'s prompt says it reads nothing else in the run folder. The derive dispatch's input still carries premise and source only.
- **"No outcome carried forward from an earlier run"** keeps its meaning under this document's definition of a run (Terms): a resume continues the same run, so this run's own verifier results are reused; an earlier run's never are, because starting over deletes the folder. The rules file is amended to say so explicitly.

**D15 — `/prd-ground`'s later phases read results from files.** Phases 5–8 are rewritten so the renumbering, the horizons, the verification set and the Phase 8 write work from the saved results rather than the conversation. **A repository that moved while the run was stopped is pinned again.** On resume Phase 3 runs again; a repository whose `HEAD` has left the pin this run logged is pinned at its new `HEAD`, which changes the inputs of its dispatches, so its grounding and verification are redone (D7), and so is every design pass — whose input carries every repository's code findings — with the `[DG#n]` verification it feeds wherever its findings come back otherwise; every other repository's results are reused. *(Amended 2026-11-24 while building Part 1: the first wording said exactly the moved repository's grounding and verification were redone, which overlooked the design passes that read its findings.)* The resume question names the repositories that moved and how many saved results that discards, so a user who pulled all seven can choose *Start over* knowingly. A pin on file from an **earlier** run keeps today's rule (`PRD_GROUND_NEEDS_REBASELINE`). *Builder's call:* whether the later phases read the saved results through a script (the improvised run used Python for the merge and renumbering) or by the orchestrator reading them in bounded batches. The improvised run also split each repository's claims into chunks of 30 per `code-grounder` dispatch, which the command does not allow today; whether to allow it is a separate change, not part of this design.

**D16 — `/upgrade` and `/vuln`.** Per component or CVE, a branch or pull request is already the durable result of the fix. The progress log records each one's completion, so a resumed run does not redo a finished component; research and planner results are saved as any dispatch's are.

### Rollout and coverage

**D17 — Covered commands.** Every command that dispatches an agent or asks the user to approve something mid-run, in every plugin of the family (`workflows-core`, `dev-workflows`, `product-workflows`, `docs-workflows`, `security-workflows`). Not covered: `/implement`, which has its own resume (IMP-G5); commands with neither (`/statusline`, the `/prompt*` commands, `/feedback`, the `obsidian-llm-wiki` commands), `/docs-serve` (no agents; its state is a running server), and the `guideline-reviewers` and `prose-style` commands (one or two dispatches, nothing worth resuming). *Builder's call:* whether a gate in `check-docs.sh` holds every covered command to opening its run.

**D18 — Two parts.**
1. **Part 1:** `workflows-core:run-folder` and `run-folder.py` (with its copies and the CI check), and `/prd-ground` (D14, D15), the command that lost the work. A dispatch a command makes through another shared reference (`/prd-ground`'s Phase 4.5 `docs-grounder`, through `workflows-core:docs-grounding`) and the end-of-run maintenance dispatch are not saved in Part 1: each is one cheap dispatch, and saving the first means changing a reference other commands share, which is Part 2's.
2. **Part 2:** every other covered command: open at start, the dispatch, writer and gate steps, side effects logged, removal at the end, and the D7 audit of each dispatch's input.

Each part releases on its own, with the usual version bumps and dated `CHANGELOG.md` sections.

## Risks

- **A reused result that should not have been.** Mitigated by D7's rule that inputs name external state by version, and by the builder's per-dispatch audit. A missed version is the most likely defect; review should look for it first.
- **Disk.** A large `/prd-ground` run holds tens of megabytes; D11 and D12 bound how long it stays.
- **Sensitive content kept longer.** Inputs and results can hold diffs and code. Today the `mktemp` copies are removed at a run's end; now an interrupted run keeps them up to 30 days, in a 0700 folder under `~/.local/state`, never in a repository and never committed.
- **Context.** Agents that write their own results keep the orchestrator's context small; those that return inline (reviewers) are few per run.
- **A replay that repeats a side effect.** D6a's started/done entries cover the side effects a command makes itself; the builder lists each command's side effects in the plan, so none is missed.

## Left to the builder

- `run-folder.py`'s interface and file formats; the dispatch-id scheme per command; how a writer's scope is snapshotted (D6b).
- The exact text of the open offer and the stop message.
- How `/prd-ground`'s later phases read results (D15).
- Whether a `check-docs.sh` check enforces coverage (D17).
- Each covered command's D7 audit: which inputs need versions added.
- Version bumps and `CHANGELOG.md` entries per plugin.

# Run folder (shared reference)

Single source of truth for a command's **run folder**: where one run of one command keeps its working state, so that a run interrupted mid-way — a crash, a container restart, usage limits that stop the user for hours — and started again on the same machine continues where it stopped. Every agent that finished keeps its result, every answer the user gave stands while what they were shown is unchanged, and a side effect already made is not made again. An agent cut off mid-flight is dispatched again. This file's consumers are not listed in it, so that no copy of the list goes stale: re-derive them with `grep -l 'args: "run-folder ' plugins/*/commands/*.md`.

It is not `/dev-workflows:implement`'s mechanism, which resumes by its own script, `dev-workflows`' `scripts/run-state.py`, with its own state file; the two never share a folder. Nor does it hand work between commands: that stays the specs repository's job — committed, pushed, merged — and `resume.md` stays the pointer between commands. A run folder lives and dies within one run of one command, on one machine.

## 1. The script, the folder and its key

**The call.**

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/run-folder.py" <subcommand> <arguments…>
```

It is a script, called by its path like every other, so a run that never read this file runs the same thing. `${CLAUDE_PLUGIN_ROOT}` is the plugin whose file makes the call — a command's own plugin, and `workflows-core` for this reference — so every plugin whose commands call it ships the same `scripts/run-folder.py`, and CI fails a copy that differs from `workflows-core`'s, and a plugin whose commands, agents or references call it without shipping one. It needs `python3` 3.11, standard library only, and asks `git` for a repository's `origin` and root, taking the physical path where `git` cannot say. Every subcommand prints one JSON object on stdout; a failure, or a note, goes to stderr.

**Values on its command line.** A value the run did not write itself — arguments as typed, an answer, a fact, a log text — goes in single quotes, each `'` inside it written `'\''`, so the shell expands nothing in it. A text passed on stdin (`--input -`, `--shown -`, `--from -`) goes in a quoted here-document, `<<'RUN_FOLDER_EOF'`, whose delimiter line the text does not contain.

**Where.** `$XDG_STATE_HOME/ai-workflows/runs/<run-key>/`, or `~/.local/state/ai-workflows/runs/<run-key>/` where `XDG_STATE_HOME` is unset, empty or not an absolute path; mode `0700`, on the machine that runs the command, outside every repository, so nothing in it is ever committed. On a host it survives a reboot; in a container, it survives a restart where that directory is kept.

**The run key** names the folder, and the same invocation in a new session computes the same key: `<plugin>.<command>-<KEY>-<h>` for a keyed run, one whose address resolved to a folder under `$SPECS_PATH/specifications/` — `<KEY>` being the key that resolution returned, never one parsed out of free text — and `<plugin>.<command>-<h>` for a keyless one. `<h>` is the first 8 hex digits of a SHA-256 over the run's identity: the specs repository's `origin` URL, or its physical path where it has none; the working directory's repository root, or its physical path outside a repository, only where the command passes `--workdir`; and, on a keyless run only, its arguments. So two specs repositories holding the same KEY — two projects that share one state directory, each with its own specs repository mounted at the same path — get two folders, and a keyless command run with other arguments opens a run of its own. The script computes the key from the parts a command passes to `open`.

**The owner.** `run.json` records the session that owns the run — `CLAUDE_CODE_SESSION_ID`, null where it is unset or empty — and when it last wrote. `open` never takes ownership of an unfinished run; `resume` does. Every call that writes into a run — `phase`, `log`, `fact --set`, `dispatch`, `done`, `gate-record`, `effect start` and `effect done`, `keep` and `close` — refuses, with exit 9 and nothing written, when the owner and the caller are both non-null and differ; a null on either side passes, since it cannot be told apart. Two calls that write are not checked, by design: `resume`, which is how a session takes a run over, and `discard`, which is how *Start over* removes it whoever owns it. `open` writes only a run it makes itself. So an older session still running after another resumed its run stops at its next write. So does one still running after another chose *Start over*: `discard` removes the folder and the `open` after it makes a new run at the same path, owned by the session that started over, so the older session's reads succeed on that new run and its next write exits 9, both sessions carrying an id. A subagent it had already dispatched may keep working, and the result it writes is never read: that session's `done` exits 9, and the new owner's dispatch of the same id names a result file of its own (`run-dispatch`).

**What the folder holds.**

- `run.json` — the identity in clear (command, KEY, the arguments given, a run id, start and last-write times), the owner, the last phase, the facts, and the records of dispatches, results, answers, side effects and kept results. Only the script writes it.
- `progress.md` — the progress log, one line per event, `<UTC time> <session or -> <text>`, append-only, for a person to read.
- `main/inputs/<id>.md` — one input per dispatch, by dispatch id — and `main/results/<id>.<nonce>.md`, one result file per dispatch, its name taking a nonce that each `dispatch` draws anew and records: so an agent of an earlier dispatch of the same id — one a superseded session made, still running — writes a file no record names, which is never read. `blind/inputs/` and `blind/results/` the same for a dispatch kept apart (`run-dispatch`).
- `scratch/` — made by the command, for any other file a later step of the same run reads (§5).
- `.lock` — what the script serialises every write on, so a command may make its calls in parallel; `discard` and `close` wait on it too, so a write in flight lands before the folder goes, and move the folder off its path before removing it. A lock the call cannot take (`flock` fails, as on a network home with no lock service), or whose file keeps being replaced while the call waits, ends the call with exit 2 before it writes anything: no call writes unlocked.

## 2. What each exit means

- **0** — done: read the JSON.
- **9** — **taken over**: another session owns the run now — it resumed it, or chose *Start over*, which makes a new run at the same path — or removed its folder and none stands there now. **Stop at once and write nothing more**: no further call of the script, no dispatch, no question, no write into any repository or file, no commit, no push, and none of the command's tail — maintenance, cost, feedback, follow-ups and the terminal specs-repository commit among it. The command prints its own taken-over stop, naming the session the script's stderr line names (`owned by session <id>`), or saying that another session started the run over or finished it where the line says the folder was removed, and nothing else — no `run-stop-line`, since the folder is not this session's any more. An exit 2 whose stderr line reads `run folder no longer exists`, from a call that only reads, made once `run_folder` names that folder, means the same. It comes only while no folder stands at that path — between another session's `discard` and the `open` after it, where that `open` made none, or once the run another session owns has finished and removed it; where a new folder stands there, a read succeeds on the new run and the next write exits 9.
- **3** — only from `done`: the result file is missing or empty (`run-dispatch` step 4).
- **2** — the call could not run: a usage error, a folder that cannot be read or written, such as a full disk, or a lock it cannot take (§1, `.lock`). **It never fails the run.** Print one line, `NOTE: run folder no longer usable (<the script's stderr line>); continuing without it — this run cannot be resumed from here`, set `run_folder: unavailable` and `lost_folder: <the folder>`, and go on exactly as the command does without a folder. The step whose call failed goes on as it would without one — the dispatch is made, the question asked, the effect made.
- **Any other exit** — one this list does not name, such as 127 from a shell that finds no `python3` — is read as exit 2, its stderr line as the script's: the run goes on without its folder, so a run never fails because of its folder there either.

**A write the command makes into the folder itself** — a file under `scratch/` written through a here-document or a copy, the `mkdir -p` before it — that fails is met as an exit 2, the shell's error line standing in the `NOTE:` for the script's: the run goes on without its folder, and the step goes on as it would without one.

**Where the run folder is unavailable** — `open-run` found none, or a call exited 2 — every entry point below is skipped as its last line says, and the command acts exactly as it did before it kept a run folder. The run carries `run_folder: <path>` or `run_folder: unavailable`, and `run_resumed: true` where it resumed.

## 3. Phases, facts and the log

- `phase <folder> <name>` at the start of each phase the command names; the last one logged is the *last phase* `open-run`'s question shows.
- `log <folder> '<text>'` appends a line for a person to read. `open`, `resume`, `dispatch`, `done`, `gate-record`, `effect`, `keep` and `phase` log their own.
- `fact <folder> <name> --set '<value>'` records a value a later phase, or a resumed run, needs and that is no dispatch result — a repository's pin, the outputs of a write; `fact <folder> <name>` reads it back, `value` being `null` where none was set. A resumed run reads a fact wherever it would otherwise compute the value again, which could come out differently.

Each is skipped where the run folder is unavailable; an exit 9 stops the run (§2).

## 4. Entry points

A resumed run walks its phases from the start. Steps that only read run again; each dispatch goes through `run-dispatch` and is reused where its fingerprint still matches; each recorded question takes its answer through `run-gate`; each side effect `run-effect` guards is skipped once done; and phase-level facts come from `fact`. A run that dies says nothing: the next start finds its folder.

### Entry point: `open-run`

Run once, at the step the command names: once its run key is known — after address resolution where that comes first — and every refusal it can take before any work has had its chance, before any dispatch or recorded question. The command supplies `--command <plugin>.<command>`; `--key <KEY>` on a keyed run; `--specs`, its `$SPECS_PATH`; `--workdir <directory>` only where its run depends on the directory it is started in; and `--args '<arguments>'`, the arguments the command names (on a keyless run they are part of its key).

1. Where `$SPECS_PATH` is unset or names no directory, there is no folder to key: print `NOTE: no run folder (SPECS_PATH unset or not a directory); continuing without one`, set `run_folder: unavailable`, and go on.
2. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/run-folder.py" open --command <plugin>.<command> [--key <KEY>] --specs "$SPECS_PATH" [--workdir <directory>] --args '<arguments>'`. Print every `NOTE:` line it writes to stderr, as it stands: the folders it removed because no session had written them for 30 days (each `open` removes those first, and nothing outside `runs/`), a `run.json` that did not parse and was replaced, or the folder it could not make.
3. By `state`:
   - `new` — set `run_folder: <folder>`, and go on.
   - `unavailable` — set `run_folder: unavailable`, and go on as the command does without a folder; the `NOTE: no run folder (<reason>); continuing without one` step 2 printed is the one line that says so. An exit 2, or any other exit §2 reads as one, is the same, the `NOTE:` printed with the script's stderr line as its reason.
   - `unfinished` — ask step 4's question, or, where the command asks a resume question of its own, step 5's.
4. Ask, through `AskUserQuestion`, with `escalation-rules` loaded as the command's **Load the question rules.** step loaded them:

   ```
   An unfinished run of <the command and its address> was found — started <summary.started>, last written <summary.updated>, last phase <summary.last_phase, or "none logged">, <summary.results> saved agent result(s).
   [where summary.other_session is true:] It belongs to another session (<summary.owner>), which may still be running in another terminal or container: resuming takes it over, and that session stops at its next write.
   [where the arguments given now differ from summary.args:] It ran with: <summary.args>. Given now: <the arguments>. Resuming continues with the arguments given now, and redoes the saved results they change.
   [the lines the command adds]
   Resume it, or start over? Starting over deletes its saved results and answers.
   choices: ["Resume (Recommended)", "Start over"]
   ```

   A typed answer that is neither is asked again.
   - **Resume** — `resume <folder> --args '<the arguments>'`, the arguments given now as step 2 passed them: this session owns the run from now on, and those arguments replace the ones the run recorded, so the question a later session asks compares with these. Set `run_folder: <folder>` and `run_resumed: true`, and go on: the command walks its phases from the start.
   - **Start over** — `discard <folder>`, then `open` again with the same arguments, and read its `state` as step 3 does: `new`, or `unavailable`. *Start over* removes the folder whichever session owns it, and `open` makes a new run at the same path, owned by this session: a session that owned the old run reads the new one where it reads, and its next write exits 9 where both sessions carry an id (§1), so it stops (§2).
   - Either call exiting 2, or with any other exit §2 reads as one — as `unavailable`.
5. **One question, never two.** A command that already asks a resume question of its own — from a session file — asks no second one: it adds step 4's lines to its own question and applies the answer to both. Resuming its session resumes the run folder too (`resume`, with `--args` as step 4 passes it); a fresh start starts the run folder over (`discard`, then `open`). The command names that question.

Where the run folder is unavailable, nothing more: each entry point below says what it does then.

### Entry point: `run-dispatch`

Around one Agent call whose result the command saves. The command supplies, for each dispatch:

- **its id** — matching `^[a-z0-9][a-z0-9._-]*$`, and a function of what the dispatch is (phase, agent, item: `p5-cg-backend`), never of timing or of a position in a reply, so the same dispatch has the same id in every session;
- **its area** — `main`, or `blind` for a dispatch whose agent must not see what other dispatches returned: its input and result live under `blind/`, apart from `main/`; the command hands that agent its own result path and nothing else of the folder, and its input names no file under `main/`;
- **the agent** — its name and its definition file, `agents/<agent>.md` under the root of the plugin that ships it (`${CLAUDE_PLUGIN_ROOT}/agents/<agent>.md`, written in a command of that plugin); only an agent the calling command's own plugin ships is dispatched through this entry point, since its file must be named;
- **the model** — the Agent call's `model`, as the command passes it;
- **the input** — the prompt, without the `result_path:` line step 3 adds, **built so that a later session builds the same bytes**: the command's own fixed prompt text, each value it fills in taken from a file, a fact (§3) or the folder — never from the conversation, which a later session does not hold — and written as it stands, in an order the command fixes, never paraphrased, reworded or reordered. A large or variable part — a list, a diff, a claims file — goes in a file under `scratch/`, built the same way, which the prompt names and `--attach scratch/<file>` passes (a path relative to the folder), so that its bytes count too. One byte that differs redoes the saved result, so an input rebuilt loosely redoes every saved result on a resume. **It names by version every external thing the agent reads** — a repository by its commit, a specs or docs file by its blob id or content hash, a diff by the run-folder file that holds it — and the arguments and flags that change the agent's work. A change the input does not show leaves the fingerprint as it was, and a stale result is reused.

The **fingerprint** is a SHA-256 over the input's bytes, each attached file's bytes (sorted by path), the agent definition file's SHA-256 and the model. Nothing else counts: a plugin's version, or a change to a command, a skill, a reference or another agent, redoes nothing. A shared reference the agent reads while it works can so change its output unseen; that is a stated limit.

1. `dispatch <folder> <id> --area <main|blind> --agent <name> --agent-file <file> --model <model> --input - [--attach <path>]…`, the input on stdin. Its `result` is the result file: on `action: dispatch` a new path, `<area>/results/<id>.<nonce>.md`, which no earlier dispatch of the id named; on `reuse`, the file the recorded result names.
2. `action: reuse` — a result recorded complete under the same fingerprint: **do not dispatch.** The result is the file at `result`; the command reads it wherever it would have read the agent's return.
3. `action: dispatch` — make the Agent call with the input as its prompt and the model as its `model`. Where the agent's contract accepts a `result_path` input (the command names those agents), add the line `result_path: <result>`: the agent writes its whole return to that file and replies with a short receipt. Any other agent returns inline.
4. Record it complete — only a return the command goes on with, never one it retries or treats as the dispatch failing, which stays unrecorded so that a resume dispatches it again:
   - with `result_path`: read the agent's reply and the file at `result`; where the command goes on with that return, `done <folder> <id>`. A file missing or empty there means the agent left nothing, and so does an exit 3 from that `done`: where the agent's reply holds its whole return, read that, and where the command goes on with it, save it with `done <folder> <id> --from -`; where its reply says it could not write `result_path` (a missing input naming it, with no receipt), dispatch it once more without that line and meet its inline return as the `inline` case below says; otherwise the dispatch failed, and the command handles it as it handles that agent failing.
   - inline: where the command goes on with the return, `done <folder> <id> --from -`, the agent's whole return on stdin.

**A result file with no completion record is not a result, and neither is a file no record names.** A session that died between an agent's write and its `done` dispatches that agent again. Each `dispatch` that returns `action: dispatch` names a result file of its own and removes the files the earlier dispatch and the recorded result of that id named; `done` records, and a reuse reads, only the file the dispatch record names. So an agent still running for a session another one took over, or for an earlier dispatch of the same id, writes where nothing is read.

**A batch** — at most four concurrent per Agent message — runs step 1 for every member first (those calls may run in parallel), dispatches in one message only the members whose `action` is `dispatch`, and runs step 4 for each of those; a member whose `action` is `reuse` is read as step 2 says. A resumed batch so dispatches only the members with no recorded result.

**A resumed run says what it reused.** On a run that resumed (`run_resumed`), count each `dispatch` call's `action`, `reuse` or `dispatch`, by agent, as the call returns, and hold the counts; the final report carries one line, `Resumed: <r> saved agent result(s) reused, <d> dispatched (<agent>: <r> reused, <d> dispatched; …)`, the totals summed over the agents, each agent that had a `dispatch` call named in the order of its first, an agent with none left out — and a dispatch made once the folder is lost (§2) makes no call and is not counted. It is the one place a resume shows its reuse: an input whose rebuild differs by one byte redoes its saved result without a word, and `progress.md`, which logs each reuse, goes with the folder. A run that did not resume prints no such line.

**A dispatch that edits files** — a writer, whose work changes the tree or the files its next input is built from — is not made through this entry point: its fingerprint cannot see what it wrote, so a reused result could stand beside files that no longer hold its work. It runs as it did before.

Where the run folder is unavailable: dispatch as before; nothing is saved.

### Entry point: `run-gate`

Around one question asked after `open-run` whose answer a later step acts on — an approval, a choice of repositories, a consent. The command names its recorded questions and their gate ids, which follow the dispatch-id grammar. The questions of `open-run` and `changed-agents` are never recorded: they decide the folder itself.

**The shown text** — the question's text with its options exactly as presented, and the contents of any file it asks the user to approve — is built as a dispatch's input is (`run-dispatch`): the command's fixed text, each value taken from a file, a fact or the folder, in an order the command fixes, never reworded. Both calls below get the same bytes on stdin. A shown text built differently is not found and only asks the question again; a question that changed — a regenerated plan, a new finding — is asked again for the same reason. Nothing is written into the folder before an owner-checked call has passed.

1. `gate <folder> <gate-id> --shown -`, the shown text on stdin. It writes nothing.
2. An `answer` that is not `null` — the same question, shown the same, was answered earlier in this run: **do not ask.** First `log <folder> 'gate <gate-id> reused'`: an exit 9 there stops the run (§2) before it acts on an answer another session may have given. Then print `Answer reused from earlier in this run — <the question's first line>: <answer>`, and act on it as though it had just been given.
3. `null` — `log <folder> 'gate <gate-id> asked'`, so that an exit 9 stops the run before the question; ask as the command does; then `gate-record <folder> <gate-id> --shown - --answer '<the answer>'`, the same shown text on stdin, a free-text answer recorded verbatim. An exit 9 from `gate-record` stops the run before it acts on the answer.

Where the run folder is unavailable: ask as before.

### Entry point: `run-effect`

Around one side effect a replay would otherwise repeat — a write into the specs or a docs repository, a commit, a push, a pull request. The command names its effects and their ids, the facts it records after each, and what it does for one found `started`.

1. `effect <folder> <effect-id> state`.
2. `done` — made by an earlier session of this run: **skip it**, and read the facts recorded after it wherever the command would have used its outputs.
3. `none` — `effect <folder> <effect-id> start`; make it; record as facts the outputs a later step reads (§3); then `effect <folder> <effect-id> done`.
4. `started` — begun by an earlier session, its end never recorded, so it may be half made. Where the command names re-run handling for it — the specs-repository preflight, or a handoff that reuses its own branch — that handling decides, and the run then records `effect <folder> <effect-id> done`. Where it names none, it names a question instead: ask it, and act on the answer. The effect is never made a second time on a guess.

Where the run folder is unavailable: make the effect as before.

### Entry point: `changed-agents`

Run once, on a resumed run only, at the step the command names: where both are known — the agent files at once, the models where the command resolves them — and before any dispatch the answer could redo. The command supplies `--agent <name>=<file>` and `--model <name>=<model>` for each agent whose results it saves, as `run-dispatch` passes them; an agent left out counts as unchanged.

1. `stale <folder> --agent <name>=<file>… --model <name>=<model>…` → `total`, and for each changed result its `id`, `agent`, `agent_changed`, `old_model` and `new_model`.
2. `total` 0 — nothing.
3. `total` 10 or fewer — nothing is asked: each is redone when its dispatch comes, its fingerprint no longer matching. Print, and `log`, one line: `<total> saved result(s) will be redone: their agent's instructions or model changed since they were saved (<agent>: <n>, …).`
4. More than 10 — ask once:

   ```
   <total> saved results of this run were written under an agent's instructions or a model that has changed since: <agent> — <n> (instructions changed | model <old> → <new>), …
   [the command's line naming the results it always redoes, and why]
   Redoing them runs those dispatches again; keeping them reuses them as they are, and the final report names each one. No option is recommended: redoing costs the dispatches, and keeping reuses results the current instructions did not write.
   choices: ["Resume and redo them", "Resume and keep them", "Start over"]
   ```

   A typed answer that is none of the three is asked again.
   - **Resume and redo them** — `log` the answer; each is redone when its dispatch comes.
   - **Resume and keep them** — `keep <folder> --ids <every changed id but those the command always redoes> --agent … --model …`, the same pairs as step 1; those results are reused from now on. Where no id is left — every changed result is one the command always redoes — make no `keep` call (`--ids` with nothing after it is a usage error), and `log` the answer instead.
   - **Start over** — `discard <folder>`, then `open` as `open-run` step 2 does and read its `state` as its step 3 does; `run_resumed` is no longer true, and the command goes back to the step after `open-run` and runs as a new run, asking its questions again.

**A command's own rule may withhold *keep*** for some results, which the command names — a result whose invariant forbids reusing it under another model, say. Those are left out of `--ids` and redone whatever the answer.

**The final report names the results kept.** A resumed run calls `kept <folder>` before `close-run` removes the folder and holds what it returns, and where that is not empty its final report carries the line `Kept from earlier agent instructions or models: <the ids>`.

Where the run folder is unavailable, or the run did not resume: skip it.

### Entry point: `run-stop-line`

On every stop the command takes after `open-run` — a refusal, a `NEEDS HUMAN`, the user ending the run, a stop `run-effect` asked for — save the taken-over stop (§2):

1. `log <folder> 'stop <CODE>'`, `<CODE>` being the stop's code. A stop with no code logs `stop: <the first line of its message>`, or `stop: ended by the user` where the user ended the run.
2. After the command's own stop message, print `Run folder kept: <folder> — run <command> again to resume.`, `<command>` being the command and its address as the user types it (`/product-workflows:prd-ground MWC-001-01`). On a stop the command names as one a resume meets again — its own message says to start over — print `Run folder kept: <folder> — resuming it meets this stop again; run <command> again and choose Start over.` instead.

An exit 9 from step 1 makes this the taken-over stop: print that instead, and no line. The folder is kept, so running the same command again finds it and offers to resume. Where the run folder is unavailable: print nothing.

### Entry point: `close-run`

On a run that finished, and never on a stop: once every other step that reads the folder has read it — the `kept` read its final report needs among them — and just before its terminal specs-repository commit, which stays the run's last action:

1. `close <folder>`: the folder is removed. Everything the run produced is in the specs repository or on a branch by now.
2. Exit 9 — another session took the run over at its end: print `NOTE: another session took this run over; its run folder is left to it.`, and make no terminal specs-repository commit: nothing more is written once another session owns the run (§2). Exit 2 — print `NOTE: run folder not removed (<the script's stderr line>); a later run of any command removes it 30 days after its last write.`, and go on to the terminal commit.

Where the run folder is unavailable: nothing, save on a run that lost it mid-way (§2), which calls `close <lost_folder>` once and says nothing more, whatever it exits.

## 5. Files a later step reads

In a command that keeps a run folder, a file a later step of the same run reads — a handoff file, a plan, a claims file, a review package, a diff capture handed to an agent — is written into the folder: as a dispatch's input or result, or under `scratch/`. A file used within one shell command and removed by its own `trap` stays a `mktemp` file. The folder's removal by `close-run` replaces the per-file removals of the files that moved. Where the run has no folder, those files are `mktemp` files, as before.

## 6. What a command names for itself

A command that keeps a run folder names, in its own text:

- its `--command` value, `--key` or none, whether it passes `--workdir`, what `--args` carries, the step that runs `open-run`, and its own resume question where it has one;
- the phases it logs with `phase`, and the facts it records with `fact`;
- each dispatch it saves: its id scheme, its area (which use `blind`), its agent and that agent's file, its model, which agents take `result_path`, its input's fixed text and the files, facts or folder files each value in it is taken from, and what the input names by version;
- each recorded question, its gate id, and its shown text built the same way;
- each guarded side effect, its id, the facts recorded after it, and its handling of one found `started`;
- where `changed-agents` runs, its `--agent` and `--model` pairs, and the results its own rule always redoes;
- where its final report carries the `Resumed:` line (`run-dispatch`) and the `Kept …` line (`changed-agents`);
- its taken-over stop, that every other stop after `open-run` runs `run-stop-line`, and each of those a resume meets again;
- where `close-run` runs.

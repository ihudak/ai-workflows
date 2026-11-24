---
paths:
  - "plugins/*/scripts/run-folder.py"
  - "plugins/*/commands/*.md"
  - "plugins/*/agents/*.md"
  - "plugins/*/references/**"
---

# workflows-core — the run-folder authority

Loaded when any plugin's copy of `scripts/run-folder.py`, or any command, agent or reference file, is read: a command that keeps a run folder can be written in any plugin, and an agent it dispatches can be handed the path to write its result to. Kept in a file of its own so that `.claude/rules/workflows-core.md` stays under 20,000 characters; repo-wide rules are in `CLAUDE.md`; the design is `docs/superpowers/specs/2026-11-24-run-folder-design.md`.

## Authority

`plugins/workflows-core/references/run-folder.md` is the **single source of truth** for a command's run folder — where one run of one command keeps its working state, so that a run interrupted mid-way continues on the same machine: the folder and its key, the session that owns it, the saved dispatches and their fingerprints, the recorded answers, the guarded side effects, the changed-agents question, the stop line and the folder's removal, through its entry points `open-run`, `run-dispatch`, `run-gate`, `run-effect`, `changed-agents`, `run-stop-line` and `close-run`. A command cites it — `Skill(skill: "workflows-core:reference", args: "run-folder <entry point>")` — and never restates it. Its mechanics are `scripts/run-folder.py`, called by its path, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/run-folder.py" <subcommand> …`, so `${CLAUDE_PLUGIN_ROOT}` is the calling file's own plugin, and each plugin that calls it ships a copy equal to `workflows-core`'s, which CI checks (the copied-scripts rule, `.claude/rules/workflows-core-bounded-run.md`). Its consumers are what `grep -l 'args: "run-folder ' plugins/*/commands/*.md` lists. **`/dev-workflows:implement` is not one**: it resumes a stopped run by a different mechanism, `dev-workflows`' `scripts/run-state.py`, with its own state file in the worktree's git directory, and the two are never mixed — nor is `run-folder.py` ever named `run-state.py`.

## Invariants

1. **A run never fails because of its folder.** Where the folder cannot be made or written, `open` reports `unavailable` and exits 0, and the run goes on exactly as it would without one, after one `NOTE:`; a later call that exits 2 does the same from there on. A change that lets a folder failure stop a run, or skip work the run does without a folder, breaks this.
2. **Exit 9 stops the run, writing nothing more.** A call that writes into a run, from a session other than its owner (`CLAUDE_CODE_SESSION_ID`, both non-null), or on a folder another session's *Start over* removed, exits 9 and writes nothing — save `resume` and `discard`, unchecked by design: they are how a session takes a run over and how *Start over* removes it. The command stops at once — no further call, dispatch, question, write, commit or tail, and no stop line, since the folder is the other session's.
3. **A saved result is reused only where its recorded fingerprint equals the new one and its completion was recorded** (`done`). A result file with no completion record is never read as a result. The fingerprint covers the input's bytes, each attached run-folder file's bytes, the agent definition file and the model, and nothing else, so an input must name by version every external thing the agent reads — a repository by its commit, a file by its blob id or content hash; a missing version is the likeliest defect, and review looks for it first. And a later session must build the same bytes: an input built from the command's fixed text with values from files, facts or the folder, never from the conversation, never reworded or reordered — or every saved result is redone on a resume.

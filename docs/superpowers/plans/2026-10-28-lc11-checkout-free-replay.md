# LC11 Checkout-free Replay Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When a session-file push is rejected because the remote branch moved on, `commit-artifacts` replays the run's own session-file commits onto it without touching the checkout, settles appended files entry by entry and a security register by rebuild, moves the branch in one locked transaction, and pushes; and session-branch mode's merges stop fusing entries.

**Architecture:** One pure function, `entry_set_merge`, settles a block-shaped appended file from three versions; it replaces git's `union` everywhere `session-branch.py` merges (§8's `commit`, `sync`, `put-back`) and is used by a new `replay` subcommand that does fetch → replay (`merge-tree --merge-base`, `commit-tree`) → move (`update-ref --stdin` transaction around `read-tree -m -u`) → push, at most three attempts. `specs-repo-git` §4 step 6 calls it on a non-fast-forward rejection; `/security-workflows:scan` hands over `register.py`'s path.

**Tech Stack:** Python 3 standard library, git ≥ 2.40 (`merge-tree --write-tree --merge-base`), Markdown references.

**Spec:** `docs/superpowers/specs/2026-10-27-lc11-run-settles-rejected-push-design.md` (approved by the user 2026-10-28). Measurements and reviews: `docs/superpowers/verification/2026-10-27-lc11-measurements/` (`scripts/replay.py` and `scripts/move.py` are working prototypes of spec §3.2 and §3.4 — read them; do not copy them blindly, they predate the entry-set rule). Plan review: Opus, READY WITH CHANGES, folded in below (2026-10-28).

## Global Constraints

- Work only in `/workspace/.worktrees/lc11` on branch `iv-gu/lc11-design`; verify `git branch --show-current` before every commit; never `git checkout`/`switch`/`rebase`/`reset`/`stash` there; commits carry `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`; new commits only, never amend.
- `session-branch.py` stays Python standard library only. Every git call goes through its `git()` helper (`git -C <root> -c core.quotePath=false`), save two named exceptions with the same prefix: the `update-ref --stdin` transaction (an interactive `Popen`, Task 4's `ref_transaction`) and the bounded fetch and push (Task 4's `git_bounded`, a process-group SIGTERM-then-SIGKILL as `workflows-core:bounded-run` does — never `subprocess.run(timeout=)`, whose kill leaves the transport child and any `*.lock` behind). Output one JSON object on stdout; exit 0 = it ran, exit 2 = it could not run, one `session-branch: not run (...)` line on stderr.
- Never force-push, `reset`, `rebase`, `branch -D`, delete a lock file, or write `info/attributes` outside session-branch mode (`specs-repo-git` §1; spec §5).
- The reference and the script change together (`specs-repo-git` §8's opening): what Task 2 changes in §8 is stated in §8 in Task 2; the replay's reference text lands in Task 5, before anything calls it.
- Versions from `main` at `3a33d333`: `workflows-core` 1.65.0 → **1.66.0**, `security-workflows` 0.6.0 → **0.7.0**; any dependent whose docs page changes takes its next minor. CHANGELOG sections dated `2026-10-28`. (Renumbered at merge time if `main` moves.)
- Entry headings (spec §3.3), pinned from the references that define them: `implementation-format` §1 `## <YYYY-MM-DD> — /implement`, `feedback-emission` §1 `## <YYYY-MM-DD> — <command> — <category>`, `/security-workflows:scan` §7.3 `## <YYYY-MM-DD> — /security-workflows:scan`, `cost-emission` §6 `## <YYYY-MM-DDTHH:MM:SSZ> — <command> — <phase>`. One pattern covers all four: `ENTRY_HEAD = re.compile(rb"^## \d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}Z)? \xe2\x80\x94 ", re.M)` (the em dash in UTF-8). **Never loosen `ENTRY_HEAD` or `merge_class` to make an old selftest pass**: convert the test to the real format instead.
- Selftests use the real formats above, never one-line stand-ins. Replay selftests that need git ≥ 2.40 run only where `git --version` reports ≥ 2.40; below it they assert the `cannot-replay` refusal instead (a version check, so a broken `replay_ok` cannot hide the suite).
- The script's CLI defaults and the reference's Bash timeout are one figure: `attempts` 3 × (fetch bound 60 s + push bound 60 s) + 60 s margin = **420 s**, under the Bash tool's 600 s ceiling.

## Review Focus

1. **An entry ending without a newline on one side and with one on the other** (a hand edit, an editor that strips it) must match, never double; appending to a side whose last line lacks a newline must not glue lines — Task 1.
2. **CRLF content** (`core.autocrlf=input` is in the user's own config, measured) must merge byte-exact with the file's own line ending — Task 1, and `settle_copy`'s working-tree form in Task 2.
3. **The "branch has not moved" rule with no placed record** (after any `lift`, which clears the records) must still let a hand edit through — Task 2.
4. **Identical changes on both sides** (a scan's `runs/` and `scans/` files `origin` already holds) are not conflicts: kept, and a fully identical commit dropped — Task 3.
5. **A repository `.gitattributes`** — `* merge=text`, `* -merge`, `security/** export-ignore` — must change no outcome of the replay or of §8's merges — Tasks 2 and 3.
6. **`replay_ok` on git 2.41+** (`merge-tree -h` prints `--[no-]merge-base`) must answer yes — Task 3.
7. **A race during the push upload** reads `[remote rejected] (failed to update ref)`, not `[rejected]`: no loop, classified by step 6 as today — Task 4.
8. **Localised git messages** (`LANG=de_DE`): no path or reason is parsed out of git's text — Task 4.
9. **A linked-worktree specs checkout**: in-progress and lock files resolved by `rev-parse --git-path` — Task 4.

---

### Task 1: The entry-set merge

**Files:**
- Modify: `plugins/workflows-core/scripts/session-branch.py` (new constants and functions after `classify`; selftest cases in `scenarios()`)

**Interfaces:**
- Produces:
  - `ENTRY_HEAD` (above).
  - `merge_class(path: str) -> str | None` — `None` for any path `classify` rejects; otherwise `"block"` for `implementation.md`, `_security.md`, and every session file under a `dev-workflows/` directory, `dev-workflows-feedback/` or `dev-workflows-cost/` except `resume.md`; `"lines"` for `follow-ups.md`; `"whole"` for `dev-workflows/resume.md`, `pr-draft.md`, `*-implementation-gaps.md`; `"register"` for `security/<slug>/register.json` and `register.md`; `None` for every other session path (a `runs/` or `scans/` record). By path, never by `check-attr`.
  - `split_entries(data: bytes) -> tuple[bytes, list[bytes]]` — the header (bytes before the first `ENTRY_HEAD` line) and the entries (each from an `ENTRY_HEAD` line to the next, or the end).
  - `entry_key(chunk: bytes) -> bytes` — the chunk with every trailing line that is empty or whitespace-only, and every trailing line ending, removed (`rstrip` of `b" \t\r\n"` at the end only). Headers and entries are compared by this key.
  - `entry_set_merge(base: bytes | None, ours: bytes, theirs: bytes) -> bytes | None` — `None` (refuse) where `entry_key(ours header) != entry_key(theirs header)`, or any entry of `base` (by key) is missing from `ours` or from `theirs`. Otherwise: `ours`, given a final line ending where it lacks one; then, for each entry of `theirs` whose key `ours` lacks, in `theirs`' order: one empty line, then the entry with its trailing blank lines removed and exactly one final line ending. The line ending is `\r\n` where the entry's first line ends `\r\n`, else `\n` (and the same rule, applied to `ours`' last line, decides the ending added to `ours`). The result always ends with a line ending. `base=None` is the add/add case. Callers never pass `None` for `ours` or `theirs`: a side that deleted the file is a refusal decided by the caller.

- [ ] **Step 1: Write the failing selftest cases** in `scenarios()`, a new block `# ---- entry_set_merge ----`, with real-format entries (`implementation-format` §1's two example blocks; `feedback-emission` §1's entry; scan §7.3's `_security.md` block; a `cost-emission` §6 entry), asserting:
  - two same-day `/implement` entries differing in one line (`pushed: true` vs `pushed: false`) → both kept, in order, one header;
  - `ours = base + E1`, `theirs = base + E1` → `ours` byte-unchanged;
  - `ours = base + E1 + B1`, `theirs = base + B1` (a merge reordered them) → `ours` unchanged; `theirs = base + B1 + E2` → `ours` then a blank line then `E2`;
  - **Review Focus 1:** `E1` last on one side with no final newline and on the other with one (and with an extra blank line) → matched, not doubled; `ours` ending without a newline plus a new entry → `ours`' last line intact, a newline, an empty line, the entry;
  - **Review Focus 2:** CRLF `ours` and `theirs` → merged with `\r\n` endings throughout, no bare `\n` introduced;
  - add/add with identical headers → merged; different headers → `None`;
  - an edit inside a base entry, an addition to the last base entry, a removal → each `None`;
  - a `## Notes` line inside an entry body stays in that entry;
  - `merge_class` for each path in the classifier table already in `scenarios()`, plus `…/dev-workflows/resume.md` → `"whole"`, `…/follow-ups.md` → `"lines"`, `security/acme/register.md` → `"register"`, `security/acme/runs/0001-x.json` → `None`, `README.md` → `None`.
- [ ] **Step 2: Run** `python3 plugins/workflows-core/scripts/session-branch.py --selftest` — expected: FAIL naming the new cases.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the selftest — expected: PASS (every existing case still passes).
- [ ] **Step 5: Commit** `feat(workflows-core): entry-set merge for block-shaped session files (LC11)`.

### Task 2: Session-branch mode stops fusing entries

**Files:**
- Modify: `plugins/workflows-core/scripts/session-branch.py` — `ATTRIBUTES` and its comment, `union_shaped` (removed), `union_copy` → `settle_copy`, `commit`, `sync`, `put_back`, `world()`'s seed and the existing scenarios that use stand-in entries.
- Modify: `plugins/workflows-core/references/specs-repo-git.md` §8.2 steps 2–3, §8.3 `put-back`, and §6's session-branch rows (a new `unsettled` line).

**Interfaces:**
- Consumes: `merge_class`, `entry_set_merge`, `entry_key` (Task 1).
- Produces:
  - `ATTRIBUTES` = `**/follow-ups.md merge=union` plus `-merge` for `**/dev-workflows/resume.md`, `**/pr-draft.md`, `**/*-implementation-gaps.md`, `security/*/register.json`, `security/*/register.md`; no `merge=union` for any block-shaped path. `ensure_attributes` already rewrites its own marked block.
  - `settle_copy(root: str, path: str, tip: str) -> bytes | None` — in working-tree form (`cat-file --filters`, as `union_copy` read its sides): `base` the version at `merge-base HEAD <tip>`; `"block"` → `entry_set_merge(base, ours=<tip's version>, theirs=<working copy>)`; `"lines"` → `git merge-file -p --union <tip's version> <base> <working copy>`; `None` where `entry_set_merge` refuses or either side is absent.
  - `commit(...)` result gains `"unsettled": [paths]`. For each kept path whose working copy differs from the tip: `given = placed[p] if p in placed else blob(root, "HEAD", p)`; **where `blob(tip, p) == given` the branch has not moved for this path, and the working copy is committed as it is**; otherwise `settle_copy`, whose `None` leaves the path out of the commit, in `unsettled`, the working copy untouched.
  - `sync(...)`: after `merge-tree --write-tree -X ours <tip> <c>`, every path classed `"block"` or `"lines"` whose three blobs (at `git merge-base <tip> <c>` — the one git prints — at `<tip>` and at `<c>`) all differ is replaced in the merged tree through a temporary index — `"block"` by `entry_set_merge(base, ours=tip's, theirs=c's)`, `"lines"` by `merge-file -p --union` over the same three — with the merged tree's file mode kept. A refusal, or any other path `merge-tree` reports conflicted, means **no merge commit for that source**; the path goes to `conflict`.
  - `put_back(...)`: `settle_copy` in place of `union_copy`; `None` lists the path in `skipped`, the copy untouched.

- [ ] **Step 1: Convert the existing fixtures.** Add a selftest helper `entry(date: str, command: str, body: str) -> str` writing a real-format entry; convert `world()`'s seed feedback file and every stand-in `## a1`-style entry in the scenarios that merge appended files (today around lines 816–869, 925–937, 982–1009, 1010–1025, 1093–1105, 1222–1232, 1251–1262, 1319–1331) to it, keeping each scenario's intent; the cases that asserted "both sides' entries survive the union merge" keep that assertion against the new rule.
- [ ] **Step 2: Write the failing selftests**, with real-format entries:
  - two `commit` calls in a row on one `implementation.md` → each entry once on the session branch;
  - `commit` after a `sync` merged a teammate's entry (`E1 B1` on the branch, `B1` at HEAD) → `E2` committed, nothing doubled;
  - a second `sync`; a squash-merged session pull request then a `sync` → nothing doubled;
  - a `sync` where both sides appended to one `implementation.md` → both entries on the branch (not `-X ours`' version);
  - a `sync` where the default side edited a base entry → no merge commit, path in `conflict`, the tip unchanged;
  - **Review Focus 3:** the `implementation-format` §1 block move (a removal) committed as it is where the branch has not moved — once with a placed record, once after a `lift` cleared it; and in `unsettled`, working copy untouched, where another worktree moved the branch on since;
  - `settle_copy` reached: another worktree appended to the branch, this worktree appended to its working copy → committed with both entries; the same with CRLF content (**Review Focus 2**);
  - `put-back` over a foreign working copy the rule refuses → in `skipped`, the copy untouched;
  - **Review Focus 5:** with a committed `.gitattributes` of `* merge=text`, then `* -merge`, the two-appends `sync` case gives the same result;
  - the rewritten `info/attributes` block: `merge=union` only for `follow-ups.md`, `-merge` for the five whole and register shapes.
- [ ] **Step 3: Run** the selftest — expected: FAIL on the new cases.
- [ ] **Step 4: Implement** the interfaces above; remove `union_copy`, `union_shaped` and every caller.
- [ ] **Step 5: Update `specs-repo-git` §8**: §8.2 step 2's merge of a working copy (the "branch has not moved" rule, `unsettled`); step 3's merges (block and line paths settled from three blobs, a refusal makes no merge commit); §8.3 `put-back` (`skipped`); a §6 line for `unsettled` — the path; that it holds an edit the session branch's version does not; `git -C "<SPECS_PATH>" show <session branch>:<path>`; that the next run commits it once the working copy holds every entry of both; that until then `lift` skips each move of the checkout. Re-read §8 whole for every sentence that still says `union` keeps both sides' entries.
- [ ] **Step 6: Run** the selftest, then `python3 scripts/reference-parts.py check-parts && ./scripts/check-docs.sh --root .` — expected: PASS.
- [ ] **Step 7: Commit** `fix(workflows-core): session-branch merges keep entries whole — entry-set merge replaces union (LC11)`.

### Task 3: The replay

**Files:**
- Modify: `plugins/workflows-core/scripts/session-branch.py` — new functions; `commit_tree` gains author and message-file arguments; selftests.

**Interfaces:**
- Consumes: `merge_class`, `entry_set_merge` (Task 1); `blob`, `rev` (existing).
- Produces:
  - `commit_tree(root, tree, parents, message, env=None)` — `env` carries `GIT_AUTHOR_NAME`/`_EMAIL`/`_DATE`; the message is passed byte-exact through `-F -` (`git log -1 --format=%B`), never `-m`; signing unchanged.
  - `REPLAY_BLOCK` — the attributes text the replay passes with `-c core.attributesFile=<temp file>`: `**/follow-ups.md merge=union`, `-merge` for the `"whole"` and `"register"` shapes, nothing for `"block"` shapes.
  - `replay_ok(root: str) -> bool` — `merge-tree -h` output contains `--write-tree` and `merge-base` (covers `--[no-]merge-base`, **Review Focus 6**).
  - `replay_commits(root: str, onto: str, commits: list[str], register_rebuild: str | None) -> dict` — for each commit `c`, oldest first, against `p = c^`: `merge-tree --write-tree -z --name-only --no-messages --merge-base=<p> <onto> <c>` (never `-X`), with the block. **The paths to settle** are those whose three blobs at `p`, `onto` and `c` all differ (computed with `diff-tree -r -z --no-renames` of `p..onto` and `p..c`); a path where `onto` and `c` agree keeps that content (**Review Focus 4**). Each is settled by `merge_class`: `"block"` → `entry_set_merge(base=p's, ours=onto's, theirs=c's)`, refusing where either side deleted it; `"lines"` → `merge-file -p --union <onto's> <p's> <c's>`; `"whole"` → `c`'s version, a deletion included; `"register"` → the rebuild below; `None` → refuse. Any other path `merge-tree` reports conflicted → refuse. **The register rebuild** runs wherever both sides changed anything under `security/<slug>/`: fill a temporary root with `security/<slug>/` of the merged tree by `ls-tree -r -z` plus `cat-file blob` (never `git archive`, which honours `export-ignore`, **Review Focus 5**), run `python3 -I <register_rebuild> rebuild --specs <tmp root> --slug <slug>`, write `register.json` and `register.md` back through a temporary index; `register_rebuild=None` or a non-zero exit → refuse. A resulting tree equal to `onto`'s tree drops `c`; otherwise `commit_tree(root, tree, [onto], <c's %B>, env=<c's author>)`, file modes from the merged tree. Returns `{"tip": str, "replayed": [new shas], "dropped": [old shas], "numbers": {"before_remote": {...}, "before_run": {...}, "after": {...}}, "refused": None | {"reason": "conflict" | "register-rebuild", "path": str}}`; the three `numbers` maps come from `rebuild`'s `numbers` run on the first `onto`, on the last original `c`, and on the final tree (Task 4 turns them into `moves`).
- [ ] **Step 1: Write the failing selftests** (a bare origin and two clones built in the test, without `world()`'s pre-receive hook), one run commit replayed onto a teammate's commit unless named otherwise:
  - two same-day `implementation.md` entries → both, teammate's first; `feedback` and `_security.md` likewise;
  - a byte-identical append on both sides → the commit dropped; a scan commit whose `runs/` and `scans/` files `origin` already holds byte for byte, plus a new entry → replayed, the shared files untouched (**Review Focus 4**);
  - `resume.md` changed on both sides → `c`'s version; `c` deleting `resume.md` → deleted;
  - `follow-ups.md` appended on both sides → union, `onto`'s lines first;
  - both sides creating the same per-date docs feedback file (add/add) → merged under one header;
  - a register both sides changed, `register_rebuild` = a stub script written in the test (writes `register.json`/`register.md` from `runs/`, prints `{"numbers": {...}}` whose values differ between `onto`, `c` and the rebuilt tree) → rebuilt files equal the stub's output, the three `numbers` maps as the stub printed them; `register_rebuild=None` → refused, `reason: "register-rebuild"`, the path named;
  - a modify/delete, a `runs/` add/add of different content → refused, `reason: "conflict"`, naming the path;
  - two local commits onto a remote that appended to the same file → both replayed, nothing doubled;
  - a session file whose path holds `é` → settled, not refused;
  - **Review Focus 5:** a committed `.gitattributes` of `* merge=text`, then `* -merge`, then `security/** export-ignore`, changes no result above;
  - `replay_ok` → true on this git (≥ 2.40), asserted with the version check;
  - after every case, the checkout's `status --porcelain -z`, `ls-files -s` and HEAD are identical to before.
- [ ] **Step 2: Run** the selftest — expected: FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the selftest — expected: PASS.
- [ ] **Step 5: Commit** `feat(workflows-core): checkout-free replay of session-file commits (LC11)`.

### Task 4: Move, push, and the `replay` subcommand

**Files:**
- Modify: `plugins/workflows-core/scripts/session-branch.py` — new functions, `refuse_checked_out` and `ahead_paths` generalised, `main()`/`dispatch()`, the module docstring; selftests.

**Interfaces:**
- Consumes: `replay_ok`, `replay_commits`, `commit_tree` (Task 3); `classify`.
- Produces:
  - `checked_out_at(root: str, branch: str) -> list[str]` — every worktree path (`worktree list --porcelain -z`) holding `refs/heads/<branch>`; `refuse_checked_out` keeps its behaviour on top of it. "Checked out here" means the list holds `realpath(rev-parse --show-toplevel)`.
  - `push_scope(root: str, head: str, base: str) -> tuple[list[str], str | None]` — `ahead_paths`' test (non-merge, every path a session path) over `rev-list --reverse <head> --not <base>`, plus a root commit fails; returns the list and the first failing sha or `None`. `ahead_paths` is rewritten on it.
  - `git_bounded(root, seconds, *args) -> CompletedProcess` — `git -C root -c core.quotePath=false …` in a new session, SIGTERM to the group at `seconds`, SIGKILL 10 s later.
  - `ref_transaction(root) -> Popen` — `git -C root -c core.quotePath=false update-ref --stdin -m "session-branch: replayed onto origin/<b>"`, driven by `move_branch`.
  - `move_branch(root, branch, old, tip, here: bool) -> dict | None` — `None` on success, else a refusal. `here`: `update-index -q --refresh` (an `index.lock` → `{"reason": "locked"}`); the would-overwrite paths are the intersection of `diff-tree -r -z --name-only --no-renames <old> <tip>` with `status --porcelain -z --untracked-files=all --ignored`'s paths — non-empty → `{"reason": "would-overwrite", "path": <first>, "paths": [...]}` before anything moves; then the transaction: `start`, `update refs/heads/<b> <tip> <old>`, `prepare` (a failure → `{"reason": "branch-moved"}`), `read-tree -m -u <old> <tip>` (a failure → `abort`, `{"reason": "would-overwrite"}` with the computed paths, or `"locked"`), then `commit`; where `commit` fails after `read-tree` succeeded, `read-tree -m -u <tip> <old>` and `{"reason": "branch-moved"}`. Not `here` and checked out nowhere: `update-ref -m … refs/heads/<b> <tip> <old>`. No path or reason is read out of git's message text (**Review Focus 8**).
  - The closed `refused.reason` set: `conflict`, `register-rebuild` (Task 3), `would-overwrite`, `cannot-replay`, `in-progress`, `locked`, `push-scope`, `checked-out`, `fetch-failed`, `branch-moved`.
  - `class Partial(NotRun)` carrying the result dict; `main()` prints `Partial`'s result on stdout before its stderr line and exit 2.
  - `replay(root, branch, register_rebuild=None, set_upstream=False, attempts=3, fetch_seconds=60, push_seconds=60) -> dict` and the CLI `replay --branch <b> [--register-rebuild <path>] [--set-upstream] [--attempts 3] [--fetch-seconds 60] [--push-seconds 60]`, printing `{"moved", "pushed", "attempts", "replayed", "dropped", "tip", "porcelain", "moves", "upstream_error", "refused"}`. Per attempt: `git_bounded` fetch `origin +refs/heads/<b>:refs/remotes/origin/<b>` (failure → `fetch-failed`); condition 3 `replay_ok` (`cannot-replay`); condition 5 — `rev-parse --git-path` of `rebase-merge`, `rebase-apply`, `MERGE_HEAD`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`, `sequencer` (`in-progress`) and `index.lock` (`locked`) (**Review Focus 9**); condition 6 `push_scope(refs/heads/<b>, refs/remotes/origin/<b>)` (`push-scope` with the sha); condition 7 `checked_out_at` holds another worktree (`checked-out` with its path). An empty list, or every commit dropped → move a branch strictly behind (or now at the replayed tip) onto the remote ref, `pushed: false`. Then `replay_commits`, `move_branch`, and `git_bounded` push `--porcelain origin <tip>:refs/heads/<b>`; `porcelain` is the ref's status line. `[rejected]` → next attempt; anything else, `[remote rejected]` included, stops (**Review Focus 7**). After a successful push with `--set-upstream`: `branch --set-upstream-to=origin/<b> <b>`, a failure in `upstream_error`. `moves`: one entry per origin whose number in `after` differs from `before_remote` (`side: "remote"`) or `before_run` (`side: "run"`), `from` from the first attempt's maps and `to` from the last; `replayed`/`dropped` count the last attempt. Any exception after a move raises `Partial` with `moved: true`.
  - The module docstring: the usage line for `replay`; "Nothing here switches a branch, moves HEAD, pushes, or writes a working-tree path outside …" and the exit-2 paragraph rewritten for `replay` (it moves a branch and the checkout's files by `read-tree`, pushes, and prints its partial result on exit 2).

- [ ] **Step 1: Write the failing selftests**, end to end through `Repo.run("replay", ...)` unless named:
  - the s1 dirty set in the run's clone (`A`, ` M`, `AM`, `MM`, untracked) → pushed; every user file keeps its exact status letters and bytes; origin holds both sides' entries;
  - a dirty file the tip changes; an untracked file at a path the tip adds → `moved: false`, `refused.reason: "would-overwrite"`, the path named, HEAD/index/bytes identical;
  - a same-bytes rewrite of a file the tip changes → moves after the refresh;
  - a concurrent commit: in-process, call `replay_commits`, commit in the clone, then `move_branch` → `branch-moved`, nothing touched;
  - a plugin branch checked out nowhere → moved by `update-ref`, pushed; checked out in another worktree (`git worktree add`) → `checked-out` with that path;
  - an empty list (local strictly behind) → moved onto origin, `pushed: false`;
  - a non-session commit among the local commits → `push-scope` with its sha, nothing moved; a root commit → `push-scope`;
  - a race: a fake `git` first on `PATH` (written by the test) that, on the run's first two `push` calls, first pushes a teammate commit from clone B → `attempts: 3`, `pushed: true`; three races → `moved: true`, `pushed: false`;
  - `world()`'s pre-receive refusal → `porcelain` carries `[remote rejected]`, `attempts: 1`, no loop;
  - a later attempt refused (attempt 2's replay meets a conflict) after attempt 1 moved → `moved: true`, `pushed: false`;
  - exit 2 after a move (a signer stub that fails on attempt 2) → stdout carries the partial JSON with `moved: true`;
  - `--set-upstream` on a branch with no upstream → `@{u}` is `origin/<b>`; with `.git/config` read-only → `upstream_error` set, nothing else changed;
  - `LANG=de_DE.UTF-8` in the environment → the same `would-overwrite` path named;
  - `moves` from Task 3's stub maps, across two attempts, `from` the original number.
- [ ] **Step 2: Run** the selftest — expected: FAIL.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** the selftest — expected: PASS. (The reverse `read-tree` after a failed `commit` is not reproducible in a test; the code path is reviewed by reading.)
- [ ] **Step 5: Commit** `feat(workflows-core): session-branch.py replay — fetch, replay, locked move, push (LC11)`.

### Task 5: The references, the rules file, and the scan command call it

**Files:**
- Modify: `plugins/workflows-core/references/specs-repo-git.md`:
  - §1 rule 4: a named exception — the replay's move of the checkout by `read-tree` inside the locked transaction — beside §8's checkout-free merges; §1 rule 8: the upstream §4 step 6's replay sets.
  - §3.4: the flush and the retry of other plugin branches reach the replay; rewrite "Nothing else here brings the default branch up to date…".
  - §4 step 2: rewrite "step 6 says what to run".
  - §4 step 6's non-fast-forward bullet: where session-branch mode is off (condition 2, tested here), run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/session-branch.py" --specs "$SPECS_PATH" replay --branch <branch> [--register-rebuild <path>] [--set-upstream]` — `--set-upstream` exactly where step 5's push carried `-u`, `--register-rebuild` where the caller passed `register_rebuild` — in a Bash call with a 420000 ms timeout; read its JSON: `refused` → today's report with the reason clause (by `reason`; `would-overwrite` names the user's path and says the next run settles it once that path is clear); `pushed` → the new row; `moved` and not `pushed` → the moved-not-pushed row; `porcelain` → classified as for any push, a `[remote rejected]` writing the refusal record. Exit 2 with no stdout → today's *push rejected* row with `session-branch.py could not run (<first stderr line>)`; exit 2 with `moved: true` on stdout → the moved-not-pushed row.
  - §6: the rows (pushed after a replay; moved, not pushed; the *push rejected* row's remedy `git -C "<SPECS_PATH>" pull --rebase --no-autostash origin <branch>` plus the push, with the reason clause), content per spec §3.5 and §3.7.
  - §7: the optional `register_rebuild` input to `specs-preflight` and `commit-artifacts`.
- Modify: `.claude/rules/workflows-core-git.md` — the authority paragraph (what `commit-artifacts` does on a rejection) and the invariant "never merge/rebase/reset (§8's checkout-free merges … aside)" naming the replay beside them; re-derive by command every number in the paragraphs you touch (thirty-four, seventeen, eleven, twenty-two, fifteen) and state the command beside any you change; keep the file under 20,000 characters.
- Re-read, and fix where now false: `CLAUDE.md`'s hard constraint ("switching only plugin branches and pushing only per §4 step 5"); `phase-handoff` §1 rule 4 ("WIDER than the rule it inherits") and the rules file's "the fourth widened" — `specs-repo-git`'s rule 4 now carries an exception `phase-handoff` does not take.
- Modify: `plugins/security-workflows/commands/scan.md` — `register_rebuild: ${CLAUDE_PLUGIN_ROOT}/scripts/register.py` at its `specs-preflight` and `commit-artifacts` calls; its paragraph after the `Specs repo:` line applies only where the replay refused with the register unsettled; the new row's register moves are this run's report of renumbered findings.
- Modify: `plugins/workflows-core/references/security-register-format.md` §1 and §2 where they say a rejected push is the user's to settle.

**Interfaces:**
- Consumes: the `replay` subcommand's CLI, JSON and `refused.reason` set (Task 4).

- [ ] **Step 1: Record the before-counts** (claim-sweep refinement 7, wrap-insensitive, across `plugins/` with every `CHANGELOG.md`, root `README.md`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/`) of each phrase this task changes: `never auto-rebase mid-run`, `this reference never rebases`, `no run takes them in for you`, `pull --rebase --autostash`, `step 6 says what to run`, `Nothing else here brings the default branch up to date`, `never merge/rebase/reset`.
- [ ] **Step 2: Edit** the files as listed; Read each section before editing so the area rules load.
- [ ] **Step 3: Run** `python3 scripts/reference-parts.py generate && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && ./scripts/check-docs.sh --root . && python3 scripts/validate-catalog.py` — expected: PASS, no new warning.
- [ ] **Step 4: Record the after-counts**; every remaining hit of an old phrase is rewritten, or is history in a `CHANGELOG.md` and named in the commit message.
- [ ] **Step 5: Commit** `feat(workflows-core): commit-artifacts settles a rejected push by replay; scan hands over register.py (LC11)`.

### Task 6: The sweep, the rationale, and the release

**Files:**
- Modify: `docs/maintainers/rationale.md` — `#specs-push-scope`'s refused bullet *Rebasing the plugin's session-file commits onto a diverged default branch* retired in place with the measured reasons (cite `docs/superpowers/verification/2026-10-27-lc11-measurements/`); its "A branch that has already diverged is not rebased"; `#session-branch`'s account of `union`.
- Modify: every docs page that states the push rule or `union` — find them by subject: `grep -rln 'pull --rebase\|union\|never rebases\|takes them in\|diverged' plugins/*/docs`, then read each hit — starting with the `workflows-core` references page and the two `security-workflows` docs pages.
- Modify: `plugins/workflows-core/.claude-plugin/plugin.json`, `plugins/security-workflows/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, both `CHANGELOG.md`s (and any dependent whose docs page changed), `.claude/rules/plugin-updates-coupling.md` (1.66.0 with security-workflows 0.7.0: an older scan passes no `register_rebuild`, so a register both sides changed refuses; an older `workflows-core` reads no such input).
- Modify: `docs/superpowers/to-fix.md` (delete LC11), `docs/superpowers/to-test-on-real-project.md` (a section for this release: spec §4's two live re-tests).

- [ ] **Step 1: Sweep** by subject, not wording (claim-sweep refinements 1–8): every sentence across the scope that says the plugin never takes in the remote's commits, never rebases, that a diverged branch is the user's to bring up to date, or that `union` keeps both sides' entries; record before/after counts per phrase.
- [ ] **Step 2: Edit** the files above.
- [ ] **Step 3: Run the full gate chain** — every `run:` step of `.github/workflows/validate-catalog.yml`, in order, as one `&&` chain, from inside the worktree — then `ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .`; read both exit codes. Expected: both 0.
- [ ] **Step 4: Commit** `docs(workflows-core): LC11 sweep, rationale, release workflows-core 1.66.0 / security-workflows 0.7.0`.

### After Task 6 (the controller, not an implementer)

- A whole-branch Opus review of `main..iv-gu/lc11-design`, its findings fixed as new commits and re-reviewed.
- The verification record, written last (`CLAUDE.md` § Editing discipline): `docs/superpowers/verification/2026-10-27-lc11-measurements/README.md` extended with the build's selftest results and the SDD rulings and review verdicts, before the scratch workspace goes.
- The user's approval before the push and the pull request.

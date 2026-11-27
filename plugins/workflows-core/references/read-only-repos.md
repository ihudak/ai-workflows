# Read-only repository mounts (shared reference)

The AI container mounts repositories from the host, and some arrive **read-only** — verified 2026-08-11, 2 of 12 clones under `/workspace` are (`docs` and a requirements repository). Every agent that prepares a clone before reading it must work on those mounts rather than fail on them.

This file is the single source of truth for that behavior, and, in §0, for the test that admits a repository taken from committed data or a workspace listing as a clone before any git call names it. Its consumers are not listed here, so that no copy of the list goes stale: re-derive them with `grep -l 'read-only-repos' plugins/*/agents/*.md plugins/*/commands/*.md plugins/*/references/*.md plugins/*/references/*/*.md`, less this file. Two of them, `code-scanner` and `diff-summarizer`, also emit the §6 `prep` block; the other agents return a digest or a finding instead, and `docs-grounder` consumes §1–§4 only. §3 also defines, for these callers, the default branch they switch onto or cut a branch from (**A switch takes the name**), and how a missing local copy of it is made before the switch (**A switch never makes the branch**): `code-scanner`'s and `diff-summarizer`'s writable refresh, and `/document`, `/docs-profile`, `/docs-brand`, `/docs-init`, `/docs-write` and `/docs-verify` where each bases a branch in a docs repository. Two ladders stay outside it, each with its own reason: `dev-workflows:code-handoff` §2.8 adds `develop` for the code-changing commands, and `specs-repo-git.md` §3.2 serves the specs repository.

**Nothing here restricts a writable mount.** `git switch` and `git pull --ff-only` remain sanctioned prep on a writable clone — they change which committed revision is present, not the content of it. §2's skips and §5's escalation are for a read-only mount. A writable run reaches more of this file than §1's detection: §3's chain, which a writable caller that switches onto the default branch follows for that branch's name; §3's three recorded facts and §6's `prep` block, which `code-scanner` and `diff-summarizer` report on every run, `read_only: false` included; and §7's caller contract, which binds a caller on any mount. **And §4's reading at the ref serves a writable clone too**: its primitives write nothing, so a reader of a pinned commit may use them on any mount, and `code-scanner` uses them on a writable clone where its brief sets `refresh.read_default_by_ref` — a **read by ref** of the default branch's tip, for a checkout that must stay where it is: after one capped fetch and a capped `git remote set-head origin --auto`, it follows §3's chain for the ref and reads through §4's ref primitives, never the working tree (§4, *A writable clone read by ref*).

## 0. The clone test

**A repository a run takes from committed data, or from a listing of `${REPOS_PATH:-/workspace}`, is a clone only where it passes the clone test**: `test -e '<path>/.git'` succeeds — made before any git call names the path — and `git -c safe.bareRepository=explicit -C '<path>' rev-parse --show-toplevel` then exits 0, printing the path's resolved path. Committed data is a path a committed file records — a docs profile's `source_repos[].path`, a resume pointer's repository; a listing is the directories one level under each entry of `${REPOS_PATH:-/workspace}` that a run reads for code repositories, or for the documentation repository its command works in. **A slug→clone map makes the first part of the test before its one git call per directory**: a directory where `test -e '<dir>/.git'` fails is skipped before any git call names it, and the call that reads its slug is written `git -c safe.bareRepository=explicit -C '<dir>' remote get-url origin`. **Every path these forms write is single-quoted, each `'` it holds written `'\''`** — here and at every caller that writes them — so a quote, a `$(…)` or a backtick in a path a committed file records, or in a directory's name, ends no quoting and runs nothing. The specs repository, `${DOCS_PATH:-/workspace/docs}`, the session's own repository and a path the operator typed are resolved by their commands' own rules, not by this test.

**Why `.git` first.** A directory laid out as a repository's git directory — `HEAD`, `objects/`, `refs/`, and a `config` naming the directory as its own work tree — can be committed into any repository, and git run in it reads that committed `config`: a `git status` there runs the command its `core.fsmonitor` names, and `remote get-url origin` prints whatever URL it records, so it matches any slug (measured on git 2.53, in a clone of a repository that commits one). Git tracks no path named `.git`, so no committed tree supplies one; and `-c safe.bareRepository=explicit` refuses to read such a directory as a repository — git exits 128, `cannot use bare repository`, and runs nothing. A git older than 2.38, which has no such setting, ignores it, and the `.git` test alone holds there.

**An agent handed a clone.** `code-scanner` and `diff-summarizer` make the test's first part themselves: where `repo_path` holds no `.git` of its own, each returns `REPO_MISSING` before any git call names the path. They write every git call they make there — the calls §1–§4 of this file name among them — as `git -c safe.bareRepository=explicit -C "<repo_path>"`, so a directory a caller admitted without this test runs nothing its committed `config` names.

## 1. Detection

Before any git call that writes:

```
test -w "<repo_path>" && test -w "<repo_path>/.git"
```

Either test failing ⇒ **read-only mode**. Secondary trigger: any git command failing with an error containing `Read-only file system` ⇒ enter read-only mode and retry there, rather than returning `REFRESH_BLOCKED`.

A false positive is benign: the agent then reads at `origin/<default-branch>`, which is what a caller passing `switch_to_default_branch: true` or `refresh.pull: true` asked for anyway.

## 2. What read-only mode skips

- `git fetch`, `git pull`, `git switch` and the `git branch` calls that make a missing local branch before it (§3, *A switch never makes the branch*), `git remote set-head` — all write.
- **The dirty-tree gate.** A dirty working tree is irrelevant when the working tree is never mutated, so read-only mode NEVER returns `DIRTY_TREE`.

Read-only mode is not a failure. It NEVER returns `REFRESH_BLOCKED` on its own; that status stays reserved for a genuine failure — §3's chain exhausted, or §4's read primitives all failing.

## 3. Resolving the ref without writing

In order, stopping at the first that succeeds:

1. `git -C "<repo_path>" symbolic-ref --quiet --short refs/remotes/origin/HEAD` — `--quiet` is
   required, or a clone whose `origin/HEAD` is unset leaks `fatal: ref refs/remotes/origin/HEAD is not
   a symbolic ref` into the run's output. **Before any command names it, the name must be in the safe
   class**, `^[A-Za-z0-9_][A-Za-z0-9._/@+-]*$` — the class `specs-repo-git.md` §3.2 holds the specs
   repository's branch names to: git allows `$`, `(`, `)`, `;`, a backtick, a quote, `|` and `&` in a
   branch name, and every command that wrote this one, the probe below first, would run what it holds.
   Test it with a program handed the name as one single-quoted argument, each `'` it holds written
   `'\''`, `<name>` being the name without its `origin/`:
   `python3 -I -c 'import re, sys; sys.exit(0 if re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9._/@+-]*", sys.argv[1], re.ASCII) else 1)' '<name>'`, which exits 0
   where the name is in the class — never with a here-document, which a line of a name a person typed,
   or one a pattern built, could end, running the lines after it. Where it fails, rung 1 has failed —
   go on to rung 2, and never print the name. **It succeeds only where the ref it prints exists:**
   `git -C "<repo_path>" rev-parse --verify --quiet origin/<name> >/dev/null`, with `origin/<name>`
   what it printed. Where that probe fails, rung 1 has failed; go on to rung 2. A remote that renames
   its default branch — `master` to `main` — and a clone that then fetches with `--prune` leave
   `origin/HEAD` naming a branch the remote deleted: rung 1 still prints `origin/master` and exits 0,
   while `origin/master` is gone and `origin/main` is what rung 2 finds.
2. `git -C "<repo_path>" rev-parse --verify --quiet origin/main >/dev/null`
3. `git -C "<repo_path>" rev-parse --verify --quiet origin/master >/dev/null`

**Rungs 2–3 are existence probes, not name sources.** `rev-parse` prints a 40-character SHA, so a
caller that takes its stdout records a SHA where §6 defines a read-only `scanned_ref` as a ref *name* (`origin/main`).
Redirect the output and use the literal name you probed — the same rule
`dev-workflows:code-handoff` §2.8 states for its own ladder.

`git remote set-head origin --auto` is **not** part of this chain — it writes. An exhausted chain is a genuine `REFRESH_BLOCKED` with reason `cannot resolve default branch on a read-only mount`.

Then record three facts, all pure reads:

- `git -C "<repo_path>" log -1 --format=%cI <ref>` → `ref_committed_at`
- `git -C "<repo_path>" rev-list --left-right --count <ref>...HEAD` → `behind` then `ahead`, tab-separated
- `git -C "<repo_path>" rev-parse --abbrev-ref HEAD` → the working-tree branch name — `HEAD`, as for a detached HEAD, where the name is outside the safe class (*Branch names*, below)

**Branch names.** Every branch name a run reads from a repository is held to the safe class rung 1 gives, `^[A-Za-z0-9_][A-Za-z0-9._/@+-]*$`: a default branch's, wherever it is resolved; HEAD's, wherever a command, agent or reference reads it (`branch --show-current`, `symbolic-ref --short HEAD`, `rev-parse --abbrev-ref HEAD`); and each name a listing of branches prints, wherever a command, agent or reference reads one. **A listing prints each ref whole**, `git for-each-ref --format='%(refname)'` over `refs/heads` or `refs/remotes`, or with `%(refname:lstrip=<n>)`, never with `%(refname:short)`, which prints `heads/<name>` or `remotes/origin/<name>` wherever a tag or another ref shares the short name, nor as `git branch --list` or `git branch -r` print by default, each name indented and decorated (`* `, `+ `, `origin/HEAD -> origin/main`); each name is tested on its own, any `refs/heads/` or `refs/remotes/origin/` the listing printed taken off first, the rest being the name. Test it as rung 1 does, with the program handed the name as one argument, before any command names it. A default branch's name outside the class counts as unresolved, and the reader's own fallback goes on, as rung 1's does. HEAD on a branch whose name is outside the class counts as detached: where the reader records or switches back to a detached HEAD's commit, `git -C "<repo_path>" rev-parse HEAD`, it does so here, and where it records `HEAD` or `detached`, so here. A listed name outside the class is passed over, as if the listing had not printed it, and no command names it. Such a name is never printed, nor written into a stop or a report: a field or record that would hold HEAD's holds the detached form its reader already uses — the commit, `HEAD` or `detached` — and text that would name any of them reads `a branch whose name is outside the safe class` in its place, a reader that says what a listing held counting each listed name passed over that way.

**A switch takes the name; a read may take the ref.** The chain yields a **ref**: rung 1 prints
`origin/<name>` — `origin/main` — and rungs 2–3 probe `origin/main` and `origin/master`. A caller that
only **reads** a tree, a file or a log may use that ref as it stands, as §4 does. A caller that
**switches to** the default branch, or **cuts a branch from** it, uses the branch's **name**: rung 1's
output with its leading `origin/` removed, or the literal `main` or `master` whose ref rung 2 or 3
found. The ref will not do in its place: `git switch origin/main` exits 128 (*"fatal: a branch is
expected, got remote branch 'origin/main'"*), and `git switch -c <new> origin/main` sets `<new>` to
track `origin/main`, where a branch cut from `main` tracks nothing under git's default `branch.autoSetupMerge`. Such a caller is on a writable
clone — read-only mode switches nothing (§2) — so it may go further than this chain: where rung 1
fails, run `git remote set-head origin --auto` and retry rung 1 before rungs 2–3 — it resets an unset
`origin/HEAD` and a dangling one alike to the branch the remote names now — or fall back past rung 3
when the chain is exhausted. Neither is part of the chain, and a caller that does either says so where
it cites this rule. A read by ref on a writable clone (§4, *A writable clone read by ref*) runs that `git remote set-head
origin --auto` too, capped, before the chain rather than where rung 1 fails, and reads at the ref the
chain then yields.

**A switch never makes the branch.** Where no local `<name>` exists — `git -C "<repo_path>" rev-parse --verify --quiet refs/heads/<name>` prints nothing — a caller that switches to the default branch makes it first, from the ref the chain found, with no configuration write: `git -C "<repo_path>" branch --no-track <name> origin/<name>`. It then sets the upstream best-effort, `git -C "<repo_path>" branch --set-upstream-to=origin/<name> <name>`, whose failure — a `.git/config` that cannot be written — moves nothing and stops nothing, and only then switches, `git -C "<repo_path>" switch --no-guess <name>`. Where it then brings the branch up to date, it names the source, `git -C "<repo_path>" pull --ff-only --no-rebase origin <name>`, since a branch made where `.git/config` cannot be written has no upstream for a bare `git pull` to read, which exits 1 there for want of tracking information. A switch left to make the branch itself takes git's `--guess`, which writes the upstream as it switches, and where `.git/config` cannot be written — a container that mounts it read-only — git creates the branch, moves the index and the working tree onto its tree, then fails on that write and exits 1 with HEAD where it was: a staged reversal of the branch HEAD stands on, which reads as a switch refused with nothing moved (measured on git 2.43, with `.git/config` held locked). `git switch -c <new> origin/main` fails the same way there, its tracking being a write too. Under this form a switch git refuses moves nothing; the local `<name>` made for it stays at `origin/<name>`, holding nothing of anyone's. **Nor does the cut that follows make an upstream**: a caller cuts its branch from the default branch with `git -C "<repo_path>" switch --no-track -c <new>`, since a user's `branch.autoSetupMerge=always` makes even a branch cut at HEAD track the branch HEAD stands on, and that write, where `.git/config` cannot be written, leaves the new branch made — and, from a local start whose tree differs, the index and the working tree moved — with HEAD where it was and exit 1. `--no-track` changes nothing under git's default setting.

## 4. Reading at the ref

Two write-free scan targets:

- **The working tree**, with the native `Grep` / `Glob` / `Read` tools.
- **The ref**, via git plumbing that never consults or writes the index:
  - enumerate — `git -C "<repo_path>" ls-tree -r --name-only <ref>`
  - search — `git -C "<repo_path>" grep -n <pattern> <ref> -- <pathspec>`
  - read — `git -C "<repo_path>" show <ref>:<path>`

**When HEAD is already at the ref and the working tree is clean — `git -C "<repo_path>" rev-parse HEAD` equals `git -C "<repo_path>" rev-parse <ref>`, and `git --no-optional-locks -C "<repo_path>" status --porcelain` prints nothing and exits 0 — scan the working tree natively.** The content is identical and the native tools are better, so the common read-only case costs nothing extra. **HEAD at the ref is not enough on its own**: a read-only mount still carries whatever the host left uncommitted, and a line read from the working tree there is one no commit holds, cited as if it were at the ref. `--no-optional-locks` keeps `status` from trying to refresh the index, which a read-only mount refuses. **A non-zero exit counts as dirty**: an index the mount does not let git read makes `status` exit 128 with nothing on its standard output, which an emptiness test alone would take for a clean tree.

Otherwise — HEAD elsewhere, or a dirty tree — read at the ref. If `git grep <tree-ish>` is unavailable or errors, fall back to `git show`-per-file over an `ls-tree` shortlist. If that also fails, return `REFRESH_BLOCKED` with the one-line git error.

**A writable clone read by ref.** The ref primitives write nothing, so they read a writable clone as well as a read-only one. `code-scanner` reads one that way where its brief sets `refresh.read_default_by_ref` — the session's own repository on a feature branch, say, whose checkout is someone's work in progress — and its step 2 says how: one capped `git fetch --quiet origin`, whose failure leaves the ref as last fetched rather than stopping the scan, and a capped `git remote set-head origin --auto` before §3's chain, whose failure only leaves the chain to resolve the ref without it — the two writes, which move only remote-tracking refs; §3's chain for the ref; no `git switch`, no `git pull` and no dirty-tree gate; and every read through the ref primitives above, never the working tree — not even where HEAD is at the ref and the tree is clean, a shortcut this read does not take, since a working tree someone is editing can change while the scan reads it. §5's escalation does not apply: a writable clone can fetch, so a ref the fetch could not refresh shows as `prep.refreshed: false` with the failure named in `prep.refresh_note`, and `head_divergence.ahead > 0` is the work in progress the read exists to leave out.

## 5. When to escalate

Escalate to the caller — which prompts the user per the `Read-only mount — ref stale or diverged` entry in `escalation-rules.md` — when **either** holds:

- `ref_committed_at` is more than **14 days** old — the host has not fetched recently, so the ref itself is stale; or
- `head_divergence.ahead > 0` — the working tree carries commits the ref does not, so local work is invisible at the scanned ref.

`head_divergence.behind > 0` alone is **silent**: the scan reads the ref, so being behind locally changes nothing. On a read-only mount sitting at the default branch with a recent ref, the run proceeds with no prompt.

## 6. Output contract

`code-scanner` and `diff-summarizer` report these four fields in their `prep` block, always present so a caller never branches on absence:

```yaml
prep:
  read_only:        true | false
  scanned_ref:      <ref name, e.g. "origin/main"; on a writable mount read by ref, the default ref it read, e.g. "origin/main"; on any other writable mount, the branch the prep left checked out — the default branch where it switched onto it, else the one it found — or HEAD's commit where HEAD is detached, or on a branch outside §3's *Branch names* class>
  ref_committed_at: <ISO-8601 timestamp of the ref's newest commit>
  head_divergence:  { branch: <working-tree branch>, ahead: <n>, behind: <n> }
```

`docs-grounder` follows §1–§4 (read-only detection, what to skip, ref resolution, reading at the ref) but returns a digest — `status` / `retrieval` / `docs_references` / `docs_challenges` / `notes` — not a `prep` block; its staleness signal is the 14-day clause in `docs-grounding.md` instead.

Every path an agent returns keeps its documented meaning — relative to the repo root — and denotes content **at `scanned_ref`**, save the uncommitted changes of a writable working tree `code-scanner` read, which no ref holds; §7 says how a caller records them. A read by ref (§4, *A writable clone read by ref*) reads no working tree, so every path it returns is at `scanned_ref` exactly. **`diff-summarizer` reads no working tree** — it diffs the refs it is given — so on a writable mount its `scanned_ref` says only where HEAD stood, and no caller reads it there.

## 7. Caller contract

A caller that reads repository files directly, rather than through one of these agents, must first confirm `HEAD` is at the remote default ref — or cite the content via `scanned_ref` (`git -C "<repo_path>" show <scanned_ref>:<path>`) where `scanned_ref` is the default ref: on a read-only mount, after a read by ref, or after a prep that switched onto the default branch. On a writable mount whose prep neither switched nor read by ref, `scanned_ref` names whatever branch was checked out, which may be unmerged too. A working tree on an unmerged branch is not released behavior, and citing it as current is the failure this reference exists to prevent.

**A caller that records the ref a scan read — to cite it later, or to measure drift from it — records the commit, never the name.** `scanned_ref` names a branch or a remote ref, and both move: a month later the name points somewhere else, and the claim made against it can no longer be checked. Take `git -C "<repo_path>" rev-parse <scanned_ref>` as soon as the agent returns, and record that. **And on a writable mount whose working tree the agent read — every writable `code-scanner` scan but a read by ref, which reads none — record what the commit does not hold**: where `git --no-optional-locks -C "<repo_path>" status --porcelain` prints anything or exits non-zero, the working tree the agent read may have carried uncommitted changes, so `with uncommitted changes` goes beside the commit. After a read by ref, the commit is the whole record, whatever the working tree holds.

## 8. Hard rules

- NEVER edit, create, or delete files under `repo_path`. NEVER commit, cherry-pick, reset, rebase, or force.
- NEVER write to `.git` in read-only mode — that includes `git remote set-head`, `git fetch`, `git pull`, and `git switch`.
- NEVER delete an `index.lock`.
- NEVER make HTTPS / REST calls to any git host. All work is on the local clone.
- Read-only mode is never fatal: it degrades to reading at the ref and reports what it did.

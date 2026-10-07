# Read-only repository mounts (shared reference)

The AI container mounts repositories from the host, and some arrive **read-only** — verified 2026-08-11, 2 of 12 clones under `/workspace` are (`docs` and a requirements repository). Every agent that prepares a clone before reading it must work on those mounts rather than fail on them.

This file is the single source of truth for that behavior. Consumers: `code-scanner`, `diff-summarizer`, `docs-grounder`, `code-grounder` and `grounding-verifier` — the first two also emit the §6 `prep` block; the other three return a digest or a finding instead, and `docs-grounder` consumes §1–§4 only. §3 also defines, for these callers, the default branch they switch onto or cut a branch from (**A switch takes the name**): `code-scanner`'s and `diff-summarizer`'s writable refresh, and `/document`, `/docs-profile`, `/docs-brand` and `/docs-init` where each bases a branch in a docs repository. Two ladders stay outside it, each with its own reason: `dev-workflows:code-handoff` §2.8 adds `develop` for the code-changing commands, and `specs-repo-git.md` §3.2 serves the specs repository.

**Nothing here restricts a writable mount.** `git switch` and `git pull --ff-only` remain sanctioned prep on a writable clone — they change which committed revision is present, not the content of it. §2's skips and §5's escalation are for a read-only mount. A writable run reaches more of this file than §1's detection: §3's chain, which a writable caller that switches onto the default branch follows for that branch's name; §3's three recorded facts and §6's `prep` block, which `code-scanner` and `diff-summarizer` report on every run, `read_only: false` included; and §7's caller contract, which binds a caller on any mount.

## 1. Detection

Before any git call that writes:

```
test -w "<repo_path>" && test -w "<repo_path>/.git"
```

Either test failing ⇒ **read-only mode**. Secondary trigger: any git command failing with an error containing `Read-only file system` ⇒ enter read-only mode and retry there, rather than returning `REFRESH_BLOCKED`.

A false positive is benign: the agent then reads at `origin/<default-branch>`, which is what a caller passing `switch_to_default_branch: true` or `refresh.pull: true` asked for anyway.

## 2. What read-only mode skips

- `git fetch`, `git pull`, `git switch`, `git remote set-head` — all write.
- **The dirty-tree gate.** A dirty working tree is irrelevant when the working tree is never mutated, so read-only mode NEVER returns `DIRTY_TREE`.

Read-only mode is not a failure. It NEVER returns `REFRESH_BLOCKED` on its own; that status stays reserved for a genuine failure — §3's chain exhausted, or §4's read primitives all failing.

## 3. Resolving the ref without writing

In order, stopping at the first that succeeds:

1. `git -C "<repo_path>" symbolic-ref --quiet --short refs/remotes/origin/HEAD` — `--quiet` is
   required, or a clone whose `origin/HEAD` is unset leaks `fatal: ref refs/remotes/origin/HEAD is not
   a symbolic ref` into the run's output. **It succeeds only where the ref it prints exists:**
   `git -C "<repo_path>" rev-parse --verify --quiet origin/<name> >/dev/null`, with `origin/<name>`
   what it printed. Where that probe fails, rung 1 has failed; go on to rung 2. A remote that renames
   its default branch — `master` to `main` — and a clone that then fetches with `--prune` leave
   `origin/HEAD` naming a branch the remote deleted: rung 1 still prints `origin/master` and exits 0,
   while `origin/master` is gone and `origin/main` is what rung 2 finds.
2. `git -C "<repo_path>" rev-parse --verify --quiet origin/main >/dev/null`
3. `git -C "<repo_path>" rev-parse --verify --quiet origin/master >/dev/null`

**Rungs 2–3 are existence probes, not name sources.** `rev-parse` prints a 40-character SHA, so a
caller that takes its stdout records a SHA where §6 defines `scanned_ref` as a ref *name* (`origin/main`).
Redirect the output and use the literal name you probed — the same rule
`dev-workflows:code-handoff` §2.8 states for its own ladder.

`git remote set-head origin --auto` is **not** part of this chain — it writes. An exhausted chain is a genuine `REFRESH_BLOCKED` with reason `cannot resolve default branch on a read-only mount`.

Then record three facts, all pure reads:

- `git -C "<repo_path>" log -1 --format=%cI <ref>` → `ref_committed_at`
- `git -C "<repo_path>" rev-list --left-right --count <ref>...HEAD` → `behind` then `ahead`, tab-separated
- `git -C "<repo_path>" rev-parse --abbrev-ref HEAD` → the working-tree branch name

**A switch takes the name; a read may take the ref.** The chain yields a **ref**: rung 1 prints
`origin/<name>` — `origin/main` — and rungs 2–3 probe `origin/main` and `origin/master`. A caller that
only **reads** a tree, a file or a log may use that ref as it stands, as §4 does. A caller that
**switches to** the default branch, or **cuts a branch from** it, uses the branch's **name**: rung 1's
output with its leading `origin/` removed, or the literal `main` or `master` whose ref rung 2 or 3
found. The ref will not do in its place: `git switch origin/main` exits 128 (*"fatal: a branch is
expected, got remote branch 'origin/main'"*), and `git switch -c <new> origin/main` sets `<new>` to
track `origin/main`, where a branch cut from `main` tracks nothing. Such a caller is on a writable
clone — read-only mode switches nothing (§2) — so it may go further than this chain: where rung 1
fails, run `git remote set-head origin --auto` and retry rung 1 before rungs 2–3 — it resets an unset
`origin/HEAD` and a dangling one alike to the branch the remote names now — or fall back past rung 3
when the chain is exhausted. Neither is part of the chain, and a caller that does either says so where
it cites this rule.

## 4. Reading at the ref

Two write-free scan targets:

- **The working tree**, with the native `Grep` / `Glob` / `Read` tools.
- **The ref**, via git plumbing that never consults or writes the index:
  - enumerate — `git -C "<repo_path>" ls-tree -r --name-only <ref>`
  - search — `git -C "<repo_path>" grep -n <pattern> <ref> -- <pathspec>`
  - read — `git -C "<repo_path>" show <ref>:<path>`

**When HEAD is already at the ref and the working tree is clean — `git -C "<repo_path>" rev-parse HEAD` equals `git -C "<repo_path>" rev-parse <ref>`, and `git --no-optional-locks -C "<repo_path>" status --porcelain` prints nothing — scan the working tree natively.** The content is identical and the native tools are better, so the common read-only case costs nothing extra. **HEAD at the ref is not enough on its own**: a read-only mount still carries whatever the host left uncommitted, and a line read from the working tree there is one no commit holds, cited as if it were at the ref. `--no-optional-locks` keeps `status` from trying to refresh the index, which a read-only mount refuses.

Otherwise — HEAD elsewhere, or a dirty tree — read at the ref. If `git grep <tree-ish>` is unavailable or errors, fall back to `git show`-per-file over an `ls-tree` shortlist. If that also fails, return `REFRESH_BLOCKED` with the one-line git error.

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
  scanned_ref:      <ref name, e.g. "origin/main"; on a writable mount, the branch the prep left checked out — the default branch where it switched onto it, else the one it found — or HEAD's commit where HEAD is detached>
  ref_committed_at: <ISO-8601 timestamp of the ref's newest commit>
  head_divergence:  { branch: <working-tree branch>, ahead: <n>, behind: <n> }
```

`docs-grounder` follows §1–§4 (read-only detection, what to skip, ref resolution, reading at the ref) but returns a digest — `status` / `retrieval` / `docs_references` / `docs_challenges` / `notes` — not a `prep` block; its staleness signal is the 14-day clause in `docs-grounding.md` instead.

Every path an agent returns keeps its documented meaning — relative to the repo root — and denotes content **at `scanned_ref`**, save, on a writable mount, the uncommitted changes of the working tree it read, which no ref holds; §7 says how a caller records them.

## 7. Caller contract

A caller that reads repository files directly, rather than through one of these agents, must first confirm `HEAD` is at the remote default ref — or cite the content via `scanned_ref` (`git -C "<repo_path>" show <scanned_ref>:<path>`). A working tree on an unmerged branch is not released behavior, and citing it as current is the failure this reference exists to prevent.

**A caller that records the ref a scan read — to cite it later, or to measure drift from it — records the commit, never the name.** `scanned_ref` names a branch or a remote ref, and both move: a month later the name points somewhere else, and the claim made against it can no longer be checked. Take `git -C "<repo_path>" rev-parse <scanned_ref>` as soon as the agent returns, and record that. **And on a writable mount, record what the commit does not hold**: where `git --no-optional-locks -C "<repo_path>" status --porcelain` prints anything, the working tree the agent read carried uncommitted changes, so `with uncommitted changes` goes beside the commit.

## 8. Hard rules

- NEVER edit, create, or delete files under `repo_path`. NEVER commit, cherry-pick, reset, rebase, or force.
- NEVER write to `.git` in read-only mode — that includes `git remote set-head`, `git fetch`, `git pull`, and `git switch`.
- NEVER delete an `index.lock`.
- NEVER make HTTPS / REST calls to any git host. All work is on the local clone.
- Read-only mode is never fatal: it degrades to reading at the ref and reports what it did.

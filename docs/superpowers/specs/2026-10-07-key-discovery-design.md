# Pull-request discovery by key — design

**Date:** 2026-10-07 · **Plugins:** docs-workflows and workflows-core → the next free minors. The script in § 2 is shared byte for byte with the family's other editions, which adopt it under their own designs.

## Goal

`/document` and `/release-notes` (with diff grounding on) find a feature's code in two sources: the `implementation.md` record and a whole-key scan of commit messages (`workflows-core:implementation-format` §4). Work whose commits name no key — a pull request whose title carries the key while its commits do not — is found by neither, and only the report-only probe hints at it.

After this change the scan runs through one tested script, and — where a scanned clone is on GitHub and `gh` is installed and logged in — the commands also read GitHub pull requests whose title or description names a key, through the commits those pull requests landed. Without `gh`, nothing changes.

## Facts this design rests on (measured 2026-10-07)

1. **The scan today** (`workflows-core:implementation-format` §4): one `git log --no-merges -E -i` per repository with one `--grep` per token, each wrapped in `(^|[^A-Za-z0-9_-])…([^A-Za-z0-9_-]|$)` with its ERE metacharacters escaped, run by the model from prose; a reach report (`rev-list --no-merges --count HEAD`, matched); and a report-only unanchored probe on a repository the scan left at zero matches.
2. **`diff-summarizer` is pure local git.** It takes `refs[]` elements only, `{branch_from, branch_to, title}`, and a commit only the scan found is `{<sha>, <sha>^}`.
3. **`/release-notes` bounds a note by read sets.** A commit enters a note's read set only where its diff was read; a later run drops every commit an earlier note covering a record read, and the commits whose tokens matched that record (`implementation-format` §4, `references/release-note-types.md` §1).
4. **A whole-key scan of many clones is cheap.** One whole-key `git log --all --no-merges` over 22 clones — one of them holding 102,875 commits — took 2.0 s wall time.
5. **`gh search prs` reaches what the design needs.** With two `--owner` flags and the query `<K1> OR <K2>`, it returned the seven pull requests naming either key across three repositories, with states `open` and `merged` and full bodies. **The `OR` terms must be separate arguments:** the same query as one quoted string returned `[]`. GitHub allows five `OR` operators per query, so six keys per query.
6. **Search matching is loose.** A search for one key also returned a pull request whose title named neither it nor anything like it; a whole-key test of each hit's title and body is required.
7. **The search API allows 30 requests a minute** (`gh api rate_limit`); `gh pr view` goes through GraphQL (5,000 an hour).
8. **`gh pr view` gives what a landing needs:** `state`, `headRefName`, `baseRefName`, `headRefOid`, `mergeCommit.oid`, `isCrossRepository`, and `commits[]` with each `oid` and `messageHeadline`. A merged pull request's merge commit had two parents in the local clone.
9. **SSH aliases hide GitHub.** `ssh -G <alias>` prints the real `hostname`; `workflows-core:phase-handoff` §2.6 already resolves aliases this way before calling `gh`, keeps every host other than `github.com`, maps `ssh.github.com` to `github.com`, and passes only a plain hostname to `ssh`.
10. **The family already runs `gh` where it wraps the API:** `workflows-core:phase-handoff` §2.6 and §3.5, `dev-workflows:code-handoff` §2.6, `workflows-core:architecture-promotion` §11.1. The commands' own rule is that a run never calls a forge's REST API directly over HTTPS.
11. **Bundled scripts carry a `--selftest`, run in CI** (`proposal-record.py`, `session-branch.py`, `secret-scan.py`, …).

## Decisions (agreed 2026-10-07)

- **K2 — GitHub is searched in the owners of the scanned clones**, not only the cloned repositories, so a pull request in a repository outside the scanned set is reported rather than unseen.
- **K3 — The `gh` layer is optional.** The commands stay complete without `gh`; with it, GitHub pull requests that name a key are read too.
- **K5 — One script.** `plugins/docs-workflows/scripts/key-discovery.py`, standard library only, with a `--selftest` in CI. It finds; it never reads a diff — `diff-summarizer` still does.

## Design

### 1. What stays as it is

- **The whole-key boundary**, case-insensitive, metacharacters escaped, and its refusal to reach a key inside a branch name.
- **Merge commits stay out of the scan** (`--no-merges`), for `workflows-core:implementation-format` §4's reasons.
- **Nothing is parsed out of a commit message or a pull request.** Every key searched for is one the run already holds; a pull request's number, branches and merge commit come from `gh`'s JSON.
- **`diff-summarizer` is unchanged.** A pull request reaches it only as the commits it landed.

### 2. The script — `scripts/key-discovery.py`

```
key-discovery.py scan --key <K> [--key <K> ...] --repo <clone> [--repo <clone> ...]
                      --scope head|default [--probe] [--no-github]
key-discovery.py --selftest
```

Exit 0 when it ran, whatever it found or failed to reach (each failure is a field of the JSON); exit 2 when it could not run — no `--key`, no `--repo`, a key that is empty or holds whitespace, a `--repo` that is not a directory, no `git` on `PATH`. It prints one JSON document on stdout and never writes a file, fetches, or changes a clone.

**The commit scan, per `--repo`:**

- **The ref.** `--scope head` scans `HEAD`. `--scope default` scans the origin's default branch, resolved by `workflows-core:read-only-repos` §3's chain — `refs/remotes/origin/HEAD`, else `origin/main`, else `origin/master` — and falls back to `HEAD`, saying so in the repository's `ref` field.
- **The log.** One `git -C <clone> log <ref> --no-merges --extended-regexp --regexp-ignore-case` with one `--grep` per key in the whole-key form, bounded at 60 s. Python re-tests each commit's full message against each key with the same pattern, case-insensitive, and records which keys it names.
- **The reach.** `git -C <clone> rev-list --no-merges --count <ref>` → `scanned`; the commits kept → `matched`.
- **The probe** (`--probe` only, and only where `matched` is 0): the same log with the keys bare — still escaped, unanchored — and without `--no-merges`, each hit reported by SHA, date and subject, minus any commit the GitHub layer below already accounts for (a found PR's merge commit or landed commits).
- A clone whose `git` call fails or times out gets an `error` and no commits; the others carry on.

**The GitHub layer** (unless `--no-github`):

1. **Which clones are on GitHub.** Each clone's `git remote get-url origin` is split into host and path as `workflows-core:phase-handoff` §2.6 does: an scp-like or `ssh://` host other than `github.com`, when it is a plain hostname (`^[A-Za-z0-9][A-Za-z0-9.-]*$`), is resolved through `ssh -G <host>`'s `hostname` line; `ssh.github.com` reads as `github.com`; an `http(s)://` host is kept as written. Only a host of exactly `github.com` with a path of exactly `<owner>/<repo>` qualifies; every other clone has `github: null`.
2. **Whether `gh` can search.** `gh` on `PATH`, and `gh auth status --hostname github.com` exiting 0. Otherwise `status: not-installed` or `not-authenticated`, and no search runs. No clone on GitHub → `status: no-github-clones`.
3. **The search.** The owners are the qualifying clones' owners, deduplicated. The keys go in batches of at most six; each batch is one `gh search prs --owner <O> [--owner <O> ...] --limit 1000 --json number,title,body,state,url,repository -- <K1> OR <K2> …`, the `OR`s as separate arguments, bounded at 30 s.
4. **The local test.** A hit is kept only where its title or body names a key whole, by the scan's pattern; the keys it names are recorded. The rest are dropped and counted (`dropped_loose`).
5. **The details.** For a kept PR in a repository one of the `--repo` clones holds, one `gh pr view <number> --repo <owner>/<repo> --json state,headRefName,baseRefName,headRefOid,mergeCommit,isCrossRepository,commits`, bounded at 30 s. A PR in a repository no clone holds is kept with `clone: null` and no details.
6. **The landing** (a merged PR whose merge commit the clone holds — `git cat-file -e <oid>^{commit}`):
   - two or more parents → `landed_as: merge`, `landed` = `git rev-list --reverse --no-merges <oid>^1..<oid>^2`;
   - one parent, and the PR's `commits[]` holds `n` > 1 entries whose `messageHeadline`s equal, in order, the subjects of the `n` first-parent commits ending at the merge commit → `landed_as: rebase`, `landed` = those `n` commits;
   - one parent otherwise → `landed_as: squash`, `landed` = the merge commit alone.

   A merged PR whose merge commit the clone lacks has `landed_as: null` and `reason: merge commit not in the clone`; an open or closed PR has neither.
7. **Failures.** A search that fails stops nothing: the layer reports `partial` with each failed batch's reason. A failure whose message names a rate limit stops the remaining searches and reports `rate-limited`. A `gh pr view` that fails leaves that PR without details and with a `reason`.

**Every scanned commit is tagged with the found PRs it landed in** (`prs`), and every landed commit the scan did not find — its own message names no key — is added with `via: pull-request`.

**Output:**

```json
{
  "keys": ["<K>", "..."],
  "scope": "head | default",
  "repos": [
    {"path": "<clone>", "ref": "<ref scanned>", "scanned": 0, "matched": 0,
     "github": "<owner>/<repo> | null", "error": null, "probe": []}
  ],
  "commits": [
    {"repo": "<clone>", "sha": "<40 hex>", "date": "<ISO 8601>", "subject": "<line>",
     "keys": ["<K>"], "via": "message | pull-request", "prs": ["<PR url>"]}
  ],
  "github": {
    "status": "ok | partial | rate-limited | off | not-installed | not-authenticated | no-github-clones",
    "detail": "<reason or null>", "owners": ["<owner>"], "queries": 0, "dropped_loose": 0,
    "prs": [
      {"url": "<url>", "owner": "<owner>", "repo": "<repo>", "number": 0, "title": "<title>",
       "state": "MERGED | OPEN | CLOSED", "keys": ["<K>"], "clone": "<clone> | null",
       "head_ref": "<name> | null", "base_ref": "<name> | null", "head_oid": "<sha> | null",
       "merge_commit": "<sha> | null", "cross_repository": false,
       "landed_as": "merge | squash | rebase | null", "landed": ["<sha>"], "reason": "<text> | null"}
    ]
  }
}
```

The script never passes a credential as an argument: `gh` reads its own login.

### 3. `/document` and `/release-notes`

**The scan moves into the script, unchanged in meaning.** Phase 3's "The scan" step runs

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/key-discovery.py" scan --scope head --probe \
  --key <token> … --repo <clone> …
```

with the same tokens (`workflows-core:implementation-format` §4's, for this run's scope) over the same repositories (those `implementation.md` names, or every clone under `$REPOS_PATH`). The GitHub owners searched are those of these scanned clones (K2, applied to the set this command scans). Its `commits` with `via: message` are today's scan result; its `repos[].scanned`/`matched` are today's reach report; its `repos[].probe` is today's probe. `workflows-core:implementation-format` §4 stays the authority on what the scan means; the script is how it runs.

**Merged pull requests add commits.** A found PR with `landed` commits contributes them: the ones the scan already found are tagged "via pull request #N", and the others — `via: pull-request`, whose own message names no token — join the scan's commits as commits only the scan found, each handed to `diff-summarizer` as `{branch_from: <sha>, branch_to: <sha>^}` like any other. Their tokens, for the note boundary, are the tokens their PR named. So `/release-notes`' read set and note boundary take them without change.

**Every other found PR is listed, never read:** open, closed, merged without its merge commit in the clone, or in a repository outside the scanned set — each by URL and reason, in a "Pull requests found but not read" report line.

**What `ai-workflows` now says about itself.** The commands' and `implementation-format`'s "nothing in this plugin reads a … pull-request API" and "no `gh` requirement" become: no pull-request API is required; where a scanned clone is on GitHub and `gh` is installed and logged in, GitHub's pull-request search is read through `gh`, which wraps the API. The rule that a run never calls a forge's REST API directly over HTTPS stands.

### 4. Testing

`key-discovery.py --selftest` builds throwaway repositories under a temporary directory and puts stub `gh` and `ssh` executables first on `PATH`, each answering from a canned table keyed by its arguments and logging its calls. It runs in CI in all three repositories, and asserts:

- the boundary: `ACME-7` matches `[ACME-7]`, `acme-7` and `ACME-7:`, and not `ACME-77`, `ACME-70-01`, `XACME-7` or `feat/ACME-7-x`; a key holding `.` matches only itself;
- merges are excluded from the scan and included in the probe; the probe runs only at zero matches and omits a found PR's commits;
- `--scope head` and `--scope default` read the right ref, and `default` without an origin falls back to `HEAD` and says so;
- reach counts, and a failing clone that leaves the others' results intact;
- seven keys make two queries, the `OR`s as separate arguments, with every owner passed;
- a loose hit is dropped and counted; a body-only hit is kept;
- an alias resolving to `github.com` qualifies, `ssh.github.com` reads as `github.com`, an Enterprise host and a Bitbucket path do not, and a host that is not a plain hostname never reaches `ssh`;
- `gh` absent, not logged in, a failing batch (`partial`) and a rate-limit message (`rate-limited`, no further queries);
- merge, squash and rebase landings; a merge commit the clone lacks; a PR in an uncloned repository;
- exit 2 for each refused input, and no credential in any logged argument.

Each edition's `check-docs.sh`, `check-id-grammar.sh`, `validate-catalog.py` and mermaid check stay green, and each branch gets one Opus whole-branch review before merge.

## Consumers to update (re-derive at execution)

- `plugins/docs-workflows/scripts/key-discovery.py` (new); `.github/workflows/validate-catalog.yml` (self-test step).
- `plugins/docs-workflows/commands/document.md`, `commands/release-notes.md` — the scan step, pull-request commits, the not-read list, the "no pull-request API" sentences, invariants, reports.
- `plugins/workflows-core/references/implementation-format.md` §4 — the pull-request layer.
- `plugins/docs-workflows/docs/…` command and reference pages; both CHANGELOGs; versions.

## Out of scope

- **Reaching a key inside a branch name.** `workflows-core:implementation-format` §4 declined it; that stands.
- **Other forges' pull-request search, and GitHub Enterprise.** A clone on another host is scanned for commits and never searched.
- **Open pull requests' content.** They are listed, never read: an open pull request is not work that reached the feature.

## Amendment — after the sibling edition's whole-branch review (2026-10-07)

The shared script changed under that review, and this edition follows it.

- **The specs and docs repositories are never code.** Their commits and pull requests carry the run's tokens by the family's own conventions, so read as code they would verify a requirement by its own text. The script takes `--exclude <clone>`: every `--repo` with an excluded clone's `origin` slug is left unscanned, every pull request in a repository of that name is dropped, and the output gains `excluded`. Both commands pass `$SPECS_PATH` and the docs repository; `workflows-core:implementation-format` §4's scan scope says so too.
- **Every clone's owner is searched**: a clone not picked for its slug goes as `--owner-of <clone>`.
- **Tokens are quoted as phrases** in the search; a batch that returns the 1000-hit limit makes the layer `partial`. `dropped_loose` counts pull requests; a rate limit keeps the earlier failures in `detail`; `not-authenticated` carries `gh auth status`'s last line.
- **The script cannot be broken by a commit message**: the log is read NUL-separated and an unparsable record skipped; any unexpected failure exits 2 with one line; git runs with `GIT_NO_LAZY_FETCH=1`; a rebase landing compares each commit's first line with the pull request's headline, an ellipsis-cut headline as a prefix.
- **Any failure counts as exit 2** in the commands — another exit, stdout that is not JSON, or the Bash tool's 600000 ms timeout.

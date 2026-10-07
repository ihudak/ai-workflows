# Key discovery

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

How `/document` (keyed mode) and `/release-notes` (with diff grounding on) run the commit scan `workflows-core:implementation-format` §4 defines, and the optional pull-request layer beside it, through one script: `${CLAUDE_PLUGIN_ROOT}/scripts/key-discovery.py`. That §4 stays the authority on what the scan means; this file says how it runs and what the two commands do with what it returns.

## 1. Run it

In Phase 3's diff-source step, once the slug→clone map is built and the tokens are known — §4's tokens for this run's scope, each read off a folder the run resolved or listed — in one shell block, with the Bash tool's timeout set to 600000 ms, since it reads every clone and asks GitHub once per pull request it keeps:

```bash
kd=$(command mktemp) && python3 "${CLAUDE_PLUGIN_ROOT}/scripts/key-discovery.py" scan --scope head --probe \
  --key <token> --key <token> … --repo <clone> --repo <clone> … \
  --exclude <specs repository> --exclude <docs repository> --owner-of <clone not picked> … > "$kd"; echo "exit=$? out=$kd"
```

Each token is its own `--key`. Each repository the scan covers — those `implementation.md` names, resolved through the map, or, when it names none, every clone in the map, one per slug by Phase 4's preference (a basename ending `-repo`, then `_repo` or `_fast`, then the alphabetically last) — is its own `--repo`; every other clone the map holds goes as `--owner-of`, so every GitHub owner a clone under `$REPOS_PATH` belongs to is searched, although only the scanned clones are read.

The JSON goes to a file of the run's own, never to the tool's output, which a large result would overflow: read the file the printed line names — the script indents it, so it reads line by line however large — and remove it with `rm -f` once this phase has taken what it needs.

**Never code: the specs repository and the docs repository.** Pass `--exclude <the specs repository>` — the top level of the PRD folder's repository, `git -C <PRD folder> rev-parse --show-toplevel` — and `--exclude <the docs repository>`: `/document`'s resolved `docs_repo_path`, and `/release-notes`' docs root, the one its documentation grounding resolved (`--docs <path>`, else `${DOCS_PATH:-/workspace/docs}`). Pass either only where it is a git checkout's top level and not a repository `implementation.md` names: documentation kept inside a code repository is that code's, and the code stays scanned. `--exclude` leaves out nothing for a path inside a repository, or outside any. The script leaves out every clone whose `origin` slug is one of theirs, a second clone of either included, and drops every pull request in a repository of that name: their commits and pull requests carry the run's tokens by the family's own conventions — the specs repository's artifact commits and handoff pull-request titles, the docs repository's squash subjects — and read as code they would verify a requirement by its own text.

`exit=0` with one JSON document in the file (§2) is the only success. Any other exit, a file that is not JSON, or a call the tool's timeout ended, means it could not run: run it once more with `--no-github` — the scan alone — and report the pull-request search as not run, with the first call's reason (its stderr line, or that it timed out). Only where that fails too, report it as the scan's result for every repository, and continue on the record alone.

**A clone mounted mid-run.** Where Phase 4 waits for a missing repository — "Mount the missing repo(s) now", "I'll clone it — wait" — or takes a path the user specifies for one, rebuild the map and run the script again over the new set, the new clone among the scanned ones; its result replaces the earlier one. It is cheap, and it is the only way the new clone's commits are scanned, and its pull requests given a `clone`.

The script fetches nothing and writes nothing: it reads each clone as it stands.

## 2. What it returns

- `excluded` — the slugs `--exclude` left out.
- `repos[]` — per clone: `path`, the `ref` scanned (`HEAD`), `scanned` (its non-merge commits), `matched`, `github` (`<owner>/<repo>`, or null where the clone is not on github.com), `error` (where it could not be read; `scanned` is then null), and `probe` — §4's unanchored probe, by SHA, date and subject, on a clone where `matched` is 0.
- `commits[]` — each non-merge commit on `HEAD` whose message names a token whole (`via: message`), and each commit a found pull request landed whose own message names none (`via: pull-request`): `repo` (the clone), `sha`, `date` (local time), `subject`, `keys` — the tokens its message names and those of every found pull request that landed it — and `prs`, the URLs of the found pull requests that landed it.
- `github` — `status` (`ok`; `partial` where a search failed, reached its 1000-hit limit, returned what the script cannot use, or ran out of its time budget; `rate-limited`; `not-installed`; `not-authenticated`; or `no-github-clones`), `detail` (each failure, or why `gh` cannot search), the `owners` searched, `queries`, `dropped_loose`, and `prs[]`: `url`, `owner`, `repo`, `number`, `title`, `state` (`MERGED`, `OPEN` or `CLOSED`), `keys`, `clone` (null where no scanned clone holds the repository), `head_ref`, `base_ref`, `head_oid`, `merge_commit`, `cross_repository`, `landed_as` (`merge`, `squash`, `rebase` or null), `landed` and `reason`.

## 3. The scan's result

- `commits[]` with `via: message` are exactly the scan §4 describes.
- `repos[].scanned` and `matched` are the scan's reach; a repository with an `error` was not read, and is reported as such, never as zero matches.
- `repos[].probe` is §4's report-only probe, less any commit a found pull request accounts for — its merge commit, or a commit it landed — which the run reads or lists under §4 below instead.

## 4. Pull requests — optional

Where a scanned clone's `origin` is on github.com — an SSH host alias resolved as `workflows-core:phase-handoff` §2.6 resolves it — and `gh` is installed and logged in, the script also searches the GitHub pull requests of every owner a clone under `$REPOS_PATH` belongs to for the tokens, and keeps one only where its title or body names a token whole: GitHub's own search matches loosely, even with each token quoted as a phrase, and `dropped_loose` counts the pull requests it dropped. Where `gh` is absent or logged out, `github.status` says so and nothing else changes.

- **A merged pull request that shipped and is its own** — its merge commit in the clone and on `HEAD`, its range bringing in no other branch's merges — contributes its `landed` commits: the branch's own commits for a merge commit, the one commit for a squash, the rebased run for a rebase. One the scan already found is that same commit, tagged with the pull request in `prs`. One whose own message names no token comes back `via: pull-request` and joins the scan's commits as a commit only the scan found — reported as unrecorded work like any other, and handed to `diff-summarizer` as `{branch_from: <sha>, branch_to: <sha>^}`.
- **A commit's tokens are its `keys`** wherever a rule reads them — `/release-notes`' note boundary among them: those its message names and those of every found pull request that landed it. A commit two pull requests landed carries the tokens of both.
- **Every other found pull request is listed, never read**: an open one; a closed unmerged one; a merged one whose merge commit the clone does not hold, or is not on `HEAD` (a pull request merged into a branch that never shipped); a release or promotion pull request that merges other branches onward (`reason: lands other branches' merges -- read by hand`); one the time budget left unviewed; and one in a repository no scanned clone holds (`clone: null`) — each by URL and its `reason`.

## 5. What the report says

- One `GitHub PR search:` line: `ok — <owners>, <queries> queries, <n> kept, <dropped_loose> loose matches dropped`, or the `status` and its `detail` — or "not run", with the first call's reason, where the `--no-github` retry ran.
- The merged pull requests read through their landed commits, each by URL with its commits' SHAs.
- The pull requests found but not read, each by URL and why.
- Left out as never code: the `excluded` slugs.
- Each repository the script could not read, by path and its `error`.
- Where the script could not run at all, its stderr line, or that it timed out.

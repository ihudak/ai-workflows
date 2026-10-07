# Key discovery

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

How `/document` (keyed mode) and `/release-notes` (with diff grounding on) run the commit scan `workflows-core:implementation-format` §4 defines, and the optional pull-request layer beside it, through one script: `${CLAUDE_PLUGIN_ROOT}/scripts/key-discovery.py`. That §4 stays the authority on what the scan means; this file says how it runs and what the two commands do with what it returns.

## 1. Run it

In Phase 3's diff-source step, once the slug→clone map is built and the tokens are known — §4's tokens for this run's scope, each read off a folder the run resolved or listed — in one shell block:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/key-discovery.py" scan --scope head --probe \
  --key <token> --key <token> … --repo <clone> --repo <clone> …
```

Each token is its own `--key`. Each repository the scan covers — those `implementation.md` names, resolved through the map, or, when it names none, every clone in the map, one per slug by Phase 4's preference (a basename ending `-repo`, then `_repo` or `_fast`, then the alphabetically last) — is its own `--repo`.

Exit 0 prints one JSON document (§2). Exit 2 means it could not run: report its stderr line as the scan's result for every repository, and continue on the record alone.

The script fetches nothing and writes nothing: it reads each clone as it stands.

## 2. What it returns

- `repos[]` — per clone: `path`, the `ref` scanned (`HEAD`), `scanned` (its non-merge commits), `matched`, `github` (`<owner>/<repo>`, or null where the clone is not on github.com), `error`, and `probe` — §4's unanchored probe, by SHA, date and subject, on a clone where `matched` is 0.
- `commits[]` — each non-merge commit on `HEAD` whose message names a token whole (`via: message`), and each commit a found pull request landed whose own message names none (`via: pull-request`): `repo` (the clone), `sha`, `date`, `subject`, `keys` (the tokens), and `prs` — the URLs of the found pull requests that landed it.
- `github` — `status` (`ok`, `partial`, `rate-limited`, `not-installed`, `not-authenticated` or `no-github-clones`), `detail`, the `owners` searched, `queries`, `dropped_loose`, and `prs[]`: `url`, `owner`, `repo`, `number`, `title`, `state` (`MERGED`, `OPEN` or `CLOSED`), `keys`, `clone` (null where no scanned clone holds the repository), `head_ref`, `base_ref`, `head_oid`, `merge_commit`, `cross_repository`, `landed_as` (`merge`, `squash`, `rebase` or null), `landed` and `reason`.

## 3. The scan's result

- `commits[]` with `via: message` are exactly the scan §4 describes.
- `repos[].scanned` and `matched` are the scan's reach.
- `repos[].probe` is §4's report-only probe, less any commit a found pull request accounts for — its merge commit, or a commit it landed — which the run reads or lists under §4 below instead.

## 4. Pull requests — optional

Where a scanned clone's `origin` is on github.com — an SSH host alias resolved as `workflows-core:phase-handoff` §2.6 resolves it — and `gh` is installed and logged in, the script also searches the GitHub pull requests of every owner the scanned clones belong to for the tokens, and keeps one only where its title or body names a token whole: GitHub's own search matches loosely, and `dropped_loose` counts the hits it dropped. Where `gh` is absent or logged out, `github.status` says so and nothing else changes.

- **A merged pull request whose merge commit the clone holds** contributes its `landed` commits — the branch's own commits for a merge commit, the one commit for a squash, the rebased run for a rebase. One the scan already found is that same commit, tagged with the pull request in `prs`. One whose own message names no token comes back `via: pull-request` and joins the scan's commits as a commit only the scan found — reported as unrecorded work like any other, and handed to `diff-summarizer` as `{branch_from: <sha>, branch_to: <sha>^}`. Its tokens, wherever a rule reads a commit's tokens — `/release-notes`' note boundary among them — are the tokens its pull request named (`keys`).
- **Every other found pull request is listed, never read**: an open one, a closed unmerged one, a merged one whose merge commit the clone does not hold (`reason`), and one in a repository no scanned clone holds (`clone: null`) — each by URL and why.

## 5. What the report says

- One `GitHub PR search:` line: `ok — <owners>, <queries> queries, <n> kept, <dropped_loose> loose matches dropped`, or the `status` and its `detail`.
- The merged pull requests read through their landed commits, each by URL with its commits' SHAs.
- The pull requests found but not read, each by URL and why.
- Where the script exited 2, its stderr line.

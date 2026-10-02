# diff-summarizer Handoff Format

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

## Input

```yaml
repo_path:   <absolute path to a local clone, e.g. /workspace/<repo-name>>
repo_url_slug: <repo slug, e.g. "cluster"; optional, enables upstream cross-check>
refs:                              # what implementation.md records, and commits only the scan found; the only element list
  - branch_from: <the feature branch, or the commit sha, this run wrote; or a commit only the scan found>
    branch_to:   <the base it was branched from; for a commit only the scan found, <sha>^>
    title:       <one line naming the work; optional>
context: |
  <what this repo's changes relate to — for documentation focus>
keys_hierarchy:   # optional; passed by caller to enable the key-commit fallback
  - <PRD-KEY>
  - <every EPIC- folder's key discovered by the folder read>
refresh:
  fetch: true   # default true
  pull:  false  # default false — a historical diff does not need the current branch tip;
                # pulling risks moving HEAD away from the commit we want to reach.
```

Refuse to run without `repo_path` and at least one element in **`refs`**.

**No `model_routing:` block is passed.** The caller pins this agent's tier with `model:` on the dispatch, and nothing in the agent reads a field of that block.

**`refs` is the shape the callers have, and the only one.** `workflows-core:implementation-format` §1
records `repo` / `branch` / `base` / `commit` / `pushed` — no URL, no host, no PR id — so there is no
host to route on and no forge to ask. The diff is taken directly
(`git -C <repo_path> diff <branch_to>...<branch_from>`, `branch_from` accepted as a commit sha, the
form both callers hand, `branch_to` read as `origin/<branch_to>` wherever the local branch is absent
or an ancestor of it) — except where `branch_from` has already landed on `branch_to`, which empties that range:
the agent then reads the merge that landed it (`<landing>^1...<branch_from>`), or, where a
fast-forward left no merge and `branch_from` is a single commit, that commit's own change. Where
the branch or the sha does not resolve, where a branch name or a merge commit landed with no merge to read, or where
a range changes no file, the agent's **Key-commit fallback** greps `keys_hierarchy` when the caller
supplied one. An empty range is never reported as resolved, save a single commit whose own change is empty.

When `repo_url_slug` is provided, before summarising run
`git -C <repo_path> remote get-url origin`, strip a trailing `.git`, and compare
the URL's last path segment to `repo_url_slug`. On mismatch, return
`status: REPO_MISSING` with a note naming both slugs — do NOT summarise the wrong
repository. When `repo_url_slug` is absent, trust `repo_path` as given.

## Output

```yaml
status: OK | REPO_MISSING | DIRTY_TREE | REFRESH_BLOCKED | NO_PRS_RESOLVED | PARTIAL

repo:       <repo name (last segment of repo_path)>
repo_path:  <absolute path>

prep:
  fetched:          true | false
  pulled:           true | false
  refresh_note:     <e.g. "fetched 3 new refs" | "read-only mount; resolved at origin/main" | "tree was dirty, refresh skipped">
  read_only:        true | false
  scanned_ref:      <ref name, e.g. "origin/main"; the default branch name when writable>
  ref_committed_at: <ISO-8601 timestamp of the ref's newest commit>
  head_divergence:  { branch: <working-tree branch>, ahead: <n>, behind: <n> }

per_pr:                        # one entry per input element, the key-commit fallback included
  - ref:            <"<branch_to>...<branch_from>">
    resolved_via:   local_ref | key_commits | unresolved
    base:           <sha | null>
    head:           <sha | null>
    files_changed:  <count>
    insertions:     <count>
    deletions:      <count>
    diff_truncated: false
    summary: |
      <prose; 3–8 sentences>

unresolved_prs:                # unresolved input elements
  - ref:        <"<branch_to>...<branch_from>">
    reason:     <e.g. "neither branch nor sha resolves, and no keys_hierarchy to grep">

aggregate_summary: |
  <1–2 paragraphs: what this repo contributed to the feature>
```

`prep.read_only`, `prep.scanned_ref`, `prep.ref_committed_at`, and `prep.head_divergence` are always present, so a caller never branches on absence. See `workflows-core:read-only-repos`.

## Status codes

| Status              | Meaning                                                                        |
|---------------------|--------------------------------------------------------------------------------|
| `OK`                | Every element resolved on its own ref; summaries complete.                     |
| `REPO_MISSING`      | `repo_path` does not exist or is not a git repo.                              |
| `DIRTY_TREE`        | Working tree is dirty and refresh was requested, on a **writable** mount; orchestrator must escalate. A read-only mount never returns this. |
| `REFRESH_BLOCKED`   | `git fetch` or `git pull` genuinely failed (auth, network, non-fast-forward); orchestrator escalates. A read-only mount is NOT a cause — resolution proceeds at `prep.scanned_ref` with `prep.read_only: true`. |
| `NO_PRS_RESOLVED`   | None of the provided `refs` elements could be resolved; `unresolved_prs` lists all of them.|
| `PARTIAL`           | Some elements resolved and some did not (both `per_pr` and `unresolved_prs` populated), **or** at least one element resolved only through the key-commit fallback, whose content correctness is reduced. |

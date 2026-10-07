# code-scanner Handoff Format

## Input

```yaml
repo_path: <absolute, e.g. /workspace/<repo-name>>
repo_url_slug: <repo slug from source URL; optional, enables upstream cross-check>
capability_themes:
  - <short phrase>
context: |
  <3–5 sentences>
search_hints:
  symbols:  [<optional>]
  paths:    [<optional directory globs>]
  keywords: [<optional>]
refresh:
  switch_to_default_branch: true
  pull: true
```

**No `model_routing:` block is passed.** The caller pins this agent's tier with `model:` on the dispatch, and nothing in the agent reads a field of that block.

## Output

```yaml
status: OK | PARTIAL | REPO_MISSING | DIRTY_TREE | REFRESH_BLOCKED | EMPTY

repo:       <repo name (last segment of repo_path)>
repo_path:  <absolute path>

prep:
  branch_at_scan:   <branch name | "unknown">
  refreshed:        true | false
  refresh_note:     <e.g. "switched to main, pulled 12 commits" | "read-only mount; scanned at origin/main" | "skipped per user">
  read_only:        true | false
  scanned_ref:      <ref name, e.g. "origin/main"; on a writable mount, the branch the prep left checked out — the default branch where it switched onto it, else the one it found — or HEAD's commit where HEAD is detached>
  ref_committed_at: <ISO-8601 timestamp of the ref's newest commit>
  head_divergence:  { branch: <working-tree branch>, ahead: <n>, behind: <n> }

capability_map:
  - theme:          <theme text>
    classification: present | partial | absent | error
    evidence:
      - path:    <file path relative to repo root>
        lines:   [<1-based line numbers>]   # optional — present when the match came from a grep hit
        symbols: [<class/function names found>]
        note:    <one-line characterisation of what this file provides>
    gap_summary: |
      <required when classification is partial or absent>
      <2–4 sentences: what is missing or needs to be implemented>
    error: <only when classification == error — one-line reason>

reusable_components: |
  <1–2 paragraphs: what existing code the new Epic can build on>

gap_summary: |
  <1–2 paragraphs: what needs to be implemented from scratch>
```

`prep.read_only`, `prep.scanned_ref`, `prep.ref_committed_at`, and `prep.head_divergence` are always present, so a caller never branches on absence. Every `evidence.path` is relative to the repo root and denotes content **at `scanned_ref`** — on a writable mount, the working tree of that branch, uncommitted changes included; on a read-only mount, open one with `git -C "<repo_path>" show <scanned_ref>:<path>`. A caller that records the ref records its commit, per `read-only-repos.md` §7. See `${CLAUDE_PLUGIN_ROOT}/references/read-only-repos.md`. `evidence.lines` is optional — present when the entry came from a grep hit, absent for a path glob or a whole-file read — and is meaningful only together with `scanned_ref`, because a line number moves with the ref it was read at.

## Status codes

| Status            | Meaning                                                                        |
|-------------------|--------------------------------------------------------------------------------|
| `OK`              | Every theme was scanned and classified (including `absent`, a legitimate scan result, not a failure). |
| `PARTIAL`         | Scan completed but at least one theme has `classification: error`. Failing themes do NOT abort the scan; mirrors `diff-summarizer`'s `PARTIAL` status. |
| `REPO_MISSING`    | `repo_path` does not exist.                                                    |
| `DIRTY_TREE`      | Working tree is dirty and refresh was requested, on a **writable** mount; orchestrator must escalate. A read-only mount never returns this. |
| `REFRESH_BLOCKED` | Ref resolution or a writable-mount refresh genuinely failed (no resolvable default branch, network, auth, non-fast-forward); orchestrator escalates. A read-only mount is NOT a cause — that scan proceeds at `prep.scanned_ref` with `prep.read_only: true`. |
| `EMPTY`           | Repo exists but every theme classified as absent and no relevant files found. Emit instead of `OK` when `capability_map` would contain only `absent` entries. |

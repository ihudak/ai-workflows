# conformance-tracer — input and output

## Input (from `/dev-workflows:conformance` Phase 2)

```yaml
repo_path: <absolute path of the local clone>
ref: <the ref to read: the repository's default branch, origin/<default>>
commit: <the full commit id <ref> resolves to, for the evidence>
requirements:
  - key: <the folder key the requirement belongs to>
    id: <[U02]/[AC03], [AC#4], [FR#2], [AD#3] Rule, or epic.md:<the bullet's quoted text>>
    document: <specification.md | epic.md | prd.md | ard.md>
    text: <the requirement as written>
hints:
  files: [<paths the recorded commits touched in this repository>]
  paths: [<the target component's paths, where it has any>]
```

## Output

One section per requirement, in input order, headed by the requirement's `key` and `id` as the input gives them — the `id` alone repeats on a PRD run, where the PRD-level `specification.md` and every Epic's carry their own `[U01]` and `[U01]/[AC01]`:

```markdown
### <key> <id>

- verdict: <satisfied | partial | missing | contradicts | not-checkable>
- shipped: <one sentence on what the code does>
- evidence: <file:line@commit>, one per place relied on — or, for `missing`, `evidence: none — searched <the searches run>`
- reason: <not-checkable only: why no code can show it>
```

**Every verdict cites evidence, `satisfied` included** — save `not-checkable`, which gives its `reason` instead, and `missing`, whose evidence is `evidence: none — searched …`, the searches that found nothing. A `satisfied` with no `file:line` is read by the caller as *unverified*.

## How the caller merges repositories

A requirement handed to more than one repository gets one verdict after the caller merges the sections, carrying each repository's evidence. It needs only one repository — an Epic's requirement handed to its target repository and to another its implementation record names, or a PRD-level one, which states no home and goes to every repository in scope: `contradicts` where any repository returned that, otherwise the strongest of their verdicts (`satisfied` before `partial` before `missing` before `not-checkable`). A `## Contract` line traced on both sides — produced by one Epic and consumed by another — merges each side that way over that side's Epic's repositories, then needs every side: `satisfied` only where every side is, otherwise the weakest of the sides' verdicts (`contradicts` before `missing` before `partial`). So return `missing` wherever your repository does not do it, even where another repository may: the merge, not you, decides whether that is a discrepancy.

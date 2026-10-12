# conformance-tracer — input and output

## Input (from `/dev-workflows:conformance` Phase 3)

```yaml
repo_path: <absolute path of the local clone>
ref: <the ref to read: origin/<branch>, <branch>, or the default branch's ref>
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

One section per requirement, in input order:

```markdown
### <id>

- verdict: <satisfied | partial | missing | contradicts | not-checkable>
- shipped: <one sentence on what the code does>
- evidence: <file:line@commit>, one per place relied on
- reason: <not-checkable only: why no code can show it>
```

**Every verdict cites evidence, `satisfied` included** — save `not-checkable`, which gives its `reason` instead. A section with neither is read by the caller as *unverified*.

## How the caller merges repositories

A requirement handed to more than one repository — a `## Contract` line produced in one and consumed in another — gets one verdict after the caller merges the sections: `satisfied` only where every repository it needs satisfies it; otherwise the weakest of the repositories' verdicts (`contradicts` before `missing` before `partial`), carrying each repository's evidence.

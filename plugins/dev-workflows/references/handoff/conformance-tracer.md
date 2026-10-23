# conformance-tracer — input and output

## Input (from `/dev-workflows:conformance` Phase 2)

```yaml
repo_path: <absolute path of the local clone>
repo_slug: <the clone's <repo-slug>, as /conformance Phase 1 (a) resolved it>
ref: <the ref to read: the repository's default branch, origin/<default> — or, on an Epic run, the Epic's branch, <branch> or origin/<branch>, where /conformance Phase 1 (c) traces it>
commit: <the full commit id <ref> resolves to, for the evidence>
components:            # an Epic run whose epic.md names a target: only — omitted otherwise
  own:
    id: <this Epic's target: component id>
    paths: [<its paths>]
  siblings:            # the other Epics of its PRD that name another target: — [] where none does
    - epic: <EPIC-KEY>
      id: <that Epic's target: component id>
      paths: [<its paths>]
requirements:
  - key: <the folder key the requirement belongs to>
    id: <[U02]/[AC03], [AC#4], [FR#2], [AD#3] Rule, or epic.md:<the bullet's quoted text>>
    document: <specification.md | epic.md | prd.md | ard.md>
    text: <the requirement as written>
    own_part: <true on a PRD-level [AD#n] Rule and an epic.md ## Contract line, where components is given — omitted otherwise>
    binds: <with own_part, on an [AD#n] Rule: the decision's Binds as written>
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
- sibling parts: <own_part only: each sibling Epic whose component the requirement places a part on, as "<EPIC-KEY> (<component id>) — <that part, in a few words>" — omitted where it places none>
```

**Every verdict cites evidence, `satisfied` included** — save `not-checkable`, which gives its `reason` instead, and `missing`, whose evidence is `evidence: none — searched …`, the searches that found nothing. A `satisfied` with no `file:line` is read by the caller as *unverified*.

## A requirement marked `own_part` — a sibling Epic's part is that Epic's

A PRD-level `[AD#n]` Rule binds the components of its whole PRD, and an `epic.md` `## Contract` line has a side on another Epic's component, so on an Epic run each can place a part on a component another Epic of the PRD builds — on that Epic's own branch, which the ref you read need not hold. Such a part is that Epic's:

1. **Place each part of the requirement on a component** — by a component id its `text` or `binds` names, matched whole against the ids `components` holds, never a name that only resembles one; and the code you read on the component of `components` whose `paths` hold the longest prefix of its path, compared segment by segment — the components reference's `component-of` (§1.1) — counting only a component whose id names this repository: `repo_slug`, the id up to its first `:`. A component's `paths` are relative to its repository's top level, and `[]` is a bare slug's: it holds every path of its repository.
2. **A part on a component of `components.siblings` is that sibling Epic's: it is never a reason for `partial`, `missing` or `contradicts`, and code on that component is never your evidence.** Name it under `sibling parts`. Judge the verdict on every other part, as you judge any requirement, and cite the evidence of those parts alone.
3. **A requirement that places no part on `components.own` is `not-checkable`**: nothing of it is this Epic's to build. Its `reason` names each sibling Epic, by key, whose component it binds, and each other component it binds, by its id; its `sibling parts` are named as in 2.

Without `components`, or on a requirement not marked `own_part`, every part is yours to judge.

## How the caller merges repositories

A requirement handed to more than one repository gets one verdict after the caller merges the sections, carrying each repository's evidence. It needs only one repository — an Epic's requirement handed to its target repository and to another its implementation record names, or a PRD-level one, which states no home and goes to every repository in scope: `contradicts` where any repository returned that, otherwise the strongest of their verdicts (`satisfied` before `partial` before `missing` before `not-checkable`). A `## Contract` line traced on both sides — produced by one Epic and consumed by another — merges each side that way over that side's Epic's repositories, then needs every side: `satisfied` only where every side is, otherwise the weakest of the sides' verdicts (`contradicts` before `missing` before `partial` before `not-checkable`), a side none of whose repositories was traced counting as `not-checkable`. So return `missing` wherever your repository does not do it, even where another repository may: the merge, not you, decides whether that is a discrepancy. A sibling Epic's part of an `own_part` requirement is the exception: it is that Epic's, wherever it would be built (*A requirement marked `own_part`*, above).

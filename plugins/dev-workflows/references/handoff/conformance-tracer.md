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
  siblings:            # each other Epic of its PRD whose target: is not this Epic's — [] where none is
    - epic: <EPIC-KEY>
      id: <that Epic's target: component id>
      paths: [<its paths>]
  others:              # each component of the ARD's components: that neither own nor a sibling is — [] where none is
    - id: <component id>
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
- reason: <not-checkable only: why no code can show it — or, under rule 3 below, the components the Rule binds in place of this Epic's>
- sibling parts: <own_part only: each sibling Epic whose component the requirement places a part on, as "<EPIC-KEY> (<component id>) — <that part, in a few words>" — omitted where it places none>
```

**Every verdict cites evidence, `satisfied` included** — save `not-checkable`, which gives its `reason` instead, and `missing`, whose evidence is `evidence: none — searched …`, the searches that found nothing. A `satisfied` with no `file:line` is read by the caller as *unverified*.

## A requirement marked `own_part` — a sibling Epic's part is that Epic's

A PRD-level `[AD#n]` Rule binds the components of its whole PRD, and an `epic.md` `## Contract` line has a side on another Epic's component, so on an Epic run each can place a part on the component of a sibling Epic — another Epic of the PRD, whose target is not this Epic's — built on that Epic's own branch, which the ref you read need not hold. Such a part is that Epic's:

1. **Place each part of the requirement on a component of `components`** — `own`, a sibling's or one of `others` — by a component id its `text` or `binds` names, matched whole against those ids, never a name that only resembles one; and by the code you read, on the component whose `paths` hold the longest prefix of its path, compared segment by segment — the components reference's `component-of` (§1.1) — counting only a component whose id names this repository: `repo_slug`, the id up to its first `:`. A component's `paths` are relative to its repository's top level; an id with no `:` — a bare slug — holds every path of its repository, and is the one component handed `paths: []`. Code on none of them — a repository's shared ground — is on no sibling's component. A component the requirement names only as the caller of another component's interface — "as bookstore:web calls them" — holds no part of it: the part lies on the component whose behaviour the requirement states, and the call is the caller's own `## Contract` line, traced as that.
2. **A part on a sibling's component is that sibling Epic's: it is never a reason for `partial`, `missing` or `contradicts`, and code on that component is never your evidence.** Name it under `sibling parts`. Where 3 does not apply, judge the verdict on every other part — this Epic's, and any on a component of `others` — as you judge any requirement, and cite the evidence of those parts alone.
3. **An `[AD#n]` Rule that binds only components other than this Epic's is `not-checkable`** on this run: every part it places (1) lies off `components.own` — placed by the component ids its `text` or `binds` names or, where it names none, by the code that does what it states — and no code doing what it states lies on `own`. Its `reason` names each component it binds, by its id, and the sibling Epic, by key, that targets it where one does; its `sibling parts` are named as in 2. A Rule that names no component id and whose code you found nowhere places no part, so it is judged as in 2, never `not-checkable` under this rule: where nothing does what it states, it is `missing`. Rule 3 never applies to a `## Contract` line: its side on this Epic is always this Epic's.

Without `components`, or on a requirement not marked `own_part`, every part is yours to judge.

## How the caller merges repositories

A requirement handed to more than one repository gets one verdict after the caller merges the sections, carrying each repository's evidence. It needs only one repository — an Epic's requirement handed to its target repository and to another its implementation record names, or a PRD-level one, which states no home and goes to every repository in scope: `contradicts` where any repository returned that, otherwise the strongest of their verdicts (`satisfied` before `partial` before `missing` before `not-checkable`). A `## Contract` line traced on both sides — produced by one Epic and consumed by another — merges each side that way over that side's Epic's repositories, then needs every side: `satisfied` only where every side is, otherwise the weakest of the sides' verdicts (`contradicts` before `missing` before `partial` before `not-checkable`), a side none of whose repositories was traced counting as `not-checkable`. So return `missing` wherever your repository does not do it, even where another repository may: the merge, not you, decides whether that is a discrepancy. A sibling Epic's part of an `own_part` requirement is the exception: it is that Epic's, wherever it would be built (*A requirement marked `own_part`*, above).

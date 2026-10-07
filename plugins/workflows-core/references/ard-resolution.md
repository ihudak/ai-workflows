# ARD resolution (embedded — shared reference)

Given a resolved item, resolve any applicable **Architecture Requirements/Decision Document(s)** produced by
`/create-ard` and return a normalized **ARD context** — or **`none`**. Cited by `/create-ard`, `/design`,
`/implement`, `/specify`, `/epics`, and `/ready` so the resolution logic, the **optional/no-regression** rule, and the deviation-record
convention live in ONE place.

## Inputs

`prd` (PRD key), `epic` (or `null`), `area` (or `null`), `$SPECS_PATH`.

## Resolution (most-specific first)

1. Resolve the PRD folder by calling `resolve-address <PRD>` — the entry point
   `${CLAUDE_PLUGIN_ROOT}/references/addressing.md` §3 defines. It searches every level §3 bounds and
   carries §5's legacy fallback, so this step states no matching rule of its own: a key-number match
   tolerating a stray `-`/`_` and a human-adjusted slug is exactly what §5 does, and a second copy of
   it here is the drift `addressing.md` §1 warns about. `status: absent` → no ARD exists; return
   `none`. `status: misrooted` is `addressing.md` §3's hard stop and stops the run here with
   its `SPECS_PATH_INSIDE_TREE` message — never `none`, which would let the caller go on without an
   ARD it should have enforced.

   **This step is the only route by which that resolution reaches an ARD.** All six consumers below
   delegate their ARD lookup here, so none of them finds an ARD by resolving its *own* folder —
   `/implement` included, which resolves its own folder on a keyed run and still reaches an ARD
   solely by citing this file.
2. Collect candidate ARD files **inside the folder step 1 resolved**, by filename — never a path
   re-derived from the key (`addressing.md` §4):
   - **Epic-level** (`epic` set): the Epic folder's `ard.md` and any `ard-<area>.md` (the area-scoped
     file when `area` is given, else every per-area ARD) **plus** the PRD folder's own `ard.md` for
     inherited invariants.
   - **PRD-level** (`epic` null): only the PRD folder's `ard.md`.
3. Parse each file's `## Architecture decisions` into `AD#N {id, binds, prevents, rule, source}` where
   `source` ∈ `prd | epic | area`. PRD-level `AD#N` are the inherited base; Epic/area `AD#N` layer on top
   (Epic/area wins on any conflict — contradictions were already blocked by `ard-reviewer` at authoring).
   **Skip a decision carrying `**Superseded by:**` or `**Withdrawn:**`** — it binds nothing (`product-workflows`'
   `ard-format.md` § Superseding a decision), and emitting it would have consumers enforce a rule the ARD itself
   replaced or dropped. A replacement is a decision of its own and is emitted as one.
   Accept **both** `### [AD#N]:` and the legacy `### [AD-N]:`, and ALWAYS emit the `#` form in `id`. <!-- id-grammar-ok: legacy reader tolerance -->
   This resolver is a **reader**, and an ARD has no `/update-ard` to convert it the way `/update-prd`
   converts a PRD, so a dash-form ARD authored by a pre-2.53.0 install on another machine would never
   drain. Failing to parse it is silent in the worst way: the file still resolves `status: found`, but
   with an empty `invariants` list every consumer's ARD-conformance dimension is skipped exactly as if
   no ARD existed — a binding architecture document enforcing nothing, under a run that reports success.
4. From the PRD-level ARD alone — the PRD folder's `ard.md`, or, where `epic` names a `PRD-` folder (a BRD-route slice, `addressing.md` §4.1), that slice's own `ard.md`, which `/create-ard <SLICE>` writes as the slice's PRD-level ARD; on an Epic-level resolution too, since an Epic's ARD carries neither (the ARD format's `components:` rule) — read the frontmatter `components:` list into `components`, and the `## Contracts` section into `contracts`: one row per line of its interface table (`| AD | Producer | Consumers | Kind | Status | Artifact |`, the `Consumers` cell split on commas, an `Artifact` of `—` read as null) and the ids of its `### Landing order` list, in order. Accept `[AD#N]` and the legacy dash form in the `AD` column exactly as step 3 does, emitting the `#` form. This step runs on `status: found` and `unmerged` alike — `/ready` reads both. An ARD with no `components:` key yields `components: []`; one with no `## Contracts` heading yields `contracts: null`.

## Output — the ARD context, or `none`

```yaml
status: found | none | unmerged
ard_paths: [ <absolute paths of the ARD files used> ]
branch: <carrying branch> | null   # present only when status: unmerged
pr: <open pull request number> | null   # present only when status: unmerged
invariants:
  - id: AD#1
    source: prd | epic | area
    binds: <text>
    prevents: <text>
    rule: <testable statement>
guidance_summary: <short prose: the ARD's non-AD#N architecture guidance the consumer should heed>
components:          # the PRD-level ARD's `components:` (step 4), or []
  - id: <component id>
    kind: code | deploy
    paths: [ <path>, ... ]
contracts:           # the PRD-level ARD's `## Contracts` (step 4), or null
  rows:
    - ad: AD#N
      producer: <component id>
      consumers: [ <component id>, ... ]
      kind: REST | message | shared schema | shared library | generated client
      status: new | changed | exists
      artifact: <path in the producer> | null
  landing_order: [ <component id>, ... ]
```

`status: none` when no ARD file resolves (the common case — `/create-ard` is optional), and `components` is then `[]` and `contracts` `null`.

`status: unmerged` when an ARD file resolves but is **not on the specs repo's default branch** — verified via `${CLAUDE_PLUGIN_ROOT}/references/phase-handoff.md` §3 (`require-on-main`), whose rows D and E find it on a plugin branch and return the carrying `branch` and any open `pr`. Both are passed through to the caller.

**An ARD file no plugin branch carries is not `unmerged`.** There `require-on-main` returns row F — `on_main: absent`, with no branch to pass through — which is the state a declined `/create-ard` handoff leaves, or that an ARD committed only on a branch of the person's own leaves, and it is `status: none`, exactly as `phase-handoff.md` §3.4's ARD row records it: the file is not read, and the no-regression rule below applies unchanged. Reading it as `unmerged` would stop every consumer but `/ready`, naming no branch, in a state §3.4 lets them proceed past.

**`unmerged` is reachable only when an ARD file resolves.** An absent ARD is `none`, unchanged — see the no-regression rule below. This status does not make `/create-ard` a prerequisite for anything.

## No-regression rule (central)

A caller that gets `status: none` **MUST behave exactly as it did before this feature** — no prompt, no
extra phase output, no reviewer dimension. The ARD steps are strictly additive and guarded on
`status: found`.

**One stated exception: a multi-component PRD.** Where `${CLAUDE_PLUGIN_ROOT}/references/components.md` §3 finds two or more `kind: code` components — from an ARD's `components:`, or, with `none` here, from an `/epics` run's confirmed set or the targets the PRD's Epics carry — an ARD without `## Contracts`, `none` included, leaves the Epics with no contract to fit together by. So `/epics` (Phases 2.7 and 5.5) and `/implement` (Phase 1) ask whether to stop and author it first (`components.md` §6), each offering to continue without it; `/design <PRD>` and `/implement <PRD>` take a flat PRD-level specification as a requirements source rather than a unit, save by their override; and `/ready` asks nothing and caps its verdict. Continuing without the ARD proceeds exactly as `none` does here: it is still never a prerequisite. **This rule binds the ARD's steps, not another input's**: what an Epic's `target:` drives — `/specify`'s and `/design`'s narrowing to it, `/design`'s re-split question, `/implement`'s target-repository question, `/ready`'s target repositories — runs on a one-component PRD with no ARD too, because the target, not the ARD, is its input.

A caller that gets `status: unmerged` **stops**, naming the branch and any open pull request, except `/ready` — which is a read-only verifier and records it as a readiness finding capping the verdict at `PARTIAL`. The distinction matters: reporting a phase as complete while its ARD sits unmerged is exactly the claim `/ready` exists to check.

## Deviation-record convention

When an artifact must NOT honor an `AD#N`, the consumer records — in its **own** artifact, NEVER in the
ARD (role separation: the ARD is the architect's) — a line:

`- ARD deviation: [<AD#N id>] — <what deviates> — <why> — flag: architect`

and surfaces it in the run's final report. A reviewer treats a violating artifact **with** a matching
deviation record as *allowed-but-flagged* (the architect adjudicates), **without** one as a **BLOCKER**.

## Consumers (informative)

- `/create-ard` — reads the inherited PRD-level ARD on an Epic-level run (`epic: null` maps to PRD-level-only); `AD#N` = the invariants the newly-authored Epic-level `AD#N` must not contradict; `ard-reviewer` checks non-contradiction directly against the drafted file — no separate deviation-record path.
- `/design` — Epic-level ARD = design guidance; PRD-level `AD#N` = inherited invariants; deviations → a `## ARD deviations` section in `design.md` + an open question.
- `/implement` — keyed runs only; `AD#N` = implementation guardrails; deviations → the Phase 5 report. Direct mode → `none`.
- `/specify` — keep user stories + scope consistent with `AD#N` + scope; deviations → the spec's `### Open questions`.
- `/epics` — PRD-level only (`epic: null` on a re-refine run as on a draft one, `prd` the PRD folder's key either way); `AD#N` = inherited invariants the drafted Epics must respect; deviations → a `- ARD deviation: …` line in the Epic draft + the Phase 9 report.
- `/ready` — PRD-level + Epic-level `AD#N` = inherited invariants passed to `readiness-reviewer` as `applicable_ard`; read-only — it never authors a deviation record, only checks the artifacts it reads for an existing one.

`components` and `contracts` are read by `${CLAUDE_PLUGIN_ROOT}/references/components.md` §3 and §6, read directly by `/specify`, `/design` and `/ready`, and passed on by `/epics` to `epic-writer` and `epic-reviewer`, and by `/design` to `design-reviewer` (its interface rows); a caller that reads neither field behaves exactly as it did before they existed.

The five consumers listed above other than `/create-ard` pass `invariants` to their reviewer as `applicable_ard`; the reviewer's ARD-conformance dimension is skipped entirely when it is absent. `/create-ard` alone does not: it inherits PRD-level `AD#N` read-only straight into its own grill and drafting (Phase 4), and `ard-reviewer` checks non-contradiction directly against the drafted file, never via that field.

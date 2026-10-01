---
paths:
  - "plugins/docs-workflows/commands/release-notes.md"
  - "plugins/docs-workflows/agents/release-notes-writer.md"
  - "plugins/docs-workflows/references/release-note-types.md"
  - "plugins/docs-workflows/docs/commands/release-notes.md"
---

# docs-workflows — `/release-notes`

Loaded when `/release-notes`' command file or docs page is read, `release-notes-writer`, or `docs-workflows:release-note-types`. Split out of `.claude/rules/docs-workflows.md` to keep that file under 20,000 characters; the plugin's other rules are there.

## Authority

`plugins/docs-workflows/references/release-note-types.md` is the **single source of truth** for the release-note **section map** — the three destinations as three sections, `## Breaking changes` / `## Feature updates` / `## Fixes`, of one `release-notes.md` in the resolved PRD folder, under a heading for the release version, each draft under a scope comment naming the PRD or Epic it was drafted for and every commit its run read — the per-section **draft shape** (label + title + prose, vs one bare sentence for `## Fixes`), the per-section prose rules, the deprecation-note rule (end-of-life date required, end-of-support optional), and Change Type sourcing (the PRD's `change_type` → infer). It is consulted by `release-notes-writer`; `/release-notes` cites it for its own invariants but never re-derives the writer's decision. The Change Type is never rendered as text.

## Workflow map

```
/release-notes       → read the resolved PRD folder → [diff-summarizer×N (parallel, optional)] → [docs-grounder] → [release-notes-writer: resolve destination + shape per destination + source the **Category:** label + detect deprecation] → [prose-style-checker → prose-fixer (optional), on a scratch copy, the checker handed the specs repository as the repo whose house-style rules apply] → append the draft to the PRD folder's release-notes.md, under its version and Change Type section, never rewriting an earlier section (destination-shaped Summary; yours to paste wherever release notes are published) → impl-maintenance → commit-artifacts
```

## Invariants

### Key invariants for `/release-notes`

- **Zero direct API calls** — the run has no forge URL to resolve in the first place: Phase 3 builds `refs[]` from `implementation.md` and the commit scan, and the opt-in diff grounding reuses `diff-summarizer`, which takes a ref's diff with pure local `git`; all resolution runs against clones under `$REPOS_PATH`
- The draft is the **authored body only** — for a titled destination a **Category:** label, `### title`, and customer-facing prose; for `fixes` ONE bare past-tense sentence. NEVER a key or issue ID, a PR link, a `Change type:` line, or a `{{#internal-note}}` block (the docs automation adds the metadata wrapper)
- The **Category:** label IS the PRD's own `release_notes_category`, used verbatim; absent ⇒ the line is omitted. Change Type is sourced from the PRD's `change_type` → infer, drives destination + shape only, and is confirmed with the user only on a low-confidence inference — by shape and destination, never by enum label
- The Summary is shaped per its destination (breaking → present tense, what breaks, remediation; feature update → benefit-led, plus a docs/blog link on a dev-phase run only; fixes → one past-tense sentence, no hedging, no internal terms); exactly ONE Summary per run, and no title or prose names the release version
- The run has **no worthiness gate**, and that is a retirement rather than an omission: `relevant_for_release_notes` is retired from `workflows-core:prd-format`, no command reads it, and a value left in an existing PRD is inert ([why](../../docs/maintainers/rationale.md#release-notes-worthiness)). The command refuses only on its address and on what that address needs — `RELEASE_NOTES_NEEDS_KEY` where the prompt carries no positional address at all or one that fails the key grammar, an unset `$SPECS_PATH` on a `<KEY>` (an `@<path>` needs no specs tree and runs on), a stop naming every match where one resolves ambiguously, `SPECS_PATH_INSIDE_TREE` on either address form where `$SPECS_PATH` is set inside the specs tree, the shared re-enter/cancel escalation where one resolves to nothing, and a Phase 0 named stop where an address resolves but leads to no `prd.md` the run can read, or to a PRD folder carrying no key — `RELEASE_NOTES_BRD_NOT_SLICED` on a BRD container, `RELEASE_NOTES_FOLDER_NOT_PLACED` on a folder placed at no level, `RELEASE_NOTES_PRD_NO_KEY` on a PRD folder carrying no key, `RELEASE_NOTES_NO_PRD` on a PRD folder with no `prd.md` or one it cannot read, its remedy following a BRD-route slice's ledger state
- A deprecation carries a deprecation note in the Summary — end-of-life date (required) + end-of-support date (optional); a missing required date becomes a `deprecation_eol` gap the command asks about (never invented)
- NEVER writes into a docs repo; the draft's one destination, `release-notes.md` in the resolved PRD folder, is persistent (never `/tmp`), and the draft is appended to it, never overwriting an earlier section
- Light gate only — `prose-style-checker` (optional, skipped only on the user's own "Skip style check" answer in Phase 1 — `prose-style` is a declared dependency of `docs-workflows`, so the phase never skips itself for want of a plugin); no Opus review, no tests, no branch (`specs-preflight`, its same-run re-run after a slice key is entered included (`workflows-core:specs-repo-git` §3.5), switches `$SPECS_PATH` only between branches that already exist, and only plugin-created ones — §2.2; it creates none), and no commit of anything in a docs/code repo or the current working directory, where it is not the specs repository. The terminal `commit-artifacts` step still runs, committing ONLY `$SPECS_PATH`'s bounded session-artifact paths (`workflows-core:specs-repo-git` §2.1) — the draft, `release-notes.md` in the resolved PRD folder, among them, so the draft is committed in the specs repository and nowhere else, unless the run carries `specs_git: blocked` or `specs_git: misrooted`, when it is written and not committed
- Diff grounding is opt-in; when on, it reuses `$REPOS_PATH` resolution + `diff-summarizer`

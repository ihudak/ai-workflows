# Bugs review — 0e02e28b (2026-10-26)

**Reviewed state:** `main` at `0e02e28b` (`0e02e28b1b83e362c592dd45cbf287195508b7cb`), 2026-10-24 — the last commit this review read. Anything committed after it is unreviewed.
**Window:** every change since 2026-09-25 (base: the last commit on `main` before 2026-09-25; `git log --first-parent --since=2026-09-25 main` lists 124 first-parent commits, 1,014 in all, 961 files). Where a reviewer met an older defect that is still live in the text it read, it is logged too and says so.
**Also triaged:** the field-feedback files from the earlier live runs in the demo specs repository `bookstore-specs` (132 entries, 2026-10-07 … 2026-10-17); see *Field feedback accounted for* below. Feedback that has since been fixed is not logged.
**Companion file:** `2026-10-26-feature-gaps-review.md` — designed or promised work that never landed.

## How to use this file (for the fixer)

- **One heading per defect**, `### <ID> — <SEVERITY> — <title>`, each with *Where* (`path:line` at `0e02e28b`), *What is wrong* (quoted), *Failure scenario*, *Evidence*, *Suggested fix*, *Source* and *Confidence*. Line numbers are at `0e02e28b`: re-locate by the quoted text before editing, since the tree moves.
- **IDs are the reviewers' own**, prefixed by slice (`SEC`, `GIT`, `CORE`, `SCR`, `IMP`, `DEV`, `VU`, `PRD`, `PRD2`, `BRD`, `BRD2`, `BRD3`, `DOC`, `FBA`, `FBB`, `TRK`). They are unique across the file; gaps in a numbering sequence are defects merged into another entry (its *Also found as* line names them) or moved to the feature-gaps file (the field-feedback `Gap:` entries).
- **Severity:** BLOCKER — a run fails, corrupts or publishes wrongly; MAJOR — wrong behaviour in a reachable case; MINOR — an edge case, misleading text or small inconsistency; NIT — cosmetic but still a defect. No BLOCKER was found.
- **Confidence** is the reviewer's. `low` and `medium` entries state what would confirm them; verify before fixing. The entries marked as re-checked were re-read against the tree by the slice lead or by the review's coordinator; the rest are a single reviewer's reading.
- **This repository's process still applies.** `CLAUDE.md` § Editing discipline (the claim-expiry sweep, the sentence-context checks, re-deriving counts), version bumps with dated `CHANGELOG.md` sections and the `.claude/rules/plugin-updates.md` coupling notes, and the gate chain in `.github/workflows/validate-catalog.yml` before pushing. Read the area's `.claude/rules/` file before editing there.
- **`docs/superpowers/to-fix.md` is not duplicated here.** Its items are cross-referenced in the next section with their status at `0e02e28b` and a restatement that stands on its own; fix them from there, by its own rules (delete an item there in the commit that fixes it). Where a finding below extends a to-fix item, the item is named in the finding.

## Summary

273 defects: **0 BLOCKER, 26 MAJOR, 170 MINOR, 77 NIT**, after merging 10 duplicates found by more than one reviewer. Every gate in `.github/workflows/validate-catalog.yml` passes at `0e02e28b` (run in a scratch copy, chain exit 0) except the mermaid gate, which was not run: the host has no Node. So most of what follows is prose a gate cannot see — instructions an agent would execute wrongly.

The MAJOR defects, in area order:

- **SEC-B1** — after `REGISTER_MOVED`, a re-plan rebinds the person's `id:<n>` decisions to a different finding
- **GIT-B1** — `branch-merged`'s squash test misses a squash merge when the default branch changed lines near the branch's hunks
- **CORE-B1** — the cost path resolves "the current session" as the newest transcript, which is another session's whenever two share a working directory
- **CORE-B2** — `<cwd-slug>` replaces only `/` and `.`, but Claude Code replaces every non-alphanumeric character
- **DEV-B1** — `/ready` asks its "dirty or non-main checkout" question on every run in session-branch mode, and its re-check can never pass
- **VU-B1** — An auto-fixed test regression is returned as a pass without verify being run again
- **VU-B2** — Research and planning read the tree before the run moves onto the base, so the fix is computed against a different tree
- **VU-B3** — `vuln-research` cannot detect a transitive-only vulnerable library in Maven or Gradle, and reports it `NOT_IN_REPO`
- **PRD2-ARD-B1** — An Epic-level run under a BRD slice is told to write the slice's frontmatter: `epic: <SLICE-KEY>`, `components:`, and an `inherits:` that points past the slice ARD it must inherit
- **PRD2-ARD-B2** — On a BRD slice with no `prd.md`, the ordinary state, the run passes `key: null` to `emit-auto`, `emit-cost` and `commit-artifacts`, so its cost lands in a pending file; `/create-prd` passes the slice key
- **PRD2-SPEC-B1** — *Next Epic* loops back to Step B and Phases 3–7, skipping Phase 2.5, so the next Epic is specified and reviewed against the previous Epic's ARD
- **PRD2-SPEC-B2** — An existing `specification.md` (even `Published: yes`) is silently re-authored and overwritten with `Published: no`; the picker's *revise* is never defined
- **BRD3-B1** — A run stopped after Phase 5 wrote the register but before Phase 12 wrote the reconciliation record leaves `[CD#n]`s the re-run cannot reach, so the re-run mints a second `[CD#n]` for the same question
- **BRD3-B2** — A stop or interruption after Phase 5 loses the run's defect resolutions, ledger moves and sweep: the re-run reads its own frozen [CD#n] as re-affirmations
- **BRD3-B3** — The documented remedy for a recorded-not-written dependent cannot write anything: the re-run's changed-id set is empty for the earlier pass's ids
- **BRD3-B4** — A prerequisite's bundle is copied in "wholesale", so its own copied-in prerequisites come along under a key the partition set does not hold. The "cannot arise" collision claim is false.
- **DOC-A-B1** — Phase 5.8's no-discrepancy exit jumps to Phase 6.3, skipping Phase 6.1 (CDN handoff) and Phase 6.2 (branch setup)
- **DOC-A-B2** — Phase 6.4's clean-style exit jumps to Phase 7, skipping Phase 6.5 (render verification) and its two ledger rows
- **DOC-A-B3** — `doc-planner` makes a `changelog:` entry mandatory on every target, new pages included; the plugin's own frontmatter rules forbid one on first publish
- **DOC-A-B4** — Declining branching at plan approval still commits into the docs repo, and Phase 8.5 then squashes against an unset `base_branch`
- **DOC-B-B1** — A re-draft under `# Unreleased` is bounded by the note it is about to supersede, so the superseding note never reads the earlier commits
- **DOC-C-B1** — Writing a page by the route page's step 4 breaks the scaffold's `--strict` builds, because nothing regenerates the "never hand-edited" `nav:`
- **DOC-C-B2** — `/docs-init` and standalone `/docs-brand` stops after the specs preflight skip the emitter tail, against `specs-repo-git` §4
- **FBB-B1** — `/prd-proposal` writes `proposal-profile.yml` and calls it committed, but nothing ever stages it
- **DQW-B1** — The docs-workflows Update block leaves out `workflows-core`, which every recent docs-workflows release has to be updated with
- **DQW-B2** — obsidian-llm-wiki README says the Stop hook updates `hot.md` "at session end", but the hook blocks Claude at the end of every turn

### Documentation quality

Added the same day, after the first version of this file was pushed (`cf139b47`): five more reviewers read every plugin's README and `docs/` tree as a user would — navigation, broken links, page-set parity across plugins, workflow diagrams against the commands, and internal vocabulary reaching users. They found 65 defects (2 MAJOR, 45 MINOR, 18 NIT), listed under the *documentation quality* areas below. All 1,330 relative links in the 117 human-facing files resolve and no page is an orphan; what is wrong is what the pages link to and say. The most visible: `guideline-reviewers`' README does not link its workflow diagram and its root-README row has no Docs link (DQS-B1); 18 command pages never link back to their plugin's workflow page and the overview pages link no command page (DQS-B2, DQS-B3); 18 links leave the plugin directory and break in an installed copy (DQS-B5); the workflow diagrams of dev- and product-workflows skip `/conformance` and the security scan (DQD-B3, DQP-B5); maintainer vocabulary — design-decision ids, `§` citations, grep recipes over `plugins/`, change history — runs through every plugin's user pages (DQS-B7, DQS-B8 and the per-plugin entries); and the two MAJORs: docs-workflows' update block leaves `workflows-core` behind (DQW-B1), and obsidian-llm-wiki's `Stop` hook blocks every response while its README says it runs at session end (DQW-B2, re-checked by the coordinator against `hooks/hooks.json`).

### Coverage and its limits

Seventeen review passes, each on one slice, read the slice end to end at `0e02e28b` against its `.claude/rules/` file, the workflows-core references it cites, and its docs pages; the BRD route took three passes and the product ladder and dev-workflows two, because a first pass ran out of room. Known limits:
- `plugins/dev-workflows/agents/test-baseliner.md` (about 154k characters) was read only at its detection table, parse table and status definitions.
- The mermaid gate was not run.
- Several findings rest on a reading no live run has tested (each says so under *Confidence*); `CORE-B2`'s slug rule and `SEC-B4`'s report location are the two most worth confirming first.
- The coordinator re-read DOC-A-B1, DOC-A-B2, FBB-B1, PRD2-SPEC-B2 and VU-B1 against the tree; each holds.

## Index

| ID | Severity | Area | Title |
|---|---|---|---|
| SEC-B1 | MAJOR | security-workflows | after `REGISTER_MOVED`, a re-plan rebinds the person's `id:<n>` decisions to a different finding |
| GIT-B1 | MAJOR | workflows-core — git, handoff, resume pointer | `branch-merged`'s squash test misses a squash merge when the default branch changed lines near the branch's hunks |
| CORE-B1 | MAJOR | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | the cost path resolves "the current session" as the newest transcript, which is another session's whenever two share a working directory |
| CORE-B2 | MAJOR | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | `<cwd-slug>` replaces only `/` and `.`, but Claude Code replaces every non-alphanumeric character |
| DEV-B1 | MAJOR | dev-workflows — /design, /ready, /conformance | `/ready` asks its "dirty or non-main checkout" question on every run in session-branch mode, and its re-check can never pass |
| VU-B1 | MAJOR | dev-workflows — /vuln, /upgrade | An auto-fixed test regression is returned as a pass without verify being run again |
| VU-B2 | MAJOR | dev-workflows — /vuln, /upgrade | Research and planning read the tree before the run moves onto the base, so the fix is computed against a different tree |
| VU-B3 | MAJOR | dev-workflows — /vuln, /upgrade | `vuln-research` cannot detect a transitive-only vulnerable library in Maven or Gradle, and reports it `NOT_IN_REPO` |
| PRD2-ARD-B1 | MAJOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | An Epic-level run under a BRD slice is told to write the slice's frontmatter: `epic: <SLICE-KEY>`, `components:`, and an `inherits:` that points past the slice ARD it must inherit |
| PRD2-ARD-B2 | MAJOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | On a BRD slice with no `prd.md`, the ordinary state, the run passes `key: null` to `emit-auto`, `emit-cost` and `commit-artifacts`, so its cost lands in a pending file; `/create-prd` passes the slice key |
| PRD2-SPEC-B1 | MAJOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | *Next Epic* loops back to Step B and Phases 3–7, skipping Phase 2.5, so the next Epic is specified and reviewed against the previous Epic's ARD |
| PRD2-SPEC-B2 | MAJOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | An existing `specification.md` (even `Published: yes`) is silently re-authored and overwritten with `Published: no`; the picker's *revise* is never defined |
| BRD3-B1 | MAJOR | product-workflows — BRD route (third pass) | A run stopped after Phase 5 wrote the register but before Phase 12 wrote the reconciliation record leaves `[CD#n]`s the re-run cannot reach, so the re-run mints a second `[CD#n]` for the same question |
| BRD3-B2 | MAJOR | product-workflows — BRD route (third pass) | A stop or interruption after Phase 5 loses the run's defect resolutions, ledger moves and sweep: the re-run reads its own frozen [CD#n] as re-affirmations |
| BRD3-B3 | MAJOR | product-workflows — BRD route (third pass) | The documented remedy for a recorded-not-written dependent cannot write anything: the re-run's changed-id set is empty for the earlier pass's ids |
| BRD3-B4 | MAJOR | product-workflows — BRD route (third pass) | A prerequisite's bundle is copied in "wholesale", so its own copied-in prerequisites come along under a key the partition set does not hold. The "cannot arise" collision claim is false. |
| DOC-A-B1 | MAJOR | docs-workflows and the smaller plugins | Phase 5.8's no-discrepancy exit jumps to Phase 6.3, skipping Phase 6.1 (CDN handoff) and Phase 6.2 (branch setup) |
| DOC-A-B2 | MAJOR | docs-workflows and the smaller plugins | Phase 6.4's clean-style exit jumps to Phase 7, skipping Phase 6.5 (render verification) and its two ledger rows |
| DOC-A-B3 | MAJOR | docs-workflows and the smaller plugins | `doc-planner` makes a `changelog:` entry mandatory on every target, new pages included; the plugin's own frontmatter rules forbid one on first publish |
| DOC-A-B4 | MAJOR | docs-workflows and the smaller plugins | Declining branching at plan approval still commits into the docs repo, and Phase 8.5 then squashes against an unset `base_branch` |
| DOC-B-B1 | MAJOR | docs-workflows and the smaller plugins | A re-draft under `# Unreleased` is bounded by the note it is about to supersede, so the superseding note never reads the earlier commits |
| DOC-C-B1 | MAJOR | docs-workflows and the smaller plugins | Writing a page by the route page's step 4 breaks the scaffold's `--strict` builds, because nothing regenerates the "never hand-edited" `nav:` |
| DOC-C-B2 | MAJOR | docs-workflows and the smaller plugins | `/docs-init` and standalone `/docs-brand` stops after the specs preflight skip the emitter tail, against `specs-repo-git` §4 |
| FBB-B1 | MAJOR | field feedback — BOOK-2-01 runs | `/prd-proposal` writes `proposal-profile.yml` and calls it committed, but nothing ever stages it |
| DQW-B1 | MAJOR | documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki | The docs-workflows Update block leaves out `workflows-core`, which every recent docs-workflows release has to be updated with |
| DQW-B2 | MAJOR | documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki | obsidian-llm-wiki README says the Stop hook updates `hot.md` "at session end", but the hook blocks Claude at the end of every turn |
| SEC-B2 | MINOR | security-workflows | `register.py commit` takes any status from the decisions file, so "closed only on evidence" is enforced by prose alone |
| SEC-B3 | MINOR | security-workflows | an empty `--by` is accepted, so an accepted risk can be recorded with no owner |
| SEC-B4 | MINOR | security-workflows | Phase 3 looks for the report only at the scan root, while Claude Security creates it with a cwd-relative `mkdir` |
| GIT-B2 | MINOR | workflows-core — git, handoff, resume pointer | §3.4's flush commits leftovers onto a merged plugin branch before §3.5 can see it merged, and strands them |
| GIT-B3 | MINOR | workflows-core — git, handoff, resume pointer | `<merge-clause>`'s table has no row for §4.1's *Commit failed*, while it claims to resolve every outcome row |
| GIT-B4 | MINOR | workflows-core — git, handoff, resume pointer | epic-picker's cap: the worked example and the "four or fewer" rule disagree, and the rule overlaps `/specify`'s cap |
| CORE-B3 | MINOR | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | the model-onboarding checklist names two files; a new generation touches more, and a Haiku one touches neither the way it says |
| CORE-B4 | MINOR | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | §6.1 cites "§8 tier 5", which does not exist |
| CORE-B5 | MINOR | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | `/prompt-brainstorm` has no absent-companion path, though `dependencies.md` says the run probes for `superpowers` and falls back to an "embedded technique" |
| CORE-B6 | MINOR | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | `followup-emission` §7's `select` option needs text from the user but is not labelled `(you'll be prompted …)`, against `escalation-rules` §0 |
| CORE-B7 | MINOR | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | the feedback ladder's tier 1 matches the PRD folder only by the legacy unprefixed name `<KEY>{-\|_}<slug>` |
| CORE-B8 | MINOR | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | the feedback entry `id` has no defined key segment for a keyless run |
| SCR-B1 | MINOR | scripts, gates and hooks | `test-notify` reads `tool_response.output`, which a Bash payload does not carry, so it never reports a count |
| SCR-B2 | MINOR | scripts, gates and hooks | CLAUDE.md says check 13 enforces vendor neutrality for every text file under `plugins/`; it scans only `PLUGIN_RELS`, and two catalog plugins name trackers unmarked |
| SCR-B3 | MINOR | scripts, gates and hooks | the `/implement` and `/document` preload hooks restate the key grammar, narrower than `addressing` §1, so some keyed runs get no specs context |
| SCR-B4 | MINOR | scripts, gates and hooks | the spec-ID census "tripwire" is run by no gate, and its own header records two drifts that went unnoticed |
| IMP-B1 | MINOR | dev-workflows — /implement | Pre-Phase 3 step 3 hard-codes a branch name that contradicts steps 1–2 (convention discarded, key doubled) |
| IMP-B2 | MINOR | dev-workflows — /implement | Phase 4.7 appends an implementation record on a run that committed nothing, a block shape `implementation-format` §1 does not define |
| DEV-B2 | MINOR | dev-workflows — /design, /ready, /conformance | `/ready` says `specs-preflight` "creates no branch, a hard invariant", which is false in session-branch mode |
| DEV-B3 | MINOR | dev-workflows — /design, /ready, /conformance | `/design`'s "Next Epic" loop skips Phase 1.5, so the next Epic is never classified or model-gated |
| DEV-B4 | MINOR | dev-workflows — /design, /ready, /conformance | the `/design` docs page quotes a stop message the command no longer prints |
| VU-B4 | MINOR | dev-workflows — /vuln, /upgrade | A `keep-anyway` regression has no return status; `/vuln` names one, `REGRESSION_KEPT`, that nothing defines |
| VU-B5 | MINOR | dev-workflows — /vuln, /upgrade | Both docs pages still say a revert leaves `node_modules` as the upgrade left it; since 4.14.0 the run restores it |
| VU-B6 | MINOR | dev-workflows — /vuln, /upgrade | `nvd-api.md`'s worked example contradicts its own range rule |
| VU-B7 | MINOR | dev-workflows — /vuln, /upgrade | `nvd-api.md`'s Maven Central query cannot list versions, and its CPE vendor examples are Maven group IDs |
| VU-B8 | MINOR | dev-workflows — /vuln, /upgrade | The GitHub Actions SHA-pin update writes a tag object's SHA for an annotated tag |
| VU-B9 | MINOR | dev-workflows — /vuln, /upgrade | `/upgrade`'s `clean_finish` flips on a component that never reached the repository |
| VU-B10 | MINOR | dev-workflows — /vuln, /upgrade | `/upgrade` writes keys and a resolved folder it can never have |
| VU-B11 | MINOR | dev-workflows — /vuln, /upgrade | `/vuln`'s Step 0 reads `--allow-install-scripts`' value as an `ADDRESS:CVE-ID` token |
| VU-B12 | MINOR | dev-workflows — /vuln, /upgrade | "Branch each CVE from `<current>` instead" gives later CVEs no instruction to switch back to `<current>` |
| VU-B13 | MINOR | dev-workflows — /vuln, /upgrade | The `/vuln` commit template both follows the project's style and is used verbatim |
| VU-B14 | MINOR | dev-workflows — /vuln, /upgrade | `fix-vuln/build-systems.md` lists Cargo in its detection table but has no Cargo section |
| VU-B15 | MINOR | dev-workflows — /vuln, /upgrade | `ecosystems.md`'s NuGet query says the last version is the latest stable |
| PRD-B1 | MINOR | product-workflows — idea → PRD → ARD → spec → epics, decisions, proposals | *Set SPECS_PATH* in four product commands carries any typed path, against the rule that re-asks until it names an existing directory (the D5 class, at sites D5 does not list) |
| PRD-B2 | MINOR | product-workflows — idea → PRD → ARD → spec → epics, decisions, proposals | `/epics` has no `$SPECS_PATH`-unset step and no mapping for `resolve-address`'s `status: invalid`, while the hook and the docs promise that it asks |
| PRD-B3 | MINOR | product-workflows — idea → PRD → ARD → spec → epics, decisions, proposals | `/epics` reads a `refinement_candidate` frontmatter flag that nothing writes or defines, attributing it to a retired reader |
| PRD-B4 | MINOR | product-workflows — idea → PRD → ARD → spec → epics, decisions, proposals | `/update-prd` Phase 1 asks a Refresh-or-Re-do question whose answer nothing reads |
| PRD-B5 | MINOR | product-workflows — idea → PRD → ARD → spec → epics, decisions, proposals | the agents reference page's exclusivity claim about `docs-grounder` is false |
| PRD-B6 | MINOR | product-workflows — idea → PRD → ARD → spec → epics, decisions, proposals | `/epics` Phase 8's Instructions agent still edits files after the handoff, the reason Agent 1 was changed to report only |
| PRD2-B1 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | `/create-prd` never says to write `brd_key`, `brd_parent`, `depends_on` or the BRD-route `sources`, although its final report, its cost step and its docs page all say it does |
| PRD2-B2 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | `/create-prd` cannot take an `@<path>` address, but its docs page offers one, and the resolver's `ambiguous` stop sends the operator there |
| PRD2-B3 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | `--from-prd` on the BRD route: Phase 0 reads the seed and Phase 1 offers two arrays, but Phase 2 says "exactly two files … and no other seed" |
| PRD2-ARD-B3 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | A BRD-route refine resolves the slice's own prior ARD as read-only inherited invariants |
| PRD2-ARD-B4 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | The Phase 6 array selection falls through on *Start fresh* over an ARD the default branch carries |
| PRD2-ARD-B5 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | Phase 7 names `/prd-proposal <PRD>` unconditionally, and it stops on arrival in the ordinary BRD state of a slice with no `prd.md` |
| PRD2-ARD-B6 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | The Epic-level array offers `/dev-workflows:design <EPIC>` without testing for the merged `specification.md` that `/design` stops without |
| PRD2-ARD-B7 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | Phase 0 step 5 gauges `$REPOS_PATH` and runs `enumerate-components` before Phase 1 step 3 resolves `$REPOS_PATH` |
| PRD2-ARD-B8 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | A per-area split writes only `ard-<area>.md`, but the prior-ARD test and the pre-lint look only at `ard.md` |
| PRD2-ARD-B9 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | The docs page misstates the conditions on the `/brd-split` remedy and on repository discovery |
| PRD2-SPEC-B3 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | On a BRD-route Epic run, Phase 2.5 passes `epic: <SLICE-KEY>`, so the Epic's own ARD is never resolved; the claim that "the route resolves a slice and nothing else" is false |
| PRD2-SPEC-B4 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | The `### Next step` routes by what the address resolved, so a picker-chosen per-Epic spec is told to run `/epics <PRD>` rather than `/design <EPIC>` |
| PRD2-SPEC-B5 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | Phase 0 resolves the address in step 1 before step 2 checks `$SPECS_PATH`, against its own "resolve only after `$SPECS_PATH` is settled" paragraph, and maps no `status: invalid` |
| PRD2-SPEC-B6 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | On a BRD slice with no `prd.md`, `/specify` passes key `null` to `emit-cost`/`emit-auto`, so the run's cost goes to pending although its folder exists; the paragraph still says "Phase 0 resolved a BRD key" |
| PRD2-SPEC-B7 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | Phase 5.5 lets pre-lint renumber any duplicate ID, where `pre-lint` restricts that to one this run introduced |
| PRD2-SPEC-B8 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | The commercial step names `/prd-proposal` and "tier 4" on a BRD slice without testing for `prd.md`, though that command stops without one |
| PRD2-PROP-B1 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | Tier 2's "settled register" is met by a register `/create-prd` created holding only open `[AS#n]`, the vacuous case §5 says its presence test exists to prevent |
| PRD2-PROP-B2 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | `/brd-proposal` Phase 7 classifies coverage from "Phase 3's membership list", missing a slice that Phase 6 step 1 excluded |
| PRD2-PROP-B3 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | `proposal-reviewer` check 6 has no umbrella form, so an umbrella's tier claim and its brief floor are checked by nothing, or checked wrongly |
| PRD2-PROP-B4 | MINOR | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | The proposal pair reads a legacy `<KEY>_*.md` PRD "through `addressing` §5's legacy fallback", which §5 says covers folder names only, with no command carrying a filename fallback |
| BRD-B1 | MINOR | product-workflows — BRD route | `/brd-package`'s docs page still says every `fixed` correction changes what the customer is shown (the copy 0e02e28b missed) |
| BRD-B2 | MINOR | product-workflows — BRD route | `/prd-ground` Phase 10's *Ground another declared prerequisite first* names no command, no key and no action, and grounding a prerequisite is not what moves this run's horizons |
| BRD2-B1 | MINOR | product-workflows — BRD route (second pass) | `/brd-interview`'s `[V]` picker is described two contradictory ways, one sentence apart |
| BRD2-B2 | MINOR | product-workflows — BRD route (second pass) | The `/brd-split` docs table gives the `allocate-only` bulk offer the firing condition the command calls a defect |
| BRD2-B3 | MINOR | product-workflows — BRD route (second pass) | The `/brd-split` docs page's "No-op … with two exceptions" drops the third exception, a child out of step |
| BRD2-B4 | MINOR | product-workflows — BRD route (second pass) | The `/brd-split` docs page says a slice block's rationale is "the buildable / blocked / depends-on reading", a grounded-root concept the command retired |
| BRD2-B5 | MINOR | product-workflows — BRD route (second pass) | The will-change picker's `conditional_on: <BRD-KEY>/<decision-id>` collides with the command's own `<BRD-KEY>` placeholder |
| BRD2-B6 | MINOR | product-workflows — BRD route (second pass) | `/prd-ground` Phase 4.5's documentation-lead question has no choices array, and its "re-resolve through Phase 1, then pin through Phase 3" has no defined return path |
| BRD2-B7 | MINOR | product-workflows — BRD route (second pass) | The `/brd-interview` and `/brd-package` docs examples invoke the root key that the docs' own convention names, which both commands refuse |
| BRD3-B5 | MINOR | product-workflows — BRD route (third pass) | Phase 10 names the wrong BRD in the rebaseline fix for a dependent's will-change finding |
| BRD3-B6 | MINOR | product-workflows — BRD route (third pass) | `/prd-ground` Phase 5 does not handle design-grounder's `STALE_INDEX` |
| BRD3-B7 | MINOR | product-workflows — BRD route (third pass) | The missing-reason picker offers `Cancel` that no prose handles, under a sentence that says "exactly two resolutions follow" |
| BRD3-B8 | MINOR | product-workflows — BRD route (third pass) | A finding that keeps its verdict but has an `unprovable` verifier outcome counts as settled in Phase 3 and unsettled in Phase 5 |
| BRD3-B9 | MINOR | product-workflows — BRD route (third pass) | Phase 5 can answer a `[G]` from a `SUPERSEDED` finding |
| BRD3-B10 | MINOR | product-workflows — BRD route (third pass) | A copied-in prerequisite package brings its own rendered prompt and manifest, and part 3 then sends the reviewer to that second prompt |
| BRD3-B11 | MINOR | product-workflows — BRD route (third pass) | Rule 5 marks a copied prerequisite document on "its own front matter line". Rule 4 strips every bundled frontmatter block, and rule 7 forbids rewriting such a copy. |
| BRD3-B12 | MINOR | product-workflows — BRD route (third pass) | A same-day re-run rewrites this date's self-review, prompt and note. Phase 0's guard covers only the bundle directory, and the self-review's numbering rule reads as appending to the earlier run's file. |
| BRD3-B13 | MINOR | product-workflows — BRD route (third pass) | `/brd-reconcile`'s `BRD_RECONCILE_EMPTY_DIGEST` tells the operator to re-run "telling the run the file is prose", but the command gives them no way to say so |
| BRD3-B14 | MINOR | product-workflows — BRD route (third pass) | §7 relation 1 never checks part 6's `in-scope` `[CDF#n]` list, and its reason for excluding part 6 ("prose… not the requirement ids") is false of that list |
| BRD3-B15 | MINOR | product-workflows — BRD route (third pass) | §7.1 calls part 7's escalated-finding fraction "testable", but its source is the self-review, which the same section rules out of relation 1 because it is not in the bundle |
| BRD3-B16 | MINOR | product-workflows — BRD route (third pass) | The `brd-package-reviewer` `INPUT_MISSING` stop has no stop code, and Phase 11's capture-at-block classification leaves it out |
| BRD3-B17 | MINOR | product-workflows — BRD route (third pass) | Phase 5's tier picker lists a fourth option, `Cancel`, that no prose handles, while the paragraph under it says "a fourth would be a tier nothing downstream can read" |
| BRD3-B18 | MINOR | product-workflows — BRD route (third pass) | The docs page says the rendered schema headings are renumbered "so the customer's copy runs from 1"; the command renumbers them `<part>.1`–`<part>.5` and says outright that a restart at 1 is the wrong scheme |
| BRD3-B19 | MINOR | product-workflows — BRD route (third pass) | `/brd-reconcile` gates on the folder's *most recent* prompt, before it knows which package the review answers |
| DOC-A-B5 | MINOR | docs-workflows and the smaller plugins | Phase 5.8's decision arrays differ from the `workflows-core:source-truth` §7.2/§7.3 arrays the run is told it "MUST follow" |
| DOC-A-B6 | MINOR | docs-workflows and the smaller plugins | Stale "inline writer" claims: `current_model` is reported as the writer's model, and §10's handling of `implementation_model` contradicts itself |
| DOC-A-B7 | MINOR | docs-workflows and the smaller plugins | The keyed-mode invariant prescribes a `/clear` docs→PM handoff; the report template and `session-hygiene` prescribe `/compact` (Dev→Dev) |
| DOC-A-B8 | MINOR | docs-workflows and the smaller plugins | The key-discovery scan is invoked with no `--repo` when the slug→clone map holds no clone, which argparse rejects; the run then reports a script failure twice |
| DOC-A-B9 | MINOR | docs-workflows and the smaller plugins | Phase 7's PASS WITH RECOMMENDATIONS branch dispatches `doc-fixer` "for MAJOR findings only" even when no MAJOR survived |
| DOC-A-B10 | MINOR | docs-workflows and the smaller plugins | Docs page says `/epics` has 22 `## Phase` headings; it has 23 |
| DOC-A-B11 | MINOR | docs-workflows and the smaller plugins | Phase 6.4's text labels the `doc-fixer` dispatch as the linter re-run |
| DOC-B-B2 | MINOR | docs-workflows and the smaller plugins | The `# Unreleased` supersede trigger is stated two incompatible ways |
| DOC-B-B3 | MINOR | docs-workflows and the smaller plugins | "No command of this plugin opens [a pull request] anywhere" has been false since `/release-notes` gained its handoff |
| DOC-B-B4 | MINOR | docs-workflows and the smaller plugins | The release-version question has no step and no array, and is displayed before it is asked |
| DOC-B-B5 | MINOR | docs-workflows and the smaller plugins | `key-discovery.py`'s GitHub time budget does not bound the searches it claims to bound |
| DOC-C-B3 | MINOR | docs-workflows and the smaller plugins | `resolve-docs-repo` rung 4's choice is uncapped and has no stated shape, yet `/docs-audit` relies on a Cancel there |
| DOC-C-B4 | MINOR | docs-workflows and the smaller plugins | `docs-audit-reviewer` is told to read the site's `docs_dir` from the profile, a field the profile schema does not have |
| DOC-C-B5 | MINOR | docs-workflows and the smaller plugins | Live contradiction on branch names: the commands' no-convention form is `<prefix>/NOISSUE-<slug>`, but `branch-naming` §1.4 builds `<prefix>/<slug>` |
| DOC-C-B6 | MINOR | docs-workflows and the smaller plugins | The `/docs-init` docs page says the domain vocabulary is "a later command's job", but the authority says no command writes it |
| DOC-C-B7 | MINOR | docs-workflows and the smaller plugins | The `/docs-profile` docs page claims detection of "cross-space override manifests" and "shared registries", which the command never scans |
| DOC-C-B8 | MINOR | docs-workflows and the smaller plugins | `/docs-init`'s Phase 6 leaves `spaces[].id` and `dev_servers.servers[].space` unstated |
| FBA-B1 | MINOR | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | A stale remote-tracking ref forces a `-2` suffix on every handoff branch whose earlier PR merged with delete-on-merge |
| FBA-B2 | MINOR | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | Merged local plugin branches the run is not standing on are never deleted, so they pile up and force suffixes |
| FBA-B3 | MINOR | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | `/create-ard`'s optionality advisory fires "for a small single-repo item" with "small" never defined |
| FBA-B7 | MINOR | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | A repo-local instruction file or README is not named as a "documentation page" in the no-doc-evidence rule, and the grounding agents' evidence contract does not exclude it |
| FBA-B8 | MINOR | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | `grounding-format` §3 has no verdict rule for a premise that is vacuously true because its surface does not exist |
| FBB-B2 | MINOR | field feedback — BOOK-2-01 runs | `consumed_by` is single-valued, so `/specify` overwrites the ARD's consumption record |
| FBB-B3 | MINOR | field feedback — BOOK-2-01 runs | The pre-lint placeholder scan flags literal code, markup and display formats, even in fenced blocks |
| FBB-B4 | MINOR | field feedback — BOOK-2-01 runs | `/create-prd`'s own route template fails its own pre-lint |
| FBB-B5 | MINOR | field feedback — BOOK-2-01 runs | `prd-format` does not say how `[AC#N]` are grouped, and the natural reading trips the duplicate-id BLOCKER |
| FBB-B9 | MINOR | field feedback — BOOK-2-01 runs | `proposal-format` §6 makes a false claim about rounding |
| FBB-B13 | MINOR | field feedback — BOOK-2-01 runs | The fix-cycle overlap read is too narrow: it misses imported rules and new outcomes added to an existing trigger |
| FBB-B15 | MINOR | field feedback — BOOK-2-01 runs | The version line after a verdict names no requirement whose Rule changed after the verdict |
| FBB-B17 | MINOR | field feedback — BOOK-2-01 runs | `/epics` asks keep-whole only after `epic-writer` has already split by size |
| FBB-B18 | MINOR | field feedback — BOOK-2-01 runs | `code-scanner` line numbers are not validated |
| FBB-B19 | MINOR | field feedback — BOOK-2-01 runs | The pre-lint auto-link branches leave a bare specs key in limbo, and `epic-writer` writes keys bare |
| FBB-B20 | MINOR | field feedback — BOOK-2-01 runs | `/epics` `body_facts` makes a false claim on the falling-back handoff |
| FBB-B24 | MINOR | field feedback — BOOK-2-01 runs | The `/design` fan-out brief carries no spec literals, surviving surface or settled values |
| FBB-B28 | MINOR | field feedback — BOOK-2-01 runs | The `conformance-tracer` handoff has no file input or output for large runs, and its evidence may use loose ranges |
| FBB-B29 | MINOR | field feedback — BOOK-2-01 runs | `not-checkable` requirements are count-only in `_conformance.md`, yet `/conformance` relies on them being recognisable later |
| FBB-B32 | MINOR | field feedback — BOOK-2-01 runs | Step 7.5 writes an open `- [ ]` note for a deferral the user decided in the same run |
| FBB-B38 | MINOR | field feedback — BOOK-2-01 runs | A post-review departure from the literal `design.md` or spec text leaves the specs contradicting the code |
| FBB-B41 | MINOR | field feedback — BOOK-2-01 runs | Small `/prd-ground` ambiguities: the tail after a Phase 3 stop, in-repo prose as evidence, reusing a repository answer, and a BRD wireframe absent from the census |
| FBB-B43 | MINOR | field feedback — BOOK-2-01 runs | `/brd-interview`: follow-up prompts may be batched, and the round-record and question-set layouts are unspecified |
| FBB-B45 | MINOR | field feedback — BOOK-2-01 runs | `/brd-package` and `/brd-reconcile`: the display before the question, scan tooling, prose references, author attribution, `[SR#n]` answer mapping, and bundle filenames in section 12 |
| TRK-B2 | MINOR | older review records | An edition-port obligation from the 2026-08-22 docs restructure has no entry in to-fix.md |
| DQS-B1 | MINOR | documentation quality — links, navigation, page-set parity (all plugins) | `guideline-reviewers`: README does not link its workflow diagram or getting-started page, and the repo-root table has no Docs link for it |
| DQS-B2 | MINOR | documentation quality — links, navigation, page-set parity (all plugins) | Workflow, BRD-route, roles and getting-started pages draw or name every command but link to none of the command pages |
| DQS-B3 | MINOR | documentation quality — links, navigation, page-set parity (all plugins) | 18 command pages do not link back to their plugin's workflow page |
| DQS-B4 | MINOR | documentation quality — links, navigation, page-set parity (all plugins) | Next and previous commands named in prose but not linked; `/harvest-decisions` never mentions `/promote-decisions`; no command page links `/docs-audit` |
| DQS-B5 | MINOR | documentation quality — links, navigation, page-set parity (all plugins) | 18 relative links leave the plugin directory and break in the installed cache |
| DQS-B6 | MINOR | documentation quality — links, navigation, page-set parity (all plugins) | Page-set parity holes in `docs-workflows` and `security-workflows`; command pages name a "Roles and phases" page that the plugin does not have |
| DQS-B7 | MINOR | documentation quality — links, navigation, page-set parity (all plugins) | Internal design-decision IDs (D4 … D25) leak into user pages with nothing to resolve them against |
| DQS-B8 | MINOR | documentation quality — links, navigation, page-set parity (all plugins) | 317 bare `workflows-core:<name>` citations and 306 `§` section citations on user pages, none linked |
| DQS-B11 | MINOR | documentation quality — links, navigation, page-set parity (all plugins) | obsidian-llm-wiki README: the local-install command is `cc`, not `claude`, and the marketplace step gives no command |
| DQS-B12 | MINOR | documentation quality — links, navigation, page-set parity (all plugins) | The READMEs of the three plugins without a `docs/` tree leave out what a user needs |
| DQC-B2 | MINOR | documentation quality — family entry points and workflows-core | "Option B" cost snapshot and `cost_statusline_usd` point at a page that never mentions either |
| DQC-B3 | MINOR | documentation quality — family entry points and workflows-core | three of the five family getting-started pages skip the status-line step the root README calls step 5 and the core index says to "run first" |
| DQC-B4 | MINOR | documentation quality — family entry points and workflows-core | maintainer `grep` recipes over `plugins/*/…` are given to users as the way to find things |
| DQC-B5 | MINOR | documentation quality — family entry points and workflows-core | internal vocabulary and § citations into references a user never opens, on the core plugin's user pages |
| DQC-B6 | MINOR | documentation quality — family entry points and workflows-core | stale and changelog-style statements on user pages |
| DQC-B7 | MINOR | documentation quality — family entry points and workflows-core | the family map omits two forward steps the commands offer |
| DQC-B8 | MINOR | documentation quality — family entry points and workflows-core | the core docs never point a user to the three run flags under their own name |
| DQD-B1 | MINOR | documentation quality — dev-workflows and security-workflows | The first-run example key `EPIC-98760` is not a key shape any Epic gets, so a new user copying it learns the wrong form |
| DQD-B2 | MINOR | documentation quality — dev-workflows and security-workflows | The `/implement` page's example promises a next step the command no longer offers |
| DQD-B3 | MINOR | documentation quality — dev-workflows and security-workflows | The dev workflow diagram skips the PE's PRD-level `/conformance` before documentation, and sends every *amend the document* to `/specify` |
| DQD-B4 | MINOR | documentation quality — dev-workflows and security-workflows | The environment layout files follow-ups under `dev-workflows/`, contradicting the follow-ups and roles pages |
| DQD-B5 | MINOR | documentation quality — dev-workflows and security-workflows | "`dev-workflows` reads five environment variables" counts one it never reads |
| DQD-B6 | MINOR | documentation quality — dev-workflows and security-workflows | The dev Session cost page's worked example names product-workflows commands as "dev-workflows commands", and leaks an internal team count |
| DQD-B7 | MINOR | documentation quality — dev-workflows and security-workflows | Maintainer vocabulary and change history fill the user pages |
| DQD-B8 | MINOR | documentation quality — dev-workflows and security-workflows | The `/vuln` and `/upgrade` diagrams leave out the commit, push and pull request step, and the per-unit loop |
| DQP-B1 | MINOR | documentation quality — product-workflows | Getting started promises a handoff and a `/create-prd` takeover that a run with an unanswered question never gets |
| DQP-B2 | MINOR | documentation quality — product-workflows | Getting started never tells the reader to merge the pull request, or what to do with a specs repo that has no remote |
| DQP-B3 | MINOR | documentation quality — product-workflows | The BRD-route parameter table lists `@<idea.md>` as an optional argument of `/create-prd` on that route; the command skips the idea ladder there entirely |
| DQP-B4 | MINOR | documentation quality — product-workflows | The `/create-prd` page says the BRD route seeds from `prd-seed.md`, which a normal BRD route never has |
| DQP-B5 | MINOR | documentation quality — product-workflows | The main workflow diagram routes `/implement` straight to the docs commands, leaves out the security scan, and gives the PE's PRD conformance no edge onward |
| DQP-B6 | MINOR | documentation quality — product-workflows | Both workflow diagrams leave out offers their commands make, and `brd-workflow.md` describes the re-entry from `/brd-reconcile` as two edges when it is four |
| DQP-B7 | MINOR | documentation quality — product-workflows | Internal rulings and reference-section citations leak into user pages, with no link a user could follow |
| DQP-B8 | MINOR | documentation quality — product-workflows | The docs teach example keys that carry a folder-kind token, and use a different key on every BRD-route page |
| DQP-B15 | MINOR | documentation quality — product-workflows | Nine of the 16 command pages never link to either workflow page |
| DQW-B3 | MINOR | documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki | getting-started's "no docs yet" path sends the new user to `/document` and never mentions `/docs-audit` or the route page |
| DQW-B4 | MINOR | documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki | `/docs-serve`'s next-step offer and its docs page name `/document` as the next step, which contradicts the route |
| DQW-B5 | MINOR | documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki | The plugin README draws a third version of the documentation route, and it disagrees with the route page |
| DQW-B6 | MINOR | documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki | The split between `workflow.md` and `docs-workflow.md` is unclear: the file names invert the titles, and one command page calls the route "The documentation workflow" |
| DQW-B8 | MINOR | documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki | The `/api-guideline-reviewer` page hides that five bundled Spectral rules ship with placeholder literals that fail every real spec at `error` |
| DQW-B9 | MINOR | documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki | The `/guideline-reviewer` page says it needs "nothing else", but the agent runs a bundled Python scanner that getting-started says needs `python3` 3.11 |
| DQW-B10 | MINOR | documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki | The docs-workflows docs leak maintainer vocabulary a user cannot resolve: design-decision ids, `§` citations into references, "ceded" runs and "the split" |
| DQW-B11 | MINOR | documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki | `/document` and `/release-notes` pages refer to "the tracker" and "the docs automation" as if every reader had them |
| DQW-B13 | MINOR | documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki | Three docs-workflows command pages never link back to the Workflow overview |
| DQW-B14 | MINOR | documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki | prose-style README is stale about which family uses it, and gives no install command |
| DQW-B15 | MINOR | documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki | The acli README does not say how to use the skill or how to authenticate headless, though it says both are documented |
| SEC-B5 | NIT | security-workflows | the roles page understates which unwritten fixes are offered again |
| GIT-B5 | NIT | workflows-core — git, handoff, resume pointer | phase-handoff §3.6 misquotes the offline note it says it reuses |
| GIT-B6 | NIT | workflows-core — git, handoff, resume pointer | followup-emission says it mirrors nothing, then says twice to mirror another plugin's command |
| GIT-B7 | NIT | workflows-core — git, handoff, resume pointer | read-only-repos' own consumer list is short of its rules file |
| CORE-B9 | NIT | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | "the twenty-eight commands that measure themselves (§1)" points at a section that does not list them |
| CORE-B10 | NIT | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | a stale "pending check" sits beside the live measurement that settles it |
| CORE-B11 | NIT | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | two comments in `cost-prices.yaml` are behind the page they cite |
| CORE-B12 | NIT | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | `classification.md` §4's "Both agents this parenthetical names" names no agents |
| CORE-B13 | NIT | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | `handoff/code-scanner.md` gives `REPO_MISSING` a narrower meaning than the agent returns it for |
| CORE-B14 | NIT | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | `test-notify` misses the single-module Gradle form the family itself prescribes |
| CORE-B15 | NIT | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | the session-feedback page says the feedback ladder's second rung is "a pending location" |
| CORE-B16 | NIT | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | the workflows-core README's documentation table omits the Grounding sources reference page |
| IMP-B3 | NIT | dev-workflows — /implement | Phase 4.5's reason for the falling-back array lists the §3.4 rows naming `design.md` without `/conformance` |
| IMP-B4 | NIT | dev-workflows — /implement | the `/implement` docs page's agent census omits `defect-reporter` |
| DEV-B5 | NIT | dev-workflows — /design, /ready, /conformance | an author's note has leaked into `DESIGN_NO_SPEC`'s printed message |
| VU-B16 | NIT | dev-workflows — /vuln, /upgrade | `/upgrade`'s executor dispatch names no model for `SIGNIFICANT` |
| VU-B17 | NIT | dev-workflows — /vuln, /upgrade | The install references say `install-time-code.md` "says why" Poetry and the others install unchanged; it gives no reason |
| PRD-B7 | NIT | product-workflows — idea → PRD → ARD → spec → epics, decisions, proposals | the hooks page miscounts the plugin's other commands and calls them all keyed |
| PRD-B8 | NIT | product-workflows — idea → PRD → ARD → spec → epics, decisions, proposals | the environment page says every command offers to enter a path when `$SPECS_PATH` is unset; `/harvest-decisions` and `/promote-decisions` stop flat |
| PRD-B9 | NIT | product-workflows — idea → PRD → ARD → spec → epics, decisions, proposals | `/epics` Phase 3.5's adaptive code-scan array can show the same setting twice |
| PRD2-B4 | NIT | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | `prd-reviewer` still calls the BRD-route key `<BRD-KEY>` |
| PRD2-B5 | NIT | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | small text defects in `/create-prd` and its docs page |
| PRD2-ARD-B10 | NIT | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | Smaller disagreements between the docs page and the command or its references |
| PRD2-ARD-B11 | NIT | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | Three stops carry no stop code and are missing from Phase 8's `emit-block` classification |
| PRD2-SPEC-B9 | NIT | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | On the BRD route, the handoff always declares `<prd_dir>/decisions.md`, even where the slice holds none, so §4.1 reports a false *declaration unaccounted for* |
| PRD2-SPEC-B10 | NIT | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | The docs page's BRD-route example puts a slice "one level under `specifications/`", and its `--enforce-model` list omits `architecture-grounder` |
| PRD2-PROP-B5 | NIT | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | The `/prd-proposal` docs example says the tier-2 next-step array offers `/create-ard` "first"; the command's array puts it third |
| PRD2-PROP-B6 | NIT | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | A folder holding a `proposal-brief.md` but no `proposal.md` counts as a revision, so the run looks for an anchor and archives a proposal that do not exist |
| BRD-B3 | NIT | product-workflows — BRD route | `/prd-ground` Phase 9 names `brd-link.md` unconditionally on a full run, against its own "never name an unchanged path" rule |
| BRD2-B8 | NIT | product-workflows — BRD route (second pass) | Agent input examples use a key the agent's caller refuses; `/brd-package` Phase 3 does not say `questions` is optional |
| BRD2-B9 | NIT | product-workflows — BRD route (second pass) | The `/brd-split` docs "What it produces" omits `covered-here` and says "the first two of the following" about a list that sits above |
| BRD2-B10 | NIT | product-workflows — BRD route (second pass) | The `/brd-intake` docs page says `/brd-interview` "gates on" the slice ledger |
| BRD3-B20 | NIT | product-workflows — BRD route (third pass) | Both grounders are told to assign `horizon`, which their caller says they cannot and then overrides; design-grounder's class-4 rule needs data it is never handed |
| BRD3-B21 | NIT | product-workflows — BRD route (third pass) | The Final report explains a slice's non-zero `unallocated` term as a row "delegated to a child" |
| BRD3-B22 | NIT | product-workflows — BRD route (third pass) | `coverage-ledger-format` §6 still models a root ledger holding `covered-here` rows, a state §5 calls illegal |
| BRD3-B23 | NIT | product-workflows — BRD route (third pass) | §6.2 says `/brd-split` gates `grounding/code-grounding.md`, which it does only in `allocate-only` mode |
| BRD3-B24 | NIT | product-workflows — BRD route (third pass) | The shared lane offers `/brd-reconcile <BRD-KEY> @<review-file>` after `/brd-package` unconditionally; Phase 10 writes no path on the repository route |
| DOC-A-B12 | NIT | docs-workflows and the smaller plugins | Model-routing text names a dispatched step, "the folder read", that is no agent |
| DOC-A-B13 | NIT | docs-workflows and the smaller plugins | Garbled residue in `doc-planner`: "NO kea key", "generated by keyed automation" |
| DOC-A-B14 | NIT | docs-workflows and the smaller plugins | Agents reference omits `defect-reporter` from the list of `workflows-core` agents these commands dispatch |
| DOC-A-B15 | NIT | docs-workflows and the smaller plugins | `toolchain-preflight` §5 says Cancel leaves nothing written, which is false after `/document`'s inline profiling |
| DOC-B-B6 | NIT | docs-workflows and the smaller plugins | A repository with an `error` can still carry a non-null `scanned`, against the reference's contract |
| DOC-B-B7 | NIT | docs-workflows and the smaller plugins | The docs page states address rules the command does not have |
| DOC-B-B8 | NIT | docs-workflows and the smaller plugins | Phase 6's route array promises a docs link on a PM-phase run, where the run never asks for one |
| DOC-B-B9 | NIT | docs-workflows and the smaller plugins | Two character counts in the changelog guidelines are wrong |
| DOC-C-B10 | NIT | docs-workflows and the smaller plugins | `/docs-serve`'s invariant lists its `workflows-core` citations as "`epic-picker` and `next-phase-offer`", omitting `run-flags` and the new `escalation-rules core` load |
| DOC-C-B11 | NIT | docs-workflows and the smaller plugins | The backlog page reads `threshold` as "at or above", where the schema and the route say "at or below" the priority number |
| DOC-C-B12 | NIT | docs-workflows and the smaller plugins | The workflow page says `/docs-serve` writes "only a pid/port record", but the command writes three things |
| FBA-B4 | NIT | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | `/brd-intake`'s "byte-for-byte" copy does not exclude the source's mode bits |
| FBA-B5 | NIT | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | `/brd-split`'s *Assign to a named slice* key prompt: no rule for asking it in the same call, and no pre-fill from the Phase 1.5 placement |
| FBA-B6 | NIT | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | `/prd-ground` Phase 0 does not say which of `specs-repo-git` §3's two orders it takes |
| FBA-B9 | NIT | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | A re-asked handoff consent choice leaves two contradictory `Phase handoff:` outcome lines |
| FBB-B6 | NIT | field feedback — BOOK-2-01 runs | `/create-prd` Phase 1 step 1 says "Confirm" but gives no choices array |
| FBB-B22 | NIT | field feedback — BOOK-2-01 runs | `/epics` does not pass house style to `prose-style-checker` |
| FBB-B27 | NIT | field feedback — BOOK-2-01 runs | The `/conformance` walk's question and rationale cadence is unstated |
| FBB-B34 | NIT | field feedback — BOOK-2-01 runs | `risk-planner` acceptance checks are not required to use fixed-string grep |
| FBB-B36 | NIT | field feedback — BOOK-2-01 runs | `test-baseliner` verify lists new failures by name only |
| FBB-B39 | NIT | field feedback — BOOK-2-01 runs | Session files pushed straight to the default branch are not called out |
| TRK-B1 | NIT | older review records | The 2026-10-15 review record says C1–C8 are still tracked in to-fix.md, but they were fixed and removed |
| DQS-B9 | NIT | documentation quality — links, navigation, page-set parity (all plugins) | Command pages without a diagram where their siblings have one |
| DQS-B10 | NIT | documentation quality — links, navigation, page-set parity (all plugins) | workflows-core's README does not link the family map, the one diagram that draws the whole family |
| DQC-B9 | NIT | documentation quality — family entry points and workflows-core | root README's "three core environment variables" cannot be matched to the five it exports |
| DQC-B10 | NIT | documentation quality — family entry points and workflows-core | dev-workflows' getting-started says it reads five variables, and the core environment page says four |
| DQC-B11 | NIT | documentation quality — family entry points and workflows-core | workflow.md counts "three dashed and solid edges" where the diagram draws five |
| DQC-B12 | NIT | documentation quality — family entry points and workflows-core | /frames' diagram labels Phase 0 "kind-gated" on a page that says no kind is passed |
| DQC-B13 | NIT | documentation quality — family entry points and workflows-core | core pages call the five-plugin family "the `dev-workflows` plugin family" |
| DQC-B14 | NIT | documentation quality — family entry points and workflows-core | the root README's "Directory structure" leaves out three of the layouts the variables expect |
| DQD-B9 | NIT | documentation quality — dev-workflows and security-workflows | The security workflow diagram draws `/dev-workflows:conformance` as an edge label, not a node, and omits the scan's own next step to the PE's `/conformance <PRD>` |
| DQD-B10 | NIT | documentation quality — dev-workflows and security-workflows | The register's status diagram has no `reopened → open` edge, though triage suggests *decide later* for a reopened finding |
| DQD-B11 | NIT | documentation quality — dev-workflows and security-workflows | Missing space joins two paragraphs on the `/ready` page |
| DQP-B9 | NIT | documentation quality — product-workflows | "Two segments or three" contradicts the key grammar, which fixes no depth |
| DQP-B10 | NIT | documentation quality — product-workflows | `brd-workflow.md` and `prd-ground.md` carry search-and-replace residue and development-history wording |
| DQP-B11 | NIT | documentation quality — product-workflows | The `/idea` page names a personal-vault path and lists "a file" and "a saved file" as different sources |
| DQP-B12 | NIT | documentation quality — product-workflows | The workflow page's role and artifact-home tables disagree with the roles page and the `/specify` page |
| DQP-B13 | NIT | documentation quality — product-workflows | Getting started says the three optional variables each "degrade to a documented default or a silent skip"; two do not |
| DQP-B14 | NIT | documentation quality — product-workflows | The README's documentation table leaves out three reference pages that the sibling README lists |
| DQP-B16 | NIT | documentation quality — product-workflows | Three reference paragraphs are too long for a person to read |

## Cross-reference: `docs/superpowers/to-fix.md` at `0e02e28b`

**None of its items is fixed.** D6 is partly fixed; every other D, C and L item is still present, and the E items are ports to editions on another machine, which this repository cannot verify. The restatement column is written for a fixer who has not read to-fix.md's surrounding context. Line numbers are at `0e02e28b`.

| ID | Status | Evidence (`path:line` or commit) | Fixer-ready restatement |
|---|---|---|---|
| E1 | Not verifiable from this repo | Body changes: `cb19fa38`, `d0829c80`, `11a4fa70`, `56a3c842`. The census comment cited is still at `scripts/check-docs.sh:1843` ("500 of this tree's 643"). | Port this repo's `scripts/check-docs.sh` body (from `FAILURES=0` down) by `cp` into the internal Claude and Copilot editions. That body includes check 12's ASKS/PROMISES split. Fix any edition label that now fails as a promise, prove parity with `cmp`, and run the edition's gate chain with `--selftest`. |
| E2 | Not verifiable from this repo | `cb19fa38`, `d0829c80`, `16acc463` | In each edition that carries the same passages, port the 2026-10-15 review's plugin fixes (F1–F5, the fixed MINORs, the re-review fixes). An edition that lacks the underlying merge takes the merge first, or records the skip. |
| E3 | Not verifiable from this repo | `git log -S'command emits' -- scripts/check-docs.sh` | Check 9's singular count ("slash commands?", "command emits") ports with E1's body copy. Re-measure each gated README's first match before porting. The internal edition lands by pull request only. |
| E4 | Not verifiable from this repo. Its text is slightly stale (see §5). | `git log --first-parent 7c13ce05..56a3c842` | Port every merge since `7c13ce05` to both editions, classified by port scope. First decide whether the editions take the load-by-part machinery. The BRD route is never ported. |
| C2 | Still present | `plugins/workflows-core/references/implementation-format.md:430-434` — the subject leg still accepts any default-branch commit "made no earlier than that block" carrying `[<key>]`. | In `implementation-format` §5's merged test, the subject leg passes on any later commit whose subject carries the unit's `[<key>]`. That includes a teammate's commit, or an older pull request merging after a newer run. So an Epic whose pull request is still open reads as merged (branch gone) or as `after_merge` (branch present). Fix it in §5 only, never in a consumer, and verify against the PRD run and all three `unit-branch` consumers (`/implement`, `/conformance`, `/security-workflows:scan`). Done means a key-carrying commit that is not this block's merge no longer satisfies the test. |
| C9 | Still present | The third leg exists only inside `unit-branch` step 2 (`implementation-format.md:409`). The merged test itself still has two legs (`:428-430`). The PRD run uses the merged test alone (`plugins/dev-workflows/commands/conformance.md:104`, `:125-129`). | `/conformance`'s PRD run cannot see a squash merge whose subject lost `[<key>]`. It calls that Epic "not shown merged" and recommends *Stop until it is merged*, which can never be lifted. Fix it in §5: move the content-test third leg (the tip adds nothing to `<ref>`) into the merged test itself, so the PRD run sees the same merge `unit-branch` sees. |
| D1 | Still present | `plugins/workflows-core/references/phase-handoff.md:236-237`. B′ requires the worktree to equal the fork point. Where the branch also changed the path, B′ fails and row B passes. | `require-on-main` row B reads the branch's copy of a document whenever this run owns the branch, even when the default branch also changed that document since the fork. A `/design` that amended the spec on its branch, after a refine merged on `main`, then reads a copy without the refine. Add a test for "both sides changed" (`git diff --quiet <merge-base> <default-ref> -- ./<path>` exits 1) and stop, or merge, instead of passing. |
| D2 | Still present | B′'s stop prints `git merge <default-ref>` unconditionally (`phase-handoff.md:236`). Row C withholds its write remedy under `specs_git: misrooted` (`:240`) and on a read-only mount (`:320`), which says "B′'s merge is the operator's to run". | On a run carrying `specs_git: misrooted`, or on a read-only specs mount, row B′'s stop still tells the operator to run a merge in the specs repo. Make B′ match row C: under either condition, name the reason and drop or qualify the merge command. |
| D3 | Still present (medium confidence) | `plugins/dev-workflows/commands/ready.md:148-151`. `/ready` runs `require-on-main` only on each `specification.md`/`design.md` "path located above", found in the working tree. F1's ref listing covers the ARD only (`ard-resolution`). | Apart from the ARD, artifacts a consumer finds by listing the working tree are missed when they reached `main` after the consumer's own branch was cut. `/ready` then reports such a `specification.md` as missing instead of stopping on B′. First measure which consumers list rather than gate. Then list `<default-ref>` too, as F1 did for `ard-resolution`, so the gate sees the ref-only file. |
| D4 | Still present | `plugins/docs-workflows/commands/document.md:323-324`: a base named at *Revise plan* "replaces it the same way". `:514` and `:573` still skip the missing-repos gates whenever "Phase 1 took *Proceed without the repos*". `:394`'s `Repos:` line has no PRD-only form. | In `/document` keyed mode, naming a repos base at Phase 2's *Revise plan* does not cancel Phase 1's *Proceed without the repos*: Phase 4 still treats every repo as PRD-only. Make the Phase 4 conditions say "unless a base was named at *Revise plan*". Give the plan's `Repos:` line a PRD-only form. |
| D5 | Still present, at four more sites than to-fix.md lists: `/create-prd:77`, `/update-prd:29`, `/create-ard:209`, `/specify:211` (also logged as PRD-B1 below) | `plugins/dev-workflows/commands/design.md:84`, `ready.md:104`, `conformance.md:47`: each "asks for the path in plain text and carries it". None cites the re-ask rule (`plugins/workflows-core/references/escalation-rules.md:224-233`), and none is in its citer list (`:235-246`). | The *Set SPECS_PATH* answer in `/design`, `/ready` and `/conformance` accepts any typed path, even one that does not exist. Each should cite `escalation-rules`' *Required path environment variable unset* rule: carry the answer only once it names an existing directory, else ask again. Add the three to that rule's citer list. |
| D6 | Partly fixed: `/epics` Phase 3.5 now asks the refresh policy only where its question turns the scan on (`epics.md:543`); `/create-ard`, `/specify` and `/epics` Phase 1 still ask it before the no-code answer | `plugins/product-workflows/commands/create-ard.md:353-354` (refresh asked at step 4, after step 3's REPOS_PATH answer). `epics.md:316-326` (asked before the REPOS question; "goes unused" after *Turn code scan off*) and `:543` (Phase 3.5 asks it after re-resolving). `specify.md:417-430` (step 3 refresh before step 4's *Proceed without code scan*). | The repo refresh-policy question is put even when the run's code-scan / REPOS_PATH answer means no code will be read. In `/create-ard`, `/epics` (Phase 1 and Phase 3.5) and `/specify`, order the steps so that refresh is asked only once code scanning is known to be on, and is skipped otherwise. |
| D7 | Still present | `plugins/product-workflows/commands/brd-split.md:1488-1498` resolves REPOS_PATH once. `:1737`'s Skill call passes only `--repos …`. The child's `prd-ground.md:527-533` re-resolves `${REPOS_PATH:-/workspace}` and stops/asks again. | A REPOS_PATH the operator gives at `/brd-split`'s *Ground now* is not passed to the child `/prd-ground` runs, so each child asks again. Either pass the base to the children (a flag, or `--repos` absolute paths that skip Phase 0 step 7), or make step 7 accept `--repos` absolute paths without requiring `$REPOS_PATH`. |
| D8 | Still present | `plugins/product-workflows/commands/epics.md:819`: a split at *Count once more before the handoff* "follow[s] the review", and the run only names it in the verdict line (`:821`). There is no offer of the unspent re-review (`escalation-rules.md:520`). | `/epics`' final size count can split an Epic after the review returned. The run names the split among the post-verdict edits, but never offers the re-review the cap still holds. Add the *Edits after a verdict that is not BLOCK — the unspent re-review* offer after a post-review split, or move the final count ahead of the review. |
| D9 | Still present (low confidence: the slug rule was not re-traced) | `plugins/product-workflows/commands/prd-ground.md:832-849`: pins are compared by slug, and the remedies name a repo "the file records". `grounding-format` §4 is unchanged. No upgrade note was added for 3.33.3. | Renaming an origin-less clone (slug = directory name) between `/prd-ground` runs makes the new name collide with the old pin under another slug. The run loops between `PRD_GROUND_AMBIGUOUS_PIN` and the path question, or records the repo twice. Give an origin-less clone a stable identity, or recognise the rename, and add a CHANGELOG upgrade note. |
| D10 | Still present | `prd-ground.md:670-676`: the specs repo (`rev-parse --show-toplevel`) and the docs root are left off by path, with no `realpath`. The file contains no `realpath`. | `/prd-ground` excludes the specs repo and the docs root from its candidate list by comparing paths as strings. A symlinked or relative path slips through. Compare `realpath`s, as `release-notes.md` does. |
| D11 | Still present | `plugins/product-workflows/agents/epic-writer.md:42`: "carries a `kept_whole:` line … write that Epic whole". | `epic-writer`'s `kept_whole` instruction ("write that Epic whole") can be read as forbidding a component split too, though `kept_whole` only overrides the size limit. Reword it to "never split it by size" (a component split still applies). |
| D12 | Still present | `scripts/check-docs.sh:1498-1519`: the ASKS/PROMISES families lack `\(describe\b`, `^provide\b` and `^quote\b`. | With the `(you'll be prompted` marker removed, most marked labels still pass check 12. Re-measure, then add the cheap ASKS/PROMISES families that fire on no correct label (`\(describe\b`, `^provide\b`, `^quote\b`; not `^add\b`). Port the body per E1. |
| D13 | Still present | `escalation-rules.md:52`: "never as a picker built for it". About 38 `["… (you'll be prompted…)", "Cancel"]` arrays remain (`grep -rhoE` over commands, references and agents; to-fix counted 41 at `7c13ce05`). | §0 says a text-only answer is never asked through a picker, yet dozens of two-option "text (you'll be prompted)" + "Cancel" arrays remain. Either amend §0 to say an array with a real alternative (Cancel) is not "built for" the text, or convert the arrays to plain-text questions. |
| D14 | Still open (a decision is owed) | `phase-handoff.md:236`: B′'s plain form ends "then commit the merge and re-run", with nothing about the push. | After the operator merges `main` into the plugin branch per B′, `commit-artifacts`' `push-scope` will not push the operator's merge commit, so the run reports *Committed, not pushed*. Pick (a), the recommended option: add to B′'s stop that the operator pushes the merge (`git -C "$SPECS_PATH" push origin <branch>`) or the next handoff will, and that session commits wait until then. Or pick (b): widen `push-scope`, which first needs the rationale re-argued. |
| D15 | Still present (fix only with a measured case) | `phase-handoff.md:236` still tests `ls-files --others --exclude-standard`. | B′'s untracked-copy test ignores `.gitignore`d files, so an ignored copy at a gated path reads as unchanged and B′ fires. No family run is known to reach this; leave it until a case is measured. |
| D16 | Still present (still to verify; its quoted text is stale) | `plugins/product-workflows/commands/create-prd.md:365`, `create-ard.md:296`, `specify.md:342`: "Ignored, every /create-prd, /create-ard and /specify run on this slice stops here the same way." to-fix quotes it as "…on this slice from <branch> stops…". | The general (non-B′) `*_REGISTER_NOT_ON_MAIN` stops claim that every run of the three commands on the slice stops the same way. A run from another command's branch may instead meet row C, which offers a switch-and-pull. Check each row the general form reports (D, E, the C rows), then make the sentence true or narrow it. |
| L2 | Still open (live-run verification) | No gate checks it. The one resume pointer modified in the demo specs repo since D merged (`bookstore-specs/…/PRD-BOOK-2-01-verified-ratings/dev-workflows/resume.md`) was written on 2026-10-16, before D, and has no `(waiting since …)` marker. | In the next live run that writes `resume.md`, confirm three things: the `(waiting since …)` marker beside a carried command item, *Last completed* with its UTC offset, and the register slug beside each Security Engineer offer. Then confirm the next run's §1 carry reads them back. |
| Accepted 1 (`/brd-reconcile` *Correct it* reason) | Accepted, unchanged | product-workflows 3.34.5's pick record | Not to fix. |
| Accepted 2 (resume-pointer settle rule errs to carrying) | Accepted, unchanged | `session-hygiene` §1; Ruling 39 | Not to fix. A case outside the stated lists is a new defect. |
| Accepted 3 (`.coverage-ledger.*.tmp` after a kill) | Accepted, unchanged | Ruling 37 | Not to fix. |

### Stale text in to-fix.md itself

- **The *Design-level* intro (`docs/superpowers/to-fix.md:96`) says "Of those items only C2, in the section above, is still open."** C9, added by `b0272794` after that sentence was written, is also open in that section. The same paragraph still speaks of re-reviewing once the `/conformance` rework "reaches [main] with the `iv-gu/security-workflows-scan` merge". That merge landed as `c3cd9d3e`, so the condition has already happened and the re-review it defers is owed now.
- **D16's quotation (`to-fix.md:115`) no longer matches the tree.** It quotes "…run on this slice from <branch> stops here the same way". The text at `create-prd.md:365`, `create-ard.md:296` and `specify.md:342` now reads "…run on this slice stops here the same way". The `:361`/`:292`/`:338` line numbers are at `25a3373c`, which the item says.
- **E4's source range stops at `56a3c842`.** It does not list the three later commits on main: `01e80e9c` (to-fix itself), `b4ab29c7` (product-workflows 3.36.1; it rewords `/brd-package`, `bundle-packaging`, `/create-prd`, its docs page and `decision-register-format` §7 about what the customer sees) and `0e02e28b` (`/brd-package`). All three are the list itself or BRD-route customer wording, so most likely "not ported". But `b4ab29c7` also edits `/create-prd` and `decision-register-format`, which the editions do carry. Classify that edit explicitly rather than leaving it out by range.
- **The *Coverage* line (`to-fix.md:9`) says "as of 2026-10-15"** and lists the 2026-10-24 additions as "E4, L2 and the last two *Accepted* entries". That is accurate after `b4ab29c7` removed L1.
- E1's census quote ("500 of this tree's 643") still matches `scripts/check-docs.sh:1843`.
- **The review record `docs/superpowers/reviews/2026-10-15-review-of-five-merges.md`** still says C1–C8 are tracked in to-fix.md; they were fixed and removed (TRK-B1 below).

### The other older records

- **`ai-workflows-bugs.md`** (repository root, rounds 1–3, 2026-09-30 … 10-01): every item, AW-1 … AW-24, is fixed, withdrawn or documented at `0e02e28b`. AW-3's headroom note still holds: `.claude/rules/gates.md` is at 19,987 and `.claude/rules/dev-workflows.md` at 19,939 characters, against the 20,000 warning.
- **`docs/superpowers/reviews/2026-10-15-review-of-five-merges.md`:** C1, C4, C7, C8 fixed (`12f2408b`, `4069aa29`); C3, C5 fixed on the commit's word; C6 moot; C2 still open (to-fix.md).
- **`docs/superpowers/verification/2026-08-22-docs-restructure-open-items.md`:** every item closed; its edition-port obligation is untracked (TRK-B2 below). **`2026-07-14-copilot-port-found-claude-bugs.md`:** its one item is moot.

## Field feedback accounted for

| File in `bookstore-specs` | Entries | Fixed since | Still present (logged here or in the gaps file) | No longer applicable |
|---|---|---|---|---|
| `specifications/PRD-BOOK-1-…/dev-workflows/BOOK-1-feedback.md`, `…/BRD-BOOK-2-…/dev-workflows/BOOK-2-feedback.md`, `…/PRD-BOOK-2-02-…/dev-workflows/BOOK-2-02-feedback.md` | 44 | 25 | 19 (FBA-*) | 0 |
| `…/PRD-BOOK-2-01-verified-ratings/dev-workflows/BOOK-2-01-feedback.md`, non-`/scan` | 78 | 13 | 64 (FBB-*, grouped into 45 entries) | 1 |
| `/scan` entries: `dev-workflows-feedback/2026-10-16.md` (5) and BOOK-2-01 (5) | 10 | 7 | 3 (SEC-G4, SEC-G5, SEC-G6) | 0 |
| **Total** | **132** | **45** | **86** | **1** |

Each still-present entry names its feedback `id` and file under *Source*. A fixed one is not logged.

# Defects, by area

## security-workflows

### SEC-B1 — MAJOR — after `REGISTER_MOVED`, a re-plan rebinds the person's `id:<n>` decisions to a different finding
- **Where:** `plugins/security-workflows/commands/scan.md:342`, `:392`; `plugins/security-workflows/scripts/register.py:1077-1090` (`resolve`), `:1062-1072` (`allocate`, `matches[].id`), `:1131-1132`
- **What is wrong:** The decisions file names every existing finding by its number: "a match or an existing finding by `id:<n>`, the number the plan shows" (scan.md:342), and `matches[].id` is "the `[SEC#n]` chosen". `commit` resolves `id:<n>` through whatever plan it is handed (`by_num = _plan_origins(p)`). On `REGISTER_MOVED`, scan.md:392 says "re-plan with the same arguments and commit again, asking nothing already answered". But the records that moved the register can renumber existing findings (§2's give-way and collision rules: a record from another clone that sorts earlier and published the same number takes it, and the local finding moves). The new plan's `origins` then maps the same `<n>` to a different origin, and the unchanged decisions file applies the person's answer to that other finding. The register's own invariant is "a renumbering cannot point a record's decisions at another finding" (`.claude/rules/security-workflows.md`, *A finding is named by its origin*); the run's own decisions file breaks it on exactly the path built for a moving register.
- **Failure scenario:** Clone B records finding `bb` (CWE-79, `src/b.py`) as `[SEC#1]` at 08:00; clone A records finding `aa` (CWE-89, `src/a.py`) as `[SEC#1]` at 09:00, both seq 1. A `--triage` run on clone A shows `[SEC#1]` = `aa`, and the Security Engineer marks it a false positive (`id:1`). Before 7.2, B's record reaches A's checkout (another session's pull or `commit-artifacts` fast-forward on the shared checkout). `commit` stops `REGISTER_MOVED`; the run re-plans; `[SEC#1]` is now `bb` and `aa` moved to `[SEC#2]`; the commit records `bb` as a false positive and leaves `aa` open. Reproduced: `probe2.py` prints `plan seen by person: {'1': 'sA:v3:aa'}`, `re-plan origins: {'1': 'sB:v3:bb', '2': 'sA:v3:aa'}`, final state `1 sB:v3:bb CWE-79 src/b.py false-positive` / `2 sA:v3:aa CWE-89 src/a.py open`. A *Confirm fixed*, *Accept the risk* or a possibly-same `Same as [SEC#n]` answer misroutes the same way.
- **Evidence:** probe above; `resolve` reads only the plan given; scan.md:392 tells the run to reuse the decisions file unchanged. 7.1's re-plan is safe (reserved records feed numbering only, never `origins`), so the defect is specific to `REGISTER_MOVED`.
- **Suggested fix:** Make the decisions file name an existing finding by its origin (the plan's `origins[n]`), e.g. `"target": "origin:<origin>"`, and `matches[].origin`; or have `commit` take the plan the person answered (`--seen-plan`) and translate `id:<n>` through it; at minimum, on `REGISTER_MOVED` compare the old and new plans' `origins` and re-ask every row whose number now names another origin. Add a selftest for the shape above.
- **Source:** review
- **Confidence:** high

### SEC-B2 — MINOR — `register.py commit` takes any status from the decisions file, so "closed only on evidence" is enforced by prose alone
- **Where:** `plugins/security-workflows/scripts/register.py:1091-1103` (`resolve`), `:1162-1167`; `plugins/workflows-core/references/security-register-format.md:11`, `:116`; `scan.md:346` ("each decision's target, status, evidence and date are `commit`'s to check")
- **What is wrong:** `resolve` checks only that a status is one of `STATUSES`, that a false positive's evidence matches `\S+:\d+`, and that an accepted risk has a reason and a date. It accepts `fixed` on a finding the plan neither closes nor proposes (no `closable`/`gone` entry), on a change scan, and in a `dev` run for a `via: moved` row; and it accepts `fixing` with no follow-up link, or `reopened` by hand. The format reference says `register.py` "implements this file" and §5 rule 2 says a finding is "never closed on absence alone, and never by a change scan"; scan.md:346 says those checks are `commit`'s.
- **Failure scenario:** A run that writes a decisions file wrongly (a mis-mapped row, a free-text answer written through) records `fixed` on an open finding after a change scan, with no `fixed_in_scan`; `register.md` lists it under *Fixed* as "confirmed in triage". Probe: a change-scan plan plus `{"target":"plugin:v3:aa","status":"fixed"}` commits, and a later triage `{"target":"id:1","status":"fixing"}` commits with `links: {}`.
- **Evidence:** `probe.py` case "fixed/fixing by hand" → `('fixing', {})`; code at the lines above.
- **Suggested fix:** In `commit`, refuse with `TRIAGE_INVALID` a `fixed` decision whose target is not in the plan's `closable`/`gone` (and, for `role dev`, one marked `via: moved`), and any user decision of `fixing`, `reopened` or `new`; or narrow scan.md:346's claim to what `commit` actually checks.
- **Source:** review
- **Confidence:** medium (reachable only through a defective decisions file; the command's mapping never writes these)

### SEC-B3 — MINOR — an empty `--by` is accepted, so an accepted risk can be recorded with no owner
- **Where:** `plugins/security-workflows/commands/scan.md:380` (`--by "$(git -C "$SPECS_PATH" config user.name)"`), `:546`; `plugins/security-workflows/scripts/register.py:1118-1165`
- **What is wrong:** Where the specs repository has no `user.name` (git can still commit with an auto-detected identity), `--by ""` is passed. `commit` never checks it, sets `owner = by` on every accepted risk and `by` on every history entry. The format says an accepted risk has "`owner` and `review_by` (`YYYY-MM-DD`) are set" (§4) and D9 "The owner of an accepted risk is the person deciding".
- **Failure scenario:** A Dev on a fresh container accepts a risk: the register records `owner: ''`, `register.md`'s *Risk register* and *Awaiting security review* show an empty *Owner* / *Decided by*.
- **Evidence:** `probe.py` case "empty --by" → `('accepted-risk', "''", '2020-01-01')` (it also shows a review-by date in the past is accepted, which is defensible as a typed date).
- **Suggested fix:** `commit` refuses an empty or whitespace `--by` with `REGISTER_BAD_ARGS`; scan.md reads `user.name` at Phase 0 and asks for a name (or stops) where it is unset.
- **Source:** review
- **Confidence:** medium

### SEC-B4 — MINOR — Phase 3 looks for the report only at the scan root, while Claude Security creates it with a cwd-relative `mkdir`
- **Where:** `plugins/security-workflows/commands/scan.md:231` ("the scan root is `<repo root>`"), `:252` ("the newest `CLAUDE-SECURITY-2*` folder at the scan root"); Claude Security 0.12.0 `skills/claude-security/jobs/scan-changes.md:91` and `scan-codebase.md:69` (`mkdir -p CLAUDE-SECURITY-<UTC YYYYMMDD-HHMMSS>/.claude-security-run`, "in the repository")
- **What is wrong:** Phase 0 step 5 takes `<repo root>` as `git rev-parse --show-toplevel`, and Phase 3 step 3 searches only there. Claude Security's recipes make the report directory with a relative path. Where the session is open in a subdirectory of the repository (a monorepo package), the change job's report can land in that subdirectory, and the run stops with `SECURITY_NO_REPORT` and "nothing is recorded" after a paid scan; the user is not told where the report went.
- **Failure scenario:** Session cwd `/work/mono/web`; `/security-workflows:scan ACME-7-01` scans; the report is `/work/mono/web/CLAUDE-SECURITY-…`; Phase 3 looks in `/work/mono/` → `SECURITY_NO_REPORT`.
- **Evidence:** text of both recipes; scan.md never names the cwd as a place to look. Not reproduced live.
- **Suggested fix:** Search the scan root and the session's working directory (newest qualifying folder in either, still gated on `<scan start>` and the stamp's commit), or name the report directory in the skill's args.
- **Source:** review
- **Confidence:** low — a live change scan from a subdirectory would confirm. (The same question for `--verify-fixes`, whose scan root `$wt` is not the cwd, is apparently answered by the spike's item 8 and Task 12's route 4, which ran; not reported.)

### SEC-B5 — NIT — the roles page understates which unwritten fixes are offered again
- **Where:** `plugins/security-workflows/docs/roles-and-phases.md:26`
- **What is wrong:** "each finding marked fix whose follow-up was never written … unless the scan closes it by itself". `register.py plan` (register.py:976-985) and scan.md (`pending_fix`, "save a finding the scan closes or proposes fixed") also leave out a finding the scan only *proposes* fixed; `docs/commands/scan.md:110` says so correctly ("the scan neither closing it nor proposing it fixed").
- **Failure scenario:** A Security Engineer reading the roles page expects a to-fix row for a finding the scan proposed closed, and gets a *Confirm fixed* row instead.
- **Evidence:** lines quoted.
- **Suggested fix:** "unless the scan closes it or proposes it fixed".
- **Source:** review
- **Confidence:** high

## workflows-core — git, handoff, resume pointer

### GIT-B1 — MAJOR — `branch-merged`'s squash test misses a squash merge when the default branch changed lines near the branch's hunks
- **Where:** `plugins/workflows-core/references/specs-repo-git.md:446` (test 3). Its consumers are `specs-repo-git.md:436` (B2), `:437` (B3), `:414` (§3.4 retry), `phase-handoff.md:59-61` (§2.2 rule 3) and `session-hygiene.md:98-102` (§1's merged check).
- **What is wrong:** the squash test is "the patch id of the branch's whole change, … `git diff --no-renames <base> <ref> | git patch-id --stable`, is the first field of a line of `git log -p --no-renames --no-merges <base>..<default-ref> | git patch-id --stable`". A patch id hashes the hunks' context lines. So when any commit that lands on the default branch after the fork changes a line within three lines of one of the branch's hunks, the squash commit's diff carries different context. Its patch id then differs, and the test reads **unmerged**. Ancestry fails and `cherry` prints `+`, so all three tests read unmerged, for good. No text records this limit (`docs/maintainers/rationale.md:421` states only the design).
- **Failure scenario:** a `prd/K-1-x` pull request is squash-merged with *delete branch on merge*. Between the fork and the squash, another merged pull request changed a nearby line of a file the branch touched. Plausible cases are `/conformance` ticking a `follow-ups.md` line near the end where the branch appended, or an annotation in `prd.md` next to the branch's edit. The next run keyed K-1 on that branch then gets B3 rather than B2, and stays on a merged branch, which is never cleaned up. Its handoff reuses the branch (§2.2 rule 3 sees "not merged"). §2.5's `git push -u origin <branch>` then recreates the branch the host deleted (§4 step 5's deleted-branch guard applies only to session commits). `gh pr list --state open` finds nothing, so `gh pr create` opens a second pull request whose head carries the already-squashed commits. `session-hygiene` §1 also carries that branch's merge item indefinitely.
- **Evidence:** `work/sq/`: base `seq 1 30`. The branch changes line 10; main changes line 12; then `git merge --squash` and commit on main. Results: ancestry exit 1, `cherry` `+ 2538a11…`, branch patch id `4996884…`, and neither commit on main has that id. In the control, main changes line 25 instead, and the squash commit's patch id equals the branch's (`4996884…`), so the test passes.
- **Suggested fix:** replace or supplement test 3 with a content test that context drift cannot defeat. "Merging `<ref>` into `<default-ref>` changes nothing" works: `git merge-tree --write-tree <default-ref> <ref>` exits 0 and prints `<default-ref>^{tree}`. §8 already requires a `merge-tree` that supports `--write-tree`. Gate it on a non-empty branch change, as the current test does. Record the limit in the meantime.
- **Source:** review
- **Confidence:** high on the git behaviour; medium on how often the state is reached.

### GIT-B2 — MINOR — §3.4's flush commits leftovers onto a merged plugin branch before §3.5 can see it merged, and strands them
- **Where:** `specs-repo-git.md:375-384` (stage 2 runs first and commits "onto the current branch"), `:436` (B2 asks `branch-merged HEAD` afterwards), `:448`, `:739-757` (deleted-branch push refusal), `:409-418` (the retry skips it silently).
- **What is wrong:** stage 2 flushes dirty session files from an interrupted earlier run onto HEAD before stage 3 classifies HEAD. Suppose HEAD is a plugin branch whose pull request has merged and whose remote was deleted on merge. The new commit makes all three `branch-merged` tests read unmerged ("a commit made on it after its pull request merged makes it read unmerged again", `:448`), so B2's cleanup never fires. The flush's push then meets "the remote deleted the branch" and pushes nothing. The run then goes to B3 (it stays on a dead branch, and the handoff recreates it, as in GIT-B1) or to B4 (it switches away). After that, §3.4's retry of other branches fails step 5's deleted-branch condition and prints nothing. The session files are therefore committed on a local branch no run will ever push. B4's report even says "a later run's preflight retries them wherever §4 step 5 lets it", which it never will.
- **Failure scenario:** a session is killed after its run wrote cost or feedback but before `commit-artifacts`. The operator merges that run's `prd/` pull request on the host (delete-on-merge). The next run starts on the same checkout. Its cost and feedback commit lands on the dead branch and never reaches the maintainer.
- **Evidence:** `work/fl/`: bare origin, `prd/K-1-x` pushed with `-u`, then merged `--no-ff` on the server and deleted, then `fetch --prune`. Before the flush, `merge-base --is-ancestor HEAD origin/main` succeeds (B2 would fire). After a flush commit of `dev-workflows/cost-b.md` it fails, `cherry` prints `+`, the upstream is still `refs/remotes/origin/prd/K-1-x`, and `ls-remote --exit-code` exits 2.
- **Suggested fix:** in §3.4, where HEAD is a plugin branch, ask `branch-merged HEAD` before flushing. Where it is merged, run B2's switch first and carry the dirty session files across (they are new files, so the switch carries them), then flush on the default branch. Alternatively, have B4's and §6's deleted-branch lines name the remedy (cherry-pick the session commits onto the default branch).
- **Source:** review
- **Confidence:** high on the mechanics; medium on frequency.

### GIT-B3 — MINOR — `<merge-clause>`'s table has no row for §4.1's *Commit failed*, while it claims to resolve every outcome row
- **Where:** `plugins/workflows-core/references/next-phase-offer.md:112-124`; `phase-handoff.md:447`.
- **What is wrong:** §4.1 gained `| Commit failed | Phase handoff: NOT handed off — the commit failed (…). The deliverable is staged on <branch>, not committed.` in `9c8f3e8b` (2026-10-05). The resolution table still lists eight outcomes with no *Commit failed* row, and says "**The table resolves every one of §4.1's eight outcome rows, and the catch-all is for a line that could not be read at all** — never for an outcome §4.1 defines". §4.1 now has nine non-append outcome rows. Its two newer appends (*Declaration unaccounted for*, *Record unreadable*) are also missing from the "are appends" sentence. A run that hit a commit failure therefore takes the catch-all, `(once this phase's artifacts are on the default branch)`, which never names the branch the deliverable is staged on. That breaks the paragraph's own rule that a row which leaves something on a branch names it.
- **Failure scenario:** a `pre-commit` hook in the specs repo rejects `/specify`'s deliverable commit. The `### Next step` offer of `/dev-workflows:design` then carries the vague catch-all clause rather than "commit what is staged on `<branch>`, push it and merge it".
- **Evidence:** `git log -S'| Commit failed | `Phase handoff:'` returns `9c8f3e8b`. `grep -n "Commit failed" next-phase-offer.md` finds nothing.
- **Suggested fix:** add a row, for example `Commit failed | (once the deliverable staged on <branch> is committed, pushed and its pull request merged)`. Change "eight" to the derived count, or say "every outcome row", and name all four appends.
- **Source:** review
- **Confidence:** high

### GIT-B4 — MINOR — epic-picker's cap: the worked example and the "four or fewer" rule disagree, and the rule overlaps `/specify`'s cap
- **Where:** `plugins/workflows-core/references/epic-picker.md:68-74` (example), `:80` ("Four or fewer Epics need none of this: the array carries them all"), `:86`, `:89`.
- **What is wrong:** the example lists **four** Epics (02, 03, 05, 01) and still uses three Epic rows plus "Another Epic from the list above…". The rule two lines later says four or fewer need no remainder option. The rule is also unconditional, but `/specify` always appends an option: it "carries at most **two** Epic rows plus that option plus the remainder option". Under the first rule, three Epics means all three plus `/specify`'s option (four options); under the second, it means two plus the option plus the remainder. A run copying the example adds a needless free-text step on an ordinary four-Epic PRD.
- **Failure scenario:** `/implement` on a PRD with exactly four Epics follows the example and shows a remainder option, so the fourth Epic needs a typed key. `/specify` with three Epics can render either array.
- **Evidence:** lines read as quoted above.
- **Suggested fix:** make the example five Epics. Say "where the Epics and the command's own option fit in four, the array carries them all; otherwise the cap applies (…)".
- **Source:** review
- **Confidence:** high

### GIT-B5 — NIT — phase-handoff §3.6 misquotes the offline note it says it reuses
- **Where:** `phase-handoff.md:319` versus `specs-repo-git.md:309-310`.
- **What is wrong:** §3.6 says "the precedent `specs-repo-git.md` §3.2 already sets: `offline — checked against the last-fetched ref`". §3.2's note is `offline — ancestry checked against the last-fetched ref`. One run can print two wordings for one degraded state.
- **Suggested fix:** quote §3.2 exactly, or say the wording differs on purpose.
- **Source:** review
- **Confidence:** high

### GIT-B6 — NIT — followup-emission says it mirrors nothing, then says twice to mirror another plugin's command
- **Where:** `followup-emission.md:11-14` ("**Self-contained, and no longer mirroring anything.** … no dependency — runtime or editorial — on any other plugin") against `:77` ("mirrors `/wiki-tasks-extract` Step 5") and `:111` ("Mirror `/wiki-tasks-extract`: NO mid-run interruption").
- **What is wrong:** two live claims contradict each other. `/wiki-tasks-extract` ships in `obsidian-llm-wiki`, which is not a dependency of any family plugin, so the "mirror" pointers send a reader to a file a run cannot load.
- **Suggested fix:** drop the two "mirror" pointers. The rules they point at are already stated in place.
- **Confidence:** high

### GIT-B7 — NIT — read-only-repos' own consumer list is short of its rules file
- **Where:** `read-only-repos.md:5` names `code-scanner`, `diff-summarizer`, `docs-grounder`, `code-grounder` and `grounding-verifier`. `.claude/rules/workflows-core-read-only.md` also names `docs-auditor`, `conformance-tracer`, `/implement`, `/security-workflows:scan` and others, and `grep -l read-only-repos plugins/*/agents/*.md` returns `docs-auditor.md` and `conformance-tracer.md` as well.
- **Suggested fix:** replace the list with the re-derive recipe, or add the two agents.
- **Confidence:** high

## workflows-core — routing, cost, feedback, loader, family commands, instruction tiers

### CORE-B1 — MAJOR — the cost path resolves "the current session" as the newest transcript, which is another session's whenever two share a working directory
- **Where:** `plugins/workflows-core/references/cost-emission.md:63-64`, `plugins/workflows-core/references/run-flags.md:102` (the `skip-cost` copy)
- **What is wrong:** "**Main transcript** — the newest `*.jsonl` directly under `~/.claude/projects/<cwd-slug>/`. Its basename minus `.jsonl` is `session_id`." Nothing checks that the newest file is this run's own session. The sibling reference already knows this is wrong: `session-diagnosis.md:22` says the current session is "the newest `*.jsonl` there **whose last records hold this run's own invocation** … the newest file alone is not enough, since another session may be running in the same directory."
- **Failure scenario:** two Claude Code sessions are open in the same cwd. That is a supported state: `CLAUDE.md` § Git says "This checkout can be shared by more than one agent session at once". Session A runs `/specify` while session B wrote its transcript last. A's `emit-cost` reads B's transcript from B's checkpoint (`cost-state/<B>.json`), files B's spend under A's `/specify` labels in `cost/<B-sid8>.md`, and advances B's checkpoint. B's next command then loses that window. Under `--skip-costs`, `skip-cost` advances the wrong session's checkpoint and drops the wrong session's deferred file (`deferred-<B>.json`).
- **Evidence:** read both §1 copies and `session-diagnosis.md:22`. Neither cost copy adds the own-invocation test.
- **Suggested fix:** adopt session-diagnosis's rule in both copies: take the newest `*.jsonl` whose tail holds this run's own command invocation, and fall back to report-only when none does. Or pass the session id where the harness exposes one.
- **Source:** review
- **Confidence:** high (text); medium on how often it is reached

### CORE-B2 — MAJOR — `<cwd-slug>` replaces only `/` and `.`, but Claude Code replaces every non-alphanumeric character
- **Where:** `plugins/workflows-core/references/cost-emission.md:61-62`, `plugins/workflows-core/references/run-flags.md:101`, `plugins/workflows-core/references/session-diagnosis.md:22`
- **What is wrong:** "`<cwd-slug>` — the absolute `cwd` with every `/` and `.` replaced by `-`".
- **Failure scenario:** with a cwd containing `_`, a space or `@`, such as `/workspace/my_service`, the rule yields `-workspace-my_service`. Claude Code stores that session under `-workspace-my-service`. The cost phase finds no transcript, so `session-cost.py` exits on `--transcript is not a readable file`, no cost entry is written, and the checkpoint never advances. `skip-cost` and `/diagnose-session` miss the same way.
- **Evidence:** on this machine, `ls ~/.claude/projects` shows `-tmp-remember-summarizer-cwd--4hpx-zz`, `…-cwd-6gxlt3i-` and `…-cwd-91wrl5s-`. These are `mkdtemp` directories, whose random suffix is drawn from `[a-z0-9_]`, so their `_` was written as `-`. The dirs held no transcripts to read a `cwd` field from, so the mapping is inferred rather than read.
- **Suggested fix:** state the rule as "every character outside `[A-Za-z0-9]` replaced by `-`", or locate the directory by the `cwd` field in its transcripts.
- **Source:** review
- **Confidence:** medium-high

### CORE-B3 — MINOR — the model-onboarding checklist names two files; a new generation touches more, and a Haiku one touches neither the way it says
- **Where:** `plugins/workflows-core/references/cost-emission.md:724-748` (§12)
- **What is wrong:** "A new model generation … touches **two** files that must change together": `classification.md` §2 and `cost-prices.yaml`. Chain-head ids are also written literally in three other places:
  - `run-flags.md:58`, the unpriced check for a family-only harness: "it prices that family's newest chain row (`claude-opus-5-5`, `claude-sonnet-5-5`, and `claude-haiku-5-5` …)";
  - `run-flags.md:41-42`, the Haiku rows: no `classification.md` chain names Haiku, so §12 step 1's "add the new model id to the correct fallback chain (Opus / Sonnet)" has no home for a new Haiku;
  - `classification.md`'s §4 example block, `.claude/rules/workflows-core.md`'s chain statement, and the chains printed in `plugins/dev-workflows/docs/reference/model-routing.md:41-49` and `plugins/product-workflows/docs/reference/model-routing.md:45-53`.

  The workflows-core CHANGELOG entry that added Sonnet 5.5 (`CHANGELOG.md:812`) moved "41 literal chain-head references". The sentence at `:739-742` is also garbled: "so for such an id (2) is not optional so it still lists every model actually in the chain".
- **Failure scenario:** a maintainer follows §12 for Opus 5.6. `run-flags` §2's family-only price check then still prices `opus` against `claude-opus-5-5`. A new Haiku has no rule to land in at all. The docs chains go stale.
- **Evidence:** read §12; ran `grep -rn "claude-opus-5-5" plugins/*/references plugins/*/docs`.
- **Suggested fix:** list every site, or a recipe (`grep -rn '<old head id>' plugins/ .claude/rules`). Add the Haiku-rows step. Rewrite the garbled sentence.
- **Source:** review
- **Confidence:** high

### CORE-B4 — MINOR — §6.1 cites "§8 tier 5", which does not exist
- **Where:** `plugins/workflows-core/references/cost-emission.md:346`
- **What is wrong:** "in every persistence tier, including report-only (§8 tier 5)". §8 has tiers 1–4, and report-only is tier 4 (`:592`). The two other references to it say "as in tier 4" (`:559`, `:567`).
- **Failure scenario:** an agent looking for tier 5 finds nothing. Low impact.
- **Suggested fix:** "(§8 tier 4)".
- **Source:** review
- **Confidence:** high

### CORE-B5 — MINOR — `/prompt-brainstorm` has no absent-companion path, though `dependencies.md` says the run probes for `superpowers` and falls back to an "embedded technique"
- **Where:** `plugins/workflows-core/references/dependencies.md:21-23`; `plugins/workflows-core/commands/prompt-brainstorm.md:45` (Phase 2 Resolution), `:95-99` (Phase 3)
- **What is wrong:** `dependencies.md` defines an optional companion as "convention + runtime-resolve + graceful fallback: nothing declares it, the run probes for it, and a miss degrades exactly one feature", and its row for `superpowers` (skill `brainstorming`) says the fallback when absent is "Embedded technique; no hard dependency." `/prompt-brainstorm` does no probing. It writes the feedback entry's Resolution as the literal `Handed off to superpowers:brainstorming to redesign the correction.` in Phase 2, commits it, writes the deferred cost record, and only then, in Phase 3, "invokes the skill if present". No embedded brainstorming technique exists anywhere in the family. Only `/prompt-grill-me` has one (`grilling-technique.md`).
- **Failure scenario:** a user without `superpowers` installed runs `/workflows-core:prompt-brainstorm "…"`. A committed, pushed feedback entry then says the correction was handed off to brainstorming, which never happened. The Phase 3 hand-off has no defined behaviour, so the run ends with nothing explored, or the agent improvises. The reference's promised fallback does not exist.
- **Evidence:** read both files end to end. `grep -n -i brainstorm references/dependencies.md` returns only line 23. `prompt-brainstorm.md` has no `absent`/`not installed` branch.
- **Suggested fix:** either (a) probe for the skill in Phase 1 or 2. When it is absent, say so and fall back to `/prompt-grill-me`'s inline grill, or to `/prompt`'s direct fix, and write the Resolution to match. Or (b) correct the `dependencies.md` row to "none — `/prompt-brainstorm` ends after logging; use `/prompt-grill-me` instead" and have Phase 3 say that.
- **Source:** review
- **Confidence:** high

### CORE-B6 — MINOR — `followup-emission` §7's `select` option needs text from the user but is not labelled `(you'll be prompted …)`, against `escalation-rules` §0
- **Where:** `plugins/workflows-core/references/followup-emission.md:115-118`; restated by `plugins/dev-workflows/commands/implement.md:1330`, `ready.md:670`, `plugins/docs-workflows/commands/document.md:1424`, `:1888`, `release-notes.md:696`, `plugins/product-workflows/commands/epics.md:1070`
- **What is wrong:** `choices: ["approve-all", "select", "cancel"]`, then "**select** → let the user pick a subset by row number". §0 (*A selection carries no text*) requires any option that needs text from the operator to be "labelled `… (you'll be prompted)` or `… (you'll be prompted for <what>)` … and choosing it is followed at once by one plain-text question". The `select` label carries no marker. The rule's mechanism, one plain-text question for the row numbers, is never stated.
- **Failure scenario:** in every one of the twelve follow-up callers, a user picks `select`. Nothing tells the run to ask the follow-up question in plain text. The agent may read the bare selection as the subset, ask with a second picker that cannot hold arbitrary row lists, or improvise. This is the inconsistency the §0 rule exists to remove. The commands must present the array verbatim (*Choice lists are presented verbatim*), so they cannot fix the label locally.
- **Evidence:** read `followup-emission.md` §7 and `escalation-rules.md:44-53`. `grep -rn approve-all` across `plugins/` shows the six command sites that cite §7. Check 12 does not flag it because `select` does not open with any of the asking verbs its `ASKS` list matches.
- **Suggested fix:** relabel the option `"Select some (you'll be prompted for the row numbers)"`, and say the run then asks one plain-text question. Update the six `(approve-all | select | cancel)` restatements to match.
- **Source:** review
- **Confidence:** high

### CORE-B7 — MINOR — the feedback ladder's tier 1 matches the PRD folder only by the legacy unprefixed name `<KEY>{-|_}<slug>`
- **Where:** `plugins/workflows-core/references/feedback-emission.md:114-116`. The same text is in `plugins/workflows-core/references/cost-emission.md:561-563`, which is outside this sub-slice: flag it to whoever owns cost-emission.
- **What is wrong:** tier 1 is "the dir matched by `$SPECS_PATH/{specs|specifications|vis}/…/<KEY>{-|_}<slug>/…` → `<PRD-dir>/dev-workflows/<KEY>-feedback.md`". Since the kind prefixes landed, every folder the family creates is `<KIND>-<KEY>-<slug>` (`addressing.md:190-193`), and `<KEY>{-|_}<slug>` is §5's *legacy-layout* fallback form (`addressing.md:637-643`). Read literally, `PRD-BOOK-1-back-in-stock-alerts/` does not match `…/<KEY>{-|_}<slug>/`, so tier 1 never fires for a prefixed folder and the entry falls to tier 2's "unfiled" bucket. The reference does not say to resolve the folder through `resolve-address`, which is the one resolver `CLAUDE.md` § Hard constraints mandates.
- **Failure scenario:** an agent following tier 1 as written on a current specs tree finds no PRD dir and writes `$SPECS_PATH/dev-workflows-feedback/<KEY>.md` with the notice "unfiled — move under the PRD dir". Cost does the same and lands in the pending file, where §9's reconciliation is then needed. The demo specs repo (`/home/ihudak/dev/demo/bookstore-specs`) shows that live runs so far interpreted the glob loosely and filed entries under `PRD-`/`BRD-` folders correctly. That is why the severity is MINOR: the text is false, and an agent obeys it at the agent's discretion.
- **Evidence:** read `feedback-emission.md` §2 and `addressing.md` §2 and §5. `grep -n 'KEY>{-|_}'` across `references/` shows that only feedback-emission, cost-emission and addressing §5 (legacy) carry this form.
- **Suggested fix:** state tier 1 as "the folder `resolve-address <KEY>` (`workflows-core:addressing` §3) returns `found` — prefixed, or the §5 legacy fallback". Make the same edit in cost-emission §8.
- **Source:** review
- **Confidence:** medium

### CORE-B8 — MINOR — the feedback entry `id` has no defined key segment for a keyless run
- **Where:** `plugins/workflows-core/references/feedback-emission.md:83-84` (`id` rule). Dedupe relies on it at `:144-147`.
- **What is wrong:** "`id` — stable: `<KEY>-<command>-<short-slug>` (drop the leading `/` from the command; use `manual` / `prompt` when `command` is `n/a`)". There is no rule for `<KEY>` when `key` is `null`. Keyless runs are routine: `/feedback`, `/prompt*`, `/diagnose-session`, `/security-workflows:scan <repo-path>`, `/docs-*` and `/document` direct mode all reach tier 2 or tier 3. §1 defines only the file-level `prd: n/a`. §3's auto-entry dedupe is "skip any [id] that already exist", so it works only if every run invents the same placeholder.
- **Failure scenario:** the demo specs repo's `dev-workflows-feedback/2026-10-16.md` carries `id: NOKEY-scan-verify-scope-ignores-later-test`. Nothing in the reference says `NOKEY`. Another run could write `n/a-scan-…`, `null-scan-…` or `scan-…`, and the same signal is then logged twice, which is the duplication §1.1 says a stable id exists to prevent.
- **Evidence:** read `feedback-emission.md` §1 and §3. Inspected the demo repo read-only (`head -30 dev-workflows-feedback/2026-10-16.md`).
- **Suggested fix:** add "`<KEY>` is the run's key, or `NOKEY` where none resolved" (the form already in use) to the `id` bullet.
- **Source:** review
- **Confidence:** medium

### CORE-B9 — NIT — "the twenty-eight commands that measure themselves (§1)" points at a section that does not list them
- **Where:** `plugins/workflows-core/references/cost-emission.md:649`, `:853`
- **What is wrong:** §1 is session-artifact resolution. The set of 28 is stated in the preamble (`:3-9`) and §7, so "(§1)" is a stale pointer.
- **Suggested fix:** cite §7 or the preamble.
- **Source:** review
- **Confidence:** high

### CORE-B10 — NIT — a stale "pending check" sits beside the live measurement that settles it
- **Where:** `plugins/workflows-core/references/cost-emission.md:264-266`
- **What is wrong:** "Pending a one-line implementation check that `.cost.total_cost_usd` is present on the statusline stdin … if absent, B is simply unavailable". The same section's compaction caveat (`:261-263`) reports a live `/specify` window whose B figure differed from A by $3.23, so B demonstrably works. This is a claim with an expiry date (`CLAUDE.md` § Editing discipline).
- **Suggested fix:** drop the bullet, or restate it as "where a Claude Code version omits the field, B is unavailable".
- **Source:** review
- **Confidence:** medium

### CORE-B11 — NIT — two comments in `cost-prices.yaml` are behind the page they cite
- **Where:** `plugins/workflows-core/references/cost-prices.yaml:12`, `:63-66`
- **What is wrong:**
  - `:12` says "the page does not say which tokens count". The pricing page now says: "A request's prompt length counts all of its input tokens, including cache reads and cache writes". The engine's reading matches it, so only the comment is wrong.
  - The multiplier summary at `:63-66` names Opus 5.5, Sonnet 5.5 and Fable 5.1 as the exceptions and omits Mythos 5.1, which is keyed at 0.025x (`:173-177`). `cost-emission.md` §4 (`:213-214`) names Mythos 5.1.
- **Suggested fix:** update both comments.
- **Source:** review (live pricing page fetched 2026-10-26)
- **Confidence:** high

### CORE-B12 — NIT — `classification.md` §4's "Both agents this parenthetical names" names no agents
- **Where:** `plugins/workflows-core/references/model-routing/classification.md:249-253`
- **What is wrong:** the parenthetical is "(NVD lookup, detect, compatibility checks)": three steps, no agents. "Both agents" means `vuln-research` and `upgrade-planner`, which are named only later in the bullet. This is a pointer-face defect.
- **Suggested fix:** name the two agents in the parenthetical.
- **Source:** review
- **Confidence:** high

### CORE-B13 — NIT — `handoff/code-scanner.md` gives `REPO_MISSING` a narrower meaning than the agent returns it for
- **Where:** `plugins/workflows-core/references/handoff/code-scanner.md:68`; contrast `plugins/workflows-core/agents/code-scanner.md:36-41` and `plugins/workflows-core/references/escalation-rules.md` § *Repo missing (after resolution)*
- **What is wrong:** the handoff's status table says `REPO_MISSING` means "`repo_path` does not exist". The agent also returns it when the clone's `origin` slug does not match `repo_url_slug` ("On mismatch, return `status: REPO_MISSING` with a note naming both slugs"), and escalation-rules relies on that second case: "*Specify a different absolute path for this repo* is the option that resolves the second case". A caller that reads only the handoff, as `/docs-audit` does ("`workflows-core:handoff/code-scanner` fixes six"), reports an existing directory as missing. The agent also runs the slug check (`git -C <repo_path> remote get-url origin`) before its Process step 1 checks that the directory exists, and does not say what happens when there is no `origin`.
- **Failure scenario:** a repo mounted under a fork name or a renamed origin returns `REPO_MISSING`. A handoff-driven caller tells the user the path does not exist when it does.
- **Evidence:** lines read as cited.
- **Suggested fix:** make the handoff row read "`repo_path` is not a directory, or its `origin` slug differs from `repo_url_slug`". In the agent, put the existence check before the slug check.
- **Source:** review
- **Confidence:** high

### CORE-B14 — NIT — `test-notify` misses the single-module Gradle form the family itself prescribes
- **Where:** `plugins/workflows-core/hooks/test-notify.sh` (the `grep -qE '(mvnw test|…)'` gate); `plugins/workflows-core/docs/reference/hooks.md` (`test-notify` paragraph)
- **What is wrong:** `cleanTest test` got its own entries "because `dev-workflows`' `test-baseliner` runs" it. `dev-workflows/references/fix-vuln/build-systems.md:57` and `references/upgrade/ecosystems.md:74` prescribe `./gradlew :<module>:test` for a single module, and that form contains neither `gradlew test` nor `gradle test`, so it never notifies. The hooks page lists the forms that do not match (`mvn clean test`, `npm run test` …) but not this one, which the family itself runs.
- **Failure scenario:** a `/vuln` or `/upgrade` run testing one Gradle module gives no test notification.
- **Evidence:** substring test read in the script. Grep of dev-workflows for `gradlew :<module>:test`.
- **Suggested fix:** add `gradlew :` and `gradle :` (with `:test`) alternations, or document the omission.
- **Source:** review
- **Confidence:** high

### CORE-B15 — NIT — the session-feedback page says the feedback ladder's second rung is "a pending location"
- **Where:** `plugins/workflows-core/docs/reference/session-feedback.md` § *Where files land* ("The resolution ladder is the same as cost's: a resolved folder in `$SPECS_PATH` first, a pending location where no folder resolves, and report-only where nothing does.")
- **What is wrong:** feedback's tier 2 is not a pending location. It is the docs-repo branch or the **unfiled** `$SPECS_PATH/dev-workflows-feedback/<KEY-or-date>.md` (`feedback-emission.md` §2). Only cost has a pending file (§9) that a later run reconciles, and cost also has a per-repository security branch that feedback lacks. "The same as cost's" is false on both counts.
- **Failure scenario:** a reader looks for a feedback pending file that never gets reconciled and does not find their entry, which sits in the unfiled directory.
- **Suggested fix:** "a resolved folder first; otherwise, for the docs commands, the docs repository's folder, and for everything else an unfiled file at the top of `$SPECS_PATH`; report-only where nothing resolves".
- **Source:** review
- **Confidence:** high

### CORE-B16 — NIT — the workflows-core README's documentation table omits the Grounding sources reference page
- **Where:** `plugins/workflows-core/README.md` (documentation table, "## Documentation") at 0e02e28b
- **What is wrong:** the table lists six `docs/reference/` pages (Agents, References, Environment, Hooks, Session cost, Session feedback); `plugins/workflows-core/docs/reference/` holds seven — `grounding.md` ("Grounding sources", linked from `docs/README.md:14` and `:33`) is missing from the README table.
- **Failure scenario:** a reader starting from the plugin README does not find the page that says what each authoring command grounds on and how to switch a source off.
- **Evidence:** `ls plugins/workflows-core/docs/reference` → agents, environment, grounding, hooks, references, session-cost, session-feedback; `grep -n grounding plugins/workflows-core/README.md` matches only the prose blurb, not the table.
- **Suggested fix:** add a `[Grounding sources](docs/reference/grounding.md)` row.
- **Source:** review
- **Confidence:** high

## scripts, gates and hooks

### SCR-B1 — MINOR — `test-notify` reads `tool_response.output`, which a Bash payload does not carry, so it never reports a count
- **Where:** `plugins/workflows-core/hooks/test-notify.sh:26` (`out = (d.get('tool_response') or {}).get('output', '') or d.get('output', '')`); docs `plugins/workflows-core/docs/reference/hooks.md:8`, `:22`
- **What is wrong:** Claude Code's Bash tool result is `{"stdout": …, "stderr": …, "interrupted": …}`. The `toolUseResult` records in this session's own transcript (`~/.claude/projects/…/38f385e9-….jsonl`) have that shape, with `stdout` as the first key, and the hook's `tool_response` is that object. Nothing in it is named `output`, so `$output` is always empty. The parser therefore matches nothing, and every test run notifies the literal `Test run: tests completed`. A red suite also notifies only "tests completed". The docs page says the hook "parses its pass/fail counts". The window's own gradle-sum fix (the comment at `:103-109`, "a red build could be notified as green") tunes a parser that never receives any input.
- **Failure scenario:** `pytest` reports `3 failed, 10 passed` → the notification says `Test run: tests completed`.
- **Evidence:** The hook was fed `{"tool_input":{"command":"pytest -q"},"tool_response":{"stdout":"=== 3 failed, 10 passed in 1.2s ===","stderr":""}}` with a stub `notify-send` and notified `Test run: tests completed`. The same payload with the key renamed to `output` notified `Test run: 10 passed, 3 failed`.
- **Suggested fix:** Read `tool_response.stdout` (plus `stderr`, since Gradle and Maven print summaries there) and keep `output` as a fallback. Add a fixture with the real payload shape.
- **Source:** review
- **Confidence:** high on the payload key (seen in transcripts). Medium that no Claude Code version sends `output`.

### SCR-B2 — MINOR — CLAUDE.md says check 13 enforces vendor neutrality for every text file under `plugins/`; it scans only `PLUGIN_RELS`, and two catalog plugins name trackers unmarked
- **Where:** `CLAUDE.md:131` ("no text file under `plugins/` … names a tracker unless … carries `<!-- vendor-token-ok … -->`; … check 13 enforces it"), against `scripts/check-docs.sh:52` (`PLUGIN_RELS` lacks `acli`, `prose-style` and `obsidian-llm-wiki`) and `.claude/rules/gates.md:81`/`:83` (scope: "every text file under any plugin in `PLUGIN_RELS`"; "the scope stops at the plugin and the repo-root instruction tiers")
- **What is wrong:** Two live statements of the same rule disagree, and CLAUDE.md's is false of the tree. `plugins/acli` has 120 unmarked lines naming the tracker, and `plugins/obsidian-llm-wiki` has 18 (e.g. `commands/wiki-task.md:3`, `skills/_shared/task-rules.md:103`). Check 13 passes because it never reads them.
- **Failure scenario:** An agent editing `acli` or `obsidian-llm-wiki` reads CLAUDE.md, takes the hard constraint as binding, and either "fixes" a plugin whose subject is a tracker CLI or treats a green check 13 as proof the rule holds there.
- **Evidence:** `grep -rniE '\bjira\b' plugins/acli --exclude=CHANGELOG.md | grep -v vendor-token-ok | wc -l` → 120; the same over `plugins/obsidian-llm-wiki` with the full `VENDOR_TOKENS` set (`check-docs.sh:1675`) → 18.
- **Suggested fix:** Narrow CLAUDE.md:131 to the gated scope, e.g. "no text file under a plugin in `check-docs.sh`'s `PLUGIN_RELS`…". Run the claim sweep (refinement 8) over the copies of the rule.
- **Source:** review
- **Confidence:** high

### SCR-B3 — MINOR — the `/implement` and `/document` preload hooks restate the key grammar, narrower than `addressing` §1, so some keyed runs get no specs context
- **Also found as:** IMP-B5, DEV-B6 (merged here)
- **Where:** `plugins/dev-workflows/hooks/preload-context.sh:129` and `plugins/docs-workflows/hooks/preload-context.sh:97` (`[A-Z][A-Z0-9]+-[0-9]+`), against `plugins/workflows-core/references/addressing.md:21` (`^[A-Z][A-Z0-9_]*(-\d+)+$`)
- **What is wrong:** The hook's copy needs at least two prefix characters, rejects `_`, and cannot see a whole folder name, which `read-key` accepts (`addressing` §1 reading 2). `addressing` §1 itself names a local restatement of the grammar as the defect family.
- **Failure scenario:** `/implement ACME_X-90`, `/implement A-1` or `/implement PRD-ACME-90-…` (a typed folder name) run without the `SPECS_PATH` context block that `/implement ACME-90` gets.
- **Evidence:** The dev hook was piped the four prompts: only `ACME-90` printed the "specs workflow" block (0, 0, 1, 0).
- **Suggested fix:** Use `^/(dev-workflows:)?implement[[:space:]]+[A-Z][A-Z0-9_]*-[0-9]` (and the same for `document`), or preload for any non-flag argument. A hook cannot load the reference, so add a comment citing `addressing` §1.
- **Source:** review (the line predates the window, 2026-09-06; the hooks were edited in the window)
- **Confidence:** high

### SCR-B4 — MINOR — the spec-ID census "tripwire" is run by no gate, and its own header records two drifts that went unnoticed
- **Where:** `scripts/spec-id-baseline.txt:1-77`; `.claude/rules/gates-id-grammar.md:15` ("`scripts/spec-id-baseline.txt` is its census tripwire"); `.github/workflows/validate-catalog.yml` (no step reads it)
- **What is wrong:** A tripwire only works if something trips it. The verify recipe is in the file's comment and nothing runs it. The header itself records the consequence: the drift of 2026-08-30 and 2026-09-22 was found only on 2026-09-23, and fe8ce332 (2026-10-13) "named the ids … without regenerating this file", found later by hand.
- **Failure scenario:** A global replace reaches the `[U01]`/`[AC01]`/`[TC01]` namespace and CI stays green.
- **Evidence:** No reference to `spec-id-baseline` under `.github/` or in any gate script (`grep -rn spec-id-baseline scripts/*.sh scripts/*.py .github` → nothing). The verify recipe prints nothing at HEAD (clean today).
- **Suggested fix:** Add a CI step running the file's verify recipe (it must print nothing), or a `--baseline` mode in `check-id-grammar.sh`. Alternatively, reword the rules line to say it is a manual check.
- **Source:** review
- **Confidence:** medium (whether "tripwire" was meant to promise CI enforcement is a reading; the drift history is fact)

## dev-workflows — /implement

### IMP-B1 — MINOR — Pre-Phase 3 step 3 hard-codes a branch name that contradicts steps 1–2 (convention discarded, key doubled)
- **Where:** `plugins/dev-workflows/commands/implement.md:713`, `:715`, `:717` (at 0e02e28b)
- **What is wrong:** Step 1 builds the name from the repository's documented convention, filling its segments, and only "when the repo documents no convention (§1.4) build `<prefix>/<slug>`". Step 2 then says "When `unit_key` is set and the chosen shape has no separate issue-key segment, prefix it: `<unit_key>-<slug>`." Step 3 then ignores both: "**Create and checkout** — `git checkout -b <prefix>/<unit_key>-<slug>` on a keyed run, `<prefix>/<slug>` in direct mode. If that name already exists, append the first 7 chars of HEAD's SHA: `<prefix>/<slug>-<short-sha>`."
- **Failure scenario:** (a) A repository whose CONTRIBUTING.md documents `<initials>/<KEY>-<desc>`: step 1 produces `ih/BOOK-1-01-add-x`, step 3, read literally, runs `git checkout -b <prefix>/<unit_key>-<slug>`, a shape with a prefix segment the convention does not have. (b) No convention: step 2 already makes the slug `BOOK-1-01-add-x`, and step 3's `<prefix>/<unit_key>-<slug>` yields `feat/BOOK-1-01-BOOK-1-01-add-x`. (c) On a name collision in keyed mode the fallback form `<prefix>/<slug>-<short-sha>` is written without `<unit_key>`, so the key a reader of the branch name looks for (the docs say the branch "carries" the key) is present only by the accident of step 2's prefixing. Three live instructions disagree about one name; an agent running them literally picks one.
- **Evidence:** read `:711–:717`; `docs/commands/implement.md` §What it produces says "named per the target repo's own documented convention, or `<prefix>/<key>-<slug>` as the fallback", which matches steps 1–2 and not step 3. Text last touched 2026-08-04 (`git log -L715,717`), so pre-window but still live.
- **Suggested fix:** Step 3: "`git checkout -b <the name steps 1–2 resolved>`; if it exists, append `-<first 7 chars of HEAD's SHA>` to that name." Drop the literal templates.
- **Source:** review
- **Confidence:** medium (an agent may well read through the contradiction; the text itself is contradictory)

### IMP-B2 — MINOR — Phase 4.7 appends an implementation record on a run that committed nothing, a block shape `implementation-format` §1 does not define
- **Where:** `plugins/dev-workflows/commands/implement.md:1192–1201`, `:1182`, `:32`; `plugins/workflows-core/references/implementation-format.md` §1 (`:15–:108`)
- **What is wrong:** Phase 4.7 is "Skipped entirely when `mode: direct`" — and nowhere else. Under `--no-commit` Phase 4.6 writes `code_repo_outcome` "its `commit` `null` and `pushed` `false`" (`:1182`), and on a §2.1 gate failure, a hook rejection or a secret-scan stop there is no commit either; Phase 4.7 still appends a block naming `repo`, `branch`, `base`, `commit` and `pushed` from that state. `implementation-format` §1 defines a block as recording "the one commit `/implement` Phase 4.6 made for the run" and says nothing about a block with no commit; "A record is present only where it holds a block" is what the Epic picker's ● marker, `/ready`'s inventory and `unit-branch` read.
- **Failure scenario:** `/dev-workflows:implement EPIC-BOOK-1-01 --no-commit` → the work stays in the working tree, yet `EPIC-BOOK-1-01/implementation.md` gains a block with `commit: null`. The next `/implement` on the PRD shows the Epic ● (greyed, "implement anyway"), `/ready` derives *In Progress* for it, `/conformance`/§5's merged test is asked about a null commit, and `/document`/`/release-notes` are handed a ref that does not exist — while line 32 tells the user only that "`/document` and `/release-notes` will not find it later".
- **Evidence:** grep of `implementation-format.md`, `diff-summarizer.md`, `conformance.md` for any null/absent-commit handling: none; Phase 4.7 has no `--no-commit` or uncommitted-outcome branch.
- **Suggested fix:** Either skip Phase 4.7 where `code_repo_outcome.commit` is null (and say so in the report), or define a commit-less block in `implementation-format` §1 and have every reader (picker marker, `/ready`, §5, §4's two-source read) treat it explicitly.
- **Source:** review
- **Confidence:** medium

### IMP-B3 — NIT — Phase 4.5's reason for the falling-back array lists the §3.4 rows naming `design.md` without `/conformance`
- **Where:** `plugins/dev-workflows/commands/implement.md:1142`; `plugins/workflows-core/references/phase-handoff.md` §3.4 table (`:273–:298`); `plugins/dev-workflows/commands/conformance.md:63`
- **What is wrong:** "Where the set is an annotated `design.md` **alone**, present §4.3's **gated — falling back** array … because the only §3.4 rows naming `design.md` are this command's own in-scope-only gate and `/dev-workflows:ready`'s coverage gap, neither of which stops". Since 2026-10-12 `/conformance` — the very next step `/implement`'s `### Next step` offers on an Epic — runs `require-on-main` on the Epic's `design.md` too (`conformance.md:63`), and `phase-handoff` §3.4's row-F table has no `/conformance` row at all. The conclusion still holds (`/conformance` falls back on `absent`: "An `absent` document falls back per §3.4"), so no wrong array is shown, but the stated reason is a stale exclusivity claim (claim-sweep refinement 3).
- **Failure scenario:** none behavioural today; a maintainer extending §3.4 or `/conformance`'s gate reasons from a false census.
- **Evidence:** lines read as quoted.
- **Suggested fix:** Reword as "no consumer of `design.md` stops on row F (§3.4)"; add `/conformance`'s row to `phase-handoff` §3.4 (CORE slice).
- **Source:** review
- **Confidence:** high (that the census is incomplete); low impact

### IMP-B4 — NIT — the `/implement` docs page's agent census omits `defect-reporter`
- **Where:** `plugins/dev-workflows/docs/commands/implement.md:46`
- **What is wrong:** "Eight named subagents are dispatched: … `workflows-core:impl-maintenance` (Phase 4). … `--enforce-model` overrides all eight." Under `--skip-feedback`, Phase 4 dispatches `workflows-core:defect-reporter` in Agent 4's place (`commands/implement.md:1059`), a ninth named subagent with its own model rule (`§2.1 Sonnet chain, or run_flags.enforced_model`). The page's synopsis paragraph names it, but the census and "all eight" do not.
- **Failure scenario:** a reader checking which agents `--enforce-model` reaches is told eight.
- **Evidence:** `implement.md:1059` vs docs `:46`.
- **Suggested fix:** "…and `workflows-core:impl-maintenance` (Phase 4) — `defect-reporter` in its place under `--skip-feedback`"; make the count follow.
- **Source:** review
- **Confidence:** high

## dev-workflows — /design, /ready, /conformance

### DEV-B1 — MAJOR — `/ready` asks its "dirty or non-main checkout" question on every run in session-branch mode, and its re-check can never pass
- **Where:** `plugins/dev-workflows/commands/ready.md:116-122`, `:757`; `plugins/dev-workflows/docs/commands/ready.md` ("A clean specs-repo checkout on `main`/`master`")
- **What is wrong:** Phase 0 step 3 runs a bare `git -C $SPECS_PATH status --porcelain` and treats any output as dirty: "Not on `main`/`master`, or the tree is dirty → warn … and ask: `choices: ["I've switched to a clean main — re-check", "Proceed anyway on the current checkout (read-only; noted in the report)", "Cancel"]`". In session-branch mode, `workflows-core:specs-repo-git` §8.3 deliberately keeps the session branch's version of every session file in the working tree "wherever it differs from HEAD". The preflight also "ends with `put-back` in the mode". So whenever the session branch holds a session file the default branch lacks, the default-branch checkout always shows those paths in `--porcelain`.
- **Failure scenario:** `workflows.sessionBranch=true` (or a recorded push refusal), with one earlier run's cost or feedback file on `session/<id>`. Every `/ready` run then warns that the checkout "may show unmerged, in-flight artifacts" and asks the question. *I've switched to a clean main — re-check* loops, because the overlay files come back. The operator can only take *Proceed anyway*, which marks the report as a non-main/dirty override. The same false prompt fires on every run after a declined handoff, since Phase 6a expects `_readiness.md` to be left as `??`/` M` (`ready.md:551-556`).
- **Evidence:** compared `ready.md:118-121` with `specs-repo-git.md` §8.3 ("In the mode the working tree's session files hold the session branch's version wherever it differs from HEAD … The preflight ends with `put-back` in the mode"). `ready.md` has no carve-out for §2.1 session-file shapes or for its own `_readiness.md`.
- **Suggested fix:** test dirtiness with `-z` against the `specs-repo-git` §2.1 classifier. Ignore session-file paths, and this command's own `_readiness.md` at the resolved scope. Or ignore all session-file paths whenever the preflight reported `session_branch`. Say so on the docs page.
- **Source:** review
- **Confidence:** medium (worked out from §8.3's stated behaviour, not reproduced in a live session-branch repository)

### DEV-B2 — MINOR — `/ready` says `specs-preflight` "creates no branch, a hard invariant", which is false in session-branch mode
- **Where:** `plugins/dev-workflows/commands/ready.md:22`, `:167`, `:734-737`
- **What is wrong:** "`specs-preflight` itself still creates none, switching `$SPECS_PATH` only between branches that already exist and are plugin-created (`workflows-core:specs-repo-git` §2.2)", and in the Invariants, "`specs-preflight` itself still creates no branch, a hard invariant". `specs-repo-git` §8.2 says the opposite. Where §3.4's flush would commit, the run calls `session-branch.py commit`, which "creates the session branch where it does not exist". §2.2, which `ready.md` cites, says "The session branch §8 creates is the plugin's too".
- **Failure scenario:** a first `/ready` in session-branch mode with leftover session files. The preflight's flush creates `session/<identity>` while the command's own invariant says no branch can be created. An agent that checks its invariants, or a maintainer relying on them, is misled. Two live statements contradict each other.
- **Evidence:** `specs-repo-git.md:1077-1081` (§8.2 step 1) and `:233-235` (§2.2), compared with `ready.md:735`.
- **Suggested fix:** qualify all three sites: "creates no deliverable branch; in session-branch mode its flush may create `session/<identity>` (§8.2)". Sweep the docs page and `.claude/rules/dev-workflows.md` for the same claim.
- **Source:** review
- **Confidence:** high

### DEV-B3 — MINOR — `/design`'s "Next Epic" loop skips Phase 1.5, so the next Epic is never classified or model-gated
- **Where:** `plugins/dev-workflows/commands/design.md:462-468`, against `:160-195`
- **What is wrong:** on *Next Epic*, "re-render the Phase 0 picker … then, on selection, loop back through Phases 2–7 for the selected Epic". Phase 1.5 is outside that range. Yet its classification "scales **grill depth**, `design.md` **section-inclusion** … and **`design-reviewer` rigor** together", and it owns the HARD gate for `SIGNIFICANT`/`HIGH-RISK` on a non-Opus session. Phase 1's resume-vs-fresh question for a ◐ Epic with its own `_design-session.md` is skipped too. Phase 0 step 5 / Phase 1 step 2 run only once.
- **Failure scenario:** on a Sonnet session, the first Epic classifies `MODERATE` and gets the soft advisory. The user takes *Next Epic* and picks an auth-path Epic that is `HIGH-RISK`. The run designs it with no relaunch gate, on the `MODERATE` section set and reviewer depth. A ◐ Epic picked from the loop is never offered *Resume* or *Start fresh*.
- **Evidence:** read `design.md:462-468` and Phase 1.5 `:160-195`. Nothing else in the command re-enters Phase 1.5 or Phase 1 step 2.
- **Suggested fix:** loop back through Phase 0 step 5, Phase 1 step 2 and Phase 1.5 to Phase 7. At minimum, re-classify and re-apply the gate per Epic.
- **Source:** review
- **Confidence:** medium

### DEV-B4 — MINOR — the `/design` docs page quotes a stop message the command no longer prints
- **Where:** `plugins/dev-workflows/docs/commands/design.md:58`, against `plugins/dev-workflows/commands/design.md:101`
- **What is wrong:** the docs page says absence stops with "`no specification.md exists yet for this item — run /product-workflows:specify for it and merge it to the specs repo main first.`" The command's stop is `DESIGN_NO_SPEC: no specification.md on the specs repo's default branch for <ADDRESS> — run '/product-workflows:specify <ADDRESS>' and land it there first.` The docs page never names `DESIGN_NO_SPEC`, though it names every other `/design` stop code.
- **Failure scenario:** a reader who searches the docs for the stop they hit finds neither the code nor the wording.
- **Evidence:** compared stop codes in the command with those on its docs page (command-only codes: `DESIGN_NO_SPEC`). The same comparison flags `READY_FOCUS_NOT_FOUND` (absent from `docs/commands/ready.md`) and `CONFORMANCE_ARD_NOT_ON_MAIN` (`docs/commands/conformance.md` describes the stop in words only). Those two are NIT-level omissions.
- **Suggested fix:** quote the current `DESIGN_NO_SPEC` message on the docs page, and name `READY_FOCUS_NOT_FOUND` and `CONFORMANCE_ARD_NOT_ON_MAIN` on theirs.
- **Source:** review
- **Confidence:** high

### DEV-B5 — NIT — an author's note has leaked into `DESIGN_NO_SPEC`'s printed message
- **Where:** `plugins/dev-workflows/commands/design.md:101`
- **What is wrong:** the backticked stop message runs on: "`… and land it there first. <ADDRESS> is this run's own resolved address, one address and no second key (D4).`" The last sentence is guidance for the author. It sits inside the literal message, so a run that prints the message verbatim prints that sentence too.
- **Failure scenario:** the user sees "BOOK-1-02 is this run's own resolved address, one address and no second key (D4)." in a stop message.
- **Evidence:** read line 101. Compare `READY_NEEDS_KEY` and `CONFORMANCE_NEEDS_KEY`, which keep their guidance outside the backticks.
- **Suggested fix:** move the `<ADDRESS> is …` sentence outside the code span.
- **Source:** review
- **Confidence:** high

## dev-workflows — /vuln, /upgrade

### VU-B1 — MAJOR — An auto-fixed test regression is returned as a pass without verify being run again
- **Where:** `plugins/dev-workflows/agents/vuln-fixer.md:221-222`, `plugins/dev-workflows/agents/upgrade-executor.md:124-125`. Consumers: `commands/vuln.md:318`, `references/handoff/vuln-fixer.md:143`, `references/handoff/upgrade-executor.md:133`.
- **What is wrong:** on `REGRESSIONS`, "If fixable automatically (import rename, trivial API migration …): fix and note in output, then proceed to step 6 (Output)". `upgrade-executor` says the same: "Auto-fix if straightforward … Explain every change in the output, then proceed to step 4 (Output)". Neither runs `test-baseliner` verify after its own edit. The only status that fits what follows is `SUCCESS` / `OK`. Those are defined as "no regression found" / "all previously-green tests still green". `/vuln` Step 4 says "`OK` in this column means the comparison happened and found no regression; nothing else earns it."
- **Failure scenario:** a MODERATE CVE bump breaks two tests. The fixer renames an import, never re-runs the suite, and returns `SUCCESS`. The table then shows `OK`, and `clean_finish` is `true`. Step 3.9 pushes and opens a mergeable pull request, which carries no DO-NOT-MERGE banner. On the gated path the auto-fix may also be a "trivial API migration" in source code, made after the Opus review. That edit is both unreviewed and untested.
- **Evidence:** read both agents' "Test regression" sections. No step after step 2 re-enters Verify, and no status says "auto-fixed, not re-verified". `clean_finish` (`vuln.md:277`, `upgrade.md:225`) has no condition for this case.
- **Suggested fix:** after an auto-fix, re-run step 5 (step 3 in the executor) once with the same baseline block, `Project root:` and `command_hint:`. If regressions remain, return `TEST_REGRESSION` with the auto-fix described. Alternatively, mark the return so that `clean_finish` goes `false`.
- **Source:** review
- **Confidence:** high

### VU-B2 — MAJOR — Research and planning read the tree before the run moves onto the base, so the fix is computed against a different tree
- **Where:** `commands/vuln.md:52-88` (Step 2 research) against `:100` (Step 3's §2.8.1 move); `commands/upgrade.md:38-102` (Phase 1 inventory and planning) against `:113-117` (Phase 2 prep's move). Also `agents/vuln-fixer.md:146-147` and `agents/upgrade-executor.md:46-48`, which apply the plan's `files` changes without re-reading the current version.
- **What is wrong:** `vuln-research` reads `current_version` and the `files` to change from the working tree at Step 2. `upgrade-planner` and Phase 1's inventory do the same. Only afterwards does the run switch to `<base>`, or detach at `origin/<base>` where the local base is strictly behind (`code-handoff.md` §2.8.1 step 3). That is the ordinary case of a clone that has not been pulled, and it also covers the *Switch to `<base>`* answer from a feature branch. The fixer and the executor then apply "bump X from A to B" to a tree where X may no longer be at A. `/implement` has the opposite invariant: "The branch is settled before the first read of the code" (`.claude/rules/dev-workflows-implement.md`).
- **Failure scenario:** the local `main` sits at `activemq 5.15.5` and `origin/main` has already moved to `5.18.3`. Research reports READY with `safe_version: 5.15.16`. Step 3 detaches at `origin/main`, and the fixer "updates the version pin" to `5.15.16`, which is a downgrade, or it edits a line that no longer exists. The commit body's "installed version inside the vulnerable range before" is false either way. A CVE that `origin/main` has already fixed is still worked, and a library added only on `origin/main` is reported `NOT_IN_REPO`. `/upgrade` likewise plans `from:` against the stale tree, so its "never silently downgrade" check (`upgrade.md:253`) was made against the wrong versions.
- **Evidence:** order of steps in both commands. No step re-reads versions after the move, and neither agent checks the plan's `from`/`current_version` against the file before editing it.
- **Suggested fix:** move the base resolution, the fetch and the §2.8.1 move (with the first-CVE / branch-start question) ahead of research and planning. Alternatively, have the fixer and the executor verify `current_version`/`from` against the file and return `BLOCKED` (or a new `STALE_PLAN`) on a mismatch.
- **Source:** review
- **Confidence:** medium. The ordering is certain. Whether an executing model notices the mismatch on its own is not.

### VU-B3 — MAJOR — `vuln-research` cannot detect a transitive-only vulnerable library in Maven or Gradle, and reports it `NOT_IN_REPO`
- **Where:** `agents/vuln-research.md` (tools `["Read","Glob","Grep","WebFetch","Skill"]`; "No files are written, no commands are run"; step 3 "Search the repo for the affected package … If not found: record `status: NOT_IN_REPO`"); `references/fix-vuln/build-systems.md:273-279` ("Identify which direct dependency introduces it (using `./gradlew dependencies`, `./mvnw dependency:tree`, `npm ls`, etc.)").
- **What is wrong:** the reference the research agent is told to follow resolves transitive dependencies by running build-tool commands. The agent has no Bash and is forbidden to run commands. Maven and Gradle builds usually carry no lockfile, so grep over `pom.xml` and `*.gradle` cannot find a library that only arrives transitively.
- **Failure scenario:** `/vuln CVE-2020-36518` (jackson-databind) in a Spring Boot Maven project that pulls jackson in only through `spring-boot-starter-web`. Grep finds no `jackson-databind` in any `pom.xml`, so research returns `NOT_IN_REPO`. Step 2 says "notify and skip", and the vulnerable library ships unfixed with a SKIP row.
- **Evidence:** the agent's tool list and invariants, compared with build-systems.md's transitive strategy. `/vuln` Step 2 maps `NOT_IN_REPO` to skip with no second look.
- **Suggested fix:** let research read lockfiles and also run read-only dependency-tree commands, through a narrow Bash grant or a bounded call. Alternatively, have research return `TRANSITIVE_UNKNOWN` / `NEEDS_TREE` rather than `NOT_IN_REPO` where the ecosystem has no lockfile, and have the orchestrator or fixer resolve the tree.
- **Source:** review
- **Confidence:** medium

### VU-B4 — MINOR — A `keep-anyway` regression has no return status; `/vuln` names one, `REGRESSION_KEPT`, that nothing defines
- **Where:** `agents/vuln-fixer.md:229-230`; `commands/vuln.md:377`, `:318`; `references/handoff/vuln-fixer.md:102`.
- **What is wrong:** on `regression_decision: keep-anyway` the fixer is told only to "proceed to step 6, recording the failures in `notes`". It sets no status. `upgrade-executor` sets `TEST_REGRESSION_KEPT` in the same place. `vuln.md:377` lists "`OK`, `TESTS_NOT_RUN` and `REGRESSION_KEPT`" as committed statuses, but `REGRESSION_KEPT` appears nowhere else in the plugin (`grep -rn REGRESSION_KEPT plugins/dev-workflows` hits only that line and the executor's `TEST_REGRESSION_KEPT`). It is not in the fixer's status list, and it is not in Step 4's fixed `Result` vocabulary (`:318`).
- **Failure scenario:** the user keeps a regression. The fixer returns `SUCCESS` (the only "proceed to output" status), so Step 4 writes `OK`, which the column defines as "the comparison happened and found no regression". Alternatively it repeats `TEST_REGRESSION`, which reads as an unresolved state. Either way the table misreports a CVE the user knowingly shipped with failing tests. `clean_finish` is still right, because it keys on the user's choice.
- **Evidence:** grep as above. The fixer's status list is at `handoff/vuln-fixer.md:102`.
- **Suggested fix:** add `REGRESSION_KEPT` (or `TEST_REGRESSION_KEPT`, to match `/upgrade`) to the fixer's step 4, its handoff status list and Step 4's `Result` vocabulary.
- **Source:** review
- **Confidence:** high

### VU-B5 — MINOR — Both docs pages still say a revert leaves `node_modules` as the upgrade left it; since 4.14.0 the run restores it
- **Where:** `plugins/dev-workflows/docs/commands/vuln.md:54`, `plugins/dev-workflows/docs/commands/upgrade.md:56`
- **What is wrong:** both pages say "It restores files, not installed packages: a package installed into an ignored directory such as `node_modules` stays until the next install." `install-time-code.md:49` ("After a revert") requires the opposite: "after any revert in a Node project … restore `node_modules` to the lockfile … run the install from the first section again". The agents (`vuln-fixer.md:212`, `:232`; `upgrade-executor.md:115`, `:135`) and both commands' *After a revert* paragraphs (`vuln.md:140`, `upgrade.md:156`) do this, and list each package put back as `restored unbuilt`.
- **Failure scenario:** a reader trusts the page, reinstalls by hand, and is surprised by the `restored unbuilt` entries. The page also hides that the revert reinstalls packages. This is a claim-expiry miss from `df4e9e38`. The lines are blamed to `dd72b9eb`, which predates the "After a revert" rule.
- **Evidence:** text comparison above.
- **Suggested fix:** rewrite the sentence on both pages: in a Node project the revert reinstalls the lockfile's versions without their install scripts, and the summary names each package put back unbuilt with its rebuild command.
- **Source:** review
- **Confidence:** high

### VU-B6 — MINOR — `nvd-api.md`'s worked example contradicts its own range rule
- **Where:** `plugins/dev-workflows/references/fix-vuln/nvd-api.md:79` against `:49-51`
- **What is wrong:** step 4 says to take the range containing the current version: "a project on `5.15.3` with ranges `[5.0.0, 5.15.16)` and `[5.16.0, 5.16.7)` — … the safe floor is `5.15.16`", and it warns that the global maximum "may push a `5.15.x` project to `5.16.7`". The example directly below, with those same two ranges, concludes "Safe version: `5.16.7` (or the latest 5.x patch release >= that bound)". The handoff examples (`handoff/vuln-research.md:37`) use `5.15.16` for `5.15.5`.
- **Failure scenario:** an agent anchoring on the worked example picks `5.16.7` (a minor jump) for a 5.15.x project. That over-classifies the CVE and widens the change.
- **Evidence:** lines quoted.
- **Suggested fix:** make the example's conclusion depend on the current version ("`5.15.16` for a 5.15.x project, `5.16.7` for a 5.16.x one").
- **Source:** review
- **Confidence:** high

### VU-B7 — MINOR — `nvd-api.md`'s Maven Central query cannot list versions, and its CPE vendor examples are Maven group IDs
- **Where:** `plugins/dev-workflows/references/fix-vuln/nvd-api.md:95`, `:37`
- **What is wrong:** (a) `https://search.maven.org/solrsearch/select?q=g:<groupId>+AND+a:<artifactId>&rows=20&wt=json` has no `core=gav`. The default core returns one document per group:artifact pair, carrying only `latestVersion`, so "confirm the version exists and find the latest patch in that line" cannot be done from it. `upgrade/ecosystems.md:64` has `core=gav` correctly. (b) ":37 `vendor` and `product` together identify the library (e.g., `org.apache.activemq` / `activemq`, `com.fasterxml.jackson.core` / `jackson-databind`)" is wrong: CPE vendors are `apache` and `fasterxml`, as this file's own example at `:64` shows (`cpe:2.3:a:apache:activemq`).
- **Failure scenario:** research gets one latest version, which may be a new major, and either picks it or cannot confirm the patch line. An agent that matches a CPE vendor against a Maven groupId misses the match and returns `NOT_IN_REPO` or `LOOKUP_FAILED`.
- **Evidence:** read the lines. Solr `core=gav` semantics are from the Maven Central search API.
- **Suggested fix:** add `&core=gav` (as in ecosystems.md), and correct the vendor examples to `apache` / `fasterxml`.
- **Source:** review
- **Confidence:** high for (b); medium-high for (a)

### VU-B8 — MINOR — The GitHub Actions SHA-pin update writes a tag object's SHA for an annotated tag
- **Where:** `plugins/dev-workflows/references/upgrade/ecosystems.md:427-430`
- **What is wrong:** "If pinned to a SHA … also update the SHA to the commit at the new tag: `git ls-remote https://github.com/<owner>/<repo>.git refs/tags/<tag>`". For an annotated tag this prints the tag object's id, not the commit's. The peeled commit is on the `refs/tags/<tag>^{}` line, which an exact-tail pattern does not print.
- **Failure scenario:** an action whose release tags are annotated gets `uses: owner/repo@<tag-object-sha>`. That is not a commit, so the workflow fails to resolve the action, or pins something other than the intended commit.
- **Evidence:** measured in the scratchpad. For an annotated `v1`, `git ls-remote <url> refs/tags/v1` printed only `293c435…	refs/tags/v1` (the tag object). `git ls-remote <url> 'refs/tags/v1*'` also printed `a275984…	refs/tags/v1^{}`, which is the commit `git rev-parse HEAD` reported.
- **Suggested fix:** query `refs/tags/<tag>` and `refs/tags/<tag>^{}`, and take the `^{}` line where present (for example `git ls-remote <url> 'refs/tags/<tag>*'` and filter the peeled line). Alternatively, use `gh api repos/<o>/<r>/commits/<tag> --jq .sha`.
- **Source:** review
- **Confidence:** high

### VU-B9 — MINOR — `/upgrade`'s `clean_finish` flips on a component that never reached the repository
- **Where:** `commands/upgrade.md:225` against `:213` and `code-handoff.md` §2.9 (third bullet)
- **What is wrong:** step 6.5 says step 3a's `BLOCKED` (an unreadable `plan_file`, a missing `pre_edit_tree:`, a snapshot git could not write) "does **not** set `clean_finish: false`". Step 7.5, which is where the flag is computed, says "`clean_finish: false` when any component ended `BLOCKED` …" with no qualifier. §2.9 limits it to a unit "**that reached the repository**". These are two live instructions that disagree, and the one that does the computing is the wrong one.
- **Failure scenario:** a snapshot write fails for one component, and three others pass every gate. Step 7.5 opens the batch's pull request as a draft carrying the DO-NOT-MERGE banner for a component that changed nothing.
- **Evidence:** lines quoted.
- **Suggested fix:** in step 7.5, write "any component that reached the repository and ended `BLOCKED`".
- **Source:** review
- **Confidence:** high

### VU-B10 — MINOR — `/upgrade` writes keys and a resolved folder it can never have
- **Where:** `commands/upgrade.md:10` (Usage: no address), `:112` ("an **issue-key** segment from the run's own resolved key when it has one"), `:209` ("the subject ends with `[<key>]` where the run resolved one and carries a `Work-Item:` trailer where the folder has one"), `:225` ("`key` and `workitem_key` from the resolved folder … `upgrade <first> and <N> more [<key>]`"), `:243`, `:245`; `:32` (Phase 0 names no run key set)
- **What is wrong:** `/upgrade` takes component tokens only. It reads no address, resolves no folder and states no run key set for `specs-preflight` (`specs-repo-git` §3 runs "once the run key set (§3.2) is known"). Yet four steps tell it to use "the run's" key and folder.
- **Failure scenario:** an agent looking for the key it was told to use derives one from the current branch name, which CLAUDE.md § Editing discipline forbids ("never parse one out of free text"). The result is a commit `[KEY]` suffix and a `Work-Item:` trailer that no folder backs. At best the prose is dead and misleads a maintainer about a capability that does not exist.
- **Evidence:** `grep -n "address\|resolve-address\|read-key" commands/upgrade.md` returns nothing.
- **Suggested fix:** state that `/upgrade` is keyless (empty run key set at Phase 0). Pass `key: null` and `workitem_key: null`, and drop the `[<key>]` clauses. Alternatively, add an optional `--key`/address token if keyed upgrades are wanted (see VU-G3).
- **Source:** review
- **Confidence:** high

### VU-B11 — MINOR — `/vuln`'s Step 0 reads `--allow-install-scripts`' value as an `ADDRESS:CVE-ID` token
- **Where:** `commands/vuln.md:38` (Step 0: the run key set "is the key each token of `$ARGUMENTS` carries as its optional address, read with `read-key`"), against `:44` (Step 1 is where `--allow-install-scripts <name>[,<name>…]` is first taken out)
- **What is wrong:** `strip-run-flags` removes only `--skip-costs`, `--skip-feedback` and `--enforce-model`. At Step 0 the `--allow-install-scripts` option and its value are still tokens. Its documented values include `project:<hook>` and `project:<member path>:<hook>` (`install-time-code.md:53`), which have exactly the `ADDRESS:CVE-ID` shape.
- **Failure scenario:** `/vuln CVE-2024-1234 --allow-install-scripts project:postinstall`. Step 0 reads `project` as the address of a token and passes it to `read-key`. That returns `invalid` (or `needs-tree`), and Step 0 defines no outcome for it. It may stop the run, or put a bogus key in the preflight's key set, before Step 1 ever removes the option.
- **Evidence:** order of the two steps; `addressing.md:61` (`read-key`'s `invalid` / `needs-tree`).
- **Suggested fix:** take `--allow-install-scripts` out right after `strip-run-flags`, before Step 0 reads any token. Alternatively, have Step 0 skip the option and its value explicitly.
- **Source:** review
- **Confidence:** medium

### VU-B12 — MINOR — "Branch each CVE from `<current>` instead" gives later CVEs no instruction to switch back to `<current>`
- **Where:** `commands/vuln.md:106` (and `:100`, `:102`)
- **What is wrong:** the rule for later CVEs is "On later CVEs the branch HEAD sits on is one this run created, so switch without asking". That rule is written for the move onto `<base>`. For *Branch each CVE from `<current>` instead* the text says only that it "stays the user's choice and changes nothing else". No step records `<current>` and switches back to it before each later CVE. The exhausted-ladder paragraph (`:102`) does spell this out for its own case: record the position, then `git switch <that branch>` before each later CVE.
- **Failure scenario:** on CVE 2 HEAD is on CVE 1's fix branch. The agent either switches to `<base>`, overriding the user's choice, or makes no switch. In the second case CVE 2 branches off CVE 1 and ships CVE 1's fix in its own diff and pull request, which is the contamination `:100` exists to prevent.
- **Evidence:** read `:100-107`. The *Cancel this run* text (`:126`) confirms that no switch is issued under that answer, at least on the first CVE.
- **Suggested fix:** under that answer, record `<current>` and switch back to it before each later CVE's first dispatch, under the failed-switch rule, as `:102` does.
- **Source:** review
- **Confidence:** medium

### VU-B13 — MINOR — The `/vuln` commit template both follows the project's style and is used verbatim
- **Where:** `commands/vuln.md:394` ("Use the project's existing style.") against `:274` ("`/vuln` is the one caller with a full template of its own, so §2.3 uses it verbatim rather than deriving a subject from the repo's log"), `:423` and `code-handoff.md:101` ("A caller with a full template of its own overrides this paragraph")
- **What is wrong:** these are two live instructions about the same subject line. One says to adapt it to the log; three say to use it verbatim.
- **Failure scenario:** in a repository whose log has no conventional-commit prefixes, one run writes `fix(deps): upgrade …` and another writes `Upgrade …`, depending on which sentence the model weighs.
- **Evidence:** lines quoted.
- **Suggested fix:** drop "Use the project's existing style", or say explicitly that the template's subject type adapts to the log while the rest is verbatim.
- **Source:** review
- **Confidence:** high

### VU-B14 — MINOR — `fix-vuln/build-systems.md` lists Cargo in its detection table but has no Cargo section
- **Where:** `plugins/dev-workflows/references/fix-vuln/build-systems.md:16` (detection row `Cargo.toml | Rust / Cargo`); no `## Cargo` section; "Confirming the fix" (`:282-298`) covers Gradle, Maven, npm and Go only.
- **What is wrong:** `vuln-fixer` step 3 ("Use the ecosystem-appropriate update command (see build-systems.md)") and `vuln-research` step 3 ("per-ecosystem library detection") get nothing for Cargo. Nor is there anything for confirming a NuGet, pip or Bundler fix. `upgrade/ecosystems.md:304-331` does have a Cargo section (`cargo update -p <crate> --precise <version>`).
- **Failure scenario:** a RustSec CVE in `Cargo.lock` gets an improvised fix. The likely one is editing `Cargo.toml`, which does not move a transitive pin, where the right fix is `cargo update -p <crate> --precise <ver>`.
- **Suggested fix:** add a Cargo section (detect in `Cargo.toml` and `Cargo.lock`; update with `cargo update -p … --precise …`; confirm with `cargo tree -i <crate>`), and add confirm lines for the other rows.
- **Source:** review
- **Confidence:** high

### VU-B15 — MINOR — `ecosystems.md`'s NuGet query says the last version is the latest stable
- **Where:** `plugins/dev-workflows/references/upgrade/ecosystems.md:253-255`
- **What is wrong:** "`GET https://api.nuget.org/v3-flatcontainer/<package_lower>/index.json` … `.versions` — list of all versions (last is latest stable)." The flat-container index lists prerelease versions too, in SemVer order, so the last entry is a prerelease whenever one is newer than the latest stable release (for example `9.0.0-preview.7` after `8.0.8`).
- **Failure scenario:** `/upgrade SomePackage:latest` resolves to a preview build.
- **Suggested fix:** "the last entry with no `-` prerelease suffix".
- **Source:** review
- **Confidence:** high

### VU-B16 — NIT — `/upgrade`'s executor dispatch names no model for `SIGNIFICANT`
- **Where:** `commands/upgrade.md:161` (`<detection_model — §2.1 Sonnet chain — for SIMPLE/MODERATE; planning_model — §2 Opus chain — only if HIGH-RISK>`), compared with `commands/vuln.md:212` (`<detection_model for SIGNIFICANT; planning_model … only if HIGH-RISK>`)
- **What is wrong:** `SIGNIFICANT` falls between the two arms, and the `model_routing` comment on `:182` names `upgrade-executor` only under `SIMPLE/MODERATE` too.
- **Suggested fix:** use `/vuln`'s wording ("detection_model for SIMPLE/MODERATE/SIGNIFICANT").
- **Source:** review
- **Confidence:** high

### VU-B17 — NIT — The install references say `install-time-code.md` "says why" Poetry and the others install unchanged; it gives no reason
- **Where:** `references/fix-vuln/build-systems.md:167` ("by its own command, unchanged (`install-time-code.md` says why)"), `references/upgrade/ecosystems.md:184` ("Poetry installs unchanged (`install-time-code.md` says why)") against `install-time-code.md:18` ("…have their own no-build or no-scripts settings that this file does not yet adopt")
- **What is wrong:** the referenced text states that these ecosystems are not yet covered, which is not a reason. A reader following the pointer finds no justification.
- **Suggested fix:** write "(`install-time-code.md`: not yet covered)", or close the gap (VU-G1).
- **Source:** review
- **Confidence:** high

## product-workflows — idea → PRD → ARD → spec → epics, decisions, proposals

### PRD-B1 — MINOR — *Set SPECS_PATH* in four product commands carries any typed path, against the rule that re-asks until it names an existing directory (the D5 class, at sites D5 does not list)
- **Where:** `plugins/product-workflows/commands/create-prd.md:77`, `update-prd.md:29`, `create-ard.md:209`, `specify.md:211-212`; the rule is at `plugins/workflows-core/references/escalation-rules.md:226-233`.
- **What is wrong:** Each of the four says *"Set SPECS_PATH* asks for the path in plain text and carries it as `$SPECS_PATH` for the run". The shared rule says the answer is carried *"once it names an existing directory … and the question is asked again where it does not"*. None of the four cites that rule, and the rule's own citer list does not name them. So two live instructions disagree, and the local one, which the agent follows, has no validation.
- **Failure scenario:** `SPECS_PATH` is unset, `/create-ard ACME-7` runs, and the operator types a mistyped path. The run carries the path anyway, and the preflight then reports "not a directory / not a git repo". `resolve-address` returns `absent`, and the run stops with `CREATE_ARD_NOT_FOUND`, which says the folder does not exist. In `/create-prd` and `/idea` the `absent` branch goes on and creates a folder. A typo that happens to name an existing non-specs directory sends `/create-prd`'s first write to `<typo>/specifications/PRD-…/`.
- **Evidence:** I compared the quoted lines with each other. `/idea:44`, `/prd-proposal:89-91` and `/brd-proposal:80-82` cite the rule by name and so inherit its re-ask; these four do not. to-fix.md D5 names only `/design`, `/ready` and `/conformance`.
- **Suggested fix:** Replace each local clause with a citation of *Required path environment variable unset*, as `/prd-proposal` does, and add the four to that rule's citer list. Alternatively, fold these sites into D5 when it is fixed.
- **Source:** review (extends to-fix D5)
- **Confidence:** high

### PRD-B2 — MINOR — `/epics` has no `$SPECS_PATH`-unset step and no mapping for `resolve-address`'s `status: invalid`, while the hook and the docs promise that it asks
- **Where:**
  - `plugins/product-workflows/commands/epics.md:31-53` (Phase 0 step 1 maps only `found`, `ambiguous`, `misrooted` and `absent`; `EPICS_NEEDS_KEY` is only for "no positional address");
  - `plugins/product-workflows/hooks/preload-context.sh:76` (`"SPECS_PATH: (not set — the command will ask)"`);
  - `plugins/product-workflows/docs/reference/environment.md:11` (*"Every command that needs it stops naming `SPECS_PATH` explicitly and offers to enter a path or cancel"*);
  - `plugins/workflows-core/references/addressing.md:61` (*"a caller whose address is required takes its own `$SPECS_PATH` stop on it"*) and `:269`.
- **What is wrong:**
  - `/epics` never tests `$SPECS_PATH`. `grep -n 'SPECS_PATH. (required)\|Set SPECS_PATH\|needs-tree' epics.md` finds nothing.
  - A malformed key makes `resolve-address` return `status: invalid`, which no branch of step 1 handles.
  - With the variable unset, the run reaches `EPICS_NOT_FOUND`, whose text, *"no folder found for <ADDRESS> under $SPECS_PATH/specifications/"*, blames the address rather than the variable.
  - Related: `/create-ard:53`, `/specify`, `/prd-proposal:95` and `/brd-proposal:86` read the key with `read-key` before their `$SPECS_PATH` step and map only `invalid`. They do not handle `needs-tree`, which `read-key` returns for a whole-folder-name token while the variable is unset. `/idea`, `/create-prd` and `/update-prd` handle it.
- **Failure scenario:**
  - A fresh shell with no `SPECS_PATH` runs `/epics ACME-7`. The hook prints "the command will ask", but the command never asks, and the run stops claiming no folder exists for `ACME-7`.
  - `/epics acme-7` (a malformed key) reaches an unmapped status and has no defined stop.
- **Evidence:** I read `epics.md:26-283`, and the greps above.
- **Suggested fix:**
  - Add a `$SPECS_PATH (required)` step to `/epics` Phase 0, citing *Required path environment variable unset*.
  - Map `status: invalid` to `EPICS_NEEDS_KEY` with the grammar.
  - Have the four key-first commands take their `$SPECS_PATH` stop on `needs-tree`, as `/create-prd` step 1 does.
- **Source:** review
- **Confidence:** high

### PRD-B3 — MINOR — `/epics` reads a `refinement_candidate` frontmatter flag that nothing writes or defines, attributing it to a retired reader
- **Where:** `plugins/product-workflows/commands/epics.md:520` (*"read each `epic.md`'s `refinement_candidate` and `scope_hint` (emitted by the folder read at `prd-plus-epics`)"*), `:526-537` (the Phase 3.5 detected-drafts branch), `:1155` and `:1160`; also `plugins/dev-workflows/references/workflow-states.md:63`.
- **What is wrong:** `grep -rn refinement_candidate plugins --include=*.md` finds only readers. No format reference defines the field, `epic-writer`'s frontmatter template does not write it, and no command does. The "folder read at `prd-plus-epics`" was an agent. `epics.md:487-491` says that agent was deleted and replaced by a direct read, and `:501` says *"nothing creates an empty Epic"*.
- **Failure scenario:** Phase 3.5's "Detected N near-empty Epic drafts" branch, its mode question and the leftover gate can be reached only through a hand-written field. A reader trusting the invariant at `:1155` believes detection runs, when the branch is dead. An operator who hand-writes `refinement_candidate: true` meets a mode that no format documents.
- **Evidence:** the grep above and `epics.md:487-520`.
- **Suggested fix:** Either define the field in an Epic format reference and have something write it, or retire the detection branch and leave refine reachable only through `focus_key`. Then sweep `:526`, `:1155`, `:1160` and `workflow-states.md:63`.
- **Source:** review
- **Confidence:** high

### PRD-B4 — MINOR — `/update-prd` Phase 1 asks a Refresh-or-Re-do question whose answer nothing reads
- **Where:** `plugins/product-workflows/commands/update-prd.md:106`.
- **What is wrong:** The command asks `choices: ["Refresh (incorporate new info / comments / transcript) (Recommended)", "Re-do (substantive re-scope driven by an ARD/spec obstacle)", "Cancel"]`, but no later phase branches on the answer. `grep -n 'Re-do\|re-scope'` over the command and its docs page finds only this line. `escalation-rules`' *When a choice list fires* calls a list whose answer changes nothing a defect.
- **Failure scenario:** An operator who picks *Re-do* expects a re-scope mode, gets exactly the same grill as *Refresh*, and is never told so.
- **Evidence:** the grep above; this has been present since the plugin was renamed (`7b47f23b`).
- **Suggested fix:** Either define what *Re-do* changes (grill breadth, the diff-against-base rule, the `revision_of` note) or drop the question and keep a plain *Cancel* or confirmation.
- **Source:** review
- **Confidence:** high

### PRD-B5 — MINOR — the agents reference page's exclusivity claim about `docs-grounder` is false
- **Where:** `plugins/product-workflows/docs/reference/agents.md:40`.
- **What is wrong:** The page says *"`workflows-core:docs-grounder` is the one agent no command here dispatches by writing a `subagent_type:` inline — its callers invoke a named procedure"*. Three more agents are reached the same way:
  - `architecture-grounder`, through `dispatch-architecture-grounder` in `/create-ard:586` and `/specify:870`;
  - `promotion-scout` and `adr-drafter`, whose `subagent_type:` lines are in `workflows-core/references/architecture-promotion.md:103` and `:174` and not in `/promote-decisions`.
- **Failure scenario:** A maintainer sweeping the agents that commands dispatch by inline `subagent_type` trusts "the one" and misses three.
- **Evidence:** `grep -n 'subagent_type: "workflows-core:architecture-grounder' commands/*.md` finds nothing; the `architecture-promotion.md` lines are quoted above.
- **Suggested fix:** Name all four, or state the class ("agents dispatched through a reference's named procedure") without a count.
- **Source:** review
- **Confidence:** high

### PRD-B6 — MINOR (low confidence) — `/epics` Phase 8's Instructions agent still edits files after the handoff, the reason Agent 1 was changed to report only
- **Where:** `plugins/product-workflows/commands/epics.md:899-907` against `:881`.
- **What is wrong:** Agent 1 is told *"do NOT edit the file — this run has already handed its drafts off, and an edit made now would sit uncommitted"*. Agent 3 is told to check `CLAUDE.md` in the project root (the resolved PRD folder) and `~/.claude/CLAUDE.md`, and *"If YES: apply minimal, additive, scoped changes only"*. The same reasoning applies to Agent 3.
- **Failure scenario:** A run leaves an edited `CLAUDE.md` uncommitted in the specs repository after Phase 7.5 has already committed. That file is an OTHER path, so §3.3's G1 advisory fires on every later run. A global `~/.claude/CLAUDE.md` edit also lands with no review.
- **Evidence:** I read both prompts. Whether a PRD folder ever holds a `CLAUDE.md` is unmeasured, which is why confidence is low.
- **Suggested fix:** Make Agent 3 report-only, like Agent 1, or drop it in favour of `impl-maintenance`'s instruction-file findings.
- **Source:** review
- **Confidence:** low

### PRD-B7 — NIT — the hooks page miscounts the plugin's other commands and calls them all keyed
- **Where:** `plugins/product-workflows/docs/reference/hooks.md:17`.
- **What is wrong:** The page says *"`/epics` is the one command this plugin ships that this hook covers — the other thirteen are keyed but resolve their own address"*. The plugin ships sixteen commands (`docs/README.md`, `plugin.json`), so there are fifteen others. `/harvest-decisions` and `/promote-decisions` take no address at all; they are keyless runs.
- **Failure scenario:** A reader sizing the hook's scope gets a wrong count.
- **Evidence:** `ls commands | wc -l` gives 16; `harvest-decisions.md:16` and `promote-decisions.md:18` show their usage lines.
- **Suggested fix:** Change it to "the other fifteen", noting that two are keyless.
- **Source:** review
- **Confidence:** high

### PRD-B8 — NIT — the environment page says every command offers to enter a path when `$SPECS_PATH` is unset; `/harvest-decisions` and `/promote-decisions` stop flat
- **Where:** `plugins/product-workflows/docs/reference/environment.md:11`, against `commands/harvest-decisions.md:22` (`HARVEST_NEEDS_SPECS_PATH: set SPECS_PATH …`, no choice) and `workflows-core/references/architecture-promotion.md` §1 step 4 (`PROMOTE_NEEDS_SPECS_PATH`, no choice). `/epics` has no step at all (PRD-B2).
- **What is wrong:** The page says *"Every command that needs it … offers to enter a path or cancel"*.
- **Suggested fix:** Qualify the sentence: the two knowledge-base commands stop and name the variable.
- **Source:** review
- **Confidence:** high

### PRD-B9 — NIT — `/epics` Phase 3.5's adaptive code-scan array can show the same setting twice
- **Where:** `plugins/product-workflows/commands/epics.md:541`.
- **What is wrong:** The array is `choices: ["<adaptive default> (Recommended)", "<the other setting>", "Keep my Phase 1 choice"]`. Where the Phase 1 answer equals the adaptive default, which is the common case, options 1 and 3 do the same thing. *When a choice list fires* then calls for no list, or for a two-option one.
- **Failure scenario:** Phase 1 leaves the scan ON (its default) and there are two or more refinement targets, so the adaptive default is ON. The operator is asked a three-option question in which two options do the same thing.
- **Suggested fix:** Ask only where the adaptive default differs from the Phase 1 answer, with two options.
- **Source:** review
- **Confidence:** medium

## product-workflows — /create-prd, /create-ard, /specify, proposals (second pass)

### PRD2-B1 — MINOR — `/create-prd` never says to write `brd_key`, `brd_parent`, `depends_on` or the BRD-route `sources`, although its final report, its cost step and its docs page all say it does
- **Where:**
  - `plugins/product-workflows/commands/create-prd.md:572`. The spine's frontmatter item lists only *"`sources` (propagated), `derived_from`, `seeded_from_prd` (only when `--from-prd` was used), and `key`"*.
  - `:891` (cost step): *"which is also the value this run writes as the PRD's `brd_key`"*.
  - `:906-908` (final report): *"the frontmatter `brd_key` / `brd_parent` / `depends_on` as written"*.
  - `plugins/product-workflows/docs/commands/create-prd.md:73`: on the BRD route the PRD *"carries `brd_key`, `brd_parent` … and `depends_on` … instead of `derived_from`"*, and *"Its `sources` ref is … the path the `source:` header of its `brd/brd-inventory.md` names"*.
  - `workflows-core/references/prd-format.md:44`: the three fields are *"written only by `/create-prd` on the BRD route, from the BRD's own `brd-link.md`"*.
- **What is wrong:**
  - No step of the command says to write the three provenance fields, or where their values come from (`brd-link.md`'s `parent:` and `depends-on:`).
  - Phase 2's `sources` and `derived_from` rule (`:454`) is defined only from an `idea.md`, and the BRD route has none.
  - Only the docs page says what `sources` holds on the BRD route and that `derived_from` is dropped. An agent runs the command, not the docs page.
  - The final report and the cost step take for granted a write that no step instructs.
- **Failure scenario:** A BRD-route run follows the spine literally. It writes `key` but no `brd_key` or `brd_parent`, and it writes either no `sources` or an invented one. `brd_parent` absent beside `brd_key` is the only state `prd-reviewer` 2a checks, so the reviewer does not flag a PRD that carries neither. The `depends_on` that `/brd-proposal` reads for peak concurrency is then missing on every slice, and the final report prints values that were never written.
- **Evidence:** `grep -n "brd_key\|brd_parent\|depends_on" create-prd.md` returns only `:891`, `:906` and `:907`, all of which are readers or reports.
- **Suggested fix:** Extend spine item 1 with a BRD-route clause:
  - `brd_key` = the slice key;
  - `brd_parent` = `brd-link.md`'s `parent:`;
  - `depends_on` = its `depends-on:`, omitted when empty;
  - `sources` = the customer document that the inventory's `source:` header names;
  - no `derived_from`.
- **Source:** review
- **Confidence:** high

### PRD2-B2 — MINOR — `/create-prd` cannot take an `@<path>` address, but its docs page offers one, and the resolver's `ambiguous` stop sends the operator there
- **Where:**
  - `plugins/product-workflows/commands/create-prd.md:44`: it parses the first non-flag token *"and read[s] it with `read-key`"*, and a token `read-key` finds `invalid` stops with `CREATE_PRD_NEEDS_KEY` (`:54-55`).
  - `:20`: the usage line, `<ADDRESS> [@idea.md]`, uses an `@` token for the idea.
  - `docs/commands/create-prd.md:15`: *"`<ADDRESS>` (mandatory) — a key you choose, or an `@<path>` naming a folder in the specs tree"*.
  - `workflows-core/references/addressing.md:496-498`: `status: ambiguous` is *"a hard stop naming every match … Name `@<path>` in the stop as the way through it"*.
- **What is wrong:** `read-key` has three readings — a key, a whole folder name, and a prefixed key (`addressing.md:44-61`). An `@<path>` matches none of them, so it is `invalid`, and step 1 stops before `resolve-address`, whose `@<path>` branch would have accepted it. On this command an `@` token is the idea argument in any case. The docs page promises a form the command refuses. Where two folders assert one key, the shared `ambiguous` stop gives `@<path>` as the only way through, and that path is a dead end for `/create-prd`.
- **Failure scenario:**
  - The tree holds two folders asserting `ACME-7`. `/create-prd ACME-7` stops `ambiguous` and names `@<path>`.
  - The operator re-runs `/create-prd @specifications/PRD-ACME-7-a`. That token is read as a key, found invalid, and the run stops with `CREATE_PRD_NEEDS_KEY`.
  - If the operator also gives the key, the `@` path is read as the idea and the run is ambiguous again.
- **Evidence:** I read step 1 against `read-key` §1 and `resolve-address` §3 step 1, and the docs line quoted above.
- **Suggested fix:** Either accept an `@<path>` address in step 1 (taking the first `@` token that names a directory under `specifications/` as the address, and any other as the idea), or remove the `@<path>` form from the docs page and have the ambiguous case name a repair (de-duplicate the folders) instead. The same `read-key`-first pattern is in the other key-first commands (PRD-B2 lists them), so check whether they share this dead end.
- **Source:** review
- **Confidence:** medium (the `ambiguous` dead end is certain; whether the docs line was meant for the address or only for other commands is not)

### PRD2-B3 — MINOR — `--from-prd` on the BRD route: Phase 0 reads the seed and Phase 1 offers two arrays, but Phase 2 says "exactly two files … and no other seed"
- **Where:**
  - `plugins/product-workflows/commands/create-prd.md:59-73` (step 2a resolves and reads the `--from-prd` seed, and stops on an unreadable one, on every route);
  - `:236` (*"redirect … unless `--from-prd` **or the BRD route** is present"*);
  - `:394-409` (Phase 1 step 2 has one bullet for *"the BRD route present"* and one for *"`--from-prd` present"*, each with its own array, and no rule for both);
  - `:460-461` (*"If `--from-prd` was resolved … also read the seed PRD"*);
  - `:467` (BRD route: *"Read exactly two files from the BRD folder … and no other seed"*).
- **What is wrong:** The rules say `--from-prd` survives as a flag (`.claude/rules/brd-route-detection.md`), so a BRD-route run with `--from-prd` is reachable. Phase 0 reads and gates the seed, and Phase 2's BRD section forbids reading it, so the two instructions contradict. Phase 1 step 2 matches two bullets with different arrays: the BRD one's *Overwrite* says "authored from the BRD seed" and the `--from-prd` one's says "as a new seeded PRD". Step 6 says to redirect "unless" either is present, while Phase 1 offers the redirect as *(Recommended)* in all three cases.
- **Failure scenario:** `/create-prd EPIC-008-01 --from-prd ACME-3` on a slice that already holds a `prd.md`. The agent has to choose which of two arrays to present, which `escalation-rules`' *verbatim* rule forbids it to improvise. In Phase 2 it either drops a seed that it validated and stopped on in Phase 0, or reads a file the BRD section says it must not.
- **Evidence:** I read the lines quoted above. No sentence in the command names the combination.
- **Suggested fix:** State the combination once:
  - either refuse it in step 2a (the BRD route is seeded by its register), or allow it as extra read-only grounding, as `@<path>` is allowed (`:94-96`);
  - give Phase 1 step 2 a precedence (the BRD bullet first);
  - reword step 6's "unless" to "see Phase 1".
- **Source:** review
- **Confidence:** medium

### PRD2-B4 — NIT — `prd-reviewer` still calls the BRD-route key `<BRD-KEY>`
- **Where:** `plugins/product-workflows/agents/prd-reviewer.md:26`: *"`key` is required on every route, including the BRD route, where it is the `<BRD-KEY>` naming this PRD's own folder"*.
- **What is wrong:** On the BRD route the PRD's folder is the `PRD-` slice, and its key is the slice key (`create-prd.md:572`; `prd-format.md` *"the `PRD-` slice's own key"*). A `BRD-` key names the container, which the command refuses. A reviewer that takes the placeholder literally may expect `key` to equal the parent BRD's key, which is `brd_parent`'s value.
- **Suggested fix:** Change it to "where it is the `<SLICE-KEY>` of the `PRD-` slice folder this PRD is written into".
- **Source:** review
- **Confidence:** high

### PRD2-B5 — NIT — small text defects in `/create-prd` and its docs page
- **Where and what:**
  - `create-prd.md:866`: *"Handing to PA (`/product-workflows:create-ard <PRD>`) or PE (`/product-workflows:epics <PRD>`)"* uses `<PRD>`, while the paragraph at `:829` insists that every option takes the one `<ADDRESS>`.
  - `create-prd.md:921`: *"All three the BRD route refusals are Phase 0 stops"* is garbled. Phase 0 now has five route-independent and BRD-route refusals (5a, 5b, 7's two, and 7a's two), so "three" is also stale.
  - `create-prd.md:876`: the capture-at-block list of user halts names every Phase 0 stop except `CREATE_PRD_SEED_NOT_FOUND` (step 2a). That stop is a user halt too, and its omission from a list that reads as exhaustive leaves the agent to decide whether to `emit-block`.
  - `docs/commands/create-prd.md:85`: *"for an already-created empty ticket"* is tracker-era wording. The key is a folder key that nothing mints, so there is no ticket.
  - `docs/commands/create-prd.md:99`: *"resolves `EPIC-008-01`'s `PRD-` slice folder one level under `specifications/`"*. A slice sits under its `BRD-` root, two levels down. `/create-ard`'s and `/specify`'s docs pages make the same mistake (PRD2-ARD-B10, PRD2-SPEC-B10).
- **Suggested fix:** Make each wording fix.
- **Source:** review
- **Confidence:** high

<!-- /create-ard -->

### PRD2-ARD-B1 — MAJOR — An Epic-level run under a BRD slice is told to write the slice's frontmatter: `epic: <SLICE-KEY>`, `components:`, and an `inherits:` that points past the slice ARD it must inherit — **Fixed in product-workflows 3.37.0 (batch B07)**
- **Where:**
  - `plugins/product-workflows/commands/create-ard.md:386-390` (an Epic under a slice *"is the BRD route with that slice as the BRD folder and this Epic as the focus"*);
  - `:513-518` (*"a `parent:` (this folder is a slice — the only shape this route resolves …) → `prd: <parent-key>`, `epic: <SLICE-KEY>`"*);
  - `:655-673` (*"Frontmatter on the BRD route"*: `scope: epic — the route resolves a slice and nothing else`, `prd:`/`epic:` = *"the `parent:` key and `<SLICE-KEY>`"*, `inherits:` *"the parent BRD folder's `ard.md`"*, `components:` *"as on any PRD-level run"*);
  - against `:595` (*"The ARD of an `EPIC-` folder (an Epic-level run) carries no `components:`"*) and `:742-744` (which names *"an Epic-level run under a slice"* explicitly, so the case is reachable);
  - also `:349` and `:957-958` (*"every run of this route is slice-level"*);
  - `references/ard-format.md:27` (*"epic: … on the BRD route, always the slice's own key"*) and `:41`.
- **What is wrong:** Phase 2 puts an `EPIC-` folder under a slice on the BRD route. Every BRD-route rule after that, however, assumes the run resolved the slice itself. For an Epic's ARD, the frontmatter list then:
  - sets `epic:` to the slice key rather than the Epic's key;
  - sets `prd:` to the parent BRD;
  - writes `components:`, which `:595` and `ard-format.md:41` forbid on an Epic ARD;
  - sets `inherits:` to the parent BRD's `ard.md`. A BRD container never holds one (step 1a, `:128-133`), so the value is `null`, although the PRD-level ARD the Epic actually inherits is the slice's `ard.md`.
- **Failure scenario:** `/create-ard EPIC-ACME-7-01-01` runs on an Epic inside slice `PRD-ACME-7-01-…`, and the slice already has a merged `ard.md`.
  - The ARD is written with `epic: ACME-7-01` and `inherits: null`.
  - `ard-reviewer` reads *"the inherited PRD-level ARD named in `inherits:`"* (`ard-reviewer.md:20`), which is null, so its BLOCKER dimension *Inherited invariants* has nothing to check against. A contradiction of the slice's `[AD#N]` passes.
  - If the run also copies the confirmed `components:` in, *Contract completeness* (`ard-reviewer.md:39`, which keys on the ARD's own `components:`) applies at Epic level.
  - `key:` and `epic:` disagree in one file.
- **Evidence:** I read the lines quoted above. The Epic-level paragraph at `:415` and the BRD inheritance block at `:513` both run on this case, with different `(prd, epic)` pairs. The frontmatter list takes the BRD pair.
- **Suggested fix:** Scope the BRD-route frontmatter, inheritance and Final-report rules to a PRD-level (slice) run. On an Epic under a slice, use the Epic-level rules: `scope: epic`, `epic: <EPIC>`, `prd: <SLICE-KEY>`, `inherits: <slice>/ard.md`, and no `components:`. Fix `ard-format.md:27` and `:36` to match. Drop the claims "the only shape this route resolves" and "every run of this route is slice-level".
- **Source:** review
- **Confidence:** high

### PRD2-ARD-B2 — MAJOR — On a BRD slice with no `prd.md`, the ordinary state, the run passes `key: null` to `emit-auto`, `emit-cost` and `commit-artifacts`, so its cost lands in a pending file; `/create-prd` passes the slice key — **Fixed in product-workflows 3.37.0 (batch B07)**
- **Where:** `plugins/product-workflows/commands/create-ard.md:910-918` (*"Phase 0 resolved a BRD key … the `key` passed to `emit-auto` and `emit-cost` below is that minted key when the folder holds a PRD carrying one, and `null` otherwise … The `<BRD-KEY>` is never passed as a `key`"*), against `commands/create-prd.md:890-891` (*"the run's `key` — which on the BRD route is the `<SLICE-KEY>` … so the write stays on that reference's primary tier instead of dropping to the unfiled one"*) and `workflows-core/references/cost-emission.md:599-606` (§9: when no PRD key resolves, the entry goes to `pending-<date>-<sid8>.md`).
- **What is wrong:**
  - The paragraph predates the container refusal. Phase 0 now resolves a `PRD-` slice key, not a BRD key, and the PRD's `key` is that slice key by construction (`.claude/rules/brd-route.md`: *"The PRD's `key` is written by `/create-prd` … set to the resolved folder's own key"*).
  - "Minted key" contradicts the one-namespace rule that nothing mints a key.
  - *"commit-artifacts resolves its own key the same way"* is not what `specs-repo-git` §4 step 4 says. That step takes the run's resolved key.
  - The same paragraph appears in `/specify` at `specify.md:1083`.
- **Failure scenario:** `/create-ard ACME-7-01` runs on a slice with no `prd.md`, which `:250` calls *"the ordinary BRD-route state"*.
  - The cost entry goes to `$SPECS_PATH/dev-workflows-cost/pending-*.md` instead of `<slice>/dev-workflows/cost/`, and a later keyed run offers to relocate it.
  - Feedback drops to the unfiled tier.
  - The session commit reads `NOISSUE`, while the preflight's run key set and the resume pointer both use the slice.
  - The same slice's `/create-prd` files its cost correctly.
- **Evidence:** I compared the three quoted passages and greped `minted key` (two hits: `create-ard.md:914` and `specify.md:1083`).
- **Suggested fix:** Pass the resolved `PRD-` folder's key, the slice key on this route, as `/create-prd` does. Delete the "minted key / BRD key" paragraph from both commands.
- **Source:** review
- **Confidence:** high

### PRD2-ARD-B3 — MINOR — A BRD-route refine resolves the slice's own prior ARD as read-only inherited invariants — **Fixed in product-workflows 3.37.0 (batch B07)**
- **Where:**
  - `plugins/product-workflows/commands/create-ard.md:513-524` (`prd: <parent-key>`, `epic: <SLICE-KEY>`; *"`found` → inherit those `AD#N` read-only; `unmerged` → **stop**"*);
  - `workflows-core/references/ard-resolution.md:29-31` (Epic-level collection: *"the Epic folder's `ard.md` … **plus** the PRD folder's own `ard.md`"*);
  - against `create-ard.md:593` (on a refine, a changed decision is superseded by a new `[AD#M]`).
- **What is wrong:** With `epic: <SLICE-KEY>`, `ard-resolution` collects the slice's own `ard.md`, which is the file this run is refining, as the Epic layer. It returns `found` with that ARD's decisions as `invariants`, and the command says to inherit them read-only. That conflicts with the refine rules, under which the run may supersede or withdraw its own decisions. It also means an `ard/` branch carrying this slice's own earlier ARD stops the run as `unmerged` (rows D/E), unless the preflight kept the run on that branch.
- **Failure scenario:** On a refine of a slice ARD, the grill treats the existing `[AD#2]` as an immutable inherited invariant, and a changed decision is never superseded. Or, where the earlier ARD's PR is still open and the run starts on another branch, the run stops naming the slice's own ARD branch rather than offering the refine. On the idea route, a PRD-level refine runs no inheritance read and has neither problem.
- **Evidence:** I read the resolution steps against the BRD mapping. `ard-format.md:36` expects `inherits:` to be the parent BRD's `ard.md`, which never exists, so only the slice's own file can make the status `found`.
- **Suggested fix:** On a PRD-level slice run, inherit only from the parent's `ard.md` (in practice nothing), or pass the slice as `prd` with `epic: null`. Treat the slice's own `ard.md` as `prior_ard`, never as inherited.
- **Source:** review
- **Confidence:** medium

### PRD2-ARD-B4 — MINOR — The Phase 6 array selection falls through on *Start fresh* over an ARD the default branch carries
- **Where:** `plugins/product-workflows/commands/create-ard.md:740`.
- **What is wrong:** The two branches are:
  - *"Where that set is the ARD file(s) **alone** and the ARD is new — `<default-ref>` carries none of them"* → the falling-back array;
  - *"Where the set **also** carries `grounding/…` or `decisions.md`, or the run **refined** an ARD the default branch already carries"* → the stopping array.

  A run that chose Phase 1's *"Start fresh — rewrite it; decisions already on the default branch keep their IDs"* over a merged ARD, with no grounding and no register (the idea-route ordinary case), matches neither: the ARD is not new, and the run did not "refine". A declined handoff of that rewrite leaves the merged ARD changed in the working tree, which `ard-resolution.md:95` says stops every consumer at the C rows. So the stopping array is the right one, but neither branch names it.
- **Failure scenario:** An idea-route PRD with a merged `ard.md` takes *Start fresh*. The agent picks an array by guesswork, and the falling-back label (*"the next phase does not stop on this"*) is false here.
- **Suggested fix:** Phrase the second condition as "or `<default-ref>` already carries any of the ARD files", which covers both refine and start-fresh.
- **Source:** review
- **Confidence:** high

### PRD2-ARD-B5 — MINOR — Phase 7 names `/prd-proposal <PRD>` unconditionally, and it stops on arrival in the ordinary BRD state of a slice with no `prd.md` — **Fixed in product-workflows 3.37.0 (batch B07)**
- **Where:** `plugins/product-workflows/commands/create-ard.md:866-877` (*"`/product-workflows:prd-proposal <PRD>` now prices this folder against a settled architecture … No merge wait: that command gates on `prd.md`, which this run does not write"*), against `commands/prd-proposal.md:188-194` (`PRD_PROPOSAL_NEEDS_PRD: no prd.md on any ref for <KEY>, and none in <path> either — there is nothing to estimate yet.`).
- **What is wrong:** The paragraph concedes that the command gates on `prd.md`, yet names it on every route with no test. Phase 7's own opening precondition (`:755-772`) exists to avoid "offering … a run that stops on arrival", and it tests `prd.md` for `/epics`.
- **Failure scenario:** On a slice with an ARD and no `prd.md`, the operator follows the prose and gets `PRD_PROPOSAL_NEEDS_PRD`.
- **Suggested fix:** Name `/prd-proposal` only where the PRD folder holds an authored `prd.md`, reusing the same test. Otherwise say it becomes available after `/create-prd`.
- **Source:** review
- **Confidence:** high

### PRD2-ARD-B6 — MINOR — The Epic-level array offers `/dev-workflows:design <EPIC>` without testing for the merged `specification.md` that `/design` stops without — **Fixed in product-workflows 3.37.0 (batch B07)**
- **Where:** `plugins/product-workflows/commands/create-ard.md:803` (`"Hand to Dev — /dev-workflows:design <EPIC> (Dev) <merge-clause>"`), against `plugins/dev-workflows/commands/design.md:101` (`absent` (row F) → stop: `DESIGN_NO_SPEC: no specification.md on the specs repo's default branch for <ADDRESS>`). The command itself says this at `:854-855`: *"`/dev-workflows:design` … takes over a merged `specification.md` — a file this run did not write"*.
- **What is wrong:** The Epic-level ARD is usually authored before the Epic's spec, which is the recommended next step, so the second option commonly names a run that stops on arrival.
- **Failure scenario:** `/create-ard EPIC-…-01` runs on an Epic with no spec, and the operator picks *Hand to Dev*. `/design` stops with `DESIGN_NO_SPEC`.
- **Suggested fix:** Test `<default-ref>:./<epic-folder>/specification.md`. Offer `/design` only where it is present, and otherwise drop the option, which leaves `/specify` and *Stop here*.
- **Source:** review
- **Confidence:** medium (the shared `pa` lane, `next-phase-offer/pa.md:147-148`, names the same route unconditionally)

### PRD2-ARD-B7 — MINOR — Phase 0 step 5 gauges `$REPOS_PATH` and runs `enumerate-components` before Phase 1 step 3 resolves `$REPOS_PATH`
- **Where:**
  - `plugins/product-workflows/commands/create-ard.md:229-237` (*"on a PRD-level run where `enumerate-components` … finds two or more code components in that one repository"*; *"the number of candidate repos, always"*);
  - against `:353` (*"Repos search base (`$REPOS_PATH`) — resolved, never asked. Resolve `${REPOS_PATH:-/workspace}` … carry it as `$REPOS_PATH`"*);
  - and Phase 3 step 1 (`:535`), the first listing.
- **What is wrong:** The advisory counts candidate repos and enumerates a repository's components in Phase 0. The search base is only resolved, and the "no existing directory" question only asked, two phases later. The data is read before it is set.
- **Failure scenario:** With `REPOS_PATH` unset, the agent either reads the raw variable (empty, giving zero candidate repos, so it judges a small item and recommends "an ARD may be optional"), or improvises the `/workspace` default. Both happen before the operator's answer to Phase 1 step 3.
- **Suggested fix:** Move the optionality advisory after Phase 1 step 3, or have step 5 resolve `${REPOS_PATH:-/workspace}` itself with the same rule.
- **Source:** review
- **Confidence:** medium

### PRD2-ARD-B8 — MINOR — A per-area split writes only `ard-<area>.md`, but the prior-ARD test and the pre-lint look only at `ard.md`
- **Where:**
  - `plugins/product-workflows/commands/create-ard.md:675` (*"On per-area, author one `ard-<area>.md` per area"*);
  - `:228` (*"Prior ARD. If the target `ard.md` exists → Phase 1 offers refine-vs-fresh"*);
  - `:681` (pre-lint *"against the drafted `ard.md`"*).
  - Contrast `:352` (*"copy each prior ARD file"*) and `:708` (*"review each area ARD, each with its own prior copy"*), which assume per-area priors are found.
- **What is wrong:** On a re-run of an Epic split per area, step 4 does not find the existing `ard-<area>.md` files. So:
  - there is no refine offer;
  - `prior_ard` is `none`, which turns off `ard-reviewer`'s supersession check;
  - the run can author a fresh `ard.md` beside them, and `ard-resolution.md:30` then collects all of them, with colliding `[AD#N]` series.

  Separately, the per-area files never get the structural pre-lint.
- **Suggested fix:** Have step 4 test `ard.md` and `ard-*.md`, and run Phase 4.5 on each ARD file drafted.
- **Source:** review
- **Confidence:** medium (`ard-format.md:15` says the area files sit *"beside the folder's `ard.md`"*, which may mean an `ard.md` always exists too; the command does not say so)

### PRD2-ARD-B9 — MINOR — The docs page misstates the conditions on the `/brd-split` remedy and on repository discovery
- **Where:**
  - `plugins/product-workflows/docs/commands/create-ard.md:64` (*"with that command's own two conditions stated in the offer: it gates on verified grounding findings, and it is a no-op on a ledger with no `unallocated` row"*);
  - against `commands/create-ard.md:165-171` (the two conditions are that the slicing instruction is mandatory, since *"a root is never ground"*, with `BRD_SPLIT_NEEDS_INSTRUCTION`, and the no-op), and `:851-852` (a root `/brd-split` *"skips that gate entirely"*).
  - Also docs `:66` (*"Repo discovery starts from `grounding/baselines.md` … rather than from PRD themes"*) against command `:550-556` (*"That is joined to the themes above, not substituted for them"*).
- **What is wrong:** The docs page names a grounding gate that a root run never applies, and omits the instruction requirement that actually stops it. It also says discovery replaces the PRD themes, where the command says it adds to them.
- **Failure scenario:** An operator reading the page runs `/brd-split <BRD-KEY>` with no instruction and gets `BRD_SPLIT_NEEDS_INSTRUCTION`.
- **Suggested fix:** Restate both conditions from the command's text.
- **Source:** review
- **Confidence:** high

### PRD2-ARD-B10 — NIT — Smaller disagreements between the docs page and the command or its references
- **Where:** `plugins/product-workflows/docs/commands/create-ard.md`:
  - `:82` and `:120`: *"`[AD#N]` decisions bind six downstream commands"*. The list omits `/conformance`, which `ard-resolution.md:5` and `:127` name as a consumer that traces each Rule. That makes seven.
  - `:19`: the `--enforce-model` list of pinned agents omits `workflows-core:architecture-grounder`, which `:37` and the command (`create-ard.md:369`, `:586`) dispatch.
  - `:106`: *"resolves `EPIC-008-01`'s folder one level under `specifications/`"*. A slice is an immediate subdirectory of its `BRD-` folder (`create-ard.md:157-158`), so it is two levels down.
  - `:17`: *"a BRD holds `brd/`, `grounding/`, `coverage-ledger.md` and `slices.md`"*. The command (`:129-131`) gives a root `grounding/` only as a leftover of the earlier two-level model.
- **Suggested fix:** Correct each item.
- **Source:** review
- **Confidence:** high

### PRD2-ARD-B11 — NIT — Three stops carry no stop code and are missing from Phase 8's `emit-block` classification
- **Where:**
  - `plugins/product-workflows/commands/create-ard.md:89-90` (an unplaceable unprefixed folder: *"stop, naming the folder and what it carries"*);
  - `:415` and `:524` (`ard-resolution` `status: unmerged` → *"**stop**, naming the returned `branch` and any `pr`"*);
  - against `:899` (*"The six argument-, tree- and git-shaped stops … none of them `emit-block`s"*).
  - Also `ard-resolution.md:95` (*"Any other stopping state of that gate stops the caller as `unmerged` does"*), which `/create-ard` maps nowhere. It handles only `found`, `unmerged` and `none`.
- **What is wrong:** These stops have no code for a reader or a later run to match on. They are also not in the list that says which stops skip `emit-block`, so an agent may file plugin feedback for an operator-state stop.
- **Suggested fix:** Give each a `CREATE_ARD_*` code, map `ard-resolution`'s other stopping rows explicitly, and add them to `:899`.
- **Source:** review
- **Confidence:** medium

<!-- /specify -->

### PRD2-SPEC-B1 — MAJOR — *Next Epic* loops back to Step B and Phases 3–7, skipping Phase 2.5, so the next Epic is specified and reviewed against the previous Epic's ARD — **Fixed in product-workflows 3.37.0 (batch B07)**
- **Where:** `plugins/product-workflows/commands/specify.md:1045`; Phase 2.5 at `:769`.
- **What is wrong:**
  - The loop says: *"on selection, set `focus_key` to the new Epic and loop back through Phase 2 Step B — whose *Gate the Epics first* gates it — → Phases 3–7 for it"*. Phase 2.5, which resolves the ARD with `<EPIC>` (`focus_key`), sits between Step B and Phase 3, and the loop does not re-enter it.
  - Phase 2.5's `invariants`, `components` and `contracts` therefore still hold the first Epic's resolution. That includes the first Epic's own Epic-level `ard.md`/`ard-<area>.md` decisions (`ard-resolution.md:25-27`, where Epic-level layers on top).
  - Phase 6 passes those stale invariants to `spec-reviewer` as `applicable_ard`. Phase 3 narrows by the stale `components`, and Phase 4 passes the stale `ard_paths` as `own_sources`.
- **Failure scenario:**
  - A PRD has Epics E1 and E2, and E1 has an Epic-level ARD. The operator specifies E1 from the picker and takes *Next Epic → E2*.
  - E2's spec is grilled and reviewed against E1's `AD#N`. `spec-reviewer` raises BLOCKERs for E1 decisions E2 never had to honour.
  - E2's own Epic-level ARD, if it has one, is never resolved. An `unmerged` E2 ARD is never stopped on, and E2's `AD#N` are never enforced.
- **Evidence:** `:1045` compared with the phase order at `:767-773`. Nothing else in the command re-runs `ard-resolution`: `grep -n "ard-resolution" specify.md` finds `:665`, `:769` and `:944`, and none of them is in the loop.
- **Suggested fix:** Loop through "Phase 2 Step B → Phase 2.5 → Phases 3–7", re-resolving the ARD for the new `focus_key`. Note in the loop that `applicable_ard`, `components` and `contracts` are re-derived per Epic.
- **Source:** review
- **Confidence:** high

### PRD2-SPEC-B2 — MAJOR — An existing `specification.md` (even `Published: yes`) is silently re-authored and overwritten with `Published: no`; the picker's *revise* is never defined
- **Where:**
  - `specify.md:293-295` (Phase 0 step 4 detects only `_session.md`);
  - `:561-562` (*"● done — `specification.md` exists there → shown greyed … selecting it offers *revise*"*);
  - `:624-625` (an earlier `specification.md` is read only as raw material);
  - `:878` (Phase 5 authors `specification.md` live, starting from stage 1, the header);
  - `:1007` (*"Write `specification.md` (`Published: no`)"*);
  - against `references/specification-format.md:39` (*"only a human sets `yes`"*) and `:129` (*"After `Published: yes`, IDs are contracts — never silently change/remove"*).
- **What is wrong:**
  - No phase tests for an existing `specification.md` in the feature folder, asks whether to overwrite, or archives it, as `/create-prd` does under `revisions/`.
  - The picker promises a *revise* option, which `epic-picker` also documents (`epic-picker.md:50`), but `grep -n -i revise specify.md` finds only `:562`. No phase defines what revise does.
  - A direct `/specify <EPIC-KEY>` re-run on an Epic that already has a spec offers nothing at all.
  - The run re-grills from the header, rewrites `Version: 1` and `Created`, and writes `Published: no` over the human's `yes`. Phase 5.5's pre-lint also renumbers IDs (see B7).
- **Failure scenario:**
  - A spec has been merged and marked `Published: yes` by a human, and `/design` and `/implement` cite its `[U03]/[AC02]/[TC01]`.
  - Someone re-runs `/specify <EPIC>` to add one criterion, or picks the ● row.
  - The run authors a fresh `specification.md`, resets `Published: no`, and may renumber the contracted IDs. The handoff then opens a PR replacing the published spec.
- **Evidence:** the greps and lines above. Phase 0 step 4 and Phase 1 step 2 handle a prior `_session.md` only.
- **Suggested fix:**
  - Add a Phase 0/1 existing-spec branch. Offer to revise in place (keep the header's `Published`/`Created`, bump `Version`, never renumber a published ID) or to start fresh, archiving the old spec.
  - Define the picker's *revise* as that branch.
- **Source:** review
- **Confidence:** high (the overwrite path); medium (how much a live grill would preserve by reading the old file as material)

### PRD2-SPEC-B3 — MINOR — On a BRD-route Epic run, Phase 2.5 passes `epic: <SLICE-KEY>`, so the Epic's own ARD is never resolved; the claim that "the route resolves a slice and nothing else" is false — **Fixed in product-workflows 3.37.0 (batch B07)**
- **Where:**
  - `specify.md:769` (*"On the BRD route the pair comes from `brd-link.md`'s `parent:` … the route resolves a slice and nothing else (Phase 0 step 0), so the `parent:` is always there — pass `prd: <parent-key>`, `epic: <SLICE-KEY>`"*);
  - against `:41-43` and `:259-271` (an `EPIC-` folder inside a slice **is** on the BRD route, addressed directly or set by the picker);
  - `:1187` (*"every run of this route is slice-level"*);
  - `docs/commands/specify.md:87` (*"the route resolves a slice and nothing else"*).
- **What is wrong:**
  - On the BRD route with `focus_key` set, the pair still names the slice as the Epic. `ard-resolution` step 2 therefore collects the slice's `ard.md` (and the container's, which never holds one) and never the `EPIC-` folder's `ard.md`/`ard-<area>.md`.
  - Those Epic-level ARDs are exactly what `/create-ard <EPIC-KEY>` writes. Their `AD#N` never reach the grill or `spec-reviewer`, and an `unmerged` Epic ARD is never stopped on.
  - The Final report then states the run was slice-level.
- **Failure scenario:**
  - A slice holds `EPIC-X`, and `/create-ard EPIC-X` wrote `EPIC-X/ard.md` with `[AD#3]`.
  - `/specify EPIC-X` runs on the BRD route (step 3's look-one-level-up) and resolves `(parent, slice)`.
  - The spec is reviewed with no `[AD#3]`. A criterion violating it passes, where on the idea route it would BLOCK.
- **Evidence:** I read the lines above and `ard-resolution.md:24-27` (Epic-level collects the Epic folder's ARD). `/create-ard` carries the same mapping at `create-ard.md:517-518`; that is outside this part, so it is noted only.
- **Suggested fix:** On the BRD route with `focus_key` set, pass a triple, or have `ard-resolution` collect three levels: the Epic folder's ARDs plus the slice's `ard.md` as the PRD-level base. Fix the "nothing else" and "every run of this route is slice-level" sentences in the command and on the docs page.
- **Source:** review
- **Confidence:** medium (the exact `ard-resolution` semantics for a three-level stack are not specified anywhere, which is itself the gap)

### PRD2-SPEC-B4 — MINOR — The `### Next step` routes by what the address resolved, so a picker-chosen per-Epic spec is told to run `/epics <PRD>` rather than `/design <EPIC>` — **Fixed in product-workflows 3.37.0 (batch B07)**
- **Where:** `specify.md:1200` (*"**Epic-level spec** (the address resolved an `EPIC-` folder) → … `/dev-workflows:design <EPIC>` …; **PRD-level spec** (the address resolved a `PRD-` folder) → `/product-workflows:epics <PRD>`"*); also `:1208-1209`.
- **What is wrong:** Phase 2 Step A re-points a PRD address to an Epic (single-Epic auto-select, or a picker selection; `:547-571`, `:601-606`), and the spec written is then per-Epic. The Next step tests the *address*, not `focus_key`, so it classifies that run as PRD-level.
- **Failure scenario:**
  - `/specify ACME-7` runs on a PRD whose only Epic is auto-selected. The spec lands in `EPIC-…/`.
  - The report recommends `/product-workflows:epics ACME-7`, which re-refines the Epics, and never names `/dev-workflows:design <EPIC>`, the actual next phase.
- **Evidence:** `:1200` compared with `:547-549` and `:1007`. The *Next Epic* offer (`:1041`) covers only the ≥2-Epic picker, and only for the sibling.
- **Suggested fix:** Key the Next step on `focus_key` (set → Epic-level, null → PRD-level), not on what the address resolved.
- **Source:** review
- **Confidence:** high

### PRD2-SPEC-B5 — MINOR — Phase 0 resolves the address in step 1 before step 2 checks `$SPECS_PATH`, against its own "resolve only after `$SPECS_PATH` is settled" paragraph, and maps no `status: invalid`
- **Where:**
  - `specify.md:141-142` (step 1: *"resolve it with `resolve-address`"*);
  - `:190-194` (*"**Resolve the address only after `$SPECS_PATH` is settled.** … this command resolves **once**"*);
  - `:209-213` (step 2, the `$SPECS_PATH` check, comes after step 1);
  - `:186-188` (`SPECIFY_NEEDS_KEY` only for "no positional address").
- **What is wrong:**
  - Two live instructions disagree on order. Executed in number order, step 1 resolves with `$SPECS_PATH` unset; `addressing.md:269` makes that `read-key` → `needs-tree` → `status: invalid`.
  - No branch of `/specify` maps `status: invalid`: `grep -n "invalid\|needs-tree\|read-key" specify.md` finds no mapping.
  - A malformed key (`acme-7`) with the variable set reaches the same unmapped status.
  - PRD-B2's related bullet says `/specify` "map[s] only `invalid`". In fact it maps neither `invalid` nor `needs-tree`, and does not call `read-key` at all.
- **Failure scenario:**
  - With `$SPECS_PATH` unset, `/specify ACME-7` resolves to `invalid`. There is no stop for that, and step 2 then asks for the path.
  - Because the command "resolves once", the run proceeds on a stale non-`found` record to the `SPECIFY_BRD_NOT_FOUND` stop (if the agent treats it as absent), which blames the address.
  - A malformed key gets no grammar stop and no `key-summary`, unlike `/create-prd`'s.
- **Evidence:** the lines above; `addressing.md:249` (`specs-root-check` runs only "where `$SPECS_PATH` is set") and `:269`.
- **Suggested fix:**
  - Move step 2 ahead of step 1, or put step 1's resolution after it.
  - Map `invalid` to a `SPECIFY_NEEDS_KEY`-style grammar stop with `key-summary`, as `/create-prd` step 1 does. Map `needs-tree` to the `$SPECS_PATH` stop and re-read.
  - Define the stop text.
- **Source:** review (extends PRD-B2's related bullet, which misstates `/specify`'s mapping)
- **Confidence:** high

### PRD2-SPEC-B6 — MINOR — On a BRD slice with no `prd.md`, `/specify` passes key `null` to `emit-cost`/`emit-auto`, so the run's cost goes to pending although its folder exists; the paragraph still says "Phase 0 resolved a BRD key" — **Fixed in product-workflows 3.37.0 (batch B07)**
- **Where:** `specify.md:1079-1087`.
- **What is wrong:**
  - The paragraph says *"Phase 0 resolved a BRD key … Any tracker identity for this work, if one exists at all, is the `key` in the PRD this BRD folder holds — glob the BRD folder's `prd.md` … that minted key when the folder holds a PRD carrying one, and `null` otherwise"*.
  - Since Phase 0 step 0, the route resolves a `PRD-` slice, whose own key is the PRD's key (`prd-format`: `/create-prd` writes the folder's key). The key `emit-cost` takes is the folder key, which tier 1 resolves to `<PRD-dir>` (`cost-emission.md:562-563`); it is not a "tracker identity".
  - The CLAUDE.md *One key namespace* constraint puts tracker identity in `workitem_key`.
  - With `null`, `cost-emission` §8 tier 2 falls to **pending** (`:568`).
- **Failure scenario:** `/specify <SLICE-KEY>` runs on a slice with no `prd.md` (the case this command calls ordinary on the BRD route, `:528`). The cost entry is written to `$SPECS_PATH/dev-workflows-cost/pending-…` instead of `<slice>/dev-workflows/cost/`, and waits for some later keyed run to offer relocation. The resume pointer and feedback similarly lose their folder.
- **Evidence:** `cost-emission.md:562-568`, `:606-615`; the quoted paragraph. `create-ard.md:910-913` carries the same text (outside this part).
- **Suggested fix:** Pass the resolved `prd_dir`'s own `key` on every route, and delete the tracker-identity paragraph.
- **Source:** review
- **Confidence:** medium (whether `emit-cost` would otherwise resolve the folder from `null` is not stated; §8 tier 1 needs a key)

### PRD2-SPEC-B7 — MINOR — Phase 5.5 lets pre-lint renumber any duplicate ID, where `pre-lint` restricts that to one this run introduced
- **Where:** `specify.md:956` (*"inline-fix the mechanical ones (renumber a duplicate `[Uxx]`/`[ACxx]`/`[TCxx]` …)"*), against `workflows-core/references/pre-lint.md:13-14` (*"renumber a duplicate ID this run introduced, never one the artifact already carried"*).
- **What is wrong:** These are two live instructions with different scope. On a re-run over an existing spec (B2), `/specify`'s wording licenses renumbering IDs the artifact already carried, which become contracts after `Published: yes` (`specification-format.md:129`).
- **Failure scenario:** A spec edited by hand holds two `[TC02]` under one AC. A `/specify` re-run's pre-lint renumbers the downstream TCs that `/implement`'s tests already cite.
- **Evidence:** the quoted lines.
- **Suggested fix:** Add "this run introduced, never one the artifact already carried" to `:956`, or cite pre-lint's rule rather than restating it.
- **Source:** review
- **Confidence:** high

### PRD2-SPEC-B8 — MINOR — The commercial step names `/prd-proposal` and "tier 4" on a BRD slice without testing for `prd.md`, though that command stops without one — **Fixed in product-workflows 3.37.0 (batch B07)**
- **Where:** `specify.md:1261-1274`.
- **What is wrong:**
  - The step says: *"On the BRD route, where verified grounding and a settled register already exist and an `ard.md` is already in place, this specification takes the folder to tier 4 … **`/product-workflows:prd-proposal <PRD>` prices it at the tightest range the format allows** … No merge wait: that command gates on `prd.md`, which this run does not write."*
  - `proposal-format.md` §5's tiers are cumulative from tier 1, *"Reached when the resolved folder holds `prd.md`"*.
  - `/prd-proposal` stops with `PRD_PROPOSAL_NEEDS_PRD` where no `prd.md` exists (`prd-proposal.md:188-193`).
  - `/specify` itself treats a slice with no `prd.md` as the ordinary BRD-route state (`:526-529`, `:1204-1206`), and elsewhere refuses to offer a run that stops on arrival (`:581-587`, `:1213-1215`).
- **Failure scenario:** On a ground, interviewed, architected slice with no PRD yet, `/specify` tells the operator the folder is at tier 4 and recommends `/prd-proposal`, which stops at once.
- **Evidence:** the lines above.
- **Suggested fix:** Apply the same `prd.md` test the `/epics` offer uses. Where it fails, say the proposal waits on the PRD (named per the slice-gate table), and drop the tier-4 claim.
- **Source:** review
- **Confidence:** high

### PRD2-SPEC-B9 — NIT — On the BRD route, the handoff always declares `<prd_dir>/decisions.md`, even where the slice holds none, so §4.1 reports a false *declaration unaccounted for* — **Fixed in product-workflows 3.37.0 (batch B07)**
- **Where:** `specify.md:1037` (*"and, additionally on the BRD route, `<prd_dir>/decisions.md`"*, unconditional), against `:334-336` (no `decisions.md` is an ordinary, non-stopping state) and `phase-handoff.md` §2.3 step 4 (a declared path nothing wrote and `HEAD` lacks is *"named in §4.1's *declaration unaccounted for* clause"*).
- **What is wrong:** The grounding files are declared only *"wherever `prd_dir` holds `grounding/`"*, but the register is declared unconditionally. A slice nobody has interviewed holds no register, so the declaration names a file that does not exist.
- **Failure scenario:** `/specify <SLICE>` runs on a ground but un-interviewed slice. The `Phase handoff:` line reports `decisions.md` as declared but not on the branch, which suggests a lost write.
- **Suggested fix:** Declare `decisions.md` only where the folder holds one (or only where a stamp was written).
- **Source:** review
- **Confidence:** medium

### PRD2-SPEC-B10 — NIT — The docs page's BRD-route example puts a slice "one level under `specifications/`", and its `--enforce-model` list omits `architecture-grounder`
- **Where:**
  - `docs/commands/specify.md:120` (*"The run resolves `EPIC-008-01`'s folder one level under `specifications/`"*), against `workflows-core/references/addressing.md` §6 (`specifications/BRD-<PARENT>-<slug>/PRD-<CHILD>-<slug>/`, so a slice is two levels down);
  - `docs/commands/specify.md:29` (the agents `--enforce-model` pins: docs-grounder, code-scanner, spec-reviewer, impl-maintenance and defect-reporter), against `:58` and command `:470` (`architecture-grounder` is dispatched on `review_model`, which §10 overrides).
- **What is wrong:** Each states a fact the tree contradicts.
- **Suggested fix:** Change it to "two levels under `specifications/`, inside its parent BRD", and add `architecture-grounder` to the list.
- **Source:** review
- **Confidence:** high

<!-- /prd-proposal and /brd-proposal -->

### PRD2-PROP-B1 — MINOR — Tier 2's "settled register" is met by a register `/create-prd` created holding only open `[AS#n]`, the vacuous case §5 says its presence test exists to prevent
- **Where:**
  - `plugins/product-workflows/commands/prd-proposal.md:391-397` (*"a settled register is `decisions.md` present, and every `interview/round-<N>.md` it names settled … Test the presence first and do not collapse the two"*);
  - `references/proposal-format.md:149-155` (*"The presence half is not redundant: a folder holding no register at all names no round, so a condition worded only as every round is settled is vacuously true there"*);
  - `references/proposal-format.md:206-210` (*"every other write into one — `commands/create-prd.md`'s `[AS#n]` for a customer-authority gap, which may create the file …"*);
  - `commands/create-prd.md:792` (*"a new `[AS#n]` for a customer-authority gap … which creates a"* register);
  - `agents/proposal-reviewer.md:155-159` (check 6 re-grades with the same two-part test).
- **What is wrong:** The presence test was added so that tier 2 cannot be granted on grounding alone. It does not close that gap. The BRD route reaches `/create-prd` before any interview: `/create-prd` treats a missing `decisions.md` as the ordinary case and goes on. On a customer-authority gap, `/create-prd` then creates `decisions.md` holding only an open `[AS#n]`, with no round. That file is "present", and because it names no round, "every round it names is settled" is vacuously true. The folder therefore grades tier 2 with no decision settled at all. Check 6 applies the same test, so it confirms the grade.
- **Failure scenario:**
  1. A slice is ground, allocated by `/brd-split`, and not yet interviewed.
  2. `/create-prd` writes `prd.md` and an `[AS#n]` into a new `decisions.md`.
  3. `/prd-proposal` grades the slice tier 2 · Grounded with a Medium ceiling and renders the brief, whose floor is meant to withhold it until the drivers are known.
  4. The customer receives a "Grounded" document whose register holds only open assumptions.
- **Evidence:** I read the lines above. `create-prd.md:792` confirms the register can be created by that command. No settledness rule in `proposal-format` §5 or `brd-package`'s test requires the register to hold at least one decided `[VD#n]`/`[CD#n]` or one round.
- **Suggested fix:** Define the settled half as "`decisions.md` present, naming at least one `interview/round-<N>.md`, and every round it names settled". Alternatively, require at least one `status: decided` `[VD#n]`/`[CD#n]`. Apply the same wording in §5, prd-proposal Phase 3 and reviewer check 6.
- **Source:** review
- **Confidence:** medium

### PRD2-PROP-B2 — MINOR — `/brd-proposal` Phase 7 classifies coverage from "Phase 3's membership list", missing a slice that Phase 6 step 1 excluded
- **Where:**
  - `plugins/product-workflows/commands/brd-proposal.md:592-595` (*"Which slices count as included is this run's own input to that, and it is Phase 3's decision … Carry Phase 3's membership list into the classification"*);
  - against `:521-530` (Phase 6 step 1's exclusion *"would reach the coverage statement Phase 7 computes … it is named in the final report and enumerated in the coverage statement"*) and `:647-649` (stamp `--excluded` *"in the walk, and in Phase 6 step 1"*).
- **What is wrong:** Phase 6 step 1 can exclude a slice after the walk, when the slice's figures cannot be read. The command states that this exclusion reaches the coverage statement and the stamp. Phase 7, however, tells the agent to carry *Phase 3's* membership list, which still counts that slice as included.
- **Failure scenario:** A slice's `proposal.md` has an unreadable section 6, and the operator answers *Exclude it* at Phase 6 step 1. Phase 7 classifies that slice's `covered-by` rows as "covered by an included slice, and therefore priced". The coverage proportion overstates what is priced, and the excluded slice's requirements are not enumerated as unpriced. Reviewer check 9 re-derives coverage from its own reading and may catch this; if it does not, the error reaches the customer.
- **Evidence:** I compared the three passages quoted.
- **Suggested fix:** Have Phase 7 carry "the membership list as Phase 3 and Phase 6 step 1 left it".
- **Source:** review
- **Confidence:** high

### PRD2-PROP-B3 — MINOR — `proposal-reviewer` check 6 has no umbrella form, so an umbrella's tier claim and its brief floor are checked by nothing, or checked wrongly
- **Where:**
  - `plugins/product-workflows/agents/proposal-reviewer.md:152-163` (check 6 re-grades "the folder" against §5's ladder: `decisions.md`, `ard.md`, `specification.md`);
  - `:314-319` (*"check 6 re-grades against `proposal-format.md` §5, which grades no umbrella off its ladder at all"*);
  - `:271-282` (the `passes:` block, which gives check 6 no `N/A` form);
  - `commands/brd-proposal.md:697-701`;
  - `references/proposal-format.md:160-163` and `§14` (an umbrella's tier is the minimum of its included slices' tiers).
- **What is wrong:** On a `BRD-` folder the reviewer is told that check 6 delegates to a ladder that grades no umbrella. It is not told what to check instead (the minimum over the included slices, the printed mix, and the brief floor read against that minimum), and it is not told to report check 6 as `N/A`. Read literally, check 6 re-grades the container itself, which holds no `prd.md`, `ard.md` or `specification.md`.
- **Failure scenario:** Either way, the umbrella's tier honesty goes unchecked:
  - The reviewer finds no rule it can apply and either skips check 6, which contradicts *"NEVER skip a check silently"*, or files a spurious tier BLOCKER.
  - Where an umbrella prints tier 3 while one included slice's proposal carries tier 1, check 6 does not catch it. The brief, which §14 says must be withheld, passes as well.
- **Evidence:** I read the lines above. `grep -n "minimum" agents/proposal-reviewer.md` finds only check 2's umbrella bullet context and nothing in check 6.
- **Suggested fix:** Add an umbrella bullet to check 6, using the same folder-kind test as check 9: read each included slice's header tier, confirm that the printed tier is their minimum and that the mix is printed, and apply the brief floor against that minimum.
- **Source:** review
- **Confidence:** medium

### PRD2-PROP-B4 — MINOR — The proposal pair reads a legacy `<KEY>_*.md` PRD "through `addressing` §5's legacy fallback", which §5 says covers folder names only, with no command carrying a filename fallback
- **Where:**
  - `plugins/product-workflows/commands/prd-proposal.md:180-181` (*"`prd.md` on a current tree, a `<KEY>_*.md` entry only through `workflows-core:addressing` §5's legacy fallback"*);
  - `references/proposal-format.md:533` (*"or, where none exists, the `<KEY>_<slug>.md` PRD `workflows-core:addressing` §5's legacy fallback accepts"*);
  - `scripts/proposal-record.py:859-864` and `:55` (`LEGACY_PRD_RE`);
  - against `plugins/workflows-core/references/addressing.md:683-688` (*"The fallback covers the folder name and nothing inside it … Every command resolves an artifact by its current name and none carries a fallback of its own, so a folder written before the artifact filenames lost their keys still needs its `<KEY>_<slug>.md` renamed to `prd.md`"*).
- **What is wrong:** These are two live, contradictory instructions:
  - The proposal pair carries a filename fallback and attributes it to a section that disclaims one.
  - `addressing` says no command carries such a fallback.
  - Inside `/prd-proposal` itself, Phase 0's row-F split tests only for `prd.md` (*"no prd.md on any ref … and none in <path>"*, `:193`), and Phases 3–7 read `prd.md`. A legacy-named PRD can therefore pass the gate under one name and then be missing under the other.
- **Also:** `LEGACY_PRD_RE` (`[A-Z][A-Z0-9_]*(?:-\d+)+_[^/]*\.md`) also matches `<KEY>_ARD.md`. Such a folder records its ARD as a PRD input too.
- **Failure scenario:** A legacy folder holds `PROD-7_checkout.md` and no `prd.md`. Two outcomes are possible:
  - The run gates the legacy file and then prices a folder whose `prd.md` does not exist.
  - The run follows `addressing` and stops with `PRD_PROPOSAL_NEEDS_PRD`, while the script records the legacy file as the priced PRD.
  Which one happens depends on which reference the agent trusts.
- **Evidence:** I read the quoted lines. `slice_inputs` implements the fallback.
- **Suggested fix:** Drop the fallback from the pair (command, §15.1 and script) so it matches `addressing` §5, which tells users to rename the file. Alternatively, amend `addressing` §5 to name this one exception, and make Phases 0–7 use the resolved name throughout.
- **Source:** review
- **Confidence:** medium

### PRD2-PROP-B5 — NIT — The `/prd-proposal` docs example says the tier-2 next-step array offers `/create-ard` "first"; the command's array puts it third
- **Where:** `plugins/product-workflows/docs/commands/prd-proposal.md:92` (*"Its next-step array offers `/product-workflows:create-ard PRODUCT-1234-01` first"*), against `commands/prd-proposal.md:714`.
- **What is wrong:** The tier-2 array is `["Stop here …", "Roll it into the programme umbrella …", "Raise the tier first — /product-workflows:create-ard <KEY> …", "Price the next sibling slice …"]`. The example is a BRD slice, so it has a parent and the umbrella option stays. `/create-ard` is therefore the third option, and it is not marked Recommended.
- **Failure scenario:** A reader expects a different menu from the one the run presents verbatim.
- **Evidence:** I compared the two lines.
- **Suggested fix:** Change "first" to "among its options", or say that it is the tier-raising option.
- **Source:** review
- **Confidence:** high

### PRD2-PROP-B6 — NIT — A folder holding a `proposal-brief.md` but no `proposal.md` counts as a revision, so the run looks for an anchor and archives a proposal that do not exist
- **Where:** `plugins/product-workflows/commands/prd-proposal.md:239-241` (*"whether `proposal.md` and `proposal-brief.md` already exist … Where either does, Phase 6 treats the prior as the anchor (§8) unless `--redo` was given, Phase 7 archives it (§2), and §4's section 23 renders (§12)"*); the same wording is at `commands/brd-proposal.md:161-163`.
- **What is wrong:** "Either" makes a leftover brief alone enough to start the stability anchor, the proposal archive and the changelog section. All three need a prior `proposal.md`.
- **Failure scenario:** A brief is left after a hand-deleted `proposal.md`. The run:
  - passes `Anchor revision:` with no file behind it;
  - renders a section 23 changelog against nothing;
  - may file a check-3 finding against an anchor that does not exist.
- **Evidence:** I read the lines above.
- **Suggested fix:** Key the anchor, the proposal archive and section 23 on `proposal.md`, and the brief archive on `proposal-brief.md`.
- **Source:** review
- **Confidence:** low (the state needs a hand deletion)

## product-workflows — BRD route

### BRD-B1 — MINOR — `/brd-package`'s docs page still says every `fixed` correction changes what the customer is shown (the copy 0e02e28b missed)
- **Where:** `plugins/product-workflows/docs/commands/brd-package.md:298-299`
- **What is wrong:** The docs page says: "**Phase 4 — a `fixed` correction re-opens the review, exactly once, whatever artifact it named.** The correction changes what the customer will be shown, and one made under one finding can break a position another left standing". Commit 0e02e28b corrected this same claim in the command (`commands/brd-package.md:817-820`). The command now says "A correction **can** change what the customer will be shown — three of the five artifacts the row above admits, the prompt, the delivery note and the bundle's own rendered copies, are what this command renders for them". A `fixed` against the self-review or a `[SR#n]`'s own record changes nothing rendered for the customer.
- **Failure scenario:** An operator disposes a finding `fixed` against `self-review-<date>.md`. The page tells them the correction changes what the customer is shown, which is false. The command's own CHANGELOG 3.36.1 bullet calls the old wording a defect. This is the claim-sweep refinement-8 case: the `docs/` copy is the one a person acts on.
- **Evidence:** `git show 0e02e28b --stat` touches only `CHANGELOG.md`, `commands/brd-package.md` and `references/bundle-packaging.md`. The docs page line 299 is unchanged since b4ab29c7.
- **Suggested fix:** Change the line to "A correction can change what the customer is shown — the prompt, the delivery note and the bundle's rendered copies — and one made under one finding can break a position another left standing". Keep "whatever artifact it named" as the trigger.
- **Source:** review (claim sweep of 0e02e28b)
- **Confidence:** high

### BRD-B2 — MINOR — `/prd-ground` Phase 10's *Ground another declared prerequisite first* names no command, no key and no action, and grounding a prerequisite is not what moves this run's horizons
- **Where:** `plugins/product-workflows/commands/prd-ground.md:2206`, `:2216`; the selection rule is at `:2161-2167`; Phase 4 is at `:910-961`.
- **What is wrong:** 8i (6bcdf13f) narrowed the option so it is offered only where a prerequisite is declared. The option is still a bare label: `"Ground another declared prerequisite first"`. Nothing in Phase 10 says what a run does on that answer: which prerequisite, which command, or which key form. Phase 4 and Phase 6 also take a prerequisite's effect only from its **frozen** `decisions.md` records (`status: decided`, `:925-935`). Grounding a prerequisite produces no frozen decision, so the option does not change what it implies it changes. Phase 4's own example keys are also `EPIC-` keys (`:946-947`: `prerequisites: EPIC-008-01 — …`), and `/prd-ground` refuses those outright (`PRD_GROUND_EPIC_LEVEL`, `:182`).
- **Failure scenario:** A slice declares `--depends-on` on a sibling. The operator picks the option. The orchestrator has no instruction, so it either improvises `/prd-ground <PREREQ-KEY>` (an Opus-heavy run that cannot move this slice's `will-change` horizons) or ends the run without a next step.
- **Evidence:** `grep -n "Ground another" plugins/*/commands/*.md plugins/workflows-core/references/*.md` finds only the selection sentence and the two arrays. No prose handles the answer. The option predates the window (`git show 640e5024:…/prd-ground.md:1817`), and 8i edited its condition without giving it an action.
- **Suggested fix:** Either drop the option, or make it actionable. The actionable form names the step that actually moves a horizon: `/product-workflows:brd-interview <PREREQ-KEY>` (or that slice's route to frozen decisions), with the key, offered per declared prerequisite that is not `decisions frozen`. Phase 10 should then say what the run prints on that answer. Fix Phase 4's example keys to `PRD-` slice keys.
- **Source:** review
- **Confidence:** medium

### BRD-B3 — NIT — `/prd-ground` Phase 9 names `brd-link.md` unconditionally on a full run, against its own "never name an unchanged path" rule
- **Where:** `plugins/product-workflows/commands/prd-ground.md:2052-2061`
- **What is wrong:** The `route: brd` `deliverable_paths` list `brd-link.md` with no condition on a full run. The `--no-code` set takes it only "where Phase 4 persisted a prerequisite", and justifies that with "naming an unchanged path in a handoff is how a commit comes to claim work it did not do". Phase 4 changes `brd-link.md` only when `--depends-on` adds a key (`:912-916`), so a full run with no `--depends-on` names a path it did not change. The two modes apply different rules to the same file, and the paragraph's stated reason contradicts the full-mode list.
- **Failure scenario:** No data loss: staging an unchanged file is a no-op. Body facts or a reviewer reading the handoff list will say `brd-link.md` was handed off when nothing in it moved. This is low impact.
- **Evidence:** I read `:2052-2061` against Phase 4 at `:912-916`.
- **Suggested fix:** Make `brd-link.md` conditional in both modes ("where Phase 4 persisted a prerequisite").
- **Source:** review
- **Confidence:** medium

## product-workflows — BRD route (second pass)

### BRD2-B1 — MINOR — `/brd-interview`'s `[V]` picker is described two contradictory ways, one sentence apart
- **Where:** `plugins/product-workflows/commands/brd-interview.md:1490-1492` against `:1495-1500`
- **What is wrong:** The lead-in to the array says: "The options presented are that question's own `options_considered` …, with one trailing entry for an option the operator supplies themselves and the two standing exits". That describes an "own option" entry plus two exits, Defer and Cancel. The array that follows it, and the two paragraphs under it, say the opposite:
  - "The entries are two options at most, plus the defer entry: three, never four";
  - "There is no listed `Cancel` and no listed free-text entry";
  - "an authored `Another option from the list above` both duplicated it and spent a slot".
- **Failure scenario:** An orchestrator follows the lead-in and appends an "own option" entry and a Cancel to a question that weighed two options. That makes five entries, which `AskUserQuestion` cannot render (`maxItems: 4`). The added text-carrying "Other"-style entry is also one that `escalation-rules` §0 forbids. On a question that weighed one option it renders four entries, against the paragraph's own "three, never four".
- **Evidence:** Lines 1490–1500 read together. `git log -S"two standing exits"` shows the sentence predates the rename (`7b47f23b`), and it survived the later rewrite of the array beneath it.
- **Suggested fix:** Replace the lead-in with: "…its own `options_considered`, at most two of them as entries, and the defer entry."
- **Source:** review
- **Confidence:** high

### BRD2-B2 — MINOR — The `/brd-split` docs table gives the `allocate-only` bulk offer the firing condition the command calls a defect
- **Where:** `plugins/product-workflows/docs/commands/brd-split.md:174`; the command is at `plugins/product-workflows/commands/brd-split.md:743`
- **What is wrong:** The docs table says that on `allocate-only`, Step 1 "fires whenever ≥2 rows are unallocated". The command's condition is "two or more rows are in the set this step would actually offer — every row still `unallocated`, *minus* any row Phase 1.5's reading already placed on a different disposition". It then names the raw-count reading as the shipped defect: "Counting the raw `unallocated` set instead fires the offer on a set of one or zero … the degenerate prompt the rule below says is skipped".
- **Failure scenario:** On a slice with five unallocated rows and the instruction "defer everything except the login flow", an operator reading the page expects a bulk `covered-here` offer. The command correctly skips it, because only one row is offerable. The page describes the defect that was fixed, so the operator meets a different behaviour from the one documented. The page's own intro (`:10`, "and offerable") already has it right; the table contradicts the intro.
- **Evidence:** I compared docs `:10`, docs `:174` and command `:741-743`.
- **Suggested fix:** Change the table cell to "fires where ≥2 rows are still `unallocated` and not placed on another disposition by the instruction".
- **Source:** review
- **Confidence:** high

### BRD2-B3 — MINOR — The `/brd-split` docs page's "No-op … with two exceptions" drops the third exception, a child out of step
- **Where:** `plugins/product-workflows/docs/commands/brd-split.md:544-548`; the command is at `commands/brd-split.md:395-412`
- **What is wrong:** The page says: "Re-running `/brd-split` once every row already has a disposition changes nothing **unless** a child is standing empty … **or** the run was given an instruction that found a re-cuttable row … A **bare** re-run … with no child standing empty … reports the ledger line and stops." The command's step 10 has three parts. It is a no-op only with "no standing empty child **and** no child out of step", and otherwise it takes the reconcile path, where Step 3 rewrites the child's `claims:`, inventory and ledger. The same page states this correctly at `:226-238`.
- **Failure scenario:** `/prd-ground` stops with `PRD_GROUND_SLICE_UNRECONCILED` and names a bare `/brd-split <PARENT-KEY>` as the fix. An operator reading the Gates section is told that run changes nothing and stops, so they doubt the remedy or skip it. The run in fact writes the child's files and opens a pull request.
- **Evidence:** I compared docs `:544-548` against docs `:226-238` and command step 10.
- **Suggested fix:** Add "or a child is out of step with this ledger, in which case Step 3 reconciles it (the reconcile path)". Also change "with no child standing empty" to "with no child standing empty or out of step".
- **Source:** review (claim-sweep refinement 8: the docs copy is the one acted on)
- **Confidence:** high

### BRD2-B4 — MINOR — The `/brd-split` docs page says a slice block's rationale is "the buildable / blocked / depends-on reading", a grounded-root concept the command retired
- **Where:** `plugins/product-workflows/docs/commands/brd-split.md:362-364`; the command is at `commands/brd-split.md:1289-1291`
- **What is wrong:** The docs say `slices.md` gives "one block per confirmed slice (its key, its folder, and the rationale that grouped its rows: the buildable / blocked / depends-on reading, or, for a group a slicing instruction placed, what in the instruction placed it)". The command's Phase 5 has one rationale only: "what in the instruction placed it". A root is never ground and carries no findings (command Phase 2, `:539`; docs `:84-88`: "In `full` mode the instruction is the whole picture"), so there is no buildable/blocked/depends-on reading to record.
- **Failure scenario:** A reader of `slices.md`, or an agent writing it from the docs, looks for or invents a grounding-based rationale on a root that has no findings.
- **Evidence:** `grep -n "buildable\|blocked / depends" plugins/product-workflows` finds only this docs line.
- **Suggested fix:** Drop the first alternative and keep "what in the instruction placed it".
- **Source:** review
- **Confidence:** high

### BRD2-B5 — MINOR — The will-change picker's `conditional_on: <BRD-KEY>/<decision-id>` collides with the command's own `<BRD-KEY>` placeholder
- **Where:** `plugins/product-workflows/commands/brd-interview.md:1743`; the intended value is at `:1754`
- **What is wrong:** Everywhere in this command, `<BRD-KEY>` is the run's own slice key, which the orchestrator substitutes into every array (for example `:2201`, `/product-workflows:brd-package <BRD-KEY>`). In this one option, `"Make it explicitly conditional on the prerequisite — conditional_on: <BRD-KEY>/<decision-id>"`, it must instead be the **prerequisite's** key: "a `conditional_on` naming one specific decision of the prerequisite (`EPIC-008/[VD#3]` …)".
- **Failure scenario:** A run substitutes its own key the way it does in every other array. The operator is then shown, and the record may then carry, `conditional_on: <this slice>/<id>`: a decision conditional on its own register. `/brd-reconcile`'s propagation sweep, which reaches a held record by that field, would never fire for the real prerequisite.
- **Evidence:** I read `:1743`, `:1754` and `:1577` against the command's uses of `<BRD-KEY>`.
- **Suggested fix:** Spell it `conditional_on: <PREREQ-KEY>/<decision-id>`, and say beside the picker that both are taken from the will-change finding's `prerequisite` field.
- **Source:** review
- **Confidence:** medium

### BRD2-B6 — MINOR — `/prd-ground` Phase 4.5's documentation-lead question has no choices array, and its "re-resolve through Phase 1, then pin through Phase 3" has no defined return path
- **Where:** `plugins/product-workflows/commands/prd-ground.md:988-992`
- **What is wrong:** The text says a lead "is surfaced now, before Phase 5 dispatches anything, with one choice: add that repository and re-resolve it through Phase 1 step 2–3 (then pin it through Phase 3 like any other), or proceed on the record". Nothing defines the array, the option strings or which option is recommended. Every other question in this command presents a verbatim array, and `escalation-rules core`, which Phase 0 loads, binds that. The detour back through Phase 1 and Phase 3 is also unspecified:
  - It does not say whether Phase 1's cost statement (K repositories) is re-printed.
  - It does not say whether Phase 3's *No two repositories share a pin* check re-runs across the whole set.
  - It does not say whether Phase 4 runs again.
- **Failure scenario:** On a run where the docs digest names a subsystem that no clone covers, the orchestrator invents option wording and recommendation. Taken "add", it re-enters Phase 3 for one repository with the K×N cost statement already printed for the old K. That understates the run's cost, which is the statement Phase 1 calls "the first output".
- **Evidence:** `grep -n "choices:" prd-ground.md` shows none between `:963` and `:1019`. The docs page (`docs/commands/prd-ground.md:467-468`) describes the lead in prose only.
- **Suggested fix:** Add a two-option array, for example `["Add that repository — it is resolved and pinned like the others (you'll be prompted for its name)", "Proceed — claims it covers land as NOT-PROVABLE"]`. Then say the run re-prints the cost statement with the new K and re-runs Phase 3's shared-pin check over the whole set before Phase 5.
- **Source:** review
- **Confidence:** medium

### BRD2-B7 — MINOR — The `/brd-interview` and `/brd-package` docs examples invoke the root key that the docs' own convention names, which both commands refuse
- **Where:**
  - `plugins/product-workflows/docs/commands/brd-interview.md:518-521` and `:549`;
  - `plugins/product-workflows/docs/commands/brd-package.md:448-451`;
  - the convention: `docs/commands/brd-split.md:556`, `:570` (root `EPIC-008`, slice `EPIC-008-01`); `references/coverage-ledger-format.md:773-774` ("A synthetic BRD `EPIC-008` … its one child `EPIC-008-01`"); and `docs/commands/brd-reconcile.md:680` and `prd-ground.md:555`, which use the slice key.
- **What is wrong:** The examples read:
  - "Work the first round of a synthetic customer BRD, once its split has merged: `/product-workflows:brd-interview EPIC-008`";
  - "Package a synthetic customer BRD … `/product-workflows:brd-package EPIC-008 --depends-on EPIC-014`".

  Both commands refuse a root (`BRD_INTERVIEW_ROOT_LEVEL`, `BRD_PACKAGE_ROOT_LEVEL`). In the family's synthetic example, `EPIC-008` is the root.
- **Failure scenario:** An operator copies the example's shape and runs the command on the parent key. The run stops at Phase 0 step 5a. The example's own wording, "a synthetic customer BRD … once its split has merged", reinforces the reading that the BRD itself is the target.
- **Evidence:** `grep -rn "EPIC-008" plugins/product-workflows/docs`. The sibling pages that run on a slice all use `EPIC-008-01`.
- **Suggested fix:** Use `EPIC-008-01` and "a slice of a synthetic customer BRD" in both pages, both `brd-interview` examples included.
- **Source:** review
- **Confidence:** medium (the key's shape does not by itself fix its level, but the page's prose and the family's example set do)

### BRD2-B8 — NIT — Agent input examples use a key the agent's caller refuses; `/brd-package` Phase 3 does not say `questions` is optional
- **Where:**
  - `plugins/product-workflows/agents/brd-package-reviewer.md:44`, `agents/customer-review-reader.md:48` (`brd_key: <BRD-KEY>  # e.g. EPIC-008`);
  - `plugins/product-workflows/commands/brd-package.md:595` (`questions: [path to interview/customer-questions.md]`).
- **What is wrong:** Both callers run on a slice only, and `EPIC-008` is the root in the family's example set (see BRD2-B7). The Phase 3 dispatch marks `defects` and `prior_reviews` "omit when …", but not `questions`. Yet Phase 0 step 6b says "a slice whose rounds held no `[C]` has no question set", and the agent lists `questions` as optional (`brd-package-reviewer.md:62`, "every input above but the three this section refuses without").
- **Failure scenario:** A dispatch hands over a path that does not exist. The agent's own text tolerates this, so the impact is cosmetic.
- **Suggested fix:** Use `EPIC-008-01` in both comments. Write `questions: [path …, or omit when the folder holds none]`.
- **Source:** review
- **Confidence:** high

### BRD2-B9 — NIT — The `/brd-split` docs "What it produces" omits `covered-here` and says "the first two of the following" about a list that sits above
- **Where:** `plugins/product-workflows/docs/commands/brd-split.md:354-356`, `:385`
- **What is wrong:**
  - Line 354: "`coverage-ledger.md` — updated so no row remains `unallocated`: each row now reads `covered-by: <SLICE-KEY>`, `deferred-to: <this BRD>`, `rejected: [DEF#n]`, or `superseded-by: [BR#n]`". On an `allocate-only` run, the ordinary landing is `covered-here`, which is missing from the list.
  - Line 385: "In `allocate-only` mode the run writes exactly the first two of the following". The two files meant, the ledger and `slices.md`, are the bullets **above** that line. The list that follows holds one bullet, the nested child folder, which a slice never writes. This is the pointer-face case in `CLAUDE.md`.
- **Suggested fix:** Add "or, on a slice, `covered-here`". Change "of the following" to "of the above".
- **Source:** review
- **Confidence:** high

### BRD2-B10 — NIT — The `/brd-intake` docs page says `/brd-interview` "gates on" the slice ledger
- **Where:** `plugins/product-workflows/docs/commands/brd-intake.md:17-22`; the command is at `commands/brd-interview.md:213-216`, `:322-326`
- **What is wrong:** The paragraph contrasts reading from the working tree with gating on "where they have been merged". It then lists "`/brd-interview` on that ledger and those findings". `/brd-interview`'s only `require-on-main` targets `grounding/code-grounding.md`. It reads `coverage-ledger.md` from the worktree, and only for an `unallocated` count (step 8).
- **Suggested fix:** Change it to "`/brd-interview` on those findings (it reads the ledger from the working tree for its allocation gate)".
- **Source:** review
- **Confidence:** medium

## product-workflows — BRD route (third pass)

### BRD3-B1 — MAJOR — A run stopped after Phase 5 wrote the register but before Phase 12 wrote the reconciliation record leaves `[CD#n]`s the re-run cannot reach, so the re-run mints a second `[CD#n]` for the same question
- **Where:** `plugins/product-workflows/commands/brd-reconcile.md:1096-1106` (`[C]` chain start), `:1114-1121` (`[SR#n]` chain start), `:1067-1091` (same-review rule), `:1441-1452` (step 1 writes the *answered by the customer* line after the mint), `:1487-1491` (a record frozen `open` for want of its reason leaves its question held, with no *answered by* line), `:2473-2516` (Phase 12, the only place a pass's `[CD#n]` list is written); `plugins/product-workflows/references/decision-register-format.md:581-582` (§8: "A `[CD#n]`" is never a torn write).
- **What is wrong:** Phase 4 finds an existing `[CD#n]` for a target in only three ways:
  - the `[CD#n]` named by the target's first *answered by the customer* line, which Phase 5 step 1 writes;
  - "where an answer to it was frozen `open` for want of its reason … that record, found where an earlier reconciliation record lists it" (`:1102-1105`);
  - for an `[SR#n]`, "the `[CD#n]` an earlier pass's reconciliation record lists as answering that `[SR#n]`" (`:1119-1121`).

  The same-review rule works only from earlier `reconciliation-<YYYYMMDD>.md` passes (`:1067-1071`). Phase 12 writes that file, after the interactive Phases 6, 10 and 11. Nothing in Phase 5 orders its writes or names a commit point. `decision-register-format.md` §8 says a `[CD#n]` "is never torn" and is never removed, so a stopped run's `[CD#n]` stays counted.
- **Failure scenario:** The run freezes `[CD#4]` answering an escalated `[SR#2]`, and `[CD#5]` (frozen `open` because the customer gave no reason) answering round 2, question 3. The session is then lost during the Phase 10 sweep pickers. The re-run reads the same review and finds no reconciliation pass listing either record:
  - `[SR#2]` "has no live record: nothing is skipped, and its answer is frozen as a new `[CD#n]` that supersedes nothing" (`:1128-1131`), so `[CD#6]` is minted.
  - The held `[C]` has no *answered by* line, by design (`:1487-1491`), so its candidate meets no live record, and the missing-reason picker mints `[CD#7]` `open`.

  The register now holds two answers to one question each. The command calls this "a contradiction one record has no way to hold" (`:1082-1083`). The same thing happens to a `decided` `[C]` answer if the stop falls inside Phase 5, between the mint and step 1's *answered by* write. `/create-prd` then reads two `decided` customer decisions for one question.
- **Evidence:** Read `:1093-1149` and `:1298-1340`, the step order at `:1439-1452`, and Phase 12 at `:2496-2516`. Grepped the command for "commit point", "torn", "interrupt" and "in this order": none applies to Phase 5's own writes. `:145-149` foresees a stop after the freeze only for the decided-and-reachable case ("a re-run would find each re-affirmed").
- **Suggested fix:** Make a freeze findable from the register itself. One way: before minting, look up a `[CD#n]` whose record names the review file and target (for example, a provenance line written into each `[CD#n]`'s statement or a dedicated field). The other way: write a pass stub to `reconciliation-<date>.md`, listing every `[CD#n]` with its target, as the first write of Phase 5, before step 1. The same-review rule and the `open`/`[SR#n]` chain starts then key on that stub.
- **Source:** review
- **Confidence:** high for the `open`-for-want-of-reason and `[SR#n]` paths (the prose names the reconciliation record as their only locator); medium for the `decided` `[C]` path, which needs a stop inside Phase 5.

### BRD3-B2 — MAJOR — A stop or interruption after Phase 5 loses the run's defect resolutions, ledger moves and sweep: the re-run reads its own frozen [CD#n] as re-affirmations
- **Where:** commands/brd-reconcile.md:689-697 (which review froze a [CD#n] lives only in the reconciliation record), :1067-1083 (same-review rule keys on a pass in an earlier reconciliation record; "Without this rule a run cancelled halfway and restarted would mint a second [CD#n]"), :1162-1185 (re-affirmation: "mints no [CD#n] ... and adds nothing to the propagation sweep's changed-id set"), :1714-1715 (BRD_RECONCILE_UNDISPOSED_CORRECTION stop at the end of Phase 6), :2347-2348 (BRD_RECONCILE_UNSWEPT stop at the end of Phase 10), :2473-2475 (the record is written only in Phase 12), :146-149 (the command already states this outcome for one case: "leaving records frozen that no reconciliation record names: a re-run would find each re-affirmed, freeze nothing, and resolve no defect for it").
- **What is wrong:** decisions.md carries no review provenance (§1's 13 fields), and the pass heading that every same-review rule keys on is written in Phase 12, after Phases 5–11 have written decisions.md, the corrections, banners, defect log, ledger and dependents. Two of the command's own gates stop between those writes and Phase 12. So does a lost session or exhausted context in the long interactive Phases 4–10.
- **Failure scenario:** Phase 5 freezes [CD#4]. Phase 6 ends with one row undisposed and stops UNDISPOSED_CORRECTION. No reconciliation record exists. The re-run on the same review finds no pass, so the candidate is shown again. On Confirm it re-affirms [CD#4]: it freezes nothing and adds nothing to the changed-id set. Then:
  - Phase 8 resolves no defect for it (the :148 sentence);
  - Phase 9 moves no ledger row for it;
  - Phase 10 sweeps no dependent for it;
  - Phase 11 searches nothing for it;
  - the record reports it as "already reconciled, re-affirmed by" this same review.
  The customer's withdrawal of a requirement, for example, never reaches the ledger or the defect log, and no report says so. :1081's promise is kept only for the duplicate mint, not for the effects.
- **Suggested fix:** make the pass heading the commit point at the start of Phase 5. Write the pass heading and the frozen ids before or with the first decisions.md write, then append the rest in Phase 12. Or have a re-run treat a live [CD#n] that the same canonicalised review's quotation produced as "frozen by an unrecorded pass", and re-enter Phases 6–11 for it. At minimum, both gate stop texts must say what was already written and what a re-run will not redo.
- **Source:** review
- **Confidence:** high on the mechanism (every sentence quoted). Medium on how reachable it is: it needs a gate stop or an interruption after Phase 5.
- **Also found independently by** sub-review C (its B2). It adds that Phases 7, 8 and 9 and the sweep each act only on records this run froze, completed or re-decided (`brd-reconcile.md:1794-1797`, `:1829`, `:1929-1931`, `:2014-2016`), so banners are lost too, and Phase 8's closing of fully-withdrawn held questions never fires.

### BRD3-B3 — MAJOR — The documented remedy for a recorded-not-written dependent cannot write anything: the re-run's changed-id set is empty for the earlier pass's ids
- **Where:** commands/brd-reconcile.md:2114-2118 (the changed-id set is what was frozen, completed, re-decided, reopened or superseded "this run"), :1067-1076 (a re-run skips the earlier pass's candidates as *already reconciled*, so they are frozen nothing this run), :2232-2239 and :2300 (a conditional_on position "this run did not move" "takes this disposition [inherited-unchanged] and no other"), :2340-2345 (the recorded-not-written dependent "is swept again in full ... the operator merges the dependent's pull request exactly so the sweep can land"), :2557-2559 (the fix named: re-run `/brd-reconcile <BRD-KEY> @<review-file>` on this same review); Phase 14 offers the same (docs/commands/brd-reconcile.md:125).
- **What is wrong:** on that re-run, every candidate of the earlier pass is skipped by the same-review rule, so the changed-id set holds none of the ids that reached the dependent. The citation pass then matches nothing. The conditional_on pass presents each position with "this run did not move it", and that case admits only inherited-unchanged. So the reopened/reverted/withdrawn dispositions that were recorded for the dependent cannot be written. Nothing says the re-run reads the dispositions the earlier pass recorded (:2328-2329 "the dispositions this run would have written").
- **Failure scenario:** dependent D's register is on an open PR, so pass 1 records "reopen D [VD#2]". The operator merges D's PR and re-runs as told. The sweep reaches D [VD#2] by conditional_on. It is told the prerequisite did not move this run, and can only take inherited-unchanged. D [VD#2] stays decided on a moved prerequisite, and the run records the sweep as landed.
- **Suggested fix:** on a re-run over the same review, seed the changed-id set with the earlier passes' changed-id sets (as recorded under *The sweeps*) for every recorded-not-written dependent, or apply the recorded intended dispositions after re-checking them.
- **Source:** review
- **Confidence:** medium-high. The re-run sentence ("swept again in full") could be read as carrying the old set, but no text supplies one.

### BRD3-B4 — MAJOR — A prerequisite's bundle is copied in "wholesale", so its own copied-in prerequisites come along under a key the partition set does not hold. The "cannot arise" collision claim is false.
- **Where:** `plugins/product-workflows/references/bundle-packaging.md:483` ("A prerequisite package is copied into the bundle wholesale (§1.1)"), `:503-507` (the partition key is "this run's key plus every prerequisite key Phase 2 carried… no candidate in the set matches" → unkeyed-document stop), `:601-606`; `plugins/product-workflows/commands/brd-package.md:548` (Phase 2 walks "every declared prerequisite (this run's plus any already on file)", which means direct ones only), `:559-560` (step 3 copies the prerequisite's "most recent `bundle-<YYYYMMDD>/`"), `:1385-1387` ("one **between two prerequisite packages**, which neither may rename, cannot arise"), `:1502-1506`.
- **What is wrong:** Slice A depends on B, and B was packaged with its own prerequisite C. B's `bundle-<date>/` therefore holds C's `C-…` documents (B's rule 5). A copies B's bundle wholesale, so the C-prefixed files enter A's bundle. C is not in A's key set, because Phase 2 carries only A's declared prerequisites. Rule 8 then finds documents whose key "no candidate in the set matches" and stops with `BRD_PACKAGE_DEAD_CITATION`. That stop's message ("some sentence in the package assumed that id or that file, and the sentence is what has to change") points the operator at prose. The real problem is a never-rewritten prerequisite copy, which they cannot change. Second case: A declares both B and C. C's own latest bundle and B's older copy of C's bundle both carry `C-decisions.md` and other C-prefixed names. That is a collision between two prerequisite packages, which rule 1 says "cannot arise" and gives no resolution for, since neither may be renamed.
- **Failure scenario:** Any prerequisite chain of length 2 (A→B→C, with B packaged after C) makes A unpackageable. The stop message names no way out. Declaring C as well only trades the dead-citation stop for an unresolvable name collision.
- **Evidence:** Read the lines above. Phase 2 has no transitive walk. Rule 5 and §1.1 do not say which files of a prerequisite bundle are copied, so the whole directory is copied, B's own prerequisite copies included. A grep for any rule on nested or transitive prerequisite copies across `commands/brd-package.md` and `references/bundle-packaging.md` returns nothing.
- **Suggested fix:** Copy only the prerequisite's own-keyed documents (those whose prefix is that prerequisite's key, its prompt excluded, see BRD3-B10), never the packages it carried in. Alternatively, extend the key set transitively and define a single copy per key. Then correct rule 1's "cannot arise".
- **Source:** review
- **Confidence:** medium (the wholesale copy is stated; whether a live chain of length 2 exists in any user tree is not measured)

### BRD3-B5 — MINOR — Phase 10 names the wrong BRD in the rebaseline fix for a dependent's will-change finding
- **Where:** commands/brd-reconcile.md:2332-2337 ("A [CG#n] or [DG#n] carrying horizon: will-change whose named prerequisite decision this run has just frozen ... recorded with the concrete fix — `/product-workflows:prd-ground <BRD-KEY> --rebaseline`").
- **What is wrong:** a finding whose prerequisite decision is one of this BRD's decisions sits in a dependent BRD's grounding. It is set there by prd-ground Phase 6 from that dependent's declared prerequisite, and grounding-format §5 says a horizon names *another* BRD's decision. Throughout the command, `<BRD-KEY>` is this run's own slice (compare BRD2-B5). The fix therefore tells the operator to re-ground the slice just reconciled, which has no such finding, and not the dependent that does.
- **Suggested fix:** `/product-workflows:prd-ground <DEPENDENT-KEY> --rebaseline`, naming the dependent the finding sits in. The same applies to the *what still needs a human* line (:2536).
- **Source:** review
- **Confidence:** medium.

### BRD3-B6 — MINOR — `/prd-ground` Phase 5 does not handle design-grounder's `STALE_INDEX`
- **Where:** agents/design-grounder.md:80-84, :151, :198-201 (it returns `STALE_INDEX` when no index row names a frame still present); commands/prd-ground.md:1112-1116 (the Phase 5 handler covers OK, INPUT_MISSING/FRAME_SET_MISSING, and NO_INDEX only). `grep -n STALE_INDEX commands/prd-ground.md` finds only :1360, the Phase 7 verifier.
- **Failure scenario:** a frame set whose images were moved out, leaving index.md. grounding-format §6.2 step 1a names this state as reachable ("A set that once held frames and now holds none is reported as stale"). The design pass returns STALE_INDEX, and Phase 5 has no branch for it. The orchestrator then has to improvise between skipping and stopping. It also gets no remedy to print: the agent's own says to restore the frames or re-run /frames, while NO_INDEX's remedy is /frames.
- **Suggested fix:** add `STALE_INDEX` → report and skip that set, naming the restore-the-frames remedy, beside NO_INDEX.
- **Source:** review
- **Confidence:** high.

### BRD3-B7 — MINOR — The missing-reason picker offers `Cancel` that no prose handles, under a sentence that says "exactly two resolutions follow"
- **Where:** `plugins/product-workflows/commands/brd-reconcile.md:1050-1053`; the docs page agrees with the prose and not with the array: `plugins/product-workflows/docs/commands/brd-reconcile.md:399-400` ("takes one of exactly two routes").
- **What is wrong:** "exactly two resolutions follow:" is followed by `choices: ["Ask the customer for the reason — …", "Freeze the answer as [CD#n] with status: open, …", "Cancel"]`. Nothing in Phase 4 (`grep -n Cancel` over `:898-1294` finds only `:978` and `:1053`) says what `Cancel` does. It could abort the run (the *Aborting the walk* paragraph, `:977-986`, is about the four-option array and says that array deliberately has no `Cancel`), return the candidate to the four-option picker, or leave it unconfirmed so that `BRD_RECONCILE_UNCONFIRMED` fires at the gate.
- **Failure scenario:** The operator realises the reason is in the quotation and picks `Cancel` to go back and take *Correct it*. The agent has no instruction. It may stop the run, losing every confirmation taken, or treat the pick as a third resolution and drop the candidate silently, which `:1001-1002` forbids.
- **Evidence:** Lines quoted. The conflicting-answer picker and the unmatched picker carry no `Cancel`. The Phase 0 pickers that do carry one each define it (`:418`, `:461`, `:493`).
- **Suggested fix:** Either drop `Cancel`, since the harness's free-text option already allows an abort (as `:978-980` argues for the four-option array), or define it, for example as "return to the four-option picker for this candidate", and say so in the docs page.
- **Source:** review
- **Confidence:** high

### BRD3-B8 — MINOR — A finding that keeps its verdict but has an `unprovable` verifier outcome counts as settled in Phase 3 and unsettled in Phase 5
- **Where:** `plugins/product-workflows/commands/brd-interview.md:851-857` (Phase 3's second source), `:512-514` (Phase 2's no-question test) and `:1905-1908` (the walk record) against `:1401-1402` (Phase 5 outcome 2) and `:96-98` (invariant 4). Also `:2421` (Final report) and `plugins/product-workflows/docs/commands/brd-interview.md:136-137`.
- **What is wrong:**
  - Phase 3 raises a question for "a `[BR#n]` whose findings are `NOT-PROVABLE` — the repository could not settle it". That tests the **verdict** only.
  - Phase 5 says a finding "cannot settle" a question when "its verdict is `NOT-PROVABLE`, or the verifier returned `unprovable`".
  - Invariant 4 also admits a re-tag against "a named `NOT-PROVABLE` finding or an `unprovable` verifier outcome".
  - `grounding-format.md:1012` produces exactly the state no generation bullet sees. When two blind verdicts disagree, "the outcome is `unprovable`, the finding keeps its verdict and evidence". A plain verifier `unprovable` produces it too (`:975`).
  - Phase 2's no-question test and the walk record list "no finding whose verdict leaves the premise open (… one the repository could not settle)". Both are phrased over verdicts.
  - The Final report says "every re-tag, with the `NOT-PROVABLE` finding that caused it", and the docs page says a re-tag "is admissible only against a named `NOT-PROVABLE` finding". Both drop the outcome half.
- **Failure scenario:** `[CG#4]` reads `verdict: CONFIRMED`, `outcome: unprovable`, because the verifier's second blind derive disagreed.
  - Round 1's generation raises nothing for its `[BR#n]`, since no bullet matches a CONFIRMED verdict.
  - A slice where this is the only open point takes the nothing-askable branch. It writes a walk record saying no finding left its premise open.
  - The same finding, met by a `[G]` in Phase 5, is treated as unable to settle anything and forces a re-tag.
  - So one requirement the verifier could not settle reaches `/create-prd` as grounded without any person ever being asked.
- **Evidence:**
  - Read `brd-interview.md:849-857` and `:1401-1402` side by side.
  - Ran `grep -n unprovable brd-interview.md`. Its only hits are `:98` and `:1402`, and Phase 3 has none.
  - `grounding-format.md:1012` confirms that the verdict is kept beside `unprovable`.
- **Suggested fix:** Pick one reading and use it everywhere.
  - Either extend Phase 3's second bullet, Phase 2's test and the walk-record wording to cover "or whose verifier outcome is `unprovable`", and add "or the `unprovable` outcome" to the Final report and the docs page.
  - Or state in Phase 5 that an `unprovable` outcome on a decisive verdict still settles the question.
- **Source:** review
- **Confidence:** medium. The design intent for CONFIRMED plus `unprovable` is not stated anywhere, but the two phases' texts plainly disagree.

### BRD3-B9 — MINOR — Phase 5 can answer a `[G]` from a `SUPERSEDED` finding
- **Where:** `plugins/product-workflows/commands/brd-interview.md:1393-1400`
- **What is wrong:**
  - The text reads: "For each `[G]` in the round, search the verified findings for one whose `claim` settles it. Only a finding carrying a verifier `outcome` counts".
  - A superseded block keeps "every other field — its `outcome` included — as it stood" (`grounding-format.md:579`, `:990`). It also keeps the same `claim` as its successor (`:987-989`).
  - So the outcome filter does not exclude a superseded finding, and nothing else in Phase 5 does either.
  - Every other reader of the findings in this command excludes `SUPERSEDED` explicitly:
    - Phase 8's re-base requires "a verdict other than `SUPERSEDED` — a superseded finding is ground no longer on file" (`:1747-1749`);
    - the `generated against:` line lists findings "not reading `SUPERSEDED`" (`:1981`);
    - a later round's generation passes over "every finding reading `SUPERSEDED`" (`:1282-1283`);
    - Phase 0 step 9's input read ("every verified `[CG#n]`/`[DG#n]`", `:335`) does not filter.
- **Failure scenario:**
  - A `--rebaseline` pass superseded `[CG#3]` (prior `CONFIRMED`, evidence intact) and appended `[CG#9]` reading `NOT-PROVABLE`.
  - A `[G]` about the same `[BR#n]` is matched against `[CG#3]`'s claim and evidence. It is recorded *answered from findings* naming `[CG#3]`, instead of being re-tagged against `[CG#9]` (outcome 2).
  - The finding ids recorded there "are what a decision drawing on this answer later puts in its own `evidence` list" (`:1399-1400`). So a `[VD#n]` is born resting on a superseded finding.
  - The next round's *A decision the re-grounding moved* then reopens it, because `prior_verdict` `CONFIRMED` differs from the successor's `NOT-PROVABLE`. That is a question asked twice, and the first answer rested on ground no longer on file.
- **Evidence:**
  - Read `:1388-1427`; the word `SUPERSEDED` does not occur in Phase 5.
  - Compared that against `:1747-1749`, `:1981` and `:1282-1283`.
  - Checked the grounding-format supersession rule at `:987-990`.
- **Suggested fix:** In outcome 1, add "a finding reading `SUPERSEDED` never settles a `[G]`; read its successors (*A superseded finding's successors*, in *Generate the round's question set*) in its place".
- **Source:** review
- **Confidence:** medium

### BRD3-B10 — MINOR — A copied-in prerequisite package brings its own rendered prompt and manifest, and part 3 then sends the reviewer to that second prompt
- **Where:** `plugins/product-workflows/references/bundle-packaging.md:88` (the rendered prompt is §1.1's first row of a bundle), `:100`, `:483`; `plugins/product-workflows/commands/brd-package.md:907` (part 3 lists "every other document `bundle-packaging.md` §1.1 admits **except the rendered prompt itself**"), `:1445-1449` (rule 5).
- **What is wrong:** A prerequisite's `bundle-<date>/` contains that package's own `customer-review-prompt` and manifest. Nothing excludes them from the copy. The prompt carries its own one-new-file rule, its own `Package reviewed: <PREREQ-KEY> <date>` line and its own "the only file to send back" instruction naming `<PREREQ-KEY> Customer Review <YYYYMMDD>.md`. Part 3 excludes only *this* package's prompt, so it lists the prerequisite's prompt among the documents to review.
- **Failure scenario:** A vanilla agent reads every document part 3 names. It meets a second complete review prompt that tells it to write a different file under the prerequisite's key, and may write two reviews or the wrong one. `/brd-reconcile` step 6a looks only for `<BRD-KEY> Customer Review <YYYYMMDD>.md` (`commands/brd-reconcile.md:361`, `:370`), so it finds nothing for a review written under the prerequisite's key.
- **Evidence:** Read the lines above. A grep for any rule naming a prerequisite's prompt or manifest in the bundle returns nothing.
- **Suggested fix:** Exclude a prerequisite's rendered prompt (and, optionally, its manifest) from rule 5's copy, or name both in part 2 as context not addressed to this reviewer.
- **Source:** review
- **Confidence:** medium

### BRD3-B11 — MINOR — Rule 5 marks a copied prerequisite document on "its own front matter line". Rule 4 strips every bundled frontmatter block, and rule 7 forbids rewriting such a copy.
- **Where:** `plugins/product-workflows/commands/brd-package.md:1445-1447` ("The marking is on the documents' own front matter line in the bundle and in the manifest"), against `:1434-1437` (rule 4: "every bundled document that carries a frontmatter block loses it whole"), and `:1480-1484` (rule 7: "that package is never rewritten… rewriting the copy would make it disagree with the dated package it was copied from"); `bundle-packaging.md` §5 (`:452-455`).
- **What is wrong:** These are three live instructions that cannot all be followed. Marking the copy means writing a frontmatter line into it. Rule 4 removes frontmatter from every bundled document. Rule 7 and §5 say the copy is never rewritten, because it must stay byte-identical with the dated bundle it came from.
- **Failure scenario:** An agent following rule 5 edits each prerequisite document, which falsifies the "copy of the dated package" property that rule 7's model-id exemption depends on. An agent following rule 7 leaves the documents unmarked, against rule 5.
- **Evidence:** Read the three rules in order.
- **Suggested fix:** Carry the *not for re-review* marking in the manifest and in part 2 only, and drop "on the documents' own front matter line".
- **Source:** review
- **Confidence:** high

### BRD3-B12 — MINOR — A same-day re-run rewrites this date's self-review, prompt and note. Phase 0's guard covers only the bundle directory, and the self-review's numbering rule reads as appending to the earlier run's file.
- **Where:** `plugins/product-workflows/commands/brd-package.md:496-498` (step 11: one stamp for every artifact; only `bundle-<YYYYMMDD>/` is tested), `:463-465` ("nothing below deletes, renames or rewrites a dated artifact another run wrote"), `:622` ("Write `<BRD-dir>/self-review-<YYYYMMDD>.md` now"), `:628-631` (ids continue "from the highest already in that file"), `:596` (`prior_reviews`: "every earlier self-review-<YYYYMMDD>.md"); `:1177` (`BRD_PACKAGE_PROMPT_LEAK` ends "…and re-run").
- **What is wrong:** Several stops tell the operator to repair the content and re-run. These include `BRD_PACKAGE_PROMPT_LEAK` in Phase 6, `BRD_PACKAGE_UNDISPOSED` (`:815`), and an abort of the disposition walk (`:692-693`). All of them fire after Phase 3 wrote `self-review-<date>.md`, and the prompt leak fires after the operator disposed every finding. The same-day re-run passes step 11, because no bundle exists. It then either:
  - overwrites the earlier run's self-review, prompt and note, which step 11's "nothing below… rewrites a dated artifact another run wrote" forbids, or
  - by `:628-631`'s rule, appends its findings after the earlier run's records, whose dispositions still stand.

  Under the second reading, part 9 renders the earlier run's `accepted-risk` findings beside this run's restatements of them. `restates:` is applied only to a second pass within one run (`:760-769`), so nothing pairs them. The command never says whether a same-dated file is "earlier" for `prior_reviews` or the *Re-escalates* lookup, or is this run's own file.
- **Failure scenario:** A run stops with `BRD_PACKAGE_PROMPT_LEAK` after twelve dispositions. The operator fixes the grounding file and re-runs the same day. Depending on the reading, the dispositions are silently lost, or the customer sees each attack twice.
- **Evidence:** Read the lines above. Step 11 tests only `bundle-<YYYYMMDD>/`. No step mentions an existing same-dated self-review, prompt or note.
- **Suggested fix:** Make step 11 test all four dated artifacts. Alternatively, rule that a same-dated self-review from a run that built no bundle is this run's scratch, overwritten whole, and is never `prior_reviews`.
- **Source:** review
- **Confidence:** medium

### BRD3-B13 — MINOR — `/brd-reconcile`'s `BRD_RECONCILE_EMPTY_DIGEST` tells the operator to re-run "telling the run the file is prose", but the command gives them no way to say so
- **Where:** `plugins/product-workflows/commands/brd-reconcile.md:859` (the stop text), `:790` (the dispatch hard-codes `mode: auto`), `:77-78` and `:839-840` ("`free-text` where the operator has told it the file is prose"), `:164-200` (Phase 0 parses `<BRD-KEY>`, `@<review-file>`, `--sent` and the run flags, and nothing else).
- **What is wrong:** There is no flag, no question and no step that sets the reader's mode to `free-text`. The dispatch's mode is the literal `auto`.
- **Failure scenario:** A schema-looking review parses to three empty sets with section 2 reading `approved-with-required-changes`. The run stops. The operator re-runs as told, with `@<review-file>`. The dispatch is `auto` again, the reader returns the same digest, and the same stop fires. There is no exit except editing the review, which breaks the one-new-file rule.
- **Evidence:** A grep of `brd-reconcile.md` for `free-text`, `prose` and `--prose`/`--free` finds only the sentences quoted above and no parser.
- **Suggested fix:** Add a `--free-text` argument, parsed in Phase 0 step 2 and passed as `mode: free-text`, or a Phase 3 question with that effect. Then name it in the stop.
- **Source:** review
- **Confidence:** high

### BRD3-B14 — MINOR — §7 relation 1 never checks part 6's `in-scope` `[CDF#n]` list, and its reason for excluding part 6 ("prose… not the requirement ids") is false of that list
- **Where:** `plugins/product-workflows/references/bundle-packaging.md:956-960` (scope: "the open assumptions, the conditional positions and conditional defect entries, and the out-of-scope defect entries"), `:991-996` ("The review scope part renders… prose in the customer's own vocabulary… not the requirement ids"), `:1041-1049` (§7.2 names only part 6's other-BRD list as unseen); `plugins/product-workflows/commands/brd-package.md:970-973` (part 6: "every `[CDF#n]` disposed `in-scope`, named by id"); docs `plugins/product-workflows/docs/commands/brd-package.md` *Phase 8 — the set-resolution check* (same omission).
- **What is wrong:** Part 6 enumerates identified records, `in-scope` `[CDF#n]` by id, from a source the bundle carries (`code-defect-log.md`, §1.1 `:95`), filtered on a record field (`disposition`). That is exactly relation 1's scope test. The conditional (part 8) and out-of-scope (part 11) slices of the same log are in scope; the in-scope slice is not, and §7.2 does not admit the gap. §1.1 `:95` calls this slice "the delivery boundary", and omitting an entry understates what the customer agrees to (`brd-package.md:972-973`).
- **Failure scenario:** Part 6 drops one `in-scope` defect. Every relation stays green, and §7.2 does not list this case among what §7 cannot see.
- **Evidence:** Read the scope list. `ea3f0554` (2026-09-08) added part 6's `[CDF#n]` list; §7 was written on 2026-09-09 (`e72cc994`, `83332f08`) with the other two slices only.
- **Suggested fix:** Add "the in-scope defect entries" to relation 1's scope, or list the slice in §7.2 with its reason.
- **Source:** review
- **Confidence:** medium

### BRD3-B15 — MINOR — §7.1 calls part 7's escalated-finding fraction "testable", but its source is the self-review, which the same section rules out of relation 1 because it is not in the bundle
- **Where:** `plugins/product-workflows/references/bundle-packaging.md:996-998` ("so only the assumption and escalated-finding fractions of it are testable"), against `:957-958` (scope requires a source "itself in the bundle") and `:985-989` (accepted-risk findings are outside because their source "is the adversarial self-review, which §1.1 excludes… a relation that reached for it would resolve to an absent file on every correct bundle").
- **What is wrong:** The escalated `[SR#n]`s come from the same excluded file as the accepted-risk ones. Calling them testable invites an executor to compare part 7's `[SR#n]` set against a source that yields nothing.
- **Failure scenario:** An executor tests that fraction. The source yields zero records while part 7 restates some, which is `BRD_PACKAGE_SET_UNREADABLE` (`:1030-1039`; `brd-package.md:1558-1559`) on every package carrying an escalated finding.
- **Evidence:** Read the three passages in order.
- **Suggested fix:** Change it to "only the assumption fraction of it is testable; the escalated findings are outside for the accepted-risk reason".
- **Source:** review
- **Confidence:** medium

### BRD3-B16 — MINOR — The `brd-package-reviewer` `INPUT_MISSING` stop has no stop code, and Phase 11's capture-at-block classification leaves it out
- **Where:** `plugins/product-workflows/commands/brd-package.md:598-602` ("Map that return to a stop naming the field it named — it is a defect in this dispatch, not in the package"); `:1722-1736` (Phase 11: "Six of this command's stops **do** qualify… `BRD_PACKAGE_REVIEW_UNACCOUNTED` is an agent-contract gap… **Every other stop fails that test**").
- **What is wrong:** The command itself calls this a dispatch defect, which is an agent-contract or plugin gap of exactly the kind `emit-block` exists for. It is the counterpart of `/brd-reconcile`'s coded `BRD_RECONCILE_READER_CONTRACT` (`brd-reconcile.md:834`), which Phase 11 cites as the model. But it has no code, and Phase 11 says every stop outside the six fails the test, so no feedback is captured when it fires.
- **Failure scenario:** A dispatch omits `package.grounding`. The run stops with a free-form message, and no `emit-block` record is written for a plugin defect.
- **Evidence:** The code list from `grep -o 'BRD_PACKAGE_[A-Z_]*'` has no code for that stop. Phase 11's list holds six codes.
- **Suggested fix:** Define `BRD_PACKAGE_REVIEWER_CONTRACT: brd-package-reviewer returned INPUT_MISSING (<field>) — …` and add it to Phase 11's qualifying list (seven).
- **Source:** review
- **Confidence:** high (Phase 3 is outside this slice's phase range; found through Phase 11's list)

### BRD3-B17 — MINOR — Phase 5's tier picker lists a fourth option, `Cancel`, that no prose handles, while the paragraph under it says "a fourth would be a tier nothing downstream can read"
- **Where:** `plugins/product-workflows/commands/brd-package.md:863` (the array ends with `"Cancel"`), `:866-869` ("the three options are the three rows of `bundle-packaging.md` §3's own table… a fourth would be a tier nothing downstream can read").
- **What is wrong:** *Cancel* has no consequence anywhere in the command. Phase 4 avoids a listed Cancel for this reason (`:690-694`), and Phase 7 defines its own (`:1268-1270`). The sentence about four options contradicts the array beneath which it stands.
- **Failure scenario:** The operator picks *Cancel*. The agent must guess whether to stop the run, which leaves an uncommitted `self-review-<date>.md` and skips or runs the tail, or to re-ask. It may also treat *Cancel* as a tier.
- **Evidence:** `grep -n Cancel` on the command returns only `:142`, `:690`, `:863`, `:1262` and `:1270`. None of them handles `:863`'s option.
- **Suggested fix:** Drop `Cancel`, which the free-text option already makes an abort reachable, as in Phase 4, or state what it does and reword `:866-869`.
- **Source:** review
- **Confidence:** high (Phase 5 is outside this slice's phase range; not in BRD/BRD2/FBB)

### BRD3-B18 — MINOR — The docs page says the rendered schema headings are renumbered "so the customer's copy runs from 1"; the command renumbers them `<part>.1`–`<part>.5` and says outright that a restart at 1 is the wrong scheme
- **Where:** `plugins/product-workflows/docs/commands/brd-package.md` *Gates*, Phase 6 bullet ("The rendered headings are renumbered so the customer's copy runs from 1 rather than visibly beginning at 2"), against `plugins/product-workflows/commands/brd-package.md:1129-1137` ("`## 2.` becomes `### <part>.1`… **and it does not restart at 1 inside a numbered outline either** — a body renumbered `1.`–`5.` inside part 10 of eleven reads as 1–10, then 1–5, then 11").
- **What is wrong:** The docs page describes the rejected scheme.
- **Failure scenario:** A maintainer or operator reading the docs expects `1.`–`5.` headings and reads the `10.1`–`10.5` render as a defect.
- **Evidence:** Read both passages.
- **Suggested fix:** Change it to "renumbered under the part they are rendered into (`10.1`–`10.5`), so the copy neither begins at 2 nor restarts at 1".
- **Source:** review
- **Confidence:** high

### BRD3-B19 — MINOR — `/brd-reconcile` gates on the folder's *most recent* prompt, before it knows which package the review answers
- **Where:** `plugins/product-workflows/commands/brd-reconcile.md:319-325` ("Execute it against the resolved folder's **most recent `customer-review-prompt-<YYYYMMDD>.md`**"), `:345-351` (`BRD_RECONCILE_PACKAGE_NOT_HANDED_OFF`: "Commit and merge the package's files…"), against `:792-819` (Phase 3 resolves the answered package later, by the `Package reviewed` line).
- **What is wrong:** The gate is about "what the customer saw", but it tests the newest package, not the one the review answers.
- **Failure scenario:** Package D1 is sent and merged. Package D2 is built later with its handoff declined, abandoned or not yet merged. The customer returns a review of D1, whose `Package reviewed:` line names D1. `/brd-reconcile` stops on D2 with `PACKAGE_NOT_HANDED_OFF` and tells the operator to land D2's files, a package nobody reviewed, before D1's answers can be reconciled.
- **Evidence:** Read the gate and Phase 3's resolution order.
- **Suggested fix:** Gate on the prompt the review's `Package reviewed:` line names, read from the review before the gate where it is present. Fall back to the most recent only where the line is absent.
- **Source:** review
- **Confidence:** medium

### BRD3-B20 — NIT — Both grounders are told to assign `horizon`, which their caller says they cannot and then overrides; design-grounder's class-4 rule needs data it is never handed
- **Where:** agents/code-grounder.md:128-131 and agents/design-grounder.md:138-140 (step 6, assign horizon; for class 4 "horizon and commit follow the cited [CG#n]'s own"); agents/design-grounder.md:37-42 (cg_findings carries id, claim, verdict, evidence and commit, with no horizon or prerequisite); commands/prd-ground.md:1155-1157 ("Every finding leaves Phase 5 as horizon: current by default (an agent ... has no visibility into another BRD's decisions to do otherwise)"); commands/prd-ground.md:1110 (the dispatch hands only those five fields).
- **What is wrong:** these are two live contradictory instructions. The agents are handed no prerequisite decisions, yet are told to name one. design-grounder cannot follow its cited [CG#n]'s horizon because the field is not passed. Phase 6 then judges each finding independently, so a class-4 [DG#n] can get a different horizon from the [CG#n] it cites.
- **Suggested fix:** in both agents, say horizon is always `current` on return, because the caller sets it. Either drop "follow the cited [CG#n]'s own", or move that rule into prd-ground Phase 6 as "a class-4 [DG#n] takes its cited [CG#n]'s horizon".
- **Source:** review
- **Confidence:** medium.

### BRD3-B21 — NIT — The Final report explains a slice's non-zero `unallocated` term as a row "delegated to a child"
- **Where:** `plugins/product-workflows/commands/brd-interview.md:2466-2467`
- **What is wrong:**
  - The text reads: "a non-zero `unallocated` term in the line — a row this BRD delegated to a child that has not walked it yet — is that resolution working".
  - The same paragraph has just established that "this run always stands on a slice … so that is always a sibling or the parent" (`:2459-2463`). A slice has no child, because nesting is capped at one level (`coverage-ledger-format.md:661-662`).
  - On a slice, the term counts an orphan row resolved one hop into a sibling that has not walked it, or one whose parent row reads `unallocated` after a `/brd-intake` re-run (`coverage-ledger-format.md:643`).
  - The same sentence in `/brd-reconcile` was already corrected to "delegated to a BRD that has not walked it yet" (`brd-reconcile.md:3026-3028`).
- **Failure scenario:** The operator is told to wait for a child walk that cannot exist. The two real causes, a sibling's pending walk and a parent re-intake, go unnamed.
- **Evidence:**
  - `grep -n "a child that has not walked" plugins/product-workflows/commands/*.md` returns only `brd-interview.md:2467`.
  - Compared that against `brd-reconcile.md:3026`.
- **Suggested fix:** Use `/brd-reconcile`'s wording: "a row this slice's ledger names `covered-by` a sibling or the parent that has not walked it yet, or whose parent row a `/brd-intake` re-run reset".
- **Source:** review
- **Confidence:** high

### BRD3-B22 — NIT — `coverage-ledger-format` §6 still models a root ledger holding `covered-here` rows, a state §5 calls illegal
- **Where:** `plugins/product-workflows/references/coverage-ledger-format.md:773-783` (§6.5's worked example: root `EPIC-008` with "`covered-here` | 4" and "`unallocated` | 1"), `:657-658` (§6.1: "The parent case lands on a row the parent resolved `covered-here` or `deferred-to`"), and §3's orphan table row at `:173` ("`covered-here` — the parent builds it").
- **What is wrong:**
  - §5's table (`:386`) says: "Every row of a root's ledger ends `covered-by`, `deferred-to`, `rejected` or `superseded-by`; `covered-here` is not among them, and a root row carrying one is a ledger written before a BRD became a container, or edited by hand".
  - `/brd-split` offers a root walk only `covered-by`, `deferred-to`, `rejected` and `superseded-by` (`brd-split.md:35`).
  - The only worked example of a parent's line therefore starts from a hand-damaged ledger that every consumer refuses. §6.1 and §3 also describe a parent that "builds it", which D5 removed.
- **Failure scenario:** A maintainer or agent treats §6.5 as a valid shape. For example, it builds a fixture or self-test from it, or reasons that a root may legally carry `covered-here`. That contradicts the container refusal §5 states.
- **Evidence:** Read `:330-460` against `:771-817`. The re-cut and removal-repair text (§3.2) only ever writes `deferred-to: <PARENT-KEY>` onto a root.
- **Suggested fix:** Recast §6.5's four `covered-here` root rows as `deferred-to: <this BRD>` (with the arithmetic adjusted), or say that the example predates D5. Mark §3's `covered-here` orphan-table row and §6.1's "`covered-here` or" as reachable only on a pre-container ledger.
- **Source:** review
- **Confidence:** medium. This is misleading text in an authority, not a runtime failure.

### BRD3-B23 — NIT — §6.2 says `/brd-split` gates `grounding/code-grounding.md`, which it does only in `allocate-only` mode
- **Where:** `plugins/product-workflows/references/coverage-ledger-format.md:718-720`
- **What is wrong:**
  - The text reads: "only `/prd-ground` gates **this file**, in its Phase 0 step 6. `/brd-split` and `/brd-interview` each gate `grounding/code-grounding.md` there and then read the ledger from the working tree".
  - `brd-split.md:158` says: "**This step and step 7 run in `split_mode: allocate-only` only.** A root BRD is never ground". The brd-route map line says the same ("`allocate-only` only — a root is never ground").
  - On a `full`-mode root run, which is the run that prints this line over a root's delegated rows, `/brd-split` gates nothing at all.
- **Failure scenario:** A reader takes the paragraph's provenance account as covering root runs, and believes a root split's ledger line rests on a merged grounding gate that never ran.
- **Evidence:** Compared `brd-split.md:158` and `:194` with `coverage-ledger-format.md:717-724`.
- **Suggested fix:** Change the sentence to "`/brd-split` (on a slice, in `allocate-only` mode) and `/brd-interview` each gate …".
- **Source:** review
- **Confidence:** high

### BRD3-B24 — NIT — The shared lane offers `/brd-reconcile <BRD-KEY> @<review-file>` after `/brd-package` unconditionally; Phase 10 writes no path on the repository route
- **Where:** `plugins/workflows-core/reference-parts/next-phase-offer/brd.md:161-164` (source `references/next-phase-offer.md`), against `plugins/product-workflows/commands/brd-package.md:1675-1682` (`<review-clause>`: on the repository route "(once you merge the customer's pull request — or @<review-file> where they sent it back instead)").
- **What is wrong:** Phase 10 loads that lane "before anything below is printed". On the repository route the two live instructions disagree on the offered command line.
- **Failure scenario:** An agent printing the lane's form tells a repository-route operator to pass a file path they do not have.
- **Evidence:** Read both.
- **Suggested fix:** Make the lane's line route-neutral (`[@<review-file>]`), or name the repository-route form.
- **Source:** review
- **Confidence:** low

## docs-workflows and the smaller plugins

### DOC-A-B1 — MAJOR — Phase 5.8's no-discrepancy exit jumps to Phase 6.3, skipping Phase 6.1 (CDN handoff) and Phase 6.2 (branch setup)
- **Where:** `plugins/docs-workflows/commands/document.md:744`
- **What is wrong:** "Run the rest of this phase when the `doc-planner` handoff contains any `verification_warnings` with `finding: CONTRADICTED`, `NOT_FOUND`, `AMBIGUOUS`, or verdict `SPEC-VS-PRD`. If there are none, skip to Phase 6.3 — the row above is already recorded." Phases 6.1 (`:789`) and 6.2 (`:813`) come between 5.8 and 6.3, and each has its own run condition that does not depend on discrepancies. Line 741 says the same no-escalation case is the one where "this phase's body does not run", and that case is common: every run whose `code_repos` is empty, and every run whose warnings are all `VERIFIED`.
- **Failure scenario:** A keyed run in a `docs_repo` context has no escalating warnings, and the user approved branching. The run does what the text says and goes straight to 6.3. No branch is cut, and 6.3's commit (`:864`, table `:882` "Commit YES") lands on whatever branch HEAD is on, often the default branch. In the inline-profiling case, `profile_branch` is never renamed. Where a screenshot is `cdn_upload_required`, Phase 6.1 never asks for the CDN decision, so `doc-writer` gets no `cdn_handoff_decision`. Its entry validation (`agents/doc-writer.md:33-34`) only covers a decision that is present but whose inputs are missing.
- **Evidence:** Read `:736-787` and `:789-848`. `grep -n "skip to Phase"` finds only `:744`.
- **Suggested fix:** "If there are none, the rest of this phase does not run; go on to Phase 6.1." (Phase 6.1 already skips itself when nothing applies.)
- **Source:** review
- **Confidence:** high

### DOC-A-B2 — MAJOR — Phase 6.4's clean-style exit jumps to Phase 7, skipping Phase 6.5 (render verification) and its two ledger rows
- **Where:** `plugins/docs-workflows/commands/document.md:923`; contradicts `:947`, `:952`
- **What is wrong:** "**`status: OK`** — the chain ran (primary and/or complementary), zero merged violations. Proceed to Phase 7." Phase 6.5 says "Both gates this phase owns must carry a row on every run" (`:947`) and "Run this phase after Phase 6.4" (`:952`).
- **Failure scenario:** The style check comes back clean, which is the best case. The run then skips the build check and the smoke check, and never writes the `build_check` / `render_smoke_check` rows. Where Phase 0's preflight pre-seeded no row, `doc-reviewer`'s Verification-gate integrity dimension BLOCKs on "a registry gate has no row" (`agents/doc-reviewer.md:60`, `references/gate-ledger.md` §6). The run then burns its one fix cycle on a ledger that `doc-fixer` cannot repair, and a broken build ships unchecked. The `VIOLATIONS_FOUND` branch names no next phase, so only the clean path is misdirected.
- **Evidence:** Read `:921-941` and `:945-1061`.
- **Suggested fix:** "Proceed to Phase 6.5."
- **Source:** review
- **Confidence:** high

### DOC-A-B3 — MAJOR — `doc-planner` makes a `changelog:` entry mandatory on every target, new pages included; the plugin's own frontmatter rules forbid one on first publish
- **Where:** `plugins/docs-workflows/agents/doc-planner.md:55`, `:148`; `plugins/docs-workflows/agents/doc-writer.md:46`; contradicts `plugins/docs-workflows/references/docs-profiles/changelog-guidelines.md:32-33`, `references/docs-profiles/frontmatter-guidelines.md:64-66`, `skills/docs-frontmatter/SKILL.md:15-17`, `:62-63`
- **What is wrong:** The planner says "`changelog:` — append a dated entry … This is mandatory on every target", and the checklist schema gives every target `changelog: {action: append, …}`. The changelog guideline says "**Never on first publish.** Do not create a changelog entry when a page is first published; the published timestamp is used instead". The frontmatter guideline says "Do **not** add a `changelog:` entry on first publish", and the skill says "NOT brand-new pages … never pair it with a first-publish changelog entry".
- **Failure scenario:** A `new-page-in-existing-section` or `new-section` target gets a planned changelog entry. `doc-writer` follows the checklist (step 2) and writes it. `doc-reviewer` then either judges the page against the checklist and passes it, or judges it against the guideline it is told to apply "in full" (`doc-reviewer.md:53`) and raises a MAJOR. Either way, a page that breaks the repository's convention reaches the pull request, or a fix cycle is spent on it.
- **Evidence:** Read the lines above.
- **Suggested fix:** In `doc-planner` step 3 and the writer's step 2: "on an existing page only. A new page gets `published`, never a changelog entry". Make the schema's `changelog` entry conditional on `kind: extend-existing`.
- **Source:** review
- **Confidence:** high

### DOC-A-B4 — MAJOR — Declining branching at plan approval still commits into the docs repo, and Phase 8.5 then squashes against an unset `base_branch`
- **Where:** `plugins/docs-workflows/commands/document.md:345`, `:396`, `:402`, `:815`, `:842`, `:882`, `:1217`, `:1223`, `:1337`
- **What is wrong:**
  - Branching is "confirmed at plan approval" (`:345`, `:815`), but Phase 2's array is only `["Approve & continue (Recommended)", "Revise plan (you'll be prompted)", "Cancel"]`. A decline can only come through *Revise*, which the report anticipates ("user declined branching", `:1337`).
  - Phase 6.3's table still commits for `docs_repo` unconditionally ("YES (orchestrator commits doc-writer's `files_written` …)", `:882`). Only the Branch column is opt-in.
  - Phase 8.5 runs whenever 6.3 "wrote + committed" (`:1217`). It squashes onto `merge-base <base_branch> HEAD` (`:1223`), but `base_branch` is recorded only in Phase 6.2 step 5 (`:842`), which did not run.
- **Failure scenario:** The operator revises the plan to "no branch". The docs commit lands on the current branch, possibly the default branch. Phase 8.5 then runs `reset --soft` against an undefined base, and offers to push that branch.
- **Evidence:** Read the lines above. Nothing in Phase 6.3 or 8.5 tests whether branching was confirmed.
- **Suggested fix:** Either give the plan an explicit branch choice and make the Commit column follow it (no branch → no commit, and 8.5 is skipped), or remove the opt-out and the "user declined branching" wording.
- **Source:** review
- **Confidence:** medium

### DOC-A-B5 — MINOR — Phase 5.8's decision arrays differ from the `workflows-core:source-truth` §7.2/§7.3 arrays the run is told it "MUST follow"
- **Where:** `plugins/docs-workflows/commands/document.md:771`, `:777`; `plugins/workflows-core/references/source-truth.md:347-352`, `:384-392`, `:403-411`
- **What is wrong:**
  - **Batch array.** The command has `"Document ALL as intended (spec)"`, `"Skip ALL and report (drafts a bug report)"`; the reference has `"Document as intended (spec) for ALL"`, `"Skip & report for ALL (drafts a bug report; no claims documented)"`.
  - **Per-discrepancy array.** The command has `["Document as intended (spec)", "Document as actual (code)", "Skip this claim and report it", "Cancel"]` with no `(Recommended)`. The reference has `"Document as intended (spec) (Recommended) — …"` and `"Cancel the whole run"`.
  - **Why it matters.** §7 says "the orchestrator MUST follow this protocol", and the command cites §7 for this phase (`:746`) and loads `source-truth` (`:751`). With the verbatim-presentation rule in force, there are two live arrays and they disagree on wording and on whether an option is recommended.
- **Failure scenario:** A run loads both and presents whichever it reads last, recommending "Document as intended" in one session and nothing in the next.
- **Evidence:** Read both passages.
- **Suggested fix:** Make §7.2/§7.3 say the caller's arrays are authoritative (as `escalation-rules` does), or align the arrays.
- **Source:** review
- **Confidence:** medium

### DOC-A-B6 — MINOR — Stale "inline writer" claims: `current_model` is reported as the writer's model, and §10's handling of `implementation_model` contradicts itself
- **Where:** `plugins/docs-workflows/commands/document.md:362`, `:363`, `:368`, `:376`, `:1294`, `:1494`
- **What is wrong:**
  - **Writer model.** The writer is the delegated, Opus-pinned `doc-writer` (`:368`, `:852`, `:858`). But `:362` annotates `current_model` "= the inline writer + Phase 5.8 framing". The Phase 9 template prints "Session / writer model (current_model)" (`:1294`), and the invariant says "the inline writer + gates run on `current_model`" (`:1494`). That invariant's pin list also omits `doc-writer`.
  - **§10 and `implementation_model`.** `:363` says that under §10 "inline authoring_model / implementation_model keep the session model". `:376` says "`planning_model`, `review_model` and `implementation_model` already carry the enforced id".
- **Failure scenario:** A run on a Sonnet session reports the pages as written on Sonnet when Opus wrote them. Under `--enforce-model`, the `model_routing` block's `implementation_model` is filled in two contradictory ways.
- **Evidence:** Read the lines above.
- **Suggested fix:** Drop "inline writer" everywhere. Report `doc-writer` under `implementation_model`, and drop `implementation_model` from `:363`'s keep-the-session-model list.
- **Source:** review
- **Confidence:** high

### DOC-A-B7 — MINOR — The keyed-mode invariant prescribes a `/clear` docs→PM handoff; the report template and `session-hygiene` prescribe `/compact` (Dev→Dev)
- **Where:** `plugins/docs-workflows/commands/document.md:1504` against `:1399`; `plugins/workflows-core/reference-parts/session-hygiene/guidance.md:45-56`; `reference-parts/next-phase-offer/dev.md:174`
- **What is wrong:** The invariant says "then a docs→PM handoff suggestion (`/clear`) + `/rename <PRD-ID>-<slug>-dev`". The template says "**On to `/docs-workflows:release-notes <PRD>` (still Dev …)?** → run **`/compact`**". The `next-phase-offer` dev lane sends `/document` → `/release-notes` (same role), and `session-hygiene` says that pair takes `/compact` and that a command must not hardcode a per-command compact/clear verdict.
- **Failure scenario:** Two live instructions, so a run may print `/clear` and tell the Dev to drop the context `/release-notes` needs.
- **Evidence:** Read the lines above.
- **Suggested fix:** Reword `:1504` to "the role-aware suggestion `session-hygiene` §2 gives (here Dev→Dev, `/compact`)".
- **Source:** review
- **Confidence:** high

### DOC-A-B8 — MINOR — The key-discovery scan is invoked with no `--repo` when the slug→clone map holds no clone, which argparse rejects; the run then reports a script failure twice
- **Where:** `plugins/docs-workflows/references/key-discovery.md:9-17`, `:21`; `plugins/docs-workflows/scripts/key-discovery.py:1205`; `plugins/docs-workflows/commands/document.md:323`, `:417`, `:433-437`
- **What is wrong:**
  - **The script.** `scan.add_argument("--repo", action="append", required=True)`.
  - **When the map is empty.** The command gives "Proceed without the repos" whenever no `$REPOS_PATH` entry exists (`:321-323`, so "Phase 3's slug→clone map holds no clone"). Separately, a slug that matches no clone "is scanned in no repository" (`:417`). Either way the scan can have zero repositories, but nothing says to skip the call then. The reference always runs it and treats any non-zero exit as "could not run", retries with `--no-github`, and "Only where that fails too, report it as the scan's result for every repository".
- **Failure scenario:** A PRD-only run, with no clones mounted, makes two failing script calls and prints "Repositories the script could not read" / "where the script could not run: …" (`:1329-1330`). That is a false account of a scan that had nothing to scan.
- **Evidence:** Reproduced the argparse behaviour in the scratchpad: `required: --repo` → exit 2.
- **Suggested fix:** In `key-discovery.md` §1: "Where no repository is to be scanned, do not run the script; report the scan as not run — no clone resolved."
- **Source:** review
- **Confidence:** medium

### DOC-A-B9 — MINOR — Phase 7's PASS WITH RECOMMENDATIONS branch dispatches `doc-fixer` "for MAJOR findings only" even when no MAJOR survived
- **Where:** `plugins/docs-workflows/commands/document.md:1095-1105`; `agents/doc-reviewer.md:41`
- **What is wrong:**
  - **When the verdict fires.** `doc-reviewer` returns PASS WITH RECOMMENDATIONS on "at least one MAJOR, MINOR or NIT", so a MINOR/NIT-only review takes it.
  - **What the branch does.** It "invoke[s] `doc-fixer` for MAJOR findings only", writes the Fix Report to `claims_file`, and offers the unspent re-review per *Edits after a verdict that is not BLOCK*. No branch covers the case with no MAJOR survivor.
  - **The rule it breaks.** `finding-triage`'s "Never dispatch the fixer with an empty survivor list" covers only an emptied survivor set, not a set whose survivors are all below the fixer's severities.
- **Failure scenario:** A review with only NITs dispatches a fixer with nothing to apply, then offers a re-review of "edits" that were never made.
- **Evidence:** Read the lines above and `reference-parts/finding-triage/triage.md:107-116`.
- **Suggested fix:** "Where no MAJOR survived triage, dispatch nothing and go to Phase 8; MINOR / NIT go to the Phase 9 report."
- **Source:** review
- **Confidence:** medium

### DOC-A-B10 — MINOR — Docs page says `/epics` has 22 `## Phase` headings; it has 23
- **Where:** `plugins/docs-workflows/docs/commands/document.md:29`
- **What is wrong:** "(the pipeline plugin's `/product-workflows:epics`, the next-largest, has 22)". `grep -c '^## Phase' plugins/product-workflows/commands/epics.md` gives 23 at HEAD. The page's own counts (34 total, 23 keyed, 11 direct) are correct.
- **Failure scenario:** A false count in a docs page, which no gate checks.
- **Evidence:** Ran `grep -c '^## Phase'` over every command file: document 34, epics 23, implement 20.
- **Suggested fix:** Replace "has 22" with "has 23", or drop the number.
- **Source:** review
- **Confidence:** high

### DOC-A-B11 — MINOR — Phase 6.4's text labels the `doc-fixer` dispatch as the linter re-run
- **Where:** `plugins/docs-workflows/commands/document.md:924-932`
- **What is wrong:** The bullet says "invoke `doc-fixer` … After `doc-fixer` completes, check its `Stop condition flag` … Only on `CLEAR` re-run the linter once:", and then the code block directly below that colon is `Agent (subagent_type: "workflows-core:doc-fixer", …)`. The re-run of the linter (a second `docs-style-checker` dispatch) is never written out. Read in order, the block under "re-run the linter once:" is a second `doc-fixer` call. The direct-mode twin (`:1686`) has no such block and reads correctly.
- **Failure scenario:** A run dispatches `doc-fixer` twice and never re-lints, so "If violations remain after the re-run" (`:934`) is judged on a check that never ran, and the `style_check` findings count (`:939`) is not the post-fix count.
- **Evidence:** Read `:924-939`.
- **Suggested fix:** Move the `doc-fixer` block above the `Stop condition flag` sentence, and make "re-run the linter" name a `docs-style-checker` re-dispatch with the same brief.
- **Source:** review
- **Confidence:** medium

### DOC-A-B12 — NIT — Model-routing text names a dispatched step, "the folder read", that is no agent
- **Where:** `plugins/docs-workflows/commands/document.md:374`, `:1296`, `:1494`
- **What is wrong:** "the folder read, `diff-summarizer`, `doc-location-finder`, … → `detection_model`". Phase 3 reads the PRD folder inline ("Read the PRD folder directly", `:413`), and no agent is dispatched for it (`grep subagent_type` finds diff-summarizer, doc-location-finder, doc-planner, doc-reviewer, doc-writer, docs-style-checker, doc-fixer, general-purpose).
- **Failure scenario:** The report's "Detection steps — the folder read, …" line credits work to a model that did not run it.
- **Evidence:** Ran the `grep` above.
- **Suggested fix:** Remove "the folder read" from the three lists.
- **Source:** review
- **Confidence:** high

### DOC-A-B13 — NIT — Garbled residue in `doc-planner`: "NO kea key", "generated by keyed automation"
- **Where:** `plugins/docs-workflows/agents/doc-planner.md:55`, `:46`
- **What is wrong:** "a customer-readable 1-line change summary and NO kea key" and "is generated by keyed automation". These are artefacts of a vendor-token replacement. The sibling hard rule (`:203`) reads "generated from the tracker by the docs team's automation".
- **Failure scenario:** The meaning is recoverable, but it is executed prose.
- **Suggested fix:** "NO key"; "generated from the tracker by automation".
- **Source:** review
- **Confidence:** high

### DOC-A-B14 — NIT — Agents reference omits `defect-reporter` from the list of `workflows-core` agents these commands dispatch
- **Also found as:** DOC-C-B9 (merged here)
- **Where:** `plugins/docs-workflows/docs/reference/agents.md:3`
- **What is wrong:** "Four further agents these commands dispatch — `doc-fixer`, `impl-maintenance`, `code-scanner` … and `docs-grounder` …". `/document` (`:1179`, `:1751`) and the other emitting commands also dispatch `workflows-core:defect-reporter` under `--skip-feedback`.
- **Suggested fix:** "Five further agents …, and `defect-reporter` in `impl-maintenance`'s place under `--skip-feedback`".
- **Source:** review
- **Confidence:** high

### DOC-A-B15 — NIT — `toolchain-preflight` §5 says Cancel leaves nothing written, which is false after `/document`'s inline profiling
- **Where:** `plugins/docs-workflows/references/toolchain-preflight.md` §5 (the `"Cancel"` bullet: "→ stop the run. Nothing has been written.")
- **What is wrong:** In `/document` keyed mode, Phase 0 step 4(c) may already have committed a generated profile on `profile_branch` before step 7's preflight. The command knows this and appends the left-on-a-branch notice (`document.md:276-277`), but the reference it presents verbatim tells the operator otherwise.
- **Suggested fix:** "Nothing this check wrote; a caller that wrote before it (`/document`'s inline profiling) says what it left."
- **Source:** review
- **Confidence:** medium

<!-- from part B -->

### DOC-B-B1 — MAJOR — A re-draft under `# Unreleased` is bounded by the note it is about to supersede, so the superseding note never reads the earlier commits
- **Where:** `plugins/docs-workflows/commands/release-notes.md:270`, `:284-288`, `:545-548`; `plugins/workflows-core/references/implementation-format.md` §4 (*`/release-notes` reads only what no earlier note covering it read*); `plugins/docs-workflows/references/release-note-types.md:68-75`
- **What is wrong:** Phase 3 skips every block, and drops every scan commit, in "the read set of an earlier note covering its record" (`:270`, `:285-286`). Phase 8 then says a same-key note under `# Unreleased` "supersedes rather than accumulates". It marks the old note `<!-- superseded by the note below … -->` and "leave[s] its own scope comment and text intact" (`:547`). Nothing in the command, `release-note-types` §1 or `implementation-format` §4 takes a superseded note, or a same-key `# Unreleased` note this run will supersede, out of the boundary (`grep -i supersed` over the three files finds only the Phase 8 rule and unrelated deprecation text).
- **Failure scenario:** Run 1, with diff grounding on and the version declined, drafts ACME-7 under `# Unreleased` and reads commits A and B. The PRD changes and new commit C lands. Run 2 re-drafts. Its boundary skips A and B because run 1's note read them, so the writer is grounded on C alone. Run 2 then marks run 1's note superseded and appends a note whose `read:` line names only C. The live note was never grounded in A and B, and the only note that read them is marked superseded. Its scope comment still bounds every later run, so no later run reads A or B either. `Blocks used` lists only C's block, so the loss is hard to see.
- **Evidence:** I read Phase 3 steps 1–2, Phase 5's settle step, Phase 8 step 1 and the *Unreleased* exception. I also read `implementation-format` §4's boundary paragraphs and `release-note-types` §1. None of them exempts a superseded note.
- **Suggested fix:** In Phase 3, and in §4 and §1, say that a `# Unreleased` note with the same `<KEY>` as this run's, which this run will supersede, and any note already marked `superseded by`, bounds nothing. Its read set is re-read and carried into the new note's `read:` lines.
- **Source:** review
- **Confidence:** medium. The prose is unambiguous, and a live re-draft with grounding on would confirm the effect.

### DOC-B-B2 — MINOR — The `# Unreleased` supersede trigger is stated two incompatible ways
- **Where:** `plugins/docs-workflows/commands/release-notes.md:545`, `:551`
- **What is wrong:** `:545` scopes the trigger to one section: "when this run's draft would land under `# Unreleased` in a section that already holds a note with the same `<KEY>`". `:551` scopes it to the whole of `# Unreleased`: "Two notes for the **same key** under `# Unreleased` is the trigger, not two notes under the same Change Type".
- **Failure scenario:** A note drafted as a Feature update under `# Unreleased` is re-drafted after the PRD's `change_type` becomes `Breaking change`, or after the operator picks another route at the Phase 6 prompt. The new draft lands in `## Breaking changes`. Under `:545` the old `## Feature updates` note is left unmarked, so the stale claim stays live beside the true one, which is the defect `:545` names as the rule's reason. Under `:551` it is marked. Two runs following the same file can do different things.
- **Evidence:** I read both sentences in Phase 8 step 1.
- **Suggested fix:** Use one trigger: a note with the same `<KEY>` anywhere under `# Unreleased`, whatever its section, which is what `:551` and the rule's stated reason imply.
- **Source:** review
- **Confidence:** high

### DOC-B-B3 — MINOR — "No command of this plugin opens [a pull request] anywhere" has been false since `/release-notes` gained its handoff
- **Where:** `plugins/docs-workflows/references/finish-and-handoff.md:8`, `:102`; `plugins/docs-workflows/commands/document.md:1241`
- **What is wrong:** All three sites say the family opens a pull request through `phase-handoff` §2.6 or `code-handoff` §2.6, "but no command of this plugin opens one anywhere" (`:102` and `document.md:1241` add "this docs repo included"). Since `92a0b5bf` (2026-10-12), `/release-notes` Phase 8 step 1a runs `handoff-to-main` with `prefix: prd` (`release-notes.md:581-583`). That runs `gh pr create` in `$SPECS_PATH` (`release-notes.md:31`, `:758`). The sentence was written in `586377b4` (2026-09-16), when it was true; CHANGELOG 1.1.3 records why: "nothing under `docs-workflows` calls `handoff-to-main`".
- **Failure scenario:** An agent or maintainer reading `finish-and-handoff` or `/document` Phase 8.5 is told the plugin opens no pull request anywhere. This is a claim-expiry defect beside the shipped feature (`CLAUDE.md` § Editing discipline).
- **Evidence:** `git log -S'no command of this plugin opens one'` and `git log -S'prefix: prd' -- …/release-notes.md`; I read the three sites.
- **Suggested fix:** Rewrite the three sentences: no command of this plugin opens one in a docs repository, and `/release-notes` opens one in the specs repository for its draft, through `handoff-to-main`. Then sweep for other copies (`grep -rn "opens one anywhere\|opens it nowhere" plugins .claude docs/maintainers`).
- **Source:** review
- **Confidence:** high

### DOC-B-B4 — MINOR — The release-version question has no step and no array, and is displayed before it is asked
- **Where:** `plugins/docs-workflows/commands/release-notes.md:26-27`, `:242`, `:254`, `:259`, `:361-363`
- **What is wrong:** `--version` is "Absent, the grill asks once" (`:26`), and the only place that asks is Phase 3: "`release_versions` — `--version <v>`, else ask" (`:361`). Phase 3 runs after Phase 2's plan approval. But Phase 1 already says "Also display: … and the version this draft will be filed under" (`:242`). Phase 2's *Revise* lists "the version" among the things to change (`:259`), while Phase 2's plan list (`:254`) does not present it. No question text and no `choices:` array say how the user declines into `# Unreleased`, which the invariant at `:765` (ALWAYS use `choices` arrays) expects.
- **Failure scenario:** A run without `--version` either shows Phase 1 a version it has not asked for, or asks out of order and improvises the decline option. The operator then approves a plan in Phase 2 that does not show the version the draft will be filed under.
- **Evidence:** `grep -n version` over the command; I read Phases 1–3.
- **Suggested fix:** Ask the version in Phase 1 with a fixed array, for example `["Enter the release version (you'll be prompted)", "File under # Unreleased"]`. Present it in Phase 2's plan list, and make Phase 3 consume it.
- **Source:** review
- **Confidence:** high

### DOC-B-B5 — MINOR — `key-discovery.py`'s GitHub time budget does not bound the searches it claims to bound
- **Where:** `plugins/docs-workflows/scripts/key-discovery.py:18-19` ("GitHub calls stop after a time budget"), `:1056-1090` (the search loop), `:1090-1096` (`started = time.monotonic()` is taken after the searches); spec `docs/superpowers/specs/2026-10-07-key-discovery-design.md:167` ("GitHub calls stop after a 300-second budget")
- **What is wrong:** `GH_BUDGET` is checked only before each `gh pr view`. The clock starts after every `gh search prs` batch has run, and `gh auth status` also falls outside it. Each search can take `GH_TIMEOUT` (30 s), so GitHub time is 30 s for auth, plus 30 s × ⌈keys/6⌉, plus 300 s, plus one more view.
- **Failure scenario:** Take a PRD with many Epics, each also carrying a `workitem_key`: 60 tokens make 10 batches. With slow searches (a 1000-hit page set at 30 s each), the GitHub layer alone runs past 600 s. Add the git scan, and the Bash tool's 600000 ms timeout (`references/key-discovery.md:9`) kills the call. The command then retries with `--no-github` (`key-discovery.md:23`) and loses every pull request it had found, after waiting the whole 10 minutes.
- **Evidence:** I read `github_layer` and `case_the_view_budget_runs_out` (which pins views only).
- **Suggested fix:** Start the budget before `gh_blocker()` and check it before each search batch too, marking the remaining batches `partial`. Or document that the budget covers views only, and bound the searches separately.
- **Source:** spec `docs/superpowers/specs/2026-10-07-key-discovery-design.md` (second amendment)
- **Confidence:** medium. The code path is certain; reaching 600 s needs slow searches.

### DOC-B-B6 — NIT — A repository with an `error` can still carry a non-null `scanned`, against the reference's contract
- **Where:** `plugins/docs-workflows/scripts/key-discovery.py:857-869`, `:1190-1194`; `plugins/docs-workflows/references/key-discovery.md:32`, `:39`
- **What is wrong:** The reference says `error` is set "where it could not be read; `scanned` is then null", and "a repository with an `error` was not read, and is reported as such". In `scan_clone`, `entry["scanned"]` is set from `rev-list` before `_log` runs, so a `git log` failure returns `error` beside an integer `scanned`. A failed probe also sets `entry["error"] = "probe: …"` on a repository whose scan succeeded at zero matches. The command then reports that repository as not read, when it was scanned and only the report-only probe failed.
- **Failure scenario:** A `git log` timeout or failure after a good count, or a failed probe, produces a report line that misstates that repository's reach.
- **Evidence:** I read the code. This was not triggered live; the state needs a git failure between the two calls.
- **Suggested fix:** Reset `scanned` to `None` on a scan failure, and record a probe failure in a separate `probe_error` field.
- **Source:** review
- **Confidence:** medium

### DOC-B-B7 — NIT — The docs page states address rules the command does not have
- **Where:** `plugins/docs-workflows/docs/commands/release-notes.md:21`, `:49`; against `plugins/docs-workflows/commands/release-notes.md:46`
- **What is wrong:** `:49` says "`mode: direct` is rejected outright". No step of the command, and nothing in `workflows-core:addressing`, has a `mode: direct` (`grep -n "mode: direct"` hits only the docs page; the sentence dates from `d3445176`). `:21` says "there is no free-text or `@file` input", and `:49` says the address is "an `@<path>` naming a PRD or Epic folder". The command accepts "an `@<path>` naming a folder or a file inside one" (`:46`).
- **Failure scenario:** A reader learns a non-existent refusal, and believes an `@<path>` to a file is refused.
- **Evidence:** I compared the two files and ran the grep.
- **Suggested fix:** Drop the `mode: direct` clause. Say that an `@<path>` may name the folder or a file inside it, and that the file is an address, not an input.
- **Source:** review
- **Confidence:** high

### DOC-B-B8 — NIT — Phase 6's route array promises a docs link on a PM-phase run, where the run never asks for one
- **Where:** `plugins/docs-workflows/commands/release-notes.md:447`, `:455`; against `:411-412` and `references/release-note-types.md:186-189`
- **What is wrong:** The first option reads "Feature update — titled section with a docs link, under ## Feature updates". On `run_phase: pm` the note "carries no documentation link and the command never asks for one" (`:411-412`).
- **Failure scenario:** On the PM run, the consequence the operator confirms ("with a docs link") is not what the draft gets.
- **Evidence:** I read Phase 6.
- **Suggested fix:** Drop "with a docs link", or make it "a docs link on a dev-phase run".
- **Source:** review
- **Confidence:** high

### DOC-B-B9 — NIT — Two character counts in the changelog guidelines are wrong
- **Where:** `plugins/docs-workflows/references/docs-profiles/changelog-guidelines.md:58`, `:61`
- **What is wrong:** The examples say "107 characters" and "117 characters". The descriptions measure 109 and 119 (Python `len` of each quoted description).
- **Failure scenario:** A writer or reviewer calibrating against the 200-character limit trusts a miscount. The effect is small.
- **Evidence:** `python3 -c "print(len('Clarified information around auto-injection and added a section on filtering hosts based on injection status.'))"` gives 109; the Webhooks line gives 119.
- **Suggested fix:** Correct both counts.
- **Source:** review
- **Confidence:** high

<!-- from part C -->

### DOC-C-B1 — MAJOR — Writing a page by the route page's step 4 breaks the scaffold's `--strict` builds, because nothing regenerates the "never hand-edited" `nav:`
- **Also found as:** DOC-D-B1 (merged here)
- **Where:** `plugins/docs-workflows/references/docs-workflow/scaffold-tree.md:458`, `:464`, `:493-496`, `:640`; `plugins/docs-workflows/docs/docs-workflow.md:95-106`
- **What is wrong:** The scaffold's `mkdocs.yml` sets `strict: true` and `validation: nav: omitted_files: warn` (`scaffold-tree.md:493-496`). It also says "**`nav:` is generated, never hand-maintained.**" (`:458`), and the hard rule is "NEVER hand-edit a generated `nav:`. Change `order:` or `title:` and regenerate (§4)" (`:640`). Only one thing regenerates it: "today that is `/docs-init` when it scaffolds, and `/docs-write`, a later command, is to regenerate it whenever it adds or renames a page" (`:464`). `/docs-write` does not ship. The route page's step 4, "Write the next unit — by hand", says "Create the page under the section its surface belongs to…" and then lists the frontmatter, `unit:`, `evidence:`, `review_by` and the marker (`docs-workflow.md:95-106`). It never says to add the page to either config's `nav:`.
- **Failure scenario:** The operator runs `/docs-init`, then `/docs-audit`, then follows step 4 and adds `docs/guides/place-an-order.md`. The page is in neither `nav:`. MkDocs reports it under `validation.nav.omitted_files` at `warn`, and `strict: true` turns that warning into a failure. The scaffold's own CI step `mkdocs build --strict -f mkdocs.yml`, which is gate 1 (`visibility.md` §6), now fails on every page written by the route. The operator can add a `nav:` entry by hand, which the scaffold forbids and which "vanishes" on the next write, or turn off strict mode, which retires gate 1. The same happens to a page `/document` adds to a scaffolded repo: `commands/document.md` has no `nav` handling (grep finds none).
- **Evidence:** Read `scaffold-tree.md` §4, §5 and §8 and the whole of `docs-workflow.md`. `grep -n '\bnav\b' commands/document.md agents/doc-writer.md` returns nothing that maintains `mkdocs.yml`'s `nav:`. Under MkDocs 1.6, `strict` aborts on any warning, and `validation.nav.omitted_files: warn` logs a page missing from the nav at warning level.
- **Suggested fix:** Give step 4 an explicit procedure: regenerate both `nav:` blocks by §4's rule (sort by `order`, then `title`), or add the entry by §4's rule. Also amend `scaffold-tree.md` §4 and §8 so they allow a §4-rule edit by hand until a regenerating command ships. Alternatively, make `/document` keyed and direct mode regenerate the nav in a profiled MkDocs repository that `/docs-init` scaffolded.
- **Source:** review
- **Confidence:** high on the prose. Medium-high on the MkDocs behaviour; a 2-page mkdocs build would confirm it.

### DOC-C-B2 — MAJOR — `/docs-init` and standalone `/docs-brand` stops after the specs preflight skip the emitter tail, against `specs-repo-git` §4
- **Where:** `plugins/docs-workflows/commands/docs-init.md:36`, `:43`, `:45`, `:86`, `:213`, `:330`; `plugins/docs-workflows/commands/docs-brand.md:19` ("On a standalone run each stop ends the run exactly as written below"), `:89`, `:139`, `:246`, `:364`
- **What is wrong:** `workflows-core:specs-repo-git` §4 (`plugins/workflows-core/references/specs-repo-git.md:567-600`) says: "A run that refuses before it has written anything still runs this tail". The cost entry is written and `commit-artifacts` runs, and "A refusal that skipped the tail would break §11 silently". In `/docs-init`, the specs preflight runs at Phase 0 step 2 (`:32`). After it come `DOCS_INIT_TARGET_NOT_WRITEABLE`, `DOCS_INIT_NOT_A_GIT_WORKTREE`, `DOCS_INIT_TARGET_BELOW_TOPLEVEL`, `DOCS_INIT_EXISTING_DOCS_REPO`, `DOCS_INIT_TOOLCHAIN_INCOMPLETE` and `DOCS_INIT_UNRESOLVED_BLOCKER`. Each is only "stop:". None routes to Phase 8.5 or to the tail (Phases 9–11). Only the Cancels say "the emitter tail (Phases 9–11) still runs" (`:42`, `:98`, `:211`). Phase 11 says "Cost ALWAYS runs — including a run that cancelled at Phase 2.5, and including one whose Phase 7 verification failed" (`:330`) and does not mention the stops. Standalone `/docs-brand` has the same gap: its preflight is at the end of Phase 0, and after it come `DOCS_BRAND_NO_CODE_REPO` (Phase 2), `DOCS_BRAND_NOTHING_TO_APPLY` (Phase 4) and `DOCS_BRAND_UNRESOLVED_BLOCKER` (Phase 9). `/docs-audit` is the counter-example: it routes every stop through the tail explicitly (`docs-audit.md:18`).
- **Failure scenario:** `/docs-init /workspace/docs` is run on a repository that already has `mkdocs.yml`. The specs preflight runs, then `DOCS_INIT_EXISTING_DOCS_REPO` ends the run: no cost entry, no `commit-artifacts`, no `Specs repo:` line. Worse, a run that scaffolded, verified and Opus-reviewed, then hit `DOCS_INIT_UNRESOLVED_BLOCKER` or `DOCS_BRAND_UNRESOLVED_BLOCKER`, records none of that spend.
- **Evidence:** `grep -n 'Phases 9–11\|Phases 12–14\|emitter tail' commands/docs-init.md commands/docs-brand.md` hits only the Cancel paths and the `--inline` skip.
- **Suggested fix:** Add a stop-route paragraph to both commands, as `/docs-audit` has. Every `DOCS_INIT_*` / standalone `DOCS_BRAND_*` stop after the preflight goes to the report and then the emitter tail. Name the pre-preflight exceptions: `DOCS_INIT_UNKNOWN_GENERATOR`, `/docs-brand`'s Phase 0 steps 2–3, and the run-flag stops. Mirror this on both docs pages' Failure modes.
- **Source:** review
- **Confidence:** medium-high. An agent might run the tail anyway, but the text never tells it to.

### DOC-C-B3 — MINOR — `resolve-docs-repo` rung 4's choice is uncapped and has no stated shape, yet `/docs-audit` relies on a Cancel there
- **Where:** `plugins/docs-workflows/references/docs-workflow/repo-resolution.md:29` ("A single hit is taken. Several hits are offered as a choice."), `:30` ("Else ask."); `plugins/docs-workflows/commands/docs-audit.md:32`
- **What is wrong:** Rung 4 searches the unbounded `${REPOS_PATH:-/workspace}` listing, and every hit becomes a choice. No arity rule, cap or overflow row is given, although every other picker over that listing in this plugin applies `workflows-core:epic-picker` *The cap* (`docs-init.md:82`, `docs-brand.md:82-87`, `docs-audit.md:59`, `docs-serve.md:122`). Rung 5's question has no wording at all. `/docs-audit` Phase 0 step 2 says "Where the operator cancels at the ladder's rung 4 choice or its rung 5 question", but neither is defined to carry a Cancel.
- **Failure scenario:** A workspace has five directories carrying a §3 signal. The signal set is deliberately generous: a `*:build` script, `_snippets/`, any Vale config. `/docs-profile`, `/docs-brand`, `/docs-serve` or `/docs-audit` then renders a 5-option `AskUserQuestion`, which the harness rejects (`maxItems: 4`). Separately, `/docs-audit`'s cancel branch depends on an option nobody defined.
- **Evidence:** Read `repo-resolution.md` end to end. `grep -rn 'rung 4\|rung 5'` finds no other definition.
- **Suggested fix:** Give rung 4 epic-picker's shape: auto-select at one, list every hit as prose, then 2–3 rows plus an overflow row. Write out rung 5's question, including a Cancel where callers depend on one.
- **Source:** review
- **Confidence:** medium

### DOC-C-B4 — MINOR — `docs-audit-reviewer` is told to read the site's `docs_dir` from the profile, a field the profile schema does not have
- **Where:** `plugins/docs-workflows/agents/docs-audit-reviewer.md:25` ("**`profile`** — the resolved `docs-profile.yml`, read for the site's `docs_dir`, which is what fixes where the internal tree is for dimension 2's second half.")
- **What is wrong:** `docs-profile-schema.md` has no `docs_dir`. The profile records `spaces[].content_root` (and `builds[].config`), and `grep -n docs_dir references/docs-profiles/docs-profile-schema.md` returns nothing. `docs_dir` is a key in the MkDocs config, not in the profile. Dimension 2's BLOCKER check (`visibility: internal` on a `page_path` outside the internal tree) therefore depends on a value the input cannot supply.
- **Failure scenario:** The reviewer looks for `docs_dir` in the profile and finds none. It may then report dimension 2's second half as "not checked", which silently drops a BLOCKER-class check, or it may guess `docs/`. Either way it does not use the `content_root` that the scaffold records.
- **Evidence:** grepped the schema and the agent.
- **Suggested fix:** Say "read for `spaces[].content_root` (the internal tree is `<content_root>/internal/` on a scaffolded profile)". Alternatively, have it read `docs_dir` from the MkDocs config the profile's `builds[].config` names.
- **Source:** review
- **Confidence:** high

### DOC-C-B5 — MINOR — Live contradiction on branch names: the commands' no-convention form is `<prefix>/NOISSUE-<slug>`, but `branch-naming` §1.4 builds `<prefix>/<slug>`
- **Where:** `plugins/docs-workflows/commands/docs-init.md:94` (`<prefix>/NOISSUE-docs-init`), `docs-brand.md:184` (`<prefix>/NOISSUE-docs-brand`), `docs-profile.md:154`, `:193` (`<prefix>/NOISSUE-docs-profile`, "Else (no convention documented, §1.4)"); against `plugins/workflows-core/references/branch-naming.md:67` ("Only when §1.1 finds nothing: build **`<prefix>/<key>-<slug>`** on a keyed run … or `<prefix>/<slug>` where there is no key") and `:161-163` (the slugs `docs-profile`, `docs-init`, `docs-brand`)
- **What is wrong:** All three commands cite `branch-naming` and its §1.4, but name a different branch from the one §1.4 builds. `/docs-profile` labels its form "§1.4" outright.
- **Failure scenario:** An agent holding both texts gets two answers, `docs/NOISSUE-docs-profile` or `docs/docs-profile`. Different runs, or `/document`'s Phase 6.2 rename logic, can disagree about which branch the command owns. The resume case is one example: `/docs-profile`'s "switch `<name>` if it already exists".
- **Evidence:** read both texts.
- **Suggested fix:** Either change the three commands to §1.4's `<prefix>/<slug>`, or add the no-issue literal to §1.4 for keyless docs runs. Do this in one edit, and sweep `docs/` pages that name the branch.
- **Source:** review
- **Confidence:** medium. The commands may mean to override; if so, they should say so rather than cite §1.4.

### DOC-C-B6 — MINOR — The `/docs-init` docs page says the domain vocabulary is "a later command's job", but the authority says no command writes it
- **Where:** `plugins/docs-workflows/docs/commands/docs-init.md:51` ("that seed is only what the scaffold needs to pass its own gate, and the product's domain vocabulary is a later command's job.")
- **What is wrong:** `scaffold-tree.md:632` says "**The domain seed — nobody's, and added by hand.** **No command of this family extracts a product's domain nouns, and nothing adds to this file after `/docs-init` writes the seed above**, `/docs-audit` included". The command body (`commands/docs-init.md:128`, `:283`) and `docs-scaffold-reviewer.md:55` say the same. The docs page promises a command that does not exist. This is a claim-expiry leftover: the intended "later command" (`/docs-audit`) shipped without the behaviour.
- **Failure scenario:** A reader waits for, or looks for, a command to seed `accept.txt` instead of adding terms by hand, and Vale flags every product noun as a spelling error.
- **Evidence:** `grep -rn "later command's job" plugins/docs-workflows/docs` returns only this line.
- **Suggested fix:** "…and the product's domain vocabulary is added by hand — no command of this family extracts it (`scaffold-tree.md` §7)."
- **Source:** review
- **Confidence:** high

### DOC-C-B7 — MINOR — The `/docs-profile` docs page claims detection of "cross-space override manifests" and "shared registries", which the command never scans
- **Where:** `plugins/docs-workflows/docs/commands/docs-profile.md:27` ("a Sonnet-tier detection pass (mechanical repo scanning — package scripts, cross-space override manifests, shared registries, templating tokens, …)")
- **What is wrong:** The command's Phase 2 brief (`commands/docs-profile.md:92-98`) lists seven items: package.json scripts, templating tokens, content/snippet roots, branch-naming and internal-link conventions, image policy, prerequisites, and announcement pages. It has no override manifest or registry item, and neither does the schema. CLAUDE.md requires each docs-page claim to be derived from the thing that runs it.
- **Failure scenario:** An operator expects the profile to capture override manifests or registries, and nothing records them.
- **Evidence:** `grep -rn 'override manifest\|shared registr' plugins/docs-workflows` matches only this docs line.
- **Suggested fix:** Replace the list with Phase 2's seven items.
- **Source:** review
- **Confidence:** high

### DOC-C-B8 — MINOR — `/docs-init`'s Phase 6 leaves `spaces[].id` and `dev_servers.servers[].space` unstated
- **Where:** `plugins/docs-workflows/commands/docs-init.md:159` ("**`spaces[]`** — exactly one entry, `content_root: docs`, `snippet_root: docs/_snippets`."), `:161`
- **What is wrong:** The schema's `spaces[]` entry carries `id` (and `base_path`): see the template at `docs-profile-schema.md:31`, `/docs-profile` Phase 3's "(`id`, `content_root`, `snippet_root`, `base_path`)" at `docs-profile.md:118`, and the default profile. `dev_servers.servers[]` entries key on `space`, and `commands.per_space`, `frontmatter.owners_spaces` and `/docs-serve`'s lookup (`docs-serve.md:243`) all key on the space id. Phase 6 fixes every other value of the scaffolded profile but leaves the id to whatever the agent invents. So two scaffolds can differ, and the two server entries could even carry different `space` values.
- **Failure scenario:** One run writes `id: docs`, another `id: main`. A two-server profile whose servers name different `space` values breaks `/docs-serve`'s lookup filter, which keys on `space` and `visibility` (Phase 7, step 1).
- **Evidence:** read Phase 6 and the schema template.
- **Suggested fix:** Fix `id: docs` (and `base_path: /`) in Phase 6, and `space: docs` on both server entries.
- **Source:** review
- **Confidence:** medium

### DOC-C-B10 — NIT — `/docs-serve`'s invariant lists its `workflows-core` citations as "`epic-picker` and `next-phase-offer`", omitting `run-flags` and the new `escalation-rules core` load
- **Where:** `plugins/docs-workflows/commands/docs-serve.md:300` ("every `workflows-core:<name>` citation — `epic-picker` and `next-phase-offer` — is loaded through … `next-phase-offer` by part"); against `:22` (`run-flags strip-run-flags`) and `:24` (`escalation-rules core`, added in 1.18.0)
- **What is wrong:** The list is exhaustive in form but incomplete, and it says that only `next-phase-offer` loads by part, while `escalation-rules` is also requested by part at `:24`. This is a claim-sweep miss from the 1.18.0 **Load the question rules.** change.
- **Failure scenario:** A maintainer or agent trusts the list. Cosmetic in effect.
- **Evidence:** read lines 22, 24, 300.
- **Suggested fix:** Name all four (`run-flags`, `escalation-rules`, `epic-picker`, `next-phase-offer`), with `escalation-rules` and `next-phase-offer` by part, or drop the enumeration.
- **Source:** review
- **Confidence:** high

### DOC-C-B11 — NIT — The backlog page reads `threshold` as "at or above", where the schema and the route say "at or below" the priority number
- **Where:** `plugins/docs-workflows/docs/reference/docs-backlog.md:24` ("`threshold` | The priority at or above which "done" applies")
- **What is wrong:** `backlog-format.md` uses "done = every unit with priority <= threshold", and the route page says "Every unit whose `priority` number is at or below the backlog's `threshold`" (`docs/docs-workflow.md:226`). "At or above" can only be squared with that by reading priority as rank, the inverse of the number the file stores.
- **Failure scenario:** A reader sets `--threshold` the wrong way.
- **Suggested fix:** "The priority number at or below which…"
- **Source:** review
- **Confidence:** medium

### DOC-C-B12 — NIT — The workflow page says `/docs-serve` writes "only a pid/port record", but the command writes three things
- **Where:** `plugins/docs-workflows/docs/workflow.md:83` ("`/docs-serve` writes only a pid/port record under that same `.dev-workflows/`")
- **What is wrong:** The command says "The only things it writes itself are three": the state file, one line in the repository's local `info/exclude`, and a `dw-serve-*` log per start (`commands/docs-serve.md:32`). The command page states the exclude line (`docs/commands/docs-serve.md:24`).
- **Suggested fix:** Add "and, where nothing ignores it, one line in the repository's local `.git/info/exclude`".
- **Source:** review
- **Confidence:** high

<!-- from part D -->

## field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs

### FBA-B1 — MINOR — A stale remote-tracking ref forces a `-2` suffix on every handoff branch whose earlier PR merged with delete-on-merge
- **Also found as:** FBB-B42 (merged here)
- **Where:** `plugins/workflows-core/references/phase-handoff.md:57-64` (§2.2 rules 1, 3, 4), `plugins/workflows-core/references/specs-repo-git.md:307` (the only fetch)
- **What is wrong:** Rule 1 tests "`git -C "$SPECS_PATH" rev-parse --verify --quiet refs/heads/<name>` and `… refs/remotes/origin/<name>`". Rule 3 finds such a ref merged and refuses to reuse it, and rule 4 then "append[s] the lowest free integer suffix, starting at `-2`". The preflight's only fetch is "`fetch origin <default>`" (specs-repo-git.md:307), with no `--prune` and no probe of the host. So a `refs/remotes/origin/<name>` whose remote branch GitHub deleted on merge stays in the clone indefinitely and counts as "exists".
- **Failure scenario:** A slice's `/brd-intake` or `/brd-split` PR merges, and GitHub deletes the branch. The next `/brd-*` handoff on that slice wants `brd/<KEY>-<slug>`, which is free on the host. The stale tracking ref still makes rule 1 report it as existing, so the run names the branch `brd/<KEY>-<slug>-2`. This happens on every later handoff for that key. Two slices reproduced it in one session (BOOK-2-01 and BOOK-2-02).
- **Evidence:** I read §2.2 end to end and grepped specs-repo-git.md and phase-handoff.md for `prune` and `ls-remote` on a collision path. The only `prune` mention is the renamed-default-branch note at specs-repo-git.md:297.
- **Suggested fix:** In rule 1, when only `refs/remotes/origin/<name>` exists and no local branch backs it, confirm it with `git ls-remote --exit-code --heads origin refs/heads/<name>`, the probe §4 step 5 already uses. Treat a ref the host lacks as absent, and optionally delete the stale tracking ref (`git update-ref -d`).
- **Source:** feedback `BOOK-2-02-brd-split-stale-tracking-ref-branch-suffix` in F3
- **Confidence:** high

### FBA-B2 — MINOR — Merged local plugin branches the run is not standing on are never deleted, so they pile up and force suffixes
- **Where:** `plugins/workflows-core/references/specs-repo-git.md:409-420` (§3.4 retry walk), `:436` (B2 deletes only `HEAD`'s branch)
- **What is wrong:** B2 runs `branch -d` only on the plugin branch `HEAD` stands on. §3.4's walk over "every other local plugin branch" runs `branch-merged` only as a reason not to push: "`branch-merged` (§3.5) does not find it merged … Where a test fails, nothing is pushed and nothing is printed". No row deletes a merged plugin branch that `HEAD` is not on.
- **Failure scenario:** Over a pipeline (idea → prd → ard → spec), each merged `idea/…` or `prd/…` branch stays local unless a later run happened to start on it. On BOOK-2, the merged `brd/<KEY>-<slug>` stayed because the preflight started on main (row B1). Rule 4 of phase-handoff §2.2 then named the next run's branch `…-2`, and every later `/brd-*` handoff on that BRD will need a suffix until someone deletes the ref by hand.
- **Evidence:** I read §3.4 and §3.5 in full. `grep -n "branch -d"` in specs-repo-git.md finds it only in B2.
- **Suggested fix:** In §3.4's retry walk, when `branch-merged` finds a listed plugin branch merged by its first test (ancestry), delete it with `branch -d` (never `-D`), using B2's read-only-config handling, and print one `Specs preflight: deleted merged <branch>` line. For a rebase or squash merge, print B2's `branch -D` advice line rather than delete.
- **Source:** feedback `BOOK-1-epics-preflight-stale-merged-branches` in F1; feedback `BOOK-2-brd-split-merged-local-branch-forces-suffix` in F2
- **Confidence:** high

### FBA-B3 — MINOR — `/create-ard`'s optionality advisory fires "for a small single-repo item" with "small" never defined
- **Where:** `plugins/product-workflows/commands/create-ard.md:229-237`
- **What is wrong:** The text says: "Gauge size and, for a small single-repo item, note 'an ARD may be optional here' and offer — adding, on a PRD-level run where `enumerate-components` … finds two or more code components in that one repository, that a PRD touching two of them is multi-component…". The step defines the gauge (the union of user stories, decisions, findings and repositories) but sets no threshold on it. The multi-component sentence hangs off the advisory, so it prints only when the undefined "small" test passes.
- **Failure scenario:** A single-repo PRD with 6 stories and 17 ACs reaching six code components of one repository: the orchestrator has to judge whether the advisory fires. If it judges "not small", it never says that the PRD is multi-component and that `/epics` will require the ARD.
- **Evidence:** I read Phase 0 step 5 in full. No number or comparison follows "small".
- **Suggested fix:** State a threshold on the union gauge. Make the multi-component case its own branch: two or more code components touched means not small, no optionality offer, and one line saying so.
- **Source:** feedback `BOOK-1-create-ard-optionality-advisory-small-undefined` in F1
- **Confidence:** high

### FBA-B4 — NIT — `/brd-intake`'s "byte-for-byte" copy does not exclude the source's mode bits
- **Where:** `plugins/product-workflows/commands/brd-intake.md:386-391` (Phase 2)
- **What is wrong:** The step says: "copy `@<brd-file>` **verbatim, byte-for-byte** into `<BRD-dir>/brd/source/<basename>`". It says nothing about permissions, and nowhere under `plugins/product-workflows/` normalises them (`grep -rn "chmod\|0644\|file mode"` finds only scripts).
- **Failure scenario:** The source comes from a mount whose files are mode 777, and a mode-preserving copy commits `brd/source/*.md` and `*.svg` as 100755. That is noise in the specs history, though not data loss.
- **Evidence:** Grep, plus a read of Phase 2's copy paragraph.
- **Suggested fix:** Say that "byte-for-byte" covers content only. Copy without preserving mode (`cp` without `-p`, or `install -m 0644`) under both `brd/source/` and `brd/source-external/`.
- **Source:** feedback `BOOK-2-brd-intake-copy-carries-source-file-mode` in F2
- **Confidence:** high

### FBA-B5 — NIT — `/brd-split`'s *Assign to a named slice* key prompt: no rule for asking it in the same call, and no pre-fill from the Phase 1.5 placement
- **Where:** `plugins/product-workflows/commands/brd-split.md:893` (picker), `:1015-1017` (the key prompt)
- **What is wrong:** The text says: "**Assign to a named slice** … → prompt for the slice's key: any created in Phase 3 this run, or any found already nested … Reject a key that resolves to neither and re-prompt". `<recommended>` already marks `covered-by` where Phase 1.5 placed the row (`:946-948`), but the key prompt that follows does not offer that placement's key as its default. The command also does not say whether the key may be asked in the same `AskUserQuestion` call as the disposition, or how the re-prompt validation applies when it is.
- **Failure scenario:** A 19-row walk takes 38 prompts even though every row's target is already fixed by the instruction. An orchestrator that folds the two questions into one call is improvising validation.
- **Evidence:** I read Step 2 and the `<recommended>` resolution table.
- **Suggested fix:** Where Phase 1.5 placed the row and Phase 2 keyed its group, ask the key as a picker whose first option is that child's key (Recommended), or state that the fold is allowed and validated as the separate prompt is.
- **Source:** feedback `BOOK-2-brd-split-slice-key-second-prompt-unspecified` in F2
- **Confidence:** medium

### FBA-B6 — NIT — `/prd-ground` Phase 0 does not say which of `specs-repo-git` §3's two orders it takes
- **Where:** `plugins/product-workflows/commands/prd-ground.md:128-131` (step 4, preflight) against `:61` (step 1, `read-key`) and `:132` (step 5, `resolve-address`); `plugins/workflows-core/references/specs-repo-git.md:250-255`
- **What is wrong:** §3 gives two orders: resolve first where the key set comes from resolution, or preflight first where it is "the keys … `read-key` reads off its arguments". `/prd-ground` runs the preflight before resolving, which is correct for the second case, but never says its run key set is what `read-key` read at step 1. It also does not say whether the `--depends-on` and `--from-split` keys, also read with `read-key` (`:64`, `:80`), belong to that set. That matters for B3/B4 branch disposition.
- **Failure scenario:** An orchestrator has to reconcile the two texts itself. One that adds the `--depends-on` keys to the set would keep the run on another BRD's branch (B3).
- **Evidence:** Lines read. `grep -n "run key set"` in prd-ground.md finds nothing.
- **Suggested fix:** Add one sentence to step 4: "the run key set is the `<BRD-KEY>` step 1 read with `read-key` (never a `--depends-on` or `--from-split` key), so §3's preflight-first order applies."
- **Source:** feedback `BOOK-2-02-prd-ground-preflight-key-set-order` in F3
- **Confidence:** medium

### FBA-B7 — MINOR — A repo-local instruction file or README is not named as a "documentation page" in the no-doc-evidence rule, and the grounding agents' evidence contract does not exclude it
- **Where:** `plugins/product-workflows/commands/prd-ground.md:972-986`; `plugins/product-workflows/agents/code-grounder.md:230-236`; `plugins/product-workflows/agents/grounding-verifier.md:258-264`
- **What is wrong:** The rule reads: "**No `[CG#n]` or `[DG#n]` may cite a documentation page in its `evidence`**", and it is enforced by "the digest is **not** passed into `code-grounder` … or `grounding-verifier`". Those agents still read the repository, and their only mention of `CLAUDE.md`/`AGENTS.md` treats them as untrusted content ("no instruction file adds a task or changes a verdict"), not as files barred from evidence. A repository's `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md` or `README` is a document about behaviour inside the repo, and nothing says it counts as one.
- **Failure scenario:** The blind derive for BR#19 (FALSE-FRIEND) cited the code repo's `CLAUDE.md:79` as evidence. The orchestrator had to exclude it by judgement, and sibling slice BOOK-2-01 made the same call independently. A different orchestrator could keep it, putting a stale doc claim into a `[CG#n]`.
- **Evidence:** Grep for `README|CLAUDE.md|AGENTS.md|documentation` across the three files and `grounding-format.md`. None of the hits is an evidence exclusion.
- **Suggested fix:** Name repo-local instruction files, READMEs and other prose docs (`*.md` and `docs/`) explicitly in prd-ground's rule. State in both agents' evidence rules that such a file is never evidence: at most a lead to code that is.
- **Source:** feedback `BOOK-2-02-prd-ground-repo-instruction-files-as-docs` in F3
- **Confidence:** high

### FBA-B8 — MINOR — `grounding-format` §3 has no verdict rule for a premise that is vacuously true because its surface does not exist
- **Where:** `plugins/workflows-core/references/grounding-format.md:399-410` (verdict table), `:442-479`
- **What is wrong:** `AMENDED` is "Partly true; the finding states the correction" and `REWRITTEN` is "The premise is materially wrong". Nothing covers a rule about a surface the pinned commit lacks ("a not-for-sale book is never suggested" where no suggestions exist). The later *A claim that restricts a value* subsection does not cover it either.
- **Failure scenario:** On BOOK-2-02, `code-grounder` classed BR#13, 14, 17 and 18 all `AMENDED`, while the blind derive classed 13/14 `AMENDED` and 17/18 `REWRITTEN`. The compare `contradict` branch then rewrote 17/18, so one corpus carries two verdicts for the same shape of premise, decided by which side ran last.
- **Evidence:** I read §3 in full. `grep -i "vacuous\|does not exist\|non-existent"` finds no verdict rule.
- **Suggested fix:** Add a paragraph after the verdict table that fixes the verdict for a rule about a non-existent surface (for example `AMENDED`, with the correction "the surface does not exist at <commit>; the rule is a requirement on new work"), with BR#13/14 against 17/18 as the worked pair. Have both agents cite it.
- **Source:** feedback `BOOK-2-02-prd-ground-vacuous-surface-verdict` in F3
- **Confidence:** medium (the fix is a design choice; the gap is certain)

### FBA-B9 — NIT — A re-asked handoff consent choice leaves two contradictory `Phase handoff:` outcome lines
- **Where:** `plugins/workflows-core/references/phase-handoff.md` §4.1
- **What is wrong:** Nothing in §4.1 says that a consent choice asked again in the same run supersedes the outcome line already printed for that offer. `grep -i "supersede\|re-ask\|asked again"` in phase-handoff.md finds nothing on the subject.
- **Failure scenario:** The user picks "Just write the files", interrupts, and on the re-ask picks the branch+PR option. The transcript and the final report then carry both *Declined by the user* and the pushed outcome for one offer.
- **Evidence:** Grep. The feedback itself says the evidence that the command caused this is thin.
- **Suggested fix:** Add one sentence to §4.1: a re-asked consent choice supersedes the earlier outcome line, and the Final report repeats only the last one.
- **Source:** feedback `BOOK-2-02-prd-ground-handoff-reask-outcome-line` in F3
- **Confidence:** low

## field feedback — BOOK-2-01 runs

### FBB-B1 — MAJOR — `/prd-proposal` writes `proposal-profile.yml` and calls it committed, but nothing ever stages it
- **Where:** `plugins/product-workflows/commands/prd-proposal.md:290`, `:345` (calls it "a committed `proposal-profile.yml`"); `:693` (`deliverable_paths` = `proposal.md`, `proposal-brief.md`, archived priors only); `plugins/workflows-core/references/specs-repo-git.md` §2.1 (no `.dev-workflows/` path; `grep -n '\.dev-workflows' specs-repo-git.md` returns nothing); `brd-proposal.md:447`.
- **What is wrong:** The profile is read back by every later `/prd-proposal` and `/brd-proposal`, and the prose calls it committed. However, neither the handoff nor `commit-artifacts` stages it.
- **Failure scenario:** A first proposal run grills a profile into `$SPECS_PATH/.dev-workflows/proposal-profile.yml`. The handoff commits only the proposal, and `commit-artifacts` treats the profile as outside its bounded paths. The profile stays untracked, so a teammate's clone has none and their `/brd-proposal` stops with `BRD_PROPOSAL_NEEDS_PROFILE`.
- **Evidence:** I read the lines above and grepped both files.
- **Suggested fix:** Add `.dev-workflows/proposal-profile.yml` to `deliverable_paths` whenever Phase 2 grilled or corrected the profile, in both proposal commands. Alternatively, add it as a single-file path in §2.1.
- **Source:** feedback `prd-proposal-profile-not-committed` in `BOOK-2-01-feedback.md`
- **Confidence:** high

### FBB-B2 — MINOR — `consumed_by` is single-valued, so `/specify` overwrites the ARD's consumption record
- **Where:** `plugins/workflows-core/references/grounding-format.md:57` ("one of `PRD | ARD | specification | none`"), `:86`; `plugins/product-workflows/commands/specify.md:271` ("write `consumed_by: specification` back there").
- **What is wrong:** A finding the ARD drew on and the spec then drew on loses `ARD`. The route's "nothing was lost" tracking for the earlier consumer then cannot be checked. Nothing states that the overwrite is intended.
- **Failure scenario:** On the live run, nine `[CG#n]` went from `ARD` to `specification`.
- **Evidence:** I read the lines above.
- **Suggested fix:** Make `consumed_by` a list that is appended to, or state the overwrite and its loss in each stamping paragraph.
- **Source:** feedback `specify-consumed-by-overwrites-provenance` in `BOOK-2-01-feedback.md`
- **Confidence:** high

### FBB-B3 — MINOR — The pre-lint placeholder scan flags literal code, markup and display formats, even in fenced blocks
- **Where:** `plugins/workflows-core/references/pre-lint.md:18-26` (Universal check 1; it has no fenced-block or inline-code exclusion, while the auto-link check at `:44` has one).
- **What is wrong:** `<fieldset>`, `EventEmitter<number>`, `(<n> ratings)` and a lowercase `<b>` fixture are all BLOCKER "placeholders". In particular, a fenced code block that *is* the design's decision cannot reach zero BLOCKERs.
- **Failure scenario:** A frontend `/design` or `/specify` run must reword correct content around the regex, or label false positives by hand.
- **Evidence:** I read `pre-lint.md:18-26` and `:44`.
- **Suggested fix:** Exclude fenced blocks, and possibly inline code spans, from check 1. Keep the "do not widen" note and a fixture that proves a prose placeholder is still caught. Document how to write a display format with a variable part.
- **Source:** feedback `specify-pre-lint-placeholder-literal-format`, `specify-pre-lint-flags-markup-fixture`, `design-pre-lint-placeholder-flags-code` in `BOOK-2-01-feedback.md`
- **Confidence:** high

### FBB-B4 — MINOR — `/create-prd`'s own route template fails its own pre-lint
- **Where:** `plugins/product-workflows/commands/create-prd.md:648`, `:704`, `:915` (`/product-workflows:brd-reconcile <SLICE-KEY> @<review-file>` is to be written into `prd.md`); `pre-lint.md:18` (placeholder regex), `:44-45` (inline code is not exempt from the auto-link grep).
- **What is wrong:** When the instructed route string is written into the PRD, it trips two BLOCKERs: `<review-file>` is read as a placeholder, and the slice key in inline code is read as an auto-link.
- **Failure scenario:** On the BRD route, a contradiction with a `[CD#n]` is recorded, pre-lint blocks it, and the run drops the exact command.
- **Evidence:** I read both files.
- **Suggested fix:** Say how the route is written inside the PRD (the bare command, with the key and file named in words), or exempt the canonical template.
- **Source:** feedback `create-prd-route-template-fails-pre-lint` in `BOOK-2-01-feedback.md`
- **Confidence:** high

### FBB-B5 — MINOR — `prd-format` does not say how `[AC#N]` are grouped, and the natural reading trips the duplicate-id BLOCKER
- **Where:** `plugins/workflows-core/references/prd-format.md:139` ("`[AC#N]` under each story").
- **What is wrong:** Repeating the `### [US#N]:` headings under `## Acceptance Criteria` defines each story twice.
- **Failure scenario:** The pre-lint duplicate-id check raises a BLOCKER, and the fix (a bold `**[US#N] title**` label) can be found only by reading another PRD.
- **Evidence:** I read `prd-format.md:139` and found no grouping rule.
- **Suggested fix:** Add one line with an example, and have pre-lint's duplicate message name the fix.
- **Source:** feedback `create-prd-ac-grouping-unspecified` in `BOOK-2-01-feedback.md`
- **Confidence:** high

### FBB-B6 — NIT — `/create-prd` Phase 1 step 1 says "Confirm" but gives no choices array
- **Where:** `plugins/product-workflows/commands/create-prd.md:384` (Phase 1 step 1).
- **What is wrong:** The run improvises the confirmation picker, and a bare "Correct something" answer comes back carrying no text.
- **Failure scenario:** Three question rounds were needed to learn that the correction was the profile.
- **Evidence:** I read Phase 1 (`:380-417`). Only the overwrite and profile pickers carry arrays.
- **Suggested fix:** Add an array such as `["Proceed (Recommended)", "Change the profile (--full / --hybrid / --lean)", "Cancel"]`.
- **Source:** feedback `create-prd-phase1-confirm-no-choices` in `BOOK-2-01-feedback.md`
- **Confidence:** high

### FBB-B9 — MINOR — `proposal-format` §6 makes a false claim about rounding
- **Where:** `plugins/product-workflows/references/proposal-format.md:246-247` ("Whole-hour rounding moves a band by up to a point").
- **What is wrong:** On a 38 h Medium package, the low end of 30.4 rounds to 30, which is −21.05 %. That is more than a point off the band, so the rule fires on arithmetic alone. The rendering precision of Low and High is unstated.
- **Failure scenario:** A default band on a small package fails the one-point tolerance.
- **Evidence:** I read `:246-247`. There is no precision rule.
- **Suggested fix:** State the precision (for example, one decimal place) and the true bound (about 0.5 h ÷ the expected hours). Optionally, have `proposal-record.py` re-derive the bands.
- **Source:** feedback `prd-proposal-band-rendering-precision` in `BOOK-2-01-feedback.md`
- **Confidence:** high

### FBB-B13 — MINOR — The fix-cycle overlap read is too narrow: it misses imported rules and new outcomes added to an existing trigger
- **Where:** `plugins/workflows-core/references/escalation-rules.md:570-606` (*An inline fix is read against what it overlaps*). It reads requirements "whose trigger, precondition, state or figure overlaps"; it lists no importers-by-reference and no outcome-set enumeration. `plugins/workflows-core/references/pre-lint.md:76-83` (the spec block checks only headings, ID contiguity and the open-question count).
- **What is wrong:** Three `/specify` runs on this PRD spent their review cap on one defect class. In the first, a criterion imports "every rule of a change", so the changed rule reaches `POST`. In the second, a new outcome is added to a trigger's implicit outcome set, but sibling criteria keep their old wording. Neither case reads as an overlap. No deterministic check of category coverage or required inputs exists either.
- **Failure scenario:** The re-review finds BLOCKERs the fix or the draft itself wrote. The cap is spent, so the spec ships under unreviewed manual notes.
- **Evidence:** I read both sections.
- **Suggested fix:** (1) Widen the overlap set to cover importers and the rules they import. (2) Add an outcome-set read (per trigger, list every outcome and check that each has a criterion and a stated precedence) at the Stage 4 gate, before the first review and after the fix cycle. (3) Add an advisory to pre-lint's spec block that lists cross-criterion imports, and add per-AC Happy-path and Negative coverage checks.
- **Source:** feedback `specify-fix-cycle-unverified-overlaps`, `specify-overlap-read-misses-inherited-rules`, `specify-precedence-and-inheritance-playback`, `specify-new-outcome-siblings-unqualified` in `BOOK-2-01-feedback.md`
- **Confidence:** high

### FBB-B15 — MINOR — The version line after a verdict names no requirement whose Rule changed after the verdict
- **Where:** `plugins/workflows-core/references/escalation-rules.md:444-460` (*A recorded verdict names the version it was taken against*: "names the edits", with no requirement to list changed `[AD#N]`/contract rows or `[Uxx] [ACxx]` ids apart from rewording); `plugins/product-workflows/commands/create-ard.md:712`; `/specify` Phase 6; `/design`.
- **What is wrong:** A pull-request reviewer cannot tell which decisions or criteria changed after the last verdict without diffing.
- **Failure scenario:** In `/create-ard`, `[AD#2]`'s lookup changed after the capped re-review. In `/specify`, ten edits were applied after a PASS WITH RECOMMENDATIONS. In `/design`, post-review MINOR edits were made. Each shipped only with "the current text has not been reviewed".
- **Evidence:** I read `escalation-rules.md:444-470`.
- **Suggested fix:** List, by id, every decision, contract row or criterion whose substance changed after the last verdict, separately from editorial edits. Put the list in the final report, the session record and `body_facts`, for example under a `## Unreviewed edits` heading.
- **Source:** feedback `create-ard-post-cap-decision-edits-unreviewed`, `specify-post-verdict-edits-unlisted`, `design-post-recommendation-edits-unreviewed` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B17 — MINOR — `/epics` asks keep-whole only after `epic-writer` has already split by size
- **Where:** `plugins/product-workflows/commands/epics.md:648` (step 1's handoff carries `scope` from Phase 2 only), `:662-672` (step 4's split / keep-whole question comes after the writer returns).
- **What is wrong:** The writer splits over-limit work unless `scope` carries keep-whole, which only a Phase 2 *Revise* supplies. So the planned "split or keep whole" question is moot by the time it is asked.
- **Failure scenario:** On a two-component PRD with 62 folded criteria, both Epics would have been split before the operator was asked.
- **Evidence:** I read Phase 6 at `:641-675`.
- **Suggested fix:** Add a pre-dispatch size estimate that asks the step-4 question, with the reason in the same prompt, and passes a keep-whole answer through `scope`.
- **Source:** feedback `epics-keep-whole-asked-after-writer-splits` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B18 — MINOR — `code-scanner` line numbers are not validated
- **Where:** `plugins/workflows-core/agents/code-scanner.md:63` (`lines` come from grep hits); no post-scan bound check anywhere.
- **What is wrong:** The scan cited lines 376–382 of a 21-line file. The scanner apparently numbered lines across a concatenated read, and nothing catches it.
- **Failure scenario:** Invented `file:line` evidence reaches `epic-writer` and `epic-reviewer`. The orchestrator stripped every line number, losing the valid ones too.
- **Evidence:** I read `code-scanner.md:63-96`. It has no `wc -l` check.
- **Suggested fix:** Bound each `lines` value by `git show <ref>:<path> | wc -l` in the scanner's output step, or in a shared post-scan check.
- **Source:** feedback `epics-code-scanner-line-numbers-out-of-range` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B19 — MINOR — The pre-lint auto-link branches leave a bare specs key in limbo, and `epic-writer` writes keys bare
- **Where:** `plugins/workflows-core/references/pre-lint.md:44-50`. Branch 2 says "confirm the key with the author before wrapping"; a specs-tree key is neither a tracker ticket nor a standard. `plugins/product-workflows/agents/epic-writer.md` wraps only `Parent PRD` and `Consumes` keys (`:103`, `:113`).
- **What is wrong:** Every sibling-Epic or slice key `epic-writer` writes in prose is a BLOCKER that needs author confirmation, although `[[KEY]]` is the specs tree's required traceability form.
- **Evidence:** I read both files.
- **Suggested fix:** Have `epic-writer` wikilink every specs key it cites. State that a key that resolves via `addressing` §3 is wrapped without confirmation.
- **Source:** feedback `epics-pre-lint-autolink-flags-specs-keys` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B20 — MINOR — `/epics` `body_facts` makes a false claim on the falling-back handoff
- **Where:** `plugins/product-workflows/commands/epics.md:836` (`body_facts` … "the next command — `/product-workflows:specify <EPIC>`, which will not run until this pull request is merged"), against `:831` (the stopping array applies only where the run edited a merged `epic.md`).
- **What is wrong:** For all-new Epics, the class is gated — falling back. `/specify` then reads the working copy, so the sentence written into every pull request is false.
- **Evidence:** I read `:825-838`.
- **Suggested fix:** Derive the sentence from the same class that selects the consent array.
- **Source:** feedback `epics-handoff-body-next-command-claim` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B22 — NIT — `/epics` does not pass house style to `prose-style-checker`
- **Where:** `plugins/product-workflows/commands/epics.md:713-753` (Phase 6.2). `prose-style-checker` accepts `rules_path` (`plugins/prose-style/agents/prose-style-checker.md:32`), but `/epics` passes none.
- **What is wrong:** The tree's house spellings ("e-mail", "catalogue") generated 18 NITs that nothing acts on.
- **Suggested fix:** Pass the specs repository's overlay, or the PRD folder's conventions.
- **Source:** feedback `epics-prose-style-nits-on-house-spelling` in `BOOK-2-01-feedback.md`
- **Confidence:** low

### FBB-B24 — MINOR — The `/design` fan-out brief carries no spec literals, surviving surface or settled values
- **Where:** `plugins/dev-workflows/commands/design.md:360` (`problem_frame: [what the interface is for, the constraints any proposal must satisfy, the seam it sits at]`).
- **What is wrong:** 1df8630c added a check of the recommendation against `problem_frame` and the `[AD#N]` Rules (`:378-386`). However, `problem_frame` is still not required to quote the `[Uxx]`/`[ACxx]`/`[TCxx]` lines, the public surface that must survive (with its callers), or the grill values the interface depends on. So that check cannot catch a take that breaks them.
- **Failure scenario:** A take rendered "4" where `[TC02]` says "★ 4.0" and dropped `getRatingById`, which a caller still needs.
- **Evidence:** I read `:355-392`.
- **Suggested fix:** Require those items in `problem_frame`, and check each take against them before the comparison.
- **Source:** feedback `design-fanout-brief-lacks-spec-literals` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B27 — NIT — The `/conformance` walk's question and rationale cadence is unstated
- **Where:** `plugins/dev-workflows/commands/conformance.md:262` (one call per item, then a rationale prompt after each decision). Compare `:116`, where up to four questions share a call.
- **What is wrong:** It is unclear whether items may share a call and whether a rationale may be a note on the choice. Six items cost twelve round trips.
- **Suggested fix:** State the rule explicitly either way.
- **Source:** feedback `conformance-walk-batching-ambiguous` in `BOOK-2-01-feedback.md`
- **Confidence:** low

### FBB-B28 — MINOR — The `conformance-tracer` handoff has no file input or output for large runs, and its evidence may use loose ranges
- **Where:** `plugins/dev-workflows/references/handoff/conformance-tracer.md` (requirements inline only; no `requirements_path` or `output_path`; the evidence rule at `:47` allows any range).
- **What is wrong:** With 77 or 88 requirements, the orchestrator scripted the input file and scraped the agent transcript to recover the output. The `## Satisfied` evidence used approximate ranges.
- **Suggested fix:** Add `requirements_path` above a threshold, and `output_path`. Require exact `file:line` or a tight range.
- **Source:** feedback `conformance-tracer-requirements-file`, `conformance-tracer-output-handoff` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B29 — MINOR — `not-checkable` requirements are count-only in `_conformance.md`, yet `/conformance` relies on them being recognisable later
- **Where:** `plugins/dev-workflows/references/conformance-format.md:27` (the header count only; the lists are `## Satisfied`, `## Unverified` and `## Discrepancies`); `plugins/dev-workflows/commands/conformance.md:136` (a later run traces a requirement that was "`not-checkable` there" in full).
- **What is wrong:** A reader cannot tell which requirements were not checkable, or why.
- **Evidence:** I read both files.
- **Suggested fix:** Add an optional `## Not checkable` list with the tracer's `reason`, or state that the count alone is intended.
- **Source:** feedback `conformance-not-checkable-unrecorded` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B32 — MINOR — Step 7.5 writes an open `- [ ]` note for a deferral the user decided in the same run
- **Where:** `plugins/dev-workflows/commands/implement.md:1018` (every unresolved `missing`/`contradicts` gets a note), against `plugins/dev-workflows/agents/code-review.md:245-247` (a `missing` with a recorded deferral is a `MINOR` flagged note).
- **What is wrong:** A decided deferral (the plan's Out of scope, or an ARD deviation) raises the spec's Open questions from 0 to 1.
- **Suggested fix:** Exempt a recorded deferral, or write a closed "deferred by decision" note that the open-question count does not include.
- **Source:** feedback `implement-deferral-forced-open-note` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B34 — NIT — `risk-planner` acceptance checks are not required to use fixed-string grep
- **Where:** `plugins/dev-workflows/agents/risk-planner.md:119-120` (`### Acceptance checks` — "[concrete observable conditions that prove success]").
- **What is wrong:** A `grep -c` on a literal containing `${…}` printed 0 against files that hold the line.
- **Suggested fix:** Require `grep -F` for literal text, or a dry run of each check against the tree.
- **Source:** feedback `implement-acceptance-grep-regex` in `BOOK-2-01-feedback.md`
- **Confidence:** high

### FBB-B36 — NIT — `test-baseliner` verify lists new failures by name only
- **Where:** `plugins/dev-workflows/agents/test-baseliner.md:254-255` (`### New failures` — "one test identifier per line"); `:231` (the status does not count new failures).
- **What is wrong:** The fix loop must re-run each failing spec to learn why it fails.
- **Suggested fix:** Carry each failure's first assertion line, plus a `New failures: N` header field.
- **Source:** feedback `implement-verify-status-ok-with-new-failures` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B38 — MINOR — A post-review departure from the literal `design.md` or spec text leaves the specs contradicting the code
- **Where:** `plugins/dev-workflows/commands/implement.md:1018` (step 7.5 escalates only the review's `missing`/`contradicts`); no step covers edits made after the review. A grep for `depart` in `implement.md` hits only `:805` and `:971`, neither of which applies here.
- **What is wrong:** Fixes chosen by the user after the review changed markup and validation that `design.md` states literally. Nothing amended the design or wrote a note, so a later `/conformance` flags both.
- **Suggested fix:** When an edit after the review changes literally specified behaviour, amend the document and hand it off through Phase 4.5, or at least write a step-7.5-style note.
- **Source:** feedback `implement-post-review-design-departures-unrecorded` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B39 — NIT — Session files pushed straight to the default branch are not called out
- **Where:** `plugins/workflows-core/references/specs-repo-git.md:1006` (the outcome line reads `committed … on main — pushed`, with no "no PR" wording and no pointer to session-branch mode).
- **What is wrong:** A user used to pull-request landings missed a direct push to `main`, twice.
- **Suggested fix:** Add a default-branch variant of the outcome line that says no pull request was opened. Name session-branch mode (§8) once where the history shows deliverables landing through pull requests.
- **Source:** feedback `implement-artifacts-pushed-to-main-unannounced` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B41 — MINOR — Small `/prd-ground` ambiguities: the tail after a Phase 3 stop, in-repo prose as evidence, reusing a repository answer, and a BRD wireframe absent from the census
- **Where:** `plugins/product-workflows/commands/prd-ground.md:2235` (Phase 11 "runs after Phase 10, NEVER interrupts an earlier phase"; `specs-repo-git.md:568-575` is phrased for Phase 0 refusals); `:973-986` (the evidence ban says "documentation page" and does not say whether an in-repo `README`, `docs/` or `CLAUDE.md` counts); Phase 1 (no rule on reusing a repository choice from a stopped run); Phase 8 and 10 (no census of parent `brd/source/assets/` design sources a row cites).
- **What is wrong:** Each case left the orchestrator to decide by judgement or analogy.
- **Suggested fix:** State which tail members run after a Phase 3 or Phase 7 stop. Say whether in-repo prose files are documentation for the ban, and who filters them. State the reuse rule. Name any parent design asset a row cites, together with the `/frames` route.
- **Source:** feedback `prd-ground-tail-after-phase3-stop`, `prd-ground-instruction-files-as-evidence`, `prd-ground-repo-choice-on-rerun`, `prd-ground-brd-wireframe-not-in-census` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B43 — MINOR — `/brd-interview`: follow-up prompts may be batched, and the round-record and question-set layouts are unspecified
- **Where:** `plugins/product-workflows/commands/brd-interview.md:1485` ("exactly one at a time, never batched" reads as covering only the picker); `references/decision-register-format.md` (no whole-file template for `interview/round-<N>.md` or `customer-questions.md`; `ls references` has no interview-round format).
- **What is wrong:** A run merged one `[V]`'s argumentation prompt and code-defect offer with the next picker. Each run also improvises state lines that `/brd-package`, `/brd-reconcile` and resume parse.
- **Suggested fix:** Say that the follow-ups are separate calls. Add a worked round record and a worked `customer-questions.md` entry.
- **Source:** feedback `brd-interview-v-followups-batched`, `brd-interview-round-record-layout-unspecified` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B45 — MINOR — `/brd-package` and `/brd-reconcile`: the display before the question, scan tooling, prose references, author attribution, `[SR#n]` answer mapping, and bundle filenames in section 12
- **Where:** `plugins/product-workflows/commands/brd-package.md:639-641` (the display rule is one sentence above the picker, with no "same message" binding); `plugins/product-workflows/scripts/` (no scan tool; Phase 8 has no temporary-directory build); `brd-package.md:1367-1372` (rule 1 does not say whether prose references in plugin-written text are rewritten); `plugins/product-workflows/commands/brd-reconcile.md` *Ingest the review* (no anomaly class for reasons the review says were written by another author); `:1341` (no rule for mapping a factual answer onto `["as the package states", "as the finding argues"]`); `:1753-1757` (a section-12 row naming `<KEY>-decisions.md` reads as "anything under `bundle-<YYYYMMDD>/`" and is never rewritten; nothing maps it back through the manifest).
- **What is wrong:** (1) The operator answered `[SR#4]` blind. (2) The ad-hoc scans gave a false commit match on `20261012`, and a failed build left a partial dated bundle. (3) Two prose references were rendered by judgement. (4) Eighteen `[CD#n]` froze AI-written reasons as the customer's own. (5) Six answers needed judgement. (6) A bundle-name row is classed as a dated snapshot and refused, not applied to the working file it was rendered from.
- **Suggested fix:** Make the display and the picker one template in one message. Ship a deterministic scan script and build into a temporary directory. State rule 1's scope for prose references. Add a third-party-author anomaly class. Give mapping rules with worked examples. Resolve bundle names through the manifest.
- **Source:** feedback `brd-package-finding-not-shown-before-question`, `brd-package-no-shipped-bundle-scans`, `brd-package-rule1-prose-references`, `brd-reconcile-agent-authored-reasons-unflagged`, `brd-reconcile-sr-answer-option-mapping`, `brd-reconcile-section12-bundle-filenames` in `BOOK-2-01-feedback.md`
- **Confidence:** medium (high for the section-12 misclassification)

## older review records

### TRK-B1 — NIT — The 2026-10-15 review record says C1–C8 are still tracked in to-fix.md, but they were fixed and removed
- **Where:** `docs/superpowers/reviews/2026-10-15-review-of-five-merges.md:64` (*Deferred*: "C1–C7 … is tracked, in full … in `docs/superpowers/to-fix.md`"), `:82` (C8 "recorded there too"), `:84-86` (*Open items after both fix waves*: "every deferred finding (C1–C8 …) … are in `docs/superpowers/to-fix.md`")
- **What is wrong:** The record says every C finding "is tracked, in full … in `docs/superpowers/to-fix.md`". C1 and C3–C8 were deleted from to-fix.md as fixed or moot in `12f2408b` and `4069aa29`. to-fix.md now holds C2, plus C9, which this record never mentions.
- **Failure scenario:** A reader, or an agent sweeping open items, follows the record's pointer and either looks for C1 and C3–C8 in to-fix.md and finds nothing, or treats them as open.
- **Evidence:** `git log -- docs/superpowers/to-fix.md`, then `git show 12f2408b -- docs/superpowers/to-fix.md` (removes C1 and C3–C8) and `git show 4069aa29 …` (removes C1's remaining half).
- **Suggested fix:** Append a line to the record: C1 and C3–C8 were fixed in the `/conformance` rework (`12f2408b`, `4069aa29`, merged by `c3cd9d3e`); C2 and the later C9 remain in to-fix.md.
- **Source:** feedback in `docs/superpowers/reviews/2026-10-15-review-of-five-merges.md`
- **Confidence:** high

### TRK-B2 — MINOR — An edition-port obligation from the 2026-08-22 docs restructure has no entry in to-fix.md
- **Where:** `docs/superpowers/verification/2026-08-22-docs-restructure-open-items.md` § *Carried forward, outside this branch*; `docs/superpowers/to-fix.md:9`, `:11-82`
- **What is wrong:** The record says both editions "still carry the five-role vocabulary and the retired `QA` label" and that the port "is its own change". to-fix.md calls itself "the one list of known, unfixed issues … and of the work it owes the editions", yet its E1–E4 do not include this port. Line 9 admits `verification/` records "have not been swept".
- **Failure scenario:** Someone porting to an edition reads to-fix.md, which says to read it "before starting work on any edition", and never learns of the role-collapse port. The edition keeps `team`/`QA` roles while the cost-emission §7 and next-phase-offer text it ports from this repo use four roles.
- **Evidence:** Read the record's carried-forward paragraph; `grep -n 'role\|QA\|team' docs/superpowers/to-fix.md` finds no such item. Whether the editions have since taken it cannot be checked from this machine.
- **Suggested fix:** Sweep the record into to-fix.md as an E-item ("check whether each edition still carries `team`/`QA`; if so, port the role collapse"), saying in the commit that it moves an open item. Or record here that it already landed.
- **Source:** `docs/superpowers/verification/2026-08-22-docs-restructure-open-items.md`
- **Confidence:** medium. The port may have landed in the editions; that is not verifiable here.

## documentation quality — links, navigation, page-set parity (all plugins)

### DQS-B1 — MINOR — `guideline-reviewers`: README does not link its workflow diagram or getting-started page, and the repo-root table has no Docs link for it
- **Also found as:** DQW-B7 (merged here)
- **Where:** `plugins/guideline-reviewers/README.md:5`, `:7`; `README.md:13`
- **What is wrong:** The plugin README links the two command pages (`:5`) and "[the documentation index](docs/README.md)" (`:7`), and nothing else. It does not link `docs/workflow.md`, which holds the plugin's only mermaid diagram, or `docs/getting-started.md`. All five sibling `PLUGIN_RELS` READMEs link both. The repo-root table row (`README.md:13`) ends after its description, with no `[Docs](plugins/guideline-reviewers/docs/README.md)`. The rows for dev-, product-, docs-, security-workflows and workflows-core all carry one (`README.md:11,12,14,15,16`).
- **Failure scenario:** A user who starts from the repo root, or from the plugin README, reaches the diagram only through the index. That is two clicks, against one for every sibling. From the root table, nothing shows that the plugin has a docs tree at all. This is the user-reported case that started this review.
- **Evidence:** `graph.py` prints `README missing direct links to: [docs/getting-started.md, docs/workflow.md]` for this plugin alone. For the root README it prints `guideline-reviewers: docsindex=False anydocs=[]`.
- **Suggested fix:** Give the README the same Documentation table the siblings carry (index, getting started, workflow overview, the two command pages, the three reference pages). Append `[Docs](plugins/guideline-reviewers/docs/README.md)` to `README.md:13`.
- **Source:** review (user observation, BRIEF-DOCS)
- **Confidence:** high

### DQS-B2 — MINOR — Workflow, BRD-route, roles and getting-started pages draw or name every command but link to none of the command pages
- **Where:**
  - `plugins/dev-workflows/docs/workflow.md` (4 links, 0 to `commands/`; it names `/design` 11×, `/implement` 11×, `/ready` 8×)
  - `plugins/product-workflows/docs/workflow.md` (3 links, 0 to `commands/`; it names `/specify` 12×, `/brd-reconcile` 15×, `/create-prd` 10×)
  - `plugins/docs-workflows/docs/workflow.md:91` ("See the [documentation index](README.md) for the per-command pages")
  - `plugins/security-workflows/docs/workflow.md:67` (same deferral)
  - `plugins/product-workflows/docs/brd-workflow.md`: the BRD route page links 5 command pages (`brd-proposal`, `create-prd`, `epics`, `idea`, `specify`) but **none of the six BRD-route commands it describes**, although it names `/brd-reconcile` 36×, `/brd-interview`, `/brd-split` and `/prd-ground` 23× each, and `/brd-intake` and `/brd-package` 15× each (first at `:20`, `:25`)
  - roles pages with 0 command links: `dev-workflows/docs/roles-and-phases.md`, `product-workflows/docs/roles-and-phases.md`, `security-workflows/docs/roles-and-phases.md` (names `/scan` 4×), `workflows-core/docs/roles-and-phases.md`
  - getting-started pages with 0 command links: `dev-workflows` (names `/design` 12×; its walkthrough is "run `/design` end to end", `:3`), `docs-workflows` (`/document` 13×), `product-workflows` (`/idea` 9×)
- **What is wrong:** GitHub renders mermaid without `click` navigation, so the diagram page's prose is the only way to click from a node to its command page. On these pages that prose names the commands as code spans, not links. The siblings show the pattern: `guideline-reviewers/docs/workflow.md`, `workflows-core/docs/workflow.md`, `docs-workflows/docs/docs-workflow.md` (6 command links) and `workflows-core/docs/getting-started.md` (6) all link their commands.
- **Failure scenario:** A reader on `/brd-reconcile`'s node in `brd-workflow.md` wants its parameters. They must go back to the index or the README to find `commands/brd-reconcile.md`. The same is true on every workflow page above, and on the getting-started pages that tell the reader to run a command.
- **Evidence:** `unlinked.py` (output summarised under *Evidence*) lists each page with the sibling commands it names but never links. The overview-page link count is in the *Evidence* table.
- **Suggested fix:** Link the first mention of each command on each of these pages. Better, add a "Commands on this diagram" list under each diagram, linking each node's page.
- **Source:** review
- **Confidence:** high

### DQS-B3 — MINOR — 18 command pages do not link back to their plugin's workflow page
- **Where:** each page's *See also* list:
  - `dev-workflows/docs/commands/` — all six: `conformance.md:103`, `design.md:90`, `implement.md:110`, `ready.md:80`, `upgrade.md:72`, `vuln.md:70`
  - `docs-workflows/docs/commands/` — `docs-brand.md:61`, `document.md:109`, `release-notes.md:97`
  - `product-workflows/docs/commands/` — `brd-intake.md:296`, `brd-interview.md:552`, `brd-package.md:466`, `brd-reconcile.md:724`, `brd-split.md:616`, `epics.md:89`, `idea.md:177`, `prd-ground.md:589`, `update-prd.md:79`
- **What is wrong:** None of these pages links `../workflow.md` (or, for the BRD commands, `../brd-workflow.md`), and none links the docs index either. Their siblings do: both guideline-reviewers pages, `security-workflows/docs/commands/scan.md`, all seven workflows-core pages, docs-workflows' `docs-audit`, `docs-init`, `docs-profile` and `docs-serve`, and product-workflows' `brd-proposal`, `create-ard`, `create-prd`, `harvest-decisions`, `prd-proposal`, `promote-decisions` and `specify`.
- **Failure scenario:** A reader who lands on a command page from a search or a link cannot get from it to the diagram showing where the command sits. In `dev-workflows` no command page offers that path at all.
- **Evidence:** `graph.py`, "CMD no link to any workflow page", which also reports `links to index: False` for all 18.
- **Suggested fix:** Add `- [Workflow overview](../workflow.md) — where this command sits` (and `../brd-workflow.md` for the six BRD-route commands) to each *See also* list.
- **Source:** review
- **Confidence:** high

### DQS-B4 — MINOR — Next and previous commands named in prose but not linked; `/harvest-decisions` never mentions `/promote-decisions`; no command page links `/docs-audit`
- **Where:**
  - `plugins/product-workflows/docs/commands/harvest-decisions.md`: no occurrence of "promote" in the page (`grep -c promote` → 0), although `promote-decisions.md:7` says it runs "after [`/harvest-decisions`]". The harvest command's own handoff text names `/promote-decisions` (`commands/harvest-decisions.md:46`). `promote-decisions.md` has no inbound link from any command page.
  - `plugins/docs-workflows/docs/commands/docs-audit.md` has no inbound link from any command page. `docs-init.md` names `/docs-audit` 5× (`:3`, `:23`, `:35`, `:62`) and `docs-serve.md` names it 3×, all unlinked. The README diagram draws `SERVE --> AUDIT` (`plugins/docs-workflows/README.md:30`).
  - `plugins/dev-workflows/docs/commands/ready.md` names `/implement` 4× (`:23`, `:47`) unlinked. `design.md` names `/ready` unlinked (`:58`).
  - Smaller cases on command pages: `brd-intake.md` (`/epics`, `/idea`, `/create-prd`), `brd-package.md` (`/prd-ground` 4×, `/brd-intake`), `brd-split.md` (`/create-ard`, `/specify`), `prd-ground.md` (`/idea`, `/prd-proposal`), `brd-reconcile.md` (`/update-prd`), `docs-brand.md` (`/docs-audit` 2×, `/document`, `/release-notes`), `document.md` (`/docs-init`, `/docs-profile`), `frames.md` (`/prompt-brainstorm`, `/prompt-grill-me`), `diagnose-session.md` (`/feedback` 3×).
- **What is wrong:** The brief's navigation rule: a "see X" that names a page must link it, and a command page should link its next and previous command. The decision-harvest pair is the sharpest case. Nothing on the harvest page tells the architect that a promotion step exists.
- **Failure scenario:** An architect who has just harvested decisions reads the harvest page and never learns that `/promote-decisions` turns the harvested records into ADRs.
- **Evidence:** `unlinked.py` and the command-to-command link matrix (*Evidence*).
- **Suggested fix:** Add `/promote-decisions` to `harvest-decisions.md`'s *See also* as the next step. Link the first mention of each named sibling on each listed page.
- **Source:** review
- **Confidence:** high

### DQS-B5 — MINOR — 18 relative links leave the plugin directory and break in the installed cache
- **Where:**
  - Seven plugin READMEs → `../../README.md`: `dev-workflows/README.md:5`, `docs-workflows/README.md:5`, `product-workflows/README.md:5`, `security-workflows/README.md:5`, `workflows-core/README.md:5`, `obsidian-llm-wiki/README.md:80`, `prose-style/README.md:407`.
  - Nine getting-started links → `../../../README.md`: `dev-workflows/docs/getting-started.md:21` (`#prerequisites`) and `:25`, `docs-workflows/...:23`, `guideline-reviewers/...:19`, `product-workflows/...:21` and `:23`, `security-workflows/...:34` (`#prerequisites`) and `:62` (`#4-raise-claude-codes-skill-listing-budget`), `workflows-core/...:25`.
  - Two links into another plugin: `dev-workflows/docs/reference/hooks.md:9` → `../../../workflows-core/docs/reference/hooks.md`, and `dev-workflows/docs/reference/model-routing.md:57` → `../../../workflows-core/docs/reference/environment.md`.
- **What is wrong:** An installed plugin sits at `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`, which holds one plugin and no repository root. From `<plugin>/<version>/README.md`, `../../README.md` resolves to `cache/<marketplace>/README.md`, which does not exist. The cross-plugin links go to `cache/<marketplace>/dev-workflows/workflows-core/...`, which is also absent. All 18 resolve on GitHub and in a checkout (0 broken in the repo).
- **Failure scenario:** A user reading the installed `prose-style` README, which is that plugin's only documentation and carries no install command of its own (`:402-407`), follows "repo-root setup guide" and gets a missing file. The same happens to a reader of any installed getting-started page who follows "Prerequisites".
- **Evidence:** `linkcheck.py`'s `escapes_plugin` list (18 entries, reproduced under *Evidence*). The cache layout comes from `CLAUDE.md` § Internal reference convention.
- **Suggested fix:** Use absolute `https://github.com/ihudak/ai-workflows#prerequisites` URLs for the root-guide links. Check 10 allows a marketplace/container-repo name only in `getting-started.md`, so for the README back-links keep the wording generic, or confirm that check 10 does not cover READMEs. For the two cross-plugin links, cite the page by plugin name in prose, as the rest of the tree does ("it ships in the companion `workflows-core` plugin").
- **Source:** review
- **Confidence:** medium (the cache layout is from CLAUDE.md; that a user browses the cache is a judgement)

### DQS-B6 — MINOR — Page-set parity holes in `docs-workflows` and `security-workflows`; command pages name a "Roles and phases" page that the plugin does not have
- **Also found as:** DQW-B12 (merged here)
- **Where:** parity matrix (*Evidence*). `plugins/docs-workflows/docs/commands/document.md:111` and `release-notes.md:99` (unlinked "Roles and phases —" bullets).
- **What is wrong:**
  - `docs-workflows` has no `roles-and-phases.md`, although dev-, product-, security-workflows and workflows-core all carry one and its commands emit roles (`document` dev/documenting; `release-notes` pm/dev). The two *See also* bullets begin "Roles and phases —" with no link, then explain that "No one page defines all four" and that "`documenting` has no roles page" (`release-notes.md:99`).
  - `docs-workflows` also has no `session-feedback.md` (5 of 7 commands run `emit-auto`: `docs-init`, `docs-brand`, `docs-audit`, `release-notes`, `document`), no `resume-and-checkpoints.md`, and no `model-routing.md` (all 7 commands cite model routing). dev- and product-workflows carry all three.
  - `security-workflows` has no `session-feedback.md`, although `/scan` runs `emit-auto` (`commands/scan.md`, 2 hits).
  - No rules file or rationale section calls these holes deliberate. `.claude/rules/docs-workflows.md:29` and `.claude/rules/security-workflows.md:18` only enumerate the page sets. `docs-serve`'s "outside the role pipeline" status is deliberate, but that covers one command, not the plugin.
- **Failure scenario:** A docs-workflows user who wants to know where a `/document` run's feedback note lands, or how its Opus review falls back, finds no page in this plugin. The *See also* item that should take them to the roles page is plain text.
- **Evidence:** parity matrix; `grep -c emit-auto` per command (*Evidence*).
- **Suggested fix:** Add `docs-workflows/docs/roles-and-phases.md` that defines the `documenting` phase, and link the two bullets to it. Add short `session-feedback.md` pages, or link the workflows-core page by name in prose, to docs- and security-workflows. Alternatively, record in `.claude/rules/docs-workflows.md` that the plugin defers these pages to `workflows-core`, and say so on the index.
- **Source:** review
- **Confidence:** high (the holes); medium (whether each one deserves its own page)

### DQS-B7 — MINOR — Internal design-decision IDs (D4 … D25) leak into user pages with nothing to resolve them against
- **Where:**
  - `plugins/docs-workflows/docs/commands/docs-brand.md:33`: "**Opus review regardless of class (D17, D20)**", "**There is no dedicated fixer for this diff (D25)**"
  - `docs-serve.md:34`: "**No review gate, by design (D17).**"
  - `docs-workflows/docs/reference/environment.md:31`: "read it oppositely (D23)"
  - `product-workflows/docs/roles-and-phases.md:24`: "**All three refuse a `BRD-` container** (D5)"
  - `product-workflows/docs/workflow.md:168` and `commands/specify.md:15`: "no command takes a chain (D4)"
  - `product-workflows/docs/commands/create-prd.md:49`: "(D7)"
  - `product-workflows/docs/reference/references.md:16`: "(D12)", "(D18)"
- **What is wrong:** These are decision numbers from design specs under `docs/superpowers/specs/`. Those specs are not in the plugin and are never linked, and each spec numbers its decisions from D1, so "D17" means different things in different specs. A reader cannot resolve any of them. BRIEF-DOCS names this internal vocabulary as a defect.
- **Failure scenario:** A docs-workflows user reads "(D17, D20)" as a reference to something they should look up, and finds nothing in the docs tree.
- **Evidence:** `grep -rnoE "\((D|C|E|F|L)[0-9]{1,2}…\)" plugins/*/docs` (10 hits in 8 files, quoted above).
- **Suggested fix:** Delete the parenthesised IDs. The sentences already state the rule.
- **Source:** review
- **Confidence:** high

### DQS-B8 — MINOR — 317 bare `workflows-core:<name>` citations and 306 `§` section citations on user pages, none linked
- **Where:** bare `` `workflows-core:<name>` `` citations per plugin's `docs/`: dev-workflows 74 (15 files), docs-workflows 48 (11), product-workflows 179 (25), security-workflows 6 (2), workflows-core 10 (4). `§` counts: 52 / 43 / 135 / 6 / 70. Examples in *See also* lists: `dev-workflows/docs/commands/design.md` ("`workflows-core:ard-resolution` — how the optional ARD is resolved and inherited"), `implement.md`, `upgrade.md`, `vuln.md` (`workflows-core:finding-triage`), `docs-workflows/docs/commands/document.md:115` and `release-notes.md:103` (`workflows-core:model-routing/classification`), `workflows-core/docs/commands/feedback.md` ("`references/cost-emission.md` §7").
- **What is wrong:** `workflows-core:<name>` is the agents' citation form (CLAUDE.md § Internal reference convention). On a human page it reads as a *See also* entry with nothing to click. A user-facing inventory of every such file exists, `plugins/workflows-core/docs/reference/references.md`, but no page in another plugin can link it (see DQS-B5), and the pages do not name it either.
- **Failure scenario:** A reader follows *See also* → "`workflows-core:finding-triage` — the triage step run between `code-review` and `review-fixer`" and has no way to open it from the plugin's docs.
- **Evidence:** `grep -rhoE '`workflows-core:[a-z/-]+`' plugins/<p>/docs | wc -l` and `grep -rho '§'` per plugin (*Evidence*).
- **Suggested fix:** In *See also* lists, replace each bare citation with "the `<name>` reference, listed on `workflows-core`'s References page". Inside `workflows-core/docs`, link `reference/references.md#…`. Drop `§n` numbers from user prose where the sentence already says what the rule is.
- **Source:** review
- **Confidence:** medium (the counts are exact; how many to rewrite is a judgement)

### DQS-B9 — NIT — Command pages without a diagram where their siblings have one
- **Also found as:** DQP-G6 (merged here)
- **Where:** `plugins/docs-workflows/docs/commands/` `docs-audit.md`, `docs-brand.md`, `docs-init.md`, `docs-profile.md`, `docs-serve.md` (no mermaid block; `document.md:31` and `release-notes.md:27` have one); `plugins/product-workflows/docs/commands/harvest-decisions.md` (none; the other 15 product command pages, `promote-decisions.md:21` among them, have one); `plugins/workflows-core/docs/commands/` (only `frames.md:29` has one).
- **What is wrong:** All six dev-workflows command pages and `scan.md` carry a per-command flow diagram. In docs-workflows five of seven pages lack one, and `/harvest-decisions` is the only product command page without one.
- **Failure scenario:** A reader cannot see `/docs-init`'s phase flow the way they can see `/document`'s, though `/docs-init` has 11+ phases (`docs-init.md:35`).
- **Evidence:** `linkcheck.py`'s mermaid inventory (*Evidence*).
- **Suggested fix:** Add phase-flow diagrams to `docs-init`, `docs-audit`, `docs-brand` and `harvest-decisions` at least. The workflows-core utilities and `docs-serve` can stay prose-only.
- **Source:** review
- **Confidence:** medium

### DQS-B10 — NIT — workflows-core's README does not link the family map, the one diagram that draws the whole family
- **Where:** `plugins/workflows-core/README.md` (the family map's inbound links are `README.md:23` at the repo root, `plugins/workflows-core/docs/README.md` and `docs/workflow.md`)
- **What is wrong:** `docs/family-map.md` is the family-wide diagram that `CLAUDE.md` and the repo-root README point to, but the README of the plugin that ships it does not link it. Reaching it from that README takes two clicks. In the installed cache it is reachable only through the index, because the root README is absent there.
- **Failure scenario:** A user who opens workflows-core's README to see how the plugins fit together does not find the map.
- **Evidence:** `graph.py`'s mermaid reachability list.
- **Suggested fix:** Add a `[Family map](docs/family-map.md)` row to the README's documentation table, next to CORE-B16's missing grounding row.
- **Source:** review
- **Confidence:** high

### DQS-B11 — MINOR — obsidian-llm-wiki README: the local-install command is `cc`, not `claude`, and the marketplace step gives no command
- **Also found as:** DQW-B16 (merged here)
- **Where:** `plugins/obsidian-llm-wiki/README.md:100` (`cc --plugin-dir /path/to/obsidian-llm-wiki`); `:86-92` ("add it once via Claude Code settings or the `/plugin` command, then install: `/plugin install obsidian-llm-wiki@shipwright`")
- **What is wrong:** `cc` is the C compiler on Linux and macOS. Claude Code's executable is `claude` (CLAUDE.md, the root README, `.claude/rules/plugin-updates.md`), so a user who pastes the line runs `cc` on a directory. The marketplace step names the action but gives no command. The command (`claude plugin marketplace add ihudak/ai-workflows`) sits behind the `../../README.md` link, which is broken in the cache (DQS-B5).
- **Failure scenario:** A user who pastes `cc --plugin-dir …` gets a compiler error instead of a Claude Code session with the plugin loaded.
- **Evidence:** read `:80-110`; `grep -n plugin-dir` → `:100` only.
- **Suggested fix:** Change it to `claude --plugin-dir /path/to/obsidian-llm-wiki`, and show `claude plugin marketplace add ihudak/ai-workflows` inline, as `acli`'s README does (`plugins/acli/README.md:29-30`).
- **Source:** review
- **Confidence:** medium (`cc` may be a personal alias of the author, but a reader does not have it)

### DQS-B12 — MINOR — The READMEs of the three plugins without a `docs/` tree leave out what a user needs
- **Where:** `plugins/prose-style/README.md`, `plugins/acli/README.md`, `plugins/obsidian-llm-wiki/README.md`
- **What is wrong:** Each README is the plugin's only user documentation.
  - **prose-style** (407 lines) documents its commands, agents, skill and overlay well. Its *Installation* section (`:402-407`) has no install command, only "Install it through Claude Code's plugin system" and the broken-in-cache root link. *How it fits* (`:383-400`) cites `/document` "Phase 6.4" and `/epics` "Phase 6.2" with no explanation of what a phase number is (both are accurate at HEAD: `docs-workflows/commands/document.md:890`, `product-workflows/commands/epics.md:713`). It has no diagram of the overlay resolution order, which is the plugin's one non-obvious mechanism (`:40-96`).
  - **acli** (31 lines) has an install block but no usage section. It gives no example prompt that triggers the skill, no first-run authentication steps (the headless token-on-stdin flow is described only as a change from upstream, `:15-17`, never as instructions), and no statement of what the skill refuses to do without approval, beyond the change note at `:18-21`.
  - **obsidian-llm-wiki**: see DQS-B11. Its command table (`:167-180`) does not link the ten command files, and it has no troubleshooting section for a missing `VAULT_PATH` or an uninitialised vault.
- **Failure scenario:** An acli user installs the plugin and does not know how to authenticate in a container or what to ask for. A prose-style user who reads the installed README finds no install line.
- **Evidence:** heading lists and reads of each README (*Evidence*).
- **Suggested fix:** For prose-style, add the install line (`claude plugin install prose-style@shipwright`; it is also pulled in as a dependency) and drop the phase numbers. For acli, add *Authenticate* and *Example requests* sections. For obsidian, add the fix in DQS-B11.
- **Source:** review
- **Confidence:** medium

## documentation quality — family entry points and workflows-core

### DQC-B2 — MINOR — "Option B" cost snapshot and `cost_statusline_usd` point at a page that never mentions either
- **Where:** `README.md:111` ("enables the Option-B snapshot used by session-cost reporting"); `plugins/workflows-core/docs/commands/statusline.md:26` ("the per-session **cost snapshot** ("Option B") that [Session cost](../reference/session-cost.md) reads when computing `cost_statusline_usd`"), `:43` ("the Option B cost snapshot this command enables")
- **What is wrong:** `plugins/workflows-core/docs/reference/session-cost.md` contains neither "Option B", "snapshot" nor `cost_statusline_usd` (`grep -n "snapshot\|cost_statusline_usd\|Option" …/session-cost.md` returns nothing). It mentions the cross-check only to send the reader to `references/cost-emission.md` (`:45`). "Option B" is a name left over from a design discussion, and no user page defines it.
- **Failure scenario:** a user who wants to know what the status line adds to cost reporting follows the link and finds nothing about a snapshot or `cost_statusline_usd`. The getting-started pages (`plugins/workflows-core/docs/getting-started.md:83`) describe it as "the cost cross-check" instead, so the reader meets three names for one thing.
- **Evidence:** grep above; lines quoted.
- **Suggested fix:** drop "Option B" everywhere. Add a short "Status-line cross-check" section to `session-cost.md`, saying what the snapshot is, where it is stored, and which entry field (`cost_statusline_usd`) it fills. Link to that section from the two places above.
- **Source:** review
- **Confidence:** high

### DQC-B3 — MINOR — three of the five family getting-started pages skip the status-line step the root README calls step 5 and the core index says to "run first"
- **Where:** `README.md:109-111` ("### 5. Run `/workflows-core:statusline` first"); `plugins/workflows-core/docs/README.md:12` ("**run this first**"); present in `plugins/dev-workflows/docs/getting-started.md:70-84` and `plugins/workflows-core/docs/getting-started.md:77-89`; absent from `plugins/product-workflows/docs/getting-started.md`, `plugins/docs-workflows/docs/getting-started.md` and `plugins/security-workflows/docs/getting-started.md`. Their headings (`grep -n '^#'`) have no status-line section, and each mentions the status line only inside the `jq` prerequisite sentence.
- **What is wrong:** the install path a user follows depends on which plugin's page they open. Three of them never say to install the status line. Without it, the cost report has no figure to check the price table against: dev's page `:76` explains this, and the others do not.
- **Failure scenario:** a PM who installs `product-workflows` from its getting-started page runs `/idea` and `/create-prd` with no status line. The cost entries carry no cross-check figure, and nothing told them why.
- **Evidence:** headings listed above.
- **Suggested fix:** give the three pages the same short "Install the status line" section that dev and core have, or at least one sentence linking to the core page's section.
- **Source:** review
- **Confidence:** high

### DQC-B4 — MINOR — maintainer `grep` recipes over `plugins/*/…` are given to users as the way to find things
- **Where:** `README.md:93` ("Required by the commands that stop without it — `grep -lE 'Set SPECS_PATH|Required path environment variable unset' plugins/*/commands/*.md` lists them"); `plugins/dev-workflows/docs/getting-started.md:21` ("`grep -ln 'WebFetch\|WebSearch' plugins/dev-workflows/agents/*.md` re-derives that set rather than trusting this list"); `plugins/workflows-core/docs/reference/agents.md:22` ("re-derive both halves with `ls plugins/workflows-core/commands/` and `grep -n subagent_type …`"); `plugins/workflows-core/docs/reference/references.md:3` (the "36 + 2 = 38" arithmetic)
- **What is wrong:** these recipes belong to the repository's maintainer discipline (CLAUDE.md, *Re-measure in one place*). In user-facing pages they replace the answer. The paths `plugins/…` exist only in a clone of this repository, not in the installed cache (`~/.claude/plugins/cache/shipwright/<plugin>/<version>/`).
- **Failure scenario:** a new user reads the root README to learn which commands need `SPECS_PATH`. They get a shell command to run against a repository they have not cloned, and no list.
- **Evidence:** lines quoted.
- **Suggested fix:** state the answer in plain words. For README:93: "every command that writes into the specs tree, and `/implement`, keyed `/document` and `/release-notes` on a key address". Move the recipes to `docs/maintainers/` or to an HTML comment.
- **Source:** review
- **Confidence:** high

### DQC-B5 — MINOR — internal vocabulary and § citations into references a user never opens, on the core plugin's user pages
- **Where:** `plugins/workflows-core/docs/roles-and-phases.md:3` ("the **lifecycle** phases `references/cost-emission.md` §7 carries — read them off its table, as fixed pairs, and off the inference paragraphs beside it … A sibling page that counts lifecycle phases counts them without the fallback, which is not a disagreement"), `:9`, `:14`, `:26`; `plugins/workflows-core/docs/reference/environment.md:3` ("the names its own inventory check encounters … `OWNER_REPO` are … internal template names"), `:5` (a paragraph on which sibling plugin reads four of the five variables); `plugins/workflows-core/docs/getting-started.md:29` ("for eight of the nine, the only read anywhere in this plugin"), `:57`, `:61`, `:65` ("`workflows-core:run-flags` is the single source of truth"); `plugins/dev-workflows/docs/getting-started.md:108` ("as `workflows-core:phase-handoff` §3.4 lists"); `plugins/workflows-core/docs/commands/statusline.md:17` and `plugins/docs-workflows/docs/getting-started.md:23` (bare "Phase 4" / "the Phase 0 toolchain preflight")
- **What is wrong:** the opening paragraph of roles-and-phases is addressed to someone maintaining page counts, not to someone asking what phase their run was charged to. It never names the phases, and sends the reader to a § of a file the docs do not link. environment.md opens with which *source files* read which variable. The getting-started pages use `plugin:reference` ids (`workflows-core:run-flags`) as if they were page names.
- **Failure scenario:** a user who opens Roles and phases to learn which phase `/create-prd` costs land in is told to read `references/cost-emission.md` §7. A user who reads "See `workflows-core:run-flags`" finds no page by that name and no link.
- **Evidence:** lines quoted. `grep -c "§"` over the core docs gives 4 on roles-and-phases, 7 on environment, 9 on frames, 9 on references, 5 on agents, and 4 each on session-cost and session-feedback.
- **Suggested fix:** open roles-and-phases with a plain list of the phase names and what each means, and move the counting caveat to `docs/maintainers/`. Replace each `workflows-core:<ref>` "see" with a link to the [References](reference/references.md) entry or a plain description. Cut environment.md:3 and :5 to one sentence per plugin.
- **Source:** review
- **Confidence:** high

### DQC-B6 — MINOR — stale and changelog-style statements on user pages
- **Also found as:** DQW-B17 (merged here)
- **Where:** `plugins/workflows-core/docs/reference/session-cost.md:33` ("Before the manifest existed the rule was … which, once the family spanned four, made a *sibling's* run … invisible"); `plugins/workflows-core/docs/commands/frames.md:108` ("Before this, such a file was reported and never read…"), `:112` ("Three such exports once rejoined the describe set on every future run, forever"), `:120` ("Design grounding on the `/product-workflows:idea` route ships in this same increment as the BRD route's own — §6.1 says so … now on both routes"); `README.md:161` and the five getting-started pages (`dev :34`, `product :32`, `docs :33`, `workflows-core :17`, `guideline-reviewers :17`): "This page used to say the first line alone was enough"
- **What is wrong:** these are change history, not documentation. "Once the family spanned four" is now false: the family has five plugins (README:23, family-map:3). "Ships in this same increment" has no meaning for a reader, and on the frames page it is a claim with an expiry date that has passed. "This page used to say…" corrects a page the new reader never saw.
- **Failure scenario:** a reader takes "four" to be the current size of the family, or reads "this increment" as meaning design grounding on the idea route is new or partial.
- **Evidence:** lines quoted; family size from `README.md:23`.
- **Suggested fix:** delete the history sentences and keep the rule each one explains, for example "A claim is matched against a manifest of every family command" with no "before". Move the history to `CHANGELOG.md`.
- **Source:** review
- **Confidence:** high

### DQC-B7 — MINOR — the family map omits two forward steps the commands offer
- **Where:** `plugins/workflows-core/docs/family-map.md:137-144` (the `conformanceprd` and `secscan` edges)
- **What is wrong:** `workflows-core:next-phase-offer` says the PRD-level `/dev-workflows:conformance <PRD>` → "once settled → `/docs-workflows:document <PRD>`" (`plugins/workflows-core/references/next-phase-offer.md:333`). It also says the Dev's `/security-workflows:scan <EPIC>` → "… then the PE's `/dev-workflows:conformance <PRD>`" (`:334`). The map's `conformanceprd` node has only the two amendment edges (to `specify` and `updateprd`), and `secscan` has no edge to `conformanceprd`. The map's only edge into `/document` comes from `/implement` (`:134`), but `/implement` offers `/document` only after the PE's PRD conformance (`next-phase-offer.md:330-331`).
- **Failure scenario:** a PE reading the map sees PRD conformance end in amendments, with no forward path. A reader may conclude that `/document` follows each Epic's `/implement` directly, when the offer puts it after every Epic has merged and the PRD has been checked.
- **Evidence:** edges listed at `family-map.md:88-161`; offers at `next-phase-offer.md:330-334`.
- **Suggested fix:** add `conformanceprd -->|"settled PRD"| document` and `secscan -.->|"after the merge, every Epic merged"| conformanceprd`. Optionally relabel `implement --> document` to say "once every Epic has merged".
- **Source:** review
- **Confidence:** medium. The map says "An artifact edge is not an automatic invocation" (`:176`), so the missing edges may be deliberate. Nothing on the page says so.

### DQC-B8 — MINOR — the core docs never point a user to the three run flags under their own name
- **Where:** `plugins/workflows-core/docs/README.md` (no row or entry for run flags); `plugins/workflows-core/README.md:22-33` (same); `plugins/workflows-core/docs/getting-started.md:57`, `:61`, `:65` ("See `workflows-core:run-flags`", unlinked)
- **What is wrong:** `workflows-core` owns `--skip-costs`, `--skip-feedback` and `--enforce-model`. Its docs describe them only under environment-variable headings (getting-started, environment.md) and in pieces across session-cost.md and session-feedback.md. The accepted `--enforce-model` values are explained only in environment.md:105 with § citations to `run-flags.md` §2. The fuller user explanation is in the dev and product `docs/reference/model-routing.md` pages ("Enforcing one model"), which the core docs do not link.
- **Failure scenario:** a user who wants to know what `--enforce-model=` accepts, or what `--skip-feedback` drops, looks at the core docs index and finds no entry.
- **Evidence:** `grep -rn "run-flags\|enforce-model" plugins/workflows-core/docs` lists only the env-var sections, the per-command synopses and `references.md:68`.
- **Suggested fix:** add an index row, "skip cost or feedback, or pin one model for a run", that links to a short "Run flags" section in environment.md. That section should list the three flags, the accepted `--enforce-model` values (`opus`, `sonnet`, `haiku`, `fable`, a newest-row version id, `routing`), and an example invocation. Turn the three "See `workflows-core:run-flags`" mentions into links to it.
- **Source:** review
- **Confidence:** high

### DQC-B9 — NIT — root README's "three core environment variables" cannot be matched to the five it exports
- **Where:** `README.md:83-90`
- **What is wrong:** "three core environment variables — plus an optional `DOCS_PATH` … and an optional `ARCHITECTURE_REPO_PATH`". The block that follows exports five variables, and only `SPECS_PATH` and `REPOS_PATH` are not marked optional. The third `GIT_USER_INITIALS`, is marked "optional" in the block.
- **Failure scenario:** a new user cannot tell which three are "core" and which they must set. Only `SPECS_PATH` is required.
- **Suggested fix:** "One required variable, `SPECS_PATH`; `REPOS_PATH` has a default; the rest are optional."
- **Source:** review
- **Confidence:** high

### DQC-B10 — NIT — dev-workflows' getting-started says it reads five variables, and the core environment page says four
- **Where:** `plugins/dev-workflows/docs/getting-started.md:38` ("`dev-workflows` reads five environment variables"), `:50` (`DOCS_PATH`: "None of this plugin's own six commands grounds against it … documented here only because … a boundary statement, not a consumer"); `plugins/workflows-core/docs/reference/environment.md:5` ("`dev-workflows` reads four of the five — … `$DOCS_PATH` is not among the variables its own commands or references read")
- **What is wrong:** the two pages give different counts, and the dev page's own `DOCS_PATH` section says the plugin does not read the variable.
- **Suggested fix:** "reads four … and `DOCS_PATH` is listed only to say it is never touched", or drop the `DOCS_PATH` section from dev.
- **Source:** review
- **Confidence:** high

### DQC-B11 — NIT — workflow.md counts "three dashed and solid edges" where the diagram draws five
- **Where:** `plugins/workflows-core/docs/workflow.md:38` against `:25-32`
- **What is wrong:** five edges run into `pipeline`: `loader`, `skill` and `agents` (solid), and `setup` and `repair` (dashed). The sentence means the three solid ones (read a reference, load the skill, dispatch an agent).
- **Suggested fix:** "The three solid edges into …".
- **Source:** review
- **Confidence:** high

### DQC-B12 — NIT — /frames' diagram labels Phase 0 "kind-gated" on a page that says no kind is passed
- **Where:** `plugins/workflows-core/docs/commands/frames.md:78` (`"Phase 0 — Resolve the address (kind-gated) + model routing"`) against `:54` ("with no kind narrowing") and `:70` ("No kind is passed, because `design/` is reserved at every level"); the command's heading is `## Phase 0 — Resolve the address + model routing` (`plugins/workflows-core/commands/frames.md:35`)
- **What is wrong:** the diagram adds a qualifier that contradicts its own page and is not in the command.
- **Suggested fix:** drop "(kind-gated)", or say "(any BRD, PRD or Epic folder)".
- **Source:** review
- **Confidence:** high

### DQC-B13 — NIT — core pages call the five-plugin family "the `dev-workflows` plugin family"
- **Where:** `plugins/workflows-core/README.md:3`; `plugins/workflows-core/docs/getting-started.md:21`; `plugins/workflows-core/docs/workflow.md:3`; `plugins/workflows-core/docs/roles-and-phases.md:3`; `plugins/workflows-core/docs/reference/references.md:5`
- **What is wrong:** the root README and family map call it "the workflow plugin family" or "the family" of five plugins (`README.md:14`, `:23`). The core plugin's first sentence calls it the `dev-workflows` family.
- **Failure scenario:** a docs-workflows or security-workflows user who reads only the core README's first line takes `workflows-core` to be a `dev-workflows` add-on.
- **Suggested fix:** "the workflow plugin family (`product-workflows`, `dev-workflows`, `docs-workflows`, `security-workflows`)".
- **Source:** review
- **Confidence:** high

### DQC-B14 — NIT — the root README's "Directory structure" leaves out three of the layouts the variables expect
- **Where:** `README.md:163-176`
- **What is wrong:** it shows `$SPECS_PATH/specifications/PRD-<KEY>-<slug>/` only. It leaves out `BRD-<KEY>-<slug>/` (the second entry route, `README.md:28`), `$SPECS_PATH/security/<repo-slug>/` (the findings register; `plugins/security-workflows/docs/getting-started.md:56`) and `$SPECS_PATH/architecture/` (team decision records; `plugins/workflows-core/docs/reference/grounding.md:35`). `ARCHITECTURE_REPO_PATH`, which the section above exports, is also absent.
- **Failure scenario:** a team setting up a new specs repository from this section does not expect `security/` and `architecture/` to appear at its root, or the BRD folders.
- **Suggested fix:** add the three entries, one line each.
- **Source:** review
- **Confidence:** high

## documentation quality — dev-workflows and security-workflows

### DQD-B1 — MINOR — The first-run example key `EPIC-98760` is not a key shape any Epic gets, so a new user copying it learns the wrong form
- **Also found as:** DQC-B1 (merged here)
- **Where:** `plugins/dev-workflows/docs/getting-started.md:97`, `:100`, `:104`, `:110`; `plugins/dev-workflows/docs/commands/design.md:85`, `:88`; `plugins/dev-workflows/docs/commands/implement.md:105`, `:108`; `plugins/dev-workflows/docs/commands/ready.md:75`, `:78`; `plugins/dev-workflows/docs/reference/session-cost.md:80`
- **What is wrong:** Getting started says "`/dev-workflows:design EPIC-98760`" and "`EPIC-98760` resolves the Epic within its PRD, the same key `/product-workflows:specify` used to land `specification.md`". The design page says "The run resolves `EPIC-98760` as the focus Epic within PRD `PRODUCT-1234`". But `/epics` mints every Epic key as the PRD key plus a two-digit segment, in a folder `EPIC-<PRD-KEY>-NN-<eslug>/` (`plugins/product-workflows/docs/commands/epics.md:69`; this plugin's own layout block at `plugins/dev-workflows/docs/reference/environment.md:76` shows `EPIC-<KEY>-NN-<eslug>/`). An Epic of PRD `PRODUCT-1234` is `PRODUCT-1234-01`. Under `workflows-core:addressing` §1 `read-key`, `EPIC-98760` is the whole key `EPIC-98760`, because `98760` alone is not a valid key. It is not "`EPIC-` plus key `98760`", which is how the example reads. The other pages in the same plugin use the minted shape: `BOOK-1-02` (`conformance.md:99`) and `ACME-77-01` (`commit-convention.md:6`). The security getting-started uses `ACME-7-01`.
- **Failure scenario:** A new user reads that a folder `EPIC-PRODUCT-1234-01-alerts/` is addressed as `EPIC-98760` and types `EPIC-01` or `EPIC-1234`. Either stops with `DESIGN_NEEDS_KEY` or finds no folder. The same user cannot connect the example to the folders `/epics` created.
- **Evidence:** `grep -rn 'EPIC-98760' plugins/dev-workflows/docs` (11 lines across 5 pages); `addressing.md` §1 `read-key` rules 1 and 3; `epics.md:69`.
- **Suggested fix:** Use a minted key everywhere, for example `PRODUCT-1234-01` (or `EPIC-PRODUCT-1234-01` to show the prefix form). In getting started, add one sentence: an Epic's key is its PRD's key plus `-NN`, and the `EPIC-` prefix is optional. Make the session-cost sample entry follow the same shape.
- **Source:** review
- **Confidence:** high

### DQD-B2 — MINOR — The `/implement` page's example promises a next step the command no longer offers
- **Where:** `plugins/dev-workflows/docs/commands/implement.md:108`
- **What is wrong:** "…closes with the four Phase 4 maintenance agents and the Final Report — recommending the next Epic, or `/docs-workflows:document` once every Epic under the PRD is implemented." The command's `### Next step` (`plugins/dev-workflows/commands/implement.md:1291`) follows the dev lane. That lane offers, before the pull request merges, `/dev-workflows:conformance <EPIC>` and then `/security-workflows:scan <EPIC>`, then the remaining Epics. Once every Epic has merged it offers the PE's `/dev-workflows:conformance <PRD>`, and only then `/docs-workflows:document <PRD>` (`next-phase-offer.md:318-319`). Nowhere on the `/implement` page does a user learn that `/conformance` and the security scan are the next step after an Epic. Its *See also* (`:110-`) does not link `/conformance` either.
- **Failure scenario:** A Dev following the page goes straight to the next Epic or to `/document`. They skip the pre-merge conformance check and scan that the family's delivery assumes. `/dev-workflows:conformance`'s own page says `/implement` "offers this command as its next step" (`conformance.md:105`), so the two pages contradict each other.
- **Evidence:** compared the example's sentence with `next-phase-offer.md:318` and `commands/implement.md:1291-1302`.
- **Suggested fix:** Rewrite the example's ending: "…and the Final Report, whose next step is `/dev-workflows:conformance EPIC-…` and then `/security-workflows:scan`, before the pull request merges." Add a short *What comes next* paragraph and a `/conformance` see-also link.
- **Source:** review
- **Confidence:** high

### DQD-B3 — MINOR — The dev workflow diagram skips the PE's PRD-level `/conformance` before documentation, and sends every *amend the document* to `/specify`
- **Where:** `plugins/dev-workflows/docs/workflow.md:28`, `:31`
- **What is wrong:** The diagram draws `implement -.->|code + implementation.md, in docs-workflows| docsplugin` directly. It has no edge for the lane's "once ALL Epics implemented and merged → PE → `/dev-workflows:conformance <PRD>` → `/docs-workflows:document <PRD>`" (`next-phase-offer.md:319`), nor for "`/dev-workflows:conformance <PRD>` … once settled → `/docs-workflows:document <PRD>`" (`:321`). The single `conformance -.->|"PRD: the PE, every Epic merged — amend the document"| specify` edge says an amendment always goes to `/specify`. The lane sends it to "the command its note names" (`:321`), which can be `/update-prd` or `/create-ard` too.
- **Failure scenario:** A reader takes the diagram as the order of work. They go from the last `/implement` straight to `/document`, without the PE's PRD conformance run the docs and offers expect first. Or they run `/specify` to amend a PRD-level requirement.
- **Evidence:** diagram lines 21-31 read against `next-phase-offer.md:316-321`.
- **Suggested fix:** Route the docs edge from `conformance` ("PRD: once settled") instead of from `implement`, or add that edge beside it. Relabel the amend edge to "amend the document — the command its note names" and point it at the `PMPRD` subgraph rather than at `specify` alone.
- **Source:** review
- **Confidence:** medium

### DQD-B4 — MINOR — The environment layout files follow-ups under `dev-workflows/`, contradicting the follow-ups and roles pages
- **Where:** `plugins/dev-workflows/docs/reference/environment.md:77`
- **What is wrong:** The layout block says `dev-workflows/                  # bookkeeping: feedback, cost, resume.md, follow-ups`. The follow-ups page says "**`follow-ups.md` in the folder the run resolved**, appended, alongside the artifacts the follow-ups are about" (`reference/follow-ups.md:24`). The roles page says "Two records land outside that subfolder … follow-up tasks, in the folder the run resolved" (`workflow.md:60`).
- **Failure scenario:** A user looking for the follow-ups `/implement` or `/conformance` wrote searches `<PRD-dir>/dev-workflows/` and finds nothing. The tasks are in the Epic folder's `follow-ups.md`.
- **Evidence:** the three lines quoted.
- **Suggested fix:** Drop `follow-ups` from the `dev-workflows/` comment. Add a `follow-ups.md`, `implementation.md` line under the PRD and `EPIC-` folders.
- **Source:** review
- **Confidence:** high

### DQD-B5 — MINOR — "`dev-workflows` reads five environment variables" counts one it never reads
- **Where:** `plugins/dev-workflows/docs/getting-started.md:38`; `plugins/dev-workflows/docs/reference/environment.md:3` ("The plugin reads five user-settable variables")
- **What is wrong:** One of the five is `DOCS_PATH`. The same page says "None of this plugin's own six commands grounds against it … It is documented here only because `code-handoff.md`'s git finish states plainly that it never touches this path either — a boundary statement, not a consumer" (`getting-started.md:50`). `grep -rn DOCS_PATH plugins/dev-workflows/{commands,agents,references,hooks,scripts}` hits only `references/code-handoff.md:360`, a "never touches" sentence.
- **Failure scenario:** A new user setting up from *What you set on your machine* spends time on a docs clone and `DOCS_PATH` that this plugin never uses. Or they conclude that `/implement` reads their docs.
- **Evidence:** grep above; both sentences quoted.
- **Suggested fix:** "reads four … `DOCS_PATH` is not read by this plugin; it is listed here because the companion plugins read it". Or move the `DOCS_PATH` section under a "read by companion plugins, not this one" heading.
- **Source:** review
- **Confidence:** high

### DQD-B6 — MINOR — The dev Session cost page's worked example names product-workflows commands as "dev-workflows commands", and leaks an internal team count
- **Where:** `plugins/dev-workflows/docs/reference/session-cost.md:13`
- **What is wrong:** "A single session that runs several dev-workflows commands in a row — `/idea` then `/create-prd` then `/specify`, say — appends one entry per command invocation". Those three ship in `product-workflows`. Line 38 of the same page says so: "Twelve more commands that used to make this list — `/idea`, `/create-prd` … — ship in the companion `product-workflows` plugin now". The same paragraph also says "the largest PRD to date was worked by 23 teams". That is a statistic about the organisation the plugin came from, which no user can check or use.
- **Failure scenario:** A dev-workflows user is told that `/idea` is one of this plugin's commands, contradicting the README's command table. The "23 teams" figure reads as an operational fact about the user's own repository.
- **Evidence:** lines 13 and 38 of the page.
- **Suggested fix:** Use `/design` then `/implement` then `/conformance` as the example. Replace the team count with "a PRD worked by many teams".
- **Source:** review
- **Confidence:** high

### DQD-B7 — MINOR — Maintainer vocabulary and change history fill the user pages
- **Where (examples, not exhaustive):**
  - change history addressed to no user: `plugins/dev-workflows/docs/getting-started.md:34` ("This page used to say the first line alone was enough"); `commands/vuln.md:7` and `commands/upgrade.md:7` ("the rule lived only on this page until it was restated there"); `reference/follow-ups.md:34` ("It used to have four rungs, the first of which was a vault"); `commands/ready.md:23` ("A block an `/implement` run before 4.1.2 left…"); `reference/agents.md:3` (the 19 agent names that moved out); `reference/hooks.md:9`, `:11`, `:17` (how `preload-context` was split)
  - maintainer recipes: `getting-started.md:21` ("`grep -ln 'WebFetch\|WebSearch' plugins/dev-workflows/agents/*.md` re-derives that set rather than trusting this list" — a repository path a user of the installed cache does not have); `reference/environment.md:3` ("the names the plugin's own inventory check encounters while scanning for `$VAR` reads … `OSTYPE`, `BASH_SOURCE`, `BASH_REMATCH`, `ROOT`, and `OWNER_REPO`"); `security-workflows/docs/reference/environment.md:3` (the same)
  - harness and reference internals: `commands/implement.md:15` ("`$ARGUMENTS` resolves to one of two modes"); `roles-and-phases.md:12`, `:26` and `commands/ready.md:54`, `:82` (three restatements of `/product-workflows:brd-reconcile`'s "cross-BRD write guard, and a `--sent` run's redundancy check at Phase 0 step 6, which reads the gate inverted (`phase-handoff` §3.7)" — a BRD-route detail with no bearing on any dev-workflows command); `commands/design.md:58` ("Of this plugin's three gated inputs" — never named — "§3.3 rows D/E"); about 40 lines carrying `§` citations into `workflows-core` references the user never sees (`grep -rc '§' plugins/dev-workflows/docs`); security `roles-and-phases.md:42` and `reference/session-cost.md:7-11` ("passes `phase: inferred, role: inferred` with the run's role as `run_role`", "Its §7 row names it by its bare name, `/scan`"); raw `choices: [...]` arrays on `security-workflows/docs/commands/scan.md` (5 lines) and `dev-workflows/docs/reference/environment.md:11`
- **What is wrong:** These are notes for the maintainer, history of earlier releases, and citations into internal references. The brief names them as user-facing defects. The BRD-reconcile caveat is repeated four times across two dev pages. Its terms ("stopping row", "reads the gate inverted") are defined nowhere a dev-workflows user can reach.
- **Failure scenario:** A new user reading Roles and phases to learn what the Dev owns meets three lines on a command of another plugin's BRD route. A user told to "re-derive that set" with a repository-relative `grep` has no `plugins/` directory in the installed cache. A user who sees "before 4.1.2" cannot tell whether it applies to their tree.
- **Evidence:** lines quoted. Ran `grep -rn 'used to\|until it was\|before 4\.' plugins/dev-workflows/docs plugins/security-workflows/docs`.
- **Suggested fix:** Move history to `CHANGELOG.md` and maintainer recipes to `docs/maintainers/`. Cut the `/brd-reconcile` caveat from the dev pages: "`/ready` is the one command here whose gate never stops it" is enough. Replace each `§` citation with what it means, in plain words, and keep at most one link to the companion plugin's page. Show the options of a question as prose (*Set SPECS_PATH* / *Cancel*) rather than as a `choices:` array.
- **Source:** review
- **Confidence:** high (that the text is there); the impact is reader confusion, not a wrong run

### DQD-B8 — MINOR — The `/vuln` and `/upgrade` diagrams leave out the commit, push and pull request step, and the per-unit loop
- **Where:** `plugins/dev-workflows/docs/commands/vuln.md:25-35`, `plugins/dev-workflows/docs/commands/upgrade.md:23-35`
- **What is wrong:** `/vuln`'s diagram ends `tv --> s4["Step 4 — Summarise"]`. `/upgrade`'s ends `tv --> done["Collect results → Post-batch maintenance"]`. Neither draws the commit `code-handoff` makes per CVE (Step 3.9) or per component (step 6.5), nor the consent-gated push and pull request (per CVE, or once for the batch at step 7.5). Neither draws the loop back for the next CVE or component, nor the rule that a commit that does not land ends the loop (workflow map in `.claude/rules/dev-workflows.md`). These steps are the user-visible result of both commands, and the only point where the user is asked a question after the plan.
- **Failure scenario:** A reader of either diagram cannot tell that one pull request is opened per CVE and one per upgrade batch, or that they will be asked about pushing. The prose under each diagram says so only in the example paragraph.
- **Evidence:** diagrams read against `commands/vuln.md` `## Git Workflow` and the rules-file workflow map lines for `/vuln` and `/upgrade`.
- **Suggested fix:** Add `tv --> commit["Commit (per CVE / per component) → push + PR behind one consent choice"]`, a loop edge back to the next unit, and a "commit did not land → stop" edge.
- **Source:** review
- **Confidence:** high

### DQD-B9 — NIT — The security workflow diagram draws `/dev-workflows:conformance` as an edge label, not a node, and omits the scan's own next step to the PE's `/conformance <PRD>`
- **Where:** `plugins/security-workflows/docs/workflow.md:23`, `:5-38`
- **What is wrong:** `implement -.->|"action: offered after /dev-workflows:conformance, before the merge"| scan`. `/dev-workflows:conformance` has no node, so its own offer of the scan ("where it decided no fix", stated at `:49`) cannot be drawn. The lane's offers after a change scan — the remaining Epics, then "the PE's `/dev-workflows:conformance <PRD>`" (`next-phase-offer.md:322`; `docs/commands/scan.md:165`), and a change scan from each other repository the Epic names — have no edge either.
- **Failure scenario:** A Dev reading only the diagram sees `/implement` hand straight to the scan. They do not learn that `/conformance` comes first, or that the PE's PRD check follows the merge. The ASCII block on `getting-started.md:68-79` shows both, so the two pages differ.
- **Evidence:** diagram vs `next-phase-offer.md:320-322`.
- **Suggested fix:** Add a `conformance["/dev-workflows:conformance"]:::dev` node in the DEV subgraph, with edges `implement → conformance → scan`. Add a dashed `scan -.->|"after the merge: the PE"| prdconf["/dev-workflows:conformance PRD"]`.
- **Source:** review
- **Confidence:** medium

### DQD-B10 — NIT — The register's status diagram has no `reopened → open` edge, though triage suggests *decide later* for a reopened finding
- **Where:** `plugins/security-workflows/docs/reference/security-register.md:66-101`
- **What is wrong:** The diagram's edges out of `reopened` are `fix`, `false_positive`, `accepted_risk` and `fixed`. The scan page's triage says the suggested decision is "**decide later** for the rest, on a new, reopened or open row" (`docs/commands/scan.md:110`), and decide later records `open` (status table, `:58`). The suggestion `/security-workflows:scan` makes for a reopened MEDIUM or LOW finding is therefore a move the diagram does not draw.
- **Failure scenario:** A Security Engineer checking the diagram thinks a reopened finding cannot go back to *decide later*.
- **Evidence:** diagram lines read against `scan.md:110` and the status table.
- **Suggested fix:** Add `reopened --> open: decide later`.
- **Source:** review
- **Confidence:** medium (`register.py`'s decision validation was not read; `security-register-format` §4 names no restriction)

### DQD-B11 — NIT — Missing space joins two paragraphs on the `/ready` page
- **Where:** `plugins/dev-workflows/docs/commands/ready.md:62`
- **What is wrong:** "…never `_readiness.md` itself.Phase 7 additionally emits one follow-up per named readiness gap…"
- **Failure scenario:** The follow-up rule reads as part of the handoff sentence. Cosmetic.
- **Evidence:** `grep -n 'itself.Phase' plugins/dev-workflows/docs/commands/ready.md`.
- **Suggested fix:** Start a new paragraph at "Phase 7".
- **Source:** review
- **Confidence:** high

## documentation quality — product-workflows

### DQP-B1 — MINOR — Getting started promises a handoff and a `/create-prd` takeover that a run with an unanswered question never gets
- **Where:** `plugins/product-workflows/docs/getting-started.md:78`, `:80`
- **What is wrong:** Step 1 says *"a question you cannot answer yet becomes a logged `[NEEDS CLARIFICATION]` marker rather than a blocker"*. Step 3 says *"At the end it offers to commit the brief, push it, and open a pull request … Once that lands, `/create-prd ACME-77` finds `idea.md`"*. But any open marker makes the brief `status: draft`, and a draft is never handed off and no offer is made: `commands/idea.md:705` (*"`status: draft` … **never hand off**, and do not ask"*), and the command's own docs page says the same at `docs/commands/idea.md:157`. On a draft, `/create-prd ACME-77` with no path does not read the brief in contract (`commands/idea.md:714-723`). Only `/idea <KEY> <same source>` or `/create-prd <KEY> @<path>` work.
- **Failure scenario:** A new PM skips one of the ten questions, as the page invites. No commit or PR offer appears. They then run `/create-prd ACME-77`, which names the brief but does not read it, and grills from scratch or offers a same-session idea.
- **Evidence:** Read getting-started steps 1–3 against `commands/idea.md:700-723` and the docs page's *Gates* section.
- **Suggested fix:** In step 1, say that an unanswered question leaves the brief a draft. In step 3, say the handoff is offered only for a refined brief, and name the two ways forward from a draft: re-run `/idea` with the same source, or `/create-prd <KEY> @<path>`.
- **Source:** review
- **Confidence:** high

### DQP-B2 — MINOR — Getting started never tells the reader to merge the pull request, or what to do with a specs repo that has no remote
- **Where:** `plugins/product-workflows/docs/getting-started.md:80` (*"Once that lands, `/create-prd ACME-77` finds `idea.md`"*); `:40` (the `SPECS_PATH` section)
- **What is wrong:** "Once that lands" is the page's only hint that the reader must merge the pull request before the next command. While it is open, `/create-prd` stops (`docs/commands/idea.md:180`). The page also never says the specs repo must be a git repository, or what happens without an `origin` remote. In that case the handoff commits on a plugin branch, pushes nothing, opens no PR, and reports *"The phase is NOT handed off"* (`workflows-core/references/phase-handoff.md:445`). The next command then stops on that unmerged branch until the reader merges it locally. None of this is on the page, and the page has no `export` example either. The root README has one (`README.md:86`), but only the "Prerequisites" anchor is linked from here.
- **Failure scenario:** A PM runs `/idea`, accepts the PR offer, and runs `/create-prd ACME-77` at once. It stops on the open PR. Or a PM working in a local-only specs repo is told the phase is not handed off, and no page explains how to continue.
- **Evidence:** Read getting-started end to end, and `phase-handoff.md:44`, `:108` and `:445`.
- **Suggested fix:** Add a "Before you start" block: create or clone a specs git repository (with an `origin` for PRs), and give a three-line `export SPECS_PATH=…` example. In step 3, add "merge the pull request (or, with no remote, merge the `idea/…` branch into your default branch), then run `/create-prd ACME-77`".
- **Source:** review
- **Confidence:** high

### DQP-B3 — MINOR — The BRD-route parameter table lists `@<idea.md>` as an optional argument of `/create-prd` on that route; the command skips the idea ladder there entirely
- **Where:** `plugins/product-workflows/docs/brd-workflow.md:284` (`/create-prd` row, Optional: *"`--lean`/`--hybrid`/`--full`, `--no-docs`, `--docs <path>`, `@<idea.md>`"*), in a table whose last three rows are *"shown in their the BRD route form only"* (`:273`)
- **What is wrong:** `commands/create-prd.md:90` says *"Resolve `idea.md` … **Skipped entirely on the BRD route**, where `prd-seed.md` is the seed and there is no `idea.md` to find"*. The rules file puts it the same way: *"no idea ladder"* (`.claude/rules/brd-route.md` BRD route tail). `workflow.md:162` gives the same row without `@<idea.md>`, so the two copies of the table disagree.
- **Failure scenario:** A PM hands a slice an idea file through `@`, expecting it to seed the PRD. It is never read on that route.
- **Evidence:** Compared the two tables, then read `commands/create-prd.md:90-93`.
- **Suggested fix:** Drop `@<idea.md>` from the BRD-route row.
- **Source:** review
- **Confidence:** high

### DQP-B4 — MINOR — The `/create-prd` page says the BRD route seeds from `prd-seed.md`, which a normal BRD route never has
- **Where:** `plugins/product-workflows/docs/commands/create-prd.md:3` (*"a decided BRD slice's register and seed"*), `:17` (*"the run seeds the PRD from that BRD's `prd-seed.md` and `decisions.md`"*)
- **What is wrong:** `brd-workflow.md:421-426` says `--sort-existing` is *"the only writer of any of the three"* seeds and that *"a reconciled BRD normally holds no seed at all, so each of those runs reports its seed absent as the **ordinary** case"*. `.claude/rules/brd-route.md` warns against wording that sends a reader after a seed file that does not exist. A PM reading the `/create-prd` page expects a `prd-seed.md` and goes looking for it. The two pages contradict each other.
- **Failure scenario:** A PM sees "prd-seed absent" in the run and thinks the route lost content.
- **Evidence:** Compared `create-prd.md:17` with `brd-workflow.md:421-429`.
- **Suggested fix:** Reword to "seeds the PRD from the slice's `decisions.md` (filtered by altitude) and its grounding findings; a `prd-seed.md` exists only after a `--sort-existing` migration".
- **Source:** review
- **Confidence:** high

### DQP-B5 — MINOR — The main workflow diagram routes `/implement` straight to the docs commands, leaves out the security scan, and gives the PE's PRD conformance no edge onward
- **Where:** `plugins/product-workflows/docs/workflow.md:65-70`, `:91`, `:192-198`
- **What is wrong:** The diagram draws `implement -.->|code + implementation.md, in docs-workflows| docsplugin` (`:91`), and `conformanceprd` has edges only back to `specify`, `epics` and `updatevi` (`:68-70`). The routing graph is different. `/implement` goes to `/conformance <EPIC>`, then `/security-workflows:scan <EPIC>`, then the remaining Epics. Once all have merged, `/conformance <PRD>` goes to `/docs-workflows:document` and then `/release-notes`, and `/conformance <PRD>` → *"once settled → `/docs-workflows:document <PRD>`"* (`workflows-core/references/next-phase-offer.md`, part `dev`). `/security-workflows:scan` appears nowhere in `workflow.md`. Its *Cross-cutting commands* list (`:192-198`) names the commands of `workflows-core`, `docs-workflows` and `dev-workflows` but not `security-workflows`. Meanwhile `roles-and-phases.md:46` does name `/security-workflows:scan`.
- **Failure scenario:** A PE following the diagram thinks the docs run follows `/implement` directly. They never learn that `/conformance <PRD>` is the gate before docs, or that a security scan sits between an Epic's implementation and its merge.
- **Evidence:** `grep -n security plugins/product-workflows/docs/workflow.md` returns nothing. The edge list was read against the `next-phase-offer.md` routing graph.
- **Suggested fix:** Replace the `implement → docsplugin` edge with `conformanceprd -.->|"settled"| docsplugin`. Add a `/security-workflows:scan` node (class `dev`) between `conformanceepic` and the merge. Add a `security-workflows` bullet to *Cross-cutting commands*.
- **Source:** review (and spec `docs/superpowers/specs/2026-10-12-conformance-design.md` D22, see DQP-G2)
- **Confidence:** high

### DQP-B6 — MINOR — Both workflow diagrams leave out offers their commands make, and `brd-workflow.md` describes the re-entry from `/brd-reconcile` as two edges when it is four
- **Where:** `plugins/product-workflows/docs/workflow.md:46-90`; `plugins/product-workflows/docs/brd-workflow.md:41-58`, `:104-106` (*"The two dashed edges leaving `/brd-reconcile` are different in kind … either state is settled by running the command that owns it again"*)
- **What is wrong:** The routing graph (`next-phase-offer.md`, parts `pa`, `pe`, `brd`, `proposals`) makes these offers, and neither diagram draws them:
  - `/create-ard <PRD>` → `/specify <PRD>`, and Epic-level `/create-ard <EPIC>` → `/specify <EPIC>` (recommended). `createard` has no edge to `specify`.
  - `/epics` → `/create-ard <EPIC>` (optional PA).
  - `/brd-interview` → another round, and → `/prd-ground` for a question no finding bears on yet.
  - `/brd-reconcile` → `/prd-ground <KEY> --rebaseline` where the review challenged a code claim, and → `/brd-reconcile` again on the same review where a dependent's sweep was only recorded. That makes four re-entry routes, not the two the prose names.
  - `/prd-proposal` → `/create-ard` / `/specify` to raise the tier; `/brd-proposal` → `/prd-proposal <SLICE>` re-runs.

  `workflow.md:101` excuses sparse edges only for the ARD's *consumers*, not for next-step offers.
- **Failure scenario:** A PA who has just merged a PRD-level ARD finds no route to `/specify` in the diagram. A PM whose customer review challenged a code claim does not learn that `--rebaseline` grounding is the next step.
- **Evidence:** Edge lists read against `plugins/workflows-core/references/next-phase-offer.md:178-330`.
- **Suggested fix:** Add the dashed edges, or state under each diagram that it draws only the main forward path and link each command page's next-step section. Rewrite `brd-workflow.md:104-106` to name all four re-entry routes.
- **Source:** review
- **Confidence:** high

### DQP-B7 — MINOR — Internal rulings and reference-section citations leak into user pages, with no link a user could follow
- **Where (rulings, `D<n>`):** `roles-and-phases.md:24` *"(D5)"*; `workflow.md:168` *"(D4)"*; `commands/create-prd.md:49` *"(D7)"*; `commands/specify.md:15` *"(D4)"*; `commands/brd-reconcile.md:80` *"it is decision row D14"*, `:498` *"the D20 failure"*; `reference/references.md:12` *"the D23 roll-up"*, `:13` *"the D19 rule"*, `:16` *"(D12)"* and *"(D18)"*, `:17` *"the D13 rule"*.
- **Where (`§` citations):** 135 occurrences across 23 of the 31 pages (`grep -o "§" …`). Examples: `roles-and-phases.md:10` *"`workflows-core:phase-handoff` §3.4 lists them"*, `:12` *"§3.7"*; `commands/idea.md:26` *"(`workflows-core:run-flags` §5 step 3)"*, `:44` *"the §2.1 Sonnet chain"*; `brd-workflow.md:380` *"`workflows-core:grounding-format` §6.1"*.
- **Where (internal field names and gate mechanics):** `roles-and-phases.md:41` *"(`vi_spec_present: false`)"*; `commands/idea.md:44` *"`detection_model` … `current_model`"*; `commands/prd-ground.md:11-14` and `commands/epics.md:19` open on how the kind gate tests a directory prefix and not the asserted `kind:`.
- **What is wrong:** `D<n>` is a row of a design spec removed from the tree. A user has no page that defines it. The `workflows-core:<name> §n` citations name files inside another plugin, and the docs neither link nor summarise them. "Look it up in §3.4" sends a PM to a reference meant for agents, which `getting-started.md` never tells them how to find.
- **Failure scenario:** A PM reads "(D5)" or "§3.4 lists them" and cannot find what it refers to. That list of which commands stop on an absent input is exactly what `roles-and-phases.md:10` withholds.
- **Evidence:** Grep counts per page (rulings: 13 sites in 7 pages; `§`: 135 in 23 pages).
- **Suggested fix:** Delete the `(D<n>)` tags and say the rule in words. Where a `§` citation carries information the reader needs (the list in `phase-handoff` §3.4), inline the list. Elsewhere, keep at most one plain "defined in the shared `workflows-core` references" note per page.
- **Source:** review
- **Confidence:** high

### DQP-B8 — MINOR — The docs teach example keys that carry a folder-kind token, and use a different key on every BRD-route page
- **Where:** `brd-workflow.md:300-301` (*"a BRD owning its source document is keyed `EPIC-008` and a slice of it `EPIC-008-01`"*); `commands/prd-ground.md:575` (`/product-workflows:prd-ground PRD-2201` on the idea route); `commands/specify.md:109` (`/product-workflows:specify EPIC-98761` for *"a single Epic"*); BRD pages: `brd-intake.md` `ACME-001`, `brd-split.md`/`brd-interview.md`/`brd-package.md` `EPIC-008`, `brd-reconcile.md` `EPIC-008-01`, `brd-proposal.md` `PRODUCT-1234`
- **What is wrong:** A folder is `<KIND>-<KEY>-<slug>` with kind `BRD`/`PRD`/`EPIC` (`getting-started.md:40`). Examples whose *key* is `EPIC-008` or `PRD-2201` give folders named `BRD-EPIC-008-…`, `PRD-EPIC-008-01-…` and `PRD-PRD-2201-…`. They lead a reader to think the key carries the folder kind. Here `EPIC-008-01` is a BRD *slice* and `EPIC-98761` a focus Epic, while a real Epic's key is `<PRD-KEY>-NN` (`roles-and-phases.md:40`). Addressing has to special-case keys that begin with a kind token (`.claude/rules/brd-route.md`, the prefix rule). Across the BRD route the key also changes on every page, so a reader cannot follow one BRD from intake to reconciliation.
- **Failure scenario:** A PM keys their first BRD `BRD-12` or their first Epic `EPIC-5`, copying the pages. They get doubled-prefix folders and keys that are hard to tell apart from folder names.
- **Evidence:** `grep -oE '/[a-z-]+ [A-Z][A-Z0-9_]*(-[0-9]+)+'` over every page; the keys per page are those listed under **Where**.
- **Suggested fix:** Use one neutral key family across the plugin, e.g. BRD `ACME-001`, slices `ACME-001-01`/`-02`, idea-route PRD `ACME-77`, Epic `ACME-77-01`. Use it on every BRD-route page and in both workflow pages. (The earlier finding BRD2-B7 fixes only the root-vs-slice level of two of these examples.)
- **Source:** review
- **Confidence:** medium (the keys are valid by grammar, but the confusion is the defect)

### DQP-B9 — NIT — "Two segments or three" contradicts the key grammar, which fixes no depth
- **Where:** `workflow.md:168` (*"`<SLICE-KEY>` is `^[A-Z][A-Z0-9_]*(-\d+)+$` — **two segments or three**"*); `brd-workflow.md:300` (*"**That shape is two segments or three**"*)
- **What is wrong:** `CLAUDE.md` and `commands/create-prd.md` docs page `:15` say the grammar *"fixes no depth"*. `ACME-1-2-3` is valid. The same `brd-workflow.md` paragraph then says *"a key's segment count is a naming convention, never a depth declaration"*, which contradicts its own bold sentence.
- **Suggested fix:** Replace with "one or more numeric segments; the grammar fixes no depth".
- **Source:** review
- **Confidence:** high

### DQP-B10 — NIT — `brd-workflow.md` and `prd-ground.md` carry search-and-replace residue and development-history wording
- **Where:** `brd-workflow.md:12` and `commands/prd-ground.md:56` (*"where so, a PA or PE runs it instead where the PM cannot clone the code repositories"*, with the condition doubled); `brd-workflow.md:234` (a sentence starting in lower case: *"the BRD route **ships** on …"*); `:273` (*"shown in their the BRD route form only"*); `:243` (*"the one this increment added"*); `:272` (*"not a preview of what a later increment adds"*); `getting-started.md:32` (*"This page used to say the first line alone was enough"*); `commands/idea.md:51` (*"past the old bounds"*), `:53` (*"exactly as a broken link always has"*), `:141` (*"the finder that searched a personal store … is gone"*); `commands/update-prd.md:59` (*"The run used to end with a manual reminder …"*); `reference/environment.md:13` (*"it used to be indistinguishable"*)
- **What is wrong:** A new user has no "increment" and no earlier version to compare against. These sentences describe a change history that belongs in `CHANGELOG.md`. The garbled ones read as errors.
- **Suggested fix:** Fix the three garbled sentences. Delete or rewrite the history clauses as present-tense facts.
- **Source:** review
- **Confidence:** high

### DQP-B11 — NIT — The `/idea` page names a personal-vault path and lists "a file" and "a saved file" as different sources
- **Where:** `commands/idea.md:3` (*"a prompt, a file, a community post, or a saved file"*), `:17` (*"a saved community post the operator downloaded (typically under `Projects/Products/…`)"*)
- **What is wrong:** The synopsis gives exactly two forms (`:15`, *"one of **two** source forms"*). The four-item opener contradicts it. `Projects/Products/…` is someone's vault layout, not a convention of the plugin.
- **Suggested fix:** "Refines one raw source — an inline prompt or a markdown file (a note, a saved community post, a PRD) — …". Drop the path.
- **Source:** review
- **Confidence:** high

### DQP-B12 — NIT — The workflow page's role and artifact-home tables disagree with the roles page and the `/specify` page
- **Where:** `workflow.md:176` (PA row: runs only *"`/create-ard` (optional)"*); `:177` (PE row: `/epics`, `/specify` only); `:183` (*"the PRD and the ARD, with `specification.md` in the `EPIC-` folders below it"*)
- **What is wrong:** `README.md:15` and `roles-and-phases.md:29` give the PA `/harvest-decisions` and `/promote-decisions` too. `roles-and-phases.md:38` gives the PE `/dev-workflows:conformance <PRD-KEY>`. A broad PRD-level `specification.md` lives in the PRD folder itself (`commands/specify.md:92`, and `workflow.md:60`'s own *"PRD-level specification.md"* edge).
- **Suggested fix:** Bring the two rows into line with the roles page. Say "`specification.md` in the PRD folder (PRD-level) or in each `EPIC-` folder".
- **Source:** review
- **Confidence:** high

### DQP-B13 — NIT — Getting started says the three optional variables each "degrade to a documented default or a silent skip"; two do not
- **Where:** `getting-started.md:36`
- **What is wrong:** When `$REPOS_PATH` has no existing entry, `/create-ard`, `/specify`, `/epics` and `/prd-ground` ask you to set it, and `/prd-ground` offers only *Set REPOS_PATH* or *Cancel* (`reference/environment.md:25`). An unset `$ARCHITECTURE_REPO_PATH` reports `OFF` *"with a line naming the variable"* (`environment.md:33`). That is neither a default nor silent.
- **Suggested fix:** "the other three are optional: `DOCS_PATH` is skipped silently, `ARCHITECTURE_REPO_PATH` is reported off, and `REPOS_PATH` defaults to `/workspace` and is asked for where that does not exist".
- **Source:** review
- **Confidence:** high

### DQP-B14 — NIT — The README's documentation table leaves out three reference pages that the sibling README lists
- **Where:** `plugins/product-workflows/README.md:24-36`
- **What is wrong:** The table has no rows for [Effort proposals](docs/reference/proposal-format.md), [Session feedback](docs/reference/session-feedback.md) or [Resume and checkpoints](docs/reference/resume-and-checkpoints.md). `plugins/dev-workflows/README.md:35,37` lists its Session feedback and Resume pages. Effort proposals is the one page a PM sends a customer about. `README.md:20` also calls the twelve `references/` files "reference pages", although the docs tree has nine pages under `docs/reference/`.
- **Suggested fix:** Add the three rows. Say "twelve reference files (see References)".
- **Source:** review
- **Confidence:** high

### DQP-B15 — MINOR — Nine of the 16 command pages never link to either workflow page
- **Where:** `docs/commands/brd-intake.md`, `brd-interview.md`, `brd-package.md`, `brd-reconcile.md`, `brd-split.md`, `prd-ground.md`, `epics.md`, `idea.md`, `update-prd.md` (`grep -c "workflow.md"` = 0 on each)
- **What is wrong:** None of the six BRD-route pages links [BRD workflow](../brd-workflow.md), the page that shows how they chain together. `idea.md`, `epics.md` and `update-prd.md` do not link [Workflow overview](../workflow.md). The other seven pages do.
- **Failure scenario:** A PM who lands on `/brd-interview` from a search cannot reach the route diagram or the parameter table from that page.
- **Suggested fix:** Add the route page (BRD pages) or the overview (idea-route pages) as the first *See also* item on every command page.
- **Source:** review
- **Confidence:** high

### DQP-B16 — NIT — Three reference paragraphs are too long for a person to read
- **Where:** `reference/resume-and-checkpoints.md:19` (one paragraph of 13,886 characters on carry-forward settling, including `git blame --porcelain` dating rules and `/security-workflows:scan` 0.2.0 compatibility); `reference/environment.md:15` (6,051 characters on `SPECS_PATH_INSIDE_TREE`); `commands/idea.md:138` (3,046 characters on `IDEA_NOT_AN_IDEA_FOLDER`'s named next commands)
- **What is wrong:** These are agent-facing contracts pasted into user pages. A PM looking for "what happens if my `SPECS_PATH` is wrong" or "why is this item still in my resume pointer" cannot pull the answer out of them.
- **Suggested fix:** Lead each with a short user-facing summary (the symptom, what to do), and move or link the full contract.
- **Source:** review
- **Confidence:** medium (readability, but the length is measured)

## documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki

### DQW-B1 — MAJOR — The docs-workflows Update block leaves out `workflows-core`, which every recent docs-workflows release has to be updated with
- **Where:** `plugins/docs-workflows/docs/getting-started.md:27-33`
- **What is wrong:** The block is `claude plugin marketplace update shipwright` / `claude plugin update docs-workflows@shipwright` / `claude plugin update prose-style@shipwright`, and the text after it says only "**Update `prose-style` with it**". It never mentions `workflows-core`. But `.claude/rules/plugin-updates.md` pairs `docs-workflows` 1.15.0, 1.16.0, 1.17.0 and 1.18.0 with a matching `workflows-core` release (1.39.0, 1.40.0, 1.44.0 and 1.45.0). For 1.17.0 it explains that an older loader reads `args: "escalation-rules review"` as an entry point and "may run a section whose heading merely contains the word". The page also says `claude plugin update` "re-fetches exactly one plugin" (plugin-updates.md: "An update re-fetches exactly one plugin").
- **Failure scenario:** A user on docs-workflows 1.16 / workflows-core 1.43 follows this page. They end up with docs-workflows 1.18.0 beside workflows-core 1.43. Every `/document`, `/docs-audit` and `/release-notes` run then asks an older loader for reference parts it cannot serve, or meets a `next-phase-offer` that disagrees with it (the 1.44.0 and 1.45.0 bullets).
- **Evidence:** I read the Update block and compared it with `plugins/security-workflows/docs/getting-started.md:43-48`. That page lists `claude plugin update workflows-core@shipwright` and says "**Update `workflows-core` with it**". `plugins/docs-workflows/.claude-plugin/plugin.json` is at 1.18.0 and `workflows-core` at 1.45.0.
- **Suggested fix:** Add `claude plugin update workflows-core@shipwright` to the block, with a sentence saying why: the commands load the shared references and the part loader from it at runtime. Follow security-workflows' page.
- **Source:** review
- **Confidence:** high

### DQW-B2 — MAJOR — obsidian-llm-wiki README says the Stop hook updates `hot.md` "at session end", but the hook blocks Claude at the end of every turn
- **Where:** `plugins/obsidian-llm-wiki/README.md:95`, `:224-225`; `plugins/obsidian-llm-wiki/hooks/hooks.json` (the `Stop` entry); also `plugins/obsidian-llm-wiki/CLAUDE.md:77-78`
- **What is wrong:** The README says "Hooks activate automatically: session start reads `hot.md`, session end updates it" and "auto-updated at session end (Stop hook)". The `Stop` hook fires each time the main agent finishes a response. It prints `{"decision":"block","reason":"Read …/skills/wiki-hot/SKILL.md fully, then update wiki/hot.md …"}` whenever `${VAULT_PATH:-$HOME/obsidian_vault}/wiki` exists, and it is suppressed only on the immediate re-stop (`stop_hook_active`). Its own reason text even handles a turn with no wiki activity ("If nothing wiki-related happened this session, update Last Updated…").
- **Failure scenario:** A user installs the plugin, and their machine has `~/obsidian_vault/wiki`. From then on, in every Claude Code session in any repository, each answered prompt is followed by a forced extra cycle: read the skill, then rewrite the vault's `hot.md`. That costs tokens and time and rewrites a file in another repository. The README tells them nothing of this. It also goes against the marketplace convention "Hook scripts must exit 0 — they must never block Claude" (`CLAUDE.md` § Conventions). The plugin keeps its own `CLAUDE.md`, but that file repeats the same "session end" claim.
- **Evidence:** I read `hooks.json`. The Stop command emits `"decision":"block"`. Claude Code's Stop event fires once per completed response, not once per session (SessionEnd is the session-end event).
- **Suggested fix:** At minimum, correct the README (and the plugin's `CLAUDE.md` and `AGENTS.md:25`) to say "after every response, while the vault's `wiki/` exists", and document the cost and how to turn it off. Better: move the update to `SessionEnd`, or gate it on wiki activity in this session.
- **Source:** review
- **Confidence:** medium. The README misstatement is certain. Whether the per-turn firing counts as MAJOR depends on how often users have a vault and the plugin installed while working elsewhere.

### DQW-B3 — MINOR — getting-started's "no docs yet" path sends the new user to `/document` and never mentions `/docs-audit` or the route page
- **Where:** `plugins/docs-workflows/docs/getting-started.md:83`, and the whole page (no occurrence of `docs-audit` or `docs-workflow.md`)
- **What is wrong:** After `/docs-init` the page says: "Then `/docs-workflows:docs-serve` serves the result … and `/document` starts filling it in." That disagrees with three other sources:
  - The route page says that after serving comes `/docs-audit`, then writing units by hand. It also says `/document` "reads no backlog" (`docs-workflow.md:67-81`, `:111`).
  - `/docs-init`'s own Next step says "Then `/docs-workflows:docs-audit <root>` to find out what this portal is still missing" (`commands/docs-init.md:285`).
  - `/document` keyed mode needs a PRD folder with an implementation record, which a cold-start project usually does not have.
- **Failure scenario:** A new user scaffolds a portal, serves it, and then runs `/document` on an empty portal. They have no PRD key, or they get a feature page with no coverage plan. They never learn that `/docs-audit` and the route exist, because getting-started is the page that "takes you from zero to your first successful run" and the route page is its only link to the backlog loop.
- **Evidence:** `grep -n "docs-audit\|docs-workflow.md" getting-started.md` returns nothing.
- **Suggested fix:** Replace the "and `/document` starts filling it in" clause with "then `/docs-workflows:docs-audit` to see what the portal is missing, and follow [The documentation route](docs-workflow.md)". List the route page in the line 3 orientation sentence too.
- **Source:** review
- **Confidence:** high

### DQW-B4 — MINOR — `/docs-serve`'s next-step offer and its docs page name `/document` as the next step, which contradicts the route
- **Where:** `plugins/docs-workflows/commands/docs-serve.md:272`; `plugins/docs-workflows/docs/commands/docs-serve.md:68`; against `plugins/docs-workflows/docs/docs-workflow.md:9-17` (`SERVE --> AUDIT`), `:57-73`, and `plugins/docs-workflows/commands/docs-init.md:285`
- **What is wrong:** The command says "On a successful serve, recommend reviewing the site at the reported URL, then `/docs-workflows:document <address>` to write or update pages once satisfied". The docs page says "[`/document`](document.md) — the natural next step once the served site looks right". On the route page, step 2 (`/docs-serve`) leads to step 3 (`/docs-audit`), and `/document` is only an optional prose aid in step 4. `/docs-init`'s own offer also puts `/docs-audit` after `/docs-serve`.
- **Failure scenario:** A user follows the route: `/docs-init`, then `/docs-serve`. The serve run tells them to run `/document <address>`. That needs a PRD key they do not have, and it skips the audit that the route and `/docs-init` both name. The workflow diagram (`workflow.md:48-52`) draws no edge from `docsserve` to `document` either, so the offer matches no diagram.
- **Evidence:** I read the lines cited.
- **Suggested fix:** Make the offer depend on the backlog. Where no `.dev-workflows/docs-backlog.yml` exists, recommend `/docs-workflows:docs-audit`. Otherwise recommend the route's step 4, with `/document` direct mode as an aid. Mirror that on the docs page's See also.
- **Source:** review
- **Confidence:** high

### DQW-B5 — MINOR — The plugin README draws a third version of the documentation route, and it disagrees with the route page
- **Where:** `plugins/docs-workflows/README.md:21-32`; against `plugins/docs-workflows/docs/docs-workflow.md:9-39`
- **What is wrong:** The README's diagram:
  - draws `WRITE --> CAPTURE --> VERIFY` unconditionally;
  - has no "re-read what review_by has aged" node;
  - puts `/docs-brand` on the route as a separate step between init and serve.

  The route page, which the README calls "the page to read next", draws the following, and its step 1 says `/docs-brand` runs inside `/docs-init`:
  - `WRITE -->|"a how-to or a tutorial"| CAPTURE` and `WRITE -->|"anything else"| VERIFY`;
  - a cadence group with `ROT["re-read what review_by has aged — by hand"]`.
- **Failure scenario:** A reader of the README thinks every page needs a screenshot capture, and never learns that step 8 (the `review_by` re-read) is part of the loop. That matters because the route stresses that "nothing anywhere on this route sets [`review_by`] for you" (`docs-workflow.md:99`).
- **Evidence:** I compared the two mermaid blocks side by side.
- **Suggested fix:** Drop the README's diagram in favour of a one-line link to the route, or copy the route's diagram exactly. Two hand-kept copies of one graph are what drifted here.
- **Source:** review
- **Confidence:** high

### DQW-B6 — MINOR — The split between `workflow.md` and `docs-workflow.md` is unclear: the file names invert the titles, and one command page calls the route "The documentation workflow"
- **Where:** `plugins/docs-workflows/docs/commands/docs-audit.md:7`, `:11`; `plugins/docs-workflows/commands/docs-audit.md:344`; `plugins/docs-workflows/docs/README.md:6-7`
- **What is wrong:** `workflow.md` is titled "Workflow overview" and `docs-workflow.md` is titled "The documentation route". The `/docs-audit` page links `../workflow.md` as "Workflow overview" in one sentence. In the next sentence it links `../docs-workflow.md` as "[The documentation workflow]", and again at `:11`. The command's own Next step names the route only by path ("this plugin's route page, `docs/docs-workflow.md`"), which is a path in a repository the user may not have.
- **Failure scenario:** A reader sees "Workflow overview" and "The documentation workflow" side by side, takes them for the same page, and does not follow the second link. That is the only link to the manual procedure this command's backlog needs. Opening `docs/` by file name, `docs-workflow.md` reads as the plugin's workflow page and `workflow.md` as a generic one.
- **Evidence:** I read the lines cited. `docs-workflow.md:1` is "# The documentation route", and `workflow.md:1` is "# Workflow overview".
- **Suggested fix:** Use "The documentation route" for every link to `docs-workflow.md`. Consider renaming the file to `docs-route.md` (with a redirect note), and have the command's Next step name the page by title.
- **Source:** review
- **Confidence:** high

### DQW-B8 — MINOR — The `/api-guideline-reviewer` page hides that five bundled Spectral rules ship with placeholder literals that fail every real spec at `error`
- **Where:** `plugins/guideline-reviewers/docs/commands/api-guideline-reviewer.md:25`, `:47`, `:53`; `plugins/guideline-reviewers/references/api-guidelines/spectral/ruleset.yaml:33-45`, `:525-539`, `:870-885`
- **What is wrong:** The page says the ruleset pins "the single org-wide tenant-header spelling and the org-wide security-scheme name … as literals". It then says organization-specific rules "deliberately do not ship". It never says that the literals are placeholders: `Example-Tenant`, the `Example-` custom-header prefix, the `oauth2` scheme id, and an open verb list. The ruleset's header names five such rules that "an organization is expected to replace exactly once". Two of them, `api-tenant-header-canonical-spelling` and `api-security-scheme-name-consistent`, are `severity: error`, and errors land under "Mistakes (MUST violations)" (`:47`).
- **Failure scenario:** A user runs the documented example on their real spec, which uses a tenant header such as `Acme-Tenant` and a scheme named `bearerAuth`. They get MUST-level "Mistakes" for both, with no word in the docs that these are placeholders they must override in their own `.spectral.yaml`. The ruleset header holds the explanation, but no docs page points to it. Getting-started even says the command needs no configuration (`docs/getting-started.md:61`).
- **Evidence:** I read the ruleset's header comment and the two rules. `grep -rn "placeholder\|Example-" plugins/guideline-reviewers/docs` returns nothing. Separately, the ruleset contradicts itself: the header says "Five rules carry a placeholder literal", while `:529` says the scheme name is "one of the four an adopting organization replaces".
- **Suggested fix:** Add a "Before your first real run" subsection to the page. Name the five placeholder rules and show the `extends:` override snippet from the ruleset header. Fix "one of the four" to "one of the five".
- **Source:** review
- **Confidence:** high

### DQW-B9 — MINOR — The `/guideline-reviewer` page says it needs "nothing else", but the agent runs a bundled Python scanner that getting-started says needs `python3` 3.11
- **Where:** `plugins/guideline-reviewers/docs/commands/guideline-reviewer.md:19-24`; against `plugins/guideline-reviewers/agents/guideline-reviewer.md:75-85` and `plugins/guideline-reviewers/docs/getting-started.md:61`
- **What is wrong:** The page's "What it needs" says "Nothing else — no `$SPECS_PATH`…". It describes only the ESLint and axe detection as the deterministic step. The agent's "Automated Checks" says "Run automated checks before manual review: `python3 ${CLAUDE_PLUGIN_ROOT}/references/guidelines/check_guidelines.py …`" and calls it "this plugin's own heuristic scanner". Getting-started says "`/guideline-reviewer`'s automated checks need `python3` 3.11". So the command page and getting-started disagree, and the command page never mentions the scanner.
- **Failure scenario:** A user without Python 3.11 reads the command page, expects a pure LLM-plus-ESLint review, and cannot tell why a scanner step fails or produces findings, or where those findings come from.
- **Evidence:** I read the three sites.
- **Suggested fix:** Add the heuristic scanner and its `python3` 3.11 prerequisite to the page's "What it needs" and to its description of what runs before the review passes.
- **Source:** review
- **Confidence:** high

### DQW-B10 — MINOR — The docs-workflows docs leak maintainer vocabulary a user cannot resolve: design-decision ids, `§` citations into references, "ceded" runs and "the split"
- **Where (representative):**
  - `plugins/docs-workflows/docs/commands/docs-serve.md:7` ("D17, the docs-workflow family design's rule … That family is the one the design's §4 table lists") and `:34`
  - `docs/commands/docs-brand.md:33` ("D17, D20", "D25")
  - `docs/reference/environment.md:31` ("(D23)"), and `:11`, which tells the reader to run `grep -lE … plugins/*/commands/*.md` "from the repository root"
  - `docs/commands/docs-profile.md:7` ("§7's list of commands with nothing to inherit … and in §13.2 as a boundary no deferred claim pairs with")
  - `docs/commands/docs-init.md:7` and `docs-audit.md:9`, `:36` ("§10")
  - every command page's run-flag paragraph: "a ceded `/prompt-brainstorm` or `/prompt-grill-me` run" (`document.md:21`, `release-notes.md:19`, `docs-init.md:19`, `docs-audit.md:21`, `docs-brand.md:17`, `reference/session-cost.md:17`)
  - `docs/README.md:58` ("the third increment of the marketplace split")
  - `reference/session-cost.md:31` ("after the split it usually is")
- **What is wrong:** These names are the design's decision ids, section numbers inside `workflows-core` references, and commands of another plugin, in a state ("ceded") no page here defines. A user of the installed plugin cannot follow any of them. The design documents are not shipped, and the `§` targets live in another plugin's `references/`. `grep -c "§"` over `plugins/docs-workflows/docs` counts 32 lines across 11 pages.
- **Failure scenario:** A reader trying to learn why `/docs-serve` has no review gate gets "D17 … the design's §4 table". They cannot find either, and cannot tell whether the rule binds them. The environment page's grep recipe cannot be run from an installed plugin, which has no "repository root".
- **Evidence:** I ran `grep -noE "\bD[0-9]{1,2}\b" -r plugins/docs-workflows/docs` and `grep -n prompt-brainstorm -r plugins/docs-workflows/docs`, and read each hit.
- **Suggested fix:** On user pages, state the rule itself ("every command that writes an artefact passes an Opus review; `/docs-serve` writes none"). Drop the decision ids, the `§` numbers and the grep recipes, or move them to maintainer docs. Define "ceded" once on the Session cost page and link to it.
- **Source:** review
- **Confidence:** high

### DQW-B11 — MINOR — `/document` and `/release-notes` pages refer to "the tracker" and "the docs automation" as if every reader had them
- **Where:** `plugins/docs-workflows/docs/commands/document.md:25`; `plugins/docs-workflows/docs/commands/release-notes.md:3`, `:61`; `plugins/docs-workflows/docs/workflow.md:84`
- **What is wrong:** `document.md:25` says "`/document` never writes release-notes or what's-new pages, since those are generated from the tracker by the docs team's own automation". The same sentence opens "For release notes, use `/release-notes`". `release-notes.md:61` says the draft never carries "a `{{#internal-note}}` block, since the docs automation adds that metadata wrapper when it publishes". No page defines "the tracker", "the docs team's own automation" or the `{{#internal-note}}` syntax. These are leftovers from the environment the plugin was extracted from.
- **Failure scenario:** A user without such automation reads that release notes are "generated from the tracker" and cannot tell whether `/release-notes` is meant for them. They also do not learn that they must add identifiers or metadata themselves when they publish the draft.
- **Evidence:** I read the lines cited. `grep -rn "docs automation\|the tracker" plugins/docs-workflows/docs` finds no definition.
- **Suggested fix:** Say what the draft omits and that the publisher adds it ("the draft is the body only; add any identifiers or wrapper your publishing process needs"). Drop "generated from the tracker" from `document.md:25`, keeping vendor neutrality.
- **Source:** review
- **Confidence:** medium

### DQW-B13 — MINOR — Three docs-workflows command pages never link back to the Workflow overview
- **Where:** `plugins/docs-workflows/docs/commands/document.md`, `release-notes.md`, `docs-brand.md` (whole files)
- **What is wrong:** `docs-init.md`, `docs-audit.md`, `docs-profile.md` and `docs-serve.md` each link `../workflow.md`. These three do not, though `/document` and `/release-notes` are the spine of that diagram (`workflow.md:15-18`).
- **Failure scenario:** A user who lands on `/document` from a search or the README table has no path to the diagram that shows where `/release-notes` and the PRD inputs fit.
- **Evidence:** `grep -n "workflow.md" docs/commands/{document,release-notes,docs-brand}.md` returns nothing.
- **Suggested fix:** Add a "[Workflow overview](../workflow.md)" entry to each See also. On `docs-brand.md`, also add the route page, since branding is route step 1.
- **Source:** review
- **Confidence:** high

### DQW-B14 — MINOR — prose-style README is stale about which family uses it, and gives no install command
- **Where:** `plugins/prose-style/README.md:383`, `:398`, `:402-407`
- **What is wrong:** The section heading says "How it fits with the dev-workflows family", `:398` says "without going through the `dev-workflows` pipeline", and `:405` says "Install it through Claude Code's plugin system — it will be available alongside `dev-workflows`." Per `CLAUDE.md`, `dev-workflows` "does not use `prose-style` at all". The consumers are `docs-workflows` and `product-workflows`, which the section body itself names (`/document`, `/epics`, `/create-prd`, `/release-notes`). The Installation section has no `claude plugin install prose-style@shipwright` line, unlike the acli README (`plugins/acli/README.md:28-31`).
- **Failure scenario:** A user who only wants the standalone reviewers looks for the install command and finds none. A user of `dev-workflows` expects prose-style to come with it, but it does not: dev-workflows declares only `workflows-core`.
- **Evidence:** `plugins/dev-workflows/.claude-plugin/plugin.json` dependencies, and `CLAUDE.md` § Active plugins.
- **Suggested fix:** Retitle the section "How it fits with docs-workflows and product-workflows". Say that both install it as a dependency. Add the marketplace-add, install and update commands.
- **Source:** review
- **Confidence:** high

### DQW-B15 — MINOR — The acli README does not say how to use the skill or how to authenticate headless, though it says both are documented
- **Where:** `plugins/acli/README.md:8`, `:16-18`, `:26-31`
- **What is wrong:** `:8` says it "authenticates via `acli … auth login`", with an ellipsis where the command should be. `:16-18` says that "the token-on-stdin form is documented instead" but shows no command. The README never says that the plugin is a model-invoked skill with no slash command, so the way to use it is to ask in prose (for example "list my open work items in project X"). It shows no example and no update command.
- **Failure scenario:** A user installs the plugin, looks for a `/acli` command, and finds none. In a container they also do not know the headless auth form; the README's only hint, `--web`, is the form it says fails there. The working form (`acli jira auth login --site … --email … --token` with the token on stdin) appears only in `skills/acli/SKILL.md:328`.
- **Evidence:** I read the README in full and `SKILL.md:12-15`, `:317-329`.
- **Suggested fix:** Add a "Use" section ("no slash command; ask Claude in prose, and the `acli` skill loads"), a two-line headless auth example with the token on stdin, and the update command.
- **Source:** review
- **Confidence:** high

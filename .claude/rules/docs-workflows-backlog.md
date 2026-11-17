---
paths:
  - "plugins/docs-workflows/**"
  - "plugins/product-workflows/commands/epics.md"
  - "plugins/product-workflows/agents/epic-*.md"
  - "plugins/product-workflows/docs/commands/epics.md"
---

# docs-workflows — the docs backlog: `/docs-audit` and the backlog runs

Loaded with `.claude/rules/docs-workflows.md`, whose `paths:` it shares. Split out of `.claude/rules/docs-workflows.md` to keep that file under 20,000 characters; the plugin's other rules are there; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

## Workflow map

```
/docs-audit          → [resolve-docs-repo (signal-positive)] → resolve <top> + read the profile → [confirm/record source_repos[] where the key is absent — recorded only where a profile exists] → [require nothing on main: this command gates on no prior phase] → [code-scanner×N over the recorded repos (parallel, cap 4, default branch — the session's own repository on another branch read there by ref, `workflows-core:scan-refresh`'s fixed-policy case) + the caller's own $SPECS_PATH read for the `decision` and `release` kinds] → [§8.5 seeded round 2; a theme still unresolved is named, never flattened into a gap] → [docs-auditor: surfaces[] with volatility from git log density] → [ia-planner@Opus: cross each surface with the types it earns, rank on four signals, propose tutorial candidates] → [mint a picked tutorial candidate — --refresh only] → write .dev-workflows/docs-backlog.yml + reconcile existing pages by their `unit:` frontmatter key → [docs-audit-reviewer@Opus] → [triage: verify each finding; the orchestrator applies survivors — no fixer and no re-review (D25)] → impl-maintenance → commit-artifacts   (no branch and no commit in the docs repo: the backlog is left in the working tree for the operator to review and commit; resolves no docs grounding (`.claude/rules/docs-grounding.md`); its cost and feedback land under $SPECS_PATH/documentation/<docs-repo-slug>/, ahead of pending, because this run has no PRD and never will — D19; report-only if misrooted)
                      └── docs-auditor (docs-workflows)       (used by /docs-audit)
                      └── ia-planner (docs-workflows)         (used by /docs-audit)
                      └── docs-audit-reviewer (docs-workflows) (used by /docs-audit)
```

## Invariants

- **`plugins/docs-workflows/references/docs-audit/backlog-format.md` §1's line shape and `plugins/docs-workflows/scripts/backlog-lines.py` change in one commit.** The paragraph *The line shape a backlog run reads.* states the shape, and the script is its one implementer: every line-wise read or edit a backlog run makes of `.dev-workflows/docs-backlog.yml` goes through it. Its `--selftest` pins the script to the paragraph — it reads the paragraph's out-of-shape reasons and §1's schema from the reference itself and fails where either disagrees with the script — so a reason added to one and not the other turns the build red. `.github/workflows/validate-catalog.yml`'s *Self-test the backlog line reader* step runs it on every push.
- **`plugins/docs-workflows/references/docs-iteration/unit-brief.md` §1 holds, once, the list of the sections a backlog run's brief replaces in `doc-writer` and `doc-reviewer`.** Each agent carries one pointer paragraph, *A backlog run's brief.*, which sends a brief carrying `brief_kind: unit` as a top-level field of its own to that file and restates none of the list; a brief without that field — every `/document` dispatch — reads both agents as they stand. An edit to any section §1 names, or to either agent's inputs, steps or dimension table, re-reads it in the same change — `unit-brief.md` whole, not §1 alone, since four of its paragraphs say how a section §1 does not name reads under a unit brief: §2's *Phase numbers*, §3.1's last paragraph, §4.1's *The page is what is graded.* and §4.3's *A marked claim, in the dimensions that stand.* — so that a section renamed, renumbered, added or split either joins §1 or still reads true under a unit brief.

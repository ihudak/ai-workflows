---
paths:
  - "plugins/dev-workflows/**"
---

# dev-workflows — `/design` and `/ready` invariants

Loaded with `.claude/rules/dev-workflows.md`, whose `paths:` it shares. Split out of `.claude/rules/dev-workflows.md` to keep that file under 20,000 characters; the plugin's other rules are there and in `.claude/rules/dev-workflows-implement.md`, and the test-writing requirement for code changes is in `.claude/rules/dev-workflows-tests.md`; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

## Invariants

### /design and /ready

- `/design` Phase 5 offers a three-take `interface-designer` fan-out (one take per constraint — minimise the interface, maximise flexibility, optimise for the most common caller) on a contested interface — any `dev-workflows:design-format` `## Seams` signal; `--design-twice` forces the fan-out itself, skipping the offer, even with no signal fired (a user who typed the flag has already answered what the offer would ask); the offer's two options carry no `(Recommended)` marker, because the list is only shown once the interface is already contested; declining costs nothing — the interview continues and `design.md`'s unconditional `### Alternatives considered` requirement is satisfied by hand, as without the offer
- `/ready` is **read-only about status** — it **derives the workflow phase from the artifacts present** and verifies the ARD/spec/design justify it, comparing an operator's `--claimed` status against that derivation where one is given; there is no workflow phase recorded anywhere for it to read — `prd.md`'s own `status:` is the document's authoring state, never read as one (the status peek D8 retired had no source in `$SPECS_PATH` and `ready.md` forbids reconstructing it), and it never sets one and never reads a tracker, and never stops on an unmerged artifact (`workflows-core:phase-handoff` §3.3 rows D/E, a readiness finding capping the verdict at `PARTIAL`) or a missing one (row F, delegated per §3.4, recorded as a coverage gap); it commits the deliverable or the `_readiness.md` snapshot only through `phase-handoff.md` §4.3's consent choice via `handoff-to-main` (§2), never automatically (its terminal `commit-artifacts` step commits ONLY `$SPECS_PATH`'s bounded session-artifact paths, `workflows-core:specs-repo-git` §2.1)

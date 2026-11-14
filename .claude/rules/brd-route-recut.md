---
paths:
  - "plugins/product-workflows/**"
  - "plugins/dev-workflows/commands/design.md"
  - "plugins/dev-workflows/commands/ready.md"
  - "plugins/dev-workflows/commands/implement.md"
  - "plugins/dev-workflows/commands/conformance.md"
  - "plugins/workflows-core/references/addressing.md"
  - "plugins/workflows-core/references/cost-emission.md"
  - "plugins/workflows-core/commands/frames.md"
  - "plugins/docs-workflows/commands/document.md"
  - "plugins/docs-workflows/commands/release-notes.md"
  - "plugins/security-workflows/commands/scan.md"
---

# BRD route — the sibling re-cut

Loaded with `.claude/rules/brd-route.md`, whose `paths:` it shares. Split out of `.claude/rules/brd-route.md` to keep that file under 20,000 characters; the route's map lines and its folder-kind invariants are there; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

## Invariants

- **The sibling re-cut is the one place `/brd-split` re-allocates a row that already carries a fate by the owner's choice, and its precondition is the whole of it.** (Phase 4.5's removal repair also rewrites fated rows — a removed child's `covered-by` — but that is the key repair a removal forces, not a re-allocation.) On a fully-allocated **root** carrying an `<instruction>` — the one run on which that argument is otherwise free, which is why it takes no flag — a row whose parent ledger reads `covered-by: <A>` while A's **own** ledger reads `deferred-to: <A>` may be re-pointed onto a sibling under the same parent that has not been interviewed (no `decisions.md` holding a `[VD#n]`/`[CD#n]`, no `interview/round-*.md`), one already standing or one that same run carves. Both halves are read off the `disposition` column at both levels, never off `claims:` or an inventory. **What relaxes is only the weaker rule** that this command never re-allocates a settled row, and it relaxes against the owner's own written refusal and against nothing else. **What survives, and a reader needs to see that it survived: no row ever returns to `unallocated`** — every write here replaces one terminal disposition with another, so §4's allocation gate is never reopened — and the one-level nesting cap is untouched, because a re-cut carves a *sibling*, never a child. `product-workflows:coverage-ledger-format` §3.2 is the authority, and the rule is changed there. **Its readers are not a set a glob expresses, so no recipe stands here.** Sweep a §3.2 change from §3.2's own citations across `plugins/`, never from a command-name pattern — a recipe that returns a wrong answer is worse than no recipe, because the next reader trusts what it returns. ([why](../../docs/maintainers/rationale.md#brd-recut-readers))

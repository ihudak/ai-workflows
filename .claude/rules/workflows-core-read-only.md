---
paths:
  - "plugins/workflows-core/references/read-only-repos.md"
  - "plugins/workflows-core/references/escalation-rules.md"
  - "plugins/workflows-core/references/specs-repo-git.md"
  - "plugins/dev-workflows/references/code-handoff.md"
  - "plugins/workflows-core/agents/code-scanner.md"
  - "plugins/docs-workflows/agents/diff-summarizer.md"
  - "plugins/workflows-core/agents/docs-grounder.md"
  - "plugins/product-workflows/agents/code-grounder.md"
  - "plugins/product-workflows/agents/grounding-verifier.md"
  - "plugins/docs-workflows/agents/docs-auditor.md"
  - "plugins/dev-workflows/commands/implement.md"
  - "plugins/dev-workflows/commands/design.md"
  - "plugins/product-workflows/commands/idea.md"
  - "plugins/product-workflows/commands/create-ard.md"
  - "plugins/product-workflows/commands/specify.md"
  - "plugins/product-workflows/commands/epics.md"
  - "plugins/product-workflows/commands/prd-ground.md"
  - "plugins/docs-workflows/commands/document.md"
  - "plugins/docs-workflows/commands/release-notes.md"
  - "plugins/docs-workflows/commands/docs-audit.md"
  - "plugins/docs-workflows/commands/docs-profile.md"
  - "plugins/docs-workflows/commands/docs-brand.md"
  - "plugins/docs-workflows/commands/docs-init.md"
---

# workflows-core — the read-only-repos authority

Loaded when `workflows-core:read-only-repos` is read, or an agent, command or reference the paragraph below names: the agents that emit or consume `prep`, the commands that dispatch `code-scanner` or `diff-summarizer` and the others it names, and `workflows-core:escalation-rules`, `workflows-core:specs-repo-git` and `dev-workflows:code-handoff`, whose ladders it sets beside its own. A file that starts consuming it needs adding to these `paths:`. Split out of `.claude/rules/workflows-core-git.md` to keep that file under 20,000 characters; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

## Authority

`plugins/workflows-core/references/read-only-repos.md` is the **single source of truth** for read-only repository mounts — the detection probe (`test -w` on the repo and `.git`, plus the `Read-only file system` error as a secondary trigger), what read-only mode skips (`fetch`/`pull`/`switch`/`remote set-head`, and the dirty-tree gate), write-free ref resolution and reading (`ls-tree`, `git grep <ref>`, `git show <ref>:<path>`), the default branch its scanner and docs-repository callers switch onto or cut a branch from (§3's **A switch takes the name**: the branch's name, `main`, never the `origin/main` ref the resolution yields, which `git switch` refuses — a caller that only reads may take the ref; `dev-workflows:code-handoff` §2.8 and `specs-repo-git.md` §3.2 keep their own ladders), the 14-day staleness / ahead-of-ref escalation trigger, and the `prep` output contract (`read_only`, `scanned_ref`, `ref_committed_at`, `head_divergence`). Consumed by `code-scanner` and `diff-summarizer`, which emit the `prep` block; `docs-grounder`, `code-grounder`, `grounding-verifier` and `docs-auditor` (which reads each repository at the `prep.scanned_ref` `code-scanner` returned) also consume it but return a digest or a finding rather than a `prep` block (`docs-grounder` reads §1–§4 only — read-only detection, what to skip, ref resolution, reading at the ref). The nine commands that dispatch the `prep`-emitting agents act on the returned `prep.read_only` via `workflows-core:escalation-rules`; `/prd-ground` cites `read-only-repos.md` directly for the read-only posture its Phase 1 holds toward every repository it resolves, and `/document`, `/docs-profile`, `/docs-brand` and `/docs-init` cite §3 for the default branch each resolves before cutting a branch in a docs repository. Nothing in it restricts a writable mount: `git switch` and `git pull --ff-only` remain sanctioned prep on a writable clone.

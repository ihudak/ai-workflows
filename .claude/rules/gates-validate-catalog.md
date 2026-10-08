---
paths:
  - "scripts/**"
  - ".github/**"
---

# Gates — `scripts/validate-catalog.py`

Loaded with `.claude/rules/gates.md`, whose `paths:` it shares and whose opening rule binds every gate. Split out of `.claude/rules/gates.md` to keep that file under 20,000 characters; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

## `scripts/validate-catalog.py`

Besides the catalog, it gates the instruction tiers. **Sizes**, as Python `len` of the decoded file, at `CLAUDE.md` § Running the gates' thresholds; a rules file past its warning is split with narrower `paths:` globs, or its evidence moved to the rationale. **Paths**: every rules file must carry frontmatter with a top-level `paths:` block list (without one it loads every session), and every glob must match at least one *file* outside `.git`, worktrees, fixtures, `node_modules`, `.superpowers` and `.claude/rules/`. Globs are matched by pathlib, which has no brace expansion, so a `{a,b}` glob is reported dead: write each alternative as its own entry. **Descriptions**: a command, agent or skill `description` fails above 1,024 characters and warns above 600. ([why](../../docs/maintainers/rationale.md#entry-descriptions)) **Typed-only commands** (`CLAUDE.md` § Command, agent, and skill taxonomy): it sees a call only as the Skill tool named before `skill: "<plugin>:<name>"`, or `Skill(skill: …)`, outside a fence; a run's call must say so.

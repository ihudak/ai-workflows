---
paths:
  - "scripts/**"
  - ".github/**"
---

# Gates — `check-docs.sh`'s checks 22 and 23

Loaded with `.claude/rules/gates.md`, whose `paths:` it shares and whose opening rule binds every gate. Split out of `.claude/rules/gates.md` to keep that file under 20,000 characters; the rest of `scripts/check-docs.sh`, its one body across three editions included, is there; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

### Check 22

**Check 22 holds a vendored copy to its original**: each `<original>:<copy>` pair `VENDORED_COPIES` names must be byte-identical, an absent copy is skipped, and an empty list — this edition's — makes it a no-op. The internal Claude edition lists the two scripts one of its plugins ships as copies of another's.

### Check 23

**Check 23 holds a path question to its rule**: every paragraph of a command under `PLUGIN_RELS` offering *Set <NAME>_PATH (you'll be prompted …)* — a run of non-blank lines, a fenced `choices:` block inside it included — names the rule `PATH_UNSET_RULE` names, *Required path environment variable unset* here, whitespace collapsed; none at all fails as vacuous. The unit is the paragraph, not the file, because `/design`, `/create-ard` and `/specify` cited the rule for `REPOS_PATH` while carrying a typed `SPECS_PATH` locally, which a file-level test passes. Measured at batch B20: on the tree before its fixes it fired on exactly the seven sites the batch fixed, and on none after. **What it cannot see:** whether a cited paragraph's own prose then contradicts the rule, nor a path asked for in prose with no such option. A numbered list with no blank line between its steps is one paragraph to it, so the rule named in one step passes a sibling step's option — a false pass; and prose separated from its fenced `choices:` block by a blank line fails though it cites the rule — a conservative false fail, fixed by closing the gap.

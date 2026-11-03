---
paths:
  - "scripts/**"
  - ".github/**"
---

# Gates — `check-docs.sh`'s checks 22 to 24

Loaded with `.claude/rules/gates.md`, whose `paths:` it shares and whose opening rule binds every gate. Split out of `.claude/rules/gates.md` to keep that file under 20,000 characters; the rest of `scripts/check-docs.sh`, its one body across three editions included, is there; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

### Check 22

**Check 22 holds a vendored copy to its original**: each `<original>:<copy>` pair `VENDORED_COPIES` names must be byte-identical, an absent copy is skipped, and an empty list — this edition's — makes it a no-op. The internal Claude edition lists the two scripts one of its plugins ships as copies of another's.

### Check 23

**Check 23 holds a path question to its rule**: every paragraph of a command under `PLUGIN_RELS` offering *Set <NAME>_PATH (you'll be prompted …)* — a run of non-blank lines, a fenced `choices:` block inside it included — names the rule `PATH_UNSET_RULE` names, *Required path environment variable unset* here, whitespace collapsed; none at all fails as vacuous. The unit is the paragraph, not the file, because `/design`, `/create-ard` and `/specify` cited the rule for `REPOS_PATH` while carrying a typed `SPECS_PATH` locally, which a file-level test passes. Measured at batch B20: on the tree before its fixes it fired on exactly the seven sites the batch fixed, and on none after. **What it cannot see:** whether a cited paragraph's own prose then contradicts the rule, nor a path asked for in prose with no such option. A numbered list with no blank line between its steps is one paragraph to it, so the rule named in one step passes a sibling step's option — a false pass; and prose separated from its fenced `choices:` block by a blank line fails though it cites the rule — a conservative false fail, fixed by closing the gap.

### Check 24

**Check 24 holds a keyed preload hook to the key grammar, by running it**: each `<hook>:<command>` pair `KEYED_HOOKS` names is piped a JSON payload for the command followed by each of `A-1`, `ACME_X-90`, `ACME-1-2-3` and two whole folder names, and must print `KEYED_HOOK_MARKER`, the specs-context line; on a free-text argument it must not. Behavioural rather than a regex compare, because a hook may test more loosely than `workflows-core:addressing` §1 (the command validates the address) and never more narrowly — batch B28 found both hooks rejecting `A-1`, `ACME_X-90` and a typed folder name. An absent hook is skipped with a note, an empty list switches it off, and without `python3`, which the hooks read the prompt with, it does not run. **What it cannot see:** a hook `KEYED_HOOKS` does not name, and a key shape outside its fixed tokens.

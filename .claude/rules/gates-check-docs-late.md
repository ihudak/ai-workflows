---
paths:
  - "scripts/**"
  - ".github/**"
---

# Gates — `check-docs.sh`'s checks 22 to 25

Loaded with `.claude/rules/gates.md`, whose `paths:` it shares and whose opening rule binds every gate. Split out of `.claude/rules/gates.md` to keep that file under 20,000 characters; the rest of `scripts/check-docs.sh`, its one body across three editions included, is there; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

### Check 22

**Check 22 holds a vendored copy to its original**: each `<original>:<copy>` pair `VENDORED_COPIES` names must be byte-identical, an absent copy is skipped, and an empty list — this edition's — makes it a no-op. The internal Claude edition lists the two scripts one of its plugins ships as copies of another's.

### Check 23

**Check 23 holds a path question to its rule**: every paragraph of a command under `PLUGIN_RELS` offering *Set <NAME>_PATH (you'll be prompted …)* — a run of non-blank lines, a fenced `choices:` block inside it included — names the rule `PATH_UNSET_RULE` names, *Required path environment variable unset* here, whitespace collapsed; none at all fails as vacuous. The unit is the paragraph, not the file, because `/design`, `/create-ard` and `/specify` cited the rule for `REPOS_PATH` while carrying a typed `SPECS_PATH` locally, which a file-level test passes. Measured at batch B20: on the tree before its fixes it fired on exactly the seven sites the batch fixed, and on none after. **What it cannot see:** whether a cited paragraph's own prose then contradicts the rule, nor a path asked for in prose with no such option. A numbered list with no blank line between its steps is one paragraph to it, so the rule named in one step passes a sibling step's option — a false pass; and prose separated from its fenced `choices:` block by a blank line fails though it cites the rule — a conservative false fail, fixed by closing the gap.

### Check 24

**Check 24 holds a keyed preload hook to the key grammar, by running it**: each `<hook>:<command>` pair `KEYED_HOOKS` names is piped a JSON payload for the command followed by each of `A-1`, `ACME_X-90`, `ACME-1-2-3` and two whole folder names — each also behind `--skip-costs` and behind `--enforce-model opus`, a run flag's one-token and two-token forms — and must print `KEYED_HOOK_MARKER`, the specs-context line; on a free-text argument, behind either or neither, it must not. Behavioural rather than a regex compare, because a hook may test more loosely than `workflows-core:addressing` §1 (the command validates the address) and never more narrowly — batch B28 found both hooks rejecting `A-1`, `ACME_X-90` and a typed folder name, and D41 every preload hook injecting nothing behind a leading run flag, which the command strips there. An absent hook is skipped with a note, an empty list switches it off, and without `python3`, which the hooks read the prompt with, it does not run. **What it cannot see:** a hook or command `KEYED_HOOKS` does not name — `product-workflows`' `/epics` hook, which tests no key, and the other commands of the two hooks it names, `/vuln`, `/dev-workflows:upgrade` and `/docs-workflows:release-notes`, whose leading-flag skip it never runs, among them — a key shape outside its fixed tokens, and a leading flag other than its two leads, a command's own flag taking a value of its own among them.

### Check 25

**Check 25 holds a user page to the reader's language**: no page under a `PLUGIN_RELS` plugin's `docs/`, no such plugin's `README.md` and not the repo-root `README.md` cites a section by `§`, names a design-decision id (`D` and one to three digits standing as a word), or cites a reference as `<plugin>:<name>` where `<name>` resolves to a file under that plugin's `references/` — any plugin of the tree, by directory or declared name, the subtree kept (`model-routing/classification`). Resolved, never parsed by shape, so an agent, a skill or a command of the same form passes, and so does a name that is only a reference subtree. An HTML comment is not read: a recipe that re-derives a number on the page goes there. `internal-ref-ok:` sanctions its line, and on a fence-opening line the block it opens, for a customer's own `§ 4.2` or a run's verbatim output; a fenced block is otherwise read like prose. `USER_PAGE_VOCAB=0` switches it off, the internal editions' setting until their pages are rewritten. Measured at batch B30: 488 lines on 71 pages before its rewrite, none after. **What it cannot see:** the path form `references/<name>.md`, which also names files a user acts on; change history; a maintainer recipe outside a comment; and a citation reworded to name no section, id or reference.

---
paths:
  - "scripts/**"
  - ".github/**"
---

# Gates — the branch-check gate

Loaded with `.claude/rules/gates.md`, whose `paths:` it shares and whose opening rule binds every gate. It describes a subcommand of `scripts/reference-parts.py`, split out of `.claude/rules/gates-reference-parts.md` to keep that file under 20,000 characters.

**`check-branch-check`** gates `workflows-core:phase-handoff` §6's `branch-check`. Every command in `workflows-core`'s or a dependent plugin's `commands/` whose text names `resolve-address` — the set `CLAUDE.md`'s addressing constraint re-derives with `grep -l resolve-address plugins/*/commands/*.md` — must request `args: "phase-handoff branch-check"` in a paragraph or list item outside every fenced block. Every one of them that presents §4.3's consent choice — the array quoted, read by its first option, or a line naming both `phase-handoff` and `§4.3`, as `check-questions` reads it — must pass `prefix:` in the paragraph of one such request, save the commands the script's `EXEMPT_PREFIX` names with a reason each: `/implement`, whose Phase 4.5 handoff is conditional and onto prefixes it does not own, and `/update-spec`, whose own Phase 0 already stops on a branch that changed `specification.md`. A command that names `handoff-to-main` without presenting the choice is not read as a producer: `/document` names it in a host footer and hands nothing off in the specs repository. It prints the census `branch-check: N command(s) resolve a folder, M run branch-check, P producer(s) pass a prefix`, `--verbose` lists each command's disposition, and it fails closed: a scan that finds no command naming `resolve-address` fails.

**What it cannot see:** where a command's request stands — after its preflight and its resolution, before anything reads the resolved folder — nor whether the prefix it passes is the one its handoff names; a command that names `resolve-address` only to say it resolves nothing is held to the request anyway; and it reads a producer by its consent choice alone, so a command that hands off without presenting §4.3's choice goes unseen. Review holds those.

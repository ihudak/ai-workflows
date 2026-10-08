---
paths:
  - "scripts/**"
  - ".github/**"
---

# Gates — the ID-grammar gate

Loaded with `.claude/rules/gates.md`, whose `paths:` it shares and whose opening rule binds every gate. Split out of `.claude/rules/gates.md` to keep that file under 20,000 characters; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

## ID-grammar gate (`scripts/check-id-grammar.sh`)

It runs on every push via `.github/workflows/validate-catalog.yml` — preceded there by `--selftest`, which asserts, per fixture, the exit code **and every ID form the gate must have named** — one grep per alternation of `PATTERN`. The exit code alone is not enough: each negative fixture carries several violating lines, so any surviving alternation holds the exit at 1. `scripts/validate-catalog.py`'s own `--selftest` does the same, ahead of its run. ([why](../../docs/maintainers/rationale.md#id-grammar))

Of the `id-grammar-ok` markers, one accepts the legacy form as a tolerant reader — `workflows-core:ard-resolution`; the others are the reviewers that check identifier integrity and must quote the form they reject. Re-derive the census with `grep -rn 'id-grammar-ok' plugins/ --include=*.md | grep -v CHANGELOG` — scoped to `plugins/`, not to one plugin, since the split put `workflows-core:ard-resolution`'s marker outside `dev-workflows` rather than adjusting it. The spec/design numbered-ID namespace is deliberately outside this grammar and unchanged; `scripts/spec-id-baseline.txt` is its census tripwire.

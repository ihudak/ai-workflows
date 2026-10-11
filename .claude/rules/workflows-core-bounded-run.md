---
paths:
  - "plugins/*/scripts/bounded.py"
  - "plugins/*/commands/*.md"
  - "plugins/*/agents/*.md"
  - "plugins/*/references/**"
  - ".github/workflows/validate-catalog.yml"
---

# workflows-core — the bounded-run authority

Loaded when any plugin's copy of `scripts/bounded.py`, any command, agent or reference file, or `.github/workflows/validate-catalog.yml` is read: a capped call can be written in any of those files, and CI holds the copies equal. Split out of `.claude/rules/workflows-core.md` to keep that file under 20,000 characters; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

## Authority

`plugins/workflows-core/references/bounded-run.md` is the **single source of truth** for capping a call's run time — `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bounded.py" <seconds> <command…>`, a script called by its path, so a run that never read the reference runs it all the same; exit 124 is a timeout. `workflows-core`, `dev-workflows`, `docs-workflows` and `product-workflows` each ship the same `scripts/bounded.py`, since `${CLAUDE_PLUGIN_ROOT}` is the calling file's own plugin; CI fails a copy that differs from `workflows-core`'s. A command, agent or reference never writes a bare `timeout <N>s …`: macOS ships no `timeout` binary, and a call that fails there with `command not found` reads as "skip".

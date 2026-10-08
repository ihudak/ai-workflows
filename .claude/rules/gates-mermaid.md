---
paths:
  - "scripts/**"
  - ".github/**"
---

# Gates — the mermaid gate

Loaded with `.claude/rules/gates.md`, whose `paths:` it shares and whose opening rule binds every gate. Split out of `.claude/rules/gates.md` to keep that file under 20,000 characters; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

## Mermaid gate (`scripts/mermaid/check-mermaid.mjs`)

The gate finds diagrams with a real CommonMark lexer (`marked`) and parses each with mermaid's own parser, both pinned by exact version and a committed lockfile, over tracked files only — which is what GitHub renders, and which leaves out every worktree copy under the ignored `.worktrees/` — and excluding its own fixture tree, `scripts/fixtures/mermaid/`, whose green cases are skipped as well as the red ones broken on purpose. Do not replace the lexer with a regex: the selftest runs it over a fixture for each of the four constructs a hand-rolled fence scanner got wrong, so an extractor that misses them again fails it. It never runs the old scanner. ([why](../../docs/maintainers/rationale.md#mermaid-gate))

A failure names the **source-file line**, found by content — the context mermaid prints around a failure, located in the diagram — never by replaying mermaid's own rewrites of the text. Where that context matches no single place, the gate names the fence line and says why; it never guesses. An unclosed fence is not rejected for being unclosed — CommonMark runs it to the end of its container and GitHub draws what it holds — so only its content is judged.

It runs on every push after its `--selftest`, every fixture case of which asserts the block count as well as the exit code, and each red case what the gate reported. Two cases are red/green pairs, named in the script's selftest comment; every other green case pins a construct the lexer must find or leave alone.

**What it cannot see:** it parses and does not render, so a diagram that parses and then fails at layout passes — a render needs a browser CI does not carry — and a mermaid fence inside a raw HTML block is outside it, as it is outside any CommonMark lexer. Run it locally as `.github/workflows/validate-catalog.yml` does.

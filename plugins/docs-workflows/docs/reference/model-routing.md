# Model routing

Six of this plugin's seven commands classify their own task before doing real work, and the class, with the kind of step being dispatched, decides which model each subagent runs on. [`/docs-serve`](../commands/docs-serve.md) classifies nothing: it starts a process and reports a URL. The policy is the companion `workflows-core` plugin's model-routing classification reference, listed on its References page; this page says what these commands do with it.

## How each command classifies

| Command | Class | What runs on Opus |
|---|---|---|
| [`/document`](../commands/document.md), keyed | Typically `SIGNIFICANT` | `doc-planner` and `doc-writer`, pinned to the Opus chain by the dispatch; `doc-reviewer`, by its own frontmatter |
| `/document`, direct | `SIMPLE` or `MODERATE`, never higher | Nothing |
| [`/release-notes`](../commands/release-notes.md) | Always `MODERATE` | Nothing: no Opus planner and no Opus review |
| [`/docs-profile`](../commands/docs-profile.md) | `SIGNIFICANT` | The synthesis of the draft profile, pinned by the dispatch |
| [`/docs-init`](../commands/docs-init.md) | `MODERATE` | `docs-scaffold-reviewer`, by its frontmatter |
| [`/docs-brand`](../commands/docs-brand.md) | `MODERATE` | `docs-scaffold-reviewer`, on the standalone path only |
| [`/docs-audit`](../commands/docs-audit.md) | `SIGNIFICANT` | `ia-planner` and `docs-audit-reviewer`, by their frontmatter |

Every other step these commands dispatch — reading, summarising, locating, scanning, style-checking, fixing and session maintenance: `diff-summarizer`, `doc-location-finder`, `docs-style-checker`, `doc-fixer`, `release-notes-writer`, `code-scanner`, `docs-auditor`, `impl-maintenance` and, under `--skip-feedback`, `defect-reporter`, `/docs-profile`'s detection scan and direct mode's exploration — runs on the Sonnet chain, even on an Opus session, so mechanical work never burns Opus.

**The review gate of `/docs-init`, `/docs-brand` and `/docs-audit` is Opus whatever the class.** A `MODERATE` class lowers which model plans and executes, never which model reviews. **Direct-mode `/document` never reaches for Opus:** where the task reads as `SIGNIFICANT` or `HIGH-RISK` — several repositories, new feature pages from a PRD folder, or a change big enough to need a reviewer — it stops and offers keyed mode, `/product-workflows:epics`, or going on in direct mode anyway.

## Agents pinned by frontmatter

Four of this plugin's agents carry `model: opus` in their frontmatter — `doc-reviewer`, `docs-audit-reviewer`, `docs-scaffold-reviewer` and `ia-planner` — and one carries `model: sonnet`, `docs-auditor`, which keeps mechanical enumeration off the expensive tier. The other six carry no pin and take the model the dispatching command passes: `diff-summarizer`, `doc-location-finder`, `doc-planner`, `doc-writer`, `docs-style-checker` and `release-notes-writer`. [Agents](agents.md) says which command dispatches each.

## On a session below Opus

No command here stops for a session below Opus. Every Opus step is a dispatched subagent, so it runs on Opus wherever Opus is reachable, whatever model the session itself runs; what stays on the session's model is the orchestration — the classification, the questions, and keyed `/document`'s own interactive gates. Keyed `/document` is the one command that says anything about it: on a session off the Opus chain, with Opus reachable, it offers a relaunch under Opus only on a large multi-repo ticket, where the orchestrator's context window is the risk — relaunch (recommended), proceed, or cancel — and otherwise goes on without asking. Its report records the session model, and whether you proceeded past the offer.

Where no Opus model is reachable at all, every Opus step falls to the Sonnet floor, and the run records the degradation in its routing block and its report, then proceeds.

## The fallback chains

- **Opus steps** take the first model available of `claude-opus-5-5`, `claude-opus-5`, `claude-opus-4-8`, `claude-opus-4-7` and `claude-opus-4-6`, then fall back through `claude-sonnet-5-5`, `claude-sonnet-5`, `claude-sonnet-4-6` and `claude-sonnet-4-5`, the report saying that no Opus was available.
- **Sonnet steps** take the first of `claude-sonnet-5-5`, `claude-sonnet-5`, `claude-sonnet-4-6` and `claude-sonnet-4-5`; with no Sonnet available, the session model, announced.

Where the agent tool selects models by family name only, as Claude Code's does today, a chain lands on the first row of an available family and the harness picks that family's version.

## Enforcing one model (`--enforce-model`)

`--enforce-model=<model>` (or `WORKFLOWS_ENFORCE_MODEL`) pins every subagent a run dispatches to one model, bypassing both chains. It overrides frontmatter pins — the four Opus-pinned agents and `docs-auditor` included — and reaches nested dispatches, such as the `prose-style-checker` that `docs-style-checker` runs. Classification still runs and still decides which steps happen. The orchestrator stays on the session model, since nothing inside a running command can switch it; where the two differ, the run prints one relaunch advisory. Under the flag, keyed `/document`'s relaunch offer does not fire, and direct mode's never-Opus rule gives way where the enforced model is Opus. A `/docs-profile` or `/docs-brand` run `--inline` takes its caller's flags rather than reading its own, and `/docs-serve` reports the flag ignored. The report then carries `Model routing: bypassed — enforced <id> (flag|env)`.

The full policy — the classification triggers, the routing block a command records, and the enforced-model rules — is authoritative in the classification reference; this page summarises it.

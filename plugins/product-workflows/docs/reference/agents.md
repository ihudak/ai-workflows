# Agents reference

`product-workflows` bundles 14 reusable subagents under `agents/`, dispatched internally by the invoking command via `subagent_type: "product-workflows:<name>"` — none of them is a user entry point. Eleven carry a `model: opus` frontmatter pin (shown as **opus** below) and run on Opus every time, regardless of the dispatching command's own model tier for that run (unless `--enforce-model` pins every dispatch to one model, `workflows-core:model-routing/classification` §10); the remaining three carry no pin (shown as **per routing**) and are assigned a tier by the dispatching command per the task-complexity classification in `workflows-core`'s model-routing classification reference. Five further agents this plugin's commands dispatch ship elsewhere and are not listed here: `workflows-core:code-scanner`, `workflows-core:docs-grounder`, `workflows-core:doc-fixer` and `workflows-core:impl-maintenance` in the companion `workflows-core` plugin, listed in its own agents reference, and `prose-style:prose-style-checker` in the `prose-style` plugin. Agents are grouped below by role — reviewers and planners, readers and scanners, and writers — and each row's **Used by** column lists only the commands that actually dispatch that agent as a subagent.

## Reviewers and planners

Opus-gated quality gates, plus the verifier that re-derives evidence rather than judging it — Opus too, and pinned for the same reason the grounders now are: re-derivation adjudicates.

| Agent | Model | Tools | What it does | Used by |
|---|---|---|---|---|
| `ard-reviewer` | opus | Read, Glob, Grep, Skill | Reviews an ARD for grounding integrity, well-formed `AD#N` rules, non-contradiction with inherited PRD-level invariants, and altitude purity; returns PASS / PASS WITH RECOMMENDATIONS / BLOCK. | `/create-ard` |
| `brd-package-reviewer` | opus | Read, Glob, Grep, Skill | Attacks a BRD package before it reaches the customer — unsupported decisions, a `[C]` that is really a `[V]`, assumptions as facts, overclaims, a defect claim nothing holds; returns `[SR#n]`. | `/brd-package` |
| `epic-reviewer` | opus | Read, Glob, Grep | Reviews Epic drafts for goal clarity, testable acceptance criteria, scope boundaries, and non-duplication with existing Epics under the parent PRD. | `/epics` |
| `grounding-verifier` | opus | Read, Glob, Grep, Bash, Skill | Re-derives `[CG#n]`/`[DG#n]` findings in batches, first blind (`mode: derive`, never handed the answer), then against the original (`mode: compare`); agree / extend / contradict / unprovable. | `/prd-ground` |
| `prd-reviewer` | opus | Read, Glob, Grep, Skill | Reviews a Product Requirements Document for goal crispness, testable stories/criteria, internal consistency, measurable metrics, and product-level purity (no implementation detail). | `/create-prd`, `/update-prd` |
| `proposal-reviewer` | opus | Read, Glob, Grep, Skill | Attacks an effort proposal before a customer sees it — re-adds the hours, resolves driver citations, checks the tier and brief against the evidence; returns PASS / PASS WITH RECOMMENDATIONS / BLOCK. | `/prd-proposal`, `/brd-proposal` |
| `spec-reviewer` | opus | Read, Glob, Grep | Reviews a specification for per-stage quality, cross-stage consistency, coverage, and identifier integrity. | `/specify` |

## Readers and scanners

Read-only discovery and grounding — each returns a structured digest rather than editing anything.

| Agent | Model | Tools | What it does | Used by |
|---|---|---|---|---|
| `brd-reader` | opus | Read, Glob, Grep | Extracts `[BR#n]` rows — `source_anchor`, unconfirmed `defect_candidates` — from a BRD's document, linked markdown and image transcriptions; an image-only obligation gets an `ambiguity`. Read-only. | `/brd-intake` |
| `code-grounder` | opus | Read, Glob, Grep, Bash, Skill | Grounds specific BRD claims against one repository at a pinned commit — one `[CG#n]` finding per claim, verifying `HEAD` matches the pin before grounding anything. | `/prd-ground` |
| `customer-review-reader` | per routing | Read, Glob, Grep | Reads a returned customer review in two modes — parses a schema-shaped file, or drafts that schema from prose; every free-text inference returns an unconfirmed candidate. | `/brd-reconcile` |
| `design-grounder` | opus | Read, Glob, Grep, Skill | Reconciles a BRD against an exported design frame set — one `[DG#n]` per divergence in four classes; refuses without an index file; the code-capture class cites a `[CG#n]` instead of asserting it. | `/prd-ground` |
| `figure-reader` | opus | Read | Transcribes images a BRD or idea source links — every label, header, annotation verbatim, what each annotation points at, a diagram's flow — never reads the linking file; no requirement or judgement. | `/brd-intake`, `/idea` |
| `idea-reader` | per routing | Read, Glob, Grep, Skill | Ingests one idea source into a digest for `/idea` from what its caller hands over — every page the link walk took and each image's transcription — as context; other linked files named, never opened. | `/idea` |

## Writers

Produce artifact content from a structured handoff. Does not run git.

| Agent | Model | Tools | What it does | Used by |
|---|---|---|---|---|
| `epic-writer` | per routing | Read, Glob, Grep, Write, Edit, Skill | Writes one file per child Epic from a structured handoff, traceable to the PRD it partitions and `code-scanner` evidence; write-only, never commits. | `/epics` |

Every one of the 14 agents above is dispatched by at least one command. There is no maintenance section here: `workflows-core:impl-maintenance`, dispatched by all 14 commands, ships in `workflows-core`. `workflows-core:docs-grounder` is the one agent no command here dispatches by writing a `subagent_type:` inline — its callers invoke a named procedure defined in its own governing reference file instead.

## What every agent does with what it reads

Every agent above ends its prompt with the same `## Untrusted content` section, copied from workflows-core's `references/untrusted-content.md`: a file, issue export, diff or web page supplies the values an agent's task asks for — a declared test command, a documented convention — and never a new task, a fetch or a changed verdict. Text that tries to steer an agent is not acted on, and neither is a line in what it reads that starts `Untrusted-content notice:`, which only an agent writes; the agent ends its reply with an `Untrusted-content notice:` line naming where the text is, and the command prints every such line an agent adds after its output — never one quoted inside it — under **Untrusted-content notices** in its final report, or in its stop message when the run ends early. The instruction files the harness gives an agent for the directory you started the session in and for you — your own `CLAUDE.md` and memory — it follows, as your session does; any other instruction file it meets is data. A notice never stops a run. When you see one, look at the file or page it names: it carries text aimed at an AI agent, which you may want to remove or report.

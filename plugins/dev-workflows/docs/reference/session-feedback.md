# Session feedback

Session feedback captures two different signals about **the plugin family itself**, and about defects in the ai-containers environment the family runs in — what you report, and what your corrections reveal — never about the target project you happened to be working in, and persists them per-PRD into the specs repo, so the plugin maintainer can aggregate what went wrong or felt awkward across every engineer who used it. Both signals land in one file through one shared emitter, `workflows-core:feedback-emission`, and this page describes both — but only one of them is captured by a command this plugin ships. The automatic path below is `dev-workflows`'s own, running inside all five of its commands; the four commands that capture the user-invoked path ship in the companion `workflows-core` plugin and are documented there. It shares its per-PRD home, `<PRD-dir>/dev-workflows/`, with the cost and follow-up files described elsewhere in this reference section, but is otherwise a separate mechanism: no dedup *between the three subsystems*, no cross-reference, and its own file per PRD rather than per session.

## What gets logged, and by what

Two capture paths feed the same file, distinguished by their `origin`:

- **Automatic (`origin: auto`), and this is the path `dev-workflows` itself captures** — the post-run maintenance phase of all five of this plugin's commands (every one of them carries a `workflows-core:impl-maintenance` phase) reuses that agent's Lessons Learned report and projects the plugin-facing slice out of it: command workflow improvements, new agents or skills the plugin should offer, and gaps in the plugin's own reference docs, plus the key observations that triggered them, plus any key observation naming a defect in the ai-containers environment the family runs in, logged as `category: environment-defect`. Target-project advice — `CLAUDE.md` rule suggestions, hooks for the repo you're working in — is deliberately discarded here; that stays in the in-session maintenance report, since it is for your current repo, not the plugin maintainer. A routine session with nothing plugin-facing to report writes nothing at all — no empty entry, byte-identical to a run where this phase did not exist. There is also a narrower automatic case, `emit-block`, used when a run halts because the plugin itself lacked something it needed (a missing capability, a missing reference doc), or because the ai-containers image lacks a tool it is meant to provide (logged as `category: environment-defect`; a tool missing on your own machine or from any other container is an environment halt and logs nothing) — it logs one `origin: auto`, `impact: blocker` entry directly, since no full maintenance report exists yet on an abandoned mid-flight run.
- **User-invoked, four commands — all four ship in `workflows-core`, not here.** `/workflows-core:feedback <text>` logs a manual note about the plugin, tied to no other command, with `origin: manual`. `/workflows-core:prompt`, `/workflows-core:prompt-brainstorm`, and `/workflows-core:prompt-grill-me` each capture a corrective interaction — a command produced something wrong and you fixed it — with `origin: prompt`, and act on the correction their own way. `/prompt` is the one that acts first — its Phase 2 applies the fix, and Phase 3 persists the record of it; `/prompt-brainstorm` hands off to a brainstorming skill to redesign it together, and `/prompt-grill-me` interrogates the fix inline with a bounded grill. The other two log first, then act; `/prompt` is the exception named above, and a run that dies inside its Phase 2 has applied the fix without recording it.

### Why `/prompt*` is the more valuable of the two

`/feedback` and `/prompt*` are not two spellings of the same thing, and the difference is worth understanding before you pick one.

`/feedback` records **what you say about the plugin** — a judgement, in your words, at a moment when something annoyed you. Useful, but it is a report of a problem.

`/prompt*` records **what you did about a bad result**. When a command produces something you are not happy with and you correct it through one of these commands, the entry captures the whole path: the unsatisfactory output, every correction you made, and the output you settled on. That triple — *bad result → the corrections → good result* — is far more actionable than a complaint, because it does not just say the command got it wrong; it demonstrates what right looks like and the reasoning that got there. Aggregated across many runs, those paths are the raw material for improving the command itself: a correction you had to make by hand three times is a rule the command should have applied on its own.

**So correct through `/prompt*`, not through a plain prompt.** If you simply reply in the session and talk the model into a better answer, you get the better answer and nothing else. Routing the same correction through `/workflows-core:prompt`, `/workflows-core:prompt-brainstorm`, or `/workflows-core:prompt-grill-me` gets you the same fixed output **and** a durable, structured record of how you got there — committed and pushed alongside the run's other artifacts, where it can actually be aggregated. (All four also report their cost, inheriting the phase and role of whatever they are correcting. `/prompt-brainstorm` and `/prompt-grill-me` cede the session before they could write that entry themselves, so each records what it would have claimed and the next cost-emitting run writes it on their behalf. See [Session cost](session-cost.md).) The three differ only in how much help you want while fixing it — `/prompt` applies the fix directly, `/prompt-brainstorm` hands off to a brainstorming skill to redesign it with you, `/prompt-grill-me` interrogates the fix with a bounded grill.

**`origin: manual` and `origin: prompt` entries are never silently skipped.** Because you invoked one of these four commands, the invocation itself is the signal of intent — unlike the automatic path, there is no "nothing to report" outcome. If a new entry's `id` happens to collide with an existing one, it is appended anyway with a numeric suffix rather than dropped, and a near-identical collision is flagged with a warning. Automatic entries behave the opposite way: before appending an `origin: auto` entry, the existing `id:` values in the file are checked, and a match is skipped as `SKIP — already logged` — because `id` is built from a stable `<KEY>-<command>-<short-slug>` shape, re-running a pipeline never double-logs the same automatic signal twice.

None of this pauses the run for approval. Capture is silent and high-recall by design — curation is the maintainer's job centrally, at analysis time, not something to ask a non-expert engineer to triage mid-run, where the honest risk is that they would either rubber-stamp everything or drop exactly the signal the maintainer needed.

## Bugs only (`--skip-feedback`)

`--skip-feedback` (or `WORKFLOWS_SKIP_FEEDBACK`) narrows the automatic maintenance phase — carried by all five of this plugin's commands — to bug capture only. Under the flag, the maintenance phase dispatches `workflows-core:defect-reporter` in place of `workflows-core:impl-maintenance`, on the cheap `classification.md` §2.2 chain (or the run's enforced model), with the same compact session handoff plus a `Plugin root:` line — the dispatching command's own plugin directory, which is where `defect-reporter` looks for the command, reference or agent file a candidate defect names. `defect-reporter` returns only real defects — a wrong or self-contradictory instruction, a broken script, gate or hook, a missing or wrong reference, a command contradicting its own documentation, a crash, or a defect in the ai-containers environment the family runs in (a missing tool, a wrong mount, a bad default) — never friction, wishes, polish, or the target-project tooling advice the in-session Lessons Learned report would otherwise carry, all of which this path drops entirely.

Any defect it returns is persisted through `emit-bugs` into the same `<KEY>-feedback.md` file, `origin: auto`, `category: environment-defect` for a container-environment location and the usual vocabulary otherwise. A defect-free run loads `workflows-core:feedback-emission` not at all and writes nothing. The run reports `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` in place of the usual persisted-path line.

## Where files land

The primary target is `<PRD-dir>/dev-workflows/<KEY>-feedback.md` — one file per PRD, resolved the same specs-first way session cost is — follow-ups run the same specs-first ladder now: walk down and stop at the first tier that applies. `$SPECS_PATH` writable with the PRD directory matched is the primary case; `$SPECS_PATH` writable but no PRD directory found writes to `$SPECS_PATH/dev-workflows-feedback/<KEY-or-date>.md` at the top of `$SPECS_PATH` instead, marked unfiled so it can be moved under the right PRD dir later with a loud warning that it will not auto-aggregate to the maintainer; a folder in the specs tree with neither available writes beside that directory; and if nothing resolves at all, the entry stays in the run's own printed output and is never written into your current working directory, since that may be a code repository. On a run carrying `specs_git: misrooted`, meaning `$SPECS_PATH` set inside the specs tree or below its repository's top level, the entry stays in the run's printed output instead, whatever else resolves, so nothing is written under a path the run found wrong. In every non-primary tier the entry also stays visible in the run's final output, so nothing is silently lost even when it can't be filed where it belongs.

**Committing and pushing this file alongside your specs is expected and encouraged, not clutter.** Feedback only reaches the maintainer once it lands in the committed, pushed specs repo, so every command's terminal step commits and pushes it as a matter of course — team-visible feedback across engineers is the entire point of this feature.

## Entry format

One file per PRD, `<KEY>-feedback.md`, opening with frontmatter written once on creation:

```yaml
---
type: dev-workflows-feedback
prd: PRODUCT-1234
slug: env-ag-update-window
---
```

Each logged entry is a dated heading, a fenced YAML block, and prose — appended chronologically, never modified or deleted once written:

````markdown
## 2026-07-09 — /design — missing-capability

```yaml
id: PRODUCT-1234-design-scope-boundary
date: 2026-07-09
command: /design              # controlled: exact command name, or n/a
plugin_version: 2.9.0
origin: auto                 # auto | manual | prompt
author: you@example.com
category: missing-capability # controlled, extensible, reuse-first
impact: friction             # blocker | friction | polish
```

**Friction:** Three screenshots landed without alt text and the page got pushed
back in review; the image phase collects URLs but never prompts for a description.

**Suggested improvement:** Have the image phase ask for alt text per image at
collection time, so the gap is caught before the page is written.
````

`category` is a controlled but extensible vocabulary — reuse an existing value when it fits rather than minting a near-duplicate, so signals cluster instead of fragmenting: `missing-capability`, `wrong-output`, `ambiguous-prompt`, `missing-reference-doc`, `model-routing`, `manual-workaround`, `false-positive`, `docs-ux`, `environment-defect`, `other`. `impact` is `blocker`, `friction`, or `polish`. `author` comes from `git config user.email` in the specs repo, best-effort, `unknown` if it can't be resolved — the git commit author is the second, authoritative identity layer once the entry is actually committed and pushed. An `origin: prompt` entry carries two additional prose blocks after Friction and Suggested improvement: **User prompt** (your corrective request, verbatim) and **Resolution** (what the AI actually did in response).

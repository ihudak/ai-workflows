# Session Feedback Emission — Shared Reference

Single source of truth for the plugin family's session-feedback emitter. Every capture surface — the automatic maintenance phase of all twenty-five workflow commands, or, under `--skip-feedback`, its bugs-only replacement, and the `/feedback` and `/prompt*` commands — cites this file and executes its steps inline. The orchestrator owns every prompt; this reference owns the entry format, the persistence ladder, dedup/attribution, the plugin-facing predicate, and the caller contract.

**Purpose.** Capture friction and improvement signals about the **plugin
family itself**, and defects in the ai-containers environment the family runs in (§4), and persist them per-PRD into the **specs repo** so the plugin
maintainer can aggregate feedback across engineers. Feedback reaches the
maintainer only if it lands in the committed, pushed specs repo — hence the
persistence ladder is **specs-first** (§2), and hence every command's terminal `commit-artifacts` step commits it, and pushes it per `${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` §4 step 5, save on a run carrying `specs_git: blocked` or `specs_git: misrooted`; under the second, §2 writes no entry in the first place. This emitter still
never touches git itself (§6 caller contract); the commit is a separate,
bounded, end-of-run step.

**Self-contained — no hard cross-plugin dependency.** `/prompt-brainstorm` uses
`superpowers:brainstorming`; `/prompt-grill-me` grills the fix inline following
the embedded grilling technique (`${CLAUDE_PLUGIN_ROOT}/references/grilling-technique.md`). Neither is
a declared install-time dependency.

**Relationship to B4 (`followup-emission.md`).** B4 captures the *engineer's own*
follow-up actions → audience = the engineer. This feature captures
*plugin* friction → specs-first, audience = the maintainer. Both share the
`<PRD-dir>/dev-workflows/` per-PRD area. **No dedup between them** — different
purpose, different audience.

**Relationship to `impl-maintenance`.** The automatic surface reuses the existing
`impl-maintenance` agent's analysis; the agent definition is **untouched**. The
caller passes its Lessons Learned report to `emit-auto` (§6), which projects the
plugin-facing slice (§4) and persists it. This reference never analyses a
session itself.

## 1. Entry format (machine-friendly hybrid)

One file per PRD, named `<KEY>-feedback.md`. Deterministic YAML for
filtering/clustering; prose for human judgment.

File-level frontmatter, written once on creation:

```yaml
---
type: dev-workflows-feedback
prd: PRODUCT-1234
slug: env-ag-update-window
---
```

- `prd` — the run's key, or `n/a` when no key resolved.
- `slug` — the feature slug from the PRD dir, or the ISO date on a keyless file.

Each entry is appended as a dated H2 header + a fenced YAML block + prose:

````markdown
## 2026-07-09 — /document — missing-capability

```yaml
id: PRODUCT-1234-document-cloud-self-hosted-split
date: 2026-07-09
command: /document           # controlled: exact command name, or n/a
plugin_version: 2.9.0
origin: auto                 # auto | manual | prompt
author: jane.doe@example.com
category: missing-capability # controlled, extensible, reuse-first
impact: friction             # blocker | friction | polish
```

**Friction:** One page covered both Cloud and Self-hosted; the Cloud half got pushed
back in review because the two products differ here.

**Suggested improvement:** Add an optional `cloud|self-hosted` parameter to
`/document` so the run scopes to one product.
````

- YAML fields, all required: `id`, `date`, `command`, `plugin_version`,
  `origin`, `author`, `category`, `impact`.
- `origin` — `auto | manual | prompt`.
- `impact` — `blocker | friction | polish`.
- **`category`** — controlled vocab, extensible, reuse-first (reuse an existing
  value when it fits so clusters don't fragment):
  `missing-capability`, `wrong-output`, `ambiguous-prompt`,
  `missing-reference-doc`, `model-routing`, `manual-workaround`,
  `false-positive`, `docs-ux`, `environment-defect`, `other`.
- **`origin: prompt` entries add two more prose blocks** after Friction /
  Suggested improvement: **User prompt** (the user's corrective request,
  verbatim save §1.1's redactions) and **Resolution** (what the AI actually did).
- `id` — stable: `<KEY>-<command>-<short-slug>` (drop the leading `/` from the
  command; use `manual` / `prompt` when `command` is `n/a`).

### 1.1 Redaction — while the entry is rendered

Every entry point (§6) redacts an entry **while it renders it**, before §3 compares its `id` with the ids already in the file and before it writes anything. The entry is committed and pushed to the specs repository (§2), where everyone with access to that repository reads it alongside the maintainer, so a value the user typed, or the session saw, must not travel with it. Redact every prose block, the **User prompt** included. Never redact `author`, which is the attribution §3 asks for, or the fields the plugin fills from its own vocabulary and records (`date`, `command`, `plugin_version`, `origin`, `category`, `impact`).

**The `id`'s short slug is derived from the redacted Friction, and carries neither a caught value nor a placeholder.** Name the slug after what went wrong (`registry-timeout`), never after the host, path or token involved. A slug is kebab-case, so a value in it no longer looks like what it is: one run would catch it and another would not, and §3's dedupe would then compare two different ids for one signal and log it twice.

Apply the rows in this order. A value one row has replaced is not matched again by a later row.

| Category | Replace with | What to catch | What to keep |
|---|---|---|---|
| Secrets | `[SECRET-n]` | A private-key block, from its `-----BEGIN … PRIVATE KEY-----` line through its `END` line. A token of a known shape: one of the prefixes `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`, `github_pat_`, `glpat-`, `xox` plus one letter and `-`, `AKIA`, `ASIA`, `sk-` (`sk-ant-` and `sk-proj-` included), `AIza` or `npm_`, at the start of a word and followed by at least 20 letters, digits, `_` or `-`; or a JWT (`eyJ….eyJ….…`). The password in a URL (`scheme://user:[SECRET-n]@host`). A bearer or basic `Authorization` value. A literal value assigned (`=` or `:`) to a name ending `_KEY`, `_TOKEN` or `_SECRET`, or named `PASSWORD` or `PASSWD`. | A word that merely contains a prefix (`risk-planner`, `npm_config_cache`). A reference to an environment variable rather than its value (a `$` followed by the variable's name), or a placeholder such as `<your-token>`. The family's own `workitem_key`. |
| Home paths | `~` | An absolute path under a home directory — `/home/<user>/…`, `/Users/<user>/…`, `C:\Users\<user>\…`, `/root/…` — becomes `~/…`, dropping the account name. | The rest of the path, so a plugin file stays recognisable (`~/.claude/plugins/cache/…`). |
| Hosts and addresses | `[HOST-n]` | A host in a private or corporate domain: a single-label name, or a name under `.internal`, `.local`, `.lan`, `.corp`, `.intranet` or an organisation's own internal domain. A private-range IP address (`10.`, `172.16.`–`172.31.`, `192.168.`, `fc00::/7`), and any other routable IP address. When a hostname could be either, redact it. In a URL, replace the host and keep the scheme, port and path. | `localhost`, loopback (`127.0.0.0/8`, `::1`), unspecified (`0.0.0.0`, `::`) and link-local (`169.254.`, `fe80::`) addresses, `host.docker.internal` and `host.containers.internal`, and the domain of a publicly reachable service — a code host, a package registry, a public API, a public documentation site (`github.com`, `api.github.com`, `pypi.org`, `registry.npmjs.org`, `services.nvd.nist.gov`). |
| Email addresses | `[EMAIL-n]` | Anything shaped like `local@domain.tld` that the rows above left in place. | A git remote such as `git@github.com:owner/repo.git`, which is a host, not an address; the user part of a URL; and a `name@<version>` package specifier. |

- **Number each category separately**, in order of first appearance in the entry: `[SECRET-1]`, `[SECRET-2]`, `[HOST-1]`. The same value takes the same placeholder throughout one entry, and numbering starts again in the next entry. Placeholders use square brackets, not angle brackets: `<SECRET-1>` is an HTML tag to a Markdown renderer, which would show nothing at all.
- **A placeholder replaces the value and nothing else.** The words around it stay exactly as written, so a redacted **User prompt** is still verbatim in every other character.
- **Keep what the maintainer needs in order to act:** command and agent names, plugin file paths (a home path becomes `~/…`, not a placeholder), flags, versions, line numbers, ports, and error messages with only their values redacted.
- **What is already in the file is never rewritten** (§3, append-only). Redaction applies to what this run appends.
- **Report it.** The entry point returns, beside the persisted path, what it redacted, by category and count: `redacted <N> value(s): <category> ×<n>[, …]`, or nothing when nothing was redacted. The caller appends that clause to whichever feedback line it prints: the persisted path, or under `--skip-feedback` the bugs-only line (`workflows-core:run-flags` §4). A report-only run (§2 tier 4) writes nothing, so it redacts nothing: the user sees their own text in their own terminal.

## 2. Persistence ladder (specs-first; never cwd)

`$SPECS_PATH` is primary — central aggregation is the whole point. Resolution is
**deterministic** (no interactive path prompt, consistent with silent
capture, §5). Walk the ladder top-down and stop at the first tier that applies:

**Before tier 1: the run carries `specs_git: misrooted`** (`specs-repo-git.md` §3.1, or `addressing.md` §3 `specs-root-check`'s stop) → **report-only**, as in tier 4, whatever else would apply. `$SPECS_PATH` is set but misplaced, so any write under it lands where `specs-repo-git.md` §2.1's classifier puts it in OTHER, or takes it for an artifact that cannot be staged from `$SPECS_PATH` and that the first run after the variable is fixed would commit in the wrong place. Every entry point below resolves its target here, so this covers them all.

1. **`$SPECS_PATH` resolvable + writable + the PRD dir exists** — the dir matched
   by `$SPECS_PATH/{specs|specifications|vis}/…/<KEY>{-|_}<slug>/…` →
   `<PRD-dir>/dev-workflows/<KEY>-feedback.md`. *[primary — the whole point]*
2. **`$SPECS_PATH` writable but no PRD dir matched** (no `key`, or no
   matching spec dir) — two destinations, and the documentation branch is tried
   first:
   - **The run is `/docs-init`, `/docs-audit`, `/docs-brand` on its standalone path, or `/document` in direct mode**, and it resolved the target it writes into (design D19) → `$SPECS_PATH/documentation/<docs-repo-slug>/dev-workflows/feedback/<date>.md`, where `<docs-repo-slug>` is the one-segment name `specs-repo-git.md` §2.1 defines for that repo — for direct mode, the write target its own Phase 0 step 3 resolved, which every direct-mode run holds from that step on — cited, never re-derived here, because the staging classifier admits exactly one segment there. Filed, not unfiled: the docs repo is that family's unit of attribution exactly as the PRD directory is the pipeline's, so there is nothing to move it under later. **Per docs repo, not one flat bucket**, and the inner `dev-workflows/` names the *family*, not the emitting plugin. `specs-repo-git.md` §2.1's `<specs-root>/documentation/*/dev-workflows/**` shape stages it.
   - **Otherwise** → `$SPECS_PATH/dev-workflows-feedback/<KEY-or-date>.md` at
     the top of `$SPECS_PATH`. Still committed & aggregated; notice:
     `unfiled — move under the PRD dir if it belongs to one.`

   **The branch names the runs it serves rather than testing "did the run resolve a
   docs repo"** — the same four, for the same reasons, as `cost-emission.md` §8
   gives. `/document` direct mode joined it after shipping outside it, when its
   entries landed unfiled at the top of `$SPECS_PATH` with no PRD to be moved under;
   entries it filed there before then stay where they are.
3. **`source = directory`** (a passed directory, no `$SPECS_PATH`) → beside that
   directory.
4. **Nothing resolvable** → **report-only**: keep the feedback in the run's
   final output and emit the notice. **NEVER write into the current working
   directory** — it may be a code repo.

In every non-primary tier the feedback also stays in the run's final output
(zero loss) and the run never fails. A write that fails mid-write (read-only
mount / permission) drops to the next tier with the same notice.

## 3. Dedup / append + attribution

- **Append-only.** Never modify or delete an existing entry. Append entries
  **chronologically** (newest at the end) for clean git diffs.
- **Auto entries dedupe:** before appending an `origin: auto` entry, read the
  existing `id:` values in the file and **skip** any that already exist (report
  `SKIP — already logged`). Because `id = <KEY>-<command>-<short-slug>` is
  stable, re-running a pipeline never double-logs.
- **Manual (`/feedback`) and prompt (`/prompt*`) entries are intentional** and
  are **never silently skipped.** On an `id` collision, append a numeric suffix
  (`-2`, `-3`, …) and warn if one looks near-identical.
- The file is created from the frontmatter template (§1) on first write.
- **Attribution:** `author` from `git config user.email` run in the specs repo
  (best-effort; `unknown` if unset). The *commit* author gives a second,
  authoritative layer once the engineer commits and pushes the specs.
  `plugin_version` is **supplied by the caller** — the version of the plugin whose command ran, read at run time from **that plugin's** `.claude-plugin/plugin.json` (`python3 -c "import json;print(json.load(open('<path>'))['version'])"`), which is exactly what every calling command already passes in. It is **not** resolved here: this reference is read through the loader skill, so a `${CLAUDE_PLUGIN_ROOT}` written *in this file* resolves to the plugin that **ships this reference**, and twenty-four of the twenty-nine callers ship from a sibling — their entries would silently take `workflows-core`'s version number instead of their own, beside a `command:` naming a command `workflows-core` does not ship — named outright, because every reader of this sentence is in a different plugin from the one it is about.

## 4. Plugin-facing predicate — what persists

Persist **only** signals about **this plugin family** itself — `workflows-core` and every plugin that declares it, currently `dev-workflows`, `product-workflows` and `docs-workflows` — and **defects in the ai-containers environment** the family is run in (`ihudak/ai-containers`). This line said "the dev-workflows plugin" until the family spanned four, and read literally it dropped every signal about the other three:

- Command workflow improvements (a command should behave differently — e.g. the
  `cloud|self-hosted` scoping case).
- New agents / skills the plugin should offer.
- Gaps in the reference docs of **whichever family plugin the signal is about** — `plugins/<that plugin>/references/**`, resolved from the running command's own plugin, and **not** `${CLAUDE_PLUGIN_ROOT}/references/**`. Written in this file that variable resolves to the plugin that *ships this reference* (`workflows-core`), so a `/prd-ground` run classifying a gap in `product-workflows`'s `brd-format.md` would test it against the wrong tree — the same hazard §3's `plugin_version` paragraph states, met one section later.
- Corrective interactions captured by `/prompt*` (any command output the user
  had to fix).
- Defects in the ai-containers environment — a tool the ai-containers image is meant to provide and lacks, a wrong mount, a bad default — as `category: environment-defect`.

**Do NOT persist target-project tooling advice** — project `CLAUDE.md` rules,
target-repo hooks, and other repo-specific suggestions stay in
`impl-maintenance`'s in-session report, not the feedback file. That advice is
for the engineer's current repo, not the plugin maintainer.

### 4.1 Defect predicate

Fixable in the plugin family or in ai-containers:

- a wrong or self-contradictory instruction; a broken script, gate or hook; a missing or wrong reference; a command contradicting its own documentation; a crash;
- a container environment defect: a tool missing from the ai-containers image, a wrong mount, a bad default (a tool missing on the user's own machine or from any other container is not one — §6 `emit-block`).

Excluded: friction, wishes, improvements, polish; user mistakes (wrong argument, typo, misaddressed key); target-project issues; Claude Code / model / external-service issues neither repo can fix.

`workflows-core:defect-reporter` applies this predicate directly under `--skip-feedback` (`workflows-core:run-flags` §4) — it cites this section, never copies it. The widening in this section's opening paragraph applies to every run, not only a bugs-only one: an ai-containers defect is now in scope for a full `emit-auto` run too, so a container bug surfacing during an ordinary session is no longer dropped by the plugin-only reading this predicate used to have.

When projecting an `impl-maintenance` report (§6 `emit-auto`), the plugin-facing
slice is exactly its **Command workflow improvements**, **New agents / skills**,
and **Reference docs** (paths under `${CLAUDE_PLUGIN_ROOT}`) sections, plus the
**Key observations** that triggered them, plus any **Key observations** naming an ai-containers defect (§4), projected as `category: environment-defect`. Discard its **CLAUDE.md rules** and
**Hooks** sections (target-project advice).

## 5. Interaction model — silent, high-recall

No curation/approval gate on capture. Capture is high-recall and zero-friction;
curation is the maintainer's job, centrally, at analysis time. A non-expert
engineer asked to approve/select/edit would rubber-stamp or drop the exact
signal the maintainer needs.

- **Automatic (`emit-auto`)** entries are written **silently**; the caller lists
  the persisted path (or "no plugin-facing signal — nothing persisted") in its
  output. A routine session with no plugin-facing signal writes nothing — no
  empty entry, byte-identical to the report-only behavior the run has without `emit-auto`.
- **`/feedback` and `/prompt*`** are user-invoked, so invocation *is* the
  intent; they write silently and surface the resulting path (and any
  degradation notice) in the command output.
- **`emit-block`** writes silently exactly like `emit-auto`; the halt is
  surfaced by the caller's existing `BLOCKED` escalation, **not** by a feedback
  prompt — capture-at-block stays inside the silent model (no interrupt beyond
  the block that was already happening, no curation gate).
- **`emit-bugs`** writes silently exactly like `emit-auto`; the caller surfaces the persisted path — or the "no defects" notice — only in its `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` / `— no defects` report line (`workflows-core:run-flags` §4), never as a curation prompt.

## 6. Caller contract

Five named entry points: `emit-auto`, `emit-manual`, `emit-prompt`, `emit-block`, and `emit-bugs`. Every caller supplies `plugin_version` (§3) and lets
this reference resolve the target (§2), dedupe/append (§3), and format the
entry (§1). Every entry point redacts the entry per §1.1 while it renders it, before §3's dedupe compares ids. None of them commits; none writes into a docs/code repo or the
current working directory, where it is not the specs repository. The artifacts are committed later, once, by the
run's terminal `commit-artifacts` step
(`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` §4).

### `emit-auto` — automatic callers (the twenty-five commands' maintenance phases, §1)

Inputs: the `impl-maintenance` **Lessons Learned report**, `command` (the exact
slash-command name), `key` (or `null`), `source` (`specs | directory | none`).

Behavior: project the plugin-facing slice per §4 (Command workflow improvements
+ New agents / skills + plugin Reference docs + the triggering Key observations
+ Key observations naming an ai-containers defect (§4), as `category: environment-defect`);
render one `origin: auto` entry per distinct plugin-facing signal (Friction =
the observation, Suggested improvement = the suggestion); dedupe by stable `id`
(§3); resolve the target (§2); write silently (§5). Return the persisted path,
or "no plugin-facing signal — nothing persisted" when the slice is empty.

### `emit-manual` — `/feedback`

Inputs: `command` (the exact name, or `n/a`), the user-authored **Friction** and
**Suggested improvement** prose, an inferred-and-confirmed `category` (§1 vocab),
`impact`, `key` (or `null`), `source`.

Behavior: `origin: manual`; never silently skipped (§3 collision rule); resolve
the target (§2); write; surface the path + any degradation notice.

### `emit-prompt` — `/prompt`, `/prompt-brainstorm`, `/prompt-grill-me`

Inputs: `command` (inferred from recent context, or `n/a`), the **corrective
triple** — Friction, the **verbatim User prompt** (redacted here per §1.1, never by the caller), and the Resolution — a
`category`, `impact`, `key` (or `null`), `source`.

Behavior: `origin: prompt`; write the entry with the two extra prose blocks
(User prompt verbatim save §1.1's redactions + Resolution, §1); never silently skipped (§3); resolve
the target (§2); write silently (§5); surface the path.

### `emit-block` — capture-at-block (a run halting on a plugin gap or on a tool the ai-containers image lacks)

Inputs: `command` (exact slash-command name), `key` (or `null`), `source` (`specs | directory | none`), and the **halting gap** — a short description of
the plugin capability / reference / skill / command-path the run needed but the
plugin lacked, or the tool the run needed that the ai-containers image is meant to provide and lacks. Unlike `emit-auto`, no `impl-maintenance` report exists (the run
is being abandoned mid-flight), so the gap is passed directly.

Behavior: render **one** entry with `origin: auto` and **`impact: blocker`**;
`category` from the §1 vocab (`missing-capability` / `missing-reference-doc` /
`manual-workaround` / `model-routing` as fits, and `environment-defect` for a
tool the ai-containers image lacks); dedupe by the stable `id` (§3) —
so it will not double-log if a later terminal `emit-auto` captures the same gap
on a resumed run; resolve the target (§2); **write silently** (§5). Return the
persisted path (for the caller's block message / report). The caller then
surfaces its normal `BLOCKED` escalation — `emit-block` never prompts.

**Predicate — fires ONLY for a plugin-facing gap** (the plugin lacked something
the run needed) **or a halt on a tool the ai-containers image is meant to provide and lacks** — a §4.1 container defect, which fires
`emit-block` with `category: environment-defect`. That case wins over the
environment exclusion below, and it is the only missing-tool halt that does: a tool missing on the user's own machine, or from any container not built from ai-containers (e.g. the project's own build tool behind a `test-baseliner` `COMMAND_NOT_FOUND`, or a docs tool `toolchain-preflight` reports missing), is an environment halt and does not fire `emit-block`. This paragraph is the single statement of that scope; every command's capture-at-block paragraph points here rather than restating it. It does **NOT** fire for: a code / doc / Epic review **BLOCK**
(a defect in the *work*, not the plugin); any other environment / user halt
(repo-missing, dirty-tree, key-not-found, refresh-blocked, and the other
`escalation-rules.md` cases); or user cancellation. The §4 plugin-facing scoping
applies (never target-project `CLAUDE.md` / hook advice).

### `emit-bugs` — bugs-only callers (`--skip-feedback`, `workflows-core:run-flags` §4)

Inputs: the `defect-reporter` **Defects** list, `command` (the exact slash-command name), `key` (or `null`), `source` (`specs | directory | none`), and `plugin_version`.

Behavior: render one `origin: auto` entry per defect — Friction = the defect plus its evidence; Suggested improvement = the repro plus the location to fix; `impact` is `blocker | friction` only, never `polish` — `emit-bugs` drops any defect marked `polish` and writes no entry for it; `category` is drawn from §1's vocabulary — `environment-defect` for a container-environment location, else `wrong-output` / `missing-reference-doc` / `missing-capability` / `other` as fits; dedupe by the stable `id` (§3); resolve the target (§2); write silently (§5). Return the persisted path.

`emit-bugs` replaces `emit-auto` for the duration of `--skip-feedback`, and is called only when `defect-reporter` returned at least one defect — the orchestrator dispatches `workflows-core:defect-reporter` in place of `impl-maintenance` and, only on a non-empty Defects list, calls `emit-bugs` on the result; when the list is empty, this reference is not loaded at all and the caller reports `— no defects` directly (`workflows-core:run-flags` §4).

# Session Cost Emission — Shared Reference

Single source of truth for the plugin family's session-cost subsystem. Twenty-six of
the twenty-eight commands with an §7 row cite this file from their terminal
"Session cost" phase and execute its steps inline through the single `emit-cost`
entry point (§11). The other two — `/prompt-brainstorm` and `/prompt-grill-me` —
cede the session before such a phase could run, call `emit-cost` never, and
instead record an intent in Phase 2 that a later run replays on their behalf
(§13). Both routes produce the same §6 entry.

**Which commands those are is §7's attribution table, and nothing else.** A command
emits a cost entry if and only if §7 gives it a row, so no roster and no total is
restated here: the PRD-lifecycle commands have rows there, so do the `/brd-*`
commands of the BRD-to-PRD route, so do the two effort-proposal commands, and so
do the four feedback
commands, which are not PRD-lifecycle and infer their labels rather than carrying
fixed ones. Read the
table for the set; a second copy of it in this preamble is what went stale before —
the list this sentence replaces named the PRD-lifecycle commands only, and had
already omitted every `/brd-*` emitter.

The orchestrator owns every prompt; this reference owns session-artifact resolution,
the chained-checkpoint model, the transcript-window computation, the price table,
the report format, the persistence ladder, pending/reconciliation, and the
optional statusline augmentation.

**Purpose.** Know how many **dollars** a Product Requirements Document (PRD) cost across its
whole lifecycle, broken down by **phase**, **role**, and **model** — persisted
per-PRD into the specs repo so the maintainer can aggregate spend across every
engineer and team. A PRD's cost is the sum of per-command cost lines contributed
by every session that worked on it; summing is a read-time concern for the
maintainer — the plugin only ever appends immutable per-invocation measurements.

**Cost is computed, never read.** Claude Code stores no dollar figure in the
transcript. Every assistant message carries `.message.usage` + `.message.model`;
`${CLAUDE_PLUGIN_ROOT}/scripts/session-cost.py` sums tokens per model and multiplies by a price table
(§4). One API response is written as several assistant records sharing one `.message.id`, each
repeating the usage — a streaming partial first, the final record later — so within one measured
window each message id is counted once, at its final usage, across the main transcript and its
subagent transcripts together. A call whose records straddle two windows' edge is still counted in
each. Dollars are therefore an estimate that drifts from Claude Code's own figure
by the accuracy of the price table — an accepted trade (cost accuracy is
explicitly secondary to code/doc quality).

**Relationship to siblings.** Shares the `<PRD-dir>/dev-workflows/` per-PRD home
with `feedback-emission.md` / `followup-emission.md` and the self-contained
emitter pattern, but diverges deliberately: a **`cost/` subdir with per-session
files** (merge-safety under massive team fan-out — the largest PRD to date was
worked by 23 teams) and **no dedup / no prose** (pure measurement, append-only).
No dedup or cross-reference between the three. This subsystem does NOT use the
`impl-maintenance` agent.

**Cost runs unless the user skipped it.** Unlike feedback (which writes nothing when there is no plugin signal), the cost phase always computes and always advances the checkpoint (§3) — even when it can only report-only — except under `--skip-costs`, where `workflows-core:run-flags` `skip-cost` advances the checkpoint without loading this file and writes no entry. A silent write with no interaction is the norm; the sole interactive moment is pending reconciliation (§9), and only when pending files exist.

## 1. Session-artifact resolution

Derive from `cwd` and the current session (Claude Code's project-slug rule):

- **`<cwd-slug>`** — the absolute `cwd` with every `/` and `.` replaced by `-`
  (e.g. `/workspace/docs` -> `-workspace-docs`).
- **Main transcript** — the newest `*.jsonl` directly under
  `~/.claude/projects/<cwd-slug>/`. Its basename minus `.jsonl` is `session_id`.
- **`<sid8>`** — the first 8 characters of `session_id`.
- **Subagents dir** — `~/.claude/projects/<cwd-slug>/<session_id>/subagents/`
  (holds `agent-*.jsonl` with their own Sonnet/other `usage` + `model`).

## 2. Cost computation (`session-cost.py`)

Invoke the shipped helper (stdlib-only, pure computation, no specs-repo writes):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/session-cost.py" \
  --transcript    <main transcript .jsonl (§1)> \
  --subagents-dir <subagents dir (§1)> \
  --prices        <resolved price table (§4)> \
  --checkpoint    ~/.claude/dev-workflows/cost-state/<session_id>.json \
  --snapshot      ~/.claude/dev-workflows/cost-snapshots/<session_id>.json \
  --now-ts        <current UTC ISO8601> \
  --claim         </command per §13.1 deferred record, oldest first; repeatable>
```

**Nothing here names a `commands/` directory, and that absence is the fix rather than an omission.** Command boundaries resolve in **two** steps that used to be one, and the distinction is load-bearing: a window is **cut** at any well-formed command envelope, whatever marketplace it came from, while an invocation is **claimable** only when it resolves against `scripts/command-namespaces.json`, the manifest shipped beside the helper — namespace → that plugin's own command names, one entry per plugin of this marketplace that ships commands — read with no flag and no path assumption. The invocation used to carry `--commands-dir "${CLAUDE_PLUGIN_ROOT}/commands"`, and that flag was wrong twice over. **This file is read through the loader skill**, so `${CLAUDE_PLUGIN_ROOT}` resolves to the plugin that *ships this reference* and its handful of family-meta commands, while the run emitting the entry is routinely a sibling's — the path resolved, just to the wrong files, which is why no assertion ever saw it. And one plugin's set is the wrong set regardless: §13.2's boundary rule spans every plugin here, so a caller-supplied per-plugin path could only ever narrow it back. `--namespaces <path>` overrides the manifest and exists to be pointed at a fixture; where it resolves to nothing, **boundary detection is off** — every claim comes back unmatched and §13.4 discards the attribution. `--claim` is absent on the ordinary run, which is every run with no §13.1 file.

The helper reads the main transcript **from the checkpoint's line offset
forward, skipping JSON-parsing of every line before that offset** — I/O still
scans the whole file (the transcript can be tens of MB), but the offset saves
re-parsing lines already processed by a prior command — plus every
`subagents/agent-*.jsonl` entry with `timestamp` in `(last_ts, now]`, groups
`usage` by `model`, applies the price table, and prints JSON to stdout:

```json
{
  "models": [
    {"model": "...", "cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0,
     "cache_read_tokens": 0, "cache_write_tokens": 0}
  ],
  "cost_computed_usd": 0.0,
  "cost_statusline_usd": null,
  "duration_s": 0,
  "compactions": 0,
  "command_boundaries": [{"command": "/x", "ts": "...Z", "line_offset": 0}],
  "claims": [
    {"command": "/x", "ts": "...Z", "models": [], "cost_computed_usd": 0.0,
     "duration_s": 0, "compactions": 0}
  ],
  "unmatched_claims": [],
  "new_checkpoint": {"line_offset": 0, "last_ts": "...Z", "last_snapshot_cost": null}
}
```

With no `--claim`, `claims` and `unmatched_claims` are empty and
`models`/`cost_computed_usd` cover the whole window exactly as before. With
claims, **the top-level block is the remainder** — this run's own spend — and each
`claims[]` entry carries its own `models`, `cost_computed_usd`, `duration_s` and
`compactions`, which is what §13.3 builds a replayed §6 entry from. `command_boundaries` is
reported whenever the §2 manifest resolves, claim or no claim, and `namespaces`
lists the plugin namespaces it was resolved against.

An unknown model (absent from the table) is recorded with its tokens,
`cost_usd: null`, and `note: unpriced-model` — the run never fails. `emit-cost`
formats `models` + `cost_computed_usd` + `cost_statusline_usd` + `duration_s` +
`compactions` into the entry (§6) and writes `new_checkpoint` back (§3).

**`compactions` counts what the computed figure cannot price.** Claude Code bills
the call that summarises a context on `/compact`, or on its own when the context
fills, but writes no `usage` for it into the transcript — only a `system` record
with `subtype: compact_boundary`. So `cost_computed_usd` leaves every compaction
out, and nothing on disk says what one cost: the record's `preTokens` is the size
of the context it summarised, not what was billed for it. The script counts these
records where it counts usage — main-transcript lines from the checkpoint's
offset, subagent records in `(last_ts, now]` — and splits them across claims as it
splits usage, so a compaction inside a claimed segment is that claim's. It never
estimates their price.

## 3. Chained-checkpoint model

Single touchpoint per command; a command's window START is the previous
family command's END in the same session.

- **Checkpoint file:** `~/.claude/dev-workflows/cost-state/<session_id>.json` —
  per-user, per-session, **transient/local, NEVER committed** (safe to delete).
- **Contents:** `{line_offset, last_ts, last_snapshot_cost}` captured at the END
  of the last cost phase.
- **First command in a session:** no checkpoint -> `line_offset: 0`,
  `last_ts: null` -> the window starts at the session origin (start = $0).
- **Advance ALWAYS.** After computing, write `session-cost.py`'s `new_checkpoint`
  back to the checkpoint file — **even in the pending / report-only tiers (§8),
  so the next command's window is correct.** The write is a plain overwrite of
  the transient local file (no git, no specs repo).
- **A command that cedes the session advances the checkpoint late, not never**
  (§13): a later run closes its window retroactively, at **the next command
  invocation of any kind** — not at that later run's own start, which would fold
  any intervening command's spend into the ceded run's phase.
- **Semantics (for users):** the whole session's spend is attributed to the PRD;
  activity between commands rolls into the next command's bucket; the
  pre-first-command and post-last-command tails are unattributed (~0 for a clean
  per-PRD container session). Per-command costs therefore sum to the session total
  minus those tails.

## 4. Price table

`${CLAUDE_PLUGIN_ROOT}/references/cost-prices.yaml` requires a top-level **`models:`** map keyed by
model id, **USD per million tokens** (`input`, `output`, `cache_read`,
`cache_write_5m`, `cache_write_1h`), plus a top-level `default: null`:

```yaml
models:
  <model-id>:
    input: <usd-per-million>
    output: <usd-per-million>
    cache_read: <usd-per-million>
    cache_write_5m: <usd-per-million>
    cache_write_1h: <usd-per-million>
    fast:                          # optional: the same five rates for usage.speed == "fast"
      input: <usd-per-million>
      ...
modifiers:                         # optional
  inference_geo:
    us: 1.1                        # multiplies every category of a usage.inference_geo == "us" record
default: null
```

**Two facts in a transcript change the rate rather than the token count, and both are priced.** Every assistant message carries `usage.speed` (`standard` | `fast`) and `usage.inference_geo` (`global` | `us` | `not_available`). The engine buckets each model's tokens by that pair and prices each bucket separately:

- **`speed: fast`** prices from the model's own `fast:` sub-block — explicit rates, like every other rate in the table, never a multiplier. Fast mode exists on Opus 5.5 ($8/$40) and on Opus 5 and Opus 4.8 ($10/$50). Opus 4.6 accepts `speed: fast` but runs and bills at standard, so its `fast:` block repeats the standard rates; Opus 4.7 rejects it and has no block. Prompt-caching multipliers apply on top of the fast input price, so Opus 5.5's fast cache read is 0.05 × $8, not 0.05 × $4. A fast record on a model whose entry has no `fast:` block is **`unpriced-speed:fast`, cost null** — never priced at the standard rate, which would be a confident figure known to be low by half.
- **`inference_geo: us`** multiplies every category by `modifiers.inference_geo.us` (1.1), and stacks on fast mode. `global`, `not_available` and an absent field are the standard case and are never looked up, so an override file written before this map existed still prices every global record. Any other value with no entry is **`unpriced-inference-geo:<value>`, cost null**.

Both follow this file's one rule about an unknown: a null the run reports beats a plausible figure nobody confirmed. The engine previously read neither field and the table said these modifiers were "NOT applied (interactive Claude Code sessions bill at standard rates)" — false from the first `/fast` session, and wrong in one direction only. No entry written before then is affected: every record observed locally was `standard` with `global` or `not_available`.

Model lookup is exact-first, then longest-prefix: an undated base key (e.g.
`claude-sonnet-5`) prices a dated transcript model id (e.g.
`claude-sonnet-5-20250930`) when no exact key matches.

The `models:` wrapper is **required** — `price_model()` reads
`prices.get("models")`, so model ids placed at the top level (as siblings of
`default`, instead of nested under `models:`) are never found and every model
prices as unpriced / `$0`. An override supplied via `$DEV_WORKFLOWS_COST_PRICES`
(below) is read by this same `price_model()`, so it must use this identical
nested shape.

**`default: null` is documentary only** — `price_model()` never consults it as a
fallback rate map. Any model id absent from `models:` is always priced
`cost_usd: null` with `note: unpriced-model` (§6), regardless of what `default`
is set to.

Cache multipliers follow Anthropic's standard model (read 0.1x, 5m write 1.25x,
1h write 2x) — except Opus 5.5, whose cache reads bill at 0.05x, and the table keys
every rate explicitly for that reason; the transcript's `ephemeral_5m` / `ephemeral_1h` split lets cache
pricing be exact, and a message without the split prices
`cache_creation_input_tokens` at the 5m rate.

**Resolution order (first found wins):** `$DEV_WORKFLOWS_COST_PRICES` (a path) ->
a repo-local `cost-prices.yaml` -> the shipped
`${CLAUDE_PLUGIN_ROOT}/references/cost-prices.yaml`. The shipped rates are the
standard first-party Claude API prices (from Anthropic's pricing page) for every
model the routing policy can reach — the Opus chain and the Sonnet chain —
**plus the models no chain names but a session's own model or an `--enforce-model` (or `$WORKFLOWS_ENFORCE_MODEL`) value can be — Opus 4.5, Mythos, Fable and Haiku**; a maintainer refreshes them when
Anthropic's prices change. **Permanent standard
rates are used deliberately — never promotional/introductory rates** — so cost
stays comparable across PRDs over time (a temporary promo would make identical
work look cheaper now and dearer later, distorting efficiency comparisons).

## 5. Statusline augmentation (optional — "Option B")

An authoritative cross-check, available only when the plugin statusline is
installed (via `/workflows-core:statusline`):

- The shipped statusline writes a snapshot each render:
  `~/.claude/dev-workflows/cost-snapshots/<session_id>.json = { ts, cost_usd }`
  from its stdin `.cost.total_cost_usd` (an overwrite of a single object each
  render — bounded size).
- `emit-cost` passes `--snapshot`; `session-cost.py` sets `cost_statusline_usd` =
  (current snapshot `cost_usd`) - (the `last_snapshot_cost` stored in the
  checkpoint) — a **per-invocation delta on this entry only**, chained
  identically to Option A. **Never an aggregate, never a shared source of truth**
  -> immune to the merge concern.
- **Auto-detect:** the field is emitted only when the current snapshot file
  exists, a prior checkpoint baseline (`last_snapshot_cost`) is already recorded,
  **and no §13 claim matched in this window** (a whole-render measurement cannot
  be apportioned across a split); otherwise it is `null` and simply omitted from
  the entry. No
  configuration. In practice, the **first** cost phase in a session always omits
  the field — even with the statusline installed, there is no baseline yet — and
  the **second and later** commands emit the delta against it.
- **Boundary caveat:** B is authoritative on price but lags at the tail (the
  statusline renders *after* the final turn); A reads the per-turn transcript so
  it is more complete at the boundary. **Over a window with no compaction**, the
  two differing by cents is the intended calibration signal (drift => refresh
  the price table).
- **Compaction caveat:** B includes every compaction in the window and A
  includes none (§2's `compactions`), so over a window that held one, B exceeds A
  by roughly what the compactions cost — dollars, not cents, on a large context:
  a live `/specify` window holding one manual `/compact` of a 675,221-token
  context differed by $3.23. That gap is not price-table drift, and the entry's
  `compactions:` field (§6) is what tells a reader so.
- Pending a one-line implementation check that `.cost.total_cost_usd` is present
  on the statusline stdin in the target Claude Code version; if absent, B is
  simply unavailable and A stands alone.

## 6. Report artifact & entry format

**Location (merge-safe by construction):** one file per session under the PRD's
shared area — `<PRD-dir>/dev-workflows/cost/<sid8>.md`. No two sessions share a
file -> no merge conflicts across many teams or one person's N sessions. **No
user name anywhere in the file** (§10).

File-level frontmatter (written once on creation):

```yaml
---
type: dev-workflows-cost
prd: PRODUCT-1234
session: <sid8>
---
```

One appended entry per command invocation (append-only, **never deduped** — each
invocation is a distinct measurement, so `/design Epic1` then `/design Epic2` in
one session are two lines):

````markdown
## 2026-07-09T14:22:33Z — /implement — implementation

```yaml
id: PRODUCT-1234-98760-implement-2026-07-09T14:22:33Z   # timestamp => unique
date: 2026-07-09T14:22:33Z
command: /implement
phase: implementation
role: dev
prd: PRODUCT-1234
epic: EPIC-98760            # present only when an Epic key is in scope
plugin_version: 2.10.0
duration_s: 1284
cost_computed_usd: 3.4821
cost_statusline_usd: 3.5102   # present only when the plugin statusline is installed
compactions: 1               # present only when the window held a compaction (§2)
models:
  - {model: claude-opus-5, cost_usd: 2.9114, input_tokens: 12043, output_tokens: 88210, cache_read_tokens: 2109887, cache_write_tokens: 145002}
  - {model: claude-sonnet-5, cost_usd: 0.5707, input_tokens: 45120, output_tokens: 210334, cache_read_tokens: 880122, cache_write_tokens: 42011}
```
````

Machine-friendly YAML so the maintainer can filter/sum with Claude Code. No prose
block (unlike feedback). `cost_statusline_usd` is omitted when Option B is
unavailable; `compactions` is omitted when §2 returned 0, and otherwise says that
`cost_computed_usd` leaves that many billed compactions out (§5's compaction
caveat); a model priced `null` carries a `note:` saying why — `unpriced-model`
(no key for the id), `unpriced-speed:<value>` (the record ran in a speed the model's
entry has no rate block for), or `unpriced-inference-geo:<value>` (a residency the
table has no multiplier for).

**A row may carry `modifiers:`** — a list such as `[speed:fast]` or
`[inference-geo:us, speed:fast]` — present only when some of that model's tokens were
priced at a non-default rate. Fast mode and US-only inference change the **rate**, not
the token count, so a row's tokens are still the plain totals while its `cost_usd` is
the sum over its `(speed, geo)` variants; without the field, a fast row's cost per
token would simply look like a wrong price table. A row with no `modifiers:` was
priced entirely at standard, global rates. The engine reads `usage.speed` and
`usage.inference_geo` off every assistant message (§4).

### 6.1 Unpriced-model dominance warning

A `note:` on a null-cost row (above) is an inline field inside the persisted YAML
entry — easy to miss when nobody opens the cost file. When the run's tokens
are actually **dominated** by an unpriced model, that has to be visible where
the user is already looking: the run output.

**Trigger.** Among the entry's `models` array (§6), some model has `cost_usd: null` —
whichever of the three notes it carries: `unpriced-model`, `unpriced-speed:<value>`, or
`unpriced-inference-geo:<value>` — **and** its token total
(`input_tokens + output_tokens + cache_read_tokens + cache_write_tokens`) is
the largest of any model in the array — i.e. the model the price table cannot
price is the single biggest contributor to this run, not a minor stray call.

**Action.** `emit-cost` prints one visible warning line to the run output —
not just the inline YAML note — in every persistence tier, including
report-only (§8 tier 5), naming the model id and stating that the figure is a
lower bound:

```
⚠ Cost estimate is a lower bound — <model-id> is unpriced (<reason>) and
accounts for the most tokens in this run; its cost is recorded as null and
excluded from cost_computed_usd. See the maintainer checklist (§12) to price it.
```

`<reason>` is the row's own note in words: `absent from cost-prices.yaml` for
`unpriced-model`; `no fast-mode rates for this model in cost-prices.yaml` for
`unpriced-speed:fast`; `no multiplier for inference_geo <value> in cost-prices.yaml` for
`unpriced-inference-geo:<value>`. The last two name a table that is *behind* rather than
a model that is missing — the fix is a `fast:` block or a `modifiers.inference_geo` entry,
not a new model key.

Print-only — no extra file write, no interactivity, and it never blocks or
alters the entry that gets persisted (§6 still writes `cost_usd: null` for
that model exactly as before).

## 7. Attribution (phase / role / keys)

Fixed per-command labels, with seven inferred exceptions:

| Command | phase | role |
|---------|-------|------|
| `/specify` | specification | pe |
| `/epics` | epic-refinement | pe |
| `/design` | planning | dev |
| `/implement` | implementation | dev |
| `/ready` | readiness | dev |
| `/document` | documenting | dev |
| `/release-notes` | **inferred** | **inferred** |
| `/idea` | prd-creation | pm |
| `/create-prd` | prd-creation | pm |
| `/update-prd` | prd-update | pm |
| `/create-ard` | architecture | pa |
| `/frames` | **inferred** | **inferred** |
| `/brd-intake` | brd-to-prd | pm |
| `/prd-ground` | brd-to-prd | pa |
| `/brd-split` | brd-to-prd | pm |
| `/brd-interview` | brd-to-prd | pm |
| `/brd-package` | brd-to-prd | pm |
| `/brd-reconcile` | brd-to-prd | pm |
| `/prd-proposal` | proposal | pm |
| `/brd-proposal` | proposal | pm |
| `/prompt` | **inferred** | **inferred** |
| `/feedback` | **inferred** | **inferred** |
| `/prompt-brainstorm` | **inferred** | **inferred** |
| `/prompt-grill-me` | **inferred** | **inferred** |
| `/diagnose-session` | **inferred** | **inferred** |
| `/docs-brand` | docs-scaffold | dev |
| `/docs-init` | docs-scaffold | dev |
| `/docs-audit` | docs-audit | dev |

**`/release-notes` inference (PM PRD-run vs. dev documenting-run).** The
discriminator is the presence of **downstream engineering artifacts** — any
`specification.md` or `design.md` under the PRD's specs dir:

- **None present -> `phase: prd-creation`, `role: pm`** (the PM's early run: the PRD
  exists but no engineering work has started — Epics may or may not exist yet,
  which is fine, since a freshly created PRD with no Epics is exactly the PM case).
- **Either present -> `phase: documenting`, `role: dev`** (the dev re-run, when
  PRD + Epics + specs + design + code all exist).

**`/frames` inference (which route the indexed folder sits on).** The
discriminator is the **resolved folder's own `kind`**, which the run has already
read off its frontmatter (`${CLAUDE_PLUGIN_ROOT}/references/addressing.md` §4) in
order to address it at all — re-derivable from disk, like `/release-notes`'s and
unlike the `target_command` one below:

- **`kind: brd` -> `phase: brd-to-prd`, `role: pm`.** A folder asserting
  `kind: brd` — a BRD container, or a BRD-route slice, a `PRD-` folder whose
  `brd-link.md` asserts it — is on the BRD-to-PRD route, where `/prd-ground` is
  the command that reconciles a slice's frame sets; spend preparing one belongs to
  that route's phase. The kind decides, not the prefix, so a slice's frame set is
  `brd-to-prd` although the slice is a `PRD-` folder.
- **`kind: prd` or `kind: epic` -> `phase: prd-creation`, `role: pm`.** A folder
  asserting `prd` is an idea-route PRD folder, whose frame set is the PRD's own
  design record — `/idea` vendors one there during PRD creation — and one
  asserting `epic` is an Epic folder, which sits under its PRD on that route.
  **An Epic folder under a BRD-route slice lands here too**: it asserts `epic`,
  and `/prd-ground` grounds the slice's own `design/`, never an Epic's.

**There is no third branch**, because §3 of
`${CLAUDE_PLUGIN_ROOT}/references/addressing.md` returns exactly those three kinds
and `/frames` refuses to run on an address that resolves to none of them. Indexing
a frame set is real spend on a real artifact in the specs tree, which is why this
command emits at all — the alternative is not "unmeasured" but *misattributed*, per
§3's semantics rolling it into whatever command runs next.

**`/diagnose-session` passes `target_command: n/a` on every run**, so the bullet below for a target of `n/a` charges it to `plugin-feedback`/`n/a`: a diagnosis is about the plugin itself, whichever command it reads, so it inherits nothing.

**`/prompt`, `/feedback`, `/prompt-brainstorm` and `/prompt-grill-me` inference
(inherit the corrected command's labels).**
The discriminator is **`target_command`**, passed in by the caller per §11 — the
command whose output is being corrected or remarked on, or `n/a`. Unlike
`/release-notes`'s discriminator, this one is **not** re-derivable from disk: it
lives in the run's own context, so the caller must supply it and `emit-cost` must
not attempt to infer it from anything else.

- **Target has a fixed `phase`/`role` in the table above -> inherit both.** A
  `/prompt` correcting a `/specify` output is `specification`/`pe` spend; one
  correcting a `/design` output is `planning`/`dev`. This is the point of the
  rule: the cost of fixing a phase's output belongs to that phase, so "what did
  specifying cost" includes the cost of making the spec right.
- **Target is `/release-notes` -> resolve ITS inference first**, then inherit the
  result. One level only; `/release-notes` never resolves to another inferred row.
  **If no PRD dir resolves** — a keyless run, which both callers explicitly support —
  its discriminator cannot be evaluated at all, so do **not** fall through to its
  "none present" branch: that would attribute a keyless plugin correction to
  `prd-creation`/`pm`, which is exactly the guess `role: n/a` exists to forbid.
  Treat it as the `n/a` case below.
- **Target is `n/a`, or a command with no row above -> `phase: plugin-feedback`,
  `role: n/a`.** The second case covers `/vuln`, `/upgrade`, `/docs-profile`,
  `/docs-serve`, `/statusline`, `/harvest-decisions` and `/promote-decisions`, none of which emits cost and so has
  nothing to inherit.
- **Target is `/frames` -> resolve ITS inference first**, then inherit the result,
  exactly as for `/release-notes`. One level only. Where no folder resolves — which
  for `/frames` means the run never started — treat it as the `n/a` case.
- **Target is `/feedback`, `/prompt`, `/prompt-brainstorm`, `/prompt-grill-me` or `/diagnose-session` -> treat as `n/a`.**
  A correction to a correction, or to a diagnosis, has no lifecycle phase of its own, and inheriting
  from an inferred row would regress without a base case. This is the one rule the
  two deferring commands share with the two immediate ones: what a run inherits is
  decided by its `target_command`, never by which of the four is asking.

`role: n/a` is **not a fifth role** — it is the absence of one, recorded rather
than guessed, and aggregation should treat it as unattributed rather than folding
it into `dev`.

**`/vuln`, `/upgrade`, `/docs-profile`, `/docs-serve`, `/harvest-decisions` and `/promote-decisions` emit no cost entry, and that is a decision about what the number is for.** A cost entry measures **AI investment in a product increment**, and the rule is: *a cost entry attaches to a run that advances a PRD- or BRD-scoped artifact — or builds the documentation repository a product is documented in, which is the `docs-workflows` family's unit of attribution and which §8 rung 2 files per docs repo.* That second clause is what `/docs-init` and a standalone `/docs-brand` satisfy, and why they have §7 rows. A CVE remediation, a library version bump, a docs-profile refresh, a dev-server start and a decision harvest into the team architecture knowledge base, or the promotion of its records, advance none — they are noise against a PRD, a BRD or a docs repository, and a metric that averages the two answers a question nobody asked.

**This is restated here because it lived only on the command pages.** `docs/commands/vuln.md` and
`docs/commands/upgrade.md` have carried the reason all along — *"runs outside the PRD pipeline: no
cost-attribution phase and no role"* — but this file, which is the runtime authority, said nothing,
and an audit reading it found two commands emitting nothing and reported a defect. **Adding emission
to them would be the defect.** Note also what is *not* the reason: both run `specs-preflight` and
`commit-artifacts` and do write into `$SPECS_PATH`, with a `NOISSUE …` commit message where no key
resolved — so "nowhere to write it" was never true either.

**Session feedback is a different question with a different answer.** `/vuln` and `/upgrade` do emit
it, and should: `emit-auto` records that *the plugin whose command ran* lacked a capability the run
needed (`references/feedback-emission.md` §6), which is how the family learns about its own gaps. A
vulnerability run surfaces one as readily as a PRD run does, and the size of the work has nothing to
do with it.

**`/prompt-brainstorm` and `/prompt-grill-me` cannot measure their own spend, so
they defer it (§13).** Both cede the session at their Phase 3 — a hand-off to
another skill, or a long interactive grill — so there is no later point at which
the command still controls execution: a cost phase placed there would never run,
and one placed before the hand-off would price the logging prologue alone. The
same constraint already puts their `commit-artifacts` step before the hand-off
rather than at the end (`specs-repo-git.md` §4).

**What the deferral fixes.** Before §13 existed, neither command advanced the §3
checkpoint, so its spend was **not lost but misattributed**: per §3's semantics
activity between commands rolls into the next command's bucket, and a long grill
followed by `/implement` was priced as `implementation`/`dev` — a *larger* error
than a small one would have been, since a grill is expensive. §13 closes that by
splitting the next command's window at the transcript's own record of where each
run began, so the grill is attributed to the phase whose output it corrected and
`/implement` carries only its own work. Both commands therefore have rows in the
table above: they produce a cost entry, written on their behalf by a later run.
**What remains unmeasured** is a session in which no cost-emitting command ever
follows the grill — there the spend stays in §3's ordinary post-last-command
tail, unattributed, exactly as it is for every other command.

**Epic presence is deliberately NOT part of `/release-notes`'s signal** — a PRD can have drafted
Epics while still in PM/PE hands, so keying on Epics would misattribute the PM
run. Cheap to check; matches the real workflow. Still a heuristic —
reattributable at aggregation time (cost < quality).

**`proposal` is its own phase rather than a second `brd-to-prd` one.**
`/prd-proposal` runs on the idea route as readily as on the BRD route, so
attributing its spend to the BRD-to-PRD route would file idea-route spend under a
route that run never touched; and an effort proposal is a commercial activity over
a requirement set rather than a step that advances one. Both proposal commands tag
it, at the `pm` role.

**Keys.** Reuse the run's own resolution — `resolve-address`
(`${CLAUDE_PLUGIN_ROOT}/references/addressing.md` §3) plus the specs-dir matching feedback and
follow-ups already use. Record `prd` always and `epic` when the resolved kind is `epic`.

## 8. Persistence ladder (specs-first; never cwd)

Reuse `feedback-emission.md`'s specs-first ladder, targeting the **`cost/`**
subdir. Walk top-down; stop at the first tier that applies:

**Before tier 1: the run carries `specs_git: misrooted`** (`specs-repo-git.md` §3.1, or `addressing.md` §3 `specs-root-check`'s stop) → **report-only**, as in tier 4, whatever else would apply. `$SPECS_PATH` is set but misplaced, so any write under it lands where `specs-repo-git.md` §2.1's classifier puts it in OTHER, or takes it for an artifact that cannot be staged from `$SPECS_PATH` and that the first run after the variable is fixed would commit in the wrong place. A pending entry written there would never reconcile, and §9 does not run either.

1. `$SPECS_PATH` writable **and** the PRD dir exists (matched by
   `$SPECS_PATH/{specs|specifications|vis}/…/<KEY>{-|_}<slug>/…`) ->
   `<PRD-dir>/dev-workflows/cost/<sid8>.md`. *[primary]*
2. `$SPECS_PATH` writable but no PRD dir (or no key resolved) — two destinations,
   and the documentation branch is tried first:
   - **The run is `/docs-init`, `/docs-audit`, `/docs-brand` on its standalone path, or `/document` in direct mode**, and it resolved the target it writes into (design D19) -> `$SPECS_PATH/documentation/<docs-repo-slug>/dev-workflows/cost/<sid8>.md`, where `<docs-repo-slug>` is the one-segment name `specs-repo-git.md` §2.1 defines for that repo — for direct mode, the write target its own Phase 0 step 3 resolved, which every direct-mode run holds from that step on — cited, never re-derived here, because the staging classifier admits exactly one segment there. **Per docs repo, not one flat bucket**, for the same reason the PRD-directory rung exists for the pipeline: a person documenting two products must still be able to answer what documenting each one cost. The inner `dev-workflows/` names the *family*, not the emitting plugin — `specs-repo-git.md` §2.1 says why — and that section's `<specs-root>/documentation/*/dev-workflows/**` shape is what stages it.
   - **Otherwise** -> **pending** (§9).

   **Why this rung is inserted before pending rather than folded into it.**
   Documentation work frequently has no PRD and never will, so a pending entry
   from such a run awaits a reconciliation that is never coming and accumulates
   forever. §9's opportunistic reconciliation is built for a *keyless* run that
   will later acquire a key; this one will not.

   **The branch names the runs it serves rather than testing "did the run resolve a
   docs repo".** Each of the four works against a target it resolved — a repository,
   or a path that is not one (`specs-repo-git.md` §2.1 names the runs that meet
   that case) — and resolves no PRD folder: `/docs-init`, `/docs-audit` and a standalone `/docs-brand` never resolve one, and
   `/document` direct mode is the mode with no address, so its key is ordinarily
   `null` — where one does resolve a PRD folder, tier 1 takes it first, as it
   would for any run. `/document` in keyed mode resolves a PRD folder and so is
   tier 1's. **Direct mode joined this branch after shipping outside it**, when
   its entries went to pending and reconciled against nothing — exactly the
   problem D19 describes. Pending files it wrote before then stay where they are:
   nothing moves them automatically, and §9 treats them like any other pending
   file.
3. `source = directory` (a passed directory, no `$SPECS_PATH`) -> beside that
   directory.
4. Nothing resolvable -> **report-only** in the run output. **NEVER write into the
   current working directory** — it may be a code repo.

The run never fails, and **the checkpoint (§3) still advances in every tier** so
the next command's window is correct. A write that fails mid-write (read-only
mount / permission) drops to the next tier with the same notice.

## 9. Pending & reconciliation (keyless runs)

When no PRD key resolves and §8 tier 2's documentation branch does not apply,
and the run does not carry `specs_git: misrooted` (§8), write the entry to a pending file:

```
$SPECS_PATH/dev-workflows-cost/pending-<date>-<sid8>.md
```

(same `type: dev-workflows-cost` format; `prd: n/a`).

**`/idea` is not an example of this tier and never reaches it.** The key is a mandatory
argument — Phase 0 refuses the run without one (`IDEA_NEEDS_KEY`) — so an idea run always
resolves a folder and always lands on §8 tier 1. What reaches pending is a run that resolved
no folder at all: `/feedback` or `/prompt` invoked outside any PRD, and `/implement` in
direct mode. Derive the set from §8 tier 2's `Otherwise` branch rather than from any list,
here or elsewhere.

**Opportunistic suggest-and-confirm reconciliation.** Whenever any command
resolves a PRD key **and** pending files exist, the cost phase lists them (each
summarized by date / session / commands / total) and offers to relocate their
entries into `<PRD-dir>/dev-workflows/cost/<sid8>.md`:

- **Same-session `<sid8>` match is pre-selected** as the likely one -> the
  create-in-markdown -> keyed-command flow becomes
  effectively one tap. **An entry charged to `plugin-feedback` is listed but never
  pre-selected:** it is spend on the plugin itself, which a later keyed run in the
  same session does not make that PRD's.
- New-session pending files are listed for the user to pick.
- No match -> leave for manual relocation, or accept the partial loss.
- **Relocation moves, then DELETES.** On a confirmed relocation the pending
  file's entries are appended into `<PRD-dir>/dev-workflows/cost/<sid8>.md` and the
  **pending file is deleted** (move, not copy) so it never re-surfaces. Each
  pending file is relocated atomically; a failed/partial move leaves the file in
  place for a safe retry. Pending files the user *declines* are left in place and
  may be offered again next time (expected — the user chose not to file them).

This is the **only** interactive moment in the cost subsystem, and only when
pending files exist; the cost write itself is always silent.

## 10. Privacy

No user name is written to any cost file — filenames use `<sid8>`, not identity;
entries carry no author. The git commit author remains the only identity layer,
once the engineer commits and pushes the specs — outside this feature's control
and acceptable.

## 11. Caller contract — `emit-cost`

One entry point, called by the twenty-six commands that measure themselves (§1) and by
whichever of them replays a §13 record (never by the two that defer — they call
nothing). Every caller supplies `command`, `phase`, `role` (or the
`inferred` marker — `/release-notes`, `/frames`, the four feedback commands and
`/diagnose-session`), `key` (or `null`), `source`, and `plugin_version`; the four
feedback commands and `/diagnose-session` additionally supply `target_command` — `/prompt` and `/feedback` directly, `/prompt-brainstorm`
and `/prompt-grill-me` through the §13 record a replay reads it from. `emit-cost` does the rest; it NEVER commits, NEVER writes
into a docs/code repo or the current working directory, where it is not the specs repository, and NEVER fails the
run. The cost entry is committed later, once, by the run's terminal
`commit-artifacts` step (`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md`
§4). Cost runs unless the user skipped it — under `--skip-costs` the calling command runs `workflows-core:run-flags`' `skip-cost` in place of this entry point, and `emit-cost` is never called at all.

Inputs:
- `command` — the exact slash-command name (e.g. `/implement`,
  `/document (keyed mode)`, `/document (direct mode)`).
- `phase`, `role` — the §7 labels, or the `inferred` marker for the seven
  commands §7 resolves. They resolve from **different** data, and each must
  therefore be given it:
  - `/release-notes` — resolved from `specification.md` / `design.md` presence
    under the PRD's specs dir. `emit-cost` reads that itself; nothing is passed.
  - `/frames` — resolved from the resolved folder's own `kind` (§7's `/frames`
    inference), re-derivable from the folder `key` names. `emit-cost` reads that
    itself; nothing is passed beyond the `key`.
  - The four feedback commands — resolved from `target_command`, which **cannot**
    be re-derived from disk (it lives in the run's own context). It is passed in:
    directly by `/prompt` and `/feedback`, and out of the §13.1 record for the two
    that deferred.
  - `/diagnose-session` — resolved from `target_command`, which it always passes as
    `n/a`, so it lands on `plugin-feedback`/`n/a`.
- `target_command` — **required for all four feedback commands and for `/diagnose-session`** (supplied
  directly by `/prompt`, `/feedback` and `/diagnose-session`, which always passes `n/a`; read out of the §13.1 record when a
  replay builds the entry for `/prompt-brainstorm` or `/prompt-grill-me`). The
  §7 **row name** of the command whose output is being corrected or remarked on, or
  `n/a`. Note this is the bare row name (`/document`), not the mode-qualified form
  the `command` field above uses (`/document (keyed mode)`) — a qualified value
  matches no row and would silently degrade to `plugin-feedback`/`n/a`. This is the same value the run writes as the feedback entry's `command:`
  field, so the two never disagree. Omitting it is a caller error: §7 has no other
  source for it, and the entry would silently fall back to
  `plugin-feedback`/`n/a`, quietly mis-attributing every correction.
- `key` (or `null`), `source` (`specs | directory | none`).
- `plugin_version` — the version of **the plugin whose command ran**: the one that ships the command named in `command:`, read from **that plugin's** `.claude-plugin/plugin.json` (`python3 -c "import json;print(json.load(open('<path>'))['version'])"`). It is **supplied by the caller and never resolved here**, and the distinction is not pedantic: this reference is read through the loader skill, so a `${CLAUDE_PLUGIN_ROOT}` written *in this file* resolves to the plugin that **ships this reference**, and a run of a sibling's command would file its entry under `workflows-core`'s version — named outright, because every reader of this sentence is in a different plugin from the one it is about. Each calling command already reads the value from its own `${CLAUDE_PLUGIN_ROOT}`, which resolves correctly there, and passes it in. Two things make the emitter's convenience the wrong trade. The field sits beside `command:`, so an entry pairing one plugin's command with another plugin's version describes no artifact that ever shipped. And every entry already on disk carries the version series of the plugin whose command ran — silently re-basing that series onto a different counter destroys exactly the comparability the field exists for. A §13 replay uses the **record's own** `plugin_version` (§13.1), never the replaying run's.

Behavior:
1. Resolve session artifacts (§1) and the price table (§4).
2. Read the §13.1 deferred file, if any. Run `session-cost.py` (§2) with the
   checkpoint (§3), the snapshot (§5) when present, and **one `--claim` per
   deferred record, oldest first**. With no deferred file this is the call it has
   always been and every step below is unchanged.
3. If `unmatched_claims` comes back non-empty, take §13.4 before writing
   anything.
4. Apply attribution (§7) to **this run**, whose spend is the returned remainder;
   build the per-invocation entry (§6); evaluate the §6.1 dominance trigger
   against the built entry and print its warning to the run output if it holds.
   Evaluate it **per built entry**, replayed ones included — §6.1 fires in every
   tier, and a claim dominated by an unpriced model is exactly as misleading as
   this run's would be.
5. Resolve the target via the ladder (§8) — on a keyless run, the documentation
   branch where it applies and pending (§9) otherwise; on a keyed run, run §9's
   opportunistic reconciliation of any pending files.
6. Append the entry (create the file with frontmatter on first write), then
   append one entry per **matched claim** as §13.3 describes.
7. **Write `new_checkpoint` back (§3) in EVERY tier**, including pending /
   report-only, and delete the deferred file.
8. Return the persisted path (or the report-only notice) as the phase's output.

## 12. Maintainer checklist — onboarding a new model generation

A new model generation (e.g. a hypothetical Opus 4.9, or a new Sonnet minor)
touches **two** files that must change together. Skipping one is exactly the
omission that produced the stale "Opus 4.5-4.8" chain comment this reference
and `cost-prices.yaml:22` both used to carry:

1. `${CLAUDE_PLUGIN_ROOT}/references/model-routing/classification.md` §2 — add
   the new model id to the correct fallback chain (Opus / Sonnet), in
   priority order, ahead of the model(s) it supersedes.
2. `${CLAUDE_PLUGIN_ROOT}/references/cost-prices.yaml` — add a matching
   `models:` entry (`input`, `output`, `cache_read`, `cache_write_5m`,
   `cache_write_1h`, USD per million tokens, **permanent/standard rate only**
   — §4) keyed by the same undated model id, and update the chain-summary
   comment above the relevant block (e.g. "Opus 5 and Opus 4.6-4.8 all bill at
   $5 / $25"). **A new id that extends an existing key** (`claude-opus-5-5` extends
   `claude-opus-5`) is priced at the shorter key's rates by the prefix fallback until it
   has its own entry — silently, with no `unpriced-model` note — so for such an id (2)
   is not optional so it still lists every model actually in the chain.

Do (1) without (2) and the new model routes but prices as `unpriced-model`
every run — silently at first, loudly once §6.1's dominance warning fires. Do
(2) without (1) and the price table carries a dead key nothing ever routes to.
After editing either file, `grep` both for the new model id to confirm the
other was updated too.

## 13. Deferred attribution (a command that cedes the session)

Two commands — `/prompt-brainstorm` and `/prompt-grill-me` — hand control to
something else at their Phase 3 and never get it back. Neither can run a cost
phase after its own expensive work, because there is no "after" it controls.
This section is how their spend is measured anyway: **the run that cedes records
what it would have claimed; the next cost-emitting run in the session claims it
on that run's behalf** — short of `--skip-costs`, which writes no entry for it
from either side: a `skip: true` record (§13.1) is carved out and discarded,
and a replaying run under the flag drops the record unreplayed
(`workflows-core:run-flags` §5 step 3).

### 13.1 The intent file

A ceding command writes one record in its **Phase 2**, after the feedback entry
and **before** the terminal `commit-artifacts` step — which stays the last thing
the run does before ceding, exactly as `specs-repo-git.md` §4 requires:

```
~/.claude/dev-workflows/cost-state/deferred-<session_id>.json
```

**A JSON array, and appending to it is the whole point** — a session may cede
more than once, and each cede is a separate measurement. Read the file if it
exists, append this record to the array, and write it back; **create it with a
one-element array when absent, and never overwrite an existing one.** A record
that replaces its predecessor destroys an attribution nothing can reconstruct,
because the earlier run is over.

```json
[
  {"command": "/prompt-grill-me", "plugin": "workflows-core",
   "phase": "inferred", "role": "inferred",
   "target_command": "/document", "key": "PRODUCT-1234", "epic": null,
   "source": "specs", "plugin_version": "1.0.0",
   "ceded_at": "2026-09-01T10:04:00Z", "skip": false}
]
```

No field is a measurement — the spend has not happened yet — and each is here
because a replay cannot re-derive it once the run is over. `command` and
`plugin_version` build the entry (§6). **`plugin` is the plugin that ships the ceding command** — its `name` from the same `.claude-plugin/plugin.json` that ceding run reads its own `plugin_version` from, and necessarily one of the §2 manifest's keys. The pair travels together and describes the **ceding** run, never the replaying one: a replay in another plugin builds the entry from these two, so the entry names the command that ran and the version it ran at. The two commands that write this record ship from the same plugin as this reference, which is why the example above reads `workflows-core` and that plugin's own version. What it protects is **uniqueness, not resolvability**: §13.3 matches a claim to a boundary by bare command name, which is unambiguous only because each command has exactly one home in this marketplace. Recording the home turns that from a property of today's allocation into one the record itself carries, so a command that ever moves cannot silently pair a claim with a namesake. It is not what makes a cross-plugin claim resolve — the §2 manifest already does that, and a replay in any plugin matches without reading this field. `target_command` resolves `phase`/`role`
through §7 at replay time; the two are carried literally as `inferred` because
that is the marker §11's contract takes, and carrying them keeps the record a
complete §11 input rather than one the replay must patch. `key`, `epic` and
`source` choose the §8 tier and fill §7's Keys rule — `epic` set when the
resolved kind is `epic`, `null` otherwise, so a replayed entry is keyed exactly
as a self-measured one. `ceded_at` becomes the replayed entry's `date` and the
timestamp in its `id`, which is what keeps two records replayed by one run from
colliding on §6's uniqueness rule.

`skip: true` is written by a ceding run under `--skip-costs`. The replay (§13.3) still passes the `--claim`, so the segment is carved out of the replaying run's remainder exactly as before; it then writes **no entry** for that claim. An absent field means `false`.

Same home, lifetime and status as the §3 checkpoint beside it — **per-user,
per-session, transient, local, NEVER committed, and safe to delete.**

### 13.2 Where the window is cut

The boundary is not guessed and is not recorded by the ceding run: it is read out
of the transcript, which records every command invocation — a typed one as a
`<command-name>` envelope, a model-invoked one (on a prose request, or one command
running another) as a Skill `tool_use` block.
`session-cost.py` reports them as `command_boundaries`, resolved against the §2
manifest. Four disciplines make that safe, and each exists because its absence was a live
defect:

- **Anchored to the envelope, not to one tag.** Claude Code writes the envelope
  in two orders — built-ins name-first (`<command-name>…`), plugin commands
  message-first (`<command-message>…<command-name>…`) — so a match anchored on
  `<command-name>` alone sees **no plugin command at all** and the feature is
  silently inert. Anchoring on either opener keeps the property that matters: the
  envelope must *start* the message, so the same marker text quoted inside prose
  or a pasted file is not an invocation.
- **Namespaced, and both halves resolved against the §2 manifest.** A boundary is accepted only as `<a plugin of this marketplace>:<that plugin's own command>` — the namespace must be a key of the manifest and the name must be in *that key's* list. Two facts force the namespace requirement. Claude Code's built-ins are written **bare**, and several of them — `/upgrade`, `/feedback`, `/statusline` and `/release-notes` — collide with commands plugins here also ship, so accepting a bare name mints a boundary from a built-in nothing here ever ran. And another marketplace's `/superpowers:implement` must not read as this family's `/implement`, which is what discarding the namespace would do. This is `specs-repo-git.md` §3.5's `branch-key` discipline applied to a transcript: resolve against the set you hold, never parse.
  **Since PS3 the manifest governs claiming only; cutting needs no manifest at all.** A command from a marketplace outside this one now ends the open window — its spend is its own — while remaining unclaimable, because a claim may only match a manifest name. Before that split a foreign invocation between a cede and its replay minted nothing and its spend was absorbed into the claim, which is the same conflation described just below, one marketplace further out. **What widened at the split is which namespaces are accepted, and a namespace *list* would not have been enough.** The rule used to be `<this plugin>:<this plugin's command>`, resolved against whichever single plugin supplied the command set — so once the family spanned several plugins, a **sibling's** invocation between a cede and its replay was invisible, and §13.3 gives a claim the segment up to the next boundary *of any kind*. The claim then swallowed the sibling's run whole: reproduced at 9000 tokens claimed where 5000 was correct, taken silently out of the replaying run's own remainder. Both halves are resolved at once, which is why widening only the namespaces still rejects `/dev-workflows:vuln` and still mis-measures; the manifest widens both, and the two safety properties above are asserted against it rather than argued. It errs safe either way — an invocation missed becomes an unmatched claim, reported and dropped (§13.4), where a phantom one would silently file one command's spend under another's phase.
- **Matched by name, never by position.** See §13.3.
- **Both invocation shapes are read, because only one leaves an envelope.** The
  envelope above is emitted when the user **types** the slash command. When the model
  reaches the command through the **Skill tool** — on a prose request, or one command
  running another — the invocation appears only as an assistant `tool_use` block named
  `Skill` whose `input.skill` is the command — no user message, no envelope — so a
  detector reading user messages alone misses the whole invocation, and §13.3 hands the
  preceding claim the segment running to the next boundary of any kind, i.e. straight
  through it. Measured: a typed grill command followed by two prose-invoked runs, neither
  cutting the window, and the grill's claim absorbed both. Typed-only commands (flagged
  `disable-model-invocation: true`) changed what reaches this path, not the path: the
  Skill tool refuses a flagged command unless the user typed `/<name>` in that turn's
  message, and a call the tool refused — its result an error — cuts nothing; a command
  left unflagged still arrives this way, from a caller or on a prose request. **The Skill half resolves against
  the manifest where the typed half does not** — a deliberate asymmetry. The typed half
  is permissive because a user can only type a real command, so a name it cannot see
  is a swallowed boundary at no cost. A Skill call is different in kind: commands
  dispatch non-command skills constantly (model-routing, the reference loader, several
  times a run), and cutting on those would shatter one command's window into spurious
  segments — worse than the miss. Both halves are asserted in the selftest so a later
  reader cannot "harmonise" them and reintroduce one of the two defects.

`session-cost.py --selftest` covers each, paired with the broken implementation it
exists to catch.

### 13.3 The replay

`emit-cost` step 2 (§11). **No deferred file ⇒ nothing changes**; the twenty-six
commands that measure themselves (§1) never take this path.

Otherwise the run passes one `--claim <command>` per deferred record, oldest
first, and the script partitions the window:

- Each claim is matched to a boundary **by name**, scanning forward. It gets
  exactly the segment from its own boundary to the **next boundary of any kind**.
- Everything else — including whole segments belonging to commands that emit no
  cost entry — stays in the **remainder**, which is this run's own spend, exactly
  as it would have been without any of this.

**Matching by name is the whole point, and positional pairing is the trap.** A
window routinely holds boundaries no claim corresponds to: `/vuln`, `/upgrade`,
`/docs-profile`, `/docs-serve`, `/statusline`, `/harvest-decisions` and `/promote-decisions` are real commands that
emit no cost entry,
and an interrupted run leaves a boundary too. Pair the
k-th claim with the k-th boundary and a single `/vuln` in the window shifts every
claim by one — filing a security run's spend under a PRD lifecycle phase, which
is the exact misattribution this section exists to remove.

For each matched claim whose record does not carry `skip: true`, build the entry (§6) from its segment, taking
`phase`/`role` by resolving that record's own `target_command` through §7, and
dating it `ceded_at` (§13.1). Append it through the §8 ladder using the record's
own `key`, `epic` and `source` — which may differ from this run's. A matched claim whose record carries `skip: true` builds no entry: its segment is still carved out of this run's remainder by the partition, and then discarded.

The partition is **exhaustive and disjoint at the token level**: every usage
record lands in exactly one bucket, so the claims' tokens plus the remainder's
are exactly those of the unsplit window. Dollars are rounded per bucket, so the
summed dollar figures may differ from the unsplit total by a fraction of a cent —
an artefact of rounding, never lost spend.

**A deferred entry is committed by the run that replays it**, through that run's
own terminal `commit-artifacts`. The ceding run's `commit-artifacts` has long
since finished, which is why it could never have committed its own.

### 13.4 What this does not do

- **It never invents a boundary.** A claim matching no boundary comes back in
  `unmatched_claims`. Its entry is **not written** — nothing is guessed onto a
  neighbouring boundary — and its spend simply stays in the remainder, where it
  would have been anyway. The run reports one line naming the command whose
  attribution was lost, and the deferred file is still deleted: the checkpoint has
  advanced past that boundary, so no later run could ever match it, and leaving
  the file would re-print the same line every run for the rest of the session.
  Nothing is lost that was not already lost; only the attribution is.
- **It does not split Option B.** The statusline cross-check (§5) measures whole
  renders and cannot be apportioned, so a window in which any claim **matched**
  omits `cost_statusline_usd` rather than over-reporting it against the remainder.
  A window whose claims all went unmatched was never split, so it keeps the
  field.
- **It does not rescue a session that ends there.** With no later cost-emitting
  command the spend stays in §3's post-last-command tail, unattributed — the same
  tail every command already has. A resumed session that starts a new transcript
  is this case: the new session has its own `deferred-<session_id>.json`, so the
  old record is never read again and is safe to delete.
- **It is not a general mechanism for skipping the cost phase.** A command that
  *can* measure itself must — unless the user skipped it (`workflows-core:run-flags` §5); deferral exists only for a run that provably cannot,
  and adding a third deferring command means showing that its Phase 3 cedes the
  session too.

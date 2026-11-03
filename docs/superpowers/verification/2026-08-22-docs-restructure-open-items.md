# dev-workflows docs restructure — open items

**Branch:** `iv-gu/docs-restructure` · **Version:** 2.57.0 · **State:** all gates pass (`check-docs.sh --selftest` at 15 cases, `check-docs.sh --root .`, `check-id-grammar.sh` both modes, `validate-catalog.py`, spec-ID census), not yet pushed.

This file was written before compaction to carry the review's findings across it. **Every item below has now been closed** in the fix wave of 2026-08-22 — the record is kept so the reasoning, and the two rejected items, survive the branch.

## A. Cosmetic minors — six, all closed

| # | Item | Disposition |
|---|---|---|
| 1 | `docs/workflow.md`'s Jira-status bullet paraphrased the retired README with no primary source cited | **Fixed** — now cites `references/workflow-states.md`, which states the same thing outright and stores no status of its own. |
| 2 | `docs/reference/environment.md` attributed "the bookkeeping is not committed" to `specs-preflight` | **Fixed** — the commit is the terminal `commit-artifacts` step's; both share the §3.1 writable gate, which is why the consequence was true and only the attribution loose. |
| 3 | `docs/commands/release-notes.md`'s `## Example` read dev-first | **Fixed** — the PM run and the dev re-run now get equal treatment, matching `## Who runs it`. |
| 4 | `docs/commands/ready.md:15` omitted the single-Epic case its own parenthetical states | **Fixed** — the two commands part company as soon as spec'd Epic subfolders exist at all. |
| 5 | `docs/commands/ready.md:71`'s See-also phrasing needed a second read | **Fixed** — recast as "the opposite extreme on the same gate". |
| 6 | The plugin README's pitch enumerated phases, omitting `/epics`, `/release-notes`, `/ready` | **Fixed** — names the spine explicitly and hands completeness to the table below it. |

## B. Findings that had no durable record before this file — all closed

| # | Item | Disposition |
|---|---|---|
| 7 | Follow-ups had two "primary location" answers: `$SPECS_PATH` in `workflow.md` + `environment.md`, the vault in `follow-ups.md` | **Fixed** — `follow-ups.md` is the authority; both other pages now name the vault first and point at the full ladder. |
| 8 | `docs/commands/ready.md`'s collapsed node `p678` drifted from the source headings | **Fixed** — relabelled verbatim, matching `commands/ready.md`'s `## Phase` headings and the equivalent node in `epics.md`. |
| 9 | `docs/workflow.md`'s diagram showed `/epics → /specify` as the only path into `/specify` | **Fixed** — `createvi -->\|VI-level spec\| specify` added. |

## C. Gate follow-ups — all closed

| # | Item | Disposition |
|---|---|---|
| 10 | The skills sub-check's direction 2 had no selftest case | **Fixed** — a documented-but-nonexistent skill case added; the selftest went 11 → 15 cases (this one plus three for the new check 8). |
| 11 | The spec-ID census was constraining the corpus rather than describing it | **Fixed** — the README clause held solely to keep the counts steady is now plain English; `scripts/spec-id-baseline.txt` regenerated at −1 on each of `[Uxx]`/`[ACxx]`/`[TCxx]`, with the reason in its header. Verified before regenerating that no concrete `[U01]`-style identifier moved. |
| 12 | D2's fix was defended by no persisted gate | **Fixed** — `check-docs.sh` **check 8**: every command handing `emit-cost` a fixed `phase`/`role` pair has a matching `references/cost-emission.md` §7 row, and no §7 row names a command that emits no fixed pair. Proven to fire in all three directions (missing row, drifted value, orphan row) on both the real tree and the fixture. |

## D. Owner decisions — settled 2026-08-22

**D3 and D6 both resolve into one change: the role vocabulary is four roles, not five. `team` is folded into `dev`; `QA` is retired outright.**

Ivan's ruling: `dev` and `team` denote the same thing in this workflow, `QA` "looked weird", and a role carrying a single command reads as an aside rather than a lane. Keep whichever name is used most.

`dev` is that name, on two grounds:

1. **Usage.** `dev` already labelled four of the five delivery-lane call sites (`/design`, `/implement`, `/document`, and `/release-notes`'s inferred late run) against `team`'s one (`/ready`). The same test Ivan applied to `QA` — one command looks like an aside — applies to `team`.
2. **Collision.** `team` is a live identifier elsewhere in the plugin: `jira-reader` emits a per-Epic `team` field verbatim from Jira Epic frontmatter (`[DTT] Team Storage`), consumed by `epic-writer`, `epic-reviewer`, and `references/pre-lint.md`. Two meanings of one word in one plugin is the kind of thing that silently corrupts a later sweep. Every `team:`-the-Jira-field site is deliberately untouched.

Carriers changed: `references/cost-emission.md` §7, `references/workflow-states.md` (both ladders), `references/next-phase-offer.md`, `references/session-hygiene.md`, six command files (`ready`, `document`, `implement`, `design`, `create-ard`, `specify` — `emit-cost` calls, next-phase offers, `/rename` lane tags, one `choices:` option), and eight docs pages — including the plugin's only Mermaid carrier of a role label, `docs/workflow.md`'s `QA["Team — verification & gates"]` subgraph, now merged into `DEV`; the 13 command-page diagrams label phases, not roles, and needed no change. Nine cost phases, unchanged — only the role label moved. Check 8 now defends the `§7`-vs-command half of this.

## E. Not to be "fixed" — rejected findings, recorded so they are not re-raised

1. **`ROOT` and `OWNER_REPO` in `check-docs.sh`'s `RUNTIME_VARS`.** The final review called them dead exclusions. They are live and correctly excluded: `$ROOT` is read at `hooks/changelog-owners-reminder.sh:10`, `$OWNER_REPO` at `references/phase-handoff.md:70,166,168`. One is a hook-local shell variable, the other a reference template placeholder; neither is user-settable. **Do not remove them.**
2. **A reviewer's claim that `CLAUDE.md`'s taxonomy "uses QA throughout".** It contains zero occurrences of "QA". Acting on that finding would have made twelve consistent pages wrong to match one.

## Carried forward, outside this branch

The role collapse touches files that are `cp`-ported to the internal edition and hand-adapted for `ihudak-copilot-plugins`. Both editions still carry the five-role vocabulary and the retired `QA` label wherever their own copies of these references live. The port is its own change — see the cross-repo porting notes before starting it.

**Tracked since 2026-11-03 as E5 in `docs/superpowers/to-fix.md`** (batch B29), which is where this port's status is kept.

---

## F. Gate findings — all fourteen built, none deferred

From the adversarial gate review (2026-08-22). This section went through three states, and the
history is the point.

**First pass:** six items deferred as "latent — nothing in the tree triggers it today."
**Second pass:** challenged, the grounds were re-derived instead of restated. Two were not latent
at all, only unbuilt, and were built (check 9, and the `RUNTIME_VARS` tripwire).
**Third pass:** challenged again — *"a bug that isn't from today's work is still a bug; deferred
for whom, and when?"* — the remaining four had no owner and no trigger date, which makes "deferred"
a synonym for abandoned. They are now fixed. The real reason they were deferred was that the run was
optimising for closing out, not that the fixes were expensive: **three of the four were one to three
lines.**

Worse, the test itself had been wrong. Three of the four were not dormant hazards but gate bugs that
**fail on correct content** — legal CommonMark that would have turned the build red for no reason.
That is not latent; it is a landmine with a trip-wire pointed at the next author.

| Was deferred | What it actually was | Fix |
|---|---|---|
| `slugify()` deletes non-ASCII letters | A **correct** `#über-config` link failed check 2 — the letter was stripped, yielding `ber-config` | Slug generation moved to `python3`, which casefolds and classifies Unicode **regardless of locale**. The first attempt at this only probed for a UTF-8 locale and *announced* the gap when none was found — a disclaimer, not a fix, since the gate still mis-resolved. `python3` is already a hard requirement of this repo's CI (`validate-catalog.py` runs in the same job), so it costs no new dependency. Verified byte-identical to the old path across all 292 headings in the tree, and verified correct under a forced `LC_ALL=C` |
| No `-1` duplicate-heading disambiguator | A correct link to the second `## Notes` failed check 2 | One `awk` line: first occurrence bare, then `-1`, `-2` |
| Check 1 rejects `[x](f.md "Title")` / `[x](<f.md>)` | Legal CommonMark resolved as a literal path and failed | Two `sed` clauses in the extractor |
| Check 3's single reachability root | A page linked only from the plugin README was a **false orphan** | Seed the frontier with the plugin README too |
| Check 6 and `~~~` fences | A table inside a `~~~` fence was measured and flagged | Extend the fence pattern |
| Check 6 skips indented rows | An over-long cell in an indented row was **never measured** — the one vacuous-pass of the six | `^[[:space:]]*\|` |

All six legal constructs now live in the fixture, so the standing pass-case proves the gate accepts
them; five new fail-cases prove it still rejects the broken forms. Selftest: **33 cases, 9 checks.**

**Nothing from the review is outstanding.**

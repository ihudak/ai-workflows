# GIT-G1 Part 2, batch 2a — start and end — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every command's specs-repository start (`specs-preflight`) and end (`commit-artifacts`) runs in `workflows-core`'s `specs-git.py` through one new skill, `specs-git`, with the state the two share kept in a record that survives compaction, so no run reads the 163 KB `specs-repo-git.md` to run either.

**Architecture:** `specs-git.py` gains four subcommands — `start`, `end`, `replay` and `declined` — beside Part 1's primitives, and two helper modules beside it: `specs_git_state.py` (the per-session record) and `specs_git_lines.py` (every notice and outcome line as `specs-repo-git` writes it, pinned to the reference's text by the selftest). It imports `session-branch.py` for the mode, the overlay, the session-branch commit, the bounded git call and the replay. A new skill, `workflows-core:specs-git`, is the only way a command reaches the script; the `reference` loader routes every existing `specs-repo-git specs-preflight` and `specs-repo-git commit-artifacts` request to it, and `workflows-core`'s six commands call it directly. The reference keeps its step-by-step text in 2a, marked as the rule the script follows and the fallback where it cannot start.

**Tech Stack:** Python 3 standard library; git ≥ 2.38 (the replay and the session-branch merge need `merge-tree --write-tree`, as before); the repository's gate chain (`.github/workflows/validate-catalog.yml`).

**Spec:** `docs/superpowers/specs/2026-11-08-git-g1-shared-specs-git-design.md` (§4, §5.1, §5.3, §5.5, §7 Part 2, §8, §10). Evidence: `docs/superpowers/specs/2026-11-08-git-g1-evidence/contract.md` §0, §1, §2, §6, §7, §8; audit-A §2 (items 1, 2, 4, 12–15), audit-B §13(2) (N9, N11–N14, C4, C5), audit-C (2) (N8, N9, the tail profiles). The reference the script implements: `plugins/workflows-core/references/specs-repo-git.md` (SRG below) §1–§8. Part 1, the style this plan follows: `docs/superpowers/plans/2026-11-08-git-g1-part1-script-core.md` and its record `docs/superpowers/verification/2026-11-08-git-g1-part1.md`.

## Global Constraints

Carried verbatim from Part 1:

- Python 3 standard library only, as `session-branch.py`, `lineage.py` and `bounded.py` (design §3).
- One JSON object on stdout per call; exit 0 when it ran, whatever it found; exit 2 when it could not run, printing exactly one `specs-git: not run (<reason on one line>)` line on stderr, never a traceback — `session-branch.py`'s contract (`main()`, `Parser.error`).
- `--specs <root>` must be the repository's top level (`rev-parse --show-toplevel`, compared by `realpath`), as `session-branch.py` checks; `owner-repo` alone takes `--repo <path>` instead, since it also serves non-specs repositories.
- The classifier is `session-branch.py`'s `classify`, imported, never copied — "one implementation" (design §2 goal 1). Same for `push_scope`, `mode` and `git`/`text`/`nul_list`.
- New prose is never hard-wrapped (`workflows-core:prose-formatting`); the references' existing hard-wrapped blocks keep their own style where edited in place.
- `plugins/workflows-core/reference-parts/` is regenerated with `python3 scripts/reference-parts.py generate`, never edited.

Added for 2a:

- **The `--specs` exception.** `start`, `end` and `specs-root-check` take `--specs "${SPECS_PATH-}"` as the run holds it — empty meaning unset — because their first job is SRG §3.1's gate, which reports a value that is no repository or not its top level; every other subcommand keeps the top-level rule. `declined` takes no `--specs`.
- **Exit 2 means nothing was done** (ruling R2). `start`, `end`, `declined` and `replay` exit 2 only before their first write, and the state record is written immediately before the first action that changes a repository (commit, push, switch, pull, branch deletion, refusal record, any session-branch call); a fetch may precede it. After that, every outcome is exit 0 JSON, an unexpected exception included (`error` set, one line). A usage error's line begins `specs-git: not run (usage: ` — `Parser.error` gains that prefix.
- **Imports, never copies**, extended: `sb.commit`, `sb.lift`, `sb.put_back`, `sb.mode`, `sb.replay`, `sb.Partial`, `sb.refusal_record`, `sb.git_bounded`, `sb.KILL_AFTER`, `sb.rev`. The two new modules are imported beside `sb`; any of the three failing to load is one `not run` line and exit 2.
- **Bounded calls.** Every git call that can hang — `fetch`, `pull`, `push`, `ls-remote` — runs through `sb.git_bounded(root, seconds, …)` (process-group kill, `workflows-core:bounded-run`'s mechanism): fetch, pull and push 60 s, `ls-remote` 30 s. `start` keeps a budget of 480 s per call (`--budget`, default 480) and stops before a capped call that could cross it, returning `next` (Task 7). The skill runs `start` and `end` with a Bash timeout of 600000 ms and `replay` with 420000 ms (SRG §4 step 6).
- **The script asks nothing and decides no wording the reference does not fix.** Every line it prints is a template in `specs_git_lines.py` that the selftest finds, verbatim, in SRG or `workflows-core:addressing` §3 (Task 3); a line SRG left unworded gets its wording written into SRG first (Task 3).
- **The selftest touches no real home and no real session.** It pops `CLAUDE_CODE_SESSION_ID` and `GIT_USER_INITIALS` from its own environment and gives every scenario a `HOME` and a session id under its temporary directory, as Part 1's selftest pins `GIT_CONFIG_GLOBAL`.
- **Budgets**, measured as Python `len(open(f, encoding='utf-8').read())`: every `.claude/rules/*.md` under 20,000, `CLAUDE.md` under 36,000 — after every task that touches either. Re-derive every number written into `CLAUDE.md` or a rules file against the tree, with the command beside it (`CLAUDE.md` § Editing discipline).
- **Gates**, run as one `&&` chain and read by its own printed status, from the worktree root:

```bash
python3 scripts/validate-catalog.py --selftest && python3 scripts/validate-catalog.py && ./scripts/check-id-grammar.sh --selftest && ./scripts/check-id-grammar.sh --root . && ./scripts/check-id-grammar.sh --baseline && ./scripts/check-docs.sh --selftest && ./scripts/check-docs.sh --root . && python3 scripts/reference-parts.py --selftest && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && python3 scripts/reference-parts.py check-branch-check && npm ci --prefix scripts/mermaid --ignore-scripts --no-audit --no-fund && node scripts/mermaid/check-mermaid.mjs --selftest && node scripts/mermaid/check-mermaid.mjs --root . && python3 plugins/workflows-core/scripts/session-cost.py --selftest && python3 plugins/dev-workflows/scripts/secret-scan.py --selftest && python3 plugins/dev-workflows/scripts/run-state.py --selftest && python3 plugins/dev-workflows/scripts/pieces.py --selftest && python3 plugins/product-workflows/scripts/architecture-harvest.py --selftest && python3 plugins/product-workflows/scripts/promotion-signals.py --selftest && python3 plugins/product-workflows/scripts/proposal-record.py --selftest && python3 plugins/product-workflows/scripts/ledger-evidence.py --selftest && python3 plugins/product-workflows/scripts/bundle-scan.py --selftest && python3 plugins/security-workflows/scripts/register.py --selftest && python3 plugins/docs-workflows/scripts/key-discovery.py --selftest && python3 plugins/workflows-core/scripts/bounded.py --selftest && python3 plugins/workflows-core/scripts/lineage.py --selftest && python3 plugins/workflows-core/scripts/tree-snapshot.py --selftest && ( ok=1; for n in bounded.py tree-snapshot.py; do for d in plugins/*/; do if [ -f "$d/scripts/$n" ] && ! cmp -s "plugins/workflows-core/scripts/$n" "$d/scripts/$n"; then ok=0; fi; done; done; [ "$ok" = 1 ] ) && python3 plugins/workflows-core/scripts/session-branch.py --selftest && python3 plugins/workflows-core/scripts/specs-git.py --selftest; echo "EXIT=$?"
```

  `EXIT=0` is a pass. Where `scripts/` is unchanged, `check-docs.sh --selftest` may be skipped locally, as Part 1 did; it is never skipped in the final run.
- **Identity quarantine and vendor neutrality** (`check-docs.sh` checks 10, 13, 14, 19): no new text names a tracker, the organisation this plugin came from, or, on a `docs/` page, the marketplace; no `§`, decision id or `<plugin>:<reference>` token on a `docs/` page (check 25); no table cell above 200 characters (check 6).
- **Commits.** Immediately before each: `git branch --show-current` prints `feat/git-g1-part2a` (the worktree `/workspace/.worktrees/git-g1-part2a`; never `git checkout` in `/workspace/ai-workflows`). Each message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. No push.
- **Only `workflows-core` changes** (ruling R7 confirmed below): no file under `plugins/dev-workflows`, `product-workflows`, `docs-workflows` or `security-workflows` is edited.

## Review Focus

1. **Two sessions on one specs repository at once, and one conversation compacted between its start and its end.** Each `end` must read its own session's record and no other; a reasonable person expects run A's misrooted flag never to skip run B's commit, and B's guard block never to print under A's line. Test in Task 5 (`e_two_sessions`).
2. **A stale record of the same command, left by a run the user interrupted, then a new run that stops before its preflight.** `end --no-preflight` must ignore and remove it, and a new `start` must replace it; the stale run's flags must never decide the new run's commit. Test in Task 5 (`e_stale_no_preflight`) and Task 7 (`t_replaced`).
3. **A `$SPECS_PATH` with a trailing slash, through a symlink, relative, nonexistent, holding a space, or taken from the *Set SPECS_PATH* answer.** The `Environment:` line the script prints must equal, byte for byte, what `session-hygiene` §7's Bash call prints in the run's own shell — otherwise every later `env-check` reads *Environment changed* and the run commits, hands off and records nothing. Test in Task 4 (`g_env_line_equal`).
4. **A declined deliverable the run later commits (the consent asked again and answered *Yes*), and a declined set of several paths with spaces or non-ASCII names.** The `Specs repo:` line must name only what is still uncommitted, in `phase-handoff` §4.1's `<artifacts>` form. Test in Task 5 (`e_declined`).
5. **A preflight with several plugin branches each holding pushable commits, and a slow origin.** `start` must stay inside its Bash call's timeout and must not lose or repeat a branch's push between calls. Test in Task 7 (`t_budget_resume`).

## Rulings this plan takes

Each is the plan's own call where the brief left it to the builder; the cost of each if wrong is in the final report.

- **R5 — the record's key and home.** One file per Claude Code session, `~/.claude/dev-workflows/specs-git/<session id>.json`, the session id being the harness's `CLAUDE_CODE_SESSION_ID` — the same value `workflows-core:cost-emission` §1 derives as `session_id` from the transcript's name (checked: the variable equals the transcript basename), read directly instead of by scanning transcripts. The family already keeps per-session state there (`cost-emission`'s `~/.claude/dev-workflows/cost-state/<session_id>.json` and its §13.1 deferred file). **Not the specs repository's git directory**, the design's "obvious candidate" and R6's premise, for three measured reasons: SRG §3.1's gate fails exactly where a git directory is missing or unwritable (unset, not a repository, a read-only mount), yet a not-a-repository `$SPECS_PATH` with a `specs-root-check` signal sets `specs_git: misrooted`, whose notice `end` must repeat; a resume in another container points `$SPECS_PATH` at another repository, where a record in the first one's git directory cannot be found; and nothing outside every repository is ever staged. **Why it is safe:** the session id survives compaction, which the conversation's text does not; one file per session keeps two sessions on one repository apart; `run-state.py remove` deletes only files in the code repository's git directory, so the record outlives it; a nested run (`/brd-split`'s *Ground now* starting `/prd-ground`, one child after another) starts only after its parent's `end`, which SRG §4's cede-control exception places before the hand-off, so each child's `start` opens a fresh record; an `--inline` run calls neither entry point. Where `CLAUDE_CODE_SESSION_ID` is unset or malformed, `start`, `end`, `declined` and `replay` exit 2 before any write and the run takes the reference's prose, as it does today.
- **Record lifecycle.** `start` opens a fresh record, setting aside whatever the session held (reported as `replaced`), save `--rerun` and `--resume`, which continue the run's own; `declined` adds paths, creating a record marked `started_by_script: false` where none stands; `end` reads it and removes it as its last act, or `replay --for end` does where `end` handed it a replay.
- **R3 — the replay's own call.** A non-fast-forward rejection is never replayed inside `start` or `end`. `start` records each rejected branch in the record's `pending` list, in the order met, finishes §3.4 (the settle loop included), and returns `next` naming the first replay; each `replay --for start` call returns `next` naming the following one, and the last names `start --resume`, which runs §3.5 and the session-branch mode's closing `put-back`. `end` returns `next` naming `replay --for end`, which prints the `Specs repo:` line. `next` is `{"run": "<the exact shell line>", "timeout_ms": 420000|600000, "on_timeout": "<shell line>"|null}`; the skill runs `next.run` verbatim as a Bash call of its own, and `next.on_timeout` (`replay … --timed-out`) where the harness ends that call. **Cost:** the current branch's replay line prints after the settle loop's lines rather than before them; no rule reads that order.
- **The start budget.** 480 s per call; before each capped call `start` checks that the elapsed time plus the cap plus `sb.KILL_AFTER` stays inside it, and otherwise saves its stage and returns `next` naming `start --resume` (timeout 600000 ms). A call always makes at least one capped call before it may stop, so every call makes progress.
- **Wording SRG leaves free** is fixed in SRG by Task 3 (the B4 report, the non-repository and below-top-level notices, the offline line, B2's success line, the failed pull and failed deletion lines, the re-run's failed switch back, the `Specs preflight:` form of *push FAILED* and of a session-branch call that could not run, and the two "stopped early" lines), then pinned.
- **D2 and the declined append.** On `phase-handoff` §4.3's option 2 or 3 the producer runs the skill's `declined` with the handoff's `deliverable_paths`; `end` appends `; the deliverable at <path> remains uncommitted, as you asked` for the recorded paths `git status` still lists, `<path>` written as `phase-handoff` §4.1 writes `<artifacts>` (three or fewer comma-separated, else `<n> files under <dir>`). A path the run committed after all — a consent asked again and answered *Yes* — drops out.
- **Citations.** A citation of `specs-repo-git` §3 to §8 in a run that calls the skill is served by the skill's text and the script's output; only the skill's own fallback and a step a command runs by hand from the reference (its own session-branch `commit`, `lift` or `put-back`; a commit into a docs repository in §4 step 4's form) read the reference whole. Without this, the many restated wrappers that cite §3.2, §3.3, §5 or §6 would each reload the 163 KB file for a lookup, as lean context D measured for `phase-handoff`'s citations (`docs/maintainers/rationale.md`, *Why a citation of a section the file holds reads the file*).
- **The loader routes by a Skill call**, `Skill(skill: "workflows-core:specs-git", args: "start" | "end")`, never by reading the skill's file, so `${CLAUDE_PLUGIN_ROOT}` in the skill expands to `workflows-core`'s root.
- **The `Environment:` line is printed by the script**, which runs `session-hygiene` §7's Bash call character for character (pinned), so a run no longer loads `session-hygiene env-check` to print it.
- **Inputs a command's text never states** reach the script as options the skill defines: `--command`, `--key`, `--commit-key`, `--register-rebuild`, `--rerun`, `--no-preflight`, `--misrooted-stdin` (a misrooted notice set outside the script — `specs-root-check`'s stop, `env-check`, `session-hygiene` §6's *Stop* — on stdin) and `--session-branch-created` (a creation by a session-branch call the command made itself).
- **`end` with no record** (a run that stopped before its preflight, or `--no-preflight`) runs SRG §4 step 1's no-preflight path, resolves `<default>` and `<default-ref>` by §3.2's name and ref rules with no fetch, resolves session-branch mode with no second fetch, and **also re-runs §3.1's placement tests** (`specs-root-check` and the below-top-level test), taking the misrooted outcome where one fires: a named behaviour change, since a run that stopped before its preflight would otherwise stage top-relative paths from below the top level, which `git add` refuses, or commit into a repository the preflight would have flagged.
- **B2 prints a line when it acts**, §3.4's `Specs preflight: deleted merged <branch>`; SRG §3.5 says so after Task 3.
- **The G2 variant for a direct `/implement` run from inside the specs repository** is chosen by the script: `--command /implement` and the current directory's top level equal to `$SPECS_PATH`'s.
- **`--rerun`** carries the earlier start's flags (OR), its `-D` advisories and its B4 branch; the guard block repeated at the end is the last one fired.
- **§5's `<path list>`** is comma-separated on the *Found* line and shell-quoted, space-separated, on the *Fix* line; a variant line SRG gives in prose (G2's session-branch and direct-`/implement` variants) is rendered unwrapped on its one line.
- **File layout.** Orchestration and its selftest stay in `specs-git.py` (the `session-branch.py` precedent); the record and the templates are two modules beside it, so the two pure concerns are tested and pinned on their own.
- **R6, confirmed against `/implement`'s text.** Its terminal paragraph reads `specs_git`, `key` and `session_branch_created` from run-state before `run-state.py remove` and then requests `commit-artifacts`; the loader routes that to `end`, which reads `specs_git` from its own record and takes `key` and `session_branch_created` as `--commit-key` and `--session-branch-created`, both of which the run holds at that point. The record is outside every repository, so the removal cannot reach it. **One thing does not change in 2a:** on a direct run from inside the specs repository in session-branch mode, `/implement`'s own `lift`, `put-back` and `commit` calls (its Phase 1.4, Pre-Phase 3 and Phase 4.6) are by hand from SRG §8.2–§8.3, so such a run still reads the reference for them — the `dev-workflows` batch's preparation (design §6).
- **R7, confirmed.** No command outside `workflows-core` needs a change: their loader requests are routed; `/security-workflows:scan`'s `register_rebuild` path is already expanded in its command body; `/document` and `/release-notes` name their re-run; `/promote-decisions` reaches the preflight through `workflows-core:architecture-promotion` §1 step 4, which Task 9 edits.

## Out of scope (later batches)

The per-command wrapper slimming (2b onward, one plugin or command family per batch, `/implement`'s preparation in the `dev-workflows` batch); retiring SRG's step-by-step text (the batch that switches the part's last command); `handoff-to-main`, `require-on-main`, `branch-check` and the per-phase `inputs_read` call (Part 3); the tail profiles as skill calls and the rest of the end-of-run sequence (TAIL-G1). The record holds the `Environment:` line already, unread in 2a, for TAIL-G1's `env-check`.

## File map

| File | Change | Task |
|---|---|---|
| `.claude/rules/plugin-authoring.md` | Create: `CLAUDE.md`'s taxonomy and Karpathy sections, moved | 1 |
| `.claude/rules/workflows-core-handoff.md` | Create: `workflows-core-git.md`'s `phase-handoff` paragraph, moved | 1 |
| `CLAUDE.md`, `.claude/rules/workflows-core-git.md`, `workflows-core.md`, `gates-validate-catalog.md`, `security-workflows.md` | Relief and pointers (1); skill and loader facts (10) | 1, 10 |
| `plugins/workflows-core/scripts/specs_git_state.py` | Create: the record | 2 |
| `plugins/workflows-core/scripts/specs_git_lines.py` | Create: templates, `fill`, pins | 3 |
| `plugins/workflows-core/scripts/specs-git.py` | Modify: imports, `declined`, `specs-root-check`, `end`, `replay`, `start`, mode, selftest | 2–9 |
| `plugins/workflows-core/references/specs-repo-git.md` | Fixed wording, D2 (3); banners, caller contract, state record (9) | 3, 9 |
| `plugins/workflows-core/references/phase-handoff.md` | §4.3: the `declined` call on options 2 and 3 | 9 |
| `plugins/workflows-core/references/session-hygiene.md`, `architecture-promotion.md` | §7 note; §1 step 4's call | 9 |
| `plugins/workflows-core/skills/specs-git/SKILL.md` | Create | 9 |
| `plugins/workflows-core/skills/reference/SKILL.md` | The routing paragraph | 9 |
| `plugins/workflows-core/commands/{feedback,prompt,prompt-brainstorm,prompt-grill-me,frames,diagnose-session}.md` | The start and end call phrases | 9 |
| `plugins/workflows-core/reference-parts/**` | Regenerated | 3, 9 |
| `plugins/workflows-core/docs/**`, `plugins/workflows-core/README.md` | The skill's docs entry, counts | 10 |
| `docs/maintainers/rationale.md` | A section for R5 | 10 |
| `.github/workflows/validate-catalog.yml` | The specs-git step's comment | 10 |
| `plugins/workflows-core/CHANGELOG.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.claude/rules/plugin-updates-coupling.md`, `docs/superpowers/to-fix.md`, `docs/superpowers/to-test-on-real-project.md` | Release | 11 (LC31's deletion: 9) |
| `docs/superpowers/verification/2026-11-09-git-g1-part2a.md` | Create, last | 12 |

## The pins — every line the script renders

Every line is a template in `specs_git_lines.T`, and Task 3's `pins` check finds each template in its source, whitespace-collapsed. The **Test** column says how its use is held besides: **E** end to end on temporary repositories and a bare `origin`, **C** rendered from canned facts in process (the behaviour behind it is `session-branch.py`'s and pinned by its selftest).

| Item | Source | Task | Test |
|---|---|---|---|
| `Environment:` line | `session-hygiene` §7 (the command, not a template) | 4 | E, byte-equal to the Bash call |
| Non-repository notice, its signal clause, the left-behind line | SRG §3.1 (wording: Task 3); `addressing` §3 | 4 | E |
| Inside-tree notice: the one-line, stray-folder and two-readings forms; left-behind line | `addressing` §3 `specs-root-check` | 4 | E (each form) |
| Below-top-level notice | SRG §3.1 (Task 3) | 4 | E |
| Offline line | SRG §3.2 (Task 3) | 7 | E |
| G0, G1, G2 blocks | SRG §5 | 7 (G0 also 5) | E |
| G2 session-branch variants (another branch; the session branch itself) | SRG §5 | 8 | E |
| G2 direct-`/implement` variant | SRG §5 | 7 | E |
| Failed pull (catch-up, B2, B4) | SRG §3.4, §3.5 (Task 3) | 7 | E |
| Merged-branch flush cherry-pick line | SRG §3.4 | 7 | E |
| Settle: deleted merged; failed `-d`; `-D` advisory with `rm -f`; pushed N left on | SRG §3.4 | 7 | E (advisory once per run across `--rerun`) |
| B2: deleted line; configuration left over; squash `-D` line | SRG §3.5 (+ Task 3) | 7 | E (config left over: C, needs an unwritable `.git/config`) |
| B4 report, with and without the commit count | SRG §3.5 (Task 3) | 7 | E |
| Misrooted stay line, both variants | SRG §3.5 | 7 | E |
| Re-run's failed switch back | SRG §3.5 (Task 3) | 7 | E |
| `Specs preflight:` *push refused* (recorded; unrecorded) and *push FAILED* forms | SRG §4 step 6, §6 (Task 3) | 7 | E (refused via a `pre-receive` hook); unrecorded: C |
| Session branch created, both forms; session-branch call could not run | SRG §3.4, §8 (Task 3) | 8 | E |
| Stopped-early lines (start, end) | SRG (Task 3) | 7, 5 | C (in-process injected failure) |
| §6 rows: pushed on a plugin branch; pushed straight to default | SRG §6 | 5 | E |
| §6 rows: not ours; no remote; pushed elsewhere; remote deleted (+ default tail); origin lacks; refused before (file and config-key records) | SRG §6 | 5 | E |
| §6 rows: push refused (record file; config fallback; unrecorded) | SRG §6 | 5 | E (file); C (fallbacks: need an unwritable common dir) |
| §6 row: push-scope (path; merge; no file; hook variant) and the hook line | SRG §6 | 5 | E |
| §6 rows: push FAILED; nothing to commit; locked; commit failed; blocked; misrooted; silent | SRG §6 | 5 | E |
| §6 rows: replayed and pushed (+ dropped clause); already there; push rejected (reason clauses) | SRG §6, §4 step 6 | 6 | E (conflict-free replay, already there, `register-rebuild`, `checked-out`); C (the other reasons) |
| §6 row: moved, not pushed — its four `<why>`s and refused form; register clause; `upstream_error` | SRG §6 | 6 | C |
| The 420 s timeout reason clause; `session-branch.py could not run` and `stopped` clauses | SRG §4 step 6 | 6 | E (`--timed-out`); C |
| Remedies: switch first on a branch not stood on; `checked-out`; `checkout-moved` (none); session wrapper | SRG §4 step 6, §6 | 6, 8 | E (switch first, `checked-out`); C |
| §6 rows: pushed on the session branch (`<F>`); no identity; session-branch could not run | SRG §6, §8 | 8 | E |
| Session appends: created; `sync.conflict` (two sources); `sync.error`; `unsettled`; `stranded`; `unsupported`; session *push rejected* (two endings); refused remedy for the session branch; default-branch refusal turning the mode on (with and without an identity) | SRG §6 | 8 | E (created, unsupported via a `git` shim on `PATH`, as `session-branch.py`'s selftest does); C (the rest) |
| Declined append (D2) and the singular file count | SRG §6 | 5 | E |

**Not pinned by the selftest, and why:** whether a run prints `print` verbatim at the point the skill says, follows `next`, and passes the inputs the skill defines (agent behaviour — the live round, Task 11's to-test items); whether `CLAUDE_CODE_SESSION_ID` is set and stable across a compaction and a `claude --resume` in every harness version (live round); the 420 s harness timeout itself (its rendering is pinned through `--timed-out`); a host's own refusal wording (one `pre-receive` refusal is pinned; the reason text is git's); an unwritable `.git` or common directory when the selftest runs as root (those cases skip under `os.geteuid() == 0`, as `session-branch.py`'s do, and fall back to C); `checkout-moved` and `stranded`, which need a concurrent session or a refused default push (C here; `session-branch.py`'s selftest holds the behaviour).

---

### Task 1: Budget relief

**Files:**
- Create: `.claude/rules/plugin-authoring.md`, `.claude/rules/workflows-core-handoff.md`
- Modify: `CLAUDE.md` (two sections out; two table rows in; the `phase-handoff` pointer under § Shared authorities), `.claude/rules/workflows-core-git.md` (the `phase-handoff` paragraph out; a pointer in), `.claude/rules/workflows-core.md` (its "Split out for the 20,000-character budget" line names the new file), `.claude/rules/gates-validate-catalog.md` (its pointer to `CLAUDE.md` § Command, agent, and skill taxonomy), `.claude/rules/security-workflows.md` (its list of the rules files holding the authorities `/scan` consumes gains the new handoff file, since `/scan` runs `branch-check`)

**Interfaces:** none; every later task edits these files within the room this one makes.

- [ ] **Step 1: Read first and measure.** Read `CLAUDE.md`, `.claude/rules/workflows-core-git.md` and `workflows-core.md` with the Read tool. Record the sizes (expected at `bfa147fd`: `CLAUDE.md` 35,946; `workflows-core-git.md` 19,994; `workflows-core.md` 17,172):

```bash
python3 -c "import glob; [print(len(open(f,encoding='utf-8').read()), f) for f in ['CLAUDE.md']+sorted(glob.glob('.claude/rules/*.md'))]"
```

Count the pointers this task repoints, whitespace-collapsed over refinement 4's scope (`plugins/`, `README.md`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/`): `§ Command, agent, and skill taxonomy` (expect 1, `gates-validate-catalog.md`) and `the handoff consent choice → \`workflows-core-git.md\`` (expect 1, `CLAUDE.md`).

- [ ] **Step 2: Move `CLAUDE.md`'s two sections.** Create `.claude/rules/plugin-authoring.md`:

```markdown
---
paths:
  - "plugins/**"
  - "scripts/validate-catalog.py"
---

# Plugin authoring — the command, agent and skill taxonomy, and the Karpathy notes

Loaded when any file under `plugins/` or `scripts/validate-catalog.py` is read. Moved out of `CLAUDE.md` to keep it under its 36,000-character warning, as `claim-sweep.md` and `plugin-updates.md` were; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.
```

followed by `## Command, agent, and skill taxonomy` and `## Behavioral guardrails (Karpathy) — marketplace-specific notes` with their bodies **verbatim**, save the one link, rewritten `../../docs/maintainers/rationale.md#typed-only-commands`. Delete both sections from `CLAUDE.md`. Add to its rules table, after the `plugin-updates.md` row: ``| `plugin-authoring.md` | `plugins/**`; `scripts/validate-catalog.py` (repo root) | the command, agent and skill taxonomy; the Karpathy notes |``. In `gates-validate-catalog.md`, `(\`CLAUDE.md\` § Command, agent, and skill taxonomy)` becomes `(\`.claude/rules/plugin-authoring.md\`)`.

- [ ] **Step 3: Move the `phase-handoff` authority.** Create `.claude/rules/workflows-core-handoff.md` with `workflows-core-git.md`'s `paths:` block copied entry for entry, then:

```markdown
# workflows-core — the `phase-handoff` authority

Loaded with `.claude/rules/workflows-core-git.md`, whose `paths:` it shares. Split out of that file to keep it under 20,000 characters; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

## Authority
```

and the paragraph opening `` `plugins/workflows-core/references/phase-handoff.md` is the **single source of truth** `` verbatim (its relative links resolve unchanged from the same directory). Delete it from `workflows-core-git.md`; extend that file's "Split out for the same budget:" line with `; the \`phase-handoff\` authority → \`.claude/rules/workflows-core-handoff.md\`, which shares this file's \`paths:\``. Add to `CLAUDE.md`'s table, after the `workflows-core-read-only.md` row: ``| `workflows-core-handoff.md` | as `workflows-core-git.md` | the `phase-handoff` authority |``; repoint `CLAUDE.md` § Shared authorities' `workflows-core:phase-handoff` line to `workflows-core-handoff.md`; name the new file in `workflows-core.md`'s split-out line and in `security-workflows.md`'s list.

- [ ] **Step 4: Itemise the moves** (`workflows-core:instruction-file-maintenance`: a move deletes nothing). Check with Python that each moved section's text, less the one link rewrite, is a substring of its new file, and that no sentence of it remains in its old file. Re-run Step 1's counts: `§ Command, agent, and skill taxonomy` 1 → 0; `the handoff consent choice → \`workflows-core-handoff.md\`` 0 → 1.

- [ ] **Step 5: Measure and gate.** Expected: `CLAUDE.md` about 34,300 (35,946 − 1,877 + the two rows); `workflows-core-git.md` about 15,850; every file under its limit. Run the gate chain. Expected: `EXIT=0` (check 1 resolves the moved links; `validate-catalog.py` finds every new glob live).

- [ ] **Step 6: Commit** — `docs: budget relief — the taxonomy and Karpathy notes, and the phase-handoff authority, move to rules files of their own`

### Task 2: The state record and `declined`

**Files:**
- Create: `plugins/workflows-core/scripts/specs_git_state.py`
- Modify: `plugins/workflows-core/scripts/specs-git.py` (module import, `declined`, `Parser.error`'s `usage: ` prefix, selftest `scenarios_state`)

**Interfaces:**
- Produces, in `specs_git_state` (imported as `state`):
  - `class NoSession(Exception)` — `specs-git.py`'s `main()` reports it as `not run`.
  - `session_id() -> str` — `os.environ["CLAUDE_CODE_SESSION_ID"]`, matching `^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$`; anything else raises `NoSession("CLAUDE_CODE_SESSION_ID is unset or not a session id")`.
  - `path(session: str) -> str` — `os.path.join(os.path.expanduser("~"), ".claude", "dev-workflows", "specs-git", session + ".json")`, resolved at call time.
  - `FIELDS: dict` — the record's keys and defaults, exactly: `version` 1, `session` "", `command` "", `started` "", `started_by_script` True, `specs` "", `env_line` None, `gate` None, `top` None, `keys` [], `commit_key` None, `register_rebuild` None, `specs_git` None, `misrooted_notice` None (list of lines), `guard` None, `guard_block` None, `guard_paths` [], `default` None, `default_ref` None, `remote` None, `offline` False, `mode` None, `session_branch` None, `session_branch_created` None, `b2_left` None, `b4_left` None, `advised_D` [], `declined` [], `stage` "new", `pending` [], `settle_todo` [], `flush_done` False, `end_commit` None.
  - `new(command: str, **values) -> dict` — `FIELDS` copied, `session` and `started` (UTC, `%Y-%m-%dT%H:%M:%SZ`) filled; an unknown key raises `ValueError`.
  - `load(session: str) -> dict | None` — `None` where the file is absent, does not parse, or holds another `version`.
  - `save(session: str, rec: dict) -> None` — creates the directory (mode 0o700), writes a temporary file beside the record and `os.replace`s it; an unknown key raises `ValueError` before anything is written.
  - `remove(session: str) -> bool` — whether a file was removed.
- Produces, in `specs-git.py`: CLI `declined --command /<name> --path <p> [--path <p>]…` printing `{"recorded": [paths in order, unique], "record": "found" | "created" | "replaced"}` — `replaced` where the session's record names another command, which is set aside for a fresh one (`started_by_script: false`) holding this command's paths only. `--command` must match `^/[a-z][a-z0-9-]*$` (else a usage exit 2).

- [ ] **Step 1: Write the failing selftests**, `scenarios_state(tmp)`, every check setting `HOME` and `CLAUDE_CODE_SESSION_ID` itself and restoring them:
  - `s_session_id`: unset, empty and `../x` raise `NoSession`; `ab-12_x.y` is returned.
  - `s_path`: with `HOME=<tmp>/home`, `path("s1") == "<tmp>/home/.claude/dev-workflows/specs-git/s1.json"`.
  - `s_roundtrip`: `save` then `load` returns the record, a non-ASCII and a space-carrying path in `declined` included; no file but `s1.json` is left in the directory; `save` with an unknown key raises before the file changes.
  - `s_unparsable`: a file holding `{` loads as `None`.
  - `s_two_sessions`: records saved for `s1` and `s2` load back each its own.
  - `s_remove`: `True`, then `False`; `load` then `None`.
  - `s_declined_cli`: with no record, `declined --command /create-ard --path "specifications/PRD-A-1 x/prd.md" --path a.md` prints `record: "created"`, and the record holds both paths and `started_by_script: false`; a second call with `a.md` again and `b.md` adds `b.md` only (`record: "found"`); a record of `/idea` is replaced (`record: "replaced"`) by one holding this call's paths alone.
  - `s_declined_no_session`: without `CLAUDE_CODE_SESSION_ID`, exit 2, one `specs-git: not run (` line, no file under `HOME`.
  - `s_usage_prefix`: `declined --path a.md` (no `--command`) exits 2 with one line beginning `specs-git: not run (usage: `.
  - `s_outside_repo`: a `declined` call made from inside a repository leaves its `git status --porcelain` unchanged.
- [ ] **Step 2: Run** `python3 plugins/workflows-core/scripts/specs-git.py --selftest`. Expected: FAIL on the new checks.
- [ ] **Step 3: Implement** `specs_git_state.py` and the `declined` subcommand; import the module beside `sb` inside a `try` that prints one `not run` line and exits 2 where it fails; `Parser.error` prints `specs-git: not run (usage: <message>)`; `main()` maps `state.NoSession` to the `not run` line and exempts `declined` from `--specs`, as it does `owner-repo`. The selftest pops `CLAUDE_CODE_SESSION_ID` and `GIT_USER_INITIALS` at its start and extends Part 1's `cli()` helper to `cli(*args, env=None, stdin=None, cwd=None)`; add the lone-copy check: a copy of `specs-git.py` and `session-branch.py` without `specs_git_state.py` exits 2 with one line.
- [ ] **Step 4: Run** the selftest. Expected: `specs-git selftest: PASS (<n> checks)`.
- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git — the per-session state record and declined`

### Task 3: The line templates and the wording SRG leaves free

**Files:**
- Create: `plugins/workflows-core/scripts/specs_git_lines.py`
- Modify: `plugins/workflows-core/references/specs-repo-git.md` (§3.1, §3.2, §3.4, §3.5, §4.1, §6 — wording only); `specs-git.py` (import; selftest `scenarios_lines`)
- Regenerate: `plugins/workflows-core/reference-parts/` (nothing should change: SRG loads by no part; run `generate` and `check-parts` to prove it)

**Interfaces:**
- Produces, in `specs_git_lines` (imported as `lines`):
  - `T: dict[str, str]` — every template, keyed by id, each the exact text of its source with `<…>` placeholders as the source writes them. Ids: §5 `g0`, `g1`, `g2` (the three fenced blocks, whole); `g2.session.not_done`, `.fix`, `.if_ignored`; `g2.self.not_done`, `.fix`, `.if_ignored`; `g2.implement.not_done`, `.fix`, `.if_ignored` (the backticked lines of §5's two prose paragraphs). §6 rows `row.<id>` for each id in `ROWS` below, plus the variant pieces `row.remote-deleted.default-tail`, `row.scope.merge` (`which is a merge commit`), `row.scope.no-file` (`which changes no file`), `row.scope.hook`, `row.replayed.dropped` (`, <D> of them already there and dropped`), `row.moved.refused`, `row.session-rejected`, `row.session-rejected.conflict-ending`. Appends `app.hook-line`, `app.record-key`, `app.record-unset`, `app.unrecorded`, `app.register-clause`, `app.register-move`, `app.upstream-error`, `app.why.later-refused`, `app.why.moved-on`, `app.why.failed`, `app.why.stopped`, `app.session.created`, `app.session.conflict-default`, `app.session.conflict-origin`, `app.session.sync-error`, `app.session.unsettled`, `app.session.stranded`, `app.session.unsupported`, `app.session.refused-remedy`, `app.mode-on`, `app.mode-on.no-identity`, `app.declined`. Reason clauses `reason.<refused.reason>` for the twelve of §6 plus `reason.not-run`, `reason.timed-out`, `reason.session-mode`; remedies `remedy.rejected`, `remedy.not-standing`, `remedy.checked-out`, `remedy.session-wrap`. Preflight lines `pre.nonrepo`, `pre.nonrepo.signal`, `pre.below-top`, `pre.offline`, `pre.pull-failed`, `pre.merged-flush`, `pre.refused`, `pre.refused.unrecorded`, `pre.failed`, `pre.created.empty`, `pre.created.committed`, `pre.deleted`, `pre.delete-failed`, `pre.advisory-D`, `pre.advisory-D.rm`, `pre.pushed-left`, `pre.b2-config`, `pre.b2-squash`, `pre.b4`, `pre.b4.count`, `pre.stay`, `pre.rerun-failed`, `pre.session-not-run`, `pre.stopped`, `end.stopped`. From `addressing` §3: `root.one-line`, `root.stray`, `root.two-readings`, `root.left-behind`, `root.unsupported` (the unsupported-layout clause).
  - `ROWS: tuple[str, ...]` — the 24 `end` row ids, in SRG §6's order: `pushed-plugin`, `pushed-default`, `pushed-session`, `no-identity`, `session-not-run`, `not-ours`, `no-remote`, `elsewhere`, `remote-deleted`, `origin-lacks`, `refused-before`, `push-refused`, `scope`, `replayed`, `already-there`, `moved`, `rejected`, `failed`, `nothing`, `locked`, `commit-failed`, `blocked`, `misrooted`, `silent` (`silent` has no template: it prints nothing).
  - `fill(template_or_id: str, values: dict[str, str | list[str]]) -> str` — replaces each outermost balanced `<…>` span by `values[span]`, a list being consumed one item per occurrence in order (`<sha7>` names two commits in the push-scope row); a span with no key raises `ValueError` naming it, so no placeholder ever reaches a user.
  - `count_files(n: int) -> str` — `(1 file)` or `(<n> files)` (SRG §6's singular rule).
  - `artifacts(paths: list[str]) -> str` — `phase-handoff` §4.1's `<artifacts>`: the paths comma-separated where three or fewer, else `<n> files under <dir>`, `<dir>` the nearest directory holding every path (`os.path.commonpath` of their directories, repo-relative).
  - `pins(srg: str, addressing: str) -> list[str]` — one failure per template not found in its source; comparison collapses every whitespace run to one space on both sides, save the three §5 blocks, compared line for line against SRG §5's fenced blocks.

- [ ] **Step 1: Write SRG's missing wording first** — prose, one line each, no hard wrap — so the templates have a source:
  - §3.1, the non-repository notice: `` `Specs preflight: SPECS_PATH is <value>, which <is not a directory | is not in a git repository> — nothing this run writes there is committed or handed off; set SPECS_PATH to your specs repository's top level, where it is set, and re-run.` ``; where `specs-root-check` finds a signal, the same line goes on with `` ` It <is itself a specifications/ directory | is inside the specifications/ directory | is itself a specs folder, asserting key <key> | holds the specs folder <subdirectory> directly> — set SPECS_PATH to <the value the walk found | the directory that holds specifications/> instead.` `` (one leading space), then the unsupported-layout clause where `specs-root-check`'s stop carries it.
  - §4 step 1, after "a run that ran no preflight and carries neither flag tests G0's state here": such a run also runs §3.1's two placement tests — `specs-root-check`'s signals and the below-top-level test — and, where one fires, takes the `specs_git: misrooted` outcome with that notice, since its preflight would have set the flag and a commit from below the top level stages paths `git add` cannot find from there (the plan's named behaviour change).
  - §3.1, the below-top-level notice: `` `Specs preflight: SPECS_PATH is <value>, below the top level of its repository (<top>) — a specs tree inside a larger repository is unsupported, because this plugin switches branches and commits in the repository SPECS_PATH belongs to, so this run switches and commits nothing there; set SPECS_PATH to a dedicated specs repository's top level.` ``
  - §3.2, *Freshness*: the note is printed as `` `Specs preflight: offline — ancestry checked against the last-fetched ref` ``.
  - §3.4's catch-up, §3.5's B2 and B4 pulls: a failed pull prints `` `Specs preflight: could not fast-forward <default> (<git's first error line>); the run goes on from it as it stands` ``.
  - §3.4's settle loop and §3.5's B2: a failed `-d` prints `` `Specs preflight: could not delete merged <branch> (<git's first error line>)` ``; B2 that deleted its branch prints §3.4's `Specs preflight: deleted merged <branch>`.
  - §3.5's B4: `` `Specs preflight: left <branch> for <default>, since no key of this run names it — the branch and its pull request are as they were` ``, followed, where it holds commits a push would publish, by `` `; <N> commit(s) on it are not on origin, and a later run's preflight pushes them where §4 step 5 lets it` ``.
  - §3.5's re-run: a failed switch back prints `` `Specs preflight: could not switch back to <branch> (<git's first error line>); this run goes on from <current>` ``.
  - §6's *Inside §3.4's flush and retry* paragraph: "each of these four rows" becomes "each of these four rows, and the *push FAILED* row,", so `Specs preflight: <branch> — push FAILED (<reason>); the commit is local and a later run retries it` is that substitution.
  - §8's opening: an exit 2 inside the preflight prints `` `Specs preflight: session-branch.py could not run (<the first line of its stderr>)` ``.
  - §1 rule 5, after its first sentence: where the script stops on a failure it did not foresee after its first write, it prints `` `Specs preflight: stopped early (<the error>) — what it did is above, and the next run's preflight goes on from where this one stands` `` at the start and `` `Specs repo: NOT FINISHED — the terminal step stopped early (<the error>); what it committed or pushed is as it left it, and the next run's preflight flushes the rest` `` at the end, the end's one outcome line.
  - **D2.** §4.1's third bullet names both declines: "when the user declined git at handoff — `phase-handoff.md` §4.3's option 2 (*just write the files*) or option 3 (*Cancel*)". §6's last paragraph: "When the deliverable is still uncommitted because the user declined git at handoff (§4.1), on either option, append to the line: `; the deliverable at <path> remains uncommitted, as you asked`, `<path>` being the declined handoff's declared paths that `git status` still lists, written as `phase-handoff.md` §4.1 writes `<artifacts>`."
- [ ] **Step 2: Write the failing selftests**, `scenarios_lines(tmp)`:
  - `l_pins`: `lines.pins(<SRG text>, <addressing text>) == []`.
  - `l_pins_bite`: the same with one word of SRG §6's *Nothing to commit* row changed in memory → exactly one failure, naming `row.nothing`.
  - `l_ids`: every id the Interfaces list names is in `T`; every `row.<id>` but `silent` exists for each of `ROWS`; `len(ROWS) == 24`.
  - `l_fill`: `fill("row.nothing", {}) == "Specs repo: no session artifacts to commit"`; a list value fills two `<sha7>`s in order in `row.scope`; a missing key raises `ValueError` naming it; the misrooted stay line's nested alternation span is filled whole by its key.
  - `l_count`: `count_files(1) == "(1 file)"`, `count_files(2) == "(2 files)"`.
  - `l_artifacts`: one, two and three paths comma-separated; four paths under `specifications/PRD-A-1-x/` → `4 files under specifications/PRD-A-1-x`; four spanning `specifications/` → `… under specifications`; a path with a space kept as it is.
- [ ] **Step 3: Run** the selftest. Expected: FAIL (`lines` undefined).
- [ ] **Step 4: Implement** `specs_git_lines.py` (templates as literal strings copied from the sources, never built from pieces of other templates), import it beside `state`, extend the lone-copy check to a copy missing it.
- [ ] **Step 5: Run** the selftest and `python3 scripts/reference-parts.py generate && python3 scripts/reference-parts.py check-parts`. Expected: PASS, and `git status` shows no change under `reference-parts/`.
- [ ] **Step 6: Commit** — `feat(workflows-core): specs-git — every notice and outcome line, pinned to specs-repo-git; SRG fixes the wording it left free; D2`

### Task 4: The gate — the `Environment:` line, §3.1 and `specs-root-check`

**Files:** Modify `plugins/workflows-core/scripts/specs-git.py` (functions, the `specs-root-check` subcommand, selftest `scenarios_gate`).

**Interfaces:**
- Consumes: `lines.fill`, `lines.T` (`pre.nonrepo`, `pre.nonrepo.signal`, `pre.below-top`, `root.*`).
- Produces:
  - `SH7_LINE: str` — `session-hygiene` §7's Bash call (the fenced `bash` block under **The line.**), character for character.
  - `env_line(specs: str) -> str` — runs `bash -c SH7_LINE` with `SPECS_PATH` set to `specs` in its environment, or removed where `specs` is empty, and every other variable inherited; returns its one line.
  - `RESERVED: re.Pattern` — `addressing` §2's register of reserved subdirectory names as a whole-name match: `brd`, `grounding`, `interview`, `dev-workflows`, `design`, `attachments`, `revisions`, `bundle-[0-9]{8}`, `customer-sent-[0-9]{8}`, `Doc screenshots`.
  - `specs_root_check(specs: str) -> {"signal": None | "a-prefix" | "a-ef" | "b-self" | "b-sub", "form": None | "one-line" | "stray" | "two-readings", "value": str | None, "subdirs": [str], "lines": [str]}` — `workflows-core:addressing` §3 `specs-root-check` exactly: signal (a)'s two tests, signal (b)'s carrier test (`addressing` §4's carrier order — top-level files in byte-wise order, then `brd/brd-inventory.md` — read off frontmatter `key:` and `kind:` of `brd`, `prd` or `epic`, with §4.1's `<KIND>-<key>-` prefix test, the folder's own name tested physically and a subdirectory skipped where it resolves inside `$SPECS_PATH/specifications/`), the value-to-set walk (at most three levels above, both halves required), the three forms and the left-behind line. `lines` is `[]` where no signal holds.
  - `gate(specs: str, notices: bool = True) -> {"state": "unset" | "not-a-repo" | "read-only" | "pass", "top": str | None, "git_dir": str | None, "misrooted": bool, "lines": [str]}` — SRG §3.1's three dispositions and its two passing-gate tests (`specs-root-check`, then the below-top-level test, skipped where the first fired); `misrooted` where the inside-tree notice, the below-top-level notice, or a non-repository notice with a signal fired. With `notices=False` it returns `state`, `top` and `git_dir` alone (Task 5's §4 step 1).
  - CLI `--specs "<value>" specs-root-check` printing `specs_root_check`'s object.

- [ ] **Step 1: Write the failing selftests**, `scenarios_gate(tmp)`:
  - `g_sh7_pinned`: `SH7_LINE` equals the fenced block read from `plugins/workflows-core/references/session-hygiene.md` §7.
  - `g_env_line_equal` (Review Focus 3): for `SPECS_PATH` unset; a repository path with a trailing `/`; a symlink to it; a relative path; a nonexistent path; a path holding a space; `REPOS_PATH` unset and set — `env_line(value)` equals the output of `bash -c '<the block read from session-hygiene.md>'` run with `SPECS_PATH` exported to `value` (or unset) in the same environment.
  - `g_unset`: `gate("")` → `state: "unset"`, `lines: []`, `misrooted: False`.
  - `g_file`: a regular file → `not-a-repo`, one line from `pre.nonrepo` with `is not a directory`.
  - `g_plain_dir`: a directory in no repository, no signal → `not-a-repo`, one line, `misrooted: False`.
  - `g_mounted_tree`: a directory in no repository holding `PRD-A-1-x/prd.md` (frontmatter `key: A-1`, `kind: prd`) → `not-a-repo`, the line carrying the signal clause, `misrooted: True`; with a nested `specifications/PRD-A-2-y/` and a `dev-workflows-cost/` beside it, a second line from `root.left-behind`.
  - `g_inside_tree`: `<repo>/specifications` → `pass`, `misrooted: True`, the one-line form naming `<repo>` as the value; `<repo>/specifications/PRD-A-1-x` → the same signal.
  - `g_below_top`: `<repo>/specs` holding `specs/specifications/` → `pass`, `misrooted: True`, one line from `pre.below-top` naming `<repo>`.
  - `g_stray`: a repository's top level holding `specifications/` and a hand-placed `PRD-S-9-x/` with a carrier → the stray-folder form naming `PRD-S-9-x`, no left-behind line.
  - `g_two_readings`: `<repo>/specs` holding `PRD-A-1-x/` directly and no `specifications/` → the two-readings form with the unsupported-layout clause.
  - `g_correct_root`: a top level with `specifications/PRD-A-1-x/`, a `templates/prd.md` carrying `key:` and `kind: prd`, and a `README.md` carrying both → `pass`, no lines, `misrooted: False`.
  - `g_reserved`: `RESERVED` matches every name of `addressing` §2's list as that file writes it, and `session-branch.py`'s `EXCLUDED` holds the same names but `dev-workflows`.
  - `g_read_only` (skipped as root): `chmod a-w` on `.git` → `read-only`, no lines.
  - `g_cli`: `specs-root-check` prints the function's object, exit 0, for the mounted tree and for an unset value.
- [ ] **Step 2: Run** the selftest. Expected: FAIL.
- [ ] **Step 3: Implement** the four functions and the subcommand; `main()` passes `specs-root-check`'s `--specs` through unchecked — empty, a file, a subdirectory — as it will `start`'s and `end`'s (the `--specs` exception). The frontmatter read is the lines between a first `---` and the next, `key:` and `kind:` taken by `^(key|kind):\s*(.+?)\s*$`, quotes stripped; nothing is parsed out of a name.
- [ ] **Step 4: Run** the selftest. Expected: PASS.
- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git — the Environment line, the §3.1 gate and specs-root-check`

### Task 5: The commit engine and `end`

**Files:** Modify `plugins/workflows-core/scripts/specs-git.py` (engine, `end`, selftest `scenarios_end`).

**Interfaces:**
- Consumes: `state.*`, `lines.*`, `gate()`, Part 1's `status()` and `push_scope()`, `sb.git_bounded`, `sb.refusal_record`, `sb.mode`.
- Produces:
  - `resolve_default(root: str, fetch: bool) -> {"default": str, "default_ref": str, "remote": "origin" | "none", "offline": bool}` — SRG §3.2's name, ref and freshness rules; the fetch (`fetch origin <default>`, 60 s) only where `fetch` is true and a remote exists.
  - `catch_up(root, default, default_ref) -> str | None` — §3.4's catch-up where HEAD is on the default branch and strictly behind `<default-ref>` (`pull --ff-only --no-rebase origin <default>`, 60 s); the `pre.pull-failed` line where it fails, else `None`.
  - `commit_session_files(root: str, message: str) -> {"status": "committed" | "nothing" | "locked" | "failed", "sha": str | None, "paths": [str], "hook_paths": [str], "error": str | None}` — SRG §2.1 steps 1–3 (Part 1's `status()`, `git add -A -- ':(literal)<p>'…`) and §4 step 4 (the staged list by `diff --cached --name-only -z --no-renames -- ':(literal)…'`, the staged-before read, the pathspec commit `commit -q -m <message> -- ':(literal)…'`, the index restore over the paths both `diff-tree … HEAD` and `diff --cached` list less those somebody else had staged); `locked` where `git rev-parse --git-path index.lock` exists, tested before staging; `hook_paths` the paths the commit carries that its pathspecs did not name.
  - `push_check(root, branch, default, session_branch=None) -> {"row": None | "not-ours" | "no-remote" | "elsewhere" | "remote-deleted" | "refused-before" | "origin-lacks" | "scope", "remote": str | None, "record": str | None, "record_kind": "file" | "config" | None, "date": str | None, "scope": dict | None, "set_upstream": bool}` — §4 step 5's three conditions and four nowhere-to-push states, tested in SRG's order, `ls-remote --exit-code --heads origin refs/heads/<branch>` capped at 30 s; `row` `None` where all hold; `set_upstream` by step 5's `-u` rule.
  - `push(root, branch, set_upstream) -> {"outcome": "pushed" | "refused" | "rejected" | "failed", "reason": str | None, "recorded": "file" | "config" | None, "record": str | None, "record_error": str | None}` — `push --porcelain [-u] origin <branch>` (60 s; a cap is *failed* with reason `the push did not finish within 60 s`); the outcome read from the `--porcelain` status line for `refs/heads/<branch>` alone; `[remote rejected]` is *refused* save the five transient reasons of step 6, which are *failed*; a refusal writes the push-refusal record (§1 rule 8: the file under `<git-common-dir>/workflows/push-refused/<branch>` holding the date, else the `branch.<branch>.workflowsPushRefused` key).
  - CLI `--specs "<value>" end --command /<name> [--commit-key K] [--register-rebuild P] [--no-preflight] [--misrooted-stdin] [--session-branch-created SHA7]`, printing `{"print": [str], "line": str | None, "row": <a ROWS id> | None (None only while `next` names the replay), "sha7": str | None, "files": int | None, "branch": str | None, "pushed": bool, "next": dict | None, "record": "found" | "missing" | "stale" | "ignored", "error": str | None}`. `print` is the outcome line (appends included), then the §5 block or the misrooted notice it repeats, then the hook line where it applies. `--commit-key` must match `workflows-core:addressing` §1's `^[A-Z][A-Z0-9_]*(-\d+)+$`, else a usage exit 2.
- **Order inside `end`** (SRG §4 steps 1–7): read the record (`missing` where none; `stale` where it names another command; `ignored` under `--no-preflight` — the last two removed, the run treated as having no preflight); the flags — the record's, then `--misrooted-stdin`'s notice, then, with no record, §4 step 1's G0 test and the ruling's re-run of §3.1's placement tests; `gate(specs, notices=False)` → `silent` where it fails and no flag stands; `<default>` from the record or `resolve_default(fetch=False)`; mode from the record or `sb.mode` (Task 8 fills the mode branch; outside it, `mode` off); `catch_up`; `commit_session_files` with `<KEY|NOISSUE> Add dev-workflows session artifacts (<command>)`; where it committed, `push_check`, then `push`; a `rejected` push returns `next` naming `replay --for end --branch <b> [--set-upstream]` (timeout 420000, `on_timeout` the same with `--timed-out`), with `stage: "end-replay"` and `end_commit: {sha7, files, branch, paths, hook_paths}` saved; otherwise render the row, the appends in SRG §6's order (declined last, naming only the recorded declined paths that `status()` still lists, through `lines.artifacts`), the repeated block, the hook line where a hook path is one the record's `guard_paths` or the declined append names, and remove the record. R2's boundary in `end` is its first repository write — the catch-up's pull, else the `git add`: before it, a failure is an exit 2; after it, an exception returns `error` with `end.stopped` as the line.

- [ ] **Step 1: Write the failing selftests**, `scenarios_end(tmp)`, on a `world(tmp, name)` helper — a bare `origin`, a clone with `specifications/PRD-ACME-1-x/prd.md` committed and pushed on `main`, `HOME=<tmp>/home-<name>`, `CLAUDE_CODE_SESSION_ID=<name>` — and a `seed(env, **fields)` helper that saves a record as `start` would:
  - `e_nothing`: clean tree → `row: "nothing"`, `print == ["Specs repo: no session artifacts to commit"]`, record removed.
  - `e_pushed_default`: a new `specifications/PRD-ACME-1-x/dev-workflows/resume.md` on `main` with `--commit-key ACME-1` → `row: "pushed-default"`, subject `ACME-1 Add dev-workflows session artifacts (/create-ard)`, no `Co-Authored-By`, `origin/main` holds it; without `--commit-key` the subject opens `NOISSUE`; one file reads `(1 file)`.
  - `e_pushed_plugin`: the same on a pushed `prd/ACME-1-x` → `pushed-plugin`.
  - `e_not_ours`: on `feature/x` with a record holding G2's block → `not-ours`, then the block, verbatim.
  - `e_no_remote`, `e_elsewhere` (`branch.main.pushRemote fork`), `e_remote_deleted` (a pushed plugin branch deleted on the bare; and the default branch's form with its `remote set-head` tail), `e_origin_lacks` (a plugin branch never pushed), `e_refused_before` (a record file holding `2026-11-01` → that date and the file's path; the config-key form naming `branch.<b>.workflowsPushRefused` and its `config --unset`) → each its row.
  - `e_push_refused`: a bare whose `pre-receive` exits 1 → `push-refused`, the record file written under the common git directory with today's date.
  - `e_scope`: an unpushed commit of the user's touching `notes.md` on `main` → `scope` naming its sha7, subject and path; a merge commit → `which is a merge commit`; a `pre-commit` hook that adds `generated.txt` to the commit → the hook variant naming it, and, where a G1 block in the record lists `generated.txt`, the hook line after the block.
  - `e_push_failed`: `origin` pointed at a missing path after the clone → `failed`.
  - `e_locked`: an `index.lock` present → `locked`, nothing staged.
  - `e_commit_failed`: a `pre-commit` hook that exits 1 → `commit-failed`, the session file still staged.
  - `e_blocked`: a record with `specs_git: blocked` → `blocked` and the G0 block; with no record and `--no-preflight`, a detached HEAD and a dirty session file → `blocked` with the block (the first time), and with nothing to stage → `nothing`.
  - `e_misrooted`: a record with `specs_git: misrooted` and its notice → `misrooted`, then that notice verbatim; with no record, `--no-preflight --misrooted-stdin` and an `Environment changed: …` line on stdin → the same with that line.
  - `e_no_record_below_top`: no record, `--no-preflight`, `$SPECS_PATH` at `<repo>/specs` holding `specs/specifications/` with a dirty session file → `misrooted` with the below-top-level notice, nothing committed.
  - `e_silent`: a directory that is no repository and no flag → `row: "silent"`, `print == []`, `line: null`.
  - `e_declined` (Review Focus 4): a record declining `specifications/PRD-ACME-1-x/prd.md` and `specifications/PRD-ACME-1-x/a b.md` (both untracked) → the line ends `; the deliverable at specifications/PRD-ACME-1-x/prd.md, specifications/PRD-ACME-1-x/a b.md remains uncommitted, as you asked`; with `prd.md` committed by hand before `end`, only `a b.md` is named; four declined paths in that folder → `4 files under specifications/PRD-ACME-1-x`.
  - `e_two_sessions` (Review Focus 1): records for sessions `s1` (misrooted) and `s2` (clean, G1 block) on the same repository → `end` under `s2` commits and prints `s2`'s block only; `s1`'s record is untouched.
  - `e_stale_no_preflight` (Review Focus 2): a record of `/create-ard` with `specs_git: misrooted`, then `end --command /create-ard --no-preflight` → `record: "ignored"`, the commit made, the record gone; the same record and `end --command /idea` with no flag → `record: "stale"`, the commit made.
  - `e_missing_record`: no record and no `--no-preflight` → `record: "missing"`, run as the no-preflight path.
  - `e_catch_up`: `main` behind `origin/main` → pulled before the commit; the push lands.
  - `e_nonff`: `origin/main` moved by another clone after the record was seeded → `row: null`, `print == []`, `next.run` names `replay --for end --branch main` with timeout 420000 and an `on_timeout` carrying `--timed-out`; the record holds `end_commit`.
  - `e_exit2`: without `CLAUDE_CODE_SESSION_ID`, exit 2, one line, and `git status`, `HEAD` and the refs are as they were; `--commit-key acme-1` → a usage exit 2.
  - `e_error_after_write` (R2): in process, replace `push_check` by a function that raises, run `end` on a dirty tree → exit-0 result with `error` set, the commit made, `line` the `end.stopped` line.
- [ ] **Step 2: Run** the selftest. Expected: FAIL.
- [ ] **Step 3: Implement** the engine and `end` as the Interfaces say.
- [ ] **Step 4: Run** the selftest. Expected: PASS.
- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git end — commit-artifacts by script, its rows and appends`

### Task 6: The replay

**Files:** Modify `plugins/workflows-core/scripts/specs-git.py` (`replay` subcommand, row rendering for §4 step 6, selftest `scenarios_replay`).

**Interfaces:**
- Consumes: `state.*`, `lines.*`, `sb.replay`, `sb.Partial`, `sb.NotRun`, Task 5's renderer for appends and record removal.
- Produces:
  - `classify_replay(result: dict | None, error: str | None, partial: bool, timed_out: bool) -> {"row": "replayed" | "already-there" | "moved" | "rejected", "why": str | None, "reason": str | None}` — §4 step 6's four cases in order, its exit-2 and timeout rules, and `<why>`'s order (`refused`, `[rejected]` in `porcelain`, a refusal in `porcelain` — which also writes the push-refusal record — then any other).
  - CLI `--specs <top> replay --for start|end --branch <b> [--set-upstream] [--timed-out]`: reads `register_rebuild` and the run's context from the record; runs `sb.replay(top, branch, register_rebuild, set_upstream)` in process, unless `--timed-out`; `--for end` prints `end`'s object (the row with `end_commit`'s `<sha7>`/`<N>` and every append, the record removed); `--for start` prints `{"print": [the row in its Specs preflight: form], "next": <the next pending replay, else start --resume>, "error": null}` and drops that branch from `pending`. A branch the run is not standing on gets `remedy.not-standing`; `checked-out` its own remedy; `checkout-moved` none. It never exits 2 once the record is found.

- [ ] **Step 1: Write the failing selftests**, `scenarios_replay(tmp)`:
  - `r_replayed`: two clones; A's `end` commits `…/dev-workflows/feedback/x.md` while B has pushed `…/dev-workflows/feedback/y.md` → `end` returns `next`; running `next.run` → `row: "replayed"`, the line names `1 commit(s)`, `origin/main` holds both files, record removed.
  - `r_dropped`: B pushed the same change → `already-there` (or `replayed` with the `<D>` clause where one of two commits was already there).
  - `r_register_rebuild`: both sides changed `security/web/register.json`, no `register_rebuild` → `rejected` with `reason.register-rebuild`'s first form and the `pull --rebase --no-autostash` remedy.
  - `r_checked_out`: the branch checked out in a second worktree → `reason.checked-out` and the remedy naming that worktree, no switch.
  - `r_timed_out`: `replay --for end --timed-out` → `rejected` with the 420 s clause, record removed.
  - `r_start_form`: a seeded record with `pending: [{branch: "prd/ACME-2-y", set_upstream: false, standing: "main"}]` and `prd/ACME-2-y` rejected → `print[0]` opens `Specs preflight: prd/ACME-2-y` and its remedy switches to the branch first and back to `main` after; `next.run` names `start --resume`.
  - `r_canned`: `classify_replay` and the renderer over canned results → each `<why>` (later refused with `checkout-moved`'s `… so <branch> was not moved again; …` form; moved on again over `<attempts>`; failed with a status line and with none; stopped), the refused form, the register clause with a `run` and a `remote` move, `upstream_error`, an exit 2 with nothing on stdout (`reason.not-run`), and a `Partial` with `pushed: true` (*replayed and pushed*).
- [ ] **Step 2: Run** the selftest. Expected: FAIL.
- [ ] **Step 3: Implement** `classify_replay`, the renderer and the subcommand.
- [ ] **Step 4: Run** the selftest. Expected: PASS.
- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git replay — §4 step 6 in a call of its own, for start and end`

### Task 7: `start`

**Files:** Modify `plugins/workflows-core/scripts/specs-git.py` (`start`, selftest `scenarios_start`).

**Interfaces:**
- Consumes: Tasks 2–6.
- Produces: CLI `--specs "<value>" start --command /<name> [--key K]… [--commit-key K] [--register-rebuild P] [--rerun] [--resume] [--budget S]`, printing `{"print": [str], "next": dict | None, "specs_git": None | "blocked" | "misrooted", "gate": str, "default": str | None, "default_ref": str | None, "remote": "origin" | "none" | None, "offline": bool, "session_branch": str | None, "mode": str | None, "guard": None | "G0" | "G1" | "G2", "branch": str | None, "b2_left": str | None, "b4_left": str | None, "replaced": dict | None, "error": str | None}`; `branch` is HEAD's branch when the call returns. `--key` and `--commit-key` must match `addressing` §1's grammar.
- **Stages** (saved as the record's `stage`, each resumable from its start): `fetch` (§3.2), `guards` (§3.3), `flush` (§3.4's catch-up, the merged-branch leave and the flush or retry of the current branch), `settle` (§3.4's loop over `settle_todo`, computed once on entering it), `replays` (waiting on `pending`), `disposition` (§3.5, the re-run's switch back having run after `fetch`), `done`. `--resume` continues the saved stage with the saved arguments; `--rerun` opens on the session's own record (fresh where none), keeps `specs_git` (OR), `advised_D`, `b4_left` and `declined`, and switches back to `b4_left` first where `branch_key(b4_left, new keys)` resolves a key. A rejected push in `flush` or `settle` appends `{branch, set_upstream, standing}` to `pending`; a refused or failed one prints its `Specs preflight:` form.
- **Choices the script makes, from the rulings:** G2's direct-`/implement` lines where `--command` is `/implement` and the current directory's top level equals `$SPECS_PATH`'s; §5's `<path list>` comma-separated on the *Found* line and shell-quoted (`shlex.quote`), space-separated, on the *Fix* line, the paths saved as `guard_paths`; a G2 variant SRG gives in prose rendered unwrapped on its one line; B2 that deleted its branch prints `pre.deleted`; `<YYYY-MM-DD>` is today's UTC date; `<SPECS_PATH>` in a remedy is `--specs` as given.

- [ ] **Step 1: Write the failing selftests**, `scenarios_start(tmp)` on Task 5's `world`:
  - `t_clean`: on `main`, clean → `print == [<the Environment: line>]`, `specs_git: null`, `default: "main"`, `default_ref: "origin/main"`, `remote: "origin"`, `branch: "main"`, `next: null`, record saved with `stage: "done"`.
  - `t_unset`: `--specs ""` → the `Environment:` line naming `SPECS_PATH=unset`, `gate: "unset"`, nothing else, a record saved.
  - `t_misrooted`: `<repo>/specs` holding `specs/specifications/`, HEAD on a merged `prd/A-1-x` → the below-top notice and `pre.stay`'s merged variant, no switch; HEAD on an unmerged `prd/B-2-y` with keys `{A-1}` → the unkeyed variant; nothing committed.
  - `t_offline`: `origin` unreachable for the fetch → `offline: true` and `pre.offline`'s line.
  - `t_g0`, `t_g1`, `t_g2`: a detached HEAD → G0's block, `specs_git: blocked`; a dirty `notes.md` → G1's block listing it, no flush, no switch; on `feature/x` → G2's block naming `main`. `t_g2_implement`: `--command /implement` run from inside the specs repository's work tree on `feature/x` → G2 with the direct-`/implement` lines.
  - `t_catch_up` and `t_catch_up_failed`: behind `origin/main` → fast-forwarded silently; with `origin` made unreachable after the fetch → `pre.pull-failed`.
  - `t_flush`: a dirty session file on `main` → committed with `NOISSUE Add dev-workflows session artifacts (/feedback)` and pushed, nothing printed past the `Environment:` line; with `--commit-key ACME-1` the subject opens `ACME-1`.
  - `t_retry`: an earlier run's unpushed session commit on `main` → pushed, silent.
  - `t_merged_leave`: HEAD on a fast-forward-merged `prd/A-1-x` with a dirty session file → switched to `main`, `prd/A-1-x` deleted, `Specs preflight: deleted merged prd/A-1-x` printed, the flush on `main`, `b2_left: "prd/A-1-x"`; where `resume.md` differs between the two so the switch is refused → the flush on the branch and `pre.merged-flush`'s cherry-pick line.
  - `t_settle`: another fast-forward-merged plugin branch with an existing upstream → `deleted merged`; a squash-merged one → the `-D` advisory once, and not again after `start --rerun`; one with a session-file commit `origin` lacks on its pushed upstream → `pushed 1 session-file commit(s) left on <branch>`.
  - `t_b3_b4`: on unmerged `spec/ACME-1-01-x` with keys `{ACME-1-01, ACME-1}` → stays (B3); with keys `{ACME-2}` → switched to `main`, `pre.b4` with its count clause where the branch holds an unpushed commit, `b4_left` set.
  - `t_b2`: HEAD on a fast-forward-merged plugin branch, clean → switched to `main`, `pre.deleted`, `b2_left` set; on a squash-merged one → switched, `-d` refused, `pre.delete-failed` with git's first line and `pre.b2-squash`'s `branch -D` line after it, the branch kept.
  - `t_rerun`: after `t_b3_b4`'s B4, `start --rerun --key ACME-2 --key ACME-1-01` → back on `spec/ACME-1-01-x`; with the branch deleted meanwhile → `pre.rerun-failed`.
  - `t_nonff_flush` (R3): `origin/main` moved by another clone before a dirty-session-file start → `next.run` names `replay --for start --branch main`; running each `next` in turn ends with `start --resume`, which returns `next: null`, `stage: "done"`, and `origin/main` holds both changes.
  - `t_budget_resume` (Review Focus 5): three other plugin branches each holding a pushable session-file commit, `--budget 0` → each call makes one capped call and returns `next` naming `start --resume`; following `next` to its end leaves every branch pushed exactly once and the same final state as one call with the default budget on a copy of the same world.
  - `t_replaced` (Review Focus 2): a record of `/idea` from an interrupted run → `start --command /create-ard` reports `replaced: {"command": "/idea", …}` and the new record holds no flag of the old one.
  - `t_exit2_nothing_done` (R2): without `CLAUDE_CODE_SESSION_ID`, and with `--key bad`, exit 2, one line, no record, and `git status`, `HEAD`, the branch list and the refs are as they were.
  - `t_error_after_write` (R2): in process, replace the settle step by one that raises after `t_flush`'s commit → exit-0 result, `error` set, `print` holding the `Environment:` line and `pre.stopped`'s line, the commit pushed, the record saved.
- [ ] **Step 2: Run** the selftest. Expected: FAIL.
- [ ] **Step 3: Implement** `start` as the stages say, the budget check before each capped call, the record saved before the first repository write and at each stage boundary.
- [ ] **Step 4: Run** the selftest. Expected: PASS.
- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git start — specs-preflight by script, resumable, its replays in calls of their own`

### Task 8: Session-branch mode in `start` and `end`

**Files:** Modify `plugins/workflows-core/scripts/specs-git.py` (the mode branches of Tasks 5–7, selftest `scenarios_mode`).

**Interfaces:**
- Consumes: `sb.mode`, `sb.commit`, `sb.lift`, `sb.put_back`, Part 1's `push_scope(…, session_default_ref)`.
- Produces, without changing any CLI shape:
  - `start`: §8.1 at `fetch` (never under misrooted) — `mode`, `session_branch`, the second fetch of the session branch (60 s, silent where it fails); §3.3's G2 variants; §3.4 in the mode — the catch-up wrapped in `lift`/`put-back`, the flush through `sb.commit` (`--include-ahead` where HEAD is the default branch) with `pre.created.*` where it printed `created: true`, the session branch pushed under §8.4's conditions, a rejected session push in its `Specs preflight:` form, a plugin branch's rejection with `reason.session-mode` and `remedy.session-wrap`; §3.5's B2, B4 and the re-run's switch back each wrapped; the closing `put-back` (also where a guard ended the preflight, never under misrooted); `lift`'s `unpreserved` → `sb.commit` with §4 step 4's message, then `lift` again, a second `unpreserved` skipping the move as a refused switch; no identity → nothing committed in the mode, moves unwrapped; an `sb` call raising `NotRun` → `pre.session-not-run`, the run going on.
  - `end`: §4 step 2's catch-up wrapped; step 4 by `sb.commit` (its `committed` and `files` filling the row, `committed: null` → `nothing`); the session branch pushed under §8.4; the rows `pushed-session` (with `<F>` from `diff --name-only -z --no-renames <default-ref>...refs/heads/<session branch>`), `no-identity`, `session-not-run`, the not-pushed rows naming the session branch, `row.session-rejected` and its conflict ending; every session append of SRG §6 in its order, the created append from `session_branch_created` — saved in the record by any `start` call that created the branch but its flush (whose creation `start` prints and nothing repeats), passed as `--session-branch-created`, or set by `end`'s own `sb.commit`; `app.session.unsupported` where `mode` is `unsupported`; on a default-branch push `origin` refused outside the mode, `app.mode-on` (or `app.mode-on.no-identity`).

- [ ] **Step 1: Write the failing selftests**, `scenarios_mode(tmp)`, with `git config workflows.sessionBranch true` and `GIT_USER_INITIALS=ab` unless a case says otherwise:
  - `m_created`: a clean `main` → `start` prints `pre.created.empty` naming `session/ab` and the base sha7; a dirty session file → `pre.created.committed`; the session branch pushed; the overlay in place after `start` (the working copy equals the branch's version).
  - `m_end_pushed`: `end` with a new session file → `pushed-session` naming `session/ab` and `<F>`; `--session-branch-created abc1234` → the created append.
  - `m_no_identity`: no `GIT_USER_INITIALS`, no `user.initials`, no inferable identity → `end`'s `no-identity` row; `start`'s B4 move runs unwrapped.
  - `m_not_run`: `session/ab` checked out in a second worktree → `end`'s `session-not-run` row naming it; `start` prints `pre.session-not-run`.
  - `m_g2`: on `feature/x` → G2's session-branch lines; on `session/ab` itself → its own variant.
  - `m_unsupported`: a `git` shim first on `PATH` that fails `merge-tree --write-tree` (as `session-branch.py`'s selftest builds one) → `mode: "unsupported"`, the run as with the mode off, and `end`'s line ends with `app.session.unsupported`.
  - `m_wrapped_b4`: on an unkeyed plugin branch with the overlay holding a session file → B4 switches, and after `start` the overlay is back over `main`.
  - `m_no_replay`: a plugin branch's settle push rejected in the mode → `reason.session-mode` with the `lift`/`put-back` remedy; `pending` stays empty.
  - `m_canned`: the renderer over canned `sb.commit` results → `sync.conflict` from each source, `sync.error`, `unsettled`, `stranded`, `row.session-rejected` with both endings, the session refused remedy, `app.mode-on` with and without an identity.
- [ ] **Step 2: Run** the selftest. Expected: FAIL.
- [ ] **Step 3: Implement** the mode branches.
- [ ] **Step 4: Run** the selftest, then `python3 plugins/workflows-core/scripts/session-branch.py --selftest`. Expected: both PASS.
- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git — session-branch mode in start and end`

### Task 9: The skill, the loader, the call sites and the references

**Files:**
- Create: `plugins/workflows-core/skills/specs-git/SKILL.md`
- Modify: `plugins/workflows-core/skills/reference/SKILL.md`; the six commands `plugins/workflows-core/commands/{feedback,prompt,prompt-brainstorm,prompt-grill-me,frames,diagnose-session}.md`; `plugins/workflows-core/references/specs-repo-git.md` (intro, banners, §7); `phase-handoff.md` (§4.3); `session-hygiene.md` (§7); `architecture-promotion.md` (§1 step 4); `specs-git.py` (selftest `scenarios_skill`); `docs/superpowers/to-fix.md` (LC31 deleted)
- Regenerate: `plugins/workflows-core/reference-parts/`

**Interfaces:**
- Consumes: the CLI of Tasks 2, 5, 6 and 7, exactly.
- Produces: `Skill(skill: "workflows-core:specs-git", args: "start" | "end" | "declined")`, which the loader and every caller use.

- [ ] **Step 1: Count before** (claim-sweep refinement 7, whitespace-collapsed, refinement 4's scope): ``references/specs-repo-git.md` and execute its`` (expect 12, two in each of the six commands); `executes its steps inline` (expect 3: SRG, `feedback-emission`, `followup-emission` — only SRG's is this batch's claim; the other two describe their own references); `Cite and execute \`specs-preflight\`` and `Cite and execute \`commit-artifacts\`` (expect 1 each, SRG §7); `(\`workflows-core:specs-repo-git\` §3), as a keyless run` (expect 1, `architecture-promotion`); `workflows-core:specs-git` (expect 0).
- [ ] **Step 2: Create the skill** — exactly this text, then cut nothing it says and add nothing it does not:

````markdown
---
name: specs-git
description: Runs a command's specs-repository start (specs-preflight) and end (commit-artifacts) through workflows-core's specs-git.py, which keeps what the two share in a record of its own, and says which returned lines to print and where. Loaded at the start and end of every command that writes into $SPECS_PATH, and by the reference loader for a specs-repo-git specs-preflight or commit-artifacts request.
user-invocable: false
allowed-tools: Bash, Skill
---

# specs-git — a run's specs-repository start and end

The argument names the entry point: `start`, `end` or `declined`. `workflows-core:specs-repo-git` §3 to §8 are the rules, and `${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py` runs them and asks nothing. This text is what your run executes; it never reads that reference to run its start or its end. A run that another command started `--inline` (`/docs-brand` under `/docs-init`) calls none of this.

## The call

Each call is one Bash call, with a timeout of 600000 ms:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" --specs "${SPECS_PATH-}" <start|end> --command /<name> …
```

Where your run took `$SPECS_PATH` from the *Set SPECS_PATH* answer, open the call with `export SPECS_PATH='<the value>';`. Pass:

- `--command /<name>` — the command now running, as its commit message names it: `/create-ard`, `/scan`, `/feedback` — the slash and the name, never the plugin.
- `--key <K>` (start), once for each key of the run key set: every key already resolved when the call is made — the resolved folder's key, and on an `EPIC-` folder its parent PRD's key too; the key each argument carries where your command reads keys off its arguments or off the carrier an `@<path>` names. None where nothing resolved: the run is keyless. Never a key a later phase would mint. Where your command's start paragraph names its key set, take its words.
- `--commit-key <K>` (start and end) — the one key the run addressed: an Epic run's own key, never its parent's; a slice's key; where several, the first resolved. At start, only where it is already resolved. At end, the key your command's commit paragraph names for `<KEY>`. Omit it for none; the commit then reads `NOISSUE`.
- `--register-rebuild <path>` (start and end) — only where your command hands `register_rebuild`: that path.
- `--rerun` (start) — only on a second start in one run with a changed key set: `/document` and `/release-notes`, after the operator entered a slice key at their BRD-container stop.
- `--no-preflight` (end) — where your run stopped before its start call.
- `--misrooted-stdin` (end) — where your run carries `specs_git: misrooted` from anything but this skill's start — `specs-root-check`'s `SPECS_PATH_INSIDE_TREE:` stop, `env-check`'s `Environment changed:` line, or `session-hygiene` §6's `RESUME_ENVIRONMENT_CHANGED:` line — with that notice, verbatim, on stdin: `<<'EOF'`, the notice, `EOF`.
- `--session-branch-created <sha7>` (end) — where a session-branch `commit` or `lift` your command ran itself printed `created: true` (`/implement` keeps it as run-state `session_branch_created`): the `<base short sha>` taken then.

## Start

Make the call where your command's start step stands, once its run key set is known. Then **print every entry of the JSON's `print`, verbatim and in order, as your next output** — the `Environment:` line first, then each notice or line, an entry of several lines inside a `text` fence. These are the lines your command's text tells you to emit at its preflight: print each once. For the rest of the run, read the preflight's results from the same JSON — `specs_git` (`blocked` or `misrooted`), `default`, `default_ref`, `remote`, `offline`, `session_branch`, `branch` and `b2_left` — wherever your command's text reads them.

## End

Make the call where your command's commit step stands: its last action, or the step before a phase that hands the session elsewhere. Its `print` is the run's `Specs repo:` line, then any notice that line repeats, then any line that follows it. Put them where your command says — in its final report, or here as the run's last output — verbatim, in order and once; nothing after them restates the report.

## When the JSON names `next`

Print that call's `print` first. Then run `next.run` exactly as given, as a Bash call of its own with `next.timeout_ms` as its timeout, and treat what it returns the same way, until `next` is null. Where such a call ends with no exit status of its own — the harness stopped it at its timeout — run `next.on_timeout` instead.

## Declined

Where a handoff's consent choice is answered with its second or third option, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" declined --command /<name> --path '<path>'`, one `--path` for each path of that handoff's `deliverable_paths`. It prints nothing for you to show.

## Where the script cannot start

Exit 2 means it did nothing: one `specs-git: not run (…)` line on stderr. Where that line begins `specs-git: not run (usage:`, your call was wrong: correct it and make it again. Otherwise print the line and run this entry point by hand from the reference — `Skill(skill: "workflows-core:reference", args: "specs-repo-git")`, then its §3 for start or its §4 for end — and run your run's other entry point by hand too. JSON with `error` set did part of its work and says so in `print`: print it and go on; never run that entry point again by hand.

## Citations

A citation of `workflows-core:specs-repo-git` §3 to §8, or of its file by path, in a run that calls this skill is served by this text and the script's output: it is no request to read the reference. Two cases read it whole: the fallback above, and a step your command runs by hand from it — its own session-branch `commit`, `lift` or `put-back`, or a commit into a documentation repository in §4 step 4's form.
````

- [ ] **Step 3: Route the loader.** In `skills/reference/SKILL.md`: the second paragraph's closing clause `save, either way, a request the entry-point rules answer from an entry point's own file.` gains `, or one the paragraph on \`specs-repo-git\` below routes or serves`; the paragraph opening `To read the whole reference —` gains the same exception beside its entry-point one; and a new paragraph goes before it, unwrapped:

```markdown
**Two entry points of `specs-repo-git` run in a script.** A request `args: "specs-repo-git specs-preflight"` or `args: "specs-repo-git commit-artifacts"` reads no reference: invoke `Skill(skill: "workflows-core:specs-git", args: "start")` for the first and `args: "end"` for the second, and follow that skill. A request `args: "specs-repo-git"` made for a citation that skill's *Citations* paragraph serves reads nothing more.
```

  The paragraph opening `These entry points read their own file:` is not touched (`check-citations` pins it word for word).
- [ ] **Step 4: Switch the six commands.** In each, the start sentence ``Cite `${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` and execute its `specs-preflight` entry point (§3) inline`` becomes ``Invoke `Skill(skill: "workflows-core:specs-git", args: "start")`, which runs the `specs-preflight` entry point of `${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` (§3) by script, and follow it``, and the end sentence the same with `end`, `commit-artifacts` and §4 — the rest of each paragraph unchanged, the new sentence on one line where its paragraph is hard-wrapped. `diagnose-session.md`'s "with an empty run key set" stays beside it.
- [ ] **Step 5: `architecture-promotion.md` §1 step 4**: `Then \`specs-preflight\` (\`workflows-core:specs-repo-git\` §3), as a keyless run.` becomes `Then \`specs-preflight\` — \`Skill(skill: "workflows-core:specs-git", args: "start")\`, which runs \`workflows-core:specs-repo-git\` §3 by script — as a keyless run.`
- [ ] **Step 6: `phase-handoff.md` §4.3**, its *What each option means* paragraph, after "the producer emits §4.1's "Declined by the user" line either way": `On either, it also records the declared paths for the run's terminal commit, \`Skill(skill: "workflows-core:specs-git", args: "declined")\` with this handoff's \`deliverable_paths\`, so that commit's \`Specs repo:\` line says the deliverable stays uncommitted as the user asked (\`specs-repo-git.md\` §6).`
- [ ] **Step 7: SRG (R1: the step-by-step text stays, and cannot be read as a procedure to run by hand).**
  - The intro's "cites this file and executes its steps inline" becomes "runs them through the `workflows-core:specs-git` skill, which runs `scripts/specs-git.py`; this file is the contract that script follows and is tested against, and the procedure a run follows by hand only where the skill says the script cannot start".
  - Directly under `## 3.` and under `## 4.`, one paragraph each: ``**Run by `scripts/specs-git.py`.** A run reaches this entry point through `Skill(skill: "workflows-core:specs-git", args: "start")` — the loader routes `args: "specs-repo-git specs-preflight"` there — which runs `specs-git.py start` and prints what it returns. What follows in §3 is the rule that script follows and is tested against, and the fallback the skill names where the script cannot start; it is never a procedure to run by hand beside the script.`` (§4: `end`, `commit-artifacts`, `specs-git.py end`, "in §4").
  - Under `## 5.` and `## 6.`: one sentence each — the script renders every block and line below, and a run prints what it returns.
  - Under `## 8.`: inside `start` and `end` the script makes these calls itself; a command that moves the checkout or commits session files by its own text (`/dev-workflows:implement` on a direct run from inside the specs repository) still makes them as this section says.
  - §7 rules 1–3: "Cite and execute `specs-preflight` (§3)" becomes "Run `specs-preflight` (§3) through the skill's `start`", and the same for `commit-artifacts` with `end`; the *One optional input* paragraph adds that the skill passes `register_rebuild` as `--register-rebuild`. Then this paragraph, unwrapped:

```markdown
**The run's state record.** What the two entry points share, and what a run once carried only in its conversation, `scripts/specs-git.py` keeps in one file per Claude Code session, `~/.claude/dev-workflows/specs-git/<session id>.json`, the session id being the harness's `CLAUDE_CODE_SESSION_ID` — the `session_id` `cost-emission.md` §1 reads off the transcript's name. It holds the flags and the notice that set `specs_git: misrooted`, the guard block §4 step 7 repeats and the paths it lists, `<default>`, `<default-ref>`, `remote` and the offline clause, `session_branch`, `mode` and `session_branch_created`, the branches §3.5's B2 and B4 left, the branches §3.4's `-D` advisory has named, the deliverable paths a declined handoff recorded (§6), the run's `Environment:` line, and where an interrupted `start` or `end` stands. `start` opens a fresh one, setting aside whatever the session held — save on a re-run (§3.5) and on its own continuation, which keep the run's own; the skill's `declined` adds to it; `end` reads it and removes it as its last act. **Why it is safe.** It lives outside every repository, so no staging sees it, and `/dev-workflows:implement`'s `run-state.py remove`, which removes files in the code repository's git directory, cannot reach it; one file per session keeps two sessions on one specs repository apart; the session id survives a compaction, which the conversation's text does not; and a nested run starts only after its parent's `end`, which §4's exception places before the hand-off (`/product-workflows:brd-split`'s *Ground now*), so each child's `start` opens a fresh record and nothing of its parent's reaches it. A run started `--inline` by another command calls neither entry point. It is not kept in the specs repository's git directory because §3.1's gate fails exactly where that directory is missing or unwritable, while a not-a-repository `$SPECS_PATH` with a `specs-root-check` signal still sets the flag whose notice `end` repeats. Where `CLAUDE_CODE_SESSION_ID` is unset, the script runs neither entry point (exit 2, nothing done), and the run follows this reference's prose instead.
```
- [ ] **Step 8: `session-hygiene.md` §7**, *The line.*: after "what this one Bash call prints", add ", which `scripts/specs-git.py` runs as written — its selftest holds the two equal".
- [ ] **Step 9: Pin the skill to the CLI.** Selftest `k_skill_options`: every `--<option>` the skill's text names is an option the parser accepts for `start`, `end` or `declined`, and each of `start`, `end`, `declined` is a subcommand; `k_loader_routes`: the loader's text names `workflows-core:specs-git` with `args: "start"` and `args: "end"`. Run it. Expected: PASS.
- [ ] **Step 10: Delete LC31** from `docs/superpowers/to-fix.md` (its whole bullet, sub-bullets included): the script now returns the session branch's creation line and each guard's notice, and the skill makes printing them the run's next output.
- [ ] **Step 11: Count after.** ``references/specs-repo-git.md` and execute its`` 12 → 0; `executes its steps inline` 3 → 2 (SRG's gone); `Cite and execute \`specs-preflight\`` and `… \`commit-artifacts\`` 1 → 0 each; the `architecture-promotion` phrase 1 → 0; ``workflows-core:specs-git", args: "start"`` → 6 commands + the loader + SRG §3's banner + `architecture-promotion` + the skill's own text where it names itself (count and record the figure). Re-derive the thirty-five: `grep -lE 'commit-artifacts\` entry point|args: "specs-repo-git commit-artifacts|workflows-core:specs-git", args: "end' plugins/*/commands/*.md | wc -l` → 35.
- [ ] **Step 12: Regenerate and gate.** `python3 scripts/reference-parts.py generate`, then the gate chain. Expected: `EXIT=0`; `check-citations` passes the loader's pinned paragraph; check 16 counts the loader calls as before.
- [ ] **Step 13: Commit** — `feat(workflows-core): the specs-git skill — every command's start and end runs by script; LC31; D2`

### Task 10: Docs tree, rules and the claim-expiry sweep

**Files:**
- Modify: `plugins/workflows-core/docs/reference/references.md` (the `specs-repo-git.md` entry; § Skills: count, prose, a table row), `plugins/workflows-core/docs/README.md` (`the two bundled skills` → `the three bundled skills`, naming `specs-git`), `plugins/workflows-core/docs/workflow.md` (the opening sentence, a `skills/specs-git` node with a solid edge to the pipeline, "The three solid edges" → four, the paragraph naming the skills), `plugins/workflows-core/README.md` (line 9 names the skill), `.claude/rules/workflows-core.md`, `.claude/rules/workflows-core-git.md`, `CLAUDE.md`, `docs/maintainers/rationale.md`, `.github/workflows/validate-catalog.yml` (the specs-git step's comment)

**Interfaces:** none.

- [ ] **Step 1: Count before**, whitespace-collapsed over refinement 4's scope: `two bundled skills` (expect 2), `Two skills ship` (1), `its \`model-routing\` skill the named one` (1, `CLAUDE.md`), `Both are listed in` (1, `workflow.md`), `The three solid edges` (1), ``(`args: "specs-repo-git specs-preflight"`)`` (1, `CLAUDE.md` § Internal reference convention), `Neither skill reads a file again` (1). Then run the exclusivity probe (refinement 3) over the same scope for the loader and the skills: `the only`, `the sole`, `only way`, `named one`, `Both exist`, `Neither skill` — and the subject sweep (refinement 6) for the preflight and the commit being executed by reading SRG, or SRG being read whole at start and end: grep `read whole`, `reads it whole`, `two reads`, `execute its \`specs-preflight\``, `execute its \`commit-artifacts\``, `specs-repo-git.md\` and execute`. Record each hit and its disposition. Already known: `skills/reference/entry-files.md` holds no such sentence (`grep -c specs-repo-git` → 0) — record that; the other plugins' commands' `execute its … entry point` sentences stay true (the loader routes them) — record that; `docs/superpowers/to-fix.md` PR10 is Task 11's; `docs/maintainers/rationale.md`'s lean-context table row is a dated measurement and stays.
- [ ] **Step 2: Docs.** `references.md`'s `specs-repo-git.md` entry gains: a run reaches both entry points through the `specs-git` skill, which runs `scripts/specs-git.py`, and the reference is the contract the script follows. § Skills: "Three skills ship"; the shared-reason sentence becomes true of the two reading skills and the third is described on its own (it reads no reference: it runs the script and keeps the run's state in a file of its own under `~/.claude/dev-workflows/`); every "Both"/"Neither skill" becomes "Both reading skills"/"Neither reading skill" where it is about reading. Table row, each cell under 200 characters, no `§`: ``| `specs-git` | No — loaded internally, at the start and the end of every command that writes into the specs repository | Runs `scripts/specs-git.py` for a run's specs-repository start and end, keeps their shared state across the run, and says which lines to print. |``.
- [ ] **Step 3: Rules.** `workflows-core.md` *Plugin facts*: "two bundled skills" → three, `specs-git` described in one clause, and the loader's description names its one routing exception (`specs-repo-git specs-preflight` and `commit-artifacts` go to `specs-git`); `specs-git` in the scripts list gains "with its two modules". `workflows-core-git.md`: `paths:` gains `plugins/workflows-core/skills/specs-git/SKILL.md`; its opening line names the skill; the `specs-repo-git` authority paragraph says both entry points run in `scripts/specs-git.py` through the `specs-git` skill, which every request reaches (the loader routes the two requests there), with the state record's home and key and a `([why](../../docs/maintainers/rationale.md#specs-git-state-record))`; its count recipe becomes ``grep -lE 'commit-artifacts` entry point|args: "specs-repo-git commit-artifacts|workflows-core:specs-git", args: "end' plugins/*/commands/*.md``, which "matches the three phrasings" and returns 35. `CLAUDE.md`: the rules-table row for `workflows-core-git.md` names the skill; § Internal reference convention's example becomes `` (`args: "addressing resolve-address"`) `` with ", save `specs-repo-git`'s `specs-preflight` and `commit-artifacts`, which the loader routes to its `specs-git` skill" after it, and "its `model-routing` skill the named one" becomes "its `model-routing` and `specs-git` skills named ones".
- [ ] **Step 4: Rationale.** A section headed `## specs-git-state-record`, the file's convention (each heading is its anchor), its first sentence saying why the state record lives under `~/.claude`, keyed by the session. Its content: the design's candidate was the specs repository's git directory, as `/implement`'s `run-state.py` keeps its file in the code repository's; three facts moved it. (1) SRG §3.1's gate fails exactly where that directory is missing or unwritable — unset, not a repository, a read-only mount — yet a not-a-repository `$SPECS_PATH` with a `specs-root-check` signal sets `specs_git: misrooted`, whose notice `end` must repeat. (2) A resume in another container points `$SPECS_PATH` at another repository, where a record in the first one's git directory cannot be found. (3) Nothing outside every repository is ever staged. The key: `CLAUDE_CODE_SESSION_ID` equals the transcript's basename, the `session_id` `cost-emission` §1 derives by scanning transcripts for the invocation (checked on 2026-11-09), and the family already keeps per-session state beside it (`~/.claude/dev-workflows/cost-state/<session_id>.json`, `cost-emission` §13.1's deferred file). The safety argument as SRG §7's paragraph states it. The fallback where the variable is unset: the prose, exactly as before 2a.
- [ ] **Step 5: CI comment.** The `Self-test the specs-repo git primitives` step's comment names the start and end it now also holds, and their failure mode (a commit made under a flag that should have stopped it; a notice the run must repeat lost to a compaction); the `run:` line is unchanged.
- [ ] **Step 6: Count after and measure.** `two bundled skills` 2 → 0 (`three bundled skills` 0 → 2); `Two skills ship` 1 → 0; `its \`model-routing\` skill the named one` 1 → 0; `Both are listed in` 1 → 0; `The three solid edges` 1 → 0; the `CLAUDE.md` example 1 → 0; `Neither skill reads a file again` 1 → 0. Every rules file under 20,000, `CLAUDE.md` under 36,000.
- [ ] **Step 7: Gate.** The chain. Expected: `EXIT=0` (check 4 finds the row, check 9 reads "three bundled skills", check 6, check 25, the mermaid gate parses the new node).
- [ ] **Step 8: Commit** — `docs(workflows-core): the specs-git skill in the docs tree and the rules; the claim-expiry sweep`

### Task 11: Release

**Files:** Modify `plugins/workflows-core/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (its `workflows-core` entry; the description unchanged), `plugins/workflows-core/CHANGELOG.md`, `.claude/rules/plugin-updates-coupling.md`, `docs/superpowers/to-fix.md` (PR10), `docs/superpowers/to-test-on-real-project.md`.

- [ ] **Step 1: Version.** The next free minor of `workflows-core` on the branch's base — `1.82.0` at `bfa147fd`; where `main` has moved by merge time, the next after it — in both manifests.
- [ ] **Step 2: CHANGELOG**, a dated section (`## [1.82.0] — <date>`), opening: "GIT-G1 Part 2, batch 2a: every command's specs-repository start and end runs by script, through the new `specs-git` skill. Update `workflows-core` alone." `### Added`: the skill; `start`, `end`, `replay`, `declined`, `specs-root-check`; the state record. `### Changed`: the loader's routing and citation rule; the six commands' calls; SRG's fixed wordings, banners and §7; `session-hygiene` §7; `architecture-promotion` §1 step 4; `phase-handoff` §4.3's `declined` call. `### Fixed`: LC31; D2 (*Cancel* gets the append). Docs and rules in one bullet.
- [ ] **Step 3: Coupling bullet**, after the 1.81.0 one: ``- **Update `workflows-core` to 1.82.0 alone**: no dependent changes. 1.82.0's loader routes every `specs-repo-git specs-preflight` and `specs-repo-git commit-artifacts` request — the form every command of the four dependent plugins makes — to its new `specs-git` skill, so updating `workflows-core` switches every command's start and end at once; `phase-handoff` §4.3's new `declined` call is read by every producer from `workflows-core`'s own file. No dependent release needs 1.82.0 and none is needed by it.`` Check its size under 20,000.
- [ ] **Step 4: PR10.** Its closing sentence becomes: Part 2 batch 2a (`workflows-core` 1.82.0) moved the preflight and the terminal commit behind the `specs-git` skill, so a run reads that skill's text and the script's output, not the reference, to run its start and end (measured in `docs/superpowers/verification/2026-11-09-git-g1-part2a.md`); the handover's reads of `phase-handoff` end with Part 3.
- [ ] **Step 5: To-test items**, a new section `## GIT-G1 Part 2, batch 2a — \`workflows-core\` 1.82.0` ("Install it alone."), each item with its setup and what to expect:
  - **LC31** — a run in session-branch mode that creates the session branch prints `Specs preflight: created local session/<identity> at …` straight after its `Environment:` line; a run with a dirty unrelated path prints G1's notice there, and again after its `Specs repo:` line.
  - **The reads** — a keyed `/create-ard` and a `/ready` run's transcripts show no read of `specs-repo-git.md` for the start and the end; record the bytes the skill and the script's output come to.
  - **Compaction** — `/compact` between a misrooted run's start and its end: the end still skips with the notice.
  - **Two sessions** — two sessions on one specs repository, one misrooted: each end reads its own state.
  - **Nesting** — `/brd-split`'s *Ground now* with two children: each `/prd-ground` opens a fresh state, none prints the parent's guard block.
  - **`/implement`** — a keyed run in session-branch mode: its end reports the session branch its Phase 4.6 created.
  - **D2** — a producer's consent answered *Cancel*: the `Specs repo:` line ends `; the deliverable at <path> remains uncommitted, as you asked`.
  - **The replay** — a rejected push at the end: the replay runs as a call of its own and prints its row.
  - **The re-run** — `/release-notes` on a BRD container, a slice key entered at its stop: the second start switches back to the branch the first left.
- [ ] **Step 6: Gate** (the chain; check 18 is unarmed off `main`, the section is dated anyway). Expected: `EXIT=0`.
- [ ] **Step 7: Commit** — `release: workflows-core 1.82.0 — GIT-G1 Part 2 batch 2a`

### Task 12: The verification record — written last

**Files:** Create `docs/superpowers/verification/2026-11-09-git-g1-part2a.md`.

Written after the final whole-branch review's fix pass, against the branch's own tree (`CLAUDE.md` § Editing discipline, *A sub-project's verification record is written last*); every figure re-derived, with its command beside it, none copied from this plan.

- [ ] **Step 1: The script.** `python3 plugins/workflows-core/scripts/specs-git.py --selftest` → its `PASS (<n> checks)` line; one table row per scenario group (`state`, `lines`, `gate`, `end`, `replay`, `start`, `mode`, `skill`) naming the cases it pins, and the *Not pinned* list carried from this plan's pins section, each still true.
- [ ] **Step 2: The reads (design §8, PR10).** Bytes an agent reads to run start and end, before (`bfa147fd`) and after: before = 2 × the loader's `SKILL.md` + 2 × `specs-repo-git.md` + `reference-parts/session-hygiene/env-check.md` (what the old `Environment:` line request loaded); after = 2 × the new loader `SKILL.md` + 2 × `skills/specs-git/SKILL.md` + the JSON of a clean `start` and `end` on a fixture world. `wc -c` each file at each commit (`git show <sha>:<path> | wc -c`); say which reads a run still makes (the fallback, `/implement`'s direct-run session-branch calls, a docs-repository commit's §4 step 4 citation).
- [ ] **Step 3: The command text (design §1).** State the recipe and run it at `bfa147fd` and at the branch tip: the bytes of `plugins/*/commands/*.md`, and of their blank-line-separated paragraphs matching `specs-preflight|commit-artifacts|handoff-to-main|require-on-main|branch-check|specs-repo-git|phase-handoff|workflows-core:specs-git` (this plan measured 4,417,213 and 946,519 at `bfa147fd` with that recipe — re-derive, do not copy; it differs from the design's 770 KB, which used another cut). 2a slims no wrapper, so the figure barely moves: say so.
- [ ] **Step 4: The sweep.** Each Task 9 and Task 10 count, before and after, from the tree.
- [ ] **Step 5: The gates and the budgets.** The chain's `EXIT=0`; `len()` of `CLAUDE.md` and every rules file the batch touched.
- [ ] **Step 6: The review.** The final review's counts by severity, and the fix pass's commit.
- [ ] **Step 7: Commit** — `docs: GIT-G1 Part 2 batch 2a — verification record`

---

## Self-review notes

- **Spec coverage.** Design §5.1: the explicit key set, keyless and Epic forms (`--key`), before or after resolution (the skill's *Start*), the outputs as fields (`start`'s JSON: `default`, `default_ref`, `remote`, read-only as `gate`, `specs_git`, `session_branch`, `b2_left`, `b4_left`), `register_rebuild`, the direct-`/implement` G2 variant, the LC31 lines (Tasks 7, 8, 9); standalone primitives were Part 1's and `specs-root-check` joins them (Task 4); session-branch `commit`/`lift`/`put-back` for a command stay `/implement`'s preparation (out of scope, said). §5.3: the commit stays a call of its own (`end`), the commit key explicit (`--commit-key`), the outcome as fields and as the line (`row`, `sha7`, `line`, `print`), printable in place or held (the skill's *End*), the cede-control placement (the skill's *End*); the tail profiles are TAIL-G1's, the commit-only and refusal tails needing nothing of `end` but `--no-preflight`. §5.5: every requirement, by ruling R5. §6's `/implement`: R6. §6's rule gap (iv): D2, Task 3 and Task 9. §7 Part 2's "all 35 commands switch": the loader (Task 9). §8: the reads and the command text (Task 12). Brief: budget relief first (Task 1); the release, docs entry, CI step, to-test items, record (Tasks 10–12); LC31 deleted with its fix (Task 9).
- **Design §8's call-site gate is not built in 2a.** No wrapper is slimmed in this batch, so a gate over call-site shape would fire on every command still carrying its restated rules; the batch that slims the last wrapper decides whether to build it (design §9 leaves it to the builder).
- **Interfaces.** `state.*`, `lines.*`, `gate`, `resolve_default`, `catch_up`, `commit_session_files`, `push_check`, `push`, `classify_replay` and the five CLI shapes are named once, in the task that produces them, and used by those names after.
- **Proportion.** The plan writes out the skill, the loader paragraph, SRG's new wording and the release text — copy the brief fixes or the reference must hold verbatim — and gives the script as signatures, stage orders and test cases, SRG being the algorithm.

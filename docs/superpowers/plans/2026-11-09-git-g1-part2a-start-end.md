# GIT-G1 Part 2, batch 2a — start and end — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every command's specs-repository start (`specs-preflight`) and end (`commit-artifacts`) runs in `workflows-core`'s `specs-git.py` through one new skill, `specs-git`, with the state the two share kept in a record that survives compaction, so no run reads the 163 KB `specs-repo-git.md` to run either.

**Architecture:** `specs-git.py` gains five subcommands — `start`, `end`, `replay`, `declined` and `specs-root-check` — beside Part 1's primitives, and two helper modules beside it, loaded only by those subcommands: `specs_git_state.py` (the record, one file per session and command) and `specs_git_lines.py` (every notice and outcome line as `specs-repo-git` writes it, pinned to the reference's text by the selftest). It imports `session-branch.py` for the mode, the overlay, the session-branch commit, the bounded git call and the replay. A new skill, `workflows-core:specs-git`, is the only way a command reaches the script; the `reference` loader routes every existing `specs-repo-git specs-preflight` and `specs-repo-git commit-artifacts` request to it, and `workflows-core`'s six commands call it directly. The reference keeps its step-by-step text in 2a, marked as the rule the script follows and the fallback where it cannot start.

**Tech Stack:** Python 3 standard library; git ≥ 2.38 (the replay and the session-branch merge need `merge-tree --write-tree`, as before); the repository's gate chain (`.github/workflows/validate-catalog.yml`).

**Spec:** `docs/superpowers/specs/2026-11-08-git-g1-shared-specs-git-design.md` (§4, §5.1, §5.3, §5.5, §7 Part 2, §8, §10). Evidence: `docs/superpowers/specs/2026-11-08-git-g1-evidence/contract.md` §0, §1, §2, §6, §7, §8; audit-A §2 (items 1, 2, 4, 12–15), audit-B §13(2) (N9, N11–N14, C4, C5), audit-C (2) (N8, N9, the tail profiles). The reference the script implements: `plugins/workflows-core/references/specs-repo-git.md` (SRG below) §1–§8. Part 1, the style this plan follows: `docs/superpowers/plans/2026-11-08-git-g1-part1-script-core.md` and its record `docs/superpowers/verification/2026-11-08-git-g1-part1.md`. The plan's independent review (READY WITH CHANGES) and the coordinator's rulings on it, 2026-11-09, are folded in below.

## The maintainer's decisions (2026-11-09)

- **D1 — all at once.** The loader routes every existing start and end request to the new skill in 2a; later batches only slim each command's own wrapper. A script bug reaches every command at once, offset by the selftest, the narrow fallback to the reference's prose where the script cannot start, and a live round right after 2a.
- **D2 — *Cancel* gets the same append.** On `phase-handoff` §4.3's option 3, as on option 2, the `Specs repo:` line appends `; the deliverable at <path> remains uncommitted, as you asked`. SRG §4.1 and §6, and every copy of the rule a sweep finds, say so.
- **D3 — `end` with no record re-tests §3.1's placement.** Where `end` runs with no record of a preflight (a run that stopped before it, `--no-preflight`, or a record `declined` alone created), it also runs §3.1's two placement tests — `specs-root-check`'s signals and the below-top-level test — and takes the `specs_git: misrooted` outcome with that notice where one fires: such a run would otherwise stage top-relative paths from below the top level, which `git add` cannot find, or commit into a repository its preflight would have flagged.
- **D4 — every `end` compares the run's environment.** Every `end` compares the `SPECS_PATH` half of a fresh `Environment:` line — `$SPECS_PATH`'s real path and its `origin` — with the same half of the line its start recorded. A mismatch is `session-hygiene` §7's environment change: `specs_git: misrooted`, with §7's `Environment changed:` notice built from the two whole lines, nothing committed. That covers `--specs ""` against a recorded path, and a different repository. The `REPOS_PATH` half stays `env-check`'s, which the tail runs, since a run `session-hygiene` §6 pinned exports its own per call. The rule is written where the contract lives — SRG §4 step 1, §3.1's list of what sets the flag, `session-hygiene` §7's *Callers*, the "Two run-wide flags" bullet of `workflows-core-git.md` — so the prose fallback and the script agree, and every other sentence listing the flag's setters is swept (Task 3 Step 1; the rules bullet in Task 10 Step 5).

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
- **Imports, never copies**, extended: `sb.commit`, `sb.lift`, `sb.put_back`, `sb.mode`, `sb.replay`, `sb.Partial`, `sb.refusal_record`, `sb.git_bounded`, `sb.KILL_AFTER`, `sb.rev`. **The two new modules load only for the new subcommands**, inside their dispatch, so a missing or broken one is a `not run` line for those subcommands and leaves Part 1's primitives running.
- **Bounded calls.** Every git call that can hang — `fetch`, `pull`, `push`, `ls-remote` — runs through `sb.git_bounded(root, seconds, …)` (process-group kill, `workflows-core:bounded-run`'s mechanism): fetch, pull and push 60 s, `ls-remote` 30 s; a capped push or pull is reported in the words Task 3 writes into SRG. `start` keeps a budget of 480 s per call (`--budget`, default 480) and stops before a capped call, or a wrapped move holding one, that could cross it, returning `next` (Task 7). The skill runs `start` and `end` with a Bash timeout of 600000 ms and `replay` with 420000 ms (SRG §4 step 6).
- **The script asks nothing and decides no wording the references do not fix.** Every line it prints is a template in `specs_git_lines.py` that the selftest finds, verbatim, in SRG, `workflows-core:addressing` §3 or `workflows-core:session-hygiene` §7 (Task 3); a line SRG left unworded gets its wording written into SRG first (Task 3).
- **The session variable is never written with a `$`** in any file under `plugins/` — always plain `CLAUDE_CODE_SESSION_ID` — since `check-docs.sh` checks 5 and 9 read every `$NAME` there as a variable the plugin reads and must document.
- **The selftest touches no real home and no real session.** It pops `CLAUDE_CODE_SESSION_ID` and `GIT_USER_INITIALS` from its own environment and gives every scenario a `HOME` and a session id under its temporary directory, as Part 1's selftest pins `GIT_CONFIG_GLOBAL`.
- **Budgets**, measured as Python `len(open(f, encoding='utf-8').read())`: every `.claude/rules/*.md` under 20,000, `CLAUDE.md` under 36,000 — after every task that touches either. Re-derive every number written into `CLAUDE.md` or a rules file against the tree, with the command beside it (`CLAUDE.md` § Editing discipline).
- **Gates**, run as one `&&` chain and read by its own printed status, from the worktree root:

```bash
python3 scripts/validate-catalog.py --selftest && python3 scripts/validate-catalog.py && ./scripts/check-id-grammar.sh --selftest && ./scripts/check-id-grammar.sh --root . && ./scripts/check-id-grammar.sh --baseline && ./scripts/check-docs.sh --selftest && ./scripts/check-docs.sh --root . && python3 scripts/reference-parts.py --selftest && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && python3 scripts/reference-parts.py check-branch-check && npm ci --prefix scripts/mermaid --ignore-scripts --no-audit --no-fund && node scripts/mermaid/check-mermaid.mjs --selftest && node scripts/mermaid/check-mermaid.mjs --root . && python3 plugins/workflows-core/scripts/session-cost.py --selftest && python3 plugins/dev-workflows/scripts/secret-scan.py --selftest && python3 plugins/dev-workflows/scripts/run-state.py --selftest && python3 plugins/dev-workflows/scripts/pieces.py --selftest && python3 plugins/product-workflows/scripts/architecture-harvest.py --selftest && python3 plugins/product-workflows/scripts/promotion-signals.py --selftest && python3 plugins/product-workflows/scripts/proposal-record.py --selftest && python3 plugins/product-workflows/scripts/ledger-evidence.py --selftest && python3 plugins/product-workflows/scripts/bundle-scan.py --selftest && python3 plugins/security-workflows/scripts/register.py --selftest && python3 plugins/docs-workflows/scripts/key-discovery.py --selftest && python3 plugins/workflows-core/scripts/bounded.py --selftest && python3 plugins/workflows-core/scripts/lineage.py --selftest && python3 plugins/workflows-core/scripts/tree-snapshot.py --selftest && ( ok=1; for n in bounded.py tree-snapshot.py; do for d in plugins/*/; do if [ -f "$d/scripts/$n" ] && ! cmp -s "plugins/workflows-core/scripts/$n" "$d/scripts/$n"; then ok=0; fi; done; done; [ "$ok" = 1 ] ) && python3 plugins/workflows-core/scripts/session-branch.py --selftest && python3 plugins/workflows-core/scripts/specs-git.py --selftest; echo "EXIT=$?"
```

  `EXIT=0` is a pass. Where `scripts/` is unchanged, `check-docs.sh --selftest` may be skipped locally, as Part 1 did; it is never skipped in the final run.
- **Identity quarantine and vendor neutrality** (`check-docs.sh` checks 10, 13, 14, 19): no new text names a tracker, the organisation this plugin came from, or, on a `docs/` page, the marketplace; no `§`, decision id or `<plugin>:<reference>` token on a `docs/` page (check 25); no table cell above 200 characters (check 6).
- **Commits.** Immediately before each: `git branch --show-current` prints `feat/git-g1-part2a` (the worktree `/workspace/.worktrees/git-g1-part2a`; never `git checkout` in `/workspace/ai-workflows`). Each message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. No push.
- **What changes outside `workflows-core`** (ruling R7, amended): no command, agent, reference, script or skill of another plugin. Only `docs/` pages whose claims the batch makes false — `security-workflows`' workflow page; the four other plugins' getting-started pages (`dev-workflows`, `docs-workflows`, `guideline-reviewers`, `product-workflows`), which carry the skill-listing figure; and the four other plugins' `reference/environment.md` pages (`dev-workflows`, `docs-workflows`, `product-workflows`, `security-workflows`), which say when a run compares its environment — each plugin with one docs-only patch release (Tasks 10, 11).

## Review Focus

1. **Two sessions on one specs repository at once, a command typed mid-run (`/feedback` during a `/specify`), and a compaction between a run's start and its end.** Each `end` must read the record of its own session and command and no other; a reasonable person expects one run's misrooted flag never to skip another's commit, and its guard block never to print under the other's line. Test in Task 5 (`e_two_sessions`) and Task 7 (`t_two_commands`).
2. **A stale record of the same command, left by a run the user interrupted, then a new run that stops before its preflight.** `end --no-preflight` must ignore and remove it, and a new `start` must replace it; the stale run's flags must never decide the new run's commit. Test in Task 5 (`e_stale_no_preflight`) and Task 7 (`t_replaced`).
3. **A `$SPECS_PATH` with a trailing slash, through a symlink, relative, nonexistent, holding a space, or taken from the *Set SPECS_PATH* answer.** The `Environment:` line the script prints must equal, byte for byte, what `session-hygiene` §7's Bash call prints in the run's own shell — otherwise every later `env-check` reads *Environment changed* and the run commits, hands off and records nothing. Test in Task 4 (`g_env_line_equal`).
4. **A declined deliverable the run later commits (the consent asked again and answered *Yes*), and a declined set of several paths with spaces or non-ASCII names.** The `Specs repo:` line must name only what is still uncommitted, in `phase-handoff` §4.1's `<artifacts>` form. Test in Task 5 (`e_declined`).
5. **A preflight with several plugin branches each holding pushable commits, and a slow origin.** `start` must stay inside its Bash call's timeout, must not lose or repeat a branch's push between calls, and must never return between a `lift` and its `put-back`. Test in Task 7 (`t_budget_resume`) and Task 8 (`m_budget_overlay`).

## Rulings this plan takes

The plan's own calls where the brief left them to the builder; the cost of each if wrong is in the final report.

- **R5 — the record's key and home.** One file per Claude Code session and command: `~/.claude/dev-workflows/specs-git/<session id>/<command>.json`, `<command>` the command's name without its slash. The session id is `CLAUDE_CODE_SESSION_ID`, documented on Claude Code's environment-variables page (<https://code.claude.com/docs/en/env-vars>): set in every Bash tool subprocess, equal to the hook input's `session_id` and updated on `/clear` — and the same value `workflows-core:cost-emission` §1 derives as `session_id` from the transcript's name (checked: the variable equals the transcript basename), read directly instead of by scanning transcripts. The family already keeps per-session state there (`cost-emission`'s `~/.claude/dev-workflows/cost-state/<session_id>.json` and its §13.1 deferred file). **Not the specs repository's git directory**, the design's "obvious candidate" and R6's premise, for two reasons: SRG §3.1's gate fails exactly where a git directory is missing or unwritable (unset, not a repository, a read-only mount), yet a not-a-repository `$SPECS_PATH` with a `specs-root-check` signal sets `specs_git: misrooted`, whose notice `end` must repeat; and nothing outside every repository is ever staged. **Why it is safe:** the session id survives compaction, which the conversation's text does not; one file per session and command keeps two sessions on one repository apart, and keeps a command typed mid-run (`/feedback` during a `/specify`) off the outer run's record; `run-state.py remove` deletes only files in the code repository's git directory, so the record outlives it; a nested run (`/brd-split`'s *Ground now* starting `/prd-ground`, one child after another) is another command, and starts only after its parent's `end` anyway (SRG §4's cede-control exception); an `--inline` run calls neither entry point. **Subagents carry their parent's session id** (`CLAUDE_CODE_CHILD_SESSION=1` beside it), which is harmless because no agent calls `start`, `end` or `declined`: `grep -lE 'args: "specs-repo-git (specs-preflight|commit-artifacts)|workflows-core:specs-git' plugins/*/agents/*.md | wc -l` → 0 at `bfa147fd`, and Task 10 re-runs it. **Where the id changes mid-run** — a `/clear`, or a resume that hands the run a new id — `end` finds no record and runs as D3 and the no-preflight path say, with the flags the run passes; what such a run loses is the repeated guard block and the declined append. Where the variable is unset or malformed, `start`, `end`, `declined` and `replay` exit 2 before any write and the run takes the reference's prose, as it does today.
- **Record lifecycle.** `start` opens a fresh record for its session and command, saved (stage `fetch`) right after its argument and session checks, before the fetch, and sets aside whatever one stood there (reported as `replaced`), save `--rerun` and `--resume`, which continue it (`--rerun` with no record opens a fresh one). **`--resume` continues a record only where its stage is not `done`, its saved arguments equal the call's, and it was saved within the last 15 minutes**; otherwise it runs as a fresh start — so a first call killed before its first write never hands an earlier run's flags to its resume. `declined` adds paths, creating a record marked `started_by_script: false` where none stands; `end` reads it and removes it as its last act, or `replay --for end` does where `end` handed it a replay. **`start` prunes**, right after saving its own record: every record file in `~/.claude/dev-workflows/specs-git/` last modified more than 7 days ago is removed, and a session directory left empty with it — never one of the current session's.
- **R3 — the replay's own call, in SRG's order.** A non-fast-forward rejection is never replayed inside `start` or `end`. A rejected push of the current branch in §3.4's flush or retry returns at once, before the settle loop, with `next` naming `replay --for start`, whose own `next` names `start --resume`, which begins the settle loop ("Then, either way, settle every other local plugin branch" — after the current branch's replay, as SRG has it). A rejection inside the settle loop is queued in the record's `pending` list, the loop goes on, and once it ends `start` returns `next` naming the first queued replay; each `replay --for start` names the next one, and the last names `start --resume`, which runs §3.5 and the mode's closing `put-back`. `end` returns `next` naming `replay --for end`, which prints the `Specs repo:` line. `next` is `{"run": "<the exact shell line>", "timeout_ms": 420000 | 600000, "on_timeout": "<shell line>" | null}`; the skill runs `next.run` verbatim as a Bash call of its own, and `next.on_timeout` (`replay … --timed-out`) where the harness ends that call.
- **The start budget.** 480 s per call; before each capped call, and before each `lift` of a wrapped move that holds one, `start` checks that the elapsed time plus the cap plus `sb.KILL_AFTER` stays inside it, and otherwise saves its stage and returns `next` naming `start --resume` (timeout 600000 ms). A call always makes at least one capped call before it may stop, so every call makes progress, and no call returns between a `lift` and its `put-back`.
- **Wording SRG leaves free** is fixed in SRG by Task 3, then pinned: the B4 report; the non-repository and below-top-level notices; B2's success line; the failed pull and failed deletion lines; the re-run's failed switch back; the `Specs preflight:` forms of *push FAILED*, *Locked*, *Commit failed* and of a session-branch call that could not run; a capped push's and pull's reason; and the two "stopped early" lines.
- **The offline note is carried, not printed.** `start` returns `offline: true` and `offline_clause`, and prints nothing for it, so SRG §1 rule 7's "otherwise silent unless it acts, a guard fires, or §3.1 reports" and §3's "silent when…" stay true, and so do the thirty commands that restate that sentence; `phase-handoff` §3.6 already says the clause where its gate reads against the stale ref.
- **Citations (M1, N7).** The loader's paragraph on `specs-repo-git` scopes them, and the skill's *Citations* section points at it: every command that commits loads the loader before its preflight (`run-flags strip-run-flags`, `escalation-rules core`), while the skill is loaded only at the start call, so a Phase 0 citation meets the loader first. Served, with no read of the reference: every citation of `specs-repo-git`, by name or path, in the command's own start or end step — the paragraph that makes the start or end request or calls the skill, and the commit step — and, anywhere in the command's own text, a citation of §3.2's run key set, of §5 (the notices the script prints) or of §6 (the lines it renders). **The run-key-set rule a Phase 0 citation needs** is in front of the run by the cheapest true route: its one copy is a ~1 KB file, `skills/specs-git/run-key-set.md`, which the loader's paragraph names for that citation and the skill's `--key` bullet names too. Read once, the loader's reuse rule lets every later citation and the start call use it. The rejected options cost more: stating the rule in the loader puts ~900 characters into each of a run's ten or more loader requests; naming the skill's own file has a Phase 0 citation read its 5–6 KB. The file is checked sentence by sentence against §3.2 (Task 9 Step 8a). Every other citation reads the reference as before — one elsewhere in the command, a step of another reference applying one of its rules (`phase-handoff`'s three entry points, until Part 3), a command's own session-branch call, a docs-repository commit in §4 step 4's form, the fallback — and Task 11's to-test item and Task 12's second table name those reads. **Measured at `bfa147fd`** (the recipe is Task 12 Step 2's): of the 272 paragraphs in `plugins/*/commands/*.md` that cite the reference, 77 are served and 195 still read it. Without the rule, the restated start and end wrappers, which cite §3.1, §3.2, §3.3, §5 and §6, would each reload the 163 KB file for a lookup, as lean context D measured for `phase-handoff`'s citations (`docs/maintainers/rationale.md`, *Why a citation of a section the file holds reads the file*).
- **The loader routes by a Skill call**, `Skill(skill: "workflows-core:specs-git", args: "start" | "end")`, never by reading the skill's file, so `${CLAUDE_PLUGIN_ROOT}` in the skill expands to `workflows-core`'s root; the loader's `allowed-tools` gains `Skill`.
- **The `Environment:` line is printed by the script**, which runs `session-hygiene` §7's Bash call character for character (pinned), so a run no longer loads `session-hygiene env-check` for its start.
- **The skill-listing figure (N6).** The root `README.md` and five getting-started pages say the marketplace's share of Claude Code's skill listing is "about 5,800 characters". `git log -S` finds it set at `649e8454` (5,600) and `1f72f4fd` (5,800), with no recipe recorded. A recipe that re-derives it from the catalog, each listed entry being `- <plugin>:<name>: <description><when_to_use>` and a line break (5 characters of overhead, as `docs/maintainers/rationale.md`'s *typed-only-commands* measured in the binary), reproduces both — 5,556 at `649e8454` and 5,866 at `1f72f4fd` — and gives 3,184 at `bfa147fd`: the figure has been stale since `obsidian-llm-wiki` left the catalog (`e003f181`, 2026-10-26). With the `specs-git` skill (24 + 153 + 5 = 182) it is 3,366, "about 3,400". So all six places change, and the four other plugins whose getting-started pages carry it ship docs-only patches. The recipe goes into `docs/maintainers/rationale.md` beside the figure's history, and the README's sentence points at it (Task 10).
- **Inputs a command's text never states** reach the script as options the skill defines: `--command`, `--key`, `--commit-key`, `--register-rebuild`, `--rerun`, `--no-preflight`, `--misrooted-stdin` (a misrooted notice set outside the script — `specs-root-check`'s stop, `env-check`, `session-hygiene` §6's *Stop* — on stdin; empty stdin is the misrooted row with no repeated notice), `--session-branch-created` (a creation by a session-branch call the command or its handoff made), `--declined` (paths a `declined` call could not record) and `--resume` (a `start` or `end` call the harness stopped).
- **B2 prints a line when it acts**, §3.4's `Specs preflight: deleted merged <branch>`; SRG §3.5 says so after Task 3.
- **The G2 variant for a direct `/implement` run from inside the specs repository** is chosen by the script: `--command /implement` and the current directory's top level equal to `$SPECS_PATH`'s.
- **`--rerun`** carries the earlier start's flags (OR), its `-D` advisories, its B4 branch and its declined paths; the guard block repeated at the end is the last one fired.
- **§5's `<path list>`** is comma-separated on the *Found* line and shell-quoted, space-separated, on the *Fix* line; a variant line SRG gives in prose (G2's session-branch and direct-`/implement` variants) is rendered unwrapped on its one line.
- **File layout.** Orchestration and its selftest stay in `specs-git.py` (the `session-branch.py` precedent); the record and the templates are two modules beside it, so the two pure concerns are tested and pinned on their own.
- **R6, confirmed against `/implement`'s text.** Its terminal paragraph reads `specs_git`, `key` and `session_branch_created` from run-state before `run-state.py remove` and then requests `commit-artifacts`; the loader routes that to `end`, which reads `specs_git` from its own record and takes `key` and `session_branch_created` as `--commit-key` and `--session-branch-created`, both of which the run holds at that point. The record is outside every repository, so the removal cannot reach it. **One thing does not change in 2a:** on a direct run from inside the specs repository in session-branch mode, `/implement`'s own `lift`, `put-back` and `commit` calls (its Phase 1.4, Pre-Phase 3 and Phase 4.6) are by hand from SRG §8.2–§8.3, so such a run still reads the reference for them — the `dev-workflows` batch's preparation (design §6).
- **R7, amended.** No command, agent, reference, script or skill outside `workflows-core` changes: the other plugins' loader requests are routed; `/security-workflows:scan`'s `register_rebuild` path is already expanded in its command body; `/document` and `/release-notes` name their re-run; `/promote-decisions` reaches the preflight through `workflows-core:architecture-promotion` §1 step 4, which Task 9 edits. What does change is docs: `security-workflows`' workflow page lists what a run writes under `~/.claude/` and ends "Nowhere else.", which the record makes false (`security-workflows` 0.11.1); and the skill-listing figure ("about 5,800 characters"), in the root `README.md` and in the getting-started pages of `dev-workflows`, `docs-workflows`, `guideline-reviewers`, `product-workflows` and `workflows-core`, stale since 2026-10-26 and moved again by the new skill, becomes "about 3,400" (the ruling above); and each `reference/environment.md` that says when a run compares its environment gains the terminal commit (D4) — one docs-only patch of each other plugin whose pages change.

## Out of scope (later batches)

- **The per-command wrapper slimming** — 2b onward, one plugin or command family per batch, `/implement`'s preparation in the `dev-workflows` batch.
- **The tail-profile names** — defined in SRG §4 by the first group batch whose commands cite them (2b); TAIL-G1 later has the skill run a profile's other members.
- **Retiring SRG's step-by-step text** — in the last Part 2 batch, after the live round that follows 2a has run the script on real repositories; that batch decides whether a prose fallback stays (ruling R1).
- **Part 3** — `handoff-to-main`, `require-on-main`, `branch-check`, and `inputs_read` with its per-phase call. Until then those entry points read `phase-handoff`'s files, and SRG wherever they apply one of its rules.
- The record holds the `Environment:` line already, unread in 2a, for TAIL-G1's `env-check`.

## File map

| File | Change | Task |
|---|---|---|
| `.claude/rules/plugin-authoring.md` | Create: `CLAUDE.md`'s taxonomy and Karpathy sections, moved | 1 |
| `.claude/rules/workflows-core-handoff.md` | Create: `workflows-core-git.md`'s `phase-handoff` paragraph, moved | 1, 10 |
| `CLAUDE.md`, `.claude/rules/workflows-core-git.md`, `workflows-core.md`, `gates-validate-catalog.md`, `security-workflows.md` | Relief and pointers (1); skill, loader and record facts (10) | 1, 10 |
| `plugins/workflows-core/scripts/specs_git_state.py` | Create: the record | 2 |
| `plugins/workflows-core/scripts/specs_git_lines.py` | Create: templates, `fill`, pins | 3 |
| `plugins/workflows-core/scripts/specs-git.py` | Modify: lazy imports, `declined`, `specs-root-check`, `end`, `replay`, `start`, mode, selftest | 2–9 |
| `plugins/workflows-core/references/specs-repo-git.md` | Fixed wording, D2, D3 (3); banners, §1 rule 8, caller contract, state record (9) | 3, 9 |
| `plugins/workflows-core/references/phase-handoff.md` | §4.3: the `declined` call on options 2 and 3 | 9 |
| `plugins/workflows-core/references/session-hygiene.md`, `architecture-promotion.md` | §7 note; §1 step 4's call | 9 |
| `plugins/workflows-core/skills/specs-git/SKILL.md`, `run-key-set.md` | Create | 9 |
| `plugins/workflows-core/skills/reference/SKILL.md` | The routing paragraph, its scope, `allowed-tools` | 9 |
| `plugins/workflows-core/commands/{feedback,prompt,prompt-brainstorm,prompt-grill-me,frames,diagnose-session}.md` | The start and end call phrases | 9 |
| `plugins/workflows-core/reference-parts/**` | Regenerated | 3, 9 |
| `plugins/workflows-core/docs/**`, `plugins/workflows-core/README.md` | The skill's docs entry, counts, the loader's routing | 10 |
| `plugins/security-workflows/docs/workflow.md` | The record among what a run writes | 10 |
| `plugins/{workflows-core,dev-workflows,docs-workflows,product-workflows,security-workflows}/docs/reference/environment.md`; `workflows-core`'s `docs/reference/references.md` | The terminal commit's environment check (D4) | 10 |
| `README.md`; `plugins/{dev-workflows,docs-workflows,guideline-reviewers,product-workflows,workflows-core}/docs/getting-started.md` | The skill-listing figure | 10 |
| `docs/maintainers/rationale.md` | `## specs-git-state-record` | 10 |
| `.github/workflows/validate-catalog.yml` | The specs-git step's comment | 10 |
| `plugins/workflows-core/CHANGELOG.md`, `.claude-plugin/plugin.json`; the same for `security-workflows` and each plugin whose page moved; `.claude-plugin/marketplace.json`; `.claude/rules/plugin-updates-coupling.md`; `docs/superpowers/to-fix.md`; `docs/superpowers/to-test-on-real-project.md` | Release | 11 (LC31's deletion: 9) |
| `docs/superpowers/verification/2026-11-09-git-g1-part2a.md` | Create, last | 12 |

## The pins — every line the script renders

Every line is a template in `specs_git_lines.T`, and Task 3's `pins` check finds each template in its source, whitespace-collapsed. The **Test** column says how its use is held besides: **E** end to end on temporary repositories and a bare `origin`, **C** rendered from canned facts in process (the behaviour behind it is `session-branch.py`'s and pinned by its selftest).

| Item | Source | Task | Test |
|---|---|---|---|
| `Environment:` line | `session-hygiene` §7 (the command, not a template) | 4 | E, byte-equal to the Bash call |
| Non-repository notice; where `specs-root-check` finds a signal, its stop in the form `addressing` §3 picks and its left-behind line | SRG §3.1 (Task 3); `addressing` §3 | 4 | E: a mount named `specifications` (one-line form), one otherwise named (two-readings form) |
| Inside-tree notice: the one-line, stray-folder and two-readings forms; left-behind line | `addressing` §3 `specs-root-check` | 4 | E (each form) |
| Below-top-level notice | SRG §3.1 (Task 3) | 4 | E |
| `Environment changed:` notice (`end`'s environment compare) | `session-hygiene` §7 | 5 | E |
| G0, G1, G2 blocks | SRG §5 | 7 (G0 also 5) | E |
| G2 session-branch variants (another branch; the session branch itself) | SRG §5 | 8 | E |
| G2 direct-`/implement` variant | SRG §5 | 7 | E |
| Failed pull (catch-up, B2, B4), capped pull | SRG §3.4, §3.5 (Task 3) | 7 | E |
| Merged-branch flush cherry-pick line | SRG §3.4 | 7 | E |
| Flush *Locked* and *Commit failed* forms | SRG §6 (Task 3) | 7 | E |
| Settle: deleted merged; failed `-d`; `-D` advisory with `rm -f`; pushed N left on | SRG §3.4 | 7 | E (advisory once per run across `--rerun`) |
| B2: deleted line; configuration left over; squash `-D` line | SRG §3.5 (+ Task 3) | 7 | E (config left over: C, needs an unwritable `.git/config`) |
| B2's and the settle loop's removal of a deleted branch's push-refusal record (file and config key) | SRG §1 rule 8, §3.4, §3.5 | 7 | E |
| B4 report, with and without the commit count | SRG §3.5 (Task 3) | 7 | E |
| Misrooted stay line, both variants | SRG §3.5 | 7 | E |
| Re-run's failed switch back | SRG §3.5 (Task 3) | 7 | E |
| `Specs preflight:` *push refused* (recorded; unrecorded) and *push FAILED* (git's; capped) forms | SRG §4 step 6, §6 (Task 3) | 7 | E (refused via a `pre-receive` hook); unrecorded: C |
| Session branch created, both forms; session-branch call could not run | SRG §3.4, §8 (Task 3) | 8 | E |
| Stopped-early lines (start, end) | SRG §1 rule 5 (Task 3) | 7, 5 | C (in-process injected failure) |
| §6 rows: pushed on a plugin branch; pushed straight to default | SRG §6 | 5 | E |
| §6 rows: not ours; no remote; pushed elsewhere; remote deleted (+ default tail); origin lacks; refused before (file and config-key records) | SRG §6 | 5 | E |
| §6 rows: push refused (record file; config fallback; unrecorded) | SRG §6 | 5 | E (file); C (fallbacks: need an unwritable common dir) |
| §6 row: push-scope (path; merge; no file; hook variant with `[, and <M-1> more]`) and the hook line | SRG §6 | 5 | E |
| §6 rows: push FAILED (git's reason; capped); nothing to commit; locked; commit failed; blocked; misrooted (with a notice; with none); silent | SRG §6 | 5 | E |
| §6 rows: replayed and pushed (+ dropped clause); already there; push rejected (reason clauses, `would-overwrite`'s `[ and <M> more]`) | SRG §6, §4 step 6 | 6 | E (conflict-free replay, already there, `register-rebuild`, `checked-out`); C (the other reasons) |
| §6 row: moved, not pushed — its `<why>`s, optional clauses and refused form; register clause; `upstream_error` | SRG §6 | 6 | C |
| The 420 s timeout reason clause; `session-branch.py could not run` and `stopped` clauses | SRG §4 step 6 | 6 | E (`--timed-out`); C |
| Remedies: switch first on a branch not stood on; `checked-out`; `checkout-moved` (none); session wrapper | SRG §4 step 6, §6 | 6, 8 | E (switch first, `checked-out`); C |
| §6 rows: pushed on the session branch (`<F>`); no identity; session-branch could not run | SRG §6, §8 | 8 | E |
| Session appends: created; `sync.conflict` (two sources); `sync.error`; `unsettled`; `stranded`; `unsupported`; session *push rejected* (two endings); refused remedy for the session branch; default-branch refusal turning the mode on (with and without an identity) | SRG §6 | 8 | E (created, unsupported via a `git` shim on `PATH`, as `session-branch.py`'s selftest does); C (the rest) |
| Declined append (D2) and the singular file count | SRG §6 | 5 | E |

**Not pinned by the selftest, and why:** whether a run prints `print` verbatim at the point the skill says, follows `next`, and passes the inputs the skill defines (agent behaviour — the live round, Task 11's to-test items); whether `CLAUDE_CODE_SESSION_ID` stays the same across a compaction and a resume in practice (live round); the 420 s harness timeout itself (its rendering is pinned through `--timed-out`); a host's own refusal wording (one `pre-receive` refusal is pinned; the reason text is git's); an unwritable `.git` or common directory when the selftest runs as root (those cases skip under `os.geteuid() == 0`, as `session-branch.py`'s do, and fall back to C); `checkout-moved` and `stranded`, which need a concurrent session or a refused default push (C here; `session-branch.py`'s selftest holds the behaviour).

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

- [ ] **Step 2: Move `CLAUDE.md`'s two sections**, keeping them as near always-on as they were. Create `.claude/rules/plugin-authoring.md`:

```markdown
---
paths:
  - "**"
---

# Plugin authoring — the command, agent and skill taxonomy, and the Karpathy notes

Loaded when any file is read (`paths: "**"`), as near to always-on as a rules file comes: it was always-on in `CLAUDE.md`, and moved out to keep that file under its 36,000-character warning, as `claim-sweep.md` and `plugin-updates.md` were; evidence is in `docs/maintainers/rationale.md`.
```

followed by `## Command, agent, and skill taxonomy` and `## Behavioral guardrails (Karpathy) — marketplace-specific notes` with their bodies **verbatim**, save the one link, rewritten `../../docs/maintainers/rationale.md#typed-only-commands`. Delete both sections from `CLAUDE.md`. Add to its rules table, after the `plugin-updates.md` row: ``| `plugin-authoring.md` | `**` (any file) | the command, agent and skill taxonomy; the Karpathy notes |``. In `gates-validate-catalog.md`, `(\`CLAUDE.md\` § Command, agent, and skill taxonomy)` becomes `(\`.claude/rules/plugin-authoring.md\`)`.

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
- Modify: `plugins/workflows-core/scripts/specs-git.py` (the lazy module loader, `declined`, `Parser.error`'s `usage: ` prefix, selftest `scenarios_state`)

**Interfaces:**
- Produces, in `specs_git_state` (imported as `state`):
  - `class NoSession(Exception)` — `specs-git.py`'s `main()` reports it as `not run`.
  - `session_id() -> str` — the `CLAUDE_CODE_SESSION_ID` environment value, matching `^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$`; anything else raises `NoSession("CLAUDE_CODE_SESSION_ID is unset or not a session id")`.
  - `root() -> str` — `os.path.join(os.path.expanduser("~"), ".claude", "dev-workflows", "specs-git")`, resolved at call time.
  - `path(session: str, command: str) -> str` — `os.path.join(root(), session, command.lstrip("/") + ".json")`; `command` matching `^/[a-z][a-z0-9-]*$`, else `ValueError`.
  - `FIELDS: dict` — the record's keys and defaults, exactly: `version` 1, `session` "", `command` "", `started` "", `updated` "", `args` {} (the start call's arguments: `specs`, `keys`, `commit_key`, `register_rebuild`), `started_by_script` True, `specs` "", `env_line` None, `gate` None, `top` None, `keys` [], `commit_key` None, `register_rebuild` None, `specs_git` None, `misrooted_notice` None (list of lines), `guard` None, `guard_block` None, `guard_paths` [], `default` None, `default_ref` None, `remote` None, `offline` False, `mode` None, `session_branch` None, `session_branch_created` None, `b2_left` None, `b4_left` None, `branch` None, `advised_D` [], `declined` [], `stage` "new", `pending` [], `settle_todo` [], `end_commit` None.
  - `new(command: str, **values) -> dict` — `FIELDS` copied, `session`, `command` and `started` (UTC, `%Y-%m-%dT%H:%M:%SZ`) filled; an unknown key raises `ValueError`.
  - `load(session: str, command: str) -> dict | None` — `None` where the file is absent, does not parse, or holds another `version`.
  - `save(session: str, command: str, rec: dict) -> None` — sets `updated` (UTC, as `started`), creates the directories (mode 0o700), writes a temporary file beside the record and `os.replace`s it; an unknown key raises `ValueError` before anything is written.
  - `resumable(rec: dict, args: dict, minutes: int = 15) -> bool` — true only where `rec["stage"]` is not `done`, `rec["args"] == args`, and `rec["updated"]` is within `minutes` of now.
  - `remove(session: str, command: str) -> bool` — whether a file was removed; the session directory is removed too where that left it empty.
  - `prune(keep_session: str, days: int = 7) -> list[str]` — removes every `*.json` under `root()` last modified more than `days` days ago, in any session directory but `keep_session`'s, and each session directory that leaves empty; returns the removed paths.
- Produces, in `specs-git.py`:
  - `_flow() -> (state, lines)` — imports the two modules (`lines` from Task 3 on) the first time a new subcommand needs them; a failure raises `NotRun("<module> could not be loaded: …")`. Part 1's subcommands never call it.
  - CLI `declined --command /<name> --path <p> [--path <p>]…` printing `{"recorded": [paths in order, unique], "record": "found" | "created"}`.

- [ ] **Step 1: Write the failing selftests**, `scenarios_state(tmp)`, every check setting `HOME` and the session variable itself and restoring them:
  - `s_session_id`: unset, empty and `../x` raise `NoSession`; `ab-12_x.y` is returned.
  - `s_path`: with `HOME=<tmp>/home`, `path("s1", "/create-ard") == "<tmp>/home/.claude/dev-workflows/specs-git/s1/create-ard.json"`; `path("s1", "create-ard")` raises `ValueError`.
  - `s_roundtrip`: `save` then `load` returns the record, a non-ASCII and a space-carrying path in `declined` included; no file but `create-ard.json` is left in `s1/`; `save` with an unknown key raises before the file changes.
  - `s_unparsable`: a file holding `{` loads as `None`.
  - `s_keys`: records saved for (`s1`, `/specify`), (`s1`, `/feedback`) and (`s2`, `/specify`) load back each its own.
  - `s_remove`: `True`, then `False`; `load` then `None`; `s1/` gone once its last record is.
  - `s_prune`: with `keep_session="cur"`, a record in `old/` touched 8 days ago (`os.utime`) is removed with `old/`; one touched 6 days ago is kept; one in `cur/` touched 8 days ago is kept.
  - `s_resumable`: a record at stage `settle` saved now with the same `args` → true; the same at stage `done`, with other `args`, or `updated` 20 minutes ago → false.
  - `s_declined_cli`: with no record, `declined --command /create-ard --path "specifications/PRD-A-1 x/prd.md" --path a.md` prints `record: "created"`, and the record holds both paths and `started_by_script: false`; a second call with `a.md` again and `b.md` adds `b.md` only (`record: "found"`); a `declined --command /idea` call leaves `/create-ard`'s record unchanged.
  - `s_declined_no_session`: without the session variable, exit 2, one `specs-git: not run (` line, no file under `HOME`.
  - `s_usage_prefix`: `declined --path a.md` (no `--command`) exits 2 with one line beginning `specs-git: not run (usage: `.
  - `s_outside_repo`: a `declined` call made from inside a repository leaves its `git status --porcelain` unchanged.
  - `s_lazy_import`: in a copy of `specs-git.py` and `session-branch.py` without `specs_git_state.py`, `status` on a repository still exits 0 with its JSON, and `declined` exits 2 with one line.
- [ ] **Step 2: Run** `python3 plugins/workflows-core/scripts/specs-git.py --selftest`. Expected: FAIL on the new checks.
- [ ] **Step 3: Implement** `specs_git_state.py`, `_flow()` and the `declined` subcommand. `Parser.error` prints `specs-git: not run (usage: <message>)`; `main()` maps `state.NoSession` to the `not run` line and exempts `declined` from `--specs`, as it does `owner-repo`. The selftest pops `CLAUDE_CODE_SESSION_ID` and `GIT_USER_INITIALS` at its start and extends Part 1's `cli()` helper to `cli(*args, env=None, stdin=None, cwd=None)`.
- [ ] **Step 4: Run** the selftest. Expected: `specs-git selftest: PASS (<n> checks)`.
- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git — the state record, one per session and command, and declined`

### Task 3: The line templates and the wording SRG leaves free

**Files:**
- Create: `plugins/workflows-core/scripts/specs_git_lines.py`
- Modify: `plugins/workflows-core/references/specs-repo-git.md` (§1 rule 5, §3.1, §3.2, §3.4, §3.5, §4 step 1, §4 step 6, §4.1, §6 — wording, D2, D3 and D4); `session-hygiene.md` (§7 *Callers*, D4); `specs-git.py` (`_flow()` loads `lines`; selftest `scenarios_lines`)
- Regenerate: `plugins/workflows-core/reference-parts/` (`session-hygiene`'s parts change; `phase-handoff`'s must not)

**Interfaces:**
- Produces, in `specs_git_lines` (imported as `lines`):
  - `T: dict[str, str]` — every template, keyed by id, each the exact text of its source with its `<…>` placeholders and `[…]` segments as the source writes them. Where `addressing` §3 wraps a form in a label (`[stray-folder form: …]`, `[two-readings form: …]`, `[<in the two-readings form only: …>…]`), the template is the text inside the label, which is still a substring of the source. Ids: §5 `g0`, `g1`, `g2` (the three fenced blocks, whole); `g2.session.not_done`, `.fix`, `.if_ignored`; `g2.self.not_done`, `.fix`, `.if_ignored`; `g2.implement.not_done`, `.fix`, `.if_ignored`. §6 rows `row.<id>` for each id in `ROWS` but `silent`, plus `row.remote-deleted.default-tail`, `row.scope.merge` (`which is a merge commit`), `row.scope.no-file` (`which changes no file`), `row.scope.hook`, `row.moved.refused`, `row.session-rejected`, `row.session-rejected.conflict-ending`. Appends `app.hook-line`, `app.record-key`, `app.record-unset`, `app.unrecorded`, `app.register-clause`, `app.register-move`, `app.upstream-error`, `app.why.later-refused`, `app.why.moved-on`, `app.why.failed`, `app.why.stopped`, `app.session.created`, `app.session.conflict-default`, `app.session.conflict-origin`, `app.session.sync-error`, `app.session.unsettled`, `app.session.stranded`, `app.session.unsupported`, `app.session.refused-remedy`, `app.mode-on`, `app.mode-on.no-identity`, `app.declined`. Reason clauses `reason.<refused.reason>` for the twelve of §6 plus `reason.not-run`, `reason.timed-out`, `reason.session-mode`; remedies `remedy.rejected`, `remedy.not-standing`, `remedy.checked-out`, `remedy.session-wrap`. Preflight lines `pre.nonrepo`, `pre.below-top`, `pre.pull-failed`, `pre.merged-flush`, `pre.refused`, `pre.refused.unrecorded`, `pre.created.empty`, `pre.created.committed`, `pre.deleted`, `pre.delete-failed`, `pre.advisory-D`, `pre.advisory-D.rm`, `pre.pushed-left`, `pre.b2-config`, `pre.b2-squash`, `pre.b4`, `pre.b4.count`, `pre.stay`, `pre.rerun-failed`, `pre.session-not-run`, `pre.stopped`, `end.stopped`; reasons `text.push-capped`, `text.pull-capped`. From `addressing` §3: `root.one-line`, `root.stray`, `root.two-readings`, `root.left-behind`, and its pieces `root.left-behind.nested`, `root.left-behind.dir`, `root.left-behind.close`. From `session-hygiene` §7: `env.changed`.
  - `ROWS: tuple[str, ...]` — the 24 `end` row ids, in SRG §6's order: `pushed-plugin`, `pushed-default`, `pushed-session`, `no-identity`, `session-not-run`, `not-ours`, `no-remote`, `elsewhere`, `remote-deleted`, `origin-lacks`, `refused-before`, `push-refused`, `scope`, `replayed`, `already-there`, `moved`, `rejected`, `failed`, `nothing`, `locked`, `commit-failed`, `blocked`, `misrooted`, `silent` (`silent` has no template: it prints nothing).
  - `preflight_form(row_line: str) -> str` — SRG §6's *Inside §3.4's flush and retry* rule: `Specs repo: committed <sha7> (<N> files) on <branch>` becomes `Specs preflight: <branch>`, and a line opening `Specs repo:` with no such prefix (*Locked*, *Commit failed*) opens `Specs preflight:` instead.
  - `fill(template_or_id: str, values: dict) -> str`, by these rules, in this order:
    1. `(<N> files)` is replaced by `count_files(values["<N>"])`.
    2. A **list marker** is dropped, and the placeholder just before it takes its whole list, joined by `, `, as its value: `[, …]`; a segment repeating that placeholder, `<P>[, <P>…]` (`root.stray`'s `<subdirectory>[, <subdirectory>…]`); and an unbracketed `, …` straight after it, `(<folder>, …)` (`root.left-behind`).
    3. An **optional segment** — any other balanced `[…]` not opening `[SEC#`, which is literal — is kept, its brackets dropped, where every placeholder inside it has a value that is not `None`, and dropped whole otherwise.
    4. A **repeated clause** — one a source ends with `; …`, as `root.left-behind`'s `<value>/<bookkeeping directory>/, which belongs at …` does — is never filled whole: it is its own template (`root.left-behind.nested`, `root.left-behind.dir`, `root.left-behind.close`, each a substring of the source), which the renderer fills once per item and joins with `; `.
    5. A **placeholder** — a balanced `<…>` — is replaced by `values[span]`; a list value for a placeholder no list marker follows is consumed one item per occurrence, in order (`<sha7>` names two commits in the push-scope row). An **alternation** placeholder, one holding ` | ` at its own level, takes an `int` picking its alternative, whose own placeholders are then filled from the same `values`.
    6. A placeholder left with no value raises `ValueError` naming it, so no placeholder ever reaches a user.
  - `count_files(n: int) -> str` — `(1 file)` or `(<n> files)` (SRG §6's singular rule).
  - `artifacts(paths: list[str]) -> str` — `phase-handoff` §4.1's `<artifacts>`: the paths comma-separated where three or fewer, else `<n> files under <dir>`, `<dir>` the nearest directory holding every path (`os.path.commonpath` of their directories, repo-relative).
  - `pins(srg: str, addressing: str, hygiene: str) -> list[str]` — one failure per template not found in its source; comparison collapses every whitespace run to one space on both sides, save the three §5 blocks, compared line for line against SRG §5's fenced blocks.

- [ ] **Step 1: Write SRG's missing wording first** — prose, one line each, no hard wrap — so the templates have a source:
  - §3.1, the non-repository notice: `` `Specs preflight: SPECS_PATH is <value>, which <is not a directory | is not in a git repository> — nothing this run writes there is committed or handed off; set SPECS_PATH to your specs repository's top level, where it is set, and re-run.` `` Where the path is a directory and `specs-root-check` finds a signal there, the notice goes on with that entry point's own stop text, in whichever of its forms `workflows-core:addressing` §3 picks — the one-line form, or, where only signal (b)'s second half fired and the walk found no value, the two-readings form, whose second reading names making `<value>` a repository's top level — and its left-behind line where it has one: never advice that section rules out. (This replaces the sentence that had the line "also say which one, and name the value to set".)
  - §3.1, the below-top-level notice: `` `Specs preflight: SPECS_PATH is <value>, below the top level of its repository (<top>) — a specs tree inside a larger repository is unsupported, because this plugin switches branches and commits in the repository SPECS_PATH belongs to, so this run switches and commits nothing there; set SPECS_PATH to a dedicated specs repository's top level.` ``
  - §3.2, *Freshness*: the note is carried, not printed — the script returns it as `offline` and `offline_clause` — so the preflight stays silent as §1 rule 7 says; `phase-handoff.md` §3.6 says it where its gate reads against that ref.
  - §3.4's catch-up, §3.5's B2 and B4 pulls: a failed pull prints `` `Specs preflight: could not fast-forward <default> (<git's first error line>); the run goes on from it as it stands` ``, the parenthesis reading `` `the pull did not finish within 60 s` `` where the 60 s cap ended it.
  - §3.4's settle loop and §3.5's B2: a failed `-d` prints `` `Specs preflight: could not delete merged <branch> (<git's first error line>)` ``; B2 that deleted its branch prints §3.4's `Specs preflight: deleted merged <branch>`.
  - §3.5's B4: `` `Specs preflight: left <branch> for <default>, since no key of this run names it — the branch and its pull request are as they were` ``, followed, where it holds commits a push would publish, by `` `; <N> commit(s) on it are not on origin, and a later run's preflight pushes them where §4 step 5 lets it` ``.
  - §3.5's re-run: a failed switch back prints `` `Specs preflight: could not switch back to <branch> (<git's first error line>); this run goes on from <current>` ``.
  - §4 step 6, second bullet: a push the 60 s cap ended reads `` `the push did not finish within 60 s` `` as its reason.
  - §6's *Inside §3.4's flush and retry* paragraph: "each of these four rows" becomes "each of these four rows and the *push FAILED* row", and a sentence is added: the *Locked* and *Commit failed* rows, which a flush can meet, print there with `Specs repo:` replaced by `Specs preflight:`.
  - §8's opening: an exit 2 inside the preflight prints `` `Specs preflight: session-branch.py could not run (<the first line of its stderr>)` ``.
  - §1 rule 5, after its first sentence: where the script stops on a failure it did not foresee after its first write, it prints `` `Specs preflight: stopped early (<the error>) — what it did is above, and the next run's preflight goes on from where this one stands` `` at the start and `` `Specs repo: NOT FINISHED — the terminal step stopped early (<the error>); what it committed or pushed is as it left it, and the next run's preflight flushes the rest` `` at the end, the end's one outcome line.
  - **D3.** §4 step 1, after "a run that ran no preflight and carries neither flag tests G0's state here": such a run also runs §3.1's two placement tests — `specs-root-check`'s signals and the below-top-level test — and, where one fires, takes the `specs_git: misrooted` outcome with that notice, since its preflight would have set the flag (the maintainer's decision D3, 2026-11-09).
  - **D4, where the contract lives.** One noun across every copy: *the `SPECS_PATH` half of the run's `Environment:` line* — `$SPECS_PATH`'s real path and its `origin`.
    - §4 step 1, in the gate, before its flag bullets: ``**The run's environment, at the end (the maintainer's decision D4).** Where the run's preflight printed an `Environment:` line, compare the `SPECS_PATH` half of the run's `Environment:` line with the same half of the line `session-hygiene.md` §7's Bash call prints now. Where they differ, the run carries `specs_git: misrooted` from here on, with §7's `Environment changed:` notice, built from the two whole lines, as the notice that set it, and the misrooted outcome below follows. The `REPOS_PATH` half is `env-check`'s, which the tail runs: a run `session-hygiene.md` §6 pinned exports its own value per call.``
    - §3.1's list of what sets the flag (the paragraph opening `` **`specs_git: misrooted` is the run-wide record** ``) gains, after §6's *Stop*: `; or by \`commit-artifacts\` itself (§4 step 1), where the \`SPECS_PATH\` half of the run's \`Environment:\` line no longer matches the one its preflight printed — §7's environment change, met at the end`.
    - §6's *Misrooted* row's case column gains `, or §4 step 1's comparison of the \`SPECS_PATH\` half of the run's \`Environment:\` line`; its line, a pinned template, is unchanged.
    - `session-hygiene.md` §7's *Callers* paragraph gains: `And \`workflows-core:specs-repo-git\` §4 step 1 compares the \`SPECS_PATH\` half of the run's \`Environment:\` line itself, at the end, so a run whose tail wrote nothing is still checked before its commit.` (Regenerate its parts.)
    - The rules bullet is Task 10's.
  - **The sweep of who sets the flag** (refinements 6 and 8), before these edits. Recipe: `grep -rniE --include=*.md 'misrooted' plugins CLAUDE.md .claude/rules docs/maintainers README.md | grep -v '/CHANGELOG.md' | grep -v 'reference-parts/' | grep -v 'coupling-history' | grep -E "env-check|Environment changed|§6's \*Stop\*|RESUME_ENVIRONMENT_CHANGED|specs-root-check\`'s stop|setters|either notice above" | wc -l` → 46 at `bfa147fd`, and the four D4 sites above, whose lines the recipe misses where the list wraps. Dispositions:
    - the sites above get D4;
    - of the 46, 14 are reference lines, two of them D4 sites (SRG §3.1's list and §6's row); the other 12 — the emission references' `env-check` steps, `phase-handoff`'s gate, `session-hygiene` §1 and §6, SRG's refusal tail — each describe the flag at a step that runs before `end`, where D4's comparison has not yet run, so each stays true; the one rules line is Task 10's bullet;
    - the 31 command lines restate a narrower list (most "§3.1, or `specs-root-check`'s stop") of the flags a run carries into the step, which audit-A already found narrower than SRG and not false, since the skip is keyed on the flag. D4's flag is set inside the step, not carried into it, so each stays true but incomplete; the 2b+ wrapper slimming removes them.

    Count `the \`SPECS_PATH\` half of the run's \`Environment:\` line`, whitespace-collapsed over refinement 4's scope: 0 before; 4 after this task (SRG §4 step 1, §3.1, §6's row; `session-hygiene` §7); 5 after Task 9 (SRG §7's record paragraph); 6 after Task 10 (the rules bullet).
  - **D2.** §4.1's third bullet names both declines: "when the user declined git at handoff — `phase-handoff.md` §4.3's option 2 (*just write the files*) or option 3 (*Cancel*)". §6's last paragraph: "When the deliverable is still uncommitted because the user declined git at handoff (§4.1), on either option, append to the line: `; the deliverable at <path> remains uncommitted, as you asked`, `<path>` being the declined handoff's declared paths that `git status` still lists, written as `phase-handoff.md` §4.1 writes `<artifacts>`."
- [ ] **Step 2: Write the failing selftests**, `scenarios_lines(tmp)`:
  - `l_pins`: `lines.pins(<SRG>, <addressing>, <session-hygiene>) == []`.
  - `l_pins_bite`: the same with one word of SRG §6's *Nothing to commit* row changed in memory → exactly one failure, naming `row.nothing`.
  - `l_ids`: every id the Interfaces list names is in `T`; a `row.<id>` exists for each of `ROWS` but `silent`; `len(ROWS) == 24`.
  - `l_fill_basic`: `fill("row.nothing", {}) == "Specs repo: no session artifacts to commit"`; a missing key raises `ValueError` naming it.
  - `l_fill_list`: a list value fills the push-scope row's two `<sha7>`s in order.
  - `l_fill_optional`: `row.replayed` with `<D>` `None` and no register clause ends `onto it`; with `<D>` `"1"` it ends `onto it, 1 of them already there and dropped`; `row.moved` with and without its optional clauses; `row.scope.hook` with one path (no `, and … more`) and with three (`, and 2 more`); `reason.would-overwrite` with `<M>` `None` and `"2"`; `root.one-line` with and without its trailing unsupported-layout segment; `root.stray` keeping its inner segment only where its values are given.
  - `l_fill_list_marker`: `app.session.unsettled`'s `<path>[, …]` with `["a.md", "b c.md"]` reads `a.md, b c.md`.
  - `l_fill_root_lists` (11): `root.stray` with `<subdirectory>` `["PRD-S-9-x", "EPIC-S-9-01-y"]` names both, comma-joined, in each of its two places, and with one name names it alone; the left-behind renderer with folders `["PRD-A-2-y", "PRD-A-3-z"]` and two bookkeeping directories fills `(<folder>, …)` as `(PRD-A-2-y, PRD-A-3-z)`, writes the directory clause twice joined by `; `, and ends with the closing sentence; its output equals the source's form with those values, no `…` and no `[` left.
  - `l_fill_alternation`: the misrooted stay line with `1` reads its second alternative, its nested `<default>` filled; `root.one-line`'s signal alternation with `2` fills `<key>` inside it.
  - `l_fill_count`: `row.pushed-plugin` with `<N>` `1` reads `(1 file)`, with `2` `(2 files)`.
  - `l_literal_bracket`: `app.register-move` keeps `[SEC#7]` literal.
  - `l_preflight_form`: `preflight_form` of a filled *push FAILED* row opens `Specs preflight: main — push FAILED (`; of `row.locked` opens `Specs preflight: skipped — another session holds the repo`.
  - `l_artifacts`: one, two and three paths comma-separated; four paths under `specifications/PRD-A-1-x/` → `4 files under specifications/PRD-A-1-x`; four spanning `specifications/` → `… under specifications`; a path with a space kept as it is.
- [ ] **Step 3: Run** the selftest. Expected: FAIL (`lines` undefined).
- [ ] **Step 4: Implement** `specs_git_lines.py` (templates as literal strings copied from the sources, never built from pieces of other templates), and load it in `_flow()`; extend `s_lazy_import` to a copy missing it.
- [ ] **Step 5: Run** the selftest and `python3 scripts/reference-parts.py generate && python3 scripts/reference-parts.py check-parts`. Expected: PASS; under `reference-parts/` only `session-hygiene/`'s files that hold §7 changed.
- [ ] **Step 6: Commit** — `feat(workflows-core): specs-git — every notice and outcome line, pinned to its reference; SRG fixes the wording it left free; D2, D3, D4`

### Task 4: The gate — the `Environment:` line, §3.1 and `specs-root-check`

**Files:** Modify `plugins/workflows-core/scripts/specs-git.py` (functions, the `specs-root-check` subcommand, selftest `scenarios_gate`).

**Interfaces:**
- Consumes: `lines.fill`, `lines.T` (`pre.nonrepo`, `pre.below-top`, `root.*`).
- Produces:
  - `SH7_LINE: str` — `session-hygiene` §7's Bash call (the fenced `bash` block under **The line.**), character for character.
  - `env_line(specs: str) -> str` — runs `bash -c SH7_LINE` with `SPECS_PATH` set to `specs` in its environment, or removed where `specs` is empty, and every other variable inherited; returns its one line.
  - `RESERVED: re.Pattern` — `addressing` §2's register of reserved subdirectory names as a whole-name match: `brd`, `grounding`, `interview`, `dev-workflows`, `design`, `attachments`, `revisions`, `bundle-[0-9]{8}`, `customer-sent-[0-9]{8}`, `Doc screenshots`.
  - `specs_root_check(specs: str) -> {"signal": None | "a-prefix" | "a-ef" | "b-self" | "b-sub", "form": None | "one-line" | "stray" | "two-readings", "value": str | None, "subdirs": [str], "lines": [str]}` — `workflows-core:addressing` §3 `specs-root-check` exactly: signal (a)'s two tests, signal (b)'s carrier test (`addressing` §4's carrier order — top-level files in byte-wise order, then `brd/brd-inventory.md` — read off frontmatter `key:` and `kind:` of `brd`, `prd` or `epic`, with §4.1's `<KIND>-<key>-` prefix test, the folder's own name tested physically and a subdirectory skipped where it resolves inside `$SPECS_PATH/specifications/`), the value-to-set walk (at most three levels above, both halves required), the choice among its three forms, and the left-behind line. `lines` is `[]` where no signal holds.
  - `gate(specs: str, notices: bool = True) -> {"state": "unset" | "not-a-repo" | "read-only" | "pass", "top": str | None, "git_dir": str | None, "misrooted": bool, "lines": [str]}` — SRG §3.1's three dispositions and its two passing-gate tests (`specs-root-check`, then the below-top-level test, skipped where the first fired); on a non-repository directory with a signal, `pre.nonrepo`'s line, then `specs_root_check`'s own lines; `misrooted` where the inside-tree notice, the below-top-level notice, or a non-repository notice with a signal fired. With `notices=False` it returns `state`, `top` and `git_dir` alone.
  - CLI `--specs "<value>" specs-root-check` printing `specs_root_check`'s object.

- [ ] **Step 1: Write the failing selftests**, `scenarios_gate(tmp)`:
  - `g_sh7_pinned`: `SH7_LINE` equals the fenced block read from `plugins/workflows-core/references/session-hygiene.md` §7.
  - `g_env_line_equal` (Review Focus 3): for `SPECS_PATH` unset; a repository path with a trailing `/`; a symlink to it; a relative path; a nonexistent path; a path holding a space; `REPOS_PATH` unset and set — `env_line(value)` equals the output of `bash -c '<the block read from session-hygiene.md>'` run with `SPECS_PATH` exported to `value` (or unset) in the same environment.
  - `g_unset`: `gate("")` → `state: "unset"`, `lines: []`, `misrooted: False`.
  - `g_file`: a regular file → `not-a-repo`, one line from `pre.nonrepo` with `is not a directory`.
  - `g_plain_dir`: a directory in no repository, no signal → `not-a-repo`, one line, `misrooted: False`.
  - `g_mounted_specifications` (M2): a directory **named `specifications`** in no repository, holding `PRD-A-1-x/prd.md` (frontmatter `key: A-1`, `kind: prd`) → `not-a-repo`, `misrooted: True`, `pre.nonrepo`'s line, then `specs-root-check`'s **one-line** form (signal `a-ef`) naming *the directory that holds specifications/* as the value to set; with a nested `specifications/PRD-A-2-y/` and a `dev-workflows-cost/` beside it, `root.left-behind` after.
  - `g_mounted_other_name` (M2): a directory **named `tree`** in no repository, holding `PRD-A-1-x/prd.md` directly → `not-a-repo`, `misrooted: True`, `pre.nonrepo`'s line, then the **two-readings** form (only signal (b)'s second half fired, the walk found no value, `rev-parse` fails), whose second reading names making `tree` a repository's top level; and no line names a value to set that `addressing` §3 rules out.
  - `g_inside_tree`: `<repo>/specifications` → `pass`, `misrooted: True`, the one-line form naming `<repo>` as the value; `<repo>/specifications/PRD-A-1-x` → the same signal.
  - `g_below_top`: `<repo>/specs` holding `specs/specifications/` → `pass`, `misrooted: True`, one line from `pre.below-top` naming `<repo>`.
  - `g_stray`: a repository's top level holding `specifications/` and a hand-placed `PRD-S-9-x/` with a carrier → the stray-folder form naming `PRD-S-9-x`, no left-behind line.
  - `g_two_readings`: `<repo>/specs` holding `PRD-A-1-x/` directly and no `specifications/` → the two-readings form with the unsupported-layout clause.
  - `g_correct_root`: a top level with `specifications/PRD-A-1-x/`, a `templates/prd.md` carrying `key:` and `kind: prd`, and a `README.md` carrying both → `pass`, no lines, `misrooted: False`.
  - `g_reserved`: `RESERVED` matches every name of `addressing` §2's list as that file writes it, and `session-branch.py`'s `EXCLUDED` holds the same names but `dev-workflows`.
  - `g_read_only` (skipped as root): `chmod a-w` on `.git` → `read-only`, no lines.
  - `g_cli`: `specs-root-check` prints the function's object, exit 0, for the two mounts and for an unset value.
- [ ] **Step 2: Run** the selftest. Expected: FAIL.
- [ ] **Step 3: Implement** the four functions and the subcommand; `main()` passes `specs-root-check`'s `--specs` through unchecked — empty, a file, a subdirectory — as it will `start`'s and `end`'s (the `--specs` exception). The frontmatter read is the lines between a first `---` and the next, `key:` and `kind:` taken by `^(key|kind):\s*(.+?)\s*$`, quotes stripped; nothing is parsed out of a name.
- [ ] **Step 4: Run** the selftest. Expected: PASS.
- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git — the Environment line, the §3.1 gate and specs-root-check`

### Task 5: The commit engine and `end`

**Files:** Modify `plugins/workflows-core/scripts/specs-git.py` (engine, `end`, selftest `scenarios_end`).

**Interfaces:**
- Consumes: `state.*`, `lines.*`, `gate()`, `env_line()`, Part 1's `status()` and `push_scope()`, `sb.git_bounded`, `sb.refusal_record`, `sb.mode`.
- Produces:
  - `resolve_default(root: str, fetch: bool) -> {"default": str, "default_ref": str, "remote": "origin" | "none", "offline": bool}` — SRG §3.2's name, ref and freshness rules; the fetch (`fetch origin <default>`, 60 s) only where `fetch` is true and a remote exists.
  - `catch_up(root, default, default_ref) -> str | None` — §3.4's catch-up where HEAD is on the default branch and strictly behind `<default-ref>` (`pull --ff-only --no-rebase origin <default>`, 60 s); the `pre.pull-failed` line where it fails (its parenthesis `text.pull-capped` where the cap ended it), else `None`.
  - `commit_session_files(root: str, message: str) -> {"status": "committed" | "nothing" | "locked" | "failed", "sha": str | None, "paths": [str], "hook_paths": [str], "error": str | None}` — SRG §2.1 steps 1–3 (Part 1's `status()`, `git add -A -- ':(literal)<p>'…`) and §4 step 4 (the staged list by `diff --cached --name-only -z --no-renames -- ':(literal)…'`, the staged-before read, the pathspec commit `commit -q -m <message> -- ':(literal)…'`, the index restore over the paths both `diff-tree … HEAD` and `diff --cached` list less those somebody else had staged); `locked` where `git rev-parse --git-path index.lock` exists, tested before staging; `hook_paths` the paths the commit carries that its pathspecs did not name.
  - `push_check(root, branch, default, session_branch=None) -> {"row": None | "not-ours" | "no-remote" | "elsewhere" | "remote-deleted" | "refused-before" | "origin-lacks" | "scope", "remote": str | None, "record": str | None, "record_kind": "file" | "config" | None, "date": str | None, "scope": dict | None, "set_upstream": bool}` — §4 step 5's three conditions and four nowhere-to-push states, tested in SRG's order, `ls-remote --exit-code --heads origin refs/heads/<branch>` capped at 30 s; `row` `None` where all hold; `set_upstream` by step 5's `-u` rule.
  - `push(root, branch, set_upstream) -> {"outcome": "pushed" | "refused" | "rejected" | "failed", "reason": str | None, "recorded": "file" | "config" | None, "record": str | None, "record_error": str | None}` — `push --porcelain [-u] origin <branch>` (60 s; a cap is *failed* with `text.push-capped` as its reason); the outcome read from the `--porcelain` status line for `refs/heads/<branch>` alone — its flag ` `, `+`, `*` or `=` (`[up to date]`, `origin` already holding the commit, as after an earlier call's push the harness cut short) is *pushed*; `[remote rejected]` is *refused* save the five transient reasons of step 6, which are *failed*; a refusal writes the push-refusal record (§1 rule 8: the file under `<git-common-dir>/workflows/push-refused/<branch>` holding the date, else the `branch.<branch>.workflowsPushRefused` key).
  - CLI `--specs "<value>" end --command /<name> [--commit-key K] [--register-rebuild P] [--no-preflight] [--misrooted-stdin] [--session-branch-created SHA7] [--declined <path>]… [--resume]`, printing `{"print": [str], "line": str | None, "row": <a ROWS id> | None (None only while `next` names the replay), "sha7": str | None, "files": int | None, "branch": str | None, "pushed": bool, "next": dict | None, "record": "found" | "missing" | "ignored" | "declined-only", "error": str | None}`. `print` is the outcome line (appends included), then the §5 block or the misrooted notice it repeats, then the hook line where it applies. `--commit-key` must match `workflows-core:addressing` §1's `^[A-Z][A-Z0-9_]*(-\d+)+$`, else a usage exit 2.
- **Order inside `end`** (SRG §4 steps 1–7):
  1. **The record**, `state.load(session, command)`: `found`; `missing` where none; `ignored` under `--no-preflight` (removed); `declined-only` where `started_by_script` is false (its declined paths kept). Each but `found` takes the no-preflight path.
  2. **The flags**, in this order: the record's `specs_git` and notice; a `--misrooted-stdin` notice (empty stdin: the misrooted row with no notice after it); D4 — on a `found` record whose `env_line` is set, the `SPECS_PATH` half of the run's `Environment:` line against the same half of `env_line(--specs)`, and where they differ, `misrooted` with `env.changed` built from the two whole lines; on the no-preflight path, §4 step 1's G0 test and D3's two placement tests (`gate(specs)`'s lines).
  3. `gate(specs, notices=False)` → `silent` where it fails and no flag stands.
  4. `<default>` from the record or `resolve_default(fetch=False)`; mode from the record or `sb.mode` (Task 8 fills the mode branch; outside it, `mode` off).
  5. `catch_up`, then `commit_session_files` with `<KEY|NOISSUE> Add dev-workflows session artifacts (<command>)`; where it committed, `end_commit: {sha7, files, branch, paths, hook_paths}` is saved at once.
  6. `push_check`, then `push`. A `rejected` push returns `next` naming `replay --for end --command /<name> --branch <b> [--set-upstream]` (timeout 420000, `on_timeout` the same with `--timed-out`), the record kept with `stage: "end-replay"`.
  7. Otherwise render the row, the appends in SRG §6's order (declined last, naming only the paths — the record's and `--declined`'s — that `status()` still lists, through `lines.artifacts`), the repeated block, the hook line where a hook path is one the record's `guard_paths` or the declined append names; remove the record.
  - **`--resume`**: where the record holds `end_commit` and was saved within the last 15 minutes, go on from step 6 for that commit, rendering with its facts; otherwise run from step 1.
  - **R2's boundary** is `end`'s first repository write — the catch-up's pull, else the `git add`: before it, a failure is an exit 2; after it, an exception returns `error` with `end.stopped` as the line.

- [ ] **Step 1: Write the failing selftests**, `scenarios_end(tmp)`, on a `world(tmp, name)` helper — a bare `origin`, a clone with `specifications/PRD-ACME-1-x/prd.md` committed and pushed on `main`, `HOME=<tmp>/home-<name>`, the session variable `<name>` — and a `seed(env, command, **fields)` helper that saves a record as `start` would, its `env_line` from `env_line(<the clone>)`:
  - `e_nothing`: clean tree → `row: "nothing"`, `print == ["Specs repo: no session artifacts to commit"]`, record removed.
  - `e_pushed_default`: a new `specifications/PRD-ACME-1-x/dev-workflows/resume.md` on `main` with `--commit-key ACME-1` → `row: "pushed-default"`, subject `ACME-1 Add dev-workflows session artifacts (/create-ard)`, no `Co-Authored-By`, `origin/main` holds it; without `--commit-key` the subject opens `NOISSUE`; one file reads `(1 file)`.
  - `e_pushed_plugin`: the same on a pushed `prd/ACME-1-x` → `pushed-plugin`.
  - `e_not_ours`: on `feature/x` with a record holding G2's block → `not-ours`, then the block, verbatim.
  - `e_no_remote`, `e_elsewhere` (`branch.main.pushRemote fork`), `e_remote_deleted` (a pushed plugin branch deleted on the bare; and the default branch's form with its `remote set-head` tail), `e_origin_lacks` (a plugin branch never pushed), `e_refused_before` (a record file holding `2026-11-01` → that date and the file's path; the config-key form naming `branch.<b>.workflowsPushRefused` and its `config --unset`) → each its row.
  - `e_push_refused`: a bare whose `pre-receive` exits 1 → `push-refused`, the record file written under the common git directory with today's date.
  - `e_scope`: an unpushed commit of the user's touching `notes.md` on `main` → `scope` naming its sha7, subject and path; a merge commit → `which is a merge commit`; a `pre-commit` hook that adds `generated.txt` and `gen2.txt` to the commit → the hook variant naming `generated.txt, and 1 more`, and, where the record's `guard_paths` lists `generated.txt`, the hook line after the block.
  - `e_push_failed`: `origin` pointed at a missing path after the clone → `failed` with git's reason.
  - `e_locked`: an `index.lock` present → `locked`, nothing staged.
  - `e_commit_failed`: a `pre-commit` hook that exits 1 → `commit-failed`, the session file still staged.
  - `e_blocked`: a record with `specs_git: blocked` → `blocked` and the G0 block; with no record and `--no-preflight`, a detached HEAD and a dirty session file → `blocked` with the block (the first time), and with nothing to stage → `nothing`.
  - `e_misrooted`: a record with `specs_git: misrooted` and its notice → `misrooted`, then that notice verbatim; with no record, `--no-preflight --misrooted-stdin` and an `Environment changed: …` line on stdin → the same with that line; with empty stdin → the `misrooted` row and nothing after it, nothing committed.
  - `e_env_changed` (m8, D4): a record whose `env_line` names the clone, then `end --specs ""` → `misrooted`, `env.changed` naming both lines, nothing committed; `end --specs <another repository>` → the same; a record whose line differs only in its `REPOS_PATH` half → `found`, committed.
  - `e_d3_below_top` (D3): no record, `--no-preflight`, `$SPECS_PATH` at `<repo>/specs` holding `specs/specifications/` with a dirty session file → `misrooted` with the below-top-level notice, nothing committed.
  - `e_declined_only` (m8): a record `declined` alone created → `record: "declined-only"`, the no-preflight path, the commit made, the declined append present.
  - `e_silent`: a directory that is no repository and no flag → `row: "silent"`, `print == []`, `line: null`.
  - `e_declined` (Review Focus 4): a record declining `specifications/PRD-ACME-1-x/prd.md` and `specifications/PRD-ACME-1-x/a b.md` (both untracked) → the line ends `; the deliverable at specifications/PRD-ACME-1-x/prd.md, specifications/PRD-ACME-1-x/a b.md remains uncommitted, as you asked`; with `prd.md` committed by hand before `end`, only `a b.md` is named; four declined paths in that folder → `4 files under specifications/PRD-ACME-1-x`; with no record and `--declined specifications/PRD-ACME-1-x/prd.md` → the append names it.
  - `e_two_sessions` (Review Focus 1): records for sessions `s1` (misrooted) and `s2` (clean, G1 block), both `/specify`, on the same repository → `end` under `s2` commits and prints `s2`'s block only; `s1`'s record is untouched.
  - `e_stale_no_preflight` (Review Focus 2): a record of `/create-ard` with `specs_git: misrooted`, then `end --command /create-ard --no-preflight` → `record: "ignored"`, the commit made, the record gone.
  - `e_missing_record`: no record and no `--no-preflight` → `record: "missing"`, run as the no-preflight path.
  - `e_catch_up`: `main` behind `origin/main` → pulled before the commit; the push lands.
  - `e_nonff`: `origin/main` moved by another clone after the record was seeded → `row: null`, `print == []`, `next.run` names `replay --for end --command /create-ard --branch main` with timeout 420000 and an `on_timeout` carrying `--timed-out`; the record holds `end_commit` and `stage: "end-replay"`.
  - `e_resume` (m13): in process, stop `end` right after its commit (replace `push_check` by one that raises `KeyboardInterrupt`, as a harness kill would end it), then `end --resume` → the commit is not made again, the push lands, the row names the first call's sha7. `e_resume_after_push` (N8): stopped the same way right after its push landed → `end --resume` reads the push's `=` (`[up to date]`) status as *pushed*: `row: "pushed-default"`, the first call's sha7, nothing pushed twice.
  - `e_exit2`: without the session variable, exit 2, one line, and `git status`, `HEAD` and the refs are as they were; `--commit-key acme-1` → a usage exit 2.
  - `e_error_after_write` (R2): in process, replace `push_check` by a function that raises `RuntimeError`, run `end` on a dirty tree → exit-0 result with `error` set, the commit made, `line` the `end.stopped` line.
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
  - CLI `--specs <top> replay --for start|end --command /<name> --branch <b> [--set-upstream] [--timed-out]`: reads `register_rebuild` and the run's context from the record; runs `sb.replay(top, branch, register_rebuild, set_upstream)` in process, unless `--timed-out`. `--for end` prints `end`'s object (the row with `end_commit`'s `<sha7>`/`<N>` and every append, the record removed). `--for start` prints `{"print": [the row in its `Specs preflight:` form], "next": …, "error": null}`: after the current branch's replay (the record's `stage: "flush"`), `next` names `start --resume`, which begins the settle loop; after a queued one, it drops that branch from `pending` and names the next queued replay, or `start --resume` (§3.5) where none is left. A branch the run is not standing on gets `remedy.not-standing`; `checked-out` its own remedy; `checkout-moved` none. It never exits 2 once the record is found.

- [ ] **Step 1: Write the failing selftests**, `scenarios_replay(tmp)`:
  - `r_replayed`: two clones; A's `end` commits `…/dev-workflows/feedback/x.md` while B has pushed `…/dev-workflows/feedback/y.md` → `end` returns `next`; running `next.run` → `row: "replayed"`, the line names `1 commit(s)`, `origin/main` holds both files, record removed.
  - `r_dropped`: B pushed the same change → `already-there` (or `replayed` with the `<D>` clause where one of two commits was already there).
  - `r_register_rebuild`: both sides changed `security/web/register.json`, no `register_rebuild` → `rejected` with `reason.register-rebuild`'s first form and the `pull --rebase --no-autostash` remedy.
  - `r_checked_out`: the branch checked out in a second worktree → `reason.checked-out` and the remedy naming that worktree, no switch.
  - `r_timed_out`: `replay --for end --timed-out` → `rejected` with the 420 s clause, record removed.
  - `r_start_current`: a seeded record with `stage: "flush"` and `main` rejected → `print[0]` opens `Specs preflight: main`, `next.run` names `start --resume`.
  - `r_start_queued`: a seeded record with `stage: "settle-done"` and `pending: [{branch: "prd/ACME-2-y", set_upstream: false, standing: "main"}, {branch: "prd/ACME-3-z", …}]` → the first call's line opens `Specs preflight: prd/ACME-2-y` with a remedy that switches to it first and back to `main` after, `next.run` names the `prd/ACME-3-z` replay; the second's `next.run` names `start --resume`.
  - `r_canned`: `classify_replay` and the renderer over canned results → each `<why>` (later refused with `checkout-moved`'s `… so <branch> was not moved again; …` form; moved on again over `<attempts>`; failed with a status line and with none; stopped), the refused form, the register clause with a `run` and a `remote` move, `upstream_error`, `would-overwrite` with one path and with three, an exit 2 with nothing on stdout (`reason.not-run`), and a `Partial` with `pushed: true` (*replayed and pushed*).
- [ ] **Step 2: Run** the selftest. Expected: FAIL.
- [ ] **Step 3: Implement** `classify_replay`, the renderer and the subcommand.
- [ ] **Step 4: Run** the selftest. Expected: PASS.
- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git replay — §4 step 6 in a call of its own, for start and end`

### Task 7: `start`

**Files:** Modify `plugins/workflows-core/scripts/specs-git.py` (`start`, selftest `scenarios_start`).

**Interfaces:**
- Consumes: Tasks 2–6.
- Produces: CLI `--specs "<value>" start --command /<name> [--key K]… [--commit-key K] [--register-rebuild P] [--rerun] [--resume] [--budget S]`, printing on **every** `start` call, `--resume` included, the full field set, read from the record: `{"print": [str], "next": dict | None, "specs_git": None | "blocked" | "misrooted", "gate": str, "default": str | None, "default_ref": str | None, "remote": "origin" | "none" | None, "offline": bool, "offline_clause": str | None, "session_branch": str | None, "mode": str | None, "guard": None | "G0" | "G1" | "G2", "branch": str | None, "b2_left": str | None, "b4_left": str | None, "replaced": dict | None, "error": str | None}`; `branch` is HEAD's branch when the call returns; `offline_clause` is `offline — ancestry checked against the last-fetched ref` where the fetch failed. `--key` and `--commit-key` must match `addressing` §1's grammar.
- **Stages**, saved as the record's `stage`, each resumable from its start:
  1. `fetch` — §3.2: the name, the ref, the fetch; the mode (Task 8); on `--rerun`, the switch back to `b4_left` where `branch_key(b4_left, new keys)` resolves a key.
  2. `guards` — §3.3.
  3. `flush` — §3.4's catch-up, the merged-branch leave and the flush or retry of the current branch. A rejected push here returns at once with `next` naming `replay --for start` for it (R3), the stage left at `flush`; `replay` advances it.
  4. `settle` — §3.4's loop over `settle_todo`, computed on entering it after the current branch's replay, if any, so `-d`'s "`HEAD` holds it" test reads the moved `HEAD`. A rejected push here is queued in `pending` (`{branch, set_upstream, standing}`); a refused or failed one prints its `Specs preflight:` form.
  5. `settle-done` — waiting on `pending`; the queued replays run, each naming the next.
  6. `disposition` — §3.5.
  7. `done`.
  - **The first save (N4).** A call that is not a resume computes the `Environment:` line and the gate (reads only), then saves a fresh record at stage `fetch` — its first write, before the fetch and every other slow call — and then prunes (`state.prune(keep_session=<this session>)`), so an exit 2 still means nothing was done.
  - **`--resume`** continues the saved stage with the saved arguments only where `state.resumable(rec, <this call's arguments>)` holds; otherwise it runs as a fresh start, as the call would without `--resume`.
  - **The two interface rules (item 3).** (a) Every `next.run` the script builds naming `start --resume` — after a replay, at a budget stop — repeats the call's `--specs`, every `--key` in order, `--commit-key` and `--register-rebuild` exactly as the record's `args` hold them, so the resume passes `resumable`'s argument test. (b) `--rerun` opens on this command's record — fresh where none — keeps `specs_git` (OR), `advised_D`, `b4_left` and `declined`, and saves its own call's arguments, the new key set among them, as the record's `args`, so the resumes that follow it carry the new set.
- **Choices the script makes, from the rulings:** G2's direct-`/implement` lines where `--command` is `/implement` and the current directory's top level equals `$SPECS_PATH`'s; §5's `<path list>` comma-separated on the *Found* line and shell-quoted (`shlex.quote`), space-separated, on the *Fix* line, the paths saved as `guard_paths`; a G2 variant SRG gives in prose rendered unwrapped on its one line; B2 that deleted its branch prints `pre.deleted`; a branch B2 or the settle loop deletes has its push-refusal record removed (§1 rule 8: the file, and the configuration key where `.git/config` can be written); `<YYYY-MM-DD>` is today's UTC date; `<SPECS_PATH>` in a remedy is `--specs` as given; the offline note is carried in `offline` and `offline_clause`, never printed.

- [ ] **Step 1: Write the failing selftests**, `scenarios_start(tmp)` on Task 5's `world`:
  - `t_clean`: on `main`, clean → `print == [<the Environment: line>]`, `specs_git: null`, `default: "main"`, `default_ref: "origin/main"`, `remote: "origin"`, `branch: "main"`, `next: null`, record saved with `stage: "done"`.
  - `t_unset`: `--specs ""` → the `Environment:` line naming `SPECS_PATH=unset`, `gate: "unset"`, nothing else, a record saved.
  - `t_misrooted`: `<repo>/specs` holding `specs/specifications/`, HEAD on a merged `prd/A-1-x` → the below-top notice and `pre.stay`'s merged variant, no switch; HEAD on an unmerged `prd/B-2-y` with keys `{A-1}` → the unkeyed variant; nothing committed.
  - `t_offline`: `origin` unreachable for the fetch → `offline: true`, `offline_clause` set, and `print` holding the `Environment:` line alone.
  - `t_g0`, `t_g1`, `t_g2`: a detached HEAD → G0's block, `specs_git: blocked`; a dirty `notes.md` → G1's block listing it, no flush, no switch; on `feature/x` → G2's block naming `main`. `t_g2_implement`: `--command /implement` run from inside the specs repository's work tree on `feature/x` → G2 with the direct-`/implement` lines.
  - `t_catch_up` and `t_catch_up_failed`: behind `origin/main` → fast-forwarded silently; with `origin` made unreachable after the fetch → `pre.pull-failed`.
  - `t_flush`: a dirty session file on `main` → committed with `NOISSUE Add dev-workflows session artifacts (/feedback)` and pushed, nothing printed past the `Environment:` line; with `--commit-key ACME-1` the subject opens `ACME-1`.
  - `t_flush_locked`, `t_flush_commit_failed` (m12): an `index.lock` → the *Locked* row in its `Specs preflight:` form; a `pre-commit` hook that exits 1 → the *Commit failed* row in that form.
  - `t_retry`: an earlier run's unpushed session commit on `main` → pushed, silent.
  - `t_merged_leave`: HEAD on a fast-forward-merged `prd/A-1-x` with a dirty session file → switched to `main`, `prd/A-1-x` deleted, `Specs preflight: deleted merged prd/A-1-x` printed, the flush on `main`, `b2_left: "prd/A-1-x"`; where `resume.md` differs between the two so the switch is refused → the flush on the branch and `pre.merged-flush`'s cherry-pick line.
  - `t_settle`: another fast-forward-merged plugin branch with an existing upstream → `deleted merged`; a squash-merged one → the `-D` advisory once, and not again after `start --rerun`; one with a session-file commit `origin` lacks on its pushed upstream → `pushed 1 session-file commit(s) left on <branch>`.
  - `t_refusal_record_removed` (m17): B2 deleting a fast-forward-merged `prd/A-1-x` whose push-refusal record file stands under the common git directory → the file gone; the settle loop deleting another whose record is the `branch.<b>.workflowsPushRefused` key → the key gone (skipped as root where it needs an unwritable file).
  - `t_b3_b4`: on unmerged `spec/ACME-1-01-x` with keys `{ACME-1-01, ACME-1}` → stays (B3); with keys `{ACME-2}` → switched to `main`, `pre.b4` with its count clause where the branch holds an unpushed commit, `b4_left` set.
  - `t_b2`: HEAD on a fast-forward-merged plugin branch, clean → switched to `main`, `pre.deleted`, `b2_left` set; on a squash-merged one → switched, `-d` refused, `pre.delete-failed` with git's first line and `pre.b2-squash`'s `branch -D` line after it, the branch kept.
  - `t_rerun`: after `t_b3_b4`'s B4, `start --rerun --key ACME-2 --key ACME-1-01` → back on `spec/ACME-1-01-x`; with the branch deleted meanwhile → `pre.rerun-failed`. `t_rerun_no_record` (m8): `--rerun` with no record of this command → a fresh start. `t_rerun_resume` (item 3): after a first start with keys `{ACME-2}`, a `start --rerun --key ACME-2 --key ACME-1-01 --budget 0` with two other plugin branches to push → its `next.run` names `start --resume` with `--specs` as given, `--key ACME-2 --key ACME-1-01` in that order, and no `--key` it did not pass; the record's `args.keys` is `["ACME-2", "ACME-1-01"]`; following `next` continues the same record — no `replaced`, the switch back not made twice — to `stage: "done"`, each branch pushed once; and a `start --resume` with the first start's keys `{ACME-2}` instead fails `resumable` and runs fresh.
  - `t_nonff_order` (M3): `origin/main` moved by another clone, a dirty session file on `main`, and a fast-forward-merged `prd/Z-9-z` whose upstream is gone, so its `-d` test reads `HEAD` → the first call's `print` holds no settle line and `next.run` names `replay --for start --branch main`; the replay's line comes next and its `next.run` names `start --resume`; that call prints `deleted merged prd/Z-9-z` — the replay's line precedes the settle line across the calls, as SRG §3.4 orders them — and ends `next: null`, `stage: "done"`, `origin/main` holding both changes.
  - `t_settle_queue` (R3): two other plugin branches each rejected as non-fast-forward in the settle loop → both queued; following `next` runs the two replays in order and then `start --resume`, which runs §3.5.
  - `t_budget_resume` (Review Focus 5): three other plugin branches each holding a pushable session-file commit, `--budget 0` → each call makes one capped call and returns `next` naming `start --resume`; following `next` to its end leaves every branch pushed exactly once and the same final state as one call with the default budget on a copy of the same world; every `--resume` call's JSON carries the full field set.
  - `t_replaced` (Review Focus 2): a record of `/create-ard` from an interrupted run → `start --command /create-ard` reports `replaced: {"command": "/create-ard", "started": …}` and the new record holds no flag of the old one.
  - `t_two_commands` (m4, nit 9, Review Focus 1): a dirty `notes.md`, then `start --command /specify` (its G1 block lists `notes.md`); then a dirty `notes2.md`, a new session file, and `start --command /feedback` (its G1 block lists both) and `end --command /feedback` → `/feedback`'s line is followed by its own two-path block, its session file committed, `/specify`'s record still standing, unchanged; then `end --command /specify` → its line is followed by the block its own start saved, naming `notes.md` alone, and its record is removed.
  - `t_prune` (nit 23, N5): after a `start`, a record of another session touched 8 days ago is gone; one touched 6 days ago stays; a record of the current session's other command touched 8 days ago stays.
  - `t_resume_stale` (N4): a stale `/create-ard` record with `specs_git: misrooted` at stage `done`; in process, a fresh `start --command /create-ard` stopped before its first write (`state.save` replaced by one raising `KeyboardInterrupt` on its first call), leaving the stale record on disk; then `start --resume --command /create-ard` with the same arguments → a fresh preflight, `specs_git: null`, no misrooted line; the same with a stale record at stage `settle` saved 20 minutes ago → fresh too; and one at stage `settle` saved now with the same arguments → continued from `settle`.
  - `t_exit2_nothing_done` (R2): without the session variable, and with `--key bad`, exit 2, one line, no record, and `git status`, `HEAD`, the branch list and the refs are as they were.
  - `t_error_after_write` (R2): in process, replace the settle step by one that raises after `t_flush`'s commit → exit-0 result, `error` set, `print` holding the `Environment:` line and `pre.stopped`'s line, the commit pushed, the record saved.
- [ ] **Step 2: Run** the selftest. Expected: FAIL.
- [ ] **Step 3: Implement** `start` as the stages say, the budget check before each capped call and before each wrapped move's `lift`, the record saved first at stage `fetch` and again at each stage boundary.
- [ ] **Step 4: Run** the selftest. Expected: PASS.
- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git start — specs-preflight by script, resumable, its replays in calls of their own`

### Task 8: Session-branch mode in `start` and `end`

**Files:** Modify `plugins/workflows-core/scripts/specs-git.py` (the mode branches of Tasks 5–7, selftest `scenarios_mode`).

**Interfaces:**
- Consumes: `sb.mode`, `sb.commit`, `sb.lift`, `sb.put_back`, Part 1's `push_scope(…, session_default_ref)`.
- Produces, without changing any CLI shape:
  - `start`: §8.1 at `fetch` (never under misrooted) — `mode`, `session_branch`, the second fetch of the session branch (60 s, silent where it fails); §3.3's G2 variants; §3.4 in the mode — the catch-up wrapped in `lift`/`put-back`, the flush through `sb.commit` (`--include-ahead` where HEAD is the default branch) with `pre.created.*` where it printed `created: true`, the session branch pushed under §8.4's conditions, a rejected session push in its `Specs preflight:` form, a plugin branch's rejection with `reason.session-mode` and `remedy.session-wrap`; §3.5's B2, B4 and the re-run's switch back each wrapped; the closing `put-back` (also where a guard ended the preflight, never under misrooted); `lift`'s `unpreserved` → `sb.commit` with §4 step 4's message, then `lift` again, a second `unpreserved` skipping the move as a refused switch; no identity → nothing committed in the mode, moves unwrapped; an `sb` call raising `NotRun` → `pre.session-not-run`, the run going on. A creation by any of `start`'s calls but its flush is saved as `session_branch_created`. The budget check comes before a wrapped move's `lift`, never between it and its `put-back`.
  - `end`: §4 step 2's catch-up wrapped; step 4 by `sb.commit` (its `committed` and `files` filling the row, `committed: null` → `nothing`); the session branch pushed under §8.4; the rows `pushed-session` (with `<F>` from `diff --name-only -z --no-renames <default-ref>...refs/heads/<session branch>`), `no-identity`, `session-not-run`, the not-pushed rows naming the session branch, `row.session-rejected` and its conflict ending; every session append of SRG §6 in its order, the created append from `session_branch_created` — saved in the record by `start`, passed as `--session-branch-created` (a creation by a call the command or its handoff made), or set by `end`'s own `sb.commit`; `app.session.unsupported` where `mode` is `unsupported`; on a default-branch push `origin` refused outside the mode, `app.mode-on` (or `app.mode-on.no-identity`).

- [ ] **Step 1: Write the failing selftests**, `scenarios_mode(tmp)`, with `git config workflows.sessionBranch true` and `GIT_USER_INITIALS=ab` unless a case says otherwise:
  - `m_created`: a clean `main` → `start` prints `pre.created.empty` naming `session/ab` and the base sha7; a dirty session file → `pre.created.committed`; the session branch pushed; the overlay in place after `start` (the working copy equals the branch's version).
  - `m_end_pushed`: `end` with a new session file → `pushed-session` naming `session/ab` and `<F>`; `--session-branch-created abc1234` → the created append.
  - `m_no_identity`: no `GIT_USER_INITIALS`, no `user.initials`, no inferable identity → `end`'s `no-identity` row; `start`'s B4 move runs unwrapped.
  - `m_not_run`: `session/ab` checked out in a second worktree → `end`'s `session-not-run` row naming it; `start` prints `pre.session-not-run`.
  - `m_g2`: on `feature/x` → G2's session-branch lines; on `session/ab` itself → its own variant.
  - `m_unsupported`: a `git` shim first on `PATH` that fails `merge-tree --write-tree` (as `session-branch.py`'s selftest builds one) → `mode: "unsupported"`, the run as with the mode off, and `end`'s line ends with `app.session.unsupported`.
  - `m_wrapped_b4`: on an unkeyed plugin branch with the overlay holding a session file → B4 switches, and after `start` the overlay is back over `main`.
  - `m_budget_overlay` (m9): the same world with a catch-up to make and `--budget 0` → at every `start` call's return, no `lift` stands without its `put-back` (each session file's working copy is the session branch's version); following `next` ends as one call would.
  - `m_no_replay`: a plugin branch's settle push rejected in the mode → `reason.session-mode` with the `lift`/`put-back` remedy; `pending` stays empty.
  - `m_canned`: the renderer over canned `sb.commit` results → `sync.conflict` from each source, `sync.error`, `unsettled`, `stranded`, `row.session-rejected` with both endings, the session refused remedy, `app.mode-on` with and without an identity.
- [ ] **Step 2: Run** the selftest. Expected: FAIL.
- [ ] **Step 3: Implement** the mode branches.
- [ ] **Step 4: Run** the selftest, then `python3 plugins/workflows-core/scripts/session-branch.py --selftest`. Expected: both PASS.
- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git — session-branch mode in start and end`

### Task 9: The skill, the loader, the call sites and the references

**Files:**
- Create: `plugins/workflows-core/skills/specs-git/SKILL.md`, `plugins/workflows-core/skills/specs-git/run-key-set.md`
- Modify: `plugins/workflows-core/skills/reference/SKILL.md`; the six commands `plugins/workflows-core/commands/{feedback,prompt,prompt-brainstorm,prompt-grill-me,frames,diagnose-session}.md`; `plugins/workflows-core/references/specs-repo-git.md` (intro, §1 rule 8, banners, §7); `phase-handoff.md` (§4.3); `session-hygiene.md` (§7); `architecture-promotion.md` (§1 step 4); `specs-git.py` (selftest `scenarios_skill`); `docs/superpowers/to-fix.md` (LC31 deleted)
- Regenerate: `plugins/workflows-core/reference-parts/`

**Interfaces:**
- Consumes: the CLI of Tasks 2, 5, 6 and 7, exactly.
- Produces: `Skill(skill: "workflows-core:specs-git", args: "start" | "end" | "declined")`, which the loader and every caller use.

- [ ] **Step 1: Count before** (claim-sweep refinement 7, whitespace-collapsed, refinement 4's scope): ``references/specs-repo-git.md` and execute its`` (expect 12, two in each of the six commands); `executes its steps inline` (expect 3: SRG, `feedback-emission`, `followup-emission` — only SRG's is this batch's claim; the other two describe their own references); `Cite and execute \`specs-preflight\`` and `Cite and execute \`commit-artifacts\`` (expect 1 each, SRG §7); `(\`workflows-core:specs-repo-git\` §3), as a keyless run` (expect 1, `architecture-promotion`); `Nothing else is written here` (expect 1, SRG §1 rule 8); `execute that entry point of it inline` (expect 1, the loader); `workflows-core:specs-git` (expect 0).
- [ ] **Step 2: Create the skill** — exactly this text, then cut nothing it says and add nothing it does not:

````markdown
---
name: specs-git
description: Runs a command's specs-repository start and end (specs-preflight, commit-artifacts) through specs-git.py, and says which of its lines to print and where.
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
- `--key <K>` (start), once for each key of the run key set, as `${CLAUDE_PLUGIN_ROOT}/skills/specs-git/run-key-set.md` defines it — read that file before your first start call, unless its text is in this conversation word for word. Where your command's start paragraph names its key set, take its words.
- `--commit-key <K>` (start and end) — the one key the run addressed: an Epic run's own key, never its parent's; a slice's key; where several, the first resolved. At start, only where it is already resolved. At end, the key your command's commit paragraph names for `<KEY>`. Omit it for none; the commit then reads `NOISSUE`.
- `--register-rebuild <path>` (start and end) — only where your command hands `register_rebuild`: that path.
- `--rerun` (start) — only on a second start in one run with a changed key set: `/document` and `/release-notes`, after the operator entered a slice key at their BRD-container stop.
- `--no-preflight` (end) — where your run stopped before its start call.
- `--misrooted-stdin` (end) — where your run carries `specs_git: misrooted` from anything but this skill's start — `specs-root-check`'s `SPECS_PATH_INSIDE_TREE:` stop, `env-check`'s `Environment changed:` line, or `session-hygiene` §6's `RESUME_ENVIRONMENT_CHANGED:` line — with that notice, verbatim, on stdin: `<<'EOF'`, the notice, `EOF`.
- `--session-branch-created <sha7>` (end) — where a session-branch `commit` or `lift` that your command, or its handoff, ran printed `created: true` (`/implement` keeps it as run-state `session_branch_created`): the `<base short sha>` taken then.
- `--declined '<path>'` (end), once for each path — only where a `declined` call below could not run.

## Start

Make the call where your command's start step stands, once its run key set is known. Then **print every entry of the JSON's `print`, verbatim and in order, as your next output** — the `Environment:` line first, then each notice or line, an entry of several lines inside a `text` fence. These are the lines your command's text tells you to emit at its preflight: print each once. For the rest of the run, read the preflight's results from the last `start` JSON — the first call's, or the last `start --resume` a `next` led to: `specs_git` (`blocked` or `misrooted`), `default`, `default_ref`, `remote`, `offline` and `offline_clause`, `session_branch`, `branch` and `b2_left` — wherever your command's text reads them. A `replaced` field names a record an unfinished earlier run of this command left in this session; it changes nothing you do.

## End

Make the call where your command's commit step stands: its last action, or the step before a phase that hands the session elsewhere. Its `print` is the run's `Specs repo:` line, then any notice that line repeats, then any line that follows it. Put them where your command says — in its final report, or here as the run's last output — verbatim, in order and once; nothing after them restates the report.

## When the JSON names `next`

Print that call's `print` first. Then run `next.run` exactly as given, as a Bash call of its own with `next.timeout_ms` as its timeout, and treat what it returns the same way, until `next` is null. Where such a call ends with no exit status of its own — the harness stopped it at its timeout — run `next.on_timeout`, or, where that is null, the same call again. Where a first `start` or `end` call ends that way, make it again with `--resume` added.

## Declined

Where a handoff's consent choice is answered with its second or third option, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" declined --command /<name> --path '<path>'`, one `--path` for each path of that handoff's `deliverable_paths`. It prints nothing for you to show. Where it exits 2 on a line that does not begin `specs-git: not run (usage:`, keep the paths and pass them to your end as `--declined`.

## Where the script cannot start

Exit 2 means it did nothing: one `specs-git: not run (…)` line on stderr. Where that line begins `specs-git: not run (usage:`, your call was wrong: correct it and make it again. Otherwise print the line and run this entry point by hand from the reference — `Skill(skill: "workflows-core:reference", args: "specs-repo-git")`, then its §3 for start or its §4 for end — and run your run's other entry point by hand too. JSON with `error` set did part of its work and says so in `print`: print it and go on; never run that entry point again by hand.

## Citations

Which citations of `workflows-core:specs-repo-git`, by name or by its file's path, this text and the script's output serve, and which still read the reference, is the `reference` loader's paragraph on `specs-repo-git`. The run key set is `run-key-set.md`, beside this file.
````

- [ ] **Step 2a: Create `plugins/workflows-core/skills/specs-git/run-key-set.md`** — the run-key-set rule's one copy, which the skill's `--key` bullet and the loader's paragraph both name, so a Phase 0 citation of §3.2's run key set, made before the skill is loaded, reads about 1 KB instead of the 163 KB reference. Exactly this text, which Step 8a then checks against §3.2:

```markdown
# The run key set — what `specs-git start --key` takes

`workflows-core:specs-repo-git` §3.2's *Run key set*, for a run that calls the `specs-git` skill. A citation of that rule is served by this file.

The run key set is every key the run is scoped to — the identity each of this run's own branches is named for — taking each key already resolved where the call is made. It exists only to recognise this run's branches. A PRD-scoped run contributes its PRD key. An Epic-scoped run — one whose single address resolved an `EPIC-` folder, on any command that takes an Epic address — contributes both the Epic's key and its parent PRD's, because the Epic's key carries its ancestry, whether or not the run reads the PRD. A command whose keys come off its arguments (`read-key`), or off the carrier the folder an `@<path>` names asserts, contributes each such key — `/vuln` one per token that carries one. Where no key is resolved when the call is made, the set is empty and the run is keyless; never defer the call to obtain a key a later phase would mint.

`/create-prd` always contributes its folder's key, on both routes, and no route is ever treated as keyless: an empty set would send a resumed run off its own unmerged branch, and its handoff to a duplicate branch ending `-2`. What stays keyless is a run that resolved no key where the call is made, never a route. A key is a folder's identity, matched against branch names exactly, a longer key as a shorter one. The commit's key is a different input, the skill's `--commit-key`.
```

- [ ] **Step 3: Route the loader.** In `skills/reference/SKILL.md`:
  - `allowed-tools: Read, Bash` becomes `allowed-tools: Read, Bash, Skill`.
  - The second paragraph's closing clause `save, either way, a request the entry-point rules answer from an entry point's own file.` gains `, or one the paragraph on \`specs-repo-git\` below routes or serves`; the paragraph opening `To read the whole reference —` gains the same exception beside its entry-point one; and the closing sentence `When a second argument names an entry point, execute that entry point of it inline.` gains `, save the two the paragraph on \`specs-repo-git\` routes to its skill`.
  - A new paragraph goes before `To read the whole reference`, unwrapped:

```markdown
**Two entry points of `specs-repo-git` run in a script.** A request `args: "specs-repo-git specs-preflight"` or `args: "specs-repo-git commit-artifacts"` reads no reference: invoke `Skill(skill: "workflows-core:specs-git", args: "start")` for the first and `args: "end"` for the second, and follow that skill. A request `args: "specs-repo-git"` made for a citation of it — by name or by its file's path — reads nothing more in two cases: a citation in a command's own start or end step (the paragraph that makes either request or calls that skill, and the command's commit step), which that skill's text and its script's output serve; and, anywhere in a command's own text, a citation of its §3.2 run key set, its §5 notices or its §6 outcome lines. For the run key set read `${CLAUDE_PLUGIN_ROOT}/skills/specs-git/run-key-set.md`, unless its text is in this conversation word for word; §5's notices and §6's lines are what the script prints. Every other request on `specs-repo-git` — a citation anywhere else in a command, one a step of another reference makes, a command's own session-branch call, a commit into a documentation repository in its §4 step 4's form, and that skill's fallback — reads the whole reference, as before.
```

  The paragraph opening `These entry points read their own file:` is not touched (`check-citations` pins it word for word).
- [ ] **Step 4: Switch the six commands.** In each, the start sentence ``Cite `${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` and execute its `specs-preflight` entry point (§3) inline`` becomes ``Invoke `Skill(skill: "workflows-core:specs-git", args: "start")`, which runs the `specs-preflight` entry point of `${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` (§3) by script, and follow it``, and the end sentence the same with `end`, `commit-artifacts` and §4 — the rest of each paragraph unchanged, the new sentence on one line where its paragraph is hard-wrapped. `diagnose-session.md`'s "with an empty run key set" stays beside it.
- [ ] **Step 5: `architecture-promotion.md` §1 step 4**: `Then \`specs-preflight\` (\`workflows-core:specs-repo-git\` §3), as a keyless run.` becomes `Then \`specs-preflight\` — \`Skill(skill: "workflows-core:specs-git", args: "start")\`, which runs \`workflows-core:specs-repo-git\` §3 by script — as a keyless run.`
- [ ] **Step 6: `phase-handoff.md` §4.3**, its *What each option means* paragraph, after "the producer emits §4.1's "Declined by the user" line either way": `On either, it also records the declared paths for the run's terminal commit, \`Skill(skill: "workflows-core:specs-git", args: "declined")\` with this handoff's \`deliverable_paths\`, so that commit's \`Specs repo:\` line says the deliverable stays uncommitted as the user asked (\`specs-repo-git.md\` §6).`
- [ ] **Step 7: SRG (R1: the step-by-step text stays, and cannot be read as a procedure to run by hand).**
  - The intro's "cites this file and executes its steps inline" becomes "runs them through the `workflows-core:specs-git` skill, which runs `scripts/specs-git.py`; this file is the contract that script follows and is tested against, and the procedure a run follows by hand only where the skill says the script cannot start".
  - §1 rule 8, *State of its own*: "Nothing else is written here" becomes true again with one clause before it: the run's state record, outside every repository (§7), which `scripts/specs-git.py` writes and removes.
  - Directly under `## 3.` and under `## 4.`, one paragraph each: ``**Run by `scripts/specs-git.py`.** A run reaches this entry point through `Skill(skill: "workflows-core:specs-git", args: "start")` — the loader routes `args: "specs-repo-git specs-preflight"` there — which runs `specs-git.py start` and prints what it returns. What follows in §3 is the rule that script follows and is tested against, and the fallback the skill names where the script cannot start; it is never a procedure to run by hand beside the script. Parts of it — `phase-handoff.md`'s applications above all — are applied by other steps too, and those steps read this text as before: `phase-handoff.md`'s three entry points apply §3.1 to §3.6, and `session-hygiene.md`, the emission references and others cite it besides (`grep -lE 'specs-repo-git(\.md)?`? §' plugins/*/references/*.md` lists them).`` For §4: `end`, `commit-artifacts`, `specs-git.py end`, "in §4", and its second sentence: ``Parts of it — `phase-handoff.md`'s applications above all — are applied by other steps too, and those steps read this text as before: `phase-handoff.md`'s three entry points apply step 4's commit-and-restore form, step 5's push target and `push-scope`, step 6 and §4.1; the documentation commands run step 4's form against their own repositories; and the references the grep above lists cite it besides.`` Count before writing them what the banners name, and do not undercount: at `bfa147fd`, `require-on-main`'s file cites SRG §1, §2.1, §2.2, §3.1–§3.6, §4 steps 5–6, §4.1, §5 and §8; `handoff-to-main`'s §1, §2.1, §2.2, §3.1–§3.6, §4 steps 4–6, §4.1 and §8; `branch-check`'s §1, §2.1, §2.2, §3.1–§3.3, §3.5, §3.6, §4 steps 5–6 and §8; and 16 reference files besides SRG cite its sections, `phase-handoff.md` and `session-hygiene.md` among them (`grep -lE 'specs-repo-git(\.md)?`? §' plugins/*/references/*.md | grep -v references/specs-repo-git.md | wc -l`; per entry, `grep -oE 'specs-repo-git(\.md)?`? §[0-9]+(\.[0-9]+)?( step [0-9]+)?' plugins/workflows-core/reference-parts/phase-handoff/<entry>.md | sort -u`).
  - Under `## 5.` and `## 6.`: one sentence each — the script renders every block and line below, and a run prints what it returns.
  - Under `## 8.`: inside `start` and `end` the script makes these calls itself; a command that moves the checkout or commits session files by its own text (`/dev-workflows:implement` on a direct run from inside the specs repository), and `phase-handoff.md` around its own moves, still make them as this section says.
  - §7 rules 1–3: "Cite and execute `specs-preflight` (§3)" becomes "Run `specs-preflight` (§3) through the skill's `start`", and the same for `commit-artifacts` with `end`; the *One optional input* paragraph adds that the skill passes `register_rebuild` as `--register-rebuild`. Then this paragraph, unwrapped:

```markdown
**The run's state record.** What the two entry points share, and what a run once carried only in its conversation, `scripts/specs-git.py` keeps in one file per Claude Code session and command, `~/.claude/dev-workflows/specs-git/<session id>/<command>.json`. The session id is `CLAUDE_CODE_SESSION_ID`, which Claude Code sets in every Bash tool subprocess, equal to a hook's `session_id` and updated on `/clear` (its environment-variables page, https://code.claude.com/docs/en/env-vars) — the `session_id` `cost-emission.md` §1 reads off the transcript's name. The record holds the flags and the notice that set `specs_git: misrooted`, the guard block §4 step 7 repeats and the paths it lists, `<default>`, `<default-ref>`, `remote` and the offline clause, `session_branch`, `mode` and `session_branch_created`, the branches §3.5's B2 and B4 left, the branches §3.4's `-D` advisory has named, the deliverable paths a declined handoff recorded (§6), the run's `Environment:` line, and where an interrupted `start` or `end` stands. `start` opens a fresh one for its command, setting aside whatever stood there — save on a re-run (§3.5) and on its own continuation — and removes every other session's record more than seven days old; the skill's `declined` adds to it; `end` reads it, compares the `SPECS_PATH` half of the run's `Environment:` line with the one the record holds (§4 step 1), and removes it as its last act. A `--resume` continues a record only where its stage is not done, its arguments are the call's, and it was saved within the last 15 minutes. **Why it is safe.** It lives outside every repository, so no staging sees it, and `/dev-workflows:implement`'s `run-state.py remove`, which removes files in the code repository's git directory, cannot reach it. One file per session and command keeps two sessions on one specs repository apart, and a command typed in the middle of another's run off the outer run's record. The session id survives a compaction, which the conversation's text does not. A nested run is another command, and starts only after its parent's `end` (§4's exception: `/product-workflows:brd-split`'s *Ground now*). A subagent carries its parent's session id, and no agent runs either entry point. A run started `--inline` by another command calls neither. A run whose id changes before its end — a `/clear`, or a resume that hands it a new one — finds no record there, and its `end` runs as a run with no preflight does (§4 step 1), on the flags the run passes. It is not kept in the specs repository's git directory because §3.1's gate fails exactly where that directory is missing or unwritable, while a not-a-repository `$SPECS_PATH` with a `specs-root-check` signal still sets the flag whose notice `end` repeats. Where `CLAUDE_CODE_SESSION_ID` is unset, the script runs neither entry point (exit 2, nothing done), and the run follows this reference's prose instead.
```

- [ ] **Step 8: `session-hygiene.md` §7**, *The line.*: after "what this one Bash call prints", add ", which `scripts/specs-git.py` runs as written — its selftest holds the two equal".
- [ ] **Step 8a: Check `run-key-set.md` against §3.2 (N7).** Read SRG §3 (its opening on `read-key` and `@<path>` keys) and §3.2's *Run key set*, *`/create-prd` contributes a key*, *Neither route may be classified keyless*, *The contributed key is a folder identity* and *This run key set is the preflight's* paragraphs, sentence by sentence, against `run-key-set.md`; list each rule with the sentence of that file that carries it, and write into the file any rule it lacks. The list goes into Task 12's record. Then the loader's claim — that a citation of §3.2's run key set is served by that file — holds.
- [ ] **Step 9: Pin the skill to the CLI.** Selftest `k_skill_options`: every `--<option>` the skill's text names is an option the parser accepts for `start`, `end` or `declined`, and each of `start`, `end`, `declined` is a subcommand; `k_loader_routes`: the loader's text names `workflows-core:specs-git` with `args: "start"` and `args: "end"`, and its `allowed-tools` holds `Skill`; `k_key_set_file`: `skills/specs-git/run-key-set.md` exists, and both the skill's text and the loader's name it by that path; `k_no_dollar_session`: no file under any plugin's `commands/`, `agents/`, `references/`, `hooks/` or `skills/` — the directories checks 5 and 9 read — holds the variable's name after a `$` or a `${`, the pattern built from pieces (`"$" + "CLAUDE_CODE_SESSION_ID"`) so the script holding the test never matches it. Run it. Expected: PASS.
- [ ] **Step 10: Delete LC31** from `docs/superpowers/to-fix.md` (its whole bullet, sub-bullets included): the script now returns the session branch's creation line and each guard's notice, and the skill makes printing them the run's next output.
- [ ] **Step 11: Count after.** ``references/specs-repo-git.md` and execute its`` 12 → 0; `executes its steps inline` 3 → 2 (SRG's gone); `Cite and execute \`specs-preflight\`` and `… \`commit-artifacts\`` 1 → 0 each; the `architecture-promotion` phrase 1 → 0; `Nothing else is written here` stays 1, now beside the record; `execute that entry point of it inline` 1 → 1, with its exception; ``workflows-core:specs-git", args: "start"`` → the 6 commands + the loader + SRG §3's banner + `architecture-promotion` (count and record the figure). Re-derive the thirty-five: `grep -lE 'commit-artifacts\` entry point|args: "specs-repo-git commit-artifacts|workflows-core:specs-git", args: "end' plugins/*/commands/*.md | wc -l` → 35.
- [ ] **Step 12: Regenerate and gate.** `python3 scripts/reference-parts.py generate`, then the gate chain. Expected: `EXIT=0`; `check-citations` passes the loader's pinned paragraph; check 16 counts the loader calls as before; check 5 finds no new variable (the session variable is never written with a `$`); `validate-catalog.py` passes the skill's description (153 characters).
- [ ] **Step 13: Commit** — `feat(workflows-core): the specs-git skill — every command's start and end runs by script; LC31; D2`

### Task 10: Docs tree, rules and the claim-expiry sweep

**Files:**
- Modify (`workflows-core`): `docs/reference/references.md` (the `specs-repo-git.md` entry; its *References that load by part* and *Entry points with a file of their own* paragraphs' "reads the whole reference, as on any other reference" sentences; § Skills: count, prose, a `specs-git` row, the `reference` row), `docs/README.md` (`the two bundled skills` → `the three bundled skills`, naming `specs-git`), `docs/workflow.md` (the opening sentence, a `skills/specs-git` node with a solid edge to the pipeline, "The three solid edges" → four, the paragraph naming the skills), `docs/getting-started.md` and `README.md` (the skill-listing figure; line 9 names the skill)
- Modify (other plugins' docs only): `plugins/security-workflows/docs/workflow.md`; the four other plugins' getting-started pages (`dev-workflows`, `docs-workflows`, `guideline-reviewers`, `product-workflows`), which carry the listing figure; the four other plugins' `docs/reference/environment.md` (`dev-workflows`, `docs-workflows`, `product-workflows`, `security-workflows`), which say when a run compares its environment; the root `README.md`
- Modify (`workflows-core` docs, D4): `docs/reference/environment.md` and `docs/reference/references.md`'s `session-hygiene.md` entry
- Modify (instruction tiers): `.claude/rules/workflows-core.md`, `.claude/rules/workflows-core-git.md`, `.claude/rules/workflows-core-handoff.md`, `CLAUDE.md`, `docs/maintainers/rationale.md` (`## specs-git-state-record`, `## skill-listing-figure`); `.github/workflows/validate-catalog.yml` (the specs-git step's comment)

**Interfaces:** none.

- [ ] **Step 1: Count before**, whitespace-collapsed over refinement 4's scope: `two bundled skills` (expect 2), `Two skills ship` (1), `its \`model-routing\` skill the named one` (1, `CLAUDE.md`), `Both are listed in` (1, `workflow.md`), `The three solid edges` (1), ``(`args: "specs-repo-git specs-preflight"`)`` (1, `CLAUDE.md` § Internal reference convention), `Neither skill reads a file again` (1), `as it does on any other reference` and `as on any other reference` (1 each, `references.md`), `its state of its own is` (1, `workflows-core-git.md`), `Nowhere else.` (1, `security-workflows/docs/workflow.md`), `about 5,800 characters` (10: the root `README.md`, five getting-started pages and four CHANGELOG entries), and the agent check of R5: `grep -lE 'args: "specs-repo-git (specs-preflight|commit-artifacts)|workflows-core:specs-git' plugins/*/agents/*.md | wc -l` (expect 0). Then run the exclusivity probe (refinement 3) over the same scope for the loader and the skills — `the only`, `the sole`, `only way`, `named one`, `Both exist`, `Neither skill` — the subject sweep (refinement 6) for the preflight and the commit being executed by reading SRG, or SRG being read whole at start and end — `read whole`, `reads it whole`, `two reads`, `execute its \`specs-preflight\``, `execute its \`commit-artifacts\``, `specs-repo-git.md\` and execute` — and the subject sweep for where a run writes, over every plugin's `docs/`: `Nowhere else`, `nothing (else )?(is )?written outside`, `writes only`, `~/.claude/dev-workflows`. Record each hit and its disposition. Already known: `skills/reference/entry-files.md` holds no such sentence (`grep -c specs-repo-git` → 0); the other plugins' commands' `execute its … entry point` sentences stay true (the loader routes them); the thirty commands restating "otherwise silent unless it acts, a guard fires, or §3.1 reports" stay true (the offline note is carried, not printed); `docs/superpowers/to-fix.md` PR10 is Task 11's; `docs/maintainers/rationale.md`'s lean-context table row is a dated measurement and stays; `docs-workflows/docs/workflow.md`'s *Where each command writes* lists two places and claims no others, so it stays.
- [ ] **Step 2: `workflows-core` docs.** `references.md`'s `specs-repo-git.md` entry gains: a run reaches both entry points through the `specs-git` skill, which runs `scripts/specs-git.py`, and the reference is the contract the script follows. The two "reads the whole reference, as (it does) on any other reference" sentences, and § Skills' "The text a request needs is the whole file, except for … a request the file of an entry point above serves", each gain: save the two `specs-repo-git` entry points the loader hands to the `specs-git` skill, which read no reference, and the citations that skill's text serves. § Skills: "Three skills ship"; the shared-reason sentence becomes true of the two reading skills and the third is described on its own (it reads no reference: it runs the script and keeps the run's state in a file of its own under `~/.claude/dev-workflows/specs-git/`, removed when the run ends); every "Both"/"Neither skill" becomes "Both reading skills"/"Neither reading skill" where it is about reading. The `reference` row's third cell names the routing (a `specs-repo-git` start or end request goes to `specs-git`). New row, each cell under 200 characters, no `§`: ``| `specs-git` | No — loaded internally, at the start and the end of every command that writes into the specs repository | Runs `scripts/specs-git.py` for a run's specs-repository start and end, keeps their shared state across the run, and says which lines to print. |``.
- [ ] **Step 3: The listing figure (N6)** — the root `README.md`'s sentence and the five getting-started pages' copies, "about 5,800 characters".
  - **Its history:** `git log -S 'about 5,600' -- README.md` → `649e8454`; `git log -S 'about 5,800' -- README.md` → `1f72f4fd`; no recipe recorded with either.
  - **The recipe**, a Python block written into `docs/maintainers/rationale.md` under a new heading `## skill-listing-figure` (the file's convention: the heading is its anchor):
    - read `.claude-plugin/marketplace.json`; for each plugin, each `skills/<name>/SKILL.md` and each `commands/<name>.md`;
    - skip one whose frontmatter sets `disable-model-invocation` to `1`, `true`, `yes` or `on` in any case;
    - where a command and a skill share a name, count one entry, the command's;
    - count each entry as `len("<plugin>:<name>") + len(description) + len(when_to_use) + 5`, the 5 being `- `, `: ` and the line break, as *typed-only-commands* records the binary's format;
    - read a description written as a YAML block scalar (`>`, `|`) folded as YAML folds it.
  - **The check, in the same section:** it reproduces both published figures — 5,556 at `649e8454` ("about 5,600") and 5,866 at `1f72f4fd` ("about 5,800") — run on `git archive <sha> .claude-plugin plugins` unpacked in a scratch directory. It gives 3,184 at `bfa147fd`: the figure has been stale since `e003f181` (2026-10-26) took `obsidian-llm-wiki` out of the catalog.
  - **The new figure:** re-run the recipe on the branch's tree, with the `specs-git` skill. Expected about 3,366 (3,184 + 24 + 153 + 5), so "about 3,400", rounded to the nearest hundred. Write it in the root `README.md` (its sentence gains an HTML comment naming `docs/maintainers/rationale.md`'s `skill-listing-figure` section) and in the five getting-started pages — `workflows-core`'s and the four other plugins' (`dev-workflows`, `docs-workflows`, `guideline-reviewers`, `product-workflows`). Their patch releases (Task 11) follow from that.
  - Task 11's to-test item confirms the figure against `claude --debug`'s `Skill listing` line.
- [ ] **Step 3a: When a run compares its environment (D4, item 1)** — swept by that subject, not by the word `misrooted`, which these pages never use. Recipe: `grep -rnE 'compares the environment it|the environment check' plugins/*/docs plugins/*/README.md README.md | wc -l` → 9 at `bfa147fd`.
  - **Six change**, each copy gaining the terminal commit in one clause — `and once more at its terminal commit, which compares only \`$SPECS_PATH\`'s real path and its \`origin\` — the one check a run that hands nothing off and writes nothing in its tail meets` — worded for its page:
    - the *When it changes under a resumed conversation* paragraph of `reference/environment.md` in `workflows-core`, `dev-workflows`, `product-workflows` and `docs-workflows` (whose copy opens with `/release-notes`' draft);
    - the same paragraph of `security-workflows`' page (*Before each write of the run's tail*), whose "the terminal commit is skipped" stays;
    - `workflows-core`'s `reference/references.md` `session-hygiene.md` entry, whose "before the handoff and before each write of the run's tail" gains "and at its terminal commit".
  - **Three stay:**
    - `workflows-core`'s `commands/feedback.md`, which already names `commit-artifacts` at the end among its checkpoints, beside the check before its entry is written;
    - `product-workflows`' `commands/specify.md`, whose environment check is the session file's on a resume;
    - `docs-workflows`' `references.md` toolchain entry, another check altogether.
  - **Counts:** `at its terminal commit` over `plugins/*/docs`, 0 before and 6 after. No page gains a `§` or a decision id (check 25).
- [ ] **Step 4: `security-workflows/docs/workflow.md`**, *Where the command writes*, its *Under `~/.claude/`* bullet gains: the run's state record under `~/.claude/dev-workflows/specs-git/`, which its terminal commit step removes — so the *Nowhere else.* bullet is true again. The same sweep's other hits are fixed the same way, each in its plugin's page, each recorded with its plugin for Task 11's patch release.
- [ ] **Step 5: Rules.** In `workflows-core.md` *Plugin facts*:
  - "two bundled skills" → three, `specs-git` described in one clause;
  - the loader's description names its one routing exception (`specs-repo-git specs-preflight` and `commit-artifacts` go to `specs-git`) and its citation scope;
  - `specs-git` in the scripts list gains "with its two modules".

  In `workflows-core-git.md` **and** `workflows-core-handoff.md`, which share it, `paths:` gains `plugins/workflows-core/skills/specs-git/SKILL.md`, `plugins/workflows-core/scripts/specs_git_state.py` and `plugins/workflows-core/scripts/specs_git_lines.py`. In `workflows-core-git.md`:
  - its opening line names the skill and the two modules, and the primitives list in it ("the §2.1 status classifier, `branch-merged`, `branch-key`, `push-scope`, `owner-repo` and `mode`") gains `specs-root-check` and the `start`, `end`, `replay` and `declined` entry points;
  - the `specs-repo-git` authority paragraph says both entry points run in `scripts/specs-git.py` through the `specs-git` skill, which every request reaches (the loader routes the two requests there), and names the state record's home and key with a `([why](../../docs/maintainers/rationale.md#specs-git-state-record))`;
  - "its state of its own is …" gains the record, outside every repository;
  - the "Two run-wide flags" bullet's list of what sets `specs_git: misrooted` gains, after §6's *Stop*: `and \`commit-artifacts\` itself, where the \`SPECS_PATH\` half of the run's \`Environment:\` line no longer matches the one its preflight printed — \`session-hygiene\` §7's environment change, met at the end (D4)`;
  - its count recipe becomes ``grep -lE 'commit-artifacts` entry point|args: "specs-repo-git commit-artifacts|workflows-core:specs-git", args: "end' plugins/*/commands/*.md``, which "matches the three phrasings" and returns 35.

  In `CLAUDE.md`:
  - the rules-table row for `workflows-core-git.md` (and so the `as` row) names the skill and the modules;
  - § Internal reference convention's example becomes `` (`args: "addressing resolve-address"`) `` with ", save `specs-repo-git`'s `specs-preflight` and `commit-artifacts`, which the loader routes to its `specs-git` skill" after it;
  - "its `model-routing` skill the named one" becomes "its `model-routing` and `specs-git` skills named ones".
- [ ] **Step 6: Rationale.** A section headed `## specs-git-state-record`, the file's convention (each heading is its anchor), its first sentence saying why the state record lives under `~/.claude`, keyed by the session and the command. Its content:
  - the design's candidate was the specs repository's git directory, as `/implement`'s `run-state.py` keeps its file in the code repository's, and two facts moved it: SRG §3.1's gate fails exactly where that directory is missing or unwritable — unset, not a repository, a read-only mount — yet a not-a-repository `$SPECS_PATH` with a `specs-root-check` signal sets `specs_git: misrooted`, whose notice `end` must repeat; and nothing outside every repository is ever staged;
  - the key: `CLAUDE_CODE_SESSION_ID`, documented on Claude Code's environment-variables page (https://code.claude.com/docs/en/env-vars) as set in Bash tool subprocesses, equal to the hook input's `session_id` and updated on `/clear` — and the transcript's basename, the `session_id` `cost-emission` §1 derives by scanning transcripts (checked on 2026-11-09); the page's caveat, that `--continue` or `--resume` without an explicit id may hand an MCP subprocess the startup id, concerns MCP subprocesses, which never run the script;
  - the command half of the key: a command typed mid-run (`/feedback` during a `/specify`) must not touch the outer run's record (the plan review's finding m4);
  - the family's precedent: `~/.claude/dev-workflows/cost-state/<session_id>.json` and `cost-emission` §13.1's deferred file;
  - the safety argument as SRG §7's paragraph states it, subagents included, with the agent-file grep's result;
  - the seven-day pruning;
  - the fallback where the variable is unset: the prose, exactly as before 2a.
- [ ] **Step 7: CI comment.** The `Self-test the specs-repo git primitives` step's comment names the start and end it now also holds, and their failure mode (a commit made under a flag that should have stopped it; a notice the run must repeat lost to a compaction); the `run:` line is unchanged.
- [ ] **Step 8: Count after and measure.**
  - `two bundled skills` 2 → 0 (`three bundled skills` 0 → 2); `Two skills ship` 1 → 0; `its \`model-routing\` skill the named one` 1 → 0; `Both are listed in` 1 → 0; `The three solid edges` 1 → 0; the `CLAUDE.md` example 1 → 0; `Neither skill reads a file again` 1 → 0; `about 5,800 characters` 10 → 4, the four left being CHANGELOG history (`about 3,400 characters` 0 → 6); `the \`SPECS_PATH\` half of the run's \`Environment:\` line` 5 → 6 with the rules bullet (Task 3 placed four, Task 9 one); `at its terminal commit` over `plugins/*/docs` 0 → 6, and Step 3a's subject recipe still 9.
  - The agent grep still 0.
  - Every rules file under 20,000, `CLAUDE.md` under 36,000.
- [ ] **Step 9: Gate.** The chain. Expected: `EXIT=0` (check 4 finds the row, check 9 reads "three bundled skills", check 6, check 25, the mermaid gate parses the new node, `validate-catalog.py` finds the new `paths:` globs live).
- [ ] **Step 10: Commit** — `docs: the specs-git skill in the docs tree and the rules; the claim-expiry sweep`

### Task 11: Release

**Files:** Modify `plugins/workflows-core/.claude-plugin/plugin.json` and `CHANGELOG.md`; the same pair for each plugin Task 10 changed a page of (`security-workflows`, `dev-workflows`, `docs-workflows`, `guideline-reviewers`, `product-workflows`); `.claude-plugin/marketplace.json` (each released plugin's entry; descriptions unchanged); `.claude/rules/plugin-updates-coupling.md`; `docs/superpowers/to-fix.md` (PR10); `docs/superpowers/to-test-on-real-project.md`.

- [ ] **Step 1: Versions.** `workflows-core` the next free minor on the branch's base — `1.82.0` at `bfa147fd`; every other plugin released the next free patch — at `bfa147fd`, `security-workflows` 0.11.1, `dev-workflows` 4.62.1, `docs-workflows` 1.38.1, `guideline-reviewers` 1.2.9, `product-workflows` 3.79.1 — re-derived where `main` has moved by merge time; each in both manifests.
- [ ] **Step 2: CHANGELOGs**, each a dated section. `workflows-core`'s opens: "GIT-G1 Part 2, batch 2a: every command's specs-repository start and end runs by script, through the new `specs-git` skill. Update `workflows-core`; the docs-only patches of this batch's other plugins need nothing of it." `### Added`: the skill; `start`, `end`, `replay`, `declined`, `specs-root-check`; the state record. `### Changed`: the loader's routing, its citation scope and `allowed-tools`; the six commands' calls; SRG's fixed wordings, banners, §1 rule 8 and §7; `session-hygiene` §7; `architecture-promotion` §1 step 4; `phase-handoff` §4.3's `declined` call; D3; D4 (every terminal commit compares the `SPECS_PATH` half of the run's `Environment:` line, as written into SRG §3.1, §4 step 1, §6 and `session-hygiene` §7). `### Fixed`: LC31; D2 (*Cancel* gets the append); the skill-listing figure on the getting-started page, "about 3,400" (stale since `obsidian-llm-wiki` left the catalog, now re-derived by a recorded recipe). Docs and rules in one bullet. Each other plugin's section: "Docs only; needs nothing from the other plugins' releases." and one `### Fixed` bullet per page it corrects:
  - its getting-started page (all four but `security-workflows`): the figure, its arithmetic (3,184 at `bfa147fd` + 182 for the new skill's entry) and where the recipe lives;
  - its `reference/environment.md` (all four but `guideline-reviewers`): that a run also compares its environment at its terminal commit, `workflows-core` 1.82.0;
  - `security-workflows`' workflow page: the run's state record among what it writes under `~/.claude/`.

  Every page lands in the patch release its plugin already makes (`security-workflows` 0.11.1, `dev-workflows` 4.62.1, `docs-workflows` 1.38.1, `product-workflows` 3.79.1, `guideline-reviewers` 1.2.9); none adds a release.
- [ ] **Step 3: Coupling bullet**, after the 1.81.0 one: ``- **Update `workflows-core` to 1.82.0 alone**: no dependent changes. 1.82.0's loader routes every `specs-repo-git specs-preflight` and `specs-repo-git commit-artifacts` request — the form every command of the four dependent plugins makes — to its new `specs-git` skill, so updating `workflows-core` switches every command's start and end at once; `phase-handoff` §4.3's new `declined` call is read by every producer from `workflows-core`'s own file. The batch's other releases — `security-workflows` 0.11.1, `dev-workflows` 4.62.1, `docs-workflows` 1.38.1, `guideline-reviewers` 1.2.9 and `product-workflows` 3.79.1, for their workflow, getting-started and environment pages — are docs only: none needs 1.82.0 to run and 1.82.0 needs none of them; beside an older side, only those pages' wording is off.`` (Name only the patches Task 10 made.) Check its size under 20,000.
- [ ] **Step 4: PR10.** Its closing sentence becomes: Part 2 batch 2a (`workflows-core` 1.82.0) moved the preflight and the terminal commit behind the `specs-git` skill, so a run reads that skill's text and the script's output, not the reference, to run its start and end (measured in `docs/superpowers/verification/2026-11-09-git-g1-part2a.md`). A run still reads the reference where another step applies one of its rules — `phase-handoff`'s `require-on-main`, `branch-check` and `handoff-to-main` until Part 3 among them — and that, with the handover's own reads of `phase-handoff`, ends with Part 3.
- [ ] **Step 5: To-test items**, a new section `## GIT-G1 Part 2, batch 2a — \`workflows-core\` 1.82.0` ("Install `workflows-core` 1.82.0; the docs-only patches change no behaviour."), each item with its setup and what to expect:
  - **LC31** — a run in session-branch mode that creates the session branch prints `Specs preflight: created local session/<identity> at …` straight after its `Environment:` line; a run with a dirty unrelated path prints G1's notice there, and again after its `Specs repo:` line.
  - **The start and end reads** — a keyed `/create-ard` and a `/ready` run's transcripts show no read of `specs-repo-git.md` for the start and the end calls themselves, nor for a citation of §3.2's run key set, §5 or §6; record the bytes the skill and the script's output come to. A read the run makes elsewhere is expected and recorded separately, with the step that made it: for `require-on-main`, `branch-check` or the handoff until Part 3; for a citation outside the start and end steps — its §2.1 paths, §3.5's branch rules, §4.1, its *Ending early* tail (195 of the 272 citing paragraphs at `bfa147fd`, by Task 12's recipe); for a session-branch call the command makes itself.
  - **D4** — a run started with one `$SPECS_PATH` and ended with another (or with it unset): the end commits nothing and prints `Environment changed: …` under its `Specs repo:` line.
  - **Compaction** — `/compact` between a misrooted run's start and its end: the end still skips with the notice.
  - **Two sessions, and a command typed mid-run** — two sessions on one specs repository, one misrooted, each end reading its own state; a `/feedback` typed during a `/specify`, whose end leaves `/specify`'s state alone.
  - **Nesting** — `/brd-split`'s *Ground now* with two children: each `/prd-ground` opens a fresh state, none prints the parent's guard block.
  - **`/implement`** — a keyed run in session-branch mode: its end reports the session branch its Phase 4.6 created.
  - **D2** — a producer's consent answered *Cancel*: the `Specs repo:` line ends `; the deliverable at <path> remains uncommitted, as you asked`.
  - **The replay** — a rejected push at the end: the replay runs as a call of its own and prints its row.
  - **The re-run** — `/release-notes` on a BRD container, a slice key entered at its stop: the second start switches back to the branch the first left.
  - **The listing figure** — one session started as `SLASH_COMMAND_TOOL_CHAR_BUDGET=100 claude --debug`, so the listing is over budget and Claude Code writes `Skill listing over budget: <N> skills, <X> chars > <Y> budget` to `~/.claude/debug/latest`; `<X>` less the entries `/skills` shows outside this marketplace (Claude Code's own skills and the user's) beside the figure Task 10 wrote and `docs/maintainers/rationale.md`'s recipe re-run on the installed versions.
- [ ] **Step 6: Gate** (the chain; check 18 is unarmed off `main`, every section is dated anyway). Expected: `EXIT=0`.
- [ ] **Step 7: Commit** — `release: workflows-core 1.82.0 — GIT-G1 Part 2 batch 2a; docs-only patches beside it`

### Task 12: The verification record — written last

**Files:** Create `docs/superpowers/verification/2026-11-09-git-g1-part2a.md`.

Written after the final whole-branch review's fix pass, against the branch's own tree (`CLAUDE.md` § Editing discipline, *A sub-project's verification record is written last*); every figure re-derived, with its command beside it, none copied from this plan.

- [ ] **Step 1: The script.** `python3 plugins/workflows-core/scripts/specs-git.py --selftest` → its `PASS (<n> checks)` line; one table row per scenario group (`state`, `lines`, `gate`, `end`, `replay`, `start`, `mode`, `skill`) naming the cases it pins, and the *Not pinned* list carried from this plan's pins section, each still true.
- [ ] **Step 2: The start and end reads (design §8, PR10).**
  - **Before** (`bfa147fd`): 2 × the loader's `SKILL.md` + 2 × `specs-repo-git.md`.
  - **After:** 2 × the new loader `SKILL.md` + 2 × `skills/specs-git/SKILL.md` + `skills/specs-git/run-key-set.md` once + the JSON of a clean `start` and `end` on a fixture world.
  - `reference-parts/session-hygiene/env-check.md` is in neither: the tail's emitters load it either way.
  - Take each figure with `git show <sha>:<path> | wc -c`.
  - Then a second table, **what a run still reads, and why**, by cause:
    - a consumer's `require-on-main` and `branch-check` (their `phase-handoff` files, and `specs-repo-git.md` wherever those apply one of its rules);
    - a producer's `handoff-to-main`;
    - a citation in a command's own text outside its start and end steps that is not of §3.2's run key set, §5 or §6;
    - the fallback;
    - `/implement`'s direct-run session-branch calls;
    - a documentation repository's commit in §4 step 4's form.

    Part 3 ends the first two.
  - **The citing-paragraph measure (N7)**, its recipe written into the record as a Python block and run at `bfa147fd` and at the tip:
    - **Scope:** every blank-line-separated paragraph of `plugins/*/commands/*.md` that cites the reference — holding `workflows-core:specs-repo-git`, `specs-repo-git.md` or `args: "specs-repo-git`.
    - **Served:** a paragraph that makes a start or end request — `specs-repo-git specs-preflight` or `commit-artifacts`, a `specs-preflight` or `commit-artifacts` entry point, or `workflows-core:specs-git` — or one that cites at least one section, every one of them §3.2 in a sentence naming the run key set, §5 or §6.
    - **Reading:** every other citing paragraph, one citing no section included.
    - **Figure:** this plan measured 272 citing paragraphs at `bfa147fd`, 77 served and 195 reading; re-derive both.
- [ ] **Step 3: The command text (design §1).** State the recipe and run it at `bfa147fd` and at the branch tip: the bytes of `plugins/*/commands/*.md`, and of their blank-line-separated paragraphs matching `specs-preflight|commit-artifacts|handoff-to-main|require-on-main|branch-check|specs-repo-git|phase-handoff|workflows-core:specs-git`. This plan measured 4,417,213 and 946,519 at `bfa147fd` with that recipe; re-derive, do not copy. It differs from the design's 770 KB, which used another cut. 2a slims no wrapper, so the figure barely moves: say so.
- [ ] **Step 4: The sweep.** Each Task 3, Task 9 and Task 10 count, before and after, from the tree — the setters recipe's lines with their dispositions among them — the agent grep's 0, and Task 9 Step 8a's list of §3.2's rules beside the sentences of `run-key-set.md` that carry them. The listing recipe's three figures (`649e8454`, `1f72f4fd`, the tip).
- [ ] **Step 5: The gates and the budgets.** The chain's `EXIT=0`; `len()` of `CLAUDE.md` and every rules file the batch touched.
- [ ] **Step 6: The review.** The final review's counts by severity, and the fix pass's commit.
- [ ] **Step 7: Commit** — `docs: GIT-G1 Part 2 batch 2a — verification record`

---

## Self-review notes

- **Spec coverage.**
  - **Design §5.1:**
    - the explicit key set, keyless and Epic forms — `--key`;
    - before or after resolution — the skill's *Start*;
    - the outputs as fields — `start`'s JSON: `default`, `default_ref`, `remote`, `offline`, read-only as `gate`, `specs_git`, `session_branch`, `b2_left`, `b4_left`;
    - `register_rebuild`, the direct-`/implement` G2 variant, the LC31 lines — Tasks 7, 8, 9;
    - standalone primitives — Part 1's, with `specs-root-check` joining them (Task 4);
    - session-branch `commit`/`lift`/`put-back` for a command — `/implement`'s preparation, out of scope as said.
  - **Design §5.3:**
    - the commit stays a call of its own — `end`;
    - the commit key is explicit — `--commit-key`;
    - the outcome comes as fields and as the line — `row`, `sha7`, `line`, `print`;
    - printable in place or held, and the cede-control placement — the skill's *End*;
    - the tail-profile names — SRG §4 in 2b, which needs nothing of `end` but `--no-preflight`.
  - **Design §5.5:** every requirement by R5 save `inputs_read`, which is Part 3's.
  - **Design §6:** `/implement` — R6.
  - **Rule gap (iv):** D2, in Tasks 3 and 9.
  - **The behaviour changes:** D3, in Tasks 3 and 5; D4, written where the contract lives in Task 3 (SRG §3.1, §4 step 1, §6; `session-hygiene` §7) and Task 10 (the rules bullet), run by `end` in Task 5.
  - **Design §7 Part 2's "all 35 commands switch":** the loader, in Task 9.
  - **Design §8:** the reads, stated honestly, and the command text — Task 12.
  - **Brief:**
    - budget relief first — Task 1;
    - the release, the docs entry, the CI step, the to-test items and the record — Tasks 10–12;
    - LC31 deleted with its fix — Task 9.
- **Design §8's call-site gate is not built in 2a.** No wrapper is slimmed in this batch, so a gate over call-site shape would fire on every command still carrying its restated rules. The batch that slims the last wrapper decides whether to build it (design §9 leaves it to the builder).
- **Interfaces.** These are named once, in the task that produces them, and used by those names after:
  - `state.*`, `lines.*`, `_flow`, `gate`, `env_line`;
  - `resolve_default`, `catch_up`, `commit_session_files`, `push_check`, `push`, `classify_replay`;
  - the five CLI shapes.

  The record's path takes the session and the command everywhere, from Task 2 on. `replay` takes `--command`, which every `next.run` carries.
- **Proportion.** The plan writes out the copy that the brief fixes or that a reference must hold verbatim: the skill, the loader paragraph, SRG's new wording and record paragraph, and the release text. It gives the script as signatures, stage orders and test cases, since SRG is the algorithm.

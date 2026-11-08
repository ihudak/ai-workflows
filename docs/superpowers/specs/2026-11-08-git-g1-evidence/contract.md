# GIT-G1 — the standard call contract for the five specs-repo git entry points

Read-only extraction from `main` at `4fef611b`. Purpose: one sheet an auditor holds while reading a command's start, end and handover text. Facts only, each cited. Nothing here is a proposal except where marked **[design note]**.

## 0. Conventions, sources, how commands load these today

Abbreviations (all under `plugins/workflows-core/`):

| Short | File | Size / lines |
|---|---|---|
| **SRG** | `references/specs-repo-git.md` | 159,048 B, 1,363 lines; does **not** load by part — every `specs-repo-git specs-preflight` / `… commit-artifacts` request reads the whole file (`skills/reference/SKILL.md`, "On a reference that does not load by part, the text a request needs is the whole file") |
| **PH** | `references/phase-handoff.md` | 183,225 B, 664 lines; three entry points read their own generated file |
| **PH-h2m / PH-rom / PH-bc** | `reference-parts/phase-handoff/{handoff-to-main,require-on-main,branch-check}.md` | 348 / 234 / 104 lines. Holds: h2m = §1, §2, §4.1, §4.2, §4.3 + part §4.0; rom = pre-§1 text, §1, §2.2, §2.6.1, §3, §4.4 + part §4.0 ("never infer"), §5 (rules 2, 3); bc = §1, §2.2, §6 + part §3.3 ("Row B′'s remedy") (`skills/reference/entry-files.md`) |
| **SH** | `references/session-hygiene.md` (§7 `env-check` in `reference-parts/session-hygiene/env-check.md`; §6 in `…/resume-environment.md`) | |
| **EF** | `skills/reference/entry-files.md` | |
| **SBP** | `scripts/session-branch.py` | subcommands `mode`, `sync`, `commit`, `lift`, `put-back`, `replay`, `--selftest` (SBP header lines 11–18; argparse at 5212–5232). One JSON object on stdout; exit 2 = could not run, first stderr line reported, run continues (SRG §8 opening) |

**Two call phrasings exist in commands today** (both execute the same entry point): `Invoke Skill(skill: "workflows-core:reference", args: "specs-repo-git specs-preflight") and execute its specs-preflight entry point (§3) inline` (other plugins, e.g. `product-workflows/commands/create-ard.md:270`), and `Cite ${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md and execute its specs-preflight entry point (§3) inline` (`workflows-core`'s own commands, e.g. `workflows-core/commands/feedback.md:30–31`). Same pair for `commit-artifacts`. `phase-handoff` entry points are always requested as `Skill(skill: "workflows-core:reference", args: "phase-handoff <entry>")`.

**Existing scripts that already do part of this:** SBP (all of SRG §8's plumbing and SRG §4 step 6's replay); `security-workflows/scripts/register.py` (only via `register_rebuild`, SRG §7); `scripts/bounded.py` (caps; SRG §4 step 6 cites `workflows-core:bounded-run` for the replay's fetch/push caps); `dev-workflows/scripts/run-state.py` already persists `specs_git`, `session_branch_lift`, `session_branch_created` for `/implement` (run-state.py:113–121) — the only precedent for persisting this run state outside the conversation.

### 0.1 Run state the five entry points share (who sets, who reads)

| State | Set by | Read by |
|---|---|---|
| `Environment:` line (printed text) | `specs-preflight`'s first act (SRG §3; command in SH §7 *The line*) | `env-check` step 1 finds "the last `Environment:` line this run printed" (SH §7) — before `handoff-to-main` (PH §2.1) and before each tail emitter's first write (SH §7 *Callers*). **Not** read by `commit-artifacts` itself. |
| `specs_git: blocked` | `specs-preflight` G0 (SRG §3.3); or `commit-artifacts` step 1 on a run that ran no preflight (SRG §4 step 1) | `commit-artifacts` step 1; `handoff-to-main` §2.1 gate + §4.3 flag line; `require-on-main` row I; `branch-check` gate (passes silently) |
| `specs_git: misrooted` | SRG §3.1 notices (non-repo with a `specs-root-check` signal; inside-tree; below top level); `workflows-core:addressing` §3 `specs-root-check` stop; SH §7 `env-check`; SH §6 *Stop* (SRG §3.1 "`specs_git: misrooted` is the run-wide record…") | everything above **plus** every tail emitter (cost, feedback, follow-ups, `resume.md` → report-only, SRG §3.1); `require-on-main` row C (no offer) and B′ remedy form; `branch-check` §6.1 forms and §6.2 skip; SRG §3.5 (classify, move nothing) |
| the notice that set `misrooted` (text) | its setter | `commit-artifacts` step 1 re-emits it verbatim; `handoff-to-main` §2.1 repeats it; §6 *Misrooted* row (SRG §4 step 1, §6) |
| which guard fired (G0/G1/G2) + its §5 block | `specs-preflight` §3.3 | `commit-artifacts` step 7 repeats the block verbatim (SRG §4 step 7, §5, §6 "When a guard fired at §3.3 G1 or G2…") |
| `<default>`, `<default-ref>` | `specs-preflight` §3.2 (also resolved by `commit-artifacts` step 5 on a run with no preflight) | `require-on-main` §3.2 ("resolved by `specs-repo-git.md` §3.2"); `branch-check` inputs (PH §6); `handoff-to-main` §2.2 cut/merge tests, §2.3 *Nothing to commit* tests; producers' per-run array test `cat-file -e "<default-ref>:./<path>"` (PH §4.1 *Row F is the next phase's reading only where…*); commands directly (e.g. `create-ard.md:831`) |
| offline clause `offline — ancestry checked against the last-fetched ref` | SRG §3.2 *Freshness* | `require-on-main` §3.6 reuses the words; `degraded` return |
| `session_branch: session/<identity>` | SRG §8.1 (`SBP mode`), at §3.2 — or at `commit-artifacts` step 1 on a run with no preflight | every move of the checkout wraps in `lift`/`put-back` (SRG §8.3 list); PH §2.2, §2.3 switch-back, row C repair; B′ and §6.1 remedy `lift` forms; C′ ignores session files |
| `mode: unsupported` | SBP `mode` | §6 line append (SRG §6 session-branch paragraph) |
| `session_branch_created: <base short sha>` | any §8.2 `commit` **other than** §3.4's flush's (SRG §8.2 last paragraph) | §6 line append |
| B4's switched-away branch name | SRG §3.5 B4 report | the same-run re-run's switch-back (SRG §3.5 *A re-run in the same run switches back first*) |
| "-D advisory printed for `<branch>`" | SRG §3.4 settle loop | the same loop on a re-run: "at most once per run for that branch, however many times the run's preflight runs" (SRG §3.4) |
| `remote: origin\|none` | PH §2.1 push-target probe, run **before** §4.3's array | §4.3 no-remote line; §2.5, §2.6 skip; §4.1 *No remote* row |
| branch created/reused by this run's own `handoff-to-main` | PH §2.2 | `require-on-main` row B ownership (PH §3.3 row B); a second handoff's rule-3 reuse (`/brd-reconcile`, PH §4.1); where `commit-artifacts` lands (SRG §4.1) |
| declined-handoff deliverable path(s) | producer, on §4.3 option 2/3 | `commit-artifacts` §6 append `; the deliverable at <path> remains uncommitted, as you asked` (SRG §6 last paragraph; SRG §4.1 bullet 3) |
| push-refusal record (persistent, `<git-common-dir>/workflows/push-refused/<branch>`, or key `branch.<b>.workflowsPushRefused`) | SRG §4 step 6 | SRG §4 step 5 condition; SRG §8.1 `mode` (record on default branch turns mode on); B2/§3.4 delete it (SRG §1 rule 8) |

### 0.2 The canonical run timeline (ordering summary)

1. Run-flag strip, question-rules load, argument parse (command-owned).
2. `specs-preflight` — once the run key set is known (SRG §3; §7 rule 1).
3. `branch-check` — after both preflight and `resolve-address`, whichever is second, and after the carrier-placement refusals; before anything reads or gates the folder's documents (PH §6 opening).
4. `require-on-main` — immediately after the preflight in most callers' Phase 0, always after it; before the first subagent dispatch, code scan, docs-grounding retrieval or grill question (PH §3 opening; PH §5 rule 2).
5. Work; deliverable written.
6. Handoff phase: `handoff-to-main` requested at the consent step → probe → (flag line | no-remote line) → §4.3 array → §2 on option 1 (PH §2 opening; EF).
7. Emitter tail, fixed order: feedback → follow-ups → cost → `resume.md` → `commit-artifacts` (SRG §4 opening; `.claude/rules/workflows-core-git.md` *canonical terminal order*). The deliverable-side finish may sit anywhere relative to the tail, including between members (same rules bullet; `/document` Phase 8.5 sits between feedback and follow-ups).
8. `commit-artifacts` is the **last action**, "before or as the run's last printed output" (SRG §4); after the report nothing restates it (SRG §4 step 7).

---

## 1. `specs-preflight` (SRG §3)

### 1.1 Caller inputs

| Input | Defined | Notes |
|---|---|---|
| **run key set** | SRG §3.2 *Run key set* | Every key already resolved at the call site. PRD-scoped → PRD key. Epic-scoped (single address resolved an `EPIC-` folder) → **both** Epic key and PRD key (ancestry carries it; SRG §3.2, §3.6). None resolved → empty set = **keyless**. Never deferred to obtain a key a later phase would mint. `/create-prd` is always keyed (both routes; SRG §3.2 *`/create-prd` contributes a key*). Set is the preflight's only; `commit-artifacts` resolves its own single key later (SRG §3.2 last paragraph). |
| how the set is built (which order) | SRG §3 first paragraph | Two cases — see V1.1. Keys from resolution (resolved key + Epic's parent key) or from `addressing` §1 `read-key` on arguments / the carrier an `@<path>` names (`/vuln` per-token keys; keyless where no token carries one). |
| `register_rebuild: <abs path>` (optional) | SRG §7 *One optional input* | Passed to §4 step 6's replay wherever §3.4 reaches one, as `--register-rebuild <path>`. Only `/security-workflows:scan` passes it (`security-workflows/commands/scan.md:93`), value `${CLAUDE_PLUGIN_ROOT}/scripts/register.py`. |
| `$SPECS_PATH` (env, or the value from the *Set SPECS_PATH* answer exported first) | SRG §3.1; SH §7 *The line* | Unset is a supported input for some callers (V1.4). |
| `$REPOS_PATH` | SH §7 *The line* | Only printed in the `Environment:` line. |
| implicit: is this a re-run in the same run with a changed key set? which branch did the earlier B4 leave? | SRG §3.5 *A re-run…* | `/document`, `/release-notes` only. |
| implicit: command name? | — | Not an input of the preflight; but §3.4's flush commits with §4 step 4's message `<KEY\|NOISSUE> Add dev-workflows session artifacts (<command>)`, so the flush needs a key and the command name too **[design note: SRG never says which key the flush's commit uses; §4 step 4 says "when the run resolved no key"]**. |

### 1.2 Outputs and flags the caller carries

- `specs_git: blocked` (G0) / `specs_git: misrooted` (§3.1) — carried for the whole run (SRG §7 rule 1). Readers: §0.1.
- `<default>`, `<default-ref>` and the offline clause (SRG §3.2) — reused by `require-on-main` ("no second network call", PH §3 opening), `branch-check`, `handoff-to-main`.
- `session_branch` when SBP `mode` prints `on` (SRG §8.1); `mode: unsupported` (§6 append).
- The guard block that fired (G0/G1/G2), for `commit-artifacts` to repeat (SRG §5 "repeats the notice in full").
- Printed output (see 1.5). No return object is defined beyond the flags; SRG §1 rule 7 "prints its `Environment:` line … otherwise silent unless it acts, a guard fires, or §3.1 reports".
- Side effects: possibly a commit + push (§3.4 flush/retry), branch switch/pull/delete (§3.5), branches pushed/deleted in the settle loop, replays (SRG §4 step 6), session-branch creation (§8.2), push-refusal records written/removed.

### 1.3 Ordering obligations

- **When:** at run start, once the key set is known — Phase 0 in most commands, Step 0 in `/vuln`, the shared `## Mode detection` section in `/document` (`CLAUDE.md` Hard constraints; SRG §3; SRG §7 rule 1).
- **Resolve-first commands** (key set = what resolution returns) resolve first and run the preflight **before any placement or refusal reads the resolved folder** (SRG §3). Example: `create-ard.md:270` "before step 1 places the folder and before step 1a or any later step reads it".
- **Preflight-first commands** (no address; or keys from `read-key`/`@<path>` carrier) run it as soon as `$SPECS_PATH` is known, and resolve afterwards — having first read the carrier of each key typed as a whole folder name and of each `@<path>` folder (SRG §3).
- Its **first act** is the `Environment:` line, printed on every run that reaches it, whatever the gate finds (SRG §3; SH §7). It requests `Skill(skill: "workflows-core:reference", args: "session-hygiene env-check")` for that line.
- Must precede `require-on-main` (which reuses its fetch) and `branch-check` (PH §3, §6).
- Under SBP mode, the preflight **ends with `put-back`** whether or not it moved, and where a guard ended it — never under `misrooted` (SRG §8.3 last paragraph).
- `/brd-proposal`/`/prd-proposal` place it before their own refusals because "`require-on-main` performs no fetch of its own" (`brd-proposal.md:96–97`, `prd-proposal.md:105–106`).

### 1.4 Variation points (reference-defined)

- **V1.1 Order: resolve-first vs preflight-first** (SRG §3 ¶1). What a `specs-root-check` stop prints depends on it: resolve-first → only the stop, no preflight; preflight-first (`/idea`, `/vuln` on a key token) → inside-tree notice, then the stop (SRG §3.1 *What a run that stops on `specs-root-check` prints*).
- **V1.2 Runs none:** a resolve-first run that stops on its address (`invalid`, `ambiguous`, `misrooted`, `absent`); any run that stops before the preflight on a check of its own inputs needing no specs-repo state (a run flag, the cwd, a path read where it sits) (SRG §3 ¶1; §7 rule 1).
- **V1.3 Keyless vs keyed; Epic contributes two keys** (SRG §3.2). Keyless commands named: `/harvest-decisions`, `/promote-decisions` (`.claude/rules/product-workflows.md` map: "specs-preflight (keyless)"); `/security-workflows:scan` "empty for a path" (`scan.md:93`). Neither route may be classified keyless (SRG §3.2 *Neither route…*): an empty set sends the run's own branch to B4 and makes PH §2.2 rule 4 append `-2`.
- **V1.4 `$SPECS_PATH` unset — three caller classes** (SRG §3.1 first bullet): (a) commands that resolve/create their deliverable folder by key stop in Phase 0 on `escalation-rules` *Required path environment variable unset* and never reach the gate unset (`grep -lE 'Set SPECS_PATH|Required path environment variable unset' plugins/*/commands/*.md`; `/implement`, keyed `/document`, `/release-notes` for a `<KEY>` address only); (b) `/implement`, keyed `/document`, `/release-notes` on an `@<path>` address run on, writing into the folder given; (c) bookkeeping-only commands (`/document` direct, `/implement` direct prompt, `/upgrade`, `/vuln` on key/no address, `/docs-init`, `/docs-brand`, `/docs-audit`, the four logging commands, `/diagnose-session`) run on with emitters report-only.
- **V1.5 Gate dispositions** (SRG §3.1): unset → silent no-op; `.git` not writable (read-only mount) → silent no-op (no fetch either, since §3.2 is past the gate); not a dir / `rev-parse` fails → one-line notice (+ signal + left-behind line where `specs-root-check` finds a signal, which also sets `misrooted`); passing gate → run `addressing` §3 `specs-root-check` tests → notice + `misrooted`; else `rev-parse --show-prefix` non-empty → below-top-level notice + `misrooted` (skipped where the inside-tree notice fired).
- **V1.6 Under `misrooted`**: no write at all — no flush, no push retry, no switch/create/delete/pull/commit/push; §3.2 (fetch included) runs; §3.3 and §3.4 skipped; §3.5 classifies and prints a stay line instead of B2/B4 (SRG §3.1 *The preflight itself performs no write*; §3.3 ¶1; §3.4 ¶1; §3.5 *Under `specs_git: misrooted`*).
- **V1.7 Guards end the preflight** (G0 → `blocked`; G1, G2 advisory, no flag) (SRG §3.3 table). G2 has three notice variants: plain; session-branch mode (two sub-variants: other branch / the session branch itself); direct `/implement` from inside the specs repository (SRG §5).
- **V1.8 Session-branch mode** (SRG §8): §3.2 runs `SBP mode --default <default>` (never under `misrooted`), a second fetch of the session branch; flush commits via `SBP commit` (+`--include-ahead` on default), prints created lines; B2/B4/re-run/catch-up wrapped in `lift`/`put-back`; ends with `put-back`; no replay (rejection is §8.4's). No identity → commits nothing in the mode, moves run unwrapped (SRG §8.1 *No identity*).
- **V1.9 Re-run in the same run with a changed key set** — `/document`, `/release-notes` after the operator enters a slice key at their BRD-container stop: switch back to the branch the earlier B4 left if `branch-key` now resolves it, then stages 1–3 again; "No other re-run switches anything" (SRG §3.5; `document.md:1559`; `release-notes.md:902`).
- **V1.10 `register_rebuild`** — `/security-workflows:scan` only (SRG §7).
- **V1.11 Proposals run it twice in text?** No: the "2" grep hits in `prd-proposal.md`/`brd-proposal.md` are one step spanning two lines (`:105–106`, `:96–97`).
- **V1.12 Nested/inline invocation runs none**: `/docs-brand --inline` runs no preflight or `commit-artifacts` ("standalone only", `docs-brand.md:45`, `:394`); its caller `/docs-init` owns them.
- **V1.13 Direct `/implement` from inside the specs repository**: G2's notice variant; the run's own branch moves wrapped by §8.3 (its Phase 1.4, Pre-Phase 3, Phase 4.6) (SRG §5 last paragraph; §8.3 *The moves*; `implement.md:391`, `:1256`).

### 1.5 Interactive points

**None — prompt-free** (SRG §1 rule 7). Everything is a notice a script can print:

- `Environment: SPECS_PATH=<realpath> (origin <url|none>), REPOS_PATH=<value|unset>` (SH §7 Bash block).
- §3.1: non-repository notice (one line; + signal clause; + left-behind line); inside-tree notice (= `specs-root-check`'s stop text; + left-behind line); below-top-level notice (names value + `--show-toplevel`).
- §3.2: `offline — ancestry checked against the last-fetched ref`.
- §5 blocks: G0 (blocking), G1 (advisory, path list), G2 (advisory, 4 variants).
- §3.4: catch-up failure → git's first error line; `Specs preflight: <branch> is merged, and this flush committed <sha7> on it, which no run pushes; to land it, standing on <default>, run git -C "<SPECS_PATH>" cherry-pick <sha7>`; flush/retry push results in `Specs preflight:` form (§6 rows re-prefixed — SRG §6 *Inside §3.4's flush and retry*); push-refused form `Specs preflight: <branch> not pushed — origin refused it (…)…` (SRG §4 step 6 bullet 1); session-branch `Specs preflight: created local session/<identity> at <sha>…` (2 forms); settle loop: `Specs preflight: deleted merged <branch>`, `Specs preflight: <branch> is merged into <default>, which git branch -d cannot see from here — delete it with … branch -D <branch>` (+ `rm -f "<record>"`), `Specs preflight: pushed <N> session-file commit(s) left on <branch>`, git's own `-d` failure message.
- §3.5: B2 `-d` failure; config-leftover line; rebase/squash `branch -D` line (+ `rm -f`); pull failure report. **B4 report has no fixed template** ("Report the branch name, and … how many" unpushed). Misrooted stay line (2 variants). Re-run switch-back failure ("reported with the branch name").
- SBP exit 2 → first stderr line (SRG §8 opening).

A question **adjacent** to it but owned by the command, not the preflight: the *Set SPECS_PATH* question (`escalation-rules` *Required path environment variable unset*), asked before the preflight; its answer is exported for the `Environment:` line (SH §7).

### 1.6 Mechanics vs judgment

| Part | Class | Cite |
|---|---|---|
| `Environment:` line, §3.1 gate and its three dispositions, `specs-root-check` tests, show-prefix test | mechanical | SRG §3.1; `addressing` §3 `specs-root-check` (filesystem/git tests, "none by parsing a name") |
| default branch / `<default-ref>` / fetch / mode | mechanical | SRG §3.2, §8.1 |
| guards G0–G2, ARTIFACT/OTHER classifier | mechanical (regexes duplicated in SBP lines 59–70, selftest-pinned) | SRG §2.1, §3.3 |
| flush, catch-up, retry, settle loop, `push-scope`, replay | mechanical (replay already scripted) | SRG §3.4, §4 steps 2–6 |
| `branch-merged` (4 tests), `branch-key` (resolution against a given set) | mechanical | SRG §3.5 |
| **building the run key set** | caller judgment/logic (which keys resolution returned; Epic parent) — deterministic given the command's resolution result, not derivable by the script | SRG §3.2 |
| **choosing resolve-first vs preflight-first, and whether a stop precedes it** | command-author judgment, fixed per command | SRG §3 |
| B4 report wording | free wording (no template) | SRG §3.5 B4 |
| "once per run" memory, re-run switch-back memory, guard-block repetition at the end | needs persistent run state (the conversation today) | SRG §3.4, §3.5, §5 |

---

## 2. `commit-artifacts` (SRG §4)

### 2.1 Caller inputs

| Input | Defined | Notes |
|---|---|---|
| `<KEY>` (single) or none → `NOISSUE` | SRG §4 step 4; §3.2 last ¶ ("a single key, at the end of the run") | **Which** key on a two-key (Epic) run is not fixed by SRG; commands state it (e.g. `create-ard.md` "The commit message's key is the run's key, resolved as Phase 8 resolves it"). A run keyless at the preflight may have one now. |
| `<command>` (e.g. `/create-ard`) | SRG §4 step 4 message | `<KEY> Add dev-workflows session artifacts (<command>)` |
| carried flags `specs_git: blocked|misrooted` + the notice that set `misrooted` | SRG §4 step 1; §7 rule 1 | |
| which guard fired at the preflight + its §5 block | SRG §4 step 7, §6 | G1/G2 blocks repeated after the line; G0 is the *Blocked* row + block |
| `session_branch`, `mode`, `session_branch_created` | SRG §8.1, §8.2, §6 | |
| `register_rebuild` (optional) | SRG §7 | `/security-workflows:scan` only |
| declined-handoff deliverable path(s) | SRG §4.1 bullet 3; §6 last ¶ | append `; the deliverable at <path> remains uncommitted, as you asked` |
| whether the preflight ran | SRG §4 step 1 | a run with no preflight tests G0's state and resolves SBP mode here |
| placement: in the final report, or own terminal block, or after a stop's message | SRG §6 ¶1; §7 rule 3 | caller-owned |

### 2.2 Outputs

- Exactly **one** `Specs repo:` line per run (SRG §6; §7 rule 3), plus: the §5 block where a guard fired (G0 *Blocked* row; G1/G2 after the line); the misrooted row + the notice that set the flag verbatim; appends — hook variant `Specs repo: <path>[, …] is now committed in <sha7>, put there by a pre-commit hook, and not pushed`; register clause; `upstream_error`; session-branch appends (`created`, `sync.conflict` ×2 sources, `sync.error`, `unsettled`, `stranded`, `unsupported`); declined-deliverable append.
- §6 row catalogue (case names; texts in SRG §6 table): pushed on plugin branch; pushed straight to default; pushed on session branch; no identity; script could not run; not pushed — not a branch this plugin pushes / no origin / pushRemote elsewhere / remote deleted branch (+ default-branch `remote set-head` tail) / origin lacks this plugin branch / refused before; push REFUSED by origin; not pushed — push-scope (+ hook variant); replay: replayed and pushed / already there / moved, not pushed (+ refused form); push REJECTED non-ff nothing moved (12 reason clauses + 3 step-6 clauses; `checked-out` and `checkout-moved` remedy variants; session-branch `lift`/`put-back` wrapper); push FAILED; nothing to commit; locked; commit failed; blocked (G0); misrooted; gate failed on environment → **no line at all**.
- Persistent: push-refusal record write (SRG §4 step 6).
- HEAD unchanged except by replay's locked move (SRG §1 rule 4).

### 2.3 Ordering obligations

- **Last action of the run**, after `resume.md` (where written) and after the cost phase (SRG §4 ¶1; §7 rule 2), as the last member of the tail feedback → follow-ups → cost → `resume.md` → `commit-artifacts`.
- **Before or as the run's last printed output** (SRG §4 ¶1). Step 7: from the report to the end, print only what the command's own steps after the report say (maintenance, feedback, follow-up, cost lines, a question one of those asks, a context-hygiene line, this line + §5 block + appends, a line the command names after it) — never a recap, never the report's own `Code repo:`/`Phase handoff:` lines again (SRG §4 step 7).
- **After the handoff**: the session commit lands on the branch the handoff cut, "so the push updates the pull request already open" (SRG §4.1 bullet 2); a plugin branch `origin` lacks is never pushed by this step (SRG §4 step 5, "only `phase-handoff.md` §2.5 publishes one").
- Step 5's push is a **separate command** after the commit's exit status is read; never chained, never after `rc=$?`, `|| true`, `;` (SRG §4 step 5).
- The replay (step 6) runs "in a Bash call of its own with a timeout of 420000 ms" (SRG §4 step 6).
- On a run that ended early, the line prints **after the stop's own message** (e.g. `create-ard.md:33`, `:951`).
- SH §6 point 3 (`/design`, `/specify` only) runs before the tail's first write, hence before `commit-artifacts`, "unless an earlier comparison this run ended in *Stop*" (SH §6 *Compare*).
- `env-check` is **not** run by `commit-artifacts`; it runs first in each tail emitter (SH §7 *Callers*), which precede it.

### 2.4 Variation points

- **V2.1 Cede-control exception**: runs immediately **before** a phase that hands the session to another skill or opens an open-ended interactive stretch, and prints its §6 line there; never split across invocations. Named: `/prompt-brainstorm` (before Phase 3 → `superpowers:brainstorming`, `prompt-brainstorm.md:102`), `/prompt-grill-me` (before Phase 3 grill, `prompt-grill-me.md:95`), `/brd-split`'s *Ground now* (`brd-split.md:1687`) (SRG §4 *The one exception*).
- **V2.2 Refusal tail** (Phase 0 refusal before the run has a deliverable, a branch or a handoff): feedback writes nothing; follow-ups no-op; cost written (unless `--skip-costs` → `skip-cost`; unless `misrooted` → report-only; unless no transcript holds the invocation); **no `resume.md`**; `commit-artifacts` runs (SRG §4 *A run that refuses…*). Each command states this in an **Ending early.** paragraph (SRG §7 rule 2). Not keyed on whether the run wrote under `$SPECS_PATH` (SRG §4 *Nothing here is keyed…*).
- **V2.3 Stop taken after the run cut a branch** is outside the refusal tail; its tail is the command's to state — `/document` keyed mode, whose Phase 0 cut a docs-repository branch and committed the profile before later Phase 0 stops (SRG §4 ¶ after the bullets).
- **V2.4 No tail at all**: `/prd-ground`'s `PRD_GROUND_TYPED_ONLY` (no run; `prd-ground.md:39`, `:53`); and a command may state that a refusal before it resolved its target takes no tail where its cost entry is filed per target — `/docs-init`, `/docs-audit`, standalone `/docs-brand` (stops before a docs repo is resolved; also `strip-run-flags`' own stops, `docs-brand.md:21`), `/document` direct-mode stop before its write target is resolved (SRG §4, lines 687–694).
- **V2.5 Stop before the preflight**: the tail runs, skipping only the preflight (SRG §7 rule 2); `commit-artifacts` step 1 then tests detached HEAD itself (blocked outcome only where something would stage) and resolves SBP mode (SRG §4 step 1).
- **V2.6 Gate outcomes**: flags tested first and win over an environment failure; `blocked` → re-emit G0; `misrooted` → re-emit the setter's notice; neither + env failure → silent (SRG §4 step 1).
- **V2.7 Where the commit lands** (SRG §4.1): session branch (mode); the handoff branch (every `handoff-to-main` producer, incl. `/promote-decisions` via `architecture-promotion` §11.2), or the branch returned to / cut branch on *Nothing to commit* variants, unpushed where `origin` lacks it; default branch with deliverable uncommitted when the user declined; otherwise default, or G2's branch, or B3's branch; direct `/implement` from inside the specs repository → the code branch it cut (pushed only if it carries a plugin prefix) or HEAD's branch if it stopped first.
- **V2.8 Push targets**: default branch, plugin branch, session branch; never G2's branch; never against `pushRemote`/`pushDefault`; never recreate a remote-deleted branch (session branch excepted, §8.4); never publish a plugin branch `origin` lacks; never past a refusal record; `push-scope` must hold (SRG §4 step 5, §8.4).
- **V2.9 Non-fast-forward** → replay (outside mode) via `SBP replay [--register-rebuild] [--set-upstream]`; JSON → one of four §6 rows (SRG §4 step 6). In mode: nothing replayed.
- **V2.10 `--skip-costs`**: no cost entry; the step's gates settle as for any run with nothing new (SRG §4 *This step runs*).
- **V2.11 Two calls in text** in `/document` (one per mode: Mode A/Mode B, `document.md:2026` etc.) — still one per run.
- **V2.12 Nested inline run** (`/docs-brand --inline`) runs none (`docs-brand.md:394`).
- **V2.13 `/security-workflows:scan` post-line handling**: register clause / settle line after the outcome line (`scan.md:585–589`) — command-specific prose that reads the line.

### 2.5 Interactive points

None (SRG §1 rule 7). All outputs are notices: the §6 line + blocks + appends (2.2). No question is asked even on refusal, conflict or non-ff.

### 2.6 Mechanics vs judgment

| Part | Class | Cite |
|---|---|---|
| gate, enumerate/classify/stage, pathspec commit, index restore, push conditions, `push-scope`, push, porcelain parsing, refusal record, replay, §6 line selection and rendering | mechanical | SRG §4 steps 1–7, §6 |
| key choice on a two-key run; `<command>` | caller-supplied | SRG §4 step 4 |
| where the line sits in the report; "nothing after the report restates it" | orchestrator discipline (not scriptable; a script can only print) | SRG §4 step 7, §6 ¶1 |
| whether a stop takes the tail (refusal tail / no tail / command-stated tail) | command-author classification, fixed per stop | SRG §4, §7 rule 2 |

---

## 3. `handoff-to-main` (PH §2; consent PH §4.3; outcome PH §4.1)

### 3.1 Caller inputs

| Input | Defined | Notes |
|---|---|---|
| `prefix` | PH §2.9 | `idea`, `prd` (`/create-prd`, `/update-prd`, `/prd-proposal`, `/release-notes`, idea-route `/prd-ground`), `ard`, `spec`, `epics`, `design` (`spec`/`design` also `/implement`'s conformance handoff), `ready`, `brd` (every `/brd-*`, BRD-route `/prd-ground`), `frames`, `kb` (`/harvest-decisions`, `/promote-decisions`), `conformance` |
| `feature_folder` | PH §2.9 | resolved folder the deliverable was written into; **none for `kb`**. Branch `<prefix>/<KEY>-<slug>` is taken from its basename, never re-derived (PH §2.2). Callers may name the PRD folder above an Epic (e.g. `/release-notes`, PH §6 *Inputs*). |
| `deliverable_paths` | PH §2.9, §2.3 | literal repo-relative files, never a directory or glob; enumerate every vendored/copied file; proposals declare `.dev-workflows/proposal-profile.yml` every run |
| `title` | PH §2.9, §2.7 | commit subject **and** PR title; in practice includes the key (`create-ard.md`: `title: <PRD|EPIC> Add architecture requirements document`); §2.4 message is `<KEY> <summary>` |
| `body_facts` | PH §2.9, §2.7 | what the phase produced; artifact paths; reviewer verdict where any; open-question / `[NEEDS CLARIFICATION]` count; **where the caller has one**, the next command + not-until-merged sentence (per artifact for mixed sets, by the `<default-ref>` test — `/epics`) |
| `inputs_read` | PH §2.9 | every non-session file under `$SPECS_PATH` this run or its agents read; "derived by the run from its own reads … recorded as it reads"; feeds §2.2's stack test |
| the **class** and, if gated, the **half** → selects the array and both clauses | PH §4.0, §4.1, §4.3 | strongest class in the set; per-run test where a falling-back artifact is already on `<default-ref>` |
| the consent answer (or an earlier answer carried) | PH §4.3; EF | |
| run key set | PH §2.2 rule 3 (via SRG §3.5 `branch-key`) | |
| `<default-ref>`, flags, `session_branch` | SRG §3.2, §3.1, §8 | |
| session model's name | PH §2.4 | `Co-Authored-By: <the session model's name> <noreply@anthropic.com>` |
| scratchpad dir (`TMPDIR`) | PH §2.4; `run-flags` §7 | message file via `command mktemp -t dw-handoff-msg-XXXXXX` |
| which handoff (label) | PH §4.1 *One producer offers two handoffs* | `/brd-reconcile` only |

### 3.2 Outputs

- **`Phase handoff:` line** — exactly one per offer (PH §4.1); rows: PR opened; PR already existed; PR not opened (+ §4.2 fallback text); push failed; push refused for access; no remote; nothing to commit (4 branch variants × 4 location variants); commit failed; declined by the user (`<artifacts>` = all declared paths ≤3, else `<n> files under <dir>`); gate failed (`specs_git: misrooted (<first line>)` form); switch refused. Appends: branch name substituted; stacked on another phase's branch; declaration unaccounted for; record unreadable.
- Indented list of every committed path (≤8 then `…and <n> more`) under each row that committed (PH §4.1 *Every committed path is named*).
- `<downstream-clause>` (success rows) and `<next-phase-clause>` (declined row), both from the class (PH §4.1).
- HEAD now on the deliverable branch (or back where it was on *Nothing to commit* removal) — `commit-artifacts` then lands there (SRG §4.1).
- `remote` value (probe), carried to §2.5/§2.6 (PH §2.1).
- Readers later in the run: the Final report ("Emit its §4.1 outcome line in the Final report", e.g. `create-ard.md:768`); `workflows-core:next-phase-offer`'s `<merge-clause>` resolution table reads it (next-phase-offer.md:110; `create-ard.md:892`); `require-on-main` row B ownership in the same run; `commit-artifacts` declined append.

### 3.3 Ordering obligations

- Requested **at the consent step**: `Skill(… args: "phase-handoff handoff-to-main")` loads PH-h2m, which holds §4.3; present §4.3's choice from that file first; §2 runs only on option 1 (PH §2 ¶1; EF). A request after the answer (the step following the choice, or a later phase carrying it — `/brd-package` Phase 9) does not ask again (EF).
- **Before the array**, in order: (1) read flags → flag line; (2) else §2.1 push-target probe → no-remote line; (3) present array verbatim (PH §4.3 *Selecting an array is not the whole…*, *Before anything else*, *Before presenting the array*). The probe runs where `rev-parse --git-dir` succeeds; else print nothing.
- §2.1: `env-check` **first**, then the gate (PH §2.1).
- §2.2 *Where a new branch is cut*: note HEAD's branch first (for §2.3's switch back).
- §2.4 commit's exit status read before §2.5's push, a separate command (PH §2.5).
- SH §6 point 2 (`/design`, `/specify`): before the deliverable write that leads to the handoff.
- Deliverable written (and stamped — lineage etc., command-specific) before staging.
- Before the emitter tail; options 2/3 do not stop the tail (PH §4.3 *What each option means*).
- A re-asked choice voids the earlier answer's line (PH §4.1 *A consent choice asked again*).
- `branch-check` §6.2 (earlier in the run) is where reuse of an open branch is asked, to avoid §2.2 rule 3's *Switch refused* at handoff time.

### 3.4 Variation points

- **V3.1 Four arrays** (PH §4.3), one per `<next-phase-clause>` (PH §4.1 bullets): *gated — stopping*, *gated — falling back*, *advisory*, *unread*. Only option 2's parenthetical differs. Class by naming the reader, never by the absence of a §3.4 row (PH §4.0 *Classify by naming the reader*); register of artifacts in PH §4.0 (whole reference only — not in PH-h2m beyond the class table and two rules). Set spanning classes → strongest (PH §4.0); set spanning both gated halves → stopping (PH §4.1).
- **V3.2 Per-run array selection**: a declined edit of a copy `<default-ref>` already carries meets C rows → stopping, tested before the offer with `cat-file -e "<default-ref>:./<path>"`: `/idea` refine, `/create-ard` refine, `/implement` Phase 4.5 annotating a merged `design.md`, `/epics` re-drafting a merged Epic; varying sets: `/create-ard`, `/implement` 4.5 (PH §4.1 *Row F is…*, *A producer whose set varies…*; `create-ard.md:768`).
- **V3.3 Quoted vs cited array**: quoting sanctioned (only exemption to never-restate); a command that **cites** must name the class and, if gated, the half (PH §4.3 ¶1; PH §5 rule 4).
- **V3.4 Flag line vs no-remote line** above the array (PH §4.3). `remote: none` → commit only, no push/PR, *No remote* row (PH §2.1, §2.5).
- **V3.5 Gate refusal** on `blocked`/`misrooted`/environment → *Gate failed* row, never silent (PH §2.1).
- **V3.6 Keyless `kb` form**: `kb/harvest-<YYYY-MM-DD>`, `kb/promote-<YYYY-MM-DD>`; no `feature_folder`; rule 3 never matches (callers stop first on any unmerged `kb/`) (PH §2.2). `/promote-decisions` reaches it via `architecture-promotion` §11.2 (`promote-decisions.md:86`), so `grep 'phase-handoff handoff-to-main'` misses it.
- **V3.7 Branch resolution** (PH §2.2): rule 2 new; rule 3 reuse own unmerged branch (switch, or `switch --no-track -c <name> origin/<name>`), refused switch → *Switch refused*; rule 4 suffix `-2…` + substitution append; remote-only ref confirmed with `ls-remote --exit-code`.
- **V3.8 Cut point**: at HEAD (default branch or G2 branch); at `<default-ref>` with `--no-track` where HEAD is another plugin branch — unless that branch changed a declared path or an `inputs_read` file (`diff --quiet <default-ref>...HEAD`) → stacked at HEAD + *Stacked* append; refused switch → stacked at HEAD + append (PH §2.2).
- **V3.9 Nothing staged**: created branch → switch back + `branch -d` (or kept, named); reused branch → re-publish where it carries a non-session commit missing from `<default-ref>` and `origin` (PH §2.3).
- **V3.10 Declared paths unaccounted / unreadable records** → appends, not a stop (PH §2.3 step 4).
- **V3.11 Repository PR template** fills the body (PH §2.7.1).
- **V3.12 Skipped offer** → no line: `/frames` with no index, `/idea` on `status: draft`, `/implement` Phase 4.5 no-op, `/brd-proposal` readiness walk ending early; a run that stops before its handoff (PH §4.1 *A run that never reaches an offer*).
- **V3.13 Two handoffs, two choices, two lines** — `/brd-reconcile` (second reuses the first's branch by rule 3); the first answer never stands for the second (PH §4.1; EF).
- **V3.14 Session-branch mode**: switch onto `<name>` and the switch back wrapped in `lift`/`put-back`; a `lift` that skips refuses the handoff (PH §2.2, §2.3).
- **V3.15 Non-ff push is reported, never replayed** (PH §1 rule 4; §2.5). Read-only `.git/config` costs `-u` only (PH §2.5).
- **V3.16 Non-producers in the specs repo**: `/document` (hands off in the docs repo via `finish-and-handoff`), `/vuln`, `/security-workflows:scan`, `/upgrade`, docs commands, logging commands — no `handoff-to-main` (PH §6.1 "any branch under a run that hands nothing off in the specs repository"; `vuln.md:49`, `scan.md:99`, `document.md:71`).

### 3.5 Interactive points

| Point | Kind | Cite |
|---|---|---|
| flag line (`This run carries specs_git: … so the first option will be refused…`) | notice (printable) | PH §4.3 |
| no-remote line (`This specs repo has no \`origin\` remote: …`) | notice | PH §4.3 |
| **§4.3 consent choice** (3 options, one of four arrays) | **needs the user's answer**; presented verbatim; free text normalised or re-asked (`escalation-rules` *Choice lists are presented verbatim*; `CLAUDE.md` Hard constraints) | PH §4.3 |
| re-asked choice (interrupt) | answer supersedes | PH §4.1 |
| everything in §2 after option 1 | prompt-free (no question even on refusal, access denial, `gh` failure — "the run asks nothing and tries no other credentials") | PH §2.5, §2.6 |
| §4.1 line, path list, §4.2 fallback text | notices | PH §4.1, §4.2 |

Every command presenting the choice must have loaded `escalation-rules core` in a **Load the question rules.** step before its first question (`CLAUDE.md`; gated by `scripts/reference-parts.py check-questions`).

### 3.6 Mechanics vs judgment

| Part | Class | Cite |
|---|---|---|
| probe, flag/no-remote line choice, gate, `env-check` | mechanical | PH §2.1, §4.3; SH §7 |
| branch name from folder basename, collision rules, merged test, cut-point test (given `deliverable_paths` + `inputs_read`) | mechanical | PH §2.2 |
| staging, accounting, pathspec commit + restore, push, porcelain/access parsing | mechanical | PH §2.3–§2.5 |
| `owner-repo` (incl. `ssh -G`), `gh pr list`, `gh auth status`, `gh pr create` | mechanical | PH §2.6, §2.6.1 |
| §4.1 row + appends + clause rendering given the class | mechanical | PH §4.1 |
| **class/half selection** (naming the reader; the §4.0 register) | **judgment** (per-run `cat-file -e` part is mechanical) | PH §4.0 "held by review … naming a guard or the reader … is reading, and no script does it" |
| `title`, `body_facts` (verdict, counts, next command) | caller judgment/content | PH §2.7, §2.9 |
| **filling a PR template** ("answer each section", "tick a checkbox only where the run can show what it claims") | **judgment** (LLM) | PH §2.7.1 |
| `inputs_read` | caller record-keeping only the run can do | PH §2.9 |
| presenting the choice | harness `AskUserQuestion` — not scriptable | PH §4.3 |
| Co-Authored-By model name | caller-supplied | PH §2.4 |

---

## 4. `require-on-main` (PH §3)

### 4.1 Caller inputs

| Input | Defined |
|---|---|
| `path` of the artifact, relative to `$SPECS_PATH`; one call per gated artifact (callers gate several: `/create-ard` PRD, slice `decisions.md`, `epic.md`; `/brd-package` up to three classes) | PH §3.2 |
| `default` branch / `<default-ref>` (from the preflight's §3.2) | PH §3.2 |
| the caller's own branch prefixes | PH §3.2 (row B ownership) |
| the run key set | PH §3.2 |
| implicit: flags (`blocked` → row I; `misrooted` → row C stop, B′ form), `session_branch` (B′ `lift` form, C′ excludes session files, C repair wrapped), read-only mount (§3.6), "branch this run created or reused" (row B) | PH §3.3, §3.6 |

### 4.2 Outputs

`{on_main: pass|pass_amending|absent|unmanaged, stopped, branch, pr, degraded}` (PH §3.7). `on_main` defined only when `stopped: false`; **test `stopped` before `on_main`** (PH §3.7). Rows → H `unmanaged` (silent), A `pass`, B `pass_amending` (+ printed `reading <path> from your in-progress <branch>, which amends the approved version on <default>`), F `absent` (caller applies its §3.4 row), I/G/B′/C′/C″/C/D/E stop (worded by §4.4's four parts; B′ by *Row B′'s remedy*, 4 forms). Later readers: the command's own `absent` branch and stop handling; the final report (e.g. `create-ard.md:961` reports "the PRD gate's return value").

### 4.3 Ordering obligations

- After `specs-preflight`, reusing its fetch — no second network call (PH §3 opening); in most callers' Phase 0 immediately after it.
- Before the first subagent dispatch, code scan, docs-grounding retrieval or grill question (PH §5 rule 2). A departure is stated in the command.
- After `branch-check` ("before anything reads or gates the folder's documents", PH §6).

### 4.4 Variation points

- **V4.1 Later call sites** (PH §5 rule 2): `/ready` Phase 1; `/epics` Phase 2.6 (and `/epics` runs `resolve-docs-grounding` first — "a deliberate exception to §5 rule 2's ordering", `.claude/rules/product-workflows.md` map); `/specify` against an Epic its Step A picks; `/brd-proposal` Phase 4.
- **V4.2 Reading a stop without stopping** (PH §3.7): `/ready` (records as finding, caps `PARTIAL`); `/brd-reconcile` at three sites (cross-BRD write guard; `--sent` redundancy check where a pass stops; ordinary Phase 0 gate walking older prompts); `/brd-interview` Phase 0 step 8a. No other caller.
- **V4.3 `absent` mapping per caller** (PH §3.4 table): fall back (`/create-prd` idea ladder, `/create-ard`/`/specify`/`/update-spec` read folder reported, ARD `status: none`, `/epics` silent skip, `/implement` in-scope only, `/ready` coverage gap, `/conformance` traces what exists) vs stop (`/design`, `/update-spec` base, `/prd-ground`, `/brd-split`, `/brd-interview`, `/brd-package`, `/brd-reconcile`, `/prd-proposal`, `/brd-proposal`) and row-F splits on worktree tests the gate cannot make.
- **V4.4 Read-only mount**: no fetch, degraded clause; row C stops instead of offering; B′ read-only form (PH §3.6, §3.3).
- **V4.5 `misrooted`**: fetch still ran; row C stops naming files and flag; B′ misrooted form (PH §3.3).
- **V4.6 Session-branch mode**: C′ ignores session files; C repair wrapped; B′ `lift` form (PH §3.3).
- **V4.7 `gh` failure / non-`gh` remote** on D/E → row E wording + "could not be checked" note; probe skipped where `owner-repo` slug fails validation (PH §3.5).
- **V4.8 Callers**: 16 — `/create-prd`, `/create-ard`, `/specify`, `/update-spec`, `/design`, `/implement`, `/epics`, `/ready`, `/prd-ground`, `/brd-split`, `/brd-interview`, `/brd-package`, `/brd-reconcile`, `/prd-proposal`, `/brd-proposal`, `/conformance`; `/update-prd` and `/brd-intake` deliberately not (`.claude/rules/workflows-core-git.md`).

### 4.5 Interactive points

| Point | Kind | Cite |
|---|---|---|
| **Row C repair offer** `choices: ["Switch to <default> and pull --ff-only, then continue (Recommended)", "Cancel"]`; on option 1 switch + `pull --ff-only` (wrapped in mode), re-test **once**, second failure stops | **needs answer** | PH §3.3 *Row C's repair offer* |
| all stops (I, G, B′, C′, C″, D, E, and C under misrooted/RO) | notices (4-part, PH §4.4) | |
| row B pass line; `degraded` clause | notices | PH §3.3, §3.6 |
| `/brd-reconcile`'s check-again-or-cancel on its parent-log row | command-owned question (PH §3.4 row) | |

### 4.6 Mechanics vs judgment

All rows and primitives are git reads (`rev-parse --verify`, `cat-file -e "<ref>:./<path>"`, `diff --quiet`, `for-each-ref`, `merge-base`, `ls-files --others`, `hash-object`) + `gh pr list` → **mechanical** (PH §3.2, §3.3, §3.5). Row B's ownership test is mechanical given the caller's prefixes, key set, and the run's "created/reused this run" record. **Judgment/caller logic:** which paths to gate and when; what to do on `absent` (command behaviour, PH §3.4/§5 rule 3); whether a stop is read without stopping (fixed per caller, PH §3.7). Stop wording: rows D/E/B′ have fixed texts; G, C′, C″, I need §4.4's four parts composed — templatable, not given verbatim.

---

## 5. `branch-check` (PH §6)

### 5.1 Caller inputs

| Input | Defined |
|---|---|
| `folder` — the folder the handoff names as `feature_folder` (or the PRD folder above an Epic address, where that is what the handoff names), or each folder a multi-folder run resolved | PH §6 *Inputs* |
| `prefix` (optional) — the prefix the caller's handoff will name, passed once prefix and unit key are known; for several folders, for the first | PH §6 *Inputs* |
| `reuse: later` (optional) — §6.2 skipped this call; caller re-runs without it once its folder settles | PH §6 *Inputs* |
| implicit: `<default-ref>`/`<default>` from the preflight; flags; `session_branch`; read-only mount | PH §6 *Inputs*, *Gate*, §6.1 |

### 5.2 Outputs

`{stopped, finding, switched}` (PH §6.3). Printed: `Branch check: stopped — <the stop>` (one line); `Branch check: switched to <branch>, which holds open work under <root>`; git-refusal stop line (2 variants). A §6.2 switch moves HEAD (later steps, incl. the handoff's rule-3 reuse, see it). A stop ends the run before its work and takes the refusal tail (PH §6.3).

### 5.3 Ordering obligations

- Once at run start, after **both** `specs-preflight` and `resolve-address` (whichever second) and the carrier-placement refusals, before anything reads or gates the folder's documents (PH §6 ¶1).
- `/ready`: after its clean-main test (PH §6 ¶1; `ready.md:150`).
- §6.2 before §6.1 where both apply; §6.1 then tests the branch after any switch (PH §6 ¶1).
- Several roots → once per distinct root (PH §6.1 last ¶).

### 5.4 Variation points

- **V5.1 `reuse: later` + second call** — `/design` with `<EPIC>` null (`design.md:98`), `/specify` on a PRD address (`specify.md:295`, again at `:627`/`:630` after Step A).
- **V5.2 No `prefix`** — commands handing nothing off in the specs repo: `/vuln` (each distinct root, `vuln.md:49`), `/security-workflows:scan` (`scan.md:99`), keyed `/document` (`document.md:71`). Effect: §6.2 never runs; §6.1 always takes the "does not build on it" switch remedy.
- **V5.3 Folder not yet created** — a folder this run is about to create has nothing to compare (`idea.md:146`, `brd-intake.md:164`).
- **V5.4 Callers reading a §6.1 stop without stopping** (PH §6.3): `/ready` (records, caps; except after a §6.2 switch), `/brd-reconcile` cross-BRD guard on a dependent's folder under another root. No other.
- **V5.5 Gate passes silently**: `$SPECS_PATH` unset/not a repo, `<default-ref>` missing, `blocked`, detached HEAD (PH §6 *Gate*). `.git` need not be writable.
- **V5.6 §6.1 applies only where HEAD is a plugin branch** (not default, not G2's, not the session branch); "builds on" (name test or stack test) → B′ remedy forms; else switch-to-default forms; each with plain / `lift` / misrooted / read-only variants (PH §6.1).
- **V5.7 §6.2 skipped** without `prefix`, with `reuse: later`, under `misrooted`, on a read-only mount (PH §6.2).
- **V5.8 Folder outside `specifications/`** (an `@<path>` elsewhere) has no root → passes (PH §6 *The root*).
- **V5.9 Non-callers**: commands resolving no specs-tree folder — `/upgrade`, `/docs-init`, `/docs-brand`, `/docs-audit`, `/harvest-decisions`, `/promote-decisions`, the four logging commands, `/diagnose-session` (matrix §7).

### 5.5 Interactive points

| Point | Kind | Cite |
|---|---|---|
| **§6.2 reuse question** `choices: ["Switch to <branch> and continue there (Recommended)", "Stop — merge <branch>'s pull request, or close it and delete <branch>, first"]` | **needs answer** | PH §6.2 |
| `Branch check:` stop / switched lines | notices | PH §6.1–§6.3 |

### 5.6 Mechanics vs judgment

Root computation, §6.1 diff less session shapes, name test and stack test, §6.2 ref/merge tests, switch, stop text → **mechanical** (PH §6). Caller judgment: which `folder`(s), whether and when a `prefix` is known, `reuse: later` (PH §6 *Inputs*). The question → harness.

---

## 6. Cross-cutting: tail, ending early, session-hygiene

- **Emitter tail** (SRG §4; SH §5 rule 2): feedback → follow-ups → cost → `resume.md` → `commit-artifacts`. Each emitter (and `resume.md`) runs `env-check` first (SH §7 *Callers*). Under `misrooted` all fall to report-only, no `resume.md` (SRG §3.1).
- **Ending early.** (SRG §7 rule 2): a command that can stop states once, in a paragraph headed **Ending early.**, what each stop leads to: the refusal tail; a stop before the preflight skipping only the preflight; or a route the stop's own text names. 30 commands carry the heading (`grep -l '^\*\*Ending early\.\*\*'`); the logging commands and `/diagnose-session` carry none (matrix §7).
- **SH §7 `env-check`** sets `misrooted` with `Environment changed: started in …, now … — nothing more is committed, handed off or recorded here…`; once per run; skipped where SH §6 pinned the run; passes where no `Environment:` line was printed since this invocation.
- **SH §6 resume-environment** (`/design`, `/specify` only): compare at (1) resume, (2) before the deliverable write leading to the handoff, (3) before the tail's first write; each point re-loads the part afresh; mismatch → **question** (point 1: 2 arrays depending on `specs_origin`; points 2/3: Stop / Go on pinned, offered only where the recorded env still exists, else *Stop* without asking); *Stop* sets `misrooted` with `RESUME_ENVIRONMENT_CHANGED:` line, which `commit-artifacts` and `handoff-to-main` repeat.
- **Never restate** (SRG §7 rule 4; PH §5 rule 4): cite section numbers; PH §4.3 arrays the one quotable exception; in a file requesting a PH entry file, explanatory pointers to text the file does not hold are worded, not cited (`scripts/reference-parts.py check-citations`).

## 7. Per-command call-site matrix (grep, run from `plugins/`)

Columns: `pre` = lines matching `specs-repo-git specs-preflight|specs-preflight\` entry point`; `com` = same for `commit-artifacts`; `h2m` = `phase-handoff handoff-to-main`; `rom` = `phase-handoff require-on-main`; `bc` = `phase-handoff branch-check`; `EE` = `^\*\*Ending early\.\*\*`; `rl` = `reuse: later`. Counts are matching lines, not calls.

| Command | pre | com | h2m | rom | bc | EE | rl |
|---|---|---|---|---|---|---|---|
| dev-workflows/conformance | 1 | 1 | 2 | 1 | 1 | 1 | 0 |
| dev-workflows/design | 1 | 1 | 2 | 1 | 2 | 1 | 1 |
| dev-workflows/implement | 1 | 1 | 2 | 1 | 1 | 1 | 0 |
| dev-workflows/ready | 1 | 1 | 2 | 1 | 1 | 1 | 0 |
| dev-workflows/upgrade | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| dev-workflows/vuln | 1 | 1 | 0 | 0 | 1 | 1 | 0 |
| docs-workflows/docs-audit | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| docs-workflows/docs-brand | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| docs-workflows/docs-init | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| docs-workflows/document | 1 | 2 | 0 | 0 | 1 | 1 | 0 |
| docs-workflows/release-notes | 1 | 1 | 2 | 0 | 1 | 1 | 0 |
| product-workflows/brd-intake | 1 | 1 | 2 | 0 | 1 | 1 | 0 |
| product-workflows/brd-interview | 1 | 1 | 2 | 2 | 1 | 1 | 0 |
| product-workflows/brd-package | 1 | 1 | 2 | 3 | 1 | 1 | 0 |
| product-workflows/brd-proposal | 2 | 2 | 2 | 1 | 1 | 1 | 0 |
| product-workflows/brd-reconcile | 1 | 1 | 4 | 3 | 2 | 1 | 0 |
| product-workflows/brd-split | 1 | 1 | 2 | 2 | 1 | 1 | 0 |
| product-workflows/create-ard | 1 | 1 | 1 | 3 | 1 | 1 | 0 |
| product-workflows/create-prd | 1 | 1 | 2 | 2 | 1 | 1 | 0 |
| product-workflows/epics | 1 | 1 | 2 | 1 | 1 | 1 | 0 |
| product-workflows/harvest-decisions | 1 | 1 | 2 | 0 | 0 | 1 | 0 |
| product-workflows/idea | 1 | 1 | 1 | 0 | 1 | 1 | 0 |
| product-workflows/prd-ground | 1 | 1 | 2 | 2 | 1 | 1 | 0 |
| product-workflows/prd-proposal | 2 | 2 | 2 | 1 | 1 | 1 | 0 |
| product-workflows/promote-decisions | 1 | 1 | 0 (via `architecture-promotion` §11.2) | 0 | 0 | 1 | 0 |
| product-workflows/specify | 1 | 1 | 2 | 3 | 3 | 1 | 1 |
| product-workflows/update-prd | 1 | 1 | 1 | 0 | 1 | 1 | 0 |
| product-workflows/update-spec | 1 | 1 | 2 | 1 | 1 | 1 | 0 |
| security-workflows/scan | 1 | 1 | 0 | 0 | 1 | 1 | 0 |
| workflows-core/diagnose-session | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| workflows-core/feedback | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| workflows-core/frames | 1 | 1 | 1 | 0 | 1 | 1 | 0 |
| workflows-core/prompt-brainstorm | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| workflows-core/prompt-grill-me | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| workflows-core/prompt | 1 | 1 | 0 | 0 | 0 | 0 | 0 |

35 commands call both SRG entry points; no call in `docs-profile`, `docs-serve`, `statusline` (family) or the `guideline-reviewers`/`prose-style` commands. `rom 0` on a producer is by design where it gates no prior deliverable: `/update-prd` and `/brd-intake` are named exclusions (`.claude/rules/workflows-core-git.md`); `/idea`, `/frames`, `/release-notes`, `/harvest-decisions` and `/promote-decisions` are simply not among the sixteen consumers listed there.

## 8. What the references leave open, or that a script cannot do (for the GIT-G1 design)

1. **Questions cannot be scripted**: §4.3 consent, row C repair, §6.2 reuse (and SH §6's mismatch). The skill must split each into prepare (probe, flags, class) → ask (harness) → execute (script). EF's "a request after the choice was answered does not ask again" must survive the split.
2. **Run state currently lives in the conversation**: the last `Environment:` line since this invocation (SH §7 step 1), `specs_git` flags and the setter's notice text, the fired guard's block, B4's branch, "-D advisory once per run", `session_branch_created`, "branch created/reused by this run" (row B), the declined deliverable list, `remote`. A script needs a per-invocation state file (precedent: `dev-workflows/scripts/run-state.py`).
3. **Replay timing**: SRG §4 step 6 requires a Bash call of its own with a 420000 ms timeout (372 s capped git + margin under the 600 s ceiling). §3.4 can reach the replay **per branch** (flush, retry, and each other plugin branch in the settle loop), so one preflight Bash call could need several 420 s budgets — a single script invocation cannot honour "a Bash call of its own" per replay without returning control between them.
4. **Unfixed by the reference**: which single key `commit-artifacts` uses on a two-key run, and which key §3.4's flush commit uses; whether *Cancel* (option 3) also gets the "deliverable remains uncommitted, as you asked" append (SRG §4.1/§6 tie it to option 2's wording; PH §4.3 says 2 and 3 both decline); B4's report wording.
5. **Judgment that must stay with the command/LLM**: run key set construction; resolve-first vs preflight-first; class/half selection (§4.0 register); `title`, `body_facts`, `inputs_read`; PR-template filling (§2.7.1); `absent` handling and stop-reading exceptions; tail classification of each stop; where lines sit in the report and "nothing restates the report".
6. **Path resolution**: SBP and the B′/§6.1 `lift` remedies name `${CLAUDE_PLUGIN_ROOT}/scripts/session-branch.py` resolved to `workflows-core`'s root; a caller plugin's own `${CLAUDE_PLUGIN_ROOT}` does not reach it (`CLAUDE.md` *Internal reference convention*), so the thin skill must live in `workflows-core`. `register_rebuild` is the one value that must cross a plugin boundary as an argument (SRG §7).
7. **Load cost being replaced**: SRG is read whole (~159 KB) at each of two requests per run, PH-h2m 348 lines, PH-rom 234, PH-bc 104, SH env-check part (SKILL.md; EF).

# GIT-G1 Part 1 — the script's core — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One tested `workflows-core` script, `specs-git.py`, carries the deterministic primitives of `specs-repo-git` and `phase-handoff` — the §2.1 status classifier, `branch-merged`, `branch-key`, `push-scope`, `owner-repo` and `mode` — and the two references call it where they now spell those steps out by hand.

**Architecture:** A new standard-library Python script beside `session-branch.py`, loading that script as a module so the classifier, the push-scope walk, `mode` and the git helper exist once. Each primitive is a subcommand printing one JSON object, exit 0 when it ran and exit 2 (one `specs-git: not run (…)` line on stderr) when it could not. No command file changes in this part; the references keep every rule and its reason and replace only the step-by-step git they now delegate.

**Tech Stack:** Python 3 standard library, git ≥ 2.38 for `merge-tree --write-tree` (older git: test 4 reads unmerged, as the reference already says), the repository's CI (`.github/workflows/validate-catalog.yml`).

**Spec:** `docs/superpowers/specs/2026-11-08-git-g1-shared-specs-git-design.md` (§4, §5.1, §7 Part 1). Evidence: `docs/superpowers/specs/2026-11-08-git-g1-evidence/contract.md` §1 (preflight), §2 (commit), §8.

## Global Constraints

- Python 3 standard library only, as `session-branch.py`, `lineage.py` and `bounded.py` (design §3).
- Every git call is `git -C <root>`, never a `cd`; nothing here writes the working tree, the index or a ref (`specs-repo-git` §1).
- One JSON object on stdout per call; exit 0 when it ran, whatever it found; exit 2 when it could not run, printing exactly one `specs-git: not run (<reason on one line>)` line on stderr, never a traceback — `session-branch.py`'s contract (`main()`, `Parser.error`).
- `--specs <root>` must be the repository's top level (`rev-parse --show-toplevel`, compared by `realpath`), as `session-branch.py` checks; `owner-repo` alone takes `--repo <path>` instead, since it also serves non-specs repositories.
- The classifier is `session-branch.py`'s `classify`, imported, never copied — "one implementation" (design §2 goal 1). Same for `push_scope`, `mode` and `git`/`text`/`nul_list`.
- `branch-key` never extracts a key from text: candidates are only the keys passed in (`CLAUDE.md` § Editing discipline, *Resolve an identifier against a known set*; `specs-repo-git` §3.5).
- New prose is never hard-wrapped (`workflows-core:prose-formatting`); the references' existing hard-wrapped blocks keep their own style where edited in place.
- `plugins/workflows-core/reference-parts/` is regenerated with `python3 scripts/reference-parts.py generate`, never edited.
- A rules file stays under 20,000 characters (`wc -m`), `CLAUDE.md` under 36,000.
- No command, agent or page of another plugin changes in this part (design §7 Part 1). `dev-workflows:code-handoff` §2.6 keeps its own `owner-repo` text: a `dev-workflows` reference cannot call a `workflows-core` script by path.

## Review Focus

1. **A porcelain `-z` path the old prose mishandled** — a rename record (`R  <new>\0<old>\0`), a path with a space, a non-ASCII byte (`PRD-ACME-1-zahlungsauslösung`), `Doc screenshots/`: `status` must put each in the right list and never treat a rename's old path as a record. Test in Task 1.
2. **A key that prefixes another** — a run holding `ACME-77` and `ACME-77-01`, a branch `spec/ACME-77-01-slug`; and a digit-led slug (`spec/PRODUCT-1234-2fa-rollout` with `PRODUCT-1234-2` in the set): the longest candidate wins and the separator is required. Test in Task 3.
3. **A squash the patch-id tests miss** (GIT-B1's 30-line case: branch changes line 10, default changes line 12 before the squash) must read merged by test 4, and a branch whose only change sits in a merge commit must not read merged by test 2. Test in Task 2.
4. **A remote URL the old two-expression form passed through** — `ssh://git@host:2222/Org/repo.git`, an scp form, a trailing slash, an SSH `Host` alias whose `HostName` is `github.com`, and a nonsense `https://github.com/` that names no owner: `owner-repo` must return the reference's value or `null`, never a URL. Test in Task 5.
5. **The script run where it cannot work** — `--specs` pointing at a subdirectory, at no repository, or a ref that does not exist: exit 2 with one stderr line, no traceback, no partial JSON. Test in Task 1 (harness) and each subcommand's own task.

---

### Task 1: The script, its harness and `status`

**Files:**
- Create: `plugins/workflows-core/scripts/specs-git.py`
- Modify: `.github/workflows/validate-catalog.yml` (one selftest step after `session-branch.py`'s; mirror its comment style)

**Interfaces:**
- Consumes: `session-branch.py` loaded once at import as module `sb` via `importlib.util.spec_from_file_location("session_branch", <HERE>/session-branch.py)`; uses `sb.git(root, *args, check=True)`, `sb.text(r)`, `sb.nul_list(r)`, `sb.classify(path) -> bool`, `sb.NotRun`.
- Produces: `status(root) -> {"artifact": [str], "other": [str]}` (both sorted, de-duplicated); CLI `specs-git.py --specs <root> status`; `selftest() -> int` (0 pass, 1 fail) with a `check(ok, what)` collector and a `Repo` helper like `session-branch.py`'s; `main() -> int`.

- [ ] **Step 1: Write the failing selftest for `status`**

In `selftest()`, build a repository in a `tempfile.TemporaryDirectory()` with `GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1`. Create and leave untracked or modified:
- `specifications/PRD-ACME-1-zahlungsauslösung/dev-workflows/resume.md` → artifact
- `specifications/PRD-ACME-2-a b/follow-ups.md` → artifact
- `specifications/PRD-ACME-3/design/frame-set/index.md` → other (reserved `design/`)
- `specifications/PRD-ACME-3/Doc screenshots/a.png` → other
- `specifications/PRD-ACME-3/prd.md` → other (a deliverable)
- `security/web/register.json` → artifact; `security/web/threat-model.md` → other
- a committed `dev-workflows-cost/x.md` renamed with `git mv` to `dev-workflows-cost/y.md` and staged → `y.md` artifact, and `x.md` never appears as its own record

```python
got = status(repo)
check(set(got["artifact"]) == {".../resume.md", ".../follow-ups.md", "security/web/register.json", "dev-workflows-cost/y.md"}, "status: artifacts (%r)" % got)
check("dev-workflows-cost/x.md" not in got["artifact"] + got["other"], "status: a rename's old path is no record")
check(set(got["other"]) >= {"specifications/PRD-ACME-3/design/frame-set/index.md", "specifications/PRD-ACME-3/prd.md", "security/web/threat-model.md"}, "status: other")
```

Also: the CLI on a subdirectory of the repository exits 2 with exactly one stderr line starting `specs-git: not run (`, and on a non-repository directory the same.

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 plugins/workflows-core/scripts/specs-git.py --selftest`
Expected: FAIL (the file has only the harness; `status` undefined), exit 1, failures printed one per line.

- [ ] **Step 3: Implement `status(root)` and the CLI**

`git status --porcelain -z --untracked-files=all`; split on NUL; each record's path is the record minus its first three bytes; where the record's first or second status byte is `R` or `C`, consume the next field as the original path and drop it. Classify with `sb.classify`. `main()` follows `session-branch.py`'s `main()`/`Parser` shape (argparse with a `Parser.error` that prints the one `not run` line and exits 2; `--selftest`; `--specs` required for every subcommand but `owner-repo`; top-level check; `except (sb.NotRun, OSError)` and a final `except Exception` both printing one line). Print `json.dumps(result, indent=2)`.

- [ ] **Step 4: Run it to verify it passes, and the CI step**

Run: `python3 plugins/workflows-core/scripts/specs-git.py --selftest`
Expected: `specs-git selftest: PASS (<n> checks)`, exit 0.
Add the step to `validate-catalog.yml` right after `session-branch.py --selftest`: `run: python3 plugins/workflows-core/scripts/specs-git.py --selftest`.

- [ ] **Step 5: Commit**

```bash
git add plugins/workflows-core/scripts/specs-git.py .github/workflows/validate-catalog.yml
git commit -m "feat(workflows-core): specs-git.py — the status classifier, with selftest"
```

### Task 2: `branch-merged`

**Files:** Modify `plugins/workflows-core/scripts/specs-git.py`.

**Interfaces:**
- Produces: `branch_merged(root, ref, default_ref) -> {"merged": bool, "test": 1|2|3|4|None}`; CLI `branch-merged --ref <ref> --default-ref <ref>`; a `ref` that does not resolve → `sb.NotRun` (exit 2).

- [ ] **Step 1: Write the failing selftests** — one repository per case, `main` as the default, `<default-ref>` = `main`:
- fast-forward merged → `{"merged": True, "test": 1}`
- rebase-merged (branch commits re-applied on `main` with new shas) → `test: 2`
- a branch whose only change sits in a merge commit (merge a side branch into the plugin branch, nothing else) → `merged: False` (test 2 must not hold: `rev-list --merges main..<ref>` is non-empty)
- squash-merged with no context drift → `test: 3`
- GIT-B1's case: a 30-line file; the branch changes line 10; `main` changes line 12, then squash-merges the branch → `merged: True, test: 4`; the same branch before the squash → `merged: False`
- an empty branch (no change of its own) → never `test: 3`; `merged` only by test 1
- unmerged work → `{"merged": False, "test": None}`
- GIT-B2's case: a plugin branch squash-merged on `main` with a dirty session file in the working tree → `merged: True` (the test reads refs only; the dirt does not matter)

- [ ] **Step 2: Run the selftest** — Expected: FAIL on each new check.

- [ ] **Step 3: Implement `branch_merged`** as `specs-repo-git` §3.5's four tests in order, first holding wins: (1) `merge-base --is-ancestor`; (2) `cherry <default-ref> <ref>` non-empty with every line starting `-`, and `rev-list --merges <default-ref>..<ref>` empty; (3) `<base>` = `merge-base <ref> <default-ref>`, the first field of `diff --no-renames <base> <ref> | patch-id --stable` equals the first field of a line of `log -p --no-renames --no-merges <base>..<default-ref> | patch-id --stable` (pipe the bytes through `subprocess` with `input=`; an empty diff has no patch id and fails the test); (4) `diff --quiet <base> <ref>` exits 1, and `merge-tree --write-tree <default-ref> <ref>` exits 0 with its first line equal to `rev-parse <default-ref>^{tree}`; a non-zero exit of `merge-tree` (old git, or a conflict) reads unmerged.

- [ ] **Step 4: Run the selftest** — Expected: PASS.

- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git.py branch-merged — specs-repo-git §3.5's four tests`

### Task 3: `branch-key`

**Files:** Modify `plugins/workflows-core/scripts/specs-git.py`.

**Interfaces:**
- Produces: `branch_key(branch, keys) -> {"plugin_branch": bool, "prefix": str|None, "key": str|None}`; CLI `branch-key --branch <name> [--key <K>]…` (zero `--key` = a keyless run). Pure function: no git call, no `--specs` needed for the function, but the CLI keeps `--specs` for uniformity.
- The prefixes, exactly `specs-repo-git` §2.2's: `idea prd ard spec epics design ready brd frames kb conformance` — pinned as a constant the selftest compares against the regex in `specs-repo-git.md` §2.2 (read the file, as `session-branch.py`'s selftest does for `ARTIFACT`).

- [ ] **Step 1: Write the failing selftests**
- `spec/PRODUCT-1234-2fa-rollout`, keys `{PRODUCT-1234}` → `key: "PRODUCT-1234"`
- same branch, keys `{PRODUCT-1234, PRODUCT-1234-2}` → `"PRODUCT-1234"` (`PRODUCT-1234-2` is followed by `f`, not a separator)
- `spec/ACME-77-01-checkout`, keys `{ACME-77, ACME-77-01}` → `"ACME-77-01"` (longest candidate)
- `ard/EPIC-008-01_slug`, keys `{EPIC-008-01}` → `"EPIC-008-01"` (`_` separator)
- `prd/ACME-7`, keys `{ACME-7}` → `"ACME-7"` (exact)
- `prd/ACME-77-x`, keys `{ACME-7}` → `key: None` (no separator after `ACME-7`)
- `kb/harvest-2026-11-08`, any keys → `plugin_branch: True, key: None`
- `feature/ACME-7-x`, keys `{ACME-7}` → `plugin_branch: False, prefix: None, key: None`
- keys `{}` on `prd/ACME-7-x` → `key: None`
- the prefix constant equals `specs-repo-git.md` §2.2's alternation

- [ ] **Step 2: Run the selftest** — Expected: FAIL.

- [ ] **Step 3: Implement `branch_key`** per §3.5 steps 1–4: strip a `<prefix>/` from the constant set; `R` the rest; candidates are keys `K` with `R == K` or `R.startswith(K + "-")` or `R.startswith(K + "_")`; the longest wins; none → `None`.

- [ ] **Step 4: Run the selftest** — Expected: PASS.

- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git.py branch-key — resolved against the run's keys`

### Task 4: `push-scope`

**Files:** Modify `plugins/workflows-core/scripts/specs-git.py`.

**Interfaces:**
- Consumes: `sb.push_scope(root, head, base) -> (commits, failed_sha_or_None)`.
- Produces: `push_scope(root, branch, session_default_ref=None) -> {"base": str|None, "commits": [str], "in_scope": bool, "failed": None|{"sha": str, "reason": "merge"|"paths"|"branch-path", "path": str|None}}`; CLI `push-scope --branch <name> [--session-default-ref <ref>]`.
- Plugin, default and named branches (`specs-repo-git` §4 step 5): `base` = `refs/remotes/origin/<branch>` where `show-ref --verify -q` finds it, else `None` and the walk is over `--not --remotes=origin`.
- The session branch (§8.4, `--session-default-ref` given): the commits are `rev-list --reverse refs/heads/<branch> --not <base> <default-ref>` (or `--not --remotes=origin` with no base); each is a session-file commit as above **or a merge with exactly two parents**; then `diff --name-only -z --no-renames <default-ref>...refs/heads/<branch>` must list ARTIFACT paths only, the first other one reported as `reason: "branch-path"` with `path` and `sha` the branch's newest merge commit (`rev-list --merges -n 1 refs/heads/<branch>`), or `null` where it has none.

- [ ] **Step 1: Write the failing selftests** with a bare `origin` built in the temp directory:
- a plugin branch pushed, then one session-file commit on it → `base: "refs/remotes/origin/<b>"`, one commit, `in_scope: True`
- a commit touching `specifications/X/prd.md` → `in_scope: False`, `failed.reason: "paths"`, `failed.path` that path
- a merge commit on a plugin branch → `failed.reason: "merge"`
- a branch never pushed → `base: None`, walked over `--remotes=origin`
- the session form: a merge of `main` into `session/ab` plus a session-file commit → `in_scope: True`; a whole change naming `prd.md` → `reason: "branch-path"`

- [ ] **Step 2: Run the selftest** — Expected: FAIL.

- [ ] **Step 3: Implement `push_scope`** — the non-session form calls `sb.push_scope` and maps its failed sha to a reason: where `rev-list --parents -n 1 <sha>` prints two shas (the commit and one parent) the commit failed on its paths, `reason: "paths"`, with the first non-ARTIFACT path of `diff-tree --no-commit-id --name-only -r -z --root --no-renames <sha>` (or `null` for a commit that touches no path); otherwise — a merge, or a root commit — `reason: "merge"`. The session form walks its own list, also allowing a commit for which that call prints exactly three shas (a two-parent merge), then runs the whole-change test.

- [ ] **Step 4: Run the selftest** — Expected: PASS.

- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git.py push-scope — §4 step 5 and §8.4`

### Task 5: `owner-repo`

**Files:** Modify `plugins/workflows-core/scripts/specs-git.py`.

**Interfaces:**
- Produces: `owner_repo(url, resolve_alias=True) -> {"url": str|None, "host": str|None, "slug": str|None, "owner_repo": str|None}`; CLI `owner-repo --repo <path> [--no-alias]` reads `git -C <path> remote get-url origin` (none → all `null`, exit 0).
- The rules are `phase-handoff` §2.6.1's: strip a scheme, a `user@`, a host with an optional `:port` ended by `/` or `:`; then a trailing `/` and `.git`; an `http(s)://` remote keeps its host; any other remote whose host is not `github.com` resolves an SSH alias by `ssh -G <host>`'s `hostname` line (`ssh.github.com` → `github.com`), skipped under `--no-alias`; `github.com` drops the host. A slug failing `^[^/]+/[^/]+$` → `owner_repo: null`.
- `ssh -G` runs with a 10-second cap (`subprocess.run(…, timeout=10)`); a failure leaves the host unresolved, never an exit 2.

- [ ] **Step 1: Write the failing selftests** (pure, no network; the alias case writes a temporary `HOME/.ssh/config` with `Host github-ig.com` / `HostName github.com` and runs with that `HOME`):
- `git@github.com:acme/docs.git` → `"acme/docs"`
- `https://github.com/acme/docs` → `"acme/docs"`
- `ssh://git@git.example.com:2222/team/docs.git` → `"git.example.com/team/docs"`
- `https://git.example.com/team/docs/` → `"git.example.com/team/docs"`
- `git@github-ig.com:acme/repo.git` → `"acme/repo"` with alias resolution, `"github-ig.com/acme/repo"` under `resolve_alias=False`
- `https://github.com/` → `owner_repo: None`
- the CLI on a repository with no `origin` → all four fields `null`, exit 0

- [ ] **Step 2: Run the selftest** — Expected: FAIL.

- [ ] **Step 3: Implement `owner_repo`** with `re` equivalents of §2.6.1's three `sed -E` expressions, applied in its order.

- [ ] **Step 4: Run the selftest** — Expected: PASS.

- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git.py owner-repo — phase-handoff §2.6.1`

### Task 6: `mode`

**Files:** Modify `plugins/workflows-core/scripts/specs-git.py`.

**Interfaces:**
- Consumes: `sb.mode(root, default) -> {"mode", "source", "identity", "identity_rung", "branch"}`.
- Produces: CLI `mode --default <name>`, returning `sb.mode`'s object unchanged.

- [ ] **Step 1: Write the failing selftest** — on a fresh repository `mode --default main` returns `mode: "off"`, and with `git config workflows.sessionBranch true` and `GIT_USER_INITIALS=ab` returns `mode: "on"`, `branch: "session/ab"` (or `"unsupported"` where `merge-tree --write-tree` is missing — accept either, as `session-branch.py`'s own selftest does).
- [ ] **Step 2: Run** — Expected: FAIL.
- [ ] **Step 3: Implement** the subcommand as a call to `sb.mode`.
- [ ] **Step 4: Run** — Expected: PASS.
- [ ] **Step 5: Commit** — `feat(workflows-core): specs-git.py mode`

### Task 7: The references call the script

**Files:**
- Modify: `plugins/workflows-core/references/specs-repo-git.md` — §2.1's staging steps 1–2; §3.5's *Merged — `branch-merged <ref>`* (tests 1–4 become the call; *Why the fourth test* and the history paragraph stay); §3.5's *Branch key resolution* (steps 1–4 become the call; *Why this is a resolution* and *A two-segment key* stay); §4 step 5's `push-scope` bullet; §8.1's `mode` call; §8.4's `push-scope` bullet; §2.1's `<docs-repo-slug>` step 1 (the source string is `owner-repo --repo <docs-repo-root> --no-alias`'s `owner_repo`).
- Modify: `plugins/workflows-core/references/phase-handoff.md` — §2.6.1 (the shell block becomes the call; *An SSH host alias*, *The host is kept* and the expressions paragraph stay as the rules the script follows).
- Regenerate: `plugins/workflows-core/reference-parts/` (`python3 scripts/reference-parts.py generate`).

**Interfaces:**
- Consumes: Tasks 1–6's CLI and JSON fields, exactly as named there.
- Each call is written `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" --specs "$SPECS_PATH" <subcommand> …`, as §4 step 6 already writes `session-branch.py`'s; an exit 2 is reported with the first line of its stderr and the run goes on (§1 rule 5) — a `branch-merged` that cannot run reads **unmerged**, a `push-scope` that cannot run pushes nothing, a `branch-key` that cannot run resolves to no key (B4), a `status` that cannot run stages nothing.

- [ ] **Step 1: Write the check first** — before editing, list every site that spells out a delegated step: `grep -nE 'merge-base --is-ancestor|git -C "\$SPECS_PATH" cherry|patch-id --stable|merge-tree --write-tree|rev-list --reverse refs/heads|status --porcelain -z --untracked-files=all|sed -E .s#\^\[a-zA-Z\]' plugins/workflows-core/references/specs-repo-git.md plugins/workflows-core/references/phase-handoff.md` and record the count per file in the commit message. Every hit is either replaced by the call or is a sentence explaining a rule (keep), never both.
- [ ] **Step 2: Edit** each section: the rule stays as a statement of what holds, the git sequence becomes the call and the JSON fields the section acts on. Keep every *Why* paragraph. Do not touch §3.3, §3.4's text beyond its citation of `branch-merged`, §4 step 6 or §8.2–§8.3.
- [ ] **Step 3: Regenerate and run the gates**

Run: `python3 scripts/reference-parts.py generate && <the validate-catalog.yml chain>` (the repository's `gates` sequence; the check-docs selftest may be skipped locally only where `scripts/` is unchanged — it is unchanged here).
Expected: EXIT=0; `specs-git selftest: PASS`.

- [ ] **Step 4: Commit** — `refactor(workflows-core): specs-repo-git and phase-handoff call specs-git.py for their git primitives`

### Task 8: Rules, records and the release

**Files:**
- Modify: `.claude/rules/workflows-core.md` (*Plugin facts*: the scripts under `scripts/` gain `specs-git`), `.claude/rules/workflows-core-git.md` (its `paths:` and opening line name `scripts/specs-git.py` beside `session-branch.py`; the authority paragraph says the primitives run there), `CLAUDE.md` (the `workflows-core-git.md` table row's paths)
- Modify: `plugins/workflows-core/CHANGELOG.md`, `plugins/workflows-core/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` — minor bump (a new script) to the next free `1.79.x`/`1.79.0`, dated, `### Changed`
- Modify: `.claude/rules/plugin-updates-coupling.md` — a bullet: `workflows-core` alone; no dependent changes; the references now call `specs-git.py`, which ships in the same release
- Modify: `docs/superpowers/to-fix.md` PR10 — one sentence: Part 1 moved the primitives into `specs-git.py`; the whole-reference reads end in Part 2
- Create: `docs/superpowers/verification/2026-11-08-git-g1-part1.md` — written last (`CLAUDE.md` § Editing discipline): the selftest's check count, the grep counts from Task 7 step 1 before and after, `wc -c` of `specs-repo-git.md` and `phase-handoff.md` before and after.

- [ ] **Step 1: Edit**, re-deriving every number with the command beside it.
- [ ] **Step 2: Run the gates** — Expected: EXIT=0; `wc -m .claude/rules/*.md` all under 20,000; `CLAUDE.md` under 36,000.
- [ ] **Step 3: Commit** — `docs: GIT-G1 Part 1 — rules, release and verification record`

---

## Self-review notes

- **Spec coverage:** design §7 Part 1 names the classifier, `branch-merged`, `branch-key`, `push-scope`, `owner-repo`, `mode` (Tasks 1–6), "no command changes yet" (Global Constraints), "`specs-repo-git` cites the script" (Task 7), B01's GIT-B1/GIT-B2 as first tests (Task 2). §5.1's "standalone primitives a command can call" are the CLI subcommands; the commands start calling them in Part 2.
- **Left for Part 2:** the preflight and `commit-artifacts` as subcommands, the state record, the skill, and every command's switch — this part changes no command text, so `main` is never mixed by it.
- **Out of scope here, deliberately:** `<docs-repo-slug>`'s flattening as a subcommand (its emitters are `docs-workflows` commands, which switch in Part 2), and `dev-workflows:code-handoff` §2.6.

# Run-state checks — design (to-fix D18, D24, D26)

**Status:** draft for the maintainer's approval, revised after a builder check. **Decided by the maintainer (2026-10-29):** D18 — check up front and define the refusal; D24 — one Phase 0 check, not per-site listings (a per-site attempt was built, reviewed and dropped: listing `<default-ref>` made ref-only artifacts visible that scripts, agents and key minting downstream could not use), counting **deliverables only**; D26 — the environment record lives in the conversation, and a mismatch is a **prompt-free stop**, never a question. Everything below the decisions is this design's call unless marked otherwise, and the calls are listed at the end.

## Why these three together

Each is a run whose start state differs from what its later steps assume, found only after the work:

- **D24** — the preflight keeps a run on an unmerged plugin branch named for its key (`specs-repo-git` §3.5 B3), and that branch is **behind the default branch** for the folder the run works in. Every working-tree listing then misses what merged since the branch was cut — an Epic, a `design.md`, a slice, a package — and the run proceeds without it rather than stopping.
- **D18** — a producer's `handoff-to-main` reuses an existing branch of its own prefix and key (`phase-handoff` §2.2 rule 3). Measured: where that branch changed a path the run also changed, `git switch` **refuses**, so nothing is overwritten — but the refusal comes after the whole run, with no instruction, and git's own advice (*move or remove them*) does the overwrite by hand. 18 of the 23 producers can reach it; `/ready` does on every re-run while its last pull request is open.
- **D26** — a conversation resumed in another container goes on against whatever `$SPECS_PATH` names there. 36 of the 38 commands keep no record to compare; `handoff-to-main`'s §2.1 gate and `commit-artifacts` compare nothing with the run's start.

All three are cheapest to catch at the run's start, or at its first write, and none needs a file of its own.

## 1. `branch-check` — one entry point, run once at Phase 0 (D24, D18)

A new entry point in `workflows-core:phase-handoff`, beside `require-on-main`. **Every command that resolves a folder in the specs tree runs it once, right after both the preflight and its own address resolution have run** — whichever comes first in that command — and before anything reads the resolved folder's contents. Inputs: the resolved folder; for a producer, the `prefix` its handoff will use.

### 1.1 Behind (D24)

**Applies only where HEAD is a plugin branch** — the state B3 leaves. A local default branch left behind where the preflight's catch-up was skipped (a G1 guard) or its pull failed, and a branch of the operator's own that G2 keeps, are out of scope: §2.3's *Nothing to commit* row, row C″ and `/conformance` step 5.3 already handle the artifacts those states reach, and widening the check to them is a separate change.

**The scope is the address's root folder**: the top-level folder under `specifications/` that holds the resolved folder — a `BRD-` root for a slice, the `PRD-` folder for an Epic, the folder itself for a root. The run reads across that tree (a slice reads its parent's `brd/` and ledger; an Epic its PRD's `prd.md` and `ard.md`; a PRD-level run its Epics), so it is the smallest scope that covers every listing D24 found.

**The test counts deliverables only**: with `<base>` = `git -C "$SPECS_PATH" merge-base HEAD "<default-ref>"`, the paths `git -C "$SPECS_PATH" diff --name-only "<base>" "<default-ref>" -- "./<root>/"` prints, **less every path `specs-repo-git` §2.1's bookkeeping classifier names** — the cost, feedback and follow-up entries, the resume pointer, `implementation.md` and the rest of the session files, which land on the default branch on almost every run and would otherwise stop nearly every resumed one. At least one path left means the default branch added, changed or removed a deliverable under the root since this branch was cut. (Accepted cost: a newer `implementation.md` block on the default branch is not seen from a branch behind it, so `/implement`'s picker may show an Epic as not started.)

**Where any is left, stop**, naming up to ten (and how many more), with one of two remedies by **ownership** — row B's own test:
- **The branch is the run's own** (its prefix the caller's, its key in the run key set): merge the default branch into it, worded as row B′'s remedy already is — `merge <default> into <branch> ('git -C "$SPECS_PATH" merge <default-ref>')`, its conflict guidance, its session-branch `lift` form, and its *no merge is named where none can run* forms for `specs_git: misrooted` and a read-only mount.
- **It is another unit's branch** B3 kept through a shared key (`/specify <ACME-90-02>` standing on `spec/ACME-90-01-…` through the PRD key): switch to the default branch, `git -C "$SPECS_PATH" switch <default>`, then re-run — this run builds nothing on that branch, and `phase-handoff` §2.2 cuts its own from the default ref.

The run merges and switches nothing itself (§1 rule 4).

**`/ready` records it rather than stopping.** Its Phase 0 step 3 lets the operator proceed on the current checkout, read-only and noted in the report, and `phase-handoff` §3.7 already lets it record a stopping row as a finding; a behind branch is recorded the same way.

**Once per root.** A run resolving folders under more than one root folder — `/vuln`'s tokens, `/brd-reconcile`'s dependents — runs §1.1 once for each distinct root.

**Why a stop and not an offer to merge**: the plugin never merges into a branch (§1 rule 4), and the merge can conflict in a document both sides changed, which only a person can settle. A stop names exactly what to run.

**What this replaces**: nothing in B05's three commands (`/design`, `/ready`, `/conformance`) has to change — their `<default-ref>` listings stay true and become redundant on a branch the check has passed. D24's per-site sites (`epic-picker`, `/implement`, `/specify`, `/brd-proposal`, `/brd-package`, `/brd-split`, `/brd-reconcile`, `/prd-proposal`, `/epics`, and the ones its review found — `/specify` Step A, `/epics`' key minting, `components` §3's `epic-targets`, `/implement`'s broad-slice test) all read the working tree correctly once the branch is level, so none is edited.

### 1.2 Reuse (D18) — producers only

**Applies where the caller passed a `prefix`**, which a producer passes once its prefix and its unit key are both known — at Phase 0 for most; `/specify` on a PRD address after its Step A pick; `/brd-reconcile` for its first handoff only. **Two producers pass none**: `/implement`, whose Phase 4.5 handoff is conditional and onto a prefix it does not own (`spec`, `design`), and `/update-spec`, whose own Phase 0 already stops on a branch that changed `specification.md` — the check this would duplicate. The gate in §3 lists both as exempt. Resolve the branch `handoff-to-main` would reuse, by §2.2 rule 3's own resolution, from the run key set and that prefix. **Where one exists, is unmerged (`branch-merged`, `specs-repo-git` §3.5), and is not HEAD**, and `git -C "$SPECS_PATH" diff --name-only "$(git -C "$SPECS_PATH" merge-base "<branch>" "<default-ref>")" "<branch>" -- "./<root>/"` prints a path, ask before any work:

```
choices: ["Switch to <branch> and continue there (Recommended)", "Stop — merge or close <branch>'s pull request first"]
```

*Switch* runs `git -C "$SPECS_PATH" switch <branch>` (refused by git exactly where the tree holds work that would be overwritten, which then stops naming the paths) and then **runs §1.1 against it** — a branch picked up this way may itself be behind. *Stop* ends the run naming the branch and its pull request.

**Why ask here and not at handoff**: the measured cost of D18 is a refused switch after the whole run; asked first, the operator either continues the open work on its own branch — which is what a re-run of the same producer on the same key usually means — or settles it first.

### 1.3 A switch refused at handoff — §4.1's new outcome

A refusal can still happen — a branch created during the run by another session, or one `branch-check` did not see because it was only on `origin` and unfetched. `handoff-to-main` gains the outcome **switch refused**: keep the run's files where they are, never move or remove them and never follow git's advice to, name the paths git listed and the branch, and tell the operator to merge or close that branch's pull request and re-run the handoff (`Phase handoff: refused — <branch> holds <paths> …`). §1 rule 4 gains `switch --discard-changes` and `switch -f` beside the commands it already forbids.

## 2. The environment line (D26) — in the preflight, re-checked before every write, prompt-free

**`specs-preflight` prints one line, every run, before its first act**: `Environment: SPECS_PATH=<realpath of $SPECS_PATH> (origin <git remote get-url origin, or none>), REPOS_PATH=<value, or unset>`. The conversation carries it — the one thing a `claude --resume` takes to another container.

**A new `specs-repo-git` entry point, `env-check`, re-reads the three values and compares them with the last `Environment:` line this run printed** — prompt-free, as every entry point there is (§1 rule 7). Where any differs, it sets `specs_git: misrooted` for the rest of the run and prints one notice naming both environments and saying to re-run where the run started. That flag already does what a mismatch needs, everywhere: `handoff-to-main` refuses on it, every emitter of the tail falls to its report-only tier, and `commit-artifacts` skips — so nothing is written into a repository the run did not start in.

**Where it runs**: at the start of `handoff-to-main` §2.1's gate, and as the first step of every tail emitter — `feedback-emission`, `followup-emission`, `cost-emission` and `session-hygiene`'s `resume-pointer` — so a command that never hands off (`/vuln`, `/document`, `/security-workflows:scan`) is still checked before its first write. **Where the conversation holds no `Environment:` line** — a run started before this release, or one whose preflight did not run — `env-check` passes. **A run `session-hygiene` §6 pinned** (`/design`, `/specify`) compares against its pinned values, which are the ones its line recorded, so the two mechanisms agree.

**Why prompt-free**: `commit-artifacts` and the emitters ask nothing by a hard rule (`specs-repo-git` §1 rule 7, its refused widening in `docs/maintainers/rationale.md`), and a question at the first write would come after nothing useful; the operator re-runs in the right container instead.

## 3. What each command changes

- **Every command that calls `resolve-address`** (`grep -l resolve-address plugins/*/commands/*.md`, re-derived when built) gains one sentence: execute `branch-check` on the resolved folder, after the preflight and the resolution — passing `prefix: <its handoff prefix>` where it runs `handoff-to-main`. A command whose preflight runs after its resolution places it after the preflight.
- **A gate** — `scripts/reference-parts.py check-questions`-style — asserts that every command calling `resolve-address` also executes `branch-check`, and that every one calling `handoff-to-main` passes a `prefix`, so a new command cannot be added without it.
- **Nothing else per command.** The environment line, `env-check` and its callers live in `specs-repo-git`, `phase-handoff`, the three emitter references and `session-hygiene`.

## 4. Releases

`workflows-core` minor (the entry point, §4.1's outcome, the preflight line, the re-checks, the gate's config), and a minor of every plugin whose commands gain the sentence — `dev-workflows`, `product-workflows`, `docs-workflows`, `security-workflows`. One coupling bullet: a command calling `branch-check` needs the `workflows-core` that ships it. Built as one PR, since the gate needs every caller at once.

## Calls this design makes, for the maintainer to check

1. **`branch-check` is one entry point for both D24 and D18**, called once per command (once per root), rather than a change inside `specs-preflight`, which cannot scope D24 (it knows keys, not the folder, and some commands resolve after it) and cannot run D18 (it does not know the producer's prefix).
2. **D24's scope is the address's root folder**, deliverables only: narrower would miss what a slice reads from its parent and a PRD-level run from its Epics; wider would stop runs for unrelated work. Cost: a run stops for a merged deliverable under the same root it would not have read.
3. **D24 stops; it never merges or switches**, with the remedy chosen by ownership — merge on the run's own branch, switch to the default branch on another unit's.
4. **`/ready` records a behind branch as a finding** instead of stopping, as its existing proceed-anyway contract does for stopping rows.
5. **A stale local default branch and an operator's own branch stay out of scope**, and the reference says so rather than claiming the default branch is always level.
6. **D18 asks only where the reused branch changed something under the root**, recommends continuing on it, and exempts `/implement` and `/update-spec`; `/specify` runs it after Step A.
7. **D26 reuses `specs_git: misrooted`** rather than a new flag, since every consumer already honours it the right way.
8. **One PR**, because the gate in §3 needs every caller at once.

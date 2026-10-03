---
name: docs-audit
description: Enumerate what documentation a product is missing and write a prioritised backlog for it. Scans the code repositories the docs profile records, plus the specs tree, into a denominator of documentation surfaces, crosses each surface with the page types it actually earns, ranks the resulting units on four signals with a written reason on every one, and proposes the tutorial candidates the one quadrant that does not automate needs a human for. Writes .dev-workflows/docs-backlog.yml and prints the coverage grid; writes no documentation content, creates no branch and no commit in the docs repository. On --refresh it re-derives surfaces against today's code, reconciles existing pages back to their units, and preserves every field a human owns. Gated on an Opus backlog review whose findings are triaged before anything is applied.
allowed-tools: Read Write Edit Bash Glob Grep Task Skill
---

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

Audit a documentation repository's coverage: $ARGUMENTS

`/docs-audit` answers one question — **what is this product missing documentation about, and which of it is worth writing first.** It builds a denominator from the product's own code and from the committed documents in the specs tree, crosses that denominator with the page types each thing actually earns, ranks the result, and writes `.dev-workflows/docs-backlog.yml` in the resolved documentation repository. **It writes no documentation content**: its output is a backlog and a coverage grid, and turning a unit into a page is a later act. **Its bulk lives in this plugin's own references and it does not restate them** — the coverage vocabulary, the file's schema and the evidence contract are `${CLAUDE_PLUGIN_ROOT}/references/docs-audit/`'s, and a second copy of any of them is a second thing to keep in step. This command body names the entry point it is executing at each step, the inputs it owes each agent, and the merges no agent can make on its own.

**Signature:** `/docs-audit [<docs-repo-path>] [--audience user|engineering|both] [--refresh] [--threshold <n>] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]`

**Every stop in this command takes the same route, and each site says so.** A stop is still a run: it prints its `DOCS_AUDIT_*` line, **skips to the Phase 6 report**, which states that stop and nothing else, and then runs the **emitter tail (Phases 7–9)** — so its cost and feedback are recorded and `commit-artifacts` runs as the last action, which is the family invariant every command writing into `$SPECS_PATH` holds. That is what *takes the stop route* means wherever this body uses it below. The exceptions are the runs that end before Phase 0 step 2 has resolved a repository — step 1's three flag stops, and a Cancel at step 2's own choice — since there is nothing yet to report against; Phase 9 states them.

**Four guarantees are this orchestrator's and no agent's, and they are the reason this command is more than three dispatches in a row.** `docs-auditor` and `ia-planner` each guarantee their own rules *within their own return*; only this command holds the file, so only this command can reconcile a return against what is already in it. Those four are: the `volatility: unknown` substitution (Phase 5), handing each agent what already exists on a `--refresh` (Phases 3 and 4), keeping a theme the scan could not settle out of the gap list (Phases 2 and 4), and applying `priority_comparisons[]` (Phase 5). **A fifth is the tutorial mint (Phase 4.5)**, which `ia-planner` is forbidden to perform and `${CLAUDE_PLUGIN_ROOT}/references/docs-audit/backlog-format.md` §1 assigns to `--refresh` — this command — by name.

---

## Phase 0 — Resolve

**Strip the run flags first.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS` before anything else reads a token: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its maintenance, cost and routing steps — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. Every later step, step 1 below included, parses only what it leaves.

1. **Flags.** Strip `--refresh`, `--audience <value>` and `--threshold <n>` from `$ARGUMENTS` — **each of the last two together with the token immediately after it** — before reading a positional token. What remains is the optional `<docs-repo-path>`. A value read as a path because the flag ahead of it was not stripped is a run that audits the wrong repository, or none. `--audience` takes `user`, `engineering` or `both`, and nothing else: any other value stops with `DOCS_AUDIT_UNKNOWN_AUDIENCE: <value> is not an audience (user, engineering or both).` Absent, it is `both`. `--threshold` takes a positive integer: anything else stops with `DOCS_AUDIT_BAD_THRESHOLD: <value> is not a positive integer.` **After the recognised flags are stripped, any remaining token that begins with `--` stops the run** — `DOCS_AUDIT_UNKNOWN_FLAG: <token> is not a flag of /docs-audit.` **All three of this step's stops are exceptions to the stop route**, with step 2's Cancel: they fire before step 2 resolves anything, so there is no repository to report against and nothing to file a cost entry to — the stop is printed and the run ends there, which is the exception Phase 9 states from the other end. The rule is general, not a list: `resolve-docs-repo` rung 1 takes the first positional token **as given**, with no signal test, so a mistyped `--dryrun` would become the resolved repository and Phase 5 would write `--dryrun/.dev-workflows/docs-backlog.yml`. That includes `--docs` and `--no-docs`, which this command deliberately does not have — **it resolves no documentation grounding**, see step 7 for why.

2. **Resolve the documentation repository.** Execute **`resolve-docs-repo`** from `${CLAUDE_PLUGIN_ROOT}/references/docs-workflow/repo-resolution.md` §1 — the **signal-positive** form, the one `/docs-profile`, `/docs-brand` and `/docs-serve` use to find a repository that already exists (`/document` resolves its repository by a ladder of its own). Do not restate its ladder here, and do not copy `/docs-workflows:docs-init`'s: §4 of that file explains why the two are opposite, and this command needs a documentation repository that exists. Report which rung answered, per that file's own hard rule. **Where the operator cancels at the ladder's rung 4 choice or its rung 5 question** — or answers rung 5 with nothing to take — no repository is resolved, and the run ends there as step 1's stops end it: print `Cancelled: no documentation repository resolved — nothing was read or written.` and stop, emitting nothing, since the specs preflight has not run and there is no repository to file a cost or feedback entry against (Phase 9).

3. **Specs-repo preflight.** Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git specs-preflight")` and execute its `specs-preflight` entry point (§3) inline, as early as `$SPECS_PATH` is known. This runs against `$SPECS_PATH` only — `git -C "$SPECS_PATH"`, never a `cd` — so the documentation repository this run is about to read and write is untouched (§1 rule 1). Prompt-free, and silent unless it acts, a guard fires, or §3.1 reports a misconfigured `$SPECS_PATH`. If a guard fires, emit its §5 notice; if it returns `specs_git: blocked` (§3.3 G0) or `specs_git: misrooted` (§3.1), carry that flag for the whole run — the terminal `commit-artifacts` step skips on it. **This family creates no branch in `$SPECS_PATH`**, so this preflight only ever settles a branch that already exists.

4. **Resolve `<top>` and read the profile.** `<top>` is the **git work-tree top level** of the directory step 2 resolved — what `git -C <resolved> rev-parse --show-toplevel` prints, or the resolved directory itself where it is in no git work tree. `${CLAUDE_PLUGIN_ROOT}/references/docs-audit/backlog-format.md` §6 pins the backlog there and says why the distinction matters exactly where the resolved directory is not the top level. **The resolved repository has to be one this command may write into**, and that is settled here rather than at Phase 5: `resolve-docs-repo` assigns the check to its caller, and this command's own step 6 principle is that a refusal is only worth anything while the operator is still being asked things. `test -w <top>` must succeed, and `<top>/.dev-workflows/` must exist or be creatable; otherwise stop: `DOCS_AUDIT_NOT_WRITEABLE: <top> is not writeable, so the backlog cannot be written there.` Then take the stop route.

Read `<top>/.dev-workflows/docs-profile.yml`. **Three states, and the third is not the second:** a profile that reads gives this run its `source_repos[]` (step 5), its `spaces[].content_root` entries (Phase 5) and the `profile` input the review gate takes; **an absent profile is not a stop** — the run continues, confirms the source-repo set with the operator, reconciles over the whole tree rather than over content roots, passes the reviewer no `profile` (which that agent degrades on rather than refusing), and reports all three, naming `/docs-workflows:docs-profile` as what would write one; **a profile present and unreadable** — malformed, or a `schema_version` this reader does not know — is reported the same way and treated as absent for the rest of the run, never guessed at.

5. **Resolve the source repositories.** These are the coverage denominator: what is recorded decides what a coverage figure is a fraction *of* (`${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/docs-profile-schema.md`, `source_repos[]`).

   - **Where the profile records the key**, resolve each entry in the order that file fixes — `path` where it exists and is a git work tree on this machine; else `origin`, matched against the directories one level under `${REPOS_PATH:-/workspace}` by each one's own `git -C <dir> remote get-url origin`, comparing slugs as `<owner>/<repo>`; else ask. **An entry that resolves by neither is reported, never silently dropped** — a denominator that quietly shrinks makes coverage go *up*, which is the worst direction this field can fail in. Ask per unresolved entry:

     ```
     "source_repos[] names <name>, and neither its recorded path (<path>) nor its origin (<origin, or "none recorded">) resolves to a clone on this machine. How should I proceed?"
     choices: ["Give me the clone's absolute path", "Exclude it from this audit — the report will say the denominator is short by one repository", "Cancel this run"]
     ```

     **No `(Recommended)` marker, deliberately**: which option is right depends entirely on why the clone is not there — a workspace laid out differently from the machine that wrote the profile, a repository genuinely retired, or a profile entry that was wrong when it was written — and the run cannot tell those apart.

   - **Where the profile records the key as an empty list**, that is a positive claim rather than an absent one: `docs-profile-schema.md` says an empty `source_repos[]` asserts that this portal documents nothing, which is why `/docs-workflows:docs-init` omits the key instead of writing one. Honour it — scan no code repository, say in the report that the profile asserts none, and fall to step 6, which is where a run with no specs tree either is refused. Do not silently re-ask: the operator's own file has answered.

   - **Where the profile does not record the key at all** — a repository profiled by `/docs-workflows:docs-profile`, or scaffolded before that field existed — confirm the set with the operator and **record it**. List `${REPOS_PATH:-/workspace}` one level deep for directories that are git work trees, and add any the operator named. Print **every** candidate as prose above the prompt, one line each — its directory name and its `origin` slug where it has one — then:

     ```
     choices: ["Audit all of the repositories listed above (Recommended)", "Name the ones to include — I'll take them from the list above", "None — audit the specs-tree surfaces only"]
     ```

     A typed answer is **resolved against the list just printed, never parsed out of the free text** — the rule `workflows-core:epic-picker` *The cap* states for its own directory-listing picker, and the reason the candidates are printed as prose rather than rendered as one option per repository: `${REPOS_PATH:-/workspace}` is unbounded, so an array sized to it is a tool call the harness rejects the moment a workspace holds five clones. Load that reference with `Skill(skill: "workflows-core:reference", args: "epic-picker")` where the cap's wording is wanted. **The array above is fixed-arity by construction**, so no overflow row is needed: the set travels in the prose, and only the *disposition* is picked. Write the confirmed set into the profile as `source_repos[]`, one `{name, path, origin}` entry per repository, `origin` omitted where the clone has none — **and where step 4 found no profile at all, record nothing and say so**, naming `/docs-workflows:docs-profile` as the command that writes one; this run then confirms the set again next time, which is worth saying in the report rather than leaving to be discovered.

6. **Refuse a run with nothing to enumerate from.** Test `$SPECS_PATH` here rather than deferring to Phase 2.5 — is it set, a readable directory, and does it hold a specifications tree — because a refusal is only worth anything while the operator is still being asked things. Where the confirmed source-repo set is empty **and** that test fails, so Phase 2.5 will skip, stop: `DOCS_AUDIT_NO_SOURCES: no code repository resolved and no specs tree to read, so there is nothing to enumerate surfaces from. Confirm a source-repo set, or set $SPECS_PATH.` Then take the stop route. This is the refusal `docs-auditor` would return as `INPUT_MISSING`, taken here where the operator can still answer it.

7. **This command is not a documentation-grounding consumer, and the reason is recorded so it is not re-litigated on the strength of the repository it obviously opens.** `workflows-core:docs-grounding` has **three** consumption modes and none of them fits. **grill-rank** reorders challenges into a grill's gap list, and this command runs no grill. **writer-attach** attaches a digest to an artifact being authored as prose, and this command authors none — it writes a backlog. **lead-only** — `/prd-ground`'s — is the one a maintainer reopening this would reach for, so it gets the explicit answer: there the digest steers *where to look*, and a lead is worth having because a grounder then goes and proves something at the place it pointed at. Here there is nothing downstream of a lead: a **surface** may be enumerated only from a scanner's `capability_map[]` or from the specs inventory, which is `docs-auditor`'s own hard rule, so a page that says a feature exists cannot put it in the denominator however plainly it says so — it would be a surface nothing verified, and the coverage figure is a claim about the product. Existing documentation *is* read here, by Phase 5's reconcile, which opens the resolved documentation repository directly and matches a page to a unit by the page's own `unit:` frontmatter key. That is a file read against a known set of ids, not a retrieval, and it is not grounding. So no `docs-grounder` is dispatched, no `--docs` or `--no-docs` flag is parsed, and `workflows-core:docs-grounding`'s consumer list does not name this command.

8. **Read the existing backlog, and settle what kind of run this is.** The file is `<top>/.dev-workflows/docs-backlog.yml`.

   - **`--refresh` with a readable backlog** — this is a refresh.
   - **`--refresh` with no file there** — nothing to preserve, so the run proceeds exactly as an initial run and **says so**; it is not a stop, because the outcome is identical either way, and it is not silent, because the likeliest cause is a path that resolved somewhere the operator did not mean.
   - **No `--refresh`, and a backlog is already there** — do not overwrite it. That file holds picked tutorial candidates, corrected `priority_reason` prose and hand-added units, none of which this run could reconstruct:

     ```
     "<top>/.dev-workflows/docs-backlog.yml already exists (<N> surfaces, <M> units, <K> picked tutorial candidate(s)). An initial run would overwrite every field a human owns in it."
     choices: ["Treat this as a --refresh run (Recommended)", "Cancel — nothing is written"]
     ```

     **Cancel ends the run with nothing written**: skip Phases 1 through 5.5 and go straight to the Phase 6 report, which states plainly that the run was cancelled here. The emitter tail (Phases 7–9) still runs, so this run's cost and any feedback are still recorded.

   - **A backlog whose `schema_version` this reader does not know** — higher, absent, or unparseable — **or a file that will not parse as YAML at all**, **is reported and nothing is written into it**, whichever of the three cases above it arrived under (`backlog-format.md` §1, which gives `schema_version` the opposite disposition from an unrecognised `status`). Stop: `DOCS_AUDIT_UNKNOWN_SCHEMA: <top>/.dev-workflows/docs-backlog.yml declares schema_version <value>; this release reads 1. Nothing was written.` Then take the stop route. A run that carried on would silently drop whatever the later version added, on every block it rewrote.

   **However this run became a refresh — the typed flag, or the third bullet's prompt answered *Treat this as a `--refresh` run* — hold the file's `surfaces[]`, `units[]`, `tutorial_candidates[]` and `threshold` for Phases 3, 4, 4.5 and 5.** A promoted run is a refresh in every respect; there is no second, weaker shape of one.

9. **Settle `threshold`.** `--threshold <n>` wins and the report names it as an operator change; else a refresh writes back what the file already carries, unchanged; else an initial run seeds `2` and says in the report that this is a starting value rather than a decision (`backlog-format.md` §1 and §5 own both halves — nothing re-derives a threshold).

---

## Phase 1 — Model routing

Invoke the `model-routing` skill (Skill tool, `skill: "workflows-core:model-routing"`), then classify the task.

`/docs-audit` is **SIGNIFICANT**. It is a cross-cutting synthesis of every scanned repository whose output steers every page anybody later writes: a surface that is not there, a unit in the wrong quadrant, or a rank resting on a reason nothing supports is copied forward into prose and is expensive and silent by the time anybody notices. A wrong backlog has a large blast radius. State the classification and a one-line reason.

**The review gate is Opus regardless of class, unless `run_flags.enforced_model` is set (§10, which pins the reviewer dispatch to the enforced id instead).** D17 and D20: every artefact-writing command of the docs-workflow family the 2026-08-29 design's §4 table lists (`/docs-init`, `/docs-brand`, `/docs-audit` and the artefact-writing commands that design plans after them — **not** every command in this plugin: `/document` in direct mode takes a style check and no review gate, `/release-notes` a light gate, `/docs-profile` no review gate at all, and `/docs-serve` writes no artefact and runs none) passes a high-tier review with no tiering by unit. Record a `model_routing` block:

```yaml
model_routing:
  classification: SIGNIFICANT
  reason: "cross-cutting synthesis of every scanned repository; the backlog steers every page written from it"
  current_model: <the model this orchestrator is running under>
  enforced_model: <run_flags.enforced_model, or omit>   # §10: when set, every dispatched-step *_model below equals it (inline authoring_model / implementation_model keep the session model) and routing: bypassed
  defect_model: <§2.1 Sonnet chain — only under --skip-feedback; under §10, run_flags.enforced_model>
  detection_model: <§2.1 Sonnet chain: claude-sonnet-5-5, fallback claude-sonnet-5/4-6/4-5>   # code-scanner, docs-auditor, impl-maintenance
  review_model: <the §2 Opus chain — claude-opus-5-5, fallback per §2 — pinned regardless of classification, per D17/D20>
  opus_available: true | false
  notes: <any §2 degradation, e.g. "Opus unavailable; docs-audit-reviewer fell back to Sonnet 5.5">
```

**All five agents this run dispatches carry an explicit `model:` argument.** Three are pinned by their own frontmatter and take no override under ordinary routing — `ia-planner` and `docs-audit-reviewer` to Opus, `docs-auditor` to Sonnet — so each one's dispatch simply names that same pin, recorded rather than overriding anything, unless `run_flags.enforced_model` is set (§10), in which case the dispatch substitutes the enforced id there too; an Opus fallback (or the enforced id) is announced here and again in the final report. The other two carry no pin and are pinned by the dispatch itself: `code-scanner` at Phase 2 and `impl-maintenance` at Phase 7, both to the detection chain above, and both to the enforced id under §10.

---

## Phase 2 — Scan the source repositories

1. **The themes are the seven surface kinds, and they are not re-derived here.** Load `${CLAUDE_PLUGIN_ROOT}/references/docs-audit/coverage-model.md` and take **the surface kinds** (§2): one `capability_themes[]` entry per row of that table, phrased from that row's own `Derived from` cell. All seven go to every repository, for two reasons and not for a third that would be false: `docs-auditor` **asserts** it is dispatched with all seven and reads its `kinds[]` roll-up against that, and one theme set asked of every repository is what makes `absent` comparable across them — `absent` everywhere is an answer, `absent` here and unasked there is not. It is **not** that nothing else would settle a missing kind: `decision` and `release` are settled by Phase 2.5 alone, and `docs-auditor` sets a code repository's map entry for either of those aside unread. Do not invent an eighth, do not drop one because a repository looks unlikely to have it, and do not reword one out of your own sense of what the word means: an `absent` classification is an answer about the product, and it is only an answer if the question was §2's.

2. **`code-scanner` refuses to run without `repo_path`, at least one `capability_themes` entry, and a `context`**, so the dispatch supplies a `context` of three to five sentences saying what this scan is for: that this is a documentation coverage audit; that it is looking for **where each kind of thing lives** rather than for a defect; that an `absent` classification is a wanted answer and not a failure; and that every evidence path it returns becomes a surface's evidence in a backlog, so a path it cannot stand up is worse than a theme it classifies `absent`.

3. **Dispatch one `code-scanner` per resolved repository, in a single response, capped at 4 concurrent**, pinned to the §2.1 detection chain (`model: <detection_model — §2.1 chain; under §10, run_flags.enforced_model>`), per `workflows-core:model-routing/classification` §8 — cited by name rather than as a bare section number, because that file's own §8.5 is not the only §8.5 a reader could land on. Pass `refresh: { switch_to_default_branch: true, pull: true }`: a coverage denominator is a claim about the product as it ships, so the scan reads the default branch, and a read-only mount reaches neither of those and scans at `prep.scanned_ref` instead (`workflows-core:read-only-repos`). Record each return's `prep.scanned_ref`, with the repository's name and path and the time of the scan, into `sources[]` for the file Phase 5 writes — `{ repo, path, ref, scanned_at }`, the four fields `backlog-format.md` §1 fixes for a source and no others. **Where the confirmed set is empty this phase dispatches nothing and says so** — Phase 0 step 6 has already established that the specs tree is there to supply the two kinds it owns, so an empty set here is a specs-only audit and not a failure.

4. **Handle every status the agent can return rather than assuming `OK`.** `workflows-core:handoff/code-scanner` fixes six:

   - **`OK`** — read normally.
   - **`PARTIAL`** — at least one theme carries `classification: error`. The rest of that map is read normally; **the errored themes go to the unresolved list and never to the gap list.** `code-scanner`'s classification has four values and only one of them, `absent`, means *looked and found none*. An `error` folded into absence asserts that the product lacks something nobody managed to look for.
   - **`EMPTY`** — the repository was read and holds none of the kinds it was asked about. That is an answer: it contributes no surface, and it is **reported** in the run's own output rather than dropped in silence, because a repository the operator named and that yielded nothing is worth their attention.
   - **`REPO_MISSING`** — escalate per `workflows-core:escalation-rules`, *Repo missing (after resolution)*, per affected repository.
   - **`DIRTY_TREE`** — escalate per that file's *Dirty working tree*. Cited by name and not reproduced, so this command uses the variant written under that heading.
   - **`REFRESH_BLOCKED`** — escalate per that file's *Refresh blocked*, on the same terms.

   A return whose `prep.read_only` is `true` and whose `prep.ref_committed_at` is more than 14 days old, or whose `prep.head_divergence.ahead` is greater than zero, additionally raises that file's *Read-only mount — ref stale or diverged*, per affected repository. A read-only mount is not a failure and never raises *Refresh blocked*: the scan proceeds at `prep.scanned_ref`, which is the ref `sources[]` records and the ref every later read of that repository is made at (`workflows-core:read-only-repos`).

5. **This command adopts `workflows-core:model-routing/classification` §8.5 — the seeded second round — and says so here because that section is opt-in.** An inconclusive theme (that section's own definition: `classification` of `partial`, `absent` or `error`, or two or more scanners whose `gap_summary` texts point at each other's repository) gets **one** narrow round 2, seeded from round 1's verified `evidence[].path` and `.symbols`, capped at 4 dispatches. There is no round 3. **A theme still unresolved after round 2 is named, and the mechanism is a field rather than a hope.** `docs-auditor` puts a theme into `unresolved[]` on its own account only where a scanner classified it `error`; §8.5's **other** definition of inconclusive — mutual deferral, two or more scanners pointing at each other's repository — arrives classified `present` or `partial` and would otherwise be enumerated normally and never named at all. So this run passes such a theme in the `unresolved_themes[]` input that agent's contract takes for exactly this (`${CLAUDE_PLUGIN_ROOT}/references/handoff/docs-auditor.md`), as `{kind, theme, source, reason}`, and the agent folds it into `unresolved[]` verbatim — from there into `ia-planner`'s echo of it and into this run's report. **Never rewrite a scanner's `classification` to `error` to force the same effect**: that would put into `capability_map[]` a claim no scanner made, and `code-scanner`'s own status table would then disagree with its map. It is **never** flattened into a gap: a gap asserts absence, an unresolved theme asserts only that the scan could not tell, and this file's coverage figure is a claim about the product that the second does not support.

---

## Phase 2.5 — The `$SPECS_PATH` read

**Two of the seven surface kinds do not come from a code repository at all, and nothing before this phase has looked for them.** `coverage-model.md` §2 sources the `decision` kind from ADRs and ARDs already present in the specs repository and the `release` kind from `/docs-workflows:release-notes` drafts under `$SPECS_PATH`, grouped by release version. `code-scanner` scans a code clone and `docs-auditor` sets a code repository's map entry for either kind aside unread, so without this phase those two kinds would silently never appear.

**This is a read-only enumeration, not a scan.** No agent is dispatched; this run reads the tree itself, and it writes nothing into `$SPECS_PATH` but its own bookkeeping, through `commit-artifacts` alone (Phase 9).

1. **Resolve the tree.** Where `$SPECS_PATH` is unset, is not a directory, or holds no specifications tree, the inventory is `status: SKIPPED` with the reason stated — **a skip, not a failure.** A product documented from a code repository with no specs tree still earns its other five kinds, and this run says which two it did not earn and why.
2. **Resolve the ref.** Where `$SPECS_PATH` is a git work tree, `ref` is the commit `git -C "$SPECS_PATH" rev-parse HEAD` prints, and `docs-auditor` reads every enumerated path at it. Where it is a directory that is no git work tree, `ref` is `null`, and that agent reads those paths as plain files and records in its notes that drift has nothing to diff them against. **That is a third state and not a skip**: the tree is there and is read.
3. **Enumerate `decision` entries** — every `ard.md` under the specifications tree, whose folder layout is `workflows-core:addressing` §2's (`specs-repo-git` §2.1 is a staging allowlist and fixes no layout). One entry per file: `{ kind: decision, title: <the ARD's own title>, paths: [<path relative to $SPECS_PATH>] }`. An architecture decision the repository keeps under some other name is not enumerated — say so in the report, because the remedy is a hand-added unit (`coverage-model.md` §6, entry path 5) rather than a wider pattern that would resolve nothing against a known set.
4. **Enumerate `release` entries** — every `release-notes.md` under that same tree (again `workflows-core:addressing` §2's layout), grouped by the release version each draft is filed under. One entry **per version**, not per file: `{ kind: release, version: <the version>, paths: [<every draft path filed under it>] }`, so one version documented from two PRD folders is one surface with two evidence paths rather than two surfaces earning two *What's new* pages.
5. **Record the specs tree in `sources[]` too, as its own entry** — `{ repo: <the last path segment of `$SPECS_PATH`>, path: <$SPECS_PATH>, ref: <the ref step 2 resolved, or null>, scanned_at: <now> }`. `docs-auditor` builds every `decision` and `release` evidence entry with that same last path segment as its `repo`, so without this entry those paths name a source the file does not record — and `docs-audit-reviewer` dimension 1, which resolves each `evidence[].repo` against `sources[]`, would report every one of them as unchecked. On a **specs-only** run this is the only `sources[]` entry there is, and it is what keeps that review from refusing outright: that reviewer refuses a backlog whose `sources:` block is absent or empty, on the ground that nothing in it could then be checked at a ref.

6. **Report an entry whose path does not resolve** rather than passing it on — `docs-auditor` drops a path that does not resolve at its ref and names it, and a path this run can already see is missing is worth saying here too.

---

## Phase 3 — Enumerate surfaces (`docs-auditor`)

→ Agent (subagent_type: "docs-workflows:docs-auditor", model: `<detection_model — §2.1 Sonnet chain, equal to docs-auditor's frontmatter pin; under §10, run_flags.enforced_model>`):  # recorded in model_routing as detection_model above, frontmatter-pinned, no override added unless §10 enforces a model
  > "Enumerate this product's documentation surfaces. The brief is the one `${CLAUDE_PLUGIN_ROOT}/references/handoff/docs-auditor.md` fixes:
  >
  > repos: [one entry per scanned repository — its `repo`, `repo_path`, `status`, `prep` block and `capability_map[]`, exactly as `code-scanner` returned them, with round 2's narrowed answers folded into the theme they settled]
  > specs_inventory: [Phase 2.5's block — `status`, `specs_path`, `ref`, `skip_reason` where skipped, and `entries[]`]
  > existing_surfaces: [ON A REFRESH ONLY: every surface already in the backlog, as `{id, kind, title}`. OMITTED on an initial run]
  > unresolved_themes: [every theme Phase 2 step 5's round 2 left unresolved WITHOUT a scanner classifying it `error` — each as `{kind, theme, source, reason}`. OMITTED where there is none; an `error` theme is already in its scanner's own map and is not repeated here]"

**`existing_surfaces[]` is not optional on a refresh, and leaving it out is not a degradation — it is a corruption.** A unit points at its surface by **id**; a refresh that does not hand the agent the ids already in the file re-mints them, and every unit pointing at the old id is orphaned — which `docs-audit-reviewer` dimension 4 then reports as a BLOCKER on a file this run wrote. The agent says as much in its own notes where the list was not supplied; do not put it in a position to have to.

**Handle the four statuses it can return.** `OK` and `PARTIAL` both carry surfaces and both continue — `PARTIAL` means at least one of: a non-empty `unresolved[]`, a kind whose outcome is `unresolved`, a degraded context input, an evidence path dropped, or a surface carrying `volatility: unknown`; every one of those is carried into the report. **`NO_SURFACES`** means there is nothing to plan: **`ia-planner` is not dispatched**, no backlog is written, and **Phases 4, 4.5, 5 and 5.5 are skipped entirely** — the run goes straight to the Phase 6 report, which states `kinds[]` and `unresolved[]` so the operator can see whether the product genuinely has none of these things or the scan could not tell, and the emitter tail (Phases 7–9) still runs. On a refresh the existing file is left exactly as it was, because a unit is never deleted and a run that enumerated nothing has not learned that anything went away. **`INPUT_MISSING`** is a run that never started: stop with `DOCS_AUDIT_AUDITOR_INPUT_MISSING: <what the agent named as absent>.` Then take the stop route.

**Carry `volatility` through untouched.** The agent returns `high`, `medium`, `low` or `unknown`; `unknown` means the `git log` invocation genuinely failed. Do **not** substitute anything here — Phase 4 needs to see `unknown`, and Phase 5 is where the substitution happens and is recorded.

---

## Phase 4 — Type and prioritise (`ia-planner`)

→ Agent (subagent_type: "docs-workflows:ia-planner", model: `<review_model — §2 Opus chain, equal to ia-planner's frontmatter pin; under §10, run_flags.enforced_model>`):  # recorded in model_routing as review_model above, frontmatter-pinned, no override added unless §10 enforces a model
  > "Plan the documentation units these surfaces earn. The brief is the one `${CLAUDE_PLUGIN_ROOT}/references/handoff/ia-planner.md` fixes:
  >
  > surfaces: [`docs-auditor`'s `surfaces[]`, verbatim — every field as it returned them, `volatility: unknown` included]
  > audiences: [`[user, engineering]` under `--audience both` or with no flag; `[user]` or `[engineering]` under the flag's other two values]
  > unresolved: [`docs-auditor`'s `unresolved[]`, verbatim]
  > existing_units: [ON A REFRESH ONLY: every unit already in the backlog, each carrying its `id`, `surface`, `audience`, `type`, `priority` AND its stored `priority_reason`. OMITTED on an initial run]
  > existing_tutorial_candidates: [ON A REFRESH ONLY: every `tutorial_candidates[]` entry already in the backlog, with its `role`, `journey`, `picked` and `unit`. OMITTED on an initial run]"

**Both `existing_` lists are what make a refresh's rules checkable at all, and an agent handed neither guarantees its rules only within its own return.** Without `existing_units[]` the agent cannot see which `(surface, audience, type)` cells are occupied, which `U-` ids are taken, or which stored `priority_reason` each comparison is against — so it mints into occupied cells, re-uses ids, and returns an empty `priority_comparisons[]`, and `backlog-format.md` §8's id-collision, occupied-cell and preserve-the-human's-fields hard rules — each defined in its §1 — are all left to this command with nothing to apply them from. Without `existing_tutorial_candidates[]` it re-proposes a journey for a role that already has one, which the merge then has to discard. **Each existing unit carries its stored `priority_reason`** — a unit supplied without it cannot be compared at all, which is the whole of Phase 5's re-ranking.

**Handle the four statuses.** `OK` and `PARTIAL` both carry units and both continue. **`NO_UNITS`** is reachable and is not an error — `--audience engineering` over a set of `task` and `concept` surfaces mints nothing, because those kinds feed user types — and the run **still writes the file**: `surfaces[]` was re-derived, `priority_comparisons[]` may be non-empty, and on a refresh every existing unit is preserved. **`INPUT_MISSING`** stops the run: `DOCS_AUDIT_PLANNER_INPUT_MISSING: <what the agent named as absent>.` Then take the stop route — the backlog Phase 5 would have written is not written, and on a refresh the file already there is left exactly as it was.

**`unresolved[]` comes back echoed and is carried into the report unchanged.** It never becomes a unit, never becomes a gap, and never becomes the reason a cell is reported as covered.

---

## Phase 4.5 — The tutorial mint

**A picked tutorial candidate becomes a unit here, and nowhere else.** `ia-planner` is forbidden to mint a `type: tutorial` unit or a `surface: null` one, and `backlog-format.md` §1 assigns the mint to `/docs-audit --refresh` by name — so on an initial run this phase is a no-op (nothing in a file this run is creating can carry `picked: true`), and on a refresh it runs over every `tutorial_candidates[]` entry whose `picked` is `true` **and** whose `unit` is still `null`. An entry whose `unit` is already set is **never** minted again: that recorded id is what stops every later refresh minting a second tutorial for the same journey, each with a fresh id and none of them colliding with anything.

**What the mint writes is `backlog-format.md` §1's, in full, and is executed rather than restated here** — `surface: null` with the candidate's `journey` copied across (the sanctioned null that is *not* drift-blind), `type: tutorial`, `audience: user`, the candidate's role, `visibility: public`, a composed `title`, the priority rule §1 fixes and its `priority_reason` carrying the candidate's `rationale` verbatim, and the fixed remainder. Three things the file's rule leaves to whoever holds it:

- **The id is minted after `ia-planner` has returned**, continuing from the highest `U-` id across **both** the units already in the file and the units that agent just returned. Minting from the file alone collides with a unit this same run created.
- **A candidate whose `journey` names a surface this run did not enumerate is not minted either, and the pick is likewise left alone.** `docs-audit-reviewer` dimension 4 reports a `journey` id that names no surface in `surfaces[]` as a finding, so minting there would write a defect into the file this run then submits for review. Report the candidate and the ids that went missing, and say that a later run which re-enumerates them will mint it — the surfaces may simply not have been scanned this time.
- **A picked candidate on a run whose `--audience` excludes `user` is not minted, and the pick is not disturbed.** `tutorial` is a user type, so minting there would create a unit this run's own filter refuses. Report the candidate, leave `picked: true` and `unit: null` exactly as they are, and say that a run with `user` in scope will mint it. Discarding the pick would take the one authority this quadrant has.

---

## Phase 5 — Reconcile, merge, and write

This phase assembles the file. **It is where the backlog is first written to disk, and the spec's own phase list puts that write one phase later** — it is here because `docs-audit-reviewer` takes a `backlog_path` and reviews a file, so the file has to exist before the gate runs. Nothing else about the order moves: the review still precedes the report, and the survivors it produces are applied to this same file.

1. **Substitute `volatility: unknown`.** `backlog-format.md` §1 fixes `surfaces[].volatility` at `high|medium|low`, so `unknown` is not a value the file may carry. Write `medium` for every such surface **and name every one of them in the report**, with the reason the measurement failed. A backlog carrying `unknown` violates its own contract; a backlog carrying a silent `medium` is worse, because nothing downstream can then tell a measured middle from a measurement nobody made. The substitution happens **here and not before Phase 4**: `ia-planner` reads the handoff block rather than the file, so it sees `unknown`, ranks it as `medium` without churn-adapting on it, and says in that unit's `priority_reason` that volatility was unmeasured — which is the record the substitution would otherwise erase.

2. **Apply `priority_comparisons[]`.** This block is produced by `ia-planner` and applied by nobody else: that agent holds neither the file nor the authority to write into it, and `backlog-format.md` §1's test needs the stored pair, which only this command has. Per entry, run §1's **mechanical** test: where the stored `priority_reason` is **exactly** the reason this run derived, nothing was hand-edited and **both** fields take the new values; where it differs, **both stored values stand** and the run reports the pair it would have written. Collect the ids of every unit whose stored reason was preserved into `preserved_priority_reasons[]` for the review gate — those reasons are the operator's, not this run's output, and dimension 3 excludes them. **Skipping this step makes a `--refresh` unable to update a priority after the code moved, which is most of what a refresh is for.** An existing unit for which no comparison came back has no surface left to re-derive from; it is step 4's business, not this one's.

3. **Merge what a refresh preserves.** Execute `backlog-format.md` §1's *What a `--refresh` re-derives and what it preserves* rather than re-deriving it here: `generated_at`, `sources[]`, `surfaces[]` and every `coverage` figure are statements about the code as it is now and are re-derived; every unit already in the file is preserved with its `page_path`, `walkthrough`, `title`, `roles`, and its hand-written `surface: null`, `journey` and `evidence`; `threshold` and the four human fields of every `tutorial_candidates[]` entry are preserved; and `status` and `blocked_by` are written only through the rules of step 4 below — §3's page reconciliation and §4's two `blocked_by` tokens — and in no other way. Append `ia-planner`'s new candidates only for a role that has none, and report — without writing — any role for which this run would have proposed a different journey.

4. **Reconcile against what exists, on a refresh.**

   - **Match pages to units by the page's own `unit:` frontmatter key**, searched over the profile's `spaces[].content_root` entries where step 4 of Phase 0 read a profile, else over every markdown file under `<top>` outside `.git/` and `.dev-workflows/` — say which of the two the run did, because the second sweep can meet a build output and a reader should know that it might have.
   - **A unit still `missing` whose page is found is read before it is published.** No marked claim in that page → `published`. One or more `[NEEDS CLARIFICATION]` markers → `drafted`, with the page, the unit and the marker count reported. `backlog-format.md` §3 owns both arms and `${CLAUDE_PLUGIN_ROOT}/references/docs-audit/evidence-contract.md` §3 says why: a reconciliation that published every tagged page it found would take a page with an unresolved claim straight to the one state the coverage fraction counts.
   - **Two pages carrying the same unit id** match neither: report both and leave the unit's `status` where it is. A run cannot tell which page the id belongs to, and picking one would record a `page_path` that is half wrong.
   - **A page carrying a `unit:` id that names no unit in this file** is reported as an orphaned page and changes nothing.
   - **Units with no page stay `missing`.**
   - **A unit carrying a `status` this reader does not recognise is reported and left alone** — it is a value a later spec added, not a corrupt file, and normalising it away would destroy the only record of it (`backlog-format.md` §3). That is the opposite disposition from an unknown `schema_version`, which is a claim about the whole file and stops the run at Phase 0.
   - **`[surface-removed]`** — a unit **that names a surface** no longer in this run's `surfaces[]` gets the token added and is reported; its `status` is not changed, because nothing about the page has moved. A `surface: null` unit has no surface to lose and is never marked (`backlog-format.md` §4).
   - **`[page-missing]`** — a unit carrying a `page_path` that no longer resolves in the documentation repository gets the token added and is reported, `status` untouched.
   - **A unit is never deleted.** A surface disappearing from a scan is as likely to be a scan that failed or a repository that was not mounted as a feature that was genuinely removed, so the run records what it observed and the person reading the report decides.
   - **On an initial run** there are no units to reconcile; the sweep still reports any page carrying a `unit:` key, since a page tagged against a backlog that is not there is worth knowing about.

5. **Compute `coverage`.** Per `(audience, type)` cell, the fraction of that cell's units whose `status` is `published` over every unit in that cell whatever its status — derived from the `units[]` table **in this same run**, never carried forward and never adjusted by hand (`backlog-format.md` §5, whose definition and `coverage-model.md` §7's move together). **`--audience` filters what `ia-planner` mints; it never filters what `coverage` counts.** A refresh run under `--audience user` still computes the engineering cells over the engineering units already in the file — a grid that dropped half of itself because of a flag would report a figure about a backlog that is not the one in the file.

6. **Report the two `surface: null` counts**, not one: how many units carry no surface, and how many of **those** also carry no `journey`. The second is the only one that says how much of this backlog drift genuinely cannot see — a minted tutorial carries a journey and fans out from every surface it names, while a hand-written unit relies on its `review_by` date alone (`coverage-model.md` §6 and `backlog-format.md` §1).

7. **Test the path against the repository's own ignore rules, then write.** Run `git -C <top> check-ignore -v <top>/.dev-workflows/docs-backlog.yml`. **Where `<top>` is no git work tree there is no rule to test against**: skip the test and say in the report that the backlog is not under version control at all, which is a larger version of the same problem and worth stating rather than passing over in silence. **On a match, report the path, the matching line and the file it is in, and write the backlog anyway** — saying plainly that it will not be committed until somebody changes that rule. This repository may not be one this family scaffolded, and its `.gitignore` may carry a `.dev-workflows/` or a `*.yml` line nobody thought about; a tracked backlog is the point of the file, and an untracked one written in silence is the failure worth catching (`backlog-format.md` §6). Never force-add past a project's own rule.

8. **Write `<top>/.dev-workflows/docs-backlog.yml`**, conforming to `backlog-format.md` §1, with `schema_version: 1`, `generated_at` today's date and `generated_by: docs-audit`.

**No branch, and no commit, in the documentation repository — ever.** This run's deliverable is one tracked file that a person reads, edits and commits with the rest of their work; it is not a page set, it is not a scaffold, and there is nothing here for a pull request to be about on its own. The backlog is left in the working tree for the operator, exactly as `/docs-workflows:document`'s direct mode leaves its edits. The terminal `commit-artifacts` step (Phase 9) is a **different repository**: it stages only `$SPECS_PATH`'s bounded artifact paths and never the file written here.

---

## Phase 5.5 — Review gate

The backlog steers every page anybody later writes, so it is reviewed before anybody writes from it (D17). Dispatch `docs-audit-reviewer`, pinned to Opus by its own frontmatter:

→ Agent (subagent_type: "docs-workflows:docs-audit-reviewer", model: `<review_model — §2 Opus chain, equal to docs-audit-reviewer's frontmatter pin; under §10, run_flags.enforced_model>`):  # recorded in model_routing as review_model above, frontmatter-pinned, no override added unless §10 enforces a model
  > "Review the documentation backlog this run wrote:
  >
  > Task description: [/docs-audit run against <top> — <an initial run | a --refresh run>, --audience <value>, threshold <n>, <N> source repositories scanned]
  > backlog_path: [the absolute path of the .dev-workflows/docs-backlog.yml Phase 5 wrote]
  > repos: [one entry per source this run's `sources[]` records — every scanned code repository, **and the specs tree** where Phase 2.5 read one — each carrying `repo` (the name used as `sources[].repo` and as every `evidence[].repo`), `repo_path` (where it is mounted on this machine) and `scanned_ref` (null for a specs tree that is no git work tree, which that reviewer reads as a source it cannot check rather than as a defect)]
  > profile: [the resolved docs-profile.yml, or an explicit statement that Phase 0 resolved none and why — that input degrades rather than refusing, and dimension 2's second half is then reported unchecked]
  > preserved_priority_reasons: [the unit ids Phase 5 step 2 preserved rather than rewrote. Empty on an initial run, where every reason is this run's own]"

**Triage before applying anything.** Invoke `Skill(skill: "workflows-core:reference", args: "finding-triage")` and follow it: verify each finding's own claimed consequence at the location it names; keep it, mark it unverified, or dismiss it — a dismissal with a reason that disposes of that finding's own claim, an unverified finding with what would settle it; raise a grade only by effect; carry **survivors only** forward, and carry every dismissal, every unverified finding and every raise into the Phase 6 report, per that reference's § Reporting — a triage that reports only survivors is indistinguishable from a reviewer that found less. Where triage empties the survivor set on a non-PASS verdict, follow that reference's own disposition: surface it and let the operator settle the verdict with the prompt it gives a caller that runs no re-review, never silently promoting it to PASS. **Keep the verdict** there takes the `DOCS_AUDIT_UNRESOLVED_BLOCKER` stop below, and **Cancel** ends the run as a Cancel below does.

**There is no backlog fixer (D25) — the orchestrator applies survivors itself**, editing `docs-backlog.yml` directly and bound by `finding-triage.md`'s patch gate: fix only a defect a finding actually demonstrated, never guard state it did not show, and never edit an instruction file the gate names that this run did not itself write. A survivor whose fix is not a safe mechanical patch is surfaced rather than guessed at. **Two arrays, chosen by the survivor's own severity**, because what deferring *does* differs between them and an option that promises the wrong outcome is worse than no option: a deferred MAJOR leaves the run going, a deferred BLOCKER ends it at the paragraph below these arrays. The prompt already holds `<SEVERITY>`, so the choice of array needs nothing the run does not have. Neither array carries a `(Recommended)` marker, and that is deliberate rather than an omission: which option is right turns on whether the operator judges this backlog fit to write from, which is a judgement the run has no grounds to make for them.

For a **MAJOR** survivor:

```
"docs-audit-reviewer flagged <finding> as MAJOR, and the fix isn't a safe mechanical patch: <why>. How should I proceed?"
choices: ["Describe the fix yourself — I'll apply it", "Defer — leave it open, recorded in the report, and continue", "Proceed despite it — I've judged the backlog fit as it stands", "Cancel this run"]
```

For a **BLOCKER** survivor:

```
"docs-audit-reviewer flagged <finding> as BLOCKER, and the fix isn't a safe mechanical patch: <why>. How should I proceed?"
choices: ["Describe the fix yourself — I'll apply it", "Proceed despite it — I've judged the backlog fit as it stands; the run continues", "Defer — leave it open; the run then stops with DOCS_AUDIT_UNRESOLVED_BLOCKER", "Cancel this run"]
```

**Cancel, on either array, ends the run here.** The backlog Phase 5 wrote stays on disk — reviewed, with this finding open and nothing applied — and the run takes the stop route, with the Phase 6 report naming the review as cancelled rather than as passed. Nothing rolls the file back: a written backlog with a known open finding is more use than none, and deleting it would discard the scan that produced it.

**Neither *Proceed despite it* option agrees with the finding.** It records that the operator read it, did not dispute it, and chose to go on — the finding stays in the report at its own severity, unfixed and attributed to them. An operator who thinks the finding is *wrong* says so through the harness's free-text escape, and that is a triage dismissal with a reason, which belongs above this prompt rather than in it.

A **BLOCKER** left deferred — neither fixed nor proceeded past — stops the run: `DOCS_AUDIT_UNRESOLVED_BLOCKER: a BLOCKER finding from docs-audit-reviewer was neither fixed nor accepted by the operator — resolve it and re-run.` Then take the stop route; the backlog Phase 5 wrote stays on disk, reviewed and not fixed, and the report says so. A BLOCKER that is fixed, or that the operator chose to proceed past, continues. MAJOR survivors are applied the same way and a deferred one does not stop anything; MINOR and NIT are deferred to the report without a prompt. **There is no re-review cycle** — with no fixer there is no second pass to gate against: the orchestrator's direct edit is the fix, applied against the same finding it answers. This is `/docs-workflows:docs-init`'s disposition, not `/product-workflows:prd-proposal`'s, which does re-review once after its inline fix.

---

## Phase 6 — Report

```
## Docs-audit Report

(Three shapes of run reach this report having written no backlog, and they do **not** fill it in the same way. A **Phase 0 stop or the step-8 Cancel** happened before anything was scanned: Target reports what was resolved and why the run ended, and Sources, Surfaces, Units, Coverage, Top 20 units, Reconciliation and Review all read `N/A — ended at <the stop or the Cancel>`. A **`NO_SURFACES`** return did scan: Sources and Surfaces are filled in full, with `kinds[]` and the unresolved themes saying why nothing was enumerated, and only Units, Coverage, Top 20 units, Reconciliation and Review read `N/A — NO_SURFACES`. A **stop at Phase 3, 4 or 5.5** fills every section the run reached and reads `N/A — ended at <the stop>` below it. The Next step says what to do about it in all three.)

### Classification
SIGNIFICANT — cross-cutting synthesis of every scanned repository; the backlog steers every page written from it (review gate is Opus regardless, D17/D20, unless run_flags.enforced_model is set — §10)

### Model Routing
Detection model (§2.1): <detection_model>   Review model (§2): <review_model>   Notes: <any §2 fallback, or "none">
Opus available: <true | false>
[Under `run_flags.enforced_model`: `Model routing: bypassed — enforced <id> (flag|env)` in place of the Detection model / Review model line above — every dispatched step already carries the enforced id, per `workflows-core:model-routing/classification` §10. `Opus available` is unaffected by enforcement (§10: a property of the environment, not of the enforcement choice) and is reported on its own line exactly as it stands.]
Run flags: [the `Run flags: …` line, repeated, whenever Phase 0 printed one during this run (`workflows-core:run-flags` §6) — omit this line otherwise. The `Session feedback: …` skip line is Phase 7's own output; the `Session cost: …` skip line is Phase 9's own output, printed after this report and not restated in it.]

### Target
Docs repo: <resolved directory>  (resolved via: <which resolve-docs-repo rung answered>)
Backlog:   <top>/.dev-workflows/docs-backlog.yml  (<written | written but ignored by <file>:<N> `<line>` — not committable until that rule changes | written, but <top> is no git work tree — nothing here is under version control>)
Run:       <initial | --refresh>   Audience: <both | user | engineering>   Threshold: <n> (<seeded by this run as a starting value | carried forward unchanged | set by --threshold>)
Profile:   <path | "none resolved — /docs-workflows:docs-profile writes one; source_repos[] was confirmed for this run and not recorded" | "unreadable: <reason> — treated as absent">

### Sources
<one line per repository: name, path, scanned_ref, status, and where it came from — the profile's source_repos[] or this run's confirmation>
<every entry that resolved by neither path nor origin, and what the operator chose for it>
Specs tree: <status READ at <ref> | READ, no git work tree (ref null — drift has nothing to diff these against) | SKIPPED: <reason>>
<"source_repos[] recorded in the profile" | "not recorded: <why>">

### Surfaces
Enumerated: <N> across <the kinds, with a count each>
Unresolved themes: <N — each named with its kind, its source and its reason, NEVER counted as a gap | "none">
Volatility substituted: <the surfaces written as `medium` because their measurement failed, each with the reason | "none">
Dropped evidence paths: <N, each named with its repo and ref | "none">

### Units
Minted this run: <N>   Preserved: <N>   Total: <N>
Tutorial candidates: <N proposed, K picked, J minted this run | "none">
Re-ranked: <N units took this run's derived priority>
Preserved reasons: <N units kept a reason a human edited — one line each: the unit id, its stored priority and reason, and the priority and reason this run would have written instead | "none">
Tutorial candidates not minted: <each picked candidate this run left alone, with why — its journey names a surface this run did not enumerate, or --audience excludes user | "none">
blocked_by added: <N [surface-removed], N [page-missing]>
surface: null units: <N>, of which <N> carry no journey and are therefore outside drift entirely

### Reconciliation
(A refresh only; on an initial run this section reads "N/A — initial run; <N> page(s) carrying a unit: key were found and are listed as orphaned below".)
Pages matched: <N>   Published: <N>   Left drafted for a marked claim: <N, each with its page and marker count>
Not matched: <N unit(s) still missing>
Orphaned pages: <each page carrying a unit: key that names no unit in this file | "none">
Ambiguous ids: <each unit id carried by two pages, with both paths — neither matched | "none">
Page search: <"the profile's content roots: <the roots>" | "every markdown file under <top> outside .git/ and .dev-workflows/ — no profile resolved, so a build output could be among them">

### Coverage
user:        tutorial <a/b>  how-to <a/b>  reference <a/b>  explanation <a/b>
engineering: architecture <a/b>  decision <a/b>  runbook <a/b>  api-reference <a/b>
At or under threshold <n>: <N> unit(s), <N> published — <"done" by coverage-model.md §7 | "not done: <N> still to publish">

### Top 20 units
<up to twenty units, lowest priority number first, each with its id, priority, audience/type, title and priority_reason. Read these first: everything downstream obeys this file, and a reason that is wrong here is wrong on every page written from it.>

### Review
Verdict: <PASS | PASS WITH RECOMMENDATIONS | BLOCK, resolved | "N/A — NO_SURFACES, nothing written to review">
Findings: <N reviewed — M survived triage, U unverified, X dismissed; K applied, J deferred or overridden with reason — every dismissal, unverified finding and raise listed per `workflows-core:finding-triage` § Reporting | "N/A">
Not checked: <any dimension or half-dimension an absent input left unchecked, as the reviewer named it | "none">

### Next step
[per `workflows-core:next-phase-offer` — guidance only, never auto-invoked. On a completed run: open the backlog, read the top twenty units and correct any `priority_reason` that is wrong, then set `picked: true` on the tutorial candidates worth writing and commit the file with the rest of your work — nothing here committed it. The written procedure for turning a unit into a published page, automated steps and manual ones alike, is this plugin's route page, `docs/docs-workflow.md`. Re-run `/docs-workflows:docs-audit --refresh` when the product gains a surface — a new integration, a new role, a new release — so the denominator grows with the product rather than freezing at day one. Where the run wrote no backlog — a `NO_SURFACES` return, a stop, or the step-8 Cancel — state that plainly and name what would have to change first: for `NO_SURFACES` what `kinds[]` and the unresolved themes say about why, and for a stop or a Cancel the one thing it named.]
```

**This offer carries no `<merge-clause>`.** `workflows-core:next-phase-offer`'s merge-clause rule applies where an offer names a downstream command whose `require-on-main` gate is fed by *this run's own artefact*. This run's deliverable is one file in the documentation repository; it creates no branch in `$SPECS_PATH`, runs neither `handoff-to-main` nor `require-on-main`, and no `$SPECS_PATH` gate reads what it wrote. `scripts/check-docs.sh` check 11 asserts the placeholder across the `/product-workflows:brd-*` and `/prd-*` families only — no `/docs-*` glob is in its scope — so nothing enforces this here; it is stated by discipline, for the next maintainer who adds a `/docs-*` offer that *does* name a fed gate.

---

## Phase 7 — Session maintenance & feedback

Terminal phase — runs AFTER the Phase 6 report; NEVER interrupts an earlier phase.

**Under `run_flags.skip_feedback`** (`workflows-core:run-flags` §4), dispatch `workflows-core:defect-reporter` instead of `impl-maintenance` in step 1, with the same handoff plus `Plugin root: ${CLAUDE_PLUGIN_ROOT}` (literal — it expands in command bodies to this command's own plugin location), and `model: <§2.1 Sonnet chain, or run_flags.enforced_model>`; if it returns at least one defect, persist them with `emit-bugs` (`Skill(skill: "workflows-core:reference", args: "feedback-emission emit-bugs")`) in place of `emit-auto`, otherwise load nothing. Surface `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` in place of step 3's persisted-path line. Capture-at-block (`emit-block`) is unaffected by the flag.

1. **Invoke `impl-maintenance`** (subagent_type: "workflows-core:impl-maintenance", model: `<Sonnet detection chain — claude-sonnet-5-5, fallback claude-sonnet-5 / 4-6 / 4-5; under §10, run_flags.enforced_model>`):
   > "Analyse this session and return a Lessons Learned report.
   >
   > Session handoff:
   > - Command run: /docs-audit
   > - What was done: [one-paragraph summary — N surfaces enumerated across M repositories and the specs tree, K units in the backlog at <top>, initial or refresh, or the run that stopped at NO_SURFACES with nothing written]
   > - Key events: [an unresolved theme after round 2, a repository that could not be resolved from `source_repos[]`, a `volatility` substitution, a `schema_version` stop, a backlog a project `.gitignore` line ignores, a deferred or overridden review finding — or 'none']
   > - Workarounds used: [manual steps not automated by the workflow — or 'none']
   > - Review verdict: [PASS | PASS WITH RECOMMENDATIONS | BLOCK, resolved | N/A — never reached]
   > - Test result: N/A (no tests in /docs-audit; the review gate and the coverage figures are reported above)
   > - Project root: [the resolved documentation repository root]"
2. **Persist plugin feedback (automatic).** Invoke `Skill(skill: "workflows-core:reference", args: "feedback-emission emit-auto")` and call its `emit-auto` entry point (§6), passing the Lessons Learned report, `command: /docs-audit`, `key: null` (this run resolves no PRD or Epic key), `source: none`, and `plugin_version` (read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). No PRD dir ever resolves here, and `feedback-emission.md` §2 tier 2's documentation branch applies: the entry lands at `$SPECS_PATH/documentation/<docs-repo-slug>/dev-workflows/feedback/<date>.md`, where `<docs-repo-slug>` is the one-segment name `workflows-core:specs-repo-git` §2.1 defines for the resolved documentation repository — cited rather than re-derived here, because that section's staging rule admits exactly one segment and a second derivation is how the two drift (design D19). Under `specs_git: misrooted` (`workflows-core:specs-repo-git` §3.1) it is not written there: the entry stays in the run's output.
3. **Surface** the persisted path (or "no plugin-facing signal — nothing persisted") as this phase's only output.

ADDITIVE — this phase NEVER fails the run, NEVER commits, NEVER makes an external API call, and NEVER writes into the documentation repo, a code repo, or the current working directory, where it is not the specs repository.

---

## Phase 8 — Emit follow-up tasks

Terminal phase — runs AFTER Phases 6 and 7; NEVER interrupts an earlier phase. Invoke `Skill(skill: "workflows-core:reference", args: "followup-emission")` and execute its steps inline.

1. **Collect** the qualifying follow-ups: committing the backlog (only where one was written), a `source_repos[]` entry the operator excluded, a theme still unresolved after round 2, a backlog path a project `.gitignore` line ignores, a `[page-missing]` or `[surface-removed]` token this run added, a tutorial candidate Phase 4.5 left unminted for either of the two reasons it gives, and any deferred or overridden review finding from Phase 5.5.
2. **Filter** them with the reference's §6 qualifying predicate.
3. This run resolves **no PRD or Epic folder** — that reference's "no folder resolved" rung applies: report-only, kept in the Phase 6 report, with the one-line notice `⚠ No resolved folder — N follow-up(s) kept in this report only.`

ADDITIVE — this phase NEVER fails the run, NEVER commits, and NEVER writes into the documentation repo, a code repo, or the current working directory, where it is not the specs repository.

---

## Phase 9 — Session cost

Terminal phase — the final operational phase; runs after Phase 8 and NEVER interrupts an earlier phase. Records this command's token-cost contribution — through `emit-cost`, or, under `run_flags.skip_costs`, by advancing the checkpoint alone. **Cost ALWAYS runs once Phase 0 step 2 has resolved the documentation repository — unless `run_flags.skip_costs` (see below)** — on a completed run, on the Phase 0 step 8 Cancel, on a `NO_SURFACES` return, and on every one of this command's `DOCS_AUDIT_*` stops from step 2 onward, each of which routes itself here at its own site rather than relying on this sentence to be read from a phase it never reached. **Two kinds of run are the exception, and they are stated rather than left to be inferred** — Phase 0 step 1's three stops, and a Cancel at step 2's `resolve-docs-repo` choice: a rejected flag or flag value, or a ladder the operator abandoned, ends the run before any repository is resolved, so there is no target to file an entry against and a few tokens to attribute; the stop is printed and nothing is emitted.

**Under `run_flags.skip_costs`**, do not call `emit-cost` and do not load `cost-emission`: execute `skip-cost` (`Skill(skill: "workflows-core:reference", args: "run-flags skip-cost")`) instead, which advances the checkpoint and drops any deferred record, and surface `Session cost: skipped (--skip-costs)` (or `(WORKFLOWS_SKIP_COSTS)`). The resume-pointer write and the terminal `commit-artifacts` step below run unchanged either way.

Otherwise (not skipping), invoke `Skill(skill: "workflows-core:reference", args: "cost-emission emit-cost")` and call `emit-cost` with `command: /docs-audit`, `phase: docs-audit`, `role: dev` — a **fixed** pair (`workflows-core:cost-emission` §7), never `inferred`. Pass `key: null`, `source: none`, and `plugin_version` (read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). No PRD dir ever resolves here, and `cost-emission.md` §8 rung 2's documentation branch applies: the entry lands at `$SPECS_PATH/documentation/<docs-repo-slug>/dev-workflows/cost/<sid8>.md` rather than in the pending queue (design D19), `<docs-repo-slug>` being the same `workflows-core:specs-repo-git` §2.1 name Phase 7 used. Under `specs_git: misrooted` (`workflows-core:specs-repo-git` §3.1) it is not written there: the entry stays in the run's output. **Per docs repo, not one flat bucket** — a person documenting two products must still be able to answer what auditing each one cost — and the inner `dev-workflows/` names the *family*, not the plugin.

**Then write the resume pointer.** Invoke `Skill(skill: "workflows-core:reference", args: "session-hygiene")` §1. With no PRD dir, entry 2 of its **Location** ladder applies: skip the file, rely on the printed `### Next step`. This command is **not** on that section's *Skipped* list and does not belong there — that list exempts runs which do resolve a folder and still write no pointer, and this one never resolves a PRD folder at all, which the Location ladder already answers.

**Then commit session artifacts (terminal).** Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git commit-artifacts")` and execute its `commit-artifacts` entry point (§4) inline — the LAST action of the run. It stages ONLY the §2.1 bounded artifact paths inside `$SPECS_PATH` — here the documentation-run cost and feedback files above, under §2.1's `$SPECS_PATH/documentation/<docs-repo-slug>/…` shape — commits, and pushes per §4 step 5. It NEVER touches the documentation repo or a code repo; NEVER force-pushes; NEVER fails the run; and skips entirely when the run carries `specs_git: blocked` (§3.3 G0) or `specs_git: misrooted` (§3.1, or `specs-root-check`'s stop), re-emitting that notice. Print its §6 outcome line here, as the run's last output — prefixed `Specs repo:`, with any guard notice repeated in full.

---

## Invariants (always enforced)

- ALWAYS resolve the documentation repository via `resolve-docs-repo` (`${CLAUDE_PLUGIN_ROOT}/references/docs-workflow/repo-resolution.md` §1 — the **signal-positive** form) and report which rung answered; NEVER copy `/docs-workflows:docs-init`'s inverted ladder, which refuses the one directory this command needs
- ALWAYS strip `--audience` and `--threshold` together with the token after each before reading a positional token — the value is otherwise read as the docs-repo path
- ALWAYS write the backlog at `<top>/.dev-workflows/docs-backlog.yml`, where `<top>` is the resolved repository's git work-tree top level (`backlog-format.md` §6) — NEVER beside a content root, because one repository has one backlog however many sites it publishes
- NEVER write into a backlog whose `schema_version` this reader does not know; report the file and write nothing (`backlog-format.md` §1)
- NEVER overwrite an existing backlog on a run that carried no `--refresh` — ask, because that file holds picked candidates, corrected reasons and hand-added units nothing here could reconstruct
- ALWAYS dispatch `code-scanner` with all seven of `coverage-model.md` §2's surface kinds as `capability_themes[]`, plus a `context` — that agent refuses without one, and `docs-auditor` asserts it was asked about all seven
- ALWAYS treat a theme in `classification: error` as unresolved and NEVER as `absent`. Four classifications, one of which means "looked and found none"; an `error` folded into absence asserts the product lacks something nobody managed to look for
- ALWAYS name a theme still unresolved after §8.5's one seeded second round, in the handoff and in the report; NEVER flatten it into a gap — a gap asserts absence, an unresolved theme asserts only that the scan could not tell
- ALWAYS pass `existing_surfaces[]` to `docs-auditor` on a `--refresh`, and `existing_units[]` (each carrying its stored `priority_reason`) and `existing_tutorial_candidates[]` to `ia-planner` — without them a refresh re-mints surface ids and orphans every unit pointing at the old one, and `backlog-format.md` §8's id-collision, occupied-cell and preserve-the-human's-fields hard rules cannot be checked at all
- ALWAYS substitute `medium` for a `volatility: unknown` **at write time, never before Phase 4**, and ALWAYS name every surface it was substituted for in the report — `ia-planner` must see `unknown` so it ranks without churn-adapting and records that the measurement failed
- ALWAYS apply `priority_comparisons[]` with `backlog-format.md` §1's mechanical test — stored reason exactly equal to the derived reason means both fields take the new values, anything else means both stored values stand and the pair is reported. Skipping it makes a refresh unable to re-rank anything
- ALWAYS mint a picked tutorial candidate's unit here and never in `ia-planner`, once only, recording the new id on the candidate; NEVER mint one on a run whose `--audience` excludes `user`, and NEVER disturb `picked` to avoid the question
- NEVER delete a unit, for any reason. A surface that vanished gets `[surface-removed]` and a report line; a `page_path` that no longer resolves gets `[page-missing]`; deletion is a human's act (`backlog-format.md` §4)
- NEVER mark a unit `published` on a page carrying a `[NEEDS CLARIFICATION]` marker — that reconciliation lands the unit on `drafted` (`backlog-format.md` §3, `evidence-contract.md` §3)
- ALWAYS derive every `coverage` figure from the `units[]` table in the same run, over every unit whatever its audience — `--audience` filters what is minted, never what is counted
- ALWAYS report both `surface: null` counts — how many units carry no surface, and how many of those carry no `journey` either
- NEVER create a branch or a commit in the documentation repository; the backlog is left in the working tree for the operator, and the terminal `commit-artifacts` step is `$SPECS_PATH`'s alone
- NEVER force-add the backlog past a project `.gitignore` rule — report the path, the line and its file, write the file, and say it is not committable until that rule changes (`backlog-format.md` §6)
- ALWAYS dispatch `docs-audit-reviewer` over the written file at Opus (D17, D20 — no tiering by unit) unless `run_flags.enforced_model` is set (§10 enforces a model, and the dispatch then carries that id instead), and ALWAYS tell it which inputs were absent, so a degraded half is reported as unchecked rather than as a pass
- ALWAYS triage its findings (`workflows-core:finding-triage`) before applying anything; there is NO backlog fixer (D25) — the orchestrator applies survivors itself, bound by the patch gate, surfaces a survivor it cannot safely patch, and runs NO re-review
- NEVER dispatch `docs-grounder`, and NEVER parse `--docs` or `--no-docs`: none of `workflows-core:docs-grounding`'s **three** consumption modes applies — this command runs no grill (grill-rank), authors no prose (writer-attach), and has nothing downstream of a lead (lead-only), since a surface may be enumerated only from a scanner's `capability_map[]` or the specs inventory. Phase 5's reconcile opens the documentation repository directly and matches by `unit:` key, which is a read against a known set of ids and not a retrieval
- ALWAYS use `choices` arrays for a genuine decision point; 2–4 options, and NEVER author an "Other" option — the harness supplies the free-text escape itself. Where the candidate set is unbounded (Phase 0's repository listing), print every candidate as prose first and keep the array fixed-arity over the *disposition*, resolving a typed answer against the list just printed rather than parsing it (`workflows-core:epic-picker` *The cap*)
- ALWAYS run `specs-preflight` at Phase 0 and `commit-artifacts` as the last action (`workflows-core:specs-repo-git`) on every run that gets past Phase 0 step 2 — the runs that end before it are the two exceptions Phase 9 names — bounded to `$SPECS_PATH`'s artifact paths and to plugin-created branches, of which this family creates none; always `git -C "$SPECS_PATH"` and never a `cd`; never force-pushing; never failing the run
- NEVER write outside the resolved documentation repository's `.dev-workflows/docs-backlog.yml` and the profile's `source_repos[]` key, except for the bookkeeping paths inside `$SPECS_PATH`; NEVER write into a code repository, and NEVER into the current working directory, where it is neither that repository nor the specs repository
- ALWAYS reference this plugin's own bundled files with `${CLAUDE_PLUGIN_ROOT}`; every `workflows-core:<name>` citation is loaded through `Skill(skill: "workflows-core:reference", args: "<name>")`, never by path

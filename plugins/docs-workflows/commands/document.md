---
name: document
description: keyed feature-documentation workflow. Phase 0 preflight-discovers the docs repo + profile (in-repo → built-in example-docs default → on-demand /docs-profile) and the PRD's specs dir under /workspace. Reads a Product Requirements Document hierarchy from its PRD folder in the specs tree — the folder the address resolves to, or the one above it for an Epic address — summarises the diffs its implementation record names in parallel, synthesises product documentation, and gates on style-check and Opus doc review.
allowed-tools: Read Edit Write Bash Glob Grep Task Skill WebFetch
---

Generate product documentation for the resolved Product Requirements Document: $ARGUMENTS

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

Signature: one positional address — a key, or an `@<path>` naming a folder in the specs tree. Phase 5.5 resolves each write target against the content roots the resolved profile declares, and Phase 6.3 writes each page into the root that owns it.

`/document` (keyed mode) is the **keyed feature-documentation** workflow. Given a PRD address — or an Epic's, which scopes the repositories it resolves, the diff summaries and the documentation plan to that Epic — it reads the resolved PRD folder, resolves the implementation record's repo slugs to local clones, runs parallel diff summaries of the refs that record names, synthesises product documentation, runs style-check + Opus review gates, and writes the output into the docs repository Phase 0 step 2 resolves — the current working directory where it carries a docs signal, and otherwise `${DOCS_PATH:-/workspace/docs}`, a repository under `${REPOS_PATH:-/workspace}`, or cwd or a path you confirm: a run writes wherever that ladder answers, not wherever it was started (Phase 0 step 2, and step 4 for the profile).

For small one-off doc edits, use direct mode (below). For writing child Epic drafts from a PRD, use `/epics`. For release notes, use `/release-notes` — this command never writes release-notes / what's-new pages, because those are generated from the tracker by the docs team's automation.

Usage: `/document <KEY>|@<path> [--skip-costs] [--skip-feedback] [--enforce-model=<model>]` (keyed mode) or `/document [@<path-to-markdown-file>|<free text>] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]` (direct mode — the run flags may stand before or after the free text, never inside it).

---

## Mode detection

**Strip the run flags first.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS` before anything else reads a token: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its maintenance, cost and routing steps — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. **The strip makes its own address test, rather than waiting on the mode test below**: after the leading run of run-flag tokens is consumed, it tests the next token against `workflows-core:addressing` §1's key grammar and against `@<path>` naming a folder in the specs tree (`workflows-core:run-flags` §3 step 1). A hit gets the ordinary strip — run flags removed wherever they appear, the address left untouched. A miss gets the free-text rule: the leading region is a single `@<path>` token where the stripped argument opens with one and it is not such a folder (direct mode's own file argument, Phase 0 step 1), otherwise nothing of the command's own; the prose span begins there, kept exactly as typed even where it contains a flag name, and the usual trailing run of complete run-flag tokens is stripped at the very end either way. **The mode test below then re-reads the stripped result** to make its own, authoritative keyed/direct call — it never runs before this strip, and this strip never waits on it; every later step, the mode test included, parses only what this strip leaves.

`/document` has **two modes**, selected by the first argument token:

- **Keyed mode (Mode A)** — the first token is a **single positional address**: a `<KEY>` matching `workflows-core:addressing` §1's grammar, or an `@<path>` naming a folder in the specs tree. **On a `<KEY>`, `$SPECS_PATH` comes first:** if it is unset, stop naming it before resolving anything or running the preflight below (`choices: ["Set SPECS_PATH (enter the path)", "Cancel"]`, `workflows-core:escalation-rules` *Required path environment variable unset*) — a key is found only by searching the specs tree, so with no tree the `absent` stop below would name the wrong cause and offer a re-enter that cannot succeed. An `@<path>` address needs no specs tree and runs on, and direct mode is unaffected. `resolve-address` (§3) turns the address into a folder; `ambiguous` is a stop naming every match, and `misrooted` a stop with §3's `SPECS_PATH_INSIDE_TREE` message. **`status: absent` is a stop, not a folder to create** — it surfaces the `key dir not found` rule in `Skill(skill: "workflows-core:reference", args: "escalation-rules")` (`choices: ["Re-enter key", "Cancel"]`) and names what creates a folder this command reads — **all three creators, not one**: a `PRD-` folder comes from `/product-workflows:idea <KEY>` or `/product-workflows:create-prd <KEY>` on the idea route and from `/product-workflows:brd-split` on its parent BRD on the BRD route; an `EPIC-` folder comes from `/product-workflows:epics <PRD-ADDRESS>` and from no other command. Naming only `/create-prd` is wrong on the BRD route, where that command refuses the container above the slice, and wrong for an `EPIC-` address, which it never mints — the same list `/dev-workflows:ready`, `/docs-workflows:release-notes`, `/product-workflows:epics` and `/product-workflows:create-ard` each print in their own `absent` stops. It never falls through to direct mode: an address that resolved to nothing is a typo to correct, not a prose prompt to document. An address that resolves but leads to no `prd.md` the run can read is not this rule's: it takes one of Mode A Phase 0 step 1's named stops — `DOCUMENT_BRD_NOT_SLICED`, `DOCUMENT_FOLDER_NOT_PLACED` or `DOCUMENT_NO_PRD` — and so does one whose PRD folder carries no key, which takes `DOCUMENT_PRD_NO_KEY`.
- **Direct mode (Mode B)** — no positional address: a leading `@file` token, free-text prose, or a directory that is not in the specs tree, which Mode B handles via its existing "anything else" path.

**The mode test is the presence of an address**, which is what replaces the retired shared front-end's own mode return. Mode B is unchanged in every other respect — a direct-mode run is byte-identical to before.

**The run key set the specs-repo preflight below is handed** (`workflows-core:specs-repo-git` §3.2)
is fixed first, before either mode runs, reading only carrier frontmatter (`key:`, `kind:`) as §4
does, whatever file that is, and testing no file's presence. In Mode A it is the resolved `key`,
and, where `workflows-core:addressing` §4.1 places the resolved folder at Epic level — an `EPIC-` prefix, or with
no prefix a resolved `kind: epic` — also the key its parent's carrier asserts (§4), which is the
`<PRD>` Mode A Phase 0 step 1 carries. Without it, §3.5 would resolve a `prd/<PRD-KEY>-…` branch to
no key and switch away from it. A key that came back empty adds nothing. In Mode B there is no
address and the set is empty: a keyless run (§3.2).

**Specs-repo preflight** — with the run key set fixed in the paragraph above. Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git specs-preflight")` and execute its `specs-preflight` entry point (§3) inline: flush any leftover session
artifacts from an earlier run, retry an artifact commit that failed to push,
and settle the branch. This runs against `$SPECS_PATH` only — `git -C
"$SPECS_PATH"`, never a `cd`, so the code/docs repo this run is working
in is untouched (§1 rule 1). Prompt-free, and silent unless it acts, a guard fires, or §3.1 reports a misconfigured `$SPECS_PATH`. If a guard fires, emit its §5 notice;
if it returns `specs_git: blocked` (§3.3 G0) or `specs_git: misrooted` (§3.1), carry that flag for the whole
run — the terminal `commit-artifacts` step skips on it.

Echo the detected mode, then proceed to that mode's phases. The two modes share the same style pass and the same fixer — `docs-workflows:docs-style-checker`, which reports and never modifies a file, and `workflows-core:doc-fixer`, which applies what it reports; the two ship from different plugins and are dispatched by their qualified `subagent_type` everywhere below; only Keyed mode also runs `doc-reviewer` (each mode emits its own final report).

---

# Mode A — keyed documentation (address argument)

## Phase 0 — Load and dispatch

1. **Resolve the address.** Parse the single positional address from `$ARGUMENTS` — a `<KEY>`, or
   an `@<path>` naming a folder or a file inside one — and resolve it with `resolve-address` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3). Present and resolving → `mode: keyed`;
   absent from the argument list → `mode: direct`, and the rest of this phase's keyed steps are
   skipped. A `<KEY>` with `$SPECS_PATH` unset never reaches this step: Mode detection has already
   stopped on it. Carry the resolved `path`, `kind`, `key`, and the `specs` files found in that
   folder forward.

   **Place the folder, and carry the PRD folder and the focus.** An `EPIC-` address documents one
   Epic, and its folder holds no `prd.md`: the PRD it belongs to is the folder above it. So place the
   resolved folder at a level as `workflows-core:addressing` §4.1 does — by its prefix, never by the
   kind it asserts, which on a BRD-route slice is `brd` — taking its container test first, and carry
   forward:
   - `<PRD>` — the **PRD folder's** `key`, read off its carrier (§4): the resolved folder's own where
     §4.1 places it at PRD level, its parent's where §4.1 places it at Epic level. That folder is
     **the PRD folder** — what every later phase of this mode means by *the resolved PRD folder* —
     and Phase 3 reads it.
   - `focus_key` — the resolved folder's `key` where §4.1 places it at Epic level, `null` where it
     places it at PRD level. Phase 3 derives `focus_items` from it.

   **An address that resolves but leads to no `prd.md` the run can read stops here, and so does
   one whose PRD folder carries no key — before anything else in this phase runs, and before Phase 1
   asks anything — each with a stop of its own.** None of these is the `key dir not found` rule: the key resolved, so re-entering it cannot help. A
   PRD-level or Epic-level folder whose PRD folder holds a `prd.md` and carries a key takes none of
   them and runs on as above. **Each of these stops is a user halt** — it reports the operator's own
   tree, not a capability this plugin lacks — **so `emit-block` does not fire** on any of them.
   - **A BRD container** — the folder §4.1's container test places — holds no PRD: a BRD's PRDs are
     authored in its `PRD-` slices. List the slices under it by the positive test §4.1 names, each
     immediate subdirectory carrying a `brd-link.md` whose `parent:` names the container. A slice
     is listed by the `key` its own carrier asserts (§4); one whose carrier asserts none is listed by
     its `@<path>` with `(no key — give it a carrier, workflows-core:addressing §5)` and is not
     enterable. Stop:
     `DOCUMENT_BRD_NOT_SLICED: <KEY> resolves to a BRD container at <path>, which holds no PRD — its PRDs are authored in its PRD- slices: <each slice key, found by workflows-core:addressing §4.1's positive test>.`
     `choices: ["Enter a slice key", "Cancel"]`. **The key the operator types — after "Enter a slice
     key", or in the harness's free-text option — is resolved against the keyed slices this stop
     listed, and never parsed or resolved on its own.** An answer equal to one listed key
     re-enters step 1's address resolution with that slice's `@<path>`, which the listing already
     holds, so no key is searched for again and `$SPECS_PATH` is not needed for it.
     **Re-entering fixes the run key set afresh, for the slice** — its key, as *Mode detection* fixes it for
     any address — **and runs the specs-repo preflight again with it before step 1's stops are
     tested.** The preflight is prompt-free and idempotent, and the container's key set is the wrong
     one for the slice: it can have kept the run on a plugin branch named for the container, which
     the slice's key set switches away from (`workflows-core:specs-repo-git` §3.5 B4), exactly as a
     direct run on the slice would. A branch the first preflight's B4 left, which `branch-key`
     now resolves to the slice's key, is switched back to first, as §3.5's *A re-run in the same
     run switches back first* rule fixes — so the slice is read on the branch a direct run's B3
     would have kept. An answer equal
     to none — a keyless slice's path among them — re-presents this stop, saying the answer named
     none of the enterable slices. "Cancel" ends the run. **Where the test finds no slice, there is
     nothing to enter, so no `choices:` array is shown** and the stop is a plain one: its message
     ends at `…authored in its PRD- slices.`, and `It has no slice yet: '/product-workflows:brd-split <KEY> "<how to cut it>"' carves one where this BRD's ledger leaves a row unallocated; where it leaves none, coverage-ledger-format.md §5 names the repairs.` follows it.
   - **A folder §4.1 places at no level** is not guessed at. Stop, a plain stop with no `choices:`,
     because nothing the run can offer fixes the folder:
     `DOCUMENT_FOLDER_NOT_PLACED: <KEY> resolves to <path>, which carries <what it carries> and nothing workflows-core:addressing §4.1 places at any level. <the remedy>`
     `<what it carries>` names its top-level files and what `kind:` and `key:` each asserts — a
     `prd.md` asserting no `kind:` among them, where it holds one. `<the remedy>` is to give the
     folder a carrier (`workflows-core:addressing` §5) and, where it holds an `idea.md` and no
     `prd.md`, to run `/product-workflows:create-prd <KEY>`, whose `prd.md` places it (§4.1). On an
     `@<path>` to a folder with no carrier, §3 returns no key: `<KEY>` in the message is that
     `@<path>`, and the remedy's `<KEY>` is left for the operator to supply (§3 step 1).
   - **A PRD folder with no key.** Where §4.1 places the PRD folder at PRD level but `<PRD>` came
     back empty — an `@<path>` to a folder with no carrier (§3 step 1), such as a slice whose
     `brd-link.md` asserts no `key:`, or an Epic whose PRD folder has none — stop, a plain stop with
     no `choices:`, naming that folder and the two ways on §3 step 1 gives:
     `DOCUMENT_PRD_NO_KEY: the PRD folder <path> asserts no key, and /document needs one — it is one of the commit scan's tokens (Phase 3). Give it a carrier (workflows-core:addressing §5)<or-key>.`
     `<or-key>` is `, or address it by its <KEY>` where the folder's name is unprefixed, and empty
     where it carries a kind prefix. This command needs the key:
     it is one of the commit scan's tokens (Phase 3).
   - **A PRD folder holding no `prd.md`.** Where §4.1 places the resolved folder at PRD or Epic
     level, test the PRD folder for a `prd.md`. The test is the file's presence: a `prd.md` asserting
     no `kind: prd` is read in Phase 3, not refused. **A `prd.md` that is present and cannot be read
     is no PRD the run can read either**: stop on this same code, a plain stop naming no command and
     taking none of the remedies below —
     `DOCUMENT_NO_PRD: <KEY>'s folder <path> holds a prd.md this run cannot read (<error>). Make it readable, then re-run.`
     Where there is none, stop — a plain stop with no `choices:`:
     `DOCUMENT_NO_PRD: <KEY>'s folder <path> holds no prd.md. <the remedy>`
     `<KEY>` is `<PRD>` and `<path>` the PRD folder, on an Epic-level run as on a PRD-level one.
     `<the remedy>` turns on what that folder carries, because `/product-workflows:create-prd`
     refuses a BRD-route slice in three states, as `/product-workflows:epics`' `EPICS_NO_PRD`
     remedy table also records:
     - **No `brd-link.md`** — an idea-route PRD folder: `Run /product-workflows:create-prd <KEY> first.`
     - **A `brd-link.md`** — a BRD-route slice. Read the rows its `claims:` names (its gate set) and
       their dispositions from the slice's own `coverage-ledger.md`, never from a `ledger:` line,
       and take the first row that applies:
       - `coverage-ledger.md` missing, or present and unreadable, while `claims:` names rows: name no
         command. Report `<path>/coverage-ledger.md` as missing, or as unreadable with the read
         error, and say `/product-workflows:brd-split` wrote it with
         the slice.
       - A gate-set row still `unallocated`:
         `Allocate it with /product-workflows:brd-split <KEY>, then run /product-workflows:create-prd <KEY>.`
         Say beside it that `/brd-split`'s own Phase 0 stops, naming `/product-workflows:prd-ground <KEY>`,
         where this slice's grounding findings do not each carry a verifier verdict.
       - No gate-set row `covered-here`, and the gate set **empty**: a standing empty child. Name
         `/product-workflows:brd-split <PARENT-KEY>`, which keeps or removes it, `<PARENT-KEY>` read
         off the same `brd-link.md`'s `parent:` — with `"<how to cut it>"` where the parent's ledger
         still holds an `unallocated` row, bare where it holds none, and neither form, reporting the
         parent's ledger by path, where it cannot be read.
       - No gate-set row `covered-here`, and the gate set **non-empty**: name no command.
         `This slice holds no PRD of its own — <what each claimed row resolved to> — so there is nothing here to document.`
       - Otherwise: `Run /product-workflows:create-prd <KEY> first.`

     **Where the PRD folder is above an Epic and §4.1 does not place it at PRD level** — an Epic
     folder at the top of `specifications/`, or under a BRD container or any other folder that is
     not PRD-level — no PRD folder stands above the Epic, and the stop reads instead:
     `DOCUMENT_NO_PRD: <focus_key> resolves to an Epic folder at <path> with no PRD folder above it. Move the Epic folder into its PRD folder (git mv) and re-run.`
     — `<path>` here being the Epic folder's own.

2. **Resolve the docs repo (cwd-preferred).** This command writes feature documentation into a product docs repository; running it outside such a repository is almost always a mistake. The **docs signals** checked throughout this step are:
   - `package.json` with any script matching `*:start`, `*:build`, `*:lint`, `docs:*`, or
   - any of `.docstack/`, `mkdocs.yml`, `docusaurus.config.js`, `antora.yml`, a Vale configuration file under any of the five names Vale reads (`.vale`, `_vale`, `vale.ini`, `.vale.ini`, `_vale.ini` — `toolchain-preflight.md` §2 source 2), `DOCUMENTATION-GUIDELINES.md`, or
   - a `_snippets/` directory at any level under the repo root.

   Resolve `docs_repo_path` in this order:

   - **(a) cwd with signals (the cwd-preferred rung).** Run `git rev-parse --show-toplevel` from cwd to resolve the git root. If it succeeds **and** ≥ 1 docs signal is present there → `docs_repo_path` = that git root and proceed silently. This keeps every downstream phase that assumes cwd correct.
   - **(a.5) `$DOCS_PATH` hint.** Else, resolve `${DOCS_PATH:-/workspace/docs}`. If it exists and carries **≥ 1 docs signal** (the same signal set as (a)) **or** an in-repo `.dev-workflows/docs-profile.yml`, set `docs_repo_path` = that path and proceed. In an AI container the docs clone is mounted here, so this is the common fast path when cwd carries no docs signals. The check is signal-based, never keyed to a particular repository's name or file layout.
   - **(b) Search for a docs repo.** Else, look under `${REPOS_PATH:-/workspace}` (single dir or colon-separated list) for a git root that carries an in-repo `.dev-workflows/docs-profile.yml` **or** ≥ 1 docs signal from (a)'s set. If exactly one matches → `docs_repo_path` = that path. If several match, list them and ask which to use (`choices` array of 2–4, a profiled repo recommended first; where more repos match than fit, list them all as prose and let the array carry the three likeliest plus one option naming the rest, per `workflows-core:next-phase-offer`'s overflow rule). Discovery is by signal, never by repository name — no repo name is special-cased.
   - **(c) Ask.** Else, ask:
     ```
     "No product-docs-repo signals in this working tree and no docs repo found under ${REPOS_PATH:-/workspace}. The signals I checked in cwd:
      - package.json scripts matching *:start, *:build, *:lint, docs:*
      - .docstack/, mkdocs.yml, docusaurus.config.js, antora.yml, a Vale configuration (.vale, _vale, vale.ini, .vale.ini or _vale.ini), DOCUMENTATION-GUIDELINES.md
      - any _snippets/ directory under the repo root
      Where should I write the documentation?"
     choices: ["Use cwd anyway — I confirm this is a docs repo (Recommended)", "Enter the docs repo path", "Cancel — switch to a docs repo first"]
     ```
     "Use cwd anyway" sets `docs_repo_path` = the git root of cwd (or cwd itself if not a git tree) and carries the user's confirmation forward. "Enter the docs repo path" takes a free-text absolute path and validates it exists.

   **Then take it to its top level.** Record the directory the rung answered with as `docs_repo_resolved`, and set `docs_repo_path` to its git work-tree top level — `git -C <docs_repo_resolved> rev-parse --show-toplevel`, or `docs_repo_resolved` itself where it is in no git work tree. That top level is where the profile lives, where every path it records is rooted and where every command it records runs (`${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/docs-profile-schema.md`, **Where the profile lives**), so every later use of `docs_repo_path` in this command means it. Rungs (a) and (b), and "Use cwd anyway", already answer with a top level; `$DOCS_PATH` at (a.5) and a path entered at (c) can name a site below one — a monorepo's `website/` — whose profile step 4 would otherwise look for in the wrong place. `docs_repo_resolved` is kept for what the site's own directory decides: step 4(c) hands it to inline profiling, step 6's `.obsidian/` walk starts from it, and step 7's preflight and Phase 6.4's style check look there, and in each directory above it, before the top level, for the configuration a site keeps beside itself or above it.

   **Confirm writeable.** Once `docs_repo_path` is resolved, run `test -w <docs_repo_path>`. If it fails, stop with the named error `REPO_NOT_WRITEABLE: <docs_repo_path> is not writeable.`

3. **Does the built-in default profile apply?** Set `is_known_docs_repo` = `true` only when the resolved `docs_repo_path` matches the **built-in default profile's own layout** — it contains every `spaces[].content_root` and `snippet_root` that profile declares. This is a narrow test for "this repo is shaped like the bundled example", not a test for "this is a docs repo"; a real repo almost always answers `false` here and is served by its own in-repo profile at step 4(a), or by on-demand profiling at 4(c). Directory name is **never** a factor.

4. **Resolve the profile** (record `profile_source`). The profile steers all later phases' conventions. Resolve in this order:
   - **(a) In-repo profile →** `in-repo`. If `<docs_repo_path>/.dev-workflows/docs-profile.yml` exists — the profile's one home, since step 2 took `docs_repo_path` to the top level — load it. `profile_source: in-repo`.
   - **(b) Built-in default profile →** `built-in`. Else, if `is_known_docs_repo`, load `${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/docs-profile.default.yml`. `profile_source: built-in`.
   - **(c) Custom repo, no profile →** `generated`. Else (a custom docs repo with no profile), run **inline on-demand profiling**: invoke the `/docs-profile` flow against `docs_repo_resolved` (Skill tool, `skill: "docs-workflows:docs-profile"`, with `docs_repo_resolved --inline` as its arguments — the `--inline` token tells profiling to skip its branch-naming prompt and standalone PR-draft handoff, since this command owns the single branch + PR draft) and wait for it to return. **This run's `run_flags` — resolved once, in the shared `## Mode detection` section above — carry straight into that continuation**: `/docs-profile --inline` runs in this same session, on the record already stripped and resolved there, and does not re-invoke `strip-run-flags` on the synthetic `docs_repo_resolved --inline` argument this step constructs, which never carries a run-flag token of its own; a `run_flags.enforced_model` this run carries pins its Phase 2 detection and Phase 3 synthesis dispatches too. Pass the directory step 2's rung answered with, not its top level: profiling's Phase 0 step 3 tests the directory it is handed and that directory's top level for a docs signal, so handed the top level of a monorepo whose site sits in `docs/` it tests one signal-less directory twice and asks "Profile it anyway?" about a repository this command has just found by its signal. It resolves the same top level (its Phase 0 step 2) and, finding no profile there — (a) has just looked — bootstraps one: it cuts its branch, writes `<docs_repo_path>/.dev-workflows/docs-profile.yml`, commits it, and hands back that branch as `profile_branch` and that commit as `profile_commit` (its Phase 6). Load the file, and record `profile_source: generated` with both values — Phase 6.2 renames `profile_branch` and Phase 8.5 squashes onto `profile_commit`. It also hands back two lists, `fixed_port_servers` and `server_command_defects`, the lines its standalone report would carry: print both to the operator now, as prose under a `Profile notes:` line, before the run goes on, and carry them into Phase 9's `### Assumptions & limitations`. Each is `none` where no server qualifies, and then one line says so. If the user cancels profiling (it produces no profile), stop with the named error `PROFILE_REQUIRED: a docs-profile is required to write into a custom docs repo; run /docs-workflows:docs-profile or switch to a profiled repo.` Where profiling stops on a named error of its own instead — `DOCS_PROFILE_BOOTSTRAP_BRANCH_EXISTS`, which it raises on a bootstrap branch an earlier run left behind — stop with that error as it stands, since it names what to fix.

     **Where profiling hands back no commit** — it made none, as its refresh does when answered "Keep existing, write nothing" or when it finds nothing to change — it cut no branch either. (a) and profiling look for the profile in the same place, so profiling starts from none here and that refresh does not arise; should profiling hand back no commit anyway and leave a profile at `<docs_repo_path>/.dev-workflows/docs-profile.yml`, load it and record `profile_source: in-repo`, never `generated`. The two lists above are handed back here too, and shown the same way, since the profile this run loads is the final one either way. The in-repo base guard below then tests whether that profile is on the base, and Phase 6.2 takes its normal case: its inline-profiling case renames `profile_branch`, a branch this run did not cut, and Phase 8.5 has no `profile_commit` to squash onto.

     **A stop after inline profiling committed names what it leaves behind.** Where profiling handed
     back a `profile_commit`, the docs repository is now on `profile_branch`, holding one commit — the
     generated profile — that is on no other branch and pushed nowhere, and nothing in this command
     switches back, merges, pushes or deletes it before Phase 6.2 renames that branch into the run's
     docs branch. So **every stop and every Cancel from here until Phase 6.2's rename** — step 7's
     `TOOLCHAIN_UNAVAILABLE`, a Cancel at any Phase 1, 1.5 or 2 prompt (Phase 1.5's relaunch
     included, which ends this run), every stop in Phases 3 to 6.1, and a Cancel at Phase 6.2's
     step 2 clean-tree or step 4 branch-name prompt, both of which come before step 5 renames the
     branch — ends, after its own message,
     with this notice in the family's four-part form (`workflows-core:specs-repo-git` §5), as the
     run's last printed output. `<base>` is resolved at the stop exactly as the in-repo guard below
     resolves it — the branch Phase 6.2 would have cut from, and the one profiling cut from:

     ```
     Docs repo left on a branch: <docs_repo_path> is on <profile_branch>, whose commit <profile_commit> (the generated .dev-workflows/docs-profile.yml) is on no other branch and pushed nowhere.
     Not done: this run did not switch back to <base>, and did not merge, push or delete <profile_branch>.
     To resolve: git -C <docs_repo_path> switch <base>   — then keep the profile by merging <profile_branch> into <base> (pushing it for review keeps the branch, and the next inline-profiling run stops on it until it is merged or deleted), or drop it with: git -C <docs_repo_path> branch -D <profile_branch>
     If ignored: the next /document run that profiles this repository inline stops with DOCS_PROFILE_BOOTSTRAP_BRANCH_EXISTS until <profile_branch> is gone.
     ```

     A run whose profiling handed back no commit cut no branch, and prints no such notice.

   Hold the loaded profile for later phases.

   **In-repo-profile-not-on-base guard.** When `profile_source: in-repo`, confirm the profile is committed on the base branch before relying on a docs branch cut from it. Resolve `<base>` exactly as Phase 6.2 step 1 does — `workflows-core:read-only-repos` §3's chain run against `<docs_repo_path>`, its `git -C <docs_repo_path> remote set-head origin --auto` retry where rung 1 fails, and its local fallback where the chain is exhausted — so the base this guard reads is the base Phase 6.2 cuts from. Step 2 has already confirmed the repository writable, which that retry needs: without it, a clone whose `origin/HEAD` was never set can read `origin/main` here while Phase 6.2's retry finds the remote's default is `develop`. Then take the **ref** that stands for `<base>` — `origin/<base>` where the chain found one, or, where step 1 falls back to a local branch, that branch itself: `<base>`, or HEAD where step 1 would switch nothing — and run `git -C <docs_repo_path> cat-file -e <base-ref>:.dev-workflows/docs-profile.yml`. This check is a read, so it takes the ref rather than the name (§3's **A switch takes the name**): Phase 6.2 pulls `<base>` up to `origin/<base>` before it cuts the docs branch, and this guard runs before that pull, when the local `<base>` may not yet hold a profile merged upstream:
   - **exit 0 (present on base)** → proceed (the common case — the profile was merged earlier).
   - **non-zero (absent on base)** → the profile is only in the working tree / on an unmerged branch, so the docs branch Phase 6.2 cuts from `<base>` will not include it. Warn and ask:
     ```
     choices: ["Proceed — the run uses the in-memory profile; I'll merge the profile PR separately", "Cancel — merge the profile PR first, then re-run"]
     ```
   Skip this check for `profile_source: built-in` (no profile file) and `generated` (the inline profiling branch is adopted by Phase 6.2, so the profile rides the single docs branch — a base check would false-fire).

5. **Specs (additive).** Use the `specs` files step 1 found in the resolved
   folder. `specs: []` is fine —
   specs are additive context for `/document`; proceed without prompting. For
   the downstream phases that scan or cite a single specs location (the Phase 5.6
   image scan, the Phase 5.7 `doc-planner` dispatch, and the Phase 5.8 three-way
   analysis), also record `specs_dir` = the directory
   containing the resolved `specs` (their common parent — e.g. the
   `$SPECS_PATH/…/<KEY>…/` folder, or the directory they were found in), or
   `none` when `specs` is empty.

6. **Classify write context** for later branch/write decisions — computed against the resolved `docs_repo_path` (not necessarily cwd). Walk up from `docs_repo_resolved` — the directory step 2's rung answered with, at or below `docs_repo_path` — looking for `.obsidian/`; if found, context = `obsidian`. Else if `git -C <docs_repo_path> rev-parse --show-toplevel` succeeds AND at least one docs signal from step 2 is present — or an in-repo `.dev-workflows/docs-profile.yml`, which step 2's rungs (a.5) and (b) accept as a docs repository in a signal's place — context = `docs_repo`. Else if it succeeds with neither, context = `non_docs_repo` (step 2 has already asked the user; their confirmation promotes this to `docs_repo` behaviour). Counting the profile here is what keeps that parenthetical true: a repo whose only marker is its profile is adopted at (a.5) or (b) without the question being asked, so a classification that ignored the profile would leave it a `non_docs_repo` whose Phase 6.3 row assumes a confirmation that was never asked for. Else context = `plain_dir`. In a normal run, Phase 0's docs-repo resolution (steps 2–3) yields a real docs repo (`docs_repo`) or a user-confirmed `non_docs_repo`; `obsidian` and `plain_dir` are **defensive guards** (they forbid branch/commit) rather than expected write targets.

   Record the resolved context — it drives Phase 6.2 (branch setup) and Phase 6.3 write rules. When `docs_repo_path` differs from cwd, record **both** and note that Phase 6.3 consumes `docs_repo_path`, not cwd, for every write.

7. **Toolchain preflight.** Execute `${CLAUDE_PLUGIN_ROOT}/references/toolchain-preflight.md` against
   the resolved `docs_repo_path` and the profile loaded in step 4 — with `docs_repo_resolved` as the
   site directory its source 2 also checks, where step 2 resolved one below the top level. Derive
   the required set from all three sources (profile commands including `commands.per_space` and
   `builds[]`, together with `bash` and `curl`, and off Linux `ps`, which the smoke check runs
   (`render-verification.md` §2), wherever the profile records a dev server; repo config signals;
   the repo's documented `Prerequisites`), check each, and build the `toolchain` block.

   Initialize the run's `gate_ledger` (schema:
   `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` §3) and append its first row:

   ```yaml
   gate_ledger:
     - gate: toolchain_preflight
       phase: "0"
       outcome: RAN
       mechanism: the derived required set's checks, per toolchain-preflight.md §2–§3
       findings: <count of tools with status: missing>
   ```

   - **Every required tool present** → record the row, contribute one line to the Readiness table, and
     proceed. Do NOT prompt.
   - **One or more missing** → present the `toolchain-preflight.md` §5 report and its choice list
     **verbatim** (the "Choice lists are presented verbatim" rule in
     `workflows-core:escalation-rules` binds this prompt — `(Recommended)` stays
     on "Cancel"). On "Cancel", stop with the named error
     `TOOLCHAIN_UNAVAILABLE: <comma-separated missing tools> not available in this environment.` — followed,
     where step 4(c) committed a generated profile, by that step's left-on-a-branch notice. On
     "Continue anyway", pre-seed the affected gates' rows per `toolchain-preflight.md` §5 with the
     user's choice quoted verbatim in `user_decision`, and proceed.

   When the write context resolved in step 6 is `obsidian` or `plain_dir`, the build and render
   gates have no precondition to meet — do not name them in the consequence line. Phase 6.5 records
   their `NOT_APPLICABLE` rows before its own run-condition, so they are present even though that
   phase does not execute.

### Readiness

Before clarification, show a readiness table summarizing what Phase 0 resolved:

| Item | Resolved |
|---|---|
| Address | the resolved folder[ — an Epic folder, whose PRD folder is the one above it] |
| Docs repo | `<docs_repo_path>` (`is_known_docs_repo`: yes/no)[ — the top level of `<docs_repo_resolved>`] — write context `<obsidian \| docs_repo \| non_docs_repo \| plain_dir>` |
| Profile | `profile_source`: `<in-repo \| built-in \| generated>` |
| Toolchain | `<all required tools present>` OR `<N missing: vale, pnpm — user chose to continue>`; writing into `<docs_repo_path>`[ (cwd is `<cwd>`)] |
| Specs | `<specs_dir>` or `none` |
| Code repos | resolved later in Phase 4 (slug→clone match under `$REPOS_PATH`) |

All discovery defaults to `/workspace` (`${REPOS_PATH:-/workspace}`); on a host, or when a path is missing, the command asks rather than guessing.

---

## Phase 1 — Clarification

**Rule: Ask, don't guess. This rule is absolute.**

Group questions where possible; use `choices` arrays; 2–4 options, and never author an "Other" option — the harness supplies the free-text escape itself (`workflows-core:escalation-rules` §0).

Every **Cancel** below stops the run; where Phase 0 step 4(c) committed a generated profile, it ends with that step's left-on-a-branch notice.

Ask about:

- **Output filename / sub-path under the resolved `docs_repo_path`** (Phase 0) (default: `<KEY>-<slug>.md`; the `doc-location-finder` in Phase 5.5 may override this per target).
- **Repo refresh policy**:
  ```
  choices: ["fetch only (Recommended)", "fetch + pull default branch", "no refresh — resolve refs from local objects only; a ref not yet fetched will not resolve, and a dirty clone stops blocking"]
  ```
  The `fetch only` default matches the `diff-summarizer` default (`refresh.fetch: true, refresh.pull: false`) — the diffs of refs the implementation record already named don't need the current branch tip, and pulling risks moving HEAD away from the commit we want to reach.
- **Repos search base (`$REPOS_PATH`)**. Read `${REPOS_PATH:-/workspace}` (the container mounts every repo under `/workspace`). `$REPOS_PATH` may be a single directory or a colon-separated list. Ask:
  ```
  choices: ["Use $REPOS_PATH (default /workspace) (Recommended)", "Use a different path (you'll be prompted)", "Cancel"]
  ```
  If "different path", take free-text input (single dir or colon-separated list) and validate that at least one directory exists under it. Record the resolved value as `$REPOS_PATH`. Individual clones are located in Phase 4 by matching their `git remote` against each in-scope `repo` slug the implementation record and the commit scan named — not by assuming a `<base>/<slug>` directory name.
- **Screenshots** — this question seeds the **add-list** only; it never skips Phase 5.6. The candidate list itself is built later in **Phase 5.6** (by which point `specs_dir`, the folder read `attachments[]`, and the resolved repos are all available), and Phase 5.6 **always** runs — it also reviews the images already on the pages this run is about to edit, regardless of this answer:
  ```
  choices: ["Yes — I have new screenshots to add (you'll pick the sources in Phase 5.6) (Recommended)", "No new screenshots", "Cancel"]
  ```
  Record the answer as `new_images_wanted` (true/false). When `false`, Phase 5.6 skips its **add** list only and still reviews existing images on the edited pages. The downstream `doc-planner` (Phase 5.7) detects the repo's `image_policy` and decides per screenshot whether the writer will copy it locally or stage it for manual upload — except where the policy is `ambiguous`, which Phase 5.7's **Ambiguous image policy** step settles with you — or, for a target the planner's one re-invocation newly returns `ambiguous`, Phase 6.3, with the same question.

  **Resolve `<screenshot_staging_dir>`.** No longer gated on `new_images_wanted`: Phase 5.6 always runs and its existing-image review can need a durable location for a replacement source regardless of this answer, so `<project_dir>` (set below) must be resolved on every run, not only an add-list one. **This unconditional resolution is deliberate and stays**, including the "Not found" prompt it can raise on a run that turns out to have no image work at all: Phase 1 runs long before `write_targets` exist, so any narrower precondition ("only when this run will touch images") is undecidable here. The occasional needless prompt is the accepted cost of closing a container-restart data-loss gap — do not re-gate this on `new_images_wanted` or on a guess about image work. For the `cdn_upload_required` case the staged copies must live somewhere that survives a container restart — a host-mounted directory the operator names survives it, the docs repo (often a docker repo-volume) and `/tmp` are not. Use the resolved PRD folder:
  ```bash
  the resolved PRD folder
  ```
  - **Found** → record the matched folder as `<project_dir>` (the project-folder root — reused as an image source in Phase 5.6), and set `<screenshot_staging_dir>` to that project folder's screenshot subfolder, `Doc screenshots/` (created on first write). An existing `Attachments/` subdirectory is not a candidate: the folder's `attachments/` holds only the text and markdown sources a run vendored (`workflows-core:addressing` §2, *Reserved subdirectory names*), and on a case-insensitive filesystem the two names are one directory.
  - **Not found** (e.g. a ticket whose project has no project folder) → `<project_dir>` is null (Phase 5.6's project-folder scan then contributes nothing); ask:
    ```
    choices: ["Enter an absolute staging directory (you'll be prompted)", "Skip — only needed if the docs repo turns out to be cdn_upload_required", "Cancel"]
    ```
    Reject `/tmp` and any path inside the docs repo. Record the result as `<screenshot_staging_dir>` (or null if skipped).

Also display (for user context):
- Resolved cwd absolute path
- Write context (`obsidian` / `docs_repo` / `non_docs_repo` / `plain_dir`)
- Whether branching will happen (only when context is `docs_repo` — confirmed at plan approval)
- Resolved `$REPOS_PATH`
- The resolved address and folder

---

## Phase 1.5 — Classify

Invoke the `model-routing` skill (Skill tool, `skill: "workflows-core:model-routing"`) to load the classification rules, then classify the task as exactly one of: `SIMPLE`, `MODERATE`, `SIGNIFICANT`, or `HIGH-RISK`. keyed feature docs are typically **SIGNIFICANT** (large blast radius if wrong — published documentation). State the classification and a one-sentence reason.

SIGNIFICANT → no separate Opus **risk-planner** for the high-level plan (the PRD folder + diff summaries *are* the plan), **but `doc-planner` (Phase 5.7) is pinned to the §2 Opus reasoning chain**; the `doc-reviewer` gate (Opus) is mandatory.

**Resolve the per-step routing.** Invoke `Skill(skill: "workflows-core:reference", args: "model-routing/classification")` and, following its §9, record a `model_routing` block (reusing the §4 field names) resolving each model against the fallback chains:

```yaml
model_routing:
  classification: SIGNIFICANT
  reason: <one-line>
  current_model: <the model this orchestrator is running under>   # = the inline writer + Phase 5.8 framing
  enforced_model: <run_flags.enforced_model, or omit>   # §10: when set, every dispatched-step *_model below equals it (inline authoring_model / implementation_model keep the session model) and routing: bypassed
  defect_model: <§2.1 Sonnet chain — only under --skip-feedback; under §10, run_flags.enforced_model>
  detection_model: <§2.1 mid-tier Sonnet chain: claude-sonnet-5-5, fallback claude-sonnet-5/4-6/4-5>
  planning_model:  <§2 powerful chain: claude-opus-5-5 … fallback Sonnet per §2>   # doc-planner (5.7)
  review_model:    <§2 powerful chain>     # doc-reviewer (frontmatter-pinned; recorded here, no override added unless §10 enforces a model)
  implementation_model: <= planning_model>  # the doc-writer subagent (Phase 6.3) — now a delegated, Opus-pinned writer
  fixes_model: <= detection_model>         # doc-fixer (6.4 / 7) runs on the detection chain
  opus_available: <true if a §2 Opus model resolved, else false>
  notes: <any §2 / §2.1 fallback or degradation>
```

Each subagent dispatch below cites which chain it uses (the §9 role→chain map): `doc-planner` → `planning_model`; the folder read, `diff-summarizer`, `doc-location-finder`, `docs-style-checker`, `doc-fixer`, and the Phase 8 maintenance agents → `detection_model`; `doc-reviewer` keeps its own frontmatter Opus pin (recorded as `review_model`, no override added unless §10 enforces a model).

**Orchestration advisory (window-focused).** `doc-planner` (5.7) and `doc-writer` (6.3) run on the §2 Opus chain regardless of session; only coordination + the interactive gates (5.8 decision, 6.1) run on `current_model`. **Unless `run_flags.enforced_model` is set (`workflows-core:model-routing/classification` §10 — then neither the relaunch bullet nor the degradation bullet below fires: `planning_model`, `review_model` and `implementation_model` already carry the enforced id, per this phase's `model_routing` block, and §10 suppresses this relaunch advisory alongside its own degradation notice):**

- **`current_model` is on the §2 chain** → no advisory.
- **`current_model` is NOT on the §2 chain and `opus_available: true`** → the heavy synthesis + writing are already on Opus; the residual risk is the orchestrator's **context window** on a **large multi-repo ticket**. Offer relaunch **only** on such a ticket — that condition gates the prompt, so once the list is shown the recommendation holds unconditionally (per the `(Recommended)`-marker rule in `workflows-core:escalation-rules`):
  ```
  choices: ["Relaunch /docs-workflows:document under Opus — I'll restart (Recommended)", "Proceed on <current_model>", "Cancel"]
  ```
  Otherwise proceed without prompting. The relaunch and **Cancel** both end this run, and where Phase 0 step 4(c) committed a generated profile, each ends with that step's left-on-a-branch notice.
- **`current_model` is NOT on the §2 chain and `opus_available: false`** → `planning_model`, `review_model`, and the **doc-writer** all fall to the Sonnet floor; record the degradation in `notes` and the Phase 9 report; proceed.

---

## Phase 2 — Plan + approval

Present a concise plan:

- The resolved address and the folder it resolved to
- Output filename / path under the resolved `docs_repo_path` (from Phase 1)
- `$REPOS_PATH` and the slug→clone resolution for the repos that will be examined (inferred from the folder read output in Phase 3; if Phase 3 hasn't run yet, list "TBD — resolved after the folder read")
- Parallelism plan (up to 4 `diff-summarizer` instances per batch; up to 4 repos per Agent message)
- Write context + whether branching will happen
- Screenshots: `new_images_wanted` (yes/no, from Phase 1). Phase 5.6 always runs: when yes, its add-list candidates are gathered and confirmed there (specs scan + folder `attachments[]` + manual paths) — list "candidates resolved in Phase 5.6"; either way, Phase 5.6 also reviews the images already on the edited pages for staleness.

Ask:
```
"Documentation plan ready. What would you like to do?"
choices: ["Approve & continue (Recommended)", "Revise plan", "Cancel"]
```

- **Approve** → proceed to Phase 3
- **Revise** → ask what to change, update, re-show, re-ask
- **Cancel** → stop and summarise what was planned — and, where Phase 0 step 4(c) committed a generated profile, print that step's left-on-a-branch notice last

---

## Phase 3 — Read the PRD folder

**Read the PRD folder directly** (Phase 0 step 1) — full depth: the PRD, its Epics, and every
artifact present. Read its `prd.md` for the product content, and the `specs` files Phase 0 resolved
alongside it.

**Resolve the diff sources — two of them, merged.** Invoke `Skill(skill: "workflows-core:reference", args: "implementation-format")` and follow its §4. **Both steps below run inside a clone, so build the slug→clone map here, once** — the map Phase 4 step 3 resolves against, by the recipe stated there: for each top-level directory under each entry of `$REPOS_PATH`, `timeout 5 git -C <dir> remote get-url origin 2>/dev/null`, a directory with no `.git` or a failed or timed-out call skipped, a trailing `.git` stripped, the URL's last path segment taken as that clone's slug. Step 2's `git log` runs in the clone, and so does the `git rev-parse` that resolves a block's abbreviated `commit:` before the merge below compares it — §4 requires that resolution of every comparison, the template writing the field abbreviated. Phase 4 takes this same map rather than rebuilding it, and is where the operator settles a slug it matches to no clone; until then such a slug is scanned in no repository and compared in none:

1. **The record.** Read `implementation.md` — `/dev-workflows:implement` writes it into the folder
   of the unit it implemented, so a run that implemented an Epic records its work in that Epic's
   folder, and a broad PRD-level slice in the PRD folder
   (`workflows-core:implementation-format` §1, which also says whose a block an earlier run left in
   the PRD folder is). **Read the focus Epic's own where `focus_key` is set, and otherwise the PRD
   folder's and every `EPIC-` folder's under it, wherever one stands** — the same scope the commit
   scan below takes its tokens for, the scope `workflows-core:implementation-format` §4 fixes for
   this command, and the scope `/release-notes` reads by. An Epic-address run whose record read
   spanned the whole PRD would scan repositories no Epic-scoped token can match, and would dedupe a
   commit carrying the focus Epic's token against another unit's block and then drop it in Phase 4,
   so it would reach nothing. **Read every block in that scope** — this command documents the
   feature as it now stands, so every change that reached it is in scope and no note bounds it. A
   ref two of these records name — the same repository and the same commit — is one ref, counted
   once (that reference's §4).
2. **The scan.** For each repository — those `implementation.md` names, or, when it names none, the
   repositories resolved from `$REPOS_PATH` — search commit messages for the identifiers this run
   already holds, with the `git log` command `workflows-core:implementation-format` §4 gives: one
   `--grep` per token, each matching only as a whole key. The tokens — keys and `workitem_key`s —
   are the ones §4 names for this run's scope — the focus Epic's where `focus_key` is set, and,
   where it is null, **the PRD folder's and every `EPIC-` folder's**, since a whole-key match on the
   PRD's key does not reach the Epic keys `/product-workflows:epics` mints by extending it, and
   never reached an Epic's `workitem_key` — each read off a folder this run resolved or listed;
   **nothing is parsed out of a commit message.** This is what finds work the plugin did not do — a commit written by hand
   after a session ended, a colleague's push, a follow-up nobody ran a command for.

**Merge and dedupe by SHA.** Anything the scan finds beyond the recorded blocks is reported as
**unrecorded work**, named as such with its commits listed: folding hand-made commits silently into
the recorded set would make the record look more complete than it is.

**Report the scan's own reach.** Say **how many commits it scanned** — the non-merge commits it walked,
`git -C <repo> rev-list --no-merges --count HEAD` — **and how many matched**. Only a non-merge
commit whose message names the key is findable, and no convention compels a human to follow one — so
a zero-match scan in a repository that has commits is a signal about the commit convention
(`docs/reference/commit-convention.md`), not proof that no work happened.

**On a repository the scan left at zero matches, run §4's report-only unanchored probe** and print
what it matched, in the words that section gives — *"may name this key inside a branch name or in a
merge commit — inspect by hand"*. Printing is the whole of it: none of those commits is handed to
`diff-summarizer`, none joins the refs this phase builds, and none is reported as this run's
unrecorded work — the probe tells the operator where to look and changes nothing the run reads.

Hand each resolved ref to `diff-summarizer` as a `refs[]` element — `{branch_from, branch_to, title}`,
the shape its Inputs declare for `refs[]`, `title` optional — taken on the pure-local-git path.
Build each element from what the run holds: a record entry is `{branch_from: <its commit — its branch
only where the entry records none>, branch_to: <its base>}`, handed even where this clone does not
hold the commit yet — `diff-summarizer`'s Refresh step fetches before it resolves anything, except
under `refresh.fetch: false` or on a read-only mount, where a commit the clone lacks comes back
unresolved; and a commit only the scan found — the scan takes no merge commit
(`workflows-core:implementation-format` §4) — is `{branch_from: <its sha>, branch_to: <its sha>^}`,
its own change (a root commit's, against the empty tree; a shallow clone's boundary commit, merge or not, comes back unresolved). A squash of a recorded commit is read beside that commit's own element: the same
change summarised twice, which costs less than missing either.
`repo_path` is a top-level input of that agent, passed once at the Phase 5 dispatch and never
repeated inside an element. No URL, no host classification, no `gh` requirement.


The PRD folder holds a readable `prd.md` here: Phase 0 step 1's `DOCUMENT_NO_PRD` has already stopped a run whose PRD folder holds none, or holds one it cannot read. Store the handoff for downstream phases.

When `focus_key` is set (Phase 0 step 1 — the address named an Epic folder), also derive
`focus_items` = **that `EPIC-` folder and what it holds** — its `epic.md`, `specification.md`,
`design.md` and `implementation.md`. There is no Story / Sub-task level beneath it: those were rows of
a tracker export that no command produces any more, and the tree stops at the Epic folder
(`workflows-core:addressing` §2). The
change-scoped phases below consume `focus_items` in place of the full hierarchy — Phase 4 (repo
resolution), Phase 5 (diff summarisation) and Phase 5.7 (doc planning) — while every phase that
describes the PRD as a whole keeps the full handoff. When `focus_key`
is null, every phase uses the full hierarchy, as it does on a run with no Epic address.

---

## Phase 4 — Resolve repos

From the **implementation record** — the `implementation.md` blocks Phase 3 read, only the focus Epic's own where `focus_key` is set (Phase 3's `focus_items`), plus the commit scan that complements them (`workflows-core:implementation-format` §4):

1. Take every entry's `repo`, `branch`, `base` and `commit`. **There is no `pull_requests[]` to filter and no PR `status` to filter on** — nothing in this plugin reads a tracker or a pull-request API, so the record of what was implemented is `implementation.md` and the `git log --grep` scan beside it. An entry with `pushed: false` is still in scope: it is local to one machine, which the run reports rather than skipping.
2. Group the entries by `repo` (short repo name).
3. Take the slug→clone map Phase 3 built with the diff sources — for each top-level directory under each entry of `$REPOS_PATH`, `timeout 5 git -C <dir> remote get-url origin 2>/dev/null`, directories with no `.git` or whose `git remote` call fails or times out skipped, a trailing `.git` stripped, the URL's last path segment taken as that clone's slug, giving `<slug> → [<absolute path>, ...]`. That step and this one run on every keyed run, so the map is always in hand here and is never built twice.
4. Resolve each unique in-scope `repo` slug against the map:
   - **One match** — use that absolute path as `repo_path`.
   - **Multiple matches** (e.g. `cluster` and `cluster-repo`, both pointing at the same upstream) — auto-prefer basename ending `-repo`, then `_repo`/`_fast`, then alphabetically last; show all candidates at plan approval so the user can override.
   - **Zero matches** — record the slug as **missing** and defer it to the consolidated repo gate in step 5 (do NOT escalate per slug).
   Record each resolution as `repo_slug → repo_path` for Phase 5.
5. **Consolidated repo gate.** From step 4, compute `expected` = the unique in-scope repo slugs, `mounted` = those that resolved to a path, and `missing` = the zero-match slugs. This is the earliest point the repo set is known (it depends on the implementation record read at the top of this phase) and it runs before any diff work.
   - **`missing` is empty** — print one line and continue with no gate:
     ```
     Resolved <M>/<N> repositories from the implementation record.
     ```
   - **`missing` is non-empty** — present ONE consolidated gate (not one prompt per slug):
     ```
     This PRD's implementation record spans <N> repositories. <M> mounted, <K> missing:

       ✓ <mounted slug>            ✓ <mounted slug>
       ✗ <missing slug>            (<n> recorded refs — not found under $REPOS_PATH)

     Missing repos are skipped: their code won't be diff-summarised or checked
     against the PRD's requirements, so the discrepancy analysis will be partial.

     choices: ["Mount the missing repo(s) now — I'll wait, then re-scan (Recommended)", "Proceed without them — PRD-only for the missing repos", "Cancel", "Specify a different absolute path for a missing repo"]
     ```
     Choice semantics follow the `Repo unresolved (zero matches) — /document` rule in `workflows-core:escalation-rules`, applied to the whole missing set at once:
     - **Mount now & re-scan** (≈ the rule's "I'll clone it — wait") — pause until the user confirms the clones are present under `$REPOS_PATH`, then re-run step 3's scan and re-render this gate. Loop until `missing` is empty or the user picks another option. This is how the operator gets per-repo control: mount whichever repos are available, re-scan, then choose "Proceed" for whatever remains.
     - **Proceed without them** (≈ the rule's "Skip and continue without its refs") — record every currently-missing repo's refs as `unresolved`, out of scope; continue. Identical downstream state to the previous per-slug skip.
     - **Cancel** — abort the run.
     - **Specify a different absolute path for a missing repo** (≈ the rule's "Specify a different absolute path") — record the given path as that slug's `repo_path`, move it from `missing` to `mounted`, and re-render.
6. A `refs[]` element carries no host and needs none — the diff is taken locally, and `refs[]` is the only element list `diff-summarizer` takes. Nothing here resolves a host, and a report of this run therefore names refs, not pull requests (Phase 9).

---

## Phase 5 — Parallel diff summarisation

Spawn `diff-summarizer` instances in **batches of up to 4 concurrent agents** per Agent message. Wait for each batch to complete before spawning the next. If fewer than 4 repos remain, the final batch is smaller.

**Rationale:** Claude Code's practical parallel-subagent limit is ~4–5; going above that causes silent serialisation or rate-limiting. Capping at 4 makes runtime deterministic.

For each repo, in the same Agent message:

→ Agent (subagent_type: "docs-workflows:diff-summarizer", model: `<detection_model — §9 / §2.1 Sonnet chain; under §10, run_flags.enforced_model>`):
  > "Summarise this repo's recorded refs for the brief:
  >
  > repo_path:     <resolved absolute path for this repo from Phase 4>
  > repo_url_slug: <repo slug, e.g. "cluster">
  > refs:        [ ... the {branch_from, branch_to, title} elements Phase 3 built for this repo from `implementation.md` and the commit scan (and, when focus_key is set, restricted to focus_items) ... ]
  > context:    |
  >   [1–2 sentences: PRD goal + themes relevant to this repo]
  > keys_hierarchy:
  >   [the PRD folder's own key + the key of every EPIC- folder under it, read from each folder's frontmatter (Phase 3); when focus_key is set, restrict to focus_items — the focus Epic and nothing beside it]
  > refresh:
  >   fetch: [false if Phase 1 chose 'no refresh'; true otherwise]
  >   pull:  [true if Phase 1 chose 'fetch + pull default branch'; false otherwise]"

After the batch returns, handle each per-repo status:

- `OK` / `PARTIAL` — store the output, continue.
- `REPO_MISSING` — should not happen at this stage (Phase 4 already checked). If it does, escalate per the `Repo missing (after resolution)` rule in `workflows-core:escalation-rules`.
- `DIRTY_TREE` — escalate:
  ```
  choices: ["Stash changes and retry this repo", "Skip this repo", "Cancel"]
  ```
- `REFRESH_BLOCKED` — escalate:
  ```
  choices: ["Continue with current local state", "Skip this repo", "Cancel"]
  ```
- `prep.read_only: true` — not a failure. The scan ran at `prep.scanned_ref`. Escalate per the `Read-only mount — ref stale or diverged` rule in `workflows-core:escalation-rules` **only** when `prep.ref_committed_at` is more than 14 days old or `prep.head_divergence.ahead > 0`; otherwise proceed silently and cite evidence at `prep.scanned_ref`.
- `NO_PRS_RESOLVED` — the agent's own declared return status, whatever the elements were called; record all that repo's refs as unresolved and continue.

After every batch completes, if **every ref across every repo** is unresolved, present a single aggregate gate (not per-ref):
```
choices: ["Proceed with PRD-only content (Recommended — writer/planner draw from the folder read output; final report notes missing diff content)", "Cancel"]
```

---

## Phase 5.5 — Find documentation locations

Invoke `doc-location-finder`:

→ Agent (subagent_type: "docs-workflows:doc-location-finder", model: `<detection_model — §9 / §2.1 Sonnet chain; under §10, run_flags.enforced_model>`):
  > "Find write target(s) for the brief:
  >
  > repo_root:       [the resolved docs_repo_path (Phase 0)]
  > feature_summary: [2–4 sentences combining the Phase 3 themes + the PRD's own `## Goal` from prd.md]
  > diff_highlights: [key filenames / symbols from the diff-summarizer per_pr summaries]
  > profile:         [the resolved profile — its spaces[] content roots and its announcement_pages block]"

Handle the return:

- **`status: OK`** with a populated `targets` list:
  ```
  choices: ["Accept all proposed locations (Recommended)", "Adjust individual locations (you'll be prompted per item)", "Cancel"]
  ```
- **`status: LOW_CONFIDENCE`** — display `confidence_notes` alongside the targets so the user sees what was ambiguous:
  ```
  choices: ["Adjust individual locations (Recommended)", "Accept all proposed locations", "Cancel"]
  ```
  (The default flips to "Adjust" because confidence is low.)
- **`status: EMPTY`** — skip the accept/adjust flow:
  ```
  choices: ["Specify locations manually (you'll be prompted)", "Cancel"]
  ```
  The manual path takes a free-text entry per target (`path` + `kind` + `section`) and validates path existence for `extend-existing` targets.

The confirmed target list (from any of the three paths above) is the **authoritative write-target set** for Phase 6.3 and is handed to `doc-planner` in Phase 5.7.

---

## Phase 5.6 — Images

**Always runs**, regardless of the Phase 1 `new_images_wanted` answer. Declining new screenshots seeds an empty add list; it never skips reviewing whether the images already on the pages this run is about to edit are still accurate — that was the defect: one Phase 1 answer used to gate both concerns. Build **two** lists.

### Add list (new screenshots)

Build this list only when `new_images_wanted` is `true` (Phase 1); when `false`, the add list is empty and contributes nothing to the merged prompt below — skip straight to the existing-image list. When `true`, build a **merged, deduped candidate list** from four sources (by this point Phase 0's `specs_dir`, the Phase 1 `<project_dir>`, the Phase 3 the folder read `attachments[]`, and the Phase 4 resolved repos are all in hand):

1. **Recursive scan of `<specs_dir>`** — when Phase 0 resolved a `specs_dir` (not `none`), recursively scan it for image files — its root and every folder below it, each `EPIC-*/` subfolder included:
   ```bash
   find "<specs_dir>" \
     -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.gif" -o -iname "*.svg" -o -iname "*.webp" \) 2>/dev/null
   ```
   When `specs_dir` is `none`, this source contributes nothing.
2. **PRD-folder attachments** — the image paths enumerated under the resolved PRD folder's `attachments/` directory, where one exists. May be empty. This source reads an image already there and never moves it; this run never places one there (see *add a new image* below).
3. **Recursive scan of `<project_dir>`** — when Phase 1 resolved a `<project_dir>` (the folder this run resolved), recursively scan it for image files:
   ```bash
   find "<project_dir>" -type f \
     \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.gif" -o -iname "*.svg" -o -iname "*.webp" \) 2>/dev/null
   ```
   This surfaces images you keep in the project folder (custom diagrams, curated screenshots). When `<project_dir>` is null, this source contributes nothing.
4. **Manual paths** — the user-provided "I'll provide screenshot paths" option (free text, see the `choices` below).

**Dedupe** by resolved absolute path (collapse mixed separators / trailing-slash differences); when the same image appears in more than one source, keep one entry and note its origins.

### Existing-image list (staleness review)

**Always build this list** — it does not depend on `new_images_wanted`. The orchestrator owns it (`doc-planner` runs later, at Phase 5.7, and never supplies or reads this list). For every `extend-existing` write target in Phase 5.5's confirmed `write_targets`, read the target file and record **every image reference in document order** — one row per occurrence, not per unique URL: the same URL can recur several times on one page, and each occurrence is decided separately (two sections can carry the same stale URL, and only one of them may need the fix). For each occurrence record:
- `target` — the write target's path.
- `occurrence` — the 1-based index of this image reference within the whole target, counted in document order across **all** image references in the file — never filtered by `old_url`, never scoped to a section.
- `old_url` — the image reference's current URL/path.
- `section` — the nearest enclosing heading.

A target with no image references contributes nothing.

### Merged prompt

Present both lists — "Found `<N>` add-list candidate(s) (`<count>` from specs scan, `<count>` from folder attachments, `<count>` from the project folder)" and "Found `<M>` existing image(s) across `<K>` edited page(s) to review for staleness" — then ask:
```
choices: ["Review both lists item by item (Recommended)", "Add-list only — existing images are current", "Nothing to do — no image work this run", "Cancel"]
```
When both lists are empty, skip presenting this prompt — there is nothing to show — and set `screenshots[] = []`, `existing_image_decisions[] = []` directly.

- **Review both lists item by item**:
  - **Add list**, if non-empty, asks:
    ```
    "Found <N> candidate image(s): <count> from specs scan, <count> from folder attachments, <count> from the project folder. How would you like to source screenshots?"
    choices: ["Use all auto-discovered + add manual paths (Recommended)", "Use all auto-discovered only", "Select a subset (you'll pick per candidate)", "Provide screenshot paths manually only (you'll be prompted)"]
    ```
    - **Use all auto-discovered + add manual** → take every deduped candidate, then prompt for additional free-text absolute paths to append.
    - **Use all auto-discovered only** → take every deduped candidate; no manual prompt.
    - **Select a subset** → present the deduped candidates and let the user pick which to keep.
    - **Provide screenshot paths manually only** → ignore the auto-discovered candidates; take free text only.
    - **No images after all** is not listed — the outer prompt already offered *Nothing to do — no image work this run*, and a user who changes their mind here says so through the harness's own free-text option, which resolves to this: leave `screenshots[]` empty; the add list contributes nothing further.
  - **Existing-image list**, if non-empty, walks each occurrence in order — showing `target`, `section`, and `old_url` — and asks per item (no default is safe to recommend across arbitrary items, so no `(Recommended)` marker):
    ```
    choices: ["Replace — I'll provide a new screenshot (staged via Phase 6.1)", "Leave as is — still accurate", "Cancel"]
    ```
    "Replace" appends an `existing_image_decisions[]` entry `{target, occurrence, old_url, new_url, section, decision: accepted}` with `new_url` left pending (Phase 6.1 resolves it) and records the replacement's source (a path from the add list just reviewed, or a new free-text path). "Leave as is" appends the same shape with `decision: declined` and no `new_url`.
- **Add-list only — existing images are current** → run the add-list sub-flow above (if non-empty); `existing_image_decisions[] = []` — the user's verbatim choice is the record of the (skipped) existing-image review, not a per-item entry.
- **Nothing to do — no image work this run** → `screenshots[] = []`, `existing_image_decisions[] = []`.
- **Cancel** → stop and summarise.
- **The harness's free-text option** (supplied automatically, never authored into the array — `workflows-core:escalation-rules` §0) → takes free text and resolves to one of the three dispositions above — "Review both lists item by item", "Add-list only", or "Nothing to do" — and the run then behaves exactly as if that option had been chosen directly, including which ledger row it writes. There is no fourth disposition and no "skip on my own judgement" path here.

**Append the `image_review` ledger row once this phase's outcome is settled — by the user's answer to the merged prompt above, or by the both-lists-empty precondition when that prompt itself was skipped — outside any conditional branch above**, so every path through this phase writes exactly one row (schema: `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` §3; registry entry: §4):
- `RAN` — the choice was "Review both lists item by item" and at least one of the two lists was non-empty; `mechanism: "per-item user review of the add list and the existing-image list built from extend-existing write targets"`; `findings:` = the count of existing-image occurrences reviewed.
- `SKIPPED_BY_USER` — the choice was "Add-list only — existing images are current" or "Nothing to do — no image work this run"; `user_decision` quotes the choice verbatim.
- `NOT_APPLICABLE` — both lists were empty (the prompt above was skipped); `precondition_unmet: "no add-list candidates and no image references on any extend-existing write target"`.

For any **manual** free-text paths, accept any absolute filesystem path (`/tmp`, home, the docs repo); accept multiple (one per line or space-separated). Validate each path exists and has an image extension (`.png|.jpg|.jpeg|.gif|.svg|.webp`); drop and report any that don't.

When you need to **add a new image** for this feature (a screenshot the docs should have but no source yet holds — including a replacement source for an accepted existing-image entry), place it in the resolved PRD folder's `Doc screenshots/` subfolder — the one Phase 1 defaults `<screenshot_staging_dir>` to — where source 3's scan of `<project_dir>` finds it. **Never in the folder's `attachments/`**, which holds only the text and markdown sources a run vendored (`workflows-core:addressing` §2, *Reserved subdirectory names*); an image found there is still read, as source 2, and left where it is. There is one home for a feature's new images, and it is a subfolder of the folder the run already resolved.

The selected add-list paths populate the existing **`screenshots[]`** passed to `doc-planner` in Phase 5.7 — the downstream placement machinery (per-screenshot `dest`/`staging`/`upload_note`, `image_policy`) is unchanged. An accepted item — from either list — carries into Phase 6.1 for its CDN URL. The outcome is recorded as `existing_image_decisions[]` (schema above; matches `doc-writer`'s input contract) and carried in the Phase 6.3 handoff file alongside `cdn_urls`.

---

## Phase 5.7 — Plan the documentation

Invoke `doc-planner`:

→ Agent (subagent_type: "docs-workflows:doc-planner", model: `<planning_model — §9 / §2 Opus chain; under §10, run_flags.enforced_model>`):
  > "Produce the documentation checklist for the brief:
  >
  > folder_read: [paste full YAML from Phase 3; when focus_key is set, restrict the folder read to focus_items]
  > diff_summaries:       [paste array of diff-summarizer outputs from Phase 5]
  > write_targets:        [paste confirmed list from Phase 5.5]
  > screenshots:          [selected candidate paths from Phase 5.6, possibly empty]
  > screenshot_staging_dir: [resolved <screenshot_staging_dir> from Phase 1, or null]
  > repo_root:            [the resolved docs_repo_path (Phase 0)]
  > code_repos:           [the Phase-4 resolved {slug, path} map; [] if none resolved]
  > specs_dir:            [resolved <specs_dir> from Phase 0, or null]
  > profile:              [the docs-profile loaded in Phase 0 — supplies the spaces[] content roots, tokens, and link conventions]"

Handle the `status` and `gaps`:

- **`status: OK`, `gaps: []`** → proceed to the approval prompt.
- **`status: OK` or `PARTIAL` with `gaps` entries** — for each gap, act on its `recommended_action`:
  - `"ask user"` → prompt inline **before** showing the checklist-approval choice. Free-text prompt scoped to the gap; feed the answer back to the planner via a single re-invocation (pass the user's answer as an additional `gap_resolution` field in the brief — `[{gap, answer}]`, one entry per answered gap, the shape `doc-planner`'s input contract gives it). If the user declines, fall back to `"mark TODO in draft"`, and keep that fallback: a declined gap has no entry in `gap_resolution`, so the re-invoked planner returns it again as `"ask user"`, and it is not asked about again — it stays `"mark TODO in draft"`. A gap the re-invocation **newly** returns as `"ask user"` — one the planner's first return did not carry — is not asked about either, since no re-invocation remains to take the answer: mark it `"mark TODO in draft"` and list it in the checklist display as a visible TODO, as the next bullet says.
  - `"mark TODO in draft"` → surface in the checklist display as a visible TODO; the writer at Phase 6.3 emits `<!-- TODO: … -->` markers. Does not block approval.
  - `"skip with note in final report"` → list in the checklist display; carry forward into the Phase 9 `### Skipped items`. Does not block approval.
- **Ambiguous image policy** — a checklist target whose `image_policy` is `ambiguous` and whose `screenshots:` is non-empty. The planner found no dominant image convention among the target's sibling pages (mixed references, or none), so it planned neither a `dest` nor a `staging` path, and `doc-writer` cannot ask the user: it is a subagent. Resolve each such target in the planner's first return here, **before** the checklist-approval choice and so before Phase 6.1 and Phase 6.3 — never leave one of those to the writer. For each, show the target path and the screenshots planned for it, then ask (no option is safe to recommend without a convention, so no `(Recommended)` marker):
  ```
  choices: ["Copy them into the repository beside the page", "Stage for manual upload to the repo's image-management tool", "Leave these screenshots off this page", "Cancel"]
  ```
  - **Copy them into the repository beside the page** → record `local` for that target.
  - **Stage for manual upload to the repo's image-management tool** → record `cdn_upload_required` for that target. Where `<screenshot_staging_dir>` is null — Phase 1's **Not found** branch was skipped — first take an absolute staging directory from the user, rejecting `/tmp` and any path inside the docs repo as that branch does, and record it as `<screenshot_staging_dir>`.
  - **Leave these screenshots off this page** → once the checklist is final — after the re-invocation below, where there is one — remove that target's `screenshots:` entries from it; the writer places no screenshot on that page, and each screenshot is listed in Phase 9's `### Deferred items` as a user-declined screenshot.
  - **Cancel** → stop and summarise.
  - A free-text answer is mapped onto one of the first three, or the question is asked again; it is never written through as a policy of its own.

  Pass every `local` / `cdn_upload_required` answer to the planner as `image_policy_resolution` — `{<target_path>: local | cdn_upload_required}`, with the current `<screenshot_staging_dir>` — in the same single re-invocation that carries any `gap_resolution`, and take the checklist it returns: it plans each named target's `dest` or `staging` path under the chosen policy, exactly as it would have for a detected one. That re-invocation is made once, so a target it newly returns `ambiguous` with a screenshot is not asked about here: it reaches the operator instead as `doc-writer`'s named `BLOCKED` gap at Phase 6.3, whose loop settles it with this step's own question and plans its screenshots' paths before the one re-dispatch (Phase 6.3, **`status: BLOCKED`**). A target left `ambiguous` with no screenshot needs no answer — no screenshot is placed on it, so its policy decides nothing.
- **`status: PARTIAL`** — returned for a user-asked gap or an ambiguous policy, each resolved by the bullets above, save a target the one re-invocation newly returns `ambiguous`, which Phase 6.3 settles — is presented to the user alongside the checklist so the approval decision is informed.

Present the checklist (with any gaps + dispositions, and — when the planner returned a non-empty `repo_authoring_guidance` — the repo-specific authoring rules it extracted from the repo's own guidance files, so the user sees "this repo's CONTRIBUTING.md / CLAUDE.md requires …" before approving):
```
choices: ["Approve & write (Recommended)", "Adjust (describe)", "Cancel"]
```

---

## Phase 5.8 — Discrepancy analysis & user decision

**Ledger first — before the skip check below.** This gate must carry a row on every run, including runs with nothing to escalate. Append the `source_truth_verification` row now, per `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` §3:

- `code_repos` is empty → `NOT_APPLICABLE`, `precondition_unmet: "code_repos is empty"`.
- `code_repos` is non-empty and `doc-planner` returned no `verification_warnings` of an escalating type (`CONTRADICTED`, `NOT_FOUND`, `AMBIGUOUS`, `SPEC-VS-PRD`) → `RAN`, `mechanism: "claim-class verification per source-truth.md §2–§3"`, `findings: 0`. A list of only `VERIFIED` entries counts as none for this purpose — the row is final and this phase's body does not run.
- `code_repos` is non-empty and at least one warning IS of an escalating type → append `RAN` provisionally now, then rewrite the row at the end of this phase per **Ledger (final)** below.

Run the rest of this phase when the `doc-planner` handoff contains any `verification_warnings` with `finding: CONTRADICTED`, `NOT_FOUND`, `AMBIGUOUS`, or verdict `SPEC-VS-PRD`. If there are none, skip to Phase 6.3 — the row above is already recorded.

This phase is **three-way** when a spec was provided (Phase 0 resolved `specs_dir` and Phase 5.7 passed it to `doc-planner`): it compares the **PRD** narrative, the **Spec** (authoritative "intended"), and the **Code** ("actual"), per `workflows-core:source-truth` §7. When no spec was provided, the planner emits `spec_phrasing: "(no spec)"`; the **Spec phrasing** column simply renders `(no spec)` and the run behaves exactly as the original PRD-vs-code two-way protocol.

**Supplementary resolution (one attempt, before presenting anything).** For every
`verification_warning` whose `finding` is `AMBIGUOUS` or `NOT_FOUND`, check whether the relevant repo
is present in the Phase-4 `code_repos` map. When it is, run **one** direct grep against that resolved
local path to try to resolve the claim — using the `workflows-core:source-truth`
§3 technique matching the claim's type — **including when `diff-summarizer` returned `REFRESH_BLOCKED`
for that repo**. A repo whose refresh genuinely failed — a network or auth error, or an unresolvable
default branch — can still be grepped at its current local state, and this is exactly
the case a user previously had to resolve by hand.

Update the warning in place when the grep resolves it (`finding: VERIFIED` or `CONTRADICTED`, with
`source_phrasing` and `source_location` filled from the grep). Present only what remains unresolved.
Record the outcome in the `source_truth_verification` ledger row: a resolution obtained this way makes
the row `DEGRADED`, with `not_run:` naming what did not run (e.g.
`mechanism: diff-summarizer refresh`, `reason: REFRESH_BLOCKED`), never a clean `RAN`.

1. **Present the analysis table** (informational, before asking):
   ```
   | # | Claim | PRD phrasing | Spec phrasing | Source (code) phrasing | Source location | Verdict |
   ```
   One row per warning. The **Spec phrasing** cell reads `(no spec)` when no spec was provided. Use `Source (code) phrasing: "(not verifiable)"` for `no-source-evidence` entries. The **Verdict** carries the §4.2 finding (`CONTRADICTED`, `NOT_FOUND`, `AMBIGUOUS`) or `SPEC-VS-PRD` (the spec differs from the PRD narrative; recommended action "Document as intended (spec)").

2. **Batch decision:**
   ```
   choices: ["Decide per discrepancy (Recommended)", "Document ALL as intended (spec)", "Document ALL as actual (code)", "Skip ALL and report (drafts a bug report)"]
   ```
   "Document ALL as intended (spec)" uses the `spec_phrasing` (or the PRD phrasing when it is `(no spec)`).

3. **Per-discrepancy** (if "Decide per discrepancy"): for each warning, show claim + PRD phrasing + Spec phrasing + Source (code) phrasing + location, then:
   ```
   choices: ["Document as intended (spec)", "Document as actual (code)", "Skip this claim and report it", "Cancel"]
   ```
   "Document as intended (spec)" describes the agreed contract — the `spec_phrasing` (or the PRD phrasing when it is `(no spec)`) — and, when the code lags the intended phrasing, adds an intentional-discrepancy marker + bug-report draft. "Document as actual (code)" matches what shipped, and when it is a qualifying `document-as-code` case per §7.5, also records the gap in the bug-report draft. "Skip this claim and report it" omits the claim but still records the gap in the bug-report draft.

4. **Record `discrepancy_decisions[]`** keyed by `number` (claim, prd_phrasing, spec_phrasing, source_phrasing, source_location, decision ∈ {document-as-spec, document-as-code, skip-and-report}, rationale). `spec_phrasing` is recorded verbatim (`(no spec)` when none was provided). Set `bug_report_destination` to the resolved PRD folder (ask if none) when any decision is `document-as-spec` (where the code lags the intended phrasing), `skip-and-report`, or a qualifying `document-as-code` per `workflows-core:source-truth` §7.5.

Pass `discrepancy_decisions` to Phase 6.3.

**Ledger (final).** Rewrite the `source_truth_verification` row appended at the top of this phase, per `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` §3: when the row you appended at the top is already `NOT_APPLICABLE` (`code_repos` was empty), leave it exactly as it is — a phase body that ran on no-source-evidence warnings does not turn an unmet precondition into a performed check; `RAN` when verification ran against the resolved repos; `DEGRADED` when any claim was resolved only by the supplementary grep, with `not_run:` naming what did not run (e.g. `mechanism: diff-summarizer refresh`, `reason: REFRESH_BLOCKED`) and a `ci_still_checks:` line; `UNAVAILABLE` when the primary verification AND the supplementary grep both failed to execute at all with `code_repos` non-empty — convert that per `gate-ledger.md` §5 before leaving this phase. `findings:` is the count of `verification_warnings` presented to the user.

---

## Phase 6.1 — CDN image handoff

Run this phase when, in the checklist Phase 5.7 settled, **any** screenshot has `image_policy: cdn_upload_required` — a target whose ambiguous policy Phase 5.7's **Ambiguous image policy** step resolved to "Stage for manual upload to the repo's image-management tool" included, since the planner's re-invocation returns it as `cdn_upload_required` — **or** any Phase 5.6 `existing_image_decisions[]` entry has `decision: accepted`. (When the only image policy in play is `local` and there is no accepted existing-image replacement, skip this phase: local images are copied into the repo at Phase 6.3 with no handoff needed.)

1. **List each affected image** so the decision is informed — one row per image:
   - target page / anchor it belongs on (from the planner's per-screenshot placement, or — for an existing-image replacement — the `target` / `section` recorded in Phase 5.6);
   - proposed alt text;
   - the planner's `upload_note`.

   An item sourced from the existing-image list (Phase 5.6) is a **replacement**, not a new insertion: the writer swaps that occurrence's URL rather than inserting a new reference, and because a CDN URL is immutable, the collected `new_url` is always a different URL from `old_url`. A swap has no deferred/TODO form — `doc-writer` only ever writes a real replacement URL for an `existing_image_decisions` entry — so even when the batch choice below is "Defer", still collect each accepted existing-image entry's `new_url` individually (record it as that entry's `new_url`, not in `cdn_urls`) before Phase 6.3; only the remaining, non-swap screenshots follow the Defer path.

2. **Ask how to handle the upload:**
   ```
   choices: ["Upload now — I'll paste the CDN links (Recommended)", "Defer — stage with TODO placeholders + Phase 9 list", "Cancel"]
   ```

   - **Upload now** → collect one CDN URL per image (prompt per image, or one URL per line in image order). Validate each pasted value looks like a URL (e.g. starts with `http://` / `https://`); re-prompt for any that don't. Record `cdn_urls[<image>]` for a regular screenshot, or the entry's `new_url` for an existing-image replacement. Phase 6.3 then writes the **real CDN URL** into each markdown image reference instead of a TODO placeholder — for an existing-image replacement, it swaps that occurrence in place. Nothing is staged and the Phase 9 "Screenshots to upload manually" section stays empty for these images.
   - **Defer** → the existing async behavior for regular screenshots: stage each image under `<screenshot_staging_dir>` (the staging directory resolved in Phase 1), Phase 6.3 inserts the `TODO-upload` placeholder reference, and every staged image is listed in the Phase 9 `### Screenshots to upload manually` section. Existing-image replacements are exempt from this path (see above) — their `new_url` is still collected now.
   - **Cancel** → stop and summarise.

   Record the decision as `cdn_handoff_decision ∈ {upload-now, defer}` and carry it (with any `cdn_urls` and the updated `existing_image_decisions[]`) into Phase 6.3.

---

## Phase 6.2 — Branch setup (conditional)

Run this phase only when write context = `docs_repo` (or `non_docs_repo` after user confirmed at Phase 0 step 2) AND the user confirmed branching at plan approval. Never for `obsidian` or `plain_dir`.

Every git call in this phase, and in Phase 6.3's commit and Phase 8.5, runs as `git -C <docs_repo_path>` — the docs repository's top level (Phase 0 step 2), never the working directory — so every path given to git is relative to that top level.

1. **Update the base branch.** `<base>` is a branch **name**, never an `origin/<name>` ref, which `git switch` refuses — the name the ladder below resolves: whichever branch `origin/HEAD` names, else `main` or `master` where the remote has one, and otherwise a local `main` or `master`, or the branch HEAD is on. Resolve it by `workflows-core:read-only-repos` §3's chain, run against `<docs_repo_path>`, and its **A switch takes the name** rule: rung 1, `git -C <docs_repo_path> symbolic-ref --quiet --short refs/remotes/origin/HEAD`, prints `origin/<name>`, and `<base>` is what follows `origin/`; where rung 1 fails — `origin/HEAD` unset, or naming a ref that no longer exists (§3 rung 1) — `<base>` is the literal `main` or `master` whose ref rungs 2–3 find. Two steps are this command's own, beside that chain. Where rung 1 fails, run `git -C <docs_repo_path> remote set-head origin --auto` and retry it before rungs 2–3. Where the chain is exhausted — no `origin`, or one holding neither branch — `<base>` is the local `main`, then `master`, whichever `git -C <docs_repo_path> rev-parse --verify --quiet refs/heads/<name> >/dev/null` finds, and the fetch and the pull below are skipped, there being no remote branch to bring it up to; with neither, `<base>` is the branch HEAD is on and nothing is switched. Once the base is resolved: `git -C <docs_repo_path> fetch origin`. Then update the base working copy **only outside the inline-profiling case**: when `profile_source` is NOT `generated`, `git -C <docs_repo_path> switch <base> && git -C <docs_repo_path> pull --ff-only`. **In the inline-profiling case (`profile_source: generated`), do NOT switch** — HEAD must stay on `profile_branch`, the branch Phase 0's profiling cut off the base and committed the profile on, so this run's docs commits land on it after step 5 renames it. When a switch happened and the fast-forward pull fails:
   ```
   choices: ["Stash local changes and continue (Recommended)", "Proceed from current base state", "Cancel"]
   ```

2. **Clean-tree check.** `git -C <docs_repo_path> status --porcelain`; if non-empty:
   ```
   choices: ["Stash changes and continue (Recommended)", "Proceed anyway — pre-existing changes will appear in the diff", "Cancel"]
   ```
   **Cancel** stops the run; where Phase 0 step 4(c) committed a generated profile, it ends with that step's left-on-a-branch notice.

3. **Derive branch name from repo conventions.** In priority order, look at the repo root — `docs_repo_path` — for `CONTRIBUTING.md`, `CONTRIBUTION.md`, `README.md`, `DOCUMENTATION-GUIDELINES.md`. Grep each for a branch-naming section (case-insensitive, patterns like "Branch name", "Branch naming", "naming your branch"). If a pattern like `<user>/<KEY>-<slug>` or `<prefix>/<name>` is documented, derive the branch name by filling placeholders with known values (key from Phase 0, slug from the feature summary, and any **identity** placeholder (`<user>`, `<your-name-or-initials>`, `<initials>`, …) from the §2 ladder in `Skill(skill: "workflows-core:reference", args: "branch-naming")` — `$GIT_USER_INITIALS` → `git -C <docs_repo_path> config user.initials` → inference from existing branches → its §2.5 prompt). Classify the pattern's segments per §1.2 and never add an identity segment it does not ask for. If multiple patterns are documented, offer them all to the user. When no pattern is documented (§1.4), take the whole prefix from the same ladder, whose fallback for this command is `docs/`.

4. **Confirm the branch name** — always, even when derived from conventions (initials and slugs are subjective):
   ```
   choices: ["Use proposed name: <name>", "Edit name (you'll be prompted)", "Cancel"]
   ```
   **Cancel** stops the run; where Phase 0 step 4(c) committed a generated profile, it ends with that step's left-on-a-branch notice.
   Fallback default when no convention is found: `<prefix>/<key>-<slug>`, where `<prefix>` comes from `workflows-core:branch-naming` §2 (fallback `docs/`).

5. **Create or adopt the branch, and record handoff anchors.** Record `base_branch` = the base resolved in step 1 (the Phase 8.5 squash uses it).
   - **Normal case** (`profile_source` is `in-repo` or `built-in`, or a custom repo whose profiling did not create a branch): `git -C <docs_repo_path> switch -c <name>` from `base_branch`.
   - **Inline-profiling case** (`profile_source: generated`): Phase 0's `/docs-profile` already cut `profile_branch` and committed `.dev-workflows/docs-profile.yml` on it, so HEAD is already on that branch. Do NOT create a new branch — rename that one, by name: `git -C <docs_repo_path> branch -m <profile_branch> <name>`. Name the old branch every time: the one-argument `git branch -m <name>` renames whatever branch HEAD is on, `main` included, while the two-argument form fails where `profile_branch` does not exist rather than rename another. `profile_commit` is the commit profiling handed back (Phase 0 step 4(c)) — never a `git log --diff-filter=A` lookup, which names the newest commit that *added* the file, not necessarily the one this run made. Phase 8.5 squashes the docs commits onto `profile_commit`, keeping the profile-config commit as a distinct first commit. (Per `${CLAUDE_PLUGIN_ROOT}/references/finish-and-handoff.md` §1.)

No external CLI calls, and nothing is pushed or sent: step 1's reads of the remote — `git fetch origin`, the `pull --ff-only` behind it, and `remote set-head origin --auto` where rung 1 fails — only settle the base, and every write this phase makes is local.

---

## Phase 6.3 — Write documentation

The writing is delegated to the **`doc-writer`** subagent (pinned to the §2 Opus reasoning chain — see `workflows-core:model-routing/classification` §9.2). The orchestrator prepares a structured handoff and dispatches; it does not write pages itself.

1. **Write the handoff file.** Create a temp file (`command mktemp`, e.g. `$(command mktemp -t dw-<KEY>-XXXXXX)` — never the specs tree, never the docs repo) containing the `doc-writer` input contract: `folder_read`, `diff_summaries`, `write_targets`, `doc_planner_checklist` (+ gap dispositions), `repo_authoring_guidance` (the planner's extracted repo-specific rules), `component_patterns` (the planner's recurring content-shape → dominant-component evidence, per `workflows-core:doc-structure-conventions` §3 — like `repo_authoring_guidance`, a top-level sibling of the planner's `checklist:`, so it must be carried explicitly; `[]` when the sibling sample showed no established pattern), `discrepancy_decisions` (Phase 5.8), `cdn_handoff_decision` + `cdn_urls` + `screenshot_staging_dir` + `screenshots` + `existing_image_decisions` (Phase 5.6 / 6.1), `profile`, `docs_repo_path`, and `bug_report_destination`. Record its absolute path.

2. **Dispatch the writer:**

→ Agent (subagent_type: "docs-workflows:doc-writer", model: `<planning_model — §9 / §2 Opus chain; under §10, run_flags.enforced_model>`):
  > "Write the product documentation for this brief.
  >
  > handoff_file: [absolute path of the temp handoff file from step 1]"

3. **Handle the return.**
   - **`status: DONE`** — record `files_written` + `notes` for Phases 6.4 / 6.5 / 7 / 8. Then **commit** per the branch/commit policy below — `git -C <docs_repo_path> add -- <each path in files_written that lies under docs_repo_path>`, then `git -C <docs_repo_path> commit`. `files_written` also names what the writer put outside the docs repository — the `<KEY>-implementation-gaps.md` draft in the resolved PRD folder, and screenshots staged under `screenshot_staging_dir` — and those are never staged here: git refuses a path outside the repository (`fatal: … is outside repository`) and then stages nothing at all, so the commit would have nothing to commit. The gaps draft, like Phase 8.5's `pr-draft.md`, is `$SPECS_PATH`'s, and the terminal `commit-artifacts` step commits it (`workflows-core:specs-repo-git` §2.1) — unless the run carries `specs_git: blocked` or `specs_git: misrooted` (`workflows-core:specs-repo-git` §3.3 G0, §3.1), when it is written and not committed. The run commits a staged screenshot nowhere — it is a copy kept only until the operator uploads it — so keep each one that lies under `$SPECS_PATH` out of that repository's `git status`, where `$SPECS_PATH` is a git work tree, lest every later run's `specs-preflight` meet it as a dirty path (that reference's §3.3 G1). Take `<rel>`, the staged path with its leading `$SPECS_PATH/` removed — a path that does not begin with it is outside the specs repository, and nothing is done for it — and where `git -C "$SPECS_PATH" check-ignore -q --no-index -- "<rel>"` exits 1, no rule matching it, append one anchored line naming it, its glob characters escaped, to the repository's local exclude file:

     ```
     f=$(git -C "$SPECS_PATH" rev-parse --git-path info/exclude) && case $f in /*) ;; *) f="$SPECS_PATH/$f" ;; esac && mkdir -p "$(dirname "$f")" && printf '\n/%s\n' "$(printf '%s' "<rel>" | sed -e 's/[][*?\\]/\\&/g' -e 's/ $/\\ /')" >> "$f"
     ```

     `--git-path` prints its path relative to the directory git ran in — `.git/info/exclude` at a top level — hence the `case`. That exclude file is the repository's own and never committed, so the line changes nothing anyone else sees. Exit 0 — a rule already ignores it — appends nothing, and so does any other exit, which is git failing rather than answering. Then run the same `check-ignore` again, and where it still does not exit 0, name the path in the Phase 9 report as left untracked in `$SPECS_PATH`.
   - **`status: BLOCKED`** — surface the named gap to the user:
     ```
     choices: ["Provide the missing input (you'll be prompted)", "Cancel"]
     ```
     On a provided value, rewrite the handoff file and re-dispatch once. **Where the gap is a target left `ambiguous` with a screenshot planned for it** — one Phase 5.7's single planner re-invocation newly returned, which that phase does not ask about — the value is that target's image policy: ask Phase 5.7's **Ambiguous image policy** question for each such target the writer names, taking each answer as that step takes one, then rewrite the run's checklist as the planner would have planned it — the `doc_planner_checklist` the handoff file carries, which is also the checklist Phase 7 hands `doc-reviewer`, so the reviewer judges each page against the plan as this loop leaves it — **Copy them into the repository beside the page**: set the target's `image_policy` to `local` and each screenshot's `dest` under the target's `image_dir`, the idiomatic directory `doc-planner` step 5 found among its sibling pages' local image references, where the checklist records one, and under `<page-dir>/img/` otherwise, as `doc-planner` step 6 plans one; **Stage for manual upload**: set `cdn_upload_required` and each screenshot's `staging` under `<screenshot_staging_dir>`, taking one from the user first where it is null, as Phase 5.7's step does, keeping the `upload_note` the planner wrote for each screenshot, which Phase 9's `### Screenshots to upload manually` quotes, and settle their upload as Phase 6.1 settles one — under the run's `cdn_handoff_decision` where Phase 6.1 made one, collecting each screenshot's `cdn_urls` entry as its **Upload now** does where that decision is `upload-now`, and asking Phase 6.1's question for them where it made none; **Leave these screenshots off this page**: remove the target's `screenshots:` entries and list each screenshot in Phase 9's `### Deferred items` — and re-dispatch once.

Write context governs branch/commit (Phase 0 step 6); **the orchestrator commits the writer's output in the docs repository** (the writer never commits (still true — `doc-writer` runs no git at all; it only writes files)):

| Write context | Branch | Commit |
|---|---|---|
| `obsidian` | NEVER | NEVER |
| `docs_repo` | YES (opt-in confirmed at plan approval) — see Phase 6.2 | YES (orchestrator commits doc-writer's `files_written` that lie in the docs repo) |
| `non_docs_repo` | Phase 0 step 2 already asked user to confirm; if confirmed, behave as `docs_repo` | YES (if user confirmed at Phase 0) |
| `plain_dir` | NEVER | NEVER |

This table governs the **documentation write target only**. Independently of every row above, the run's terminal `commit-artifacts` step commits `$SPECS_PATH`'s bounded session-artifact paths (`workflows-core:specs-repo-git` §2.1) — a different repository, never the docs write target.

---

## Phase 6.4 — Style check (before reviewer)

**Mandatory:** the orchestrator MUST dispatch `docs-style-checker` and act on its return — never skip on its own judgement of which linters are installed.

`docs-style-checker` runs the chain **internally**: the repo's primary linter (Vale, etc.) AND `prose-style-checker` as a complementary semantic / cross-page-consistency pass, merging and deduping both finding sets. The two are complementary, not redundant (Vale: lexical at scale + frontmatter; `prose-style-checker`: engineer jargon, cross-page label consistency, subject-verb agreement, plural/singular label mismatch). The command does NOT invoke `prose-style-checker` separately — the agent already did. It climbs the rungs as a ladder — a detected-but-broken rung does not abandon the ones below it — and, when the caller passes `spaces`, lints each written space with that space's own command.

Invoke `docs-style-checker` on the files written in Phase 6.3:

→ Agent (subagent_type: "docs-workflows:docs-style-checker", model: `<detection_model — §9 / §2.1 Sonnet chain; under §10, run_flags.enforced_model>`):
  > "Run the style check for this brief:
  >
  > repo_root: [the resolved docs_repo_path (Phase 0)]
  > site_root: [docs_repo_resolved (Phase 0 step 2), where it differs from docs_repo_path — the site's own .vale.ini, package.json and lint configuration are looked for there first, then in each directory above it up to docs_repo_path; omit the key otherwise]
  > files:     [absolute paths of every file written or modified in Phase 6.3]
  > spaces:    [one entry per space in profile.spaces that has a profile.commands.per_space entry — {id, content_root, lint}; omit the key entirely when the profile declares no per_space commands]
  > enforced_model: [run_flags.enforced_model, when set — docs-style-checker passes it as model: on its own prose-style-checker dispatch in place of the Sonnet detection chain (workflows-core:model-routing/classification §10); omit the key otherwise]"

Write the `style_check` ledger row before acting on the return — rewriting the row Phase 0's preflight pre-seeded if there is one, per `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` §3's one-row-per-gate rule, and preserving any `user_decision` it carries (schema:
`${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` §3), deriving its outcome from the agent's
`primary_attempts` and `complementary_linter`:

- no file was written in Phase 6.3 → `NOT_APPLICABLE`, `precondition_unmet: "no files written"`.
- a primary rung succeeded → `RAN`, `mechanism: <primary_linter> + prose-style-checker` (the complementary pass always runs; name `<primary_linter>` alone only when the return carries a `complementary_error`), `findings:` = the number of merged violations returned.
- no primary rung produced a result — every detected rung failed, or none was ever detected — but `prose-style-checker` ran → `DEGRADED`, `not_run:` one entry per rung from `primary_attempts`, and `findings:` = the number of merged violations returned. `ci_still_checks:` depends on which of those two happened: where a rung was **detected and failed**, name the linter the repository's CI runs on the pull request — `"<that linter> runs on the PR in CI"` — or say that none runs where the repository's CI runs none, with its reason (`"none runs: the repository has no CI build"`, or `"none runs: the repository's CI runs no linter"`); where **no rung was ever detected** there is no repo linter to name and CI checks nothing here, so write `"no repo-level linter is configured; the complementary semantic pass was the only coverage"`. §6 makes an empty `ci_still_checks` a BLOCKER, so the field is filled either way — but never by a claim about CI the repository cannot support.
- `status: ERROR` → `UNAVAILABLE`; convert it per `gate-ledger.md` §5.

Also write the `repo_checklist` row (creating it, or rewriting it in place if one exists): `NOT_APPLICABLE` with
`precondition_unmet: "the repo publishes no authoring or verification guidance"` when
`doc-planner`'s `repo_verification_gates` block is empty; otherwise `RAN` with `findings:` = the
number of checklist items that failed against the written files.

Then act on the return:

- **`status: OK`** — the chain ran (primary and/or complementary), zero merged violations. Proceed to Phase 7.
- **`status: VIOLATIONS_FOUND`** — invoke `doc-fixer` with the violations treated as per their severity. After `doc-fixer` completes, **check its `Stop condition flag`**: `docs-style-checker` maps a linter's own blocking failure to `BLOCKER` (`agents/docs-style-checker.md`), so this dispatch can return `NEEDS HUMAN` — the fixer deferred a blocking violation it could not safely fix. On `NEEDS HUMAN`, surface each deferred BLOCKER with the fixer's reason and ask the user how to resolve it — fix by hand and re-run, or skip the check. A silent re-run only reports the same violation again. The `style_check` gate row stays open until that answer lands and then records its outcome per `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` — `RAN` after a hand fix and re-run, `SKIPPED_BY_USER` with the choice quoted verbatim if skipped. Only on `CLEAR` re-run the linter once:

  → Agent (subagent_type: "workflows-core:doc-fixer", model: `<detection_model — §9 / §2.1 Sonnet chain; under §10, run_flags.enforced_model>`):
    > "Fix the style violations for this brief:
    >
    > Task description: [doc writing for <KEY>]
    > Reviewer or style-checker output: [paste full docs-style-checker output]
    > Project root: [the resolved docs_repo_path (Phase 0)]
    > Severities to fix: BLOCKER and MAJOR"

  If violations remain after the re-run:
  ```
  choices: ["Proceed to review anyway — reviewer may still PASS", "Show remaining violations and let me fix manually", "Cancel"]
  ```

  When the re-run completes, rewrite the `style_check` row's `findings:` to the post-fix violation count so the Phase 9 table reports what survived, not what was found.

- **`status: ERROR`** — every primary rung failed or was never detected, and the `prose-style-checker` pass also failed. Surface the error reason, then STOP: the `style_check` row is `UNAVAILABLE`, and the only prompt the user sees is the `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` §5 conversion list. Do NOT ask an ad-hoc question here — §5 owns this decision, and the "Choice lists are presented verbatim" rule in `workflows-core:escalation-rules` binds it.

---

## Phase 6.5 — Render verification

**Ledger first — before the run-condition below.** Both gates this phase owns must carry a row on every run, including runs where the phase does not execute. Per `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` §3 each gate holds exactly one row, so **rewrite** the row Phase 0's preflight pre-seeded rather than appending beside it — and when that pre-seeded row carries a `user_decision`, keep it: the user already decided to proceed without this tooling, and that decision stands until the gate itself proves otherwise, or until a later answer of the user's decides the gate — Step 2's Skip (`gate-ledger.md` §3). Ledger (final) quotes that Skip on `render_smoke_check` whenever it is chosen, and on `build_check` only where a build did not run, Step 1 did not already decide the row, and the Skip declined that build's only remaining proof. A `build_check` row whose builds all ran keeps its own outcome and decision, and so does a row Step 1 left `SKIPPED_BY_USER` — except that wherever another build failed on its content, the row is `FAILED`, whatever was declined beside it. Create the row here only when the preflight did not pre-seed one:

- Write context is `obsidian` or `plain_dir` → append BOTH `build_check` and `render_smoke_check` as `NOT_APPLICABLE` with `precondition_unmet` naming the actual context — `"write context is obsidian"` or `"write context is plain_dir"`. These rows are final; the phase does not run.
- Write context is `docs_repo` or a confirmed `non_docs_repo` → append both provisionally as `RAN`, then rewrite each at the end of this phase per **Ledger (final)** below.

Run this phase after Phase 6.4 **only** when Phase 6.3 wrote files into a buildable docs repo (write context `docs_repo`, or `non_docs_repo` confirmed at Phase 0). Skip for `obsidian` / `plain_dir` (nothing was written into a repo that builds) — the rows above are already recorded. Mechanics: `${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/render-verification.md`. "Affected pages" = every file written or modified in Phase 6.3.

### Step 1 — Build check (gating)

Resolve the builds to run, most specific first (`${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/render-verification.md` §1 — the precedence `/docs-serve --build` uses):
- **The profile records `builds[]`** → run **every** entry's `command`, in list order. They are the builds one content root renders into — the profile `/docs-init` writes records a public and an internal one — and an internal-only page is compiled by the internal build alone, so running one of them would pass a page the other cannot build.
- **Otherwise** → `profile.commands.per_space.<space>.build`, else the flat `profile.commands.build`, run for every space in the **verification set** (`render-verification.md` §2): every space whose `content_root` holds at least one affected page.

Run each from `docs_repo_path`, the top level every command the profile records runs from (Phase 0 step 2). Record **each build on its own** — its `builds[]` `id` (or, without `builds[]`, its space), its command, its exit code and, on a failure, its output — so a failure names the build that failed. Do NOT re-run the Phase 6.4 prose linter. Classify each failing build:
- **Content failure** (the template won't compile, unresolved snippet include, broken postid/internal link, malformed token) → invoke `doc-fixer` (`subagent_type: "workflows-core:doc-fixer"`, model: `<detection_model — §9 / §2.1 Sonnet chain; under §10, run_flags.enforced_model>`; Severities: BLOCKER and MAJOR), handing it **the failing build's output** as its `Reviewer or style-checker output` — each failing build under its `id` (or space), with its command and its output verbatim, every error it reports a BLOCKER at the file it names — then re-run every build this step resolved, once. If failures remain:
  ```
  choices: ["Proceed to smoke-check anyway", "Show remaining and fix manually", "Cancel"]
  ```
- **Environmental failure** (the build tool will not run — missing toolchain, `command not found`, missing `.docstack` shim) → surface the reason and record the build as not run, with that reason; no `doc-fixer` loop. **Then test the registered fallback before anything is asked.** `build_check`'s fallback is the Step 2 dev-server boot (`gate-ledger.md` §4), and `UNAVAILABLE` means that neither the primary nor a fallback ran (`gate-ledger.md` §2), so a build that will not run does not by itself make the gate `UNAVAILABLE`. The fallback can run for that build where `bash` and `curl` are present, and off Linux `ps` — the smoke check's own tools, tested as Step 2's pre-check tests them — and the tool of the `command` of at least one of **that build's own servers** is present — a package manager with no installed dependencies counting as missing (`render-verification.md` §2 step 1). A build's own servers are the servers that publish what it compiles, among those Step 2 would boot for an affected page, chosen as Step 2 chooses them: for a `builds[]` entry, the server whose `visibility` pairs with the entry's (`docs-profile-schema.md`'s field rules); for a space's `commands.per_space.<space>.build`, that space's servers; for the flat `commands.build` — and, where the profile records no build command at all, for the proof Step 2 stands in for — every server Step 2 boots across the verification set. Never another build's server: it compiles another space or another configuration, so its boot proves nothing about this build. A command's tool is the one `${CLAUDE_PLUGIN_ROOT}/references/toolchain-preflight.md` §2 defines — never a leading `cd`, which `command -v` finds on every host: `cd website && pnpm start` needs `pnpm` — and it is tested as that file's §3 tests it: by the form §3 gives a tool the run starts inside `bash -c`, as it starts every server, never a bare `command -v` in the Bash tool's own shell, which an alias or a shell function of that name passes — and asked from the directory the command runs from, `docs_repo_path` or the leading `cd <dir>` under it, never from the working directory, which reports a path-valued tool such as `node_modules/.bin/vitepress` missing from anywhere else.
  - **The fallback can run** → ask nothing here and continue to Step 2, whose boot of that build's own servers is now its build proof; Ledger (final) records `build_check` from what Step 2 does. A `user_decision` Phase 0's preflight left on the row stays on it.
  - **The fallback cannot run** → neither that build nor its fallback can run, so the gate is `UNAVAILABLE`, and this is its `gate-ledger.md` §5 conversion, not an orchestrator decision:
    ```
    choices: ["Install <the missing tool> and retry this gate", "Proceed without this check — record my decision", "Cancel the run"]
    ```
    "Proceed without this check" writes `SKIPPED_BY_USER` with the chosen option quoted verbatim in `user_decision` — where another build failed on its content, Ledger (final) records the row `FAILED` and keeps this decision on it (`gate-ledger.md` §2). Do NOT present this list when the `build_check` row already carries a `user_decision` from Phase 0's preflight naming the same missing tool — the user answered this question before anything was written, and that answer stands. Record the failure reason in the row, keep the existing `user_decision`, and continue to Step 2 without prompting.

When the profile declares **no** build command at any of the three levels — no `builds[]`, no `commands.per_space.<space>.build`, no `commands.build` — record "no build command in profile; build proof deferred to the dev-server boot (Step 2)" and proceed. Under the built-in example-docs profile this branch does not apply — `commands.per_space.cloud.build` and `commands.per_space.self-hosted.build` are both defined — and under a profile `/docs-init` wrote it does not either, since that profile records `builds[]`.

### Step 2 — Dev-server smoke-check (opt-in, best-effort)

Offer it. Present this list **verbatim** — the "Choice lists are presented verbatim" rule in `workflows-core:escalation-rules` forbids moving `(Recommended)`, reordering the options, or re-wording them. Dev-server flakiness and a clean static check are reasons to say something in prose beside the list; they are never reasons to recommend Skip. Where Step 1 could not run a build — the profile records none, or a build would not run for an environmental reason and the fallback can run — say so beside the list too: the boot of that build's own servers (Step 1) is then the only proof for what it compiles, so Skip declines the build check with it (Ledger (final)).
```
choices: ["Run smoke-check (Recommended)", "Skip — use the manual table only", "Cancel"]
```

When run, check each space in the **verification set** — every space whose `content_root` holds at least one affected page (see `render-verification.md` §2) — **one server at a time** (`profile.dev_servers.concurrent: false` forbids overlap). **Choose the server per affected page, never by the space alone** (`render-verification.md` §2): `dev_servers.servers[]` is not keyed by space, and the two-build profile `/docs-init` writes records two servers for its one space. Among the `servers[]` entries whose `space` is the space's `id`:
- **one** — it checks every affected page in the space;
- **one tagged `visibility: public` and one tagged `visibility: internal`** — a page is checked on the public server unless the public build excludes it, and then on the internal server; `${CLAUDE_PLUGIN_ROOT}/references/docs-workflow/visibility.md` §1 (**the model**) decides which pages the public build excludes;
- **any other set of more than one** — nothing tells them apart, and a guessed server is a false result either way: record "smoke-check skipped for `<space>`: `<n>` servers share it and nothing tells them apart" and use the manual table for that space;
- **none** — record "smoke-check skipped for `<space>`: no dev server is recorded for it" and use the manual table for that space.

Boot a space's public server before its internal one, and skip a server no affected page was assigned to. A port **answers** while something listening on it takes a connection from `localhost`. The probe is `command curl -s -o /dev/null --noproxy '*' --max-time 2 http://localhost:<port>/`, read by its exit code alone: **7**, a refused connection, is a port that does not answer; **127** means curl could not run — no answer either way, never an answering port and never a quiet one; **any other code** is a port that answers — a listener took the connection or left it waiting, an HTTP error, an empty reply, a reset and a 28 (`--max-time` running out on a silent listener) included. The probe itself needs no socket table; the free test in Step 2 below adds the listening read to it (`render-verification.md` §2), which needs nothing installed on Linux and `lsof` off it, and where that is missing the probe decides alone. Every **GET** below — the readiness poll and the page requests — is `command curl -sL -o /dev/null -w '%{http_code}' --noproxy '*' --max-time 10 <url>`, read by the status it prints: the last response's, since `-L` follows a redirect (`mkdocs serve` answers a route without its trailing slash with a 302), or `000` where no response came. **Every request this check makes carries `--noproxy '*'`**: with `http_proxy` or `ALL_PROXY` set and no `no_proxy` naming `localhost`, curl hands a request for `localhost` to the proxy, which answers it — exit 0 on a port nothing listens on, and its own page in place of the server's. **Before the first boot, confirm that `bash` and `curl` are present and, where `test -r /proc/net/tcp` fails — off Linux — that `ps` is too**, each tested as `${CLAUDE_PLUGIN_ROOT}/references/toolchain-preflight.md` §3 tests a tool run through `bash -c` or as `command <name>`, never by a bare `command -v`, which an alias or a shell function of that name passes: step 2 reads the process group it made, and step 5 that group's members and a listener's parents, from `/proc` on Linux, which needs nothing installed, and with `ps` elsewhere (`render-verification.md` §2, **Portability**, defines each read). Where one is missing, the check cannot run — boot nothing, record "smoke-check unavailable: `<tool>` is not installed" (`render-verification.md` §2, **The endings**, ending 4), and every page uses the manual table. A probe that exits 127 anyway, part-way through, ends the check the same way: boot no further server, signal the process group of one this run already booted as step 5 does, record "smoke-check unavailable: curl could not run (exit 127) — `<space>`'s server was signalled, and its port could not be probed; its log is `<log>`" (ending 4's other form), and every page not yet checked uses the manual table. For each server booted — full mechanics in `render-verification.md` §2:
1. **Prerequisites (best-effort, never auto-applied).** Verify `profile.prerequisites`. The `.docstack` shim is a local, gitignored dev-environment workaround — check it, NEVER apply it. Unmet → record "smoke-check skipped for `<space>`: prerequisite `<x>` unmet" and use the manual table for that space. **Then check the server's command's tool** — the tool `${CLAUDE_PLUGIN_ROOT}/references/toolchain-preflight.md` §2 defines, tested as its §3 tests it, asked from the directory the command runs from — `docs_repo_path`, or the directory a leading `cd <dir>` names under it, which is what resolves a path-valued tool — the same check `/docs-serve` makes before it starts one (its Phase 4) and Step 1 makes for a failed build's own servers. A `pnpm`, `npm` or `yarn` whose lockfile, the nearest at or above the directory the command runs from, has no `node_modules/` beside it — nor, for Yarn, a `.pnp.cjs` — counts as missing too: its dependencies are not installed, and the server would fail as surely (`render-verification.md` §2 step 1 states the rule). Missing → boot nothing for this server: record "smoke-check skipped for `<space>`: `<tool>` is not installed", or, for missing dependencies, "smoke-check skipped for `<space>`: `<tool>`'s dependencies are not installed (`<lockfile>` has none beside it)", use the manual table for this server's pages, and go on to the next server. A server whose tool is missing could never start, so it is never booted, and the check never waits out a readiness timeout for it.
2. **Probe, then boot — a port is free only where nothing answers on it and nothing is listening on it** (`render-verification.md` §2, which defines free and gives the listening read). Where the server's `port` already answers, something this run did not start holds it: boot nothing, signal nothing, and **boot no further server** — record "smoke-check stopped at `<space>`: port `<port>` was answering before its server booted" (ending 1), and every page not yet checked uses the manual table. Where nothing answers but the listening read finds a socket in `LISTEN` on the port — a listener bound to an address `localhost` does not reach — do the same, recording "smoke-check stopped at `<space>`: port `<port>` had a listener the probe could not reach before its server booted" (ending 1's other form), with that listener's pid where the read names one. Otherwise boot the chosen server **in a process group of its own**, with one Bash call — `command bash -c 'set -m; (cd <docs_repo_path> && <command>) > <log> 2>&1 & echo $!'` — where `<command>` is its `command` with every `{port}` replaced by that server's configured `port` — never run with the token unsubstituted (`docs-profile-schema.md`'s field rule) — and `<log>` is a file outside every repository tree (`command mktemp -t dw-smoke-XXXXXX` names one), where a server that fails to boot leaves its output; inside the single-quoted script, write each `'` those three carry as `'\''`. The explicit `command bash -c` makes job control, `$!` and step 5's group signals bash's whatever shell the Bash tool uses — Claude Code runs that tool in bash or in zsh, zsh on a default macOS, whose `/bin/bash` (3.2) has all three. With job control on, the printed pid is the id of a new process group that every wrapper and child of the command inherits (an `npm` or `pnpm` script, the `sh` it runs, the server itself) unless one leaves it for a session of its own, which step 5 meets only by a port it already holds; and the job outlives the call. The command keeps its server in the foreground (`docs-profile-schema.md`'s field rule for `dev_servers.servers[].command`): one that detaches it — `setsid`, `nohup … &`, a trailing `&`, `docker run -d`, or a tool that detaches itself, as Astro 7 does under an agent unless `ASTRO_DEV_BACKGROUND` — or, for `astro preview`, since 7.2, `ASTRO_PREVIEW_BACKGROUND` — is set (that field rule names each opt-out) — is a profile defect, and a server it moves out of the group — as `setsid` and `docker run -d` do — is one this check can neither stop nor see bind late. Confirm it: `<pid>`'s process group, read as `render-verification.md` §2's **Portability** paragraph reads one — from `/proc/<pid>/stat` on Linux, with `command ps -o pgid= -p <pid>` elsewhere — is `<pid>`, or nothing where the job has already exited — and that pid is the `<pgid>` step 5 signals. Any other number means job control gave it no group of its own: hold the pid alone, and step 5 stops it by its no-group path.
3. **Readiness poll** — GET `http://localhost:<port><base_path>/`, this server's own, until HTTP 200 or `profile.dev_servers.readiness_timeout_seconds` seconds (fall back to **120** when absent). **At every interval at which the GET gets no response (`000`), test the group too**, where step 2 holds a `<pgid>`, by step 5's gone-group test — the process table names no member of the group, or every member it names is a zombie, never a failing `kill -0` on its own — and **a gone group ends the poll at once**, as `/docs-serve` Phase 5's poll ends: the command exited without its port answering (a theme not installed, a configuration it cannot load, a script its package lacks) and nothing of its group is left to bind the port, so the check never waits out the timeout for it. Record "smoke-check skipped for `<space>`: its server exited before it was ready — its command was `<command>`", with the last twenty lines of `<log>`, and use the manual table for this server's pages; then probe the port — the group being gone already, the probe decides: quiet → go on to the next server; still answering → a process outside the group holds it, and step 5's **Either not confirmed** applies: that process is signalled first, then both things are confirmed again, as `render-verification.md` §2 step 5, sub-step 4, the authority, says. Without a `<pgid>` the poll has no group to test and runs to its timeout. On timeout → stop it as step 5 says. Confirmed stopped → record "smoke-check skipped for `<space>`: not ready", use the manual table for this server's pages, and go on to the next server — nothing of its group survives to bind the port later. Not confirmed → step 5's record ends the check. **Without a group of its own, a timeout ends the check**, since nothing can tell whether a process of it will bind the port after the check has moved on: stop what the run holds (step 5), **boot no further server**, record "smoke-check stopped at `<space>`: not ready, and started without a process group of its own — port `<port>` may still bind; its command was `<command>`, its log `<log>`" (ending 3), and every page not yet checked uses the manual table.
4. For each affected page assigned to this server, GET its derived URL (Step 3 route rule) → **HTTP 200** passes; a 404 or a 5xx is recorded as Outcomes below says.
5. **Stop the server by signalling its process group** — after its pages and after a readiness timeout alike: `command bash -c 'kill -TERM -- -<pgid>'`, wait up to 5 seconds for the group to be gone, and where it is not, `command bash -c 'kill -KILL -- -<pgid>'` and wait up to 5 seconds more (a killed process stays in its group until its parent reaps it). **Confirm two things**: the group is gone and the port is quiet (the probe). The group is gone where the process table names **no** member of `<pgid>` at all, or where every member it names is a zombie — the states `render-verification.md` §2's **Portability** paragraph reads for the group's members, from `/proc/[0-9]*/stat` on Linux and with `command ps -A -o pgid=,stat=` elsewhere, are all `Z`, or on a `ps` all begin with `Z`: a zombie runs nothing and holds no port, and under a parent that never reaps — a container whose PID 1 is `sleep infinity` — it stays in the group for good. `command bash -c 'kill -0 -- -<pgid>'` settles only the other half: exit 0 means a member is alive and signallable, so the group is **not** gone; a non-zero exit means either no such group or one this user may signal no member of — `EPERM`, which a `sudo`'d command's group gives and which bash exits 1 for exactly as it does for "no such process" — so a failing `kill -0` is never read as a gone group, and the process table, which names another user's processes too, decides (`render-verification.md` §2 step 5). Both → the next server may boot. **Either not confirmed** → where the port still answers, a process outside the group holds it: read its listener's pid from the socket table, as `/docs-serve` Phase 5 does, by `${CLAUDE_PLUGIN_ROOT}/commands/docs-serve.md` Phase 2's definition (**The evidence**, item 1's opening paragraph: the processes `render-verification.md` §2's **Portability** socket-table read names for the port, from `/proc` on Linux and with `lsof` elsewhere; the one the others descend from where several are named; no listener where it names none, or where off Linux no `lsof` is installed to read it) — and by nothing else of it: not its checkout test, because this run started the server on a port it found silent, and not its living-entry test, because this command keeps no state file and uses the pid once, in this stop, without recording it — then `SIGTERM` it, wait up to 5 seconds for the port to stop answering, `SIGKILL` it if it still answers, and confirm both things again. Where either is still not confirmed after that → **boot no further server**: record "smoke-check stopped after `<space>`: `<what>` — left running; its command was `<command>`, its log `<log>`" (ending 2), where `<what>` is "port `<port>` still answers" (with its listener's pid where the socket table names one) or "process group `<pgid>` still runs", and every page not yet checked uses the manual table. **Without a group of its own**, stop what the run holds: `SIGTERM` the pid step 2 holds and, where the port answers, its listener; wait up to 5 seconds for the port to stop answering; `SIGKILL` both if it still answers; then the probe decides — quiet, the next server may boot unless this stop followed a timeout (step 3 ends the check); still answering, boot no further server, recorded as above. **Remove a server's `<log>` once it is confirmed stopped** — both things confirmed, after its pages, after a readiness timeout or after step 3 found its group gone, or, without a group of its own, its port quiet with no timeout behind it — with `command rm -f -- "<log>"`, once any record has quoted what it needs from it; a server the check cannot show stopped keeps its log, and the record that ends the check names it (`render-verification.md` §2 step 5). A missing `lsof` alone never ends the check; what ends it, what each ending records and what that record names are `render-verification.md` §2's **The endings**, the definition this command cites and never restates.

Where a space has two servers, `<space>` in each record above names the server as well — `docs (internal)`.

Outcomes:
- **404** on an affected page → ❌ with its URL, and the page stays on the manual table. **Never a content failure by itself, and never a `doc-fixer` dispatch**: the route is best-effort (Step 3), so a 404 cannot tell a wrong route from a missing page, and Step 1's build check — every build that compiles an affected page — owns compile failures.
- **5xx** on an affected page = render defect → treat as a Step 1 content failure (offer `doc-fixer` / surface): a server error is not a routing question.
- A **boot / prerequisite / missing server tool / readiness** problem is best-effort → never blocks; that space falls back to the manual table — on a space with two servers, that server's pages — unless it is one of the endings below.
- Each of the endings `render-verification.md` §2's **The endings** defines ends the whole smoke-check rather than one space's part of it → never blocks; every page not yet checked falls back to the manual table, and `render_smoke_check` records the ending among its `DEGRADED` reasons and never `UNAVAILABLE` (Ledger (final)). **What each ending records, and what that record names, is that list's to say.** Write the record it gives, and nothing it does not.

### Step 3 — "Pages to visit" table (always)

Emit a table, one row per affected page — its URL (`http://localhost:<port><base_path>/<route>`, derived against the server Step 2 chose for it; a page Step 2 chose no server for gets its route on each of its space's servers, or the route alone where the space records none) and what to verify ("confirm the page renders as intended"). When the smoke-check ran, annotate each row ✅ 200 / ⚠️ skipped (reason) / ❌ with its status.

**Route derivation (best-effort):** `<route>` = the page path relative to its space's `content_root` with a trailing `index.md`/`.md` removed. Approximate — so a 404 in Step 2, a wrong route or a missing page alike, is ❌ with its URL and leaves that page on the manual table; it is never a content failure by itself (Step 2's Outcomes).

Carry the table and the Step 1/Step 2 outcomes into the Phase 9 `### Render verification` section, and pass a one-paragraph `render_verification` summary to Phase 7.

**Ledger (final).** Rewrite the two rows appended at the top of this phase (schema: `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` §3). A row already written as `NOT_APPLICABLE` is never reached here — this phase did not run. Where one part of a gate `FAILED` and another only `DEGRADED` — one build failed on its content while another did not run, or one space answered a 5xx while another fell back — the row is `FAILED` and records the degraded part in its `not_run` and `ci_still_checks` (`gate-ledger.md` §2). A content `FAILED` also outranks a decision to proceed without another part — Step 1's §5 conversion, the preflight's decision Step 1 kept, or Step 2's Skip: the row is still `FAILED`, records the declined part the same way, and keeps that decision in `user_decision`, because a content failure is never hidden behind a skip (`gate-ledger.md` §2):

- `build_check` — `RAN` when every build Step 1 resolved executed; `FAILED` on a content failure.
  `mechanism` names every build Step 1 ran, each by its `id` (or space) with its result —
  `public: pass; internal: fail` — so a `FAILED` row names the build that failed.
  `DEGRADED` when a build did not run — the profile records no build command, or Step 1 met an
  environmental failure (its tool missing, a missing `.docstack` shim, any reason the build tool
  would not run) and found the fallback able to run — and, for every build that did not run, the
  Step 2 boot served as its proof: one of **that build's own servers** (Step 1 defines them — every
  server Step 2 booted, where the profile records no build command) answered its readiness poll
  with a 200, which proves what that build compiles (`render-verification.md` §1). A server of
  another build answering proves nothing about this one. `not_run:` names each build that did not
  run and why (`no build command in profile`, or the environmental failure Step 1 recorded, such as
  `<tool> is not installed`), and `ci_still_checks:` names the build CI runs on the pull request, or
  says that none runs where the repository has no CI build.
  A `user_decision` Phase 0's preflight left on the row stays on it.
  A row Step 1 leaves as `SKIPPED_BY_USER` — its §5 conversion, when neither the build nor its
  fallback could run and the user chose to proceed, or the preflight's decision on that same missing
  tool, which Step 1 kept — is **final — do not rewrite it**, except where another build failed on
  its content: the row is then `FAILED` (above), with that decision kept in `user_decision` and the
  build that did not run in `not_run` and `ci_still_checks`.
  `UNAVAILABLE` applies only when a build did not run, Step 1 did not already convert it, and the
  Step 2 boot did not serve as its proof. **Where that is because the user chose Skip at Step 2**,
  their Step 2 choice is the decision this row quotes, in place of any decision Phase 0's preflight
  left on the row: record `SKIPPED_BY_USER` with it (`FAILED` with it, where another build failed on
  its content — above), and ask nothing more. Declining the only remaining source of build proof is
  declining the build check, and it is the decision that removed the proof. **Otherwise** — Step 2
  ran and none of that build's own servers it booted became ready, or it booted none of them — this
  is the coverage hole `${CLAUDE_PLUGIN_ROOT}/references/toolchain-preflight.md` §5 predicts: convert
  per `gate-ledger.md` §5, except where the row carries Phase 0's decision on the same missing tool,
  which stands, as it does in Step 1, and the row records `SKIPPED_BY_USER` with it — in either case
  `FAILED` with the decision, where another build failed on its content (above).
- `render_smoke_check` — `RAN` when the smoke-check completed for every space in scope — a 404 does
  not change that, since the page's server booted and was checked and the 404 is no content failure:
  `findings:` counts the affected pages annotated ❌, each already surfaced with its URL; `FAILED`
  when an affected page answered a 5xx — a render defect, handled as a Step 1 content failure and
  recorded on this row, never on `build_check`'s;
  `DEGRADED` when at least one space — or one server of a space with two — fell back to the manual
  table, with `not_run:` naming the space (and the server) and its reason (prerequisite unmet / its
  command's tool not installed / boot failure / readiness timeout / servers nothing tells apart / no
  server recorded / one of the endings `render-verification.md` §2's **The endings** defines, whose
  reason and named detail are that ending's own row there — quoted from it, never widened to what
  another ending names), and with a `ci_still_checks:` line naming the build CI runs on the pull request, or
  saying that none runs where the repository has no CI build — never a claim that CI renders these
  pages;
  `SKIPPED_BY_USER` with the chosen option quoted verbatim when the user selected Skip.
  Each reason `DEGRADED` lists falls back to the manual table, and that table is this gate's
  registered fallback (`gate-ledger.md` §4), which Step 3 always emits and which needs no tool — so
  `render_smoke_check` never records `UNAVAILABLE`, and no ending of it asks the `gate-ledger.md` §5
  conversion. A `user_decision` Phase 0's preflight pre-seeded on this row stays on it (this phase's
  opening paragraph), unless the user selected Skip, whose choice the row then quotes in its place.

---

## Phase 7 — Doc review gate

Invoke `doc-reviewer` (Opus — pinned by its own frontmatter; recorded as `review_model`, no dispatch override added unless §10 enforces a model). The reviewer is **product-docs-only**; Epic drafts go through `epic-reviewer` in `/epics`.

→ Agent (subagent_type: "docs-workflows:doc-reviewer", model: `<review_model — §2 Opus chain, equal to doc-reviewer's frontmatter pin; under §10, run_flags.enforced_model>`):  # recorded in model_routing as review_model above, frontmatter-pinned, no override added unless §10 enforces a model
  > "Review the written product documentation for this brief:
  >
  > Task description: [one-paragraph summary of the feature and <KEY>]
  > Written doc file paths: [absolute paths of every file written in Phase 6.3]
  > PRD folder path:        [the PRD folder (Phase 0 step 1)]
  > Diff summaries:         [array of diff-summarizer outputs from Phase 5]
  > doc-planner checklist:  [the full YAML from Phase 5.7 — as Phase 6.3's `BLOCKED` loop left it, where that loop rewrote it]
  > style-check report: [the violations output from Phase 6.4 — from docs-style-checker or prose-style-checker; same violation schema regardless of source]
  > gate_ledger:        [the complete gate_ledger block — one row per gate in references/gate-ledger.md §4, including the Phase 0 toolchain_preflight row]
  > render_verification: [the Phase 6.5 summary — each build's result, named by its `id` (or space); smoke-check per space, and per server where a space has two (passed / skipped with reason / stopped, naming what that ending's own record names — `render-verification.md` §2, **The endings**), with every ❌ page's URL and status — a 404 left on the manual table, a 5xx a render defect]
  > code_repos:         [the Phase-4 resolved {slug, path} map; [] if none resolved]
  > existing_image_decisions: [the Phase 5.6/6.1 stale-image-swap array, one entry per **reviewed occurrence** and each {target, occurrence, old_url, new_url, section, decision}. `[]` when the per-item existing-image review did not run — the existing-image list was empty, or the user chose "Add-list only" / "Nothing to do" at the Phase 5.6 merged prompt. An all-declined review is NOT `[]`: every reviewed occurrence appends an entry, `decision: declined` included. Supplies the swap-completeness evidence for the 'Screenshots' dimension]
  > cdn_upload_resolutions: [one entry per screenshot that checklist places on a target whose `image_policy` is `cdn_upload_required` — {target, image, resolution, cdn_url}, `image` being the key Phase 6.1 records its `cdn_urls` entry under: `resolution: uploaded` with that `cdn_urls[<image>]` as `cdn_url` where the run's `cdn_handoff_decision` was `upload-now` — Phase 6.1's, or, where that phase made none, the one Phase 6.3's loop took with Phase 6.1's question — and `resolution: deferred` with `cdn_url: null` where it was `defer`. `[]` when no screenshot has that policy. Tells the 'Screenshots' dimension which form each such image must take: its real CDN URL, or a TODO placeholder listed for manual upload]
  > profile:            [the resolved docs-profile from Phase 0 — supplies frontmatter.changelog_guidelines and spaces[]]"

Act on the verdict:

**Triage sub-step** (before any fixer dispatch, and on every re-review): invoke `Skill(skill: "workflows-core:reference", args: "finding-triage")` and follow it. For each finding, verify its claimed consequence at the location it names; keep it, mark it unverified, or dismiss it; record every dismissal and every unverified finding with its reason; and raise a grade only by effect. Hand the fixer **survivors only**, and carry every disposition into this run's report. A re-review — the one the fix cycle allows, or one you chose at the first settle prompt — is triaged under that reference's § On re-review: it carries forward what this run already ruled — save, on a re-review you chose at the first settle prompt, the dismissed and unverified findings it re-verifies — and no survivor of it is handed to a fixer. At either of that reference's settle prompts, **Keep the verdict** means the review **stayed blocked** (below) — on a kept verdict that is not `BLOCK`, which raised no BLOCKER, the run ends as Cancel does — and **Cancel** aborts the run, as the escalation's own *Cancel the whole run* does.

- **BLOCK** — invoke `doc-fixer` (`subagent_type: "workflows-core:doc-fixer"`, model: `<detection_model — §9 / §2.1 Sonnet chain; under §10, run_flags.enforced_model>`) with `Severities to fix: BLOCKER and MAJOR`. Write the `doc-fixer` Fix Report to a temp file (`command mktemp -t dw-doc-claims-XXXXXX`, never inside a repo tree or the specs tree), record its path as `claims_file`, then **check `doc-fixer`'s `Stop condition flag` before re-invoking anything**. If it is `NEEDS HUMAN`, the fixer deferred at least one BLOCKER as needing a human decision: do NOT re-invoke `doc-reviewer` — a re-review can only re-find the BLOCKER the fixer has just reported it could not resolve — and instead surface each deferred BLOCKER with the reason the fixer gave, then escalate it individually per the `Review verdict BLOCK (unresolved after one fix cycle) — /document` rule in `workflows-core:escalation-rules`, which names this entry point alongside a review that stayed blocked. Only when the flag is `CLEAR` do you re-invoke `doc-reviewer` once **passing `claims_file`** — so the re-review falsifies the fixer's account rather than assuming it. Triage the re-review under `workflows-core:finding-triage` § On re-review (the triage sub-step above); on that section's **Proceed**, continue to Phase 8 as after a verdict that is not BLOCK. If the review **stayed blocked** — a BLOCKER survives that triage, or you keep the verdict at either settle prompt — escalate for each unresolved BLOCKER individually per the `Review verdict BLOCK (unresolved after one fix cycle) — /document` rule in `workflows-core:escalation-rules`:
  ```
  choices: ["Provide manual fix notes (you'll be prompted)", "Defer to a follow-up issue (record in Phase 9 report)", "Override and accept the finding", "Cancel the whole run"]
  ```
  "Manual fix notes" → take free-text from the user; apply via `doc-fixer` (`subagent_type: "workflows-core:doc-fixer"`, model: `<detection_model — §9 / §2.1 Sonnet chain; under §10, run_flags.enforced_model>`) in a bounded one-shot pass (no further re-review cycle). "Defer" → record in Phase 9 `### Deferred items` without an override flag. "Override" → record in `### Deferred items` with the user's rationale. "Cancel" aborts.

- **PASS WITH RECOMMENDATIONS** — invoke `doc-fixer` for MAJOR findings only:

  → Agent (subagent_type: "workflows-core:doc-fixer", model: `<detection_model — §9 / §2.1 Sonnet chain; under §10, run_flags.enforced_model>`):
    > "Fix the review findings for this brief:
    >
    > Task description: [doc writing for <KEY>]
    > Reviewer or style-checker output: [paste the triaged survivor list from the triage sub-step above — the surviving `doc-reviewer` findings only, never the dismissed or unverified ones]
    > Project root: [the resolved docs_repo_path (Phase 0)]
    > Severities to fix: BLOCKER and MAJOR"

  MINOR / NIT findings are deferred to the Phase 9 report.

- **PASS** — proceed to Phase 8.

Cap: one fix cycle + one re-review maximum.

**The recorded verdict names the version it was taken against** — where any edit followed it, the final report says so and names the edits, per the `A recorded verdict names the version it was taken against` rule in `Skill(skill: "workflows-core:reference", args: "escalation-rules")`. Where none did, it says that too.

---

## Phase 8 — Post-implementation maintenance

**First remove this run's temp files.** Nothing from here on reads one — Phase 6.3's `doc-writer`
handoff file — one path, which a `BLOCKED` return has that phase rewrite in place — and, where
Phase 7's BLOCK branch wrote one, its `claims_file`. Remove each as `command rm -f -- "<path>"`: `command`
because the Bash tool's shell carries the user's aliases and shell functions, and an `rm -i` or `rm -I`
of theirs would ask before removing the file, be answered no from that shell's empty standard input,
and leave it behind; `--` ends `rm`'s options. Nothing else removes one — they sit under the system's
temporary directory, outside every repository, where no later phase and no later run looks. A run that
stops before this phase removes the files it had made, in the same way.

Then gather the change context:

a. Run `git -C <docs_repo_path> diff --stat` against the base branch (if branching happened at Phase 6.2) or against HEAD (if no branching) and capture the list of changed files.
b. Compose a **change summary block**:

```
Implementation: [one-sentence description of what was documented, naming <KEY>]
Change type: docs
Classification: SIGNIFICANT
Files changed (from git diff --stat):
<paste the git diff --stat output>
Notable additions/removals: [new pages, new sections, new snippets, new cross-links, restructured navigation — one line each; or "none"]
Doc-review verdict: [PASS | PASS WITH RECOMMENDATIONS | BLOCK]
```

Then spawn all four Phase 4-style maintenance agents in a **single Agent message**. They are independent and run concurrently.

**Agent 1 — Documentation** (general-purpose, model: `<detection_model — §9 / §2.1 Sonnet chain; under §10, run_flags.enforced_model>`):
> "Post-write documentation review. Change summary:
> [paste change summary block]
>
> Scan for README.md, CHANGELOG.md, docs/, or any .md files in the project root or an adjacent docs tree.
> Determine if *other* documentation needs updating as a consequence of this write (e.g., an index page, a cross-referenced overview, a changelog entry in the repo root). Do NOT touch release-notes / what's-new pages — those are generated by automation.
> - Skip if: the edit is confined to the intended target pages with no inbound cross-references.
> - Update if: new page requires an index/sidebar entry, new sections require inbound cross-links.
> If an update is warranted: apply minimal edits to the relevant section(s).
> Return: file updated and what changed, OR 'no update required (reason)'."

**Agent 2 — Knowledge base** (general-purpose, model: `<detection_model — §9 / §2.1 Sonnet chain; under §10, run_flags.enforced_model>`):
> "Post-write knowledge review. Change summary:
> [paste change summary block]
>
> Check ~/.claude/memory/ (global) and .claude/memory/ (project-level, preferred for repo-specific knowledge) for existing knowledge files.
> Determine if a new knowledge entry is warranted — look for: reusable insights about this docs repo's conventions, non-obvious style rules uncovered, Vale / lint interactions, snippet patterns, image-policy discoveries.
> If YES: identify the most appropriate existing file (never propose a new file if an existing one fits) and return a proposed edit — write nothing. The entry format:
> ### [Short title]
> - **Context**: what problem/situation triggered this
> - **Insight**: the learned rule, pattern, or gotcha
> - **When it applies**: conditions under which this matters
> - **Date**: YYYY-MM-DD
> - **Ref**: [first 60 chars of the key + feature summary]
> Return: `{file, anchor, replacement, reason}` — `anchor` is the exact existing text to change, or the section to append to; `replacement` is the entry above in full; `reason` is why it's warranted — OR 'no update required'."

**Agent 3 — Instructions** (general-purpose, model: `<detection_model — §9 / §2.1 Sonnet chain; under §10, run_flags.enforced_model>`):
> "Post-write instructions review. Change summary:
> [paste change summary block]
>
> Check CLAUDE.md in the project root and ~/.claude/CLAUDE.md (global).
> Determine if any doc-writing rules, guidance, or guardrails are missing because of what this run revealed (e.g., a repo-specific frontmatter field that must always be present, a cross-link pattern that's easy to miss, an image-policy rule that caught you out).
> Skip if: the run followed existing conventions with no surprises. Only update if a concrete, recurring rule would have prevented a decision point or misunderstanding.
> If YES: keep it minimal, additive, and scoped — do not propose rewriting sections wholesale — and return a proposed edit — write nothing.
> Return: `{file, anchor, replacement, reason}` — `anchor` is the exact existing text to change, or the section to append to; `replacement` is the proposed new/changed text; `reason` is what this run revealed that warrants it — OR 'no update required'."

**Under `run_flags.skip_feedback`** (`workflows-core:run-flags` §4), dispatch `workflows-core:defect-reporter` instead of Agent 4 (`impl-maintenance`), with the same handoff plus `Plugin root: ${CLAUDE_PLUGIN_ROOT}` (literal — it expands in command bodies to this command's own plugin location), and `model: <§2.1 Sonnet chain, or run_flags.enforced_model>`; if it returns at least one defect, persist them with `emit-bugs` (`Skill(skill: "workflows-core:reference", args: "feedback-emission emit-bugs")`) in place of `emit-auto`, otherwise load nothing. Surface `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` in the Phase 9 report's Session learnings line, in place of the persisted-path line. Capture-at-block (`emit-block`) is unaffected by the flag.

**Agent 4 — Session maintenance** (workflows-core:impl-maintenance, model: `<detection_model — §9 / §2.1 Sonnet chain; under §10, run_flags.enforced_model>`):
> "Analyse this session and return a Lessons Learned report.
>
> Session handoff:
> - Command run: /document (keyed mode)
> - What was done: [one-paragraph summary of the documentation produced]
> - Key events: [BLOCK reviews encountered and their reason, ambiguous image policies, unresolved refs, style-check failures, branch-naming conflicts — or 'none']
> - Workarounds used: [manual steps not automated by the workflow — or 'none']
> - Review verdict: [PASS | PASS WITH RECOMMENDATIONS | BLOCK]
> - Test result: N/A (no tests in /document)
> - Project root: [the resolved docs_repo_path (Phase 0)]"

Collect all four summaries for the Phase 9 report.

**Persist plugin feedback (automatic).** After Agent 4 (`impl-maintenance`)
returns, project its plugin-facing slice into the specs repo by invoking `Skill(skill: "workflows-core:reference", args: "feedback-emission emit-auto")` and calling its `emit-auto` entry point (§6). Pass Agent 4's Lessons Learned report,
`command: /document (keyed mode)`, the run's `key` and `source`, and
`plugin_version` (read from
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). `emit-auto` renders only
the report's **Command workflow improvements**, **New agents / skills**, and
plugin **Reference docs** sections plus the **Key observations** that
triggered them (§4 plugin-facing predicate) — never target-project
`CLAUDE.md`/hook advice — as `origin: auto` entries, dedupes by stable `id`
(§3), resolves the target via the §2 specs-first ladder, and writes silently.
List the persisted path (or "no plugin-facing signal — nothing persisted") in
the Phase 9 report's Session learnings line. ADDITIVE — the impl-maintenance
report still appears in the report; this step NEVER fails the run, NEVER
commits (still true — this step only writes the feedback file; those writes
are committed by the separate terminal `commit-artifacts` step, per
`workflows-core:specs-repo-git` §4), and NEVER writes
into the docs repo or the current working directory, where it is not the specs repository.

---

## Phase 8.5 — Finish & handoff

Run this phase only when Phase 6.3 wrote + committed in a git repo (write context `docs_repo`, or `non_docs_repo` confirmed at Phase 0) — i.e. a branch with this run's commits exists. Skip otherwise (nothing to hand off). Mechanics: `${CLAUDE_PLUGIN_ROOT}/references/finish-and-handoff.md`.

### Step 1 — Squash (always)

Fold the run into clean history before handoff, every git call as `git -C <docs_repo_path>` (Phase 6.2):
1. Stage the run's uncommitted docs-repo edits — Phase 8 Agent 1 (doc index / cross-links) may have edited without committing; the Phase 6.2 clean-tree check means everything uncommitted is this run's work.
2. Compute the squash base: if Phase 0 recorded `profile_commit` (inline-profiling run), base = `profile_commit` (keeps the profile-config commit as a distinct first commit → two commits); otherwise base = `git -C <docs_repo_path> merge-base <base_branch> HEAD` (one commit).
3. `git -C <docs_repo_path> add -- <each path under docs_repo_path this run wrote or edited>` → `git -C <docs_repo_path> reset --soft <squash-base>` → one `git -C <docs_repo_path> commit`. Never a path outside the docs repository — the implementation-gaps draft, a staged screenshot, or Phase 8's feedback file under `$SPECS_PATH` — which git refuses along with every other path in the same `add`. The message follows `profile.commit_convention` when present (example-docs: `<KEY> <summary>`); for a repo with no such field, infer from recent `git -C <docs_repo_path> log` / `CONTRIBUTING`, else fall back to `<KEY> <summary>`. NEVER put the key in a reader-visible changelog — see `workflows-core:doc-structure-conventions` §1.

### Step 2 — Offer push

```
choices: ["Push <branch> to origin now", "Skip — I'll push later", "Cancel"]
```
- **Push** → `git -C <docs_repo_path> push -u origin <branch>`; report the result. (`git push` is git-protocol, not a REST API — the zero-external-API invariant is preserved.)
- **Skip** → "Branch `<branch>` ready with N commit(s). Push when ready."
- **Cancel** → stop and summarise.

### Step 3 — Copy-paste PR draft (always; no API)

Per `${CLAUDE_PLUGIN_ROOT}/references/finish-and-handoff.md` §4–§5:
1. **Detect the host** from the docs repo's `git -C <docs_repo_path> remote get-url origin` (Bitbucket Cloud / Bitbucket Server / GitHub / other).
2. **Compose the draft**: title (per `commit_convention`); body — what was documented, the output files, the Phase 6.5 render-verification summary, deferred style/review/render items, a link to the PRD. When Phase 5.8 recorded any `document-as-spec` / `skip-and-report` decision, prepend a banner: `> ⚠ DO NOT MERGE until <KEY>-implementation-gaps.md is resolved.` A qualifying `document-as-code` decision (§7.5) does NOT get this banner even though it also produces a gaps file — the docs correctly describe what shipped, so the PR is mergeable; only the source ticket needs correcting.
3. **Write + show**: write `pr-draft.md` to the resolved PRD folder (ask if none) AND print it.
4. **Host footer**: Bitbucket → "open a PR in the web UI and paste the title + body"; GitHub → additionally offer `gh pr create --title '<title>' --body-file <pr-draft path>` that the user may run, its title quoted as `finish-and-handoff.md` §5 says; other → "open a PR and paste the title + body". Bitbucket offers no CLI to open one — a host capability limit, not a policy: the family does open a pull request where a host offers a CLI (`workflows-core:phase-handoff` §2.6 in `$SPECS_PATH`, `dev-workflows:code-handoff` §2.6 in a code repo), and no command of this plugin opens one anywhere, this docs repo included.

Carry the squash result, push outcome, and PR-draft path into the Phase 9 report.

---

## Phase 8.6 — Maintenance proposals

Runs **after** Phase 8.5 — never before. The ordering is the whole safety property, and it holds whether or not Phase 8.5 ran: once this phase starts, **the run will create no further commit in the docs write target** — either Phase 8.5 sealed the docs commit, or the write context never commits at all (`obsidian` / `plain_dir`, per the Phase 6.3 branch/commit table — which governs the docs write target only, never `$SPECS_PATH`). Either way an accepted `CLAUDE.md` (or knowledge-base) edit has no commit left to ride. What still commits after this point is the terminal `commit-artifacts` step, which stages ONLY `$SPECS_PATH`'s bounded artifact paths (`workflows-core:specs-repo-git` §2.1) — it can never pick up a `CLAUDE.md` or knowledge-base edit, so the safety property holds unchanged.

Skip this phase with no prompt when both Phase 8 Agent 2 and Agent 3 returned `'no update required'`.

Otherwise present one row per proposal:

| File | Rule / entry | Reason |
|---|---|---|
[one row per Agent 2 / Agent 3 proposal — `file`, the rule or knowledge entry in one line, `reason`]

```
choices: ["Skip — report only (Recommended)", "Apply all", "Choose per proposal", "Cancel"]
```

- **Skip — report only** — apply nothing; every proposal's disposition is `proposed` for the Phase 9 report.
- **Apply all** — apply every proposal via the mechanism below; every proposal's disposition is `applied-uncommitted`.
- **Choose per proposal** — ask accept/decline for each proposal; apply the accepted ones (`applied-uncommitted`), leave the rest `declined`.
- **Cancel** — apply nothing; every proposal's disposition is `proposed`. Unlike every other "Cancel" in this command, **Cancel here does not abort the run**: by the time this phase runs there is nothing upstream left to unwind — Phase 8.5's squash (and any push / PR draft) is already done, or the write context never committed at all (`obsidian` / `plain_dir`) (still true — what still commits after this point is the terminal `commit-artifacts` step, bounded to `$SPECS_PATH`'s artifact paths per `workflows-core:specs-repo-git` §2.1, and therefore never able to carry a proposal from this phase). Cancel only declines this phase's proposals; the run proceeds to Phase 9 and the Final Report is produced exactly as it would be after Skip.

**Apply mechanism.** For each accepted proposal, re-dispatch the agent that produced it — Agent 2 or Agent 3, same general-purpose agent and model as Phase 8, no new agent type — in apply mode, carrying its own proposal back verbatim:

> "Apply this proposed edit exactly as returned — do not re-derive it:
> `{file, anchor, replacement, reason}`: [paste the proposal]
>
> Locate `anchor` in `file` and write `replacement` in its place (or append it, if the proposal is an append). Return: file written, OR a mismatch note if `anchor` no longer matches the file's current content — do NOT guess at the intended location; skip and report the mismatch."

Applied edits are left **uncommitted** — deliberately. Do NOT stage, commit, or re-run Phase 8.5 for these files: in a repo where a `CLAUDE.md` change triggers a review of its own, long enough to delay the documentation it would otherwise ride with, that change needs its own PR on the user's timing. A later `/document` run's Phase 6.2 clean-tree check will trip on these uncommitted files until the user commits or discards them — that is intended, not a bug to fix.

Carry each proposal's `{file, reason, disposition}` into the Phase 9 report.

---

## Phase 9 — Final Report

Output a structured report — do NOT ask any closing confirmation:

```
## keyed Documentation Report

### Classification
SIGNIFICANT — keyed feature documentation has large blast radius if wrong

### Model Routing
- Session / writer model (current_model): [model] — [if it ran degraded: "Sonnet; user proceeded past the Phase 1.5 advisory" | "Sonnet; no Opus available" | "on §2 chain — no degradation"]
- doc-planner synthesis (planning_model): [model]
- Detection steps — the folder read, diff-summarizer, doc-location-finder, docs-style-checker, doc-fixer, maintenance (detection_model): [model]
- doc-reviewer (review_model): [model]
- Opus available: [yes | no]
- [Under `run_flags.enforced_model`: `Model routing: bypassed — enforced <id> (flag|env)` in place of the three dispatched-step lines above (doc-planner synthesis, Detection steps, doc-reviewer) — each already equals the enforced id, per `workflows-core:model-routing/classification` §10. `current_model` and `Opus available` are unaffected by enforcement (§10: the orchestrator stays on the session model, and `opus_available` is a property of the environment) and are reported above exactly as they stand.]
- Run flags: [the `Run flags: …` line, repeated, whenever Phase 0 printed one during this run (`workflows-core:run-flags` §6) — omit this line otherwise. The `Session feedback: …` skip line, where it fires, is carried in the Session learnings (Agent 4) line below; the `Session cost: …` skip line is Phase 11's own output, printed after this report and not restated in it.]

### PRD folder summary
- PRD: [<PRD>] [summary, 1 line]
- Epic: [focus_key] [its title, 1 line] — omit the line when `focus_key` is null (a PRD-level run)
- Epics: [count of `EPIC-` folders in the resolved PRD folder — the tree stops there (Phase 3)]
- Themes: [2–4 bullet points from the folder read]

### Repos analysed
- <repo-1> (<resolved repo_path>) — [N refs in scope, M resolved, K unresolved]
- ...

### Refs in scope
[One line per **resolved** `per_pr` element `diff-summarizer` returned, then one per `unresolved_prs` element — an element that resolved to nothing is printed once, from the second list. Every field below is from that agent's own Output block: it returns **no per-element `status`** — its `status` is per repo, and Phase 4 step 1 has already said there is no PR status to filter on — and `ref` is the only thing that identifies an element, `refs[]` being the only element list that agent takes.]
- <repo> — <ref> — resolved_via: [local_ref | key_commits] — [files_changed] file(s), +[insertions]/-[deletions]
- <repo> — <ref> — unresolved: [reason from `unresolved_prs`]
- ...

### Branch-name probe
[Phase 3's *Report the scan's own reach* step, one line per repository the whole-key commit scan left at zero matches — the only repositories it runs on. Omit the section entirely when it fired nowhere.]
- <repo> — [each commit by SHA, date and subject — may name a key inside a branch name or in a merge commit, inspect by hand | matched nothing]
- Nothing here was read: no commit above reached `diff-summarizer`, joined the refs, or is reported as unrecorded work.

### Output file(s)
- [absolute path] — [kind: extend-existing | new-page-in-existing-section | new-section]
- ...

### Branch
[branch name created in Phase 6.2, e.g. docs/<key>-<slug>] OR "N/A — no branch created (context: obsidian / plain_dir / user declined branching)"

### Verification gates
| Gate | Outcome | Mechanism | Detail |
|---|---|---|---|
[One row per gate in the `gate_ledger`, in registry order (`references/gate-ledger.md` §4). "Detail" carries the row's `ci_still_checks` (DEGRADED, or FAILED with a degraded or declined part — `gate-ledger.md` §2), `user_decision` (SKIPPED_BY_USER, or FAILED with a declined part), or `precondition_unmet` (NOT_APPLICABLE) — empty otherwise. When any row carries a `ci_still_checks`, follow the table with a one-line warning naming what CI will check that this run did not — or, where a row's `ci_still_checks` says none runs, that nothing will.]

### Render verification
- Build: [one entry per build Step 1 resolved, named by its `id` (or space) — ran — pass/fail | not run (the environmental failure, e.g. `<tool>` is not installed) — the boot of its own server served as the proof | unverified (reason)] OR "no build command in profile — boot served as the proof" (does NOT apply to example-docs, which defines per-space build commands)
- Smoke-check: [per space, and per server where a space has two — passed (N pages, HTTP 200) | skipped (reason) | stopped (reason, and what that ending's own record names — `render-verification.md` §2, **The endings**); then every ❌ page with its URL — 404: on the manual table | 5xx: render defect] OR "not run (user skipped)"
- Pages to visit: [the Phase 6.5 Step 3 table]

### Doc review verdict
[PASS | PASS WITH RECOMMENDATIONS | BLOCK] — [1-line summary of findings applied / deferred]

### Review triage
- **Review triage:** [one line per review pass, per `workflows-core:finding-triage` § Reporting — N findings reviewed: M survived, U unverified, X dismissed (C carried, on a re-review)] — survivors: [on a re-review, `finding — severity` per survivor, or "none"; "N/A (first review)" otherwise] — dismissals: [`finding — reason`, or "none"] — unverified: [`finding — if-true severity — what would settle it`, or "none"] — raised: [`finding — from → to — effect`, or "none"] — settled: [the answer given at a settle prompt, or "not asked"]

### Documentation (Agent 1)
- [file updated] — [what was added/changed] OR "no update required (reason)"

### Knowledge base (Agent 2)
- [file, rule/entry summary, reason] — disposition: [proposed | applied-uncommitted | declined] OR "no update required"

### Instructions (Agent 3)
- [file, rule/entry summary, reason] — disposition: [proposed | applied-uncommitted | declined] OR "no update required"

### Maintenance applied (uncommitted)
[Every Phase 8.6 proposal with disposition `applied-uncommitted` — file, one-line summary, reason — one per line. These edits are deliberately excluded from the Phase 8.5 docs commit: a repo-governance file like `CLAUDE.md` needs its own PR on the user's timing, not a ride on this run's docs commit. Run `git status` in the docs repo to review before committing them separately. OR "none".]

### Session learnings (Agent 4)
- [top suggestions from impl-maintenance agent, or "no suggestions — routine session" — or, under `--skip-feedback`, `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` / `— no defects` in its place]

### Screenshots to upload manually
[Only populated for the **Defer** path of Phase 6.1 — i.e. a target used image_policy: cdn_upload_required (a target whose ambiguous policy Phase 5.7's **Ambiguous image policy** step, or Phase 6.3's `BLOCKED` loop after it, resolved to "Stage for manual upload to the repo's image-management tool" included) AND the user chose "Defer — stage with TODO placeholders" at the Phase 6.1 CDN handoff, or where Phase 6.3's loop asked it. For each staged screenshot: src (original user-provided path), staging path under <screenshot_staging_dir> (the staging directory), the target page it belongs on, the proposed alt-text, and the upload_note from the planner. Omit this section entirely when no screenshots were staged — including when the user chose "Upload now" in Phase 6.1 (those images carry real CDN URLs in the markdown and need no manual step).]

### Implementation gaps (PRD vs source)
[Populated when Phase 5.8 produced any `document-as-spec` / `skip-and-report` decision, **or** any qualifying `document-as-code` decision (per `workflows-core:source-truth` §7.5 — the PRD phrasing asserts a specific value that contradicts the source). All three write the same bug-report draft, so all three are listed here; the status line differs by decision:
- `document-as-spec` / `skip-and-report` → "Bug-report draft written to <path>. If docs were branched, DO NOT merge the PR until these gaps are resolved."
- qualifying `document-as-code` → "Bug-report draft written to <path>. Documented as shipped; the source ticket carries an incorrect claim — correct the ticket, no PR block."

List each gap (claim, decision) with its own status line — never print the DO-NOT-MERGE sentence for a `document-as-code` gap, and never print it at all on a run whose only gaps are `document-as-code`: the docs describe what shipped, the PR is mergeable, and Phase 8.5 deliberately withholds the PR banner for exactly this case. Omit the section when there were no discrepancies.]

### Skipped items
[Gaps the planner flagged with recommended_action: "skip with note in final report" — one line each; or "none"]

### Deferred items
[List first, each tagged **MAJOR — incomplete swap, invisible in the diff**: any accepted existing-image swap `doc-writer` skipped because the file's occurrence no longer matched `old_url` (its `notes` return — the position went stale between Phase 5.6 and Phase 6.3). This is distinct from the items below — it's a race that left an already-accepted decision unfulfilled, not a routine low-priority deferral. Then: MINOR / NIT findings that were not applied, OR user-declined screenshots, OR doc-reviewer BLOCK findings that were overridden / deferred — one line each; or "none"]

### Assumptions & limitations
- [list any — including, where Phase 0 step 4(c)'s inline profiling handed them back, its `fixed_port_servers` and `server_command_defects` lines, each as it was printed there]

### Git state
[When Phase 8.5 ran: "Branch <name> — squashed to N commit(s); pushed to origin: <yes/no>; PR draft: <pr-draft path>." When Phase 8.5 was skipped (no branch/commits): "Working tree has uncommitted changes. /document (keyed mode) writes but does not commit the docs write target in non-git contexts; this run's $SPECS_PATH session artifacts are committed separately by the terminal step."]

### Next step
[Per `workflows-core:next-phase-offer` — guidance only, never auto-invoked. Once **all** the PRD's Epics are documented, draft/finalize the release note → `/docs-workflows:release-notes <PRD>` (PRD-level; run once, not per Epic). If the review BLOCKED, resolve that first.]

### Context hygiene

The resume pointer is written in the terminal cost phase (Phase 11), per `workflows-core:session-hygiene` §1. Then:

- **On to `/docs-workflows:release-notes <PRD>` (still Dev — a spec or design exists by now, so this is the late run)?** → run **`/compact`** — context stays relevant.
- Consider **`/rename <PRD-ID>-<slug>-dev`** to relocate this session later.

Guidance only — see `workflows-core:session-hygiene`.
```

---

## Phase 10 — Emit follow-up tasks

Terminal phase — runs AFTER the Phase 9 Final Report is composed; NEVER
interrupts an earlier phase. Persist the run's out-of-scope / manual-step
follow-ups by invoking `Skill(skill: "workflows-core:reference", args: "followup-emission")` and executing its steps inline.

1. **Collect** the follow-up items already aggregated in the Phase 9 report:
   `### Screenshots to upload manually`, `### Implementation gaps (PRD vs source)`,
   `### Skipped items`, and `### Deferred items`.
2. **Filter** them with the reference's §6 qualifying predicate — emit only
   out-of-scope / manual-step signals; drop in-scope items the report already
   tracks.
3. **Resolve** the write target via §2 using the
   run's `key` and `source`; render + place tasks and verbose notes per
   §1–§3; dedupe per §5.
4. **Preview + confirm** per §7 (`approve-all | select | cancel`), then write.

ADDITIVE — the follow-ups also remain in the Phase 9 report, as they
do without this phase. This phase NEVER fails the run, NEVER commits (still true — this
phase only writes follow-up files; those writes are committed by the separate
terminal `commit-artifacts` step, per
`workflows-core:specs-repo-git` §4), and NEVER writes
into the docs repo or the current working directory, where it is not the specs repository.

---

## Phase 11 — Session cost

Terminal phase — the NEW final operational phase; runs after Phase 10 (the
follow-up phase) and NEVER interrupts an earlier phase. Records this command's
token-cost contribution to the PRD — through `emit-cost`, or, under `run_flags.skip_costs`, by advancing the checkpoint alone. Unlike feedback, **cost ALWAYS runs** — unless `run_flags.skip_costs` (see below) — it never "writes
nothing".

**Under `run_flags.skip_costs`**, do not call `emit-cost` and do not load `cost-emission`: execute `skip-cost` (`Skill(skill: "workflows-core:reference", args: "run-flags skip-cost")`) instead, which advances the checkpoint and drops any deferred record, and surface `Session cost: skipped (--skip-costs)` (or `(WORKFLOWS_SKIP_COSTS)`). The resume-pointer write and the terminal `commit-artifacts` step below run unchanged either way.

Otherwise (not skipping), invoke `Skill(skill: "workflows-core:reference", args: "cost-emission emit-cost")` and call `emit-cost` with `command: /document (keyed mode)`, `phase: documenting`,
`role: dev`, the run's `key` and `source`, and `plugin_version` (read from
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). It resolves the session
transcript + subagents (§1), loads and **advances the chained checkpoint** (§3),
computes the per-model token-cost delta against
the price table (§4), records the optional statusline cross-check (§5), and
appends one per-invocation entry to `<PRD-dir>/dev-workflows/cost/<sid8>.md` via
the specs-first ladder (§8). Keyed mode always resolves its folder — an absent one is a stop in the Mode detection section — so that is where the entry lands whenever `$SPECS_PATH` is writable, never in pending; with a key resolved, §9's opportunistic move-then-delete reconciliation offers any pending files earlier keyless runs left. **The checkpoint advances in every tier, report-only included.** Surface the persisted path (or the
report-only notice) as this phase's only output.

**Then write the resume pointer.** Invoke `Skill(skill: "workflows-core:reference", args: "session-hygiene")` and, per its §1, write/overwrite
`<PRD-dir>/dev-workflows/resume.md` now — after the cost entry above, so the
pointer reflects the completed run, and before the commit step below, so it
is included in it. Redact per §1. Silent; the printed `### Context hygiene`
guidance already appeared in the Phase 9 report.

**Then commit session artifacts (terminal).** Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git commit-artifacts")` and execute its `commit-artifacts` entry point (§4) inline — the LAST action of the
run. It stages ONLY the §2.1 bounded artifact paths inside `$SPECS_PATH`,
commits `<KEY> Add dev-workflows session artifacts (/document)`, and pushes
per §4 step 5. It NEVER writes into the docs repo this run just changed —
the documentation commit, branch, and PR are untouched — NEVER touches a
code repo, anything outside `$SPECS_PATH`;
NEVER force-pushes; NEVER fails the run; and skips entirely when the run carries
`specs_git: blocked` (§3.3 G0) or `specs_git: misrooted` (§3.1, or `specs-root-check`'s stop), re-emitting that notice. Because the Phase 9
report was composed before this phase, **print its §6 outcome line here**,
as the run's last output — prefixed `Specs repo:`, with any guard notice
repeated in full.

ADDITIVE — this phase NEVER fails the run, NEVER commits the deliverable (the
documentation commit, branch, and PR are handled in Phase 8.5; the terminal
step above commits only the bounded session-artifact paths in `$SPECS_PATH`),
and NEVER writes into the docs repo or the current working directory, where it is not the specs repository; no user
name is ever written (§10 privacy).

---

## Invariants (always enforced)

- ALWAYS `emit-block` (per `workflows-core:feedback-emission`) before escalating a halt caused by a **plugin / skill / command / reference gap** (a capability the run needed but the plugin lacked) — so a run abandoned at the block still records it. NEVER for a work-quality review BLOCK or an environment / user halt (repo-missing, dirty-tree, key-not-found, cancellation, and Mode A Phase 0 step 1's named stops on a folder that resolved — `DOCUMENT_BRD_NOT_SLICED`, `DOCUMENT_FOLDER_NOT_PLACED`, `DOCUMENT_PRD_NO_KEY` and `DOCUMENT_NO_PRD`, each reporting the operator's own tree). The one exception is a halt on a tool the ai-containers image lacks, which `workflows-core:feedback-emission` §6 `emit-block` defines.
- ALWAYS run Phase 0 docs-repo detection; if 0 signals, require user confirmation before proceeding
- NEVER call a forge's REST API directly over HTTPS, on any host. A keyed run has no forge URL to resolve in the first place: it passes `refs[]` only (Phase 4 step 6), and `diff-summarizer` takes a `refs` element's diff with pure local `git`. The one forge command this command names is the `gh pr create` Phase 8.5 offers the **user** for the run's own pull request, and `gh` wraps the API rather than calling it directly
- NEVER write inside `_archive/` — that path is read-only by convention
- NEVER write product documentation outside the resolved `docs_repo_path` (Phase 0). Outside the docs repository and its remote the run writes these and nothing else: the resolved PRD folder's two drafts, the `<KEY>-implementation-gaps.md` bug-report draft and `pr-draft.md`; a new image placed in the resolved PRD folder's `Doc screenshots/` (Phase 5.6), never its `attachments/`; screenshots staged under `<screenshot_staging_dir>`, and, for each one staged under `$SPECS_PATH`, one line in that repository's local exclude file (Phase 6.3); its session bookkeeping under `$SPECS_PATH`, with the commits, pushes and branch moves `specs-preflight` and `commit-artifacts` make there (`workflows-core:specs-repo-git`), and the session-cost checkpoint Phase 11 advances under `~/.claude/dev-workflows/cost-state/` (`workflows-core:cost-emission` §3); its temporary files, each made by `mktemp` — Phase 6.3's handoff file and Phase 7's claims file, removed at the top of Phase 8, and Phase 6.5's smoke logs, each removed as `render-verification.md` §2 step 5 removes one, save a log that step keeps because it could not show its server stopped, which the record naming it leaves in place; the refresh Phase 1 chose for the resolved code clones, in their own git state (Phase 5's `diff-summarizer`, its Refresh step); whatever the tools it invokes write of their own accord — the repository's own linter, build and server commands, which Phases 6.4 and 6.5 run, above all; and, only behind Phase 8.6's own consent, each accepted Agent 2 or Agent 3 proposal, written to the file that proposal names — which may lie outside every repository, `~/.claude/CLAUDE.md` or `~/.claude/memory/` among them.
- ALWAYS escalate missing repos before proceeding — never silent skip
- ALWAYS invoke `docs-style-checker` (Phase 6.4) before `doc-reviewer` (Phase 7)
- ALWAYS run the Phase 0 toolchain preflight (`${CLAUDE_PLUGIN_ROOT}/references/toolchain-preflight.md`) after profile resolution and before Phase 1; it prompts only when a required tool is missing
- ALWAYS run `specs-preflight` in the shared `## Mode detection` section, before dispatching to either mode — so it runs for Mode B as well as Mode A — and again, with the slice's key set, where Phase 0 step 1 re-enters for a slice the operator entered at `DOCUMENT_BRD_NOT_SLICED`; and `commit-artifacts` as the run's last action (per `workflows-core:specs-repo-git`) — bounded to `$SPECS_PATH`'s artifact paths (§2.1) and to plugin-created branches (§2.2), always `git -C "$SPECS_PATH"` and never a `cd` (§1 rule 1), never force-pushing, and never failing the run
- ALWAYS append each gate's ledger row at the moment that gate completes, per `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` — NEVER reconstruct the ledger at Phase 9, and NEVER leave a registry gate without a row
- NEVER present a phase's `choices:` array in an order, wording, or recommendation other than the one written; the "Choice lists are presented verbatim" rule in `workflows-core:escalation-rules` binds every prompt in this command
- ALWAYS invoke `doc-reviewer` before Phase 8 maintenance
- ALWAYS resolve the `model_routing` block at Phase 1.5 and pin each subagent dispatch to its §9 chain via `model:` — `doc-planner` to the §2 Opus chain, the mechanical steps (the folder read, `diff-summarizer`, `doc-location-finder`, `docs-style-checker`, `doc-fixer`, maintenance) to the §2.1 Sonnet chain; `doc-reviewer` keeps its frontmatter Opus pin (no override unless §10 enforces a model); the inline writer + gates run on `current_model` (advisory only)
- ALWAYS cap review/fix cycles: 1 fix + 1 re-review max
- ALWAYS pass `Change type: docs` in the Phase 8 change summary block
- ALWAYS pass `Command run: /document (keyed mode)` in the Phase 8 Agent 4 session handoff — the mode-qualified name this run already passes `emit-auto` in the same phase and `emit-cost` in Phase 11, and what keeps a returned phase-numbered suggestion resolvable between two modes that each number from their own Phase 0
- ALWAYS spawn Phase 8 agents in a single message — never sequentially
- ALWAYS use `choices` arrays for decision points; 2–4 options, and never author an "Other" option — the harness supplies the free-text escape itself (`workflows-core:escalation-rules` §0)
- ALWAYS produce the Phase 9 report as the final output
- ALWAYS end the Phase 9 report with a `### Next step` recommendation (per `Skill(skill: "workflows-core:reference", args: "next-phase-offer")`) — guidance only, never auto-invoked; omitted in direct doc-edit mode (Mode B)
- ALL written claims must be traceable to a resolved key or to a summarised diff — attribution goes in the run's return payload and the commit message, NEVER inline in the rendered page (`workflows-core:doc-structure-conventions` §1)
- For `image_policy: cdn_upload_required`, NEVER copy user-provided screenshots into the repo — stage under `<screenshot_staging_dir>` — the resolved PRD folder's screenshot subfolder by default, else a directory the operator names (Phase 1); never the docs repo, never `/tmp` — and surface in the Phase 9 `### Screenshots to upload manually` section
- ALWAYS end the Phase 9 report with a `### Context hygiene` block per `workflows-core:session-hygiene` — prepare-first (the `resume.md` write runs later, in the terminal cost phase, per `workflows-core:session-hygiene` §1 — this block prints the guidance only), then a docs→PM handoff suggestion (`/clear`) + `/rename <PRD-ID>-<slug>-dev`; guidance only, never auto-run. **Mode B (direct doc-edit) omits this** — no PRD context.

---

# Mode B — direct documentation edit (`@file` / free-text)

Implement the following doc edit: $ARGUMENTS

If the argument starts with `@`, treat it as a path to a markdown file. Resolve relative to the current working directory. Read its full content and use it as the description. Echo `📄 Reading prompt from \`<file>\`…` before proceeding. If the file cannot be read, stop and report the error immediately.

`/document` (direct mode) is the **one-shot doc-editing** workflow — minor edits, formatting, small updates to existing pages, and single-file additions where the content comes from the user's description alone. It is the right tool when:
- the change is small and the content is already in the user's head or the file, **not** scattered across PRD sections and the diffs behind them
- no tests, no branch (still true — the specs-repo preflight creates none, `workflows-core:specs-repo-git` §2.2), no code review, and no commit of the doc edit are warranted

For net-new documentation assembled from a PRD folder plus the diffs its implementation record names, use keyed mode (above). For writing child Epic drafts from a Product Requirements Document, use `/product-workflows:epics`.

No model-routing reminder is injected for this command — classification still happens but is always SIMPLE or MODERATE, and Opus is never invoked, unless `run_flags.enforced_model` names one (`workflows-core:model-routing/classification` §10): every dispatch below then carries the enforced id in place of the Sonnet chain, bypassing this mode's own Opus-never rule because the user explicitly chose it.

---

## Phase 0 — Load the description

1. If `@file` syntax: read the file, confirm `"Loaded prompt from <filename.md> (N lines)."`, note any embedded images as "referenced image: <path>". Otherwise use the inline text verbatim.

2. **Initialize the ledger.** Create the run's `gate_ledger` block per `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` §3 — unconditionally, before the git-tree check below. Direct mode registers three gates (`gate-ledger.md` §4); each needs a row even when this run cannot lint anything.

3. **Resolve the edit target, then the toolchain.** Direct mode edits files, and **the repo it edits is not necessarily the one you are standing in**: `/document /workspace/docs` and `/document @/workspace/docs/guides/page.md` both name a tree that may differ from cwd. Resolve the target first — a directory argument is the target; an `@file`'s directory is the target; free-text prose naming no path leaves cwd as the only anchor available, which is legitimate because there is nothing else to resolve. Then

   `repo_root` = `git -C <target> rev-parse --show-toplevel`

   — **never `git rev-parse --show-toplevel` from cwd.** Anchoring on cwd is how a run derives its toolchain and its checklist from one repository while writing into another, which is exactly what it did when invoked as `/docs-workflows:document /workspace/docs` from a different clone: the preflight read the repo it was standing in and the style check ran against the repo it was editing.

   `site_root` is the site the target sits in, where the target is in a git work tree and that site lies below `repo_root`: walk up from `<target>` towards `repo_root` and take the first directory that itself holds one of the docs signals Mode A's Phase 0 step 2 lists. A monorepo's `website/` keeps its `.vale.ini`, lockfile and lint configuration beside itself, not at the top level — the reason keyed mode hands its `docs_repo_resolved` on as well (Mode A's Phase 0 step 7, Phase 6.4). Where the first such directory is `repo_root` itself, or none is found below it, there is no site below the top level, and `site_root` is not set.

   **Confirm writeable.** Run `test -w <repo_root>`. If it fails, stop with the named error `REPO_NOT_WRITEABLE: <repo_root> is not writeable.` — the same stop Mode A raises in its own Phase 0, for the same reason. Direct mode writes files, so a read-only mount otherwise surfaces as a raw `EROFS` from the editor in Phase 3, **after** the exploration and the plan have already been paid for, naming a temp file rather than the condition.

   Then execute `${CLAUDE_PLUGIN_ROOT}/references/toolchain-preflight.md` against it — with `site_root`, where
   one was set, as the site directory its source 2 also checks. Direct mode has no profile, so
   use **sources 2 and 3 only** (repo config signals and the repo's documented `Prerequisites`); the
   only gate a tool can be mapped to here is `style_check`, so neither `required_by` nor `fallback_for`
   ever names `build_check` or `render_smoke_check`. That is narrower than the mode's gate set: direct
   mode registers three gates in the ledger — `toolchain_preflight`, `repo_checklist` and `style_check`
   (`docs-workflows:gate-ledger`) — and the first two are not gates a tool is `required_by`, which is
   why only the third appears in this map.

   Append the `toolchain_preflight` row per
   `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` §3. Present the §5 prompt verbatim only when a
   required tool is missing; on "Cancel", stop with `TOOLCHAIN_UNAVAILABLE: <missing tools> not
   available in this environment.` When the resolved target is not a git tree there is no repo to lint: record `toolchain_preflight` as `RAN` with `mechanism: "no repo to check — the resolved target is not a git repository"` and `findings: 0` (its precondition is "always", so it is never `NOT_APPLICABLE`), record `style_check` and `repo_checklist` as `NOT_APPLICABLE` with `precondition_unmet: "the resolved target is not a git repository"`, then skip the rest of this step and the checklist extraction below and proceed — the ledger is complete and Phase 3.5 runs no gates.

4. **Extract the repo's pre-PR checklist.** Direct mode has no `doc-planner`, so the orchestrator does
   this itself. In the **same pass** that read the repo's guidance files for step 3's `Prerequisites`,
   follow `${CLAUDE_PLUGIN_ROOT}/references/repo-verification-gates.md` §2–§4 and build the
   `repo_verification_gates` block. Carry it to Phase 3.5, which checks the edited files against it and
   records the `repo_checklist` ledger row. An empty block is normal — record it and move on. Skip this
   step entirely when the resolved target is not a git tree (step 3 already skipped for the same reason).

**Specs-repo preflight.** Already run — the shared `## Mode detection` section executed
`specs-preflight` (`workflows-core:specs-repo-git` §3) before dispatching to
either mode, so it runs for Mode B exactly as it does for Mode A, and any `specs_git: blocked` or
`specs_git: misrooted` flag it set is carried into this mode too. Do not run it a second time.

---

## Phase 1 — Clarification

**Rule: Ask, don't guess. This rule is absolute.**

Before producing a plan, analyze the description for:
- Ambiguous scope or unclear boundaries (which file? which section? extend or replace?)
- Conflicting style guidance in the repo vs. the user's wording
- Multiple valid placements for new content
- Undefined target audience (end-user vs developer vs operator)
- Missing acceptance criteria (what makes this "done"?)

If **any** ambiguity exists, ask the user. Rules:
- Use `choices` arrays for every question — never plain text questions
- Every `choices` array carries 2–4 options, and never author an "Other" option — the harness supplies the free-text escape itself (`workflows-core:escalation-rules` §0), which is what allows free-text
- When a clearly superior default exists, make it the first choice and label it `"(Recommended)"`
- Group related decisions into a single question (minimize total questions)
- Do **not** proceed until all questions are answered

If **nothing** is ambiguous, skip directly to Phase 1.5.

---

## Phase 1.5 — Classify task complexity

Doc edits in this command are always either **SIMPLE** or **MODERATE**:

- **SIMPLE** — single file, small additions / fixes / rewording, no cross-file linking
- **MODERATE** — multi-file edit, non-trivial restructure, or content that needs internal cross-references

If your reading of the task lands closer to SIGNIFICANT or HIGH-RISK (multi-repo, net-new feature pages from a PRD folder, published-documentation blast radius that needs a reviewer gate), **stop and redirect the user** to keyed mode or `/epics`:
```
choices: ["Re-run under /docs-workflows:document (keyed mode) (for PRD-sourced feature documentation) (Recommended)", "Re-run under /product-workflows:epics (for Epic drafting)", "Proceed under direct mode anyway — I accept the simplified flow", "Cancel"]
```

State the classification and a one-line reason, then proceed to Phase 2A.

*(There is no Phase 2B, Phase 3B, or Opus review in this command. A mandatory Phase 3.5 style check runs after Phase 3. Phase numbering is kept aligned with `/implement` to make cross-referencing straightforward; the A-suffix on Phase 2A below is retained for symmetry, not because a Phase 2B exists for docs.)*

---

## Phase 2A — Plan

**Repo exploration** — Before writing the plan, spawn an exploration subagent to map the relevant docs and any sibling conventions:

→ Agent (subagent_type: "general-purpose", tools: Read/Glob/Grep only — no Bash, no Edit, model: `<Sonnet detection chain — claude-sonnet-5-5, fallback claude-sonnet-5 / 4-6 / 4-5; under §10, run_flags.enforced_model>`):
  "Given this doc-edit description: [paste the full description from Phase 0 or Phase 1 here], find and return:
   - Target file(s) and their current structure (headings, frontmatter, approximate size)
   - Sibling / adjacent pages that may need matching updates (cross-references, navigation files, index pages)
   - Style / naming / frontmatter conventions visible in 2–3 neighbouring files (e.g. YAML frontmatter fields, heading depth, `[[wikilink]]` vs `[text](url)` preference)
   - Existing reference docs that govern this content (e.g. `CONTRIBUTION.md`, `DOCUMENTATION-GUIDELINES.md`, `STYLE.md`)
   Return a structured summary — no edits."

**Wait for the agent's response before proceeding.** If the agent returns no relevant files or fails, gather the context yourself via Read/Glob/Grep before drafting the plan.

Produce a written plan with these sections:

1. **Classification** — `SIMPLE` or `MODERATE` (with reason)
2. **Goal** — one-sentence summary of the desired end state
3. **Approach** — chosen edit strategy and why (extend existing page vs. create new vs. restructure)
4. **Steps** — numbered, concrete edits
5. **Files to create/modify** — list with brief rationale for each
6. **Validation** — spot-check steps to run after the edit. Replace the `/implement` "Tests" section with this. Typical checks:
   - Heading structure renders correctly (no orphan H3 under H1, no skipped levels)
   - All `[[wikilinks]]` resolve to existing files in the docs tree
   - All `[text](relative-path)` links resolve on disk
   - YAML frontmatter parses (if the page has frontmatter)
   - `changelog:` or equivalent field updated if the repo's convention requires one
   - No broken inline image references
   - Spell-check / grammar only if the repo has a configured linter (e.g. Vale, markdownlint); do not run any linter that isn't already configured
7. **Assumptions** — decisions made without user input (must be minimal)
8. **Out of scope** — explicitly list what is NOT being done (e.g., "not renaming the file", "not updating sibling pages")

Then ask:
```
"Doc-edit plan ready. What would you like to do?"
choices: ["Approve & implement now (Recommended)", "Revise plan", "Cancel"]
```

- **Approve** → proceed to Phase 3
- **Revise** → ask what to change, update, re-show, re-ask
- **Cancel** → stop and summarize what was planned

---

## Phase 3 — Implementation

**Implement immediately. Do NOT ask "Should I implement?" or any variation.**

1. Work through each edit in order
2. Make precise, surgical changes — do not rewrite sections wholesale when a targeted edit is enough
3. Follow the repo's detected style conventions from the Phase 2A exploration; LF line endings
4. If a **new ambiguity** emerges mid-edit: STOP, ask with choices (2–4 options; the harness supplies the free-text escape), resume after answer
5. After all edits: run the Validation checks from the plan's step 6. Fix any failures caused by your changes (broken links, unparseable frontmatter, bad heading hierarchy).
6. **Do NOT run tests.** This command has no test phase — validation checks are all that's expected.
7. **Do NOT create a branch, and do NOT commit the doc edits.** The user manages git manually for doc edits. (The run's terminal `commit-artifacts` step is a separate repository — it stages ONLY `$SPECS_PATH`'s bounded artifact paths, per `workflows-core:specs-repo-git` §2.1 — and never the files edited here.)
8. Verify the outcome matches the approved plan.
9. Proceed to Phase 3.5.

---

## Phase 3.5 — Style check (mandatory)

**Skip this entire phase** when Phase 0 recorded direct mode's gates as `NOT_APPLICABLE` (the resolved target is not a git repository): do not dispatch `docs-style-checker`, do not check the repo checklist, and write no rows — the ledger is already complete and final. Proceed to Phase 4.

After writing the edits and before Phase 4, dispatch `docs-style-checker` on the changed file(s), against the repository Phase 0 step 3 resolved from the edit target, whichever repository cwd sits in:

→ Agent (subagent_type: "docs-workflows:docs-style-checker", model: `<Sonnet detection chain — claude-sonnet-5-5, fallback claude-sonnet-5 / 4-6 / 4-5; under §10, run_flags.enforced_model>`):
  > repo_root: [the `repo_root` Phase 0 step 3 resolved]
  > site_root: [the `site_root` Phase 0 step 3 resolved, where it set one — the site's own .vale.ini, package.json and lint configuration are looked for there first, then in each directory above it up to repo_root; omit the key otherwise]
  > files:     [the files edited in Phase 3]
  > enforced_model: [run_flags.enforced_model, when set — docs-style-checker passes it as model: on its own prose-style-checker dispatch in place of the Sonnet detection chain (workflows-core:model-routing/classification §10); omit the key otherwise]

- `VIOLATIONS_FOUND` → apply safe fixes via `doc-fixer` (`subagent_type: "workflows-core:doc-fixer"`, model: `<Sonnet detection chain — claude-sonnet-5-5, fallback claude-sonnet-5 / 4-6 / 4-5; under §10, run_flags.enforced_model>`, one fix cycle), then check the fixer's `Stop condition flag`. On `NEEDS HUMAN` it deferred a blocking violation it could not safely fix: surface each deferred BLOCKER with the fixer's reason and ask the user whether to fix it by hand and re-run, or skip the check — direct mode runs no reviewer, so nothing downstream would catch it. Record the `style_check` row from that answer per `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` (`RAN` after a hand fix and re-run, `SKIPPED_BY_USER` with the choice quoted verbatim). Only on `CLEAR` re-run once.
- `OK` → proceed to Phase 4.
- `ERROR` → neither a primary rung nor the `prose-style-checker` pass produced a result, so the gate has no coverage. Record `style_check` as `UNAVAILABLE` and convert it per `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` §5 before proceeding. Direct mode has no reviewer gate, so this prompt is the only place the gap surfaces — never proceed past it silently.

Never skip this phase on your own judgement of which linters are installed. `docs-style-checker` runs the chain internally as a **ladder**: each primary rung is tried in turn (a detected-but-broken rung does not abandon the ones below it), and `prose-style-checker` always runs on top as a complementary semantic pass — so neither the repo's own linter nor the semantic / cross-page class is silently dropped. Write the `style_check` ledger row here — rewriting the preflight's pre-seeded row if there is one, per `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` §3's one-row-per-gate rule (schema: `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` §3), carrying the returned `primary_attempts`: `RAN` when a primary rung succeeded; `DEGRADED` when no primary rung produced a result — every detected rung failed, or none was ever detected — but `prose-style-checker` ran, with `not_run:` one `{mechanism, reason}` entry per rung and a `ci_still_checks:` line — where a rung was detected and failed, naming the linter the repository's CI runs on the pull request, or saying that none runs, with its reason, where its CI runs none; where none was ever detected, recording that no repo-level linter is configured — never a CI claim the repository cannot support; `UNAVAILABLE` per the bullets above; `NOT_APPLICABLE` with `precondition_unmet: "no files edited"` when Phase 3 changed nothing.

After the style check, hold the edited files against the `repo_verification_gates` block extracted in Phase 0 (`${CLAUDE_PLUGIN_ROOT}/references/repo-verification-gates.md` §5) and append the `repo_checklist` ledger row: `RAN` with `findings:` = the number of entries that failed, or `NOT_APPLICABLE` with `precondition_unmet: "the repo publishes no pre-PR checklist"` when the block is empty. Report any failed entry to the user with its `source` citation — direct mode has no reviewer gate, so this is where the repo's own rules surface.

---

## Phase 4 — Post-implementation maintenance

First gather the actual change context:

a. Run `git -C <repo_root> diff --stat` (or equivalent) — in the repository Phase 0 step 3 resolved, whichever one cwd sits in — and capture the list of changed files with line counts. Note: the user has not committed, so `git diff --stat` will reflect unstaged changes.
b. Compose a **change summary block**:

```
Implementation: [one-sentence description of what was edited]
Change type: docs
Classification: [SIMPLE | MODERATE]
Files changed (from git diff --stat):
<paste the git diff --stat output>
Notable additions/removals: [new pages, new sections, new cross-links, restructured navigation — one line each; or "none"]
Validation result: [PASS | PARTIAL — with note on what's still broken]
```

Then spawn all four Phase 4 agents. They are independent and can run in any order — spawn them all before waiting for any to complete:

**Agent 1 — Documentation** (general-purpose, model: `<Sonnet detection chain — claude-sonnet-5-5, fallback claude-sonnet-5 / 4-6 / 4-5; under §10, run_flags.enforced_model>`):
> "Post-doc-edit documentation review. Change summary:
> [paste change summary block]
>
> Scan for README.md, CHANGELOG.md, docs/, or any .md files in the project root or a docs/ directory that are adjacent to the edited files.
> Determine if *other* documentation needs updating as a consequence of this edit (e.g., an index page, a cross-referenced overview, a changelog entry in the repo root).
> - Skip if: purely a typo fix, reformat, or edit confined to a single page with no cross-references
> - Update if: new page, restructured content, renamed headings that break inbound links, new cross-references that need a mate added elsewhere
> If an update is warranted: apply minimal edits to the relevant section(s).
> Return: file updated and what changed, OR 'no update required (reason)'."

**Agent 2 — Knowledge base** (general-purpose, model: `<Sonnet detection chain — claude-sonnet-5-5, fallback claude-sonnet-5 / 4-6 / 4-5; under §10, run_flags.enforced_model>`):
> "Post-doc-edit knowledge review. Change summary:
> [paste change summary block]
>
> Check ~/.claude/memory/ (global) and .claude/memory/ (project-level, preferred for repo-specific knowledge) for existing knowledge files.
> Determine if a new knowledge entry is warranted — look for: reusable insights about this repo's doc conventions, non-obvious style rules uncovered, tooling gotchas (Vale rule interactions, snippet conventions).
> If YES: identify the most appropriate existing file (never propose a new file if an existing one fits) and return a proposed edit — write nothing. The entry format:
> ### [Short title]
> - **Context**: what problem/situation triggered this
> - **Insight**: the learned rule, pattern, or gotcha
> - **When it applies**: conditions under which this matters
> - **Date**: YYYY-MM-DD
> - **Ref**: [first 60 chars of the doc-edit description]
> Return: `{file, anchor, replacement, reason}` — `anchor` is the exact existing text to change, or the section to append to; `replacement` is the entry above in full; `reason` is why it's warranted — OR 'no update required'."

**Agent 3 — Instructions** (general-purpose, model: `<Sonnet detection chain — claude-sonnet-5-5, fallback claude-sonnet-5 / 4-6 / 4-5; under §10, run_flags.enforced_model>`):
> "Post-doc-edit instructions review. Change summary:
> [paste change summary block]
>
> Check CLAUDE.md in the project root and ~/.claude/CLAUDE.md (global).
> Determine if any doc-editing rules, guidance, or guardrails are missing because of what this edit revealed (e.g., a repo-specific frontmatter field that must always be present, a cross-link pattern that's easy to miss, a style rule that caught you out).
> Skip if: the edit followed existing conventions with no surprises. Only update if a concrete, recurring rule would have prevented a decision point or misunderstanding during this edit.
> If YES: keep it minimal, additive, and scoped — do not propose rewriting sections wholesale — and return a proposed edit — write nothing.
> Return: `{file, anchor, replacement, reason}` — `anchor` is the exact existing text to change, or the section to append to; `replacement` is the proposed new/changed text; `reason` is what this edit revealed that warrants it — OR 'no update required'."

**Under `run_flags.skip_feedback`** (`workflows-core:run-flags` §4), dispatch `workflows-core:defect-reporter` instead of Agent 4 (`impl-maintenance`), with the same handoff plus `Plugin root: ${CLAUDE_PLUGIN_ROOT}` (literal — it expands in command bodies to this command's own plugin location), and `model: <§2.1 Sonnet chain, or run_flags.enforced_model>`; if it returns at least one defect, persist them with `emit-bugs` (`Skill(skill: "workflows-core:reference", args: "feedback-emission emit-bugs")`) in place of `emit-auto`, otherwise load nothing. Surface `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` in the Phase 5 `### Session learnings (Agent 4)` line, in place of the persisted-path line. Capture-at-block (`emit-block`) is unaffected by the flag.

**Agent 4 — Session maintenance** (workflows-core:impl-maintenance, model: `<Sonnet detection chain — claude-sonnet-5-5, fallback claude-sonnet-5 / 4-6 / 4-5; under §10, run_flags.enforced_model>`):
> "Analyse this session and return a Lessons Learned report.
>
> Session handoff:
> - Command run: /document (direct mode)
> - What was done: [one-paragraph summary of the doc edit]
> - Key events: [ambiguities that required user clarification, style-rule surprises, broken links encountered and fixed, convention mismatches — or 'none']
> - Workarounds used: [manual steps not automated by the workflow — or 'none']
> - Review verdict: N/A (no review gate in /document direct mode)
> - Test result: N/A (no tests in /document direct mode)
> - Project root: [the `repo_root` Phase 0 step 3 resolved, or the resolved target itself where it is not a git repository]"

Collect all four summaries for the Phase 5 report.

**Persist plugin feedback (automatic).** After Agent 4 (`impl-maintenance`)
returns, project its plugin-facing slice into the specs repo by invoking `Skill(skill: "workflows-core:reference", args: "feedback-emission emit-auto")` and calling its `emit-auto` entry point (§6). Pass Agent 4's Lessons Learned report,
`command: /document (direct mode)`, the run's `key` (usually `null` in
direct mode) and `source`, and `plugin_version` (read from
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). `emit-auto` renders only
the report's **Command workflow improvements**, **New agents / skills**, and
plugin **Reference docs** sections plus the **Key observations** that
triggered them (§4 plugin-facing predicate) — never target-project
`CLAUDE.md`/hook advice — as `origin: auto` entries, dedupes by stable `id`
(§3), resolves the target via the §2 specs-first ladder, and writes silently. A direct-mode run with no PRD folder takes that ladder's documentation branch (design D19): `$SPECS_PATH/documentation/<docs-repo-slug>/dev-workflows/feedback/<date>.md`, where `<docs-repo-slug>` is `workflows-core:specs-repo-git` §2.1's name for the write target Phase 0 step 3 resolved — filed against the repository this run edited, never left unfiled at the top of `$SPECS_PATH`. Under `specs_git: misrooted` (`workflows-core:specs-repo-git` §3.1) it is not written there: the entry stays in the run's output.
List the persisted path (or "no plugin-facing signal — nothing persisted") in
the Phase 5 `### Session learnings (Agent 4)` line. ADDITIVE — the
impl-maintenance report still appears in the report; this step NEVER fails the
run, NEVER commits (still true — this step only writes the feedback file;
those writes are committed by the separate terminal `commit-artifacts` step,
per `workflows-core:specs-repo-git` §4), and NEVER writes
into the docs repo or the current working directory, where it is not the specs repository.

---

## Phase 4.5 — Maintenance proposals

Direct mode never commits the doc edits — Phase 3 explicitly creates no branch and no commit — so the ordering constraint that gates keyed mode's Phase 8.6 is already satisfied here: there is no docs commit for an accepted proposal to ride. What the run does commit, via the terminal `commit-artifacts` step, is bounded to `$SPECS_PATH`'s artifact paths (`workflows-core:specs-repo-git` §2.1) and can never carry a proposal from this phase. This phase exists only so an accepted proposal still gets applied instead of just reported, the same as keyed mode's Phase 8.6.

Skip this phase with no prompt when both Phase 4 Agent 2 and Agent 3 returned `'no update required'`.

Otherwise present one row per proposal:

| File | Rule / entry | Reason |
|---|---|---|
[one row per Agent 2 / Agent 3 proposal — `file`, the rule or knowledge entry in one line, `reason`]

```
choices: ["Skip — report only (Recommended)", "Apply all", "Choose per proposal", "Cancel"]
```

- **Skip — report only** — apply nothing; every proposal's disposition is `proposed` for the Phase 5 report.
- **Apply all** — apply every proposal via the mechanism below; every proposal's disposition is `applied-uncommitted`.
- **Choose per proposal** — ask accept/decline for each proposal; apply the accepted ones (`applied-uncommitted`), leave the rest `declined`.
- **Cancel** — apply nothing; every proposal's disposition is `proposed`. Unlike every other "Cancel" in this command, **Cancel here does not abort the run**: direct mode never branches or commits the doc edits (Phase 3), so there is nothing upstream to unwind (still true — what still commits after this point is the terminal `commit-artifacts` step, bounded to `$SPECS_PATH`'s artifact paths per `workflows-core:specs-repo-git` §2.1). Cancel only declines this phase's proposals; the run proceeds to Phase 5 and the Final Report is produced exactly as it would be after Skip.

**Apply mechanism.** For each accepted proposal, re-dispatch the agent that produced it — Agent 2 or Agent 3, same general-purpose agent and model as Phase 4, no new agent type — in apply mode, carrying its own proposal back verbatim:

> "Apply this proposed edit exactly as returned — do not re-derive it:
> `{file, anchor, replacement, reason}`: [paste the proposal]
>
> Locate `anchor` in `file` and write `replacement` in its place (or append it, if the proposal is an append). Return: file written, OR a mismatch note if `anchor` no longer matches the file's current content — do NOT guess at the intended location; skip and report the mismatch."

The edit lands on disk, uncommitted, alongside the rest of this run's changes — direct mode leaves the whole working tree for the user to review and commit manually.

Carry each proposal's `{file, reason, disposition}` into the Phase 5 report.

---

## Phase 5 — Final Report

Output a structured report — do NOT ask any closing confirmation:

```
## Doc-edit Report

### Classification
[SIMPLE | MODERATE] — [reason]

### Run flags
[The `Run flags: …` line, repeated, whenever Phase 0 printed one during this run (`workflows-core:run-flags` §6) — omit this section entirely otherwise. When `run_flags.enforced_model` is set, add `Model routing: bypassed — enforced <id> (flag|env)` — every dispatch above already carries the enforced id in place of the Sonnet chain, per `workflows-core:model-routing/classification` §10. The `Session cost: …` skip line is Phase 7's own output, printed after this report and not restated in it.]

### What was edited
[High-level summary]

### Files changed
- path/to/file.ext — [what changed]

### Validation
- [check name] → [result]
- ...

### Documentation (Agent 1)
- [file updated] — [what was added/changed] OR "no update required (reason)"

### Knowledge base (Agent 2)
- [file, rule/entry summary, reason] — disposition: [proposed | applied-uncommitted | declined] OR "no update required"

### Instructions (Agent 3)
- [file, rule/entry summary, reason] — disposition: [proposed | applied-uncommitted | declined] OR "no update required"

### Maintenance applied (uncommitted)
[Every Phase 4.5 proposal with disposition `applied-uncommitted` — file, one-line summary, reason — one per line. Direct mode never commits the doc edits (the terminal `commit-artifacts` step stages only `$SPECS_PATH`'s bookkeeping paths), so these edits already sit in the same uncommitted working tree as the rest of this run's changes; listed separately so an accepted `CLAUDE.md` / knowledge-base edit doesn't get lost among the doc edits when you review before committing. OR "none".]

### Session learnings (Agent 4)
- [top suggestions from impl-maintenance agent, or "no suggestions — routine session" — or, under `--skip-feedback`, `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` / `— no defects` in its place]

### Verification gates
| Gate | Outcome | Detail |
|---|---|---|
[One row per gate in the `gate_ledger` — direct mode registers three (`references/gate-ledger.md` §4). "Detail" carries the row's `ci_still_checks` (DEGRADED), `user_decision` (SKIPPED_BY_USER), or `precondition_unmet` (NOT_APPLICABLE); empty otherwise. When any row is DEGRADED or SKIPPED_BY_USER, follow the table with a one-line warning naming what this run did not check. The warning names a CI check only where a row's `ci_still_checks` records one, and where that line says none runs, it says that nothing will. A SKIPPED_BY_USER row records no `ci_still_checks` (`references/gate-ledger.md` §3), so for that row the warning names the gate the user skipped and names no CI check in its place.]

### Assumptions & limitations
- [list any]

### Deferred items
- [anything the user asked to defer, OR validation failures the user accepted, OR "none"]

### Git state
The working tree has uncommitted changes. `/document` (direct mode) never commits your doc edits — you manage git manually. Run `git -C <repo_root> status` to review, then commit when ready. (This run's `$SPECS_PATH` session artifacts are committed separately — see the terminal step's outcome line at the end of the run.)
```

---

## Phase 6 — Emit follow-up tasks

Terminal phase — runs AFTER the Phase 5 Final Report is composed; NEVER
interrupts an earlier phase. Persist any out-of-scope / manual-step follow-ups
by invoking `Skill(skill: "workflows-core:reference", args: "followup-emission")` and executing its steps inline.

1. **Collect** the follow-up items from the Phase 5 `### Deferred items` section
   (direct edits rarely produce out-of-scope work; this phase is usually a
   no-op).
2. **Filter** them with the reference's §6 qualifying predicate.
3. **Resolve** the write target via the §2 ladder. Direct mode usually has no
   `key` (`source = none`), so the phase degrades to report-only.
4. **Preview + confirm** per §7 (`approve-all | select | cancel`), then write.

ADDITIVE — the follow-ups also remain in the Phase 5 report. This phase NEVER
fails the run, NEVER commits (still true — this phase only writes follow-up
files, and the user manages git manually for the doc edits; those writes are
committed by the separate terminal `commit-artifacts` step, per
`workflows-core:specs-repo-git` §4), and NEVER writes
into the docs repo or the current working directory, where it is not the specs repository.

---

## Phase 7 — Session cost

Terminal phase — the NEW final operational phase; runs after Phase 6 (the
follow-up phase) and NEVER interrupts an earlier phase. Records this command's
token-cost contribution — through `emit-cost`, or, under `run_flags.skip_costs`, by advancing the checkpoint alone. Unlike feedback, **cost ALWAYS runs** — unless `run_flags.skip_costs` (see below) — it never "writes
nothing".

**Under `run_flags.skip_costs`**, do not call `emit-cost` and do not load `cost-emission`: execute `skip-cost` (`Skill(skill: "workflows-core:reference", args: "run-flags skip-cost")`) instead, which advances the checkpoint and drops any deferred record, and surface `Session cost: skipped (--skip-costs)` (or `(WORKFLOWS_SKIP_COSTS)`). No `resume.md` is written in this mode, so only the terminal `commit-artifacts` step below runs unchanged either way.

Otherwise (not skipping), invoke `Skill(skill: "workflows-core:reference", args: "cost-emission emit-cost")` and call `emit-cost` with `command: /document (direct mode)`, `phase: documenting`,
`role: dev`, the run's `key` (usually `null` in direct mode) and `source`,
and `plugin_version` (read from
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). It resolves the session
transcript + subagents (§1), loads and **advances the chained checkpoint** (§3),
computes the per-model token-cost delta against
the price table (§4), records the optional statusline cross-check (§5), and
appends one per-invocation entry via the specs-first ladder (§8). A direct-mode run with no PRD folder — the ordinary case — takes that ladder's documentation branch (design D19): `$SPECS_PATH/documentation/<docs-repo-slug>/dev-workflows/cost/<sid8>.md`, where `<docs-repo-slug>` is the one-segment name `workflows-core:specs-repo-git` §2.1 defines for the write target Phase 0 step 3 resolved, whether or not that target is a git work tree. Under `specs_git: misrooted` (`workflows-core:specs-repo-git` §3.1) it is not written there: the entry stays in the run's output. Every direct-mode run resolves a write target, so none parks an entry in pending; a run whose key does resolve a PRD folder lands in `<PRD-dir>/dev-workflows/cost/<sid8>.md` instead. **The checkpoint advances in every tier, report-only included.** Surface the persisted path (or the
report-only notice) as this phase's only output.

**Then commit session artifacts (terminal).** Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git commit-artifacts")` and execute its `commit-artifacts` entry point (§4) inline — the LAST action of the run. It
stages ONLY the §2.1 bounded artifact paths inside `$SPECS_PATH`, commits
`<KEY> Add dev-workflows session artifacts (/document)` — or `NOISSUE …`
when this doc-edit run resolved no key — and pushes per §4 step 5. It NEVER
writes into the docs repo this run just changed, NEVER touches a code repo,
anything outside `$SPECS_PATH`;
NEVER force-pushes; NEVER fails the run; and skips entirely when the run
carries `specs_git: blocked` (§3.3 G0) or `specs_git: misrooted` (§3.1, or `specs-root-check`'s stop), re-emitting that notice. Because
the Phase 5 report was composed before this phase, **print its §6 outcome
line here**, as the run's last output — prefixed `Specs repo:`, with
any guard notice repeated in full. No `resume.md` is written in this mode
(`workflows-core:session-hygiene` §1 skip list).

ADDITIVE — this phase NEVER fails the run, NEVER commits the deliverable
(direct-mode doc edits remain uncommitted — the user manages git manually;
the terminal step above commits only the bounded session-artifact paths in
`$SPECS_PATH`), and NEVER writes into the docs repo or the current working
directory, where it is not the specs repository; no user name is ever written (§10 privacy).

---

## Invariants (always enforced)

- ALWAYS `emit-block` (per `workflows-core:feedback-emission`) before escalating a halt caused by a **plugin / skill / command / reference gap** (a capability the run needed but the plugin lacked) — so a run abandoned at the block still records it. NEVER for a work-quality review BLOCK or an environment / user halt (repo-missing, dirty-tree, key-not-found, cancellation). The one exception is a halt on a tool the ai-containers image lacks, which `workflows-core:feedback-emission` §6 `emit-block` defines.
- ALWAYS run Phase 3.5 (style check) after editing — `docs-style-checker` always also runs `prose-style-checker` — complementary beside a repo linter that produced a result, FALLBACK where every detected rung failed, SOLE where the repository configures none (its step 5); never skip style on tool-absence judgement
- NEVER create a git branch — this mode never branches. `specs-preflight` may switch `$SPECS_PATH` between branches that already exist, and only ones the plugin created (`workflows-core:specs-repo-git` §2.2); it creates none.
- NEVER run tests (this command has no test phase)
- NEVER invoke Opus (no planning agent, no review agent — docs edits are always SIMPLE or MODERATE), unless `run_flags.enforced_model` names one (§10)
- NEVER commit the doc edits, or anything else in a docs/code repo or the current working directory, where it is not the specs repository — the user manages git manually there. The terminal `commit-artifacts` step commits ONLY `$SPECS_PATH`'s bounded artifact paths (`workflows-core:specs-repo-git` §2.1).
- ALWAYS run `specs-preflight` in the shared `## Mode detection` section, before dispatching to either mode — so it runs for Mode B as well as Mode A — and `commit-artifacts` as the run's last action (per `workflows-core:specs-repo-git`) — bounded to `$SPECS_PATH`'s artifact paths (§2.1) and to plugin-created branches (§2.2), always `git -C "$SPECS_PATH"` and never a `cd` (§1 rule 1), never force-pushing, and never failing the run
- NEVER make assumptions that could have been asked — ask instead
- NEVER end implementation with "Should I implement?" — if approved, implement
- NEVER rewrite sections wholesale when only a targeted edit is needed
- NEVER skip Phase 4 — documentation, knowledge, instructions, and session-maintenance are mandatory after every successful doc edit; always collect all four agent summaries for Phase 5
- ALWAYS run the Phase 2A exploration subagent before drafting the plan
- ALWAYS pass `Change type: docs` in the Phase 4 change summary block
- ALWAYS pass `Command run: /document (direct mode)` in the Phase 4 Agent 4 session handoff
- ALWAYS spawn Phase 4 agents in a single message — never sequentially
- ALWAYS use `choices` arrays for decision points; 2–4 options, and never author an "Other" option — the harness supplies the free-text escape itself (`workflows-core:escalation-rules` §0)
- ALWAYS produce the Phase 5 report as the final output
- ALWAYS run the Validation checks from the plan — validation failures are surfaced in the Phase 5 report, not silently accepted
- IF the task reads as SIGNIFICANT / HIGH-RISK on inspection: redirect to `/document` (keyed mode) or `/epics` rather than proceeding under the simplified flow

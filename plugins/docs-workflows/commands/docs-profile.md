---
name: docs-profile
description: Scan a documentation repository and write/refresh a machine-readable docs-profile (.dev-workflows/docs-profile.yml) plus complementary CLAUDE.md guidance, as a reviewable PR. Captures content roots, per-space dev-servers and lint/build/format commands, templating tokens, links, announcement pages, branch-naming, images, and prerequisites; defers changelog/owners to the docs-frontmatter skill. Bootstraps or refreshes the profile that /document consumes.
allowed-tools: Read Edit Write Bash Glob Grep Task Skill
---

Profile the documentation repository: $ARGUMENTS

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

`$ARGUMENTS` is an optional repo path (default: the current working directory), optionally followed by `--inline`. The `--inline` token is passed when `/document` (keyed mode) invokes this flow inline (its Phase 0 case (c)); it switches this command to **inline mode** — see Phase 0 step 2, Phase 4's "Keep existing, write nothing", Phase 5 step 1, step 2, step 6, and Phase 6.

Usage: `/docs-profile [<repo-path>] [--inline] [--enforce-model=<model>]`

`/docs-profile` **bootstraps or refreshes** the machine-readable docs-profile that `/document` (keyed mode) consumes. It scans a documentation repository, synthesises a `.dev-workflows/docs-profile.yml` (and complementary CLAUDE.md guidance) that conforms to `${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/docs-profile-schema.md`, then writes the result as a **reviewable PR** — branch + commit + a drafted PR message. It never pushes or auto-merges, and a refresh whose changes the operator declines, or that finds nothing to change, writes nothing at all (Phase 4).

The command is **generic** — it works on any docs repo. A repo publishing one documentation set gets a single `spaces[]` entry; a repo publishing several gets one entry per content root, plus the per-space dev-server and lint/build/format commands that go with them.

It does **not** re-specify changelog or owners rules. Those are owned by the `docs-frontmatter` skill (+ `${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/changelog-guidelines.md`, `${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/default-owners.txt`); the profile's `frontmatter:` fields are **pointers only**.

For one-off doc edits use direct mode; for keyed feature documentation use `/document` (keyed mode).

---

## Phase 0 — Resolve and validate the target repo

**Strip the run flags first, standalone only — where `$ARGUMENTS` carries no `--inline` token.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS`: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its routing step — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. `--skip-costs` and `--skip-feedback` do not apply to this command — it dispatches no `impl-maintenance` and calls no cost-emission entry point — so an explicit one is reported ignored and resolves to its default, unvalidated; only `--enforce-model` applies, on a standalone run. **`--inline` does not re-strip and inherits its caller's `run_flags` instead.** `/docs-workflows:document` (keyed mode) Phase 0 step 4(c) constructs this run's whole `$ARGUMENTS` explicitly — `docs_repo_resolved --inline` — from a value it already holds, so that string never carries a run-flag token of its own to find; a fresh strip would resolve each flag to its env default, losing the caller's explicit `--enforce-model`. Instead this run reuses the `run_flags` record `/document` already resolved at its own Mode detection, unchanged, for every step below that reads one.

1. **Resolve the repo path.** Strip a `--inline` token (in any position) from `$ARGUMENTS` before reading a positional token — it is the inline-mode flag, never a path; record `inline = true` when present. Execute **`resolve-docs-repo`** from `${CLAUDE_PLUGIN_ROOT}/references/docs-workflow/repo-resolution.md` §1 — the signal-positive form, since this command needs a docs repo that already exists, never one to create. Do not restate its ladder here; the entry point owns it. Report which rung answered, per its own hard rule — a command that quietly works in an unexpected directory is expensive to unpick afterwards. Record the resolved absolute path as `<repo>`.

2. **Validate it is a writeable git work tree:**
   - `git -C <repo> rev-parse --is-inside-work-tree` must print `true`. If it errors or prints anything else, stop with the named error: `NOT_A_GIT_WORKTREE: <repo> is not inside a git work tree.`
   - `test -w <repo>` must succeed. If not, stop with the named error: `REPO_NOT_WRITEABLE: <repo> is not writeable.`
   - Resolve and record the repo's git root as `<repo-root>`: `git -C <repo> rev-parse --show-toplevel`. It is the profile's one home (`${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/docs-profile-schema.md`, **Where the profile lives**): this run reads and writes `<repo-root>/.dev-workflows/docs-profile.yml` even where `<repo>` is a site below it, and all later detection and writes are relative to this root.
   - **Inline mode: a leftover bootstrap branch stops the run here.** Where `inline = true` and `git -C <repo-root> rev-parse --verify --quiet refs/heads/dev-workflows/docs-profile-bootstrap` exits 0, an earlier inline run left that branch — one that stopped after profiling — and this run never switches onto it: `/document` would rename it into the docs branch, which would then fork where the leftover forked and lack every commit the base has gained since. It is tested now, before step 3's question, Phase 2's scan and Phase 3's Opus synthesis, because nothing any of them produces can let the run finish: the operator answers nothing and no synthesis is spent. Resolve `<base>` as Phase 5 step 2 does, and stop:

     `DOCS_PROFILE_BOOTSTRAP_BRANCH_EXISTS: <repo-root> already has the branch dev-workflows/docs-profile-bootstrap, forked from <base> at <fork> — an earlier /document run left it after profiling. This run does not switch onto it: a docs branch built on it would lack every commit <base> has gained since <fork>. Delete it or merge it into <base>, then re-run.`

     `<fork>` is the short hash and subject of `git -C <repo-root> merge-base <base-ref> dev-workflows/docs-profile-bootstrap`, where `<base-ref>` is the ref Phase 5 step 2's chain finds for `<base>` — `origin/<base>` — or `<base>` itself where that step falls back to a local branch: a read takes the ref (`workflows-core:read-only-repos` §3, **A switch takes the name**), and nothing has pulled `<base>` up to it yet.

3. **Confirm a signal-less target.** Only two of `resolve-docs-repo`'s rungs can hand Phase 1 a directory that carries no docs signal: an explicit positional token, taken "as given" with no signal test at all, and the ladder's last-resort generic "which directory" question, which asks where to look rather than testing what comes back — step 3 is what catches both. So a repo named explicitly on the command line, or supplied in answer to that generic question, can still reach here carrying zero signals — this is the branch that lets `/docs-profile` profile a repo the resolver would never have found on its own, and it asks a different question from resolution: whether to *write a profile* for a repo that shows none of the signals a docs repo usually carries. Test **`<repo>`** — the directory `resolve-docs-repo` resolved, where its signal-tested rungs found their signal — and `<repo-root>` against the signal set fixed by `${CLAUDE_PLUGIN_ROOT}/references/docs-workflow/repo-resolution.md` §3 (cite it; never re-derive it here); a signal in either counts. `<repo-root>` alone is the wrong test: it is where the profile lives, not where a site below it keeps its signals, so a `mkdocs.yml` in a monorepo's `docs/` would go unseen and a signal-tested rung's own answer would be questioned.
   - **≥ 1 signal present** → proceed silently to Phase 1.
   - **0 signals present** → ask before continuing, with the bracketed part only where `<repo-root>` differs from `<repo>`:
   ```
   "No documentation-repo signals detected in <repo>[ or at its top level <repo-root>] (checked against repo-resolution.md §3's signal set). Profile it anyway?"
   choices: ["Proceed — I confirm this is a docs repo (Recommended)", "Cancel — point me at a docs repo first"]
   ```
   Default = Proceed. On Cancel, stop and report.

---

## Phase 1 — Model routing

Invoke the `model-routing` skill (Skill tool, `skill: "workflows-core:model-routing"`) to load `workflows-core:model-routing/classification`. The skill is invoked because `model-routing` is a `workflows-core` skill and the classification file it loads is a `workflows-core` reference — this plugin cannot read either by path; `${CLAUDE_PLUGIN_ROOT}` resolves to `docs-workflows`, not to the plugin that carries them.

Profiling is **SIGNIFICANT** — it is a cross-cutting synthesis of the whole repository whose output (`docs-profile.yml`) steers every later `/document` run, so a wrong profile has a large blast radius. State the classification and a one-line reason.

Record a `model_routing` block modeled on §4 (a profiling command does no implementation/fix edits, so those fields are N/A), resolving each model against the fallback chains:

```yaml
model_routing:
  classification: SIGNIFICANT
  reason: "cross-cutting synthesis of the whole docs repo; output steers all later /document runs"
  current_model: <the model this orchestrator is running under>
  enforced_model: <run_flags.enforced_model, or omit>   # §10: when set, every dispatched-step *_model below equals it (inline authoring_model / implementation_model keep the session model) and routing: bypassed
  detection_model: <§2.1 mid-tier Sonnet chain: claude-sonnet-5-5, fallback claude-sonnet-5/4-6/4-5>
  planning_model: <§2 powerful chain: claude-opus-5-5 … fallback Sonnet 5.5/5/4.6/4.5>
  review_model: <same as planning_model — conceptually the synthesis_model; the synthesis step runs on the §2 Opus chain>
  opus_available: true | false
  notes: <any §2.1/§2 degradation, e.g. "Opus unavailable; synthesis fell back to claude-sonnet-5-5">
```

The detection phase (Phase 2) pins its subagent to `detection_model` (the §2.1 chain) via the `task` tool's `model:` override — never the session model. The synthesize phase (Phase 3) pins to `planning_model` (the §2 Opus chain). Announce any fallback now and again in Phase 6.

---

## Phase 2 — Detect (Sonnet-tier)

Dispatch a **read-only** detection subagent **pinned to the §2.1 mid-tier chain** via the `task` tool's `model:` override — `claude-sonnet-5-5`, fallback `claude-sonnet-5`/`claude-sonnet-4-6`/`claude-sonnet-4-5`; record the model actually used as `detection_model` in the `model_routing` block. Detection is mechanical repo scanning, so it must NOT inherit the session model (an Opus session would otherwise burn Opus on a cheap step, per §2.1).

→ Agent (subagent_type: "general-purpose", model: `<detection_model — §2.1: claude-sonnet-5-5, fallback claude-sonnet-5/4-6/4-5; under §10, run_flags.enforced_model>`):
  > "Read-only detection scan for a docs-profile. Do NOT write or edit any file — return a structured detection report only.
  >
  > repo_root: <resolved git root from Phase 0>
  >
  > Gather and report, each with the file path + a short verbatim excerpt as evidence:
  >
  > 1. **package.json scripts** — every script whose name matches `*:start`, `*:lint`, `*:build`, `docs:*`, `format`/`prettier`. For each `*:start` script, extract the dev-server port and base path (grep the script and any referenced config — e.g. `--port`, `PORT=`, a `base`/`basePath` in a docusaurus/mkdocs/eleventy/vitepress config). Note whether two `*:start` servers can run concurrently (distinct ports → concurrent; shared port / single server → sequential).
  > 2. **Templating tokens** — grep the content roots for the repo's own inline markers, e.g. `{{tag kind='latest'}}` (a "latest version" marker) and `::app-settings::` (a settings breadcrumb). Report each marker's exact spelling and where it occurs.
  > 3. **Content + snippet roots** — every `*/_content` and every `*/_snippets` directory (e.g. `cloud/_content`, `cloud/_snippets`, `self-hosted/_content`, `self-hosted/_snippets`). This determines the `spaces[]` list: one rendered space per content root.
  > 4. **Branch-naming + internal-link conventions** — read CONTRIBUTING.md, CONTRIBUTION.md, README.md, DOCUMENTATION-GUIDELINES.md, and CLAUDE.md at the repo root (and `.claude/`). Quote any documented branch-naming pattern (e.g. `<initials>/<KEY>-<slug>`) and any internal-link convention (e.g. `[text](<postid>)` where postid comes from target frontmatter).
  > 5. **Image policy** — any documented rule for screenshots/images (CDN-hosted vs committed binaries); quote the source.
  > 6. **Prerequisites** — anything a dev server needs before `*:start` boots (e.g. a `.docstack` toolchain / shim, an axios version pin, an env var); quote the source.
  > 7. **Announcement pages** — hand-authored destination pages inside an otherwise automation-owned tree (e.g. a release-notes / what's-new tree). Detection signal: a page under such a tree whose frontmatter does NOT carry `meta.content-type: release-notes` (absent, or any other value) AND whose `git log` shows human PR commits rather than automation. For each match, record its `postid` (frontmatter `postid:`), its repo-relative `path`, and a proposed `kinds` list inferred from the page title and headings (e.g. an "End-of-life announcements" page → `[deprecation, end-of-life, shutdown, sunset]`). Report `announcement_pages: []` explicitly when none are found.
  >
  > Return one section per item above. For anything not found, say `not found` explicitly — do not guess. End with a one-paragraph summary: how many content roots the repo publishes, and whether each has its own dev server and lint/build scripts."

**Wait for the detection report.** If the agent returns nothing usable or fails, gather the same facts yourself via Glob/Grep/Read (read-only) before Phase 3 — but still record `detection_model` as the chain you attempted.

---

## Phase 3 — Synthesize the draft profile (Opus)

On the §2 powerful chain (`planning_model`), turn the detection report into a draft `docs-profile.yml`. This synthesis is the SIGNIFICANT reasoning step, so it runs on the strongest available reasoning model (Opus), pinned via the `task` tool's `model:` override — not the §2.1 detection chain.

→ Agent (subagent_type: "general-purpose", model: `<planning_model — §2 chain: claude-opus-5-5, fallback per §2; under §10, run_flags.enforced_model>`):
  > "Synthesise a docs-profile from a detection report. This is a planning/synthesis task, not a code change — return the drafted YAML + drafted CLAUDE.md additions, nothing else; do not write files.
  >
  > Schema (the draft MUST conform exactly): `${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/docs-profile-schema.md`
  > Detection report: [paste the full Phase 2 report]
  >
  > Rules:
  > - **Every path and every command is rooted at `repo_root`** (the schema's **Where the profile lives**): write each path relative to it, and each command in the form that runs from it. A script the report found in a `package.json` below `repo_root` runs in that file's directory, so record its command as `cd <that directory, relative to repo_root> && <the script invocation>` — run from `repo_root`, the bare invocation would read the wrong `package.json`, or none.
  > - Emit `schema_version: 1` and one `spaces[]` entry per detected content root (`id`, `content_root`, `snippet_root`, `base_path`). `spaces[]` is required and non-empty.
  > - `dev_servers`: one `servers[]` entry per `*:start` script with its `command`, `port`, `base_path`; set `concurrent: false` unless detection proved two servers can run at once.
  > - **The `{port}` token** (the schema's field rule for `dev_servers.servers[].command`): write it **only in place of a literal port the detected command already carries** — that entry's own `port`, standing as a whole number (not part of a longer one) exactly once in the command; replace that number with `{port}` and change nothing else. A command that carries no such literal — a script invocation like the schema's `pnpm cloud:start`, whose port lives inside the script — is written without the token, and so is one that carries it more than once, since which occurrence is the port cannot be told. **Never invent a flag or an argument-forwarding form to carry the token** (`-- --port {port}` and the like): which flag a tool takes, and whether a script forwards arguments to it, is that tool's business — `/docs-serve` refuses to guess it too.
  > - `commands`: `lint`, `format`, and any commit-hook chain detected.
  > - `tokens`: only the markers detection actually found (e.g. `latest_tag`, `settings_breadcrumb`).
  > - `internal_links.convention`, `branch_naming.pattern`, `images.policy`, `prerequisites[]`: fill from detection; leave a field out rather than inventing it. `images.policy` is one of the schema's three values — `in-repo`, `object-store`, `cdn` — never a sentence: write the value the detected rule describes, and mark it `needs-confirmation` where the rule fits none of them or fits more than one.
  > - `announcement_pages[]`: one entry per page found by detection item 7 (Announcement pages), each `{postid, path, kinds}`. Emit `announcement_pages: []` explicitly when detection found none — do not omit the key.
  > - `commands.per_space:` — when `package.json` (or the repo's task runner) exposes **per-space** lint / build / format scripts whose names correspond to entries in `spaces[]` (e.g. `docs:lint` + `self-hosted:lint` for spaces `cloud` + `self-hosted`), record them under `commands.per_space.<space id>`. Map the script name to the space id by the space's `content_root` (`cloud/_content` ⇒ script prefix `docs`), never by guessing. Omit `per_space` entirely when the repo has one content root, or when only whole-repo scripts exist.
  > - `frontmatter:` is **POINTERS ONLY** — set `owned_by_skill: docs-frontmatter`, `changelog_guidelines: references/docs-profiles/changelog-guidelines.md`, `default_owners: references/docs-profiles/default-owners.txt`. NEVER copy any changelog or owners rule text into the profile.
  > - Mark every field as `detected` (grounded in the report) or `needs-confirmation` (inferred / not found) so the orchestrator knows what to ask in Phase 4.
  > - Separately, draft minimal complementary **CLAUDE.md additions** ONLY for conventions not already covered by the docs-frontmatter skill or its reminder hook (e.g. dev-server sequencing, a repo-specific snippet or token convention). Do NOT restate changelog/owners — defer to the skill."

**Wait for the synthesis.** Hold the drafted `docs-profile.yml` and the drafted CLAUDE.md additions for Phase 4. If Opus was unavailable and the synthesis fell back to Sonnet, note it in `model_routing.notes` and carry it to Phase 6.

---

## Phase 4 — Confirm and fill gaps

**Rule: Ask, don't guess.** For every field the synthesis marked `needs-confirmation` — and anything detection could not settle — ask the user. Use `choices` arrays; 2–4 options, and never author an "Other" option — the harness supplies the free-text escape itself (`Skill(skill: "workflows-core:reference", args: "escalation-rules")` §0); the recommended default is first and labelled `"(Recommended)"`. Group related fields into one question where possible. On a **refresh** (below), a field the Phase 2 report found nothing for is not a gap: the existing profile already answers it and keeps it, so ask about it only where the existing profile does not carry it either — or carries a value the schema does not accept, which the refresh rules below never keep (a free-text `images.policy`).

Typical gaps:

- **Exact build / start command** when a script was ambiguous:
  ```
  choices: ["Use detected `<cmd>` (Recommended)", "Enter the correct command", "Leave unset"]
  ```
- **Prerequisites** such as the `.docstack` shim (e.g. an axios>=1.16 pin) that must be in place before `*:start` boots:
  ```
  choices: ["Record detected prerequisite(s) (Recommended)", "Add a prerequisite I'll describe", "No prerequisites"]
  ```
- **Ambiguous space mapping** (a content root with no obvious `id` / `base_path`):
  ```
  choices: ["Accept proposed space mapping (Recommended)", "Edit a space's id/base_path", "Drop this space"]
  ```
- **Branch-naming convention** when none was documented (drives Phase 5):
  ```
  choices: ["Use repo convention if detected, else `<prefix>/NOISSUE-docs-profile` (Recommended)", "Enter a different pattern"]
  ```

**Idempotent refresh.** Before writing, check whether `<repo-root>/.dev-workflows/docs-profile.yml` already exists:
- **Exists** → this run is a **refresh**, and it builds the new profile **from the existing one**, never from the draft alone. Phase 2 detects only what it looks for — a repository `/docs-workflows:docs-init` scaffolded has no `package.json` `*:start` script and no `*/_content` root, and nothing in Phase 2 looks for `builds[]` or `generator` at all — so the draft is a partial view of the repo, and a diff against it would read everything detection missed as a deletion. Build the refreshed profile by these rules:
  - **The refresh proposes a change only for a field detection produced a value for** — and for an existing `images.policy` the schema's enum does not accept, the one value it never keeps as it stands (below). A field detection produced a value for is one the Phase 2 report found evidence for — marked `detected`, or `needs-confirmation` over a value the report did find — and never one the report says `not found` for or never looks for, whatever the synthesis drafted in its place. Where that value differs from the existing one it is a proposed change; where the existing profile lacks the field, a proposed addition.
  - **Every other field is carried forward verbatim** — `builds[]`, `generator`, `repo`, `frontmatter.*`, a server's `visibility` and `public_base_url`, and any field the report found nothing for.
  - **The `images` block is a detected field** — detection item 5 reports an image policy — so where the report found one, the synthesis's `images.policy` is compared with the existing value and proposed through the diff like any other detected field, and so is each other `images.*` key detection produced; the rest of the block is carried forward. **An existing `images.policy` the schema's enum does not accept is never carried forward silently** — the free-text sentence a pre-1.2.0 profile carries above all: the diff lists it as **non-conforming**, `existing → new` where detection produced a value, and where it produced none the gap is asked like any `needs-confirmation` field, quoting the old sentence: `choices: ["<the value the old sentence describes> (Recommended)", "<the second of in-repo, object-store, cdn>", "<the third>"]`, each option glossed as the schema's field rule glosses it — `in-repo` committed under `images.root`, `object-store` an S3-compatible bucket, `cdn` uploaded by hand and referenced by URL — and, where the sentence describes none of the three, the three in that order with no `(Recommended)` on any. Phase 5 step 3 writes a file that MUST conform, so a non-conforming value is always a change, and a diff that lists one is never up to date.
  - **Detection finding nothing is never a proposal to delete.** A field or entry the draft omits, leaves empty or writes as `[]` because nothing was found — `announcement_pages: []`, a `dev_servers.servers[]` list with no `*:start` script behind it — leaves the existing one as it stands.
  - **`spaces[]` is kept, never emptied.** It is required and non-empty; where detection found no content root, the existing entries stand.
  - **Lists are compared entry by entry**, each entry by what identifies it — a `spaces[]` entry by its `id`, a `dev_servers.servers[]` entry by its `space`, an `announcement_pages[]` entry by its `path`, a `prerequisites[]` entry by its text — and leaf by leaf within a matched entry, so a key detection never produces inside an entry it did detect is carried over with it. Where one identifier matches more than one entry on either side — two servers sharing one space, told apart by a `visibility` detection never reads — propose nothing for that list: keep it as it stands, and say why in the diff.
  - **A `{port}` token is not a difference.** An existing `dev_servers.servers[].command` carrying `{port}` equals the detected one in either of two forms: the token stands in place of the port — replacing every `{port}` in the existing command with the detected entry's `port` gives the detected command exactly — or the existing command is the detected command followed by further arguments that carry the token, the argument-forwarding form an operator adds by hand where a script passes a port on to its tool, as `pnpm docs:start -- --port {port}` does beside a detected `pnpm docs:start`. Keep the existing command, token and any forwarded arguments included, propose nothing for it (a differing `port` is its own leaf), and list it in the diff as kept, beside the detected command it equals: the token is what the schema tells an operator to add by hand (`docs-profile-schema.md`, `dev_servers.servers[].command`), and a refresh that proposed its removal would undo that edit at every run.

  **Where the diff lists no change and no addition** — as built, or with the operator's edits folded in — every field is kept as it stands and the profile is up to date. Say so, list the kept fields, ask nothing, and end the run exactly as "Keep existing, write nothing" does below: no branch, no stash offer, no commit and no CLAUDE.md additions, with the Phase 6 report reading "up to date — nothing written", and, in inline mode, the existing profile returned to `/document` with no branch or commit to hand back (Phase 6). Asking anyway offers "Apply the diff", which cuts a branch whose commit then fails with nothing to commit.

  Otherwise, show the result as a **field-level diff** in two parts — every proposed change (`existing → new`) and addition, then every field kept — **kept, not detected**, and any server command kept by the `{port}` rule above, beside the detected command it equals — each named, so the operator sees what the refresh leaves alone — and confirm:
  ```
  "A docs-profile already exists. Apply these field-level changes?"
  choices: ["Apply the diff — change the listed fields, keep the rest (Recommended)", "Keep existing, write nothing", "Edit specific fields first (you'll be prompted)"]
  ```
  "Apply the diff" changes exactly the fields listed as changed or added and nothing listed as kept. Do not overwrite without this confirmation. Where each choice goes:
  - **"Apply the diff — change the listed fields, keep the rest"** → Phase 5, which writes the existing profile with those changes applied.
  - **"Keep existing, write nothing"** → this run writes nothing. Skip Phase 5 entirely — no branch, no stash offer, no commit, and no CLAUDE.md additions — and go straight to Phase 6, whose report reads "kept — nothing written". In inline mode, which has no Phase 6 report of its own, control returns to `/document` with the existing profile unchanged and no branch or commit to hand back (Phase 6), and `/document` proceeds with that profile (its Phase 0 step 4(c)).
  - **"Edit specific fields first (you'll be prompted)"** → take the edits and fold them into the diff; where it now lists no change and no addition, end the run as the paragraph above says, and otherwise show the diff again and ask this question again.
- **Absent** → bootstrap: proceed to Phase 5 with the confirmed draft.

Record the final, confirmed `docs-profile.yml` — on a refresh, the existing profile with the confirmed changes applied, or, where the operator kept it or the refresh found nothing to change, the existing profile as it stands — and the CLAUDE.md additions, and tag each field `detected`, `user-supplied`, or, on a refresh, `kept, not detected` for the Phase 6 report.

---

## Phase 5 — Write as a reviewable PR

Produce a reviewable PR in the **target repo** (never the plugin). **Never push or auto-merge** unless the user explicitly asks. A refresh answered "Keep existing, write nothing", or one whose diff lists no change, never reaches this phase (Phase 4): there is nothing to write, so no branch is cut, no stash is offered and nothing is committed.

1. **Resolve the branch name.** **Inline mode** (`--inline`): skip the prompt and the confirmation entirely — use the deterministic name `dev-workflows/docs-profile-bootstrap`; `/document` (keyed mode) Phase 6.2 renames it to the docs-branch convention. Phase 0 step 2 has already stopped the run where a branch of that name exists (`DOCS_PROFILE_BOOTSTRAP_BRANCH_EXISTS`), so step 2 below cuts it fresh. **Standalone** (default):
   - If the repo documents a branch-naming convention (detected in Phase 2 / confirmed in Phase 4), fill its placeholders and use it.
   - If the convention has an **identity** placeholder, fill it from the §2 ladder in `Skill(skill: "workflows-core:reference", args: "branch-naming")` (`$GIT_USER_INITIALS` → `git config user.initials` → inference from existing branches → the §2.5 prompt); its issue-key segment takes the documented no-issue literal, since profiling has no ticket.
   - Else (no convention documented, §1.4) use `<prefix>/NOISSUE-docs-profile`, where `<prefix>` comes from the same §2 ladder with fallback `docs/`. If the ladder yields nothing, run its §2.5 escalation:
     ```
     "I couldn't infer a branch prefix from $GIT_USER_INITIALS, `git config user.initials`, or existing branches. This command's default is `docs/`. What prefix should I use?"
     choices: ["Use `docs/` (default for this command)", "Use my initials — I'll enter them"]
     ```
   Always confirm the final name (initials/slugs are subjective):
   ```
   choices: ["Use proposed branch `<name>` (Recommended)", "Edit the name"]
   ```

2. **Prepare the working tree.** `git -C <repo-root> status --porcelain`; if non-empty:
   ```
   choices: ["Stash changes and continue (Recommended)", "Proceed anyway — pre-existing changes will appear in the diff", "Cancel"]
   ```
   Then base the branch on the repo's default branch so the profile PR is cut from a clean base. `<base>` is that branch's **name**, never its `origin/<name>` ref, which `git switch` refuses: resolve it by `workflows-core:read-only-repos` §3's chain, run against `<repo-root>`, and its **A switch takes the name** rule — rung 1 prints `origin/<name>` and `<base>` is what follows `origin/`; where rung 1 fails — `origin/HEAD` unset, or naming a ref that no longer exists (§3 rung 1) — `<base>` is the literal `main` or `master` whose ref rungs 2–3 find. Run `git -C <repo-root> switch <base> && git -C <repo-root> pull --ff-only` (the clean-tree check above already ran; if the fast-forward pull fails, offer the same stash/proceed/cancel choices). Where the chain is exhausted — no `origin`, or one holding neither branch — this command's own fallback applies: `<base>` is the local `main`, then `master`, whichever `git -C <repo-root> rev-parse --verify --quiet refs/heads/<name> >/dev/null` finds, switched to without the pull, there being no remote branch to bring it up to; with neither, `<base>` is the branch HEAD is on and nothing is switched. Then create the branch: `git -C <repo-root> switch -c <name>` (or, standalone, `git -C <repo-root> switch <name>` if it already exists, resuming this command's own branch — an inline run has already stopped on an existing one at Phase 0 step 2).

3. **Write the profile.** Create `<repo-root>/.dev-workflows/` if absent, then write the confirmed `.dev-workflows/docs-profile.yml` — on a refresh, the existing profile with only the changes Phase 4 confirmed, every field listed as kept exactly as it stood. It MUST conform to `${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/docs-profile-schema.md`. Apply the confirmed complementary CLAUDE.md additions to the repo's root `CLAUDE.md` (create the file if absent) — minimal, additive, scoped edits only; never restate changelog/owners rules owned by the docs-frontmatter skill.

4. **Format / lint.** If the repo has a formatter or linter (the `format`/`lint` commands captured in the profile), run it from `<repo-root>`, where every command the profile records runs, on the written files; fix anything it flags on those files. Skip silently if none is configured.

5. **Commit.** `git -C <repo-root> add .dev-workflows/docs-profile.yml CLAUDE.md` (only the files this command wrote), then commit:
   ```
   git -C <repo-root> commit -m "docs: add/refresh .dev-workflows/docs-profile.yml"
   ```

6. **Draft the PR message.** **Inline mode** (`--inline`): skip this step — control returns to `/document` (keyed mode), which owns the single PR draft (its Phase 8.5). **Standalone:** Detect the host (`git -C <repo-root> remote get-url origin`) and draft a copy-paste-ready PR title + body for Bitbucket or GitHub (whichever the remote indicates). Title e.g. `docs: bootstrap docs-profile for /document`; body summarising the profile (spaces, dev-servers, commands, tokens, branch-naming, images, prerequisites) and the CLAUDE.md additions. **Do not push, do not open the PR via any CLI** — present the branch name + the drafted message for the user to push and open themselves.

---

## Phase 6 — Final report

**Inline mode** (`--inline`): skip this report — control returns to `/document` (keyed mode), which produces the consolidated report (its Phase 9), and hands it two values: `profile_branch`, the branch Phase 5 step 1 named, and `profile_commit`, the commit Phase 5 step 5 made — `git -C <repo-root> rev-parse HEAD`, read immediately after that commit succeeds. `/document` renames that branch and squashes onto that commit (its Phase 6.2 and Phase 8.5), so it takes both from here rather than looking either up. Where Phase 5 made no commit — the operator kept the existing profile, or the refresh found nothing to change (Phase 4) — neither is handed back. **It also hands back two lists, whether or not Phase 5 made a commit**: `fixed_port_servers` and `server_command_defects`, the report's **fixed-port dev servers** and **dev-server command defects** lines below, each built exactly as the standalone report builds it, from the final profile (Phase 4's closing paragraph), and `none` where no server qualifies. Skipping this report must not drop them: both name something only the operator can fix by hand, and the profile `/document` goes on to use is that final one, so `/document` shows both to the operator (its Phase 0 step 4(c)). The rest of this section is the standalone report.

Output a structured report — do NOT ask any closing confirmation:

```
## Docs-profile Report

### Classification
SIGNIFICANT — cross-cutting synthesis of the whole docs repo; output steers all later /document runs

### Target repo
<resolved git root>  (<N> content root(s))

### Profile written
<repo-root>/.dev-workflows/docs-profile.yml  (bootstrapped | refreshed | kept — nothing written | up to date — nothing written)

### Fields: detected vs user-supplied
- detected: [spaces, dev_servers, commands, tokens, internal_links, announcement_pages, branch_naming, images, prerequisites — list those that were detected]
- user-supplied: [list the fields confirmed/filled in Phase 4]
- kept, not detected: [on a refresh, every field carried forward because detection produced no value for it — on a profile /docs-workflows:docs-init wrote, builds[], generator, frontmatter.* and dev_servers among them, and images where the scan found no image policy; "n/a — bootstrapped" otherwise]
- omitted: [e.g. "commands.per_space — the repo has only whole-repo scripts"; on a refresh, never a field the existing profile carried]
- declined: [where the operator chose "Keep existing, write nothing", every change and addition the Phase 4 diff proposed, none of them applied; "n/a" otherwise]
- frontmatter: pointers only → docs-frontmatter skill (+ changelog-guidelines.md, default-owners.txt); changelog/owners NOT re-specified
- fixed-port dev servers: [every dev_servers.servers[] entry in the written profile whose command carries no {port} token, by space — "none" when every command carries it. For each: "/docs-serve cannot fall forward from a collision on it, and --port cannot move it; add {port} by hand where its tool takes a port argument (docs-profile-schema.md, dev_servers.servers[].command)"]
- dev-server command defects: [every dev_servers.servers[] entry in the final profile (Phase 4's closing paragraph) whose command breaks one of docs-profile-schema.md's field rules for dev_servers.servers[].command in one of the ways below — the port rule judged for the two tools it names, and no other — by space, judged from the command and, where it runs a package.json script, from the script Phase 2 quoted for it — "none" when no command breaks one. For each, the rule it breaks and the fix, one line per rule broken:
  - it binds only the loopback — `-a 127.0.0.1:…`, `--host localhost`, or a tool whose own default bind is the loopback, run with no bind address of its own, a bare `mkdocs serve` among them: "binds only the loopback, so a browser on the host cannot reach it — make it bind 0.0.0.0, as `mkdocs serve -a 0.0.0.0:{port}` does";
  - it detaches its server — `setsid`, `nohup … &`, a trailing `&`, `docker run -d`, `docker compose up -d`: "detaches its server, so neither /document's render check nor /docs-serve can track or stop it — run the server in the foreground";
  - it runs `astro dev` without `ASTRO_DEV_BACKGROUND` set ahead of it, where the Astro the repository runs is 7 or later — the release that brought the background mode. That Astro is the version the repository's lockfile resolves; where the repository keeps no lockfile, the `version` its installed `node_modules/astro/package.json` records; and where it has neither, the range its `package.json` declares for `astro`, which settles the test only where every version the range admits is on the same side of the release (`^7.1.0` is 7 or later, `^6.0.0` is not, `>=6` settles nothing) — a range that settles nothing lists the command here with the version unsettled, never as clean: "Astro 7 detaches its dev server wherever it detects an AI coding agent, Claude Code among them, so neither consumer can track or stop it — set ASTRO_DEV_BACKGROUND=0 ahead of the command, Astro's documented opt-out"; or it runs `astro preview` without `ASTRO_PREVIEW_BACKGROUND` set ahead of it, where that Astro is 7.2 or later — the release that brought the background mode to the preview server: "Astro 7.2 detaches its preview server wherever it detects an AI coding agent, Claude Code among them, so neither consumer can track or stop it — set ASTRO_PREVIEW_BACKGROUND=0 ahead of the command, Astro's documented opt-out";
  - it runs a tool that moves off a busy port without pinning it, of the two whose pinning this line checks, the two the schema names — a command running any other tool is not judged on this rule, since whether it moves, and what pins it, is that tool's own behaviour, verified for these two alone, so the line neither lists nor clears it: VitePress without `--strictPort` — "moves to another port when its own is busy, so the port the profile records is not where it serves — add --strictPort, which makes a busy port an error"; or Astro, whose command line cannot pin the port, where the site's `astro.config.*` — read for this line, in the directory the command runs Astro from — sets no `strictPort: true` under `vite.server` — "moves to another port when its own is busy — set vite: { server: { strictPort: true } } in astro.config, since astro dev takes no --strictPort".
  This command changes none of them itself (D9, and Phase 3's rule against inventing a flag): which flag or setting a tool takes is that tool's business, so the operator fixes the command, or the tool's configuration, by hand]

### CLAUDE.md additions
- [what was added to the repo's CLAUDE.md, or "none — all conventions covered by the docs-frontmatter skill", or "none — the existing profile was kept, or was up to date, and nothing written"]

### Branch
<branch name created> | none — nothing written

### PR draft (copy-paste)
**Title:** <title>

<body>

[or "none — nothing written" where the existing profile was kept or up to date]

### Model Routing
- Classification: SIGNIFICANT
- Detection model (§2.1): <detection_model>
- Synthesis model (§2): <planning_model>
- Opus available: <true | false>
- Notes: <any §2.1/§2 fallback that occurred, or "none">
- [Under `run_flags.enforced_model`: `Model routing: bypassed — enforced <id> (flag|env)` in place of the two model lines above — both dispatched steps already carry the enforced id, per `workflows-core:model-routing/classification` §10.]
- Run flags: [the `Run flags: …` line, repeated, whenever Phase 0 printed one during this run (`workflows-core:run-flags` §6) — omit this line otherwise. `--skip-costs` and `--skip-feedback` do not apply to this command.]

### Git state
Branch <name> created with 1 commit on <repo-root>. NOT pushed and NOT merged — push and open the PR yourself when ready.
[or, where the existing profile was kept or up to date: "Nothing written — no branch, no stash, no commit; <repo-root>/.dev-workflows/docs-profile.yml is unchanged."]

### Assumptions & limitations
- [list any]
```

---

## Invariants (always enforced)

- ALWAYS validate the target is a writeable git work tree (Phase 0); stop with a named error if not
- ALWAYS pin detection to the §2.1 mid-tier Sonnet chain via the `task` `model:` override — never inherit the session model — and record `detection_model`
- ALWAYS run the synthesis on the §2 powerful (Opus) chain via the `task` `model:` override
- ALWAYS conform the written profile to `${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/docs-profile-schema.md`
- ALWAYS treat `frontmatter:` as pointers to the docs-frontmatter skill; NEVER copy changelog/owners rules into the profile
- ALWAYS show a field-level diff and confirm before overwriting an existing `.dev-workflows/docs-profile.yml` (idempotent refresh), and NEVER let a refresh propose changing or removing a field detection produced no value for — carry it forward verbatim, list it as kept, not detected, and never empty `spaces[]` — save an `images.policy` the schema's enum does not accept, which is listed as non-conforming and replaced or asked for, never carried forward (Phase 4)
- ALWAYS write the profile to `.dev-workflows/docs-profile.yml` at the TARGET repo's git work-tree top level (`<repo-root>`, the schema's **Where the profile lives**) — never the plugin, and never a directory below that top level
- NEVER push or auto-merge — output a reviewable PR (branch + commit + drafted PR message) for the user to push; and where a refresh is answered "Keep existing, write nothing", or its diff lists no change, write nothing at all — no branch, no stash, no commit — and end on the Phase 6 report, or, in inline mode, return the existing profile to `/document` (Phase 4)
- NEVER switch an inline run onto an existing `dev-workflows/docs-profile-bootstrap` — stop with `DOCS_PROFILE_BOOTSTRAP_BRANCH_EXISTS`, naming the branch, its base and where it forked, at Phase 0 step 2, before any question, scan or synthesis; a standalone run may resume its own existing branch (Phase 5 step 2)
- ALWAYS use `choices` arrays for decision points; recommended default first and labelled "(Recommended)"; 2–4 options, and never author an "Other" option — the harness supplies the free-text escape itself (`workflows-core:escalation-rules` §0)
- ALWAYS reference plugin paths with `${CLAUDE_PLUGIN_ROOT}`
- ALWAYS produce the Phase 6 report as the final output, noting any §2.1/§2 model fallback

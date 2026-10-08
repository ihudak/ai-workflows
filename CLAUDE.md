# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this repo is

A public, open-source Claude Code plugin marketplace hosted at `github.com/ihudak/ai-workflows`.
Added with `claude plugin marketplace add ihudak/ai-workflows`, after which it appears in
that machine's `~/.claude/plugins/known_marketplaces.json` as `shipwright`. Registration is
per-machine — do not assume any given environment has it.

## Structure

```
.claude-plugin/marketplace.json   ← plugin catalog (do not reformat; Claude Code parses it)
plugins/
  <plugin-name>/
    .claude-plugin/plugin.json    ← required: name, description, author
    README.md
    LICENSE
    commands/                     ← slash commands (.md files)
    agents/                       ← subagent system prompts (.md files, YAML frontmatter required)
    hooks/
      hooks.json                  ← hook declarations; use ${CLAUDE_PLUGIN_ROOT} for paths
      *.sh                        ← hook scripts
    skills/<name>/SKILL.md        ← skills, if any
    references/                   ← vendored reference docs the commands consult
    docs/                         ← human-facing docs tree (index, per-command, reference pages)
```

## Active plugins: dev-workflows, product-workflows, docs-workflows, and their shared dependency workflows-core

`plugins/dev-workflows/` provides five slash commands — `/design`, `/implement`, `/ready`, `/upgrade`, and `/vuln` — plus twelve reusable subagents, one hook, sixteen reference files, and no bundled skill. It depends only on `workflows-core`, and does not use `prose-style` at all.

`plugins/product-workflows/` provides sixteen slash commands — the idea→PRD→ARD→specification ladder (`/idea` → `/create-prd` → `/update-prd` → `/create-ard` → `/specify`), `/epics`, `/harvest-decisions`, `/promote-decisions`, a six-command BRD-to-PRD route (`/brd-intake`, `/brd-split`, `/prd-ground`, `/brd-interview`, `/brd-package`, `/brd-reconcile`), and the effort proposals `/prd-proposal` and `/brd-proposal` — plus fourteen subagents, twelve reference files, one hook, no bundled skill, and three environment variables (`SPECS_PATH`, `REPOS_PATH`, `DOCS_PATH`). It depends on `workflows-core` and `prose-style`, with no absent case for the second (S12). `dev-workflows` does not depend on `product-workflows`.

`plugins/docs-workflows/` provides seven slash commands — `/document`, `/docs-profile`, `/release-notes`, `/docs-init`, `/docs-brand`, `/docs-serve` and `/docs-audit` — plus eleven subagents, twenty-three reference files, one bundled skill (`docs-frontmatter`), and two hooks. It depends on `workflows-core` and `prose-style`, and carries no absent case for its style gate: `docs-style-checker` dispatches `prose-style-checker` on every run — roles in `.claude/rules/docs-workflows.md`. Neither `dev-workflows` nor `product-workflows` depends on `docs-workflows` ([why](docs/maintainers/rationale.md#docs-workflows-not-a-dependency)). `/docs-serve` writes no deliverable, so it is absent from every caller list by design, not oversight; the rest of its pure-utility rule is in `.claude/rules/docs-serve.md`.

`plugins/workflows-core/` carries the family's shared foundation — reference corpus, agents, skills, two session-wide hooks, and seven family-meta commands (listed, with detail, in `.claude/rules/workflows-core.md`). **All three of `dev-workflows`, `product-workflows`, and `docs-workflows` name it in `dependencies`**; an unsatisfied dependency disables the plugin that named it rather than letting it half-run, and there is no degraded mode to fall back to.

The catalog also ships `prose-style`, `guideline-reviewers`, `acli` and `obsidian-llm-wiki`; none has a rules file of its own, and `obsidian-llm-wiki` carries its own `CLAUDE.md`.

The workflow map is in the `## Workflow map` sections of `.claude/rules/*.md`, one per plugin or split-out area.

**Internal reference convention:**
- Agents are invoked by `subagent_type` (`<plugin>:<agent>`, e.g. `dev-workflows:risk-planner`, `workflows-core:impl-maintenance`) — never by reading the agent file. Claude Code loads the agent body as its system prompt and honours its `model:` frontmatter. **An agent crosses a plugin boundary for free**; a reference file does not.
- **A shared reference is cited `workflows-core:<name>` and loaded through the loader skill** — `Skill(skill: "workflows-core:reference", args: "<name>")`, with an optional second whitespace-separated token naming an entry point within the reference to execute inline (`args: "specs-repo-git specs-preflight"`). Never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to the *reading* plugin, which does not carry the corpus. Every command and agent outside `workflows-core` that cites one carries a preamble saying so, and `check-docs.sh` check 16 gates the contract in both directions.
- Inside **agent** and **skill** bodies (and `hooks.json` / MCP / monitor configs), reference the reading plugin's **own** bundled files via `${CLAUDE_PLUGIN_ROOT}/...`. **This variable DOES expand in slash-command bodies**: `${CLAUDE_PLUGIN_ROOT}` arrives as the plugin's real location — the working tree under a directory-source marketplace, not the cache — while `${DOCS_PATH:-/workspace/docs}` and `${REPOS_PATH:-/workspace}` arrived **literal** in the same live run. `$ARGUMENTS` is the harness's argument substitution. ([why](docs/maintainers/rationale.md#plugin-root-expansion))
- Slash **commands** that need their own plugin's bundled content invoke a skill that resolves `${CLAUDE_PLUGIN_ROOT}` on their behalf; `workflows-core`'s `reference` skill is the general form of that, and its `model-routing` skill the named one.
Do NOT hardcode `~/.claude/plugins/data/...@.../` paths — that directory holds only empty per-plugin state; installed content lives under `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`.

**When editing any of these plugins:** update the files under `plugins/<name>/` directly.
Do NOT edit `~/.claude/claude-config/` — that repo is retired and will be deleted.

## Adding a new plugin

1. Create `plugins/<name>/` with `.claude-plugin/plugin.json`.
2. Add content directories (`commands/`, `agents/`, `hooks/`, etc.).
3. For hooks: create `hooks/hooks.json` using `${CLAUDE_PLUGIN_ROOT}` for all paths.
4. Register in `.claude-plugin/marketplace.json` with `"source": "./plugins/<name>"`.
5. Commit and push to `main`. Claude Code picks up the change on the next `claude plugin update` of that plugin, and a restart.

## Conventions

- Agent `.md` files must start with YAML frontmatter (`---`) containing at minimum `name` and `description`.
- Hook scripts must exit 0 — they must never block Claude.
- `hooks.json` `matcher` field (for PostToolUse) goes at the entry level, not inside the hook object.
- Bundled and shared files are reached only as the Internal reference convention above says.
- MIT license applies to all plugins unless a plugin directory has its own LICENSE file.

## Where the rest of the guidance lives

Area rules live in `.claude/rules/`; each file loads only when you open a file matching its `paths:` with the **Read tool**. A Bash `cat`, `sed`, `grep` or `git diff` loads no rules file, and only the Read tool is proven to trigger loading, so Read a file in the area before editing or reviewing there.

The table abbreviates each file's `paths:` frontmatter, which is authoritative: paths are under `plugins/` unless shown, and `dir/`: `a`, `b` means `dir/a` and `dir/b`.

| Rules file | `paths:` | Holds |
|---|---|---|
| `gates.md` | `scripts/**`, `.github/**` (repo root) | what each `check-docs.sh` check enforces and cannot see; the rule every gate shares |
| `gates-id-grammar.md` | `scripts/`: `check-id-grammar.sh`, `spec-id-baseline.txt`, `validate-catalog.py`; `.github/workflows/validate-catalog.yml` (repo root) | the ID-grammar gate |
| `gates-validate-catalog.md` | `scripts/validate-catalog.py`, `.github/workflows/validate-catalog.yml` (repo root) | `scripts/validate-catalog.py` |
| `gates-mermaid.md` | `scripts/mermaid/**`, `.github/workflows/validate-catalog.yml` (repo root) | the mermaid gate |
| `dev-workflows.md` | `dev-workflows/**` | invariants, map, callers, three authorities |
| `dev-workflows-tests.md` | `dev-workflows/`: `commands/implement.md`, `agents/test-*.md`, `docs/commands/implement.md`, `references/handoff/test-*.md`, `docs/reference/test-suite-detection.md`, `references/code-handoff.md` | `/implement` invariants, test-writing requirement |
| `product-workflows.md` | `product-workflows/**`; `dev-workflows/commands/`: `design.md`, `ready.md`, `implement.md`; `docs-workflows/commands/release-notes.md`; `workflows-core/references/`: `addressing.md`, `grilling-technique.md`, `prd-format.md` | invariants, map, callers |
| `brd-route.md` | `product-workflows/**`; `dev-workflows/commands/`: `design.md`, `ready.md`, `implement.md`; `workflows-core/references/addressing.md`; `workflows-core/commands/frames.md`; `docs-workflows/commands/`: `document.md`, `release-notes.md` | BRD-route map lines, folder-kind invariants |
| `brd-route-detection.md` | `product-workflows/`: `commands/`: `create-prd.md`, `create-ard.md`, `specify.md`, and their `docs/commands/` pages | BRD-route detection |
| `prd-ground-verification.md` | `product-workflows/`: `commands/prd-ground.md`, `docs/commands/prd-ground.md`, `agents/grounding-verifier.md` | `/prd-ground`'s blind verification |
| `docs-workflows.md` | `docs-workflows/**`; `product-workflows/`: `commands/epics.md`, `agents/epic-*.md`, `docs/commands/epics.md` | invariants, map, callers |
| `docs-workflows-gates.md` | `docs-workflows/`: the three gate references; `/document`, `/docs-init`, `/docs-brand`, `/docs-serve`; `doc-planner`, `doc-reviewer`, `docs-style-checker` | three gate authorities |
| `docs-serve.md` | `docs-workflows/`: `commands/docs-serve.md`, `docs/commands/docs-serve.md`, `references/docs-profiles/render-verification.md`, `references/toolchain-preflight.md` | `/docs-serve` |
| `release-notes.md` | `docs-workflows/`: `commands/release-notes.md`, `agents/release-notes-writer.md`, `references/release-note-types.md`, `docs/commands/release-notes.md` | `/release-notes` and its authority |
| `docs-grounding.md` | `workflows-core/`: `references/*-grounding.md`, `agents/*-grounder.md`; and 23 command files: the nine docs-grounding consumers, `/design` (architecture only) and thirteen that resolve none | docs/architecture grounding |
| `workflows-core.md` | `workflows-core/**`, `*/commands/*.md`, `*/agents/*.md` | plugin facts, model routing, authorities, map |
| `workflows-core-triage.md` | `workflows-core/references/finding-triage.md` and the commands and agents citing it | the finding-triage authority |
| `workflows-core-git.md` | `workflows-core/scripts/session-branch.py`; `*/commands/*.md`, `*/references/**` (the git references among them), `*/agents/*.md` | git authorities and invariants |
| `workflows-core-read-only.md` | `workflows-core/references/read-only-repos.md` and the agents, commands and references its paragraph names | the read-only-repos authority |
| `claim-sweep.md` | `plugins/**`, `README.md`, `CLAUDE.md`, `docs/maintainers/**` (repo root) | the claim-expiry sweep's refinements |
| `plugin-updates.md` | `plugins/**`, `.claude-plugin/marketplace.json`, `CLAUDE.md` (repo root) | updating installed plugins after editing |

The evidence behind the rules — measured cases, refused widenings, history — is in `docs/maintainers/rationale.md`, reached by each rule's `why` link. It is never auto-loaded; read a rule's section before proposing to change the rule.

## Editing discipline

- **Nothing gates any number written in `CLAUDE.md` or `.claude/rules/`.** Re-derive every number in them against the tree when you touch either, and prefer a citation to a count wherever one will do. **Where you do count, count the thing and not your own rendering of it** — state the command and the scope it ran over beside the number, so the next reader can re-run it. ([why](docs/maintainers/rationale.md#number-gating))
- **Prose is executed.** Command, agent and reference prose is run literally by agents, in order, so a false sentence there is a defect, not a typo.
- `plugins/workflows-core/references/instruction-file-maintenance.md` is the **single source of truth** for changes to agent-instruction files (`CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, rules files, and the `references/*.md` of `workflows-core` and of every plugin that depends on it), consumed by `impl-maintenance` and binding on hand edits to `CLAUDE.md` and `.claude/rules/*.md`: verify every command claim against the thing that runs it; a pointer names an observable trigger, never one the agent must judge; two live contradictory instructions is a defect; retirement needs grounds, never "it looks derivable" and never "nothing has failed on it lately". (Narrowing is a deletion: see the drift-risk bullet.)
- **Resolve an identifier against a known set; never parse one out of free text.** A key re-derived by pattern — out of a branch name, a path, a slug — is a guess that a longer or differently-shaped identifier falsifies. Where there is no set to resolve against, that absence is the finding to report; a wider pattern is not the answer to it. `workflows-core:specs-repo-git` §3.5's `branch-key` is the worked example. ([why](docs/maintainers/rationale.md#resolve-against-a-known-set))
- **Re-measure in one place and cite it everywhere else.** A recipe that returns a wrong answer is worse than none, because the next reader trusts what it returns: **match the execution phrase, not the bare name** — a bare-name grep counts a negative mention as a caller. ([why](docs/maintainers/rationale.md#recipe-returns-wrong-answer))
- **A note saying a feature or an edge does not ship is a claim with an expiry date, and one left standing beside the now-shipped feature is its own defect.** No script gates such prose. When a capability lands, sweep for the sentences that said it would not — **by phrase, never by line number** — and rewrite each against what the shipped thing actually enforces, read out of its own Phase 0 rather than assumed. A sentence that named the absence as its *reason* for an offer needs a new reason, not a deletion. ([why](docs/maintainers/rationale.md#claim-expiry-sweep)) Its refinements are in `.claude/rules/claim-sweep.md`.
- **A sentence is true in the context it was written in; two kinds of edit break that** — one that changes the context under a sentence that stays put, and one that leaves a sentence relying on context its reader does not carry. ([why](docs/maintainers/rationale.md#sentence-context))
  - **Extent face.** Widening the extent of a claim, a trigger or a condition puts every neighbouring sentence under a premise it was not written for, where no phrase sweep reaches. **Enumerate the cases the new extent now reaches and read each against the text around it** — a trigger's cases, a condition's branches, a rationale's neighbouring claims; for a question, check **every effect it states against the preconditions the new trigger does not carry**, in the paragraphs the old precondition kept out of reach too. Re-read, never qualify every match; **where you do qualify, qualify by the class and not by the member in front of you**. After adding an effect or a reason, re-read the whole paragraph it landed in against the premise you have just moved.
  - **Pointer face.** Re-read a sentence from where it lands for a **pointer** (`this`, `that`, `here`, `above`, `below`, `it`) that re-points at whatever is now nearest, and an **omitted subject or object** carried from earlier in the sentence. **One tell is mechanical and covers one pointer only**: a bare `this <noun>` whose noun names a **kind of file** that is not the file the block belongs to; `above`, `below`, `it` and an omitted subject have no tell and fall to the re-read, which is the check — the tell is a way into it, never a substitute for it.
  - A face that needs a check of its own is a rule of its own, and a **third check** means this has stopped being one rule: the root stays in `CLAUDE.md` and the checks move to a `workflows-core` reference the sentence-context bullet cites. The test is the root and the checks, never the length.
- **A sub-project's verification record is written last** — after the final fix wave, never before it. Re-derive every expected value against the tree being verified, and never copy an `expect N` from another plan. ([why](docs/maintainers/rationale.md#verification-record-last))
- **Measure the population a fix serves before designing the fix, not after** — as for a gate widening (`.claude/rules/gates.md`, intro). Ask the reachability question first, as a count — which trees, which users, which states — and trace it **per finding**. Where the answer is "none", the defect is in the claim that made it look live, and the fix belongs where that claim is written rather than in every consumer of it. The counter-case: *newly shipped* machinery also has a population of zero, which is why it has not bitten yet, not a reason it will not. ([why](docs/maintainers/rationale.md#measure-the-population))
- **A rule's drift risk is not proportional to how obvious the rule looks.** **Before inlining a shared rule into its callers, itemise what the shared file still says, line by line, against the premise being retired.** "What remains is obvious" is a judgement about the lines you remembered, not the ones that are there. `workflows-core:instruction-file-maintenance` already binds the same point from the other direction: a rewrite that narrows a rule is a deletion, and is itemised separately. ([why](docs/maintainers/rationale.md#drift-risk))

## Hard constraints

- **A plugin `description` is a stable capability blurb, never a changelog.** Hard budget: **1024 characters** in both `plugin.json` and the `marketplace.json` entry; `scripts/validate-catalog.py` fails the build above it and warns above 900. A new capability **replaces** wording; it never appends. Release detail belongs in `CHANGELOG.md`. ([why](docs/maintainers/rationale.md#description-budget))
- **Every requirement ID a plugin doc teaches is the bracketed `[PREFIX#N]` form** — `[US#1]`, `[AC#1]`, `[SM#1]`, `[SMC#1]`, `[UC#1]`, `[FR#1]` in a PRD and `[AD#1]` in an ARD — never the dash-separated form. `scripts/check-id-grammar.sh` enforces it: run `./scripts/check-id-grammar.sh --root .` before pushing. `CHANGELOG.md` is excluded (history keeps the old form), and a line that has to quote the legacy form in order to forbid or report it carries an `id-grammar-ok` HTML-comment marker, audited per file so the marker never becomes a general escape hatch. ([why](docs/maintainers/rationale.md#id-grammar))
- **One key namespace.** Every key names a **folder** under `$SPECS_PATH/specifications/` and is validated for shape only against `workflows-core:addressing` §1's single grammar — `^[A-Z][A-Z0-9_]*(-\d+)+$`, which fixes no depth; nothing is looked up anywhere. `workflows-core:pre-lint`'s Jira-key collision grep (`\b[A-Z]{2,10}-[0-9]+\b`) is an **autolink detector**, not a key validator, and its narrowness is exactly what makes it correct: never widen it. A user's own tracker identity lives in the reserved `workitem_key` frontmatter field, which the plugin preserves and displays and never mints, validates, or resolves a folder by. ([why](docs/maintainers/rationale.md#one-key-namespace)) <!-- vendor-token-ok: names the tracker whose key shape the pre-lint autolink detector matches; the detector's narrowness is the point being made -->
- **Each plugin in `check-docs.sh`'s `PLUGIN_RELS` keeps its human-facing documentation in `plugins/<name>/docs/`, not in its README.** **The retired README is a source of topics, never a source of facts**: every claim on a page is derived from the thing that runs it — a synopsis from the command's argument-parsing phase, phases from its `## Phase` headings, gates from its reviewer dispatch, the agent inventory from `agents/`. `scripts/check-docs.sh` enforces the tree: run `./scripts/check-docs.sh --root .` before pushing. Adding a command, agent, reference file, hook, skill, or environment variable without its docs entry fails the build. ([why](docs/maintainers/rationale.md#docs-tree))
- **Vendor neutrality:** no text file under `plugins/` or in the instruction tiers (`CLAUDE.md`, `.claude/rules/`, `docs/maintainers/`) names a tracker unless its line, or the fence opening its block, carries `<!-- vendor-token-ok: <why> -->`; `CHANGELOG.md` is exempt as history; check 13 enforces it. ([why](docs/maintainers/rationale.md#check-13))
- **Identity quarantine:** no page under `docs/` may name a marketplace or a container repo — `getting-started.md` is the single sanctioned exception, pinned by check 7; check 10 enforces it ([why](docs/maintainers/rationale.md#check-10)). The organisation this plugin was extracted from is never named anywhere in the repository, with no marker and no exception; check 14 enforces it ([why](docs/maintainers/rationale.md#check-14)).
- **Every ```` ```mermaid ```` block in every tracked markdown file must parse.** **Quote any node or edge label containing `[ ] ( ) { } |` or `#`** — `-->|"verified [CG#n]"|`, never `-->|verified [CG#n]|`. `scripts/mermaid/check-mermaid.mjs` enforces it. ([why](docs/maintainers/rationale.md#mermaid-gate))
- **Date every `— Unreleased` `CHANGELOG.md` section before it reaches `main`**: whatever is on `main` is what users install, and check 18 fires only on the push that publishes it. ([why](docs/maintainers/rationale.md#check-18))
- **Every `choices:` array is an `AskUserQuestion` call, so the harness's schema is the authority on its shape**: `minItems: 2, maxItems: 4`, and *"There should be no 'Other' option, that will be provided automatically."* `workflows-core:escalation-rules` §0 states the rule, and check 12 enforces it. The free-text option is *unconditional*, so the four pickers through which a customer's authority enters the decision register cannot omit it — a free-text answer there is **normalised into the picker's own vocabulary or re-asked, never written through**. A fifth option moves rather than disappears: `workflows-core:next-phase-offer`'s overflow rule puts the full menu in prose and lets the array carry the likeliest, and `workflows-core:epic-picker` *The cap* does the same for a picker built from a directory listing. Every command of the family presents a phase's `choices:` array verbatim — order, wording, and the `(Recommended)` marker are not the orchestrator's to change (`workflows-core:escalation-rules`' *Choice lists are presented verbatim*). ([why](docs/maintainers/rationale.md#choices-arity))
- Every command that writes into `$SPECS_PATH` runs `specs-preflight` at run start (Phase 0 in most commands, Step 0 in `/vuln`, the shared `## Mode detection` section in `/document`), once its run key set is known — after address resolution where that comes first, and none on a run that stops before the preflight (`workflows-core:specs-repo-git` §3) — and `commit-artifacts` as its last action, or immediately before a phase that cedes control (`workflows-core:specs-repo-git` §4) — bounded to the artifact paths, switching only plugin branches and pushing only per §4 step 5 there, and reported once as a `Specs repo:` line.
- **`workflows-core:addressing` §7's shared-fallback adoption is additive, and it keeps no totals.** Every command that addresses a folder reaches the tree through `resolve-address` (§3), and §5's legacy unprefixed fallback is tried ONLY where the prefixed glob already returned nothing — so a key whose folder carries its kind prefix resolves exactly as it did before, and a command that creates the folder it did not find creates it **prefixed** (§2). The fallback honours a legacy folder that exists; it never proposes one. **Re-derive the set with `grep -l resolve-address plugins/*/commands/*.md`; do not count it off §7's table**, which is a finding aid and not the set. ([why](docs/maintainers/rationale.md#addressing-fallback-totals))
- **Any kind gate must test the artifact it actually cares about, never the folder's asserted kind** — a BRD-route slice is `PRD-`-prefixed yet asserts `kind: brd`; `.claude/rules/brd-route.md` states why, and how the existing gates apply the rule.
- `/create-ard`, `/design`, `/implement`, `/specify`, `/epics`, `/ready` respect the applicable ARD via `workflows-core:ard-resolution`; an `AD#N` Rule violated without a recorded "ARD deviation" is a reviewer BLOCKER.
- A phase is not finished until its artifact is on the specs repo's default branch — every producer offers branch + commit + push + PR, and every consumer executes `require-on-main` before expensive work; an absent optional input still delegates to the command's pre-existing behaviour and never becomes a prerequisite (multi-component PRDs: `workflows-core:ard-resolution`).

## Running the gates

**Run the gates as one `&&` chain and read the chain's own exit code.** `.github/workflows/validate-catalog.yml`'s `run:` steps are the authoritative list of them, in order. A trailing `echo "EXIT=$?"` makes the invocation's own status 0, so read the printed value. ([why](docs/maintainers/rationale.md#gate-chain-exit))

`scripts/validate-catalog.py` fails `CLAUDE.md` above 40,000 characters and warns above 36,000, warns on a rules file above 20,000, and fails a rules file without `paths:` or with a glob matching no file outside `.claude/rules/` — overflow belongs in a rules file or the rationale (`.claude/rules/gates-validate-catalog.md`).

## Shared authorities

Each reference below is the **single source of truth** for what it owns; `<plugin>:<name>` is `plugins/<plugin>/references/<name>.md`. Its full paragraph — consumers, entry points, invariants — is in the `.claude/rules/` file named.

- `workflows-core:model-routing/classification` — complexity classes, the model fallback chain, the Opus review checklist, the `model_routing` block, the §8 scan fan-out → `workflows-core.md`
- `workflows-core:run-flags` — `--skip-costs`, `--skip-feedback`, `--enforce-model` and their `WORKFLOWS_*` env defaults → `workflows-core.md`
- `workflows-core:source-truth` — the Implementation-vs-Description discrepancy-escalation protocol → `workflows-core.md`
- `workflows-core:prose-formatting` — output line-wrapping: never hard-wrap prose → `workflows-core.md`
- `workflows-core:implementation-format` — the append-only `implementation.md` record, the `[<key>]` commit convention, the two-source read → `workflows-core.md`
- `workflows-core:doc-structure-conventions` — traceability boundary, callout scope and adjacency, component-pattern fidelity → `workflows-core.md`
- `workflows-core:finding-triage` — the orchestrator's step between a reviewer's findings and a fixer (keep, mark unverified or dismiss), its re-review rules, and the patch gate → `workflows-core-triage.md`
- `workflows-core:specs-repo-git` — `specs-preflight`, `commit-artifacts`, the bounded write authority, the specs-repo git hard rules → `workflows-core-git.md`
- `workflows-core:phase-handoff` — `handoff-to-main`, `require-on-main`, the branch-prefix authority, the handoff consent choice → `workflows-core-git.md`
- `workflows-core:read-only-repos` — read-only mount detection, write-free ref reading, the `prep` output contract → `workflows-core-read-only.md`
- `workflows-core:docs-grounding` — `$DOCS_PATH` grounding: the resolution gate, `resolve-docs-grounding`, grill-rank / writer-attach → `docs-grounding.md`
- `dev-workflows:bug-diagnosis` — repro first, ranked hypotheses, tagged instrumentation, a regression test at a seam → `dev-workflows.md`
- `dev-workflows:code-handoff` — the code repo's `finish-code-branch`: commit, consent-gated push and pull request; a fixer's per-unit revert (§6) → `dev-workflows.md`
- `docs-workflows:release-note-types` — the release-note section map, per-section draft shape and prose rules, the deprecation note → `release-notes.md`
- `docs-workflows:gate-ledger` — verification-gate accounting: the six outcomes and the `/document` gate registry → `docs-workflows-gates.md`
- `docs-workflows:repo-verification-gates` — a docs repo's own pre-PR checklist as `repo_verification_gates` → `docs-workflows-gates.md`
- `docs-workflows:toolchain-preflight` — the pre-write environment check, the `toolchain` block, each tool's test → `docs-workflows-gates.md`
- `workflows-core:instruction-file-maintenance` — changes to agent-instruction files → § Editing discipline above

## Command, agent, and skill taxonomy

- **Commands** (`commands/`) are the user-facing slash commands: they own the end-to-end workflow, gather context, decide whether to branch, test, or review, and may dispatch helper agents via the `task` tool. Each is **typed-only** (`disable-model-invocation`) unless a file runs it as `skill: "<plugin>:<name>"` or a skill shares its name; `scripts/validate-catalog.py` checks ([why](docs/maintainers/rationale.md#typed-only-commands)).
- **Agents** (`agents/`) are Claude Code sub-agent system prompts, not user entry points: each does one bounded job — planning, research, review, fixing, test writing, grounding, or maintenance — and returns its result to the invoking command.
- **Skills** (`skills/`, optional) package durable instructions or domain knowledge that multiple commands or agents may consult; a skill is neither a command nor an agent. If a plugin has no `skills/`, keep shared runtime docs under `references/`.
- **Working rule:** keep the three roles separate so workflows stay predictable.

## Behavioral guardrails (Karpathy) — marketplace-specific notes

These notes add to the user-scope Claude guidance only the marketplace-specific behaviors that are easy to forget during workflow edits.

- **Goal-Driven Execution** maps directly onto the existing `test-baseliner` → implementation → `test-writer` → re-run flow enforced by `dev-workflows`. Frame each command invocation as a verifiable goal up front so the test gates have a concrete target to check.
- **Surgical Changes** applies in both directions when you edit command docs, agent prompts, hook declarations, or `workflows-core:model-routing/classification`: if you remove a `model_routing` field, phase, or workflow edge, remove every cross-reference to it in the same change. Stale references between commands and agents silently break the workflow.

## Git

- `origin` → `git@github.com:ihudak/ai-workflows.git`
- Default branch: `main`
- **Verify the current branch immediately before every commit — `git branch --show-current`.** This checkout can be shared by more than one agent session at once, and a `git checkout` in any of them moves the working tree for all of them. The branch checked at the start of a run is not evidence about the branch you are on now. ([why](docs/maintainers/rationale.md#verify-branch-before-commit))
- **When work must land on `main` while this tree sits on another branch, use `git worktree add` — never `git checkout` here.** Switching this tree yanks it out from under whoever else is working in it. Cherry-pick or commit in the temporary worktree, run the gates there, push from there, then `git worktree remove`. Leave another session's branch exactly as you found it: not rewritten, not deleted, not pushed. ([why](docs/maintainers/rationale.md#worktree-not-checkout))
- **Never bare `git stash`** — the stash stack is shared with every worktree and session; use a WIP commit, or `git stash push -u -m <tag>` and `apply <sha>`.

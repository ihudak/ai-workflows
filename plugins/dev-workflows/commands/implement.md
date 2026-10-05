---
name: implement
description: End-to-end code implementation workflow. Classifies task risk, creates a branch, plans (Opus for SIGNIFICANT/HIGH-RISK), implements, writes tests, runs Opus code review, and performs post-session maintenance.
allowed-tools: Read Edit Write Bash Glob Grep Task Skill WebFetch
---

Implement the following: $ARGUMENTS

Usage: `/implement <ADDRESS> | <prompt> [@file…] [@spec-folder] [@repo…] [--no-commit] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]`

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

---

## Phase 0 — Load and classify inputs

**Strip the run flags first.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS` before anything else reads a token: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its maintenance, cost and routing steps — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. Every later step parses only what it leaves. Because a direct run's `<prompt>` is free prose kept verbatim, that prose is protected per `workflows-core:run-flags` §3 step 1: a run-flag token before the prompt begins, or in a trailing run at the very end of `$ARGUMENTS`, is stripped, but one written inside the prompt itself is kept as prompt text, even where it looks like a flag. **Strip `--no-commit` next**, before any other parsing: it is the only command-specific flag this command takes, and an unstripped flag is read as free-text prose and lands in the task description. When present, Phase 4.6 is skipped entirely and the changes are left in the working tree. It is the one opt-out from a commit that is otherwise prompt-free (`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §1 rule 5) — typed rather than clicked, which is the difference — and a run under it says once what it costs: the work is recoverable only on this machine, and `/document` and `/release-notes` will not find it later.

**The working directory is classified next**, straight after the run flags — before address resolution and before any `@path` token is read, so a run that stops here has resolved no address, run no specs-repo preflight and shown no Epic picker. Run `git rev-parse --is-inside-work-tree` there. Unless it prints `true`, stop: `/implement` branches the repository it runs from, so it runs only from inside a work tree. It prints `false` inside a `.git` directory or a bare repository; where it fails instead, show git's error beside that, since the error names the cause — no repository around the directory, or one git refuses to use, as its ownership check does. Where it prints `true`, the working directory is the Code repo row's (the table below) whatever it holds, and its repository, at its top level, is the one this run branches and changes. It is not an `@path` token: no other row is tested against it and no notice below is printed for it, so a `prompt.md` or `*-design.md` file in it is read only where a token names it.

`$ARGUMENTS` may contain free-text prose plus **zero or more `@path` tokens** (today's single-`@file` form is a subset). Resolve each `@path` relative to the current working directory. Classify each `@path` **by inspection, not by matching the path string**:

| Detected as | Recognition rule | Handling |
|---|---|---|
| **Spec file** | a single `.md` file | read fully; use as the description/spec |
| **Spec folder** | a directory containing `prompt.md` and/or a `*-design.md` | read all `.md` specs within; fold into the description |
| **Specs folder** | a directory under `specifications/` that `resolve-address` resolves — its `kind:` and `key:` read off the folder's carrier (`workflows-core:addressing` §4) | hand to the folder read in Phase 1.7 |
| **Code repo** | a directory where `git -C <path> rev-parse --is-inside-work-tree` prints `true` (includes the cwd) | scan target in Phase 1.7 — or, where its top level (`git -C <path> rev-parse --show-toplevel`) is that of a code repository already classified here (the working directory's included), a search hint for that repository's scan and for Phase 2A/2B's exploration |

Test the rows top to bottom for each `@path` token: the first that matches classifies it, so a spec or specs folder below a repository's top level is that folder, never a code repo. A token naming the working directory (`@.`, or any other path that resolves to it) is classified the same way, so below the top level a spec folder there is read as one; the repository it lies in is still the run's, by the working-directory rule above. An `@path` that is its own work tree's top level (`git -C <path> rev-parse --is-inside-work-tree` prints `true` and `git -C <path> rev-parse --show-prefix` prints nothing) is always the Code repo row's whatever else it holds. Where such an `@path` also matches the Spec folder row, print `<path> is a repository's top level and is read as a code repository — its prompt.md and *-design.md files are not read into the description; name each by file (@<path>/<file>) to read it`.

**Each token's own checks run as it is classified**, before the no-description stop below and before the specs-repo preflight. A token naming nothing on disk, or a directory that is neither a recognized folder type nor a git repo, is surfaced by name — never silently skipped — and the run asks whether to continue without it or stop (`workflows-core:model-routing/classification` §8.4); where `git -C <path> rev-parse --is-inside-work-tree` failed rather than printing `false`, show git's error beside it, since a repository git refuses to use (its ownership check) is not one of no kind. A single `@file` that exists but cannot be read stops the run, reporting the error. A token under `$SPECS_PATH` is no exception: it is read where it sits, out-of-contract, as the gate below says of a lone spec or design `@path`. **A direct run with no description** — no prose, and no Spec file or Spec folder token left — then stops, still before the preflight: `/implement needs a description — prose, an @<file>.md, an @<folder> that is not a repository's top level, holding prompt.md or a *-design.md, or a <KEY> or @<specs-folder> address`, followed by the notice's remedy where a token above printed it and, where the working directory holds a `prompt.md` or `*-design.md` file that no such notice named, a line naming each by file (`@prompt.md`) — listed, not read. The design-doc open-question guard (Rules, below) runs next, on either mode and still before the preflight: its input is always a token, read where it sits.

**Address resolution.** After the working directory and before the per-`@path` classification above, look for a **single positional
address** in `$ARGUMENTS` — a `<KEY>`, or an `@<path>` naming a folder in the specs tree. Present →
resolve it with `resolve-address` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3) and the run
is **keyed**; absent → the run is **direct** (free-text / `@file`, this command's existing flow).
That is the whole mode test, and it unifies the input grammar with `/document`. **On a `<KEY>`,
`$SPECS_PATH` comes first:** if it is unset, stop naming it before resolving anything
(`choices: ["Set SPECS_PATH (enter the path)", "Cancel"]`, `workflows-core:escalation-rules`
*Required path environment variable unset*) — a key is found only by searching the specs tree, so
with no tree the `absent` stop below would name the wrong cause and offer a re-enter that cannot
succeed. An `@<path>` address needs no specs tree: it is resolved without the variable and runs on,
its record written into the folder it names, and a direct run is unaffected. `ambiguous` and
`misrooted` are §3's two hard stops, the first naming every match and the second, on either address form,
a `$SPECS_PATH` set inside the specs tree. **`status: absent` is a stop, never a fall-through to direct mode**
— the `key dir not found` rule in `workflows-core:escalation-rules` (`["Re-enter key", "Cancel"]`),
naming what creates a folder this command reads: a `PRD-` folder comes from
`/product-workflows:idea <KEY>` or `/product-workflows:create-prd <KEY>` on the idea route and from
`/product-workflows:brd-split` on its parent BRD on the BRD route; an `EPIC-` folder from
`/product-workflows:epics <PRD-ADDRESS>`. A keyed run with no folder has nowhere for Phase 4.7's
record to go.

The classification table above still applies to every other `@path` token: a spec folder contributes
to `specs`, a code repo is an `/implement`-only scan target (or, sharing the top level of one already classified here, a search hint, as the table says). Carry `mode` (`keyed | direct`), the
resolved `path`, `kind` and `key`, and `specs` forward. On a keyed run `specs` is
read out of the resolved folder only once the specs-repo preflight below has run.

**Specs-repo preflight** — run here, once address resolution, each token's checks, the no-description
stop on a direct run and the design-doc guard are done (a run that stops on any of them runs none),
and before the Epic-unit resolution below reads anything, with the run key set fixed from carrier frontmatter alone
(`key:`, `kind:`, read as `workflows-core:addressing` §4 does, whatever file that is, and testing no
file's presence; `workflows-core:specs-repo-git` §3.2): on a keyed run the resolved `key` and, where
§4.1 places the resolved folder at Epic level — an `EPIC-` prefix, or with no prefix a resolved
`kind: epic` — also the key its parent's carrier asserts (§4); on a direct run none, a keyless run.
A stale plugin branch the preflight switches away from would otherwise hide a slice's `brd-link.md`
from `IMPLEMENT_BRD_NOT_SLICED`'s listing, or an Epic folder, `specification.md` or
`implementation.md` from the picker below, and the run would list the wrong slices or units. Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git specs-preflight")` and execute its `specs-preflight` entry point (§3) inline: flush any leftover session
artifacts from an earlier run, retry an artifact commit that failed to push,
and settle the branch. This runs against `$SPECS_PATH` only — `git -C
"$SPECS_PATH"`, never a `cd`, so the code/docs repo this run is working
in is untouched (§1 rule 1). Prompt-free, and silent unless it acts, a guard fires, or §3.1 reports a misconfigured `$SPECS_PATH`. If a guard fires, emit its §5 notice;
if it returns `specs_git: blocked` (§3.3 G0) or `specs_git: misrooted` (§3.1), carry that flag for the whole
run — the terminal `commit-artifacts` step skips on it.

**Epic-unit resolution (keyed runs).** `/implement` implements one Epic at a time. When
`mode: keyed`, place the resolved folder as `workflows-core:addressing` §4.1 does — by its prefix,
never by the kind it asserts, which on a BRD-route slice is `brd` — taking its container test first.
**A BRD container** — a `BRD-` folder, or a folder with no prefix holding `coverage-ledger.md` or
`brd/brd-inventory.md` and no `brd-link.md` naming a `parent:` — holds no Epic to implement, because
a BRD's work is authored in its slices; stop, before any artifact is read:
`IMPLEMENT_BRD_NOT_SLICED: <KEY> resolves to a BRD container at <path> — a BRD's Epics belong to its PRD- slices. <the remedy>`
`<the remedy>` lists the slices under it, found by the positive test §4.1 names — `Implement within a slice instead: '/dev-workflows:implement <SLICE-KEY>' — <each slice's key>.` — and, where it finds none:
`It has no slice yet: '/product-workflows:brd-split <KEY> "<how to cut it>"' carves one — the instruction is required there, and that run carves nothing where this BRD's ledger leaves no row unallocated. Where it leaves none, coverage-ledger-format.md §5 names two repairs, the narrow one first: hand-edit the one row to be built back to unallocated in coverage-ledger.md, leaving every other row as it stands; or, to re-take the whole inventory, re-run '/product-workflows:brd-intake <KEY> @<brd-file>', which reopens every row wherever its read finds a requirement and discards every deferred-to, rejected and superseded-by the ledger records.`
It is a user halt. A folder with no prefix — one §5's legacy fallback resolved, or an unprefixed
folder an `@<path>` names, a name beginning with a kind token being prefixed only where it begins
`<KIND>-<the resolved key>-` — is otherwise placed by positive evidence: a resolved `kind: epic`
counts as an `EPIC-` folder below, and a resolved `kind: prd`, or a `brd-link.md` naming a
`parent:`, as a `PRD-` folder. A folder none of these places is not guessed at — stop, naming the
folder and what it carries — and, where it holds an `idea.md` and no `prd.md`, name `/product-workflows:create-prd <KEY>` too, whose `prd.md` places it (`workflows-core:addressing` §4.1). Then:

- **The address named an `EPIC-` folder** → `focus_key` is its `key`; proceed for that Epic. The
  Phase 1.7 scan and specs resolution both scope to it.
- **The address named a `PRD-` folder** → `focus_key` is null; enumerate the `EPIC-` folders
  directly under it — a directory listing, which is what the linked-item hierarchy has become — and
  run the progress-aware picker below. **There is no third case.** A top-level `EPIC-` folder with no
  PRD above it used to have a branch of its own here, nested — unreachably — inside this one;
  `/product-workflows:epics` is the only command that creates an `EPIC-` folder and it writes every one
  of them under a PRD folder, so an Epic address is always the bullet above.
  - **On a multi-component PRD** — `multi-component-test` (`Skill(skill: "workflows-core:reference", args: "components multi-component-test")`, §3) run on the PRD folder returns `multi_component: true` — a flat `specification.md` is a requirements source, not a unit implemented whole save by the 0-Epic override below (`${CLAUDE_PLUGIN_ROOT}/references/workflow-states.md`, *Ready for Implementation*). So every branch below reads as though the PRD folder held no flat `specification.md` — exactly 1 Epic is auto-selected, and ≥2 Epics show the picker without the broad-slice choice — save **0 Epics**, which asks `choices: ["Split into Epics first — /product-workflows:epics <PRD> (Recommended)", "Implement one broad PRD-level slice anyway"]` — the *Split* option only where the PRD folder holds an authored `prd.md`, which `/epics` needs; without one, it becomes what `workflows-core:next-phase-offer`'s `/epics` precondition names in its place — `/product-workflows:create-prd <PRD>`, or, on a BRD-route slice, whatever its ledger tests resolve that to — `/product-workflows:create-prd <SLICE>` where both clear, a `/product-workflows:brd-split` where one fails — still marked `(Recommended)` — and only where that rule names nothing is the array `["Implement one broad PRD-level slice anyway", "Cancel"]`; *anyway* is an override, carried as Phase 1's are to the Phase 5 report's `### Assumptions & limitations` and to `body_facts`. On `multi_component: false`, nothing here applies.
  - **PRD with exactly 1 Epic** → no picker; set `focus_key` to that Epic and proceed, with the
    one-line notice `workflows-core:epic-picker` requires of an auto-selection — **unless the PRD
    folder also holds a flat `specification.md`**, a broad PRD-level slice: the shape
    `/dev-workflows:design` designs as one unit and then offers to this command by the PRD's key.
    Auto-selecting the Epic there would never offer that slice, so ask, the Epic's row carrying its
    marker by the done-predicate in the next bullet:
    `choices: ["<marker> <EPIC-KEY> <title>", "Implement one broad PRD-level slice instead"]`
    The first sets `focus_key` to that Epic; the second leaves it null (specs resolve PRD-level). No
    `(Recommended)` marker: a flat specification beside an Epic means two units were specified, and
    which one this run implements is the operator's to say — the silent choice is the one this
    prompt replaces.
  - **PRD with ≥2 Epics** → render the picker per `Skill(skill: "workflows-core:reference", args: "epic-picker")`,
    honouring that file's *The cap*, which counts this command's own option against the four. **The
    broad-slice choice is offered here on the same condition as the one-Epic path's above — only
    where the PRD folder also holds a flat `specification.md`** — because the two paths ask one
    question, which of the specified units this run implements, and without that file the slice is a
    unit nothing specified: offering it unconditionally let an operator pick one, and the Phase 0
    gate below does not catch that, an absent in-scope spec being `absent` rather than a stop. So:
    every Epic listed as prose, and the array carrying **at most two** Epic rows, that broad-slice
    choice and *"Another Epic from the list above — name its key"* where the flat `specification.md`
    stands; where it does not, the choice is omitted and the freed row goes back to the Epics —
    **at most three** Epic rows plus that same remainder option, which is *The cap*'s own shape for
    a picker appending nothing of its own. **`/implement`'s
    done-predicate is now the artifacts present in each Epic folder**, which is the mechanism
    `/design`'s own Epic picker already uses:
    `specification.md` but no `design.md` → ○; `design.md` present, no record → ◐; a record → ●
    (greyed, not default-selectable; selecting offers "implement anyway") — a record being an
    `implementation.md` holding at least one block, never a file holding only its heading
    (`workflows-core:implementation-format` §1). All three markers are determinable, because
    `/implement` writes that record itself, into the Epic's own folder however the Epic was chosen
    (Phase 4.7). Reading the artifacts rather
    than a status field is
    strictly better than what it replaces: a declared status is a human's claim about the work and
    could lag it, which is why the old picker had to print the raw status text as a hedge. Include the explicit choice
    **"Implement one broad PRD-level slice instead"** (`focus_key` stays null → specs
    resolve PRD-level) **only where the PRD folder holds a flat `specification.md`**, per the
    condition above. Selecting an Epic sets `focus_key` and proceeds for **that Epic
    only** — there is **no "Next Epic?" loop** (code-writing is heavy and branchy;
    each `/implement` run targets one Epic).
  - **PRD with 0 Epics** → offer: split with `/product-workflows:epics` first, or implement one broad
    PRD-level slice (`focus_key` stays null). Nothing follows `/epics` before this command sees its Epics — it
    writes into the tree this command reads. **The flat-spec condition above does not bind here**,
    and that is the asymmetry settled rather than left: with no Epic there is no other specified
    unit to confuse the slice with, so this is not a choice between two units but a choice whether
    to partition at all, and withholding the slice would leave one option where the harness needs
    two (`workflows-core:escalation-rules` §0).

When the picker, or the one-Epic path or its choice, sets `focus_key` that was initially null,
**re-resolve `specs`** now that `focus_key` is set. A keyed run's in-scope `specs` are the
`specification.md` and `design.md` present in the unit's own folder — the focus Epic's `EPIC-`
folder where `focus_key` is set, the resolved PRD folder's flat pair where it is null — and
address resolution took them with `focus_key` null, so take them again from the Epic's folder.
No shared reference defines this set; it is this command's own rule.

**`unit_key` — the key the branch and the commit carry.** It is the key of the unit this run
implements, whose folder Phase 4.7's record goes in: `focus_key` wherever it is set, however it was
set, and the resolved folder's `key` on a broad PRD-level slice; `null` in direct mode. Its
`workitem_key` is that same folder's. Pre-Phase 3 names the branch with it and Phase 4.6 ends the
commit subject with it (`workflows-core:implementation-format` §3), so a run that implements an
Epic under a PRD address commits `[<EPIC-KEY>]` on a branch named for the Epic — the key an
Epic-level scan greps (§4 there). Those two phases are its readers. Phase 4.5's handoff title is
not one: it names the folder it hands off, which is the Epic's where the files it annotated are the
Epic's, and the PRD folder's where they are the PRD's. Where any other step names the run's `key`,
it means the resolved folder's.

Rules:
- The **primary description** is: the spec file if one was given → else the spec folder's design doc, or its `prompt.md` where it holds none → else the inline prose. Echo `📄 Reading prompt from <file>…` (or `from inline text`) and confirm `"Loaded prompt (N lines)."`.
- **Design-doc open-question guard.** It runs once each token is classified — on a direct run, after the no-description stop — and before the specs-repo preflight, on either mode: its input is a token. If the primary description is a **design doc** — a file named
  `design.md` or matching `*-design.md` (the `/design` output; distinct from a `specification.md`) —
  scan it for unresolved `- [ ]` open questions under its `## Open questions` heading. If any exist,
  **refuse to proceed**:
  `choices: ["Cancel — resolve the design's open questions in /dev-workflows:design first (Recommended)", "Override and implement anyway (logged in the Phase 5 report)"]`
  A design must be decision-complete before implementation (enforced upstream by `design-reviewer`;
  this is the cross-command backstop). **`specification.md`-level open questions are exempt** — they are
  the spec's way of flagging what the design phase resolves, and a design doc may legitimately
  incorporate a spec that still carries them. "Override" is the only escape and is recorded in the
  Phase 5 report's `### Assumptions & limitations`.
- Multiple inputs of the same kind are allowed.
- A token naming nothing on disk or an unrecognized directory, and an unreadable `@file`, are each token's own checks, made as it is classified (above), before the specs-repo preflight.
- Note any embedded images as "referenced image: <path>".
- **Specs are required for keyed runs.** When `mode: keyed` and the resolution found
  `specs: []`, do not plan blind — prompt:
  `choices: ["Point me at a specs directory (you'll provide the path)", "Proceed without specs — not recommended", "Cancel"]`
  "Point me…" takes a path, classifies it as a spec-folder, and re-resolves
  `specs`. "Proceed without specs" is logged in the Phase 5 report's
  `### Assumptions & limitations`. Direct-mode runs (no address) are exempt —
  the prompt/spec file is the instruction.

**Gate the in-scope specs on `$SPECS_PATH`'s main.** This runs after the cheap `focus_key`-null folder classification above — a deliberate, bounded exception to `workflows-core:phase-handoff` §5 rule 2's "before its first subagent dispatch", and structurally forced: this gate's `specs` set is derived from `focus_key`, which that dispatch resolves. The exception is bounded to that one read-only Epic-unit classification; every expensive step — the Phase 1.7 fan-out, `risk-planner`, and all writes — still follows the gate. (`/epics` records its own §5 rule 2 deviation the same way.) For each resolved `specs` path whose basename is `specification.md` or `design.md` — `/implement`'s **in-scope** spec/design files, the same set Phase 2B and the invariants section reference for the conformance dimension — execute `require-on-main` (`Skill(skill: "workflows-core:reference", args: "phase-handoff require-on-main")`, §3) against it, mapping its §3.7 return value by `stopped` first, never by `on_main` alone. Any stopping state → stop per §4.4, naming `$SPECS_PATH` explicitly — `/implement` stands in a **code** repo, so an unqualified stop message would point at the wrong repository. Otherwise (`stopped: false`): `pass`/`pass_amending` → proceed (on `pass_amending`, print §3.3's row-B message — reachable only when an **earlier** `/implement` run's Phase 4.5 handoff created the branch and `workflows-core:specs-repo-git` §3.5 B3 kept this run's preflight checkout on it — never this run's own Phase 4.5, which has not executed when this Phase 0 gate runs; `/implement` does not itself author `specification.md`/`design.md`, so a leftover `spec/`/`design/` branch left by an earlier `/specify`/`/design` run is never row B for this gate — it is row C/C′, and the stop/repair path above already covers it). `absent` → **only an in-scope spec is gated at all** — a direct-prompt run resolves none of these `specs` entries and is entirely unaffected, so do not stop; behave exactly as before this feature. `unmanaged` → behave exactly as before this feature. A spec/design supplied directly as a lone `@path` primary description — the Design-doc open-question guard's own input above, a separate mechanism from the `specs` list this gate reads — is **out-of-contract**: read where it sits, deliberately not gated here, the same rule this plan set for `/create-prd <KEY> @<path>`.

---

## Phase 0.5 — Readiness pre-flight (keyed runs only; advisory)

**Keyed runs only.** When `mode: direct` this phase is a **no-op** — skip it entirely
(direct-mode runs are byte-identical to before).

When `mode: keyed`, check the resolved folder for a co-located `_readiness.md`.

Surface a **one-line, non-blocking** recommendation to run `/dev-workflows:ready <ADDRESS>` first
when that `_readiness.md` records **NOT-SUPPORTED** / **PARTIAL**. This NEVER blocks — proceed
regardless; it is guidance only. If it records SUPPORTED, or there is none, say nothing and continue.

**The declared-status half of this check is gone, and that is the honest outcome rather than a
loss.** It read a status a human had set on a tracker and compared it to a readiness bar. With no
tracker there is no declaration to read — and `/ready` itself now derives the phase from the
artifacts (`references/workflow-states.md`), so `_readiness.md` is the same signal with its
reasoning attached. What disappears is the ability to catch a *wrong* declaration, which is the cost
spec §6.4 records against `/ready --claimed`, not a second one.

---

## Phase 1 — Clarification

**Rule: Look, then ask; never guess.** The description is the starting intent, however brief — never ask the user to restate it.

On a keyed run, first run Phase 1.8's ARD resolution — stopping as Phase 1.8 says on an `unmerged` result — so the look below can read the ARD's rules; Phase 1.8 acts on what it found.

**Then, on a keyed run whose unit is an Epic (`focus_key` set), the multi-component check.** Run `multi-component-prereqs` (`Skill(skill: "workflows-core:reference", args: "components multi-component-prereqs")`, §6) at `implement` scope. On `multi_component: false`, only the `target_repo_matches: false` bullet below applies — a targeted Epic belongs to one repository whatever its PRD's set — and nothing else is said. Otherwise — the one place a keyed run asks about an ARD that Phase 1.8 found `none`, the exception `workflows-core:ard-resolution`'s no-regression rule states — print one line naming the Epic's target, then:

- **`target_repo_matches: false`** → ask `choices: ["Stop — run /dev-workflows:implement <EPIC> in <the target's repository> (Recommended)", "Implement here anyway", "Cancel"]`. **Stop** and **Cancel** stop.
- **`target_repo_matches: unknown`** → one line saying the target was not compared, this repository having no `origin`; no question.
- **A prerequisite row that is neither `present` nor `unmanaged` — an Epic with no target, or one outside the ARD's set, among them (`epic_target`) — or a `coverage_gaps` entry naming this Epic** → ask once, naming each: `choices: ["Stop — <the earliest gap's remedy, §6> first (Recommended)", "Implement without them", "Cancel"]`. **Stop** and **Cancel** stop.

On **Implement here anyway** or **Implement without them**, carry what was overridden — the target mismatch, each missing artifact with its state, each coverage gap by `AD#N` — to the Phase 5 report's `### Assumptions & limitations` and to Phase 4.6's `body_facts`, which names it under the pull request's *Merge danger*.

Before producing a plan, list the candidate ambiguities in the description:
- Ambiguous scope or unclear boundaries
- Missing constraints (performance, security, backwards-compatibility)
- Multiple valid implementation approaches
- Undefined integration points or dependencies
- Missing acceptance criteria

**Look before asking.** Try to settle each candidate from what this run can read: the inputs Phase 0 resolved, the code, the repository's own `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` and `README.md`, and `git log` — and, on a keyed run, the ARD's rules resolved above. Look only as far as each candidate needs — this is not the run's codebase exploration (Phase 1.7, 2A or 2B), which still runs as before. Then sort each candidate:
- **Settled by the reading** — missing evidence, not a decision: ask nothing, and carry it into the plan with where it was found.
- **Left open, and its answer changes what the user would notice in the result** — behaviour, scope, an interface, compatibility, a constraint nobody wrote down: a **decision**. Ask it.
- **Left open, and the user would not notice the answer** — settle it yourself and list it in the plan's Assumptions.

What the run settles reaches the plan either way: Phase 2A writes it into its own plan, and on the Phase 2B path the `risk-planner` brief carries it on its `Settled by the run:` line.

Ask every decision. Rules:
- Use `choices` arrays for every question — never plain text questions
- Every `choices` array carries 2–4 options, and never author an "Other" option — the harness supplies the free-text escape itself (`Skill(skill: "workflows-core:reference", args: "escalation-rules")` §0), which is what allows free-text
- When a clearly superior default exists, make it the first choice and label it `"(Recommended)"`
- Group related decisions into a single question (minimize total questions)
- Do **not** proceed until all questions are answered

If no candidate is left a decision, skip directly to Phase 1.5.

---

## Phase 1.5 — Classify task complexity

Invoke the `model-routing` skill (Skill tool, `skill: "workflows-core:model-routing"`) to load the classification rules, then classify the task as exactly one of:

- **SIMPLE** — local, trivial, clearly reversible; no mandatory Opus steps
- **MODERATE** — bounded scope, few files, clear requirements; no mandatory Opus steps
- **SIGNIFICANT** — risky in at least one dimension from the classification reference; Opus planning + Opus review are mandatory
- **HIGH-RISK** — multiple risky dimensions, or security/migration/compliance scope; Opus planning + Opus review are mandatory and must be especially thorough

State the classification and the specific criterion that triggered it. When in doubt between MODERATE and SIGNIFICANT, pick SIGNIFICANT.

**Resolve the per-step routing.** Invoke `Skill(skill: "workflows-core:reference", args: "model-routing/classification")` and, following its §9, record a `model_routing` block resolving each model against the fallback chains:

```yaml
model_routing:
  classification: <SIMPLE | MODERATE | SIGNIFICANT | HIGH-RISK>
  reason: <one-line>
  current_model: <the model this orchestrator is running under>   # = the inline implementation coding
  enforced_model: <run_flags.enforced_model, or omit>   # §10: when set, every dispatched-step *_model below equals it (inline authoring_model / implementation_model keep the session model) and routing: bypassed
  defect_model: <§2.1 Sonnet chain — only under --skip-feedback; under §10, run_flags.enforced_model>
  detection_model: <§2.1 Sonnet chain: claude-sonnet-5-5, fallback claude-sonnet-5/4-6/4-5>   # the folder read, code-scanner, Phase 2A exploration, test-writer, test-baseliner, review-fixer, the Phase 4 maintenance agents
  planning_model: <§2 Opus chain>   # risk-planner (Phase 2B; SIGNIFICANT/HIGH-RISK only; frontmatter-pinned, recorded, no override unless §10 enforces a model)
  review_model:  <§2 Opus chain>    # code-review (Phase 3B; frontmatter-pinned, recorded, no override unless §10 enforces a model)
  implementation_model: <= current_model>   # coding done inline by the orchestrator
  fixes_model: <= detection_model>          # review-fixer (Phase 3B)
  opus_available: <true if a §2 Opus model resolved, else false>
  notes: <any §2 / §2.1 fallback or degradation>
```

Each subagent dispatch below cites its chain (§9 role→chain map); mechanical steps pin `detection_model` via `model:`, and the frontmatter-Opus gates (`risk-planner`, `code-review`) are recorded, and overridden only when §10 enforces a model.

**Detect task shape.** Inspect the description for defect signals (fix / bug / regression / broken / incorrect / wrong output / crash / fails). If bug-shaped, set `task_shape: bug`. `task_shape: bug` only affects the SIGNIFICANT / HIGH-RISK path (Phase 2B/3B); for SIMPLE / MODERATE it is guidance only (no extra question). On the SIGNIFICANT / HIGH-RISK path, if it is genuinely ambiguous whether this is a defect fix or new work, ask with a `choices` prompt (2–4 options; the harness supplies the free-text escape).

Then choose the branch:

- **SIMPLE / MODERATE** → continue to Phase 2A (standard planning)
- **SIGNIFICANT / HIGH-RISK** → continue to Phase 2B (Opus-planned)

---

## Phase 1.6 — Input scale assessment

From the Phase 0 classification, compute:
- `repo_count` = number of distinct code repositories (cwd + referenced git-repo dirs), counted by top level (`git -C <path> rev-parse --show-toplevel`), so an `@path` whose top level is already counted adds none
- `has_ticket_folder` = any specs folder present
- `has_spec_folder` = any spec/design folder present

Set `fan_out = (repo_count > 1) OR has_ticket_folder OR has_spec_folder`.

- **`fan_out = true`** → the input is multi-source. Per `workflows-core:model-routing/classification` §1.1 (the multi-source trigger; see §8 for the fan-out policy) this floors the classification at **SIGNIFICANT** (raise it now if Phase 1.5 chose SIMPLE/MODERATE). Announce: `"Multi-source input detected (<facts>) — flooring at SIGNIFICANT; this is overridable at plan approval."` Then run **Phase 1.7** (fan-out scan) and continue on the SIGNIFICANT/HIGH-RISK branch (Phase 2B).
- **`fan_out = false`** → unchanged behavior; skip Phase 1.7 and proceed to Phase 2A or 2B exactly as the Phase 1.5 classification directs (the single-explorer path).

---

## Phase 1.7 — Multi-source exploration (only when `fan_out = true`)

Runs after Phase 1.6 and replaces the single Phase 2B exploration subagent for multi-source input. Follows `workflows-core:model-routing/classification` §8.

1. **Read each referenced specs folder** (read-only):

   1. **Read the resolved folder.** Read its `prd.md` and the `specs` files resolved in Phase 0, plus —
   for a PRD-level address — the `EPIC-` subfolders under it. This phase reads no PR URLs:
   `implementation.md` (Phase 4.7) is where this run records its own refs, and
   `workflows-core:implementation-format` §4 is how a later run reads them.

   Read each folder in turn. Collect the themes; there are no PR references until `implementation.md` exists.

   When `focus_key` is set, scope the collected result to that `EPIC-` folder and what it holds,
   and drop every sibling `EPIC-` folder before folding themes into the plan. There is no Story /
   Sub-task level to keep: the `EPIC-` folders on disk are the hierarchy. The folder read
   itself is not modified — the scoping is done here.

2. **Read spec/design folders inline.** Read each spec-folder `.md` and fold its content into the themes and primary description.

3. **Fan out `code-scanner` — one per repo, single response, cap 4 concurrent.** Spawn all repo scanners in **one** message (batch in groups of 4 if there are more than 4 repos). For each distinct code repository (an `@path` sharing its top level adds that path to its scanner's `search_hints`, never a second scanner):

   → Agent (subagent_type: "workflows-core:code-scanner", model: `<detection_model — §2.1 Sonnet chain>`):
     > "repo_path: <the repo's top level — `git -C <path> rev-parse --show-toplevel` of the path Phase 0 classified>
     >  capability_themes: <themes from steps 1–2 + the implementation spec>
     >  context: <3–5 sentences: the implementation goal and what the change must accomplish>
     >  search_hints: <symbols/paths/keywords derived from the spec, plus every `@path` sharing this repository's top level and, for the working directory's repository, the working directory where it lies below the top level, each relative to that top level and each once, if any>
     >  refresh:      { switch_to_default_branch: false, pull: false }"

   **`refresh` is pinned off here, and it is the one input this dispatch must not omit.**
   `code-scanner`'s declared default is `{switch_to_default_branch: true, pull: true}`, and Phase 0
   classifies **the cwd itself** as a code repo and therefore a Phase 1.7 scan target (`repo_count`, Phase 1.6). Leaving `refresh` unset therefore ran `git switch <default>` and
   `git pull --ff-only` **in the repository this command is about to branch and modify**, before
   Pre-Phase 3 has created that branch — silently relocating a user who invoked `/implement` from a
   feature branch, and pulling into their working repo with no consent step anywhere in this command.
   It also made Pre-Phase 3 step 4 unreachable on every fan-out run: that step offers *"Branch from
   current position — continue on this work"* only when HEAD is **not** on the default branch, and the
   scan had already moved it there, so the option a user with committed work would pick could never be
   shown. `/implement` scans the repository it is about to branch and modify — the working directory's — which is exactly what no other
   `code-scanner` caller does — every one of the others scans a repository it only reads and writes
   its own output elsewhere, into `$SPECS_PATH` or, for `/docs-workflows:docs-audit`, into a docs
   repo. **Stated as the property rather than as a count of the others**, which is what went stale
   here: the sentence said *the other five* and `/docs-audit` had since made them six. Re-derive the
   set with ``grep -l 'code-scanner' plugins/*/commands/*.md`` and read each hit, since
   `/dev-workflows:ready` names the agent only to forbid dispatching it. `/idea` pins the same two
   values for the same reason.

   Wait for all scanners in the batch to return. A scanner returning `REPO_MISSING` — the path is not a directory — escalates per the `Repo missing (after resolution)` rule in `workflows-core:escalation-rules`; `DIRTY_TREE` **cannot occur here** — `code-scanner` gates it on `refresh.pull`, which this dispatch
   pins false, so no scanner stashes anything in a repo whose pre-existing changes Pre-Phase 3 is about
   to record as `stash_ref`. It escalates per the `Dirty working tree` rule and `REFRESH_BLOCKED` per the `Refresh blocked` rule in the same file. None is ever hidden, and none is merely announced — each offers the user a way forward (§8.4). A scanner returning `prep.read_only: true` is not a failure — it scanned at `prep.scanned_ref`; escalate per the `Read-only mount — ref stale or diverged` rule in `workflows-core:escalation-rules` only when `prep.ref_committed_at` is more than 14 days old or `prep.head_divergence.ahead > 0`, and cite evidence at `prep.scanned_ref`.

   **Round 2 — narrow and seeded (§8.5).** Invoke `Skill(skill: "workflows-core:reference", args: "model-routing/classification")` and apply its §8.5. A theme is **inconclusive** when its round-1 `classification` is `partial`, `absent`, or `error`, or when **two or more** scanners' per-theme `capability_map[].gap_summary` texts point at each other's repo in a cycle, or at a component/subsystem that no scanned repo covers — the shape that yields confident answers which together say nothing. For every inconclusive theme that round 1 left at least one evidence anchor for, dispatch `code-scanner` again on `detection_model` with `capability_themes` holding exactly **one** question — the single thing round 1 failed to settle, not the broad theme — and `search_hints.paths`/`.symbols`/`.keywords` seeded from that round's verified `evidence[].path` and `.symbols`; where an evidence entry carries `lines`, name the anchor as `<path>:<line>` in the `context` prose. Cap **4 dispatches, one round only** — there is no round 3. This matters more here than where §8.5 was first adopted: `/idea`'s summary feeds a grill with a human in it, while this one feeds a planner whose output becomes code. **A theme round 1 left with no evidence anchor never enters round 2** — it stays inconclusive with no round-2 attempt possible, and that absence of an attempt is not itself a resolution.

4. **Synthesize.** Combine the folder read output, all `code-scanner` reports, and the spec into a single **multi-source codebase summary** (per-repo: relevant files, existing capabilities, gaps; plus the cross-repo picture and the PRD themes). This summary is the codebase context for Phase 2B — do **not** also run the single Explore subagent. Write this summary to a temp file (`command mktemp -t dw-impl-summary-XXXXXX` — **never inside a repo working tree**, so a captured `git diff` never picks it up) and record its absolute path as `summary_file`; Phase 2B receives this path, not the pasted summary.

   **Name what the scan did not settle.** The summary carries a `## Unresolved` section listing **every theme still inconclusive at the end of Phase 1.7** — this explicitly includes a theme that never entered round 2 because round 1 left no anchor to seed from, a theme classified `error`, and a mutual-deferral theme, whether or not either scanner logged an anchor. None of these becomes resolved merely by having had no round-2 attempt. Per `workflows-core:model-routing/classification` §8.5 Bounds, name **why** each theme is unresolved — mutual deferral / scan error / partial-or-absent with no anchor — and give the repos-and-conclusions detail only where scanners actually disagreed. An inconclusive theme is **never** folded in as an ordinary gap: a gap asserts the capability is absent with no deferral outside the scanned set, an unresolved theme asserts only that the scan could not tell, and once flattened the two are indistinguishable to the planner. Omit the section entirely when nothing is unresolved.

---

## Phase 1.8 — Resolve applicable ARD (keyed mode; optional)

Only when the run resolved a key (PRD/Epic) — i.e. NOT direct-prompt mode — the ARD is resolved (at the start of Phase 1, or here where Phase 1 did not) by invoking `Skill(skill: "workflows-core:reference", args: "ard-resolution")` and running its resolution with `prd` = the PRD folder's key — the resolved folder's own for a `PRD-` address, its parent's for an `EPIC-` one (Epic-unit resolution above) — `epic` = `focus_key`, and `$SPECS_PATH`. Direct mode (no key) → treat as `status: none`. On `status: none`, **skip and proceed exactly as before**. On `status: unmerged`, **stop**, naming the returned `branch` and any `pr` and naming `$SPECS_PATH` explicitly (`/implement` stands in a code repo, not the specs repo, so an unqualified message would point at the wrong one) — per `workflows-core:ard-resolution`'s Output section, this state is unreachable when no ARD resolves. On `status: found`, carry the `invariants` as **implementation guardrails** (the implementer honors each `AD#N` `rule`; a necessary deviation is logged as an `- ARD deviation:` line in the Phase 5 report), and — in the SIGNIFICANT / HIGH-RISK path — pass them to `code-review` (Phase 3B) as `applicable_ard`. In the SIMPLE / MODERATE path there is no `code-review` gate, so the guardrails act as guidance only.

---

## Phase 2A — Standard Plan (SIMPLE / MODERATE only)

**Codebase exploration** — Before writing the plan, spawn an exploration subagent to map the relevant parts of the codebase — save where this phase was entered from a `### Re-classification` the user accepted at Phase 2B, where `summary_file` already holds the exploration and nothing is dispatched:

→ Agent (subagent_type: "general-purpose", tools: Read/Glob/Grep only — no Bash, no Edit, model: `<detection_model — §2.1 Sonnet chain>`):
  "Given this implementation description: [paste the full implementation description from Phase 0 or Phase 1 here], find in the repository at [its top level, `git rev-parse --show-toplevel`] (starting from [every `@path` the input named that shares its top level, and the working directory where it lies below the top level, each relative to that top level and each once — omit where neither]) and return:
   - Relevant source files and their primary responsibility
   - Existing patterns and conventions used in this codebase
   - Test file locations and test naming conventions
   - Naming conventions (class names, method names, file names)
   Return a structured summary — no code changes, no file edits."

**Where this phase was entered from a `### Re-classification` the user accepted at Phase 2B, skip this block — `summary_file` is the context. Otherwise, wait for the agent's response before proceeding. If the agent returns no relevant files or fails, proceed with the plan using your own file reads to gather context. Do not begin writing the plan until the file map is returned or you have gathered context yourself.**

**Write the exploration down** — save where this phase was entered from a `### Re-classification` the user accepted at Phase 2B, where `summary_file` already holds it: write the returned file map — or, where you gathered context yourself, what those reads found — to a temp file (`command mktemp -t dw-impl-summary-XXXXXX`, never inside a repo tree) and record its absolute path as `summary_file`.

→ Use the returned file map — or, where this phase was entered from an accepted `### Re-classification`, `summary_file` — as codebase context when writing the plan below.

Produce a written implementation plan:

1. **Classification** — `SIMPLE` or `MODERATE` (with reason)
2. **Goal** — one-sentence summary of what will be built
3. **Approach** — chosen strategy and why, citing each fact Phase 1's reading settled, with where it was found
4. **Steps** — numbered, concrete implementation steps
5. **Files to create/modify** — list with brief rationale
6. **Tests** — what tests will be added or run
7. **Assumptions** — each open question the run settled itself because the user would not notice the answer (Phase 1's test) — in Phase 1 or while writing this plan — with what was chosen (must be minimal)
8. **Out of scope** — explicitly list what is NOT being done, a change another code repository needs included (this run changes code only in the repository it branches)
9. **Review focus** — up to five input classes or failure modes the task implies and no step's tests exercise, most likely to bite a user first, each with the behaviour a reasonable user would expect — or `none — checked`. `test-writer` writes a test for each line, or names in its `### Notes` why one cannot be written (Phase 3.5, or Phase 3B step 4a on a run whose re-plan the user approved)

**Re-test the class against the plan** — before asking, and again after every **Revise**, save where this phase was entered from a `### Re-classification` the user accepted at Phase 2B: that acceptance is the plan-approval override, which a re-test would undo, so there it runs only after a **Revise**, and only on a trigger the revision added — one the plan before it did not state. Test the class as it stands — the `model_routing` block's — again against `workflows-core:model-routing/classification` §1.1, reading the plan's Steps and Files to create/modify and what the exploration found those files do. Where a §1.1 trigger now applies — more than 3–5 non-test files, authentication or authorization, a schema or migration, a public contract, concurrency, or any other item on that list — do not ask: raise the class to SIGNIFICANT (HIGH-RISK under §1.1's multiplier), announce `Re-classified upward at planning: <trigger> (<the path, or the paths, that show it>)`, record the new class and that reason in the `model_routing` block — resolving its `planning_model` and `review_model` where the block left them out — and continue at Phase 2B with `summary_file` as its codebase summary and every answer given at this phase's **Revise** on the brief's `Constraints:` line, with no second exploration; ask Phase 1.5's task-shape question first where it is genuinely ambiguous whether this is a defect fix or new work.

**A plan with no step in this repository.** Where a plan written before any edit — this one as first written or after any **Revise**, or Phase 2B's full plan at its approval gate, never Phase 3A step 5's re-plan — changes no file in this repository (every change lying under Out of scope for another code repository, or none at all), there is nothing to implement here, and approving it would cut an empty branch. Present the plan and ask this in place of the approval question:

```
"This plan changes no file in this repository. What would you like to do?"
choices: ["Stop here, nothing written (Recommended)", "Revise plan"]
```

- **Stop** → name one follow-up per other code repository the plan puts a change in, if any — a `/dev-workflows:implement` run from there, addressed as Phase 3A/3B step 2 says, listing its changes — and stop as **Cancel** does, nothing having been written.
- **Revise** → as the approval question's **Revise** does, in Phase 2A or Phase 2B, whichever wrote the plan.

Otherwise, ask:
```
"Implementation plan ready. What would you like to do?"
choices: ["Approve & implement now (Recommended)", "Revise plan", "Cancel"]
```

- **Approve** → write the approved plan to a temp file (`command mktemp -t dw-impl-plan-XXXXXX`, never inside a repo tree) and record its absolute path as `plan_file`; proceed to Phase 3A
- **Revise** → ask what to change, update, re-test the class against the plan as above — continuing at Phase 2B where it raises the class — otherwise re-show and re-ask, through *A plan with no step in this repository* where the revision leaves no step here
- **Cancel** → stop and summarize what was planned

---

## Phase 2B — Opus-planned (SIGNIFICANT / HIGH-RISK)

**Phase 3A step 5's re-plan also runs this phase**, from the `risk-planner` dispatch on, and that step says where each arm below leads on it.

**Codebase exploration** — If Phase 1.7 ran (`fan_out = true`), use its **multi-source codebase summary** (already written to `summary_file` in Phase 1.7 step 4) as the codebase context and skip the single Explore subagent. If Phase 2A's re-test raised the class, `summary_file` already holds this run's exploration: use it the same way, and skip the subagent likewise. Otherwise, run the same exploration subagent call as Phase 2A (same prompt, same fallback rule), then write the Explore agent's returned output to a temp file (`command mktemp -t dw-impl-summary-XXXXXX`, never inside a repo tree) recorded as `summary_file`. In every case, `summary_file` holds an absolute path before the planner is dispatched.

Once the file map is returned, delegate planning to Opus.

When a `specification.md`/`design.md` is in scope, extract its **in-scope** `[Uxx]`/`[ACxx]`/`[TCxx]` IDs (reuse the specs resolved in Phase 0) into `in_scope_ids` for the review dispatch below. When `task_shape: bug`, the plan will lead with a repro step and a ranked-hypotheses section — surface them in the normal plan-approval gate (no extra interrupt) **when the ranking is present**. When the planner instead returns `Ranking withheld — no red-capable repro`, the withheld-repro branch below fires first and the normal gate does not run.

→ Agent (subagent_type: "dev-workflows:risk-planner", model: `<planning_model — §2 Opus chain, equal to risk-planner's frontmatter pin; under §10, run_flags.enforced_model>`):  # recorded in model_routing as planning_model above, frontmatter-pinned, no override added unless §10 enforces a model
  > "Produce the risk-weighted plan for the following brief:
  >
  > Task description: [substitute full description]
  > Classification: [SIGNIFICANT | HIGH-RISK] — reason: [the criterion from Phase 1.5, the multi-source floor from Phase 1.6 when fan_out, or the raise — Phase 2A's re-test or Phase 3A step 5 — with its trigger and path]
  > Codebase summary: read it from the file at [the `summary_file` absolute path]
  > Constraints: [any from clarification, every answer given at Phase 2A's **Revise** before a raise, plus runtime/version/deadline known — and always: this run changes code only in [the working directory's repository top level, `git rev-parse --show-toplevel`]; a change any other code repository needs goes under Out of scope; run every command from that top level]
  > Settled by the run: [each fact Phase 1's reading settled, with where it was found, which the plan cites in its Approach; and each open question the run settled itself — in Phase 1, or at Phase 3A step 5 before a re-plan — with what was chosen, which the plan lists under `### Assumptions`; or "none"]
  > Current state: branch = [git branch], uncommitted = [`git -C <top level> status --short --untracked-files=normal` summary]
  > Work so far: [on Phase 3A step 5's re-plan only — read the diff at the `partial_diff_file` path: this run's uncommitted edits, part of this change, save what the paths Pre-Phase 3 recorded as `pre_existing_dirty` already held, which is somebody else's work — name those paths here, or "none"; and read the plan the user approved before it at the `plan_file` path; omit the line otherwise]
  > Specs in scope: [the resolved specification.md/design.md path(s) from Phase 0, or "none"]
  > Unresolved scan themes: [the summary's `## Unresolved` entries, or "none"] — each is a theme the scan could not settle, NOT a confirmed gap; carry every one into the plan's risks and never plan as though its location is known
  > task_shape: [bug | omit]"

**Wait for the risk-planner to return.** Its output is one of:

1. A full plan in the risk-weighted format (the normal case).
2. A short `### Re-classification` section, if the planner decided on inspection that the task is actually `SIMPLE` or `MODERATE`.

**If the return contains `### Re-classification`:** surface it to the user, ask for confirmation of the revised level with a `choices` prompt (`["Accept revised classification (Recommended)", "Override and stay SIGNIFICANT/HIGH-RISK", "Cancel"]`). If the user accepts, **fall back to Phase 2A** (standard plan) using the codebase context already captured above (the `summary_file` path) — whichever of Phase 1.7's **multi-source codebase summary**, Phase 2B's Explore output or Phase 2A's exploration this run wrote — and do not re-run exploration; every answer given at a **Revise** so far (Phase 2A's before a raise, or this gate's own) binds the plan the run continues on — the new Phase 2A plan honours it, and on Phase 3A step 5's re-plan, where the run resumes on its approved plan, Phase 3A follows it as a constraint. Accepting here is the user exercising the **plan-approval override** — of the multi-source SIGNIFICANT floor (Phase 1.6), or of a raise; that is the sanctioned way to leave either, and Phase 2A's re-test then runs only on what a later **Revise** adds. Record the revised class and its reason in the `model_routing` block. If the user overrides, re-invoke risk-planner with an additional constraint stating the classification is intentional, and handle its return as above, every arm included — a `### Re-classification` it returns despite the constraint is the user's to settle again. If the user cancels, stop and summarize.

**If the return is a full plan whose `### Hypotheses (ranked)` section contains `Ranking withheld`:**
the planner could not get a red-capable repro, so its hypotheses are absent by design and the rest of
the plan rests on unverified theory. Do NOT fall through to the normal approval gate — its Recommended
option is "Approve & implement now", which is exactly the proceed-on-a-guess outcome
`${CLAUDE_PLUGIN_ROOT}/references/bug-diagnosis.md` step 1 forbids. Surface the planner's `Tried:` line
verbatim and ask:

```
choices: ["Help construct a repro (you'll be prompted for what to try)", "Proceed without a repro (recorded in the Phase 5 report)", "Cancel"]
```

- **Help construct a repro** → take the user's suggestion, re-dispatch `risk-planner` with it carried in the brief, and handle the new return as above, every arm included.
- **Proceed without a repro** → record it in the Phase 5 report's `### Assumptions & limitations` as `No repro: <what the planner tried>` and continue to the normal full-plan gate below.
- **Cancel** → stop.

**If the return is a full plan** (ranking present, or the user chose to proceed without a repro)**:** present it to the user verbatim and ask — or, where it has no step in this repository (never on Phase 3A step 5's re-plan), ask Phase 2A's *A plan with no step in this repository* question in its place:

```
"Opus-planned. What would you like to do?"
choices: ["Approve & implement now (Recommended)", "Revise plan", "Cancel"]
```

- **Approve** → write the approved plan to a temp file (`command mktemp -t dw-impl-plan-XXXXXX`, never inside a repo tree) and record its absolute path as `plan_file`; proceed to Phase 3B
- **Revise** → ask what to change, then re-invoke risk-planner with the **complete** brief plus the additional constraint merged in (never send just a delta — the planner refuses to plan without a full brief). Handle its return as above, every arm included.
- **Cancel** → stop and summarize

---

## Pre-Phase 3 — Create feature branch

Every stop from here to the end of the run names, beside whatever else it reports, each change another code repository needs that the run has found (the plan's Out of scope or Phase 3A/3B step 2), one line per repository, and, once step 7.5 has run, every gap it reported without a note (a spec step 7.5 may not annotate) and every note it wrote into `$SPECS_PATH`, uncommitted there until handed off or removed.

Before writing any file:

1. **Clean-tree check** — Run `git status --porcelain -z --untracked-files=all`, which lists untracked files whatever the user's `status.showUntrackedFiles`. If the output is non-empty:
   - Show the user what is dirty (paste the `git status --short --untracked-files=normal` output, which shows untracked files whatever the user's `status.showUntrackedFiles` and an untracked directory as one line), and say, before asking, that a file of theirs the run then changes is committed whole, their earlier changes in it included (`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.2).
   - Ask:
     ```
     choices: ["Stash tracked changes and continue (Recommended)", "Proceed anyway — pre-existing changes will appear in the diff and review outputs", "Cancel"]
     ```
   - **Stash**: read `refs/stash` first (`git rev-parse -q --verify refs/stash`, empty where there is none), then run `git stash push -m "pre-impl stash" -- ':/' ':(top,exclude,literal)<path>' …`, which stashes tracked changes only, with one exclusion per **spec input** inside this repository, so the specs this run reads stay as the user has them: each file Phase 0 read as a Spec file, each `.md` file it read from a Spec folder — never the folder, which can hold code beside its specs — a Specs folder, and the folder a keyed run's address resolved to. Write each path relative to the top level, with no leading `./`, which matches nothing. A path is inside this repository where `git -C <its directory> rev-parse --show-toplevel` prints this repository's top level; one inside a submodule is not, and excluding it makes git fail after saving the stash. **Never exclude a path of the Code repo row** — a search hint, or this repository's own top level: the user's work there is what the stash is for, and the top level, spelled as an empty path, excludes everything, so git stashes nothing, exits 0, and the answer silently becomes **Proceed anyway** (measured, git 2.43). `literal`, because a path is a name and not a pattern: without it, excluding `sp*c.md` also excludes `spec.md`. Then name the tracked paths the exclusions kept out of the stash — those `git status --porcelain -z --untracked-files=no` still lists at or below an excluded path — and record every path the stash leaves dirty (`git status --porcelain -z --untracked-files=all` after it) as `pre_existing_dirty`, each with its fingerprint, so `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.2's carve-out keeps them out of the commit unless one's content changes during the run (they still appear in the diffs the agents read, as on **Proceed anyway**), then continue. Where git refuses the stash, show its error and stop as **Cancel** does, nothing branched yet — but read `refs/stash` again: a value that differs from the one read before the push is a stash this push still made, so record it as `stash_ref` and name it in the stop. Record the resulting stash as `stash_ref`, where git made one (`No local changes to save` makes none) — Phase 4.6 names it in its outcome line and never drops it (`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.2 carve-out 2). **Any stop from here on that does not reach Phase 4.6 names it in the stop message instead**, because no exit of this run may end without saying where the user's stashed work went — this phase's own step-4 Cancel and switch refusal, Pre-Phase 3.5's Cancel (the one post-branch exit Phase 4.6 excludes), and every stop between.
   - **Proceed**: note in the Phase 5 report that the working tree was dirty at implementation start, **and record the `git status --porcelain -z --untracked-files=all` paths as `pre_existing_dirty`**, each with its fingerprint (`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.2), taken here, before the first edit. Phase 4.6 needs them to avoid sweeping somebody else's uncommitted work into this run's commit (`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.2 carve-out 1); a run that does not record them here cannot honour that carve-out later. **`-z` is what makes that subtraction work** — §2.2 enumerates in the same form, and without it a path carrying a space or a non-ASCII byte is recorded quoted here and read raw there, so it subtracts against nothing.
   - **Cancel**: stop and summarize what was planned.

   A clean tree records `pre_existing_dirty: null` and `stash_ref: null` — the state Phase 4.6's precondition assumes.

2. **Resolve the branch name** by invoking `Skill(skill: "workflows-core:reference", args: "branch-naming")` and following it — **the repo's own documented convention wins**. Read the target repo's `CONTRIBUTING.md`, `CONTRIBUTION.md`, `README.md`, `DOCUMENTATION-GUIDELINES.md`, `CLAUDE.md` (+ `.claude/`) for a branch-naming section (§1.1); if one is found, classify its segments (§1.2) and fill them: an **identity** placeholder (`<your-name-or-initials>`, `<user>`, …) from the §2 ladder (`$GIT_USER_INITIALS` → `git config user.initials` → inference from existing branches → the §2.5 prompt), an **issue-key** segment from `unit_key` (Phase 0 — the Epic's wherever `focus_key` is set; or the pattern's documented no-issue literal in direct mode), and the **description** segment from step 3's slug. A pattern with no identity segment gets none — never inject initials into a convention that does not ask for one. Only when the repo documents no convention (§1.4) build `<prefix>/<slug>` with `<prefix>` from the §2 ladder, whose fallback here is `feat/`.

3. **Generate slug** — derive from the implementation description: lowercase, hyphens, max 40 chars, strip punctuation and special chars. Example: "Add user authentication to login page" → `add-user-authentication-login-page`. When `unit_key` is set and the chosen shape has no separate issue-key segment, prefix it: `<unit_key>-<slug>`.

4. **Check HEAD context** — resolve `<base>`, the default branch's name, by `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.8, with `<repo>` the repository this phase branches. It is the ladder Phase 4.6 resolves the pull request's base with, so the base it offers to branch from is the base its pull request targets. Never judge by a list of names: in a repository whose default is `main`, a local `develop` is a branch like any other, and the commits it carries are what this step asks about.
   - **§2.8's ladder is exhausted** — no `origin`, or an `origin/HEAD` that is unset or names a ref that does not exist, and none of the branches it probes → there is no base to measure against or to branch from, so ask nothing: print `Base branch unresolved (<reason>) — branching from the current position.`, carry that line into the Phase 5 report's `### Branch` section, and go to step 5.
   - **HEAD is on `<base>`** — `git branch --show-current` prints `<base>` → nothing to check; go to step 5.
   - **HEAD is not on `<base>`** — it prints another name, or nothing on a detached HEAD → list the commits HEAD carries that the base does not: `git log origin/<base>..HEAD --oneline`. §2.8 yields a `<base>` only where `origin/<base>` exists, so this read has a ref to name. Non-empty output → ask the question below. Empty output with exit 0 → HEAD carries nothing the base lacks; go to step 5. **A non-zero exit is a failed read, never "no ahead commits"** — keep its error rather than redirecting it away, show it, and ask the question below anyway, saying beside it that the ahead commits could not be read.

   The question names `<base>` beside it and lists the commits the read returned, or its error:
   ```
   choices: ["Branch from current position — continue on this work (Recommended)", "Branch from default branch — fresh start", "Cancel"]
   ```
   - **Branch from current position** → step 5 cuts the branch from HEAD.
   - **Branch from default branch** → `git switch <base>` and nothing more — no fetch and no pull, as at `/vuln` Step 3's switch onto the same base. It takes the name, which `git switch` accepts where it refuses an `origin/<name>` ref, and it creates a local `<base>` from `origin/<base>` where none exists. Step 5 then cuts from `<base>`. Where git refuses the switch — an uncommitted change it would overwrite — report its error and the paths it named, and stop as Cancel does: no branch exists yet, and step 5 must not cut one from the HEAD the user just declined.
   - **Cancel** → stop and summarize what was planned.

5. **Create and checkout** — `git checkout -b <prefix>/<unit_key>-<slug>` on a keyed run, `<prefix>/<slug>` in direct mode. If that name already exists, append the first 7 chars of HEAD's SHA: `<prefix>/<slug>-<short-sha>`.

---

## Pre-Phase 3.5 — Capture test baseline

Placed **after** branch creation (Pre-Phase 3), **before** any file edits. The `.5` numbering signals "inserted between step 3 and step 4 of the existing ordering" — it is its own phase, not a sub-step of Pre-Phase 3's branch-creation steps.

Invoke the `test-baseliner` agent in capture mode:

→ Agent (subagent_type: "dev-workflows:test-baseliner", model: `<detection_model — §2.1 Sonnet chain>`):
  > "Run the agent in the following mode:
  >
  > Mode: capture
  > Project root: [the repository's top level, `git rev-parse --show-toplevel` — every diff this run captures is relative to it]"

Store the returned `## Test Baseline` block verbatim — it will be passed to `test-baseliner` again in verify mode at Phase 3.5 and to `test-writer` as the baseline snapshot. On a repository with more than one test suite the agent baselines **all** of them and the block's `### Suites` section names each; store it whole, unsummarized, since the verify call pairs against those rows.

**Act on the block's `Status` here, before a single file is edited.** This is the last point in the run where the answer can still be honest: a capture is a baseline because nothing has changed yet, and a capture taken after the edits is just a test run.

- `OK` / `NO_TESTS` → continue.
- `PARTIAL` → continue, and record every suite `### Suites` does not mark `OK` or `NO_TESTS`, with the command that failed, in the Phase 5 `### Deferred items` section — this run's verification will not cover them and the Final Report says so. A suite whose runner is not installed is not a reason to stop work on the suites that do run. **Surface the block's `### Notes` lines here as well, and carry what they say about a deferred suite into that suite's entry.** A watch carve-out the capture declined lands the run in this arm wherever its own suite produced no counts and some other suite did — the `RUN_FAILED` arm below is where it lands when none did — and a suite left unmarked because its watcher ran to the per-suite bound is not a suite whose runner failed, though the `Status` and the `### Suites` rows alone cannot tell the two apart (`dev-workflows:test-baseliner` capture step 1). Naming the reason is what keeps the Final Report from reporting a runner failure this run never saw.
- `COMMAND_NOT_FOUND` (`Framework: not detected`) or `RUN_FAILED` → nothing was captured at all. **Surface the block's `### Notes` lines and its `### Suites` rows before asking** — the Phase 3.5 arm handling these same two values already does that for `### Suites`, and `### Notes` is where capture reports a watch carve-out it could not fire: which script it was, and what in it could not be resolved or rebuilt (`dev-workflows:test-baseliner` capture step 1). From the `Status` and the rows alone that state is indistinguishable from a suite that genuinely failed, and it is the state in which *Specify test command to use* has an answer to give — the runner's own single-run command, which the note has just named the script for. The section reads `none` where there is nothing to say, so on every other cause this costs one line. Then ask the user:
  ```
  choices: ["Specify test command to use", "Skip tests for this run (documented in the Phase 5 report's Deferred items)", "Cancel"]
  ```
  - **Specify test command** → when asking, tell the user that a command matching a suite the capture detected runs in that suite's own directory and any other from the repository's top level (name it), so one meant for a subdirectory with no detected suite begins `cd <dir> &&` (`dev-workflows:test-baseliner` capture step 1, *Scope*); take free-text and record it verbatim as `test_command_hint`, and re-dispatch the capture above **immediately**, adding the line `command_hint: [the answer]` to the prompt. Act on the returned block's `Status` by this same list. Ask at most twice in a run; after that record `test_decision: skip` with the last failure as its reason, **marked as the run's own record rather than the operator's answer**. The two provenances are not the same decision and Phase 4.6 reads which one this is: here the operator asked twice for a working command and never agreed to skip, so the run finishes `clean_finish: false` (`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.9), where the *"Skip tests"* answer below finishes `true`.
  - **Skip tests** → take free-text rationale; record `test_decision: skip` with that rationale in the Phase 5 `### Deferred items` section.
  - **Cancel** → stop and summarize.

**Every `### Notes` line the block opens with `CAVEAT: ` is surfaced here, and recorded in the Phase 5 `### Deferred items` section where the run reaches one, whatever the `Status` was** — `OK` and `NO_TESTS` included, which is the one arm above that carries no obligation of its own and is an arm three of the five marked kinds can arrive on (`dev-workflows:test-baseliner` capture step 5). A marked line says the baseline is not what its own numbers claim: a qualifying suite nothing ran because the candidate containing it does not recurse over it, counts a `Make` indirection may have summed twice, or an identifier list a `Make` fold leaves unattributed to what printed it — none of which the `Status` or the `### Suites` rows state. **The mark is the agent's and is not re-judged here**, and it is also the whole of the test: an unmarked note records where a command ran, and surfacing those on every run is how an operator learns to skip the section. The `PARTIAL` and `RUN_FAILED` / `COMMAND_NOT_FOUND` arms above still surface the **whole** section, marked lines included — more than this rule asks, and not narrowed by it.

**Where `test_command_hint` was recorded, every later `test-baseliner` dispatch in this run carries it** — verify compares like with like only when both calls run the same set of suites.

---

## Phase 3A — Implementation (SIMPLE / MODERATE)

**Implement immediately. Do NOT ask "Should I implement?" or any variation.**

1. Work through each step in order
2. Make precise, surgical changes — do not modify unrelated code — and change code only in the repository Pre-Phase 3 branched: any other code repository, one this run was given included, is read-only context, and a change one needs goes into the Phase 5 report's `### Session learnings`, on that repository's one follow-up line for `/dev-workflows:implement` run from there, addressed to the unit this run implemented (the Epic itself, where it was one; no key on a direct run), which Phase 6 collects; an early stop names it beside its §3.1 line instead (Phase 4.6)
3. Follow existing code style and LF line endings
4. Assume broad permissions; avoid unnecessary stops
5. If something **new** emerges mid-implementation, look before stopping, and sort it:
   - **A §1.1 trigger the approved plan did not state** — a fact its Steps and Files did not name: a schema change or migration, an authentication or authorization path, a public contract, concurrency, the non-test files this run changed (those of `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.2's run set) passing §1.1's 3–5, or any other item on `workflows-core:model-routing/classification` §1.1's list that names something the work touches — never §1.1's last item, *Unclear requirements, large unknowns, or otherwise high blast radius*, whose unknowns are a decision, below, and whose blast radius counts only through the concrete items above; nor *Multi-source input*, which is Phase 1.6's — → **re-plan upward**, once per run:
     1. Stop editing. Raise the class to SIGNIFICANT (HIGH-RISK under §1.1's multiplier), announce `Re-classified upward during implementation: <trigger> (<the path, or the paths, that show it>)`, and record the new class and that reason in the `model_routing` block, resolving its `planning_model` and `review_model` where the block left them out.
     2. Write the diff so far — `( i=$(command mktemp -t dw-index-XXXXXX) && trap 'command rm -f -- "$i"' EXIT && { command cp -- "$(git rev-parse --git-path index)" "$i" 2>/dev/null || command rm -f -- "$i"; } && export GIT_INDEX_FILE="$i" && git add -N --ignore-removal :/ && git -c diff.relative=false diff --no-ext-diff --no-color "$(git rev-parse -q --verify HEAD || git hash-object -t tree /dev/null)" )` — to a temp file (`command mktemp -t dw-impl-partial-XXXXXX`, never inside a repo tree) and record its absolute path as `partial_diff_file`.
     3. Ask Phase 1.5's task-shape question where it is genuinely ambiguous whether this is a defect fix or new work. Then run Phase 2B from its `risk-planner` dispatch on, with the complete brief: `summary_file` as its codebase summary, this raise as its classification reason, its `Constraints:` line also carrying every answer given at this step's decision arm, its `Settled by the run:` line also carrying every open question this step's last arm settled, with what was chosen and where in the code it arose, and its `Work so far:` line naming `partial_diff_file`, the `pre_existing_dirty` paths and the `plan_file` the user approved before it. Its arms lead where they always do, save these: **Approve** writes into `plan_file` both plans, opening with the line *The re-plan governs only where the two contradict, and its Steps are the work remaining (the earlier plan's Steps record what the diff so far was made under); every other item in either plan still stands, both plans' Review focus lines included* — the one approved before it, under `## Plan before the re-plan — the diff so far was made under it`, and the new one, under `## Re-plan — the rest` — and continues at Phase 3B step 1, working through the re-plan's Steps; Pre-Phase 3 and Pre-Phase 3.5 are not run again, and the baseline still predates every edit. **Accept revised classification** records the revised class as Phase 2B's acceptance does and resumes Phase 3A where it stopped, on the plan already approved — the trigger the re-plan was raised on, and its §1.1 item, count from then on as ones the approved plan states, so neither trigger arm of this step fires on them again. Each **Cancel** — the re-classification prompt's, the repro prompt's and the plan-approval prompt's — stops through Phase 4.6, since files are written (its `"Every run"` list). Every re-dispatch on this path — **Override**, **Revise**, **Help construct a repro** — carries the complete brief, its `Work so far:` line included.
   - **A §1.1 trigger the approved plan did not state, met after this run's one re-plan** → announce `Classification trigger after the re-plan: <trigger> (<the path, or the paths, that show it>)`, then ask `choices: ["Continue at the current class — this change ships without the Opus review", "Stop here — the work so far is committed through Phase 4.6 (unless --no-commit)"]`. **Continue** records the trigger in the Phase 5 report's `### Assumptions & limitations` and counts it, and its §1.1 item, as ones the approved plan states, as the re-plan's **Accept revised classification** does, so this arm does not fire on them again; **Stop** is in Phase 4.6's `"Every run"` list.
   - **A decision** — Phase 1's test: nothing this run can read settles it, and its answer changes what the user would notice in the result → STOP, ask with choices (2–4 options; the harness supplies the free-text escape), resume after answer.
   - **Anything else** → look it up and continue; an open question the user would not notice is settled by the run and recorded in the Phase 5 report's `### Assumptions & limitations`.
6. **Run Phase 3.5 below** (test writing + regression verification) — do NOT run tests directly here; Phase 3.5 owns the lint/build/test sequence and the fix loop
7. Verify the outcome matches the approved plan
8. Proceed to Phase 4 (post-implementation maintenance).

---

## Phase 3.5 — Write and verify tests (SIMPLE / MODERATE)

Runs after Phase 3A step 5 completes (all code changes written), before the outcome-verification step.

1. **Invoke `test-writer` agent.** First, at the orchestrator, capture the diff for the dispatch: write `( i=$(command mktemp -t dw-index-XXXXXX) && trap 'command rm -f -- "$i"' EXIT && { command cp -- "$(git rev-parse --git-path index)" "$i" 2>/dev/null || command rm -f -- "$i"; } && export GIT_INDEX_FILE="$i" && git add -N --ignore-removal :/ && git -c diff.relative=false diff --no-ext-diff --no-color "$(git rev-parse -q --verify HEAD || git hash-object -t tree /dev/null)" )` (so new files are included) to a temp file (`command mktemp -t dw-impl-diff-XXXXXX`, never inside a repo tree) and record its absolute path as `test_diff_file`. `test-writer` has no shell tool — it can only `Read` the path it is given. Then spawn:

   → Agent (subagent_type: "dev-workflows:test-writer", model: `<detection_model — §2.1 Sonnet chain>`):
     > "Write tests for this brief:
     >
     > Task description: [substitute full description]
     > Plan: read it from the file at [the `plan_file` path recorded at Phase 2A approval]
     > Diff: read it from the file at [the `test_diff_file` path]
     > Project root: [the repository's top level, `git rev-parse --show-toplevel` — every diff this run captures is relative to it]
     > Baseline: [paste the ## Test Baseline block captured in Pre-Phase 3.5]"

2. **Handle a `test-writer` stop.** Check the report's first line before anything else. If it is `Diff: unreadable at <path>`, the orchestrator's own `test_diff_file` could not be read — this is an orchestrator bug, not a user choice: surface the unreadable path to the user and **stop the run**; do not offer to skip tests (skipping would silently proceed past evidence that could not be read). Otherwise, **where Pre-Phase 3.5 recorded a `test_decision`, apply it** rather than asking again — that question was put to the user before any file was edited. **Record in the Phase 5 `### Deferred items` section every behaviour — a Review focus line included — that the report's `### Notes` names as untested, with the reason it gives** (one it cannot test in isolation, or a `hinted` or `declared` command with no test of its own to follow): it is a test this run could not write. On `skip`, run step 3 (linters and builds) and skip **steps 4–6**, then proceed to Phase 3A step 7 (Verify outcome). **The skip is scoped to the tests because that is what was asked**: Pre-Phase 3.5's option reads *"Skip tests for this run"*, and the lint and build gate is neither a test nor something a missing baseline prevents — a run that skips it commits code that was never compiled, which nobody consented to. There is no second prompt here, and a command supplied here would not help: a capture taken after the edits is a test run, not a baseline. **The gate is the recorded decision, not the report's `Framework` field**: `Framework: not detected` is emitted only where the capture was `COMMAND_NOT_FOUND` (`dev-workflows:test-baseliner` capture step 4), while the other capture that asked — `RUN_FAILED` — names the suites it could not run, so `test-writer` writes against them and reading the field alone would drop the recorded skip — of either provenance — and re-prompt at step 5.

3. **Run linters and builds.** Use the project's standard lint/build commands as discovered by whichever codebase exploration this run actually performed — Phase 2A's subagent, Phase 2B's Explore subagent, or the Phase 1.7 fan-out summary on a `fan_out` run — and, where none of them named one, read them from the repo's own build/lint configuration at its top level. Run each from the directory the exploration found it in, in a subshell so the session's own directory never moves: `(builtin cd "<top level>/<dir>" >/dev/null && <command>)`, `<top level>/<dir>` being the top level itself unless the exploration said otherwise. **Do not cite Phase 2A here**: Phase 3B step 8 re-enters this step on the SIGNIFICANT / HIGH-RISK path, which a run reaches with or without Phase 2A's exploration, and a Phase 2B `### Re-classification` the user accepts reaches Phase 3A with Phase 2A's own exploration deliberately not re-run. Do not run the full test suite here — that is step 4.

4. **Invoke `test-baseliner` in verify mode** against the baseline captured in Pre-Phase 3.5:

   → Agent (subagent_type: "dev-workflows:test-baseliner", model: `<detection_model — §2.1 Sonnet chain>`):
     > "Run the agent in the following mode:
     >
     > Mode: verify
     > Baseline: [paste the captured ## Test Baseline block]
     > Project root: [the same absolute path Pre-Phase 3.5's capture sent, and never a different one — `### Suites` records each marker as a path relative to this root, so a verify rooted anywhere else reads every marker as moved and, where a framework names more than one detected suite, every identifier of it as missing (`dev-workflows:test-baseliner` capture step 1, measured there)]
     > command_hint: [the recorded `test_command_hint` — include this line only where Pre-Phase 3.5 recorded one, and never a different value: a verify run over a different set of suites is not a comparison]"

5. **Act on the verify report.** **A non-empty `### New failures` list sends the run to the fix loop whatever the `Status` says.** A test this run's own `test-writer` just wrote has never been in any baseline list, so when it fails it is a **New failure** and nothing else — and `New failures` is not a `Status` value, so `OK` and `PARTIAL` are both reachable with one standing (`dev-workflows:test-baseliner` verify step 6). Branching on the `Status` alone reports a pass on the run's own broken test. **The list and the `Status` are read together, not one instead of the other**: work the `Status` arm below first, so its own record is written, and let the list decide where the run goes next. Every value is handled here, none is passed over. **And every `### Notes` line the report opens with `CAVEAT: ` is surfaced and recorded in the Phase 5 `### Deferred items` section whatever the `Status` says** — the same obligation Pre-Phase 3.5 carries over its own capture and for the same reason: a marked line is a note whose harm neither the `Status` nor this report's identifier lists show, and verify marks three of its own beside every one capture step 1's detection owed (`dev-workflows:test-baseliner` verify step 7). **On `REGRESSIONS`, read them before step 6 rather than after it**: two of verify's own three put baseline identifiers into `### Missing from run` without that being evidence this change removed them — a pairing nothing could resolve, and a `command_hint` that narrowed the run — and the fix loop would otherwise spend both its attempts chasing them.
   - `OK` → the `Status` itself leaves nothing to do, **though the lead-in's `CAVEAT: ` obligation still holds here and this is the arm on which it earns its keep**: nothing else in a green report puts a marked line into the run's record, and one of them is a suite that aborted without losing a baseline test — an abort this value is defined to tolerate. With `### New failures` empty, Phase 3.5 is done; with it non-empty, step 6 takes the run.
   - `PARTIAL` → no regressions, and a suite could not be run at either end. Record each such suite from `### Suites` in the Phase 5 `### Deferred items` section — **that record is this arm's own obligation and is made either way**, since step 6 records regressions and new failures and nothing about `### Suites`. **Read the report's `### Notes` beside those rows and carry what they say about a suite into its entry** — the same obligation Pre-Phase 3.5's own `PARTIAL` arm carries, and for the same reason: verify mode's `### Notes` carries capture step 1's detection notes as well as this call's aborts and pairing facts (`dev-workflows:test-baseliner` verify step 7), so a suite the watch carve-out never reached is recorded as that rather than as a runner that could not run. Then, with `### New failures` empty, there is nothing to fix and Phase 3.5 is done; with it non-empty, step 6 takes the run.
   - `RUN_FAILED` or `COMMAND_NOT_FOUND` → **nothing was compared, so neither is a pass.** They differ only in how far the call got: `RUN_FAILED` means no detected suite paired with the baseline (**`Comparison status: invalid`** — verify step 2), or none produced counts (**`best-effort`**, not `invalid`: "none produced counts" means every suite aborted, and verify step 3 sets `best-effort` on the first abort with nothing resetting it, so quote the field the report actually carries rather than this arm's other half's); `COMMAND_NOT_FOUND` means **this run's** detection selected no suite at all (`invalid` as well — verify step 1), which after a baseline that named one says the edits removed its marker — a renamed `pom.xml`, a deleted `Makefile`. Neither is settled by anything Pre-Phase 3.5 recorded, and a run whose baseline named no framework never reaches this step. Surface the report's `Reason` line **where it carries one** — verify step 2's `invalid` return does, step 6's `RUN_FAILED` does not, and `Reason` is no field of the return structure — and the `### Suites` rows and the `### Notes` lines either way, the notes being where a watch carve-out that did not fire is named, which is what *Investigate further* would otherwise have to rediscover, then ask:
     ```
     choices: ["Investigate further", "Accept an unverified run and proceed (document in Phase 5 report)", "Cancel"]
     ```
     **Investigate further** → diagnose manually and re-run step 4 when ready. **Accept** → record in the Phase 5 `### Deferred items` section that no comparison was made, with whatever the report gave as its reason, and set `clean_finish: false` for Phase 4.6. **Cancel** → stop and summarize.
   - `REGRESSIONS` → read the lead-in's `CAVEAT: ` lines first, since two of the kinds verify marks say these identifiers are in `### Missing from run` for something other than this change, then the fix loop below.

6. **Fix loop** — on `Status: REGRESSIONS`, or on a non-empty `### New failures` list under any `Status`:
   - The **session model** (not a subagent) applies fixes. No `review-fixer`-style indirection is used here — the scope is narrow and the context is already fully in-session. Use the `test-baseliner` verify report as the authoritative list of what broke.
   - After each fix attempt, re-capture the diff (`( i=$(command mktemp -t dw-index-XXXXXX) && trap 'command rm -f -- "$i"' EXIT && { command cp -- "$(git rev-parse --git-path index)" "$i" 2>/dev/null || command rm -f -- "$i"; } && export GIT_INDEX_FILE="$i" && git add -N --ignore-removal :/ && git -c diff.relative=false diff --no-ext-diff --no-color "$(git rev-parse -q --verify HEAD || git hash-object -t tree /dev/null)" )`) and re-run `test-baseliner` in verify mode against the **original** baseline (never re-baseline mid-loop — a mid-loop re-baseline would silently absorb a regression as the new normal).
   - Cap at **2 fix attempts**. If any regression or new failure remains after the second attempt, surface to the user:
     ```
     choices: ["Investigate further", "Accept the remaining failures and proceed (document in Phase 5 report)", "Cancel"]
     ```
     - **Investigate further** → stop the automated loop; the session model diagnoses manually and re-runs verify when ready.
     - **Accept the remaining failures** → record each regression and each new failure in the Phase 5 `### Deferred items` section with the user's rationale; proceed.
     - **Cancel** → stop and summarize.

Once Phase 3.5 returns (passed, skipped, or accepted with failures kept or without a comparison), return to Phase 3A step 7 (Verify outcome).

---

## Phase 3B — Implementation + Opus review (SIGNIFICANT / HIGH-RISK)

Use the currently selected model or Sonnet for implementation itself; Opus is reserved for the review — unless §10 enforces a model, in which case every dispatched step, the review included, runs on `run_flags.enforced_model`. 'Opus review' throughout this command names the Phase 3B review gate, whatever model it runs on.

For a long step list, apply `${CLAUDE_PLUGIN_ROOT}/references/context-management.md` — checkpoint at N,
offload parallel-safe (`[P]`) steps to subagents, or decompose — so the run does not degrade as context fills.

At each checkpoint, also consider suggesting **`/compact`** to free context before the next scope/Epic (per `workflows-core:session-hygiene` §3 — mid-command → `/compact` only, never `/clear`; guidance only).

1. Work through each step in order
2. Make precise, surgical changes — do not modify unrelated code — and change code only in the repository Pre-Phase 3 branched: any other code repository, one this run was given included, is read-only context, and a change one needs goes into the Phase 5 report's `### Session learnings`, on that repository's one follow-up line for `/dev-workflows:implement` run from there, addressed to the unit this run implemented (the Epic itself, where it was one; no key on a direct run), which Phase 6 collects; an early stop names it beside its §3.1 line instead (Phase 4.6)
3. Follow existing code style and LF line endings
4. If something **new** emerges mid-implementation, look before stopping: **a decision** — Phase 1's test: nothing this run can read settles it, and its answer changes what the user would notice in the result → STOP, ask with choices (2–4 options; the harness supplies the free-text escape), resume after answer; **anything else** → look it up and continue — an open question the user would not notice is settled by the run and recorded in the Phase 5 report's `### Assumptions & limitations`.
4a. **Invoke `test-writer` agent** (inserted before the review diff capture in step 5 so the Opus review sees code and tests together — test adequacy is already a review dimension in `code-review.md`). First, at the orchestrator, capture the diff for the dispatch: write `( i=$(command mktemp -t dw-index-XXXXXX) && trap 'command rm -f -- "$i"' EXIT && { command cp -- "$(git rev-parse --git-path index)" "$i" 2>/dev/null || command rm -f -- "$i"; } && export GIT_INDEX_FILE="$i" && git add -N --ignore-removal :/ && git -c diff.relative=false diff --no-ext-diff --no-color "$(git rev-parse -q --verify HEAD || git hash-object -t tree /dev/null)" )` (so new files are included) to a temp file (`command mktemp -t dw-impl-diff-XXXXXX`, never inside a repo tree) and record its absolute path as `test_diff_file`. `test-writer` has no shell tool — it can only `Read` the path it is given. Then spawn:

   → Agent (subagent_type: "dev-workflows:test-writer", model: `<detection_model — §2.1 Sonnet chain>`):
     > "Write tests for this brief:
     >
     > Task description: [substitute full description]
     > Plan: read it from the file at [the `plan_file` path]
     > Diff: read it from the file at [the `test_diff_file` path]
     > Project root: [the repository's top level, `git rev-parse --show-toplevel` — every diff this run captures is relative to it]
     > Baseline: [paste the ## Test Baseline block captured in Pre-Phase 3.5]"

   Check the `test-writer` report's first line before invoking Opus review. If it is `Diff: unreadable at <path>`, the orchestrator's own `test_diff_file` could not be read — this is an orchestrator bug, not a user choice: surface the unreadable path to the user and **stop the run**; do not invoke Opus review. Otherwise, where Pre-Phase 3.5 recorded a `test_decision`, apply it and carry it into the Phase 5 report (mirrors the SIMPLE/MODERATE branch, gate included — the recorded decision, never the report's `Framework` field). On `skip`, step 8 below runs **only step 3 of the Phase 3.5 sequence — the lint and build — and none of steps 4–6**, exactly as the SIMPLE/MODERATE branch scopes it, and for the same reason: what was declined — or, on the run's own record, given up on — was the tests and not the build. There is no prompt here — asking after the edits would be asking for a baseline that can no longer be taken. As in Phase 3.5 step 2, record in the Phase 5 `### Deferred items` section every behaviour — a Review focus line included — that the report's `### Notes` names as untested, with the reason it gives.

5. After all changes are written: **DO NOT run tests yet.** When `task_shape: bug`, first **strip every `[DEBUG-xxxx]` probe** added during diagnosis (per `${CLAUDE_PLUGIN_ROOT}/references/bug-diagnosis.md`); the review diff must contain no debug instrumentation. Capture the diff and the project root. Use `( i=$(command mktemp -t dw-index-XXXXXX) && trap 'command rm -f -- "$i"' EXIT && { command cp -- "$(git rev-parse --git-path index)" "$i" 2>/dev/null || command rm -f -- "$i"; } && export GIT_INDEX_FILE="$i" && git add -N --ignore-removal :/ && git -c diff.relative=false diff --no-ext-diff --no-color "$(git rev-parse -q --verify HEAD || git hash-object -t tree /dev/null)" )` — this includes intent-to-add untracked new files and, through `--ignore-removal` and the diff against `HEAD` (the empty tree before a first commit), every deletion, so the diff is never empty for implementations that only create or delete files, and it now also includes the test files from step 4a. Write this diff to a temp file (`command mktemp -t dw-impl-diff-XXXXXX`, never inside a repo tree) and record its absolute path as `review_diff_file`; the code-review dispatch (step 6) receives this path.
6. **Opus code review** — spawn.

   → Agent (subagent_type: "dev-workflows:code-review", model: `<review_model — §2 Opus chain, equal to code-review's frontmatter pin; under §10, run_flags.enforced_model>`):  # recorded in model_routing as review_model above, frontmatter-pinned, no override added unless §10 enforces a model
     > "Produce the Opus code review for this brief:
     >
     > Task description: [substitute full description]
     > Classification: [SIGNIFICANT | HIGH-RISK] — reason: [as the `model_routing` block records it — Phase 1.5's criterion, the multi-source floor, or a raise]
     > Plan: read it from the file at [the `plan_file` path]
     > Diff: read it from the file at [the `review_diff_file` path from step 5]
     > Deferred to another code repository: [each change another code repository needs (the plan's Out of scope or Phase 3A/3B step 2), as an explicit deferral note — omit where none]
     > Project root: [the repository's top level, `git rev-parse --show-toplevel` — every diff this run captures is relative to it]
     > applicable_ard: [the ARD invariants from Phase 1.8, or omit if none / direct mode]
     > applicable_spec: [ { spec_paths: [...], in_scope_ids: [...] } when a spec/design is in scope, else omit ]
     > claims_file: [the `claims_file` path — pass it only when a `review-fixer` Fix Report exists for this run; omit otherwise]"

7. Act on the return:

   **Check the review's first line before acting on the verdict.** If it is `Diff: unreadable at <path>`, the orchestrator's own `review_diff_file` could not be read — an orchestrator bug, not a user choice: surface the unreadable path to the user and stop the run. Do NOT triage the finding and do NOT dispatch `review-fixer`: the finding names a capture failure no fixer can act on, and running the cycle would spend a fix dispatch and a re-review to arrive back here.
   - **`### Re-classification` section** — the reviewer decided the change is actually `SIMPLE` or `MODERATE` on inspection. Surface it to the user and ask `choices: ["Accept revised classification (Recommended)", "Override and keep the BLOCK-gated review", "Cancel"]`. If accepted, treat the review as an implicit PASS: skip the BLOCK branch, proceed to step 8, and do NOT re-invoke the reviewer on later fix deltas. Record the revised classification for the Phase 5 report. If overridden, re-invoke code-review with an explicit note that the classification is intentional. If the user cancels, stop through Phase 4.6 — its `"Every run"` list.
   - **BLOCK** — invoke the review-fixer agent (see Review-fixer sub-step below). If `Stop condition flag` is `CLEAR`, re-run the Opus code review on the updated diff (one re-review only). If `Stop condition flag` is `NEEDS HUMAN`, do not re-review: surface the deferred BLOCKER(s) to the user with the reason `review-fixer` gave and stop. Triage the re-review under `workflows-core:finding-triage` § On re-review (the triage sub-step below). If the review **stayed blocked** — a `BLOCKER` survives that triage, or you keep the verdict at either settle prompt — stop: surface the remaining blockers to the user, exactly as the `NEEDS HUMAN` stop above does. On that prompt's **Proceed**, the verdict is settled as not BLOCK — continue to step 7.5. **The stop for a review that stayed blocked offers no arms, and the reason is worth stating so that one is not added back.** It is in Phase 4.6's `"Every run"` list, so by the time it presents anything the implementation is **already committed** on its own branch with `clean_finish: false` — and `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §1 rule 3 forbids every operation an *"abandon and restore to pre-impl state"* arm would need on that commit (`reset`, `checkout --`, `branch -D`, `--amend`). Such an arm was offered here and was unfollowable: no file defined what it did, and the one phase that could have undone it is the phase that had just made it durable. What replaces it is a report the user can act on themselves — nothing was merged and the base branch was never touched, so abandoning the work is `git switch <base>` in their own hands, and Phase 4.6's outcome line has already named the branch, the sha, the outstanding `stash_ref` where Pre-Phase 3 pushed one, and, where §2.4's consent choice, §2.8's base-branch ladder, §2.6's `gh` capability probe and §2.5's push all allowed one, the draft pull request whose DO-NOT-MERGE banner says not to merge it — or, where any of them did not, §3.1's own row saying so and what it names instead. **Four determinants, and still not a closed set**: §2.6 also emits *pushed to existing PR #<num>* on a re-run, where a pull request exists but is neither a draft nor this run's. §3.1's rows are the authority on which line the run emitted, never a determinant list written out here — state whichever line it did beside the blockers, and never the draft pull request as though it existed (§2.10). Do not run tests until the verdict is not BLOCK, or a settle prompt's **Proceed** has settled it so.
   - **PASS WITH RECOMMENDATIONS** — invoke the review-fixer agent for MAJOR findings (see Review-fixer sub-step below). MINOR / NIT findings may be deferred — note them in the Phase 5 report.
   - **PASS** — proceed.

   **Triage sub-step** (before any fixer dispatch, and on every re-review): invoke `Skill(skill: "workflows-core:reference", args: "finding-triage")` and follow it. For each finding, verify its claimed consequence at the location it names; keep it, mark it unverified, or dismiss it; record every dismissal and every unverified finding with its reason; raise a grade only by effect; and rule on each line of the review's `### Declined to judge`. Hand the fixer **survivors only**, and carry every disposition into this run's report. A re-review — the one the BLOCK branch allows, one you chose at the first settle prompt, and step 8's review of the Phase 3.5 delta — is triaged under that reference's § On re-review: it carries forward what this run already ruled — save, on a re-review you chose at the first settle prompt, the dismissed and unverified findings it re-verifies — and no survivor of it is handed to a fixer. At either of that reference's settle prompts, **Keep the verdict** means the review **stayed blocked** — the BLOCK branch's stop — **Cancel** stops the run through Phase 4.6, and **Proceed** continues to step 7.5 — or, after step 8's own delta review, to step 9.

   **Another code repository's findings** (after the triage sub-step, on every review and re-review): record each survivor whose fix lies in another code repository as Phase 3B step 2 says (the invariants), and hand it to no fixer; it is a finding the run did not apply. A `BLOCKER` among them is one this run cannot fix, whatever else survives: the review stayed blocked, so stop as the BLOCK bullet's stayed-blocked stop does, naming the repository each such fix lies in and every other survivor, which no fixer was handed, with no fixer dispatch and no re-review. On the first review, where at least one survivor was recorded so and no `BLOCKER` or `MAJOR` is left for the fixer, dispatch none: on PASS WITH RECOMMENDATIONS, continue to step 7.5; on BLOCK, ask `workflows-core:finding-triage`'s first settle prompt (§ When triage empties the survivor set), reporting every survivor (those recorded for another code repository, and any `MINOR` or `NIT` left here) in place of its *nothing survived*, and act on its answer as the triage sub-step does.

   **Review-fixer sub-step** (for BLOCK and PASS WITH RECOMMENDATIONS): first write the **triaged survivor list** from the sub-step above, less the findings the paragraph above recorded for another code repository — the surviving findings only, each with its severity, location, observation, and suggestion — to a temp file (`command mktemp -t dw-impl-review-XXXXXX`, never inside a repo tree) and record its path as `review_file`. Dismissed and unverified findings NEVER enter that file; they go to the `### Review triage` report section instead.

   → Agent (subagent_type: "dev-workflows:review-fixer", model: `<fixes_model — = detection_model, §2.1 Sonnet chain>`):
     > "Fix the review findings for this brief:
     >
     > Task description: [substitute full description]
     > Review output: read it from the file at [the `review_file` path]
     > Project root: [the repository's top level, `git rev-parse --show-toplevel` — every diff this run captures is relative to it]
     > Severities to fix: BLOCKER and MAJOR"

   Wait for the fix report. Re-capture the diff after the fixer completes, **overwriting `review_diff_file`** (write a fresh `( i=$(command mktemp -t dw-index-XXXXXX) && trap 'command rm -f -- "$i"' EXIT && { command cp -- "$(git rev-parse --git-path index)" "$i" 2>/dev/null || command rm -f -- "$i"; } && export GIT_INDEX_FILE="$i" && git add -N --ignore-removal :/ && git -c diff.relative=false diff --no-ext-diff --no-color "$(git rev-parse -q --verify HEAD || git hash-object -t tree /dev/null)" )` to that same path) — so the one re-review at step 7 reads the post-fix diff, not the stale step-5 capture. Also write the fixer's full Fix Report to a temp file (`command mktemp -t dw-impl-claims-XXXXXX`, never inside a repo tree) and record its path as `claims_file` — the one re-review reads it as the deferred claims input, so the reviewer checks the fixer's account of its own work instead of assuming it.

   - If the fix report contains any `DEFERRED — plan-conflict` finding, surface it to the user **immediately** (do not wait for the review to stay blocked): show the finding beside the plan text it contradicts and ask `choices: ["Revise the plan (the finding governs)", "Apply the fix against the plan (the plan governs — logged in Phase 5)"]`. Act on the answer before re-running the review.

7.5. **Spec/design conformance escalation.** For each unresolved `missing`/`contradicts` in-scope requirement from the code-review Spec/design-conformance dimension, write a `- [ ]` note back onto the source `specification.md`/`design.md` under an `## Engineering review` heading (the same escalation `/design` uses; annotate only — never mutate existing `[Uxx]`/`[ACxx]`/`[TCxx]` IDs). Only a `specification.md` or `design.md` in `$SPECS_PATH`, or in this repository at a path git does not ignore (`git -C "<top level>" check-ignore -q -- <path>` exits 1), is annotated; one anywhere else — inside another code repository, which Phase 3A/3B step 2 keeps this run from writing, at an ignored path no commit would carry, or outside every repository — gets no note, the Phase 5 report's `### Spec/design conformance` section carrying the gap instead, or, on an early stop, the stop's own message (Pre-Phase 3). Never silently drop them, never invent new work. Record which of `specification.md`/`design.md` in `$SPECS_PATH` received a note — Phase 4.5 needs to know whether only one, or both, were annotated. A note in `$SPECS_PATH` is written here and handed off later (see the escalation handoff after Phase 4); a note in this repository rides on Phase 4.6's commit, or stays in the working tree under `--no-commit`. **`exceeds` findings are never written here**: they report what this change added beyond the spec, which the Phase 5 report carries and the review cycle acts on — not a gap in the spec.
8. **Run Phase 3.5 (post-review).** After the review gate clears (a non-BLOCK verdict, or a settle prompt's **Proceed**), run the Phase 3.5 sequence — its steps 3–6 (lint/build, `test-baseliner` verify, the status branch, the fix loop) — **not before**. This preserves the invariant "NEVER run tests for SIGNIFICANT / HIGH-RISK before Opus review returns non-BLOCK, or a settle prompt's Proceed settles it as one". The fix loop inside Phase 3.5 applies fixes via the session model; if the fixes are non-trivial **and** the reviewer was NOT down-classified in step 7, re-invoke the Opus code review on the delta after Phase 3.5 completes (first overwrite `review_diff_file` with a fresh `( i=$(command mktemp -t dw-index-XXXXXX) && trap 'command rm -f -- "$i"' EXIT && { command cp -- "$(git rev-parse --git-path index)" "$i" 2>/dev/null || command rm -f -- "$i"; } && export GIT_INDEX_FILE="$i" && git add -N --ignore-removal :/ && git -c diff.relative=false diff --no-ext-diff --no-color "$(git rev-parse -q --verify HEAD || git hash-object -t tree /dev/null)" )` so the re-review reads the post-Phase-3.5 diff). Triage it as a re-review (step 7's triage sub-step); if the review stayed blocked (`workflows-core:finding-triage` § On re-review), stop as step 7's BLOCK branch does after its re-review. If the reviewer WAS down-classified, skip the re-review.
9. Verify the outcome matches the approved plan — on a run whose re-plan the user approved, both, as `plan_file`'s opening line reads them — and the review verdict.
10. Proceed to Phase 4.

---

## Phase 4 — Post-implementation maintenance (both branches)

**First remove this run's handoff files.** Nothing from here on reads one — `summary_file`,
`partial_diff_file` where Phase 3A step 5 wrote one, every `test_diff_file` and `review_diff_file` this
run wrote (a re-capture that overwrote a path leaves one file, a fresh `mktemp` another), `review_file`
and `claims_file` — save `plan_file`, which Phase 4.6's `body_facts` read and Phase 4.6 then
removes; under `--no-commit`, where nothing reads it, it goes now with the rest. Remove each as
`command rm -f -- "<path>"`, per `${CLAUDE_PLUGIN_ROOT}/references/context-management.md`
(**Hand off by file, not paste**), which says why nothing else would. A run that stops before this
phase — the two unreadable-`test_diff_file` stops, the unreadable-`review_diff_file` stop, the
`review-fixer` `NEEDS HUMAN` stop, a review that stayed blocked, a settle prompt's **Keep the
verdict**, Phase 3A step 5's **Stop** on a trigger met after the re-plan, or a Cancel — removes the
files it had made, `plan_file` included, as it stops — after Phase 4.6, where the stop runs it — in
the same way, save a file the stop itself named as unreadable, which stays for the operator to look
at (that reference again).

Then gather the actual change context:

a. Run `( i=$(command mktemp -t dw-index-XXXXXX) && trap 'command rm -f -- "$i"' EXIT && { command cp -- "$(git rev-parse --git-path index)" "$i" 2>/dev/null || command rm -f -- "$i"; } && export GIT_INDEX_FILE="$i" && git add -N --ignore-removal :/ && git -c diff.relative=false diff --no-ext-diff --no-color "$(git rev-parse -q --verify HEAD || git hash-object -t tree /dev/null)" --numstat -z )` and capture the files this run has changed so far, each path whole and raw with its added and removed line counts, less every path outside `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.2's run set (both in `-z` form, as §2.2 compares them). Phase 4's own edits come after it, so the pull request's list is `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.7 item 1's, read from git, not this one.
b. Compose a **change summary block**:

```
Implementation: [one-sentence description of what was built]
Change type: code
Classification: [SIMPLE | MODERATE | SIGNIFICANT | HIGH-RISK]
Files changed so far (step a):
<step a's paths with their line counts, one per line>
Notable additions/removals: [new commands, APIs, config keys, dependencies — one line each; or "none"]
Opus review verdict: [PASS | PASS WITH RECOMMENDATIONS | BLOCK — or "N/A (SIMPLE / MODERATE)"]
```

**Under `run_flags.skip_feedback`** (`workflows-core:run-flags` §4), dispatch `workflows-core:defect-reporter` in place of Agent 4 (`impl-maintenance`), with the same handoff plus `Plugin root: ${CLAUDE_PLUGIN_ROOT}` (literal — it expands in command bodies to this command's own plugin location), and `model: <§2.1 Sonnet chain, or run_flags.enforced_model>`; if it returns at least one defect, persist them with `emit-bugs` (`Skill(skill: "workflows-core:reference", args: "feedback-emission emit-bugs")`) in place of `emit-auto`, otherwise load nothing. Surface `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` in the Phase 5 `### Session learnings` line, in place of the persisted-path line. Capture-at-block (`emit-block`) is unaffected by the flag.

Then spawn all four agents. They are independent and can run in any order — spawn them all before waiting for any to complete:

**Agent 1 — Documentation** (general-purpose, model: `<detection_model — §2.1 Sonnet chain>`):
> "Post-implementation documentation review. Change summary:
> [paste change summary block]
>
> Scan for README.md, CHANGELOG.md, docs/, or any .md files in the project root (the repository's top level, `git rev-parse --show-toplevel`) or a docs/ directory.
> Determine if documentation needs updating:
> - Skip if: purely a bug fix, vulnerability fix, internal refactor, or test-only change
> - Update if: new feature, changed behavior, new commands/APIs/config options, altered usage patterns
> Use the file list above to reason precisely about what changed. If an update is warranted: apply minimal edits to the relevant section(s).
> Return: file updated and what changed, OR 'no update required (reason)'."

**Agent 2 — Knowledge base** (general-purpose, model: `<detection_model — §2.1 Sonnet chain>`):
> "Post-implementation knowledge review. Change summary:
> [paste change summary block]
>
> Check ~/.claude/memory/ (global) and .claude/memory/ (project-level, at the repository's top level from `git rev-parse --show-toplevel`, preferred for repo-specific knowledge) for existing knowledge files.
> Determine if a new knowledge entry is warranted — look for: reusable insights or patterns, non-obvious constraints or gotchas, anti-patterns discovered, clarified trade-offs.
> If YES: append to the most appropriate existing file (never create a new file if an existing one fits) using this format:
> ### [Short title]
> - **Context**: what problem/situation triggered this
> - **Insight**: the learned rule, pattern, or gotcha
> - **When it applies**: conditions under which this matters
> - **Date**: YYYY-MM-DD
> - **Ref**: [first 60 chars of implementation description]
> Return: file updated/created and summary of entry, OR 'no update required'."

**Agent 3 — Instructions** (general-purpose, model: `<detection_model — §2.1 Sonnet chain>`):
> "Post-implementation instructions review. Change summary:
> [paste change summary block]
>
> Check CLAUDE.md in the project root (the repository's top level, `git rev-parse --show-toplevel`) and ~/.claude/CLAUDE.md (global).
> Determine if any rules, guidance, or guardrails are missing because of what this implementation revealed.
> Skip if: the implementation followed existing patterns with no surprises, required no novel constraints, and introduced no anti-patterns. Only update if a concrete, recurring rule would have prevented a decision point or misunderstanding during this implementation.
> If YES: apply minimal, additive, scoped changes only — do not rewrite sections wholesale.
> Return: what was changed and why, OR 'no update required'."

**Agent 4 — Session maintenance** (workflows-core:impl-maintenance, model: `<detection_model — §2.1 Sonnet chain>`):
> "Analyse this session and return a Lessons Learned report.
>
> Session handoff:
> - Command run: /implement
> - What was done: [one-paragraph summary of the implementation]
> - Key events: [BLOCK reviews encountered and their reason, test regressions, workarounds, unexpected ambiguities — or 'none']
> - Workarounds used: [manual steps not automated by the workflow — or 'none']
> - Review verdict: [PASS | PASS WITH RECOMMENDATIONS | BLOCK | N/A]
> - Test result: [passed N tests, N regressions, not run — or actual result]
> - Project root: [the repository's top level, `git rev-parse --show-toplevel` — every diff this run captures is relative to it]"

Collect all four summaries for the Phase 5 report.

**Persist plugin feedback (automatic).** After Agent 4 (`impl-maintenance`)
returns, project its plugin-facing slice into the specs repo by invoking `Skill(skill: "workflows-core:reference", args: "feedback-emission emit-auto")` and calling its `emit-auto` entry point (§6). Pass Agent 4's Lessons Learned report,
`command: /implement`, the run's `key` and `source`, and `plugin_version`
(read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). `emit-auto`
renders only the report's **Command workflow improvements**, **New agents /
skills**, and plugin **Reference docs** sections plus the **Key observations**
that triggered them (§4 plugin-facing predicate) — never target-project
`CLAUDE.md`/hook advice — as `origin: auto` entries, dedupes by stable `id`
(§3), resolves the target via the §2 specs-first ladder, and writes silently.
List the persisted path (or "no plugin-facing signal — nothing persisted") in
the Phase 5 `### Session learnings` line. ADDITIVE — the impl-maintenance
report still appears in the report; this step NEVER fails the run, NEVER
commits (still true — this step only writes the feedback file; those writes
are committed by the terminal `commit-artifacts` step in Phase 7, per
`workflows-core:specs-repo-git` §4), and NEVER writes
into the code repo or the current working directory, where it is not the specs repository.

---

## Phase 4.5 — Escalation handoff (spec/design conformance notes)

A **silent no-op** when step 7.5 (Phase 3B) wrote no `- [ ]` notes in `$SPECS_PATH` — a note it wrote in this repository rides on Phase 4.6's commit instead (and stays in the working tree under `--no-commit`) — which covers every SIMPLE/MODERATE run (no `code-review`, so step 7.5 never runs) and every run with no spec/design in scope, direct-prompt or otherwise.

When step 7.5 did write one or more notes in `$SPECS_PATH` — the set this phase reads throughout: `prefix` = `spec` when only `specification.md` was annotated, otherwise `design`; `feature_folder` = the directory the annotated file(s) live in (the same specs-repo folder Phase 0 resolved them from); `deliverable_paths` = the annotated file(s) in `$SPECS_PATH`. Invoke `Skill(skill: "workflows-core:reference", args: "phase-handoff")` and present its §4.3 consent choice verbatim — **two arrays, selected by the annotated set per §4.1's set rule, and the test is not the `prefix` test above.** Where `specification.md` is in the set (whether or not `design.md` is too), present §4.3's **gated — stopping** array (§4.1 bullet 1), because `/dev-workflows:design` stops on an un-landed `specification.md`:

`choices: ["Branch + commit + push + open PR to main (Recommended)", "Just write the files — I'll handle git (the next phase will stop until this is on main)", "Cancel"]`

Where the set is an annotated `design.md` **alone**, present §4.3's **gated — falling back** array (§4.1 bullet 2) instead, because the only §3.4 rows naming `design.md` are this command's own in-scope-only gate and `/dev-workflows:ready`'s coverage gap, neither of which stops:

`choices: ["Branch + commit + push + open PR to main (Recommended)", "Just write the files — I'll handle git (the next phase does not stop on this, but until this is on main it might not read your copy)", "Cancel"]`

On the first choice, execute `handoff-to-main` (`Skill(skill: "workflows-core:reference", args: "phase-handoff handoff-to-main")`, §2) with `prefix`, `feature_folder`, and `deliverable_paths` as above; `title: <FOLDER-KEY> Record spec/design conformance findings from /implement`, `<FOLDER-KEY>` being `feature_folder`'s own `key`, read off its carrier (`workflows-core:addressing` §4) — the key the handoff's branch is named for (§2.2 there), and so the Epic's, not the resolved folder's, wherever a run that chose an Epic under a PRD address annotated that Epic's files; and `body_facts` = the count of escalated `- [ ]` notes, the code-review Spec/design-conformance dimension summary they came from, and the fact that whoever next reads this `specification.md`/`design.md` will not see them until this pull request is merged. Emit its §4.1 outcome line in the Phase 5 `### Spec/design conformance` section.

Placement is deliberate, not stylistic: step 7.5 sits inside Phase 3B, before the tests run, so calling `handoff-to-main` there would commit mid-review — hence the notes are written in 7.5 and handed off here instead, after Phase 4's post-implementation maintenance and before Phase 6's follow-ups and Phase 7's cost/`resume.md`/`commit-artifacts`. A call from inside Phase 6 or Phase 7 would falsify Phase 7's never-commits-the-deliverable claim below.

---

## Phase 4.6 — Code-repo handoff (commit, push, PR)

Runs on **every** run that created a branch in Pre-Phase 3 — both classification branches, keyed mode and direct mode alike. Skipped only under `--no-commit`. Cite `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` and execute its `finish-code-branch` entry point (§2) inline, against **the code repository** this run changed — never `$SPECS_PATH`.

**The commit is prompt-free and the push and pull request are not** (§1 rule 5). There is no "leave it uncommitted" option in §2.4's choice, and a run that ends with the implementation sitting in a working tree is a defect rather than a style.

**"Every run" includes every early stop that happens after the branch exists.** This command has exits that stop *after* Pre-Phase 3 created the branch and after files were written: the two unreadable-`test_diff_file` stops (Phase 3.5 step 2 and Phase 3B step 4a), the **Cancel** arms of both Phase 3.5 prompts (step 5's unverified-run prompt and step 6's regression prompt), the unreadable-`review_diff_file` stop (Phase 3B), the `review-fixer` `NEEDS HUMAN` stop, a review that stayed blocked (Phase 3B step 7, or step 8's review of the Phase 3.5 delta), the **Keep the verdict** and **Cancel** arms of either of `workflows-core:finding-triage`'s settle prompts (Phase 3B steps 7 and 8), the **Cancel** arm of Phase 3B step 7's `### Re-classification` prompt, the **Cancel** arm of each of Phase 2B's three prompts — the re-classification prompt, the repro prompt and the plan-approval prompt — when Phase 3A step 5's re-plan reached it, and the **Stop** arm of that step's question on a trigger met after the re-plan. **Each of those runs Phase 4.6 before it stops**, with `clean_finish: false` and the stop's reason as the blocking fact. Skipping it would leave a written, branched, sometimes fully-reviewed implementation uncommitted — which this command's own invariants call a defect, and which is the case where losing the work costs most. Phase 4 is skipped on these paths (its maintenance agents have nothing to summarise for an aborted run), so 4.6's "after every in-repo write" precondition is satisfied trivially. Report the §3.1 line with the stop, not in a Phase 5 report that will not be produced, and name beside it everything Pre-Phase 3's opening sentence lists, since neither Phase 4.5, Phase 5 nor Phase 6 will run.

**Neither *Investigate further* arm is in that set, because neither stops the run.** Step 5's says *"diagnose manually and re-run step 4 when ready"* and step 6's *"stop the automated loop; the session model diagnoses manually and re-runs verify when ready"* — the loop ends, the run does not, and both come back through step 4 into Phase 4 and then into this phase in its ordinary place, where the Phase 5 report the paragraph above says will not be produced *is*. Calling 4.6 on them would commit the implementation before Phase 4, which this command's own invariant forbids outright. The list dropped both arms and dropped nothing else: every arm in it that actually ends the run is still in it.

**Two Cancels are not in that set on the ordinary path, and the test is the written file rather than the branch.** Phase 2B's repro prompt runs *before* Pre-Phase 3, so cancelling there leaves no branch and no written file — save on Phase 3A step 5's re-plan, which reaches that prompt after files were written, so its Cancel there is in the set above. Pre-Phase 3.5's framework prompt runs *after* the branch and still before the first edit — its Cancel leaves a branch with nothing on it, and there is as little for this phase to commit as in the ordinary Phase 2B case. Neither loses a stash: any stop after Pre-Phase 3 step 1 names an outstanding `stash_ref` in its own message, which is that step's rule rather than this phase's.

Placement is load-bearing. Phase 4's maintenance agents edit files **inside the code repo** — `README.md`, `CHANGELOG.md`, `docs/`, `CLAUDE.md`, and any project-level memory entry — so a call placed before Phase 4 would commit a partial run and leave those edits behind (`code-handoff.md` §4 obligation 1). Phase 4.5 runs first because it commits a *different* repository (`$SPECS_PATH`), and interleaving the two would make the run's two outcome lines impossible to attribute.

Pass the §2.11 inputs:

- `repo` — the repo Pre-Phase 3 branched; `branch` — the name it created.
- `pre_existing_dirty` and `stash_ref` — as recorded in Pre-Phase 3 step 1; both `null` on the clean-tree path.
- `key` and `workitem_key` — `unit_key` and its folder's `workitem_key` (Phase 0), the Epic's wherever `focus_key` is set and the resolved folder's (`workflows-core:addressing` §4) on a broad PRD-level slice; both `null` in direct mode. §2.3 turns them into the `[<key>]` subject suffix and the `Work-Item:` trailer that `workflows-core:implementation-format` §3 requires — **this is where the plugin writes that convention rather than teaching it**.
- `title` — the commit subject §2.3 writes, which §2.7 makes the pull-request title: `<one-line summary of what was built>` in the shape the repository's `git log` shows (§2.3 — on a conventional-commits log, the type the branch prefix expresses first, as in `feat: …`), ending ` [<key>]` with a key, `<key>` being the `unit_key` above, and with no suffix in direct mode.
- `body_facts` — what §2.7's four sections render: what was implemented and the files changed (§2.7 item 1 reads them from git, on an early stop as on a finished run); every change another code repository needs (the plan's Out of scope or Phase 3A/3B step 2), named in the Summary as a companion change (saying which of the two must land first where the plan or the diff shows it, and that the order is unknown where neither does) and weighed in Merge danger's blast radius; as the evidence, the Pre-Phase 3.5 baseline before and the `test-baseliner` verify result after; on a `task_shape: bug` run whose plan carries a red repro, also that repro's command and output before (where the repro was taken at a mid-implementation re-plan, noting that it ran on the partial edits) and the regression test's result in the verify run after; the facts §2.7's door and blast-radius calls rest on, as the plan and the diff show them; and the classification, with the Opus review verdict and triage summary where Phase 3B produced one and every review finding the run did not apply, each with its severity — deferred `MINOR`/`NIT` findings, a `MAJOR` or `BLOCKER` `review-fixer` deferred, every survivor whose fix lies in another code repository (Phase 3B step 7's *Another code repository's findings*), every survivor of a review that stopped before any fixer ran, and every survivor of a re-review — and, where Phase 3A step 5's **Continue** let a §1.1 trigger ship without the Opus review, that trigger and the paths that show it, as the reason no review ran; and, where Phase 0's multi-component picker or Phase 1's multi-component check was overridden, what was overridden — a multi-component PRD's flat specification implemented whole, the target mismatch, each missing artifact, each contract gap by `AD#N` — which Merge danger names.
- `clean_finish` — `false` when **this call is being made from any of the early stops the `"Every run"` paragraph above enumerates**, when the review stayed blocked, when the Phase 3.5 fix loop ended with failures the user chose to keep, when the user accepted an **unverified** run at Phase 3.5 step 5 (`RUN_FAILED` / `COMMAND_NOT_FOUND` — nothing was compared), or when Pre-Phase 3.5's `test_decision: skip` is **the run's own record** rather than the operator's answer (the two-failed-`command_hint` path); `true` otherwise. **That last one is a provenance test, not a token test**, and §2.9 says why: the operator's own *"Skip tests for this run"* is a typed decision taken up front and is honoured without penalty, while the run's own record after two failed hints is the same bullet's "attempted and could not complete, and proceeded on anyway" with nobody's consent attached. Pass the provenance, never the bare `test_decision` value. **The first condition is this command's form of the stopped-state one both siblings carry** — `/vuln`'s *"the CVE ended `BLOCKED`"*, `/upgrade`'s *"any component ended `BLOCKED`"* — and without it the paragraph above and this list disagreed on **six** stops that reach 4.6, each of which would have been handed `true` and opened an ordinary mergeable pull request. **Six of the seven that paragraph enumerated when this condition was added, and the arithmetic is worth keeping because a reader who counted the list then got seven**: the seventh — the stop after the one re-review, now *a review that stayed blocked* — was the next condition's own state, so it was already being handed `false` and was never in the disagreement. `NEEDS HUMAN` was, because the run does **not** re-review there, so its review never stays blocked. The settle prompts' **Keep the verdict** and **Cancel** arms joined that paragraph later, and reach `false` through this condition. Derive the number from the set the two lists disagree about, never from the length of either. It cites that paragraph and deliberately does **not** restate its members: a second copy of that list is exactly how the two came to disagree. The last is the same state `/upgrade` and `/vuln` set `false` on as `TESTS_NOT_RUN`, and it is the *stronger* case, not a weaker one: kept regressions at least know what failed. A `PARTIAL` verify is **not** in the list, deliberately and for the same reason those two map it onto `OK` / `SUCCESS` — every suite the baseline covered is green, and the ones it did not are named in `### Deferred items`. Per §2.9 this changes only the pull request (draft, with a DO-NOT-MERGE banner) — never whether the commit happens, and, **in this command**, never whether the push happens either. That second half needs its own reason rather than §2.9's: §2.4's first re-ask trigger fires wherever the `clean_finish` a call carries differs from the one the choice was answered under — in either direction — and `/implement` makes exactly one `finish-code-branch` call per run, with **every** condition above settled before it, so there is nothing left to differ from. (The count that stood here went stale in the commit that added the fifth condition; a construction cannot.) The trigger exists for `/vuln`, the one caller that makes more than one **full** `finish-code-branch` call in a run — one per CVE, because §2.12's *"Where each unit gets its own branch there is no split"* puts `/vuln` outside the split form — so a later CVE can carry a flag differing from the one an earlier CVE's answer was given under, and there it does re-ask the question rather than decide it. **`/upgrade` is not a second such caller, despite its per-component loop**: the split runs §2.1–§2.3 per component and the full entry point once at step 7.5, after every component has settled, so its §2.4 is asked once with `clean_finish` already final — the same structural reason it cannot fire here.
- `commit_template: null` — `/implement` documents no full template of its own, so §2.3 derives the rest of the subject from the repo's own `git log`.

Emit the §3.1 `Code repo:` outcome line in the Phase 5 report's `### Branch` section — once, and verbatim. **Under `--no-commit`** the entry point is not called at all, and §3.1's `--no-commit` row is emitted in its place, carrying what §3.1 says it carries, so the report still says where the work ended up — and where a stash went. Where `plan_file` is still on disk — every run but an ordinary `--no-commit` one, whose Phase 4 removed it — remove it now (`command rm -f -- "<plan_file>"`): the run kept it for this phase's `body_facts`, which read it.

**No other code repository is written.** A multi-source run (Phase 1.7) may read several code repositories but changes code only in the one Pre-Phase 3 branched (Phase 3A and 3B step 2, and the invariants), so every code change it made is this phase's to commit; a change another code repository needs is a follow-up (Phase 6's, or named beside the stop's §3.1 line on an early stop), never an uncommitted edit there.

Record what this phase actually did — the commit sha, and whether the push happened — as what Phase 4.7 writes into `implementation.md`; a declined or failed push is recorded as `pushed: false` rather than omitted.

## Phase 4.7 — Write the implementation record (keyed runs only)

**Skipped entirely when `mode: direct`** — there is no resolved folder to append to, and a
directly-implemented change has no block, exactly as before.

**Write `implementation.md`** in the folder of the unit this run implemented — the Epic's folder
wherever `focus_key` is set, whether the address named that Epic or Phase 0's picker or one-Epic
path chose it, and the resolved folder for a broad PRD-level slice. Invoke
`Skill(skill: "workflows-core:reference", args: "implementation-format")` and append one block per
run against its §1, which says why the record lives with its unit: one entry, the code repository
this run branched, naming `repo`, `branch`, `base`, `commit` and `pushed`. Append-only — never edit or
remove an earlier block, and a re-run adds a block rather than replacing one.

**It records refs and nothing else.** No summary of what was implemented: a summary is a
*description*, `workflows-core:source-truth` exists because descriptions drift
from the code they describe, and one here would be an unverified description in a folder of grounded
artifacts. A ref cannot drift.

**Record `pushed:` as it actually is.** A later run reading `pushed: false` says *"this was never
pushed"* rather than reporting an empty diff against a ref the remote does not hold.

This file is what `/document` and `/release-notes` read to ground their prose in the shipped diff
(§4 of that reference), and what `workflows-core:epic-picker`'s ● marker is computed from. It is committed by
the terminal `commit-artifacts` step with the rest of the run's `$SPECS_PATH` artifacts — unless the run carries `specs_git: blocked` or `specs_git: misrooted` (`workflows-core:specs-repo-git` §3.3 G0, §3.1), when it is written and not committed.

---

## Phase 5 — Final Report

Output a structured report — do NOT ask any closing confirmation:

```
## Implementation Report

### Classification
[SIMPLE | MODERATE | SIGNIFICANT | HIGH-RISK] — [reason]
[each change of class after Phase 1.5, one line each: `<from> → <to>`, where it happened — the multi-source floor, at planning, during implementation, or a down-classification the user accepted at plan approval or at review — and why: for a raise, the trigger and the path, or the paths, that show it, as its announcement named them; omit these lines where the class never changed]
[Under `run_flags.enforced_model`: `Model routing: bypassed — enforced <id> (flag|env)` — every dispatched step (planner, reviewer, fixer, test agents, scanners) already carries the enforced id in place of its own chain, per `workflows-core:model-routing/classification` §10. The `model_routing` block's `opus_available` is unaffected by enforcement (§10: a property of the environment, never rewritten to agree with the enforced id) and, wherever this report states it, is stated exactly as it stands. Omit the line otherwise.]

### Branch
[branch name created in Pre-Phase 3, e.g. feat/add-user-authentication]
[Pre-Phase 3 step 4's `Base branch unresolved …` line, verbatim, when it printed one; omit the line otherwise]
[the Phase 4.6 `Code repo:` outcome line, verbatim (`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §3.1)]

### What was implemented
[High-level summary]

### Files changed
[the paths this run changed, Phase 4's edits included: those Phase 4.6's commits carry, read from git as `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.7 item 1 says, where it committed them; otherwise — a §2.1 gate failure, a `git add` git refused, a commit a hook or git rejected, one you stopped at the secret scan, `--no-commit` — `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.2's run set, taken after Phase 4]
- path/to/file.ext — [what changed]

### Opus review (if applicable; on the enforced id under §10)
[Verdict and 1-line summary — naming the enforced id it ran on wherever `run_flags.enforced_model` is set (`workflows-core:model-routing/classification` §10) — or "N/A (SIMPLE / MODERATE)"]

### Review triage
- **Review triage:** [one line per review pass, per `workflows-core:finding-triage` § Reporting — N findings reviewed: M survived, U unverified, X dismissed (C carried, on a re-review)] — survivors: [on a re-review, `finding — severity` per survivor, or "none"; "N/A (first review)" otherwise] — dismissals: [`finding — reason`, or "none"] — unverified: [`finding — if-true severity — what would settle it`, or "none"] — raised: [`finding — from → to — effect`, or "none"] — set aside by the reviewer: [`behaviour — ruling`, or "none"] — settled: [the answer given at a settle prompt, or "not asked"] — or "N/A (SIMPLE / MODERATE, no Opus review)"

### Spec/design conformance (if a spec/design was in scope)
[coverage summary from code-review's dimension; list any missing/partial/contradicts/exceeds, and the already-present count — or "N/A"; if Phase 4.5 escalated notes, add the `Phase handoff:` outcome line from `handoff-to-main` (`workflows-core:phase-handoff` §4.1)]

### Commands / tests run
- [command] → [result]

### Knowledge base
- [file updated/created] — [summary of entry] OR "no update required"

### Instructions
- [summary of change] OR "no update required"

### Documentation
- [file updated] — [what was added/changed] OR "no update required (bug fix / no user-facing change)" OR "no documentation files found"

### Session learnings
- [top suggestions from impl-maintenance agent, or "no suggestions — routine session"]
- [one line per other code repository a change is needed in (the plan's Out of scope or Phase 3A/3B step 2), naming each change — a follow-up for `/dev-workflows:implement` run from that repository, addressed as Phase 3A/3B step 2 says; omit the line where there is none]

### Assumptions & limitations
- [list any]

### Deferred items (from review or tests)
[every line below that has content; "none" only where all of them are empty. Nine instructions in this file write test records here and the heading admits every one of them — they land in the seven test bullets below, the two `CAVEAT: ` instructions (Pre-Phase 3.5's over its capture and Phase 3.5 step 5's over its verify) sharing one and the two `test-writer` `### Notes` instructions (Phase 3.5 step 2's and Phase 3B step 4a's) sharing another, and a template naming only the review half is how those records get dropped; this section is the run's only account of what it did not verify. Phase 6 deliberately does **not** turn these into follow-ups, on the ground that they are in-scope work already carried by this task — which holds only if they are written down here. The exception is a finding whose fix lies in another code repository, which Phase 6 collects as a Phase 3A/3B step 2 change.]
- [review findings that were not applied — MINOR / NIT, a MAJOR or BLOCKER `review-fixer` deferred, every survivor whose fix lies in another code repository (Phase 3B step 7's *Another code repository's findings*), and every survivor of a re-review, with its severity; omit the line where there are none]
- [each suite the Pre-Phase 3.5 capture left unmarked `OK`/`NO_TESTS`, with the command that failed and whatever that block's `### Notes` said about it (Pre-Phase 3.5's `PARTIAL` arm); omit where none]
- [the recorded `test_decision: skip` — the operator's rationale, or, on the run's own record, the capture failure that produced it (Pre-Phase 3.5); omit where none]
- [each suite the Phase 3.5 verify could not run at either end, with whatever that report's `### Notes` said about it (step 5's `PARTIAL` arm); omit where none]
- [an accepted unverified run, with whatever the report gave as its reason (step 5's `RUN_FAILED` / `COMMAND_NOT_FOUND` arm); omit where none]
- [each kept regression and each kept new failure, with the user's rationale (step 6's Accept arm); omit where none]
- [each behaviour, a Review focus line included, that a `test-writer` report's `### Notes` named as untested — one it cannot test in isolation, or one a `hinted` or `declared` command gave it no test to follow for — with the reason it gave (Phase 3.5 step 2, Phase 3B step 4a); omit where none]
- [each `CAVEAT: ` line the Pre-Phase 3.5 capture block or a Phase 3.5 verify report carried, verbatim and with which of the two carried it — written whatever those returns' `Status` values were, `OK` and `NO_TESTS` included, since a marked line is exactly the kind of note a return that reports nothing wrong can still carry; omit where neither carried one]

### Next step
[Per `workflows-core:next-phase-offer` — guidance only, never auto-invoked. On a keyed run, where this run found a change another code repository needs (the plan's Out of scope or Phase 3A/3B step 2), name first a `/dev-workflows:implement` run from that repository, addressed as Phase 3A/3B step 2 says, before any documentation step; a direct run, which omits this section, names that change in `### Session learnings` alone. keyed mode: finish the remaining Epics under the PRD (breadth) — `/dev-workflows:implement <SIBLING-EPIC>`, one address, the Epic's own (D4) — and, once **all** Epics are implemented, `/docs-workflows:document <PRD>` then `/docs-workflows:release-notes <PRD>` (both PRD-level, run once). Depth vs breadth is the team's call. Direct mode: no forward pipeline step (omit). If the review stayed blocked, resolve that first.]

### Context hygiene

*(keyed runs only — omit this whole block in direct-prompt mode, like the `### Next step` above.)*
The resume pointer is written in the terminal cost phase (Phase 7), per `workflows-core:session-hygiene` §1. Then:

- **More Epics to build (`/dev-workflows:implement <SIBLING-EPIC>`) or on to `/docs-workflows:document <PRD>` — same build lane?** → run **`/compact`** — context stays relevant.
- Consider **`/rename <PRD-ID>-<slug>-dev`** to relocate this session later.

Guidance only — see `workflows-core:session-hygiene`.
```

Also repeat the `Run flags: …` line whenever Phase 0 printed one during this run (`workflows-core:run-flags` §6), and carry the `Session feedback: …` line wherever Phase 4 printed one (under `--skip-feedback`). The `Session cost: …` line is Phase 7's own output, printed after this report and not restated in it.

---

## Phase 6 — Emit follow-up tasks

Terminal phase — runs AFTER the Phase 5 Final Report is composed; NEVER
interrupts an earlier phase. Persist the run's out-of-scope / manual-step
follow-ups by invoking `Skill(skill: "workflows-core:reference", args: "followup-emission")` and executing its steps inline.

1. **Collect** the qualifying follow-ups: one per other code repository a change is needed in (the plan's Out of scope or Phase 3A/3B step 2), listing each change this run found there, manual publish/config steps and
   out-of-scope maintenance items surfaced in the Phase 5 `### Session
   learnings` section (e.g. an impl-maintenance suggestion that touches
   another repo or team, or a manual post-merge step). **Do NOT** collect the
   report's `### Deferred items (from review or tests)` or skipped tests — §6
   explicitly excludes those as in-scope work already carried by the current task. A finding whose fix lies in another code repository is the exception: the first clause above collects it.
2. **Filter** them with the reference's §6 qualifying predicate.
3. **Resolve** the write target via the §2 ladder using `key` and `source`
   (keyed runs carry a key; direct-prompt runs usually do not, so tasks
   are report-only);
   render + place tasks and verbose notes per §1–§3; dedupe per §5.
4. **Preview + confirm** per §7 (`approve-all | select | cancel`), then write.

ADDITIVE — the follow-ups also remain in the Phase 5 report. This phase NEVER
fails the run, NEVER commits (still true — this phase only writes follow-up
files; those writes are committed by the terminal `commit-artifacts` step in
Phase 7, per `workflows-core:specs-repo-git` §4), and
NEVER writes into the code repo or the current working directory, where it is not the specs repository.

---

## Phase 7 — Session cost

Terminal phase — the NEW final operational phase; runs after Phase 6 (the
follow-up phase) and NEVER interrupts an earlier phase. Records this command's
token-cost contribution to the PRD. Unlike feedback, **cost ALWAYS runs** — it never "writes
nothing" (short of `run_flags.skip_costs`, below, which writes no entry).

**Under `run_flags.skip_costs`**, do not call `emit-cost` and do not load `cost-emission`: execute `skip-cost` (`Skill(skill: "workflows-core:reference", args: "run-flags skip-cost")`) instead, which advances the checkpoint and drops any deferred record, and surface `Session cost: skipped (--skip-costs)` (or `(WORKFLOWS_SKIP_COSTS)`). The resume-pointer write and the terminal `commit-artifacts` step below run unchanged either way.

Otherwise, invoke `Skill(skill: "workflows-core:reference", args: "cost-emission emit-cost")` and call `emit-cost` with `command: /implement`, `phase: implementation`,
`role: dev`, the run's `key` (or `null`) and `source`, and `plugin_version`
(read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). It resolves the
session transcript + subagents (§1), loads and **advances the chained
checkpoint** (§3), computes the per-model token-cost delta against the price table (§4), records the optional statusline
cross-check (§5), and appends one per-invocation entry to
`<PRD-dir>/dev-workflows/cost/<sid8>.md` via the specs-first ladder (§8) — pending
+ opportunistic move-then-delete reconciliation (§9) when no PRD key resolves.
**The checkpoint advances even in the pending / report-only tiers.** Surface the
persisted path (or the report-only notice) as this phase's only output.

**Then write the resume pointer (keyed runs only).** Invoke `Skill(skill: "workflows-core:reference", args: "session-hygiene")` and, per its §1, write/overwrite
`<PRD-dir>/dev-workflows/resume.md` now — after the cost entry above, so the
pointer reflects the completed run, and before the commit step below, so it
is included in it. Redact per §1. Silent; the printed `### Context hygiene`
guidance already appeared in the Phase 5 report.

**Then commit session artifacts (terminal).** Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git commit-artifacts")` and execute its `commit-artifacts` entry point (§4) inline — the LAST action of the run. It
stages ONLY the §2.1 bounded artifact paths inside `$SPECS_PATH`, commits
`<KEY> Add dev-workflows session artifacts (/implement)`, and pushes per §4
step 5. It NEVER writes into the code repo this run just changed — that repo's
own commit was Phase 4.6's, as were whatever push and pull request §2.4's
consent choice, §2.8's base-branch ladder and §2.6's `gh` capability probe
allowed, through a different reference and against a different remote —
NEVER touches a docs repo or the current working directory, where it is not the specs repository;
NEVER force-pushes;
NEVER fails the run; and skips entirely when the run carries `specs_git: blocked` (§3.3 G0) or `specs_git: misrooted` (§3.1, or `specs-root-check`'s stop), re-emitting that notice. Because the Phase 5 report was
composed before this phase, **print its §6 outcome line here**, as the run's
last output — prefixed `Specs repo:`, with any guard notice repeated in full.

ADDITIVE — this phase NEVER fails the run and NEVER commits the deliverable itself
(the terminal step above commits only the bounded session-artifact paths in
`$SPECS_PATH`; the implementation itself was committed in Phase 4.6, in the code repo, and pushed there where §2.4's consent choice, an `origin` and §2.5's push itself all allowed it — §3.1's rows rather than any list written out here are the authority on which line the run emitted, and its `push FAILED (<reason>)` row is a state in which that choice and an `origin` both allowed a push that did not happen — via `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2; the spec/design conformance notes step 7.5 wrote into `$SPECS_PATH` are handed off separately, also before this phase (one it wrote into this repository went with the implementation's commit, or stays in the working tree under `--no-commit`), via `workflows-core:phase-handoff` §2), and NEVER writes into the code repo or the current working
directory, where it is not the specs repository; no user name is ever written (§10 privacy).

---

## Invariants (always enforced)

- ALWAYS `emit-block` (per `workflows-core:feedback-emission`) before escalating a halt caused by a **plugin / skill / command / reference gap** (a capability the run needed but the plugin lacked) — so a run abandoned at the block still records it. NEVER for a work-quality review BLOCK or an environment / user halt (repo-missing, dirty-tree, key-not-found, cancellation). The one exception is a halt on a tool the ai-containers image lacks, which `workflows-core:feedback-emission` §6 `emit-block` defines.
- NEVER skip Phase 1.5 classification — every run must state the level
- NEVER change code in a code repository other than the one Pre-Phase 3 branched — not in Phase 3A or 3B, not in Phase 3.5's fixes, not through `review-fixer`; a change another code repository needs is recorded as Phase 3A/3B step 2 says
- NEVER use Opus for routine implementation, unless §10 enforces a model (`workflows-core:model-routing/classification` §10 — every dispatched step then runs on `run_flags.enforced_model`, whatever it is); otherwise reserve it for planning + review on SIGNIFICANT / HIGH-RISK
- NEVER run tests on SIGNIFICANT / HIGH-RISK work before the Opus code review (the Phase 3B review gate, whatever model it runs on) returns a non-BLOCK verdict, or a `workflows-core:finding-triage` settle prompt's **Proceed** settles it as one
- NEVER skip Phase 3.5 — where the Pre-Phase 3.5 capture returns `COMMAND_NOT_FOUND` (no framework detected) or `RUN_FAILED` (every suite the capture actually ran aborted with no parseable counts — *run*, not *detected*, since a `command_hint` can narrow one set against the other, and a suite that ran to completion printing unrecognised output never failed to start), ask the user there, where a baseline can still be taken, rather than silently skipping; a "Skip" decision must be explicit and logged in the Phase 5 report, and it drops steps 4–6 only — step 3's lint and build still run
- NEVER read a verify report as a pass on any value but `OK` or `PARTIAL` — `RUN_FAILED` means nothing was compared and `COMMAND_NOT_FOUND` means nothing was run, and each is surfaced (Phase 3.5 step 5), never passed over
- NEVER read `OK` or `PARTIAL` as a pass while the report's `### New failures` list is non-empty — a test this run wrote and that fails now is in neither baseline list, so it moves no `Status` at all; Phase 3.5 step 5 reads the list **beside** the `Status` rather than instead of it (the `PARTIAL` arm's `### Deferred items` record is still owed either way), and a non-empty list then sends the run into step 6's fix loop
- NEVER assume what the evidence leaves open and the user would notice — look first, then ask (Phase 1); NEVER ask what the repository already answers
- NEVER end implementation with "Should I implement?" — if approved, implement
- NEVER rewrite files wholesale when only an append/edit is needed
- NEVER skip Phase 4 — documentation, knowledge, instructions, and session-maintenance are mandatory after every successful impl; always collect all four agent summaries for Phase 5
- ALWAYS capture a test baseline (Pre-Phase 3.5) before writing any file
- ALWAYS create a feature branch (Pre-Phase 3) before writing any file — never implement directly on the default branch
- ALWAYS check for a clean working tree before branching; stash or get explicit user consent if dirty — and record `stash_ref` / `pre_existing_dirty` for Phase 4.6, which cannot honour `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.2's carve-outs without them
- ALWAYS run Phase 4.6 (`finish-code-branch`, per `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md`) after Phase 4 and before the Phase 5 report — the commit is prompt-free (§1 rule 5) save for §2.2's secret-scan prompt on a hit, and the push + pull request sit behind §2.4's choice; a run that ends with the implementation uncommitted is a defect, not a style, save where you stopped the commit at §2.2's secret scan, and `--no-commit` is its only opt-out
- NEVER commit the implementation before Phase 4 — Phase 4's maintenance agents write into the same repo, and a commit ahead of them ships a partial run
- NEVER skip Phase 4.6 because a gate failed — a run meeting **any** of the conditions Phase 4.6's own `clean_finish` input row lists is committed like any other and pushed behind the same §2.4 consent choice, and sets `clean_finish: false` so any pull request it opens is a draft carrying the DO-NOT-MERGE banner (`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.9). That row is where they are enumerated; this line cites it rather than keeping a second copy, which is exactly how the row and the `"Every run"` paragraph above it came to disagree
- ALWAYS run `specs-preflight` at Phase 0 and `commit-artifacts` as the run's last action (per `workflows-core:specs-repo-git`) — bounded to `$SPECS_PATH`'s artifact paths (§2.1) and to plugin-created branches (§2.2), always `git -C "$SPECS_PATH"` and never a `cd` (§1 rule 1), never force-pushing, and never failing the run
- ALWAYS spawn Phase 4 agents in a single message — never sequentially
- ALWAYS use `choices` arrays for decision points; 2–4 options, and never author an "Other" option — the harness supplies the free-text escape itself (`workflows-core:escalation-rules` §0)
- ALWAYS produce the Phase 5 report as the final output
- ALWAYS end the Phase 5 report with a `### Next step` recommendation (per `Skill(skill: "workflows-core:reference", args: "next-phase-offer")`) — guidance only, never auto-invoked; omitted in direct mode (no PRD/Epic pipeline context)
- ALWAYS pass `Command run: /implement` in the Phase 4 Agent 4 session handoff
- ALWAYS pass `Change type: code` in the Phase 4 change summary block (scopes the four maintenance agents' suggestions to code-change territory — docs variants use `docs`)
- AFTER one review-fixer pass + one re-review, if the review stayed blocked (`workflows-core:finding-triage` § On re-review): stop and surface to user — do NOT loop
- ALWAYS state, with the recorded review verdict, which version it was taken against — where any edit followed it (a review-fixer pass, a manual fix, a Phase 3.5 regression fix), the Phase 5 report says so and names the edits, per the `A recorded verdict names the version it was taken against` rule in `Skill(skill: "workflows-core:reference", args: "escalation-rules")`; where none did, it says that too
- AFTER two Phase 3.5 fix-loop attempts, if any regression or new failure remains: stop and surface to user — do NOT loop
- ALWAYS classify each `@path` input by inspection (Phase 0) — never by matching the path string
- WHEN `fan_out` is true (more than one distinct code repository, or a specs or spec/design folder): floor classification at SIGNIFICANT (overridable at plan approval), run Phase 1.7, and feed its synthesized summary to the planner instead of the single Explore subagent
- WHEN `fan_out` is true and a theme stays inconclusive: run round 2 (§8.5) when round 1 left an evidence anchor to seed it, and name every still-unresolved theme — including one that never entered round 2 for lack of an anchor — in the summary's `## Unresolved` section and the risk-planner brief's `Unresolved scan themes:` field; NEVER fold it in as an ordinary gap
- WHEN a `specification.md`/`design.md` is in scope on a SIGNIFICANT / HIGH-RISK run: extract its in-scope IDs, pass `applicable_spec` to `code-review`, report conformance in Phase 5, and escalate unresolved `missing`/`contradicts` as `- [ ]` notes on the spec/design where it lies in `$SPECS_PATH` or this repository, and, where it lies elsewhere, in the Phase 5 report or an early stop's message — never silently
- WHEN `task_shape: bug` on a SIGNIFICANT / HIGH-RISK run: risk-planner follows `bug-diagnosis.md` (repro-first + ranked hypotheses), and all `[DEBUG-xxxx]` instrumentation is stripped before the Opus-review diff is captured
- WHEN `task_shape: bug`: the ranked hypotheses MUST be backed by a repro `risk-planner` **actually ran** — its `### Hypotheses (ranked)` block carries the command, its redacted output, and the reproduction rate (`bug-diagnosis.md` step 1's completion criterion). If it returns "Ranking withheld — no red-capable repro", do NOT proceed to implementation on a guess: surface what it tried and ask `choices: ["Help construct a repro (you'll be prompted for what to try)", "Proceed without a repro (recorded in the Phase 5 report)", "Cancel"]`. Proceeding is the user's call to make explicitly, never the default.
- ALWAYS fan out `code-scanner` one-per-repo in a single response, capped at 4 concurrent — never sequentially
- NEVER silently skip a referenced `@dir` that is missing or unrecognized — surface it and ask (classification.md §8.4)
- Scanning agents (the folder read, `code-scanner`) are pinned to the §2.1 detection (Sonnet) chain like every mechanical step (never inherit the session model); escalate a single scanner to Opus only when one repo slice is oversized (under §10, `run_flags.enforced_model` for both the pin and the escalation)
- ALWAYS end the Phase 5 report with a `### Context hygiene` block per `workflows-core:session-hygiene` — prepare-first (the `resume.md` write runs later, in the terminal cost phase, per `workflows-core:session-hygiene` §1 — this block prints the guidance only), then a same-lane `/compact` suggestion + `/rename <PRD-ID>-<slug>-dev`; **omitted in direct mode** (no PRD/Epic context, no `resume.md`); the Phase 3B checkpoint additionally suggests `/compact` mid-run. Guidance only, never auto-run.
